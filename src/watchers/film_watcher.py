import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from telegram import Bot

from src.models.film import add_film, remove_film, sync_films
from src.models.user import get_all_active_users, get_all_users
from src.utils.messages import msg_new_film, msg_deleted_film
from src.utils.broadcast import broadcast_to_users
from src.email.templates.all_templates import send_new_film_email, send_deleted_film_email
from src.config.settings import (
    FILMS_SERVER_URL, FILMS_SERVER_API_KEY,
    CHANNEL_ID, ADMIN_CHAT_ID
)

logger = logging.getLogger(__name__)


async def fetch_films_from_server() -> list[dict]:
    """
    Récupère la liste des films depuis le serveur.
    Adapte cette fonction selon la structure de TON serveur.

    Retourne une liste de dicts : [{"titre": "...", "genre": "...", "duree": "..."}, ...]

    ─── CAS 1 : Ton serveur expose une API JSON ────────────────────────────
    Exemple : GET https://monserveur.com/api/films
    Réponse : [{"title": "Film X", "genre": "Action"}, ...]

    ─── CAS 2 : Ton serveur est une page HTML ──────────────────────────────
    On scrape les titres avec BeautifulSoup.

    ─── CAS 3 : Plex ou Jellyfin ───────────────────────────────────────────
    Ils ont des APIs natives avec token.
    """
    headers = {}
    if FILMS_SERVER_API_KEY:
        headers["Authorization"] = f"Bearer {FILMS_SERVER_API_KEY}"
        headers["X-Api-Key"] = FILMS_SERVER_API_KEY

    films = []

    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(FILMS_SERVER_URL, headers=headers) as resp:
                content_type = resp.headers.get("Content-Type", "")

                # ── CAS 1 : API JSON ──────────────────────────────────────
                if "application/json" in content_type or "json" in content_type:
                    data = await resp.json()

                    # Format Jellyfin/Emby
                    if isinstance(data, dict) and "Items" in data:
                        for item in data["Items"]:
                            films.append({
                                "titre": item.get("Name", ""),
                                "genre": ", ".join(item.get("Genres", [])),
                                "duree": str(item.get("RunTimeTicks", "")),
                            })

                    # Format liste simple
                    elif isinstance(data, list):
                        for item in data:
                            titre = item.get("title") or item.get("titre") or item.get("name") or item.get("Name", "")
                            genre = item.get("genre") or item.get("Genre") or item.get("genres") or ""
                            if isinstance(genre, list):
                                genre = ", ".join(genre)
                            if titre:
                                films.append({"titre": titre, "genre": genre, "duree": ""})

                # ── CAS 2 : Page HTML ─────────────────────────────────────
                else:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Adapte les sélecteurs CSS à ta page HTML
                    # Exemples de sélecteurs courants :
                    selectors_to_try = [
                        "h2.film-title",       # <h2 class="film-title">Film X</h2>
                        ".movie-title",        # <* class="movie-title">
                        ".film-name",          # <* class="film-name">
                        "a.title",             # <a class="title">
                        ".card-title",         # Cartes Bootstrap
                        "h3",                  # Titres génériques
                    ]

                    found = []
                    for selector in selectors_to_try:
                        found = soup.select(selector)
                        if found:
                            break

                    for el in found:
                        titre = el.get_text(strip=True)
                        if titre and len(titre) > 2:
                            films.append({"titre": titre, "genre": "", "duree": ""})

    except asyncio.TimeoutError:
        logger.error("⏱️ Timeout : le serveur de films ne répond pas.")
    except Exception as e:
        logger.error(f"❌ Erreur fetch films : {e}")

    logger.info(f"🎬 {len(films)} films récupérés depuis le serveur.")
    return films


async def check_and_notify(bot: Bot):
    """
    Compare le catalogue actuel avec la DB.
    Notifie si des films ont été ajoutés ou supprimés.
    """
    try:
        raw_films = await fetch_films_from_server()
        if not raw_films:
            logger.warning("⚠️ Aucun film récupéré — serveur vide ou inaccessible.")
            return

        current_titles = [f["titre"] for f in raw_films if f["titre"]]
        films_map = {f["titre"]: f for f in raw_films}

        nouveaux_titres, supprimes_titres = await sync_films(current_titles)

        active_users = await get_all_active_users()
        all_users = await get_all_users()

        # ── Nouveaux films ────────────────────────────────────────────────
        for titre in nouveaux_titres:
            film_data = films_map.get(titre, {})
            genre = film_data.get("genre", "")

            await add_film(titre=titre, genre=genre, duree=film_data.get("duree", ""))
            logger.info(f"🆕 Nouveau film ajouté : {titre}")

            # 1. Message dans le canal
            if CHANNEL_ID:
                try:
                    await bot.send_message(
                        chat_id=CHANNEL_ID,
                        text=msg_new_film(titre, genre, lang="fr"),
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.error(f"Erreur canal nouveau film : {e}")

            # 2. Admin DM
            try:
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"🆕 *Nouveau film détecté :* {titre}\n🎭 Genre : {genre or '—'}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Erreur DM admin : {e}")

            # 3. DM à tous les abonnés actifs
            await broadcast_to_users(
                bot=bot,
                users=active_users,
                message=msg_new_film(titre, genre, lang="fr")
            )

            # 4. Email à TOUS les utilisateurs (actifs + expirés)
            for user in all_users:
                email = user.get("email")
                prenom = user.get("prenom", "")
                if not email:
                    continue
                is_active = user.get("statut") == "active"
                try:
                    await send_new_film_email(email, prenom, titre, genre, is_active=is_active)
                    await asyncio.sleep(0.1)  # anti-spam
                except Exception as e:
                    logger.error(f"Erreur email nouveau film à {email}: {e}")

        # ── Films supprimés ───────────────────────────────────────────────
        for titre in supprimes_titres:
            await remove_film(titre)
            logger.info(f"🗑️ Film supprimé : {titre}")

            # 1. Message dans le canal
            if CHANNEL_ID:
                try:
                    await bot.send_message(
                        chat_id=CHANNEL_ID,
                        text=msg_deleted_film(titre, lang="fr"),
                        parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.error(f"Erreur canal film supprimé : {e}")

            # 2. Admin DM
            try:
                await bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"🗑️ *Film supprimé :* {titre}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Erreur DM admin suppression : {e}")

            # 3. DM abonnés actifs
            await broadcast_to_users(
                bot=bot,
                users=active_users,
                message=msg_deleted_film(titre, lang="fr")
            )

            # 4. Email abonnés actifs
            for user in active_users:
                email = user.get("email")
                prenom = user.get("prenom", "")
                if not email:
                    continue
                try:
                    await send_deleted_film_email(email, prenom, titre)
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"Erreur email suppression à {email}: {e}")

    except Exception as e:
        logger.error(f"❌ Erreur watcher films : {e}")
