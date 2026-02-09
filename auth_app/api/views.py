"""
auth_app API views.

Provides authentication endpoints for the KanMind backend:
- Registration (creates a new user and returns a token)
- Login (authenticates a user and returns a token)
"""

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegistrationSerializer 


class RegistrationView(APIView):
    """Register a new user and return an authentication token."""


    permission_classes = [AllowAny]


    def post(self, request):
        """Create a user from request data and return token + basic user info."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "email": user.email,
                "fullname": user.fullname,
            },
            status=status.HTTP_201_CREATED,
        )
    

class LoginView(APIView):
    """Authenticate a user and return an authentication token."""


    permission_classes = [AllowAny]


    def post(self, request):
        """Validate credentials and return token + basic user info."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "email": user.email,
                "fullname": user.fullname,
            },
            status=status.HTTP_200_OK,
        )
    