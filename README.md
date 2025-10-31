# Firenail

> AI-assisted thumbnail studio that turns any YouTube URL into a polished, on-brand cover by blending transcript understanding with Firecrawl-sourced visual inspiration.

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
  - [Pipeline Walkthrough](#pipeline-walkthrough)
  - [Backend Services](#backend-services)
  - [Frontend Experience](#frontend-experience)
  - [External Integrations](#external-integrations)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Run with Docker](#run-with-docker)
  - [Manual Setup](#manual-setup)
- [Database & Migrations](#database--migrations)
- [Supabase Setup](#supabase-setup)
- [Polar Billing Setup](#polar-billing-setup)
- [API Reference](#api-reference)
- [Realtime Events](#realtime-events)
- [Troubleshooting](#troubleshooting)
- [Additional Resources](#additional-resources)

## Overview
Firenail is a full-stack product designed to automate thumbnail production for YouTube creators. Paste a video URL, and the system:
1. Fetches transcripts and metadata from YouTube.
2. Summarises the content using Groq-hosted LLMs.
3. Mines Firecrawl for inspiration images that match the narrative.
4. Crafts a cohesive thumbnail via Freepik's image generation API.
5. Stores the artwork in Supabase while streaming progress updates to the UI through realtime channels.

The codebase is split into a FastAPI + Celery backend (`backend/`) and a Next.js 15 frontend (`frontend/`) that meet in the middle through authenticated Supabase sessions and REST APIs.

## Key Features
- Transcript-driven creative direction with structured prompts in `backend/app/constants/prompts.py`.
- Background Celery pipeline (`backend/app/celery/tasks/video_pipeline.py`) that orchestrates metadata, analysis, crawling, and generation stages.
- Firecrawl-powered reference harvesting (`backend/app/services/crawl.py`) with retry-aware HTTP sessions.
- Freepik thumbnail synthesis and Supabase storage uploads (`backend/app/services/image_generation.py`, `backend/app/services/storage.py`).
- Supabase-authenticated REST API with profile auto-provisioning (`backend/app/auth/validate.py`).
- Job event audit trail persisted to Supabase (`backend/app/services/events.py`) and surfaced live in the UI.
- Subscription-aware usage limits plus Polar checkout, portal, and webhook orchestration (`backend/app/services/subscription_services/`).
- Next.js 15 frontend structured around the App Router with typed hooks and suspense-ready layouts.
- Axios interceptor layer (`frontend/lib/axios/axios.ts`) that injects Supabase JWTs into every backend request for seamless FastAPI auth.

## System Architecture
### Pipeline Walkthrough
```
YouTube URL → FastAPI job (POST /api/tasks/) → Celery worker
  1. transcripts.fetch_metadata(url) → Video ID + Title
  2. transcripts.fetch_transcript(video_id) → Raw transcript
  3. analysis.analyze_transcript(prompt) → Summary + keywords + style notes (Groq)
  4. crawl.crawl_images(keyword) → Reference URLs (Firecrawl)
  5. image_generation.generate_thumbnail(...) → Final artwork (Freepik)
  6. storage.upload_thumbnail(...) → Supabase Storage URL
  7. events.record_event(...) → Supabase job_events row (Realtime)
  8. Database writes → jobs, videos, images, subscription counters
```
Each transition logs a `job_events` record so the frontend can reflect progress, errors, and generated assets without polling.

### Backend Services
- **FastAPI app** (`backend/app/main.py`): exposes task creation, thumbnail listing, and subscription endpoints under `/api`. Auth is handled through Supabase JWT validation.
- **Celery worker** (`backend/app/celery/celery_app.py`): consumes jobs via Redis queues and runs the heavy lifting in `process_video_pipeline`.
- **Domain services** (`backend/app/services/`):
  - `transcripts.py` downloads metadata and transcripts using `yt-dlp` and `youtube-transcript-api`.
  - `analysis.py` posts rich prompts to Groq's `moonshotai/kimi-k2-instruct-0905` model and parses structured JSON.
  - `crawl.py` talks to Firecrawl v2 for inspirational imagery with retry logic.
  - `image_generation.py` validates references, calls Freepik's AI endpoint, and persists results via `storage.upload_thumbnail`.
  - `events.py` records canonical job events into Supabase for realtime updates.
  - `subscription_services/` centralises Polar API access, entitlement tracking, and usage limit enforcement.
- **Persistence**: SQLAlchemy models live under `backend/app/models/` with Alembic migrations in `backend/alembic/`. Async APIs use Postgres through `DATABASE_URL`, while Celery relies on the sync engine for transactional writes.

### Frontend Experience
- Built with **Next.js 15 + React 19** (`frontend/`), leveraging the App Router for streaming layouts, route groups, and server components alongside Tailwind 4-compatible utilities.
- Primary user flows:
  - `app/(app)/generate/page.tsx`: hero page with `GenerateContainer` for URL submission.
  - `components/generate/JobRealtime.tsx`: subscribes to Supabase `job_events` for live status, transcript summaries, and thumbnail previews with download support.
  - Subscription-aware gating via components in `components/subscription/` using hooks in `frontend/hooks/useSubscription.ts`.
- Supabase SSR/CSR helpers in `frontend/lib/supabase/` keep authentication consistent across server and client components and power middleware-free session hydration.
- Axios client (`frontend/lib/axios/axios.ts`) wraps every REST call, automatically attaching Supabase JWTs and handling 401 redirects back to `/auth/login`.
- Pricing and checkout UX taps Polar product IDs exposed through env vars to surface the right call-to-actions on landing routes.

### External Integrations
- **Supabase**: authentication, Postgres hosting, realtime channels, and asset storage (bucket `thumbnails`).
- **Redis**: Celery broker/result backend (default `redis://localhost:6379/0`).
- **Firecrawl**: image search inspiration, keyed by `FIRECRAWL_KEY`.
- **Groq**: LLM content analysis through `GROQ_API_KEY`.
- **Freepik**: thumbnail generation API via `FREEPIK_API_KEY`.
- **Polar**: subscription checkout, webhook ingestion, and customer portal management surfaced in both backend routes and frontend pricing flows.

## Getting Started
### Prerequisites
- Python 3.13+
- Node.js 20+ with `pnpm` (v10 recommended by `frontend/package.json`)
- Docker & Docker Compose (for the quickest setup)
- Supabase project with Postgres + Realtime enabled
- API credentials: Groq, Firecrawl, Freepik, Polar
- Redis instance (Docker compose ships one automatically)

### Environment Variables
Create `.env` files at the repo root (consumed by docker-compose) and inside relevant apps when running manually. The table below lists required values.

**Backend (`backend/` or `.env.docker`)**

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | Async SQLAlchemy URL (e.g. `postgresql+asyncpg://user:pass@localhost:5432/firenail`) |
| `SYNC_DATABASE_URL` | Sync SQLAlchemy URL for Celery/Alembic (e.g. `postgresql://user:pass@localhost:5432/firenail`) |
| `CELERY_BROKER_URL` | Redis broker URL (`redis://redis:6379/0` in Docker) |
| `CELERY_RESULT_BACKEND` | Redis backend URL |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Public anon key (used for service-client fallbacks) |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (needed for storage + job events) |
| `SUPABASE_JWT_SECRET` | JWT secret for verifying access tokens |
| `FIRECRAWL_KEY` | Firecrawl API key |
| `GROQ_API_KEY` | Groq API key for transcript analysis |
| `FREEPIK_API_KEY` | Freepik image generation key |
| `POLAR_ACCESS_TOKEN` | Polar API token (sandbox or production) |
| `POLAR_WEBHOOK_SECRET` | Secret used to verify inbound Polar webhooks |
| `APP_URL` | Public app URL (defaults to `http://localhost:3000`) |

**Frontend (`frontend/.env.local`)**

| Variable | Description |
| --- | --- |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key for client SDK |
| `NEXT_PUBLIC_BACKEND_URL` | Origin for FastAPI (e.g. `http://localhost:8000`) |
| `NEXT_PUBLIC_POLAR_MONTHLY_PRODUCT_ID` | Polar product ID for the monthly plan |
| `NEXT_PUBLIC_POLAR_YEARLY_PRODUCT_ID` | Polar product ID for the yearly plan |

> Tip: never expose the Supabase service role key in frontend `.env` files—only the backend should see it.

### Run with Docker
1. Copy `.env.docker.example` (if available) or craft `.env.docker` with the variables above.
2. Build and start all services:
   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```
3. FastAPI will be available on `http://localhost:8000`, the Next.js app on `http://localhost:3000`, and Redis inside the compose network.
4. Stop everything with `Ctrl+C` and remove containers with `docker compose -f docker-compose.dev.yml down`.

### Manual Setup
#### Backend API
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Celery Worker
```bash
cd backend
source .venv/bin/activate  # reuse the same virtualenv
celery -A app.celery.celery_app worker --loglevel=info
```

#### Frontend
```bash
cd frontend
pnpm install
pnpm dev
```
The Next.js dev server runs at `http://localhost:3000` and proxies API calls to the backend via `NEXT_PUBLIC_BACKEND_URL`.

## Database & Migrations
- Models live in `backend/app/models/` (Jobs, Videos, Images, Profiles, Subscriptions, JobEvents).
- Alembic configuration is under `backend/alembic/` with existing revisions seeded for the schema.
- Run migrations with `alembic upgrade head`. To generate new migrations:
  ```bash
  alembic revision --autogenerate -m "describe change"
  alembic upgrade head
  ```

## Supabase Setup
1. **Database tables**: mirror the SQLAlchemy models (`profiles`, `jobs`, `job_events`, `videos`, `images`, `subscriptions`). If you manage the schema through Alembic against Supabase Postgres, migrations will create them for you.
2. **Storage**: create a bucket named `thumbnails` with public read access. The backend uploads files under `thumbnails/{job_id}/{uuid}.png`.
3. **Policies**: ensure the service role key used by the backend has insert rights on `job_events` and storage buckets. Client-facing queries should respect RLS rules tied to Supabase auth.
4. **Realtime**: enable realtime on the `job_events` table to power the live job feed consumed by `useJobEvents`.

## Polar Billing Setup
- Configure products and prices (monthly/yearly) in Polar and capture the product IDs for the frontend env vars.
- Point Polar webhooks to `POST https://<backend-domain>/api/webhooks/polar`. The handler lives in `backend/app/api/subscription/polar_hooks.py` and validates signatures with `POLAR_WEBHOOK_SECRET`.
- On successful checkout (`backend/app/api/subscription/checkout.py`) and subsequent webhooks, subscriptions are persisted via `SubscriptionService` and linked to `profiles`.
- The customer portal endpoint (`/api/customer-portal`) issues `create_polar_portal_session` links so users can self-manage their plan.

## API Reference
| Method & Path | Description | Auth |
| --- | --- | --- |
| `POST /api/tasks/` | Queue thumbnail generation for a YouTube URL. Returns job ID. | Supabase Bearer |
| `GET /api/tasks/{task_id}` | Retrieve status of a queued job. | Supabase Bearer |
| `GET /api/thumbnails/` | Paginated list of generated thumbnails for the current user. | Supabase Bearer |
| `POST /api/subscription/create-checkout` | Start Polar checkout for a plan. | Supabase Bearer |
| `GET /api/subscription/status` | Fetch current subscription status. | Supabase Bearer |
| `GET /api/customer-portal` | Obtain Polar customer portal link. | Supabase Bearer |
| `POST /api/webhooks/polar` | Receive Polar webhook events. | No (verified by signature) |

All endpoints rely on the Supabase JWT validator in `backend/app/auth/validate.py`, so ensure clients attach the `access_token` as a Bearer token.

## Realtime Events
Each pipeline stage emits a structured event stored in Supabase (`backend/app/services/events.py`). Example payload:
```json
{
  "id": "f3c6...",
  "job_id": "0f02...",
  "step": "analysis",
  "status": "completed",
  "payload": {
    "summary": "How to automate design decisions...",
    "keywords": ["automation", "youtube branding"]
  },
  "created_at": "2025-10-30T12:34:56.000Z"
}
```
React hooks in `frontend/hooks/realTime/JobEvents.ts` subscribe to these inserts to hydrate the user interface with progress bars, transcript summaries, and download links once generation completes.

## Troubleshooting
- **No transcript available**: `process_video_pipeline` raises `RuntimeError("Transcript disabled...")`, logs an `error` event, and marks the job as failed.
- **Invalid reference URLs**: `image_generation.generate_thumbnail` validates each Firecrawl URL with a HEAD request; failures trigger a `thumbnail:skipped` event.
- **Auth errors**: ensure `SUPABASE_JWT_SECRET` matches your Supabase project's JWT secret and that the frontend session is active. Unauthorized responses redirect users to `/auth/login`.
- **Webhook signature issues**: confirm the Polar webhook secret in the dashboard matches `POLAR_WEBHOOK_SECRET` and that the payload is forwarded unmodified.
- **Realtime subscription failures**: check that the Supabase client is authenticated before calling `useJobEvents`; the hook logs channel errors to the console for debugging.

## Additional Resources
- `markdown/` directory for targeted guides such as `SUBSCRIPTION_LIMITS_IMPLEMENTATION.md` and `thumbnails_gallery_implementation.md`.
- Alembic migration history in `backend/alembic/versions/` for schema evolution details.
- Frontend component documentation within `frontend/components/` for UI patterns and state management helpers.

Welcome to Firenail—feel free to file issues, extend the pipeline, or plug in alternative inspiration/generation providers to build your dream thumbnail workflow.
