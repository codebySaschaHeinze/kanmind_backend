from rest_framework.permissions import BasePermission

class IsBoardMemberOrCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by_id == request.user.id or obj.members.filter(id=request.user.id).exists()

class IsBoardCreatorOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by_id == request.user.id
