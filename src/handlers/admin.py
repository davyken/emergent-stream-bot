import logging
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters

from src.models.user import get_user, update_user
from src.models.transaction import update_transaction, get_transaction
from src.utils.messages import msg_approved, msg_rejected, msg_admin_ask_code, msg_admin_code_thanks, msg_admin_cancel, msg_trialRejected, msg_trialApproved
from src.email.templates.all_templates import send_activation_email
from src.config.settings import ADMIN_CHAT_ID, PLANS, SUBSCRIPTION_DURATION_DAYS, TRIAL_DURATION_HOURS, SERVER_ACCESS_LINK

logger = logging.getLogger(__name__)


PENDING_APPROVALS = {}
PENDING_TRIAL_APPROVALS = {}


async def cancel_pending_approval(user_id: int):
    if user_id in PENDING_APPROVALS:
        del PENDING_APPROVALS[user_id]


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
        expiration = datetime.now(timezone.utc) + timedelta(days=SUBSCRIPTION_DURATION_DAYS)
        expiration_str = expiration.strftime("%d/%m/%Y")

        PENDING_APPROVALS[ADMIN_CHAT_ID] = {
            "user_chat_id": user_chat_id,
            "tx_id": tx_id,
            "prenom": prenom,
            "plan_key": plan_key,
            "email": user.get("email", ""),
            "lang": lang,
            "expiration_str": expiration_str,
        }

        await query.edit_message_caption(
            query.message.caption + "\n\n⏳ *En attente du code d'activation...*",
            parse_mode="Markdown"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Annuler", callback_data=f"cancel_{tx_id}_{user_chat_id}")]
        ])

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=msg_admin_ask_code(prenom, user_chat_id, tx_id, lang=lang),
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        logger.info(f"⏳ Demande code pour {prenom} ({user_chat_id})")
        return

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


async def callback_admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_CHAT_ID:
        await query.answer("❌ Accès refusé.", show_alert=True)
        return

    await query.answer()

    tx_id = None
    user_chat_id = None

    if ADMIN_CHAT_ID in PENDING_APPROVALS:
        pending = PENDING_APPROVALS.pop(ADMIN_CHAT_ID)
        user_chat_id = pending.get("user_chat_id")
        tx_id = pending.get("tx_id")

    if tx_id:
        await update_transaction(tx_id, {"statut": "cancelled"})

    await query.edit_message_caption(
        query.message.caption + "\n\n❌ *ABONNEMENT ANNULÉ*",
        parse_mode="Markdown"
    )
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=msg_admin_cancel(lang="fr"),
        parse_mode="Markdown"
    )
    if tx_id:
        logger.info(f"❌ Abonnement annulé pour tx {tx_id}")


async def handle_admin_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    if ADMIN_CHAT_ID not in PENDING_APPROVALS:
        await update.message.reply_text(
            "ℹ️ Aucune demande d'approbation en attente.",
            parse_mode="Markdown"
        )
        return

    code = update.message.text.strip()
    if not code:
        return

    pending = PENDING_APPROVALS.pop(ADMIN_CHAT_ID)
    user_chat_id = pending["user_chat_id"]
    tx_id = pending["tx_id"]
    prenom = pending["prenom"]
    plan_key = pending["plan_key"]
    email = pending["email"]
    lang = pending["lang"]
    expiration_str = pending["expiration_str"]

    await update_user(user_chat_id, {
        "statut": "active",
        "plan_choisi": plan_key,
        "code_activation": code,
        "lien_acces": SERVER_ACCESS_LINK,
        "pending_plan": None,
    })

    await update_transaction(tx_id, {
        "statut": "approved",
        "date_traitement": datetime.now(timezone.utc),
        "admin_id": ADMIN_CHAT_ID,
    })

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=msg_admin_code_thanks(lang=lang),
        parse_mode="Markdown"
    )

    await context.bot.send_message(
        chat_id=user_chat_id,
        text=msg_approved(prenom, plan_key, code, expiration_str, lang=lang),
        parse_mode="Markdown"
    )

    try:
        await send_activation_email(
            prenom=prenom,
            email=email,
            plan_key=plan_key,
            code=code,
            expiration=expiration_str
        )
    except Exception as e:
        logger.error(f"Erreur email activation : {e}")

    logger.info(f"✅ Abonnement approuvé pour {prenom} ({user_chat_id}) avec code {code}")


async def callback_trial_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_CHAT_ID:
        await query.answer("❌ Accès refusé.", show_alert=True)
        return

    await query.answer()
    data = query.data
    parts = data.split("_")
    action = parts[0]
    tx_id = parts[2]
    user_chat_id = int(parts[3])

    user = await get_user(user_chat_id)
    if not user:
        await query.edit_message_caption("⚠️ Utilisateur introuvable.")
        return

    lang = user.get("langue", "fr")
    prenom = user.get("prenom", "")

    if action == "trial_approve":
        expiration = datetime.now(timezone.utc) + timedelta(hours=TRIAL_DURATION_HOURS)
        expiration_str = expiration.strftime("%d/%m/%Y à %Hh%M")

        PENDING_TRIAL_APPROVALS[ADMIN_CHAT_ID] = {
            "user_chat_id": user_chat_id,
            "tx_id": tx_id,
            "prenom": prenom,
            "plan_key": "trial_24h",
            "email": user.get("email", ""),
            "lang": lang,
            "expiration_str": expiration_str,
            "is_trial": True,
        }

        await query.edit_message_caption(
            query.message.caption + "\n\n⏳ *En attente du code d'activation...*",
            parse_mode="Markdown"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Annuler", callback_data=f"cancel_trial_{tx_id}_{user_chat_id}")]
        ])

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=msg_admin_ask_code(prenom, user_chat_id, tx_id, lang=lang),
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        logger.info(f"⏳ Demande code trial pour {prenom} ({user_chat_id})")

    elif action == "trial_reject":
        await update_transaction(tx_id, {
            "statut": "rejected",
            "date_traitement": datetime.now(timezone.utc),
            "admin_id": ADMIN_CHAT_ID,
        })

        await context.bot.send_message(
            chat_id=user_chat_id,
            text=msg_trialRejected(lang=lang),
            parse_mode="Markdown"
        )

        await query.edit_message_caption(
            query.message.caption + "\n\n❌ *ESSAI REJETÉ* par l'admin",
            parse_mode="Markdown"
        )
        logger.info(f"❌ Trial rejeté pour {prenom} ({user_chat_id})")


async def handle_trial_code_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    if ADMIN_CHAT_ID not in PENDING_TRIAL_APPROVALS:
        await update.message.reply_text(
            "ℹ️ Aucune demande d'essai en attente.",
            parse_mode="Markdown"
        )
        return

    code = update.message.text.strip()
    if not code:
        return

    pending = PENDING_TRIAL_APPROVALS.pop(ADMIN_CHAT_ID)
    user_chat_id = pending["user_chat_id"]
    tx_id = pending["tx_id"]
    prenom = pending["prenom"]
    plan_key = pending["plan_key"]
    email = pending["email"]
    lang = pending["lang"]
    expiration_str = pending["expiration_str"]

    expiration = datetime.now(timezone.utc) + timedelta(hours=TRIAL_DURATION_HOURS)

    await update_user(user_chat_id, {
        "statut": "active",
        "plan_choisi": plan_key,
        "code_activation": code,
        "date_expiration": expiration,
        "lien_acces": SERVER_ACCESS_LINK,
        "pending_plan": None,
    })

    await update_transaction(tx_id, {
        "statut": "approved",
        "date_traitement": datetime.now(timezone.utc),
        "admin_id": ADMIN_CHAT_ID,
    })

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=msg_admin_code_thanks(lang=lang),
        parse_mode="Markdown"
    )

    await context.bot.send_message(
        chat_id=user_chat_id,
        text=msg_trialApproved(prenom, code, expiration_str, lang=lang),
        parse_mode="Markdown"
    )

    logger.info(f"✅ Trial approuvé pour {prenom} ({user_chat_id}) avec code {code}")


async def callback_trial_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_CHAT_ID:
        await query.answer("❌ Accès refusé.", show_alert=True)
        return

    await query.answer()

    tx_id = None
    user_chat_id = None

    if ADMIN_CHAT_ID in PENDING_TRIAL_APPROVALS:
        pending = PENDING_TRIAL_APPROVALS.pop(ADMIN_CHAT_ID)
        user_chat_id = pending.get("user_chat_id")
        tx_id = pending.get("tx_id")

    if tx_id:
        await update_transaction(tx_id, {"statut": "cancelled"})

    await query.edit_message_caption(
        query.message.caption + "\n\n❌ *ESSAI ANNULÉ*",
        parse_mode="Markdown"
    )
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=msg_admin_cancel(lang="fr"),
        parse_mode="Markdown"
    )
    if tx_id:
        logger.info(f"❌ Trial annulé pour tx {tx_id}")


def get_admin_handlers():
    return [
        CallbackQueryHandler(callback_admin_decision, pattern="^(approve|reject)_"),
        CallbackQueryHandler(callback_admin_cancel, pattern="^cancel_"),
        CallbackQueryHandler(callback_trial_decision, pattern="^(trial_approve|trial_reject)_"),
        CallbackQueryHandler(callback_trial_cancel, pattern="^cancel_trial_"),
        MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_admin_code_input),
        MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_trial_code_input),
    ]
