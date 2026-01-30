from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from boards_app.models import Board
from tasks_app.models import Task
from .serializers import TaskSerializer
from .permissions import IsTaskBoardMember


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMember]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(board__member=user).distinct()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
    
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
        
        if not board.members.filter(id=request.user.id).exists():
            return Response({"detail": "Du bist kein Board-Member."},
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