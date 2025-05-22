import ollama
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from google.auth.transport import requests
from google.oauth2 import id_token
from pydantic import BaseModel

GOOGLE_CLIENT_ID = (
    "30767248244-t7n4e1o3m224bot124ntltje4ir06vei.apps.googleusercontent.com"
)

app = FastAPI()

# Allow React frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TokenData(BaseModel):
    token: str


@app.get("/")
def read_root():
    return {"message": "Backend is up!"}


@app.post("/verify-token")
async def verify_token(token_data: TokenData):
    try:
        # Verify the token with Google's OAuth2 API
        idinfo = id_token.verify_oauth2_token(
            token_data.token, requests.Request(), GOOGLE_CLIENT_ID
        )

        # idinfo contains user's Google account info
        userid = idinfo["sub"]
        email = idinfo.get("email")
        name = idinfo.get("name")

        # You can create a session or store user info here as needed
        return {"user_id": userid, "email": email, "name": name}

    except ValueError:
        # Invalid token
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/logout")
async def logout():
    # Since no session is stored, just acknowledge logout.
    return JSONResponse(
        content={"message": "User logged out (frontend should discard token)."},
        status_code=200,
    )


@app.post("/chat")
async def chat(message: dict):
    # Check if the request contains a valid token
    token = message.get("token", "")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), GOOGLE_CLIENT_ID
        )
        print("Authenticated user:", idinfo.get("email"))
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_input = message.get("text", "")

    id = message.get("userId", "")
    if idinfo.get("sub") != id:
        raise HTTPException(status_code=401, detail="Invalid user ID")


    def stream_response():
        for chunk in ollama.chat(
            model="llama3.2",  # or your preferred model
            messages=[{"role": "user", "content": user_input}],
            stream=True,
        ):
            yield chunk["message"]["content"]

    return StreamingResponse(stream_response(), media_type="text/plain")
