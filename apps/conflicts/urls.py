from apps.conflicts.views import ConflictCreateView, ConflictDetailView
from django.urls import path

urlpatterns = [
    path('create/', ConflictCreateView.as_view(), name='conflict-create'),
    path('<uuid:pk>/', ConflictDetailView.as_view(), name='conflict-form'),
    path('<uuid:pk>/cancel/', ConflictDetailView.as_view(), name='conflict-cancel'),
    path('<uuid:pk>/delete/', ConflictDetailView.as_view(), name='conflict-delete'),
]