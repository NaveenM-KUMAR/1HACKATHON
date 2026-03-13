import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.routers import auth_router, complaint_router, map_router, analytics_router, alert_router

# ── Create all tables on startup ──────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Raksha Nethra API",
    description="AI-Powered Civic Intelligence & Community Safety Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (allow all origins for local dev) ────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static file serving for uploaded images ───────────────────────────────────
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ── Static file serving for the frontend app ──────────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
os.makedirs(FRONTEND_DIR, exist_ok=True)
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router.router)
app.include_router(complaint_router.router)
app.include_router(map_router.router)
app.include_router(analytics_router.router)
app.include_router(alert_router.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "project": "Raksha Nethra",
        "status":  "online",
        "docs":    "/docs",
    }
