from rest_framework.routers import SimpleRouter
from .views import BoardViewSet


router = SimpleRouter()
router.register("boards", BoardViewSet, basename="boards")

urlpatterns = router.urls
