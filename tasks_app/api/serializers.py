"""
tasks_app API serializers.

This module contains serializers for the tasks_app API.

"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from tasks_app.models import Comment, Task
from .validators import validate_not_empty, validate_user_is_board_member


User = get_user_model()


class UserMiniSerializer(serializers.ModelSerializer):
    """Minimal user representation used inside task responses."""

    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class TaskStatusField(serializers.ChoiceField):
    """
    Map frontend status values to model values and back.

    Frontend: to-do | in-progress | review | done
    Model:    todo  | in_progress | review | done
    """

    def to_internal_value(self, data):
        mapping = {
            "to-do": "todo",
            "in-progress": "in_progress",
        }
        return super().to_internal_value(mapping.get(data, data))

    def to_representation(self, value):
        reverse = {
            "todo": "to-do",
            "in_progress": "in-progress",
        }
        return super().to_representation(reverse.get(value, value))


class TaskReadSerializer(serializers.ModelSerializer):
    """Response serializer for GET /api/tasks/ and GET /api/tasks/<id>/."""

    status = TaskStatusField(choices=Task.Status.choices)
    assignee = UserMiniSerializer(source="assigned_to", read_only=True)
    reviewer = UserMiniSerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
            "comments_count",
        ]


class TaskWriteSerializer(serializers.ModelSerializer):
    """Input serializer for POST /api/tasks/ and PATCH /api/tasks/<id>/."""

    status = TaskStatusField(choices=Task.Status.choices)

    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assigned_to",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source="reviewer",
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "priority",
            "assignee_id",
            "reviewer_id",
            "due_date",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        return validate_not_empty(value, "title")

    def validate(self, attrs):
        board = attrs.get("board") or getattr(self.instance, "board", None)
        if board is None:
            return attrs

        assigned_to = attrs.get("assigned_to", getattr(self.instance, "assigned_to", None))
        reviewer = attrs.get("reviewer", getattr(self.instance, "reviewer", None))

        validate_user_is_board_member(board, assigned_to, "assignee_id")
        validate_user_is_board_member(board, reviewer, "reviewer_id")

        return attrs
    
    
class TaskPatchResponseSerializer(TaskReadSerializer):
    """Response serializer for PATCH/PUT /api/tasks/<id>/."""

    class Meta(TaskReadSerializer.Meta):
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "reviewer",
            "due_date",
        ]


class CommentReadSerializer(serializers.ModelSerializer):
    """Response serializer for task comments."""

    author = serializers.CharField(source="author.fullname", read_only=True)
    content = serializers.CharField(source="text", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "created_at", "author", "content"]


class CommentWriteSerializer(serializers.ModelSerializer):
    """Input serializer for creating a comment."""

    content = serializers.CharField(source="text")

    class Meta:
        model = Comment
        fields = ["content"]

    def validate_content(self, value):
        return validate_not_empty(value, "content")
