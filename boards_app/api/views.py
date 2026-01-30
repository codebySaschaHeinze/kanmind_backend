from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from boards_app.models import Board
from .serializers import BoardSerializer
from .permissions import IsBoardMemberOrCreator

class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrCreator]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(members=user).distinct()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context