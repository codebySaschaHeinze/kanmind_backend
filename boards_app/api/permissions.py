from rest_framework.permissions import BasePermission


class IsBoardMemberOrCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.created_by.id == request.user.id:
            return True
        
        return obj.members.filter(id=request.user.id).exists()