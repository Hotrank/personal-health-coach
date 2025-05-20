# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import ollama

app = FastAPI()

# Allow React to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend is up!"}

@app.post("/chat")
async def chat(message: dict):
    user_input = message.get("text", "")

    def stream_response():
        for chunk in ollama.chat(
            model="llama3.2",  # or your preferred model
            messages=[{"role": "user", "content": user_input}],
            stream=True,
        ):
            yield chunk["message"]["content"]

    return StreamingResponse(stream_response(), media_type="text/plain")
