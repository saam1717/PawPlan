import calendar
import datetime
import logging
import flet as ft
import threading
import os

from model.firestore_auth import get_uid
from model.json.uid_json import UserIdStore
from model.pet_crud import get_pet_list, get_pet_color_map, DEFAULT_PET_COLOR
from model.task_crud import (
    get_task_list,
    split_tasks_by_occurrence,
    task_occurs_on,
    format_occurrence_date,
)
from model.user_account_crud import get_data
from utility.navigation import go_to
from setup.firebase_setup import db
from utility.theme import get_colors, ON_BRAND, PRIMARY, HEADER_BLUE, ORANGE, NAV_BLUE, GREEN

logger = logging.getLogger(f"pawplan.{__name__}")


# Hardcoded values

DESTINATIONS = [
    ft.NavigationBarDestination(
        icon =  ft.Icons.WIDGETS_OUTLINED,
        selected_icon = ft.Icons.HOUSE,
        label = "Home"
    ),
    ft.NavigationBarDestination(
        icon = ft.Icons.WIDGETS_OUTLINED,
        selected_icon = ft.Icons.CHECKLIST,
        label = "Taskboard"
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
    if page.auth is not None:
        current_user_id = page.auth.user["email"]
        uid = UserIdStore()
        uid.set(str(current_user_id))
    else:
        current_user_id = get_uid()

    return current_user_id


# START OF VIEWS
def homepage_view(page: ft.Page) -> ft.View:

    # async functions
    def view_task_handler(pet_name):
        async def handler(e):
            await view_task(pet_name)
        return handler

    async def view_task(pet_name):
        logger.debug("Pet reminder: %s", pet_name)
        # remember which pet's reminders to show on /petreminder
        page.session.store.set("pet_name", pet_name)
        await page.push_route("/petreminder")

    async def go_settings(e):
        logger.debug("Settings nav clicked")
        await page.push_route("/settings")

    async def go_logout(e):
        logger.debug("Logout clicked")
        await page.push_route("/")

    pill_nav_routes = ["/homepage", "/taskboard", "/account_profile"]

    # Theme-aware colors (flip between light/dark)
    toggleColor = get_colors(page)
    primary = PRIMARY
    header_blue = HEADER_BLUE
    orange = ORANGE
    soft_border = toggleColor["border"]
    white = toggleColor["surface"]
    black = toggleColor["text"]
    green = GREEN
    nav_blue = NAV_BLUE
    calendar_header_blue = "#2F6FCB"
    weekend_blue = "#3B6FD6"


    # APPBAR
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

    appbar_divider = ft.Container(height=5, bgcolor=orange)\


    # PET CARDS
    pet_list = []

    pet_cards_row_height = 35

    def empty_state(message: str) -> ft.Container:
        return ft.Container(
            height = pet_cards_row_height,
            alignment = ft.Alignment.CENTER,
            content = ft.Text(message, color=ON_BRAND),
        )

    pet_cards_row = ft.Row(
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        controls=[empty_state("Loading pets...")]
    )

    def _fetch_pets():
        try:
            pets = get_pet_list()
            # update outer pet_list so pet_card can access correct data
            pet_list[:] = pets
            if pets:
                pet_cards = [pet_card(i) for i, _ in enumerate(pets)]
            else:
                pet_cards = [empty_state("No pets yet")]
            pet_cards_row.controls[:] = pet_cards
            page.update()
        except Exception as e:
            logger.exception("Failed fetching pets: %s", e)
            pet_cards_row.controls[:] = [empty_state("Failed to load pets")]
            page.update()

    # start background thread to fetch pets without blocking UI
    threading.Thread(target=_fetch_pets, daemon=True).start()

    def pet_card(index):
        # get the name per index
        pet_name = pet_list[index]["name"]
        pet_color = pet_list[index].get("color") or DEFAULT_PET_COLOR
        uid = return_uid(page)

        # page session
        page.session.store.set("index", index)
        page.session.store.set("uid", uid)

        async def handle_pet_click(e):
            await page.push_route("/petprofile")

        return ft.Container(
            width=110,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
                controls=[

                    ft.Text(pet_name, color=ON_BRAND, size=15, weight=ft.FontWeight.W_700),
                    ft.Container(
                        width=90,
                        height=90,
                        bgcolor=pet_color,
                        border_radius=10,
                        border=ft.Border.all(2, ON_BRAND),
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.PETS, size=40, color="#8A6A3B"),
                        on_click=handle_pet_click,
                    ),
                    ft.Button(
                        content=ft.Text("View Task", size=8, color=ON_BRAND),
                        bgcolor=green,
                        on_click= view_task_handler(pet_name), # logic to go to view reminder
                    ),
                ],
            ),
        )

    current_uid = return_uid(page)
    # Greet with the stored username (e.g. "Bella's human"), falling back to
    # the raw email / placeholder when no profile details exist yet.
    if current_uid:
        try:
            profile = get_data(current_uid) or {}
            display_name = profile.get("username") or current_uid
        except Exception as ex:
            logger.warning("Failed to load username for greeting: %s", ex)
            display_name = current_uid
        header_text = f"Hello {display_name}"
    else:
        header_text = "Hello, Pet Parent!"

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
                            color=ON_BRAND,
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
                            bgcolor=ON_BRAND,
                            on_click=go_to(page, "/petprofile_input"),
                        ),
                    ],
                ),
                pet_cards_row,
            ],
        ),
    )

    # CALENDAR
    today = datetime.date.today()
    calendar_year, calendar_month = today.year, today.month
    calendar.setfirstweekday(calendar.SUNDAY)
    weeks = calendar.monthcalendar(calendar_year, calendar_month)
    month_label = f"{calendar.month_name[calendar_month].upper()} {calendar_year}"

    weekday_labels = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

    # tasks from firestore, split by their schedule
    all_tasks = get_task_list()
    pet_color_map = get_pet_color_map()
    todays_tasks, upcoming_tasks = split_tasks_by_occurrence(all_tasks, today)

    def day_cell(day, col_index):
        weekend = col_index == 0 or col_index == 6
        todays = day == today.day
        text_color = weekend_blue if weekend else toggleColor["text"]
        if day == 0:
            return ft.Container(expand=1, height=30)

        has_task = any(
            task_occurs_on(t, datetime.date(calendar_year, calendar_month, day))
            for t in all_tasks
        )

        return ft.Container(
            expand=1,
            height=30,
            border_radius=6,
            bgcolor=primary if todays else None,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                spacing=0,
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        str(day),
                        size=11,
                        color=ON_BRAND if todays else text_color,
                        weight=ft.FontWeight.W_700 if todays else ft.FontWeight.W_400,
                    ),
                    ft.Container(
                        width=4,
                        height=4,
                        border_radius=2,
                        bgcolor=orange if has_task else None,
                    ),
                ],
            # content=ft.Text(
            #     str(day),
            #     size=11,
            #     color=ON_BRAND if todays else text_color,
            #     weight=ft.FontWeight.W_700 if todays else ft.FontWeight.W_400,
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
                        month_label, size=12, weight=ft.FontWeight.W_700, color=ON_BRAND
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
                                    label, size=9, weight=ft.FontWeight.W_700, color=toggleColor["muted_text"]
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


    # TASKS
    def task_row(occ_date, item):
        task_name = item.get("task_name", "Untitled task")
        pet_name = item.get("pet_name", "Untitled pet")
        alarm = item.get("alarm") or {}
        time_str = alarm.get("time_12hr") or alarm.get("time") or "No time set"
        pet_color = pet_color_map.get(pet_name, DEFAULT_PET_COLOR)

        return ft.Container(
            border=ft.Border.all(1, pet_color),
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            content=ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=12,
                        height=12,
                        border_radius=6,
                        bgcolor=pet_color,
                    ),
                    ft.Text(
                        f"{task_name} for {pet_name} - {time_str}, {format_occurrence_date(occ_date, today)}",
                        size=15,
                        weight=ft.FontWeight.W_600,
                        color=black,
                        expand=True,
                    ),
                ],
            ),
        )

    def empty_task_state(message):
        return ft.Container(
            border=ft.Border.all(1, soft_border),
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            content=ft.Text(
                message,
                size=14,
                weight=ft.FontWeight.W_600,
                color="#6B7280",
            ),
        )

    todays_rows = [task_row(d, t) for d, t in todays_tasks] or [
        empty_task_state("No tasks scheduled today")
    ]
    upcoming_rows = [task_row(d, t) for d, t in upcoming_tasks] or [
        empty_task_state("No upcoming tasks")
    ]

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
                *todays_rows,
                ft.Text(
                    "Upcoming Task",
                    size=20,
                    weight=ft.FontWeight.W_700,
                    color=black,
                ),
                *upcoming_rows,
            ],
        ),
    )


    # NAVIGATION PILL
    def pill_destination(index, label, icon):

        is_active = page.route == pill_nav_routes[index]

        async def handle_nav_click(e):
            print(pill_nav_routes[index])
            route = str(pill_nav_routes[index])
            # restore the pill BEFORE navigating: push_route tears down this view,
            # so updating floating_nav after the await would hit a detached control
            restore_nav(e)
            await page.push_route(route)

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
                        content=ft.Icon(icon, color=ON_BRAND, size=20),
                    ),
                    ft.Text(
                        label,
                        size=11,
                        color=ON_BRAND,
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


    floating_nav_overlay = ft.Container(
        left=0,
        right=0,
        bottom=20,
        alignment=ft.Alignment.CENTER,
        content=floating_nav,
    )

    return ft.View(
        route="/homepage",
        bgcolor=toggleColor["bg"],
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


# RUNNABLE
IS_WEB = os.environ.get("PORT") is not None
def _standalone_main(page: ft.Page):
    page.title = "PawPlan"
    if not IS_WEB:
        page.window.width = 430
        page.window.height = 900

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