from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("list/", views.CopsListView.as_view()),
    path("report/", views.ReportCreationView.as_view()),
]