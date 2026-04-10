import asyncio
import logging
from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


async def broadcast_to_users(bot: Bot, users: list, message: str, parse_mode: str = "Markdown"):
    """
    Envoie un message en DM à une liste d'utilisateurs.
    Respecte le rate limit Telegram : 50ms entre chaque envoi.
    """
    sent = 0
    failed = 0

    for user in users:
        chat_id = user.get("chat_id")
        if not chat_id:
            continue
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode
            )
            sent += 1
            await asyncio.sleep(0.05)  # 50ms pour éviter le ban
        except TelegramError as e:
            logger.warning(f"Impossible d'envoyer à {chat_id}: {e}")
            failed += 1

    logger.info(f"Broadcast terminé : {sent} envoyés, {failed} échecs")
    return sent, failed
