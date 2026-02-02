from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth import authenticate


User = get_user_model()


def validate_unique_email(email: str) -> str:
    if User.objects.filter(email=email).exists():
        raise serializers.ValidationError("Diese Email existiert bereits.")
    return email


def validate_passwords_match(password: str, repeated_password: str) -> None:
    if password != repeated_password:
        raise serializers.ValidationError({"repeated_password": "Passwörter stimmen nicht überein."})
    

def validate_login(email: str, password: str):
    user = authenticate(email=email, password=password)
    if not user:
        raise serializers.ValidationError("Ungültige Anmeldeinformationen.")
    if not user.is_active:
        raise serializers.ValidationError("Benutzer ist nicht aktiv.")
    return user