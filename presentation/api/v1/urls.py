from django.urls import path
from .views.auth_views import RegisterView, VerifyEmailView, LoginView
from .views.conflict_views import CreateConflictView, ConflictView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path('conflicts/<str:slug>/', ConflictView.as_view(), name='conflict-detail-by-slug'),
    path("conflicts/", CreateConflictView.as_view(), name="create-conflict"),
    path(
        "verify-email/<uidb64>/<token>/",
        VerifyEmailView.as_view(),
        name="verify-email",
    ),
]
