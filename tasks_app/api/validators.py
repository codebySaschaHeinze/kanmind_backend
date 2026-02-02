from rest_framework import serializers


def validate_not_empty(value: str, field_name: str = "value") -> str:
    if value is None or not str(value).strip():
        raise serializers.ValidationError(f"{field_name} darf nicht leer sein.")
    return str(value).strip()


def validate_user_is_board_member(board, user, field_name: str):
    if user is None:
        return
    if not board.members.filter(id=user.id).exists():
        raise serializers.ValidationError({field_name: "Benutzer muss Board-Member sein."})