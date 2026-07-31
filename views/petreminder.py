import flet as ft
import logging

from google.cloud.firestore_v1 import FieldFilter
from model.firebase_setup import db
from model.firestore_auth import get_uid
from utility.theme import get_colors, ON_BRAND

logger = logging.getLogger(__name__)


def pet_reminder_view(page: ft.Page) -> ft.View:
    toggleColor = get_colors(page)


    # colors used for the reminder pills, cycled by index to match mockup
    pill_colors = ["#6C5CE7", "#F05648"]

    async def go_back(e):
        logger.info("Back nav clicked")
        try:
            # await page.pop_route()
            await page.push_route("/homepage")
            logger.info("Route popped")
        except Exception as e:
            logger.error(f"Error occurred: {e}")

    # header: back arrow + centered title, no overflow menu
    appbar = ft.Container(
        padding=ft.Padding.symmetric(horizontal=20, vertical=10),
        bgcolor=toggleColor["surface"],
        content=ft.Stack(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Reminders",
                            size=22,
                            weight=ft.FontWeight.W_800,
                            color=toggleColor["text"]
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=toggleColor["text"],
                            icon_size=26,
                            on_click=go_back,
                        ),
                    ],
                ),
            ],
        ),
    )

    def create_alarm():

        def delete_alarm():
            alarm_list_layout.controls.remove(alarm_unit)
            page.update()

        alarm_unit = build_reminder_pill("New Reminder", len(alarm_list_layout.controls))
        alarm_list_layout.controls.append(alarm_unit)
        page.update()

    import threading

    # temporary code
    # change all later
    pet_name = "ben"  # temporary, change later
    reminder_list = []

    def build_reminder_pill(reminder_name, index):
        color = pill_colors[index % len(pill_colors)]
        return ft.Container(
            margin=ft.Margin.only(left=16, right=16, top=8, bottom=8),
            padding=ft.Padding.symmetric(horizontal=14, vertical=14),
            border_radius=30,
            bgcolor=color,
            content=ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=32,
                        height=32,
                        border_radius=10,
                        border=ft.Border.all(width=2, color=ON_BRAND),
                    ),
                    ft.Text(
                        reminder_name,
                        color=ON_BRAND,
                        size=15,
                        weight=ft.FontWeight.W_600,
                        expand=True,
                    ),
                ],
            ),
        )

    def create_reminder_control(reminder_name, index):
        return build_reminder_pill(reminder_name, index)

    alarm_list_layout = ft.Column(
        expand=True,
        spacing=0,
        scroll=ft.ScrollMode.ADAPTIVE,
        controls=[ft.Text("Loading reminders...", color=toggleColor["text"])],
    )

    def _fetch_reminders():
        try:
            current_user_id = get_uid()  # Get the current user's email
            reminder_ref = (
                db.collection("users").document(current_user_id).collection("details").document("pets").collection("reminders").
                where(filter=FieldFilter("pet", "==", pet_name))
                .stream()
            )
            reminders = []
            for reminder in reminder_ref:
                data = reminder.to_dict()
                reminders.append(data.get("name", ""))

            reminder_list[:] = reminders
            if reminders:
                alarm_list_layout.controls[:] = [
                    create_reminder_control(r, i) for i, r in enumerate(reminders)
                ]
            else:
                alarm_list_layout.controls[:] = [ft.Text("No reminders", color=toggleColor["text"])]
            page.update()
        except Exception as ex:
            logger.exception("Failed fetching reminders: %s", ex)
            alarm_list_layout.controls[:] = [ft.Text("Failed to load reminders", color=toggleColor["text"])]
            page.update()

    threading.Thread(target=_fetch_reminders, daemon=True).start()

    # reminder container
    alarm_cont = ft.Container(
        margin=ft.Margin.only(left=16, right=16, top=15, bottom=5),
        padding=ft.Padding.symmetric(vertical=10),
        expand=True,
        border=ft.Border.all(width=2.5, color=toggleColor["text"]),
        border_radius=18,
        content=alarm_list_layout  # Inject the list layout here
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
                icon_color=ON_BRAND,
                icon_size=26,
                tooltip="Add reminder",
                on_click=create_alarm,
            ),
        ),
    )

    return ft.View(
        route="/petreminder",
        bgcolor=toggleColor["bg"],
        controls=[
            ft.Container(
                expand=True,
                bgcolor=toggleColor["bg"],
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