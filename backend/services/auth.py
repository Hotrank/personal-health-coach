import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests
from google.oauth2 import id_token

# TODO(SCRUM-24): load env file based on the environment
load_dotenv(Path(__file__).resolve().parents[2] / "dev.env")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


def verify_google_token(token: str) -> dict:
    if not token:
        raise ValueError("Missing token")
    try:
        result = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
    except GoogleAuthError as e:
        raise ValueError("Invalid token") from e

    return result
