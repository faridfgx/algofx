from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QPalette, QColor

class InputDialog(QDialog):
    def __init__(self, prompt, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Input")
        self.resize(300, 120)  # Slightly larger for better UX
        
        # Load theme setting
        settings = QSettings("AlgoFX", "AlgoFX")
        dark_mode = settings.value("dark_mode", False, type=bool)
        
        # Apply theme if dark mode is enabled
        if dark_mode:
            self.apply_dark_theme()
        
        # Dialog layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Prompt label
        self.label = QLabel(prompt)
        self.layout.addWidget(self.label)
        
        # Input field
        self.input_field = QLineEdit()
        self.layout.addWidget(self.input_field)
        
        # Button layout (improved with Cancel option)
        button_layout = QHBoxLayout()
        
        # OK button
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        # Add buttons to layout with right alignment
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        self.layout.addLayout(button_layout)
        
        # Set focus to input field
        self.input_field.setFocus()
    
    def apply_dark_theme(self):
        """Apply dark theme styling to the dialog"""
        dark_palette = QPalette()
        
        # Set color scheme for dark theme
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        # Apply the palette to the dialog
        self.setPalette(dark_palette)
    
    def get_input(self):
        return self.input_field.text()