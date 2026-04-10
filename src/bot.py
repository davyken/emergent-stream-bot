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

    # Essayer de répondre via l'IA si c'est une vraie question
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

    # Réponse par défaut
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


# ─── Démarrage du bot ─────────────────────────────────────────────────────
async def main():
    # 1. Connexion MongoDB
    await connect_db()

    # 2. Créer l'application Telegram
    app = Application.builder().token(BOT_TOKEN).build()

    # 3. Enregistrer tous les handlers (l'ordre est important !)
    app.add_handler(get_onboarding_handler())                # /start → FSM inscription

    for handler in get_subscription_handlers():             # /abonnements + callbacks plans
        app.add_handler(handler)

    for handler in get_payment_handlers():                  # Photo → admin
        app.add_handler(handler)

    for handler in get_admin_handlers():                    # Boutons approve/reject
        app.add_handler(handler)

    for handler in get_account_handlers():                  # /moncompte /monacces /aide
        app.add_handler(handler)

    for handler in get_canal_handlers():                    # IA dans le canal
        app.add_handler(handler)

    # Handler fallback pour les messages non reconnus
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_unknown_text)
    )

    # 4. Simple asyncio scheduler
    async def run_schedules():
        while True:
            try:
                await check_and_notify(app.bot)
            except Exception as e:
                logger.error(f"Film watcher error: {e}")
            await asyncio.sleep(FILMS_SCRAPE_INTERVAL * 60)

    async def run_daily_renewal():
        while True:
            try:
                await run_renewal_checks(app.bot)
            except Exception as e:
                logger.error(f"Renewal job error: {e}")
            await asyncio.sleep(86400)

    asyncio.create_task(run_schedules())
    asyncio.create_task(run_daily_renewal())
    logger.info(f"⏱️ Watcher films : toutes les {FILMS_SCRAPE_INTERVAL} minutes")
    logger.info("🌙 Cron renouvellement : chaque nuit à 00h05")

    # 5. Lancer le bot
    logger.info("🚀 Emerging-Stream Bot démarré !")
    logger.info("📡 En attente de messages...")

    await app.run_polling(drop_pending_updates=True)
