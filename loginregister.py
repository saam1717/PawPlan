from enum import nonmember

import flet as ft

def main(page: ft.Page):
    page.title = "PawPlan"

    # STARTUP PAGE TOP
    def startup_top():
        return ft.Column(
            [
                ft.Text("PawPlan", size=28, weight=ft.FontWeight.BOLD),
                ft.TextButton("Log out", on_click=lambda e: page.go("/"))
            ],

            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # LOGIN SCREEN
    def login_screen():
        back_btn = ft.TextButton("Back", on_click=lambda e: page.go("/"))
        username = ft.TextField(label="Username", width=300)
        password = ft.TextField(label="Password", password=True, width=300)
        login_btn = ft.Button("Log In", width=150, on_click=lambda e: page.go("/homepage"))
        register_link = ft.TextButton("Not registered yet?", on_click=lambda e: page.go("/register"))

        return ft.Column(
            [
                ft.Row([back_btn], alignment=ft.MainAxisAlignment.START),
                ft.Text("Login", size=24, weight=ft.FontWeight.BOLD),
                username,
                password,
                register_link,
                login_btn,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # REGISTER SCREEN
    def register_screen():
        back_btn = ft.TextButton("Back", on_click=lambda e: page.go("/"))
        username = ft.TextField(label="Username", width=300)
        fullname = ft.TextField(label="Full Name", width=300)
        gender = ft.Row(
            [
                ft.Row([back_btn], alignment=ft.MainAxisAlignment.START),
                ft.Text("Gender:"),
                ft.Button("Male", width=80),
                ft.Button("Female", width=80),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        dob = ft.Row(
            [
                ft.TextField(label="MM", width=70),
                ft.TextField(label="DD", width=70),
                ft.TextField(label="YYYY", width=100),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        password = ft.TextField(label="Password", password=True, width=300)
        create_btn = ft.Button("Create Account", width=180, on_click=lambda e: page.go("/homepage"))
        back_btn = ft.TextButton("Back to Login", on_click=lambda e: page.go("/login"))

        return ft.Column(
            [
                ft.Text("Register", size=24, weight=ft.FontWeight.BOLD),
                username,
                fullname,
                gender,
                ft.Text("Date of birth:"),
                dob,
                password,
                create_btn,
                back_btn
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # NAVIGATION HANDLING
    def navigate(e):
        page.views.clear()

        # STARTUP PAGE
        if page.route == "/":
            paw_text = ft.Text("Paw", size=32, weight=ft.FontWeight.BOLD)
            plan_text = ft.Text("Plan", size=32, weight=ft.FontWeight.BOLD)
            title_row = ft.Row([paw_text, plan_text], alignment=ft.MainAxisAlignment.CENTER)

            login_btn = ft.Button("Login", on_click=lambda e: page.go("/login"))
            signup_btn = ft.Button("Sign Up", on_click=lambda e: page.go("/register"))
            button_row = ft.Row([login_btn, signup_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

            divider = ft.Column([
                ft.Divider(thickness=1),
                ft.Text("Or Continue with"),
                ft.Divider(thickness=1)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

            google_btn = ft.Button("Sign in with Google", width=250)

            page.views.append(
                ft.View(
                    route="/",
                    controls=[
                        ft.Column([
                            title_row,
                            ft.Container(height=20),
                            button_row,
                            ft.Container(height=20),
                            divider,
                            ft.Container(height=20),
                            google_btn
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )


        elif page.route == "/homepage":
            page.views.append(
                ft.View(
                    route = "/homepage",
                    controls = [startup_top()],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        elif page.route == "/login":
            page.views.append(
                ft.View(
                    route = "/login",
                    controls = [login_screen()],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        elif page.route == "/register":
            page.views.append(
                ft.View(
                    route = "/register",
                    controls = [register_screen()],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )

        page.update()


    # Commented code below causes page to not load
    page.on_route_change = navigate
    navigate(None)
    # page.push_route("/")

ft.run(main)
