import pytest
from fastapi.testclient import TestClient
from types import SimpleNamespace

from ameck_copilot.app.main import create_app


class DummyService:
    def __init__(self):
        self.settings = SimpleNamespace(model_name='dummy-model')

    async def chat(self, message, conversation_history=None, temperature=None, max_tokens=None, model=None):
        return f"CHAT:{message}"

    async def plan(self, message, conversation_history=None, temperature=None, max_tokens=None, model=None):
        return f"PLAN:{message}"

    async def edit(self, message, conversation_history=None, temperature=None, max_tokens=None, model=None):
        return f"EDIT:{message}"

    async def agent(self, message, conversation_history=None, temperature=None, max_tokens=None, model=None):
        return f"AGENT:{message}"

    async def chat_stream(self, message, conversation_history=None, temperature=None, max_tokens=None, model=None):
        async def gen():
            yield "hello"
            yield " world"
        return gen()


@pytest.fixture()
def client(monkeypatch):
    app = create_app()
    # Monkeypatch get_groq_service used by the routes to return dummy
    import ameck_copilot.app.routes.chat as chat_routes
    monkeypatch.setattr(chat_routes, 'get_groq_service', lambda: DummyService())
    return TestClient(app)


def test_plan_mode_non_stream(client):
    resp = client.post('/api/chat/', json={'message': 'Make a plan', 'stream': False, 'mode': 'plan'})
    assert resp.status_code == 200
    assert resp.json()['message'].startswith('PLAN:')


def test_edit_mode_non_stream(client):
    resp = client.post('/api/chat/', json={'message': 'Edit this', 'stream': False, 'mode': 'edit'})
    assert resp.status_code == 200
    assert resp.json()['message'].startswith('EDIT:')


def test_agent_mode_non_stream(client):
    resp = client.post('/api/chat/', json={'message': 'Act as agent', 'stream': False, 'mode': 'agent'})
    assert resp.status_code == 200
    assert resp.json()['message'].startswith('AGENT:')


def test_default_ask_mode(client):
    resp = client.post('/api/chat/', json={'message': 'Hello', 'stream': False})
    assert resp.status_code == 200
    assert resp.json()['message'].startswith('CHAT:')
