import os
import json
import ast
import re
import sys
import tempfile
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QPushButton, QAction, QFileDialog, QMessageBox,
                            QTabWidget, QDialog, QMenu, QToolBar, QLabel, QToolButton, QStyle)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor, QTextCursor, QTextCharFormat, QTextCharFormat
from PyQt5.QtCore import Qt, QSettings, QSize, QEvent
from settings_dialog import SettingsDialog
from code_editor import CodeEditor
from syntax_highlighter import SyntaxHighlighter
from FrenchAlgorithmCompiler import FrenchAlgorithmCompiler
from app_data import about_text, syntax_help_text, templates, empty_template_cursor_position
from toolbar_manager import ToolbarManager
from menu_manager import MenuManager
from compiler_module import AlgorithmCompiler
from syntax_helpers import show_syntax_help, get_formatted_syntax_help
from settings_manager import SettingsManager

class AlgorithmIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window icon
        self.setWindowIcon(QIcon("fxlogo.png"))
        
        # Enable drag & drop
        self.setAcceptDrops(True)
        
        # Set up the compiler
        from PyQt5.QtCore import QSettings
        settings = QSettings("AlgoFX", "AlgoFX")
        steps = settings.value("algorithm_execution_steps", 1000, type=int)
        self.compiler = FrenchAlgorithmCompiler(max_steps=steps)
        
        self.settings_manager = SettingsManager("AlgoFX") 
            
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
        
        # Create editor with line numbers
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
                
        # Add execution state flag
        self.is_executing = False
        
        # Initialize settings
        self.init_settings()
        
        # Restore window state or adjust to screen size
        self.restoreWindowState()
        
    def initUI(self):
        self.app_version = "1.2.0"
        
        self.setWindowTitle(f"AlgoFX - Version 64 Bit - {self.app_version}")
        #self.setGeometry(100, 100, 1200, 700)
        
        # Create menu bar (now self.editor exists)
        menu_manager = MenuManager(self)
        self.menubar = menu_manager.create_menu()
        
        # Create toolbar
        toolbar_manager = ToolbarManager(self)
        self.toolbar = toolbar_manager.create_toolbar()
        
        # Note: self.editor is already created in __init__ now
        
        self.bottom_toolbar = QToolBar("Algorithm Blocks")
        self.bottom_toolbar.setIconSize(QSize(32, 32))
        self.bottom_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.bottom_toolbar.setMovable(False)
        
        # Get the current palette to detect if we're in dark mode
        palette = self.palette()
        is_dark_mode = palette.color(QPalette.Window).lightness() < 128
        
        # Define path for icons - using single icon directory
        icons_dir = "icons/"
        
        # Create theme-adaptive styling for toolbar
        if is_dark_mode:
            toolbar_style = """
                QToolBar {
                    background-color: #2d2d2d;
                    border-top: 1px solid #3d3d3d;
                    padding: 4px;
                    spacing: 12px;
                }
                QToolButton {
                    background-color: #363636;
                    border: 1px solid #505050;
                    border-radius: 4px;
                    padding: 6px 10px;
                    margin: 2px;
                    color: #e0e0e0;
                    font-weight: bold;
                }
                QToolButton:hover {
                    background-color: #454545;
                    border: 1px solid #6a6a6a;
                }
                QToolButton:pressed {
                    background-color: #505050;
                }
            """
        else:
            toolbar_style = """
                QToolBar {
                    background-color: #f7f7f7;
                    border-top: 1px solid #e0e0e0;
                    padding: 4px;
                    spacing: 12px;
                }
                QToolButton {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 6px 10px;
                    margin: 2px;
                    color: #333333;
                    font-weight: bold;
                }
                QToolButton:hover {
                    background-color: #e8f0ff;
                    border: 1px solid #b0d0ff;
                }
                QToolButton:pressed {
                    background-color: #d0e0ff;
                }
            """
        
        self.bottom_toolbar.setStyleSheet(toolbar_style)
        
        # Add block insertion actions with simplified icon names
        if_action = QAction(QIcon(icons_dir + "si.png"), " Si Finsi", self)
        if_action.setStatusTip("Insérer un bloc si-finsi")
        if_action.triggered.connect(self.insert_if_block)
        self.bottom_toolbar.addAction(if_action)
        
        if_else_action = QAction(QIcon(icons_dir + "sisinon.png"), " Si Sinon Finsi", self)
        if_else_action.setStatusTip("Insérer un bloc si-sinon-finsi")
        if_else_action.triggered.connect(self.insert_if_else_block)
        self.bottom_toolbar.addAction(if_else_action)
        
        # Add a separator
        self.bottom_toolbar.addSeparator()
        
        for_action = QAction(QIcon(icons_dir + "pour.png"), " Pour Finpour", self)
        for_action.setStatusTip("Insérer un bloc pour-finpour")
        for_action.triggered.connect(self.insert_for_block)
        self.bottom_toolbar.addAction(for_action)
        
        for_step_action = QAction(QIcon(icons_dir + "pourpas.png"), " Pour avec pas", self)
        for_step_action.setStatusTip("Insérer un bloc pour-finpour avec pas")
        for_step_action.triggered.connect(self.insert_for_block_pas)
        self.bottom_toolbar.addAction(for_step_action)
        
        # Add a separator
        self.bottom_toolbar.addSeparator()
        
        while_action = QAction(QIcon(icons_dir + "tantque.png"), " Tantque Fintantque", self)
        while_action.setStatusTip("Insérer un bloc tantque-fintantque")
        while_action.triggered.connect(self.insert_while_block)
        self.bottom_toolbar.addAction(while_action)
        
        # Add bottom toolbar to the editor layout
        self.editor_widget.layout().addWidget(self.bottom_toolbar)
        
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
        
        # Apply theme-adaptive tab styling
        self.apply_tab_styling(is_dark_mode)
        
        # Python code not loaded yet
        self.python_code_loaded = False
        self.python_tab_added = False
        
        # Create status bar with additional information
        self.setup_status_bar()
        
    def changeEvent(self, event):
        """Handle system theme change events"""
        from PyQt5.QtCore import QEvent
        if event.type() == QEvent.PaletteChange:
            # Theme has changed
            palette = self.palette()
            is_dark_mode = palette.color(QPalette.Window).lightness() < 128
            
            # Update the toolbar styling
            self.update_toolbar_theme()
            
            # Also update the tab styling
            self.apply_tab_styling(is_dark_mode)
        
        super().changeEvent(event)
        
    def update_toolbar_theme(self):
        """Update toolbar styling based on current theme"""
        # Detect if we're in dark mode
        is_dark_mode = self.palette().color(QPalette.Window).lightness() < 128
        
        # Update styling
        if is_dark_mode:
            toolbar_style = """
                QToolBar {
                    background-color: #2d2d2d;
                    border-top: 1px solid #3d3d3d;
                    padding: 4px;
                    spacing: 12px;
                }
                QToolButton {
                    background-color: #363636;
                    border: 1px solid #505050;
                    border-radius: 4px;
                    padding: 6px 10px;
                    margin: 2px;
                    color: #e0e0e0;
                }
                QToolButton:hover {
                    background-color: #454545;
                    border: 1px solid #6a6a6a;
                }
                QToolButton:pressed {
                    background-color: #505050;
                }
            """
        else:
            toolbar_style = """
                QToolBar {
                    background-color: #f7f7f7;
                    border-top: 1px solid #e0e0e0;
                    padding: 4px;
                    spacing: 12px;
                }
                QToolButton {
                    background-color: #ffffff;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 6px 10px;
                    margin: 2px;
                    color: #333333;
                }
                QToolButton:hover {
                    background-color: #e8f0ff;
                    border: 1px solid #b0d0ff;
                }
                QToolButton:pressed {
                    background-color: #d0e0ff;
                }
            """
        
        self.bottom_toolbar.setStyleSheet(toolbar_style)
    
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
            
    def open_file(self, filepath=None):
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
        
        # If filepath is provided, use it directly    
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read()
                self.editor.setPlainText(content)
                self.current_file = filepath
                self.statusBar().showMessage(f"Fichier ouvert: {filepath}")
                self.python_code_loaded = False
                # Update line count after loading file
                self.update_line_count()
                return
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'ouverture du fichier: {e}")
                
        # If no filepath provided or failed to open, show file dialog    
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
            import re
            # Updated pattern to handle both cases (with or without semicolon)
            match = re.search(r'Algorithme\s+(\w+)\s*;?', algorithm_code, re.IGNORECASE)
            if match:
                return match.group(1)
        except Exception as e:
            print(f"Error extracting algorithm name: {e}")  # Better error logging
        
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
        """Forward to compiler module with execution flag"""
        self.is_executing = True
        
        # Check input type from settings
        settings = QSettings("AlgoFX", "AlgoFX")
        input_type = settings.value("input_type", 1, type=int)  # Default to console (1)
        
        # If window input is selected (input_type == 2), ensure output tab is visible
        # For console input (input_type == 1), remove output tab if it exists
        show_execution_tab = (input_type == 2)
        
        # Get the index of the output tab
        output_tab_index = -1
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "Sortie d'Exécution":
                output_tab_index = i
                break
        
        if show_execution_tab:
            # Make sure the output tab is visible
            if output_tab_index == -1:  # If not present, add it
                self.tabs.addTab(self.output_widget, "Sortie d'Exécution")
                output_tab_index = self.tabs.count() - 1
            self.tabs.setCurrentIndex(output_tab_index)
        else:
            # Remove the output tab if it exists
            if output_tab_index != -1:
                self.tabs.removeTab(output_tab_index)
        
        # Pass the execution tab visibility info to the algorithm compiler
        self.algorithm_compiler.run_algorithm(self.tabs, self.python_tab_added, show_execution_tab)
        
        self.is_executing = False  # Reset flag when execution completes normally
  
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
        msg_box.setIconPixmap(QPixmap("fxlogoold.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        msg_box.exec_()

    def show_syntax_help(self):
        show_syntax_help(self)
    
    def is_dark_theme(self):
        # Méthode pour détecter si l'application utilise un thème sombre
        # Cette implémentation vérifie la couleur de fond du widget actuel
        app_palette = self.palette()
        bg_color = app_palette.color(QPalette.Window)
        # On considère le thème comme sombre si la luminosité est faible
        return bg_color.lightness() < 128

    def get_formatted_syntax_help(self, is_dark_theme=False):
        return get_formatted_syntax_help(self, is_dark_theme)
    
    def init_settings(self):
        """Initialize settings and apply them"""
        self.settings = QSettings("AlgoFX", "AlgoFX")
        self.apply_settings()
        
        if hasattr(self, 'compiler') and self.compiler:
            settings = QSettings("AlgoFX", "AlgoFX")
            steps = settings.value("algorithm_execution_steps", 1000, type=int)
            self.compiler.update_max_execution_steps(steps)
            
        # Enable undo/redo for the editor
        self.editor.setUndoRedoEnabled(True)

    def apply_settings(self):
        """Apply current settings to the IDE"""
        try:
            # Get font sizes from settings
            editor_font_size = self.settings.value("editor_font_size", 13, type=int)
            python_font_size = self.settings.value("python_font_size", 13, type=int)
            output_font_size = self.settings.value("output_font_size", 12, type=int)
            
            # Get selected font from settings
            selected_font = self.settings.value("selected_font", "", type=str)
            selected_font_path = self.settings.value("selected_font_path", "", type=str)
            font_family = "Courier New"  # Default font
            
            # First check if we have a direct path to the font file (from updated settings dialog)
            if selected_font_path and os.path.exists(selected_font_path):
                from PyQt5.QtGui import QFontDatabase
                font_id = QFontDatabase.addApplicationFont(selected_font_path)
                if font_id != -1:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        font_family = font_families[0]
                        print(f"Successfully loaded font from path: {selected_font_path}")
            # Fall back to the old method if direct path isn't available or didn't work
            elif selected_font and selected_font != "Default":
                # Get the base directory using resource_path to handle both dev and built environments
                if hasattr(self, 'resource_path'):
                    fonts_folder = self.resource_path("fonts")
                else:
                    # Fallback to direct path if resource_path isn't available
                    fonts_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
                
                print(f"Looking for font '{selected_font}' in folder: {fonts_folder}")
                
                font_extensions = ['.ttf', '.otf', '.woff', '.woff2']
                font_loaded = False
                
                for ext in font_extensions:
                    font_path = os.path.join(fonts_folder, selected_font + ext)
                    if os.path.exists(font_path):
                        print(f"Found font file: {font_path}")
                        # Load the font into the application
                        from PyQt5.QtGui import QFontDatabase
                        font_id = QFontDatabase.addApplicationFont(font_path)
                        if font_id != -1:
                            font_families = QFontDatabase.applicationFontFamilies(font_id)
                            if font_families:
                                font_family = font_families[0]
                                print(f"Successfully loaded font family: {font_family}")
                                font_loaded = True
                                # Save the path for future use
                                self.settings.setValue("selected_font_path", font_path)
                                break
                            else:
                                print(f"No font families found for font ID: {font_id}")
                        else:
                            print(f"Failed to add font {font_path} to database")
                
                if not font_loaded:
                    print(f"Could not load font '{selected_font}'. Using default font instead.")
            
            # Create font objects
            from PyQt5.QtGui import QFont
            editor_font = QFont(font_family, editor_font_size)
            python_font = QFont(font_family, python_font_size)
            output_font = QFont(font_family, output_font_size)
            
            # Apply fonts to all components
            print(f"Applying font '{font_family}' to editor (size: {editor_font_size})")
            self.editor.setFont(editor_font)
            
            print(f"Applying font '{font_family}' to python viewer (size: {python_font_size})")
            self.python_viewer.setFont(python_font)
            
            print(f"Applying font '{font_family}' to output viewer (size: {output_font_size})")
            self.output_viewer.setFont(output_font)
            
            # Apply dark mode if enabled
            dark_mode = self.settings.value("dark_mode", True, type=bool)
            print(f"Applying theme (dark mode: {dark_mode})")
            self.apply_theme(dark_mode)
            
            # Apply syntax highlighting setting
            syntax_highlight_enabled = self.settings.value("syntax_highlight_enabled", True, type=bool)
            print(f"Syntax highlighting enabled: {syntax_highlight_enabled}")
            if hasattr(self, "editor_highlighter"):
                if syntax_highlight_enabled:
                    # Make sure the highlighter is connected to the document
                    if self.editor_highlighter.document() != self.editor.document():
                        self.editor_highlighter.setDocument(self.editor.document())
                    # Update colors based on theme
                    self.editor_highlighter.update_colors(dark_mode)
                else:
                    # Disconnect the highlighter from the document
                    self.editor_highlighter.setDocument(None)
            
            print("Settings applied successfully")
            
        except Exception as e:
            import traceback
            print(f"Error applying settings: {str(e)}")
            traceback.print_exc()

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
        # Position cursor between the spaces after "si"
        cursor.movePosition(cursor.PreviousBlock, cursor.MoveAnchor, 3)
        cursor.movePosition(cursor.EndOfLine, cursor.MoveAnchor)
        cursor.movePosition(cursor.Left, cursor.MoveAnchor, 6)  # Position between spaces after "si"
        self.editor.setTextCursor(cursor)
        
    def insert_if_else_block(self):
        """Insert if-else-finsi block at cursor position"""
        cursor = self.editor.textCursor()
        cursor.insertText("si  alors\n    \nsinon\n    \nfinsi\n")
        # Position cursor between the spaces after "si"
        cursor.movePosition(cursor.PreviousBlock, cursor.MoveAnchor, 5)
        cursor.movePosition(cursor.EndOfLine, cursor.MoveAnchor)
        cursor.movePosition(cursor.Left, cursor.MoveAnchor, 6)  # Position between spaces after "si"
        self.editor.setTextCursor(cursor)
        
    def insert_for_block(self):
        """Insert pour-finpour block at cursor position"""
        cursor = self.editor.textCursor()
        cursor.insertText("pour  de allant a faire\n    \nfinpour\n")
        # Position cursor between the spaces after "pour"
        cursor.movePosition(cursor.PreviousBlock, cursor.MoveAnchor, 3)
        cursor.movePosition(cursor.EndOfLine, cursor.MoveAnchor)
        cursor.movePosition(cursor.Left, cursor.MoveAnchor, 18)  # Position between spaces after "pour"
        self.editor.setTextCursor(cursor)
        
    def insert_for_block_pas(self):
        """Insert pour-finpour block at cursor position"""
        cursor = self.editor.textCursor()
        cursor.insertText("pour  de  allant a  pas  faire\n    \nfinpour\n")
        # Position cursor between the spaces after "pour"
        cursor.movePosition(cursor.PreviousBlock, cursor.MoveAnchor, 3)
        cursor.movePosition(cursor.EndOfLine, cursor.MoveAnchor)
        cursor.movePosition(cursor.Left, cursor.MoveAnchor, 26)  # Position between spaces after "pour"
        self.editor.setTextCursor(cursor)
        
    def insert_while_block(self):
        """Insert tantque-fintantque block at cursor position"""
        cursor = self.editor.textCursor()
        cursor.insertText("tantque  faire\n    \nfintantque\n")
        # Position cursor between the spaces after "tantque"
        cursor.movePosition(cursor.PreviousBlock, cursor.MoveAnchor, 3)
        cursor.movePosition(cursor.EndOfLine, cursor.MoveAnchor)
        cursor.movePosition(cursor.Left, cursor.MoveAnchor, 6)  # Position between spaces after "tantque"
        self.editor.setTextCursor(cursor)

    def dragEnterEvent(self, event):
        """Handle drag enter events for the main window"""
        if event.mimeData().hasUrls():
            # Check if any of the URLs have .algo extension
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.endswith('.algo'):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move events"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop events - open the first dropped .algo file"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.endswith('.algo'):
                    # Use the existing open_file method to open the dropped file
                    self.open_file(file_path)
                    event.acceptProposedAction()
                    break
                    

    def saveWindowState(self):
        """Save window position, size and state"""
        settings = QSettings("AlgoFX", "AlgoFX")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("maximized", self.isMaximized())
        
        # If not maximized, save the actual size
        if not self.isMaximized():
            settings.setValue("size", self.size())
            settings.setValue("pos", self.pos())

    def restoreWindowState(self):
        """Restore window position, size and state"""
        settings = QSettings("AlgoFX", "AlgoFX")
        
        # Check if we have stored geometry settings
        if settings.contains("geometry"):
            self.restoreGeometry(settings.value("geometry"))
            self.restoreState(settings.value("windowState"))
            
            # Check if window was maximized
            maximized = settings.value("maximized", False, type=bool)
            if maximized:
                self.showMaximized()
            else:
                # If we have size and position, use them
                if settings.contains("size") and settings.contains("pos"):
                    self.resize(settings.value("size", QSize(1200, 700)))
                    self.move(settings.value("pos"))
        else:
            # First run - adapt to screen size
            self.adjustToScreenSize()

    def adjustToScreenSize(self):
        """Adjust window size based on screen resolution"""
        from PyQt5.QtWidgets import QDesktopWidget
        
        # Get available screen geometry
        desktop = QDesktopWidget()
        available_geometry = desktop.availableGeometry()
        
        # Calculate ideal size (80% of screen width/height)
        width = int(available_geometry.width() * 0.8)
        height = int(available_geometry.height() * 0.8)
        
        # Set window size
        self.resize(width, height)
        
        # Center the window
        self.move(
            available_geometry.center().x() - width // 2,
            available_geometry.center().y() - height // 2
        )
    # Add this to the closeEvent method or create it if it doesn't exist
    def closeEvent(self, event):
        # Save window state before closing
        self.saveWindowState()
        
        # Call the parent class method or handle other close operations
        super().closeEvent(event)
        
    def save_window_geometry(self):
        """Save current window geometry to settings"""
        geometry = self.geometry()
        self.settings.setValue("main_window_x", geometry.x())
        self.settings.setValue("main_window_y", geometry.y())
        self.settings.setValue("main_window_width", geometry.width())
        self.settings.setValue("main_window_height", geometry.height())
        
    
    def moveEvent(self, event):
        """Called when window is moved"""
        super().moveEvent(event)
        self.save_window_geometry()
    
    def resizeEvent(self, event):
        """Called when window is resized"""
        super().resizeEvent(event)
        self.save_window_geometry()
    
    def showEvent(self, event):
        """Called when window is shown"""
        super().showEvent(event)
        self.save_window_geometry()

    def apply_tab_styling(self, is_dark_mode):
        """Apply theme-aware styling to tabs and scrollbars"""
        # Common tab styling
        if is_dark_mode:
            tab_style = """
                QTabWidget::pane {
                    border: 1px solid #3d3d3d;
                    background-color: #2d2d2d;
                }
                QTabBar::tab {
                    background-color: #363636;
                    color: #e0e0e0;
                    border: 1px solid #505050;
                    padding: 6px 12px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #454545;
                    border-bottom-color: #454545;
                }
                QTabBar::tab:hover:!selected {
                    background-color: #404040;
                }
                
                /* Scrollbar styling for dark theme */
                QScrollBar:vertical {
                    border: none;
                    background: #2d2d2d;
                    width: 12px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #5a5a5a;
                    min-height: 20px;
                    border-radius: 6px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
                
                /* Horizontal scrollbar */
                QScrollBar:horizontal {
                    border: none;
                    background: #2d2d2d;
                    height: 12px;
                    margin: 0px;
                }
                QScrollBar::handle:horizontal {
                    background: #5a5a5a;
                    min-width: 20px;
                    border-radius: 6px;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    border: none;
                    background: none;
                    width: 0px;
                }
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                    background: none;
                }
            """
        else:
            tab_style = """
                QTabWidget::pane {
                    border: 1px solid #d0d0d0;
                    background-color: #ffffff;
                }
                QTabBar::tab {
                    background-color: #f0f0f0;
                    color: #333333;
                    border: 1px solid #d0d0d0;
                    padding: 6px 12px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    border-bottom-color: #ffffff;
                }
                QTabBar::tab:hover:!selected {
                    background-color: #e8f0ff;
                }
                
                /* Scrollbar styling for light theme */
                QScrollBar:vertical {
                    border: none;
                    background: #f0f0f0;
                    width: 12px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #c0c0c0;
                    min-height: 20px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #a0a0a0;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                    height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
                
                /* Horizontal scrollbar */
                QScrollBar:horizontal {
                    border: none;
                    background: #f0f0f0;
                    height: 12px;
                    margin: 0px;
                }
                QScrollBar::handle:horizontal {
                    background: #c0c0c0;
                    min-width: 20px;
                    border-radius: 6px;
                }
                QScrollBar::handle:horizontal:hover {
                    background: #a0a0a0;
                }
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                    border: none;
                    background: none;
                    width: 0px;
                }
                QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                    background: none;
                }
            """
        
        # Apply the styling to the tab widget
        self.tabs.setStyleSheet(tab_style)
        
        # Apply theme-adaptive styling to editors and viewers
        editor_style = """
            QTextEdit {
                background-color: %s;
                color: %s;
                border: 1px solid %s;
            }
        """ % (
            "#2d2d2d" if is_dark_mode else "#ffffff",
            "#e0e0e0" if is_dark_mode else "#000000",
            "#3d3d3d" if is_dark_mode else "#d0d0d0"
        )
        
        # Apply style to editor and Python viewer
        self.editor.setStyleSheet(editor_style)
        self.python_viewer.setStyleSheet(editor_style)
        
        # Make output_viewer theme-aware instead of always using light theme
        output_style = """
            QTextEdit {
                background-color: %s;
                color: %s;
                border: 1px solid %s;
                padding: 4px;
            }
            QScrollBar:vertical {
                border: none;
                background: %s;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: %s;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: %s;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                border: none;
                background: %s;
                height: 12px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: %s;
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: %s;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """ % (
            "#111111" if is_dark_mode else "#ffffff",  # Background color
            "#e0e0e0" if is_dark_mode else "#000000",  # Text color
            "#3d3d3d" if is_dark_mode else "#cccccc",  # Border color
            "#2d2d2d" if is_dark_mode else "#f0f0f0",  # Scrollbar background
            "#5a5a5a" if is_dark_mode else "#c0c0c0",  # Scrollbar handle
            "#6a6a6a" if is_dark_mode else "#a0a0a0",  # Scrollbar handle hover
            "#2d2d2d" if is_dark_mode else "#f0f0f0",  # Horizontal scrollbar background
            "#5a5a5a" if is_dark_mode else "#c0c0c0",  # Horizontal scrollbar handle
            "#6a6a6a" if is_dark_mode else "#a0a0a0"   # Horizontal scrollbar handle hover
        )
        
        # Apply the theme-aware style to output viewer
        self.output_viewer.setStyleSheet(output_style)
        
    def initialize_settings(self):
        """Initialize and apply all settings after the IDE has fully started"""
        print("Initializing all application settings...")
        
        # Make sure initial settings are loaded
        if not hasattr(self, 'settings_manager'):
            self.settings_manager = SettingsManager("AlgoFX")
        
        # Load or reload settings
        settings_loaded = self.settings_manager.load_initial_settings()
        
        # Apply settings to all components
        self.apply_settings()
        
        # Update compiler settings
        settings = QSettings("AlgoFX", "AlgoFX")
        steps = settings.value("algorithm_execution_steps", 1000, type=int)
        if hasattr(self, 'compiler') and self.compiler:
            self.compiler.update_max_execution_steps(steps)
        
        # Apply error language setting
        error_language = settings.value("error_language_param", "french", type=str)
        if hasattr(self, 'compiler') and self.compiler and hasattr(self.compiler, 'error_language'):
            self.compiler.error_language = error_language
        
        # Set autocomplete based on settings
        autocomplete_enabled = settings.value("autocomplete_enabled", True, type=bool)
        if hasattr(self, 'editor'):
            self.editor.set_autocomplete_enabled(autocomplete_enabled)
        
        # Apply syntax highlighting
        syntax_highlight_enabled = settings.value("syntax_highlight_enabled", True, type=bool)
        if hasattr(self, 'editor_highlighter'):
            # Handle syntax highlighter toggling
            if not syntax_highlight_enabled:
                # If highlighting is disabled, we need to clear formatting
                cursor = self.editor.textCursor()
                cursor.select(QTextCursor.Document)
                format = QTextCharFormat()
                cursor.setCharFormat(format)
                self.editor.setTextCursor(cursor)
                # And disconnect the highlighter
                self.editor_highlighter.setDocument(None)
            else:
                # Re-enable highlighting by connecting to document again
                self.editor_highlighter.setDocument(self.editor.document())
        
        # Apply theme
        dark_mode = settings.value("dark_mode", False, type=bool)
        self.apply_theme(dark_mode)
        
        print("All settings initialized and applied successfully")

    def showEvent(self, event):
        """Called when the window is shown - perfect time to initialize settings"""
        super().showEvent(event)
        
        # Initialize settings only first time the window is shown
        if not hasattr(self, '_settings_initialized'):
            self._settings_initialized = True
            self.initialize_settings()       