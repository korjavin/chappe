from chappe.analytics import engagement_score, find_outliers, generate_ideas, rank_posts


def test_engagement_score_weights_forwards_highest():
    assert engagement_score(views=1000, forwards=10, replies=5, reactions=7) == 67


def test_rank_posts_by_forwards():
    posts = [
        {"id": "1", "views": 100, "forwards": 1, "replies": 10, "reactions": 10},
        {"id": "2", "views": 100, "forwards": 7, "replies": 0, "reactions": 0},
    ]
    assert rank_posts(posts, by="forwards", limit=1)[0]["id"] == "2"


def test_outliers_include_ratio():
    posts = [
        {"id": "1", "views": 100, "forwards": 1, "replies": 0, "reactions": 0},
        {"id": "2", "views": 100, "forwards": 100, "replies": 0, "reactions": 0},
    ]
    assert find_outliers(posts, limit=1)[0]["id"] == "2"


def test_generate_ideas_uses_comment_questions():
    ideas = generate_ideas(
        [{"id": "1", "text": "Claude agents and Telegram growth", "forwards": 10}],
        [{"id": "c1", "post_id": "1", "text": "Как это настроить?"}],
        count=5,
    )
    assert any(idea["title"] == "Ответить на вопрос аудитории" for idea in ideas)

