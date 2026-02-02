from django.contrib.auth import get_user_model
from rest_framework import serializers
from boards_app.models import Board
from .validators import validate_not_empty

User = get_user_model()


class BoardSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
    )

    class Meta:

        model = Board
        fields = ["id", "title", "created_by", "members", "created_at"]
        read_only_fields = ["id", "created_by", "created_at"]

    def create(self, validated_data):
        members = validated_data.pop("members", [])
        request = self.context["request"]
        board = Board.objects.create(created_by=request.user, **validated_data)
        board.members.add(request.user)
        for user in members:
            board.members.add(user)
        return board
    
    
    def validate_title(self, value):
        return validate_not_empty(value, "title")