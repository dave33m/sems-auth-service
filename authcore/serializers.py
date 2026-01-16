from rest_framework import serializers


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
