from contextlib import asynccontextmanager

from api.v1.routes import auth, chat
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.llm.client_factory import get_llm_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.llm_client = get_llm_client("openai")
    yield
    # No teardown needed for now, but you could add cleanup here

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
