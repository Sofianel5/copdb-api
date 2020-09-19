from django.shortcuts import render
from rest_framework import generics 
from rest_framework.views import APIView
from django.http import JsonResponse
from .models import *
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from cops.models import *
from cops.serializers import *
from .permissions import *
from .tasks import *
from django.contrib.auth import password_validation
from .utils import *
from drf_multiple_model.views import FlatMultipleModelAPIView
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination
import base64
import io
from PIL import Image
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class LimitPagination(MultipleModelLimitOffsetPagination):
    default_limit = 30

class UsernameAvailable(APIView):
    def get(self, request):
        username = request.GET["username"]
        return JsonResponse({"available": not Account.objects.filter(username=username).exists()})

class EmailAvailable(APIView):
    def get(self, request):
        username = request.GET["email"]
        return JsonResponse({"available": not Account.objects.filter(email=email).exists()})

class PermissionsAddView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        permission =request.POST["permission"]
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
