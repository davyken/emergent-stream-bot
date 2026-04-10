import resend
import logging
from src.config.settings import RESEND_API_KEY, EMAIL_FROM, EMAIL_FROM_NAME

logger = logging.getLogger(__name__)

resend.api_key = RESEND_API_KEY


async def send_email(to: str, subject: str, html: str) -> bool:
    """Envoie un email via Resend. Retourne True si succès."""
    try:
        resend.Emails.send({
            "from": f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>",
            "to": [to],
            "subject": subject,
            "html": html,
        })
        logger.info(f"✅ Email envoyé à {to} : {subject}")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur email vers {to}: {e}")
        return False
