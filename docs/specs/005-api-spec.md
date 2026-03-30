# 005 - API Spec

## Base & Auth
- **URL Base**: `/api/v1`
- **Autenticación**: `X-Kiosk-Token` en el header para peticiones desde el kiosco.
- **Formato**: JSON (snake_case).

## Endpoints

### 1. Sesiones (`/sessions`)
- **POST `/`**: Inicia una nueva sesión. Devuelve `session_id`.
  - Body: `{ "kiosk_id": "uuid" }`
- **GET `/{id}`**: Recupera estado actual de la sesión.
- **POST `/{id}/answers`**: Registra una respuesta.
  - Body: `{ "question_key": "string", "answer_value": any, "answer_label": "string" }`

### 2. Turnero (`/queue`)
- **POST `/tickets`**: Emite un nuevo ticket.
  - Body: `{ "session_id": "uuid", "name": "string", "phone": "string" }`
  - Response: `{ "ticket_number": "A-12", "eta_minutes": 15 }`

### 3. Recomendación (`/recommendations`)
- **POST `/run`**: Ejecuta el motor de scoring para la sesión actual.
  - Body: `{ "session_id": "uuid" }`
- **GET `/{session_id}`**: Obtiene los resultados (top 3-5).

### 4. Asistente Conversacional (`/llm`)
- **POST `/assist`**: Solicita ayuda contextual al LLM.
  - Body: `{ "session_id": "uuid", "current_screen": "string", "user_query": "string" (optional) }`

### 5. Leads y Dashboard (`/dashboard`)
- **GET `/leads`**: Listado para el dashboard ejecutivo.
- **PATCH `/leads/{id}`**: Cambiar estado del lead (ej. "contactado").
- **POST `/leads/{id}/summary`**: Generar/Regenerar el resumen ejecutivo IA.

### 6. Telemetría (`/events`)
- **POST `/`**: Registrar evento de UI.
  - Body: `{ "session_id": "uuid", "event_type": "string", "payload": {} }`

## Códigos de Error
- `401 Unauthorized`: Token de kiosco inválido o expirado.
- `404 Not Found`: Sesión o recurso inexistente.
- `422 Unprocessable Entity`: Error de validación de esquema pydantic.
- `503 Service Unavailable`: LLM o Base de datos fuera de línea.

