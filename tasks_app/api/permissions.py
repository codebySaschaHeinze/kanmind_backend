"""
tasks_app API permissions.

This module contains permission classes used by tasks_app API views.
"""

from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission

from tasks_app.models import Task


class IsTaskBoardMember(BasePermission):
    """Allow object access if the user is a board member or the board creator."""

    def has_object_permission(self, request, view, obj):
        """Return True if user is board creator or board member."""
        user_id = request.user.id
        board = obj.board
        return board.created_by_id == user_id or board.members.filter(id=user_id).exists()


class IsTaskBoardMemberForComment(BasePermission):
    """Allow access if user is member or creator of the task's board."""

    def has_permission(self, request, view):
        task_id = view.kwargs.get("task_id")
        if not task_id:
            return False

        try:
            task = Task.objects.select_related("board").get(pk=task_id)
        except Task.DoesNotExist:
            raise NotFound("Task wurde nicht gefunden.")

        user_id = request.user.id
        board = task.board
        return board.created_by_id == user_id or board.members.filter(id=user_id).exists()
    

class IsTaskOwnerOrBoardCreator(BasePermission):
    """Allow delete if user created the task or created the board."""

    def has_object_permission(self, request, view, obj):
        user_id = request.user.id
        return obj.created_by_id == user_id or obj.board.created_by_id == user_id
