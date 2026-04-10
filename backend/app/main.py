from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.reports import router as reports_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.models import Log, Report, User
from app.services.template_service import preload_cached_templates


settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:9997"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE IF EXISTS logs ALTER COLUMN status TYPE TEXT"))
    preload_cached_templates()


app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(reports_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health_check():
    return {"status": "ok"}
