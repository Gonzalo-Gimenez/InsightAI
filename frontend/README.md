# InsightAI frontend

Next.js 15 (App Router), React 19, TypeScript y Tailwind CSS v4.

## Requisitos

- Node.js 22+
- Backend FastAPI en **http://127.0.0.1:8000** (obligatorio para métricas y chat)

En desarrollo, `next.config.ts` reescribe `/api/*` hacia `http://127.0.0.1:8000/api/*`.

## Desarrollo (PowerShell)

```powershell
cd frontend
npm install
npm run dev
```

Abrí http://127.0.0.1:3000 (Next usa el puerto 3000 por defecto).

## Build de producción

```powershell
npm run build
npm start
```

## Estructura

- `app/` layout y página (shell estático en Server Components)
- `components/` chat, métricas, gráfico 3D (Client Components)
- `lib/api.ts` tipos y llamadas a `/api/v1/metrics` y `/api/v1/chat`
