from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


User = get_user_model()


class EmailCheckView(APIView):
    """Return basic user info for a given email address."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response({"detail": "Bitte gib eine E-Mail-Adresse an."},
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