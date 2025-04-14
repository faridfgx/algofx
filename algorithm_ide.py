import os
import ast
import re
import tempfile
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QPushButton, QAction, QFileDialog, QMessageBox,
                            QTabWidget, QDialog, QMenu, QToolBar, QLabel, QToolButton, QStyle)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor, QTextCursor, QTextCharFormat
from PyQt5.QtCore import Qt, QSettings, QSize
from settings_dialog import SettingsDialog
from code_editor import CodeEditor
from syntax_highlighter import SyntaxHighlighter
from FrenchAlgorithmCompiler import FrenchAlgorithmCompiler
from app_data import about_text, syntax_help_text, templates, empty_template_cursor_position
from toolbar_manager import ToolbarManager
from menu_manager import MenuManager
from compiler_module import AlgorithmCompiler

class AlgorithmIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window icon
        self.setWindowIcon(QIcon("fxlogo.png"))

        # Set up the compiler
        self.compiler = FrenchAlgorithmCompiler()
        
        # File path for current file
        self.current_file = None
        
        # Create main widget and layout first
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create editor tab
        self.editor_widget = QWidget()
        editor_layout = QVBoxLayout()
        self.editor_widget.setLayout(editor_layout)
        
        # Create editor with line numbers - INCREASED FONT SIZE BY 20%
        self.editor = CodeEditor()
        self.editor.setFont(QFont("Courier New", 13))  # Changed from 10 to 12
        self.editor_highlighter = SyntaxHighlighter(self.editor.document())
        editor_layout.addWidget(self.editor)
        
        # Create UI (now that self.editor exists)
        self.initUI()
        
        # Set console font - INCREASED SIZE BY 20%
        console_font = QFont("Courier New", 12)  # Changed from 10 to 12
        self.output_viewer.setFont(console_font)

        # Set a white background for console with dark text for better visibility
        self.output_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #CCCCCC;
                padding: 4px;
            }
        """)
        
        # Create our algorithm compiler module
        self.algorithm_compiler = AlgorithmCompiler(
            self.editor, 
            self.output_viewer, 
            self.python_viewer, 
            self.statusBar()
        )
        # Set the French compiler instance
        self.algorithm_compiler.compiler = self.compiler

        # Insert template algorithm
        self.insert_template()
        
        # Connect editor cursor position to status bar update
        self.editor.cursorPositionChanged.connect(self.update_status_bar)
        
        # Initialize settings
        self.init_settings()
        
    def initUI(self):
        # Main window properties
        self.app_version = "1.1.0"
        
        self.setWindowTitle(f"AlgoFX - Version 64 Bit - {self.app_version}")
        self.setGeometry(100, 100, 1200, 700)
        
        # Create menu bar (now self.editor exists)
        menu_manager = MenuManager(self)
        self.menubar = menu_manager.create_menu()
        
        # Create toolbar
        toolbar_manager = ToolbarManager(self)
        self.toolbar = toolbar_manager.create_toolbar()
        
        # Note: self.editor is already created in __init__ now
        
        # Create button layout for algorithm blocks
        button_layout = QHBoxLayout()
        
        # Add block insertion buttons
        self.if_button = QPushButton(" Ajouter bloc si-finsi ")
        self.if_button.clicked.connect(self.insert_if_block)
        button_layout.addWidget(self.if_button)
        
        self.if_else_button = QPushButton(" Ajouter bloc si-sinon-finsi ")
        self.if_else_button.clicked.connect(self.insert_if_else_block)
        button_layout.addWidget(self.if_else_button)
        
        self.for_button = QPushButton(" Ajouter bloc pour-finpour ")
        self.for_button.clicked.connect(self.insert_for_block)
        button_layout.addWidget(self.for_button)
        
        self.while_button = QPushButton(" Ajouter bloc tantque-fintantque ")
        self.while_button.clicked.connect(self.insert_while_block)
        button_layout.addWidget(self.while_button)
    
        button_layout.addStretch(1)  # Add stretch to push buttons to the left
        
        # Add button layout to editor layout
        self.editor_widget.layout().addLayout(button_layout)
        
        # Create Python code tab
        self.python_code_widget = QWidget()
        python_layout = QVBoxLayout()
        self.python_code_widget.setLayout(python_layout)
        
        self.python_viewer = QTextEdit()
        self.python_viewer.setFont(QFont("Courier New", 13))  # Changed from 10 to 12
        self.python_viewer.setReadOnly(True)
        python_layout.addWidget(self.python_viewer)
        
        # Create output tab
        self.output_widget = QWidget()
        output_layout = QVBoxLayout()
        self.output_widget.setLayout(output_layout)
        
        self.output_viewer = QTextEdit()
        self.output_viewer.setFont(QFont("Courier New", 13))  # Changed from 10 to 12
        self.output_viewer.setReadOnly(True)
        output_layout.addWidget(self.output_viewer)
        
        # Add tabs to tab widget - HIDE PYTHON TAB INITIALLY
        self.tabs.addTab(self.editor_widget, "Éditeur d'Algorithme")
        # We'll add the Python tab only when needed
        self.tabs.addTab(self.output_widget, "Sortie d'Exécution")
        
        # Python code not loaded yet
        self.python_code_loaded = False
        self.python_tab_added = False
        
        # Create status bar with additional information
        self.setup_status_bar()
        
    
    def setup_status_bar(self):
        """Set up status bar with line and column information"""
        self.statusBar().showMessage("Prêt")
        
        # Add permanent widgets to status bar
        self.line_col_label = QLabel("Ligne: 1, Colonne: 1")
        self.statusBar().addPermanentWidget(self.line_col_label)
        
        self.line_count_label = QLabel("Lignes: 0")
        self.statusBar().addPermanentWidget(self.line_count_label)
        
        # Update line count initially
        self.update_line_count()
        
        # Connect text changed signal to update line count
        self.editor.textChanged.connect(self.update_line_count)
    
    def update_status_bar(self):
        """Update cursor position in status bar"""
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.line_col_label.setText(f"Ligne: {line}, Colonne: {column}")
    
    def update_line_count(self):
        """Update the line count in status bar"""
        text = self.editor.toPlainText()
        lines = text.count('\n') + 1
        self.line_count_label.setText(f"Lignes: {lines}")
           
    def increase_font_size(self):
        """Increase font size and apply immediately"""
        current_font = self.editor.font()
        current_size = current_font.pointSize()
        new_size = current_size + 1
        
        # Apply to editor
        new_font = QFont(current_font.family(), new_size)
        self.editor.setFont(new_font)
        
        # Save setting
        self.settings.setValue("editor_font_size", new_size)
        
        # Optionally apply to other views
        self.python_viewer.setFont(QFont("Courier New", new_size))
        self.settings.setValue("python_font_size", new_size)
        
    def decrease_font_size(self):
        """Decrease font size and apply immediately"""
        current_font = self.editor.font()
        current_size = current_font.pointSize()
        new_size = max(8, current_size - 1)  # Don't go below 8pt
        
        # Apply to editor
        new_font = QFont(current_font.family(), new_size)
        self.editor.setFont(new_font)
        
        # Save setting
        self.settings.setValue("editor_font_size", new_size)
        
        # Optionally apply to other views
        self.python_viewer.setFont(QFont("Courier New", new_size))
        self.settings.setValue("python_font_size", new_size)
        
    def print_code(self):
        """Imprimer le code actuel, en couleur ou en noir et blanc selon le choix de l'utilisateur."""
        from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
        from PyQt5.QtWidgets import QMessageBox
        from PyQt5.QtGui import QTextCharFormat, QColor

        # Demander à l'utilisateur son choix
        choix = QMessageBox.question(
            self,
            "Mode d'impression",
            "Voulez-vous imprimer avec la coloration syntaxique (en couleurs) ?\n"
            "Choisissez 'Non' pour une impression en noir et blanc.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)

        def handle_paint_request(p):
            if choix == QMessageBox.Yes:
                # Impression avec couleurs (coloration syntaxique)
                self.editor.document().print_(p)
            else:
                # Cloner le document et supprimer les couleurs
                doc = self.editor.document().clone()

                cursor = doc.find("")  # Début
                while not cursor.isNull() and not cursor.atEnd():
                    cursor.movePosition(cursor.NextCharacter, cursor.KeepAnchor)
                    fmt = QTextCharFormat()
                    fmt.setForeground(QColor("black"))
                    cursor.mergeCharFormat(fmt)

                doc.print_(p)

        preview.paintRequested.connect(handle_paint_request)
        preview.exec_()



    def new_file(self):
        if self.editor.document().isModified():
            reply = QMessageBox.question(self, "Nouveau fichier",
                                        "Êtes-vous sûr de vouloir créer un nouveau fichier? Les modifications non enregistrées seront perdues.",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
                
        self.editor.clear()
        self.current_file = None
        self.statusBar().showMessage("Nouveau fichier")
        self.insert_template()
        
    def open_file(self):
        if self.editor.document().isModified():
            reply = QMessageBox.question(self, "Ouvrir fichier",
                                        "Les modifications non enregistrées seront perdues. Continuer?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
                
        # Create the algorithmes folder if it doesn't exist
        algo_folder = os.path.join(os.path.expanduser("~"), "algorithmes")
        if not os.path.exists(algo_folder):
            os.makedirs(algo_folder)
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Ouvrir un fichier",
            algo_folder, 
            "Fichiers Algorithme (*.algo);;Tous les fichiers (*)"
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                self.editor.setPlainText(content)
                self.current_file = file_path
                self.statusBar().showMessage(f"Fichier ouvert: {file_path}")
                self.python_code_loaded = False
                # Update line count after loading file
                self.update_line_count()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ouverture du fichier: {e}")
                
    def extract_algorithm_name(self):
        """Extract algorithm name from the code"""
        try:
            algorithm_code = self.editor.toPlainText()
            # Look for the algorithm name pattern
            import re
            match = re.search(r'Algorithme\s+(\w+)\s*;', algorithm_code, re.IGNORECASE)
            if match:
                return match.group(1)
        except Exception:
            pass
        return "MonAlgorithme"  # Default name if extraction fails

    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as file:
                    file.write(self.editor.toPlainText())
                self.statusBar().showMessage(f"Fichier enregistré: {self.current_file}")
                self.editor.document().setModified(False)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement du fichier: {e}")
        else:
            self.save_file_as()
            
    def save_file_as(self):
        # Create the algorithmes folder if it doesn't exist
        algo_folder = os.path.join(os.path.expanduser("~"), "algorithmes")
        if not os.path.exists(algo_folder):
            os.makedirs(algo_folder)
        
        # Extract algorithm name for default filename
        algorithm_name = self.extract_algorithm_name()
        default_filename = os.path.join(algo_folder, f"{algorithm_name}.algo")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer sous",
            default_filename, 
            "Fichiers Algorithme (*.algo);;Tous les fichiers (*)"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(self.editor.toPlainText())
                self.current_file = file_path
                self.statusBar().showMessage(f"Fichier enregistré: {file_path}")
                self.editor.document().setModified(False)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement du fichier: {e}")

    
    def show_python_code(self):
        """Show Python code tab if it's not already shown"""
        # First, make sure we have compiled code
        python_code = self.compile_algorithm(switch_tab=False)
        
        if not python_code:
            return
            
        # Add the Python tab if it's not already added
        if not self.python_tab_added:
            self.tabs.insertTab(1, self.python_code_widget, "Code Python")
            self.python_tab_added = True
            
        # Switch to Python code tab
        self.tabs.setCurrentIndex(1)
                


    def compile_algorithm(self, switch_tab=True):
        """Forward to the compiler module"""
        python_code = self.algorithm_compiler.compile_algorithm(switch_tab)
        
        # Add the Python tab if compilation was successful and tab isn't already added
        if python_code and switch_tab and not self.python_tab_added:
            self.tabs.insertTab(1, self.python_code_widget, "Code Python")
            self.python_tab_added = True
            self.tabs.setCurrentIndex(1)
            
        return python_code
        
  
    def run_algorithm(self):
        """Forward to compiler module"""
        self.algorithm_compiler.run_algorithm(self.tabs, self.python_tab_added)
  

    def handle_execution_result(self, result):
        # Clear previous output
        self.output_viewer.clear()
        
        # Update output viewer with appropriate color
        if result["success"]:
            self.append_colored_text(result["output"], "#000000")  # Black text
            self.statusBar().showMessage("Exécution réussie")
        else:
            self.append_colored_text(f"Erreur d'exécution: {result['error']}", "#FF0000")  # Red for errors
            self.statusBar().showMessage("Erreur d'exécution")
        
    def clear_output(self):
        self.output_viewer.clear()
        cursor = self.output_viewer.textCursor()
        cursor.movePosition(cursor.Start)
        self.output_viewer.setTextCursor(cursor)
        
    def append_colored_text(self, text, color="#E0E0E0"):
        from PyQt5.QtGui import QTextCharFormat, QColor
        cursor = self.output_viewer.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        cursor.mergeCharFormat(format)
        cursor.insertText(text)
        self.output_viewer.setTextCursor(cursor)
        
    def show_about(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("À propos")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about_text)
        msg_box.setIconPixmap(QPixmap("fxlogo.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        msg_box.exec_()
            
    def show_syntax_help(self):

        # Création de la boîte de dialogue
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Aide sur la syntaxe")
        help_dialog.resize(850, 650)  # Dimensions légèrement augmentées
        
        # Configuration du layout principal
        main_layout = QVBoxLayout()
        help_dialog.setLayout(main_layout)
        
        # Création du widget de texte avec style amélioré
        help_text_widget = QTextEdit()
        
        # Configuration de la police et des couleurs
        code_font = QFont("Consolas", 12)  # Police monospace moderne
        if not code_font.exactMatch():
            code_font = QFont("Courier New", 12)  # Fallback si Consolas n'est pas disponible
        
        help_text_widget.setFont(code_font)
        
        # Style avancé pour le texte d'aide (fond légèrement teinté)
        palette = help_text_widget.palette()
        palette.setColor(QPalette.Base, QColor(252, 252, 255))  # Fond légèrement bleuté
        palette.setColor(QPalette.Text, QColor(25, 25, 80))     # Texte bleu foncé
        help_text_widget.setPalette(palette)
        
        # Définir le texte et rendre en lecture seule
        help_text_widget.setPlainText(syntax_help_text)
        help_text_widget.setReadOnly(True)
        
        # Ajouter le widget au layout
        main_layout.addWidget(help_text_widget)
        
        # Boutons en bas
        button_layout = QHBoxLayout()
        
        # Bouton de fermeture
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(help_dialog.accept)
        close_button.setFixedWidth(100)
        
        # Ajout de l'espacement et du bouton au layout
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)
        
        # Afficher la boîte de dialogue
        help_dialog.exec_()

    def init_settings(self):
        """Initialize settings and apply them"""
        self.settings = QSettings("AlgoFX", "AlgoFX")
        self.apply_settings()
        
        # Enable undo/redo for the editor
        self.editor.setUndoRedoEnabled(True)

    def apply_settings(self):
        """Apply current settings to the IDE"""
        # Get font sizes from settings
        editor_font_size = self.settings.value("editor_font_size", 13, type=int)
        python_font_size = self.settings.value("python_font_size", 13, type=int)
        output_font_size = self.settings.value("output_font_size", 12, type=int)
        
        # Get selected font from settings
        selected_font = self.settings.value("selected_font", "", type=str)
        font_family = "Courier New"  # Default font
        
        # If a custom font is selected, try to load it
        if selected_font and selected_font != "Default":
            fonts_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
            font_extensions = ['.ttf', '.otf', '.woff', '.woff2']
            
            for ext in font_extensions:
                font_path = os.path.join(fonts_folder, selected_font + ext)
                if os.path.exists(font_path):
                    # Load the font into the application
                    from PyQt5.QtGui import QFontDatabase
                    font_id = QFontDatabase.addApplicationFont(font_path)
                    if font_id != -1:
                        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                    break
        
        # Apply fonts to all components
        self.editor.setFont(QFont(font_family, editor_font_size))
        self.python_viewer.setFont(QFont(font_family, python_font_size))
        self.output_viewer.setFont(QFont(font_family, output_font_size))
        
        # Apply dark mode if enabled
        dark_mode = self.settings.value("dark_mode", True, type=bool)  # Changed default to True
        self.apply_theme(dark_mode)

    def apply_theme(self, dark_mode=True):
        """Apply light or dark theme to the application"""
        if dark_mode:
            # Dark theme
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #2D2D30;
                    color: #FFFFFF;
                }
                QMenuBar, QMenu {
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                }
                QMenu::item:selected {
                    background-color: #3E3E40;
                }
                QTabWidget::pane {
                    border: 1px solid #3E3E40;
                    background-color: #252526;
                }
                QTabBar::tab {
                    background-color: #2D2D30;
                    color: #FFFFFF;
                    padding: 5px 10px;
                    border: 1px solid #3E3E40;
                }
                QTabBar::tab:selected {
                    background-color: #1E1E1E;
                    border-bottom-color: #007ACC;
                }
                QPushButton {
                    background-color: #3E3E42;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #434346;
                }
                QTextEdit, QPlainTextEdit {
                    background-color: #1E1E1E;
                    color: #DCDCDC;
                    border: 1px solid #3E3E40;
                }
                QMessageBox {
                    background-color: #2D2D30;
                    color: #FFFFFF;
                }
                QLabel {
                    color: #FFFFFF;
                }
                QDialog {
                    background-color: #2D2D30;
                }
                QGroupBox {
                    color: #FFFFFF;
                }
                QToolBar {
                    background-color: #2D2D30;
                    border: 1px solid #3E3E40;
                    spacing: 3px;
                }
                QToolButton {
                    background-color: #3E3E42;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    border-radius: 2px;
                    padding: 3px;
                }
                QToolButton:hover {
                    background-color: #434346;
                }
                QStatusBar {
                    background-color: #007ACC;
                    color: #FFFFFF;
                }
                QStatusBar QLabel {
                    color: #FFFFFF;
                    padding: 3px 5px;
                }
            """)
            
            # Update syntax highlighter colors for dark theme
            if hasattr(self, "editor_highlighter"):
                self.editor_highlighter.update_colors(dark_mode=True)
                
            # Update line number area and current line highlighting
            self.editor.update_colors(dark_mode=True)
            
            # Set dark background for output viewer with readable text
            self.output_viewer.setStyleSheet("""
                QTextEdit {
                    background-color: #101010;
                    color: #DCDCDC;
                    border: 1px solid #3E3E40;
                    padding: 4px;
                    font-family: 'Courier New';
                    font-size: 13pt;
                }
            """)
            
        else:
            # Light theme (default)
            self.setStyleSheet("")
            
            # Update syntax highlighter colors for light theme
            if hasattr(self, "editor_highlighter"):
                self.editor_highlighter.update_colors(dark_mode=False)
                
            # Update line number area and current line highlighting
            self.editor.update_colors(dark_mode=False)
            
            # Set white background for console with dark text
            self.output_viewer.setStyleSheet("""
                QTextEdit {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #CCCCCC;
                    padding: 4px;
                    font-family: 'Courier New';
                    font-size: 13pt;
                }
            """)

    def show_settings_dialog(self):
        """Show the settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec_()
        
    # Template insertion methods - assumed these are included elsewhere
    def insert_template(self):
        self.editor.setPlainText(templates["empty"])
        # Place le curseur à la position après "// Déclaration des variables"
        cursor = self.editor.textCursor()
        cursor.setPosition(empty_template_cursor_position)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)
       
        
    def insert_moyenne_template(self):
        self.editor.setPlainText(templates["moyenne"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)
        
    def insert_table_template(self):
        self.editor.setPlainText(templates["table"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)
        
    def insert_max_template(self):
        self.editor.setPlainText(templates["maximum"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)
        
    def insert_afficher_template(self):
        self.editor.setPlainText(templates["AfficherNombres"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)

    def insert_somme10_template(self):
        self.editor.setPlainText(templates["Somme10"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)

    def insert_pairs_template(self):
        self.editor.setPlainText(templates["NombresPairs"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)

    def insert_impairs_template(self):
        self.editor.setPlainText(templates["NombresImpairs"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)

    def insert_sommeN_template(self):
        self.editor.setPlainText(templates["SommeN"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)

    def insert_cercle_template(self):
        self.editor.setPlainText(templates["CalculCercle"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)

    def insert_eq1_template(self):
        self.editor.setPlainText(templates["EquationPremierDegre"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)

    def insert_pgcd_template(self):
        self.editor.setPlainText(templates["CalculPGCD"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)

    def insert_ppcm_template(self):
        self.editor.setPlainText(templates["CalculPPCM"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)

    def insert_eq2_template(self):
        self.editor.setPlainText(templates["EquationSecondDegre"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)
        
    def insert_decimalversbinaire(self):
        self.editor.setPlainText(templates["DecimalVersBinaire"])
        self.editor.setFocus()
        self.tabs.setCurrentIndex(0)
    
    def insert_if_block(self):
        """Insert if-finsi block at cursor position"""
        cursor = self.editor.textCursor()
        cursor.insertText("si  alors\n    \nfinsi\n")
        # Position cursor after the condition
        cursor.movePosition(cursor.PreviousBlock, cursor.MoveAnchor, 3)
        cursor.movePosition(cursor.EndOfLine, cursor.MoveAnchor)
        cursor.movePosition(cursor.Left, cursor.MoveAnchor, 7)  # Move before "alors"
        self.editor.setTextCursor(cursor)
        
    def insert_if_else_block(self):
        """Insert if-else-finsi block at cursor position"""
        cursor = self.editor.textCursor()
        cursor.insertText("si  alors\n    \nsinon\n    \nfinsi\n")
        # Position cursor after the condition
        cursor.movePosition(cursor.PreviousBlock, cursor.MoveAnchor, 5)
        cursor.movePosition(cursor.EndOfLine, cursor.MoveAnchor)
        cursor.movePosition(cursor.Left, cursor.MoveAnchor, 7)  # Move before "alors"
        self.editor.setTextCursor(cursor)
        
    def insert_for_block(self):
        """Insert pour-finpour block at cursor position"""
        cursor = self.editor.textCursor()
        cursor.insertText("pour  de  a  faire\n    \nfinpour\n")
        # Position cursor at variable name position
        cursor.movePosition(cursor.PreviousBlock, cursor.MoveAnchor, 3)
        cursor.movePosition(cursor.Right, cursor.MoveAnchor, 5)  # After "pour "
        self.editor.setTextCursor(cursor)
        
    def insert_while_block(self):
        """Insert tantque-fintantque block at cursor position"""
        cursor = self.editor.textCursor()
        cursor.insertText("tantque  faire\n    \nfintantque\n")
        # Position cursor at condition position
        cursor.movePosition(cursor.PreviousBlock, cursor.MoveAnchor, 3)
        cursor.movePosition(cursor.Right, cursor.MoveAnchor, 8)  # After "tantque "
        self.editor.setTextCursor(cursor)