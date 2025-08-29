from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from app.core.security import verify_passport_jwt
from app.core.redis import get_jwt_from_redis, get_user_data_by_id, get_latest_jti_for_user

router = APIRouter()
auth = HTTPBearer()

@router.get("/secure")
def secure_route(claims: dict = Depends(verify_passport_jwt)):
    """
    Protected route that returns JWT claims.
    """
    return {
        "ok": True,
        "user_id": claims.get("sub"),
        "aud": claims.get("aud"),
        "scopes": claims.get("scopes", []),
        "exp": claims.get("exp"),
        "jti": claims.get("jti"),
    }

@router.get("/redis/{jti}")
def get_token_from_redis(jti: str):
    """
    Retrieve stored JWT payload from Redis by JTI.
    """
    payload = get_jwt_from_redis(jti)
    if not payload:
        raise HTTPException(status_code=404, detail="Token not found in Redis")
    return {"jti": jti, "payload": payload}

@router.get("/user/{user_id}/data")
def get_user_data(user_id: str):
    """
    Retrieve user data from Redis by user_id.
    This works even after JWT expiration.
    """
    user_data = get_user_data_by_id(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User data not found in Redis")
    return {"user_id": user_id, "data": user_data}

@router.get("/user/{user_id}/latest-jti")
def get_user_latest_jti(user_id: str):
    """
    Get the latest JTI for a user.
    Useful for retrieving user data after token expiration.
    """
    jti = get_latest_jti_for_user(user_id)
    if not jti:
        raise HTTPException(status_code=404, detail="No JTI found for user")
    return {"user_id": user_id, "latest_jti": jti}