from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import CommentViewSet, TaskViewSet


router = SimpleRouter()
router.register("tasks", TaskViewSet, basename="tasks")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "tasks/<int:task_id>/comments/",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
        name="task-comments",
    ),
    path(
        "tasks/<int:task_id>/comments/<int:pk>/",
        CommentViewSet.as_view({"delete": "destroy"}),
        name="task-comment-detail",
    ),
]
