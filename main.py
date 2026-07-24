import flet as ft
import time

# logger setup
from utility.logging_config import setup_logging
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
from views.petreminder import pet_reminder_view


def main(page: ft.Page):
    page.title = "PawPlan"
    page.window.height = 900
    page.window.width = 430
    page.window.resizable = False
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
        "/petprofile": petprofile_view
    }

    def route_change(e):
        # Route change should be quick; view builders should avoid blocking I/O.
        page.views.clear()
        view_builder = ROUTES.get(page.route)

        if view_builder is None:
            view_builder = ROUTES["/homepage"] # default route

        page.views.append(view_builder(page))
        page.update()


    async def view_pop(e: ft.ViewPopEvent):
        # Keep view_pop simple and avoid timing/logging here as requested.
        if e.view is not None:
            page.views.remove(e.view)
            if page.views:
                top_view = page.views[-1]
                await page.push_route(top_view.route)
            else:
                await page.push_route("/homepage")
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    route_change(None)


ft.run(main, port=8550, view=ft.AppView.WEB_BROWSER)