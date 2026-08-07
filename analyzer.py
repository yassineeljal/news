import json
import logging

from groq import Groq

import config

logger = logging.getLogger(__name__)

_client: Groq | None = None

PROMPT_TEMPLATE = """Tu es un analyste financier strict. Analyse cet article et réponds \
UNIQUEMENT en JSON valide avec ces clés :
- "relevant": booléen, true UNIQUEMENT si l'article rapporte un fait concret avec \
impact potentiel réel sur le cours (résultats, guidance, fusion/acquisition, \
procès, décision réglementaire, changement de direction, notation d'analyste...). \
false pour tout le reste, y compris : avis/spéculation sans fait nouveau, discussion \
de niveau de prix ("on va à 350$"), commentaire d'humeur ou de sentiment générique, \
contenu publicitaire ou promotionnel. En cas de doute, réponds false.
- "ticker": le symbole boursier concerné (ou null)
- "sentiment": "positive", "negative" ou "neutral"
- "impact": "high", "medium" ou "low"
- "reason": une phrase courte en français expliquant l'impact

Titre : {title}
Résumé : {summary}
"""


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=config.GROQ_API_KEY)
    return _client


def analyze_article(article: dict) -> dict | None:
    prompt = PROMPT_TEMPLATE.format(
        title=article.get("title", ""), summary=article.get("summary", "")
    )
    try:
        response = _get_client().chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        result = json.loads(response.choices[0].message.content)
    except Exception:
        logger.exception("Échec de l'analyse Groq pour %s", article.get("url"))
        return None

    if not result.get("relevant"):
        return None
    return result
