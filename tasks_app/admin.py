from django.contrib import admin
from .models import Task, Comment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "board", "status", "priority", "assigned_to", "reviewer", "due_date", "created_by")
    search_fields = ("title", "board__title", "assigned_to__email", "reviewer__email", "created_by__email")
    list_filter = ("status", "priority", "due_date")
    autocomplete_fields = ("board", "assigned_to", "reviewer", "created_by")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "task", "author", "created_at")
    search_fields = ("task__title", "author__email", "text")
    list_filter = ("created_at",)
    autocomplete_fields = ("task", "author")
