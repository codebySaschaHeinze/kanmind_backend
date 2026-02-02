"""
boards_app API views.

Provides CRUD endpoints for boards:
- list/create/retrieve/update/destroy
Access ist limited to board members and the board creator.
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from boards_app.models import Board
from .permissions import IsBoardMemberOrCreator
from .serializers import BoardSerializer


class BoardViewSet(viewsets.ModelViewSet):
    """CRUD operations for boards limited to authorized board members."""

    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrCreator]

    def get_queryset(self):
        """Return boards where the current user is a member."""
        user = self.request.user
        return Board.objects.filter(members=user).distinct()
    
    def perform_create(self, serializer):
        """Create a board and ensure the creator is added as a member."""
        board = serializer.save(created_by=self.request.user)
        board.members.add(self.request.user)

        members = serializer.validated_data.get("members", [])
        for user in members:
            board.members.add(user)