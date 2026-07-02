"""Local demo launcher — runs the SAME app on this machine WITHOUT Docker/K8s.

Uses SQLite instead of PostgreSQL so tahminler yine bir veritabanına kaydolur.
LLM ucu (/llm/chat) harici bir API anahtarı gerektirdiği için burada hariç
tutulmuştur; iris + advertising uçları ve /metrics gerçek modellerle çalışır.

Çalıştır:  python -m uvicorn local_run:app --reload --port 8000
Sonra tarayıcıda:  http://localhost:8000/docs
"""
import os

# database.py bu değişkeni import anında okur -> her şeyden ÖNCE ayarla.
os.environ.setdefault("SQLALCHEMY_DATABASE_URL", "sqlite:///./local_demo.db")

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from database import create_db_and_tables
from routers.iris import iris_ep
from routers.advertising import advertising_ep

app = FastAPI(title="Deploy ML/AI with API — Local Demo (iris + advertising)")

create_db_and_tables()

app.include_router(iris_ep.router)
app.include_router(advertising_ep.router)

# Prometheus /metrics — k8s'teki ile birebir aynı enstrümantasyon.
Instrumentator().instrument(app).expose(app)


@app.get("/")
async def root():
    return {"message": "Hello FastAPI! (local demo — iris + advertising)"}


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
