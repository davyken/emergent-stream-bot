# 🎬 Emerging-Stream Bot Telegram

Bot complet de gestion d'abonnements, paiements et notifications pour le service de streaming Emerging-Stream.

---

## ✅ Fonctionnalités

- Inscription complète (prénom, ville, téléphone, email)
- Email de bienvenue automatique après inscription
- Lien canal Telegram envoyé après inscription
- Affichage des abonnements avec boutons inline
- Instructions de paiement Orange Money
- Réception de screenshot → transfert admin
- Boutons Approuver / Rejeter pour l'admin
- Code d'activation unique généré automatiquement
- Email d'activation avec code + lien serveur
- Surveillance du serveur de films (toutes les 5 min)
- Notifications canal + DM + email pour nouveaux films
- Notifications canal + DM + email pour films supprimés
- Rappels renouvellement J-5 / J-1 / expiration (DM + email)
- Réponses IA dans le canal (FR + EN + tolérance fautes)

---

## 🚀 Installation

### 1. Cloner et installer

```bash
git clone https://github.com/ton-repo/emerging-stream-bot.git
cd emerging-stream-bot
pip install -r requirements.txt
```

### 2. Configurer le `.env`

Copie et remplis toutes les variables :

```bash
cp .env .env.backup  # sauvegarde
nano .env            # édite avec tes vraies valeurs
```

Variables obligatoires à remplir :
- `BOT_TOKEN` → depuis @BotFather sur Telegram
- `ADMIN_CHAT_ID` → ton ID Telegram (utilise @userinfobot pour le trouver)
- `CHANNEL_ID` → ID du canal (ex: -1001234567890)
- `CHANNEL_LINK` → lien public du canal
- `MONGO_URI` → URI MongoDB Atlas
- `RESEND_API_KEY` → depuis resend.com (gratuit)
- `ANTHROPIC_API_KEY` → depuis console.anthropic.com
- `FILMS_SERVER_URL` → URL de ton serveur de films
- `ORANGE_MONEY_NUMBER` → ton numéro OM
- `SERVER_ACCESS_LINK` → lien d'accès envoyé aux abonnés

### 3. Lancer le bot

```bash
python -m src.bot
```

---

## 📦 Obtenir ses clés

### BOT_TOKEN
1. Ouvre Telegram → cherche @BotFather
2. Tape `/newbot`
3. Suis les instructions → copie le token

### ADMIN_CHAT_ID
1. Cherche @userinfobot sur Telegram
2. Tape `/start` → il t'affiche ton ID

### CHANNEL_ID
1. Ajoute @username_to_id_bot dans ton canal
2. Il t'affiche l'ID (commence par -100...)

### MONGO_URI
1. Va sur mongodb.com/atlas → créer compte gratuit
2. Crée un cluster → Connect → Drivers
3. Copie l'URI (remplace `<password>` par ton vrai mot de passe)

### RESEND_API_KEY
1. Va sur resend.com → créer compte gratuit
2. API Keys → Create API Key
3. Configure ton domaine email si tu en as un

### ANTHROPIC_API_KEY
1. Va sur console.anthropic.com
2. API Keys → Create Key

---

## 🔧 Adapter le watcher au serveur de films

Dans `src/watchers/film_watcher.py`, la fonction `fetch_films_from_server()` gère 3 cas :

**Cas 1 — API JSON** (Jellyfin, Emby, API custom) :
Le bot détecte automatiquement le JSON et parse les titres.

**Cas 2 — Page HTML** :
Modifie les sélecteurs CSS dans la liste `selectors_to_try` selon ta page.

**Cas 3 — Plex** :
Change l'URL par : `http://ton-plex:32400/library/sections/1/all?X-Plex-Token=TON_TOKEN`

---

## 📁 Structure du projet

```
emerging-stream-bot/
├── src/
│   ├── bot.py                    ← Point d'entrée principal
│   ├── ai/claude.py              ← IA pour le canal
│   ├── conversations/onboarding.py  ← FSM inscription
│   ├── handlers/
│   │   ├── subscriptions.py      ← Plans + paiement
│   │   ├── payment.py            ← Screenshot → admin
│   │   ├── admin.py              ← Approuver/Rejeter
│   │   ├── account.py            ← Compte + accès
│   │   └── canal.py              ← Réponses IA canal
│   ├── email/
│   │   ├── email_service.py      ← Resend
│   │   └── templates/
│   │       ├── base.py           ← Template HTML
│   │       └── all_templates.py  ← Bienvenue/Activation/Rappel/Film
│   ├── models/
│   │   ├── user.py               ← Schéma utilisateur
│   │   ├── transaction.py        ← Schéma paiements
│   │   └── film.py               ← Catalogue films
│   ├── watchers/film_watcher.py  ← Surveillance serveur
│   ├── jobs/renewal_job.py       ← Cron renouvellement
│   ├── utils/
│   │   ├── messages.py           ← Tous les textes FR/EN
│   │   ├── broadcast.py          ← Envoi masse Telegram
│   │   ├── code_generator.py     ← Codes d'activation
│   │   └── lang.py               ← Détection langue + normalisation
│   └── config/
│       ├── settings.py           ← Variables d'environnement
│       └── db.py                 ← Connexion MongoDB
├── .env                          ← Tes variables (ne pas committer !)
├── requirements.txt
└── README.md
```

---

## 🌐 Déploiement sur Railway

1. Crée un compte sur railway.app
2. New Project → Deploy from GitHub
3. Ajoute toutes les variables du `.env` dans Railway → Variables
4. Start command : `python -m src.bot`
5. Deploy !

---

## 📞 Support

Email : support@emerging-stream.com
