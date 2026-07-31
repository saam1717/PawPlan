import flet as ft
import os
import logging
import threading

from model.firestore_auth import get_uid
from model.pet_crud import get_pet_list, remove_pet, DEFAULT_PET_COLOR
from model.user_account_crud import get_data
from utility.theme import get_colors, ON_BRAND, PRIMARY, ORANGE, HEADER_BLUE, NAV_BLUE

logger = logging.getLogger(__name__)


primary = PRIMARY
orange = ORANGE
header_blue = HEADER_BLUE
nav_blue = NAV_BLUE
soft_blue_bg = "#EAF0FB"




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

LOGO_SIZE = 56

NAV_SHRINK_SCALE = 0.6
NAV_HOVER_SCALE = 1.1


# Sample owner data (swap for real data later)
SAMPLE_OWNER = {
    "name": "Juan Dela Cruz",
    "email": "@juan_dcruz",
    "dob": "1990-01-01",
    "gender": "Male",
}


def account_profile_view(page: ft.Page) -> ft.View:
    # start with placeholders; load real data in background
    toggleColor = get_colors(page)
    black = toggleColor["text"]
    white = toggleColor["surface"]
    soft_border = toggleColor["border"]



    OWNER_DATA = {}
    pet_list = []

    # ROUTE PUSH
    async def go_settings(e):
        logger.debug(f"Settings route pushed: {e}")
        await page.push_route("/settings")

    async def go_logout(e):
        logger.debug(f"Logout route pushed: {e}")
        await page.push_route("/")


    pill_nav_routes = ["/homepage", "/taskboard", "/account_profile"]

    # PILL COLOR STATE
    section_state = {"active": "owner"}

    def select_section(section):
        def handler(e):
            section_state["active"] = section
            owner_tab.bgcolor = primary if section == "owner" else soft_blue_bg
            owner_tab_text.color = ON_BRAND if section == "owner" else primary
            pet_tab.bgcolor = primary if section == "pet" else soft_blue_bg
            pet_tab_text.color = ON_BRAND if section == "pet" else primary
            logger.info(f"Profile section switched to: {section}")

            profile_content.content = build_profile_content()
            profile_content.update()
            profile_nav_bar.update()

        return handler

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

    appbar_divider = ft.Container(height=5, bgcolor=orange)

    # Header
    header = ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=16),
        bgcolor=header_blue,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Account Profile",
                    color=ON_BRAND,
                    size=22,
                    weight=ft.FontWeight.W_800,
                ),
            ],
        ),
    )

    # Owner and Pet Profile Toggle
    owner_tab_text = ft.Text(
        "Owner", color=ON_BRAND, weight=ft.FontWeight.W_700, size=14, text_align=ft.TextAlign.CENTER
    )
    pet_tab_text = ft.Text(
        "Pet", color=primary, weight=ft.FontWeight.W_700, size=14, text_align=ft.TextAlign.CENTER
    )

    owner_tab = ft.Container(
        expand=True,
        bgcolor=primary,
        border_radius=8,
        padding=ft.Padding.symmetric(vertical=8, horizontal=0),
        on_click=select_section("owner"),
        content=owner_tab_text,
    )
    pet_tab = ft.Container(
        expand=True,
        bgcolor=soft_blue_bg,
        border_radius=8,
        padding=ft.Padding.symmetric(vertical=8, horizontal=0),
        on_click=select_section("pet"),
        content=pet_tab_text,
    )

    profile_nav_bar = ft.Container(
        bgcolor=soft_blue_bg,
        border_radius=10,
        padding=ft.Padding.all(4),
        content=ft.Row(
            spacing=4,
            controls=[owner_tab, pet_tab],
        ),
    )

    # Owner Profile
    def detail_row(label, value):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(label, size=13, color=toggleColor["muted_text"], weight=ft.FontWeight.W_600),
                ft.Text(value, size=14, color=black, weight=ft.FontWeight.W_700),
            ],
        )

    def owner_profile_card():
        return ft.Container(
            padding=ft.Padding.all(20),
            bgcolor=white,
            border_radius=12,
            border=ft.Border.all(1, soft_border),
            content=ft.Column(
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=80, height=80, bgcolor=soft_blue_bg, border_radius=40,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.PERSON, size=44, color=primary),
                    ),
                    ft.Text(OWNER_DATA.get("username", ""), size=20, weight=ft.FontWeight.W_800,
                            color=black, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"Email: {OWNER_DATA.get('email', '')}", size=13, color=toggleColor["muted_text"],
                            text_align=ft.TextAlign.CENTER),
                    ft.Container(height=1, bgcolor=soft_border),
                    detail_row("Date of Birth (MM-DD-YYYY)", OWNER_DATA.get("dob", "")),
                    detail_row("Gender", OWNER_DATA.get("gender", "")),
                ],
            ),
        )

    def make_delete_handler(pet_name):
        def handler(e):
            # Code for UI responsiveness
            try:
                idx = next((i for i, p in enumerate(pet_list) if p.get("name") == pet_name), None)
                if idx is not None:
                    pet_list.pop(idx)
                    profile_content.content = build_profile_content()
                    page.update()
            except Exception as ex:
                logger.exception("Failed updating UI for delete: %s", ex)

            # Perform backend deletion in background
            def _do_delete():
                try:
                    remove_pet(get_uid(), pet_name)
                    # refresh authoritative list
                    pets = get_pet_list(get_uid())
                    pet_list[:] = pets
                    profile_content.content = build_profile_content()
                    page.update()
                except Exception as ex:
                    logger.exception("Failed deleting pet: %s", ex)

            threading.Thread(target=_do_delete, daemon=True).start()

        return handler

    def pet_profile_card(pet):
        allergies = pet.get("allergies", []),
        allergies_display = " ,".join(", ".join(sublist) for sublist in allergies) if allergies else "None"
        pet_color = pet.get("color") or DEFAULT_PET_COLOR
        return ft.Container(
            padding=ft.Padding.all(20),
            bgcolor=white,
            border_radius=12,
            border=ft.Border.all(1, soft_border),
            content=ft.Column(
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=80, height=80, bgcolor=pet_color, border_radius=40,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(ft.Icons.PETS, size=44, color=primary),
                    ),
                    ft.Text(pet.get("name", "Pet"), size=20, weight=ft.FontWeight.W_800,
                            color=black, text_align=ft.TextAlign.CENTER),
                    ft.Text(pet.get("breed", ""), size=13, color=toggleColor["muted_text"],
                            text_align=ft.TextAlign.CENTER),
                    ft.Container(height=1, bgcolor=soft_border),
                    detail_row("Type", pet.get("type", "")),
                    detail_row("Age", pet.get("age", "")),
                    detail_row("Allergies", allergies_display),

                    ft.Button(
                        content="Delete Pet",
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.RED,
                            side=ft.BorderSide(3, color="000000")
                        ),
                        icon=ft.Icons.DELETE,
                        on_click=make_delete_handler(pet.get("name", ""))
                    )
                ],
            ),
        )

    # start with empty UI; populate in background
    profile_content = ft.Container(content=ft.Text("Loading profile...", color=black))

    def build_profile_content():
        if section_state["active"] == "owner":
            return owner_profile_card()
        if pet_list:
            return ft.Column(spacing=12, controls=[pet_profile_card(p) for p in pet_list])
        return ft.Text("No pets yet", color=toggleColor["muted_text"], text_align=ft.TextAlign.CENTER)

    profile_details = ft.Container(
        margin=ft.Margin.only(left=16, right=16, top=16, bottom=16),
        content=ft.Column(
            spacing=12,
            controls=[
                profile_nav_bar,
                profile_content,
            ],
        ),
    )

    # fetch data in background
    def _fetch_profile():
        try:
            uid = get_uid()
            data = get_data(uid) or {}
            pets = get_pet_list(uid) or []
            OWNER_DATA.clear()
            OWNER_DATA.update(data)
            pet_list[:] = pets
            profile_content.content = build_profile_content()
            page.update()
        except Exception as ex:
            logger.exception("Failed fetching profile data: %s", ex)

    threading.Thread(target=_fetch_profile, daemon=True).start()

    # ---------------- Floating nav bar ----------------
    nav_state = {"resting_scale": 1.0, "hovering": False}
    # This is the Account Profile page, so "Profile" (index 2) starts active.
    nav_active_index = {"value": 2}
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
            logger.info(f"Bottom nav tapped: {target_route}")
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
            on_click=nav_destination_tapped(index),  # navigation call, may need to be changed
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
                pill_destination(i, dest.label, dest.selected_icon)  # may need to change this one too
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
        on_scroll=handle_content_scroll,
        controls=[
            appbar,
            appbar_divider,
            header,
            profile_details,
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
        route="/account_profile",
        bgcolor=toggleColor["bg"],
        padding=0,
        spacing=0,
        controls=[
            ft.Stack(
                expand=True,
                controls=[
                    main_content,
                    floating_nav_overlay,
                ],
            )
        ],
    )


# Standalone runnable
IS_WEB = os.environ.get("PORT") is not None
def _standalone_main(page: ft.Page):
    page.title = "Account Profile"
    if not IS_WEB:
        page.window.width = 430
        page.window.height = 900
    page.views.append(account_profile_view(page))
    page.update()


if __name__ == "__main__":
    ft.run(_standalone_main, assets_dir="assets")