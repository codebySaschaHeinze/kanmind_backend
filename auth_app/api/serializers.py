"""
user_auth_app API serializers.

This module contains serializers for authentication endpoints.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .validators import validate_login, validate_passwords_match, validate_unique_email

User = get_user_model()

GUEST_EMAIL = "guest@user.com"


class RegistrationSerializer(serializers.Serializer):
    """Validate registration payload and create a new user."""

    fullname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        """Validate email."""
        email = value.strip().lower()
        if email == GUEST_EMAIL:
            raise serializers.ValidationError("Diese E-Mail ist reserviert.")
        return validate_unique_email(value)

    def validate(self, attrs):
        """Ensure password and repeated_password match."""
        validate_passwords_match(attrs["password"], attrs["repeated_password"])
        return attrs

    def create(self, validated_data):
        """Create and return a new user instance."""
        validated_data.pop("repeated_password")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    """Validate login payload and attach authenticated user."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the user and attach the user object to attrs."""
        attrs["user"] = validate_login(attrs["email"], attrs["password"])
        return attrs
