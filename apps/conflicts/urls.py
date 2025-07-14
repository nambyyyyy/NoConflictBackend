from apps.conflicts.views import ConflictView
from django.urls import path

urlpatterns = [
    path('create/', ConflictView.as_view(), name='conflict-create'),
]