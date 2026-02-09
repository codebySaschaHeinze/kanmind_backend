from django.contrib.auth import get_user_model
from rest_framework import serializers

from boards_app.models import Board
from tasks_app.models import Task
from tasks_app.api.serializers import TaskReadSerializer

from .validators import validate_not_empty

User = get_user_model()


class BoardReadSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for boards.

    Used for:
    - GET /api/boards/          (list)
    - GET /api/boards/<id>/     (retrieve)

    Always returns counts + owner_id.
    Returns members + tasks only for retrieve (to keep list lightweight).
    """

    owner_id = serializers.IntegerField(source="created_by_id", read_only=True)

    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    members = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "owner_id",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "members",
            "tasks",
        ]

    def _is_retrieve(self) -> bool:
        """Return True if the current view action is 'retrieve'."""
        view = self.context.get("view")
        return bool(view and getattr(view, "action", None) == "retrieve")

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status=Task.Status.TODO).count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority=Task.Priority.HIGH).count()

    def get_members(self, obj):
        if not self._is_retrieve():
            return []
        return [
            {"id": u.id, "email": u.email, "fullname": u.fullname}
            for u in obj.members.all()
        ]

    def get_tasks(self, obj):
        if not self._is_retrieve():
            return []
        return TaskReadSerializer(obj.tasks.all(), many=True).data


class BoardWriteSerializer(serializers.ModelSerializer):
    """
    Write serializer for boards.

    Used for:
    - POST  /api/boards/        (create)
    - PATCH /api/boards/<id>/   (partial_update)

    Accepts:
    - title (string)
    - members (list[int])  -> user ids (frontend sends ids)
    """

    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
    )

    class Meta:
        model = Board
        fields = ["id", "title", "members"]
        read_only_fields = ["id"]

    def validate_title(self, value):
        return validate_not_empty(value, "title")
    
    def create(self, validated_data):
        members = validated_data.pop("members", [])
        board = Board.objects.create(**validated_data)
        if members:
            board.members.set(members)
        return board

    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if members is not None:
            instance.members.set(members)

        return instance
