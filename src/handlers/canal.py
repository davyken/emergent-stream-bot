import logging
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from src.ai.claude import ask_claude
from src.config.settings import CHANNEL_ID

logger = logging.getLogger(__name__)

# Mots-clés qui déclenchent une réponse du bot dans le canal
TRIGGER_KEYWORDS = [
    # Français
    "prix", "combien", "abonnement", "payer", "comment", "aide", "help",
    "accès", "acces", "lien", "film", "serie", "streaming", "connexion",
    "marche", "fonctionne", "problème", "erreur", "code", "activer",
    "starter", "premium", "famille", "orange money", "fcfa",
    "inscription", "inscrire", "compte", "créer",
    # Anglais
    "price", "how", "subscribe", "pay", "access", "link", "work",
    "problem", "error", "activate", "account", "create", "register",
    "plan", "cost", "money",
]


def should_respond(text: str) -> bool:
    """Détermine si le bot doit répondre à ce message dans le canal."""
    if not text:
        return False
    text_lower = text.lower()

    # Toujours répondre si le bot est mentionné
    if "@emerging" in text_lower or "emerging-stream" in text_lower:
        return True

    # Répondre si le message contient un mot-clé pertinent et ressemble à une question
    is_question = "?" in text or any(
        text_lower.startswith(w) for w in
        ["comment", "combien", "quoi", "quel", "où", "how", "what", "where", "when", "why", "can", "est-ce"]
    )

    has_keyword = any(kw in text_lower for kw in TRIGGER_KEYWORDS)

    return is_question and has_keyword


async def handle_canal_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Répond aux questions dans le canal avec l'IA Claude."""
    msg = update.message or update.channel_post
    if not msg or not msg.text:
        return

    # Vérifier que c'est bien le bon canal
    chat_id = str(msg.chat.id)
    if CHANNEL_ID and chat_id != str(CHANNEL_ID):
        return

    text = msg.text.strip()

    if not should_respond(text):
        return

    try:
        response = await ask_claude(text)
        if response:
            await context.bot.send_message(
                chat_id=msg.chat.id,
                text=response,
                parse_mode="Markdown",
                reply_to_message_id=msg.message_id
            )
    except Exception as e:
        logger.error(f"Erreur réponse canal : {e}")


def get_canal_handlers():
    return [
        MessageHandler(
            (filters.TEXT & ~filters.COMMAND) &
            (filters.Chat(chat_id=int(CHANNEL_ID)) if CHANNEL_ID else filters.ALL),
            handle_canal_message
        ),
    ]
