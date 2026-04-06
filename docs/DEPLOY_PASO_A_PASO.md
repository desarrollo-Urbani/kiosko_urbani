# Deploy Paso a Paso (Urbani Kiosko)

Guia corta para dejar el sistema funcionando con costo 0 (modo demo):

- Front (portada + kiosko): Vercel
- API + dashboards: Render
- Base de datos Postgres: Supabase

## 1) Preparar y subir codigo a GitHub

En la carpeta del proyecto:

```powershell
cd c:\proyectos\urbani-kiosco
git status
git add .
git commit -m "chore: deploy prep"
git push origin master
```

Si da `403` en push:

- Verificar acceso al repo en GitHub (colaborador con write)
- Aceptar invitacion en notificaciones
- Limpiar credencial cacheada en Windows:

```powershell
cmdkey /delete:git:https://github.com
git push -u origin master
```

## 2) Crear base de datos en Supabase

1. Crear proyecto en Supabase.
2. Ir a `Project Settings -> Database -> Connection pooling` (NO usar la Direct Connection).
3. Copiar la URL del **pooler en Session mode (puerto 5432)**. Tiene este formato:

```text
postgresql+psycopg2://postgres.[ref]:[PASSWORD]@aws-0-[region].pooler.supabase.com:5432/postgres?sslmode=require
```

> **IMPORTANTE para Render free tier**: La conexion directa (`db.[ref].supabase.co:5432`) resuelve a IPv6,
> que Render no soporta. Siempre usar la URL del pooler (resolves a IPv4).
> Usar Session mode (puerto 5432), no Transaction mode (6543), porque Alembic requiere DDL support.

## 3) Deploy API en Render (Web Service)

Crear `New Web Service` con repo `desarrollo-Urbani/kiosko_urbani`.

Config:

- Branch: `master`
- Root Directory: `apps/api`
- Build Command: `pip install -r requirements.txt`
- Start Command:

```text
alembic upgrade head && gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --workers 2 --bind 0.0.0.0:$PORT --timeout 120 --keep-alive 5 --access-logfile -
```

Variables de entorno minimas:

- `APP_ENV=production`
- `DEBUG=false`
- `DATABASE_URL=<tu_url_supabase_pooler>`
- `KIOSK_TOKEN=dev-kiosk-token`
- `PYTHON_VERSION=3.12.8`
- `CORS_ALLOW_ORIGINS=https://kiosko-urbani-api.onrender.com,https://kiosko-urbani.vercel.app`
- `SUPERVISOR_EMAILS=correo1@empresa.cl,correo2@empresa.cl`  ← emails con rol supervisor
- `ADMIN_EMAILS=admin@empresa.cl`  ← opcional, rol admin (tiene acceso supervisor tambien)

Notas:

- Si Render muestra Python `3.14.x`, forzar `PYTHON_VERSION=3.12.8`.
- En este repo ya existe `.python-version` con `3.12.8`.

## 4) Deploy Front en Vercel

Crear proyecto en Vercel desde el mismo repo.

Config:

- Framework: `Vite`
- Root Directory: `apps/kiosk-web`
- Build Command: `npm ci && npm run build`
- Output Directory: `dist`

Env vars:

- `VITE_API_BASE=https://kiosko-urbani-api.onrender.com/api/v1`

Luego hacer deploy.

## 5) URLs esperadas

- API health: `https://kiosko-urbani-api.onrender.com/health`
- API docs: `https://kiosko-urbani-api.onrender.com/docs`
- Ejecutivo: `https://kiosko-urbani-api.onrender.com/executive-dashboard`
- Supervisor: `https://kiosko-urbani-api.onrender.com/supervisor-dashboard`
- Portada/Kiosko: `https://kiosko-urbani.vercel.app`

## 6) Validacion funcional end-to-end

1. Abrir portada en Vercel.
2. Click en `Abrir Kiosko` (abre nueva pestana) y tomar numero.
3. Abrir `Dashboard Ejecutivo` y llamar/iniciar atencion.
4. Abrir `Dashboard Supervisor` y revisar cola/tiempos.
5. Confirmar que los datos se reflejan entre pantallas.

## 7) Problemas comunes y solucion rapida

### Error en Vercel: `Unexpected token ... package.json`

Causa: BOM en `package.json`.
Solucion: guardar archivo UTF-8 sin BOM y redeploy.

### Render build falla con `pydantic-core` + Rust

Causa: Python 3.14.
Solucion: usar Python 3.12.8 (`PYTHON_VERSION=3.12.8`) y redeploy.

### Kiosko abre pero dashboards sin datos

Causa: API caida o CORS mal configurado.
Solucion:

- Verificar `/health`
- Corregir `CORS_ALLOW_ORIGINS`
- Redeploy API en Render

## 8) Seguridad (importante)

Si una clave se compartio por chat, rotarla:

1. Cambiar password en Supabase.
2. Actualizar `DATABASE_URL` en Render.
3. Redeploy API.

---

Ultimo tip:
- Mantener todo en `master` hasta estabilizar.
- Cuando quede estable, crear rama `main` o `release` para produccion.
