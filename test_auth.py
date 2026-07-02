from dotenv import load_dotenv
load_dotenv()

import os
import flet as ft
from flet.auth.providers import GoogleOAuthProvider

# get values from .env
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

# error checking
if not client_id or not client_secret:
    raise ValueError("Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in .env file")

def main(page: ft.Page):
    provider = GoogleOAuthProvider(
        client_id=client_id,
        client_secret=client_secret,
        redirect_url="http://localhost:8550/oauth_callback",
    )

    async def login_click(e):
        await page.login(provider)

    def on_login(e: ft.LoginEvent):
        if e.error:
            print("Login error:", e.error)
            return
        print("Logged in as:", page.auth.user["email"])

    page.on_login = on_login
    page.add(ft.Button("Login with Google", on_click=login_click))

ft.run(main, port=8550, view=ft.AppView.WEB_BROWSER)