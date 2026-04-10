import logging
from telegram import Bot

from src.models.user import get_expiring_users, get_expired_users, update_user
from src.utils.messages import msg_renewal_reminder, msg_expired
from src.email.templates.all_templates import send_renewal_reminder_email, send_expired_email

logger = logging.getLogger(__name__)


async def run_renewal_checks(bot: Bot):
    """
    Tourne chaque nuit à minuit.
    Vérifie les abonnements et envoie les rappels.
    """
    logger.info("🌙 Cron renouvellement démarré...")

    # ── Rappels J-5 et J-1 ───────────────────────────────────────────────
    for days in [5, 1]:
        users = await get_expiring_users(days_left=days)
        logger.info(f"⏰ {len(users)} utilisateurs expirent dans {days} jour(s)")

        for user in users:
            chat_id = user.get("chat_id")
            prenom = user.get("prenom", "")
            lang = user.get("langue", "fr")
            email = user.get("email")
            expiration = user.get("date_expiration")
            exp_str = expiration.strftime("%d/%m/%Y") if expiration else "—"

            # DM Telegram
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=msg_renewal_reminder(prenom, days, exp_str, lang=lang),
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Erreur DM rappel {chat_id}: {e}")

            # Email
            if email:
                try:
                    await send_renewal_reminder_email(
                        prenom=prenom,
                        email=email,
                        days=days,
                        expiration=exp_str,
                        plan_key=user.get("plan_choisi", "premium")
                    )
                except Exception as e:
                    logger.error(f"Erreur email rappel {email}: {e}")

    # ── Expirations J+0 ───────────────────────────────────────────────────
    expired_users = await get_expired_users()
    logger.info(f"❌ {len(expired_users)} abonnements expirés aujourd'hui")

    for user in expired_users:
        chat_id = user.get("chat_id")
        prenom = user.get("prenom", "")
        lang = user.get("langue", "fr")
        email = user.get("email")

        # Mettre à jour le statut
        await update_user(chat_id, {"statut": "expired"})

        # DM Telegram
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=msg_expired(prenom, lang=lang),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Erreur DM expiration {chat_id}: {e}")

        # Email
        if email:
            try:
                await send_expired_email(prenom=prenom, email=email)
            except Exception as e:
                logger.error(f"Erreur email expiration {email}: {e}")

    logger.info("✅ Cron renouvellement terminé.")
