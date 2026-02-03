"""
boards_app API views.

Provides CRUD endpoints for boards:
- list/create/retrieve/update/destroy
Access ist limited to board members and the board creator.
"""

from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from rest_framework.response import Response

from rest_framework import viewsets


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


User = get_user_model()


class EmailCheckView(APIView):
    """Return basic user info for a given email address."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response({"detail": "Bitte gib eine E-Mail-Adresse an."},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            return Response(
                {"id": user.id, "email": user.email, "fullname": user.fullname},
                status=status.HTTP_200_OK,
            )
           
        except User.DoesNotExist:
            return Response({"detail": "Benutzer wurde nicht gefunden."}, 
                status=status.HTTP_404_NOT_FOUND)