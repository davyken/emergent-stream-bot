import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters

from src.models.user import create_user, get_user, update_user
from src.utils.messages import (
    msg_welcome_new, msg_ask_ville, msg_ask_telephone,
    msg_ask_email, msg_invalid_email, msg_registration_complete
)
from src.utils.lang import detect_language, is_valid_email, normalize_name, normalize_city
from src.email.templates.all_templates import send_welcome_email

logger = logging.getLogger(__name__)

# États FSM
ASK_PRENOM, ASK_VILLE, ASK_TELEPHONE, ASK_EMAIL = range(4)


async def start_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Démarre l'onboarding si l'utilisateur n'existe pas encore."""
    chat_id = update.effective_user.id
    lang = detect_language(update.message.text or "")
    context.user_data["lang"] = lang

    existing = await get_user(chat_id)
    if existing:
        from src.utils.messages import msg_already_registered
        await update.message.reply_text(
            msg_already_registered(existing["prenom"], lang=existing.get("langue", "fr")),
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    await update.message.reply_text(msg_welcome_new(lang=lang), parse_mode="Markdown")
    return ASK_PRENOM


async def received_prenom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "fr")
    prenom = normalize_name(update.message.text)
    context.user_data["prenom"] = prenom
    await update.message.reply_text(msg_ask_ville(prenom, lang=lang), parse_mode="Markdown")
    return ASK_VILLE


async def received_ville(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "fr")
    raw = update.message.text
    ville_pays = normalize_city(raw)

    # On sépare ville et pays si possible (ex: "Douala Cameroun")
    parts = ville_pays.split()
    if len(parts) >= 2:
        ville = " ".join(parts[:-1])
        pays = parts[-1]
    else:
        ville = ville_pays
        pays = ""

    context.user_data["ville"] = ville
    context.user_data["pays"] = pays
    await update.message.reply_text(msg_ask_telephone(ville, lang=lang), parse_mode="Markdown")
    return ASK_TELEPHONE


async def received_telephone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "fr")
    telephone = update.message.text.strip()
    context.user_data["telephone"] = telephone
    await update.message.reply_text(msg_ask_email(lang=lang), parse_mode="Markdown")
    return ASK_EMAIL


async def received_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "fr")
    email = update.message.text.strip().lower()

    if not is_valid_email(email):
        await update.message.reply_text(msg_invalid_email(lang=lang), parse_mode="Markdown")
        return ASK_EMAIL  # On repose la question

    chat_id = update.effective_user.id
    prenom = context.user_data["prenom"]
    ville = context.user_data["ville"]
    pays = context.user_data["pays"]
    telephone = context.user_data["telephone"]

    # Créer l'utilisateur en base
    await create_user(
        chat_id=chat_id,
        prenom=prenom,
        ville=ville,
        pays=pays,
        telephone=telephone,
        email=email,
        langue=lang
    )

    # Message de confirmation Telegram
    await update.message.reply_text(
        msg_registration_complete(prenom, f"{ville}, {pays}", telephone, email, lang=lang),
        parse_mode="Markdown"
    )

    # Email de bienvenue (non bloquant)
    try:
        await send_welcome_email(prenom, email, f"{ville}, {pays}", telephone)
    except Exception as e:
        logger.error(f"Erreur envoi email bienvenue : {e}")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Inscription annulée. Tape /start pour recommencer.")
    return ConversationHandler.END


def get_onboarding_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start_onboarding)],
        states={
            ASK_PRENOM:    [MessageHandler(filters.TEXT & ~filters.COMMAND, received_prenom)],
            ASK_VILLE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, received_ville)],
            ASK_TELEPHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_telephone)],
            ASK_EMAIL:     [MessageHandler(filters.TEXT & ~filters.COMMAND, received_email)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
