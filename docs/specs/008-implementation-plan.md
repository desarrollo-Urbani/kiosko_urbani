# 008 - Implementation Plan

## 1. Estrategia de Construcción
La metodología será **iterativa y por módulos verticales**, priorizando la captura de datos y la estabilidad del backend antes de la estética final.

### Orden de Construcción y Dependencias
1.  **Fundamentos (Infra & Monorepo)**: Sin dependencias.
2.  **Core API & Data (Backend)**: Depende de Infra.
3.  **Kiosk UI & Session Mgmt (Frontend)**: Depende de Core API.
4.  **Perfilamiento & Turnero**: Depende de Backend + Frontend UI.
5.  **Motor de Recomendación**: Depende de Datos de Perfilamiento.
6.  **Capa LLM**: Depende de Recomendación + Contexto de Sesión.
7.  **Dashboard Operativo**: Depende de Leads y API.

---

## 2. Backlog por Fases

### Fase 1: Foundation (Infraestructura)
- **Objetivo**: Tener el entorno de desarrollo listo y automatizado.
- **Archivos Clave**: `docker-compose.yml`, `package.json` (raíz), `.env.example`, `apps/api/main.py` (dummy).
- **Criterios de Aceptación (AC)**:
  - `docker-compose up` levanta PostgreSQL 15.
  - El monorepo permite correr scripts desde la raíz.
- **Quick Win**: Healthcheck de la base de datos funcionando.

### Fase 2: Backend Core (Data & Auth)
- **Objetivo**: Establecer el contrato de API y persistencia.
- **Archivos Clave**: `apps/api/models/`, `apps/api/schemas/`, `apps/api/auth.py`, `infra/migrations/`.
- **Backend Backlog**:
  - Implementar Middleware `X-Kiosk-Token`.
  - Crear modelos SQLAlchemy para `kiosk_sessions`, `session_answers` y `projects`.
  - Crear script de **Data Seeding** para stock inicial.
- **AC**:
  - Un request sin token devuelve 401.
  - Se puede crear una sesión vía POST y verla en la DB.

### Fase 3: Kiosk Base (Frontend & Sessions)
- **Objetivo**: Primera visual del kiosco y manejo de estados.
- **Archivos Clave**: `apps/kiosk-web/app/layout.tsx`, `apps/kiosk-web/hooks/useSession.ts`.
- **Frontend Backlog**:
  - Layout portrait con Tailwind.
  - Implementar `useSession` (persistencia en LocalStorage).
  - Pantalla Home con CTA de inicio.
- **AC**:
  - El layout se ajusta a 1080x1920 sin scroll horizontal.
  - Al refrescar la página, el `session_id` se mantiene.

### Fase 4: Flujo de Perfilamiento y Turnero
- **Objetivo**: Capturar intención y emitir turnos.
- **Archivos Clave**: `apps/kiosk-web/components/questions/`, `apps/api/routers/queue.py`.
- **Backlog**:
  - UI de 5 preguntas (Tipo, Objetivo, Zona, Presupuesto, Subsidio).
  - Lógica de emisión de ticket (Número correlativo).
- **AC**:
  - Cada respuesta se guarda en la tabla `session_answers` tras hacer click.
  - Al final se muestra un número de atención (ej. A-01).

### Fase 5: El Cerebro (Recommender)
- **Objetivo**: Entregar valor comercial real.
- **Archivos Clave**: `apps/api/services/recommender.py`, `apps/kiosk-web/components/PropertyCard.tsx`.
- **Backlog**:
  - Implementar algoritmo de Scoring (0-100 pts).
  - Lógica de "Relajación de filtros" si hay pocos resultados.
  - Vista de carrusel de resultados en el Kiosco.
- **AC**:
  - Las recomendaciones mostradas tienen `stock_status = 'available'`.
  - El "Match Badge" (Alto/Medio) se muestra correctamente según el score.

### Fase 6: El Asistente (LLM Contextual)
- **Objetivo**: Humanizar la experiencia.
- **Archivos Clave**: `apps/api/services/llm.py`, `apps/kiosk-web/components/AnimatedBot.tsx`.
- **Backlog**:
  - Integración con OpenAI/Gemini.
  - Prompt System para "Kiosk Host".
  - Componente Bot con micro-animaciones CSS.
- **AC**:
  - El bot responde basado en la pantalla actual (ej. explica qué es un subsidio DS19).
  - Si el LLM falla, el bot desaparece silenciosamente.

### Fase 7: Dashboard & Conversión
- **Objetivo**: Cerrar el ciclo con el vendedor.
- **Archivos Clave**: `apps/dashboard/`, `apps/api/routers/leads.py`.
- **Backlog**:
  - Generación de **Lead Executive Summary** vía LLM.
  - Dashboard con lista de espera y detalle de perfil del cliente.
- **AC**:
  - El vendedor puede ver el resumen de 3 bullets del cliente antes de llamarlo.

---

## 3. Definition of Done (DoD)
Para cada fase y cada ticket:
- ✅ Código en TypeScript/Python con tipado estricto.
- ✅ Sin errores de Linting/Formatting.
- ✅ Pruebas básicas (Smoke tests) aprobadas.
- ✅ Documentación de la API actualizada en Swagger/OpenAPI.
- ✅ Registro de decisiones técnicas en `docs/decisions` si aplica.

---

## 4. Gestión de Riesgos Técnicos
| Riesgo | Impacto | Mitigación |
| :--- | :---: | :--- |
| **Latencia LLM** | Alto | Usar streaming (opcional) o mensajes de "Pensando..." UX. |
| **Pérdida de Sesión** | Medio | Persistencia redundante: LocalStorage + DB cada paso. |
| **Stock Sucio** | Crítico | Validación de stock en cada corrida del recomendador. |
| **Touch Precision** | Bajo | Área de click mínima de 44x44px en todos los botones. |

---

## 5. Quick Wins
- **Session Recovery**: Permite que si el kiosco se reinicia, el cliente no pierda su progreso.
- **Dashboard en Tiempo Real**: Notificación visual al ejecutivo apenas entra un lead de "Alta Prioridad".
- **Bot Fallback**: Mensajes pre-escritos si la API del LLM está caída.


