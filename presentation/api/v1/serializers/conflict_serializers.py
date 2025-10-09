from rest_framework import serializers


class ConflictItemSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    creator_choice_value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    partner_choice_value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )
    agreed_choice_value = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )


class CreateConflictSerializer(serializers.Serializer):
    partner_id = serializers.UUIDField(required=False, allow_null=True)
    title = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=None
    )
    items = serializers.ListField(
        child=ConflictItemSerializer(), required=False, default=list
    )

