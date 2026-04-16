import logging
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from src.models.user import get_user, update_user
from src.models.transaction import create_transaction
from src.utils.messages import msg_subscriptions, msg_payment_instructions, msg_no_active_sub, msg_screenshot_received
from src.config.settings import PLANS, ADMIN_CHAT_ID, TRIAL_DURATION_HOURS

logger = logging.getLogger(__name__)


async def cmd_abonnements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("👋 Tape d'abord /start pour créer ton compte !")
        return

    lang = user.get("langue", "fr")
    keyboard = [
        [
            InlineKeyboardButton("📦 Standard", callback_data="plan_standard"),
            InlineKeyboardButton("⭐ Premium", callback_data="plan_premium"),
        ],
        [
            InlineKeyboardButton("🎁 Essai gratuit 24h", callback_data="plan_trial_24h"),
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

    plan = PLANS.get(plan_key, {})
    is_trial = plan.get("is_trial", False)

    if is_trial:
        tx = await create_transaction(
            user_chat_id=query.from_user.id,
            plan=plan_key,
            montant=0,
            screenshot_file_id=None
        )
        tx_id = str(tx["_id"])

        expiration = datetime.now(timezone.utc) + timedelta(hours=TRIAL_DURATION_HOURS)
        expiration_str = expiration.strftime("%d/%m/%Y à %Hh%M")

        admin_text = (
            f"🎁 *DEMANDE D'ESSAI 24H*\n\n"
            f"👤 Prénom : {user.get('prenom', '—')}\n"
            f"📧 Email : {user.get('email', '—')}\n"
            f"📍 Ville : {user.get('ville', '—')}, {user.get('pays', '—')}\n"
            f"📱 Tél : {user.get('telephone', '—')}\n"
            f"⏱️ Demande le : {datetime.now(timezone.utc).strftime('%d/%m/%Y à %Hh%M')}\n"
            f"🆔 Chat ID : `{query.from_user.id}`"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ APROUVER", callback_data=f"trial_approve_{tx_id}_{query.from_user.id}"),
                InlineKeyboardButton("❌ REJETER", callback_data=f"trial_reject_{tx_id}_{query.from_user.id}"),
            ]
        ])

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

        await query.message.reply_text(
            "📨 *Demande d'essai gratuite envoyée !* 🎁\n\n"
            "Notre équipe va traiter ta demande. Tu recevras une réponse rapidement !",
            parse_mode="Markdown"
        )
        logger.info(f"🎁 Trial demandé par {prenom} ({query.from_user.id})")
    else:
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
