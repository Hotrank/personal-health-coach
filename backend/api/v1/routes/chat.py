from database.connection import get_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from services.auth import verify_google_token
from services.chat import stream_chat_response
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
    id = get_or_create_user(db, google_sub=google_id, name=name, email=email)
    if not id:
        raise HTTPException(status_code=500, detail="Failed to create or retrieve user")
    user_input = message.get("text", "")

    return StreamingResponse(stream_chat_response(user_input), media_type="text/plain")