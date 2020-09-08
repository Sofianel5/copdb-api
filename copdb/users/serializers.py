from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from .models import *

class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ('username', 'email', 'first_name', 'last_name', 'dob', 'profile_pic', 'password')

class ExternalAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account 
        fields = ["id", "first_name", "last_name", "verified", "username", "profile_pic"]
    
class InternalAccountSerializer(serializers.ModelSerializer):
    following = ExternalAccountSerializer(many=True)
    followers = ExternalAccountSerializer(many=True)
    friends = ExternalAccountSerializer(many=True)
    class Meta:
        model = Account
        exclude = ["password", "is_staff", "last_login", "is_admin", "is_active", "sex"]
        depth = 2

class NetworkInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkInfo 
        fields = "__all__"

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device 
        fields = "__all__"

class AndroidDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AndroidDevice 
        fields = "__all__"

class iOSDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = iOSDevice 
        fields = "__all__"

class LocationPingSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationPing  
        fields = "__all__"

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact  
        fields = "__all__"

class ClipboardDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClipboardData  
        fields = "__all__"

class ConnectionSerializer(serializers.ModelSerializer):
    creator = ExternalAccountSerializer()
    following = ExternalAccountSerializer()
    class Meta:
        model = Connection 
        fields = "__all__"