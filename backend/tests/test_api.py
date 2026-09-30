from uuid import UUID


def test_health_and_database_initialization(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.post("/api/conversations").status_code == 201


def test_create_and_retrieve_conversation(client):
    created = client.post("/api/conversations")
    assert created.status_code == 201
    conversation = created.json()
    assert UUID(conversation["id"])
    assert client.get(f"/api/conversations/{conversation['id']}").json()["id"] == conversation["id"]
    assert len(client.get("/api/conversations").json()) == 1


def test_chat_flow_persists_user_and_assistant_messages(client):
    conversation_id = client.post("/api/conversations").json()["id"]
    result = client.post(f"/api/conversations/{conversation_id}/messages", json={"content": "Hello"})
    assert result.status_code == 201
    turn = result.json()
    assert turn["user_message"]["role"] == "user"
    assert turn["assistant_message"]["role"] == "assistant"
    assert turn["assistant_message"]["content"] == "I hear you: Hello"
    history = client.get(f"/api/conversations/{conversation_id}/messages").json()
    assert [message["role"] for message in history] == ["user", "assistant"]


def test_missing_conversation_and_invalid_message(client):
    assert client.get("/api/conversations/00000000-0000-0000-0000-000000000000").status_code == 404
    conversation_id = client.post("/api/conversations").json()["id"]
    assert client.post(f"/api/conversations/{conversation_id}/messages", json={"content": ""}).status_code == 422
