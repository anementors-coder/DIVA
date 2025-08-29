from fastapi import FastAPI, HTTPException
from app.api.api import api_router
from app.core.redis import redis_client

app = FastAPI(title="AI Mentor API")


@app.on_event("startup")
async def startup_event():
    try:
        redis_client.ping()
        print("✅ Connected to Redis")
    except Exception as e:
        print("❌ Redis connection failed:", e)


@app.get("/")
def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the AI Mentor API!"}


# Include all versioned APIs
app.include_router(api_router, prefix="/api/v1")
