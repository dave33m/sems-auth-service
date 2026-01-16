from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate
import secrets
from django.utils import timezone
from datetime import timedelta
from .models import OneTimeCode, PasswordResetToken, RefreshToken, AuthUser, ClientApp
from authcore.authentication import ClientBearerAuthentication, UserBearerAuthentication
from .email_service import send_login_otp, send_reset_email
from .serializers import ChangePasswordSerializer, ClientTokenSerializer, CreateClientSerializer, ForgotPasswordSerializer, LoginSerializer, LogoutSerializer, RefreshSerializer, RegisterSerializer, ResetPasswordSerializer, VerifyOtpSerializer
from .tokens import create_client_token, create_user_token


class RegisterView(APIView):
    authentication_classes = [ClientBearerAuthentication]
    permission_classes = []

    @swagger_auto_schema(
        tags=["Auth"],
        request_body=RegisterSerializer,
        responses={201: "User created"},
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = [ClientBearerAuthentication]
    permission_classes = []

    @swagger_auto_schema(tags=["Auth"], request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower()
        password = serializer.validated_data["password"]

        try:
            user = AuthUser.objects.get(email=email)
        except AuthUser.DoesNotExist:
            return Response({"error": "invalid_credentials"}, status=401)

        if not user.check_password(password):
            return Response({"error": "invalid_credentials"}, status=401)

        otp = f"{secrets.randbelow(1000000):06d}"

        OneTimeCode.objects.create(
            user=user,
            code=otp,
            purpose=OneTimeCode.PURPOSE_LOGIN,
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        send_login_otp(user.email, otp)

        return Response(
            {"detail": "Login OTP sent to your email."},
            status=200,
        )


class ClientTokenView(APIView):
    authentication_classes = []
    permission_classes = []
    @swagger_auto_schema(
        tags=["Auth"],
        request_body=ClientTokenSerializer)
    
    def post(self, request):
        serializer = ClientTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        client_id = serializer.validated_data["client_id"]
        client_secret = serializer.validated_data["client_secret"]

        try:
            client = ClientApp.objects.get(client_id=client_id, is_active=True)
        except ClientApp.DoesNotExist:
            return Response({"error": "invalid_client"}, status=status.HTTP_401_UNAUTHORIZED)

        if not client.verify_secret(client_secret):
            return Response({"error": "invalid_client"}, status=status.HTTP_401_UNAUTHORIZED)

        token, exp = create_client_token(client.client_id)

        return Response(
            {
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": exp,
            },
            status=status.HTTP_200_OK,
        )
        
        
class CreateClientView(APIView):
    """
    Creates a new client application.
    This should later be protected by admin auth.
    """

    @swagger_auto_schema(
        tags=["Auth"],
        request_body=CreateClientSerializer,
        responses={201: "Client created"},
    )
    def post(self, request):
        serializer = CreateClientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data["name"]
        client_id = serializer.validated_data["client_id"]

        client, raw_secret = ClientApp.create_client(name, client_id)

        return Response(
            {
                "name": client.name,
                "client_id": client.client_id,
                "client_secret": raw_secret,
            },
            status=status.HTTP_201_CREATED,
        )

class RefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        tags=["Auth"],
        request_body=RefreshSerializer,
        responses={200: "Token refreshed", 401: "Invalid refresh token"},
    )
    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["refresh_token"]

        try:
            rt = RefreshToken.objects.select_related("user").get(
                token=token,
                is_revoked=False,
                expires_at__gt=timezone.now(),
            )
        except RefreshToken.DoesNotExist:
            return Response({"error": "invalid_refresh"}, status=status.HTTP_401_UNAUTHORIZED)

        # rotate
        rt.is_revoked = True
        rt.save(update_fields=["is_revoked"])

        new_raw = secrets.token_urlsafe(48)
        RefreshToken.objects.create(
            user=rt.user,
            token=new_raw,
            expires_at=timezone.now() + timedelta(days=14),
        )

        token, exp = create_user_token(rt.user, rt.user.email)

        return Response(
            {
                "access_token": token,
                "refresh_token": new_raw,
                "token_type": "Bearer",
                "expires_in": exp,
            },
            status=status.HTTP_200_OK,
        )
        
class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        tags=["Auth"],
        request_body=LogoutSerializer,
        responses={200: "Logged out"},
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["refresh_token"]

        updated = RefreshToken.objects.filter(
            token=token,
            is_revoked=False,
            expires_at__gt=timezone.now(),
        ).update(is_revoked=True)

        if not updated:
            return Response({"error": "invalid_refresh"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "logged_out"}, status=status.HTTP_200_OK)


class LogoutAllView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        tags=["Auth"],
        request_body=LogoutSerializer,
        responses={200: "All sessions revoked"},
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["refresh_token"]

        try:
            rt = RefreshToken.objects.select_related("user").get(
                token=token,
                is_revoked=False,
            )
        except RefreshToken.DoesNotExist:
            return Response({"error": "invalid_refresh"}, status=status.HTTP_400_BAD_REQUEST)

        RefreshToken.objects.filter(user=rt.user).update(is_revoked=True)

        return Response({"detail": "all_sessions_revoked"}, status=status.HTTP_200_OK)
    
class ForgotPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(tags=["Auth"], request_body=ForgotPasswordSerializer)
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower()

        try:
            user = AuthUser.objects.get(email=email)
        except AuthUser.DoesNotExist:
            return Response(
            {"detail": "If the email exists, a password reset OTP has been sent."},
            status=status.HTTP_200_OK,
        )

        otp = f"{secrets.randbelow(1000000):06d}"

        PasswordResetToken.objects.create(
            user=user,
            token=otp,
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        send_reset_email(user.email, otp)

        return Response(
        {"detail": "If the email exists, a password reset OTP has been sent."},
        status=status.HTTP_200_OK,
    )


class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(tags=["Auth"], request_body=ResetPasswordSerializer)
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower()
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        try:
            prt = PasswordResetToken.objects.select_related("user").get(
                user__email=email,
                token=otp,
                is_used=False,
                expires_at__gt=timezone.now(),
            )
        except PasswordResetToken.DoesNotExist:
            return Response({"error": "invalid_otp"}, status=status.HTTP_400_BAD_REQUEST)

        user = prt.user
        user.set_password(new_password)
        user.save(update_fields=["password"])

        prt.is_used = True
        prt.save(update_fields=["is_used"])

        return Response({"detail": "password reset succesfully"}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    authentication_classes = [UserBearerAuthentication]
    permission_classes = []

    @swagger_auto_schema(tags=["Auth"], request_body=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return Response(
                {"error": "invalid_password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response(
            {"detail": "password changed successfully"},
            status=status.HTTP_200_OK,
        )

class VerifyOtpView(APIView):
    authentication_classes = [ClientBearerAuthentication]
    permission_classes = []

    @swagger_auto_schema(tags=["Auth"], request_body=VerifyOtpSerializer)
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower()
        otp = serializer.validated_data["otp"]

        try:
            otc = OneTimeCode.objects.select_related("user").get(
                user__email=email,
                code=otp,
                purpose=OneTimeCode.PURPOSE_LOGIN,
                is_used=False,
                expires_at__gt=timezone.now(),
            )
        except OneTimeCode.DoesNotExist:
            return Response({"error": "invalid_otp"}, status=400)

        user = otc.user
        otc.is_used = True
        otc.save(update_fields=["is_used"])

        client_id = request.auth.get("sub")

        token, ttl = create_user_token(user, client_id)

        raw_refresh = secrets.token_urlsafe(48)
        RefreshToken.objects.create(
            user=user,
            token=raw_refresh,
            expires_at=timezone.now() + timedelta(days=14),
        )

        return Response(
            {
                "access_token": token,
                "refresh_token": raw_refresh,
                "token_type": "Bearer",
                "expires_in": ttl,
            },
            status=200,
        )
