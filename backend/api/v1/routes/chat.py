

from database.connection import get_db
from database.db_models import SenderEnum
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from services.auth import verify_google_token
from services.chat import save_chat_message, stream_and_store_response
from services.user import get_or_create_user

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
