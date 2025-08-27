import json
from redis import Redis
from app.core.config import settings
import ast
redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)

def get_jwt_from_redis(jti: str) -> dict | None:
    data = redis_client.get(f"jwt:{jti}")
    if not data:
        return None
    try:
        return json.loads(data)  # ✅ preferred
    except json.JSONDecodeError:
        # Fallback for existing bad data
        return ast.literal_eval(data)  # ⚠️ safe version of eval