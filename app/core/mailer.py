import smtplib
import time
import logging
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def _send_message_with_retry(msg: EmailMessage) -> None:
    """Send email with retry logic."""
    if not settings.smtp_user or not settings.smtp_password:
        raise RuntimeError("SMTP no configurado correctamente en .env")
    
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            logger.info(f"Attempt {attempt + 1}: Connecting to SMTP...")
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
                logger.info("Email sent successfully")
                return
        except Exception as exc:
            last_error = exc
            logger.warning(f"Attempt {attempt + 1} failed: {str(exc)}")
            if attempt == 0:
                time.sleep(1)

    raise RuntimeError("No se pudo enviar correo por Gmail") from last_error


def send_dojo_credentials_email(
    to_email: str,
    dojo_email: str,
    password: str,
    dojo_name: str,
) -> bool:
    """Send dojo owner credentials email."""
    logger.info(f"📧 send_dojo_credentials_email called")
    logger.info(f"   - To: {to_email}")
    logger.info(f"   - Dojo Email: {dojo_email}")
    logger.info(f"   - Dojo Name: {dojo_name}")
    
    if not settings.smtp_user or not settings.smtp_password:
        logger.error("❌ SMTP no configurado - smtp_user o smtp_password vacío")
        raise RuntimeError("SMTP no configurado")

    from_email = settings.smtp_from_email or settings.smtp_user
    logger.info(f"   - From Email: {from_email}")
    logger.info(f"   - SMTP Host: {settings.smtp_host}:{settings.smtp_port}")

    msg = EmailMessage()
    msg["Subject"] = "🥋 Tus Credenciales de DojoFlow"
    msg["From"] = from_email
    msg["To"] = to_email
    
    msg.set_content(
        "\n".join(
            [
                f"¡Bienvenido a DojoFlow!",
                "",
                f"Tu cuenta para {dojo_name} ha sido activada.",
                "",
                f"Email: {dojo_email}",
                f"Contraseña: {password}",
                "",
                "Por favor, cambia tu contraseña en tu primer acceso.",
                "Si tienes alguna pregunta, contáctanos.",
            ]
        )
    )
    
    try:
        logger.info(f"🔄 Calling _send_message_with_retry...")
        _send_message_with_retry(msg)
        logger.info(f"✅ send_dojo_credentials_email: Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"❌ send_dojo_credentials_email: Error sending to {to_email}: {str(e)}", exc_info=True)
        return False

def send_student_credentials_email(
    to_email: str,
    student_name: str,
    login_email: str,
    temporary_password: str,
) -> None:
    """Send student credentials email."""
    logger.info(f"Sending student credentials to {to_email}")
    
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
    """Send password reset email."""
    logger.info(f"Sending password reset to {to_email}")
    
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


def send_teacher_credentials_email(
    to_email: str,
    teacher_name: str,
    login_email: str,
    temporary_password: str,
) -> bool:
    """Send teacher credentials email."""
    logger.info(f"📧 send_teacher_credentials_email called")
    logger.info(f"   - To: {to_email}")
    logger.info(f"   - Teacher Name: {teacher_name}")
    logger.info(f"   - Login Email: {login_email}")
    
    if not settings.smtp_user or not settings.smtp_password:
        logger.error("❌ SMTP no configurado")
        raise RuntimeError("SMTP no configurado")

    from_email = settings.smtp_from_email or settings.smtp_user

    msg = EmailMessage()
    msg["Subject"] = "🥋 Tus Credenciales de DojoFlow - Instructor"
    msg["From"] = from_email
    msg["To"] = to_email
    
    msg.set_content(
        "\n".join(
            [
                f"¡Bienvenido a DojoFlow, {teacher_name}!",
                "",
                "Tu cuenta de instructor ha sido creada en DojoFlow.",
                "",
                f"Usuario: {login_email}",
                f"Contraseña: {temporary_password}",
                "",
                "🔒 Por favor, cambia tu contraseña en tu primer acceso.",
                ##f"Link de login: http://localhost:5173/login",
                "",
                "Si tienes alguna pregunta, contáctanos.",
            ]
        )
    )
    
    try:
        logger.info(f"🔄 Calling _send_message_with_retry...")
        _send_message_with_retry(msg)
        logger.info(f"✅ send_teacher_credentials_email: Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"❌ send_teacher_credentials_email: Error sending to {to_email}: {str(e)}", exc_info=True)
        return False