import flet as ft
import logging

from model.pet_crud import get_specific_pet
from utility.theme import get_colors, ON_BRAND, ORANGE, NAV_BLUE

logger = logging.getLogger(__name__)


def petprofile_view(page: ft.Page) -> ft.View:
    toggleColor = get_colors(page)
    orange = ORANGE
    blue = NAV_BLUE
    purple = "#8B7AE8"
    # white = "#FFFFFF"
    black = "#000000"

    # get page session values
    index = page.session.store.get("index")
    uid = page.session.store.get("uid")
    logger.debug(f"uid: {uid}")
    logger.debug(f"index: {index}")
    white = toggleColor["surface"]

    # temporary pet data, wire up to Firestore later
    pet = get_specific_pet(uid, index) or {}
    # get_specific_pet returns {} when no pet exists (e.g. stale session index),
    # so fall back to placeholders instead of crashing on pet["name"].
    if not pet:
        pet = {"name": "Unknown Pet", "age": "?", "breed": "Unknown", "allergies": []}

    async def go_back(e):
        logger.info("Back nav clicked")
        try:
            await page.go_back()
            logger.info("Route popped")
        except Exception as ex:
            logger.error(f"Error occurred: {ex}")
    async def go_settings(e):
        logger.debug(f"Settings route pushed: {e}")
        await page.push_route("/settings")

    async def go_logout(e):
        logger.debug(f"Logout route pushed: {e}")
        await page.push_route("/")

    # header
    appbar = ft.Container(
        padding=ft.Padding.symmetric(horizontal=10, vertical=10),
        bgcolor=orange,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=white,
                            icon_size=26,
                            on_click=go_back,
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Paw Profile",
                            size=22,
                            weight=ft.FontWeight.W_800,
                            color=ON_BRAND,
                        ),
                    ],
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

    photo_size = 280

    photo_cont = ft.Container(
        bgcolor=blue,
        alignment=ft.Alignment.CENTER,
        padding=ft.Padding.symmetric(horizontal=24, vertical=24),
        content=ft.Container(
            width=photo_size,
            height=photo_size,
            content=ft.Image(
                src = "https://example.com/this-image-does-not-exist.png",
                # src=pet["photo_url"],
                width=photo_size,
                height=photo_size,
                fit="cover",
                border_radius=6,
                error_content=ft.Container(
                    content=ft.Icon(ft.Icons.PETS, size=100, color=ft.Colors.GREY_400),
                    alignment=ft.Alignment.CENTER,
                    bgcolor=ft.Colors.GREY_200,
                ),
            ),
        ),
    )

    # connect to firebase
    info_section = ft.Container(
        padding=ft.Padding.only(top=18, bottom=10),
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(pet.get("name"), size=30, weight=ft.FontWeight.W_800, color=toggleColor["text"]),
                ft.Text(f"Age: {pet.get('age')}", size=16, color=toggleColor["text"]),
                ft.Text(f"Breed: {pet.get('breed')}", size=16, color=toggleColor["text"]),
            ],
        ),
    )

    # ---- allergies section only ----

    def med_pill(text, show_checkbox=True):
        row_controls = []
        if show_checkbox:
            row_controls.append(
                ft.Container(
                    width=28,
                    height=28,
                    border_radius=9,
                    border=ft.Border.all(width=2, color=ON_BRAND),
                )
            )
        row_controls.append(
            ft.Text(text, color=ON_BRAND, size=14, weight=ft.FontWeight.W_600, expand=True)
        )
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            border_radius=26,
            bgcolor=purple,
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=row_controls,
            ),
        )

    # connect to firestore
    def build_allergies_content():
        controls = []

        controls.append(ft.Text("Allergies:", size=16, weight=ft.FontWeight.W_600, color=toggleColor["text"]))
        if pet.get("allergies"):
            for a in pet["allergies"]:
                controls.append(med_pill(a, show_checkbox=False))
        else:
            controls.append(ft.Text("No known allergies", size=13, color=toggleColor["muted_text"]))

        return controls

    # dedicated container for the allergies section — keep new info blocks
    # (e.g. medication, vet records) as separate sibling containers here later
    allergies_section = ft.Container(
        content=ft.Column(
            spacing=10,
            controls=build_allergies_content(),
        ),
    )

    body_section = ft.Container(
        expand=True,
        padding=ft.Padding.symmetric(horizontal=20),
        content=ft.Column(
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                allergies_section,
                # add future sections here, e.g. medication_section, vet_records_section
            ],
        ),
    )

    main_column = ft.Column(
        spacing=0,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            appbar,
            ft.Container(
                expand=True,
                content=ft.Column(
                    spacing=0,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        photo_cont,
                        info_section,
                        body_section,
                    ],
                ),
            ),
        ],
    )


    return ft.View(
        route="/petprofile",
        bgcolor=toggleColor["bg"],
        padding=0,
        controls=[main_column],
    )


if __name__ == "__main__":
    def _main(page: ft.Page):
        page.views.append(petprofile_view(page))
        page.update()


    ft.run(_main)
