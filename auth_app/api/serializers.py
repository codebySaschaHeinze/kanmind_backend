from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers


User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    fullname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    repeated_password = serializers.CharField(write_only=True, min_length=6)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Diese Email existiert bereits.")
        return value
    
    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError({"repeated_password": "Passwörter stimmen nicht überein."})
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

    def validate(self, attrs):
        user = authenticate(email=attrs["email"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Ungültige Anmeldeinformationen.")
        if not user.is_active:
            raise serializers.ValidationError("Benutzer ist nicht aktiv.")
        attrs["user"] = user
        return attrs
    
