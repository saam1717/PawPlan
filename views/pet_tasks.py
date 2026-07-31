import flet as ft
import logging
import threading
from datetime import date

from model.pet_crud import get_pet_color_map, DEFAULT_PET_COLOR
from model.task_crud import (
    get_task_list,
    split_tasks_by_occurrence,
    format_occurrence_date,
    complete_task_occurrence,
)
from utility.navigation import go_to

logger = logging.getLogger(__name__)

black = "#000000"
white = "#FFFFFF"


def pet_reminder_view(page: ft.Page) -> ft.View:

    # which pet's reminders we're showing (set by homepage.py before navigating)
    pet_name = page.session.store.get("pet_name") or ""

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

    # header: back arrow + centered title, no overflow menu
    appbar = ft.Container(
        padding=ft.Padding.symmetric(horizontal=20, vertical=10),
        bgcolor="#FFFFFF",
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color="#000000",
                            icon_size=26,
                            on_click=go_back,
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Reminders",
                            size=22,
                            weight=ft.FontWeight.W_800,
                            color="#000000",
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

    def no_tasks_text(message):
        return ft.Container(
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.symmetric(vertical=20),
            content=ft.Text(
                message,
                size=14,
                weight=ft.FontWeight.W_600,
                color=black,
            ),
        )

    async def complete_occurrence(item, occ_date):
        try:
            return complete_task_occurrence(item, occ_date)
        except Exception as err:
            logger.error("complete_task_occurrence failed: %s", err)
            return False

    def task_label(occ_date, item):
        task_name = item.get("task_name", "Untitled task")
        alarm = item.get("alarm") or {}
        time_str = alarm.get("time_12hr") or alarm.get("time") or "No time set"
        return f"{time_str} - {task_name} ({format_occurrence_date(occ_date, date.today())})"

    def build_reminder_pill(label, occ_date, item, color, list_holder, empty_message):
        label_text = ft.Text(
            label,
            color=black,
            size=15,
            weight=ft.FontWeight.W_600,
            expand=True,
        )

        pill_container = ft.Container(
            margin=ft.Margin.only(top=8, bottom=8),
            padding=ft.Padding.symmetric(horizontal=14, vertical=14),
            border_radius=30,
            bgcolor=color,
            animate_opacity=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )

        state = {"busy": False}

        def mark_done():
            label_text.style = ft.TextStyle(
                decoration=ft.TextDecoration.LINE_THROUGH,
                decoration_color=black,
            )
            pill_container.opacity = 0.5
            label_text.update()
            pill_container.update()

        def revert_done():
            label_text.style = None
            pill_container.opacity = 1.0
            label_text.update()
            pill_container.update()

        async def on_check_change(e: ft.ControlEvent):
            if not e.control.value or state["busy"]:
                return
            state["busy"] = True
            mark_done()

            if await complete_occurrence(item, occ_date):
                # occurrence removed from Firestore -> drop the pill from its list
                column = list_holder.get("column")
                if column is not None:
                    if pill_container in column.controls:
                        column.controls.remove(pill_container)
                    if not column.controls:
                        column.controls.append(no_tasks_text(empty_message))
                    column.update()
            else:
                e.control.value = False
                revert_done()
            state["busy"] = False

        checkbox = ft.Checkbox(
            value=False,
            on_change=on_check_change,
            check_color=color,
            fill_color=white,
            active_color=white,
        )

        pill_container.content = ft.Row(
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[checkbox, label_text],
        )

        return pill_container

    reminder_list_layout = ft.Column(
        expand=True,
        spacing=0,
        scroll=ft.ScrollMode.ADAPTIVE,
        controls=[no_tasks_text("Loading reminders...")],
    )

    list_holder = {"column": reminder_list_layout}

    def _fetch_reminders():
        try:
            tasks = get_task_list()
            # only show tasks for the pet whose "View Task" was pressed on the homepage
            pet_tasks = [t for t in tasks if t.get("pet_name") == pet_name]
            pet_color = get_pet_color_map().get(pet_name, DEFAULT_PET_COLOR)

            today = date.today()
            todays, upcoming = split_tasks_by_occurrence(pet_tasks, today)
            occurrences = todays + upcoming

            if occurrences:
                reminder_list_layout.controls[:] = [
                    build_reminder_pill(
                        task_label(occ_date, task),
                        occ_date,
                        task,
                        pet_color,
                        list_holder,
                        f"No reminders for {pet_name}",
                    )
                    for occ_date, task in occurrences
                ]
            else:
                reminder_list_layout.controls[:] = [
                    no_tasks_text(f"No reminders for {pet_name}")
                ]
            page.update()
        except Exception as ex:
            logger.exception("Failed fetching reminders: %s", ex)
            reminder_list_layout.controls[:] = [no_tasks_text("Failed to load reminders")]
            page.update()

    threading.Thread(target=_fetch_reminders, daemon=True).start()

    # reminder container
    alarm_cont = ft.Container(
        margin=ft.Margin.only(left=16, right=16, top=15, bottom=5),
        padding=ft.Padding.symmetric(vertical=10),
        expand=True,
        border=ft.Border.all(width=2.5, color="#000000"),
        border_radius=18,
        content=reminder_list_layout  # Inject the list layout here
    )

    # add button
    add_button = ft.Container(
        margin=ft.Margin.only(top=10, bottom=20),
        align=ft.Alignment.CENTER,
        content=ft.Container(
            width=52,
            height=52,
            border_radius=26,
            bgcolor="#0B4FB0",
            alignment=ft.Alignment.CENTER,
            content=ft.IconButton(
                icon=ft.Icons.ADD,
                icon_color="white",
                icon_size=26,
                tooltip="Add reminder",
                on_click=go_to(page, "/taskboard_input")
            ),
        ),
    )

    return ft.View(
        route="/petreminder",
        bgcolor=white,
        controls=[
            ft.Container(
                expand=True,
                bgcolor=white,
                content=ft.Column(
                    spacing=0,
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[
                        appbar,
                        alarm_cont,
                        add_button,
                    ],
                ),
            )
        ],
    )
