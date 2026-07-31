import flet as ft
import logging
import threading

from model.pet_crud import (
    add_pet as add_pet_crud,
    get_pet_list,
    PASTEL_PET_COLORS,
    DEFAULT_PET_COLOR,
    MAX_PETS,
)
from firebase_admin import firestore

from utility.navigation import do_logout
from utility.theme import get_colors, ON_BRAND, PRIMARY, HEADER_BLUE
from model.json.uid_json import UserIdStore
from setup.firebase_setup import db

logger = logging.getLogger(__name__)


primary = PRIMARY
header_blue = HEADER_BLUE
orange = "#F5821F"


def labeled_input(label: str, field: ft.Control, colors: dict | None = None) -> ft.Column:
    """Wraps a field with a label above it, styled like the rest of the app's forms."""
    from utility.theme import LIGHT
    toggleColor = colors or LIGHT
    return ft.Column(
        spacing=6,
        controls=[
            ft.Text(label, size=13, weight=ft.FontWeight.W_600, color=toggleColor["muted_text"]),
            field,
        ],
    )


def petprofile_input_view(page: ft.Page) -> ft.View:
    toggleColor = get_colors(page)
    soft_border = toggleColor["border"]
    white = toggleColor["surface"]
    black = toggleColor["text"]

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
            await page.go_back()
            logger.debug(f"Back route pushed")
        except Exception as e:
            logger.error(f"Error occurred: {e}")
    async def go_settings(e):
        logger.debug("Settings nav clicked")
        await page.push_route("/settings")

    async def go_logout(e):
        logger.debug("Logout clicked")
        await do_logout(page)
    appbar = ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=16),
        bgcolor=header_blue,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=ON_BRAND,
                    on_click=go_back,
                ),
                ft.Text(
                    "Add Pet",
                    color=ON_BRAND,
                    size=22,
                    weight=ft.FontWeight.W_800,
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Icon(ft.Icons.NOTIFICATIONS_NONE, color=black, size=26),
                        ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            icon_color=black,
                            items=[
                                ft.PopupMenuItem(
                                    content=ft.Text("Settings"),
                                    icon=ft.Icons.SETTINGS_OUTLINED,
                                    on_click=go_settings,
                                ),
                                ft.PopupMenuItem(
                                    content=ft.Text("Log out"),
                                    icon=ft.Icons.LOGOUT,
                                    on_click=go_logout,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )

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

    # Pastel color picker for the new pet, stored in Firestore with the pet.
    selected_color = {"value": DEFAULT_PET_COLOR}

    def build_color_picker() -> ft.Row:
        swatches = []

        def select(name, hex_color):
            selected_color["value"] = hex_color
            for container, swatch_name, _ in swatches:
                is_selected = swatch_name == name
                container.border = ft.Border.all(3, black) if is_selected else None
                container.content = (
                    ft.Icon(ft.Icons.CHECK, size=18, color=black) if is_selected else None
                )
            page.update()

        for name, hex_color in PASTEL_PET_COLORS.items():
            is_selected = hex_color == selected_color["value"]
            container = ft.Container(
                width=40,
                height=40,
                border_radius=20,
                bgcolor=hex_color,
                alignment=ft.Alignment.CENTER,
                border=ft.Border.all(3, black) if is_selected else None,
                content=ft.Icon(ft.Icons.CHECK, size=18, color=black) if is_selected else None,
                on_click=lambda e, n=name, h=hex_color: select(n, h),
            )
            swatches.append((container, name, hex_color))

        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=14,
            controls=[swatch[0] for swatch in swatches],
        )

    # Avatar placeholder (visual anchor at the top of the form)
    avatar_placeholder = ft.Container(
        width=90,
        height=90,
        bgcolor="#F1D9B0",
        border_radius=45,
        border=ft.Border.all(2, soft_border),
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.PETS, size=44, color="#8A6A3B"),
    )

    # ---------- Resolve current user (no DB access here, just id lookup) ----------

    # normal functions can't call async functions
    async def handle_add_pet(e):
        if not pet_name.value or not pet_type.value:
            error_text.value = "Please enter a name and select a pet type."
            error_text.visible = True
            page.update()
            return
        error_text.visible = False

        allergies_list = [
            a.strip() for a in (pet_allergies.value or "").split(",") if a.strip()
        ]

        try:
            ok, message = add_pet_crud(
                pet_name.value,
                pet_type.value,
                pet_age.value,
                pet_breed.value,
                allergies_list,
                selected_color["value"],
            )
        except Exception as ex:
            logger.error(f"Failed to add pet: {ex}")
            error_text.value = "Something went wrong. Please try again."
            error_text.visible = True
            page.update()
            return

        if not ok:
            error_text.value = message
            error_text.visible = True
            page.update()
            return

        await go_homepage(e)

    # ---------- Pet limit (max MAX_PETS per account) ----------
    submit_btn = ft.Button(
        content=ft.Text("Save Profile", size=16, weight=ft.FontWeight.W_700),
        width=340,
        height=54,
        on_click=handle_add_pet,
        color=ON_BRAND,
        bgcolor=primary,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=30),
            side=ft.BorderSide(2, color=toggleColor["border"]),
        ),
    )

    def _check_pet_limit():
        """Disable the form and show a notice when the account is at the cap."""
        try:
            current = get_pet_list() or []
            if len(current) >= MAX_PETS:
                submit_btn.disabled = True
                submit_btn.bgcolor = "#9CA3AF"
                error_text.value = f"Pet limit reached. You can have up to {MAX_PETS} pets."
                error_text.visible = True
                page.update()
        except Exception as ex:
            logger.exception("Failed checking pet limit: %s", ex)

    threading.Thread(target=_check_pet_limit, daemon=True).start()

    form = ft.Container(
        margin=ft.Margin.only(left=16, right=16, top=24, bottom=16),
        content=ft.Column(
            spacing=18,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                avatar_placeholder,
                ft.Container(height=6),
                labeled_input("Pet Name", pet_name, colors=toggleColor),
                labeled_input("Pet Type", pet_type, colors=toggleColor),
                labeled_input("Age", pet_age, colors=toggleColor),
                labeled_input("Breed", pet_breed, colors=toggleColor),
                labeled_input("Allergies", pet_allergies, colors=toggleColor),
                ft.Column(
                    spacing=6,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Color", size=13, weight=ft.FontWeight.W_600, color="#6B7280"),
                        build_color_picker(),
                    ],
                ),
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