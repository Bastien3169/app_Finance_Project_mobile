    # on_click = handler d'événement :  une propriété qui attend une fonction (callable).
    # Événement = ce qu'il se passe (ici le clic). 
    # Handler = la fonction qui gère cet événement (ex: go_home).
    # Handler = Callback spécifique à un événement utilisateur (souvent propre à une bibliothèque UI).
    # => Tout handler est un callback, mais tout callback n’est pas forcément un handler.

# Un handler doit forcément être une fonction (callable), qu’elle soit classique (réutilisable), anonyme (lambda), ou méthode de classe.

import flet as ft
from flet.plotly_chart import PlotlyChart
import plotly.graph_objects as go
from src.models.control_datas.connexion_db_datas import *
from src.components.components_views import *


# Connexion DB et récupération des données
datas_actifs = FinanceDatabaseIndice(db_path="data.db")
liste_actifs = datas_actifs.get_list_indices()
infos_actifs = datas_actifs.get_infos_indices()
actif_default = "S&P 500"

couleur_titre_separateur = ft.Colors.CYAN_200
couleur_bouton_fleche = ft.Colors.CYAN_400

################################## GRAPHIQUE #################################################
def create_graph_section(page):
    page.scroll = "auto"

    # fonction : titre + séparateur dans conteneur
    titre = titre_separateur(text = "📈 Coming soon !", padding_text_top = 0, couleur_titre_separateur = couleur_titre_separateur)

    return [titre]
################################### FONCTION PRINCIPALE ################################

def etf_page(page: ft.Page):
    page.clean()
    page.title = "Les ETFs"
    page.scroll = "auto"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK


    # Fonction Loader général
    loader_global = loader_globale(couleur_titre_separateur)
    page.add(loader_global)

    # Fonction bouton retour haut
    bouton_retour_haut=bout_ret_haut(couleur_bouton_fleche, handler = lambda e: page.go("/"))

    # Bouton retour acceuol en bas
    bouton_acceuil = bout_ret_acceuil(couleur_bouton_fleche, handler = lambda e: page.go("/"))

    # Suppression du loader
    loader_global.visible = False

    # Un seul page.add() avec tous les éléments avec décompression des listes grace à l'étoile *
    page.add(
        bouton_retour_haut,  # Bouton en haut à droite
        bouton_acceuil)  # Bouton en dernier
    
