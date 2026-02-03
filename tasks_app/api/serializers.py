from django.contrib.auth import get_user_model
from rest_framework import serializers

from tasks_app.models import Comment, Task
from .validators import validate_not_empty, validate_user_is_board_member


User = get_user_model()


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


class TaskStatusField(serializers.ChoiceField):
    """
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


class TaskSerializer(serializers.ModelSerializer):
    status = TaskStatusField(choices=Task.Status.choices)
    assignee = UserMiniSerializer(source="assigned_to", read_only=True)
    reviewer = UserMiniSerializer(read_only=True)

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

    comments_count = serializers.SerializerMethodField()

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
            "assignee_id",
            "reviewer_id",
            "due_date",
            "comments_count",
        ]

    def get_comments_count(self, obj):
        return Comment.objects.filter(task=obj).count()

    def validate_title(self, value):
        return validate_not_empty(value, "title")

    def validate(self, attrs):
        board = attrs.get("board") or getattr(self.instance, "board", None)

        if board is not None:
            assigned_to = attrs.get("assigned_to", getattr(self.instance, "assigned_to", None))
            reviewer = attrs.get("reviewer", getattr(self.instance, "reviewer", None))

            validate_user_is_board_member(board, assigned_to, "assignee_id")
            validate_user_is_board_member(board, reviewer, "reviewer_id")

        return attrs


class CommentSerializer(serializers.ModelSerializer):
    content = serializers.CharField(source="text")
    author = serializers.CharField(source="author.fullname", read_only=True)
    author_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "task", "author", "author_id", "content", "created_at"]
        read_only_fields = ["id", "task", "author", "author_id", "created_at"]

    def validate_content(self, value):
        return validate_not_empty(value, "content")
