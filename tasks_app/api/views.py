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
from .permissions import IsTaskBoardMember, IsTaskBoardMemberForComment, IsTaskOwnerOrBoardCreator
from .serializers import (
    CommentReadSerializer,
    CommentWriteSerializer,
    TaskPatchResponseSerializer,
    TaskReadSerializer,
    TaskWriteSerializer,
)


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD operations for tasks limited to authorized board members."""


    def get_queryset(self):
        user = self.request.user

        base = (
            Task.objects
            .select_related("assigned_to", "reviewer", "board")
            .annotate(comments_count=Count("task_comments"))
        )

        if self.action == "list":
            return (
                base.filter(Q(board__members=user) | Q(board__created_by=user))
                .distinct()
            )

        return base

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return TaskWriteSerializer
        return TaskReadSerializer
    
    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsTaskOwnerOrBoardCreator()]
        return [IsAuthenticated(), IsTaskBoardMember()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        board_id = request.data.get("board")

        if not board_id:
            return Response({"detail": "Ein Board ist erforderlich."},
                        status=status.HTTP_400_BAD_REQUEST)

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return Response({"detail": "Board wurde nicht gefunden."},
                        status=status.HTTP_404_NOT_FOUND)

        is_member = board.members.filter(id=request.user.id).exists()
        is_owner = (board.created_by_id == request.user.id)

        if not (is_member or is_owner):
            return Response({"detail": "Du bist weder Board-Member noch Owner."},
                        status=status.HTTP_403_FORBIDDEN)

        write_serializer = TaskWriteSerializer(
            data=request.data,
            context=self.get_serializer_context()
        )
        write_serializer.is_valid(raise_exception=True)
        task = write_serializer.save(created_by=request.user)

        task = self.get_queryset().get(pk=task.pk)

        read_data = TaskReadSerializer(
            task,
            context=self.get_serializer_context()
        ).data

        headers = self.get_success_headers(read_data)
        return Response(read_data, status=status.HTTP_201_CREATED, headers=headers)
    
    def partial_update(self, request, *args, **kwargs):
        """Partially update a task and return a contract-compliant response."""
        response = super().partial_update(request, *args, **kwargs)

        task = self.get_queryset().get(pk=self.get_object().pk)
        data = TaskPatchResponseSerializer(task, context=self.get_serializer_context()).data

        return Response(data, status=response.status_code, headers=response.headers)


    def update(self, request, *args, **kwargs):
        """Update a task and return a contract-compliant response."""
        response = super().update(request, *args, **kwargs)

        task = self.get_queryset().get(pk=self.get_object().pk)
        data = TaskPatchResponseSerializer(task, context=self.get_serializer_context()).data

        return Response(data, status=response.status_code, headers=response.headers)

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
