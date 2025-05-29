from typing import Generator
from uuid import UUID

from database.connection import get_db
from database.db_models import ChatHistory, SenderEnum
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from services.auth import verify_google_token
from services.chat import stream_chat_response
from services.user import get_or_create_user
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/chat")
async def chat(message: dict, db=Depends(get_db)) -> StreamingResponse:
    token = message.get("token", "")

    try:
        idinfo = verify_google_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    google_id, name, email = idinfo.get("sub", ""), idinfo.get("name", ""), idinfo.get("email", "")
    user_id = get_or_create_user(db, google_sub=google_id, name=name, email=email)
    if not user_id:
        raise HTTPException(status_code=500, detail="Failed to create or retrieve user")
    user_input = message.get("text", "")
    # Save user input to chat_history table
    save_chat_message(db, user_id, SenderEnum.user, user_input)

    return StreamingResponse(
        stream_and_store_response(user_input, user_id, db),
        media_type="text/event-stream"
    )

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
