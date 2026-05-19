from chappe.tdlib import normalize_message


def test_normalize_message_extracts_tdlib_metrics():
    msg = {
        "id": 123,
        "date": 1700000000,
        "content": {"@type": "messageText", "text": {"@type": "formattedText", "text": "hello"}},
        "interaction_info": {
            "view_count": 100,
            "forward_count": 5,
            "reactions": {"reactions": [{"total_count": 7}]},
        },
        "reply_info": {"reply_count": 2},
    }
    post = normalize_message(msg, channel="@x", username="x")
    assert post["text"] == "hello"
    assert post["forwards"] == 5
    assert post["reactions"] == 7
    assert post["link"] == "https://t.me/x/123"

