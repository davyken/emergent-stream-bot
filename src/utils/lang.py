from thefuzz import fuzz

# Mots-clés pour détecter l'anglais
EN_KEYWORDS = [
    "hello", "hi", "hey", "how", "what", "where", "help", "subscribe",
    "subscription", "pay", "payment", "price", "plan", "access", "film",
    "movie", "watch", "account", "my", "i want", "i need", "please", "thank"
]

FR_KEYWORDS = [
    "bonjour", "salut", "allo", "comment", "quoi", "où", "aide", "abonnement",
    "abonner", "payer", "paiement", "prix", "plan", "accès", "film", "regarder",
    "compte", "je veux", "je voudrais", "sil vous plait", "merci", "svp", "stp"
]


def detect_language(text: str) -> str:
    """Détecte la langue (fr/en) avec tolérance aux fautes."""
    text_lower = text.lower().strip()

    en_score = max((fuzz.partial_ratio(text_lower, kw) for kw in EN_KEYWORDS), default=0)
    fr_score = max((fuzz.partial_ratio(text_lower, kw) for kw in FR_KEYWORDS), default=0)

    return "en" if en_score > fr_score and en_score > 70 else "fr"


def is_valid_email(email: str) -> bool:
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def normalize_name(text: str) -> str:
    """Nettoie le prénom de tout texte parasite."""
    words = text.strip().split()
    # On prend le premier mot s'il n'y a pas de contexte clair
    # et on capitalise
    clean = []
    for w in words:
        if len(w) > 1 and w.isalpha():
            clean.append(w.capitalize())
        if len(clean) == 2:  # max prénom + nom
            break
    return " ".join(clean) if clean else text.strip().capitalize()


def normalize_city(text: str) -> str:
    """Essaie d'extraire ville et pays du texte."""
    # Gère les formats: "douala cameroun", "je sui a doul au camroun", etc.
    # Retourne simplement le texte nettoyé en title case
    words = text.strip().split()
    # Filtre les mots parasites courants
    stop_words = {"je", "suis", "sui", "je suis", "a", "au", "en", "de", "du", "habite", "vit", "vis", "dans", "i", "am", "from", "in", "live"}
    filtered = [w for w in words if w.lower() not in stop_words and len(w) > 1]
    return " ".join(w.capitalize() for w in filtered) if filtered else text.strip().title()
