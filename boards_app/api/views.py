"""
boards_app API views.

Provides CRUD endpoints for boards and email-check:
- list/create/retrieve/update/destroy

Access is limited to board members and the board creator.
"""

from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from boards_app.models import Board
from .permissions import IsBoardMemberOrCreator
from .serializers import BoardReadSerializer, BoardWriteSerializer

User = get_user_model()


class BoardViewSet(viewsets.ModelViewSet):
    """CRUD operations for boards limited to authorized board members."""

    permission_classes = [IsAuthenticated, IsBoardMemberOrCreator]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(members=user) | Q(created_by=user)).distinct()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return BoardWriteSerializer
        return BoardReadSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        board_id = response.data.get("id")

        if board_id is None:
            return response

        board = self.get_queryset().get(pk=board_id)
        read_data = BoardReadSerializer(board, context=self.get_serializer_context()).data
        return Response(read_data, status=status.HTTP_201_CREATED, headers=response.headers)


    def perform_update(self, serializer):
        serializer.save()


class EmailCheckView(APIView):
    """Return basic user info for a given email address."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response(
                {"detail": "Bitte gib eine E-Mail-Adresse an."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Benutzer wurde nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"id": user.id, "email": user.email, "fullname": user.fullname},
            status=status.HTTP_200_OK,
        )
