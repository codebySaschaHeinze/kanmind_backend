"""
user_auth_app API validators.

This module provides small validation helpers used by auth serializers.
"""

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


def validate_unique_email(email: str) -> str:
    """Validate that the email is not already registered."""
    if User.objects.filter(email=email).exists():
        raise serializers.ValidationError("Diese Email existiert bereits.")
    return email


def validate_passwords_match(password: str, repeated_password: str) -> None:
    """Validate that password and repeated_password match."""
    if password != repeated_password:
        raise serializers.ValidationError(
            {"repeated_password": "Passwörter stimmen nicht überein."}
        )


def validate_login(email: str, password: str):
    """Authenticate the user using email and password."""
    user = authenticate(email=email, password=password)

    if not user:
        raise serializers.ValidationError("Ungültige Anmeldeinformationen.")
    if not user.is_active:
        raise serializers.ValidationError("Benutzer ist nicht aktiv.")

    return user
