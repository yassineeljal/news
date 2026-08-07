import config


def matches_keywords(article: dict) -> bool:
    text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
    return any(keyword.lower() in text for keyword in config.WATCHED_KEYWORDS)


def filter_articles(articles: list[dict]) -> list[dict]:
    return [a for a in articles if matches_keywords(a)]
