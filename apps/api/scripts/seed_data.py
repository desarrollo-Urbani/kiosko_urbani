import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from sqlalchemy import select

from apps.api.app.database import SessionLocal
from apps.api.app.models import Project, Property


PROJECTS = [
    {
        "name": "Urbani Vitacura Park",
        "commune": "Vitacura",
        "city": "Santiago",
        "delivery_status": "immediate",
        "subsidy_available": False,
    },
    {
        "name": "Urbani Nunoa Central",
        "commune": "Nunoa",
        "city": "Santiago",
        "delivery_status": "construction",
        "subsidy_available": True,
    },
    {
        "name": "Urbani Maipu Green",
        "commune": "Maipu",
        "city": "Santiago",
        "delivery_status": "white_plan",
        "subsidy_available": True,
    },
]

PROPERTIES = [
    {"property_type": "dept", "bedrooms": 2, "bathrooms": 2, "area_total_m2": 68, "price_uf": 5200, "dividend_est_clp": 680000, "stock_status": "available"},
    {"property_type": "dept", "bedrooms": 1, "bathrooms": 1, "area_total_m2": 45, "price_uf": 3900, "dividend_est_clp": 510000, "stock_status": "available"},
    {"property_type": "house", "bedrooms": 3, "bathrooms": 2, "area_total_m2": 115, "price_uf": 7600, "dividend_est_clp": 980000, "stock_status": "available"},
    {"property_type": "office", "bedrooms": 1, "bathrooms": 1, "area_total_m2": 40, "price_uf": 4300, "dividend_est_clp": 550000, "stock_status": "available"},
]


def main():
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        print("No se encontro .env. Usa .env.example como base.")

    db = SessionLocal()

    try:
        has_projects = db.scalar(select(Project.id).limit(1))
        if has_projects:
            print("Seed ya aplicado.")
            return

        project_objs: list[Project] = []
        for project in PROJECTS:
            obj = Project(**project)
            db.add(obj)
            project_objs.append(obj)
        db.flush()

        for idx, project in enumerate(project_objs):
            base = PROPERTIES[idx % len(PROPERTIES)]
            for variant in range(2):
                db.add(
                    Property(
                        project_id=project.id,
                        property_type=base["property_type"],
                        bedrooms=base["bedrooms"] + (variant % 2),
                        bathrooms=base["bathrooms"],
                        area_total_m2=base["area_total_m2"] + (variant * 5),
                        price_uf=base["price_uf"] + (variant * 300),
                        dividend_est_clp=base["dividend_est_clp"] + (variant * 40000),
                        stock_status="available",
                        image_url="https://images.unsplash.com/photo-1484154218962-a197022b5858",
                    )
                )

        db.commit()
        print("Seed aplicado correctamente.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
