from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from database.db_models import SenderEnum
from services.chat import (
    get_recent_chat_history,
    save_chat_message,
    stream_and_store_response,
    stream_llm_response,
)


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def user_id():
    return uuid4()


def test_stream_llm_response_yields_chunks():
    user_input = "Hello"
    recent_messages = [{"role": "user", "content": "Hi"}]
    fake_chunks = [
        {"message": {"content": "chunk1"}},
        {"message": {"content": "chunk2"}},
    ]
    with patch("services.chat.ollama.chat", return_value=iter(fake_chunks)):
        result = list(stream_llm_response(user_input, recent_messages))
        assert result == ["chunk1", "chunk2"]


def test_save_chat_message_commits(mock_db_session, user_id):
    save_chat_message(mock_db_session, user_id, SenderEnum.user, "test message")
    assert mock_db_session.add.called
    assert mock_db_session.commit.called
    chat_entry = mock_db_session.add.call_args[0][0]
    assert chat_entry.user_id == user_id
    assert chat_entry.sender == SenderEnum.user
    assert chat_entry.message == "test message"


def test_stream_and_store_response_yields_and_saves(mock_db_session, user_id):
    user_input = "Hi"
    fake_chunks = ["part1", "part2"]
    with patch("services.chat.stream_llm_response", return_value=iter(fake_chunks)):
        gen = stream_and_store_response(user_input, user_id, mock_db_session)
        output = list(gen)
        assert output == fake_chunks
        # Should save the concatenated response
        assert mock_db_session.add.called
        chat_entry = mock_db_session.add.call_args[0][0]
        assert chat_entry.sender == SenderEnum.bot
        assert chat_entry.message == "part1part2"


def test_get_recent_chat_history_returns_list(user_id):
    mock_db = MagicMock()
    # Create fake ChatHistory objects
    fake_entries = [
        MagicMock(sender=SenderEnum.user, message="hello", timestamp=None),
        MagicMock(sender=SenderEnum.bot, message="hi there", timestamp=None),
    ]
    # Simulate .query().filter().order_by().limit().all() chain
    mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = (
        fake_entries
    )
    result = get_recent_chat_history(mock_db, user_id)
    assert result == [
        {"role": SenderEnum.bot.value, "content": "hi there"},
        {"role": SenderEnum.user.value, "content": "hello"},
    ]
