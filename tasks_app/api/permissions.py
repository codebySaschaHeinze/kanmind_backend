from rest_framework.permissions import BasePermission


class IsTaskBoardMember(BasePermission):
    """Allow access if the user is board member."""

    def has_object_permission(self, request, view, obj):
        return obj.board.members.filter(id=request.user.id).exists()