from django.contrib.auth import get_user_model
from rest_framework import serializers

from boards_app.models import Board
from .validators import validate_not_empty


User = get_user_model()


class BoardSerializer(serializers.ModelSerializer):
    """Serialize boards and validate board input."""

    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Board
        fields = [
            "id",
            "title",
            "created_by",
            "members",
            "created_at"
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at"
        ]

    def validate_title(self, value):
        """Ensure title is not blank."""
        return validate_not_empty(value, "title")