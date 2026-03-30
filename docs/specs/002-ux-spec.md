# 002 - UX Spec

## Formato y Entorno
- **Dispositivo Target**: Kiosco tipo totem con pantalla táctil de 42"+.
- **Orientación**: Portrait (Vertical) 1080x1920.
- **Entorno**: Sala de ventas con iluminación controlada.
- **Interacción**: Touch (multitouch no obligatorio, pero targets grandes son críticos).

## Principios UX
- **1 pantalla = 1 decisión**: Evitar abrumar al usuario con múltiples inputs simultáneos.
- **Blancos generosos**: Diseño aireado para permitir lectura a distancia.
- **Máximo 3 opciones grandes** por pantalla (ej. Comprar, Invertir, Explorar).
- **Máximo 5 preguntas** en flujo de perfilamiento para evitar fatiga.
- **Siempre permitir avanzar**: El botón de "Siguiente" o "Ver resultados" debe estar siempre accesible si hay datos mínimos.
- **Voz de Bot visible pero secundaria**: El bot reside en el borde de la pantalla (ej. esquina inferior derecha) y ofrece ayuda contextual.

## Tono Visual
- **Paleta**: Gris espacial, Negro profundo, acentos en cyan o oro (premium).
- **Tipografía**: Sans-serif moderna (Inter o similar), tamaño de fuente grande (base 24px+).
- **Componentes**: Glassmorphism sutil en tarjetas y contenedores.
- **Micro-interacciones**: Feedback visual inmediato al tocar un botón.

## Flujo de Pantallas MVP
1.  **Home / Protector de Pantalla**: Llamada a la acción "Toca para comenzar".
2.  **Identificación Inicial**: ¿Vienes a ver a alguien o quieres información?
3.  **Toma de número y perfilamiento**: El usuario puede obtener su número de atención (folio) e inmediatamente comenzar a responder las preguntas de perfilamiento en la misma pantalla o flujo, viendo su folio y tiempo estimado mientras responde.
4.  **Perfilamiento - Tipo**: Departamento, Casa, Oficina (si no se integró en la pantalla anterior).
5.  **Perfilamiento - Objetivo**: Vivir, Invertir (si no se integró en la pantalla anterior).
6.  **Perfilamiento - Zona**: Filtro por comunas/sectores predefinidos.
7.  **Perfilamiento - Presupuesto**: Rango de precio (UF) o Dividendo estimado.
8.  **Perfilamiento - Subsidio**: DS19, DS01 o No aplica.
9.  **Resultados / Vitrina**: Carrusel de 3 a 5 propiedades "Match".
10. **Detalle Propiedad**: Info clave, fotos, mapa de ubicación.
11. **Finalización / Derivación**: Pantalla de "Gracias, el ejecutivo X te llamará en unos minutos".

## Bot Animado
- **Animaciones**: Idle (respiración sutil), Thinking (procesando), Happy (éxito).
- **Contexto**: Burbujas de texto cortas (máx 140 caracteres).
- **Interacción**: Se puede "tocar" al bot para que reformule la pregunta si el usuario no entiende.

## Estados de Sistema
- **Cargando**: Skeleton screens elegantes en vez de spinners genéricos.
- **Sin resultados**: Ofrecer "Relajar filtros" o "Ver todos los proyectos".
- **Timeout / Inactividad**: Aviso de "Sigues ahí?" tras 60s de inactividad, cierre de sesión a los 90s.
- **Error**: mensaje amigable "Estamos ajustando los últimos detalles, por favor pide asistencia a un ejecutivo".

