"""Sentiment de marché en temps réel via StockTwits, par ticker surveillé.

Passe par Scrapling (solve_cloudflare) car l'API publique de StockTwits est
désormais protégée par un challenge Cloudflare. Nécessite donc les mêmes
prérequis que le scraping classique (navigateur headless, vrai VPS).
"""

import json
import logging

import config

logger = logging.getLogger(__name__)

STOCKTWITS_URL = "https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"


def collect_from_stocktwits() -> list[dict]:
    from scrapling.fetchers import StealthyFetcher

    articles = []
    for symbol in config.STOCKTWITS_SYMBOLS:
        try:
            page = StealthyFetcher.fetch(
                STOCKTWITS_URL.format(symbol=symbol),
                headless=True,
                solve_cloudflare=True,
            )
            data = json.loads(page.body)
            for msg in data.get("messages", []):
                msg_id = msg.get("id")
                body = msg.get("body", "")
                if not msg_id or not body:
                    continue
                articles.append(
                    {
                        "title": f"StockTwits ${symbol}: {body[:120]}",
                        "url": f"https://stocktwits.com/symbol/{symbol}/message/{msg_id}",
                        "summary": body,
                        "source": f"StockTwits ${symbol}",
                    }
                )
        except Exception:
            logger.exception("Échec de collecte StockTwits pour %s", symbol)
    return articles
