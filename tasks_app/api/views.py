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
from .permissions import IsTaskBoardMember, IsTaskOwnerOrBoardCreator, IsCommentAuthorOnly, IsTaskBoardMemberForComment
from .serializers import CommentReadSerializer, CommentWriteSerializer, TaskReadSerializer, TaskWriteSerializer


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

        response = super().create(request, *args, **kwargs)
        task_id = response.data.get("id")

        if task_id is None:
            return response 

        task = self.get_queryset().get(pk=task_id)
        read_data = TaskReadSerializer(task, context=self.get_serializer_context()).data
        return Response(read_data, status=status.HTTP_201_CREATED, headers=response.headers)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        task = self.get_object()
        read_data = TaskReadSerializer(task, context=self.get_serializer_context()).data
        return Response(read_data, status=response.status_code, headers=response.headers)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        task = self.get_object()
        read_data = TaskReadSerializer(task, context=self.get_serializer_context()).data
        return Response(read_data, status=response.status_code, headers=response.headers)
    
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

    permission_classes = [IsAuthenticated]

    def _get_task_id(self):
        return self.kwargs.get("task_id")

    def get_queryset(self):
        task_id = self._get_task_id()
        user = self.request.user

        if task_id is None:
            return Comment.objects.none()

        return (
            Comment.objects.filter(task_id=task_id)
            .filter(Q(task__board__members=user) | Q(task__board__created_by=user))
            .distinct()
            .order_by("created_at")
        )
    
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
        task_id = self._get_task_id()
        task = get_object_or_404(Task, pk=task_id)
        serializer.save(task=task, author=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        comment_id = response.data.get("id")

        if comment_id is None:
            return response

        comment = Comment.objects.get(pk=comment_id)
        read_data = CommentReadSerializer(comment, context=self.get_serializer_context()).data
        return Response(read_data, status=status.HTTP_201_CREATED, headers=response.headers)
    
    
