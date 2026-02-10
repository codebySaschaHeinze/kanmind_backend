from django.conf import settings
from django.db import models


class Board(models.Model):
    """A Kanban board with members and a creator."""
    
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

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Board"
        verbose_name_plural = "Boards"

    def __str__(self):
        return self.title