import logging
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from src.models.user import get_user, update_user
from src.models.transaction import update_transaction, get_transaction
from src.utils.messages import msg_approved, msg_rejected
from src.utils.code_generator import generate_activation_code
from src.email.templates.all_templates import send_activation_email
from src.config.settings import ADMIN_CHAT_ID, PLANS, SUBSCRIPTION_DURATION_DAYS, SERVER_ACCESS_LINK

logger = logging.getLogger(__name__)


async def callback_admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # Sécurité : seul l'admin peut utiliser ces boutons
    if query.from_user.id != ADMIN_CHAT_ID:
        await query.answer("❌ Accès refusé.", show_alert=True)
        return

    await query.answer()
    data = query.data  # "approve_TXID_CHATID" ou "reject_TXID_CHATID"
    parts = data.split("_")
    action = parts[0]          # approve / reject
    tx_id = parts[1]           # ObjectId de la transaction
    user_chat_id = int(parts[2])

    user = await get_user(user_chat_id)
    tx = await get_transaction(tx_id)

    if not user or not tx:
        await query.edit_message_caption("⚠️ Utilisateur ou transaction introuvable.")
        return

    lang = user.get("langue", "fr")
    prenom = user.get("prenom", "")
    plan_key = tx.get("plan", "premium")
    plan = PLANS.get(plan_key, {})

    if action == "approve":
        # Générer code activation
        code = generate_activation_code(prenom)
        expiration = datetime.now(timezone.utc) + timedelta(days=SUBSCRIPTION_DURATION_DAYS)
        expiration_str = expiration.strftime("%d/%m/%Y")

        # Mettre à jour user en DB
        await update_user(user_chat_id, {
            "statut": "active",
            "plan_choisi": plan_key,
            "code_activation": code,
            "date_expiration": expiration,
            "lien_acces": SERVER_ACCESS_LINK,
            "pending_plan": None,
        })

        # Mettre à jour transaction
        await update_transaction(tx_id, {
            "statut": "approved",
            "date_traitement": datetime.now(timezone.utc),
            "admin_id": ADMIN_CHAT_ID,
        })

        # Message Telegram à l'utilisateur
        await context.bot.send_message(
            chat_id=user_chat_id,
            text=msg_approved(prenom, plan_key, code, expiration_str, lang=lang),
            parse_mode="Markdown"
        )

        # Email d'activation
        try:
            await send_activation_email(
                prenom=prenom,
                email=user.get("email", ""),
                plan_key=plan_key,
                code=code,
                expiration=expiration_str
            )
        except Exception as e:
            logger.error(f"Erreur email activation : {e}")

        # Confirmation à l'admin
        await query.edit_message_caption(
            query.message.caption + f"\n\n✅ *APPROUVÉ* par l'admin\n🔑 Code : `{code}`",
            parse_mode="Markdown"
        )
        logger.info(f"✅ Abonnement approuvé pour {prenom} ({user_chat_id})")

    elif action == "reject":
        # Mettre à jour transaction
        await update_transaction(tx_id, {
            "statut": "rejected",
            "date_traitement": datetime.now(timezone.utc),
            "admin_id": ADMIN_CHAT_ID,
        })

        # Message Telegram à l'utilisateur
        await context.bot.send_message(
            chat_id=user_chat_id,
            text=msg_rejected(lang=lang),
            parse_mode="Markdown"
        )

        # Confirmation à l'admin
        await query.edit_message_caption(
            query.message.caption + "\n\n❌ *REJETÉ* par l'admin",
            parse_mode="Markdown"
        )
        logger.info(f"❌ Abonnement rejeté pour {prenom} ({user_chat_id})")


def get_admin_handlers():
    return [
        CallbackQueryHandler(callback_admin_decision, pattern="^(approve|reject)_"),
    ]
