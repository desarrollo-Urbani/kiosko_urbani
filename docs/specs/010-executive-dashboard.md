# 010 - Executive Dashboard (Atencion Cliente)

## URL
- `http://127.0.0.1:8000/executive-dashboard`

## Objetivo
Dashboard operativo para ejecutivos de atencion, enfocado en velocidad y simplicidad para gestionar turnos en sucursal.

## Flujo Principal
1. `Llamar siguiente`
2. `Iniciar atencion`
3. `Finalizar atencion`

## Estados Operativos

### 1. Sin turno
- Muestra: `Sin turno en atencion`
- `Llamar siguiente`: activo
- `Iniciar` y `Finalizar`: no aplican

### 2. Turno llamado
- Muestra datos del turno actual:
  - Numero de turno
  - Nombre cliente (si existe)
  - Tipo de atencion (si existe)
- `Iniciar atencion`: activo
- `Finalizar atencion`: activo
- `Llamar siguiente`: desactivado

### 3. En atencion
- Estado ejecutivo: `En atencion`
- `Finalizar atencion`: activo
- `Llamar siguiente`: desactivado

## Informacion de Cabecera
- Nombre del ejecutivo
- Estado del ejecutivo (`Disponible`, `Turno llamado`, `En atencion`)
- Personas esperando
- Tiempo promedio de espera (min)

## Cola de Espera
Tabla simplificada:
- Turno
- Tiempo esperando (min)
- Perfilado (`Si/No`)

## Integracion Backend
Rutas principales del modulo ejecutivo:
- `GET /api/v1/executive/simple/state`
- `POST /api/v1/executive/simple/call-next`
- `POST /api/v1/executive/simple/start`
- `POST /api/v1/executive/simple/finish`

## Criterios UX
- Interfaz tipo kiosco: botones grandes y claros
- Accion principal dominante: `LLAMAR SIGUIENTE`
- Sin ruido tecnico en pantalla
- Actualizacion periodica para reflejar cambios de cola

## Criterios de Aceptacion
- El ejecutivo puede operar el flujo completo sin salir de la pantalla.
- No se permite llamar nuevo turno si existe uno activo.
- El estado visible refleja correctamente la etapa del turno.
- La cola muestra espera real y estado de perfilado.
