from ameck_copilot.app.models import ChatRequest, Mode


def test_default_mode_is_ask():
    req = ChatRequest(message="Hello")
    assert req.mode == Mode.ASK


def test_mode_parsing_from_string():
    req = ChatRequest(message="Plan a project", mode="plan")
    assert req.mode == Mode.PLAN


def test_mode_allowed_values():
    for m in ["ask", "agent", "edit", "plan"]:
        req = ChatRequest(message="Test", mode=m)
        assert req.mode.value == m
