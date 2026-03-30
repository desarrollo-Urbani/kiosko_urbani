# 003 - Business Rules

## 1. Turnero e Identificación
- **Emisión**: El usuario puede obtener su número de atención (ticket con ID único) y comenzar el perfilamiento en el mismo flujo o pantalla, según la configuración UX. Ambos procesos pueden estar integrados para reducir fricción.
- **Identificación**: Se pide nombre y teléfono (mínimo un campo obligatorio para cerrar el lead, opcional para ver propiedades).
- **Wait Time**: El cálculo de espera (ETA) en el MVP es **simulado** basado en una constante de "tiempo promedio de atención" (ej. 15 min) multiplicado por la cantidad de tickets activos.
- **Confirmación**: Se muestra una pantalla con el número y QR (opcional) que apunta a una URL de seguimiento de cola pública.

## 2. Flujo de Perfilamiento
- **Persistencia**: Cada respuesta debe guardarse en el backend inmediatamente (vía WebSocket o REST) para evitar pérdida en timeouts.
- **Flexibilidad**: Si el usuario elige "No estoy seguro" o "Saltar", el sistema asigna una categoría "Neutro" o "Rango Amplio" para no bloquear la recomendación.
- **Limite**: Máximo 5 preguntas clave. El usuario puede finalizar el flujo prematuramente presionando el botón de "Ver Sugerencias" si ya contestó al menos 2 preguntas.

## 3. Motor de Recomendación (Scoring MVP)
- **Filtro Duro**: Solo propiedades con `stock_status = 'available'`.
- **Match Score**:
  - +50 pts: Tipo de propiedad exacto.
  - +30 pts: Dentro del presupuesto (+/- 10% tolerancia).
  - +20 pts: Ubicación preferida.
  - +10 pts: Plazo de compra alineado (ej. entrega inmediata).
- **Fallback**: Si no hay coincidencias con score > 50, mostrar los "Top 3 más recientes" de la misma zona.

## 4. LLM y Asistencia conversacional
- **Acompañamiento**: El asistente debe comentar las elecciones del usuario (ej. "¡Excelente zona! Tenemos proyectos muy cerca del metro").
- **No es decisor**: El LLM no puede cambiar el set de resultados devuelto por el motor de recomendación, solo puede explicarlos o enfatizarlos.
- **Seguridad**: El asistente no tiene acceso a datos personales de otros clientes ni info sensible de la empresa.

## 5. El "Lead Comercial" y Resumen
- **Trigger**: Se crea el lead cuando el usuario llega a la pantalla de "Resultados" O si emite un ticket de atención.
- **Contenido**: El resumen enviado al ejecutivo debe ser en formato "Bullet points" indicando disponibilidad financiera (ahorro/crédito), urgencia de compra y preferencias.
- **Prioridad**: El lead se marca como "Alta Prioridad" si el usuario indica que tiene el pie (ahorro) listo y quiere comprar pronto.

## 6. Analítica y Eventos
- Se registran eventos UX con `timestamp`, `session_id`, `screen_name` y `action` (click, skip, back).
- El abandono se detecta si no hay actividad por más de 120 segundos en el backend.

