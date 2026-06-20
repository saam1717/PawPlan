import flet as ft

def main(page: ft.Page):
    page.title = "PawPlan"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    paw_text = ft.Text("Paw", size=32, weight=ft.FontWeight.BOLD)
    plan_text = ft.Text("Plan", size=32, weight=ft.FontWeight.BOLD)
    title_row = ft.Row([paw_text, plan_text], alignment=ft.MainAxisAlignment.CENTER)

    login_btn = ft.Container(
        content=ft.ElevatedButton(text="Login"),
        width=200,
        height=50
    )
    signup_btn = ft.Container(
        content=ft.ElevatedButton(text="Sign Up"),
        width=200,
        height=50
    )
    button_row = ft.Row([login_btn, signup_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    divider = ft.Column([
        ft.Divider(thickness=1),
        ft.Text("Or Continue with"),
        ft.Divider(thickness=1)
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    google_btn = ft.Container(
        content=ft.ElevatedButton(text="Sign in with Google"),
        width=250,
        height=50
    )

    page.add(
        ft.Column([
            title_row,
            ft.Container(height=20),
            button_row,
            ft.Container(height=20),
            divider,
            ft.Container(height=20),
            google_btn
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)
