"""Sentiment retail via l'API officielle Reddit (app-only OAuth, lecture seule).

Nécessite une app "script" créée sur https://www.reddit.com/prefs/apps
(REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET dans .env). N'utilise aucun scraping :
c'est l'API publique sanctionnée par Reddit.
"""

import logging
import time

import requests

import config

logger = logging.getLogger(__name__)

_token: str | None = None
_token_expiry: float = 0


def _get_token() -> str | None:
    global _token, _token_expiry
    if _token and time.time() < _token_expiry:
        return _token

    try:
        response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=(config.REDDIT_CLIENT_ID, config.REDDIT_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": config.REDDIT_USER_AGENT},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        _token = data["access_token"]
        _token_expiry = time.time() + data.get("expires_in", 3600) - 60
        return _token
    except requests.RequestException:
        logger.exception("Échec d'authentification Reddit")
        return None


def collect_from_reddit() -> list[dict]:
    token = _get_token()
    if not token:
        return []

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": config.REDDIT_USER_AGENT,
    }

    articles = []
    for subreddit in config.REDDIT_SUBREDDITS:
        try:
            response = requests.get(
                f"https://oauth.reddit.com/r/{subreddit}/new",
                headers=headers,
                params={"limit": 25},
                timeout=10,
            )
            response.raise_for_status()
            for child in response.json().get("data", {}).get("children", []):
                post = child.get("data", {})
                permalink = post.get("permalink")
                if not permalink:
                    continue
                articles.append(
                    {
                        "title": post.get("title", ""),
                        "url": f"https://reddit.com{permalink}",
                        "summary": (post.get("selftext") or "")[:500],
                        "source": f"r/{subreddit}",
                    }
                )
        except requests.RequestException:
            logger.exception("Échec de collecte Reddit pour r/%s", subreddit)
    return articles
