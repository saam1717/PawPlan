import flet as ft
import logging

logger = logging.getLogger(__name__)


def petprofile_view(page: ft.Page) -> ft.View:
    orange = "#F5893C"
    blue = "#0B4FB0"
    purple = "#8B7AE8"
    white = "#FFFFFF"

    # temporary pet data, wire up to Firestore later
    pet = {
        "name": "Bella",
        "age": 4,
        "breed": "Chihuahua",
        "photo_url": "https://example.com/this-image-does-not-exist.png",
        "allergies": ["Chicken Sensitivity"],
    }

    async def go_back(e):
        logger.info("Back nav clicked")
        try:
            await page.push_route("/homepage")
            logger.info("Route popped")
        except Exception as ex:
            logger.error(f"Error occurred: {ex}")

    # header
    appbar = ft.Container(
        padding=ft.Padding.symmetric(horizontal=10, vertical=10),
        bgcolor=orange,
        content=ft.Stack(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Paw Profile",
                            size=22,
                            weight=ft.FontWeight.W_800,
                            color=white,
                        ),
                    ],
                ),
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
                src=pet["photo_url"],
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

    # name / age / breed
    info_section = ft.Container(
        padding=ft.Padding.only(top=18, bottom=10),
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(pet["name"], size=30, weight=ft.FontWeight.W_800, color="#000000"),
                ft.Text(f"Age: {pet['age']}", size=16, color="#000000"),
                ft.Text(f"Breed: {pet['breed']}", size=16, color="#000000"),
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
                    border=ft.Border.all(width=2, color=white),
                )
            )
        row_controls.append(
            ft.Text(text, color=white, size=14, weight=ft.FontWeight.W_600, expand=True)
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

    def build_allergies_content():
        controls = []

        controls.append(ft.Text("Allergies:", size=16, weight=ft.FontWeight.W_600, color="#000000"))
        if pet["allergies"]:
            for a in pet["allergies"]:
                controls.append(med_pill(a, show_checkbox=False))
        else:
            controls.append(ft.Text("No known allergies", size=13, color=ft.Colors.GREY_600))

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
        bgcolor=white,
        padding=0,
        controls=[main_column],
    )


if __name__ == "__main__":
    def _main(page: ft.Page):
        page.views.append(petprofile_view(page))
        page.update()

    ft.run(_main)
