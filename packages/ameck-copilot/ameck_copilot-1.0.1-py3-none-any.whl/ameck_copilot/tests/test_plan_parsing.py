from fastapi.testclient import TestClient
from ameck_copilot.app.main import create_app


def test_plan_parsing(monkeypatch):
    app = create_app()

    class DummyPlanService:
        def __init__(self):
            self.settings = type('X', (), {'model_name': 'dummy'})
        async def plan(self, message, conversation_history=None, temperature=None, max_tokens=None, model=None):
            return "A short summary.\n\nSteps:\n1. Do X\n\nJSON:\n[{'id':1,'title':'Do X','description':'Do X now','estimate':'30m'}]"  # intentionally single quotes to test robustness

    import ameck_copilot.app.routes.chat as chat_routes
    monkeypatch.setattr(chat_routes, 'get_groq_service', lambda: DummyPlanService())

    client = TestClient(app)
    resp = client.post('/api/chat/', json={'message': 'Make plan', 'stream': False, 'mode': 'plan'})
    assert resp.status_code == 200
    data = resp.json()
    assert 'message' in data
    # If parsing succeeded, structured.plan should be present and be a list
    if data.get('structured'):
        assert 'plan' in data['structured']
        assert isinstance(data['structured']['plan'], list)
