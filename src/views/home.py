import flet as ft


def main_page(page: ft.Page):
    page.clean()

    texte_bienvenu = ft.Text("Bienvenue sur Finance facile !", size=20)

    # Liste des tuiles
    tiles_button = [
        ("Indices", ft.Colors.AMBER_200, "/indices"),      # Jaune pastel
        ("Stocks", ft.Colors.GREEN_200, "/stocks"),       # Vert clair
        ("ETFs", ft.Colors.ORANGE_200, "/etfs"),         # Orange doux
        ("Cryptos", ft.Colors.PURPLE_200, "/cryptos"),   # Violet pastel
        ("DCAvsLP", ft.Colors.RED_200, "/dca_vs_lp"),  # Rouge doux
        ("MAJ BD", ft.Colors.CYAN_200, "/maj_bd"),       # Bleu clair
        ("TEST", ft.Colors.CYAN_500, "/test"),       # Bleu clair
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


'''
    # Disposer les boutons en grille 2x3
    row1 = ft.Row(controls=[buttons[0], buttons[1], buttons[2]], alignment=ft.MainAxisAlignment.CENTER)
    row2 = ft.Row(controls=[buttons[3], buttons[4], buttons[5]], alignment=ft.MainAxisAlignment.CENTER)

    page.add(texte_bienvenu, row1, row2)

'''