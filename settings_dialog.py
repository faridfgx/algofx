from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QSpinBox, QCheckBox, QPushButton, QGroupBox, QFormLayout,
                            QComboBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QPalette, QColor
import os

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Paramètres")
        self.resize(400, 350)  # Made slightly taller to accommodate font selection
        
        # Load settings
        self.settings = QSettings("AlgoFX", "AlgoFX")
        
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
        
        # Theme settings
        theme_group = QGroupBox("Thème")
        theme_layout = QVBoxLayout()
        theme_group.setLayout(theme_layout)
        
        # Dark mode checkbox
        self.dark_mode_checkbox = QCheckBox("Mode sombre")
        self.dark_mode_checkbox.setChecked(self.settings.value("dark_mode", False, type=bool))
        theme_layout.addWidget(self.dark_mode_checkbox)
        
        main_layout.addWidget(theme_group)
        
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
    
    def load_available_fonts(self):
        """Load available fonts from the fonts folder"""
        fonts_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
        
        # Check if the fonts folder exists
        if not os.path.exists(fonts_folder):
            # If not, add a default option
            self.font_combo.addItem("Default")
            return
        
        # Font extensions to look for
        font_extensions = ['.ttf', '.otf', '.woff', '.woff2']
        
        # Find fonts in the directory
        found_fonts = False
        for file in os.listdir(fonts_folder):
            file_path = os.path.join(fonts_folder, file)
            if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in font_extensions):
                # Extract font name from filename (removing extension)
                font_name = os.path.splitext(file)[0]
                self.font_combo.addItem(font_name, file_path)
                found_fonts = True
        
        # If no fonts found, add a default option
        if not found_fonts:
            self.font_combo.addItem("Default")
    
    def apply_settings(self):
        # Save settings
        self.settings.setValue("selected_font", self.font_combo.currentText())
        self.settings.setValue("editor_font_size", self.editor_font_size.value())
        self.settings.setValue("python_font_size", self.python_font_size.value())
        self.settings.setValue("output_font_size", self.output_font_size.value())
        self.settings.setValue("dark_mode", self.dark_mode_checkbox.isChecked())
        
        # Apply settings if parent exists
        if self.parent:
            self.parent.apply_settings()
    
    def save_and_close(self):
        self.apply_settings()
        self.accept()