from django.core.mail import send_mail
from celery import shared_task


@shared_task()
def send_forgot_password_email_task(email_address, message):
    """Sends an email when a user request a forgot password option."""

    send_mail(
        "Your Feedback",
        f"\t{message}\n\nThank you!",
        "support@example.com",
        [email_address],
        fail_silently=False,
    )