from rest_framework.views import APIView
from rest_framework.response import Response
from presentation.dependencies.service_factories import get_profile_service
from rest_framework.parsers import MultiPartParser, JSONParser
from application.services.profile_service import ProfileService
from backend.application.dtos.profile_dto import ProfileDTO
from rest_framework.permissions import IsAuthenticated


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    ALLOWED_ATTRS = ("first_name", "last_name", "gender", "location", "bio")

    def patch(self, request):
        try:
            profile_data = {
                attr: request.data[attr]
                for attr in self.ALLOWED_ATTRS
                if request.data.get(attr) is not None
            }
            avatar_file = request.FILES.get("avatar")
            user_id = request.user.id

            profile_service: ProfileService = get_profile_service()
            profile_dto: ProfileDTO = profile_service.update_profile(
                user_id, profile_data, avatar_file
            )

            return Response(profile_dto.__dict__)

        except Exception as e:
            return Response({"error": str(e)}, status=400)
