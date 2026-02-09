from rest_framework.permissions import BasePermission


class IsBoardMemberOrCreator(BasePermission):
    """Allow access if the user is the board creator or a board member."""
    
    def has_object_permission(self, request, view, obj):
        if obj.created_by_id == request.user.id:
            return True
        
        return obj.members.filter(id=request.user.id).exists()
    
    
class IsBoardCreatorOnly(BasePermission):
    """Allow access only to the board creator."""
    def has_object_permission(self, request, view, obj):
        return obj.created_by_id == request.user.id