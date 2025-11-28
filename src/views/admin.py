# src/views/admin_flet.py
import flet as ft
from src.models.users_db.models_db_users_test import AuthManager, AdminManager
from src.models.datas_db.main_db_datas import *  # Pour les updates BDD
from src.components.components_views import *

# Instanciations
auth_manager = AuthManager()
admin_manager = AdminManager()

# Couleurs et tailles
couleur_titre_separateur = "#D67C7C"
couleur_bouton = "#E89292"
taille_titre = 20

bouton_on_click = bouton_on_click

############################## FONCTION INTERACTIVE MAJ BDD ##############################

def add_update_database(page: ft.Page, dossier_csv: str, csv_bdd: str, db_path: str):
    
    # fonction : titre + séparateur dans conteneur
    titre =  titre_separateur("🔄 Mise à jour BDD datas", 
                              couleur_titre_separateur)


    # Création de la colonne pour les messages de suivi d'avancement
    messages = ft.Column(spacing=5)
    
    def on_click(e):
        messages.controls.clear()
        messages.controls.append(ft.Text("⏳ Début des étapes de maj 1/6...",color=ft.Colors.GREEN, size=12, weight="bold", text_align=ft.TextAlign.CENTER))
        progress_bar.value = 0.08
        loader.content.visible = True
        page.update()

        try:
            composition_indices.csv_indices(dossier_csv)
            messages.controls.append(ft.Text("✅ Étape 1/6 terminée - Scraping tickers et composition indices",color=ft.Colors.GREEN, size=12, weight="bold", text_align=ft.TextAlign.CENTER))
            progress_bar.value = 0.17
            page.update()

            infos_stocks.infos_stocks(dossier_csv, csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 2/6 terminée - Infos entreprises",color=ft.Colors.GREEN, size=12, weight="bold", text_align=ft.TextAlign.CENTER))
            progress_bar.value = 0.34
            page.update()

            infos_indices.infos_indices(dossier_csv, csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 3/6 terminée - Infos indices",color=ft.Colors.GREEN, size=12, weight="bold", text_align=ft.TextAlign.CENTER))
            progress_bar.value = 0.50
            page.update()

            hist_indices.recuperer_et_clean_indices(csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 4/6 terminée - Historique indices",color=ft.Colors.GREEN, size=12, weight="bold", text_align=ft.TextAlign.CENTER))
            progress_bar.value = 0.67
            page.update()

            hist_stocks.recuperer_et_clean_stocks(csv_bdd)
            messages.controls.append(ft.Text("✅ Étape 5/6 terminée - Historique entreprises",color=ft.Colors.GREEN, size=12, weight="bold", text_align=ft.TextAlign.CENTER))
            progress_bar.value = 0.83
            page.update()

            sql_datas.main_creation_db(csv_bdd, db_path)
            messages.controls.append(ft.Text("✅ Étape 6/6 terminée - Base de données enregistrée",color=ft.Colors.GREEN, size=12, weight="bold", text_align=ft.TextAlign.CENTER))
            progress_bar.value = 1.0
            page.update()

            loader.content.visible = False
            messages.controls.append(ft.Text("🎉 Base de données mise à jour avec succès !",weight=ft.FontWeight.BOLD,color=ft.Colors.GREEN,size=10))
            page.update()

        except Exception as ex:
            loader.visible = False
            messages.controls.append(ft.Text(f"❌ Erreur : {ex}", color=ft.Colors.RED, size=12, weight="bold", text_align=ft.TextAlign.CENTER))
            progress_bar.value = 0
            page.update()
    
    # Création du bouton de mise à jour
    bouton = bouton_on_click(text = "MAJ BDD datas",on_click=on_click, icon=ft.Icons.UPDATE, couleur_bouton=couleur_bouton)
    
    # Création du texte info
    info = ft.Text("La maj peut prendre entre 20 et 30 min", color=couleur_titre_separateur, size=12, weight="bold", text_align=ft.TextAlign.CENTER)

    # Création de la barre de progression stylée
    progress_bar = ft.Container(content=ft.ProgressBar(value=0, bgcolor=ft.Colors.GREY_800),
                                width=380, # on fait width et height du container pour styliser la barre pas le ProgressBar directement car lui il prend tout l'espace dispo
                                height=15,
                                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.CYAN_700),
                                border_radius=20,  # arrondi
                                padding=ft.padding.all(2),  # petit espace intérieur
                                border=ft.border.all(1, ft.Colors.WHITE30,))  # bord coloré

    # Création du conteneur loader
    loader = loader_page(couleur_titre_separateur)

    # fonction pour regroupement widger section
    contenu = contenu_widget(titre, [info, progress_bar, bouton, loader, messages])
    
    return [contenu]



#################################### GESTION UTILISATEURS ####################################

def users_admin_flet(page: ft.Page):
    
    # fonction : titre + séparateur dans conteneur
    titre =  titre_separateur("📝 Modifications BDD users", 
                              couleur_titre_separateur, 
                              padding_text_top = 35)
    
    # Sous-titre pour modification user
    sous_titre = ft.Text("Chercher un users", weight="bold", size=18, 
                                 text_align=ft.TextAlign.CENTER,
                                 style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE))
    
    # Création du conteneur pour le sous-titre
    sous_titre_contenair = ft.Container(content=sous_titre, alignment=ft.alignment.center, padding=ft.padding.only(top=35))


    # Fonction input pour recherche users
    search_field = periode_input(text_label="🔍 Rechercher par email ou username", hint_texte=None, hint_styl=None, passwords=None, oeil=None, widths=400, fonc_ajouter_periode=None)

    results_column = ft.Column()


    # Dictionnaire pour suivre l'état d'édition
    edit_state = {}

    # Création de la fonction de validation de recherche
    def validate_search(e):
        results_column.controls.clear()
        search = search_field.value.strip()
        if not search:
            results_column.controls.append(ft.Text("❗ Veuillez entrer un nom ou email.", size=12, weight="bold", text_align=ft.TextAlign.CENTER))
            page.update()
            return

        # Recherche utilisateur
        user = admin_manager.get_user_by_email_username(search)
        if not user:
            results_column.controls.append(ft.Text("⚠️ Aucun utilisateur trouvé.", color=ft.Colors.RED, size=12, weight="bold", text_align=ft.TextAlign.CENTER ))
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
                                                      width=150,
                                                      bgcolor=ft.Colors.CYAN_600,
                                                      color=ft.Colors.WHITE,
                                                      icon=ft.Icons.EDIT,
                                                      on_click=lambda ev, em=email: toggle_edit(ev, em)),
                                    ft.ElevatedButton("Supprimer",
                                                      width=150,
                                                      bgcolor=ft.Colors.RED_400,
                                                      color=ft.Colors.WHITE,
                                                      icon=ft.Icons.DELETE_OUTLINED,
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
                                        border=ft.border.all(1, ft.Colors.WHITE30),
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
        results_column.controls.append(ft.Text(f"✅ Utilisateur {username} supprimé.", size=12, weight="bold", text_align=ft.TextAlign.CENTER ))
        page.update()

    # Création de la fonction de bascule édition
    def toggle_edit(e, email):
        edit_state[email] = not edit_state.get(email, False)
        validate_search(None)

    # Création du formulaire d'édition
    def edit_form(user):
        id, username, email, role, registration_date = user

        new_username = ft.TextField(label="Nouveau nom d'utilisateur",
                                    label_style=ft.TextStyle(italic=True, size=12),
                                    value=username, 
                                    width=300,
                                    border_radius=8,
                                    border_color=ft.Colors.WHITE30,)

        new_role = ft.Dropdown(label="Nouveau rôle",
                               label_style=ft.TextStyle(italic=True,size=12),
                               options=[ft.dropdown.Option("admin"), ft.dropdown.Option("user")],
                               value=role,
                               width=300,
                               border_radius=8,
                               border_color=ft.Colors.WHITE30,)
        
        new_password = ft.TextField(label="Nouveau mot de passe",
                                    label_style=ft.TextStyle(italic=True,size=12), 
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
            results_column.controls.append(ft.Text(f"✅ Utilisateur {new_username.value} modifié avec succès.", size=12, weight="bold", text_align=ft.TextAlign.CENTER ))
            edit_state[email] = False
            page.update()

        # Texte de la card de modification 
        text_edition = ft.Column([ft.Container(ft.Text("✏️ Modification de l'utilisateur", 
                                                       weight=ft.FontWeight.BOLD, 
                                                       text_align=ft.TextAlign.CENTER, 
                                                       color=couleur_titre_separateur,size=15)),
                                  ft.Container(content=ft.Divider(height=2, color=couleur_titre_separateur),)],
                                spacing=2,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
        
        # Bouton valider les modifications
        bouton_valid_modif = ft.ElevatedButton("Valider les modifications", width=300, bgcolor=ft.Colors.CYAN_600, color=ft.Colors.WHITE, icon=ft.Icons.CHECK, on_click=submit_changes,)


        # Création de la card de modification
        card_modif_iser = ft.Container(bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.CYAN_100),
                            padding=20,
                            border_radius=8,
                            border=ft.border.all(2, ft.Colors.WHITE30),
                            alignment=ft.alignment.center,  # Centre le contenu dans le container
                            content=ft.Column([text_edition, new_username, new_role, new_password, bouton_valid_modif],
                                              spacing=10,
                                              horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Centre horizontalement les éléments
                                              alignment=ft.MainAxisAlignment.CENTER))  # Centre verticalement si le container est plus grand
        return card_modif_iser

    # Création du bouton valider
    bouton = bouton_on_click(text = "Rechercher",on_click=validate_search, icon=ft.Icons.SEARCH, couleur_bouton=couleur_bouton)

    # Regroupement widger section
    contenu = contenu_widget(titre, [sous_titre_contenair, search_field, bouton])

    return [contenu, results_column]

#################################### DATAFRAME USERS ####################################
def users_table_simple():

    # Sous-titre pour modification user
    sous_titre = ft.Text("Dataframe users", weight="bold", size=18, 
                                 text_align=ft.TextAlign.CENTER,
                                 style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE))
    
    # Création du conteneur pour le sous-titre
    sous_titre_contenair = ft.Container(content=sous_titre, alignment=ft.alignment.center)

    # Récupérer tous les users
    all_users = admin_manager.get_all_users()

    # Création du tableau
    users_table = ft.DataTable(
        column_spacing=10,
        heading_row_height=30,
        heading_row_color=ft.Colors.with_opacity(1.0, "#1A1C24"),
        data_row_min_height=25,
        divider_thickness=0.5,
        columns=[
            ft.DataColumn(ft.Text("ID", size=11)),
            ft.DataColumn(ft.Text("Username", size=11)),
            ft.DataColumn(ft.Text("Email", size=11)),
            ft.DataColumn(ft.Text("Rôle", size=11)),
            ft.DataColumn(ft.Text("Date inscription", size=11)),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(id), size=11)),
                    ft.DataCell(ft.Text(username, size=11)),
                    ft.DataCell(ft.Text(email, size=11)),
                    ft.DataCell(ft.Text(role, size=11)),
                    ft.DataCell(ft.Text(str(registration_date), size=11)),
                ]
            )
            for (id, username, email, role, registration_date) in all_users
        ],
    )

    # Optionnel : cadre scrollable (comme tes autres tableaux)
    cadre_table_users = ft.Container(content=ft.Column([users_table],
                                                       scroll=ft.ScrollMode.AUTO,),
                                    border=ft.border.all(2, couleur_titre_separateur),
                                    border_radius=10,
                                    padding=5,
                                    height=300,)

    contenu = ft.Column([sous_titre_contenair, cadre_table_users], 
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,)

    return [contenu]


#################################### AJOUT USER ####################################
def users_add_form(page: ft.Page):
    
    # Sous-titre pour modification user
    sous_titre = ft.Text("Ajouter users", weight="bold", size=18, 
                                 text_align=ft.TextAlign.CENTER,
                                 style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE))
    
    sous_titre_contenair = ft.Container(content=sous_titre, alignment=ft.alignment.center)
    
    # Champs du formulaire
    username_field = periode_input(text_label="👤 Username", hint_texte=None, hint_styl=None, passwords=None, oeil=None, widths=400, fonc_ajouter_periode=None)

    email_field = periode_input(text_label="📧 Email", hint_texte=None, hint_styl=None, passwords=None, oeil=None, widths=400, fonc_ajouter_periode=None)
    
    password_field = periode_input(text_label="🔑 Mot de passe", 
                                   hint_texte="Min 5 car., maj, min, chiffre, caractère spécial", 
                                   hint_styl=ft.TextStyle(size=10, italic=True,), 
                                   passwords=True, 
                                   oeil=True,
                                   widths=400,
                                   fonc_ajouter_periode=None)

    role_field = ft.Dropdown(label="🛡️ Rôle",
                            label_style=ft.TextStyle(decoration=ft.TextDecoration.UNDERLINE, size=16),
                            options=[ft.dropdown.Option("user"), ft.dropdown.Option("admin"),],
                            value="user",
                            width=400,
                            border_radius=8,
                            text_style=ft.TextStyle(size=11),
                            border_color=ft.Colors.WHITE30,
                            expand=True,)

    message_text = ft.Text(size=12, weight="bold", text_align=ft.TextAlign.CENTER, visible=False)

    # Action au clic sur "Créer l'utilisateur"
    def on_create_user(e):
        username = username_field.value.strip() # Enlève espace début et fin
        email = email_field.value.strip()
        password = password_field.value.strip()
        role = role_field.value

        # Vérif côté front
        if not username or not email or not password:
            message_text.value = "❌ Merci de remplir tous les champs."
            message_text.color = ft.Colors.RED
            message_text.visible = True
            page.update()
            return

        # Création via AuthManager (validation mail + mdp inclue)
        success, msg = auth_manager.register(username, email, password) # “J’appelle register(...), qui me renvoie 2 valeurs, et je les range dans deux variables : success et msg.”

        message_text.value = msg
        message_text.color = ft.Colors.GREEN if success else ft.Colors.RED
        message_text.visible = True
        page.update()

        if not success:
            return

        # Si succès et rôle différent de 'user', on met à jour via AdminManager
        if role != "user":
            admin_manager.update_user(email=email, role=role)

        # Optionnel : vider les champs après succès
        username_field.value = ""
        email_field.value = ""
        password_field.value = ""
        role_field.value = "user"
        page.update()

    # Bouton de création
    bouton = bouton_on_click(text = "Ajouter",on_click=on_create_user, icon=ft.Icons.PERSON_ADD, couleur_bouton=couleur_bouton)

    # Card globale du formulaire
    form_container = ft.Container(padding=ft.padding.only(top=20, bottom=0),
                                  content=ft.Column([sous_titre_contenair,
                                                    username_field,
                                                    email_field,
                                                    password_field,
                                                    role_field,
                                                    bouton,
                                                    message_text,],
                                                    spacing=10,
                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,),)

    return form_container

 
#################################### PAGE ADMIN PRINCIPALE ####################################

def admin_flet(page: ft.Page):
    page.title = "🏛️ Administration"
    page.scroll = "adaptive"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    # Section mise à jour BDD
    maj_datas_bdd = add_update_database(page, dossier_csv="csv", csv_bdd="csv/csv_bdd", db_path="datas.bd")

    # Section gestion utilisateurs
    maj_userss_bdd = users_admin_flet(page)
    contenu = maj_userss_bdd[0]  # ton "contenu_widget" qui contient sous_titre, search_field, bouton
    results_column = maj_userss_bdd[1]  # la colonne où tu mets les résultats

    # Pour récupérer les widgets à l'intérieur de contenu :
    contenu_controls = contenu.controls  # liste des widgets à l'intérieur du Column

    titre = contenu_controls[0]        # sous_titre_contenair
    trait_titre = contenu_controls[1]       # search_field
    search_bout_val = contenu_controls[2]     # bouton "Rechercher"


    # Dataframe users
    dataframe_users = users_table_simple()

    # Ajout user
    ajout_user = users_add_form(page)

    # Création bouton retour accueil
    bouton_retour = bout_ret_acceuil(couleur_titre_separateur, handler = lambda e: page.go("/"))

    # Ajout de tout à la page
    page.add(*maj_datas_bdd,titre, trait_titre, *dataframe_users, search_bout_val, results_column, ajout_user, bouton_retour)
    page.update()