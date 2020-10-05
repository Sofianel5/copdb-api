from django.shortcuts import render
from rest_framework import generics 
from rest_framework.views import APIView
from django.http import JsonResponse
from .models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import *
from cops.models import *
from cops.serializers import *
from rest_framework.exceptions import AuthenticationFailed
from .permissions import *
from .tasks import *
from django.contrib.auth import password_validation
from rest_framework.response import Response
from .utils import *
from drf_multiple_model.views import FlatMultipleModelAPIView
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination
import base64
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import logging
from geolocation.utils import get_client_ip
db_logger = logging.getLogger('db')

class LimitPagination(MultipleModelLimitOffsetPagination):
    default_limit = 30

class UsernameAvailable(APIView):
    def get(self, request):
        username = request.GET["username"].lower()
        return JsonResponse({"available": not Account.objects.filter(username=username).exists()})

class EmailAvailable(APIView):
    def get(self, request):
        email = request.GET["email"].lower()
        return JsonResponse({"available": not Account.objects.filter(email=email).exists()})

class PermissionsAddView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        permission =request.data["permission"]
        if permission == "location_always":
            user.location_always_permission = True
        elif permission == "location_while_using":
            user.location_while_using_permission = True
        elif permission == "contacts_permission":
            user.contacts_permission = True
        elif permission == "notifications_permission":
            user.notifications_permission = True
        user.save()
        return JsonResponse(InternalAccountSerializer(request.user).data)

class SetProfilePic(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        file_name = str(request.user.id)  + "-pfp.jpg"
        msg = base64.b64decode(request.POST["img"])
        f = io.BytesIO(msg)
        img = InMemoryUploadedFile(f, None, file_name, 'image/jpeg', sys.getsizeof(f), None)
        request.user.profile_pic = img 
        request.user.save()
        return JsonResponse(InternalAccountSerializer(request.user).data)
    
class FeedList(FlatMultipleModelAPIView):

    permission_classes = [IsAuthenticated]

    pagination_class = LimitPagination

    def initial(self, request, *args, **kwargs):
        super(FeedList, self).initial(request, *args, **kwargs)
        self.coords = get_coordinates(request)
        if request.GET.get("order_by") == "distance":
            self.querylist = [
                {'queryset': CopDBEvent.get_nearby_coords(self.coords.lat, self.coords.lng), 'serializer_class': CopDBEventSerializer},
                {'queryset': Complaint.get_nearby_coords(self.coords.lat, self.coords.lng), 'serializer_class': ComplaintSerializer},
            ]
        else:
            self.querylist = [
                {'queryset': CopDBEvent.objects.all(), 'serializer_class': CopDBEventSerializer},
                {'queryset': Complaint.objects.all(), 'serializer_class': ComplaintSerializer},
            ]

class NotificationsList(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def initial(self, request, *args, **kwargs):
        super(NotificationsList, self).initial(request, *args, **kwargs)
        process_request_data.delay(request.META['HTTP_LAT'], request.META["HTTP_LNG"], request.user.id)

    def get_queryset(self):
        return self.request.user.notifications.filter(sent=True)
        
class SecureCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, CreateAccessPermission]

class SecureCreateListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, CreateListAccessPermission]
    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(many=True, *args, **kwargs)

class ConnectionCreate(SecureCreateView):
    serializer_class = ConnectionSerializer

class NetworkInfoCreate(SecureCreateView):
    def create(self, request, *args, **kwargs):
        if request.data.get("ip_address") is None:
            request.data["ip_address"] = get_client_ip(request)
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            db_logger.exception(e)
            raise e
        if int(request.data["user"]) != request.user.id:
            return AuthenticationFailed()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    serializer_class = NetworkInfoSerializer

class AndroidDeviceCreate(SecureCreateView):
    serializer_class = AndroidDeviceSerializer

class iOSDeviceCreate(SecureCreateView):
    serializer_class = iOSDeviceSerializer

class LocationPingReport(SecureCreateView):
    def create(self, request, *args, **kwargs):
        db_logger.info(request.data)
        self.request.data["coordinates"] = {
            "lat": self.request.data["location"]["coords"]["latitude"],
            "lng": self.request.data["location"]["coords"]["longitude"]
        }
        self.request.data["timestamp"] = self.request.data["location"].get("timestamp")
        self.request.data["event"] = self.request.data["location"].get("event")
        self.request.data["altitude"] = self.request.data["location"]["coords"].get("altitude")
        self.request.data["battery"] = self.request.data["location"].get("battery")
        self.request.data["speed"] = self.request.data["location"]["coords"].get("speed")
        self.request.data["odometer"] = self.request.data["location"].get("odometer")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if int(request.data["user"]) != request.user.id:
            return AuthenticationFailed()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    serializer_class = LocationPingSerializer

class ContactUpload(SecureCreateListView):
    def handle_exception(self, exc):
        db_logger.exception(exc)
        return super(ContactUpload, self).handle_exception(exc)
    serializer_class = ContactSerializer

class ClipboardDataUpload(SecureCreateView):
    serializer_class = ClipboardDataSerializer
