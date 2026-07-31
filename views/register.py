import flet as ft
import logging

from model.firestore_auth import create_user_doc, sign_up
from views.login import header_bar, labeled_field
from model.json.create_account_json import NewAccountStore
from model.firestore_auth import create_user_doc, sign_up, SignUpError

logger = logging.getLogger(f"pawplan.{__name__}")


# REGISTER SCREEN ("/register")
def register_view(page: ft.Page) -> ft.View:
    error_text = ft.Text("", color=ft.Colors.RED_600, size=13, visible=False)


    # form state
    selected_gender = {"value": None}

    username_col = labeled_field("Username", horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    email_col = labeled_field("Email", horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    password_col = labeled_field("Password", password=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def make_gender_btn(label: str):
        def on_click(e):
            selected_gender["value"] = label
            male_btn.bgcolor = ft.Colors.BLUE_700 if label == "Male" else ft.Colors.BLUE_400
            female_btn.bgcolor = ft.Colors.PINK_700 if label == "Female" else ft.Colors.PINK_400
            page.update()

        return on_click

    male_btn = ft.Button(
        content="Male",
        width=110,
        height=48,
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.BLUE_400,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=30),
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.W_600),
        ),
    )
    female_btn = ft.Button(
        content="Female",
        width=110,
        height=48,
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.PINK_400,  # was PINK_600
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=30),
            text_style=ft.TextStyle(size=16, weight=ft.FontWeight.W_600),
        ),
    )
    male_btn.on_click = make_gender_btn("Male")
    female_btn.on_click = make_gender_btn("Female")

    gender_row = ft.Row(
        [
            ft.Text("Gender:", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            ft.Container(width=15),
            male_btn,
            ft.Container(width=12),
            female_btn,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=0,
    )

    def dob_field(label: str, width: int) -> ft.TextField:
        return ft.TextField(
            label=label,
            width=width,
            height=55,
            text_align=ft.TextAlign.CENTER,
            color=ft.Colors.BLACK,
            border_radius=30,
            border_color=ft.Colors.BLACK,
            border_width=2,
            bgcolor=ft.Colors.WHITE,
            content_padding=ft.Padding.symmetric(horizontal=8, vertical=10),
        )

    mm = dob_field("MM", 85)
    dd = dob_field("DD", 85)
    yyyy = dob_field("YYYY", 110)


    dob_row = ft.Row(
        [
            ft.Text("Date of Birth:\n", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            ft.Container(width=12),
            mm,
            ft.Container(width=10),
            dd,
            ft.Container(width=10),
            yyyy,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=0,
        wrap=True,
        run_spacing=12,
    )

    # validation
    async def do_register(e):
        missing = not all([username_col.field.value, email_col.field.value, password_col.field.value])
        if missing:
            error_text.value = "Please fill in all required fields."
            error_text.visible = True
            page.update()
            return
        error_text.visible = False

        # LOGIC
        # 1) create the Firebase Auth account (email/password)
        # 1) create the Firebase Auth account (email/password)
        try:
            local_id = sign_up(email_col.field.value, password_col.field.value)
        except SignUpError as err:
            messages = {
                "EMAIL_EXISTS": "That email is already registered.",
                "WEAK_PASSWORD": "Password should be at least 6 characters.",
                "INVALID_EMAIL": "That email address looks invalid.",
            }
            error_text.value = messages.get(err.code, "Registration failed. Please try again.")
            error_text.visible = True
            page.update()
            return

        # 2) save data to json
        dob = f"{mm.value}-{dd.value}-{yyyy.value}"

        try:
            create_account = NewAccountStore()
            create_account.set(
                username=username_col.field.value,
                email=email_col.field.value,
                gender=selected_gender["value"],
                date_of_birth=dob
            )
            create_user_doc()  # db access
            create_account.clear() # delete create account json afterwards
        except Exception as e:
            logger.exception("Error during registration process.")
            error_text.value = "Registration failed. Please try again."
            error_text.visible = True
            page.update()
            return

        await page.push_route("/homepage")

    create_btn = ft.Button(
        "Create Account",
        width=260,
        height=60,
        on_click=do_register,
        color=ft.Colors.WHITE,
        bgcolor=ft.Colors.GREEN_500,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=30),
            side={ft.ControlState.DEFAULT: ft.BorderSide(2, "#000000")},
            text_style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD),
        ),
    )

    bottom_bars = ft.Column(
        [
            ft.Container(height=25, bgcolor=ft.Colors.BLUE_900, expand=True),
            ft.Container(height=25, bgcolor=ft.Colors.ORANGE, expand=True),
        ],
        spacing=0,
    )

    body = ft.Container(
        padding=ft.Padding.symmetric(horizontal=35, vertical=30),
        content=ft.Column(
            [
                username_col.views,
                ft.Container(
                    height=22
                ),
                email_col.views,
                ft.Container(
                    height=22
                ),
                gender_row,
                ft.Container(
                    height=22
                ),
                dob_row,
                ft.Container(
                    height=22
                ),
                password_col.views,
                error_text,
                ft.Container(
                    height=30
                ),
                ft.Row([
                    create_btn
                ],
                alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


    # call content
    return ft.View(
        bgcolor=ft.Colors.WHITE,
        route="/register",
        controls=[
            ft.Column(
                [
                    header_bar(page, "Register"),
                    body,
                    ft.Container(
                        expand = True
                    ),
                    bottom_bars,

                ],
                spacing = 0,
                expand = True,
                scroll = ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            )
        ],
        vertical_alignment = ft.MainAxisAlignment.START,
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
    )