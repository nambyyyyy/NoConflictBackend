from django.urls import path
from .views.auth_views import RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
]