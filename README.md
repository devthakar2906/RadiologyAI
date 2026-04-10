# RadiologyAI

RadiologyAI is a full-stack radiology dictation and structured reporting system built with FastAPI, React, PostgreSQL, Redis, and Celery. It supports doctor/admin authentication, live browser dictation, backend transcript refinement, structured report generation from findings, encrypted storage, report search, PDF export, and concurrent background processing.

## Quick Start

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
cd .\frontend
npm install
```

Then:

1. Copy `backend/.env.example` to `backend/.env`
2. Copy `frontend/.env.example` to `frontend/.env`
3. Start PostgreSQL on `localhost:9999`
4. Start Redis on `localhost:6379`
5. Run migrations:

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
.\.venv\Scripts\alembic.exe -c .\backend\alembic.ini upgrade head
```

6. Start backend:

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
powershell -ExecutionPolicy Bypass -File .\run_backend.ps1
```

7. Start worker:

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
powershell -ExecutionPolicy Bypass -File .\run_worker.ps1
```

8. Start frontend:

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI\frontend"
npm run dev
```

Optional monitoring:

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
powershell -ExecutionPolicy Bypass -File .\run_flower.ps1
```

## Stack

- Backend: FastAPI, PostgreSQL, SQLAlchemy, Redis, Celery, JWT auth, AES encryption, Alembic
- Speech: browser live transcription for UI responsiveness, Hugging Face Inference API for MedASR refinement
- Structured reporting: Hugging Face gated LLM API with RadReport-based template caching
- Frontend: React, Vite, Tailwind CSS, Quill, jsPDF
- Monitoring: Flower for Celery task visibility

## Project Structure

```text
RadiologyAI/
├── backend/
│   ├── alembic/
│   ├── app/
│   ├── templates/
│   ├── uploads/
│   ├── .env.example
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
├── run_backend.ps1
├── run_worker.ps1
├── run_flower.ps1
└── README.md
```

## Frontend Routes

- `/` -> homepage / landing page
- `/home` -> homepage / landing page
- `/report` -> existing report dashboard and transcription workspace
- `/app` -> alias to the same report dashboard
- `/login` -> login page
- `/signup` -> signup page

After login, the app redirects to the report dashboard at `/report`.

## Current User Flow

1. Open the site on `/`
2. Use the landing page to navigate into the reporting workspace
3. Log in or sign up
4. Dictate findings live in the browser or upload audio
5. Click `Stop Mic` to trigger backend MedASR refinement
6. Edit the transcript if needed
7. Click `Generate Report`
8. Backend detects study type, loads or reuses a cached template, and generates structured JSON
9. Review the structured report on the right panel
10. Save it to the database or download it as PDF

Text-only usage is also supported: findings can be typed directly and converted to a structured report without recording audio.

## End-to-End Technical Flow

### 1. Authentication Flow

1. User signs up or logs in through the frontend
2. FastAPI validates credentials against PostgreSQL
3. Passwords are verified using hashed password storage
4. Backend issues a JWT access token
5. Frontend stores:
   - `token` in `localStorage`
   - user profile in `localStorage`
6. All protected API requests include `Authorization: Bearer <token>`

### 2. Live Dictation Flow

1. Browser Web Speech API captures interim and final speech locally
2. Transcript is shown live inside the editor for immediate feedback
3. No heavy backend inference happens during live typing/dictation
4. This keeps the UI responsive and avoids unnecessary external API calls

### 3. Stop / Audio Refinement Flow

1. When the doctor clicks `Stop Mic`, the browser finalizes the recording
2. The recorded audio file is sent to `POST /api/v1/transcribe-audio`
3. Backend rate-limits the request per user
4. Backend sends audio to Hugging Face Inference API using `google/medasr`
5. If `raw_text` is already available from browser speech recognition, backend uses it as the initial base
6. Backend runs one refinement pass through MedASR-style prompting
7. Backend returns:
   - `raw_text`
   - `refined_text`
   - `status`
   - `transcription`
8. Frontend updates the editor with the refined text

### 4. Text-to-Structured-Report Flow

1. Doctor edits findings in the main editor
2. Frontend sends findings to `POST /api/v1/generate-structured-report`
3. Backend normalizes the text
4. Backend detects likely study type from keywords
5. Backend loads a cached template or fetches one from RadReport
6. Backend builds a strict JSON prompt for the LLM
7. Hugging Face gated LLM generates structured JSON
8. Backend validates and parses the JSON
9. If JSON is weak or unusable, backend falls back to deterministic structured output
10. Frontend displays the structured report in the right panel

### 5. Full Report Save Flow

1. Doctor clicks `Save`
2. Frontend sends:
   - `report_id` when available
   - current `transcription`
   - current structured `report`
3. Backend encrypts:
   - transcription
   - structured report JSON
4. Backend inserts or updates the `reports` table
5. Frontend updates the left-side history immediately with the saved record

### 6. Async Audio-to-Report Flow

1. Audio or text findings can also be sent to `POST /api/v1/process-audio`
2. Backend computes a hash for caching/idempotency
3. If a cached result exists in Redis, it returns immediately
4. Otherwise:
   - audio requests are queued into `process_audio_task`
   - text-only requests are queued into `process_text_task`
5. Celery worker processes the task in background
6. Worker:
   - transcribes/refines if needed
   - generates structured report
   - stores encrypted data in PostgreSQL
   - caches the result in Redis
7. Frontend or client polls:
   - `GET /api/v1/status/{job_id}`
   - or `GET /api/v1/task-status/{task_id}`

### 7. Report Retrieval / Dashboard Flow

1. Frontend loads report history from `GET /api/v1/reports`
2. Doctors only see their own reports
3. Admins can:
   - view all reports
   - filter by doctor
4. Search is applied across:
   - transcription
   - nested report fields
5. Selected reports are rendered into the editable structured report panel

### 8. PDF Export Flow

1. Doctor clicks `Download PDF`
2. Frontend converts the currently visible structured report into PDF
3. Export logic:
   - formats top-level headings larger and bold
   - indents nested fields
   - skips fields with `Not mentioned`
   - includes transcription only when meaningful
4. PDF is generated client-side using `jsPDF`

## Technical Data Flow Summary

- `React UI` handles interaction, editor state, routing, and PDF export
- `FastAPI` handles auth, validation, API orchestration, and DB access
- `PostgreSQL` stores encrypted users, reports, and logs
- `Redis` handles cache, Celery broker, Celery result backend, and rate-limit counters
- `Celery` handles background audio/text report jobs
- `Hugging Face Inference API` handles MedASR refinement and LLM structured generation
- `RadReport` is used as the external source for report template structure

## Reliability / Performance Design

- Heavy work is offloaded to Celery instead of blocking FastAPI routes
- Redis connection pooling reduces repeated connection overhead
- Celery tasks use retry with backoff for transient upstream failures
- Rate limiting protects transcription-heavy endpoints from overload
- Cached templates reduce repeated external template fetching
- Cached audio/text hashes reduce duplicate reprocessing
- Structured report fallback prevents blank report sections when the LLM output is weak

## Core Features

- Signup/login with JWT authentication
- Role-based access control for `doctor` and `admin`
- Admin doctor filtering
- Search by report words
- AES-encrypted transcription and report storage
- Editable structured report panel
- PDF export with heading hierarchy and hidden `Not mentioned` fields
- Persistent light/dark theme
- Homepage plus separate report dashboard
- Concurrent Celery-backed processing for audio and text report jobs

## Backend Architecture

### Speech Pipeline

- No local MedASR model loading
- No `transformers.pipeline()` or `from_pretrained()` in runtime
- `/transcribe-audio` uses Hugging Face Inference API via `HF_TOKEN`
- MedASR refinement is called only after stop/upload, not on every interim transcript
- `/transcribe-audio` returns:
  - `raw_text`
  - `refined_text`
  - `status`
  - `transcription` for compatibility

### Structured Report Generation

- Findings are normalized and passed into a structured-report service
- Study type is detected from findings text
- Templates are fetched from `https://radreport.org` on demand
- First successful templates are cached under `backend/templates/`
- Cached templates are preloaded into memory on backend startup
- Structured output is generated through a Hugging Face gated LLM model
- If the LLM output is weak or invalid, the backend falls back to a deterministic structured report instead of returning empty sections

### Async Processing

- `/process-audio` remains the same endpoint
- Audio requests are queued into Celery background workers
- Text-only findings submitted through `/process-audio` are also queued
- `/status/{job_id}` remains available
- `/task-status/{task_id}` is also available as a compatible alias

### Concurrency and Reliability

- Celery worker pool and concurrency are configurable through env vars
- Redis is used as:
  - Celery broker
  - Celery result backend
  - application cache layer
- Redis uses connection pooling
- Celery tasks track start state and use retry/backoff for external API failures
- Per-user rate limiting protects transcription-heavy endpoints

## Main API Endpoints

- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `POST /api/v1/process-audio`
- `POST /api/v1/transcribe-audio`
- `POST /api/v1/generate-structured-report`
- `POST /api/v1/reports/save`
- `GET /api/v1/status/{job_id}`
- `GET /api/v1/task-status/{task_id}`
- `GET /api/v1/reports`
- `GET /api/v1/doctors`
- `DELETE /api/v1/reports/{report_id}`
- `GET /health`

## Ports

- Frontend: `http://localhost:9997`
- Backend: `http://localhost:9998`
- PostgreSQL: `localhost:9999`
- Redis: `localhost:6379`
- Flower: `http://localhost:5555`

## Environment Files

Copy these before running:

- `backend/.env.example` -> `backend/.env`
- `frontend/.env.example` -> `frontend/.env`

### Backend `.env`

Important variables:

- `DATABASE_URL=postgresql://postgres:root@localhost:9999/radiology_ai`
- `REDIS_URL=redis://localhost:6379/0`
- `CELERY_BROKER_URL=redis://localhost:6379/1`
- `CELERY_RESULT_BACKEND=redis://localhost:6379/2`
- `STT_MODEL=google/medasr`
- `HF_TOKEN=...`
- `LLM_MODEL=meta-llama/Llama-3.3-70B-Instruct`
- `RADREPORT_BASE_URL=https://radreport.org`
- `TEMPLATE_CACHE_DIR=E:/Dev Microsoft/ChatGPT/RadiologyAI/backend/templates`
- `FRONTEND_URL=http://localhost:9997`
- `CELERY_WORKER_CONCURRENCY=4`
- `CELERY_WORKER_POOL=prefork`
- `REDIS_MAX_CONNECTIONS=50`
- `HF_REQUEST_TIMEOUT_SECONDS=120`
- `HF_MAX_RETRIES=3`
- `TRANSCRIPTION_RATE_LIMIT_COUNT=20`
- `TRANSCRIPTION_RATE_LIMIT_WINDOW_SECONDS=300`
- `FLOWER_PORT=5555`

## Requirements

- Python 3.10 or 3.11
- Node.js and npm
- PostgreSQL
- Redis
- Git
- FFmpeg available on the machine if your audio formats require it

## Setup

### 1. Create the backend virtual environment and install dependencies

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
Copy-Item .\backend\.env.example .\backend\.env -Force
```

### 2. Install frontend dependencies

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI\frontend"
npm install
Copy-Item .env.example .env -Force
```

### 3. Start PostgreSQL and Redis

Make sure these are running:

- PostgreSQL on `localhost:9999`
- Redis on `localhost:6379`

Create:

- database: `radiology_ai`
- username: `postgres`
- password: `root`

### 4. Configure backend environment

Edit `backend/.env` and set at minimum:

```env
DATABASE_URL=postgresql://postgres:root@localhost:9999/radiology_ai
HF_TOKEN=your_huggingface_token
FRONTEND_URL=http://localhost:9997
```

### 5. Run database migrations

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
.\.venv\Scripts\alembic.exe -c .\backend\alembic.ini upgrade head
```

Alembic notes:

- `backend/alembic.ini` is aligned with project port `9999`
- `backend/alembic/env.py` overrides the URL from `backend/.env`, so `.env` remains the source of truth
- current migration revision:
  - `20260403_000001_initial_schema`

### 6. Start the backend

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
powershell -ExecutionPolicy Bypass -File .\run_backend.ps1
```

Backend docs:

- `http://localhost:9998/docs`

Health check:

- `http://localhost:9998/health`

### 7. Start the Celery worker

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
powershell -ExecutionPolicy Bypass -File .\run_worker.ps1
```

The worker reads:

- `CELERY_WORKER_POOL`
- `CELERY_WORKER_CONCURRENCY`

### 8. Start Flower monitoring

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
powershell -ExecutionPolicy Bypass -File .\run_flower.ps1
```

Flower:

- `http://localhost:5555`

### 9. Start the frontend

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI\frontend"
npm run dev
```

Frontend:

- `http://localhost:9997`

## Report UI

- Structured report panel is editable
- Top-level `Transcription` section is hidden from the report editor UI
- Save updates or inserts the report into the history list immediately
- Search works across transcription and report content
- Downloaded PDFs:
  - use larger bold headings for main sections
  - use indented subpoints
  - skip values that are exactly `Not mentioned`

## Theme / UI Notes

- Theme is controlled through the `html.dark` class
- Theme persists with `localStorage`
- A small script in `frontend/index.html` prevents flash on refresh
- Light mode uses a monochrome palette for visibility
- Homepage is separate from the report dashboard

## Concurrency Notes

- The current backend is much safer for multiple doctors sending requests concurrently than before
- Heavy work is queued instead of running inline in request handlers
- Celery retries external API calls
- Redis connection pooling reduces reconnect overhead
- Rate limiting prevents a single user from overwhelming transcription routes

Practical note:

- On Windows, Celery `prefork` can still be less robust than Linux/WSL for production-style concurrency
- For the strongest multi-doctor throughput, run workers on Linux or WSL if possible

## Common Commands

### Run migrations

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
.\.venv\Scripts\alembic.exe -c .\backend\alembic.ini upgrade head
```

### Start backend

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
powershell -ExecutionPolicy Bypass -File .\run_backend.ps1
```

### Start worker

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
powershell -ExecutionPolicy Bypass -File .\run_worker.ps1
```

### Start Flower

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
powershell -ExecutionPolicy Bypass -File .\run_flower.ps1
```

### Start frontend

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI\frontend"
npm run dev
```
