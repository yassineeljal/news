import html
import logging

import requests

import config

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"

SENTIMENT_EMOJI = {"positive": "🟢", "negative": "🔴", "neutral": "⚪"}


def send_alert(article: dict, analysis: dict) -> None:
    ticker = html.escape(analysis.get("ticker") or "N/A")
    emoji = SENTIMENT_EMOJI.get(analysis.get("sentiment"), "⚪")
    impact = html.escape(analysis.get("impact", "low"))
    reason = html.escape(analysis.get("reason", ""))
    title = html.escape(article.get("title", ""))
    url = article.get("url", "")

    text = f"{emoji} <b>{ticker}</b> — impact {impact}\n{title}\n{reason}\n{url}"

    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        response = requests.post(
            TELEGRAM_API_URL.format(token=config.TELEGRAM_BOT_TOKEN),
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Échec de l'envoi Telegram pour %s", article.get("url"))
