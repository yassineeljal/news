# Stock Alert Bot

Bot d'alertes boursières 100% gratuit : collecte des flux RSS financiers (+ scraping
optionnel de sites protégés via Scrapling), filtre par mots-clés, analyse d'impact
via Groq (Llama 3.3 70B), et envoie une alerte Telegram si pertinent.

## Architecture

- `collector.py` — collecte les articles depuis les flux RSS (`config.RSS_FEEDS`)
- `scraper.py` — collecte optionnelle via navigateur headless (Scrapling), pour les
  sites protégés qui bloquent le scraping simple. Activé via `USE_SCRAPLING=true`.
- `keyword_filter.py` — pré-filtre les articles par ticker/nom d'entreprise avant
  d'appeler l'IA, pour économiser le quota Groq
- `analyzer.py` — envoie les articles retenus à Groq et récupère une analyse
  structurée (pertinence, ticker, sentiment, impact)
- `notifier.py` — envoie l'alerte formatée sur Telegram
- `db.py` — déduplication SQLite (un article n'est analysé qu'une fois)
- `main.py` — orchestre le pipeline, en une passe (`--once`) ou en boucle

## Installation locale

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
scrapling install   # uniquement si tu comptes utiliser USE_SCRAPLING=true

cp .env.example .env
# édite .env : GROQ_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, WATCHED_KEYWORDS
```

Comptes gratuits nécessaires :

1. **Groq** — console.groq.com, connexion Google, génère une clé `gsk_...`. Pas de carte.
2. **Bot Telegram** — parle à `@BotFather` sur Telegram, `/newbot`, récupère le token.
   Pour ton `chat_id` : envoie un message au bot puis va sur
   `https://api.telegram.org/bot<TOKEN>/getUpdates`.

## Tester en local

```bash
python main.py --once
```

Vérifie les logs : nombre d'articles collectés, nombre après pré-filtre mots-clés,
et si des alertes Telegram sont bien envoyées.

## Hébergement gratuit — deux options

### Option A — VPS Oracle Cloud Always Free (recommandée, supporte Scrapling)

Scrapling a besoin d'un navigateur headless : il faut un vrai VPS Linux, pas un
service serverless.

1. Crée un compte sur cloud.oracle.com (carte demandée pour vérification d'identité,
   rien n'est débité sur le tier Always Free).
2. Crée une instance Compute : shape **Ampere (ARM)**, image **Ubuntu 24.04 Minimal
   aarch64**, type de capacité "On-demand".
3. Si erreur "out of capacity" : réessaie plus tard ou change de région — c'est un
   piège connu d'Oracle sur ce tier.
4. En SSH sur le VPS :

   ```bash
   git clone <url-de-ce-repo> news
   cd news
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   scrapling install
   cp .env.example .env   # édite avec tes vraies clés
   python main.py --once  # teste une passe
   ```

5. Installe le service systemd pour tourner 24/7 :

   ```bash
   sudo cp deploy/stockbot.service /etc/systemd/system/stockbot.service
   # adapte WorkingDirectory/ExecStart dans le fichier si le chemin diffère
   sudo systemctl daemon-reload
   sudo systemctl enable stockbot     # démarre au boot
   sudo systemctl start stockbot      # lance maintenant
   sudo systemctl status stockbot     # vérifie
   journalctl -u stockbot -f          # logs en direct
   ```

### Option B — GitHub Actions (RSS uniquement, sans Scrapling)

Si tu te contentes des flux RSS (pas de sites protégés), pas besoin de VPS :
`.github/workflows/rss-only.yml` tourne toutes les 15 min gratuitement.

1. Pousse ce repo sur GitHub.
2. Dans Settings → Secrets and variables → Actions, ajoute :
   `GROQ_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
3. Le workflow committe `seen_articles.db` après chaque run pour garder la dédup
   d'une exécution à l'autre.

## Rester sous la limite gratuite Groq

- Le pré-filtre par mots-clés (`keyword_filter.py`) élimine la majorité des articles
  avant l'appel IA — ajuste `WATCHED_KEYWORDS` dans `.env` pour rester précis.
- La dédup SQLite garantit qu'un article n'est jamais analysé deux fois.
- Si tu tapes le plafond de requêtes/jour (logs avec `rate limit`), augmente
  `LOOP_INTERVAL_MINUTES` ou resserre la liste de mots-clés.

## Coût réel

0 €/mois : Groq gratuit pour l'IA, Oracle Always Free (ou GitHub Actions) pour
l'hébergement, Telegram et flux RSS gratuits.
