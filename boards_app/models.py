from django.conf import settings
from django.db import models

# Create your models here.

class Board(models.Model):
    title = models.CharField(max_length=255)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_boards",
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="boards",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title