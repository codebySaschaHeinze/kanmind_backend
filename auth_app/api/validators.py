from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers


User = get_user_model()


def validate_unique_email(email: str) -> str:
    """Raise ValidationError if email is already registered."""
    if User.objects.filter(email=email).exists():
        raise serializers.ValidationError("Diese Email existiert bereits.")
    return email

def validate_passwords_match(password: str, repeated_password: str) -> None:
    """Raise ValidationError if password and repeated_password differ."""
    if password != repeated_password:
        raise serializers.ValidationError(
            {"repeated_password": "Passwörter stimmen nicht überein."}
        )
    
def validate_login(email: str, password: str):
    """Authenticate user and return it, or raise ValidationError."""
    user = authenticate(email=email, password=password)
    if not user:
        raise serializers.ValidationError("Ungültige Anmeldeinformationen.")
    if not user.is_active:
        raise serializers.ValidationError("Benutzer ist nicht aktiv.")
    return user