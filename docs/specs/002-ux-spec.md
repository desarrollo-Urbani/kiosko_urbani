# 002 - UX Spec

## Formato y Entorno
- **Dispositivo target**: Kiosco tipo totem con pantalla tactil de 42"+.
- **Orientacion**: Portrait (vertical).
- **Resolucion base de diseno**: 1080x1920 (FHD vertical), con escalado responsivo hacia abajo.
- **Medidas del gabinete (referencia)**: ancho aprox 729.6 mm, alto aprox 1951 mm, fondo aprox 450 mm.
- **Area visible de pantalla (referencia)**: ancho aprox 680.4 mm y alto aprox 1209.6 mm (proporcion cercana a 9:16).
- **Entorno**: Sala de ventas con iluminacion controlada.
- **Interaccion**: Touch (multitouch no obligatorio, pero targets grandes son criticos).

## Principios UX
- **1 pantalla = 1 decision**: Evitar abrumar al usuario con multiples inputs simultaneos.
- **Layout principal en 1 columna**: Avatar + mensaje + acciones apiladas verticalmente para priorizar legibilidad en totem vertical.
- **Blancos generosos**: Diseno aireado para permitir lectura a distancia.
- **Maximo 3 opciones grandes** por pantalla (ej. Comprar, Invertir, Explorar).
- **Maximo 5 preguntas** en flujo de perfilamiento para evitar fatiga.
- **Siempre permitir avanzar**: El boton de "Siguiente" o "Ver resultados" debe estar siempre accesible si hay datos minimos.
- **Voz de bot visible pero secundaria**: El bot reside en el borde de la pantalla y ofrece ayuda contextual.

## Tono Visual
- **Paleta**: Gris espacial, negro profundo, acentos en cyan o dorado premium.
- **Tipografia**: Sans-serif moderna, tamano de fuente grande (base 24px+).
- **Componentes**: Glassmorphism sutil en tarjetas y contenedores.
- **Micro-interacciones**: Feedback visual inmediato al tocar un boton.

## Flujo de Pantallas MVP
1. **Home / Protector de Pantalla**: Llamada a la accion "Toca para comenzar".
2. **Identificacion Inicial**: El visitante indica si viene por atencion o por informacion.
3. **Toma de numero y perfilamiento**: El usuario obtiene su folio y puede iniciar perfilamiento en el mismo flujo, viendo su tiempo estimado.
4. **Perfilamiento - Tipo**: Departamento, Casa, Oficina (si no se integro antes).
5. **Perfilamiento - Objetivo**: Vivir, Invertir (si no se integro antes).
6. **Perfilamiento - Zona**: Filtro por comunas/sectores predefinidos.
7. **Perfilamiento - Presupuesto**: Rango de precio (UF) o dividendo estimado.
8. **Perfilamiento - Subsidio**: DS19, DS01 o No aplica.
9. **Resultados / Vitrina**: Carrusel de 3 a 5 propiedades con mejor match.
10. **Detalle Propiedad**: Informacion clave, fotos, mapa.
11. **Finalizacion / Derivacion**: Pantalla de cierre y aviso de atencion por ejecutivo.

## Bot Animado
- **Animaciones**: Idle (respiracion sutil), Thinking (procesando), Happy (exito).
- **Contexto**: Burbujas de texto cortas. Objetivo para saludo inicial: <= 70 caracteres.
- **Regla visual de burbuja**: maximo 2 lineas, con elipsis en overflow.
- **Mensaje inicial recomendado**: "Hola, soy Urbi. Saca tu numero o inicia asesoria guiada."
- **Interaccion**: Se puede tocar al bot para reformular la pregunta.

## Estados de Sistema
- **Cargando**: Skeleton screens elegantes en vez de spinners genericos.
- **Sin resultados**: Ofrecer "Relajar filtros" o "Ver todos los proyectos".
- **Timeout / Inactividad**: Aviso de continuidad tras 60s de inactividad, cierre de sesion a los 90s.
- **Error**: Mensaje amigable y derivacion a apoyo de ejecutivo.
