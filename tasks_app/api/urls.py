from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import TaskViewSet, CommentViewSet

router = SimpleRouter()
router.register("tasks", TaskViewSet, basename="tasks")

urlpatterns = [
    path("", include(router.urls)),
    path("tasks/<int:task_id>/comments/", CommentViewSet.as_view({"get": "list", "post": "create"})),
    path("tasks/<int:task_id>/comments/<int:pk>/", CommentViewSet.as_view({"delete": "destroy"})),
]