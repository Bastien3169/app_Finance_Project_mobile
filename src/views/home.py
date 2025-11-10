import flet as ft


def main_page(page: ft.Page):
    page.clean()

    texte_bienvenu = ft.Container(content=ft.Text("Bienvenue sur Finance Facile !", color=ft.Colors.TEAL_700, weight=ft.FontWeight.BOLD, size=22, text_align=ft.TextAlign.CENTER,),
                                  padding=ft.padding.symmetric(vertical=12, horizontal=20),
                                  border=ft.border.all(2, ft.Colors.TEAL_300),  # bordure fine et élégante
                                  border_radius=ft.border_radius.all(12),
                                  alignment=ft.alignment.center,)

    # Liste des tuiles
    tiles_button = [
        ("Indices",  "#7FB77E", "/indices"),      # Jaune pastel
        ("Stocks", ft.Colors.AMBER_200, "/stocks"),       # Vert clair
        ("ETFs", ft.Colors.CYAN_200, "/etfs"),         # Orange doux
        ("Cryptos", "#F7931A", "/cryptos"),     # Couleur Bitcoin
        ("Tous Actifs", "#6C8EBF", "/tous_actifs"),
        ("DCAvsLP", "#D67C7C", "/dca_vs_lp"),  # Rouge doux
        ("Admin", ft.Colors.BLUE_500, "/admin"),       # Bleu clair
        ("Auth manag", ft.Colors.BLUE_500, "/auth_manag"),       # Bleu clair
        ("Test", ft.Colors.CYAN_500, "/test"),       # Bleu clair
        ("Test2", "#4E6E81", "/test2"),       # Bleu 
    ]


    # Créer la liste de boutons avec une boucle normale
    buttons = []
    for name, color, route in tiles_button:
        btn = ft.ElevatedButton(
            content=ft.Text(name, size=12),# "content" accepte les widjets, pas juste du texte
            bgcolor=color,
            color=ft.Colors.BLACK,
            on_click=lambda e, r=route: page.go(r), # Utilisation de r=route pour capturer la route correcte au momment de l'itération
            width=100,
            height=50,
            )   
        buttons.append(btn)


    # Créer un Row centré qui contient tous les boutons
    centered_grid = ft.Row(
        controls=buttons,
        wrap=True,  # existe aussi "no_wrap" et "wrap_reverse"
        alignment=ft.MainAxisAlignment.CENTER,
        #vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
        run_spacing=10,
        expand=True
    )

    # Ajouter le padding en passant par un Container
    grid_avec_espace = ft.Container(
        content=centered_grid,
        padding=ft.padding.only(top=100)
    )
    
    page.add(texte_bienvenu, grid_avec_espace)

    page.update()

