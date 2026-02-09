from django.db.models import Count
from django.contrib.auth import get_user_model
from rest_framework import serializers

from boards_app.models import Board
from tasks_app.models import Task
from tasks_app.api.serializers import TaskReadSerializer

from .validators import validate_not_empty


User = get_user_model()


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "fullname"]


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

    owner_data = UserMiniSerializer(source="created_by", read_only=True)
    members_data = UserMiniSerializer(source="members", many=True, read_only=True)

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
            "owner_data",
            "members_data",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "members",
            "tasks",
        ]

    def _action(self):
        view = self.context.get("view")
        return getattr(view, "action", None) if view else None

    def _is_retrieve(self) -> bool:
        return self._action() == "retrieve"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        action = self._action()

        if action in ("update", "partial_update"):
            return {
                "id": data.get("id"),
                "title": data.get("title"),
                "member_count": data.get("member_count"),
                "ticket_count": data.get("ticket_count"),
                "tasks_to_do_count": data.get("tasks_to_do_count"),
                "tasks_high_prio_count": data.get("tasks_high_prio_count"),
                "owner_id": data.get("owner_id"),
                }
            

        if action != "retrieve":
            data.pop("members", None)
            data.pop("tasks", None)

        data.pop("owner_data", None)
        data.pop("members_data", None)
        return data

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
        qs = obj.tasks.all().select_related("assigned_to", "reviewer").annotate(
            comments_count=Count("task_comments")
            )
        return TaskReadSerializer(qs, many=True, context=self.context).data


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
