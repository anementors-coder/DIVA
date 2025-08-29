import time
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import ExpiredSignatureError, InvalidTokenError
from app.core.config import settings
from app.utils.redis_utils import redis_user_manager

auth = HTTPBearer()

def verify_passport_jwt(creds: HTTPAuthorizationCredentials = Depends(auth)):
    token = creds.credentials
    try:
        payload = jwt.decode(
            token,
            settings.PASSPORT_PUBLIC_KEY,
            algorithms=["RS256"],
            audience=settings.EXPECTED_AUD,
            options={"require": ["exp", "iat"]},
            leeway=settings.CLOCK_SKEW_LEEWAY,
        )

        exp = payload["exp"]
        ttl = int(exp - time.time())
        if ttl <= 0:
            raise Exception("Token already expired")

        # Store JWT payload with JTI key (expires with token)
        jti = payload.get("jti")
        if jti:
            redis_user_manager.store_jwt_payload(jti, payload, ttl)
        
        # Store user data with extended TTL (persists beyond JWT expiration)
        user_id = payload.get("sub")
        if user_id:
            redis_user_manager.store_user_data(user_id, payload)

        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


def get_user_latest_jti(user_id: str) -> str | None:
    """
    Get the latest JTI for a user, even if their current token is expired.
    This is useful for retrieving user data after token expiration.
    """
    return redis_user_manager.get_user_latest_jti(user_id)


def get_user_data_from_redis(user_id: str) -> dict | None:
    """
    Get user data directly by user_id, without needing JTI.
    This data persists longer than the JWT token itself.
    """
    return redis_user_manager.get_user_data(user_id)