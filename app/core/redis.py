import json
import ast
from redis import Redis
from app.core.config import settings

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)

# Legacy functions for backward compatibility
def get_jwt_from_redis(jti: str) -> dict | None:
    """Get JWT payload by JTI (works only if token hasn't expired)"""
    from app.utils.redis_utils import redis_user_manager
    return redis_user_manager.get_jwt_payload(jti)

def get_user_data_by_id(user_id: str) -> dict | None:
    """Get user data directly by user_id (persists longer than JWT)"""
    from app.utils.redis_utils import redis_user_manager
    return redis_user_manager.get_user_data(user_id)

def get_latest_jti_for_user(user_id: str) -> str | None:
    """Get the latest JTI for a user"""
    from app.utils.redis_utils import redis_user_manager
    return redis_user_manager.get_user_latest_jti(user_id)

def store_user_session_data(user_id: str, data: dict, ttl: int = 30 * 24 * 60 * 60):
    """Store additional user session data with extended TTL"""
    from app.utils.redis_utils import redis_user_manager
    return redis_user_manager.store_session_data(user_id, data)