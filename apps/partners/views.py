"""Вью более не актуальны!
Использовать только как ориентир для создания новых вью в Clean Arh
"""


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from apps.partners.models import Partner, PartnerRequest
# from apps.partners.serializers import PartnerSerializer, PartnerRequestSerializer
# from apps.common.permissions import IsOwnerOnly, IsOwnerOrRead


# class PartnerList(APIView):
#     permission_classes = [IsOwnerOnly]

#     def get(self, request):
#         partners = Partner.objects.all(owner=request.user)
#         serializer = PartnerSerializer(partners, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = PartnerSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class PartnerDetail(APIView):
#     permission_classes = [IsOwnerOnly]

#     def get_object(self, uuid, user):
#         try:
#             return Partner.objects.get(id=uuid, owner=user)
#         except Partner.DoesNotExist:
#             return None

#     def delete(self, request, uuid):
#         partner = self.get_object(uuid, request.user)
#         if not partner:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         partner.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class SendPartnerRequest(APIView):
#     permission_classes = [IsOwnerOnly]

#     def post(self, request):
#         serializer = PartnerRequestSerializer(
#             data=request.data, context={"request": request}
#         )
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"detail": "Запрос отправлен."}, status=status.HTTP_201_CREATED
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class PartnerRequestDetail(APIView):
#     permission_classes = [IsOwnerOnly]

#     def get_object(self, uuid, user):
#         try:
#             return PartnerRequest.objects.get(id=uuid, sender=user)
#         except PartnerRequest.DoesNotExist:
#             return None

#     def delete(self, request, uuid):
#         partner_request = self.get_object(uuid, request.user)
#         if not partner_request:
#             return Response(
#                 {"detail": "Запрос не найден."},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         if partner_request.is_accepted or partner_request.is_rejected:
#             return Response(
#                 {"detail": "Нельзя отменить уже принятый или отклонённый запрос."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         partner_request.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class AcceptPartnerRequest(APIView):
#     permission_classes = [IsOwnerOnly]

#     def post(self, request, uuid):
#         try:
#             req = PartnerRequest.objects.get(id=uuid, receiver=request.user)
#         except PartnerRequest.DoesNotExist:
#             return Response(
#                 {"detail": "Запрос не найден."}, status=status.HTTP_404_NOT_FOUND
#             )

#         # Создаем двустороннюю связь
#         Partner.objects.get_or_create(owner=req.sender, partner=req.receiver)
#         Partner.objects.get_or_create(owner=req.receiver, partner=req.sender)

#         req.is_accepted = True
#         req.save()

#         return Response(
#             {"detail": "Партнёрство установлено."}, status=status.HTTP_200_OK
#         )


# class RejectPartnerRequest(APIView):
#     permission_classes = [IsOwnerOnly]

#     def post(self, request, uuid):
#         try:
#             req = PartnerRequest.objects.get(id=uuid, receiver=request.user)
#         except PartnerRequest.DoesNotExist:
#             return Response(
#                 {"detail": "Запрос не найден."}, status=status.HTTP_404_NOT_FOUND
#             )

#         # Проверяем, не был ли уже принят или отклонён
#         if req.is_accepted:
#             return Response(
#                 {"detail": "Запрос уже принят."}, status=status.HTTP_400_BAD_REQUEST
#             )
#         if req.is_rejected:
#             return Response(
#                 {"detail": "Запрос уже отклонён."}, status=status.HTTP_400_BAD_REQUEST
#             )

#         # Помечаем как отклонённый
#         req.is_rejected = True
#         req.save()

#         return Response({"detail": "Запрос отклонён."}, status=status.HTTP_200_OK)
