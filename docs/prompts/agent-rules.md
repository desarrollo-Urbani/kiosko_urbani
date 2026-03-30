# Reglas permanentes para el agente

Trabaja con metodología **spec-driven**.

## Reglas obligatorias
- primero leer las specs antes de tocar código
- no inventar funcionalidades fuera del MVP
- no cambiar arquitectura sin documentar decisión en `docs/decisions`
- no borrar archivos sin justificación
- siempre entregar código completo y ejecutable
- siempre actualizar README y docs afectadas
- separar estrictamente UI, lógica de negocio y capa LLM
- priorizar claridad, modularidad y velocidad
- si hay ambigüedad, documentar supuestos en vez de improvisar silenciosamente

## Principios del proyecto
- 1 pantalla = 1 decisión
- máximo 5 preguntas en el MVP
- el LLM acompaña, no decide la lógica de negocio
- nunca bloquear el flujo por falta de datos
- la recomendación inicial debe ser explicable
