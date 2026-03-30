# Feature: Avatar IA Interactivo y Animado (Urbani)

## Objetivo
Crear un avatar animado e interactivo que funcione como asistente inmobiliario dentro de la plataforma. 
Debe mejorar la experiencia del usuario, reducir fricción en el contacto inicial y guiar el proceso de perfilamiento.

---

## Contexto
El avatar representa un asistente IA que:
- Recibe al usuario en la web
- Inicia conversación
- Apoya el perfilamiento
- Entrega recomendaciones básicas
- Incentiva la conversión (agendar reunión)

Debe integrarse con el flujo del MVP:
- Perfilamiento
- Recomendador
- Dashboard comercial

---

## Requerimientos funcionales

### 1. Componente Avatar
Crear componente React:

- Nombre: `AvatarIA.tsx`
- Props:
  - `state`: "idle" | "greeting" | "thinking" | "suggesting" | "cta"
  - `message`: string
  - `onClickCTA`: function

---

### 2. Estados del Avatar

El avatar debe cambiar visualmente según estado:

- idle:
  - movimiento suave (floating)
  - parpadeo cada 3-5 segundos

- greeting:
  - aparece con animación (fade + scale)
  - muestra mensaje inicial

- thinking:
  - animar puntos (azul, verde, gris) flotando
  - leve movimiento de cabeza

- suggesting:
  - gesto de mano activo
  - highlight visual

- cta:
  - botón visible (ej: "Agendar reunión")

---

### 3. Animaciones

Usar:
- Framer Motion (preferido)
- Alternativa: CSS animations

Animaciones requeridas:
- floating (loop)
- fade-in
- scale-in
- blink (ojos)
- dots loading animation

---

### 4. UI del Chat

Crear componente:
- `AvatarChatBubble.tsx`

Debe incluir:
- mensaje dinámico
- input opcional
- botón CTA

Ejemplo de mensaje:
"Hola, soy tu asesor Urbani 🤖 ¿Te ayudo a encontrar tu hogar ideal?"

---

### 5. Lógica básica

Crear hook:

`useAvatarState.ts`

Reglas:
- al cargar → greeting
- si usuario no interactúa → idle
- si escribe → thinking
- si hay resultado → suggesting
- si está listo → cta

---

### 6. Integración futura (dejar preparado)

- API chatbot (OpenAI / local LLM)
- conexión con CRM
- scoring de leads

---

## Requerimientos técnicos

- Framework: Next.js (App Router)
- Estilo: Tailwind CSS
- Animación: Framer Motion
- Código modular y reusable

---

## Ajustes para Kiosco Vertical

- Resolucion objetivo: `1080x1920` (portrait), equivalente a relacion visual 9:16.
- Medidas de referencia del totem: ancho `729.6 mm`, alto `1951 mm`, area visible aprox `680.4 x 1209.6 mm`.
- Composicion recomendada: 1 columna (avatar + burbuja + acciones), sin panel lateral.
- Regla de burbuja: maximo 2 lineas visibles con elipsis en overflow.
- Mensaje inicial recomendado: "Hola, soy Urbi. Saca tu numero o inicia asesoria guiada."

---

## UX esperado

El avatar debe:
- sentirse cercano (no invasivo)
- ser claro y útil
- guiar sin fricción
- transmitir confianza

---

## Entregables

- componente AvatarIA funcional
- animaciones implementadas
- ejemplo en página `/demo-avatar`
- código limpio y comentado

---

## Bonus (si es posible)

- soporte para voz (Web Speech API)
- modo oscuro
- configuración de personalidad del avatar
