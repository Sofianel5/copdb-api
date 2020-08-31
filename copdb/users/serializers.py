from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from .models import Account

class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

class InternalAccountSerializer(serializers.ModelSerializer):
    is_venueadmin = serializers.ReadOnlyField()
    class Meta:
        model = Account
        exclude = ["password", "is_staff", "last_login", "is_admin", "is_active"]
        depth = 2

class ExternalAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account 
        fields = ["id", "first_name", "last_name"]