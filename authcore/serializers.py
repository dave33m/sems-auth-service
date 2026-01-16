from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import AuthUser

class ClientTokenSerializer(serializers.Serializer):
    client_id = serializers.CharField()
    client_secret = serializers.CharField()
    grant_type = serializers.CharField()

    def validate_grant_type(self, value):
        if value != "client_credentials":
            raise serializers.ValidationError("Unsupported grant_type.")
        return value
    
class CreateClientSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    client_id = serializers.CharField(max_length=64)

    def validate_client_id(self, value):
        from .models import ClientApp
        if ClientApp.objects.filter(client_id=value).exists():
            raise serializers.ValidationError("client_id already exists.")
        return value

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = AuthUser
        fields = ("id", "email", "password", "first_name", "last_name")

    def validate_email(self, value):
        if AuthUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already in use.")
        return value.lower()

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = AuthUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        validate_password(data["new_password"])
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        validate_password(data["new_password"])
        return data

class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
