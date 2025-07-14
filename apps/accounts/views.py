from rest_framework.views import APIView
from apps.accounts.serializers import CreateUserSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.accounts.serializers import MyTokenObtainPairSerializer
from rest_framework.permissions import AllowAny


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=201)
        return Response(data=serializer.errors, status=400)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer