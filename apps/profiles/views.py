from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.profiles.models import Profile
from apps.profiles.serializers import ProfileSerializer
from apps.common.permissions import IsOwnerOrRead
from apps.common.utils import set_profile_and_user


class ProfileView(APIView):
    permission_classes = [IsOwnerOrRead]
    serializer_class = ProfileSerializer

    def get(self, request):
        try:
            profile = request.user.profile
            serializer = self.serializer_class(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(
                {"error": "Профиль не найден"}, status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request):
        try:
            user = request.user
            profile = user.profile
            serializer = self.serializer_class(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            set_profile_and_user(user, profile, serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response(
                {"error": "Профиль не найден"}, status=status.HTTP_404_NOT_FOUND
            )
