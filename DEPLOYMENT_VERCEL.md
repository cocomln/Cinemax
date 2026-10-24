# Cinemax Vercel & Production Deployment Guide 🚀

Cinemax is designed to deploy on **Vercel** for the Next.js 14 frontend, paired with a persistent free-tier database and scheduled GitHub Actions machine-learning training.

---

## 🔍 Root Cause of the Previous Vercel Failure

**Error Reported**:
> `No Next.js version detected. Make sure your package.json has "next" in either dependencies or devDependencies. Also check your Root Directory setting matches the directory of your package.json file.`

**Why this happened**:
1. When importing a repository into Vercel, Vercel defaults the **Root Directory** to `./` (the repository root).
2. The root of the repository does not contain a `package.json` (the Next.js application lives inside the [`frontend/`](frontend) directory).
3. The previous root `vercel.json` specified `"framework": "nextjs"`. When Vercel evaluated the framework preset on the root directory, it checked `./package.json` for `"next"`, failed to find it, and aborted the deployment during the pre-flight phase before running any build commands.

---

## 🛠️ The Correct Vercel Configuration

The Cinemax frontend must be deployed with **`frontend`** set as its Root Directory:

| Setting | Value | Notes |
| :--- | :--- | :--- |
| **Root Directory** | `frontend` | **Crucial**: Points Vercel directly to `frontend/package.json` |
| **Framework Preset** | `Next.js` | Automatically detected by Vercel from `frontend/package.json` |
| **Build Command** | `next build` (Default) | Native Next.js 14 build command |
| **Output Directory** | `.next` (Default) | Native Next.js 14 build output |
| **Install Command** | `npm install` (Default) | Uses `frontend/package-lock.json` |

---

## 📋 Step-by-Step Vercel Deployment Instructions

### 1. Configure the Frontend on Vercel
1. Log in to [Vercel](https://vercel.com) and go to your dashboard.
2. If already imported:
   - Go to your Cinemax project on Vercel.
   - Navigate to **Settings** -> **General**.
   - Under **Root Directory**, click **Edit**, type `frontend`, and click **Save**.
3. If importing fresh:
   - Click **Add New...** -> **Project**.
   - Select **`cocomln/Cinemax`**.
   - In the configuration screen, click **Edit** next to **Root Directory** and select or type **`frontend`**.
   - Verify that **Framework Preset** displays **Next.js**.
   - Click **Deploy**!

---

## 🌐 Connecting Frontend to Backend in Production

Cinemax uses a dual-routing architecture:

1. **Server-Side API Proxy (`BACKEND_URL`)**:
   - `frontend/next.config.js` is pre-configured with rewrites: any request to `/api/*` on your Vercel domain is automatically proxied to `process.env.BACKEND_URL`.
   - This eliminates browser CORS complications and avoids exposing raw backend URLs.
2. **Direct Browser API (`NEXT_PUBLIC_API_URL`)**:
   - `frontend/src/lib/api.ts` automatically normalizes `NEXT_PUBLIC_API_URL` to target `/api` correctly if provided.
   - If unset, browser requests fall back to `/api` (proxied by Next.js).

### Environment Variables on Vercel

In your Vercel Project Dashboard (**Settings** -> **Environment Variables**), add:

| Variable Name | Required | Description | Example |
| :--- | :--- | :--- | :--- |
| `BACKEND_URL` | Yes (in prod) | Base URL of your FastAPI backend service | `https://cinemax-api.onrender.com` |
| `NEXT_PUBLIC_API_URL` | Optional | Direct public API URL (if not using rewrite proxy) | `https://cinemax-api.onrender.com/api` |

---

## ⚙️ Backend Hosting Options (100% Free Tier)

FastAPI requires an ASGI server (Uvicorn) and connects to the shared database. Vercel serverless functions have specific constraints:
- Ephemeral filesystem: Local SQLite databases are wiped on cold restarts.
- Short timeouts (10 seconds on Vercel Hobby): Batch calculations and model training cannot run serverless.
- Lifespan connections: Creating connection pools on every cold start can exhaust database limits.

Therefore, Cinemax recommends one of the following free-tier backend setups:

### Option A: Render.com Free Web Service (Recommended)
1. Go to [render.com](https://render.com) and create a free account.
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository: `cocomln/Cinemax`.
4. Configure:
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `DATABASE_URL`: Your cloud PostgreSQL connection string (from Neon or Supabase).
5. Click **Create Web Service**. Render provides a permanent free HTTPS URL (e.g. `https://cinemax-api.onrender.com`).
6. Set `BACKEND_URL=https://cinemax-api.onrender.com` in your Vercel project settings!

### Option B: Koyeb / Fly.io / Docker
Cinemax includes a production [`docker-compose.yml`](docker-compose.yml) and Dockerfiles for one-click deployment on any container platform.

---

## 🗄️ Free Persistent Cloud Database Setup

To share data between the Vercel frontend, backend, and nightly GitHub Actions runners:

1. Create a free PostgreSQL database at [Neon.tech](https://neon.tech) (recommended: serverless Postgres, zero cost, no card required).
2. Copy your connection string:
   `postgresql://[user]:[password]@[host]/[dbname]?sslmode=require`
3. Add `DATABASE_URL` to:
   - **Render / Backend Service**: In backend environment variables.
   - **GitHub Repository Secrets**: Under **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret** (`DATABASE_URL`).
   - The nightly GitHub Actions pipeline (`.github/workflows/daily-update.yml`) runs at **12:00 AM IST (18:30 UTC)** to refresh the database with fresh data and trained ML models.

---

## 🧪 Verification Checklist

Once deployed:
1. **Frontend Home**: Visit your `https://*.vercel.app` domain. The UI should load with measured popularity rankings and 7-day ML forecasts.
2. **Catalog Explorer**: Navigate to `/explore`. Search and filter by genre, year (1995–present), and media type.
3. **Data Provenance**: Navigate to `/sources`. Inspect the transparency registry for AniList, TVmaze, Wikidata, and TMDB.
4. **Prediction Arena**: Navigate to `/arena`. Select a title and lock in a 7-day popularity forecast guess.
