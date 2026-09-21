# Deploy InsightAI (demo)

## Backend (Render)

1. Push this repo to `Gonzalo-Gimenez/InsightAI` on GitHub.
2. In [Render](https://render.com), **New → Blueprint** and point at the repo (`render.yaml`).
3. Set **GROQ_API_KEY** when prompted (never commit it).
4. Set **CORS_ORIGINS** to your Vercel frontend URL(s), comma-separated, e.g.  
   `https://insightai.vercel.app,https://insightai-*.vercel.app`
5. After deploy, note the API URL (e.g. `https://insightai-api.onrender.com`). Run `/health` to confirm (`database: up`).

The container seeds the Nortec warehouse on first boot when `DATABASE_URL` is set (`python -m scripts.seed_nortec`). Later deploys skip seed if `fact_ventas` already has rows.

**Cold start:** on Render free tier the API may sleep; the first request after idle can take 30–60s before chat/metrics respond.

## Frontend (Vercel)

1. **Import** the same GitHub repo in Vercel.
2. Set **Root Directory** to `frontend`.
3. Environment variable: `NEXT_PUBLIC_API_URL` = your Render API URL (no trailing slash).
4. Deploy. Open the site and ask: *¿Cuál es el total de ventas?* — the answer must match the seeded demo DB (see `/api/v1/metrics` → `total_ventas`). The chat panel shows which tools ran.

## Portfolio links

Update `Portfolio/lib/projects.ts`:

- `repoUrl`: `https://github.com/Gonzalo-Gimenez/InsightAI`
- `demoUrl`: your Vercel frontend URL
