from django.db.models import Q
from rest_framework.permissions import BasePermission

from boards_app.models import Board
from tasks_app.models import Task


class IsTaskBoardMember(BasePermission):
    """Allow access if the user is board member or board owner."""


    def has_permission(self, request, view):
        if getattr(view, "action", None) != "create":
            return True

        board_id = request.data.get("board")
        if not board_id:
            return True 

        return Board.objects.filter(pk=board_id).filter(
            Q(members=request.user) | Q(created_by=request.user)
        ).exists()

    def has_object_permission(self, request, view, obj):
        user_id = request.user.id
        return (
            obj.board.created_by_id == user_id
            or obj.board.members.filter(id=user_id).exists()
        )


class IsTaskOwnerOrBoardCreator(BasePermission):
    """Allow delete if user created the task or created the board."""

    def has_object_permission(self, request, view, obj):
        user_id = request.user.id
        return obj.created_by_id == user_id or obj.board.created_by_id == user_id


class IsCommentAuthorOnly(BasePermission):
    """Allow delete only for the comment author."""


    def has_object_permission(self, request, view, obj):
        return obj.author_id == request.user.id


class IsTaskBoardMemberForComment(BasePermission):
    """Allow comment access only if user is member/owner of the task's board."""


    def has_permission(self, request, view):
        task_id = view.kwargs.get("task_id")
        if not task_id:
            return False

        return Task.objects.filter(pk=task_id).filter(
            Q(board__members=request.user) | Q(board__created_by=request.user)
        ).exists()
