from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from .validators import validate_unique_email, validate_passwords_match, validate_login

User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    fullname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    repeated_password = serializers.CharField(write_only=True, min_length=6)

    def validate_email(self, value):
        return validate_unique_email(value)
    
    def validate(self, attrs):
        validate_passwords_match(attrs["password"], attrs["repeated_password"])
        return attrs
    
    def create(self, validated_data):
        validated_data.pop("repeated_password")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_login(self, attrs):
        attrs["user"] = validate_login(attrs["email"], attrs["password"])
        return attrs     
