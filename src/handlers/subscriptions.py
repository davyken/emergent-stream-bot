import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler

from src.models.user import get_user, update_user
from src.utils.messages import msg_subscriptions, msg_payment_instructions, msg_no_active_sub
from src.config.settings import PLANS

logger = logging.getLogger(__name__)


async def cmd_abonnements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("👋 Tape d'abord /start pour créer ton compte !")
        return

    lang = user.get("langue", "fr")
    keyboard = [
        [
            InlineKeyboardButton("⚡ Starter", callback_data="plan_starter"),
            InlineKeyboardButton("⭐ Premium", callback_data="plan_premium"),
            InlineKeyboardButton("👑 Famille", callback_data="plan_famille"),
        ]
    ]
    await update.message.reply_text(
        msg_subscriptions(lang=lang),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def callback_plan_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_key = query.data.replace("plan_", "")
    if plan_key not in PLANS:
        return

    user = await get_user(query.from_user.id)
    if not user:
        await query.message.reply_text("👋 Tape d'abord /start !")
        return

    lang = user.get("langue", "fr")
    prenom = user.get("prenom", "")

    # Sauvegarder le plan en attente
    await update_user(query.from_user.id, {"pending_plan": plan_key, "statut_paiement": "waiting_screenshot"})

    await query.message.reply_text(
        msg_payment_instructions(plan_key, prenom, lang=lang),
        parse_mode="Markdown"
    )


def get_subscription_handlers():
    return [
        CommandHandler(["abonnements", "subscriptions", "plans"], cmd_abonnements),
        CallbackQueryHandler(callback_plan_selected, pattern="^plan_"),
    ]
