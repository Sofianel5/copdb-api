from rest_framework import serializers
from .models import * 

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"

class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = "__all__"

class CopDBCitySerializer(serializers.ModelSerializer):
    hq = AddressSerializer()
    epicenter = CoordinatesSerializer()
    class Meta:
        model = CopDBCity
        fields = "__all__"