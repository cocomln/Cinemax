# Cinemax 🎬

A free, zero-cost, data-driven entertainment intelligence platform for **movies**, **television series**, and **anime**. Cinemax tracks public attention, multi-source ratings, discussion trends, historical performance, and forecasts 7-day future popularity using local machine learning.

![Cinemax Architecture Banner](https://img.shields.io/badge/Status-Operational-brightgreen)
![Budget](https://img.shields.io/badge/Budget-Zero--Cost%20%240.00-blue)
![Scheduled Refresh](https://img.shields.io/badge/Scheduled%20Refresh-12%3A00%20AM%20IST-purple)
![License](https://img.shields.io/badge/License-MIT-orange)

---

## 🌟 Core Features

- **Multi-Category Coverage**: High-integrity historical catalog from **January 1, 1995** through upcoming announced releases covering movies, television series, and anime (films, series, OVAs, ONAs, specials).
- **Multi-Source Credibility & Provenance**: Displays genuine ratings with direct links, vote counts, scale, and clear distinction between **audience** vs. **critic** reviews (AniList, TVmaze, Wikidata CC0, IMDb, Metacritic, TMDB). Ratings from different providers are never combined or fabricated.
- **TV & Anime Episode Provenance**: Tracks announced, released, known total, and estimated episodes. Distinguishes unknown episode counts without defaulting to zero.
- **Transparent Popularity Scoring (0 to 100)**: Measures audience attention and discussion volume (not artistic quality) using a documented formula:
  - **30%** Recent Discussion Volume (Log-scaled)
  - **25%** Mention Growth Velocity (% change from prior window)
  - **20%** Discussion Engagement (likes/comments ratio)
  - **15%** Cross-Source Breadth (number of active sources)
  - **10%** Sustained Historical Baseline
- **Local Machine Learning Forecasts**: Local `scikit-learn` models project 7-day popularity score changes, complete with uncertainty intervals, model versioning, and top contributing drivers.
- **Cinemax Prediction Arena**: Interactive guessing game where users predict a title's 7-day popularity, lock in guesses, and compete on the accuracy leaderboard.
- **Midnight Automatic Refresh**: Automated ingestion pipeline scheduled at **12:00 AM IST (18:30 UTC)** with idempotent database upserts, historical snapshots, and manual `workflow_dispatch` support.
- **Source Registry Dashboard**: Complete transparency into all 7 data adapters, their legal terms, licenses, rate limits, access methods, and operational health.

---

## 🛠️ Technology Stack

- **Frontend**: Next.js 14 (React, TypeScript, App Router)
- **Styling**: Tailwind CSS with dark slate cinema theme
- **Backend**: Python 3.12+ with FastAPI & Pydantic V2
- **Database**: SQLite (default local zero-cost) / PostgreSQL compatible via SQLAlchemy 2.0
- **Data Science & ML**: `pandas`, `numpy`, `scikit-learn` (Ridge & Random Forest Regressors)
- **Sentiment Engine**: Local zero-cost lexicon-based analyzer (no paid LLM calls)
- **Testing**: `pytest` (backend) & Next.js production type-checking
- **DevOps**: GitHub Actions (`daily-update.yml` and `ci.yml`), Docker & Docker Compose

---

## 🚀 Quickstart Guide

### Option 1: Native Local Development (No Docker Required)

#### 1. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run initial ingestion and populate database
python run_initial_ingest.py

# Run test suite
pytest tests/ -v

# Start FastAPI server on port 8000
python main.py
```
FastAPI documentation will be live at: `http://localhost:8000/docs`

#### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Open `http://localhost:3000` in your browser.

---

### Option 2: Docker Compose Setup
```bash
# Build and run backend and frontend simultaneously
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

---

## 🔒 Zero-Cost & Data Integrity Policy

Cinemax operates strictly under non-negotiable zero-cost and data integrity constraints:
1. **Never Fabricate Data**: Titles, ratings, vote counts, and episode numbers are sourced with traceable provenance. Missing data is displayed as "Data unavailable" or "Insufficient data" rather than invented facts.
2. **Zero Operating Cost**: No paid APIs, no paid AI/LLM models, and no subscriptions.
3. **Local Machine Learning**: All predictions and sentiment analyses run locally without external paid model APIs.
4. **Resilient Failure Handling**: If an optional provider (e.g., Reddit or X) lacks credentials, Cinemax marks the source as degraded or disabled while keeping all independent features fully operational.

---

## 📜 Data Providers & Legal Attributions

| Provider | Type | Access Method | Cost Status | License & Terms |
| :--- | :--- | :--- | :--- | :--- |
| **AniList** | Anime Catalog & Ratings | GraphQL API | Zero-Cost (Free) | [AniList Terms](https://anilist.co/terms) |
| **TVmaze** | Television & Episodes | REST API | Zero-Cost (Free) | [CC BY-SA 4.0](https://www.tvmaze.com/api) |
| **Wikidata** | Cinema & Cross-References | SPARQL Endpoint | Zero-Cost (Free) | [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) |
| **Kaggle Importer** | Historical Datasets | Local Files & CLI | Zero-Cost (Free) | [Kaggle Terms](https://www.kaggle.com/terms) |
| **TMDB** | Ratings & Media | REST API v3 | Free Non-Commercial | [TMDB Terms](https://www.themoviedb.org/terms-of-use) |
| **Reddit** | Social Discussions | Public Search API | Free Tier Etiquette | [Reddit Data Terms](https://www.redditinc.com/policies/data-api-terms) |
| **X** | Social Velocity | API v2 Interface | Verified Free Tier | [Developer Terms](https://developer.x.com/en/developer-terms) |

---

## 🕒 Midnight Refresh Pipeline

The automated ingestion pipeline is scheduled to execute daily at:
- **12:00 AM IST (Asia/Kolkata)**
- **18:30 UTC** (calculated corresponding UTC schedule)

Workflow file: [`.github/workflows/daily-update.yml`](.github/workflows/daily-update.yml)

The pipeline performs:
1. Configuration and provider verification.
2. Catalog updates from AniList, TVmaze, and Wikidata.
3. Multi-source deduplication and cross-reference reconciliation.
4. Calculation of 0–100 Popularity Scores.
5. Recording of immutable daily time-series historical observations.
6. Re-training of local 7-day popularity prediction models.
7. Resolution of due Cinemax Prediction Arena user guesses.

---

## 📄 License

Cinemax is licensed under the [MIT License](LICENSE).
