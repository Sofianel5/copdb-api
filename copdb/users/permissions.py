from rest_framework import permissions
rom rest_framework import generics

class CreateAccessPermission(permissions.BasePermission):
    message = 'wrong_user'
    def has_permission(self, request, view):
        if view is generics.CreateAPIView:
            return request.POST["user"] == request.user.id