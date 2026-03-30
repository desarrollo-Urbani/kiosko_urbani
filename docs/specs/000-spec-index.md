# 000 - Spec Index

Este documento define el orden de lectura, dependencias y estado de las especificaciones del Asistente Digital de Sala Urbani.

## Índice de lectura y dependencias

1. [001 - Product Spec](001-product-spec.md)
   - **Propósito**: Define la visión, alcance y KPIs del proyecto.
   - **Dependencias**: Ninguna.
   - **Estado**: Refinado / Listo para implementación.

2. [002 - UX Spec](002-ux-spec.md)
   - **Propósito**: Define principios de diseño, flujo de pantallas e interacción táctil.
   - **Dependencias**: 001.
   - **Estado**: Refinado / Listo para implementación.

3. [003 - Business Rules](003-business-rules.md)
   - **Propósito**: Lógica detallada del turnero, perfilamiento y leads.
   - **Dependencias**: 001, 002.
   - **Estado**: Refinado / Listo para implementación.

4. [004 - Data Spec](004-data-spec.md)
   - **Propósito**: Modelado de datos en PostgreSQL.
   - **Dependencias**: 003.
   - **Estado**: Refinado / Listo para implementación.

5. [005 - API Spec](005-api-spec.md)
   - **Propósito**: Contratos de comunicación entre Kiosk Web, Dashboard y API.
   - **Dependencias**: 004.
   - **Estado**: Refinado / Listo para implementación.

6. [006 - Recommender Spec](006-recommender-spec.md)
   - **Propósito**: Algoritmo de scoring y filtrado de propiedades.
   - **Dependencias**: 003, 004.
   - **Estado**: Refinado / Listo para implementación.

7. [007 - LLM Spec](007-llm-spec.md)
   - **Propósito**: Definición del rol del asistente conversacional y prompts.
   - **Dependencias**: 001, 005, 006.
   - **Estado**: Refinado / Listo para implementación.

8. [008 - Implementation Plan](008-implementation-plan.md)
   - **Propósito**: Roadmap técnico y fases de construcción.
   - **Dependencias**: Todas las anteriores.
   - **Estado**: Refinado / Listo para implementación.

## Estado Global
| Spec | Calidad | Dependencias | Estado |
| :--- | :---: | :--- | :--- |
| 001 - Product | 🟢 | - | Ready |
| 002 - UX | 🟢 | 001 | Ready |
| 003 - Business | 🟢 | 001, 002 | Ready |
| 004 - Data | 🟢 | 003 | Ready |
| 005 - API | 🟢 | 004 | Ready |
| 006 - Recommender | 🟢 | 003, 004 | Ready |
| 007 - LLM | 🟢 | 005, 006 | Ready |
| 008 - Implementation| 🟢 | Todas | Ready |

> [!NOTE]
> Todos los documentos han sido revisados para asegurar consistencia técnica y alineación comercial.
