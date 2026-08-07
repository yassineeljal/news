import logging

import feedparser

import config

logger = logging.getLogger(__name__)


def collect_from_rss() -> list[dict]:
    articles = []
    for feed_url in config.RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
            feed_title = parsed.feed.get("title", feed_url)
            for entry in parsed.entries:
                url = entry.get("link", "")
                if not url:
                    continue
                articles.append(
                    {
                        "title": entry.get("title", ""),
                        "url": url,
                        "summary": entry.get("summary", ""),
                        "source": feed_title,
                    }
                )
        except Exception:
            logger.exception("Échec de collecte RSS pour %s", feed_url)
    return articles


def collect_all() -> list[dict]:
    articles = collect_from_rss()

    if config.USE_SCRAPLING:
        from scraper import collect_from_scrapling

        articles.extend(collect_from_scrapling())

    if config.USE_STOCKTWITS:
        from stocktwits import collect_from_stocktwits

        articles.extend(collect_from_stocktwits())

    if config.USE_REDDIT:
        from reddit import collect_from_reddit

        articles.extend(collect_from_reddit())

    return articles
