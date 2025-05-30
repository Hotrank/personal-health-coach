from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models.token import TokenData
from services.auth import verify_google_token

router = APIRouter()


@router.post("/verify-token")
async def verify_token(token_data: TokenData) -> dict:
    try:
        idinfo = verify_google_token(token_data.token)
        return {
            "user_id": idinfo["sub"],
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/logout")
async def logout() -> JSONResponse:
    return JSONResponse(
        content={"message": "User logged out (frontend should discard token)."},
        status_code=200,
    )
