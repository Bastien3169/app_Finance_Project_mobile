import flet as ft

def navigate_to(page: ft.Page, route: str):
    def handler(e):
        page.go(route)
    return handler

def main_page(page: ft.Page):
    page.clean()  # Nettoie la page avant d'afficher le contenu

    page.add(ft.Text("Bienvenue sur Finance facile !", size=24))

    # Liste des tuiles (nom, couleur, route)
    tiles = [
        ("Indices", ft.Colors.BLUE, "/indices"),
        ("Stocks", ft.Colors.GREEN, "/stocks"),
        ("ETFs", ft.Colors.ORANGE, "/etfs"),
        ("Cryptos", ft.Colors.PURPLE, "/cryptos"),
        ("DCA vs LP", ft.Colors.RED, "/dca_vs_lp"),
        ("MAJ BD", ft.Colors.CYAN, "/maj_bd"),
    ]

    rows = []

    for i in range(0, len(tiles), 3):
        row_tiles = tiles[i:i+3]
        row_buttons = []
        for name, color, route in row_tiles:
            btn = ft.ElevatedButton(text=name,bgcolor=color,on_click=navigate_to(page, route))  # fonction normale au lieu de lambda
            row_buttons.append(btn)
        rows.append(ft.Row(row_buttons, alignment=ft.MainAxisAlignment.CENTER))

    # Ajouter toutes les lignes à la page
    page.add(*rows)
