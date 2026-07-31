import flet as ft
import logging
from datetime import time, date
import calendar

from model.json.uid_json import UserIdStore
from model.pet_crud import get_pet_list
from model.task_crud import add_task as add_task_crud

logger = logging.getLogger(__name__)

# firestore setup


primary = "#0D6EFD"
header_blue = "#1450B4"
orange = "#F5821F"
soft_border = "#DDE3EE"
white = "#FFFFFF"
black = "#000000"


def labeled_input(label: str, field: ft.Control) -> ft.Column:
    """Wraps a field with a label above it, styled like the rest of the app's forms."""
    return ft.Column(
        spacing=6,
        controls=[
            ft.Text(label, size=13, weight=ft.FontWeight.W_600, color="#6B7280"),
            field,
        ],
    )


class AlarmClockSelector(ft.Container):
    """Alarm clock selection component with time picker, calendar, and day selector"""

    def __init__(self, page: ft.Page, on_alarm_saved=None):
        # Default values
        self._page = page
        self.on_alarm_saved = on_alarm_saved

        # Default values
        self.selected_time = time(8, 0)
        self.selected_date = date.today()
        self.selected_days = []
        self.is_repeating = False
        self.current_month = date.today().month
        self.current_year = date.today().year
        self.day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # Set default tab to "Repeating" (index 0 now)
        self.tabs_selected = 0  # CHANGED: 0 is now Repeating

        # Day buttons list for updating
        self.day_buttons = []
        self.calendar_grid = None
        self.month_label = None
        self.time_picker = None
        self.time_display = None
        self.tabs = None
        self.tab_view = None
        self.tab_buttons = None

        # Build the control
        super().__init__(
            content=self._build_controls(),
            padding=10,
            width=360,
        )

    def _build_tab_buttons(self):
        """Build the tab buttons with current selection state"""
        return ft.Row(
            [
                ft.Container(
                    content=ft.Text("Repeating", color=white if self.tabs_selected == 0 else black),
                    # CHANGED: Repeating first
                    bgcolor=primary if self.tabs_selected == 0 else "#F5F7FA",
                    padding=10,
                    border_radius=8,
                    on_click=lambda e: self.switch_tab(0),
                    expand=True,
                ),
                ft.Container(
                    content=ft.Text("Specific Date", color=white if self.tabs_selected == 1 else black),
                    # CHANGED: Specific Date second
                    bgcolor=primary if self.tabs_selected == 1 else "#F5F7FA",
                    padding=10,
                    border_radius=8,
                    on_click=lambda e: self.switch_tab(1),
                    expand=True,
                ),
            ],
            spacing=5,
        )

    def _build_controls(self):
        """Build all the controls for the alarm selector"""
        # Time Picker
        self.time_picker = ft.TimePicker(
            confirm_text="Confirm",
            cancel_text="Cancel",
            value=self.selected_time,
            on_change=self.on_time_change,
        )

        self.time_display = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ACCESS_TIME, color=primary),
                    ft.Text(
                        value=self.selected_time.strftime("%I:%M %p"),
                        size=40,
                        weight=ft.FontWeight.BOLD,
                        color=black,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            on_click=self.open_time_picker,
            padding=ft.Padding.symmetric(horizontal=20, vertical=15),
            border=ft.Border.all(2, soft_border),
            border_radius=12,
            bgcolor=white,
        )

        # Build tab content
        self.calendar_content = self.build_calendar_tab()
        self.day_selector_content = self.build_day_selector_tab()

        # Create tab buttons using the helper method
        self.tab_buttons = self._build_tab_buttons()

        # Content container that will be updated - default to Repeating (day_selector)
        self.tab_content_container = ft.Container(
            content=self.day_selector_content,  # Repeating is default
            padding=10,
        )

        # Main column
        return ft.Column(
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                labeled_input("Alarm Time", self.time_display),
                self.tab_buttons,
                self.tab_content_container,
            ],
        )

    def switch_tab(self, index):
        """Switch between tabs manually"""
        self.tabs_selected = index
        if index == 0:  # Repeating tab
            self.tab_content_container.content = self.day_selector_content
            self.is_repeating = True
        else:  # Specific Date tab (index 1)
            self.tab_content_container.content = self.calendar_content
            self.is_repeating = False

        # Rebuild tab buttons to update colors
        parent_column = self.content
        if parent_column and hasattr(parent_column, 'controls'):
            for i, control in enumerate(parent_column.controls):
                if control == self.tab_buttons:
                    self.tab_buttons = self._build_tab_buttons()
                    parent_column.controls[i] = self.tab_buttons
                    break

        if self._page:
            self._page.update()

    def build_calendar_tab(self):
        """Build the calendar view for specific date selection"""
        # Month navigation header
        month_name = calendar.month_name[self.current_month]
        self.month_label = ft.Text(
            f"{month_name} {self.current_year}",
            size=18,
            weight=ft.FontWeight.BOLD,
            color=black,
        )

        # Navigation buttons
        nav_row = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_size=24,
                    icon_color=primary,
                    on_click=lambda e: self.change_month(-1),
                ),
                self.month_label,
                ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD,
                    icon_size=24,
                    icon_color=primary,
                    on_click=lambda e: self.change_month(1),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Day labels
        day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        labels_row = ft.Row(
            [ft.Text(label, size=12, weight=ft.FontWeight.BOLD, expand=True,
                     text_align=ft.TextAlign.CENTER, color="#6B7280")
             for label in day_labels],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        )

        # Calendar grid
        self.calendar_grid = ft.Column(spacing=5)
        self.update_calendar_grid()

        return ft.Container(
            content=ft.Column(
                [
                    nav_row,
                    ft.Divider(height=10, color=soft_border),
                    labels_row,
                    ft.Divider(height=5, color=soft_border),
                    self.calendar_grid,
                ],
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=10,
        )

    def update_calendar_grid(self):
        """Update the calendar grid with current month's days"""
        if not self.calendar_grid:
            return

        self.calendar_grid.controls.clear()

        cal = calendar.monthcalendar(self.current_year, self.current_month)

        for week in cal:
            week_row = ft.Row(
                [],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
            )

            for day in week:
                if day == 0:
                    # Empty cell
                    week_row.controls.append(
                        ft.Container(expand=True, height=40)
                    )
                else:
                    # Check if this day is selected
                    is_selected = (day == self.selected_date.day and
                                   self.current_month == self.selected_date.month and
                                   self.current_year == self.selected_date.year)

                    day_container = ft.Container(
                        content=ft.Text(
                            str(day),
                            size=14,
                            color=white if is_selected else black,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        expand=True,
                        height=40,
                        alignment=ft.Alignment.CENTER,
                        bgcolor=primary if is_selected else "#F5F7FA",
                        border_radius=20,
                        on_click=lambda e, d=day: self.select_date(d),
                    )
                    week_row.controls.append(day_container)

            self.calendar_grid.controls.append(week_row)

        if self._page:
            self._page.update()

    def change_month(self, delta):
        """Change the displayed month by delta months"""
        new_month = self.current_month + delta
        new_year = self.current_year

        if new_month > 12:
            new_month = 1
            new_year += 1
        elif new_month < 1:
            new_month = 12
            new_year -= 1

        self.current_month = new_month
        self.current_year = new_year

        month_name = calendar.month_name[new_month]
        self.month_label.value = f"{month_name} {new_year}"
        self.update_calendar_grid()
        if self._page:
            self._page.update()

    def select_date(self, day):
        """Select a specific date in the calendar"""
        self.selected_date = date(self.current_year, self.current_month, day)
        self.is_repeating = False
        # Switch to Specific Date tab (index 1)
        self.switch_tab(1)
        self.update_calendar_grid()
        if self._page:
            self._page.update()

    def build_day_selector_tab(self):
        """Build the day of week selector (like Samsung clock)"""
        self.day_buttons = []

        day_row = ft.Row(
            [],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        )

        for i, day_name in enumerate(self.day_names):
            is_selected = i in self.selected_days
            day_btn = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            day_name,
                            size=12,
                            color=white if is_selected else black,
                        ),
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE if is_selected else ft.Icons.CIRCLE,
                            size=20,
                            color=white if is_selected else "#B0B8C4",
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                expand=True,
                height=60,
                padding=5,
                bgcolor=primary if is_selected else "#F5F7FA",
                border_radius=10,
                on_click=lambda e, index=i: self.toggle_day(index),
            )
            day_row.controls.append(day_btn)
            self.day_buttons.append(day_btn)

        # Quick selection buttons
        quick_row = ft.Row(
            [
                ft.Button(
                    "Weekdays",
                    on_click=lambda e: self.quick_select([0, 1, 2, 3, 4]),
                    style=ft.ButtonStyle(
                        bgcolor="#F5F7FA",
                        color=black,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
                ft.Button(
                    "Weekends",
                    on_click=lambda e: self.quick_select([5, 6]),
                    style=ft.ButtonStyle(
                        bgcolor="#F5F7FA",
                        color=black,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
                ft.Button(
                    "Every Day",
                    on_click=lambda e: self.quick_select([0, 1, 2, 3, 4, 5, 6]),
                    style=ft.ButtonStyle(
                        bgcolor="#F5F7FA",
                        color=black,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
                ft.Button(
                    "Clear",
                    on_click=lambda e: self.clear_days(),
                    style=ft.ButtonStyle(
                        bgcolor="#FEE2E2",
                        color="#DC2626",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
            wrap=True,
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Select days for repeating alarm",
                        size=14,
                        color="#6B7280",
                    ),
                    day_row,
                    ft.Divider(height=10, color=soft_border),
                    quick_row,
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=10,
        )

    def toggle_day(self, index):
        """Toggle selection of a specific day"""
        if index in self.selected_days:
            self.selected_days.remove(index)
        else:
            self.selected_days.append(index)
            self.selected_days.sort()

        self.is_repeating = True
        self.update_day_buttons()

    def quick_select(self, day_indices):
        """Quick select multiple days"""
        self.selected_days = day_indices.copy()
        self.is_repeating = True
        self.update_day_buttons()

    def clear_days(self):
        """Clear all selected days"""
        self.selected_days = []
        self.is_repeating = False
        self.update_day_buttons()

    def update_day_buttons(self):
        """Update the appearance of day buttons"""
        for i, btn in enumerate(self.day_buttons):
            is_selected = i in self.selected_days
            btn.bgcolor = primary if is_selected else "#F5F7FA"
            btn.content.controls[0].color = white if is_selected else black
            btn.content.controls[1] = ft.Icon(
                ft.Icons.CHECK_CIRCLE if is_selected else ft.Icons.CIRCLE,
                size=20,
                color=white if is_selected else "#B0B8C4",
            )

        if self._page:
            self._page.update()

    def on_time_change(self, e):
        """Handle time change from time picker"""
        if e.control.value:
            self.selected_time = e.control.value
            self.time_display.content.controls[1].value = self.selected_time.strftime("%I:%M %p")
            if self._page:
                self._page.update()

    def open_time_picker(self, e):
        """Open the time picker dialog"""
        self.time_picker.value = self.selected_time
        self._page.overlay.append(self.time_picker)
        self._page.update()
        self.time_picker.open = True
        self._page.update()

    def on_tab_change(self, e):
        """Handle tab change"""
        if e.control.selected_index == 0:
            self.is_repeating = False
        else:
            self.is_repeating = True

    def get_alarm_data(self):
        """Get the current alarm data as a dictionary"""
        return {
            'time': self.selected_time.strftime("%H:%M"),
            'time_12hr': self.selected_time.strftime("%I:%M %p"),
            'date': self.selected_date.strftime("%Y-%m-%d") if not self.is_repeating else None,
            'days': self.selected_days if self.is_repeating else [],
            'is_repeating': self.is_repeating,
            'day_names': [self.day_names[i] for i in self.selected_days] if self.is_repeating else []
        }


def taskboard_input_view(page: ft.Page) -> ft.View:
    async def go_taskboard(e):
        logger.info("Go to taskboard clicked")
        try:
            await page.push_route("/taskboard")  # CHANGED: go to taskboard instead of homepage
            logger.info("Route pushed")
        except Exception as e:
            logger.error(f"Error occurred: {e}")

    # back nav
    async def go_back(e):
        logger.info("Back from task input clicked")
        try:
            await page.push_route("/taskboard")  # CHANGED: go to taskboard instead of homepage
            logger.debug(f"Taskboard route pushed")
        except Exception as e:
            logger.error(f"Error occurred: {e}")

    # ---------- App bar (matches header_blue style used on Homepage/Settings) ----------
    appbar = ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=16),
        bgcolor=header_blue,
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=white,
                    on_click=go_back,
                ),
                ft.Text(
                    "Add Task",
                    color=white,
                    size=22,
                    weight=ft.FontWeight.W_800,
                ),
            ],
        ),
    )

    # ---------- Form field styling ----------
    field_border_radius = 12
    field_content_padding = ft.Padding.symmetric(horizontal=16, vertical=14)

    # Error text for validation
    error_text = ft.Text("", color=ft.Colors.RED_600, size=13, visible=False)

    # Success text for confirmation
    success_text = ft.Text("", color=ft.Colors.GREEN_600, size=13, visible=False)

    # Pet selection dropdown

    pet_list = get_pet_list()
    pet_selection = ft.Dropdown(
        hint_text="Select pet",
        width=340,
        border_radius=field_border_radius,
        border_color=soft_border,
        bgcolor=white,
        color=black,
        content_padding=field_content_padding,
        options=[

            # fill with pet profile info
            # get from crud
            ft.dropdown.Option(pet.get("name"))
            for pet in pet_list
            if pet.get("name")
        ],
    )

    task_name = ft.TextField(
        hint_text="e.g. Medication/Walks/Feeding",
        width=340,
        border_radius=field_border_radius,
        border_color=soft_border,
        bgcolor=white,
        color=black,
        content_padding=field_content_padding,
    )

    task_desc = ft.TextField(
        hint_text="e.g. Feed kibble/prescription meds (optional)",
        width=340,
        text_align=ft.TextAlign.START,
        border_radius=field_border_radius,
        border_color=soft_border,
        bgcolor=white,
        color=black,
        content_padding=field_content_padding,
    )

    # Alarm clock selector
    alarm_selector = AlarmClockSelector(page=page)

    # Function to save alarm data
    def save_alarm_data(alarm_data):
        logger.info(f"Alarm data collected: {alarm_data}")
        return alarm_data

    alarm_selector.on_alarm_saved = save_alarm_data

    # ---------- Avatar placeholder (visual anchor at the top of the form) ----------
    avatar_placeholder = ft.Container(
        width=90,
        height=90,
        bgcolor="#F1D9B0",
        border_radius=45,
        border=ft.Border.all(2, soft_border),
        alignment=ft.Alignment.CENTER,
        content=ft.Icon(ft.Icons.FORMAT_LIST_BULLETED_ROUNDED, size=44, color="#8A6A3B"),
    )

    # Resolve the current user's uid and mirror it into the local uid store,
    # so the model CRUD calls (task_crud / pet_crud) read the right Firestore
    # doc. This matches homepage.py's return_uid() pattern: after an OAuth
    # login the temp uid file may be empty (main.py clears it on startup), so
    # page.auth is the source of truth here.
    if page.auth is not None:
        current_user_id = str(page.auth.user["email"])
    else:
        current_user_id = UserIdStore().get()
    if current_user_id:
        UserIdStore().set(current_user_id)

    # Normal functions can't call async functions
    async def add_task(e):
        # Validate required fields
        if not task_name.value or not pet_selection.value:
            error_text.value = "Please enter a task name and select a pet."
            error_text.visible = True
            success_text.visible = False
            page.update()
            return

        # Validate alarm selection
        alarm_data = alarm_selector.get_alarm_data()
        if alarm_data['is_repeating'] and not alarm_data['days']:
            error_text.value = "Please select at least one day for repeating alarm."
            error_text.visible = True
            success_text.visible = False
            page.update()
            return

        error_text.visible = False

        # Prepare task data for Firebase

        try:
            # Add task to Firestore via the model CRUD
            saved = add_task_crud(
                task_name.value,
                pet_selection.value,
                task_desc.value or "",
                alarm_data,
                uid=current_user_id,
            )

            if not saved:
                # add_task only fails when no uid is set, i.e. not logged in
                error_text.value = "Could not save task: not signed in. Please log in again."
                error_text.visible = True
                page.update()
                return

            # Show success message
            success_text.value = "✅ Task created successfully with alarm!"
            success_text.visible = True

            # Clear form fields after successful submission
            task_name.value = ""
            pet_selection.value = None
            task_desc.value = ""

            page.update()

            # Navigate back to taskboard after delay
            await go_taskboard(e)  # CHANGED: go to taskboard instead of homepage

        except Exception as err:
            logger.error(f"Error adding task: {err}")
            error_text.value = f"Error saving task: {str(err)}"
            error_text.visible = True
            page.update()

    submit_btn = ft.Button(
        content=ft.Text("Save Task", size=16, weight=ft.FontWeight.W_700),
        width=340,
        height=54,
        on_click=add_task,
        color=white,
        bgcolor=primary,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=30),
        ),
    )

    form = ft.Container(
        margin=ft.Margin.only(left=16, right=16, top=24, bottom=16),
        content=ft.Column(
            spacing=18,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                avatar_placeholder,
                ft.Container(height=6),
                labeled_input("Selected Pet", pet_selection),
                labeled_input("Task Name", task_name),
                labeled_input("Description (Optional)", task_desc),
                ft.Divider(height=10, color=soft_border),
                ft.Text("Set Alarm", size=16, weight=ft.FontWeight.W_700, color=black),
                alarm_selector,
                error_text,
                success_text,
            ],
        ),
    )

    # Scrollable fields area, expands to fill remaining space above the button.
    scrollable_form = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[form],
    )

    # Bottom-anchored button bar, stays pinned below the scrollable fields.
    bottom_button_bar = ft.Container(
        padding=ft.Padding.only(left=16, right=16, top=12, bottom=24),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[submit_btn],
        ),
    )

    main_content = ft.Column(
        spacing=0,
        expand=True,
        controls=[
            appbar,
            scrollable_form,
            bottom_button_bar,
        ],
    )

    return ft.View(
        route="/petprofile_input",
        bgcolor=white,
        padding=0,
        spacing=0,
        controls=[main_content],
    )