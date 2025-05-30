from typing import Generator
from uuid import UUID

import ollama
from database.db_models import ChatHistory, SenderEnum
from llm.prompts import SYSTEM_PROMPT, USER_MEMORY
from sqlalchemy.orm import Session


def stream_chat_response(user_input: str) -> Generator[str, None, None]:

    for chunk in ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": USER_MEMORY},
            {"role": "user", "content": user_input}],
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
) -> Generator[str, None, None]:
    buffer = ""
    for chunk in stream_chat_response(user_input):
        buffer += chunk
        yield chunk

    # Save full bot message to DB
    save_chat_message(db, user_id, SenderEnum.bot, buffer)