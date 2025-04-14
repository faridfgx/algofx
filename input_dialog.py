from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class InputDialog(QDialog):
    def __init__(self, prompt, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Input")
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        self.label = QLabel(prompt)
        self.layout.addWidget(self.label)
        
        self.input_field = QLineEdit()
        self.layout.addWidget(self.input_field)
        
        self.button = QPushButton("OK")
        self.button.clicked.connect(self.accept)
        self.layout.addWidget(self.button)
        
    def get_input(self):
        return self.input_field.text()