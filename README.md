# RadiologyAI

RadiologyAI is a full-stack radiology dictation and structured reporting system built with FastAPI, React, PostgreSQL, Redis, and Celery. It supports doctor/admin authentication, encrypted report storage, browser-based live dictation, backend transcript refinement, structured report generation, PDF export, and searchable report history.

## Quick Start

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
python -m venv .venv
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

## Stack

- Backend: FastAPI, PostgreSQL, SQLAlchemy, Redis, Celery, JWT auth, AES encryption, Alembic
- Speech pipeline: browser live transcription for fast UI feedback, Hugging Face Inference API for MedASR refinement
- Structured reporting: Hugging Face gated LLM API with RadReport-driven template caching
- Frontend: React, Vite, Tailwind CSS, Quill, jsPDF

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
└── README.md
```

## Current Workflow

1. Click `Start Mic`
2. Browser speech recognition fills the editor live
3. Click `Stop Mic`
4. The recorded audio is sent to the backend
5. Backend returns:
   - `raw_text`
   - `refined_text`
   - `status`
6. The editor is updated with the refined text
7. Click `Generate Report`
8. Backend detects the study type, fetches or reuses a cached template, and generates a structured report
9. Edit the structured report on the right if needed
10. Click `Save` to persist it or `Download PDF` to export it

You can also upload an audio file directly, or type findings manually and generate a report without recording.

## Features

- Signup/login with JWT authentication
- RBAC for `doctor` and `admin`
- Admin doctor filtering
- Search by report words
- Redis caching
- Celery async processing for `/process-audio`
- AES encryption for stored transcription and report data
- Structured editable report panel
- PDF download with hierarchical formatting
- Persistent dark mode using the `html.dark` class

## AI Architecture

### Speech

- No local MedASR model loading
- No `transformers.pipeline()` or `from_pretrained()` in runtime
- `/transcribe-audio` uses Hugging Face Inference API with `HF_TOKEN`
- MedASR refinement is called only once after the stop/upload event

### Structured Report Generation

- Study type is detected from findings text
- Templates are fetched from `https://radreport.org` on demand
- The first successful template is cached under `backend/templates/`
- Structured output is generated through a Hugging Face gated model API
- The same `HF_TOKEN` is used for MedASR and LLM access

## Main API Endpoints

- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `POST /api/v1/process-audio`
- `POST /api/v1/transcribe-audio`
- `POST /api/v1/generate-structured-report`
- `POST /api/v1/reports/save`
- `GET /api/v1/status/{job_id}`
- `GET /api/v1/reports`
- `GET /api/v1/doctors`
- `DELETE /api/v1/reports/{report_id}`
- `GET /health`

## Ports

- Frontend: `http://localhost:9997`
- Backend: `http://localhost:9998`
- PostgreSQL: `localhost:9999`
- Redis: `localhost:6379`

## Environment Files

Copy these before running:

- `backend/.env.example` -> `backend/.env`
- `frontend/.env.example` -> `frontend/.env`

### Backend `.env`

Important variables:

- `DATABASE_URL=postgresql://postgres:postgres@localhost:9999/radiology_ai`
- `REDIS_URL=redis://localhost:6379/0`
- `CELERY_BROKER_URL=redis://localhost:6379/1`
- `CELERY_RESULT_BACKEND=redis://localhost:6379/2`
- `STT_MODEL=google/medasr`
- `HF_TOKEN=...`
- `LLM_MODEL=meta-llama/Llama-3.3-70B-Instruct`
- `RADREPORT_BASE_URL=https://radreport.org`
- `TEMPLATE_CACHE_DIR=E:/Dev Microsoft/ChatGPT/RadiologyAI/backend/templates`
- `FRONTEND_URL=http://localhost:9997`

## Requirements

- Python 3.10 or 3.11
- Node.js and npm
- PostgreSQL
- Redis
- Git
- FFmpeg available on the machine if your input formats require it

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
- password: `postgres`

### 4. Configure backend environment

Edit `backend/.env` and set at minimum:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:9999/radiology_ai
HF_TOKEN=your_huggingface_token
FRONTEND_URL=http://localhost:9997
```

### 5. Run database migrations

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
.\.venv\Scripts\alembic.exe -c .\backend\alembic.ini upgrade head
```

Alembic notes:

- `backend/alembic.ini` is now aligned with the project database port `9999`
- `backend/alembic/env.py` overrides the URL from `backend/.env`, so your real `.env` remains the source of truth
- the current migration revision is:
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

Open a new terminal:

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
powershell -ExecutionPolicy Bypass -File .\run_worker.ps1
```

### 8. Start the frontend

Open another terminal:

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI\frontend"
npm run dev
```

Frontend:

- `http://localhost:9997`

## Dark Mode

- Theme is controlled through the `<html>` element using the `dark` class
- Theme persists with `localStorage`
- A small script in `frontend/index.html` prevents flash on refresh
- Light mode uses a monochrome palette for better readability

## Report UI

- The structured report panel is editable
- The top-level `Transcription` section is hidden from the report editor UI
- `Save` updates or inserts the report into the left-side history immediately
- Downloaded PDFs:
  - use larger bold headings for main sections
  - use indented bullet-style nested subpoints
  - skip values that are exactly `Not mentioned`

## Notes

- `/transcribe-audio` keeps the route name unchanged but now returns:
  - `raw_text`
  - `refined_text`
  - `status`
  - `transcription` for compatibility
- `/process-audio` still exists and still supports async job processing
- Templates are no longer manually maintained study-by-study; they are cached as they are first used
- If RadReport fetch/parsing fails for a study, the backend falls back to a minimal inferred structure instead of crashing

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

### Start frontend

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI\frontend"
npm run dev
```
