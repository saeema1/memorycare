"""
API URL patterns for accounts app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

app_name = 'accounts_api'

urlpatterns = [
    path('', include(router.urls)),
]
