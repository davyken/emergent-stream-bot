"""
╔══════════════════════════════════════════════════════╗
║       EMERGING-STREAM BOT — Point d'entrée           ║
║       Streaming · Abonnements · Notifications        ║
╚══════════════════════════════════════════════════════╝
"""

import asyncio
import logging
import sys

from telegram.ext import Application, MessageHandler, filters, ContextTypes

from src.config.db import connect_db
from src.config.settings import BOT_TOKEN, FILMS_SCRAPE_INTERVAL

from src.conversations.onboarding import get_onboarding_handler
from src.handlers.subscriptions import get_subscription_handlers
from src.handlers.payment import get_payment_handlers
from src.handlers.admin import get_admin_handlers
from src.handlers.account import get_account_handlers
from src.handlers.canal import get_canal_handlers

from src.watchers.film_watcher import check_and_notify
from src.jobs.renewal_job import run_renewal_checks

# ─── Logging ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)


# ─── Handler message texte non reconnu ────────────────────────────────────
async def handle_unknown_text(update, context):
    """Répond aux messages texte non capturés par les autres handlers."""
    from src.models.user import get_user
    user = await get_user(update.effective_user.id)

    if not user:
        await update.message.reply_text(
            "👋 Tape /start pour créer ton compte Emerging-Stream ! 🎬"
        )
        return

    lang = user.get("langue", "fr")

    from src.ai.claude import ask_claude
    text = update.message.text or ""
    if len(text) > 5:
        try:
            response = await ask_claude(text)
            if response:
                await update.message.reply_text(response, parse_mode="Markdown")
                return
        except Exception:
            pass

    if lang == "fr":
        msg = (
            "😊 Je ne suis pas sûr de comprendre...\n\n"
            "Voici ce que je peux faire pour toi :\n"
            "👉 /abonnements — Voir les offres\n"
            "👉 /moncompte — Ton profil\n"
            "👉 /monacces — Ton lien serveur\n"
            "👉 /aide — Aide complète"
        )
    else:
        msg = (
            "😊 I'm not sure I understand...\n\n"
            "Here's what I can do:\n"
            "👉 /subscriptions — View plans\n"
            "👉 /myaccount — Your profile\n"
            "👉 /myaccess — Your server link\n"
            "👉 /help — Full help"
        )

    await update.message.reply_text(msg, parse_mode="Markdown")


# ─── Background tasks ──────────────────────────────────────────────────────
async def run_schedules(bot):
    while True:
        try:
            await check_and_notify(bot)
        except Exception as e:
            logger.error(f"Film watcher error: {e}")
        await asyncio.sleep(FILMS_SCRAPE_INTERVAL * 60)


async def run_daily_renewal(bot):
    while True:
        try:
            await run_renewal_checks(bot)
        except Exception as e:
            logger.error(f"Renewal job error: {e}")
        await asyncio.sleep(86400)


# ─── post_init : appelé par PTB dans son propre event loop ────────────────
async def post_init(app: Application) -> None:
    # 1. Connexion MongoDB (on est dans l'event loop de PTB)
    await connect_db()

    # 2. Lancer les tâches de fond
    asyncio.create_task(run_schedules(app.bot))
    asyncio.create_task(run_daily_renewal(app.bot))

    logger.info(f"⏱️ Watcher films : toutes les {FILMS_SCRAPE_INTERVAL} minutes")
    logger.info("🌙 Cron renouvellement : chaque nuit à 00h05")
    logger.info("🚀 Emerging-Stream Bot démarré !")
    logger.info("📡 En attente de messages...")


# ─── Démarrage du bot ─────────────────────────────────────────────────────
def main():
    """Point d'entrée synchrone — PTB gère son propre event loop."""
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)   # ← toute l'init async se fait ici
        .build()
    )

    # Enregistrer tous les handlers (l'ordre est important !)
    app.add_handler(get_onboarding_handler())

    for handler in get_subscription_handlers():
        app.add_handler(handler)

    for handler in get_payment_handlers():
        app.add_handler(handler)

    for handler in get_admin_handlers():
        app.add_handler(handler)

    for handler in get_account_handlers():
        app.add_handler(handler)

    for handler in get_canal_handlers():
        app.add_handler(handler)

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_unknown_text)
    )

    # Appel synchrone — PTB crée et gère son propre event loop
    app.run_polling(drop_pending_updates=True)