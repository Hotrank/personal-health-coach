from datetime import datetime, timedelta
from typing import Generator, Optional
from uuid import UUID

import ollama
from database.db_models import ChatHistory, SenderEnum
from llm.prompts import SYSTEM_PROMPT, USER_MEMORY
from sqlalchemy.orm import Session


def stream_llm_response(user_input: str, recent_messages: Optional[list[dict]] = None) -> Generator[str, None, None]:
    """
    Stream the response from the LLM based on user input and recent chat history.
    If recent_messages is provided, it will be included in the context.
    """
    # Prepare the messages for the LLM
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": USER_MEMORY}]
    if recent_messages:
        messages.extend(recent_messages)
    messages.append(
        {"role": "user", "content": user_input})
    
    for chunk in ollama.chat(
        model="llama3.2",
        messages=messages,
        stream=True,
    ):
        yield chunk["message"]["content"]

def save_chat_message(db: Session, user_id: UUID, sender: SenderEnum, message: str):
    chat_entry = ChatHistory(
        user_id=user_id,
        sender=sender,
        message=message
    )
    db.add(chat_entry)
    db.commit()

def stream_and_store_response(
    user_input: str,
    user_id: UUID,
    db: Session,
    recent_messages: Optional[list[dict]] = None
) -> Generator[str, None, None]:
    buffer = ""
    for chunk in stream_llm_response(user_input, recent_messages):
        buffer += chunk
        yield chunk

    # Save full bot message to DB
    save_chat_message(db, user_id, SenderEnum.bot, buffer)

def get_recent_chat_history(db: Session, user_id: UUID) -> list[dict]:
    """
    Retrieve up to 20 most recent chat messages within the last 24 hours for a user,
    and return them as a list of dicts with 'role' and 'content' keys.
    """
    twenty_four_hours_ago = datetime.now() - timedelta(days=1)
    chat_entries = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.user_id == user_id,
            ChatHistory.timestamp >= twenty_four_hours_ago
        )
        .order_by(ChatHistory.timestamp.desc())
        .limit(20)
        .all()
    )
    return [
        {"role": entry.sender.value, "content": entry.message}
        for entry in reversed(chat_entries)
    ]

