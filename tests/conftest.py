import pytest

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def user():
    """Фабрика пользователя"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    return User.objects.create_user(
        username="existinguser",
        email="existing@example.com",
        password="StrongPass123!"
    )

@pytest.fixture
def authenticated_client(api_client, user):
    """Клиент с авторизацией.""" 
    api_client.force_authenticate(user=user)
    return api_client