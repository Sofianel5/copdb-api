from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer, TokenSerializer
from .models import *
from geolocation.serializers import *
import uuid
import base64
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ('username', 'email', 'first_name', 'last_name', 'dob', 'profile_pic', 'password')

class ExternalAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account 
        fields = ["id", "first_name", "last_name", "verified", "username", "profile_pic", "date_joined"]

class InternalAccountSerializer(serializers.ModelSerializer):
    following = ExternalAccountSerializer(many=True)
    followers = ExternalAccountSerializer(many=True)
    friends = ExternalAccountSerializer(many=True)
    auth_token = serializers.CharField()
    class Meta:
        model = Account
        exclude = ["password", "is_staff", "last_login", "is_admin", "is_active", "sex"]
        depth = 2

class NetworkInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkInfo 
        fields = "__all__"

class AndroidDeviceSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default="Android")
    class Meta:
        model = AndroidDevice 
        fields = "__all__"
    def create(self, validated_data):
        android_id, user = validated_data["android_id"], validated_data["user"]
        del validated_data["user"]
        del validated_data["android_id"]
        instance, _ = AndroidDevice.objects.update_or_create(android_id=android_id, user=user, defaults=validated_data)
        return instance

class iOSDeviceSerializer(serializers.ModelSerializer):
    type = serializers.CharField(default="iOS")
    class Meta:
        model = iOSDevice 
        fields = "__all__"
    
    def create(self, validated_data):
        identifier_for_vendor, user = validated_data["identifier_for_vendor"], validated_data["user"]
        del validated_data["user"]
        del validated_data["identifier_for_vendor"]
        instance, _ = iOSDevice.objects.update_or_create(identifier_for_vendor=identifier_for_vendor, user=user, defaults=validated_data)
        return instance

class BatterySerializer(serializers.ModelSerializer):
    class Meta:
        model = Battery 
        fields = "__all__"

class LocationPingSerializer(serializers.ModelSerializer):
    coordinates = CoordinatesSerializer()
    battery = BatterySerializer()
    class Meta:
        model = LocationPing  
        fields = "__all__"
    
    def create(self, validated_data):
        coordinates = CoordinatesSerializer().create(validated_data["coordinates"])
        validated_data["coordinates"] = coordinates
        battery = BatterySerializer().create(validated_data["battery"])
        validated_data["battery"] = battery
        instance = LocationPing.objects.create(**validated_data)
        return instance

class ContactEmailSerializer(serializers.ModelSerializer):
    contact = serializers.PrimaryKeyRelatedField(read_only=True, required=False, allow_null=True)
    class Meta:
        model = ContactEmail  
        fields = "__all__"

class ContactPhoneSerializer(serializers.ModelSerializer):
    contact = serializers.PrimaryKeyRelatedField(read_only=True, required=False, allow_null=True)
    class Meta:
        model = ContactPhone  
        fields = "__all__"

class ContactAddressSerializer(serializers.ModelSerializer):
    contact = serializers.PrimaryKeyRelatedField(read_only=True, required=False, allow_null=True)
    class Meta:
        model = ContactAddress  
        fields = "__all__"

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification 
        fields = ["image", "title", "body", "sent_at"]

class ContactSerializer(serializers.ModelSerializer):
    addresses = ContactAddressSerializer(many=True, required=False, allow_null=True)
    emails = ContactEmailSerializer(many=True, required=False, allow_null=True)
    phones = ContactPhoneSerializer(many=True, required=False, allow_null=True)
    referenced_user = ExternalAccountSerializer(read_only=True)
    avatar_base64 = serializers.CharField(write_only=True, allow_null=True)
    class Meta:
        model = Contact
        fields = "__all__"
    def create(self, validated_data):
        file_name = str(uuid.uuid4()) + "-contact.jpg"
        if validated_data["avatar_base64"] is not None:
            msg = base64.b64decode(validated_data["avatar_base64"])
            f = io.BytesIO(msg)
            img = InMemoryUploadedFile(f, None, file_name, 'image/jpeg', sys.getsizeof(f), None)
        else:
            img = None
        emails = validated_data["emails"]
        phones = validated_data["phones"]
        addresses = validated_data["addresses"]
        display_name, user = validated_data["display_name"], validated_data["user"]
        del validated_data["emails"]
        del validated_data["phones"] 
        del validated_data["addresses"]
        del validated_data["avatar_base64"]
        del validated_data["display_name"]
        del validated_data["user"]
        validated_data["avatar"] = img
        instance, _ = Contact.objects.update_or_create(display_name=display_name, user=user, defaults=validated_data)
        for data in emails:
            data["contact"] = instance
            ContactEmailSerializer().create(data)
        for data in phones:
            data["contact"] = instance 
            ContactPhoneSerializer().create(data)
        for data in addresses:
            data["contact"] = instance
            ContactAddressSerializer().create(data)
        return instance

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