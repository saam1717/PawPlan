import logging
import flet as ft

logger = logging.getLogger(__name__)
# === COPILOT NOTE ===
# go_to is a small helper used across the app to call page.push_route.
# It attempts navigation and then calls an optional on_after callback.
# Note: timing logs added earlier to main were removed per request.
# === END NOTE ===

# for push route with no extra conditions
from model.firestore_auth import uid_account

async def do_logout(page: ft.Page):
    uid_account.clear()
    if page.auth is not None:
        page.logout()
    await page.push_route("/")

def go_to(page: ft.Page, route: str, on_after=None):
    async def handler(e):
        try:
            logger.debug("Navigating to %s", route)
            await page.push_route(route)
        except Exception as ex:
            logger.error(f"Navigation to {route} failed: {ex}")
        if on_after:
            try:
                on_after(e)
            except Exception as ex:
                logger.exception("on_after callback failed: %s", ex)
    return handler