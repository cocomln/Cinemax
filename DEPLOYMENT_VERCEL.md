# Cinemax Vercel & Cloud Deployment Guide 🚀

Cinemax is pre-configured to deploy seamlessly on **Vercel** with **zero cost**, hosting both the **Next.js frontend** and the **FastAPI serverless backend** under a single free `*.vercel.app` domain.

---

## Architecture on Vercel

```
                                    +------------------------------+
                                    |         VERCEL CLOUD         |
                                    |  https://*.vercel.app        |
                                    |                              |
  User Browser ───────────────────> |  - Next.js 14 Frontend       |
                                    |  - FastAPI (api/index.py)    |
                                    +--------------+---------------+
                                                   |
                                                   | DATABASE_URL (Cloud PostgreSQL)
                                                   v
+--------------------------------+  +------------------------------+
|     GITHUB ACTIONS (Nightly)   |  |   FREE CLOUD POSTGRESQL      |
|  - Ingestion (AniList/TVmaze)  |─>|   (Neon / Supabase / Render) |
|  - Popularity Scoring (0-100)  |  |   Shared Persistent Storage  |
|  - Scikit-Learn Model Training |  +------------------------------+
+--------------------------------+
```

---

## 1. Deploy Frontend & FastAPI to Vercel (2 Minutes)

1. Go to [vercel.com/new](https://vercel.com/new) and log in with your GitHub account.
2. Under **Import Git Repository**, select **`cocomln/Cinemax`**.
3. In the configuration screen:
   - **Framework Preset**: Next.js (automatically detected)
   - **Root Directory**: `./` (leave default)
   - Click **Deploy**!
4. Vercel will build the Next.js pages and provision the FastAPI serverless functions in `api/index.py`.
5. Your platform is now publicly live at a free HTTPS domain, e.g.:
   `https://cinemax-cocomln.vercel.app`

---

## 2. Configure a Free Persistent Database (Zero-Cost)

To share data between the Vercel web app and the nightly GitHub Actions ingestion pipeline:

### Step A: Create a Free PostgreSQL Database
You can use any free managed PostgreSQL provider (no credit card required):
- **Neon** ([neon.tech](https://neon.tech)) — Recommended: Generous free serverless tier.
- **Supabase** ([supabase.com](https://supabase.com)) — Free tier with 500MB storage.
- **Render** ([render.com](https://render.com)) — Free PostgreSQL instance.

Copy your connection string, which looks like:
`postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require`

### Step B: Add `DATABASE_URL` to Vercel
1. In your Vercel project dashboard, go to **Settings** -> **Environment Variables**.
2. Add a new variable:
   - **Key**: `DATABASE_URL`
   - **Value**: `postgresql://...` (your connection string from Step A)
3. Click **Save** and trigger a redeploy.

### Step C: Add `DATABASE_URL` to GitHub Secrets
1. In your GitHub repository at [https://github.com/cocomln/Cinemax](https://github.com/cocomln/Cinemax).
2. Go to **Settings** -> **Secrets and variables** -> **Actions**.
3. Click **New repository secret**:
   - **Name**: `DATABASE_URL`
   - **Secret**: `postgresql://...` (the same connection string)
4. Click **Add secret**.

---

## 3. Nightly Ingestion & Heavy ML Training

The scheduled pipeline in [`.github/workflows/daily-update.yml`](.github/workflows/daily-update.yml) runs automatically every night at **12:00 AM IST (18:30 UTC)**:
- Connects to your persistent cloud PostgreSQL database via `secrets.DATABASE_URL`.
- Pulls fresh metadata from AniList, TVmaze, and Wikidata CC0.
- Runs deduplication and updates ratings.
- Computes the 0–100 Popularity Scores.
- Trains the local `scikit-learn` prediction model without serverless execution limits.
- Evaluates completed Prediction Arena user guesses.
- Updates the database so the Vercel web app immediately reflects the latest data every morning.

You can also trigger it manually anytime via GitHub Actions:
👉 Go to **Actions** -> **Cinemax Daily Midnight Refresh Pipeline** -> **Run workflow**.

---

## 4. Zero-Cost Integrity Verification

- **Total Mandatory Cost**: $0.00
- **Frontend & Serverless API**: Vercel Free Hobby Tier
- **Scheduled ML Pipeline**: GitHub Actions Free Public Runner Minutes
- **Data Ingestion**: AniList, TVmaze, and Wikidata (all free public endpoints)
- **Database**: Free Serverless Postgres (Neon / Supabase) or local SQLite fallback
