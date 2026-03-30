# 006 - Recommender Spec

## Objetivo & Alcance
Entregar de 3 a 5 propiedades (unidades o proyectos según disponibilidad) ordenadas por afinidad. No usa LLM para la decisión, solo reglas deterministas de negocio.

## Algoritmo de Scoring (Match Score)
El score base es 0 y se acumula según los siguientes criterios:

1. **Tipo de Propiedad (Mandatorio)**: Si coincide, +40 pts.
2. **Presupuesto (Match Directo)**: Si `price_uf <= user_budget`, +30 pts.
3. **Presupuesto (Tolerancia)**: Si `price_uf` está entre `user_budget` y `user_budget * 1.1`, +15 pts.
4. **Ubicación/Zona**: Si coincide con la comuna preferida, +20 pts.
5. **Dormitorios/Baños**: Si coincide con las preferencias o las supera, +10 pts.

## Niveles de Match
- **Match Alto**: Score >= 80.
- **Match Medio**: Score >= 50.
- **Match Bajo**: Score < 50 (se muestra solo si no hay mejores).

## Estrategia de Relajación de Filtros
Si el motor devuelve < 3 resultados:
1.  **Paso 1**: Incrementar tolerancia de presupuesto al 20%.
2.  **Paso 2**: Expandir búsqueda a comunas colindantes (si hay metadata disponible).
3.  **Paso 3**: Si aún es insuficiente, mostrar propiedades "Destacadas del mes" independientemente del perfilamiento.

## Respuesta del Motor (Auditables)
Cada ítem en la respuesta debe incluir un objeto `match_debug`:
```json
{
  "property_id": "...",
  "total_score": 85,
  "match_tags": ["tipo_ok", "budget_ok", "zona_ok"],
  "explanation": "Este proyecto en Vitacura calza perfectamente con tu presupuesto de 5000 UF y busca de 2 dormitorios."
}
```

## Restricciones Críticas
- **Exclusión por Stock**: Nunca mostrar unidades con `stock_status != 'available'`.
- **Previa Validación**: No recomendar si el usuario no ha completado al menos el campo de "Tipo de Propiedad".

