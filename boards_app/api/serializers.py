from django.contrib.auth import get_user_model
from rest_framework import serializers

from boards_app.models import Board
from tasks_app.models import Task
from tasks_app.api.serializers import TaskSerializer

from .validators import validate_not_empty


User = get_user_model()


class BoardListSerializer(serializers.ModelSerializer):
    """Board summary for GET/POST /api/boards/ (counts + owner_id)."""

    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source="created_by_id", read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "member_count",
            "ticket_count",
            "tasks_to_do_count",
            "tasks_high_prio_count",
            "owner_id",
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status=Task.Status.TODO).count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority=Task.Priority.HIGH).count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """Board detail for GET /api/boards/{board_id}/ (members + tasks)."""

    owner_id = serializers.IntegerField(source="created_by_id", read_only=True)
    members = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]

    def get_members(self, obj):
        return [
            {"id": u.id, "email": u.email, "fullname": u.fullname}
            for u in obj.members.all()
        ]

    def get_tasks(self, obj):
        return TaskSerializer(obj.tasks.all(), many=True).data


class BoardUpdateSerializer(serializers.ModelSerializer):
    """PATCH /api/boards/{board_id}/ response with owner_data + members_data."""

    owner_data = serializers.SerializerMethodField()
    members_data = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members_data"]

    def get_owner_data(self, obj):
        u = obj.created_by
        return {"id": u.id, "email": u.email, "fullname": u.fullname}

    def get_members_data(self, obj):
        return [
            {"id": u.id, "email": u.email, "fullname": u.fullname}
            for u in obj.members.all()
        ]
