from PyQt5.QtWidgets import QToolBar, QAction, QToolButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

class ToolbarManager:
    def __init__(self, parent):
        """Initialize the toolbar manager with a parent (main window)"""
        self.parent = parent
        
    def create_toolbar(self):
        """Create the main toolbar with improved icons and a prominent run button"""
        toolbar = QToolBar("Barre d'outils principale")
        toolbar.setIconSize(QSize(16, 16))  # Keep original icon size
        self.parent.addToolBar(toolbar)
        
        # File operations group
        # New file - keep original icon
        new_action = QAction(self.parent.style().standardIcon(self.parent.style().SP_FileIcon), "Nouveau", self.parent)
        new_action.setShortcut("Ctrl+N")
        new_action.setToolTip("Nouveau (Ctrl+N)")
        new_action.triggered.connect(self.parent.new_file)
        toolbar.addAction(new_action)
        
        # Open file
        open_action = QAction(self.parent.style().standardIcon(self.parent.style().SP_DialogOpenButton), "Ouvrir", self.parent)
        open_action.setShortcut("Ctrl+O")
        open_action.setToolTip("Ouvrir (Ctrl+O)")
        open_action.triggered.connect(self.parent.open_file)
        toolbar.addAction(open_action)
        
        # Save file
        save_action = QAction(self.parent.style().standardIcon(self.parent.style().SP_DialogSaveButton), "Enregistrer", self.parent)
        save_action.setShortcut("Ctrl+S")
        save_action.setToolTip("Enregistrer (Ctrl+S)")
        save_action.triggered.connect(self.parent.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Editing operations group
        # Undo - better undo icon
        undo_action = QAction(QIcon("icons/undo.png"), "Annuler", self.parent)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setToolTip("Annuler (Ctrl+Z)")
        undo_action.triggered.connect(self.parent.editor.undo)
        toolbar.addAction(undo_action)
        
        # Redo - better redo icon
        redo_action = QAction(QIcon("icons/redo.png"), "Rétablir", self.parent)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.setToolTip("Rétablir (Ctrl+Y)")
        redo_action.triggered.connect(self.parent.editor.redo)
        toolbar.addAction(redo_action)
        
        toolbar.addSeparator()
        
        # Keep original cut/copy/paste icons as requested
        cut_action = QAction(QIcon("icons/cut.png"), "Couper", self.parent)
        cut_action.setShortcut("Ctrl+X")
        cut_action.setToolTip("Couper (Ctrl+X)")
        cut_action.triggered.connect(lambda: self.parent.editor.cut())
        toolbar.addAction(cut_action)
        
        copy_action = QAction(QIcon("icons/copy.png"), "Copier", self.parent)
        copy_action.setShortcut("Ctrl+C")
        copy_action.setToolTip("Copier (Ctrl+C)")
        copy_action.triggered.connect(lambda: self.parent.editor.copy())
        toolbar.addAction(copy_action)
        
        paste_action = QAction(QIcon("icons/paste.png"), "Coller", self.parent)
        paste_action.setShortcut("Ctrl+V")
        paste_action.setToolTip("Coller (Ctrl+V)")
        paste_action.triggered.connect(lambda: self.parent.editor.paste())
        toolbar.addAction(paste_action)
        
        toolbar.addSeparator()
        
        # Execution group
        # Compile - keep original
        compile_action = QAction(self.parent.style().standardIcon(self.parent.style().SP_FileDialogDetailedView), "Compiler", self.parent)
        compile_action.setShortcut("F5")
        compile_action.setToolTip("Compiler (F5)")
        compile_action.triggered.connect(self.parent.compile_algorithm)
        toolbar.addAction(compile_action)
        
        # Run - same size but with green background
        run_button = QToolButton(self.parent)
        run_action = QAction(self.parent.style().standardIcon(self.parent.style().SP_MediaPlay), "Exécuter", self.parent)
        run_action.setShortcut("F6")
        run_action.setToolTip("Exécuter (F6)")
        run_action.triggered.connect(self.parent.run_algorithm)
        
        # Set action to button
        run_button.setDefaultAction(run_action)
        
        # Keep original icon size
        run_button.setIconSize(QSize(16, 16))
        
        # Add green background to make it stand out
        run_button.setStyleSheet("""
            QToolButton {
                background-color: #4CAF50;
                border-radius: 3px;
                padding: 3px;
                margin: 1px;
            }
            QToolButton:hover {
                background-color: #45a049;
            }
            QToolButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        # Add the custom run button to toolbar
        toolbar.addWidget(run_button)
        
        # Print code - better icon
        print_action = QAction(QIcon("icons/printer.png"), "Imprimer code", self.parent)
        print_action.setToolTip("Imprimer code")
        print_action.triggered.connect(self.parent.print_code)
        toolbar.addAction(print_action)
        
        toolbar.addSeparator()
        
        # Font size controls - keep as is
        font_plus_action = QAction("A+", self.parent)
        font_plus_action.setToolTip("Augmenter la taille de la police")
        font_plus_action.triggered.connect(self.parent.increase_font_size)
        toolbar.addAction(font_plus_action)
        
        font_minus_action = QAction("A-", self.parent)
        font_minus_action.setToolTip("Diminuer la taille de la police")
        font_minus_action.triggered.connect(self.parent.decrease_font_size)
        toolbar.addAction(font_minus_action)
        
        return toolbar