import flet as ft
import logging
from dataclasses import dataclass

from model.firestore_auth import create_oauth_user_doc, log_in
from utility.navigation import go_to

logger = logging.getLogger(f"pawplan.{__name__}")



def header_bar(page: ft.Page, title: str) -> ft.Container:
    return ft.Container(
        height = 110,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors = [
                ft.Colors.BLUE_900
            ],
        ),
        padding = ft.Padding.only(left=15, right=15, top=40),
        content = ft.Stack(
            [
                ft.Container(
                    content = ft.Text(title, size = 26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    alignment=ft.Alignment.CENTER,
                ),
                # back button (rendered last so it's on top and receives clicks)
                ft.Container(
                    content = ft.IconButton(
                        icon = ft.Icons.ARROW_BACK,
                        icon_color = ft.Colors.WHITE,
                        icon_size = 24,
                        on_click = go_to(page,"/")
                    ),
                    alignment=ft.Alignment.CENTER_LEFT,
                ),
            ],
        ),
    )


@dataclass
class LabeledField:
    views: ft.Column
    field: ft.TextField


def labeled_field(
        label: str,
        width: int = 320,
        password: bool = False,
        horizontal_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.START,

) -> LabeledField:
    field = ft.TextField(
        width = width,
        height = 55,
        password = password,
        can_reveal_password = password,
        color = ft.Colors.BLACK,
        border_radius = 30,
        border_color = ft.Colors.BLACK,
        border_width = 2,
        bgcolor = ft.Colors.WHITE,
        content_padding = ft.Padding.symmetric(horizontal=20, vertical=10),
    )
    view = ft.Column(
        [
            ft.Text(label, size = 18, weight = ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            ft.Container(
                height = 8,
            ),
            field,

        ],
        spacing = 0,
        horizontal_alignment = horizontal_alignment,
    )
    #handles the textfield for reading .value
    return LabeledField(views = view, field = field)


# LOGIN SCREEN ("/login")
def login_view(page: ft.Page) -> ft.View:
    error_text = ft.Text("", color=ft.Colors.RED_600, size = 13, visible = False)

    selected_gender = {
        "value": None
    }

    #Changed to email because that's how mafia works
    email = labeled_field("Username", horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    password  = labeled_field("Password", password = True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)



    # basic client-side validation - wires up auth check here
    async def do_login(e):

        if not email.field.value or not password.field.value:
            error_text.value = "Please enter username and password."

            error_text.visible = True
            page.update()
            return
        error_text.visible = False

        uid = log_in(email.field.value, password.field.value)

        if(uid is not None):
            # Seed the local uid store (email) so the CRUD layer resolves the
            # right Firestore doc, and ensure the doc exists if the auth
            # account was created without going through registration.
            create_oauth_user_doc(email.field.value)
            await page.push_route("/homepage")
        else:
            error_text.value = "Login failed."
            email.field.value = ""
            password.field.value = ""
            error_text.visible = True


        # # LOGIC
        # logger.debug(f"Attempting login with username: {username.field.value} and password: {password.field.value}")
        # uid_account = UserIdStore()
        # uid_account.set(str(username.field.value))
        #
        # uid = get_uid()
        #
        # # route validation or smthn
        # if(uid is not None):
        #     await page.push_route("/homepage")
        # else:
        #     error_text.value = "Login failed."
        #     username.field.value = ""
        #     password.field.value = ""
        #     error_text.visible = True


    not_registered = ft.TextButton(
        content = ft.Text(
            "Not registered yet?",
            size = 15,
            weight = ft.FontWeight.W_600,
            color = ft.Colors.GREEN_600,
            style = ft.TextStyle(
                decoration = ft.TextDecoration.UNDERLINE,
            ),
        ),
        on_click = go_to(page, "/register"),
        style = ft.ButtonStyle(padding = 0),
    )

    login_btn = ft.Button(
        "Log In",
        width = 260,
        height = 60,
        on_click = do_login,
        color = ft.Colors.WHITE,
        bgcolor = ft.Colors.BLUE_900,
        style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=30),
            side = {
                ft.ControlState.DEFAULT: ft.BorderSide(2, color="#000000"),
            },
            text_style = ft.TextStyle(
                size = 22,
                weight = ft.FontWeight.BOLD
            ),
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
        padding = ft.Padding.symmetric(horizontal=35, vertical=35),
        content = ft.Column(
            [
                email.views,
                ft.Container(
                    height = 25
                ),
                password.views,
                ft.Container(
                    height = 25
                ),
                ft.Row([
                    not_registered
                ],
                    alignment = ft.MainAxisAlignment.CENTER,
                ),
                error_text,
                ft.Container(height = 35),

                ft.Row([login_btn],
                       alignment = ft.MainAxisAlignment.CENTER,
                )
            ],
            spacing = 0,
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        ),
    )



    # call content
    return ft.View(
        bgcolor = ft.Colors.WHITE,
        route="/login",
        controls=[
            ft.Column(
                [
                    header_bar(page, "Login"),
                    body,
                    ft.Container(
                        expand = True,
                    ),
                    bottom_bars,
                ],
                spacing = 0,
                expand = True,
                horizontal_alignment = ft.CrossAxisAlignment.STRETCH,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )