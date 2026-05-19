from __future__ import annotations

import re
from collections import Counter
from statistics import median
from typing import Any


STOPWORDS = {
    "and",
    "the",
    "for",
    "with",
    "that",
    "this",
    "from",
    "https",
    "который",
    "которые",
    "чтобы",
    "теперь",
    "просто",
    "можно",
    "через",
    "только",
    "когда",
}


def engagement_score(views: int = 0, forwards: int = 0, replies: int = 0, reactions: int = 0) -> int:
    return int(forwards or 0) * 5 + int(replies or 0) * 2 + int(reactions or 0)


def enrich_post(row: dict[str, Any]) -> dict[str, Any]:
    views = int(row.get("views") or 0)
    forwards = int(row.get("forwards") or 0)
    replies = int(row.get("replies") or 0)
    reactions = int(row.get("reactions") or 0)
    score = engagement_score(views, forwards, replies, reactions)
    return {
        **row,
        "engagement_score": score,
        "forward_rate": forwards / views if views else 0,
        "reaction_rate": reactions / views if views else 0,
        "comment_rate": replies / views if views else 0,
    }


def rank_posts(posts: list[dict[str, Any]], *, by: str, limit: int) -> list[dict[str, Any]]:
    enriched = [enrich_post(post) for post in posts]
    key = "engagement_score" if by == "engagement" else by
    return sorted(enriched, key=lambda row: row.get(key) or 0, reverse=True)[:limit]


def find_outliers(posts: list[dict[str, Any]], *, limit: int = 20) -> list[dict[str, Any]]:
    enriched = [enrich_post(post) for post in posts]
    scores = [post["engagement_score"] for post in enriched]
    if not scores:
        return []
    baseline = median(scores) or 1
    for post in enriched:
        post["outlier_ratio"] = round(post["engagement_score"] / baseline, 3)
    return sorted(enriched, key=lambda row: row["outlier_ratio"], reverse=True)[:limit]


def mine_terms(texts: list[str], *, limit: int = 30) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for text in texts:
        for word in re.findall(r"[\wА-Яа-яЁё-]{4,}", text.lower()):
            if word not in STOPWORDS and not word.startswith("http"):
                counter[word] += 1
    return [{"term": term, "count": count} for term, count in counter.most_common(limit)]


def generate_ideas(posts: list[dict[str, Any]], comments: list[dict[str, Any]], *, count: int) -> list[dict]:
    top_terms = mine_terms([post.get("text") or "" for post in rank_posts(posts, by="engagement", limit=50)])
    comment_questions = [
        c
        for c in comments
        if "?" in (c.get("text") or "") or any(w in (c.get("text") or "").lower() for w in ["как", "why", "what"])
    ]
    ideas: list[dict[str, Any]] = []
    for term in top_terms[: max(3, count)]:
        ideas.append(
            {
                "title": f"Разобрать тему: {term['term']}",
                "rationale": "Term appears repeatedly in historically strong posts.",
                "evidence": {"term_count": term["count"]},
            }
        )
    for comment in comment_questions[:count]:
        ideas.append(
            {
                "title": "Ответить на вопрос аудитории",
                "rationale": "Audience question found in comments.",
                "evidence": {
                    "post_id": comment.get("post_id"),
                    "comment_id": comment.get("id"),
                    "text": (comment.get("text") or "")[:240],
                },
            }
        )
    return ideas[:count]

