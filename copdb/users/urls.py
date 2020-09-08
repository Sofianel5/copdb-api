from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("auth/", include('djoser.urls')),
    path("auth/", include("djoser.urls.authtoken")),
    path("username-available/", views.UsernameAvailable.as_view()),
    path("feed/", views.FeedList.as_view()),
    path("data/connection/", views.ConnectionCreate.as_view()),
    path("data/network-info/", views.NetworkInfoCreate.as_view()),
    path("data/device/android/", views.AndroidDeviceCreate.as_view()),
    path("data/device/ios/", views.iOSDeviceCreate.as_view()),
    path("data/locationreport/", views.LocationPingReport.as_view()),
    path("data/contacts/", views.ContactUpload.as_view()),
    path("data/clipboard/", views.ClipboardDataUpload.as_view()),
]