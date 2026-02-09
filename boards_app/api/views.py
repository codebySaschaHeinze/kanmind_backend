from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response


from boards_app.models import Board
from .permissions import IsBoardMemberOrCreator, IsBoardCreatorOnly
from .serializers import (
    BoardListSerializer,
    BoardDetailSerializer,
    BoardPatchResponseSerializer,
    BoardWriteSerializer,
)

User = get_user_model()

class BoardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsBoardMemberOrCreator]

    def get_queryset(self):
        user = self.request.user
        return (
            Board.objects.filter(Q(members=user) | Q(created_by=user))
            .select_related("created_by")
            .prefetch_related("members")
            .distinct()
        )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return BoardWriteSerializer
        if self.action == "retrieve":
            return BoardDetailSerializer
        return BoardListSerializer  # list

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsBoardCreatorOnly()]
        return [IsAuthenticated(), IsBoardMemberOrCreator()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        board = self.get_queryset().get(pk=response.data["id"])
        data = BoardListSerializer(board, context=self.get_serializer_context()).data
        return Response(data, status=status.HTTP_201_CREATED, headers=response.headers)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        board = self.get_object()
        data = BoardPatchResponseSerializer(board, context=self.get_serializer_context()).data
        return Response(data, status=response.status_code, headers=response.headers)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        board = self.get_object()
        data = BoardPatchResponseSerializer(board, context=self.get_serializer_context()).data
        return Response(data, status=response.status_code, headers=response.headers)

class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
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