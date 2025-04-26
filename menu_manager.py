from PyQt5.QtWidgets import QAction, QMenu, QMessageBox
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl, Qt
import requests
import json

class MenuManager:
    def __init__(self, parent):
        """Initialize the menu manager with a parent (main window)"""
        self.parent = parent
        self.menubar = None
    
    def create_menu(self):
        """Create and return the application menu bar with logically organized menus"""
        # Create menu bar
        self.menubar = self.parent.menuBar()
        
        # Create all menus
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_tools_menu()
        self.create_templates_menu()
        self._create_settings_menu()
        self._create_help_menu()
        
        return self.menubar
    
    def _create_file_menu(self):
        """Create the File menu with all file operations"""
        file_menu = self.menubar.addMenu("Fichier")
        
        # New file action
        new_action = QAction("Nouveau", self.parent)
        
        new_action.triggered.connect(self.parent.new_file)
        file_menu.addAction(new_action)
        
        # Open file action
        open_action = QAction("Ouvrir", self.parent)
        
        open_action.triggered.connect(self.parent.open_file)
        file_menu.addAction(open_action)
        
        # Save actions
        save_action = QAction("Enregistrer", self.parent)
        
        save_action.triggered.connect(self.parent.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Enregistrer sous", self.parent)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.parent.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Print action
        print_action = QAction("Imprimer code", self.parent)
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self.parent.print_code)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()
        
        # Check for updates action
        check_update_action = QAction("Vérifier les mises à jour", self.parent)
        check_update_action.triggered.connect(self.check_for_updates)
        file_menu.addAction(check_update_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Quitter", self.parent)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.parent.close)
        file_menu.addAction(exit_action)
    
    def _create_edit_menu(self):
        """Create the Edit menu with all editing operations"""
        edit_menu = self.menubar.addMenu("Édition")
        
        # Basic editing operations
        cut_action = QAction("Couper", self.parent)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(lambda: self.parent.editor.cut())
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Copier", self.parent)
        
        copy_action.triggered.connect(lambda: self.parent.editor.copy())
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Coller", self.parent)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(lambda: self.parent.editor.paste())
        edit_menu.addAction(paste_action)
        
        # Undo/Redo operations
        edit_menu.addSeparator()
        
        undo_action = QAction("Annuler", self.parent)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.parent.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Rétablir", self.parent)
        redo_action.setShortcut("Ctrl+Y") 
        redo_action.triggered.connect(self.parent.editor.redo)
        edit_menu.addAction(redo_action)
        
        # Font size submenu
        edit_menu.addSeparator()
        font_menu = edit_menu.addMenu("Taille de police")
        
        increase_font_action = QAction("Augmenter", self.parent)
        increase_font_action.setShortcut("Ctrl++")
        increase_font_action.triggered.connect(self.parent.increase_font_size)
        font_menu.addAction(increase_font_action)
        
        decrease_font_action = QAction("Diminuer", self.parent)
        decrease_font_action.setShortcut("Ctrl+-")
        decrease_font_action.triggered.connect(self.parent.decrease_font_size)
        font_menu.addAction(decrease_font_action)
    
    def _create_view_menu(self):
        """Create the View menu with display options"""
        view_menu = self.menubar.addMenu("Affichage")
        
        show_python_action = QAction("Afficher le code Python", self.parent)
        show_python_action.triggered.connect(self.parent.show_python_code)
        view_menu.addAction(show_python_action)
    
    def _create_tools_menu(self):
        """Create the Tools menu with compilation and execution options"""
        tools_menu = self.menubar.addMenu("Outils")
        
        compile_action = QAction("Compiler", self.parent)
        
        compile_action.triggered.connect(self.parent.compile_algorithm)
        tools_menu.addAction(compile_action)
        
        run_action = QAction("Exécuter", self.parent)
        
        run_action.triggered.connect(self.parent.run_algorithm)
        tools_menu.addAction(run_action)
    
    def create_templates_menu(self):
        """Create the Templates menu with available code templates"""
        templates_menu = self.menubar.addMenu("Templates")
        
        # Basic template - Easiest
        template_action = QAction("Template vide", self.parent)
        template_action.triggered.connect(self.parent.insert_template)
        templates_menu.addAction(template_action)
        
        # Easy algorithms
        template_afficher_action = QAction("Afficher nombres", self.parent)
        template_afficher_action.triggered.connect(self.parent.insert_afficher_template)
        templates_menu.addAction(template_afficher_action)
        
        template_somme10_action = QAction("Somme de 10 nombres", self.parent)
        template_somme10_action.triggered.connect(self.parent.insert_somme10_template)
        templates_menu.addAction(template_somme10_action)
        
        template_pairs_action = QAction("Nombres pairs", self.parent)
        template_pairs_action.triggered.connect(self.parent.insert_pairs_template)
        templates_menu.addAction(template_pairs_action)
        
        template_impairs_action = QAction("Nombres impairs", self.parent)
        template_impairs_action.triggered.connect(self.parent.insert_impairs_template)
        templates_menu.addAction(template_impairs_action)
        
        # Medium algorithms
        template_moyenne_action = QAction("Calcul de moyenne", self.parent)
        template_moyenne_action.triggered.connect(self.parent.insert_moyenne_template)
        templates_menu.addAction(template_moyenne_action)
        
        template_sommeN_action = QAction("Somme de N nombres", self.parent)
        template_sommeN_action.triggered.connect(self.parent.insert_sommeN_template)
        templates_menu.addAction(template_sommeN_action)
        
        template_table_action = QAction("Table de multiplication", self.parent)
        template_table_action.triggered.connect(self.parent.insert_table_template)
        templates_menu.addAction(template_table_action)
        
        template_cercle_action = QAction("Calcul cercle", self.parent)
        template_cercle_action.triggered.connect(self.parent.insert_cercle_template)
        templates_menu.addAction(template_cercle_action)
        
        # More advanced algorithms
        template_max_action = QAction("Recherche du maximum", self.parent)
        template_max_action.triggered.connect(self.parent.insert_max_template)
        templates_menu.addAction(template_max_action)
        
        template_eq1_action = QAction("Équation premier degré", self.parent)
        template_eq1_action.triggered.connect(self.parent.insert_eq1_template)
        templates_menu.addAction(template_eq1_action)
        
        
        template_eq1_action = QAction("Nombre decimal vers binaire", self.parent)
        template_eq1_action.triggered.connect(self.parent.insert_decimalversbinaire)
        templates_menu.addAction(template_eq1_action)
        
        # Most complex algorithms
        template_pgcd_action = QAction("Calcul PGCD", self.parent)
        template_pgcd_action.triggered.connect(self.parent.insert_pgcd_template)
        templates_menu.addAction(template_pgcd_action)
        
        template_ppcm_action = QAction("Calcul PPCM", self.parent)
        template_ppcm_action.triggered.connect(self.parent.insert_ppcm_template)
        templates_menu.addAction(template_ppcm_action)
        
        template_eq2_action = QAction("Équation second degré", self.parent)
        template_eq2_action.triggered.connect(self.parent.insert_eq2_template)
        templates_menu.addAction(template_eq2_action)
    
    def _create_settings_menu(self):
        """Create the Settings menu with application preferences"""
        settings_menu = self.menubar.addMenu("Paramètres")
        
        preferences_action = QAction("Préférences", self.parent)
        preferences_action.triggered.connect(self.parent.show_settings_dialog)
        settings_menu.addAction(preferences_action)
    
    def _create_help_menu(self):
        """Create the Help menu with documentation and about information"""
        help_menu = self.menubar.addMenu("Aide")
        
        about_action = QAction("À propos", self.parent)
        about_action.triggered.connect(self.parent.show_about)
        help_menu.addAction(about_action)
        
        syntax_action = QAction("Syntaxe", self.parent)
        syntax_action.triggered.connect(self.parent.show_syntax_help)
        help_menu.addAction(syntax_action)
    
    def check_for_updates(self):
        """Vérifier les mises à jour disponibles sur GitHub"""
        try:
            # Version actuelle de l'application (à définir dans le fichier principal)
            current_version = self.parent.app_version
            
            # URL du fichier de version sur GitHub (à adapter à votre dépôt)
            github_version_url = "https://raw.githubusercontent.com/faridfgx/algofxupdate/main/version.json"
            
            # Télécharger les informations de version
            response = requests.get(github_version_url, timeout=5)
            if response.status_code == 200:
                version_data = json.loads(response.text)
                latest_version = version_data.get("version")
                download_url = version_data.get("download_url")
                release_notes = version_data.get("notes", "Pas de notes de mise à jour disponibles.")
                
                # Formater les notes de version selon le type reçu (chaîne ou liste)
                if isinstance(release_notes, list):
                    formatted_notes = "• " + "\n• ".join(release_notes)
                else:
                    # Si c'est une chaîne, on remplace les virgules par des sauts de ligne avec puces
                    formatted_notes = "• " + release_notes.replace(", ", "\n• ")
                
                # Comparer les versions (simplement par comparaison de chaînes)
                if latest_version and current_version < latest_version:
                    # Créer la boîte de dialogue pour informer l'utilisateur
                    msg_box = QMessageBox(self.parent)
                    msg_box.setWindowTitle("Mise à jour disponible")
                    msg_box.setText(f"Une nouvelle version ({latest_version}) est disponible.\nVotre version actuelle est {current_version}.")
                    
                    # Préparer le texte informatif avec les notes de version
                    info_text = f"Nouveautés dans cette version:\n\n{formatted_notes}\n\nVoulez-vous télécharger la mise à jour ?"
                    msg_box.setInformativeText(info_text)
                    msg_box.setIcon(QMessageBox.Information)
                    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    msg_box.setDefaultButton(QMessageBox.Yes)
                    
                    # Ajuster la taille de la boîte de dialogue pour afficher plus de texte
                    msg_box.setMinimumWidth(500)
                    
                    # Rendre la boîte de dialogue redimensionnable pour de longues listes de notes
                    msg_box.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    
                    # Si l'utilisateur clique sur Oui, ouvrir l'URL de téléchargement
                    if msg_box.exec_() == QMessageBox.Yes and download_url:
                        QDesktopServices.openUrl(QUrl(download_url))
                else:
                    # Informer l'utilisateur qu'il possède déjà la dernière version
                    QMessageBox.information(self.parent, "Mise à jour", 
                                            "Vous possédez déjà la dernière version de l'application.",
                                            QMessageBox.Ok)
            else:
                # Gérer les erreurs HTTP
                QMessageBox.warning(self.parent, "Erreur de vérification", 
                                   f"Impossible de vérifier les mises à jour. Code d'erreur: {response.status_code}",
                                   QMessageBox.Ok)
                
        except Exception as e:
            # Gérer les exceptions (problèmes de réseau, etc.)
            QMessageBox.critical(self.parent, "Erreur", 
                               f"Une erreur s'est produite lors de la vérification des mises à jour:\n{str(e)}",
                               QMessageBox.Ok)