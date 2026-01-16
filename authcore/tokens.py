import time
import uuid
import jwt
from django.conf import settings


def create_client_token(client_id: str):
    now = int(time.time())
    ttl = settings.JWT_CLIENT_TTL

    payload = {
        "sub": client_id,
        "type": "client",
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_CLIENT_AUDIENCE,
        "iat": now,
        "nbf": now,
        "exp": now + ttl,
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token, ttl

def create_user_token(user, client_id):
    now = int(time.time())
    ttl = settings.JWT_USER_TTL  # e.g. 3600

    payload = {
        "iss": settings.JWT_ISSUER,
        "aud": [client_id],
        "client_id": client_id,
        "sub": user.email,
        "id": str(user.id),
        "email": user.email,
        "role": "USER",
        "claims": [],
        "iat": now,
        "nbf": now,
        "exp": now + ttl,
        "jti": str(uuid.uuid4()),
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token, ttl
