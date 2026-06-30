import flet as ft


def main(page: ft.Page):
    page.title = "PawPlan"
    page.bgcolor = "#FFFFFF"
    page.scroll = False

    primary = "#0D6EFD"
    soft_border = "#DDE3EE"
    white = "#FFFFFF"
    white38 = "#FFFFFF66"

    appbar = ft.Container(
        padding=ft.padding.symmetric(horizontal=20, vertical=10),
        bgcolor="#FFFFFF",
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("PawPlan", size=20, weight=ft.FontWeight.W_700, color="#000000"),
            ]
        ),
    )

    header = ft.Container(
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        bgcolor=primary,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Hello, John",
                            color=white,
                            size=18,
                            weight=ft.FontWeight.W_700,
                        ),
                        ft.ElevatedButton(
                            "Add Pet",
                            bgcolor=white,
                            color=primary,
                            on_click=lambda e: None,
                        ),
                    ],
                ),
                ft.Divider(height=1, color=white38),
            ],
        ),
    )

    calendar = ft.Container(
        margin=ft.margin.symmetric(horizontal=16),
        padding=ft.padding.all(12),
        bgcolor=white,
        border_radius=12,
        border=ft.border.all(1, soft_border),
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("JULY 2026", size=12, color="#4B5563"),
                        ft.Text("Calendar", size=12, color="#9CA3AF"),
                    ],
                ),
                ft.GridView(
                    runs_count=1,
                    max_extent=28,
                    spacing=4,
                    child_aspect_ratio=1,
                    controls=[
                        ft.Container(bgcolor="#F3F4F6", border_radius=4, height=22)
                        for _ in range(42)
                    ],
                ),
            ],
        ),
    )

    tasks = ft.Container(
        margin=ft.margin.only(left=16, right=16, top=10),
        content=ft.Text(
            "Today's Tasks",
            size=22,
            weight=ft.FontWeight.W_700,
            color="Black",
        ),
    )

    bottom_nav = ft.Container(
        padding=ft.padding.symmetric(horizontal=20, vertical=10),
        bgcolor="#0B4FB0",
        border_radius=ft.border_radius.only(top_left=20, top_right=20),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                ft.TextButton(
                    "Home", style=ft.ButtonStyle(color=white), on_click=lambda e: None
                ),
                ft.TextButton(
                    "Calendar",
                    style=ft.ButtonStyle(color=white),
                    on_click=lambda e: None,
                ),
                ft.TextButton(
                    "Profile",
                    style=ft.ButtonStyle(color=white),
                    on_click=lambda e: None,
                ),
            ],
        ),
    )

    page.add(
        ft.Column(
            spacing=0,
            expand=True,
            controls=[
                appbar,
                header,
                calendar,
                tasks,
                ft.Container(expand=True),
                bottom_nav,
            ],
        )
    )

    page.window_width = 430
    page.window_height = 900


if __name__ == "__main__":
    ft.app(target=main)
