import argparse
import logging
import time

import analyzer
import collector
import config
import db
import keyword_filter
import notifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("stockbot")


def run_once() -> None:
    articles = collector.collect_all()
    logger.info("%d articles collectés", len(articles))

    new_articles = [a for a in articles if a.get("url") and not db.is_seen(a["url"])]
    logger.info("%d articles nouveaux", len(new_articles))

    candidates = keyword_filter.filter_articles(new_articles)
    candidate_urls = {a["url"] for a in candidates}
    logger.info("%d articles retenus après pré-filtre mots-clés", len(candidates))

    for article in new_articles:
        if article["url"] in candidate_urls:
            analysis = analyzer.analyze_article(article)
            if analysis:
                logger.info(
                    "Alerte : %s (%s)", article["title"], analysis.get("ticker")
                )
                notifier.send_alert(article, analysis)
        db.mark_seen(article["url"])


def run_loop() -> None:
    interval_seconds = config.LOOP_INTERVAL_MINUTES * 60
    while True:
        try:
            run_once()
        except Exception:
            logger.exception("Erreur pendant le cycle du bot")
        time.sleep(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bot d'alertes boursières")
    parser.add_argument(
        "--once", action="store_true", help="Exécute un seul cycle puis quitte"
    )
    args = parser.parse_args()

    db.init_db()

    if args.once:
        run_once()
    else:
        run_loop()


if __name__ == "__main__":
    main()
