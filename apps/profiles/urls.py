from apps.profiles.views import ProfileView
from django.urls import path

urlpatterns = [
    path('', ProfileView.as_view(), name='profile-detail'),
]