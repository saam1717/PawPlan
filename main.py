import flet as ft
import os

# logger setup
from utility.logging_config import setup_logging
from utility.theme import app_themes, load_saved_theme_mode
from views.petprofile import petprofile_view
from views.settings import settings_view

setup_logging()
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from views.account_profile import account_profile_view
from views.startup import startup_view, make_on_login
from views.login import login_view
from views.register import register_view
from views.homepage import homepage_view
from views.petprofile_input import petprofile_input_view
from views.pet_tasks import pet_reminder_view
from views.taskboard import taskboard_view
from views.taskboard_input import taskboard_input_view

# clear any uid left over from a previous run so stale tabs can't read it
from model.firestore_auth import uid_account
_uid_file_cleared = False

IS_WEB = os.environ.get("PORT") is not None
logger.debug(f"IS_WEB = {IS_WEB}, PORT env = {os.environ.get('PORT')}")
async def main(page: ft.Page):
    global _uid_file_cleared
    if not _uid_file_cleared:
        _uid_file_cleared = True
        uid_account.clear()

    page.title = "PawPlan"
    if not IS_WEB:
        page.window.height = 900
        page.window.width = 430
        page.window.min_height = 900
        page.window.max_height = 900
        page.window.min_width = 430
        page.window.max_height = 900
        page.window.resizable = False
        await page.window.center()

    page.on_login = make_on_login(page)
    page.theme, page.dark_theme = app_themes()
    await load_saved_theme_mode(page)
    page.update()

    page.on_login = make_on_login(page)

    # originally a big chunk of elifs
    # add here new routes
    ROUTES = {
        "/": startup_view,
        "/login": login_view,
        "/register": register_view,
        "/homepage": homepage_view,
        "/petprofile_input": petprofile_input_view,
        "/account_profile": account_profile_view,
        "/petreminder": pet_reminder_view,
        "/settings": settings_view,
        "/petprofile": petprofile_view,
        "/taskboard": taskboard_view,
        "/taskboard_input": taskboard_input_view,
    }

    route_history = []
    nav_state = {"going_back": False}

    def route_change(e):
        page.views.clear()
        view_builder = ROUTES.get(page.route)
        if view_builder is None:
            view_builder = ROUTES["/homepage"]

        if nav_state["going_back"]:
            nav_state["going_back"] = False
        elif not route_history or route_history[-1] != page.route:
            route_history.append(page.route)

        page.views.append(view_builder(page))
        page.update()

    async def go_back(e=None):
        if len(route_history) > 1:
            route_history.pop()  # drop current route
            previous_route = route_history[-1]
            nav_state["going_back"] = True
            await page.push_route(previous_route)
        else:
            await page.push_route("/homepage")

    async def view_pop(e: ft.ViewPopEvent):
        # also handles the browser/hardware back button
        await go_back()

    page.go_back = go_back
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    route_change(None)


# ft.run(main, port=8550, view=ft.AppView.WEB_BROWSER)
ft.run(
    main,
    view=ft.AppView.WEB_BROWSER,
    port=int(os.environ.get("PORT", 8550)),
    host="0.0.0.0"
)