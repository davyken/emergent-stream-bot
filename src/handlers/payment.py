import logging
from datetime import datetime, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

from src.models.user import get_user
from src.models.transaction import create_transaction
from src.utils.messages import msg_screenshot_received
from src.config.settings import ADMIN_CHAT_ID, PLANS

logger = logging.getLogger(__name__)


async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reçoit la photo du paiement et la transfère à l'admin."""
    if not update.message.photo:
        return

    user = await get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("👋 Tape /start pour créer ton compte d'abord !")
        return

    pending_plan = user.get("pending_plan")
    if not pending_plan:
        await update.message.reply_text(
            "😊 Merci pour la photo ! Mais tu n'as pas encore choisi de plan.\n\n"
            "Tape /abonnements pour choisir ta formule d'abord 👍",
            parse_mode="Markdown"
        )
        return

    lang = user.get("langue", "fr")
    plan = PLANS.get(pending_plan, {})
    photo = update.message.photo[-1]  # Meilleure qualité
    file_id = photo.file_id

    # Créer la transaction en DB
    tx = await create_transaction(
        user_chat_id=update.effective_user.id,
        plan=pending_plan,
        montant=plan.get("prix", 0),
        screenshot_file_id=file_id
    )
    tx_id = str(tx["_id"])

    # Accusé de réception à l'utilisateur
    await update.message.reply_text(msg_screenshot_received(lang=lang), parse_mode="Markdown")

    # Message admin avec toutes les infos
    expiration_hint = datetime.now(timezone.utc)
    admin_text = (
        f"📨 *NOUVELLE DEMANDE D'ABONNEMENT*\n\n"
        f"👤 Prénom : {user.get('prenom', '—')}\n"
        f"📧 Email : {user.get('email', '—')}\n"
        f"📍 Ville : {user.get('ville', '—')}, {user.get('pays', '—')}\n"
        f"📱 Tél : {user.get('telephone', '—')}\n"
        f"📦 Plan : {plan.get('nom', pending_plan)} — {plan.get('prix', 0):,} FCFA\n"
        f"🕐 Reçu le : {expiration_hint.strftime('%d/%m/%Y à %Hh%M')}\n"
        f"🆔 Chat ID : `{update.effective_user.id}`\n"
        f"🔑 TX ID : `{tx_id}`"
    ).replace(",", " ")

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ APPROUVER", callback_data=f"approve_{tx_id}_{update.effective_user.id}"),
            InlineKeyboardButton("❌ REJETER", callback_data=f"reject_{tx_id}_{update.effective_user.id}"),
        ]
    ])

    # Envoyer la photo + texte à l'admin
    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=file_id,
        caption=admin_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


def get_payment_handlers():
    return [
        MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, handle_screenshot),
    ]
