from chappe.store import Store


def test_store_roundtrip_posts_and_drafts(tmp_path):
    store = Store(tmp_path / "chappe.db")
    store.upsert_posts(
        "@x",
        [{"id": "1", "text": "hello", "views": 10, "forwards": 2, "replies": 1, "reactions": 3}],
    )
    assert store.get_post("@x", "1")["text"] == "hello"
    draft = store.create_draft("@x", "AI agents: useful update")
    assert store.get_draft(draft["id"])["channel"] == "@x"

