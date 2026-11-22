# Namma AI — Deployment Guide (Vercel & Render)

This repository contains a full-stack civic complaint and outcome-verification system:
- **Frontend**: Next.js 14 App Router, React 18, Tailwind CSS (optimized for **Vercel**)
- **Backend**: FastAPI, SQLAlchemy, Pydantic, Uvicorn/Gunicorn (optimized for **Render**)

---

## 1. Quick Architecture Overview

```
┌─────────────────────────────────┐           ┌─────────────────────────────────┐
│       Frontend (Vercel)         │           │        Backend (Render)         │
│     Next.js 14 App Router       │           │        FastAPI + Uvicorn        │
│   https://<app>.vercel.app      │ ──REST──> │   https://<app>.onrender.com    │
└─────────────────────────────────┘           └────────────────┬────────────────┘
                                                               │
                                                               ▼
                                              ┌─────────────────────────────────┐
                                              │       Database / Storage        │
                                              │   PostgreSQL (Supabase/Render)  │
                                              │    or Local SQLite Fallback     │
                                              └─────────────────────────────────┘
```

---

## 2. Deploying Backend on Render

You can deploy the backend using either **Render Blueprints (1-Click)** or **Manual Web Service**.

### Method A: Using Render Blueprint (`render.yaml` - Recommended)
1. Push this repository to your GitHub account.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **"New"** > **"Blueprint"**.
4. Select your `namma_ai` repository.
5. Render will detect `render.yaml` and pre-configure:
   - **Service Name**: `namma-ai-backend`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
6. Click **"Apply"**.
7. Once deployed, copy your backend URL (e.g. `https://namma-ai-backend.onrender.com`).

### Method B: Manual Web Service Setup on Render
1. In Render Dashboard, click **"New"** > **"Web Service"**.
2. Connect your GitHub repository.
3. Configure the following fields:
   - **Name**: `namma-ai-backend`
   - **Region**: Any region close to your users (e.g. `Oregon` or `Singapore`)
   - **Branch**: `main`
   - **Root Directory**: leave blank (or `.`)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. In **Environment Variables**, add:
   | Key | Value | Description |
   |-----|-------|-------------|
   | `PYTHON_VERSION` | `3.11.7` | Python runtime version |
   | `ENVIRONMENT` | `production` | Deployment mode |
   | `PORT` | `10000` | Port assigned by Render |
   | `CORS_ORIGINS` | `*` | Or comma-separated list of your Vercel domains |
   | `CORS_ORIGIN_REGEX` | `https://.*\.vercel\.app` | Permits all Vercel preview & production deployments |
   | `DATABASE_URL` | `postgresql://...` (or leave default for SQLite) | Connection string for Postgres/Supabase |
   | `STORAGE_PROVIDER` | `local` (or `supabase`) | Evidence file storage |
   | `LLM_PROVIDER` | `mock` (or `gemini` / `openai`) | AI provider |
   | `LLM_API_KEY` | *(optional)* | API key if using Gemini or OpenAI |
   | `SECRET_KEY` | *(generate random string)* | Used for JWT authentication |
5. Click **"Create Web Service"**.

---

## 3. Deploying Frontend on Vercel

### Method A: Via Vercel Dashboard (Recommended)
1. Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **"Add New..."** > **"Project"**.
2. Import your GitHub repository (`namma_ai`).
3. In the **Configure Project** screen:
   - **Project Name**: `namma-ai-frontend` (or your choice)
   - **Framework Preset**: `Next.js`
   - **Root Directory**: Click **Edit** and select **`frontend`**
   - Build and Output settings will automatically populate (`npm run build` and `.next`)
4. Expand **Environment Variables** and add:
   | Key | Value |
   |-----|-------|
   | `NEXT_PUBLIC_API_BASE_URL` | `https://<your-render-backend-url>/api` |
5. Click **"Deploy"**.
6. Vercel will build and deploy your Next.js frontend in ~1 minute.

### Method B: Via Vercel CLI
```bash
# Install Vercel CLI if not already installed
npm install -g vercel

# Deploy from frontend folder
cd frontend
vercel

# For production deployment
vercel --prod
```
When prompted for environment variables, provide `NEXT_PUBLIC_API_BASE_URL=https://<your-render-backend-url>/api`.

---

## 4. Connecting Frontend & Backend

1. **Copy Render URL**: Get your live backend URL from Render (e.g. `https://namma-ai-backend.onrender.com`).
2. **Set Frontend API Base**: In Vercel Project Settings > **Environment Variables**:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://namma-ai-backend.onrender.com/api
   ```
   *(Trigger a Redeploy in Vercel to pick up new env vars).*
3. **Allow CORS on Render**: Ensure Render's `CORS_ORIGIN_REGEX` is set to `https://.*\.vercel\.app` (default in `render.yaml`) so Vercel can seamlessly make API requests.

---

## 5. Verification & Health Checks

Once deployed, verify the system:

1. **Backend Health Check**:
   Visit `https://<your-render-backend-url>/health` in browser:
   ```json
   {
     "status": "healthy",
     "app_name": "Namma AI",
     "version": "1.0.0",
     "environment": "production",
     "database": "connected"
   }
   ```
2. **Interactive API Documentation**:
   Visit `https://<your-render-backend-url>/docs` to view Swagger UI.
3. **Frontend Dashboard**:
   Visit `https://<your-vercel-domain>.vercel.app/dashboard` to verify live stats and map markers.
4. **Submit a Test Complaint**:
   Visit `https://<your-vercel-domain>.vercel.app/report` to file a sample report and verify end-to-end connectivity.
