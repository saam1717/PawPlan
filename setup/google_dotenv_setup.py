import os
from dotenv import load_dotenv
from flet.auth.providers import GoogleOAuthProvider

load_dotenv()
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

if not client_id or not client_secret:
    raise ValueError("Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in .env file")

IS_WEB = os.environ.get("PORT") is not None
REDIRECT_URL = (
    os.getenv("OAUTH_REDIRECT_URL")
    if IS_WEB
    else "http://localhost:8550/oauth_callback"
)

provider = GoogleOAuthProvider(
    client_id=client_id,
    client_secret=client_secret,
    redirect_url=REDIRECT_URL,
)