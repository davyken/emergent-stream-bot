"""
Tous les messages du bot en français et anglais.
Chaque message a plusieurs variantes pour paraître plus humain.
"""
import random
from src.config.settings import CHANNEL_LINK, PLANS, ORANGE_MONEY_NUMBER, ORANGE_MONEY_NAME, SERVER_ACCESS_LINK

def r(variants: list) -> str:
    """Choisit aléatoirement une variante de message."""
    return random.choice(variants)


# ─────────────────────────────────────────
#  ONBOARDING
# ─────────────────────────────────────────

def msg_welcome_new(lang="fr") -> str:
    if lang == "fr":
        return r([
            "👋 Salut toi ! Bienvenue sur *Emerging-Stream* 🎬\n\nJe vais créer ton compte en quelques secondes, c'est super rapide ! 🚀\n\nOn commence ? Dis-moi ton *prénom* 😊",
            "🎉 Heeey ! Content de te voir ici !\n\nBienvenue sur *Emerging-Stream* — le meilleur streaming pour nous 🌍\n\nPremière étape : c'est quoi ton *prénom* ? 😄",
            "👋 Bonjour et bienvenue ! 🎬\n\nJe suis le bot officiel d'*Emerging-Stream*.\nEnsemble on va créer ton compte en 1 minute chrono ⏱️\n\nAlors, ton *prénom* c'est quoi ? 😊",
        ])
    else:
        return r([
            "👋 Hey there! Welcome to *Emerging-Stream* 🎬\n\nLet's set up your account real quick! 🚀\n\nFirst things first — what's your *first name*? 😊",
            "🎉 Hey! So glad you're here!\n\nWelcome to *Emerging-Stream* — the best streaming for us 🌍\n\nWhat's your *first name*? 😄",
        ])

def msg_already_registered(prenom: str, lang="fr") -> str:
    if lang == "fr":
        return r([
            f"👋 Heeey *{prenom}* ! Re-bonjour ! 😄\n\nTon compte est déjà actif. Que puis-je faire pour toi ?\n\n👉 /abonnements — Voir les offres\n👉 /moncompte — Ton profil\n👉 /aide — Aide",
            f"🎬 *{prenom}* ! Bon retour parmi nous ! 🙌\n\nQue veux-tu faire aujourd'hui ?\n\n👉 /abonnements\n👉 /moncompte\n👉 /aide",
        ])
    else:
        return r([
            f"👋 Hey *{prenom}*! Welcome back! 😄\n\nYour account is all set. What can I help you with?\n\n👉 /subscriptions — View plans\n👉 /myaccount — Your profile\n👉 /help — Help",
        ])

def msg_ask_ville(prenom: str, lang="fr") -> str:
    if lang == "fr":
        return r([
            f"Super *{prenom}* ! 🙌\nDe quelle *ville et quel pays* tu viens ? 🌍",
            f"Parfait *{prenom}* ! 😊\nEt tu es basé où ? (*Ville & Pays*) 🌍",
            f"Cool ! 😄\nTu viens de quelle *ville* ? (et le pays aussi 😉)",
        ])
    else:
        return r([
            f"Nice *{prenom}*! 🙌\nWhich *city and country* are you from? 🌍",
        ])

def msg_ask_telephone(ville: str, lang="fr") -> str:
    if lang == "fr":
        return r([
            f"*{ville}*, c'est sympa ! 😎\n\nMaintenant, ton *numéro de téléphone* stp 📱",
            f"Ah, *{ville}* ! Beau coin 🌍\n\nJ'ai besoin de ton *numéro de téléphone* maintenant 📱",
        ])
    else:
        return r([
            f"*{ville}*, nice! 😎\n\nNow, what's your *phone number*? 📱",
        ])

def msg_ask_email(lang="fr") -> str:
    if lang == "fr":
        return r([
            "Presque fini ! 🎉\n\nTon *adresse email* stp ? 📧\n_(Elle servira pour tes confirmations et ton code d'accès)_",
            "On y est presque ! 😊\n\nDonne-moi ton *email* 📧\n_(Pour tes reçus et ton code d'activation)_",
        ])
    else:
        return r([
            "Almost done! 🎉\n\nWhat's your *email address*? 📧\n_(For your confirmations and activation code)_",
        ])

def msg_invalid_email(lang="fr") -> str:
    if lang == "fr":
        return "😅 Hmm, ça ressemble pas à un email valide...\n\nTu peux réessayer ? Format attendu : *exemple@gmail.com* 📧"
    else:
        return "😅 Hmm, that doesn't look like a valid email...\n\nCould you try again? Expected format: *example@gmail.com* 📧"

def msg_registration_complete(prenom: str, ville: str, telephone: str, email: str, lang="fr") -> str:
    if lang == "fr":
        return (
            f"🎉 *Félicitations {prenom} !* Ton compte est créé avec succès !\n\n"
            f"📋 *Ton profil :*\n"
            f"👤 Prénom : {prenom}\n"
            f"📍 Ville : {ville}\n"
            f"📱 Tél : {telephone}\n"
            f"📧 Email : {email}\n\n"
            f"Tu vas recevoir un email de confirmation dans quelques secondes 📨\n\n"
            f"📺 *Rejoins notre canal pour voir tous nos contenus :*\n"
            f"👉 {CHANNEL_LINK}\n\n"
            f"Quand tu es prêt à t'abonner, tape /abonnements 🚀"
        )
    else:
        return (
            f"🎉 *Congrats {prenom}!* Your account has been created!\n\n"
            f"📋 *Your profile:*\n"
            f"👤 Name: {prenom}\n"
            f"📍 City: {ville}\n"
            f"📱 Phone: {telephone}\n"
            f"📧 Email: {email}\n\n"
            f"You'll receive a confirmation email shortly 📨\n\n"
            f"📺 *Join our channel:*\n"
            f"👉 {CHANNEL_LINK}\n\n"
            f"Ready to subscribe? Type /subscriptions 🚀"
        )


# ─────────────────────────────────────────
#  ABONNEMENTS
# ─────────────────────────────────────────

def msg_subscriptions(lang="fr") -> str:
    p = PLANS
    if lang == "fr":
        return (
            "🎬 *Choisis ta formule Emerging-Stream !*\n\n"
            f"{p['standard']['emoji']} *BASIC* — {p['standard']['prix']:,}FCFA/mois\n"
            f"   ✓ {p['standard']['description'].replace('•', '• ')}\n\n"
            f"{p['premium']['emoji']} *PREMIUM* — {p['premium']['prix']:,}FCFA/mois\n"
            f"   ✓ {p['premium']['description'].replace('•', '• ')}\n\n"
            f"{p['trial_24h']['emoji']} *ESSAI 24H* — Gratuit\n"
            f"   ✓ {p['trial_24h']['description']}\n\n"
            "👇 *Clique sur la formule qui te convient :*"
        ).replace(",", " ")
    else:
        return (
            "🎬 *Choose your Emerging-Stream plan!*\n\n"
            f"{p['standard']['emoji']} *BASIC* — {p['standard']['prix']:,}FCFA/month\n"
            f"   ✓ {p['standard']['description'].replace('•', '• ')}\n\n"
            f"{p['premium']['emoji']} *PREMIUM* — {p['premium']['prix']:,}FCFA/month\n"
            f"   ✓ {p['premium']['description'].replace('•', '• ')}\n\n"
            f"{p['trial_24h']['emoji']} *24H TRIAL* — Free\n"
            f"   ✓ {p['trial_24h']['description']}\n\n"
            "👇 *Tap the plan you want:*"
        ).replace(",", " ")

def msg_payment_instructions(plan_key: str, prenom: str, lang="fr") -> str:
    plan = PLANS[plan_key]
    if lang == "fr":
        return (
            f"Super choix *{prenom}* ! 🙌 Le plan *{plan['nom']}* c'est excellent !\n\n"
            f"💳 *Comment payer :*\n\n"
            f"📱 *Numéro Orange Money :*\n"
            f"   `{ORANGE_MONEY_NUMBER}` _(appuie pour copier)_\n"
            f"   Nom : *{ORANGE_MONEY_NAME}*\n\n"
            f"💰 *Montant EXACT :* `{plan['prix']:,} FCFA`\n".replace(",", " ") +
            f"📝 *Objet du transfert :* `{prenom.upper()}-{plan_key.upper()}`\n\n"
            f"⏱️ Une fois le paiement effectué :\n"
            f"📸 Fais une *capture d'écran* de la confirmation\n"
            f"   et envoie-la moi ici !\n\n"
            f"J'attends ta photo 😊"
        )
    else:
        return (
            f"Great choice *{prenom}*! 🙌 *{plan['nom']}* is awesome!\n\n"
            f"💳 *How to pay:*\n\n"
            f"📱 *Orange Money Number:*\n"
            f"   `{ORANGE_MONEY_NUMBER}` _(tap to copy)_\n"
            f"   Name: *{ORANGE_MONEY_NAME}*\n\n"
            f"💰 *Exact Amount:* `{plan['prix']:,} FCFA`\n".replace(",", " ") +
            f"📝 *Transfer reference:* `{prenom.upper()}-{plan_key.upper()}`\n\n"
            f"⏱️ Once you've paid:\n"
            f"📸 Take a *screenshot* of the confirmation\n"
            f"   and send it to me here!\n\n"
            f"I'm waiting for your photo 😊"
        )

def msg_screenshot_received(lang="fr") -> str:
    if lang == "fr":
        return r([
            "📸 *Screenshot reçu !* Merci !\n\nJe transfère ça à notre équipe pour validation 🔄\nTu recevras une réponse très bientôt ! En général moins de 30 minutes 😊",
            "✅ *Bien reçu !* Ta capture est entre nos mains maintenant 🙌\nNotre équipe va vérifier ça rapidement !\nTiens-toi prêt(e) 😄",
        ])
    else:
        return r([
            "📸 *Screenshot received!* Thanks!\n\nForwarding it to our team for validation 🔄\nYou'll hear back very soon — usually within 30 minutes 😊",
        ])

def msg_approved(prenom: str, plan_key: str, code: str, expiration: str, lang="fr") -> str:
    plan = PLANS[plan_key]
    if lang == "fr":
        return (
            f"🎉 *Félicitations {prenom} !* Ton abonnement est *ACTIF* ! 🔥\n\n"
            f"📦 Plan : *{plan['nom']}*\n"
            f"📅 Valable jusqu'au : *{expiration}*\n\n"
            f"🔑 *Ton code d'activation :*\n"
            f"`{code}` _(appuie pour copier)_\n\n"
            f"🔗 *Accès au serveur de films :*\n"
            f"{SERVER_ACCESS_LINK}\n\n"
            f"🔒 Cet accès est *personnel*, ne le partage pas !\n\n"
            f"Tu recevras aussi un email avec toutes ces infos 📧\n\n"
            f"Bon visionnage *{prenom}* ! 🎬🍿"
        )
    else:
        return (
            f"🎉 *Congrats {prenom}!* Your subscription is now *ACTIVE*! 🔥\n\n"
            f"📦 Plan: *{plan['nom']}*\n"
            f"📅 Valid until: *{expiration}*\n\n"
            f"🔑 *Your activation code:*\n"
            f"`{code}` _(tap to copy)_\n\n"
            f"🔗 *Access your film server:*\n"
            f"{SERVER_ACCESS_LINK}\n\n"
            f"🔒 This access is *personal*, don't share it!\n\n"
            f"You'll also receive an email with all these details 📧\n\n"
            f"Enjoy *{prenom}*! 🎬🍿"
        )


def msg_admin_ask_code(prenom: str, chat_id: int, tx_id: str, lang="fr") -> str:
    if lang == "fr":
        return (
            f"📝 *Entrer le code d'activation*\n\n"
            f"Pour approuver l'abonnement de *{prenom}*, "
            f"envoie-moi le code d'activation que l'utilisateur devra utiliser sur le serveur.\n\n"
            f"🔐 *Message privé — répond ici directement avec le code*"
        )
    else:
        return (
            f"📝 *Enter the activation code*\n\n"
            f"To approve *{prenom}'s subscription, "
            f"send me the activation code the user will use on the server.\n\n"
            f"🔐 *Private message — reply here directly with the code*"
        )


def msg_admin_code_thanks(lang="fr") -> str:
    if lang == "fr":
        return "✅ *Merci !* L'utilisateur va recevoir son code d'activation 🎉"
    else:
        return "✅ *Thanks!* The user will receive their activation code 🎉"


def msg_admin_cancel(lang="fr") -> str:
    if lang == "fr":
        return "❌ *Abbreviation annulée.*"
    else:
        return "❌ *Approval cancelled.*"

def msg_rejected(lang="fr") -> str:
    if lang == "fr":
        return (
            "😕 *Hmm*, on n'a pas pu valider ton paiement...\n\n"
            "Il se peut que :\n"
            "• La capture soit floue ou incomplète\n"
            "• Le montant ne corresponde pas\n"
            "• Le nom de référence soit incorrect\n\n"
            "Réessaie en t'assurant que tout est correct "
            "et envoie-moi une nouvelle capture 📸\n\n"
            "Des questions ? Tape /aide 😊"
        )
    else:
        return (
            "😕 *Hmm*, we couldn't validate your payment...\n\n"
            "Possible reasons:\n"
            "• Screenshot is blurry or incomplete\n"
            "• Amount doesn't match\n"
            "• Wrong reference name\n\n"
            "Please try again and send a new screenshot 📸\n\n"
            "Questions? Type /help 😊"
        )


def msg_trialRejected(lang="fr") -> str:
    if lang == "fr":
        return (
            "😕 *Désolé*, ta demande d'essai gratuit a été refusée.\n\n"
            "Tu peux still会选择 un abonnement payant pour bénéficier de nos services ! 🎬\n\n"
            "👉 /abonnements — Voir les offres"
        )
    else:
        return (
            "😕 *Sorry*, your free trial request has been denied.\n\n"
            "You can choose a paid subscription to enjoy our services! 🎬\n\n"
            "👉 /subscriptions — View plans"
        )


def msg_trialApproved(prenom: str, code: str, expiration: str, lang="fr") -> str:
    if lang == "fr":
        return (
            f"🎉 *Essai gratuit activé, {prenom} !* 🎁\n\n"
            f"⏱️ Valable jusqu'au : *{expiration}*\n\n"
            f"🔑 *Ton code d'accès :*\n"
            f"`{code}` _(appuie pour copier)_\n\n"
            f"🔗 *Accès au serveur :*\n"
            f"{SERVER_ACCESS_LINK}\n\n"
            f"Profite bien de ces 24h gratuites ! 🎬🍿"
        )
    else:
        return (
            f"🎉 *Free trial activated, {prenom}!* 🎁\n\n"
            f"⏱️ Valid until: *{expiration}*\n\n"
            f"🔑 *Your access code:*\n"
            f"`{code}` _(tap to copy)_\n\n"
            f"🔗 *Server access:*\n"
            f"{SERVER_ACCESS_LINK}\n\n"
            f"Enjoy your 24h free trial! 🎬🍿"
        )


# ─────────────────────────────────────────
#  COMPTE & ACCÈS
# ─────────────────────────────────────────

def msg_my_account(user: dict, lang="fr") -> str:
    statut_emoji = {"active": "✅ Actif", "registered": "⏳ En attente", "expired": "❌ Expiré"}.get(user.get("statut", ""), "❓")
    plan = PLANS.get(user.get("plan_choisi", ""), {}).get("nom", "—")
    expiration = user.get("date_expiration")
    exp_str = expiration.strftime("%d/%m/%Y") if expiration else "—"
    if lang == "fr":
        return (
            f"👤 *Ton profil Emerging-Stream*\n\n"
            f"📛 Prénom : {user.get('prenom', '—')}\n"
            f"📍 Ville : {user.get('ville', '—')}, {user.get('pays', '—')}\n"
            f"📱 Tél : {user.get('telephone', '—')}\n"
            f"📧 Email : {user.get('email', '—')}\n\n"
            f"📦 Plan : {plan}\n"
            f"🔵 Statut : {statut_emoji}\n"
            f"📅 Expiration : {exp_str}\n\n"
            f"🔑 Code : `{user.get('code_activation', '—')}`"
        )
    else:
        return (
            f"👤 *Your Emerging-Stream Profile*\n\n"
            f"📛 Name: {user.get('prenom', '—')}\n"
            f"📍 City: {user.get('ville', '—')}, {user.get('pays', '—')}\n"
            f"📱 Phone: {user.get('telephone', '—')}\n"
            f"📧 Email: {user.get('email', '—')}\n\n"
            f"📦 Plan: {plan}\n"
            f"🔵 Status: {statut_emoji}\n"
            f"📅 Expires: {exp_str}\n\n"
            f"🔑 Code: `{user.get('code_activation', '—')}`"
        )

def msg_access_link(code: str, expiration: str, lang="fr") -> str:
    if lang == "fr":
        return (
            f"🔗 *Ton accès au serveur de films :*\n"
            f"{SERVER_ACCESS_LINK}\n\n"
            f"🔑 Code d'activation : `{code}`\n"
            f"📅 Valable jusqu'au : {expiration}\n\n"
            f"Bon visionnage ! 🎬🍿"
        )
    else:
        return (
            f"🔗 *Your film server access:*\n"
            f"{SERVER_ACCESS_LINK}\n\n"
            f"🔑 Activation code: `{code}`\n"
            f"📅 Valid until: {expiration}\n\n"
            f"Enjoy! 🎬🍿"
        )

def msg_no_active_sub(lang="fr") -> str:
    if lang == "fr":
        return "😕 Tu n'as pas d'abonnement actif pour le moment.\n\nTape /abonnements pour choisir une formule ! 🚀"
    else:
        return "😕 You don't have an active subscription yet.\n\nType /subscriptions to choose a plan! 🚀"


# ─────────────────────────────────────────
#  RENOUVELLEMENT
# ─────────────────────────────────────────

def msg_renewal_reminder(prenom: str, days: int, expiration: str, lang="fr") -> str:
    if lang == "fr":
        if days > 1:
            urgency = f"⏰ Hey *{prenom}* ! Ton abonnement expire dans *{days} jours* (le {expiration})."
        else:
            urgency = f"😬 *{prenom}* ! Plus qu'*UN JOUR* ! Ton accès expire demain ({expiration}) !"
        return f"{urgency}\n\nRenouvelle maintenant pour garder ton accès aux films ! 🎬\n\n👉 /abonnements"
    else:
        if days > 1:
            urgency = f"⏰ Hey *{prenom}*! Your subscription expires in *{days} days* (on {expiration})."
        else:
            urgency = f"😬 *{prenom}*! Only *ONE DAY* left! Your access expires tomorrow ({expiration})!"
        return f"{urgency}\n\nRenew now to keep your access to all films! 🎬\n\n👉 /subscriptions"

def msg_expired(prenom: str, lang="fr") -> str:
    if lang == "fr":
        return (
            f"😕 *{prenom}*, ton abonnement a expiré aujourd'hui.\n\n"
            f"Ton accès au serveur est temporairement suspendu.\n\n"
            f"Pour te réabonner c'est simple 👉 /abonnements\n"
            f"On t'attend ! 🙏"
        )
    else:
        return (
            f"😕 *{prenom}*, your subscription has expired today.\n\n"
            f"Your server access is temporarily suspended.\n\n"
            f"To resubscribe 👉 /subscriptions\n"
            f"We're waiting for you! 🙏"
        )


# ─────────────────────────────────────────
#  FILMS
# ─────────────────────────────────────────

def msg_new_film(titre: str, genre: str = "", lang="fr") -> str:
    if lang == "fr":
        genre_line = f"🎭 Genre : {genre}\n" if genre else ""
        return (
            f"🆕 *NOUVEAU FILM DISPONIBLE !* 🔥\n\n"
            f"🎬 *{titre}*\n"
            f"{genre_line}"
            f"📅 Ajouté aujourd'hui\n\n"
            f"👉 Disponible maintenant sur ton serveur !\n"
            f"{SERVER_ACCESS_LINK}\n\n"
            f"Bonne séance ! 🍿"
        )
    else:
        genre_line = f"🎭 Genre: {genre}\n" if genre else ""
        return (
            f"🆕 *NEW FILM AVAILABLE!* 🔥\n\n"
            f"🎬 *{titre}*\n"
            f"{genre_line}"
            f"📅 Added today\n\n"
            f"👉 Available now on your server!\n"
            f"{SERVER_ACCESS_LINK}\n\n"
            f"Enjoy! 🍿"
        )

def msg_deleted_film(titre: str, lang="fr") -> str:
    if lang == "fr":
        return (
            f"🗑️ *Film retiré du catalogue*\n\n"
            f"📽️ *\"{titre}\"* n'est plus disponible sur le serveur.\n\n"
            f"Des questions ? Écris à @emerging_stream_bot 😊"
        )
    else:
        return (
            f"🗑️ *Film removed from catalog*\n\n"
            f"📽️ *\"{titre}\"* is no longer available on the server.\n\n"
            f"Questions? Message @emerging_stream_bot 😊"
        )


# ─────────────────────────────────────────
#  AIDE
# ─────────────────────────────────────────

def msg_help(lang="fr") -> str:
    if lang == "fr":
        return (
            "🤖 *Commandes disponibles :*\n\n"
            "👉 /start — Créer ou accéder à ton compte\n"
            "👉 /abonnements — Voir les offres et s'abonner\n"
            "👉 /moncompte — Voir ton profil et statut\n"
            "👉 /monacces — Recevoir à nouveau ton lien\n"
            "👉 /renouveler — Renouveler ton abonnement\n"
            "👉 /aide — Afficher ce menu\n\n"
            "📧 Support : support@emerging-stream.com\n"
            "📺 Canal : " + CHANNEL_LINK
        )
    else:
        return (
            "🤖 *Available commands:*\n\n"
            "👉 /start — Create or access your account\n"
            "👉 /subscriptions — View plans and subscribe\n"
            "👉 /myaccount — View your profile and status\n"
            "👉 /myaccess — Get your access link again\n"
            "👉 /renew — Renew your subscription\n"
            "👉 /help — Show this menu\n\n"
            "📧 Support: support@emerging-stream.com\n"
            "📺 Channel: " + CHANNEL_LINK
        )
