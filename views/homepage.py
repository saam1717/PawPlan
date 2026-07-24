import calendar
import datetime
import logging

import flet as ft
import threading
from google.cloud.firestore_v1 import FieldFilter

from model.firestore_auth import get_uid
from model.pet_crud import get_pet_list
from utility.navigation import go_to
from model.firebase_setup import db

# LOGGER SETUP
# === COPILOT NOTE ===
# Changed by Copilot: Pets are now loaded in a background thread to avoid
# blocking UI rendering during navigation. The view now renders quickly
# and updates when pet data arrives. Also fixed IndexError by updating
# the shared pet_list before building pet cards.
# === END NOTE ===
logger = logging.getLogger(f"pawplan.{__name__}")

# Sample based on Mock Screens (will be updated later on)
TODAYS_TASKS = [
    {"time": "8:00 AM", "task": "Feed Bella"},
    {"time": "12:00 PM", "task": "Walk Max"},
    {"time": "6:00 PM", "task": "Give Bella Medication"},
]

UPCOMING_EVENT = "Upcoming Vet Visit for Bella - June 15"

DESTINATIONS = [
    ft.NavigationBarDestination(
        icon =  ft.Icons.WIDGETS_OUTLINED,
        selected_icon = ft.Icons.HOUSE,
        label = "Home"
    ),
    ft.NavigationBarDestination(
        icon = ft.Icons.WIDGETS_OUTLINED,
        selected_icon = ft.Icons.CALENDAR_MONTH,
        label = "Calendar"
    ),
    ft.NavigationBarDestination(
        icon = ft.Icons.WIDGETS_OUTLINED,
        selected_icon = ft.Icons.PERSON,
        label = "Profile"
    ),
]

LOGO_SIZE = 70
NAV_SHRINK_SCALE = 0.6



# returns uid from model
def return_uid(page):
    current_user_id = get_uid()
    return current_user_id


# START OF VIEWS
def homepage_view(page: ft.Page) -> ft.View:

    def view_reminder_handler(pet_name):
        async def handler(e):
            await view_reminder(pet_name, return_uid(page))
        return handler
    async def view_reminder(pet_name, uid): # need to change code here
        logger.debug("Pet reminder: %s", pet_name)
        reminder_ref = (
            db.collection("users").document(uid).collection("details").document("pets").collection("reminders").
            where(filter=FieldFilter("pet","==",pet_name))
            .stream()
        )
        for reminders in reminder_ref:
            print(f"{reminders.id} => {reminders.to_dict()}")

        await page.push_route("/petreminder")




    # navigation
    # no navigation here yet
    async def go_settings(e):
        # logger.info("Settings nav clicked")
        logger.debug("Settings nav clicked")
        await page.push_route("/settings")

    pill_nav_routes = ["/homepage", "/calendar", "/account_profile"]


    # content variables
    primary = "#0D6EFD"
    header_blue = "#1450B4"
    orange = "#F5821F"
    soft_border = "#DDE3EE"
    white = "#FFFFFF"
    black = "#000000"
    green = "#4CAF50"
    nav_blue = "#0B4FB0"
    calendar_header_blue = "#2F6FCB"
    weekend_blue = "#3B6FD6"



    appbar = ft.Container(
        padding=ft.Padding.symmetric(horizontal=20, vertical=12),
        bgcolor=white,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=LOGO_SIZE,
                            height=LOGO_SIZE,
                            border_radius=10,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Image(
                                src="pawplan_icon.png",
                                width=LOGO_SIZE,
                                height=LOGO_SIZE,
                                fit=ft.BoxFit.CONTAIN,
                            ),
                        ),

                        ft.Row(
                            spacing=2,
                            controls=[
                                ft.Text("Paw", size=22, weight=ft.FontWeight.W_800, color=orange),
                                ft.Text("Plan", size=22, weight=ft.FontWeight.W_800, color="#0B2E6B"),
                            ],
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
                                    content = ft.Text("Settings"),
                                    icon=ft.Icons.SETTINGS_OUTLINED,
                                    on_click=go_settings,
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )

    appbar_divider = ft.Container(height=5, bgcolor=orange)



    # firestore code (load pets in background to avoid blocking UI)
    # current_user_id = get_uid()
    # logger.debug("current_user_id: %s", current_user_id)
    #
    # pets_ref = db.collection("users").document(current_user_id).collection("details").document("pets")
    #
    #
    # # get data
    # pet_list = []
    # doc = pets_ref.get()
    #
    # # extra debugging
    # if doc.exists:
    #     data = doc.to_dict()
    #     if not data.get("pets", []):
    #         logger.debug("pet list empty")
    #     pet_list = data.get("pets", [])
    #     logger.debug("Pet list: %s", pet_list)
    # else:
    #     logger.debug("No such document!")

    pet_list = []

    # placeholder row for pet cards; populated asynchronously
    pet_cards_row = ft.Row(
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        controls=[ft.Text("Loading pets...")]
    )

    def _fetch_pets():
        try:
            pets = get_pet_list(return_uid(page))
            # update outer pet_list so pet_card can access correct data
            pet_list[:] = pets
            if pets:
                pet_cards = [pet_card(i) for i, _ in enumerate(pets)]
            else:
                pet_cards = [ft.Text("No pets yet")]
            pet_cards_row.controls[:] = pet_cards
            page.update()
        except Exception as e:
            logger.exception("Failed fetching pets: %s", e)
            pet_cards_row.controls[:] = [ft.Text("Failed to load pets")]
            page.update()

    # start background thread to fetch pets without blocking UI
    threading.Thread(target=_fetch_pets, daemon=True).start()



    def pet_card(index):
        # get the name per index
        pet_name = pet_list[index]["name"]

        return ft.Container(
            width=110,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
                controls=[

                    ft.Text(pet_name, color=white, size=15, weight=ft.FontWeight.W_700),
                    ft.Container(
                        width=90,
                        height=90,
                        bgcolor="#F1D9B0",
                        border_radius=10,
                        border=ft.Border.all(2, white),
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.PETS, size=40, color="#8A6A3B"),
                        on_click = go_to(page, "/petprofile")# edit code to reroute to a page
                    ),
                    ft.Button(
                        content=ft.Text("View Reminder", size=8, color=white),
                        bgcolor=green,
                        on_click= view_reminder_handler(pet_name), # logic to go to view reminder
                    ),
                ],
            ),
        )

    header_text = f"Hello {str(return_uid(page))}"

    header = ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=16),
        bgcolor=header_blue,
        content=ft.Column(
            spacing=16,
            controls=[

                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            header_text,
                            color=white,
                            size=24,
                            weight=ft.FontWeight.W_800,
                        ),
                        ft.Button(
                            content=ft.Row(
                                spacing=6,
                                tight=True,
                                controls=[
                                    ft.Text("Add Pet", color=primary, weight=ft.FontWeight.W_700),
                                    ft.Icon(ft.Icons.ARROW_CIRCLE_RIGHT, color=primary, size=18),
                                ],
                            ),
                            bgcolor=white,
                            on_click=go_to(page, "/petprofile_input"),
                        ),
                    ],
                ),
                pet_cards_row,
            ],
        ),
    )

    # Added Calendar (should have backend functions for vet scheduled visits)
    today = datetime.date.today()
    calendar_year, calendar_month = today.year, today.month
    calendar.setfirstweekday(calendar.SUNDAY)
    weeks = calendar.monthcalendar(calendar_year, calendar_month)
    month_label = f"{calendar.month_name[calendar_month].upper()} {calendar_year}"

    weekday_labels = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

    def day_cell(day, col_index):
        weekend = col_index == 0 or col_index == 6
        todays = day == today.day
        text_color = weekend_blue if weekend else "#1F2937"
        if day == 0:
            return ft.Container(expand=1, height=30)
        return ft.Container(
            expand=1,
            height=30,
            border_radius=6,
            bgcolor=primary if todays else None,
            alignment=ft.Alignment.CENTER,
            content=ft.Text(
                str(day),
                size=11,
                color=white if todays else text_color,
                weight=ft.FontWeight.W_700 if todays else ft.FontWeight.W_400,
            ),
        )

    calendar_rows = [
        ft.Row(
            spacing=2,
            controls=[day_cell(d, i) for i, d in enumerate(week)],
        )
        for week in weeks
    ]

    calendar_widget = ft.Container(
        margin=ft.Margin.only(left=16, right=16, top=14),
        bgcolor=white,
        border_radius=10,
        border=ft.Border.all(1, soft_border),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            spacing=6,
            controls=[

                ft.Container(
                    padding=ft.Padding.symmetric(vertical=8),
                    bgcolor=calendar_header_blue,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text(
                        month_label, size=12, weight=ft.FontWeight.W_700, color=white
                    ),
                ),

                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=8),
                    content=ft.Row(
                        spacing=2,
                        controls=[
                            ft.Container(
                                expand=1,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    label, size=9, weight=ft.FontWeight.W_700, color="#6B7280"
                                ),
                            )
                            for label in weekday_labels
                        ],
                    ),
                ),
                ft.Container(

                    padding=ft.Padding.only(left=8, right=8, bottom=10),
                    content=ft.Column(spacing=4, controls=calendar_rows),
                ),
            ],
        ),
    )





    # Today's Tasks (for backends this needs to be connected to reminder page)

    def task_row(item):
        return ft.Container(
            border=ft.Border.all(1, soft_border),
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            content=ft.Text(
                f"{item['time']} - {item['task']}",
                size=15,
                weight=ft.FontWeight.W_600,
                color=black,
            ),
        )


    tasks_section = ft.Container(
        margin=ft.Margin.only(left=16, right=16, top=16),
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Text(
                    "Today's Task",
                    size=20,
                    weight=ft.FontWeight.W_700,
                    color=black,
                ),

                *[task_row(item) for item in TODAYS_TASKS],
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=14, vertical=12),
                    border=ft.Border.all(1, soft_border),
                    border_radius=8,
                    content=ft.Text(
                        UPCOMING_EVENT,
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=black,
                    ),
                ),
            ],
        ),
    )

    # Navigation Bar (turned into a pill)

    def pill_destination(index, label, icon):

        is_active = page.route == pill_nav_routes[index]

        async def handle_nav_click(e):
            print(pill_nav_routes[index])
            route = str(pill_nav_routes[index])
            await page.push_route(route)
            restore_nav(e)

        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            border_radius=20,
            on_click=handle_nav_click,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing = 2,
                tight=True,
                controls=[
                    ft.Container(
                        width=34,
                        height=34,
                        border_radius=17,
                        bgcolor=orange if is_active else None,
                        alignment=ft.Alignment.CENTER,
                        animate=ft.Animation(100, ft.AnimationCurve.EASE_OUT_CUBIC),
                        content=ft.Icon(icon, color=white, size=20),
                    ),
                    ft.Text(
                        label,
                        size=11,
                        color=white,
                        weight=ft.FontWeight.W_700 if is_active else ft.FontWeight.W_600,
                    ),
                ],
            ),
        )

    floating_nav = ft.Container(
        bgcolor=nav_blue,
        border_radius=32,
        padding=ft.Padding.symmetric(horizontal=18, vertical=10),
        scale=1.0,
        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        shadow=ft.BoxShadow(
            blur_radius=16,
            spread_radius=1,
            color="#00000055",
            offset=ft.Offset(0, 4),
        ),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            tight=True,
            controls=[
                pill_destination(i, dest.label, dest.selected_icon)

                for i, dest in enumerate(DESTINATIONS)
            ],
        ),
    )

    def shrink_nav():
        if floating_nav.scale != NAV_SHRINK_SCALE:
            floating_nav.scale = NAV_SHRINK_SCALE
            floating_nav.update()

    def restore_nav(e=None):
        if floating_nav.scale != 1.0:
            floating_nav.scale = 1.0
            floating_nav.update()

    floating_nav.on_click = restore_nav

    def handle_content_scroll(e: ft.OnScrollEvent):
        if e.event_type == ft.ScrollType.USER:
            shrink_nav()

    main_content = ft.Column(
        spacing = 0,
        left = 0,
        top = 0,
        right = 0,
        bottom = 0,
        scroll = ft.ScrollMode.AUTO,
        on_scroll = handle_content_scroll,

        controls = [
            appbar,
            appbar_divider,
            header,
            calendar_widget,
            tasks_section,
            ft.Container(height=100),
        ],
    )

    # FIX: position the nav bar with Stack's absolute-positioning attributes
    # (left/right/bottom) instead of wrapping it in an expand=True Container.
    # Having two expand=True siblings in the Stack was preventing the
    # scrollable Column above from ever getting a bounded height, so
    # ft.ScrollMode.AUTO had nothing to scroll within and just clipped content.
    floating_nav_overlay = ft.Container(
        left=0,
        right=0,
        bottom=20,
        alignment=ft.Alignment.CENTER,
        content=floating_nav,
    )

    return ft.View(
        route="/homepage",
        bgcolor="#FFFFFF",
        padding=0,
        spacing=0,
        controls=[
            ft.Stack(
                expand = True,
                controls = [
                    main_content,
                    floating_nav_overlay,
                ],
            )
        ],
    )


def _standalone_main(page: ft.Page):
    # Lets you run `python homepage.py` on its own to preview this screen

    page.title = "PawPlan"
    page.window.width = 430
    page.window.height = 900

    # Disable the default slide/zoom page-route transition on every
    # platform, so switching views (Home/Calendar/Profile) is instant
    # with no animation.
    page.theme = ft.Theme(
        page_transitions=ft.PageTransitionsTheme(
            windows=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
            android=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
        )
    )

    page.views.append(homepage_view(page))
    page.update()


if __name__ == "__main__":
    ft.run(_standalone_main, assets_dir="assets")