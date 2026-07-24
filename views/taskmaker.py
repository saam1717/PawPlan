import flet as ft

def taskmaker_view(page: ft.Page) -> ft.View:

    appbar = ft.Container(
        padding=ft.Padding.symmetric(horizontal=20, vertical=10),
        bgcolor="#8C52FF",
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("Task Maker", size=20, weight=ft.FontWeight.W_700, color="#FFFFFF"),
            ]
        ),
    )

    tasks = ft.Container(
        margin=ft.Margin.only(left=16, right=16, top=10),
        content=ft.Text(
            "Today's Tasks",
            size=22,
            weight=ft.FontWeight.W_700,
            color="Black",
        ),
    )

    task = ft.TextField(label="Input new task here", width=300, text_align=ft.TextAlign.CENTER)

    return ft.View(
        route = "/taskmaker",
        controls = [
            appbar,
            tasks,
        ]
    )