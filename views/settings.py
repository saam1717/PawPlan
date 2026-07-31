import flet as ft
import os
import logging


from utility.theme import get_colors, apply_theme_mode, PRIMARY, ON_BRAND, HEADER_BLUE

logger = logging.getLogger(f"pawplan.{__name__}")


SETTINGS_OPTIONS = [
    "Change Username",
    "Change Email",
    "Change Password",
    "Change Appearance"
]


def settings_view(page: ft.Page) -> ft.View:

    toggleColor = get_colors(page)

    async def go_back(e):
        logger.debug("Going back")
        await page.go_back()

    def setting_option_tapped(label):
        def handler(e):
            logger.debug("Setting option tapped clicked")
        return handler

    #APPBAR
    appbar = ft.Container(
        padding = ft.Padding.symmetric(horizontal=16, vertical=16),
        bgcolor = HEADER_BLUE,
        content=ft.Row(
            vertical_alignment = ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon = ft.Icons.ARROW_BACK,
                    icon_color = ON_BRAND,
                    on_click = go_back,
                ),

                ft.Text(
                    "Settings",
                    color = ON_BRAND,
                    size = 25,
                    weight = ft.FontWeight.W_800,
                )
            ]
        ),
    )

    async def toggle_appearance(e):
        if e.control.value:  # ON
            logger.debug("Dark mode enabled")
            await apply_theme_mode(page, ft.ThemeMode.DARK)
        else:  # OFF
            logger.debug("Light mode enabled")
            await apply_theme_mode(page, ft.ThemeMode.LIGHT)

        page.views[-1] = settings_view(page)
        page.update()

    def setting_row(label):
        if label ==  "Change Appearance":
            trailing = ft.Switch(
                value = page.theme_mode == ft.ThemeMode.DARK,
                active_color = PRIMARY,
                on_change = toggle_appearance,
            )
        else:
            trailing = ft.Icon(ft.Icons.CHEVRON_RIGHT, color = toggleColor["muted_text"], size = 20)


        return ft.Container(
            bgcolor = toggleColor["card"],
            border = ft.Border.all(1, toggleColor["border"]),
            border_radius = 8,
            padding = ft.Padding.symmetric(horizontal=14, vertical=16),

            on_click = None if label == "Change Appearance" else setting_option_tapped(label),
            content = ft.Row(
                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment = ft.CrossAxisAlignment.CENTER,

                controls = [
                    ft.Text(
                        label,
                        size = 15,
                        weight = ft.FontWeight.W_400,
                        color = toggleColor["text"],
                    ),
                    trailing,
                ],
            ),
        )

    settings_list = ft.Container(
        margin = ft.Margin.only(left = 16,
                                right = 16,
                                top = 16
        ),

        content = ft.Column(
            spacing = 10,
            controls = [
                setting_row(label) for label in SETTINGS_OPTIONS
            ],
        ),
    )



    main_content = ft.Column(
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            appbar,
            settings_list,
            ft.Container(height=100),
        ],
    )


    return ft.View(
        route="/settings",
        bgcolor=toggleColor["bg"],
        padding=0,
        spacing=0,
        controls=[
            main_content
        ],
    )

IS_WEB = os.environ.get("PORT") is not None
def _standalone_main(page: ft.Page):
    # Lets you run `python homepage.py` on its own to preview this screen
    page.title = "PawPlan"
    if not IS_WEB:
        page.window.width = 430
        page.window.height = 900
    page.views.append(settings_view(page))
    page.update()


if __name__ == "__main__":
    ft.run(_standalone_main)