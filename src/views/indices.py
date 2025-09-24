import flet as ft

def main_page(page: ft.Page):
    def go_home(e):
        page.go("/")
    page.add(
        ft.Column([
            ft.Text("Page Indices", size=30),
            ft.ElevatedButton("Retour à l'accueil", on_click=go_home)
        ])
    )