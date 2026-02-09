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


# ✅ GET /api/boards/  +  POST /api/boards/ (Response)
class BoardListSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="created_by_id", read_only=True)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

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


# ✅ GET /api/boards/{board_id}/ (Response)
class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="created_by_id", read_only=True)
    members = UserMiniSerializer(many=True, read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ["id", "title", "owner_id", "members", "tasks"]

    def get_tasks(self, obj):
        qs = (
            obj.tasks.all()
            .select_related("assigned_to", "reviewer")
            .annotate(comments_count=Count("task_comments"))
        )
        return TaskReadSerializer(qs, many=True, context=self.context).data


# ✅ PATCH /api/boards/{board_id}/ (Response)
class BoardPatchResponseSerializer(serializers.ModelSerializer):
    owner_data = UserMiniSerializer(source="created_by", read_only=True)
    members_data = UserMiniSerializer(source="members", many=True, read_only=True)

    class Meta:
        model = Board
        fields = ["id", "title", "owner_data", "members_data"]


class BoardWriteSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
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
