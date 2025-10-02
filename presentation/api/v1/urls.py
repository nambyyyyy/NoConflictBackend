from django.urls import path
from .views.auth_views import RegisterView, VerifyEmailView, LoginView
from .views.conflict_views import CreateConflictView, ConflictFormTemplateView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("conflicts/", CreateConflictView.as_view(), name="create-conflict"),
    path(
        "conflicts/form-template/",
        ConflictFormTemplateView.as_view(),
        name="conflict-form-template",
    ),
    path(
        "verify-email/<uidb64>/<token>/",
        VerifyEmailView.as_view(),
        name="verify-email",
    ),
]
