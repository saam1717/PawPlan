import flet as ft
import logging
import threading

from model.firestore_auth import seed_uid_from_auth, create_oauth_user_doc
from utility.navigation import go_to
from setup.google_dotenv_setup import provider

logger = logging.getLogger(f"pawplan.{__name__}")
# === COPILOT NOTE ===
# Changed by Copilot: During login the local uid is set immediately so
# other views can read it. Creating the Firestore user document
# (create_oauth_user_doc) can take time, so that call now runs in a
# daemon background thread so navigation (page.push_route) is not blocked.
# === END NOTE ===

def make_on_login(page: ft.Page): # called on main
    async def on_login(e: ft.LoginEvent):
        if e.error:
            logger.error("Login error: %s", e.error)
            return
        # debugging
        if(page.auth != None):
            email = str(page.auth.user["email"])
            logger.info("Logged in as: %s", email)
            # set local uid immediately so other views can read it
            seed_uid_from_auth(page.auth)

            # create firestore user document in background to avoid blocking navigation
            def _create_doc():
                try:
                    create_oauth_user_doc(email)
                except Exception as ex:
                    logger.exception("Failed to create oauth user doc: %s", ex)

            threading.Thread(target=_create_doc, daemon=True).start()

            await page.push_route("/homepage")

    return on_login


# STARTUP PAGE ("/")
def startup_view(page: ft.Page) -> ft.View:
    # Re-seed the local uid store from a restored auth session so model CRUD
    # calls resolve the right Firestore doc even though main.py clears the
    # uid file on startup (e.g. after a page refresh or navigating back here
    # while still signed in).
    seed_uid_from_auth(page.auth)

    async def login_click(e):
        await page.login(provider)


    # ---------- Logo: paw icon in a cyan rounded square + "PawPlan" wordmark ----------

    paw_icon = ft.Image(
        src="pawplan_icon.png",
        height=130,
        width=130,
        fit=ft.BoxFit.CONTAIN,
    )


    wordmark = ft.Row(
        [
            ft.Text("Paw", size=38, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE),
            ft.Text("Plan", size=38, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
        ],
        spacing=0,
    )
    wordmark = ft.Container(
        content = wordmark,
        padding = ft.Padding.only(right = 40),
    )

    logo_row = ft.Row(
        [paw_icon, wordmark],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=1,
    )

    # ---------- Login / Sign Up buttons ----------
    login_btn = ft.Button(
        "Login",
        width=140,
        height=55,
        on_click=go_to(page, "/login"),
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.BLUE_900,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            side = {ft.ControlState.DEFAULT: ft.BorderSide(2, "#000000")},
            text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
        ),
    )
    signup_btn = ft.Button(
        "Sign Up",
        width=140,
        height=55,
        on_click=go_to(page, "/register"),
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.GREEN_500,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            side = {ft.ControlState.DEFAULT: ft.BorderSide(2, "#000000")},
            text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
        ),

    )
    button_row = ft.Row([login_btn, signup_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    # ---------- "Or Continue with" divider ----------
    divider = ft.Row(
        [
            ft.Container(content=ft.Divider(thickness=1), expand=True),
            ft.Text("Or Continue with", size=14, color=ft.Colors.GREY_600),
            ft.Container(content=ft.Divider(thickness=1), expand=True),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------- Google sign-in button ----------
    # Logo is bundled locally (assets/google_g_logo.png) instead of hotlinking
    # wikimedia so the button looks the same offline / without external network.
    google_logo = ft.Container(
        height = 20,
        width = 20,
        content = ft.Image(
            src="google_g_logo.png",
            height = 18,
            width = 18,
            fit = ft.BoxFit.CONTAIN,
        ),
    )

    google_btn = ft.OutlinedButton(
        content=ft.Stack(
            [
                ft.Container(
                    content= google_logo,
                    alignment=ft.Alignment.CENTER_LEFT,
                    padding=ft.Padding.only(left=15),
                ),
                ft.Container(
                    content=ft.Text("Sign in with Google", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                    alignment = ft.Alignment.CENTER,
                    padding = ft.Padding.only(left = 25),
                ),
            ],
            width = 280,
            height = 55,
        ),
        width=280,
        height=55,
        on_click=login_click, # get provider
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            side={ft.ControlState.DEFAULT: ft.BorderSide(1, "#000000")},
            bgcolor=ft.Colors.WHITE,
        ),
    )

    # ---------- Bottom accent bars (blue over orange) ----------
    bottom_bars = ft.Column(
        [
            ft.Container(height=25, bgcolor=ft.Colors.BLUE_900, expand=True),
            ft.Container(height=25, bgcolor=ft.Colors.ORANGE, expand=True),
        ],
        spacing=0,
    )

    # call content
    return ft.View(
        route="/",
        bgcolor=ft.Colors.WHITE,
        padding=0,
        controls=[
            ft.Column(
                [
                    ft.Container(height=80),
                    logo_row,
                    ft.Container(height=40),
                    button_row,
                    ft.Container(height=30),
                    ft.Container(content=divider, width=340),
                    ft.Container(height=30),
                    google_btn,
                    ft.Container(expand=True),  # pushes the bottom bars down
                    bottom_bars,
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                spacing=0,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )