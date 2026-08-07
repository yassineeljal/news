"""Collecte via navigateur headless (Scrapling) pour les sites protégés.

N'est importé que si USE_SCRAPLING=true dans .env — nécessite un vrai VPS
(pas un environnement serverless) et `scrapling install` pour les navigateurs.
"""

import logging
from urllib.parse import urljoin

import config

logger = logging.getLogger(__name__)


def collect_from_scrapling() -> list[dict]:
    from scrapling.fetchers import StealthyFetcher

    articles = []
    for source in config.SCRAPLING_SOURCES:
        try:
            page = StealthyFetcher.fetch(source["url"], headless=True)
            seen_urls = set()
            for link in page.css(source["link_selector"]):
                href = link.attrib.get("href")
                if not href:
                    continue
                if href.startswith("/"):
                    href = urljoin(source["url"], href)
                title = link.get_all_text().strip()
                if not title or href in seen_urls:
                    continue
                seen_urls.add(href)
                articles.append(
                    {
                        "title": title,
                        "url": href,
                        "summary": "",
                        "source": source["url"],
                    }
                )
        except Exception:
            logger.exception("Échec du scraping Scrapling pour %s", source["url"])
    return articles
