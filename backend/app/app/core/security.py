import time
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import ExpiredSignatureError, InvalidTokenError
from app.core.config import settings
from app.core.redis import redis_client

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

        redis_client.setex(f"jwt:{payload['jti']}", ttl, str(payload))
        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
 
