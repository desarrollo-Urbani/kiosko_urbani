# 004 - Data Spec

## Motor de Base de Datos
- **PostgreSQL 15+**
- **Migraciones**: Alembic (Python)

## Entidades Principales

### kiosk_devices
- **id**: uuid (PK)
- **name**: varchar (ej. "Kiosco Sala Vitacura 1")
- **auth_token**: varchar (hashed)
- **last_heartbeat**: timestamp
- **is_active**: boolean

### kiosk_sessions
- **id**: uuid (PK)
- **kiosk_device_id**: uuid (FK)
- **session_key**: varchar (Unique)
- **status**: enum (active, completed, abandoned, expired)
- **started_at**: timestamp
- **finished_at**: timestamp
- **last_activity_at**: timestamp

### session_answers
- **id**: serial (PK)
- **session_id**: uuid (FK)
- **question_key**: varchar (ej. "property_type", "budget")
- **answer_value**: jsonb (valor técnico, ej. "dept")
- **answer_label**: varchar (valor humano, ej. "Departamento")
- **created_at**: timestamp

### queue_tickets
- **id**: serial (PK)
- **session_id**: uuid (FK)
- **ticket_number**: varchar (ej. "A-12")
- **customer_name**: varchar
- **customer_phone**: varchar
- **status**: enum (waiting, calling, served, canceled)
- **estimated_wait_minutes**: integer
- **created_at**: timestamp

### projects
- **id**: uuid (PK)
- **name**: varchar
- **commune**: varchar
- **city**: varchar
- **delivery_status**: enum (immediate, construction, white_plan)
- **subsidy_available**: boolean
- **is_active**: boolean

### properties (Stock)
- **id**: uuid (PK)
- **project_id**: uuid (FK)
- **property_type**: enum (dept, house, office)
- **bedrooms**: integer
- **bathrooms**: integer
- **area_total_m2**: decimal
- **price_uf**: decimal
- **dividend_est_clp**: integer
- **stock_status**: enum (available, reserved, sold)
- **image_url**: varchar

### recommendation_runs
- **id**: serial (PK)
- **session_id**: uuid (FK)
- **engine_version**: varchar
- **match_params**: jsonb (filtros aplicados)
- **generated_at**: timestamp

### recommendation_items
- **id**: serial (PK)
- **run_id**: serial (FK)
- **property_id**: uuid (FK)
- **match_score**: integer (0-100)
- **match_tags**: text[] (["zona", "precio"])
- **explanation**: text

### leads
- **id**: uuid (PK)
- **session_id**: uuid (FK)
- **customer_id**: uuid (FK - optional for repeat clients)
- **lead_status**: enum (new, viewed, contact_attempt, converted)
- **priority**: enum (low, medium, high)
- **raw_data**: jsonb (todo lo capturado en la sesión)
- **created_at**: timestamp

### executives
- **id**: uuid (PK)
- **full_name**: varchar
- **email**: varchar
- **is_available**: boolean
- **current_queue_count**: integer

## Requisitos de Almacenamiento
- **Snapshots**: Guardar el estado de la sesión cada vez que el usuario avanza de pantalla.
- **Auditoría**: `ux_events` debe registrar hasta los clics en imágenes de proyectos para análisis de calor.
- **Privacidad**: Los datos de contacto deben ser accesibles solo por ejecutivos asignados o administradores.

