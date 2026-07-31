import flet as ft
import logging
import os
from datetime import date

from model.pet_crud import get_pet_color_map, DEFAULT_PET_COLOR
from model.task_crud import (
    get_task_list,
    split_tasks_by_occurrence,
    format_occurrence_date,
    complete_task_occurrence,
)
from utility.navigation import go_to
from utility.theme import get_colors, ON_BRAND, ORANGE, NAV_BLUE

logger = logging.getLogger(f"pawplan.{__name__}")

black = "#000000"
white = "#FFFFFF"
# colors used for the task pills
pill_colors = ["#6C5CE7", "#F05648"]
orange = ORANGE
nav_blue = NAV_BLUE

NAV_SHRINK_SCALE = 0.6
NAV_HOVER_SCALE = 1.1
LOGO_SIZE = 70

DESTINATIONS = [
    ft.NavigationBarDestination(
        icon=ft.Icons.WIDGETS_OUTLINED,
        selected_icon=ft.Icons.HOUSE,
        label="Home",
    ),
    ft.NavigationBarDestination(
        icon=ft.Icons.WIDGETS_OUTLINED,
        selected_icon=ft.Icons.CHECKLIST,
        label="Taskboard",
    ),
    ft.NavigationBarDestination(
        icon=ft.Icons.WIDGETS_OUTLINED,
        selected_icon=ft.Icons.PERSON,
        label="Profile",
    ),
]


def taskboard_view(page: ft.Page) -> ft.View:
    today = date.today()
    pet_color_map = get_pet_color_map()
    todays_tasks, upcoming_tasks = split_tasks_by_occurrence(get_task_list(), today)

    async def go_settings(e):
        logger.debug("Settings nav clicked")
        await page.push_route("/settings")

    async def go_logout(e):
        logger.debug("Logout clicked")
        await page.push_route("/")

    toggleColor = get_colors(page)
    black = toggleColor["text"]
    white = toggleColor["surface"]


    pill_nav_routes = ["/homepage", "/taskboard", "/account_profile"]

    # ---------------- Branded app header (logo, notifications, settings) ----------------
    # Matches homepage.py's appbar so the same top bar appears on every main tab.
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

    appbar_divider = ft.Container(height=5, bgcolor=orange)

    page_title = ft.Container(
        padding=ft.Padding.only(left=8, right=20, top=16, bottom=8),
        bgcolor=white,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Taskboard",
                    size=28,
                    weight=ft.FontWeight.W_800,
                    color=black,
                ),
            ],
        ),
    )

    def task_label(occ_date, item):
        task_name = item.get("task_name", "Untitled task")
        alarm = item.get("alarm") or {}
        time_str = alarm.get("time_12hr") or alarm.get("time") or "No time set"
        return f"{time_str} - {task_name} ({format_occurrence_date(occ_date, today)})"

    def no_tasks_text(message):
        return ft.Container(
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.symmetric(vertical=20),
            content=ft.Text(
                message,
                size=14,
                weight=ft.FontWeight.W_600,
                color=ft.Colors.BLACK,
            ),
        )

    async def complete_occurrence(item, occ_date):
        try:
            return complete_task_occurrence(item, occ_date)
        except Exception as err:
            logger.error("complete_task_occurrence failed: %s", err)
            return False

    def task_pill(label, occ_date, item, color, list_holder, empty_message):
        label_text = ft.Text(
            label,
            # task_label(item),
            color=ON_BRAND,
            size=14,
            weight=ft.FontWeight.W_600,
            expand=True,
            style=ft.TextStyle(
                # decoration=ft.TextDecoration.LINE_THROUGH if item["done"] else None,
                decoration_color=ON_BRAND,
            ),
        )

        pill_container = ft.Container(
            margin=ft.Margin.only(top=6, bottom=6),
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            border_radius=30,
            bgcolor=color,
            animate_opacity=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )

        state = {"busy": False}

        def mark_done():
            label_text.style = ft.TextStyle(
                # decoration=ft.TextDecoration.LINE_THROUGH if item["done"] else None,
                decoration_color=ON_BRAND,
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
            fill_color=ON_BRAND,
            active_color=ON_BRAND,
        )

        pill_container.content = ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[checkbox, label_text],
        )

        return pill_container

    today_list_holder = {}
    today_pill_controls = (
        [
            task_pill(
                task_label(d, t),
                d,
                t,
                pet_color_map.get(t.get("pet_name"), DEFAULT_PET_COLOR),
                today_list_holder,
                "No tasks scheduled today",
            )
            for d, t in todays_tasks
        ]
        if todays_tasks
        else [no_tasks_text("No tasks scheduled today")]
    )
    today_pills = ft.Column(
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        controls=today_pill_controls,
        # controls=[task_pill(t, i) for i, t in enumerate(TODAYS_TASKS)],
    )
    today_list_holder["column"] = today_pills

    upcoming_list_holder = {}
    upcoming_pill_controls = (
        [
            task_pill(
                task_label(d, t),
                d,
                t,
                pet_color_map.get(t.get("pet_name"), DEFAULT_PET_COLOR),
                upcoming_list_holder,
                "No upcoming tasks",
            )
            for d, t in upcoming_tasks
        ]
        if upcoming_tasks
        else [no_tasks_text("No upcoming tasks")]
    )
    upcoming_pills = ft.Column(
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        controls=upcoming_pill_controls,
    )
    upcoming_list_holder["column"] = upcoming_pills


    #     controls=(
    #         [task_pill(t, i) for i, t in enumerate(UPCOMING_TASKS)]
    #         if UPCOMING_TASKS
    #         else [
    #             ft.Container(
    #                 alignment=ft.Alignment.CENTER,
    #                 padding=ft.Padding.symmetric(vertical=20),
    #                 content=ft.Text(
    #                     "No upcoming tasks",
    #                     size=14,
    #                     weight=ft.FontWeight.W_600,
    #                     color=toggleColor["muted_text"],
    #                 ),
    #             )
    #         ]
    #     ),
    # )

    def section_header(label):
        return ft.Container(
            margin=ft.Margin.only(left=20, right=20, top=24, bottom=10),
            content=ft.Text(
                label,
                size=22,
                weight=ft.FontWeight.W_800,
                color=black,
            ),
        )

    def section_box(content_column, min_height=300):
        return ft.Container(
            margin=ft.Margin.only(left=20, right=20),
            padding=ft.Padding.symmetric(horizontal=10, vertical=10),
            border=ft.Border.all(width=2.5, color=black),
            border_radius=20,
            height=min_height,
            content=content_column,
        )

    todays_task_section = ft.Column(
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            section_header("Today's Task"),
            section_box(today_pills),
        ],
    )

    upcoming_task_section = ft.Column(
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            section_header("Upcoming Task"),
            section_box(upcoming_pills, min_height=300),
        ],
    )

    add_task_button = ft.Button(
        content=ft.Row(
            spacing=6,
            tight=True,
            controls=[
                ft.Icon(ft.Icons.ADD, color=white, size=18),
                ft.Text("Add Task", color=white, weight=ft.FontWeight.W_700),
            ],
        ),
        bgcolor="#0D6EFD",
        on_click=go_to(page, "/taskboard_input"),
    )

    # ---------------- Floating nav bar ----------------
    nav_state = {"resting_scale": 1.0, "hovering": False}
    nav_active_index = {"value": 1}
    nav_icon_containers = []
    nav_labels = []

    def apply_nav_scale(scale):
        floating_nav.scale = scale
        floating_nav.update()

    def update_nav_highlight():
        active = nav_active_index["value"]
        for i, (icon_box, label_text) in enumerate(zip(nav_icon_containers, nav_labels)):
            icon_box.bgcolor = orange if i == active else None
            label_text.weight = ft.FontWeight.W_700 if i == active else ft.FontWeight.W_600
        floating_nav.update()

    def nav_destination_tapped(index):
        async def handler(e):
            nav_active_index["value"] = index
            update_nav_highlight()
            restore_nav(e)

            target_route = pill_nav_routes[index]
            logger.debug(f"Bottom nav tapped: {target_route}")
            if page.route != target_route:
                await page.push_route(target_route)

        return handler

    def pill_destination(index, label, icon):
        is_active = nav_active_index["value"] == index

        icon_box = ft.Container(
            width=34,
            height=34,
            border_radius=17,
            bgcolor=orange if is_active else None,
            alignment=ft.Alignment.CENTER,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT_CUBIC),
            content=ft.Icon(icon, color=ON_BRAND, size=20),
        )
        label_text = ft.Text(
            label,
            size=11,
            color=ON_BRAND,
            weight=ft.FontWeight.W_700 if is_active else ft.FontWeight.W_600,
        )

        nav_icon_containers.append(icon_box)
        nav_labels.append(label_text)

        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            border_radius=20,
            on_click=nav_destination_tapped(index),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
                tight=True,
                controls=[icon_box, label_text],
            ),
        )

    floating_nav = ft.Container(
        bgcolor=nav_blue,
        border_radius=32,
        padding=ft.Padding.symmetric(horizontal=18, vertical=10),
        margin=ft.Margin.symmetric(horizontal=16, vertical=10),
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
        nav_state["resting_scale"] = NAV_SHRINK_SCALE
        if not nav_state["hovering"]:
            apply_nav_scale(NAV_SHRINK_SCALE)

    def restore_nav(e=None):
        nav_state["resting_scale"] = 1.0
        if not nav_state["hovering"]:
            apply_nav_scale(1.0)

    def handle_nav_hover(e: ft.HoverEvent):
        is_hovering = e.data == "true"
        nav_state["hovering"] = is_hovering
        if is_hovering:
            apply_nav_scale(NAV_HOVER_SCALE)
        else:
            apply_nav_scale(nav_state["resting_scale"])

    floating_nav.on_click = restore_nav
    floating_nav.on_hover = handle_nav_hover

    def handle_content_scroll(e: ft.OnScrollEvent):
        if e.event_type == ft.ScrollType.USER:
            shrink_nav()

    main_content = ft.Column(
        spacing=0,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        on_scroll=handle_content_scroll,
        controls=[
            appbar,
            appbar_divider,
            page_title,
            todays_task_section,
            upcoming_task_section,
            ft.Container(height=160),
        ],
    )

    floating_nav_overlay = ft.Container(
        left=0,
        right=0,
        bottom=20,
        alignment=ft.Alignment.CENTER,
        content=floating_nav,
    )

    # Pinned above the nav overlay so the add button can never be covered by
    # the pill, regardless of scroll position or shrink/expand state.
    # bottom=145 clears the hover-expanded (1.1x) pill top (~120px) with ~25px
    # to spare, while keeping the button as close as possible to the nav.
    add_task_overlay = ft.Container(
        left=0,
        right=0,
        bottom=145,
        alignment=ft.Alignment.CENTER,
        content=add_task_button,
    )

    return ft.View(
        route="/taskboard",
        bgcolor=toggleColor["bg"],
        padding=0,
        spacing=0,
        controls=[
            ft.Stack(
                expand=True,
                controls=[
                    main_content,
                    ft.Container(height=100),
                    add_task_overlay,
                    floating_nav_overlay,
                ],
            )
        ],
    )

IS_WEB = os.environ.get("PORT") is not None
def _standalone_main(page: ft.Page):
    page.title = "PawPlan"
    if not IS_WEB:
        page.window.width = 430
        page.window.height = 900
    page.views.append(taskboard_view(page))
    page.update()


if __name__ == "__main__":
    ft.run(_standalone_main)
