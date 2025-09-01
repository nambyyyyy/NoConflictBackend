from celery import shared_task
from no_conflict_project import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from urllib.parse import urljoin
from django.core.mail import send_mail
from uuid import UUID
from infrastructure.persistence.user_repository import DjangoUserRepository

User = get_user_model()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def send_verification_email(
    self,
    user_id: str,  # ← Теперь str (UUID как строка)
    token: str,  # ← Принимаем готовый токен
    base_url: str | None = None,
) -> None:
    # Получаем пользователя через репозиторий
    user_repo = DjangoUserRepository()
    user_entity = user_repo.get_by_id(UUID(user_id))

    if not user_entity or user_entity.email_confirmed:
        return

    # Используем переданный токен, не генерируем новый
    uidb64 = urlsafe_base64_encode(force_bytes(str(user_entity.id)))

    path = reverse("verify-email", kwargs={"uidb64": uidb64, "token": token})
    base = base_url or getattr(settings, "SITE_URL", "http://localhost:8000")
    verify_url = urljoin(base, path)

    subject = "Подтверждение e‑mail"
    body = (
        "Здравствуйте!\n\n"
        f"Для подтверждения почты перейдите по ссылке:\n{verify_url}\n\n"
        "Если вы не регистрировались — игнорируйте это письмо."
    )

    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_entity.email],
        fail_silently=False,
    )
