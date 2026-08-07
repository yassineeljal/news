import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

LOOP_INTERVAL_MINUTES = int(os.getenv("LOOP_INTERVAL_MINUTES", "10"))

DB_PATH = os.getenv("DB_PATH", "seen_articles.db")

USE_SCRAPLING = os.getenv("USE_SCRAPLING", "false").lower() == "true"

# Flux RSS gratuits, sans clé API requise. Ajuste/complète selon tes besoins.
RSS_FEEDS = [
    "https://finance.yahoo.com/news/rssindex",
    "http://feeds.marketwatch.com/marketwatch/topstories/",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://www.investing.com/rss/news.rss",
    "https://markets.businessinsider.com/rss/news",
    # Fil de dépêches officielles (communiqués d'entreprises, résultats, M&A) —
    # la source la plus rapide : souvent publiée avant même les articles de presse.
    "https://www.prnewswire.com/rss/news-releases-list.rss",
]

# Tickers / noms d'entreprises surveillés, séparés par des virgules dans .env
WATCHED_KEYWORDS = [
    kw.strip()
    for kw in os.getenv(
        "WATCHED_KEYWORDS",
        "AAPL,Apple,TSLA,Tesla,MSFT,Microsoft,GOOGL,Google,Alphabet,"
        "AMZN,Amazon,NVDA,Nvidia,META,Meta,Facebook",
    ).split(",")
    if kw.strip()
]

# Sources additionnelles nécessitant un navigateur headless (Scrapling).
# N'est utilisé que si USE_SCRAPLING=true dans .env (nécessite un vrai VPS).
SCRAPLING_SOURCES: list[dict] = [
    {"url": "https://www.fool.com/investing-news/", "link_selector": 'a[href^="/investing/20"]'},
]

# StockTwits : sentiment de marché en temps réel par ticker. Passe par Scrapling
# (solve_cloudflare) car l'API publique est désormais derrière un challenge Cloudflare.
USE_STOCKTWITS = os.getenv("USE_STOCKTWITS", "false").lower() == "true"
STOCKTWITS_SYMBOLS = [
    s.strip()
    for s in os.getenv("STOCKTWITS_SYMBOLS", "AAPL,TSLA,MSFT,GOOGL,AMZN,NVDA,META").split(",")
    if s.strip()
]

# Reddit (r/stocks, r/wallstreetbets, ...) via l'API officielle (app-only OAuth,
# lecture seule). Nécessite une app créée sur https://www.reddit.com/prefs/apps
# (type "script").
USE_REDDIT = os.getenv("USE_REDDIT", "false").lower() == "true"
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv(
    "REDDIT_USER_AGENT", "python:stock-alert-bot:1.0 (by /u/change_me)"
)
REDDIT_SUBREDDITS = [
    s.strip()
    for s in os.getenv("REDDIT_SUBREDDITS", "stocks,wallstreetbets,investing").split(",")
    if s.strip()
]
