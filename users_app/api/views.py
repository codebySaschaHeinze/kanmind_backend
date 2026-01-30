from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from .serializers import RegistrationSerializer, LoginSerializer

User = get_user_model()


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token,_ = Token.objects.get_or_create(user=user)

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
    permission_classes = [AllowAny]

    def post(self, request):
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
    

class EmailCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response({"detail": "Email Abfrageparameter erforderlich."},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            return Response(
                {"id": user.id, "email": user.email, "fullname": user.fullname},
                status=status.HTTP_200_OK,
            )   
        except User.DoesNotExist:
            return Response({"detail": "Benutzer wurde nicht gefunden."}, 
                status=status.HTTP_404_NOT_FOUND)