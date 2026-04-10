from datetime import datetime, timezone
from src.config.db import get_db

async def create_user(chat_id: int, prenom: str, ville: str, pays: str, telephone: str, email: str, langue: str = "fr"):
    db = get_db()
    user = {
        "chat_id": chat_id,
        "prenom": prenom,
        "ville": ville,
        "pays": pays,
        "telephone": telephone,
        "email": email,
        "langue": langue,
        "statut": "registered",        # registered | active | expired | banned
        "plan_choisi": None,
        "code_activation": None,
        "date_inscription": datetime.now(timezone.utc),
        "date_expiration": None,
        "lien_acces": None,
        "emails_envoyes": [],
        "pending_plan": None,           # plan en attente de validation
        "state": None,                  # état FSM conversation
    }
    await db.users.insert_one(user)
    return user

async def get_user(chat_id: int):
    db = get_db()
    return await db.users.find_one({"chat_id": chat_id})

async def update_user(chat_id: int, data: dict):
    db = get_db()
    await db.users.update_one({"chat_id": chat_id}, {"$set": data})

async def get_all_active_users():
    db = get_db()
    return await db.users.find({"statut": "active"}).to_list(length=None)

async def get_all_users():
    db = get_db()
    return await db.users.find({}).to_list(length=None)

async def get_expiring_users(days_left: int):
    """Retourne les users dont l'abonnement expire dans exactement X jours."""
    from datetime import timedelta
    db = get_db()
    now = datetime.now(timezone.utc)
    target_start = now.replace(hour=0, minute=0, second=0) + timedelta(days=days_left)
    target_end = target_start + timedelta(days=1)
    return await db.users.find({
        "statut": "active",
        "date_expiration": {"$gte": target_start, "$lt": target_end}
    }).to_list(length=None)

async def get_expired_users():
    """Retourne les users dont l'abonnement a expiré aujourd'hui."""
    from datetime import timedelta
    db = get_db()
    now = datetime.now(timezone.utc)
    return await db.users.find({
        "statut": "active",
        "date_expiration": {"$lt": now}
    }).to_list(length=None)
