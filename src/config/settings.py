import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_LINK = os.getenv("CHANNEL_LINK")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "emerging_stream")

# Email
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@emerging-stream.com")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Emerging-Stream")

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Serveur films
FILMS_SERVER_URL = os.getenv("FILMS_SERVER_URL")
FILMS_SERVER_API_KEY = os.getenv("FILMS_SERVER_API_KEY", "")
FILMS_SCRAPE_INTERVAL = int(os.getenv("FILMS_SCRAPE_INTERVAL", "5"))

# Orange Money
ORANGE_MONEY_NUMBER = os.getenv("ORANGE_MONEY_NUMBER")
ORANGE_MONEY_NAME = os.getenv("ORANGE_MONEY_NAME", "EMERGING STREAM")

# Abonnements
PLANS = {
    "starter": {
        "nom": "⚡ Starter",
        "prix": int(os.getenv("PRICE_STARTER", "2500")),
        "description": "5 000+ chaînes • HD • 1 écran",
        "emoji": "⚡"
    },
    "premium": {
        "nom": "⭐ Premium",
        "prix": int(os.getenv("PRICE_PREMIUM", "4500")),
        "description": "10 000+ chaînes • 4K • 3 écrans • Offline",
        "emoji": "⭐"
    },
    "famille": {
        "nom": "👑 Famille",
        "prix": int(os.getenv("PRICE_FAMILLE", "7500")),
        "description": "Tout Premium • 6 écrans • Contrôle parental",
        "emoji": "👑"
    },
    "trial_24h": {
        "nom": "🎁 Essai 24h",
        "prix": 0,
        "description": "24h gratuit • Accès complet",
        "emoji": "🎁",
        "is_trial": True,
        "duree_heures": 24
    }
}

SUBSCRIPTION_DURATION_DAYS = int(os.getenv("SUBSCRIPTION_DURATION_DAYS", "31"))
TRIAL_DURATION_HOURS = 24
SERVER_ACCESS_LINK = os.getenv("SERVER_ACCESS_LINK")
