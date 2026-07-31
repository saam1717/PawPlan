import flet as ft


ON_BRAND = "#FFFFFF"


PRIMARY = "#0D6EFD"
HEADER_BLUE = "#1450B4"
NAV_BLUE = "#0B4FB0"
ORANGE = "#F5821F"
GREEN = "#4CAF50"

LIGHT = {
    "bg": "#FFFFFF",
    "surface": "#FFFFFF",
    "card": "#FFFFFF",
    "input_bg": "#FFFFFF",
    "text": "#000000",
    "muted_text": "#6B7280",
    "border": "#DDE3EE",
    "icon": "#000000",
}

DARK = {
    "bg": "#121417",
    "surface": "#1B1E23",
    "card": "#20242B",
    "input_bg": "#262A31",
    "text": "#F5F6F7",
    "muted_text": "#9CA3AF",
    "border": "#33383F",
    "icon": "#F5F6F7",
}


def get_colors(page: ft.Page) -> dict:
    if page.theme_mode == ft.ThemeMode.DARK:
        return DARK
    return LIGHT


def app_themes() -> tuple[ft.Theme, ft.Theme]:
    light_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=PRIMARY,
            surface=LIGHT["surface"],
            on_surface=LIGHT["text"],
            outline=LIGHT["border"],
        ),
        page_transitions=ft.PageTransitionsTheme(
            windows=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
            android=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
        ),
    )
    dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=PRIMARY,
            surface=DARK["surface"],
            on_surface=DARK["text"],
            outline=DARK["border"],
        ),
        page_transitions=ft.PageTransitionsTheme(
            windows=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
            android=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
        ),
    )
    return light_theme, dark_theme


async def apply_theme_mode(page: ft.Page, mode: ft.ThemeMode) -> None:
    """Set theme_mode and persist the choice so it survives a refresh/reload."""
    page.theme_mode = mode
    try:
        await page.client_storage.set_async(
            "pawplan_theme_mode", "dark" if mode == ft.ThemeMode.DARK else "light"
        )
    except Exception:
        pass


async def load_saved_theme_mode(page: ft.Page) -> None:
    """Restore a previously saved theme mode, defaulting to LIGHT."""
    saved = None
    try:
        saved = await page.client_storage.get_async("pawplan_theme_mode")
    except Exception:
        pass
    page.theme_mode = ft.ThemeMode.DARK if saved == "dark" else ft.ThemeMode.LIGHT