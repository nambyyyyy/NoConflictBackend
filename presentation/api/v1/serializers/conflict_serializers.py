from rest_framework import serializers


class ConflictEventSerializer(serializers.Serializer):
    event_type = serializers.CharField(max_length=255)
    old_value = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    new_value = serializers.CharField(required=False, allow_blank=True, allow_null=True)


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
    partner_id = serializers.UUIDField(
        required=False, allow_null=True
    ) 
    title = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default=None
    )
    items = serializers.ListField(
        child=ConflictItemSerializer(), required=False, default=list
    )
    events = serializers.ListField(
        child=ConflictEventSerializer(), required=False, default=list
    )
