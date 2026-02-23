"""
API Views for accounts app using Django REST Framework
"""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model
    Doctors can view and manage all users
    Caregivers and Patients can only view their own profile
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        
        if user.is_doctor():
            # Doctors can see all users
            return User.objects.all()
        else:
            # Others can only see themselves
            return User.objects.filter(id=user.id)
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'create':
            # Only doctors can create users via API
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Only doctors can modify users
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Only doctors can create users"""
        if not self.request.user.is_doctor():
            raise permissions.PermissionDenied("Only doctors can create users.")
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
