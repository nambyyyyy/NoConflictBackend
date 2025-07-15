from apps.conflicts.views import ConflictCreateView, ConflictDetailView
from django.urls import path

urlpatterns = [
    path('create/', ConflictCreateView.as_view(), name='conflict-create'),
    path('<uuid:pk>/cancel/', ConflictDetailView.as_view(), name='conflict-cancel')
]