from rest_framework import serializers


def validate_not_empty(value: str, field_name: str = "value") -> str:
    if value is None or not str(value).strip():
        raise serializers.ValidationError(f"{field_name} darf nicht leer sein.")
    return str(value).strip()