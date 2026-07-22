from cProfile import label

import flet as ft
import datetime
from datetime import time
from flet.controls import page


def taskmaker_view(page: ft.Page) -> ft.View:
    page.scroll = ft.ScrollMode.AUTO

    selection_text = ft.Text(weight=ft.FontWeight.BOLD, value="No task selected")

    #flet spazzes out for some reason if these aren't functions
    def on_time_change(e):
        selection_text.value = f"Time selected: {time_picker.value}"
        page.update()

    def on_time_dismiss(e):
        page.show_dialog(ft.SnackBar(ft.Text("TimePicker dismissed!")))

    def on_date_change(e):
        selection_text.value = f"Date selected: {date_picker.value.strftime('%Y-%m-%d')}"
        page.update()

    def on_date_dismiss(e):
        page.show_dialog(ft.SnackBar(ft.Text("DatePicker dismissed!")))

    def on_pick_date_click(e):
        page.show_dialog(date_picker)


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

    task_input = ft.TextField(label="Input new task here", width=300, text_align=ft.TextAlign.CENTER)

    time_picker = ft.TimePicker(
    value=time(hour=4, minute=20),
    confirm_text="Confirm",
    error_invalid_text="Time out of range",
    help_text="Pick your time slot",
    entry_mode=ft.TimePickerEntryMode.DIAL,
    on_change = on_time_change,
    on_dismiss = on_time_dismiss,
    )

    today = datetime.datetime(year=2026, month=7, day=22)
    date_picker = ft.DatePicker(
        first_date=datetime.datetime(year=today.year - 1, month=1, day=1),
        last_date=datetime.datetime(year=today.year + 1, month=today.month, day=20),
        current_date=today,
        on_change=on_date_change,
        on_dismiss=on_date_dismiss,
    )

    content = ft.SafeArea(
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing = 15,
                controls=[
                    task_input,
                    ft.Button(
                        key="pick_time_button",
                        content="Pick time",
                        icon=ft.Icons.TIME_TO_LEAVE,
                        on_click=lambda e: page.show_dialog(time_picker),
                    ),
                    ft.Button(
                        key="pick_date_button",
                        content="Pick date",
                        icon=ft.Icons.CALENDAR_MONTH,
                        on_click=lambda e: page.show_dialog(date_picker),
                    ),
                    selection_text,
                ],
            ),
        )

    return ft.View(
        appbar=appbar,
        controls=[tasks, content],
    )

def _standalone_main(page: ft.Page):
    # Lets you run `python homepage.py` on its own to preview this screen
    page.title = "TaskMaker"
    page.window.width = 430
    page.window.height = 900
    page.views.append(taskmaker_view(page))
    page.update()


if __name__ == "__main__":
    ft.run(_standalone_main, assets_dir="assets")