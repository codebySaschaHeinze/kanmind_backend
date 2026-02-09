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

from tasks_app.models import Comment, Task
from .permissions import (
    IsCommentAuthorOnly,
    IsTaskBoardMember,
    IsTaskBoardMemberForComment,
    IsTaskOwnerOrBoardCreator,
)
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

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsTaskOwnerOrBoardCreator()]
        return [IsAuthenticated(), IsTaskBoardMember()]

    def create(self, request, *args, **kwargs):
        if not request.data.get("board"):
            return Response(
                {"detail": "Ein Board ist erforderlich."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        response = super().create(request, *args, **kwargs)
        task = self.get_queryset().get(pk=response.data["id"])
        read_data = TaskReadSerializer(
            task, context=self.get_serializer_context()
        ).data
        return Response(read_data, status=status.HTTP_201_CREATED, headers=response.headers)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        task = self.get_object()
        read_data = TaskReadSerializer(
            task, context=self.get_serializer_context()
        ).data
        return Response(read_data, status=response.status_code, headers=response.headers)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        task = self.get_object()
        read_data = TaskReadSerializer(
            task, context=self.get_serializer_context()
        ).data
        return Response(read_data, status=response.status_code, headers=response.headers)

    @action(detail=False, methods=["get"], url_path="assigned-to-me")
    def assigned_to_me(self, request):
        queryset = self.get_queryset().filter(assigned_to=request.user)
        serializer = TaskReadSerializer(
            queryset, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="reviewing")
    def reviewing(self, request):
        queryset = self.get_queryset().filter(reviewer=request.user)
        serializer = TaskReadSerializer(
            queryset, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)


class CommentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """List, create, and delete comments nested under a task."""

    def _get_task_id(self):
        return self.kwargs.get("task_id")

    def _get_task(self):
        user = self.request.user
        task_id = self._get_task_id()

        return get_object_or_404(
            Task.objects.filter(Q(board__members=user) | Q(board__created_by=user)),
            pk=task_id,
        )

    def get_queryset(self):
        task = self._get_task()
        return Comment.objects.filter(task=task).order_by("created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return CommentWriteSerializer
        return CommentReadSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAuthenticated(), IsCommentAuthorOnly()]
        if self.action in ("list", "create"):
            return [IsAuthenticated(), IsTaskBoardMemberForComment()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        task = self._get_task()
        serializer.save(task=task, author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        comment = serializer.instance
        read_data = CommentReadSerializer(
            comment, context=self.get_serializer_context()
        ).data
        return Response(read_data, status=status.HTTP_201_CREATED)
