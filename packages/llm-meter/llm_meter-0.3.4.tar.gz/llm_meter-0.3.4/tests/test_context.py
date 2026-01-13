from llm_meter.context import (
    AttributionContext,
    clear_context,
    get_current_context,
    set_current_context,
    update_current_context,
)


def test_context_default_values():
    ctx = get_current_context()
    assert ctx.request_id is not None
    assert ctx.endpoint is None
    assert ctx.user_id is None


def test_context_set_and_get():
    new_ctx = AttributionContext(user_id="user-123", endpoint="/test")
    token = set_current_context(new_ctx)

    current = get_current_context()
    assert current.user_id == "user-123"
    assert current.endpoint == "/test"

    clear_context(token)
    assert get_current_context().user_id is None


def test_context_update():
    update_current_context(user_id="alice", feature="chat")
    ctx = get_current_context()
    assert ctx.user_id == "alice"
    assert ctx.feature == "chat"

    # Nested update
    update_current_context(feature="summarize")
    ctx2 = get_current_context()
    assert ctx2.user_id == "alice"
    assert ctx2.feature == "summarize"


def test_to_dict():
    ctx = AttributionContext(user_id="bob", metadata={"key": "value"})
    d = ctx.to_dict()
    assert d["user_id"] == "bob"
    assert d["metadata"]["key"] == "value"
