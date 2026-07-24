import flet as ft
import logging
from firebase_admin import firestore

from model.uid_json import UserIdStore
from model.firebase_setup import db

logger = logging.getLogger(__name__)

# firestore setup


primary = "#0D6EFD"
header_blue = "#1450B4"
orange = "#F5821F"
soft_border = "#DDE3EE"
white = "#FFFFFF"
black = "#000000"


def labeled_input(label: str, field: ft.Control) -> ft.Column:
    """Wraps a field with a label above it, styled like the rest of the app's forms."""
    return ft.Column(
        spacing=6,
        controls=[
            ft.Text(label, size=13, weight=ft.FontWeight.W_600, color="#6B7280"),
            field,
        ],
    )


def petprofile_input_view(page: ft.Page) -> ft.View:
    async def go_homepage(e):
        logger.info("Go to pet profile clicked")
        try:
            await page.push_route("/homepage")
            logger.info("Route pushed")
        except Exception as e:
            logger.error(f"Error occurred: {e}")

    # back nav
    async def go_back(e):
        logger.info("Back from pet profile clicked")
        try:
            await page.push_route("/homepage")
            logger.debug(f"Homepage route pushed")
        except Exception as e:
            logger.error(f"Error occurred: {e}")

    # ---------- App bar (matches header_blue style used on Homepage/Settings) ----------
    appbar = ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=16),
        bgcolor=header_blue,
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=white,
                    on_click=go_back,
                ),
                ft.Text(
                    "Add Pet",
                    color=white,
                    size=22,
                    weight=ft.FontWeight.W_800,
                ),
            ],
        ),
    )

    # ---------- Form field styling ----------
    field_border_radius = 12
    field_content_padding = ft.Padding.symmetric(horizontal=16, vertical=14)

    pet_name = ft.TextField(
        hint_text="e.g. Bella",
        width=340,
        border_radius=field_border_radius,
        border_color=soft_border,
        bgcolor=white,
        color=black,
        content_padding=field_content_padding,
    )
    pet_type = ft.Dropdown(
        hint_text="Select type",
        width=340,
        border_radius=field_border_radius,
        border_color=soft_border,
        bgcolor=white,
        color=black,
        content_padding=field_content_padding,
        options=[
            ft.dropdown.Option(
                key="Dog",
                content=ft.Text("Dog", color=black),
            ),
            ft.dropdown.Option(
                key="Cat",
                content=ft.Text("Cat", color=black),
            ),
        ],
    )

    pet_age = ft.TextField(
        hint_text="e.g. 3",
        width=340,
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.START,
        border_radius=field_border_radius,
        border_color=soft_border,
        bgcolor=white,
        color=black,
        content_padding=field_content_padding,
    )
    pet_breed = ft.TextField(
        hint_text="e.g. Chihuahua, Husky",
        width=340,
        text_align=ft.TextAlign.START,
        border_radius=field_border_radius,
        border_color=soft_border,
        bgcolor=white,
        color=black,
        content_padding=field_content_padding,
    )
    pet_allergies = ft.TextField(
        hint_text="e.g. Chicken, Pork",
        width=340,
        text_align=ft.TextAlign.START,
        border_radius=field_border_radius,
        border_color=soft_border,
        bgcolor=white,
        color=black,
        content_padding=field_content_padding,
    )

    error_text = ft.Text("", color=ft.Colors.RED_600, size=13, visible=False)

    # ---------- Avatar placeholder (visual anchor at the top of the form) ----------
    avatar_placeholder = ft.Container(
        width=90,
        height=90,
        bgcolor="#F1D9B0",
        border_radius=45,
        border=ft.Border.all(2, soft_border),
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.PETS, size=44, color="#8A6A3B"),
    )

    # firestore code
    current_user_id = None
    if (page.auth is not None):
        current_user_id = page.auth.user["email"]
    else:
        user_session = UserIdStore()
        current_user_id = user_session.get()

    pets_ref = db.collection("users").document(current_user_id).collection("details").document("pets")

    # normla functions can't call asynch functions
    async def add_pet(e):
        if not pet_name.value or not pet_type.value:
            error_text.value = "Please enter a name and select a pet type."
            error_text.visible = True
            page.update()
            return
        error_text.visible = False

        allergies_list = [
            a.strip() for a in (pet_allergies.value or "").split(",") if a.strip()
        ]

        pets_ref.set({
            "pets": firestore.ArrayUnion([{
                "name": pet_name.value,
                "type": pet_type.value,
                "age": pet_age.value,
                "breed": pet_breed.value,
                "allergies": allergies_list
            }])
        }, merge=True)

        await go_homepage(e)

    # change this later
    submit_btn = ft.Button(
        content=ft.Text("Save Profile", size=16, weight=ft.FontWeight.W_700),
        width=340,
        height=54,
        on_click=add_pet,
        color=white,
        bgcolor=primary,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=30),
            side=ft.BorderSide(width=1.5, color=black),
        ),
    )

    form = ft.Container(
        margin=ft.Margin.only(left=16, right=16, top=24, bottom=16),
        content=ft.Column(
            spacing=18,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                avatar_placeholder,
                ft.Container(height=6),
                labeled_input("Pet Name", pet_name),
                labeled_input("Pet Type", pet_type),
                labeled_input("Age", pet_age),
                labeled_input("Breed", pet_breed),
                labeled_input("Allergies", pet_allergies),
                error_text,
            ],
        ),
    )

    # Scrollable fields area, expands to fill remaining space above the button.
    scrollable_form = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[form],
    )

    # Bottom-anchored button bar, stays pinned below the scrollable fields.
    bottom_button_bar = ft.Container(
        padding=ft.Padding.only(left=16, right=16, top=12, bottom=24),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[submit_btn],
        ),
    )

    main_content = ft.Column(
        spacing=0,
        expand=True,
        controls=[
            appbar,
            scrollable_form,
            bottom_button_bar,
        ],
    )

    return ft.View(
        route="/petprofile_input",
        bgcolor=white,
        padding=0,
        spacing=0,
        controls=[main_content],
    )