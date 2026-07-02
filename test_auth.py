from dotenv import load_dotenv
load_dotenv()

import os
import flet as ft
from flet.auth.providers import GoogleOAuthProvider

def main(page: ft.Page):
    provider = GoogleOAuthProvider(
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        redirect_url="http://localhost:8550/oauth_callback",
    )

    def login_click(e):
        page.login(provider)

    def on_login(e: ft.LoginEvent):
        if e.error:
            print("Login error:", e.error)
            return
        print("Logged in as:", page.auth.user["email"])

    page.on_login = on_login
    page.add(ft.ElevatedButton("Login with Google", on_click=login_click))

ft.app(target=main, port=8550, view=ft.AppView.WEB_BROWSER)