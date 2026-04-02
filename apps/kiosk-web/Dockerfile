# ── Etapa 1: build con Node ──────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts

COPY app/ ./app/
COPY vite.config.ts tsconfig.json* ./

# En producción el frontend habla con nginx (mismo dominio), no necesita proxy
# La variable VITE_API_BASE se puede sobrescribir en build time si se necesita
RUN npm run build

# ── Etapa 2: servir con nginx ─────────────────────────────
FROM nginx:1.25-alpine

COPY --from=builder /app/dist /usr/share/nginx/html

# La config de nginx viene del orquestador (docker-compose monta nginx.conf)
# Exponemos 80; nginx arriba hace proxy a la API
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
