# src/views/admin_flet.py
import flet as ft
from src.models.users_db.models_db_users_test import AuthManager, AdminManager
from src.models.datas_db.main_db_datas import *  # Pour les updates BDD

# Instanciations
auth_manager = AuthManager()
admin_manager = AdminManager()

# Couleurs et tailles
couleur_titre = ft.Colors.CYAN_200
couleur_bouton = ft.Colors.CYAN_600
taille_titre = 20


############################### FONCTIONS POUR LES TITRES ##############################

def data_maj_widgets():
    titre = ft.Text("🔄 Mise à jour BDD datas", color=couleur_titre, weight=ft.FontWeight.BOLD, size=taille_titre)
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre), padding=ft.padding.only(bottom=15))
    return [titre, separation]

def users_maj_widgets():
    titre = ft.Text("📝 Modifications BDD users", color=couleur_titre, weight=ft.FontWeight.BOLD, size=taille_titre)
    separation = ft.Container(content=ft.Divider(thickness=2, color=couleur_titre), padding=ft.padding.only(bottom=15))
    return [titre, separation]

############################## FONCTION INTERACTIVE MAJ BDD ##############################

def add_update_database(page: ft.Page, dossier_csv: str, csv_bdd: str, db_path: str):
    
    # Création de la colonne pour les messages de suivi d'avancement
    messages = ft.Column(spacing=5)
    
    def on_click(e):
        messages.controls.clear()
        messages.controls.append(ft.Text("⏳ Début des étapes de maj 1/6..."))
        progress_bar.value = 0.08
        loader.content.visible = True
        page.update()

        try:
            composition_indices.csv_indices(dossier_csv)
            messages.controls.append(ft.Text("✅ Étape 1/6 terminée - Scraping tickers et composition indices"))
            progress_bar.value = 0.17
            page.update()

            infos_stocks.infos_stocks(dossier_csv, csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 2/6 terminée - Infos entreprises"))
            progress_bar.value = 0.34
            page.update()

            infos_indices.infos_indices(dossier_csv, csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 3/6 terminée - Infos indices"))
            progress_bar.value = 0.50
            page.update()

            hist_indices.recuperer_et_clean_indices(csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 4/6 terminée - Historique indices"))
            progress_bar.value = 0.67
            page.update()

            hist_stocks.recuperer_et_clean_stocks(csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 5/6 terminée - Historique entreprises"))
            progress_bar.value = 0.83
            page.update()

            sql_datas.main_creation_db(csv_bdd, db_path)
            messages.controls.append(ft.Text("✅ Étape 6/6 terminée - Base de données enregistrée"))
            progress_bar.value = 1.0
            page.update()

            loader.content.visible = False
            messages.controls.append(ft.Text("🎉 Base de données mise à jour avec succès !",weight=ft.FontWeight.BOLD,color=ft.Colors.GREEN,size=10))
            page.update()

        except Exception as ex:
            loader.visible = False
            messages.controls.append(ft.Text(f"❌ Erreur : {ex}", color=ft.Colors.RED))
            progress_bar.value = 0
            page.update()
    
    # Création du bouton de mise à jour
    bouton = ft.ElevatedButton("Cliquez pour la maj de la BDD datas",
                               on_click=on_click,
                               style=ft.ButtonStyle(bgcolor=couleur_bouton, color=ft.Colors.WHITE, padding=ft.padding.symmetric(20, 15)),
                               width=400,)
    
    # Création du texte info
    info = ft.Text("La maj peut prendre entre 20 et 30 min", size=10)

    # Création de la barre de progression stylée
    progress_bar = ft.Container(content=ft.ProgressBar(value=0, bgcolor=ft.Colors.GREY_800),
                                width=380, # on fait width et height du container pour styliser la barre pas le ProgressBar directement car lui il prend tout l'espace dispo
                                height=15,
                                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.CYAN_700),
                                border_radius=20,  # arrondi
                                padding=ft.padding.all(2),  # petit espace intérieur
                                border=ft.border.all(1, ft.Colors.WHITE30,),  # bord coloré
                                margin=ft.margin.only(top = 10, bottom=40),)

    # Création du conteneur loader
    loader = ft.Container(content=ft.ProgressRing(color=ft.Colors.CYAN_400, width=25, height=25),
                          padding=ft.padding.symmetric(vertical=15), 
                          alignment=ft.alignment.center,
                          visible=False,)
    

    return [bouton, info, loader, progress_bar, messages]


#################################### GESTION UTILISATEURS ####################################

def users_admin_flet(page: ft.Page):
    search_field = ft.TextField(label="🔍 Rechercher par email ou username", 
                                label_style=ft.TextStyle(size=12, italic=True),
                                width=400, 
                                #border_color=ft.Colors.CYAN_400,
                                border_radius=8,
                                border_color=ft.Colors.WHITE30,)
    
    results_column = ft.Column(spacing=15)

    # Dictionnaire pour suivre l'état d'édition
    edit_state = {}

    # Création de la fonction de validation de recherche
    def validate_search(e):
        results_column.controls.clear()
        search = search_field.value.strip()
        if not search:
            results_column.controls.append(ft.Text("❗ Veuillez entrer un nom ou email."))
            page.update()
            return

        # Recherche utilisateur
        user = admin_manager.get_user_by_email_username(search)
        if not user:
            results_column.controls.append(ft.Text("⚠️ Aucun utilisateur trouvé.", color=ft.Colors.RED))
            page.update()
            return

        id, username, email, role, registration_date = user

        # Fiche utilisateur sous forme de colonne
        fiche = ft.Column([ft.Row([ft.Text("🆔 ID : ", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                                   ft.Text(f"{id}")]),
                            ft.Row([ft.Text("👤 Username : ", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                                    ft.Text(f"{username}")]),
                            ft.Row([ft.Text("📧 Email : ", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                                    ft.Text(f"{email}")]),
                            ft.Row([ft.Text("🔐 Rôle : ", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                                    ft.Text(f"{role}")]),
                            ft.Row([ft.Text("🗓️ Date inscription : ", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                                    ft.Text(f"{registration_date}")]),
                            ft.Divider(height=1, color=ft.Colors.GREY_300),
                            ft.Row([ft.ElevatedButton("Modifier",
                                                      width=100,
                                                      bgcolor=ft.Colors.CYAN_600,
                                                      color=ft.Colors.WHITE,
                                                      on_click=lambda ev, em=email: toggle_edit(ev, em)),
                                    ft.ElevatedButton("Supprimer",
                                                      width=100,
                                                      bgcolor=ft.Colors.RED_400,
                                                      color=ft.Colors.WHITE,
                                                      on_click=lambda ev, em=email, un=username: delete_user(ev, em, un)),], 
                            spacing=10,
                            alignment=ft.MainAxisAlignment.CENTER)], 
                        spacing=8, 
                        alignment=ft.MainAxisAlignment.START)


        # Encadré visuel de la fiche
        fiche_container = ft.Container(content=fiche,
                                        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.CYAN_100),
                                        border_radius=10,
                                        padding=15,
                                        margin=ft.margin.symmetric(vertical=10))

        # Affichage de la fiche user
        results_column.controls.append(fiche_container)

        # Si édition active : formulaire
        if edit_state.get(email, False):
            results_column.controls.append(edit_form(user))

        page.update()


    # Création de la fonction de suppression
    def delete_user(e, email, username):
        admin_manager.delete_user(email)
        results_column.controls.append(ft.Text(f"✅ Utilisateur {username} supprimé."))
        page.update()

    # Création de la fonction de bascule édition
    def toggle_edit(e, email):
        edit_state[email] = not edit_state.get(email, False)
        validate_search(None)

    # Création du formulaire d'édition
    def edit_form(user):
        id, username, email, role, registration_date = user

        new_username = ft.TextField(label="Nouveau nom d'utilisateur", 
                                    value=username, 
                                    width=300,
                                    border_radius=8,
                                    border_color=ft.Colors.WHITE30,)
        new_role = ft.Dropdown(label="Nouveau rôle",
                               options=[ft.dropdown.Option("admin"), ft.dropdown.Option("user")],
                               value=role,
                               width=300,
                               border_radius=8,
                               border_color=ft.Colors.WHITE30,)
        new_password = ft.TextField(label="Nouveau mot de passe", 
                                    hint_text="Ex : 1234",
                                    width=300,
                                    password=True,
                                    can_reveal_password=True,
                                    border_radius=8,
                                    border_color=ft.Colors.WHITE30,) # Affiche une icône pour révéler le mdp)

        # Création de la fonction de soumission des modifications
        def submit_changes(e):
            admin_manager.update_user(email=email, 
                                      username=new_username.value, 
                                      role=new_role.value, 
                                      password=new_password.value if new_password.value else None) # Met à jour seulement si un mot de passe est fourni pour éviter de le réinitialiser par une chaine "" vide 
            results_column.controls.append(ft.Text(f"✅ Utilisateur {new_username.value} modifié avec succès."))
            edit_state[email] = False
            page.update()

        # Texte de la card de modification 
        text_edition = text_edition = ft.Column([ft.Container(
                                                    ft.Text("✏️ Modification de l'utilisateur", 
                                                            weight=ft.FontWeight.BOLD, 
                                                            text_align=ft.TextAlign.CENTER, 
                                                            color=couleur_titre,
                                                            size=15)),
                                                
                                                ft.Container(
                                                    content=ft.Divider(height=2, color=couleur_titre),)],
                                                spacing=2)
    
        
        # Bouton valider les modifications
        bouton_valid_modif = ft.ElevatedButton("Valider les modifications", bgcolor=ft.Colors.CYAN_600, color=ft.Colors.WHITE, on_click=submit_changes,)

        # Création de la card de modification
        card_modif_iser = ft.Container(bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.CYAN_100),
                            padding=20,
                            alignment=ft.alignment.center,  # Centre le contenu dans le container
                            content=ft.Column([text_edition, new_username, new_role, new_password, bouton_valid_modif],
                                              spacing=10,
                                              horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centre horizontalement les éléments
                                              alignment=ft.MainAxisAlignment.CENTER))  # Centre verticalement si le container est plus grand
        return card_modif_iser

    # Création du bouton valider
    validate_button = ft.ElevatedButton("Valider",
                                        height=40,
                                        width=400,
                                        icon=ft.Icons.SEARCH,
                                        bgcolor=couleur_bouton,
                                        color=ft.Colors.WHITE,
                                        on_click=validate_search,)


    return ft.Column([ft.Column([search_field, validate_button], 
                                spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                      results_column,],
                      spacing=20,
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,)


#################################### PAGE ADMIN PRINCIPALE ####################################

def admin_flet(page: ft.Page):
    page.title = "🏛️ Administration"
    page.scroll = "adaptive"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK


    # Création flèche retour
    fleche_retour = ft.IconButton(icon=ft.Icons.ARROW_BACK,
                                  icon_color=ft.Colors.CYAN_900,
                                  tooltip="Retour accueil",
                                  on_click=lambda e: page.go("/"))

    container_fleche = ft.Container(content=ft.Row([fleche_retour], alignment=ft.MainAxisAlignment.START), height=30)


    # Section mise à jour BDD
    widget_datas_bdd = data_maj_widgets()
    maj_datas_bdd = add_update_database(page, dossier_csv="csv", csv_bdd="csv/csv_bdd", db_path="datas.bd")


    # Section gestion utilisateurs
    widget_users_bdd = users_maj_widgets()
    maj_userss_bdd = users_admin_flet(page)


    # Création bouton retour accueil
    bouton_retour = ft.ElevatedButton("Retour accueil",
                                      icon=ft.Icons.HOME,
                                      bgcolor=ft.Colors.CYAN_900,
                                      style=ft.ButtonStyle(color=ft.Colors.WHITE, padding=ft.padding.symmetric(20, 15)),
                                      on_click=lambda e: page.go("/"))

    container_bouton = ft.Container(content=bouton_retour,
                                    alignment=ft.alignment.center,
                                    padding=ft.padding.only(top=30, bottom=20),)


    # Ajout de tout à la page
    page.add(container_fleche, *widget_datas_bdd, *maj_datas_bdd, *widget_users_bdd, maj_userss_bdd, container_bouton)
    page.update()