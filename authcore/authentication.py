import jwt
from django.conf import settings
from rest_framework import authentication, exceptions

from authcore.models import AuthUser


class ClientBearerAuthentication(authentication.BaseAuthentication):
    """
    Validates a client JWT issued by /oauth/token.
    """

    def authenticate(self, request):
        header = request.headers.get("Authorization")
        if not header or not header.startswith("Bearer "):
            return None  # let DRF handle missing auth

        token = header.split(" ", 1)[1]

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=["HS256"],
                audience=settings.JWT_CLIENT_AUDIENCE,
                issuer=settings.JWT_ISSUER,
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Client token expired.")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid client token.")

        if payload.get("type") != "client":
            raise exceptions.AuthenticationFailed("Invalid token type.")

        
        return (None, payload)

class UserBearerAuthentication(authentication.BaseAuthentication):
    """
    Validates a user JWT issued by /auth/login.
    """

    def authenticate(self, request):
        header = request.headers.get("Authorization")
        if not header or not header.startswith("Bearer "):
            return None

        token = header.split(" ", 1)[1]

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=["HS256"],
                audience=None,  # user tokens may have dynamic audiences
                issuer=settings.JWT_ISSUER,
                options={"verify_aud": False},
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("User token expired.")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid user token.")

        if payload.get("type") == "client":
            # Prevent client tokens from being used as user tokens
            raise exceptions.AuthenticationFailed("Client token not allowed here.")

        user_id = payload.get("id")
        if not user_id:
            raise exceptions.AuthenticationFailed("Invalid user token payload.")

        try:
            user = AuthUser.objects.get(id=user_id)
        except AuthUser.DoesNotExist:
            raise exceptions.AuthenticationFailed("User not found.")

        return (user, payload)