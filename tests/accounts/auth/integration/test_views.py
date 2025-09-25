import pytest
from unittest.mock import patch



@pytest.mark.django_db
@patch("apps.accounts.tasks.send_verification_email.delay")
def test_register_user_success(api_client, mock_send_email):
    """
    Тестирует успешную регистрацию пользователя через API-эндпоинт /register/.

    Проверяет:
    - Корректный HTTP-статус 201 Created
    - Создание пользователя в базе данных (email, username)
    - Вызов Celery-задачи send_verification_email.delay для отправки письма
    - Формат ответа JSON: содержит ожидаемые поля email и username

    Использует:
    - api_client: клиент DRF для имитации HTTP-запросов
    - mock_send_email: мок-объект, замещающий send_verification_email.delay
      (чтобы не отправлять реальные письма)

    Важно:
    - @patch('apps.accounts.tasks.send_verification_email.delay')
      заменяет реальную celery-задачу на мок до входа в RegisterView.
    - Этот мок автоматически передаётся в тест как параметр 'mock_send_email'.
    """
    from django.urls import reverse
    from django.contrib.auth import get_user_model
    from unittest.mock import Mock

    User = get_user_model()
    mock_send_email = Mock()

    # Подготавливаем входные данные для регистрации
    url = reverse("register")  # Имя маршрута из urls.py
    data = {
        "email": "newuser@test.com",  # Валидный email
        "username": "newuser123",  # Валидное имя (3+ символа, без спецсимволов)
        "password": "StrongPass123!",  # Пароль соответствует требованиям
        "password2": "StrongPass123!",  # Подтверждение пароля совпадает
    }

    # Выполняем POST-запрос к эндпоинту
    response = api_client.post(url, data, format="json")


    # 1. Успешный статус ответа
    assert (
        response.status_code == 201
    ), f"Ожидался статус 201, получен {response.status_code}: {response.content}"

    # 2. Пользователь действительно создан в БД
    assert User.objects.filter(
        username="newuser123"
    ).exists(), "Пользователь с username 'newuser123' не был создан в базе данных"
    assert User.objects.filter(
        email="newuser@test.com"
    ).exists(), "Пользователь с email 'newuser@test.com' не был создан в базе данных"

    # 3. Celery-задача была вызвана (проверка побочного эффекта — отправка email)
    mock_send_email.assert_called_once(), "Celery-задача не была вызвана при регистрации"  # type: ignore

    # 4. Ответ содержит ожидаемые данные (DTO возвращается как dict)
    response_data = response.json()
    assert (
        response_data["email"] == "newuser@test.com"
    ), f"Ожидался email 'newuser@test.com', получен '{response_data.get('email')}'"
    assert (
        response_data["username"] == "newuser123"
    ), f"Ожидался username 'newuser123', получен '{response_data.get('username')}'"


@pytest.mark.django_db
def test_register_user_password_mismatch(api_client):
    from django.urls import reverse

    url = reverse("register")
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "StrongPass123!",
        "password2": "WrongPassword",
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == 400
    assert "Пароли не совпадают" in str(response.json())


@pytest.mark.django_db
def test_register_user_invalid_email(api_client):
    from django.urls import reverse

    # Given
    url = reverse("register")
    data = {
        "email": "not-an-email",
        "username": "testuser",
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
    }

    # When
    response = api_client.post(url, data, format="json")

    # Then
    assert response.status_code == 400
    assert "Укажите действительный email" in str(response.json())


@pytest.mark.django_db
def test_register_user_invalid_username_too_short(api_client):
    # Given
    from django.urls import reverse

    url = reverse("register")
    data = {
        "email": "test@example.com",
        "username": "ab",  # меньше 3 символов
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
    }

    # When
    response = api_client.post(url, data, format="json")

    # Then
    assert response.status_code == 400
    assert "Не менее 3 символов" in str(response.json())


@pytest.mark.django_db
def test_register_user_invalid_username_only_numbers(api_client):
    # Given
    from django.urls import reverse

    url = reverse("register")
    data = {
        "email": "test@example.com",
        "username": "123456",  # только цифры
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
    }

    # When
    response = api_client.post(url, data, format="json")

    # Then
    assert response.status_code == 400
    assert "Нельзя использовать только цифры в имени" in str(response.json())


@pytest.mark.django_db
@patch("presentation.dependencies.service_factories.get_auth_service")
def test_register_user_calls_auth_service(
    mock_get_auth_service, api_client, mock_send_email
):
    from django.urls import reverse
    from unittest.mock import Mock
    # Given
    url = reverse("register")
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "StrongPass123!",
        "password2": "StrongPass123!",
    }

    # Мокаем AuthService
    mock_service = Mock()
    mock_service.register_user.return_value = type(
        "UserDTO", (), {"id": 1, "email": "test@example.com", "username": "testuser"}
    )()
    mock_get_auth_service.return_value = mock_service

    # When
    response = api_client.post(url, data, format="json")

    # Then
    assert response.status_code == 201
    mock_get_auth_service.assert_called_once()
    mock_service.register_user.assert_called_once_with(
        email="test@example.com",
        username="testuser",
        password="StrongPass123!",
        send_email_func=mock_send_email, 
        base_url="http://testserver",
    )
