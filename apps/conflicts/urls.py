from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.conflicts.views import ConflictViewSet

router = DefaultRouter()
router.register(r'conflicts', ConflictViewSet, basename='conflict')

urlpatterns = [
    path('', include(router.urls)),
]