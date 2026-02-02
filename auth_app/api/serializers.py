from django.contrib.auth import get_user_model
from rest_framework import serializers

from .validators import (
    validate_unique_email, 
    validate_passwords_match, 
    validate_login,
)


User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    """Validate registration payload and create a new user."""

    fullname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    repeated_password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        """Ensure email is unique."""
        return validate_unique_email(value)
    
    def validate(self, attrs):
        """Ensure passwords match."""
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
        """Authenticate user by email and password."""
        attrs["user"] = validate_login(attrs["email"], attrs["password"])
        return attrs     
