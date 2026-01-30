from rest_framework.permissions import BasePermission


class IsTaskBoardMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.board.members.filter(id=request.user.id).exists()