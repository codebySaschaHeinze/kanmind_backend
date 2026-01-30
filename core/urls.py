from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include("users_app.api.urls")),
    path('api/', include("boards_app.api.urls"))
]
