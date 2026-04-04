import smtplib
import time
from email.message import EmailMessage

from app.core.config import settings


def _send_message_with_retry(msg: EmailMessage) -> None:
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
                return
        except Exception as exc:
            last_error = exc
            if attempt == 0:
                time.sleep(1)

    raise RuntimeError("No se pudo enviar correo por Gmail") from last_error


def send_student_credentials_email(
    to_email: str,
    student_name: str,
    login_email: str,
    temporary_password: str,
) -> None:
    if not settings.smtp_user or not settings.smtp_password:
        raise RuntimeError("SMTP no configurado")

    from_email = settings.smtp_from_email or settings.smtp_user

    msg = EmailMessage()
    msg["Subject"] = "Tus credenciales de acceso a DojoFlow"
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(
        "\n".join(
            [
                f"Hola {student_name},",
                "",
                "Tu encargado de dojo creó tu acceso a DojoFlow.",
                "",
                f"Usuario: {login_email}",
                f"Contraseña temporal: {temporary_password}",
                "",
                "Recomendación: inicia sesión y cambia tu contraseña lo antes posible.",
            ]
        )
    )

    _send_message_with_retry(msg)


def send_password_reset_email(
    to_email: str,
    user_name: str,
    reset_link: str,
) -> None:
    if not settings.smtp_user or not settings.smtp_password:
        raise RuntimeError("SMTP no configurado")

    from_email = settings.smtp_from_email or settings.smtp_user

    msg = EmailMessage()
    msg["Subject"] = "Recupera tu contraseña de DojoFlow"
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(
        "\n".join(
            [
                f"Hola {user_name},",
                "",
                "Recibimos una solicitud para restablecer tu contraseña.",
                "",
                f"Abre este enlace para crear una nueva contraseña: {reset_link}",
                "",
                "Si no solicitaste este cambio, ignora este correo.",
            ]
        )
    )

    _send_message_with_retry(msg)
