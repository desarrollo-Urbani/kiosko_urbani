from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Project, Property, RecommendationItem, RecommendationRun, SessionAnswer


MATCH_HIGH_THRESHOLD = 80
MATCH_MEDIUM_THRESHOLD = 50
MIN_TARGET_RESULTS = 3
MAX_RESULTS = 5
BASE_BUDGET_TOLERANCE = 1.1
RELAXED_BUDGET_TOLERANCE = 1.2

ADJACENT_COMMUNES: dict[str, set[str]] = {
    "vitacura": {"las condes", "providencia", "lo barnechea"},
    "nunoa": {"providencia", "santiago", "la reina", "macul"},
    "maipu": {"cerrillos", "estacion central", "pudahuel"},
}


def _normalize_string(value: object) -> str:
    return str(value or "").strip().lower()


def _load_answers(db: Session, session_id: str) -> dict[str, object]:
    rows = db.scalars(select(SessionAnswer).where(SessionAnswer.session_id == session_id)).all()
    out: dict[str, object] = {}
    for row in rows:
        if isinstance(row.answer_value, dict) and "value" in row.answer_value:
            out[row.question_key] = row.answer_value["value"]
        else:
            out[row.question_key] = row.answer_value
    return out


def _score_property(
    prop: Property,
    project: Project,
    answers: dict[str, object],
    budget_tolerance: float,
    allowed_communes: set[str],
) -> tuple[int, list[str], str]:
    score = 0
    tags: list[str] = []

    wanted_type = _normalize_string(answers.get("property_type"))
    budget = float(answers.get("budget_uf", 0) or 0)
    preferred_commune = _normalize_string(answers.get("zone"))
    min_bedrooms = int(answers.get("bedrooms", 0) or 0)
    min_bathrooms = int(answers.get("bathrooms", 0) or 0)
    prop_type = _normalize_string(prop.property_type)
    project_commune = _normalize_string(project.commune)

    if wanted_type and prop_type == wanted_type:
        score += 40
        tags.append("tipo_ok")

    if budget > 0:
        if prop.price_uf <= budget:
            score += 30
            tags.append("budget_ok")
        elif prop.price_uf <= budget * budget_tolerance:
            score += 15
            tags.append("budget_tolerance")

    if preferred_commune and project_commune == preferred_commune:
        score += 20
        tags.append("zona_ok")
    elif allowed_communes and project_commune in allowed_communes:
        score += 10
        tags.append("zona_expandida")

    size_ok = min_bedrooms > 0 and prop.bedrooms >= min_bedrooms
    bath_ok = min_bathrooms > 0 and prop.bathrooms >= min_bathrooms
    if size_ok or bath_ok:
        score += 10
        tags.append("size_ok")

    explanation = (
        f"{project.name} en {project.commune} con {prop.bedrooms}D/{prop.bathrooms}B por "
        f"{prop.price_uf:.0f} UF. Coincidencias: {', '.join(tags) if tags else 'parcial'}."
    )
    return score, tags, explanation


def _match_level(score: int) -> str:
    if score >= MATCH_HIGH_THRESHOLD:
        return "high"
    if score >= MATCH_MEDIUM_THRESHOLD:
        return "medium"
    return "low"


def _build_result(
    prop: Property,
    project: Project,
    score: int,
    tags: list[str],
    explanation: str,
) -> dict:
    return {
        "property_id": prop.id,
        "project_name": project.name,
        "commune": project.commune,
        "property_type": prop.property_type,
        "price_uf": prop.price_uf,
        "bedrooms": prop.bedrooms,
        "bathrooms": prop.bathrooms,
        "total_score": score,
        "match_level": _match_level(score),
        "match_tags": tags,
        "explanation": explanation,
        "match_debug": {
            "property_id": prop.id,
            "total_score": score,
            "match_tags": tags,
            "explanation": explanation,
        },
    }


def _score_candidates(
    candidates: Iterable[tuple[Property, Project]],
    answers: dict[str, object],
    budget_tolerance: float,
    allowed_communes: set[str],
) -> list[dict]:
    scored: list[dict] = []
    for prop, project in candidates:
        score, tags, explanation = _score_property(
            prop=prop,
            project=project,
            answers=answers,
            budget_tolerance=budget_tolerance,
            allowed_communes=allowed_communes,
        )
        scored.append(
            {
                "property": prop,
                "project": project,
                "score": score,
                "tags": tags,
                "explanation": explanation,
            }
        )
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored


def _dedupe_scored(items: list[dict]) -> list[dict]:
    selected: list[dict] = []
    seen: set[str] = set()
    for item in items:
        prop_id = item["property"].id
        if prop_id in seen:
            continue
        seen.add(prop_id)
        selected.append(item)
    return selected


def run_recommendation(db: Session, session_id: str) -> list[dict]:
    answers = _load_answers(db, session_id)
    if not _normalize_string(answers.get("property_type")):
        return []

    candidates = db.execute(
        select(Property, Project)
        .join(Project, Project.id == Property.project_id)
        .where(Property.stock_status == "available", Project.is_active.is_(True))
    ).all()
    if not candidates:
        return []

    preferred_commune = _normalize_string(answers.get("zone"))
    adjacent_communes = ADJACENT_COMMUNES.get(preferred_commune, set())

    base_ranked = _score_candidates(
        candidates=candidates,
        answers=answers,
        budget_tolerance=BASE_BUDGET_TOLERANCE,
        allowed_communes=set(),
    )
    selected = base_ranked[:MAX_RESULTS]

    if len(selected) < MIN_TARGET_RESULTS:
        relaxed_budget_ranked = _score_candidates(
            candidates=candidates,
            answers=answers,
            budget_tolerance=RELAXED_BUDGET_TOLERANCE,
            allowed_communes=set(),
        )
        selected = _dedupe_scored(relaxed_budget_ranked + selected)[:MAX_RESULTS]

    if len(selected) < MIN_TARGET_RESULTS and adjacent_communes:
        expanded_zone_ranked = _score_candidates(
            candidates=candidates,
            answers=answers,
            budget_tolerance=RELAXED_BUDGET_TOLERANCE,
            allowed_communes=adjacent_communes,
        )
        selected = _dedupe_scored(expanded_zone_ranked + selected)[:MAX_RESULTS]

    if len(selected) < MIN_TARGET_RESULTS:
        fallback_candidates = _dedupe_scored(base_ranked + selected)
        for item in fallback_candidates:
            if len(selected) >= MIN_TARGET_RESULTS:
                break
            if item in selected:
                continue
            item["tags"] = list(item["tags"]) + ["featured_fallback"]
            item["explanation"] = (
                f"{item['explanation']} Destacada del mes por disponibilidad inmediata."
            )
            selected.append(item)
        selected = selected[:MAX_RESULTS]

    run = RecommendationRun(
        session_id=session_id,
        engine_version="mvp-v2",
        match_params=answers,
    )
    db.add(run)
    db.flush()

    out: list[dict] = []
    for item in selected:
        rec = RecommendationItem(
            run_id=run.id,
            property_id=item["property"].id,
            match_score=item["score"],
            match_tags=item["tags"],
            explanation=item["explanation"],
        )
        db.add(rec)
        out.append(
            _build_result(
                prop=item["property"],
                project=item["project"],
                score=item["score"],
                tags=item["tags"],
                explanation=item["explanation"],
            )
        )

    db.commit()
    return out


def get_latest_recommendations(db: Session, session_id: str) -> list[dict]:
    run = db.scalars(
        select(RecommendationRun)
        .where(RecommendationRun.session_id == session_id)
        .order_by(RecommendationRun.generated_at.desc())
    ).first()
    if not run:
        return []

    rows = db.scalars(select(RecommendationItem).where(RecommendationItem.run_id == run.id)).all()
    out = []
    for row in rows:
        prop, project = db.execute(
            select(Property, Project)
            .join(Project, Project.id == Property.project_id)
            .where(Property.id == row.property_id)
        ).one()
        out.append(
            _build_result(
                prop=prop,
                project=project,
                score=row.match_score,
                tags=row.match_tags,
                explanation=row.explanation,
            )
        )
    return out
