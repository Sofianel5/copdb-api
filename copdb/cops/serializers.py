from rest_framework import serializers
from .models import *

class Cop(serializers.ModelSerializer):
    class Meta:
        model = Cop
        fields = "__all__"

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = "__all__"

class CopDBComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = CopDBComplaint
        fields = "__all__"

class CopDBEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CopDBEvent
        fields = "__all__"