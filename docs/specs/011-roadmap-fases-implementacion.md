# 011 - Roadmap de Implementacion por Fases

## Regla de trabajo acordada
- Se implementa por fases.
- Cada fase se marca en este documento.
- Se hace **1 commit por fase**, solo cuando el usuario apruebe la fase.

---

## Fase 1 - Base Solida
Objetivo: estabilizar base tecnica y flujo de turnos para operacion real.

### Checklist
- [x] Corregir tests SQLite en memoria (`StaticPool`) para evitar errores de tablas.
- [x] Estandarizar estados de turno: `waiting`, `called`, `in_service`, `completed`, `no_show`.
- [x] Exponer endpoint de actualizacion de estado de turno.
- [x] Registrar auditoria minima de cola:
  - [x] `queue_ticket_created`
  - [x] `queue_ticket_status_changed`
- [x] Dejar documentada fuente de verdad de frontend operativo en README.
- [x] Validar suite de tests en verde.

### Estado de fase
- Estado: **Completada**
- Evidencia:
  - Tests: `5 passed`
  - Endpoints de cola activos en API

---

## Fase 1.1 - Dashboard Ejecutivo Minimo
Objetivo: habilitar operacion diaria del ejecutivo con flujo corto.

### Checklist
- [x] Crear vista `/executive-dashboard`.
- [x] Implementar accion principal `LLAMAR SIGUIENTE`.
- [x] Implementar `Iniciar atencion`.
- [x] Implementar `Finalizar atencion`.
- [x] Agregar endpoint atomico `POST /api/v1/queue/call-next` para evitar colisiones.
- [x] Mostrar cola de espera con:
  - [x] Turno
  - [x] Tiempo esperando
  - [x] Perfilado (Si/No)
- [x] Validar endpoint y dashboard en runtime.

### Estado de fase
- Estado: **Completada**
- Evidencia:
  - `/api/v1/queue/call-next` responde `200`
  - `/executive-dashboard` responde `200`

---

## Fase 1.2 - Asignacion por Ejecutivo (pendiente)
Objetivo: que cada ejecutivo opere su turno activo sin interferencias.

### Checklist
- [x] Identidad operativa de ejecutivo (simple).
- [x] Asociar turno activo al ejecutivo.
- [x] Bloquear que un ejecutivo tome otro turno si ya tiene uno activo.
- [x] Vista de turno actual por ejecutivo.
- [x] Auditoria con actor (`executive_id`) por accion.
- [x] Pruebas de concurrencia minima (2 ejecutivos).

### Estado de fase
- Estado: **Completada (pendiente de aprobacion de usuario)**

---

## Fase 2 - Operacion Multi-Modulo (pendiente)
Objetivo: escalar cola por sucursal/modulo y mejorar supervision.

### Checklist
- [x] Cola particionada por sucursal/modulo.
- [x] Priorizacion configurable (SLA, cita, VIP, etc.).
- [x] Dashboard supervisor (vista global y reasignacion).
- [x] Metricas operativas:
  - [x] espera promedio
  - [x] atencion promedio
  - [x] no-show
  - [x] productividad por ejecutivo

### Estado de fase
- Estado: **Completada (pendiente de aprobacion de usuario)**

---

## Fase 3 - Produccion (pendiente)
Objetivo: endurecer seguridad, despliegue y observabilidad.

### Checklist
- [x] Migraciones (Alembic) y versionado de esquema.
- [x] Auth por roles para produccion.
- [ ] Configuracion por ambiente (dev/staging/prod).
- [ ] Observabilidad y trazas (logs estructurados, errores).
- [ ] Hardening de seguridad y privacidad de datos sensibles.

### Estado de fase
- Estado: **En progreso**
