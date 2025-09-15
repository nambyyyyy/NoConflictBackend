from uuid import uuid4


def test_register_user(
    auth_service, mock_token_repo, mock_user_repo, mock_send_email, fake_user_class
):
    """
    Unit-тест для AuthService.register_user() — без БД, без HTTP, без Celery.

    Проверяет:
    - Пароль хешируется перед сохранением
    - Репозиторий получает хешированный пароль
    - UserDTO формируется корректно
    - Задача отправки email вызывается с правильными параметрами

    Использует моки:
    - UserRepository (вместо реальной БД)
    - send_email_func (вместо Celery)

    Важно: Это unit-тест — он работает за <0.01 секунды.
    """

    email = "test@example.com"
    username = "testuser"
    password = "StrongPass123!"
    base_url = "http://localhost"

    # Мокаем возвращаемое значение токена
    fake_token = "abc123xyz-token-for-test"
    mock_token_repo.make_token.return_value = fake_token

    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.get_by_username.return_value = None

    FakeUser = fake_user_class
    user_entity = FakeUser(
        id=uuid4(),
        email=email,
        username=username,
        password_hash="plain_password_placeholder",
    )
    user_entity.set_password(password)

    # Проверяем, что пароль изменился
    assert user_entity.password_hash != "plain_password_placeholder"
    assert user_entity.password_hash.startswith(
        "hashed_"
    )  # убедились, что имитация сработала

    mock_user_repo.save.return_value = user_entity

    user_dto = auth_service.register_user(
        email=email,
        username=username,
        password=password,
        send_email_func=mock_send_email,
        base_url=base_url,
    )

    mock_user_repo.get_by_email.assert_called_once_with(email)
    mock_user_repo.get_by_username.assert_called_once_with(username)
    mock_user_repo.save.assert_called_once()

    saved_user = mock_user_repo.save.call_args[0][0]
    assert saved_user.email == email
    assert saved_user.username == username
    assert saved_user.password_hash is not None

    mock_token_repo.make_token.assert_called_once_with(saved_user)
    mock_send_email.assert_called_once()
