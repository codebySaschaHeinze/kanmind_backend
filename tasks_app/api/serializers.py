from rest_framework import serializers
from tasks_app.models import Task, Comment

class TaskSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Task
        fields = [
            "id",
            "board",
            "title",
            "description",
            "status",
            "assigned_to",
            "reviewer",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", 
            "created_by", 
            "created_at", 
            "updated_at"]
        
    def create(self, validated_data):
        request = self.context["request"]
        return Task.objects.create(created_by=request.user, **validated_data)
    

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            "id", 
            "task", 
            "author", 
            "text", 
            "created_at"]
        read_only_fields = [
            "id", 
            "task", 
            "author", 
            "created_at"]
        
