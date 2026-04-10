from datetime import datetime, timezone
from src.config.db import get_db

async def get_all_films():
    db = get_db()
    return await db.films.find({"statut": "disponible"}).to_list(length=None)

async def get_film_by_titre(titre: str):
    db = get_db()
    return await db.films.find_one({"titre": titre})

async def add_film(titre: str, genre: str = "", duree: str = "", url: str = ""):
    db = get_db()
    film = {
        "titre": titre,
        "genre": genre,
        "duree": duree,
        "url": url,
        "statut": "disponible",
        "date_ajout": datetime.now(timezone.utc),
        "date_suppression": None,
    }
    await db.films.insert_one(film)
    return film

async def remove_film(titre: str):
    db = get_db()
    await db.films.update_one(
        {"titre": titre},
        {"$set": {"statut": "supprime", "date_suppression": datetime.now(timezone.utc)}}
    )

async def sync_films(current_titles: list[str]):
    """Compare la liste actuelle avec la DB, retourne (nouveaux, supprimes)."""
    db = get_db()
    db_films = await db.films.find({"statut": "disponible"}).to_list(length=None)
    db_titles = {f["titre"] for f in db_films}
    current_set = set(current_titles)

    nouveaux = current_set - db_titles
    supprimes = db_titles - current_set

    return list(nouveaux), list(supprimes)
