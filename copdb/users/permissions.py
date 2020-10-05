from rest_framework import permissions
from rest_framework import generics
import logging
db_logger = logging.getLogger('db')

class CreateAccessPermission(permissions.BasePermission):
    message = 'wrong_user'
    def has_permission(self, request, view):
        db_logger.info(request.data)
        return int(request.data["user"]) == request.user.id

class CreateListAccessPermission(permissions.BasePermission):
    message = "wrong_user"
    def has_permission(self, request, view):
        db_logger.info(request.data)
        for obj in request.data:
            if not int(obj["user"]) == request.user.id:
                return False 
        return True