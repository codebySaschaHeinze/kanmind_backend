from rest_framework.permissions import BasePermission


class IsTaskBoardMember(BasePermission):
    """Allow access if the user is board member or board owner."""

    def has_object_permission(self, request, view, obj):
        user_id = request.user.id
        return (
            obj.board.created_by_id == user_id
            or obj.board.members.filter(id=user_id).exists()
        )