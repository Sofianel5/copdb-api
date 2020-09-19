from rest_framework import serializers
from .models import *
from geolocation.serializers import *
from users.serializers import ExternalAccountSerializer

class PoliceDepartmentSerializer(serializers.ModelSerializer):
    city = CopDBCitySerializer()
    type=serializers.ReadOnlyField(default="PoliceDepartment")
    class Meta:
        model = PoliceDepartment
        fields = "__all__"

class PrecinctSerializer(serializers.ModelSerializer):
    police_department = PoliceDepartmentSerializer()
    coordinates = CoordinatesSerializer()
    address = AddressSerializer()
    type=serializers.ReadOnlyField(default="Precinct")
    class Meta:
        model = Precinct
        fields = "__all__"

class CopSerializer(serializers.ModelSerializer):
    precinct = PrecinctSerializer()
    type=serializers.ReadOnlyField(default="Cop")
    class Meta:
        model = Cop
        fields = "__all__"

class ComplaintSerializer(serializers.ModelSerializer):
    cop = CopSerializer()
    type=serializers.ReadOnlyField(default="Complaint")
    class Meta:
        model = Complaint
        fields = "__all__"

class CopDBComplaintSerializer(ComplaintSerializer):
    coordinates = CoordinatesSerializer()
    complainant_account = ExternalAccountSerializer()
    type=serializers.ReadOnlyField(default="CopDBComplaint")
    class Meta:
        model = CopDBComplaint
        exclude = ["verified"]

class CopDBEventSerializer(serializers.ModelSerializer):
    num_shares = serializers.ReadOnlyField()
    num_promotions = serializers.ReadOnlyField()
    complaint = CopDBComplaintSerializer()
    type=serializers.ReadOnlyField(default="CopDBEvent")
    date=serializers.ReadOnlyField()
    class Meta:
        model = CopDBEvent
        exclude = ["sharers", "promoters"]