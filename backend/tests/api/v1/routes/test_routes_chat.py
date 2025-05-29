from unittest.mock import patch

import pytest

# Import the router from the chat module
from api.v1.routes.chat import router
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

app = FastAPI()
app.include_router(router)

@pytest.fixture
def client():
    return TestClient(app)

def test_chat_missing_token(client):
    response = client.post("/chat", json={"text": "hello", "userId": "123"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Missing token"

@patch("api.v1.routes.chat.verify_google_token")
def test_chat_invalid_token(mock_verify, client):
    mock_verify.side_effect = ValueError("Invalid token")
    response = client.post("/chat", json={"text": "hello", "userId": "123", "token": "badtoken"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Invalid token"

@patch("api.v1.routes.chat.verify_google_token")
@patch("api.v1.routes.chat.stream_chat_response")
def test_chat_success(mock_stream, mock_verify, client):
    mock_verify.return_value = {"sub": "123", "name": "unit test", "email": "unit-test@email.com"}
    mock_stream.return_value = iter(["response1", "response2"])
    response = client.post("/chat", json={"text": "hello", "userId": "123", "token": "goodtoken"})
    assert response.status_code == 200
    # StreamingResponse returns a generator, so we need to read the content
    assert b"response1" in response.content
    assert b"response2" in response.content