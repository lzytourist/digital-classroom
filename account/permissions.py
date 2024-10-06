from rest_framework.permissions import BasePermission

from account.models import User


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == User.UserType.ADMIN


class IsAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == User.UserType.TEACHER or request.user.user_type == User.UserType.ADMIN

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == User.UserType.ADMIN:
            return True
        return request.user == obj.teacher
