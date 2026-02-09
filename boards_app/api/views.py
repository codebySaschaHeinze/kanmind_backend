"""
boards_app API views.

This module provides endpoints for board management and related helpers.

View classes:
- BoardViewSet:
  CRUD for boards with access limited to board members or the board creator.
  Responses are aligned with the endpoint documentation by returning different
  serializers for list/retrieve and for create/update responses.

- EmailCheckView:
  Helper endpoint to look up a user by email (case-insensitive). Requires
  authentication and returns a minimal user payload on success.
"""

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from boards_app.models import Board
from .permissions import IsBoardCreatorOnly, IsBoardMemberOrCreator
from .serializers import (
    BoardDetailSerializer,
    BoardListSerializer,
    BoardPatchResponseSerializer,
    BoardWriteSerializer,
)

User = get_user_model()


class BoardViewSet(viewsets.ModelViewSet):
    """CRUD operations for boards limited to authorized users."""

    permission_classes = [IsAuthenticated, IsBoardMemberOrCreator]

    def get_queryset(self):
        """Return boards where the requesting user is a member or creator."""
        user = self.request.user
        return (
            Board.objects.filter(Q(members=user) | Q(created_by=user))
            .select_related("created_by")
            .prefetch_related("members")
            .distinct()
        )

    def get_serializer_class(self):
        """Select the serializer based on the current action."""
        if self.action in ("create", "update", "partial_update"):
            return BoardWriteSerializer
        if self.action == "retrieve":
            return BoardDetailSerializer
        return BoardListSerializer

    def get_permissions(self):
        """Use stricter permissions for destructive actions."""
        if self.action == "destroy":
            return [IsAuthenticated(), IsBoardCreatorOnly()]
        return [IsAuthenticated(), IsBoardMemberOrCreator()]

    def perform_create(self, serializer):
        """Assign the current user as the board creator."""
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a board and return a contract-compliant response."""
        response = super().create(request, *args, **kwargs)
        board = self.get_queryset().get(pk=response.data["id"])
        data = BoardListSerializer(
            board, context=self.get_serializer_context()
        ).data
        return Response(
            data, status=status.HTTP_201_CREATED, headers=response.headers
        )

    def partial_update(self, request, *args, **kwargs):
        """Partially update a board and return a contract-compliant response."""
        response = super().partial_update(request, *args, **kwargs)
        board = self.get_object()
        data = BoardPatchResponseSerializer(
            board, context=self.get_serializer_context()
        ).data
        return Response(
            data, status=response.status_code, headers=response.headers
        )

    def update(self, request, *args, **kwargs):
        """Update a board and return a contract-compliant response."""
        response = super().update(request, *args, **kwargs)
        board = self.get_object()
        data = BoardPatchResponseSerializer(
            board, context=self.get_serializer_context()
        ).data
        return Response(
            data, status=response.status_code, headers=response.headers
        )


class EmailCheckView(APIView):
    """Check whether a user exists for a given email (query param: ?email=...)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Handle GET requests for email lookups."""
        email = (request.query_params.get("email") or "").strip()

        if not email or "@" not in email:
            return Response(
                {"detail": "email query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Email not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"id": user.id, "email": user.email, "fullname": user.fullname},
            status=status.HTTP_200_OK,
        )
