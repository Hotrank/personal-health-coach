from unittest.mock import patch

from services.chat import stream_llm_response


def test_stream_chat_response():
    # Mock data to be returned by ollama.chat
    mock_chunks = [
        {"message": {"content": "Hello"}},
        {"message": {"content": "World"}},
    ]

    with patch("services.chat.ollama.chat", return_value=iter(mock_chunks)):
        result = list(stream_llm_response("Hi"))
        assert result == ["Hello", "World"]