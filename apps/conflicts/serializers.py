from rest_framework import serializers
from apps.conflicts.models import Conflict, ConflictItem
from django.contrib.auth import get_user_model

User = get_user_model()


class ConflictSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    def get_status_display(self, obj):
        # Django-метод для choices
        return obj.get_status_display()

    class Meta:
        model = Conflict
        fields = (
            "id",
            "creator",
            "partner",
            "title",
            "status",
            "slug",
            "progress",
            "created_at",
            "updated_at",
            "is_deleted",
            "deleted_at",
            "status_display",
            "resolved_at",
        )
        read_only_fields = (
            "id",
            "slug",
            "created_at",
            "updated_at",
            "creator",
            "is_deleted",
            "deleted_at",
            "partner",
            "progress",
            "status",
            "resolved_at",
        )



class ConflictItemSerializer(serializers.ModelSerializer):
    conflict = ConflictSerializer()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ConflictItem
        fields = (
            "id",
            "created_at",
            "updated_at",
            "conflict",
            "item_type",
            "value_creator",
            "value_partner",
            "agreed_value",
            "is_agreed",
        )
