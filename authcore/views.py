from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from .models import ClientApp
from .serializers import ClientTokenSerializer, CreateClientSerializer
from .tokens import create_client_token


class RegisterView(APIView):
    def post(self, request):
        return Response(
            {"detail": "Register endpoint placeholder"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class LoginView(APIView):
    def post(self, request):
        return Response(
            {"detail": "Login endpoint placeholder"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )

class ClientTokenView(APIView):
    authentication_classes = []
    permission_classes = []
    @swagger_auto_schema(request_body=ClientTokenSerializer)
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
