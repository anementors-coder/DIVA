from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from app.core.security import verify_passport_jwt
from app.core.redis import get_jwt_from_redis

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
