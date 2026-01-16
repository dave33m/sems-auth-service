import time
import jwt
from django.conf import settings


def create_client_token(client_id: str):
    now = int(time.time())
    payload = {
        "sub": client_id,
        "type": "client",
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_CLIENT_AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": now + settings.JWT_CLIENT_TTL,
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token, payload["exp"]
