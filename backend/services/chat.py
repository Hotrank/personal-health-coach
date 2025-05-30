from datetime import datetime, timedelta
from typing import Generator, Optional
from uuid import UUID

import ollama
from database.db_models import ChatHistory, SenderEnum, UserMemory
from llm.prompts import MEMORY_CONSOLIDATE_PROMPT, MEMORY_SUMMARIZE_PROMPT, SYSTEM_PROMPT, USER_MEMORY_PROMPT
from sqlalchemy.orm import Session

RECENT_CHAT_COUNT = 20


def stream_llm_response(
    user_input: str,
    recent_messages: Optional[list[dict]] = None,
    user_memory: Optional[str] = None,
) -> Generator[str, None, None]:
    """
    Stream the response from the LLM based on user input and recent chat history.
    If recent_messages is provided, it will be included in the context.
    """
    # Prepare the messages for the LLM
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    if user_memory:
        messages.append(
            {
                "role": "system",
                "content": USER_MEMORY_PROMPT.format(user_memory=user_memory),
            }
        )
    if recent_messages:
        messages.extend(recent_messages)
    messages.append({"role": "user", "content": user_input})

    for chunk in ollama.chat(
        model="llama3.2",
        messages=messages,
        stream=True,
    ):
        yield chunk["message"]["content"]


def save_chat_message(
    db: Session,
    user_id: UUID,
    sender: SenderEnum,
    message: str,
    enable_memory_update: bool = True,
):
    """
    Save a chat message to the database and optionally update the user's memory.
    If enable_memory_update is True, it will check if the memory should be updated
    based on the number of messages and update it accordingly.
    """
    chat_entry = ChatHistory(user_id=user_id, sender=sender, message=message)
    db.add(chat_entry)
    db.commit()

    if enable_memory_update and should_update_memory(db, user_id):
        update_user_memory(db, user_id)


def stream_and_store_response(
    user_input: str,
    user_id: UUID,
    db: Session,
    recent_messages: Optional[list[dict]] = None,
    user_memory: Optional[str] = None,
) -> Generator[str, None, None]:
    """
    Stream the LLM response and save the full bot message to the database.
    This function will yield chunks of the response as they are generated,
    and save the complete response to the chat history once streaming is done.
    """
    buffer = ""
    for chunk in stream_llm_response(user_input, recent_messages, user_memory):
        buffer += chunk
        yield chunk

    # Save full bot message to DB
    save_chat_message(db, user_id, SenderEnum.bot, buffer)


def get_recent_chat_history(db: Session, user_id: UUID, count: int = RECENT_CHAT_COUNT) -> list[dict]:
    """
    Retrieve up to 20 most recent chat messages within the last 24 hours for a user,
    and return them as a list of dicts with 'role' and 'content' keys.
    """
    twenty_four_hours_ago = datetime.now() - timedelta(days=1)
    chat_entries = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.user_id == user_id,
            ChatHistory.timestamp >= twenty_four_hours_ago,
        )
        .order_by(ChatHistory.timestamp.desc())
        .limit(count)
        .all()
    )
    return [{"role": entry.sender.value, "content": entry.message} for entry in reversed(chat_entries)]


def should_update_memory(
    db: Session,
    user_id: UUID,
) -> bool:
    """
    Check if the user's memory should be updated by counting the number of messages, if
    the total number if messages is multiple of 20, then return True
    """
    message_count = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).count()
    return message_count % RECENT_CHAT_COUNT == 0


def update_user_memory(db: Session, user_id: UUID):
    """
    Update or insert the user's memory by summarizing recent messages and upserting
    the result into the user_memory table.
    """
    recent_messages = get_recent_chat_history(db, user_id, count=RECENT_CHAT_COUNT)

    if not recent_messages:
        return

    new_messages = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])

    new_memory = summarize_messages(new_messages)
    if not new_memory:
        return

    existing_memory_entry = db.query(UserMemory).filter(UserMemory.user_id == user_id).first()

    if existing_memory_entry:
        existing_memory_entry.memory = consolidate_user_memory(existing_memory_entry.memory, new_memory)
    else:
        existing_memory_entry = UserMemory(user_id=user_id, memory=new_memory)
        db.add(existing_memory_entry)

    db.commit()


def summarize_messages(messages: str) -> str:
    """
    Use the LLM to summarize the provided messages into succinct bullet points.
    """

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": MEMORY_SUMMARIZE_PROMPT.format(messages=messages),
            }
        ],
        stream=False,
    )

    return response["message"]["content"].strip()


def get_user_memory(db: Session, user_id: UUID) -> Optional[str]:
    """
    Retrieve the user's memory from the user_memory table.
    Returns None if no memory exists.
    """

    memory_entry = db.query(UserMemory).filter(UserMemory.user_id == user_id).first()
    return memory_entry.memory if memory_entry else None


def consolidate_user_memory(existing_memory: Optional[str], new_memory: str):
    """
    Consolidate the user's memory by comparing new memory with existing memory,
    use llm to determine whether to update the existing memory. If so, output the
    new memory, if not, return empty string.
    """

    if not existing_memory:
        return new_memory  # If no existing memory, return the new memory directly

    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": MEMORY_CONSOLIDATE_PROMPT.format(
            existing_memory=existing_memory, new_memory=new_memory
        )}],
        stream=False,
    )

    return response["message"]["content"].strip()
