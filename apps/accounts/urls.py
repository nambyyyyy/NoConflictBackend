# from apps.accounts.views import (
#     RegisterAPIView,
#     VerifyEmailAPIView,
# )
# from django.urls import path
# from rest_framework_simplejwt.views import (
#     TokenRefreshView,
#     TokenVerifyView,
# )

# urlpatterns = [
#     path("", RegisterAPIView.as_view(), name="registration"),
#     path(
#         "verify-email/<uidb64>/<token>/",
#         VerifyEmailAPIView.as_view(),
#         name="verify-email",
#     ),

#     path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
#     path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
# ]
