# backend/app/main.py
"""
Application entrypoint.
- Configures CORSMiddleware properly for credentialed cross-origin requests.
Impact:
- Must set allow_origins explicitly; do NOT set ["*"] when allow_credentials=True.
- Ensure this file's API_PREFIX matches settings.API_V1_STR.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# --- Internal imports ---
from app.config import settings
from app.db.session import init_db

# === Routers ===
from app.api.auth import router as auth_router
# other routers are left in place; we will include them if present
try:
    from app.api.intake import router as intake_router
except Exception:
    intake_router = None
try:
    from app.api.bootstrap import router as bootstrap_router
except Exception:
    bootstrap_router = None
try:
    from app.api.user_prefs import router as prefs_router
except Exception:
    prefs_router = None

# === Middleware ===
from app.middleware import AuthMiddleware  # keep existing middleware usage

API_PREFIX = settings.API_V1_STR

app = FastAPI(title=settings.PROJECT_NAME or "FastAPI App")

# CORS config:
# - allow_credentials must be True for cookies.
# - allow_origins must be an explicit list (no "*") when withCredentials is used.
frontend_origin = getattr(settings, "FRONTEND_ORIGIN", None)
if frontend_origin is None:
    # Development fallback
    frontend_origin = "http://localhost:3000"

# Support multiple origins (dev + prod)
allow_origins = [frontend_origin]
if settings.DEBUG and frontend_origin != "http://localhost:3000":
    # In dev, also allow localhost for testing
    allow_origins.append("http://localhost:3000")
    allow_origins.append("http://192.168.0.110:3000")  # your local IP

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,  # Explicit list required with allow_credentials=True
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=API_PREFIX, tags=["Auth"])
if intake_router:
    app.include_router(intake_router, prefix=API_PREFIX, tags=["Intake"])
if bootstrap_router:
    app.include_router(bootstrap_router, prefix=API_PREFIX, tags=["Bootstrap"])
if prefs_router:
    app.include_router(prefs_router, prefix=API_PREFIX, tags=["Prefs"])

# Include middleware (if AuthMiddleware is implemented, make sure it behaves correctly
# with CORS preflight requests and doesn't consume request body)
app.add_middleware(AuthMiddleware)

# Startup: init DB
@app.on_event("startup")
async def on_startup():
    # Initialize DB (create tables if needed)
    try:
        await init_db()
    except Exception:
        # safe failure here to avoid crash during migrations or missing DB in some dev setups
        pass


# Health endpoints
@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "running"}


@app.get("/ping")
async def ping():
    return {"message": "pong"}


# Generic error handlers could be added here if desired.
