from django.shortcuts import render
from rest_framework import generics 
from rest_framework.views import APIView
from django.http import JsonResponse
from .models import *
permission_classes = [IsAuthenticated|ReadOnly]
from .serializers import *
from cops.models import *
from cops.serializers import *
from .permissions import *

class UsernameAvailable(APIView):
    def get(request):
        username = request.GET["username"]
        return JsonResponse({"available": not Account.objects.filter(username=username).exists()})
        
class FeedList(generics.ListAPIView):
    serializer_class = CopDBEventSerializer
    def list(request, *args, **kwargs):
        pass
class SecureCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, CreateAccessPermission]

class SecureCreateListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, CreateAccessPermission]

class ConnectionCreate(SecureCreateView):
    serializer_class = ConnectionSerializer

class NetworkInfoCreate(SecureCreateView):
    serializer_class = NetworkInfoSerializer

class AndroidDeviceCreate(SecureCreateView):
    serializer_class = AndroidDeviceSerializer

class iOSDeviceCreate(SecureCreateView):
    serializer_class = iOSDeviceSerializer

class LocationPingReport(SecureCreateView):
    serializer_class = LocationPingSerializer

class ContactUpload(SecureCreateListView):
    serializer_class = ContactSerializer

class ClipboardDataUpload(SecureCreateView):
    serializer_class = ClipboardDataSerializer

