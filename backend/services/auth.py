from google.auth.transport import requests
from google.oauth2 import id_token

GOOGLE_CLIENT_ID = "30767248244-t7n4e1o3m224bot124ntltje4ir06vei.apps.googleusercontent.com"

def verify_google_token(token: str) -> dict:
    return id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)