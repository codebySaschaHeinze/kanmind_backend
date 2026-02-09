from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import BoardViewSet, EmailCheckView


router = SimpleRouter()
router.register("boards", BoardViewSet, basename="boards")

urlpatterns = [
    path("", include(router.urls)),
    path("email-check/", EmailCheckView.as_view()),
]