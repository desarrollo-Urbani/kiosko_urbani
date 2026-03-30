# 001 - Product Spec

## Nombre del producto
Asistente Digital de Sala Urbani

## Visión
Crear un kiosco táctil inteligente para sala de ventas inmobiliaria que ordene la demanda, mejore la experiencia del cliente, capture contexto útil para el ejecutivo y aumente la probabilidad de conversión.

## Problema que resuelve
- tiempos muertos en sala de ventas
- baja captura de intención real del cliente
- perfilamiento inconsistente entre ejecutivos
- poca preparación del ejecutivo antes de atender
- pérdida de oportunidades por fricción
- baja continuidad entre experiencia física y seguimiento comercial

## Propuesta de valor
- entregar número de atención (digital o impreso según terminal), permitiendo que el usuario obtenga su folio y comience el perfilamiento en el mismo flujo o pantalla
- permitir perfilamiento en 30 a 90 segundos, integrado con la toma de número para reducir fricción
- recomendar opciones de propiedades con lógica útil
- generar un resumen ejecutivo accionable para el ejecutivo
- acompañar al usuario con IA sin incomodarlo

## Actores
- **Visitante de sala**: el usuario final que interactúa con el kiosco.
- **Ejecutivo comercial**: recibe el lead con el resumen para atender con contexto.
- **Supervisor comercial**: monitorea el dashboard de leads y carga de atención.
- **Administrador del sistema**: gestiona el stock de propiedades y proyectos.
- **Motor de recomendación**: lógica de backend que filtra stock y calcula match.
- **Asistente conversacional**: capa LLM que guía y asiste al visitante.

## Entradas principales del usuario
1. Sacar número (Turnero)
2. Buscar propiedad (Perfilamiento guiado)
3. Explorar (Navegación libre asistida)

## Objetivos del MVP
- capturar sesiones de kiosco
- emitir tickets de atención (ID único + QR opcional)
- realizar perfilamiento corto (máximo 5 preguntas clave)
- generar recomendaciones iniciales basadas en stock real
- crear lead resumido y derivarlo a un dashboard ejecutivo
- registrar eventos UX y métricas básicas

## No objetivos del MVP
- scoring crediticio real (solo estimaciones basadas en declarativo)
- integración bancaria profunda
- control por voz
- continuidad omnicanal completa (email/SMS de seguimiento fuera de sala)
- personalización avanzada por historial largo de usuario

## KPIs
- sesiones iniciadas vs. completadas
- tickets emitidos
- perfilamientos completados (tasa de conversión del flujo)
- tiempo promedio por pantalla y por sesión total
- leads generados con datos de contacto válidos
- recomendaciones vistas y clicks en detalle
- derivaciones a ejecutivos (leads con resumen enviado)

## Riesgos
- **Abandono**: flujo demasiado largo o complejo.
- **Alucinaciones**: el LLM inventa stock o condiciones comerciales.
- **Stock desactualizado**: recomendar propiedades vendidas.
- **Fricción técnica**: fallas de red o lentitud en el kiosco.

## Supuestos y Clarificaciones
1. El sistema de turnos (Turnero) es digital en el MVP; el "ticket" es una pantalla confirmando el número que también puede enviarse por SMS si el usuario lo solicita.
2. La "derivación al ejecutivo" en el MVP se realiza mediante una actualización en tiempo real en un Dashboard comercial que los ejecutivos tienen abierto en sus estaciones de trabajo.
3. El stock de propiedades se cargará inicialmente de forma estática o vía seed file, no requiere integración API externa en la Fase 1.

## Criterio de éxito
El MVP debe demostrar que puede ordenar la atención, capturar intención comercial y dejar al ejecutivo mejor preparado que en el flujo actual.

