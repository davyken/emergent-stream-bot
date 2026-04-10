from datetime import datetime, timezone
from src.config.db import get_db

async def create_transaction(user_chat_id: int, plan: str, montant: int, screenshot_file_id: str):
    db = get_db()
    tx = {
        "user_chat_id": user_chat_id,
        "plan": plan,
        "montant": montant,
        "screenshot_file_id": screenshot_file_id,
        "statut": "pending",           # pending | approved | rejected
        "date_soumission": datetime.now(timezone.utc),
        "date_traitement": None,
        "admin_id": None,
    }
    result = await db.transactions.insert_one(tx)
    tx["_id"] = result.inserted_id
    return tx

async def update_transaction(tx_id, data: dict):
    from bson import ObjectId
    db = get_db()
    await db.transactions.update_one({"_id": ObjectId(tx_id)}, {"$set": data})

async def get_transaction(tx_id):
    from bson import ObjectId
    db = get_db()
    return await db.transactions.find_one({"_id": ObjectId(tx_id)})
