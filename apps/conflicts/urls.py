from django.urls import path, include
from rest_framework.routers import DefaultRouter
<<<<<<< HEAD
from apps.conflicts.views import ConflictViewSet
=======
from .views import ConflictViewSet
>>>>>>> ef3b54f1f415335853a547d2bc42f824ce55242c

router = DefaultRouter()
router.register(r'conflicts', ConflictViewSet, basename='conflict')

urlpatterns = [
    path('', include(router.urls)),
]