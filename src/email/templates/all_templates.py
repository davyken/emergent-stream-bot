from src.email.templates.base import base_template
from src.email.email_service import send_email
from src.config.settings import SERVER_ACCESS_LINK, PLANS


# ─── 1. Email de bienvenue après inscription ───────────────────────────────

async def send_welcome_email(prenom: str, email: str, ville: str, telephone: str):
    content = f"""
    <div class="tag">🎉 Bienvenue !</div>
    <h1>Bonjour {prenom} ! 👋</h1>
    <p>Ton compte <strong>Emerging-Stream</strong> a été créé avec succès. On est ravis de t'avoir parmi nous ! 🙌</p>
    <hr class="divider"/>
    <p><strong>📋 Ton profil :</strong></p>
    <ul>
      <li>👤 Prénom : <span class="highlight">{prenom}</span></li>
      <li>📍 Ville : <span class="highlight">{ville}</span></li>
      <li>📱 Tél : <span class="highlight">{telephone}</span></li>
      <li>📧 Email : <span class="highlight">{email}</span></li>
    </ul>
    <hr class="divider"/>
    <p>✅ Prochaine étape : choisis ton abonnement en tapant <strong>/abonnements</strong> sur le bot Telegram.</p>
    <p style="color:#7a8694;font-size:13px;">Tu as reçu cet email car tu viens de t'inscrire sur Emerging-Stream.</p>
    """
    await send_email(
        to=email,
        subject=f"👋 Bienvenue sur Emerging-Stream, {prenom} !",
        html=base_template(content)
    )


# ─── 2. Email d'activation avec code ──────────────────────────────────────

async def send_activation_email(prenom: str, email: str, plan_key: str, code: str, expiration: str):
    plan = PLANS.get(plan_key, {})
    plan_nom = plan.get("nom", plan_key)
    content = f"""
    <div class="tag">✅ Abonnement Activé</div>
    <h1>Félicitations {prenom} ! 🎉</h1>
    <p>Ton abonnement <span class="highlight">{plan_nom}</span> est maintenant <strong>ACTIF</strong> ! 🔥</p>
    <p>📅 Valable jusqu'au : <span class="highlight">{expiration}</span></p>
    <hr class="divider"/>
    <p><strong>🔑 Ton code d'activation unique :</strong></p>
    <div class="code-box">
      <div class="code">{code}</div>
      <p style="color:#7a8694;font-size:12px;margin:8px 0 0;">Garde ce code précieusement — il est personnel.</p>
    </div>
    <p><strong>🔗 Accès au serveur de films :</strong></p>
    <p><a href="{SERVER_ACCESS_LINK}" style="color:#c9a84c;">{SERVER_ACCESS_LINK}</a></p>
    <a href="{SERVER_ACCESS_LINK}" class="btn">🍿 Accéder au serveur</a>
    <hr class="divider"/>
    <p><strong>📖 Comment utiliser ton code :</strong></p>
    <ul>
      <li>Va sur le serveur via le lien ci-dessus</li>
      <li>Clique sur <em>"Se connecter"</em></li>
      <li>Entre ton code d'activation</li>
      <li>Profite de tous les films ! 🎬</li>
    </ul>
    <hr class="divider"/>
    <p style="color:#7a8694;font-size:13px;">🔒 Cet accès est personnel. Ne le partage pas.</p>
    """
    await send_email(
        to=email,
        subject=f"🎬 Ton accès Emerging-Stream est activé, {prenom} !",
        html=base_template(content)
    )


# ─── 3. Emails de rappel renouvellement ───────────────────────────────────

async def send_renewal_reminder_email(prenom: str, email: str, days: int, expiration: str, plan_key: str):
    plan = PLANS.get(plan_key, {})
    plan_nom = plan.get("nom", plan_key)

    if days > 1:
        subject = f"⏰ Ton abonnement expire dans {days} jours, {prenom} !"
        urgency_html = f"""
        <div class="tag">⏰ Rappel renouvellement</div>
        <h1>Hey {prenom} ! 👋</h1>
        <p>Ton abonnement <span class="highlight">{plan_nom}</span> expire dans <strong>{days} jours</strong> (le {expiration}).</p>
        <p>Renouvelle maintenant pour ne pas interrompre ton accès à des milliers de films ! 🎬</p>
        """
    else:
        subject = f"😬 Dernière chance {prenom} — Ton accès expire DEMAIN !"
        urgency_html = f"""
        <div class="tag">🚨 Urgent — Expire demain</div>
        <h1>⚠️ {prenom}, il ne reste qu'un jour !</h1>
        <p>Ton abonnement <span class="highlight">{plan_nom}</span> expire <strong>DEMAIN</strong> ({expiration}).</p>
        <p>Renouvelle maintenant pour ne pas perdre ton accès ! ⚡</p>
        """

    content = f"""
    {urgency_html}
    <hr class="divider"/>
    <p>📱 Pour renouveler, retourne sur le bot Telegram et tape <strong>/abonnements</strong></p>
    <p style="color:#7a8694;font-size:13px;">Merci de faire partie de la famille Emerging-Stream 🙏</p>
    """
    await send_email(to=email, subject=subject, html=base_template(content))


async def send_expired_email(prenom: str, email: str):
    content = f"""
    <div class="tag">😕 Abonnement expiré</div>
    <h1>{prenom}, ton accès a expiré</h1>
    <p>Ton abonnement <strong>Emerging-Stream</strong> a expiré aujourd'hui. Ton accès au serveur est temporairement suspendu.</p>
    <p>Mais bonne nouvelle : tu peux te réabonner à tout moment en quelques minutes !</p>
    <hr class="divider"/>
    <p>📱 Retourne sur le bot Telegram et tape <strong>/abonnements</strong> pour choisir ta nouvelle formule.</p>
    <p style="color:#7a8694;font-size:13px;">On espère te revoir très vite ! 🙏</p>
    """
    await send_email(
        to=email,
        subject=f"😕 Ton abonnement Emerging-Stream a expiré",
        html=base_template(content)
    )


# ─── 4. Email nouveau film ─────────────────────────────────────────────────

async def send_new_film_email(email: str, prenom: str, titre: str, genre: str = "", is_active: bool = True):
    genre_html = f"<li>🎭 Genre : <span class='highlight'>{genre}</span></li>" if genre else ""

    if is_active:
        cta = f'<a href="{SERVER_ACCESS_LINK}" class="btn">🍿 Regarder maintenant</a>'
        sub_note = ""
    else:
        cta = ""
        sub_note = """
        <hr class="divider"/>
        <p style="background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:16px;">
          📢 Tu n'as plus d'abonnement actif ? <strong>Réabonne-toi pour accéder à ce film !</strong><br/>
          Tape <strong>/abonnements</strong> sur le bot Telegram. 🚀
        </p>
        """

    content = f"""
    <div class="tag">🆕 Nouveau film ajouté</div>
    <h1>Nouveau film sur Emerging-Stream ! 🔥</h1>
    <p>Hey {prenom} ! Un nouveau contenu vient d'être ajouté à ton serveur :</p>
    <hr class="divider"/>
    <ul>
      <li>🎬 Titre : <span class="highlight" style="font-size:18px;">{titre}</span></li>
      {genre_html}
      <li>📅 Disponible dès maintenant</li>
    </ul>
    <hr class="divider"/>
    {cta}
    {sub_note}
    """
    await send_email(
        to=email,
        subject=f"🎬 \"{titre}\" vient d'arriver sur Emerging-Stream !",
        html=base_template(content)
    )


async def send_deleted_film_email(email: str, prenom: str, titre: str):
    content = f"""
    <div class="tag">🗑️ Film retiré</div>
    <h1>Un film a été retiré</h1>
    <p>Hey {prenom} ! On t'informe qu'un film a été retiré du catalogue :</p>
    <hr class="divider"/>
    <p style="font-size:18px;">📽️ <span class="highlight">"{titre}"</span> n'est plus disponible.</p>
    <hr class="divider"/>
    <p>Pas d'inquiétude, de nouveaux contenus arrivent régulièrement ! 🎬</p>
    <p style="color:#7a8694;font-size:13px;">Des questions ? Contacte-nous sur le bot Telegram.</p>
    """
    await send_email(
        to=email,
        subject=f"📽️ \"{titre}\" retiré du catalogue Emerging-Stream",
        html=base_template(content)
    )
