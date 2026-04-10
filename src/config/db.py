import motor.motor_asyncio
from src.config.settings import MONGO_URI, DB_NAME

client = None
db = None

async def connect_db():
    global client, db
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    # Créer les index utiles
    await db.users.create_index("chat_id", unique=True)
    await db.users.create_index("email")
    await db.users.create_index("statut")
    await db.films.create_index("titre")
    await db.transactions.create_index("user_chat_id")

    print("✅ MongoDB connecté avec succès !")
    return db

def get_db():
    return db
