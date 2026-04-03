# RadiologyAI

RadiologyAI is a local full-stack radiology dictation workflow built with free and open-source tools. It provides authentication, report generation, encrypted storage, background processing, and a React dashboard for reviewing and exporting reports.

## Stack

- Backend: FastAPI, PostgreSQL, SQLAlchemy, Redis, Celery, JWT auth, AES encryption
- AI:
  - Speech-to-text: `google/medasr` via Hugging Face
  - Summarization/report generation: `Falconsai/medical_summarization`
- Frontend: React, Vite, Tailwind CSS, Quill, jsPDF
- Migrations: Alembic

## Project Structure

```text
RadiologyAI/
├── backend/
│   ├── alembic/
│   ├── app/
│   ├── uploads/
│   ├── .env.example
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
├── run_backend.ps1
├── run_worker.ps1
└── README.md
```

## Current Flow

The app now supports this report-generation workflow:

1. Click `Start Mic`
2. Browser live speech recognition fills the textbox in real time
3. Click `Stop Mic`
4. The recorded audio is sent to the backend for refined transcription
5. The textbox is updated with the refined transcript
6. Edit the textbox if needed
7. Click `Generate Report`
8. The structured report appears on the right side
9. Edit the structured report if needed
10. Download the edited report as PDF

The Generate button also supports direct text-to-report generation, even if no audio file is uploaded.

## Features

- Signup/login with JWT authentication
- Role-based access control for `doctor` and `admin`
- Audio upload and text-to-report generation
- Redis cache using transcription/audio hash
- Celery background processing
- AES encryption for stored transcription and report content
- Report dashboard with search, delete, and PDF export
- Editable structured report panel
- Real-time browser mic transcription with backend refinement after recording stops
- Dark mode persistence with `localStorage`

## API Endpoints

- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `POST /api/v1/process-audio`
- `POST /api/v1/transcribe-audio`
- `GET /api/v1/status/{job_id}`
- `GET /api/v1/reports`
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
- `SUMMARIZATION_MODEL=Falconsai/medical_summarization`
- `HF_TOKEN=...` for authenticated/gated Hugging Face model access
- `FRONTEND_URL=http://localhost:9997`

## Requirements

Install these locally:

- Python 3.10 or 3.11
- Node.js and npm
- PostgreSQL
- Redis
- Git

## Step-by-Step Setup

### 1. Backend dependencies

If you use the repo-root virtual environment:

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
Copy-Item .\backend\.env.example .\backend\.env -Force
```

If you use `backend\.venv` instead, keep your commands consistent with that environment.

### 2. Frontend dependencies

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI\frontend"
npm install
Copy-Item .env.example .env -Force
```

### 3. Start PostgreSQL and Redis

Make sure these are running:

- PostgreSQL on `localhost:9999`
- Redis on `localhost:6379`

Create the database:

- Database: `radiology_ai`
- Username: `postgres`
- Password: `postgres`

### 4. Configure Hugging Face token

Edit `backend/.env` and set:

```env
HF_TOKEN=your_huggingface_access_token
```

This is used for MedASR and authenticated model downloads.

### 5. Run Alembic migrations

From the repo root:

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
.\.venv\Scripts\python.exe -m alembic -c .\backend\alembic.ini upgrade head
```

To create future migrations:

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
.\.venv\Scripts\python.exe -m alembic -c .\backend\alembic.ini revision --autogenerate -m "your message"
```

### 6. Start backend

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
powershell -ExecutionPolicy Bypass -File .\run_backend.ps1
```

Backend docs:

- `http://localhost:9998/docs`

Health check:

- `http://localhost:9998/health`

### 7. Start Celery worker

Open a new terminal:

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
powershell -ExecutionPolicy Bypass -File .\run_worker.ps1
```

The worker uses `--pool=solo`, which is more reliable on Windows for ML workloads.

### 8. Start frontend

Open another terminal:

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI\frontend"
npm run dev
```

Frontend:

- `http://localhost:9997`

## How Report Generation Works

### Audio flow

1. Record or upload audio
2. Backend transcribes it with `google/medasr`
3. The refined transcript is returned to the UI
4. Clicking `Generate Report` sends the textbox content to the backend
5. The backend generates Findings, Impression, and Recommendations
6. The report and transcription are encrypted and stored in PostgreSQL
7. The response is shown in the right-side structured report panel

### Text flow

1. Type or edit text in the textbox
2. Click `Generate Report`
3. The backend generates and stores the report directly from text

## PDF Export

The structured report panel on the right is editable. You can:

- edit Findings
- edit Impression
- edit Recommendations
- edit the stored transcription text
- click `Download PDF`

The downloaded PDF uses the edited values currently shown in the panel.

## Notes and Troubleshooting

- If the backend cannot load the app, make sure you are starting it with `run_backend.ps1`
- If jobs stay in `pending`, make sure Redis is running and the Celery worker is active
- If transcription quality is poor, the issue is likely the STT model or input audio quality, not the PDF/report UI
- If Hugging Face model loading fails, verify `HF_TOKEN` in `backend/.env`
- The first model load can take time because Hugging Face weights download locally
- Web Speech API support depends on the browser; Chrome-based browsers work best
- Database schema changes are managed through Alembic in `backend/alembic/`

## Common Commands

### Run migrations

```powershell
cd "E:\Dev Microsoft\ChatGPT\RadiologyAI"
.\.venv\Scripts\python.exe -m alembic -c .\backend\alembic.ini upgrade head
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
