# app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core.redis import redis_client
from app.core.exception_handlers import register_exception_handlers
from app.core.middleware import RequestContextMiddleware
from app.utils.logging import configure_logging, LogLevels

# Configure logging once (use env var LOG_LEVEL=DEBUG|INFO|WARN|ERROR)
configure_logging(os.getenv("LOG_LEVEL", LogLevels.info))

app = FastAPI(title="AI Mentor API")

# Request context middleware (request_id + response time + logging context)
app.add_middleware(RequestContextMiddleware)

# CORS (configure strictly in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global exception handlers
register_exception_handlers(app)


@app.on_event("startup")
async def startup_event():
    try:
        redis_client.ping()
        print("✅ Connected to Redis")
    except Exception as e:
        print("❌ Redis connection failed:", e)


@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Mentor API!"}


# Include versioned APIs
app.include_router(api_router, prefix="/api/eva")