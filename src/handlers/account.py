import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from src.models.user import get_user
from src.utils.messages import (
    msg_my_account, msg_access_link,
    msg_no_active_sub, msg_help
)

logger = logging.getLogger(__name__)


async def cmd_mon_compte(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("👋 Tape /start pour créer ton compte !")
        return
    lang = user.get("langue", "fr")
    await update.message.reply_text(msg_my_account(user, lang=lang), parse_mode="Markdown")


async def cmd_mon_acces(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("👋 Tape /start pour créer ton compte !")
        return

    lang = user.get("langue", "fr")

    if user.get("statut") != "active":
        await update.message.reply_text(msg_no_active_sub(lang=lang), parse_mode="Markdown")
        return

    code = user.get("code_activation", "—")
    expiration = user.get("date_expiration")
    exp_str = expiration.strftime("%d/%m/%Y") if expiration else "—"

    await update.message.reply_text(
        msg_access_link(code, exp_str, lang=lang),
        parse_mode="Markdown"
    )


async def cmd_renouveler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redirige vers /abonnements."""
    user = await get_user(update.effective_user.id)
    lang = user.get("langue", "fr") if user else "fr"

    if lang == "fr":
        txt = "🔄 Pour renouveler ton abonnement, choisis ta formule ici 👇"
    else:
        txt = "🔄 To renew your subscription, choose your plan below 👇"

    await update.message.reply_text(txt, parse_mode="Markdown")
    # Importer et appeler directement la fonction abonnements
    from src.handlers.subscriptions import cmd_abonnements
    await cmd_abonnements(update, context)


async def cmd_aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_user.id)
    lang = user.get("langue", "fr") if user else "fr"
    await update.message.reply_text(msg_help(lang=lang), parse_mode="Markdown")


def get_account_handlers():
    return [
        CommandHandler(["moncompte", "myaccount", "profile"], cmd_mon_compte),
        CommandHandler(["monacces", "myaccess", "lien"], cmd_mon_acces),
        CommandHandler(["renouveler", "renew"], cmd_renouveler),
        CommandHandler(["aide", "help"], cmd_aide),
    ]
