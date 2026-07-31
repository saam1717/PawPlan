import flet as ft
import datetime
import logging
from datetime import time

from utility.theme import get_colors, ON_BRAND, ORANGE, NAV_BLUE

logger = logging.getLogger(f"pawplan.{__name__}")

# shared with the rest of the app

orange = ORANGE
nav_blue = NAV_BLUE


def taskmaker_view(page: ft.Page) -> ft.View:
    page.scroll = ft.ScrollMode.AUTO
    toggleColor = get_colors(page)
    black = toggleColor["text"]
    white = toggleColor["surface"]

    # flet spazzes out for some reason if these aren't functions
    selection_text = ft.Text(weight=ft.FontWeight.BOLD, value="No task selected", color=black)

    async def go_back(e):
        logger.debug("Going back")
        await page.push_route("/homepage")

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

    def on_save_task(e):
        # TODO: wire up to Firestore / task list
        logger_msg = f"Saving task '{task_input.value}' for {pet_picker.value}"
        page.show_dialog(ft.SnackBar(ft.Text("Task saved!")))
        print(logger_msg)

    appbar = ft.Container(
        padding=ft.Padding.only(left=8, right=20, top=30, bottom=20),
        bgcolor=nav_blue,
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=ON_BRAND,
                    on_click=go_back,
                ),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text("Taskmaker", size=20, weight=ft.FontWeight.W_700, color=ON_BRAND),
                ),
                ft.Container(width=48),  # balances the back button so the title stays centered
            ]
        ),
    )

    pet_picker = ft.Dropdown(
        label="Choose Pet",
        # TODO: add added pets to dropdown
        options=[
            ft.dropdown.Option("Nanet Japoles"),
            ft.dropdown.Option("Layla Mesarka od Travnik"),
        ],
        width=300,
    )

    # inputs
    task_input = ft.TextField(label="Input new task here", width=300, text_align=ft.TextAlign.CENTER)

    time_picker = ft.TimePicker(
        value=time(hour=4, minute=20),
        confirm_text="Confirm",
        error_invalid_text="Time out of range",
        help_text="Pick your time slot",
        entry_mode=ft.TimePickerEntryMode.DIAL,
        on_change=on_time_change,
        on_dismiss=on_time_dismiss,
    )

    today = datetime.datetime(year=2026, month=7, day=22)
    date_picker = ft.DatePicker(
        first_date=datetime.datetime(year=today.year - 1, month=1, day=1),
        last_date=datetime.datetime(year=today.year + 1, month=today.month, day=20),
        current_date=today,
        on_change=on_date_change,
        on_dismiss=on_date_dismiss,
    )

    form_card = ft.Container(
        margin=ft.Margin.only(left=16, right=16, top=12),
        padding=ft.Padding.symmetric(horizontal=16, vertical=20),
        border=ft.Border.all(width=2.5, color=black),
        border_radius=20,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            controls=[
                pet_picker,
                task_input,
                ft.Button(
                    key="pick_time_button",
                    content="Pick time",
                    icon=ft.Icons.SCHEDULE,
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

    save_button = ft.Container(
        margin=ft.Margin.only(left=16, right=16, top=12, bottom=20),
        content=ft.FilledButton(
            content=ft.Text("Save Task", size=20, weight=ft.FontWeight.W_700),
            icon=ft.Icons.CHECK,
            style=ft.ButtonStyle(
                bgcolor=orange,
                color=ON_BRAND,
                shape=ft.RoundedRectangleBorder(radius=30),
                side=ft.BorderSide(width=1.5, color=black),
                padding=ft.Padding.symmetric(horizontal=24, vertical=16),
            ),
            on_click=on_save_task,
            width=300,
        ),
    )

    main_content = ft.Column(
        spacing=0,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.SafeArea(
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=0,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[form_card],
                    ),
                ),
            ),
        ],
    )

    return ft.View(
        route="/taskmaker",
        bgcolor=toggleColor["bg"],
        padding=0,
        spacing=0,
        controls=[
            ft.Column(
                expand=True,
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    appbar,
                    main_content,
                    save_button,
                ],
            )
        ],
    )


def _standalone_main(page: ft.Page):
    page.title = "Taskmaker"
    page.window.width = 430
    page.window.height = 900
    page.views.append(taskmaker_view(page))
    page.update()


if __name__ == "__main__":
    ft.run(_standalone_main, assets_dir="assets")