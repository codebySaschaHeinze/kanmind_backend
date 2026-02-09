"""
tasks_app API permissions.

This module contains permission classes used by tasks_app API views.
"""

from rest_framework.permissions import BasePermission


class IsTaskBoardMember(BasePermission):
    """Allow object access if the user is a board member or the board creator."""

    def has_object_permission(self, request, view, obj):
        """Return True if user is board creator or board member."""
        user_id = request.user.id
        board = obj.board
        return board.created_by_id == user_id or board.members.filter(id=user_id).exists()


class IsTaskBoardMemberForComment(BasePermission):
    """Allow access to comments if the user is a board member or board creator."""

    def has_permission(self, request, view):
        """Allow only authenticated users to access this endpoint."""
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Return True if user is board creator or board member."""
        user_id = request.user.id
        board = obj.task.board
        return board.created_by_id == user_id or board.members.filter(id=user_id).exists()
