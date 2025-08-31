from celery import shared_task
from no_conflict_project import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from urllib.parse import urljoin
from django.core.mail import send_mail

User = get_user_model()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),  # ретраи при временных сбоях SMTP
    retry_backoff=30,  # 30с, потом экспоненциально
    retry_jitter=True,
    retry_kwargs={"max_retries": 5},
)
def send_verification_email(self, user_id: int, base_url: str | None = None) -> None:
    user = User.objects.filter(pk=user_id).first()
    if not user or user.email_confirmed:
        return

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

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
        recipient_list=[user.email],
        fail_silently=False,
    )
