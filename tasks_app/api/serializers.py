from rest_framework import serializers
from tasks_app.models import Task

class TaskSerializer(serializers.ModelSerializer):
    
    class Meta:
        Model = Task
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
        return Task.objects.create(create_by=request.user, **validated_data)
    

