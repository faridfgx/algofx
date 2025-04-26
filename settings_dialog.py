from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QSpinBox, QCheckBox, QPushButton, QGroupBox, QFormLayout,
                            QComboBox, QRadioButton, QButtonGroup, QMessageBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QPalette, QColor
import os
import sys
from settings_manager import SettingsManager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Paramètres")
        self.resize(450, 550)  # Made taller to accommodate additional settings
        
        # Load settings
        self.settings = QSettings("AlgoFX", "AlgoFX")
        
        # Try to load initial settings from JSON (only on first run)
        self.settings_manager = SettingsManager("AlgoFX")
        self.settings_manager.load_initial_settings()
    
        # Store initial values to check for changes
        self.initial_autocomplete = self.settings.value("autocomplete_enabled", True, type=bool)
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Font settings
        font_group = QGroupBox("Polices")
        font_layout = QFormLayout()
        font_group.setLayout(font_layout)
        
        # Font selection
        self.font_combo = QComboBox()
        self.load_available_fonts()
        current_font = self.settings.value("selected_font", "", type=str)
        if current_font and current_font in [self.font_combo.itemText(i) for i in range(self.font_combo.count())]:
            self.font_combo.setCurrentText(current_font)
        font_layout.addRow("Police:", self.font_combo)
        
        # Editor font size
        self.editor_font_size = QSpinBox()
        self.editor_font_size.setRange(8, 24)
        self.editor_font_size.setValue(self.settings.value("editor_font_size", 13, type=int))
        font_layout.addRow("Taille de police de l'éditeur:", self.editor_font_size)
        
        # Python code font size
        self.python_font_size = QSpinBox()
        self.python_font_size.setRange(8, 24)
        self.python_font_size.setValue(self.settings.value("python_font_size", 13, type=int))
        font_layout.addRow("Taille de police du code Python:", self.python_font_size)
        
        # Output font size
        self.output_font_size = QSpinBox()
        self.output_font_size.setRange(8, 24)
        self.output_font_size.setValue(self.settings.value("output_font_size", 12, type=int))
        font_layout.addRow("Taille de police de la sortie:", self.output_font_size)
        
        main_layout.addWidget(font_group)
        
        # Language settings
        language_group = QGroupBox("Langue")
        language_layout = QFormLayout()
        language_group.setLayout(language_layout)
        
        # Error language selection
        self.error_language_combo = QComboBox()
        self.error_language_combo.addItem("Français")
        self.error_language_combo.addItem("العربية")
        
        # Load saved error language setting
        error_language = self.settings.value("error_language", "Français", type=str)
        if error_language in ["Français", "العربية"]:
            self.error_language_combo.setCurrentText(error_language)
        
        language_layout.addRow("Langue des messages d'erreur:", self.error_language_combo)
        
        main_layout.addWidget(language_group)
        
        # Theme settings
        theme_group = QGroupBox("Thème")
        theme_layout = QVBoxLayout()
        theme_group.setLayout(theme_layout)
        
        # Dark mode checkbox
        self.dark_mode_checkbox = QCheckBox("Mode sombre")
        self.dark_mode_checkbox.setChecked(self.settings.value("dark_mode", False, type=bool))
        theme_layout.addWidget(self.dark_mode_checkbox)
        
        main_layout.addWidget(theme_group)
        
        # Code Editing Features
        editing_group = QGroupBox("Édition de code")
        editing_layout = QVBoxLayout()
        editing_group.setLayout(editing_layout)
        
        # Autocomplete
        self.autocomplete_checkbox = QCheckBox("Activer l'autocomplétion")
        self.autocomplete_checkbox.setChecked(self.initial_autocomplete)
        editing_layout.addWidget(self.autocomplete_checkbox)
        self.autocomplete_checkbox.stateChanged.connect(self.on_autocomplete_checkbox_changed)
        
        # Syntax highlighter
        self.syntax_highlight_checkbox = QCheckBox("Activer la coloration syntaxique")
        self.syntax_highlight_checkbox.setChecked(self.settings.value("syntax_highlight_enabled", True, type=bool))
        editing_layout.addWidget(self.syntax_highlight_checkbox)
        
        main_layout.addWidget(editing_group)
        
        # Execution Settings
        exec_group = QGroupBox("Exécution")
        exec_layout = QVBoxLayout()
        exec_group.setLayout(exec_layout)
        
        # Execution steps for FrenchAlgorithmCompiler
        exec_steps_layout = QFormLayout()
        self.exec_steps = QSpinBox()
        self.exec_steps.setRange(100, 100000)
        self.exec_steps.setValue(self.settings.value("algorithm_execution_steps", 1000, type=int))
        exec_steps_layout.addRow("Nombre maximal d'itérations par boucle:", self.exec_steps)
        exec_layout.addLayout(exec_steps_layout)
        
        # Input type selection
        input_group_box = QGroupBox("Type d'entrée")
        input_layout = QVBoxLayout()
        input_group_box.setLayout(input_layout)
        
        self.input_type_group = QButtonGroup()
        
        self.console_input = QRadioButton("Console")
        self.input_type_group.addButton(self.console_input, 1)
        input_layout.addWidget(self.console_input)
        
        self.window_input = QRadioButton("Fenêtre de saisie")
        self.input_type_group.addButton(self.window_input, 2)
        input_layout.addWidget(self.window_input)
        
        input_type = self.settings.value("input_type", 1, type=int)
        if input_type == 1:
            self.console_input.setChecked(True)
        else:
            self.window_input.setChecked(True)
        
        exec_layout.addWidget(input_group_box)
        
        main_layout.addWidget(exec_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("Appliquer")
        self.apply_button.clicked.connect(self.apply_settings)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.save_and_close)
        
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Apply current theme
        self.apply_theme(self.dark_mode_checkbox.isChecked())
    
    def resource_path(self, relative_path):
        """ Get absolute path to resource in both dev and EXE """
        if getattr(sys, 'frozen', False):
            return os.path.join(os.path.dirname(sys.executable), relative_path)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

    def load_available_fonts(self):
        try:
            fonts_folder = self.resource_path("fonts")
            print(f"Looking for fonts in: {fonts_folder}")
            
            if not os.path.exists(fonts_folder):
                print(f"Fonts folder not found: {fonts_folder}")
                self.font_combo.addItem("Default")
                return
            
            font_extensions = ['.ttf', '.otf', '.woff', '.woff2']
            found_fonts = False
            
            for file in os.listdir(fonts_folder):
                file_path = os.path.join(fonts_folder, file)
                if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in font_extensions):
                    font_name = os.path.splitext(file)[0]
                    print(f"Found font: {font_name} at {file_path}")
                    # Add the font name and store the full path as item data
                    self.font_combo.addItem(font_name)
                    self.font_combo.setItemData(self.font_combo.count()-1, file_path)
                    found_fonts = True
            
            if not found_fonts:
                print("No fonts found in directory")
                self.font_combo.addItem("Default")
            
            # Select previously saved font if available
            current_font = self.settings.value("selected_font", "", type=str)
            if current_font and current_font in [self.font_combo.itemText(i) for i in range(self.font_combo.count())]:
                self.font_combo.setCurrentText(current_font)
                print(f"Selected previously saved font: {current_font}")
        except Exception as e:
            print(f"Error loading fonts: {str(e)}")
            import traceback
            traceback.print_exc()
            # Fall back to default
            self.font_combo.clear()
            self.font_combo.addItem("Default")
    
    def apply_theme(self, dark_mode):
        """Apply dark or light theme to all widgets in the dialog"""
        if dark_mode:
            # Dark mode
            bg_color = QColor(45, 45, 45)
            text_color = QColor(255, 255, 255)
            disabled_text_color = QColor(150, 150, 150)
        else:
            # Light mode
            bg_color = QColor(240, 240, 240)
            text_color = QColor(0, 0, 0)
            disabled_text_color = QColor(120, 120, 120)
        
        # Setup palette
        palette = QPalette()
        palette.setColor(QPalette.Window, bg_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, bg_color.lighter(110) if dark_mode else QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, bg_color.lighter(120) if dark_mode else QColor(245, 245, 245))
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.Button, bg_color)
        palette.setColor(QPalette.ButtonText, text_color)
        palette.setColor(QPalette.Disabled, QPalette.Text, disabled_text_color)
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_text_color)
        
        # Apply palette to the dialog
        self.setPalette(palette)
        
        # Apply to all widgets
        self.apply_palette_to_widgets(self, palette)
    
    def apply_palette_to_widgets(self, parent_widget, palette):
        """Recursively apply palette to all child widgets"""
        for child in parent_widget.findChildren(QGroupBox):
            child.setPalette(palette)
        
        for child in parent_widget.findChildren(QLabel):
            child.setPalette(palette)
        
        for child in parent_widget.findChildren(QCheckBox):
            child.setPalette(palette)
        
        for child in parent_widget.findChildren(QRadioButton):
            child.setPalette(palette)
        
        for child in parent_widget.findChildren(QPushButton):
            child.setPalette(palette)
        
        for child in parent_widget.findChildren(QComboBox):
            child.setPalette(palette)
        
        for child in parent_widget.findChildren(QSpinBox):
            child.setPalette(palette)
    
    def apply_settings(self):
        try:
            # Check for autocomplete setting change
            autocomplete_changed = self.autocomplete_checkbox.isChecked() != self.initial_autocomplete
            
            # Get the font path from the combo box's item data
            font_index = self.font_combo.currentIndex()
            font_path = self.font_combo.itemData(font_index) if font_index >= 0 else ""
            
            # Convert UI language name to parameter name expected by compiler
            error_language_ui = self.error_language_combo.currentText()
            error_language_param = "arabic" if error_language_ui == "العربية" else "french"
            
            # Save all settings
            self.settings.setValue("selected_font", self.font_combo.currentText())
            self.settings.setValue("selected_font_path", font_path)  # Store the full path to the font file
            self.settings.setValue("editor_font_size", self.editor_font_size.value())
            self.settings.setValue("python_font_size", self.python_font_size.value())
            self.settings.setValue("output_font_size", self.output_font_size.value())
            self.settings.setValue("dark_mode", self.dark_mode_checkbox.isChecked())
            self.settings.setValue("autocomplete_enabled", self.autocomplete_checkbox.isChecked())
            self.settings.setValue("syntax_highlight_enabled", self.syntax_highlight_checkbox.isChecked())
            self.settings.setValue("algorithm_execution_steps", self.exec_steps.value())
            self.settings.setValue("input_type", self.input_type_group.checkedId())
            self.settings.setValue("error_language", error_language_ui)
            # Also save the parameter name for direct access in other parts of the application
            self.settings.setValue("error_language_param", error_language_param)
            
            # Debug information
            print(f"Settings saved - Font: {self.font_combo.currentText()}, Path: {font_path}")
            print(f"Font sizes - Editor: {self.editor_font_size.value()}, Python: {self.python_font_size.value()}, Output: {self.output_font_size.value()}")
            print(f"Error language set to: {error_language_ui} ({error_language_param})")
            
            # Apply theme
            self.apply_theme(self.dark_mode_checkbox.isChecked())
            
            # Apply settings if parent exists
            if self.parent:
                print("Applying settings to parent application...")
                self.parent.apply_settings()
                
                # Update compiler's max execution steps if available
                if hasattr(self.parent, 'compiler') and self.parent.compiler:
                    print(f"Updating compiler execution steps to {self.exec_steps.value()}")
                    self.parent.compiler.update_max_execution_steps(self.exec_steps.value())
                    
                    # Update compiler's error language directly for immediate effect
                    print(f"Updating compiler error language to {error_language_param}")
                    if hasattr(self.parent.compiler, 'error_language'):
                        self.parent.compiler.error_language = error_language_param
            else:
                print("No parent object available to apply settings to")
            
                
            print("Settings applied successfully")
            
        except Exception as e:
            print(f"Error applying settings: {str(e)}")
            import traceback
            traceback.print_exc()

    def save_and_close(self):
        self.apply_settings()
        self.accept()
    # In your settings window class (where the checkbox is)
    def on_autocomplete_checkbox_changed(self):
        enabled = self.autocomplete_checkbox.isChecked()
        self.settings.setValue("autocomplete_enabled", enabled)
        
        print(f"Autocomplete changed to: {enabled}")
        
        # Try to access the editor through parent
        if self.parent and hasattr(self.parent, 'editor'):
            print("Found editor through parent reference")
            self.parent.editor.set_autocomplete_enabled(enabled)
        elif hasattr(self, 'code_editor'):
            print("Found code_editor attribute")
            self.code_editor.set_autocomplete_enabled(enabled)
        else:
            print("Could not find editor reference")