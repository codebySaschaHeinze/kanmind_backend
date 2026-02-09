"""
tasks_app API views.

Provides CRUD endpoints for tasks and comments.
"""

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from boards_app.models import Board
from tasks_app.models import Comment, Task
from .permissions import IsTaskBoardMember, IsTaskBoardMemberForComment
from .serializers import (
    CommentReadSerializer,
    CommentWriteSerializer,
    TaskReadSerializer,
    TaskWriteSerializer,
)


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD operations for tasks limited to authorized board members."""

    permission_classes = [IsAuthenticated, IsTaskBoardMember]

    def get_queryset(self):
        user = self.request.user
        return (
            Task.objects.filter(Q(board__members=user) | Q(board__created_by=user))
            .select_related("assigned_to", "reviewer", "board")
            .annotate(comments_count=Count("task_comments"))
            .distinct()
        )

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return TaskWriteSerializer
        return TaskReadSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        board_id = request.data.get("board")

        if not board_id:
            return Response(
                {"detail": "Ein Board ist erforderlich."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response(
                {"detail": "Board wurde nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_member = board.members.filter(id=request.user.id).exists()
        is_owner = (board.created_by_id == request.user.id)

        if not (is_member or is_owner):
            return Response(
            {"detail": "Du bist weder Board-Member noch Owner."},
            status=status.HTTP_403_FORBIDDEN,
        )

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="assigned-to-me")
    def assigned_to_me(self, request):
        queryset = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="reviewing")
    def reviewing(self, request):
        queryset = self.get_queryset().filter(reviewer=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CommentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """List, create, and delete comments nested under a task."""

    permission_classes = [IsAuthenticated, IsTaskBoardMemberForComment]

    def _get_task_id(self):
        return self.kwargs.get("task_id")

    def get_queryset(self):
        task_id = self._get_task_id()
        if task_id is None:
            return Comment.objects.none()

        return (
            Comment.objects.filter(task_id=task_id)
            .select_related("author", "task", "task__board")
            .order_by("id")
            )

    def get_serializer_class(self):
        if self.action == "create":
            return CommentWriteSerializer
        return CommentReadSerializer

    def perform_create(self, serializer):
        task = get_object_or_404(Task, pk=self.kwargs["task_id"])
        serializer.save(task=task, author=self.request.user)

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        comment = Comment.objects.select_related("author").get(pk=write_serializer.instance.pk)
        data = CommentReadSerializer(comment, context=self.get_serializer_context()).data
        return Response(data, status=status.HTTP_201_CREATED)
