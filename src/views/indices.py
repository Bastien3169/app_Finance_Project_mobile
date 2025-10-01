import flet as ft

    # on_click = handler d'événement :  une propriété qui attend une fonction (callable).
    # Événement = ce qu'il se passe (ici le clic). 
    # Handler = la fonction qui gère cet événement (ex: go_home).
    # Handler = Callback spécifique à un événement utilisateur (souvent propre à une bibliothèque UI).
    # => Tout handler est un callback, mais tout callback n’est pas forcément un handler.

# Un handler doit forcément être une fonction (callable), qu’elle soit classique (réutilisable), anonyme (lambda), ou méthode de classe.


def main_page(page: ft.Page):
    def go_home(e):
        page.go("/")
        # On ne met pas de parenthèses : on passe la fonction elle-même, pas son résultat.
    page.add(ft.Column([
        ft.Text("Page Indices", size=30), 
        ft.ElevatedButton("Retour à l'accueil", on_click=go_home)
        ]))


def main_page(page: ft.Page):
    # Alternative avec lambda (fonction anonyme) pour le handler inline sans définir go_home au préalable.
    page.add(ft.Column([
        ft.Text("Page Indices", size=30), 
        ft.ElevatedButton("Retour à l'accueil", on_click= lambda e : page.go("/"))
        ]))







