from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services.auth import verify_google_token
from services.chat import stream_chat_response

router = APIRouter()

@router.post("/chat")
async def chat(message: dict) -> StreamingResponse:
    token = message.get("token", "")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        idinfo = verify_google_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_input = message.get("text", "")
    id = message.get("userId", "")
    if idinfo.get("sub") != id:
        raise HTTPException(status_code=401, detail="Invalid user ID")
    return StreamingResponse(stream_chat_response(user_input), media_type="text/plain")