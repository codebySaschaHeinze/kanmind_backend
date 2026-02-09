"""
boards_app API permissions.

This module contains permission classes used by boards_app API views.
"""

from rest_framework.permissions import BasePermission


class IsBoardMemberOrCreator(BasePermission):
    """Allow object access if the user is the board creator or a board member."""

    def has_object_permission(self, request, view, obj):
        """Return True if user is board creator or board member."""
        user_id = request.user.id
        return obj.created_by_id == user_id or obj.members.filter(id=user_id).exists()


class IsBoardCreatorOnly(BasePermission):
    """Allow object access only if the user is the board creator (owner)."""

    def has_object_permission(self, request, view, obj):
        """Return True if user is the board creator."""
        return obj.created_by_id == request.user.id
