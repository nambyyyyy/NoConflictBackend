from rest_framework import serializers


class CreateConflictSerializer(serializers.Serializer):
    partner_id = serializers.UUIDField(required=False, allow_null=True)
    title = serializers.CharField(max_length=255, required=False, default="")