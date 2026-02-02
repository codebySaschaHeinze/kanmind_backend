from rest_framework import serializers

from tasks_app.models import Comment, Task
from .validators import validate_not_empty, validate_user_is_board_member


class TaskSerializer(serializers.ModelSerializer):
    """Serialize tasks and validate task input."""
    
    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "assigned_to",
            "reviewer",
            "created_by",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "id", 
            "created_by", 
            "created_at", 
            "updated_at"
        ]
        
    def validate_title(self, value):
        """Ensure title is not blank."""
        return validate_not_empty(value, "title")
    
    def validate(self, attrs):
        board = attrs.get("board") or getattr(self.instance, "board", None)

        if board is not None:
            assigned_to = attrs.get("assigned_to", getattr(self.instance, "assigned_to", None))
            reviewer = attrs.get("reviewer", getattr(self.instance, "reviewer", None))

            validate_user_is_board_member(board, assigned_to,"assigned_to")
            validate_user_is_board_member(board, reviewer,"reviewer")
        
        return attrs
    

class CommentSerializer(serializers.ModelSerializer):
    """Serialize comments and validate comment input."""

    class Meta:
        model = Comment
        fields = [
            "id", 
            "task", 
            "author", 
            "text", 
            "created_at"]
        read_only_fields = [
            "id", 
            "task", 
            "author", 
            "created_at"]
        
    def validate_text(self, value):
        """Ensure comment is not blank."""
        return validate_not_empty(value, "text")