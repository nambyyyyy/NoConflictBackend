from rest_framework import serializers
from apps.partners.models import Partner, PartnerRequest
from django.contrib.auth import get_user_model

User = get_user_model()


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ("owner", "partner")


class PartnerRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)

    class Meta:
        model = PartnerRequest
        fields = ("username",)

    def validate_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден.")
        return user

    def create(self, validated_data):
        sender = self.context["request"].user
        receiver = validated_data["username"]
        if sender == receiver:
            raise serializers.ValidationError("Нельзя добавить себя.")

        request, created = PartnerRequest.objects.get_or_create(
            sender=sender,
            receiver=receiver,
            defaults={"sender": sender, "receiver": receiver}
        )
        if not created:
            raise serializers.ValidationError("Запрос уже отправлен.")
        return request
