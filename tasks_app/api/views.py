"""
tasks_app API views.

Provides CRUD endpoints for tasks and comments:
- list/create/retrieve/update/destroy
Access is limited to board members and the board creator.
"""

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets

from boards_app.models import Board
from .permissions import IsTaskBoardMember
from .serializers import CommentSerializer, TaskSerializer
from tasks_app.models import Comment, Task


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD operations for tasks limited to authorized board members."""

    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMember]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(board__members=user).distinct()
    
    def perform_create(self, serializer):
        """Create a task and set the creator automatically."""
        serializer.save(created_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        board_id = request.data.get("board")
        
        if not board_id:
            return Response(
                {"detail": "Ein Board ist erforderlich."}, 
                status=status.HTTP_400_BAD_REQUEST)
        
        try:
            board = Board.objects.get(id=board_id)
        
        except Board.DoesNotExist:
            return Response(
                {"detail": "Board wurde nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND)
        
        if not board.members.filter(id=request.user.id).exists():
            return Response(
                {"detail": "Du bist kein Board-Member."},
                status=status.HTTP_403_FORBIDDEN)
        
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


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs["task_id"]
        user = self.request.user
        return Comment.objects.filter(task_id=task_id, task__board__members=user)
    
    def create(self, request, *args, **kwargs):
        task_id = self.kwargs["task_id"]
        user = request.user

        try:
            task = Task.objects.get(id=task_id)

        except Task.DoesNotExist:
            return Response(
                {"detail": "Task wurde nicht gefunden."},
                status=status.HTTP_404_NOT_FOUND)
        
        if not task.board.members.filter(id=user.id).exists():
            return Response(
                {"detail": "Du bist kein Board-Member."},
                status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, author=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
