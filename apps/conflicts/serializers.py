from rest_framework import serializers
from apps.conflicts.models import Conflict, ConflictItem, OptionItem, OptionChoice
from django.contrib.auth import get_user_model

User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        
        
class ConflictListSerializer(serializers.ModelSerializer):
    creator = UserShortSerializer(read_only=True)
    partner = UserShortSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Conflict
        fields = ['slug', 'title', 'status', 'status_display', 'progress', 'creator', 'partner']
        

class OptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionItem
        fields = ['id', 'value', 'is_predefined', 'created_by']


class ConflictItemSerializer(serializers.ModelSerializer):
    options = OptionItemSerializer(many=True, read_only=True)

    creator_choice_value = serializers.CharField(source='creator_choice.value', read_only=True, allow_null=True)
    partner_choice_value = serializers.CharField(source='partner_choice.value', read_only=True, allow_null=True)
    agreed_choice_value = serializers.CharField(source='agreed_choice.value', read_only=True, allow_null=True)

    class Meta:
        model = ConflictItem
        fields = [
            'id', 
            'item_type', 
            'is_agreed',
            # Поля с ID выбора. Они нужны для отправки запросов.
            'creator_choice', 
            'partner_choice',
            'agreed_choice',
            # Текстовые поля для отображения
            'creator_choice_value',
            'partner_choice_value',
            'agreed_choice_value',
            # Все доступные варианты
            'options',
        ]
        
            
class ConflictDetailSerializer(serializers.ModelSerializer):
    # --- Поля для чтения (GET) ---
    creator = UserShortSerializer(read_only=True)
    partner = UserShortSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Решение циклической зависимости: вкладываем сериализатор пунктов
    items = ConflictItemSerializer(many=True, read_only=True)
    
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
        fields = [
            'slug', 'title', 'status', 'status_display', 'progress', 
            'creator', 'partner', 'items', # Для чтения
            'items_data', 'partner_id' # Для записи
        ]
        read_only_fields = ['slug', 'status', 'progress', 'creator', 'partner', 'items']

    # serializers.py -> ConflictDetailSerializer.create()

def create(self, validated_data):
    from django.db import transaction

    items_data_list = validated_data.pop('items_data')
    
    with transaction.atomic():
        conflict = Conflict.objects.create(**validated_data)

        for item_data in items_data_list:
            predefined_ids = item_data.get('predefined_options_ids', [])
            custom_values = item_data.get('custom_options_values', [])
            creator_choice_value = item_data.get('creator_choice_value')

            conflict_item = ConflictItem.objects.create(
                conflict=conflict,
                item_type=item_data.get('item_type')
            )

            # Собираем все варианты для этого пункта
            all_options_for_item = list(OptionChoice.objects.filter(id__in=predefined_ids))
            
            # Обрабатываем кастомные варианты
            for value in custom_values:
                # get_or_create: если вариант с таким текстом уже есть, берем его. 
                # Если нет - создаем новый. Это предотвращает дубликаты!
                option, created = OptionChoice.objects.get_or_create(
                    value=value, 
                    defaults={'is_predefined': False}
                )
                all_options_for_item.append(option)
            
            # Привязываем весь список вариантов к пункту
            conflict_item.available_options.set(all_options_for_item)
            
            # Устанавливаем выбор создателя
            # Ищем его среди всех добавленных вариантов
            creator_choice_obj = next(
                (opt for opt in all_options_for_item if opt.value == creator_choice_value), 
                None
            )
            if creator_choice_obj:
                conflict_item.creator_choice = creator_choice_obj
            
            conflict_item.save()

    # ... обновление прогресса и возврат conflict ...
        
        
        
    