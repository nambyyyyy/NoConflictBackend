from rest_framework import serializers
from apps.conflicts.models import Conflict, ConflictItem, OptionChoice, OptionChoice
from django.contrib.auth import get_user_model

User = get_user_model()


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username'] 


class OptionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionChoice
        fields = ['id', 'value', 'is_predefined']

       
class ConflictItemSerializer(serializers.ModelSerializer):
    available_options = OptionChoiceSerializer(many=True, read_only=True)
    creator_choice = OptionChoiceSerializer(read_only=True)
    partner_choice = OptionChoiceSerializer(read_only=True)
    agreed_choice = OptionChoiceSerializer(read_only=True)
    
    class Meta:
        model = ConflictItem
        fields = ['id',
                  'item_type',
                  'available_options',
                  'creator_choice',
                  'partner_choice',
                  'agreed_choice',
                  'is_agreed',                 
                  ]


class ConflictDetailSerializer(serializers.ModelSerializer):
    # GET
    creator = UserShortSerializer(read_only=True)
    partner = UserShortSerializer(read_only=True)
    items = ConflictItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # --- Поля для записи (POST) ---
    # Мы не можем принимать 'items', т.к. они read_only.
    # Создаем виртуальное поле для приема данных.
    items_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        help_text="Список пунктов для создания."
    )
    # Поле для добавления партнера по ID при создании
    partner_id = serializers.UUIDField(
    write_only=True, 
    required=False, 
    allow_null=True,
    help_text="UUID пользователя-партнера для прямого приглашения."
)

    class Meta:
        model = Conflict
        fields = ['title', 
                  'partner_id', 
                  'items_data', 
                  'slug',
                  'status',
                  'progress',
                  'status_display',
                  'creator',
                  'partner',
                  'items',
                  ]
        read_only_fields = [
            'slug',
            'status',
            'status_display',
            'progress',
            'creator',
            'partner',
            'items',
        ]

    # serializers.py -> ConflictDetailSerializer.create()

    def create(self, validated_data):
        from django.db import transaction

        items_data_list = validated_data.pop('items_data')
        partner_id = validated_data.pop('partner_id', None)
    
        with transaction.atomic():
            conflict = Conflict.objects.create(**validated_data)
            
            if partner_id:
                try:
                    conflict.partner = User.objects.get(pk=partner_id)
                except User.DoesNotExist:
                    # Можно обработать ошибку или просто проигнорировать
                    pass
            
            for item_data in items_data_list:
                predefined_ids = item_data.get('predefined_options_ids', [])
                custom_values = item_data.get('custom_options_values', [])
                creator_choice_value = item_data.get('creator_choice_value')
            
                conflict_item = ConflictItem.objects.create(
                    conflict=conflict,
                    item_type=item_data.get('item_type')
                )
                
                all_options_for_item = list(OptionChoice.objects.filter(id__in=predefined_ids))
                
                for value in custom_values:
                    # Здесь смотрим, были ли уже ранее добавлены такие ответы
                    option, _ = OptionChoice.objects.get_or_create(
                        value__iexact=value, 
                        defaults={'value': value, 'is_predefined': False}
                    )
                    all_options_for_item.append(option)
                
                conflict_item.available_options.set(all_options_for_item)
                
                creator_choice_obj = next(
                    (opt for opt in all_options_for_item if opt.value == creator_choice_value), 
                    None
                )
                if creator_choice_obj:
                    conflict_item.creator_choice = creator_choice_obj
                
                conflict_item.update_status()
                conflict_item.save()
            
            conflict.update_progress()
            conflict.save()
            
            return conflict
            

class ConflictListSerializer(serializers.ModelSerializer):
    creator = UserShortSerializer(read_only=True)
    partner = UserShortSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Conflict
        fields = [
            'slug', 
            'title', 
            'status', 
            'status_display', 
            'progress', 
            'creator', 
            'partner',
            'created_at',
            'updated_at',
        ]         
            
            
            
            
            
            
            
            
            
            
            
            
            

        
        
    