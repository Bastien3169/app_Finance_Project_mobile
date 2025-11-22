import flet as ft
from src.components.components_views import *

couleur_titre_separateur = ft.Colors.PURPLE_200
couleur_bouton_fleche = ft.Colors.PURPLE_700

def main_page(page: ft.Page):
    page.clean()

    # --- Titre + séparation ---
    titre = titre_separateur("🏠 Accueil",couleur_titre_separateur)

    # Texte de bienvenue
    texte_bienvenu = ft.Container(content=ft.Text("Bienvenue sur Finance Facile !",
                                                weight=ft.FontWeight.BOLD,
                                                size=18,
                                                color="rgba(255,255,255,0.5)",
                                                text_align=ft.TextAlign.CENTER,),
                                        border=ft.border.all(0.5, "rgba(255,255,255,0.5)"),
                                        border_radius=10,
                                        padding=ft.padding.all(10),
                                        alignment=ft.alignment.center)

    #Texte explicatif application
    texte_explication = ft.Container(content=ft.Text("Cette application vous permet de comparer facilement différents actifs financiers et d’analyser " \
                                                "leurs performances historiques. \nElle simule deux stratégies d’investissement : le DCA (investissement progressif) et le Lump Sum "
                                                "(investissement en une seule fois), pour vous aider à visualiser laquelle est la plus adaptée à vos objectifs. \nElle n’a pas pour but de " \
                                                "vous inciter à investir, mais uniquement de proposer un outil pédagogique basé sur des données officielles passées.", 
                                                 color="rgba(255,255,255,0.5)", 
                                                 size=12, 
                                                 text_align=ft.TextAlign.JUSTIFY,),
                                padding=ft.padding.symmetric(vertical=10, horizontal=10),
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
        ("Inscription", ft.Colors.WHITE, "/inscription"),       # Bleu clair
        ("Mdp oublié", ft.Colors.WHITE, "/mdp_oublie"),       # Bleu clair
        ("Test", ft.Colors.CYAN_500, "/test"),       # Bleu clair
    ]

    # Widget : ligne de séparation dans un container pour avoir padding que en dessous
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre_separateur), padding=ft.padding.only(top=15,bottom=15))

    # Créer la liste de boutons avec une boucle normale
    buttons = []
    for name, color, route in tiles_button:
        btn = ft.ElevatedButton(
            content=ft.Text(name, size=12),# "content" accepte les widjets, pas juste du texte
            bgcolor=color,
            color=ft.Colors.BLACK,
            on_click=lambda e, r=route: page.go(r), # Utilisation de r=route pour capturer la route correcte au momment de l'itération
            width=105,
            height=55,
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
        padding=ft.padding.only(top=20)
    )
    
    page.add(*titre, texte_bienvenu, grid_avec_espace, separation, texte_explication,)

    page.update()

