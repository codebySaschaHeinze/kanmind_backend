from django.contrib import admin
from .models import Board


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_by", "created_at")
    search_fields = ("title", "created_by__email")
    list_filter = ("created_at",)
    filter_horizontal = ("members",)