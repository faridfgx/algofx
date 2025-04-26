from PyQt5.QtWidgets import QToolBar, QAction, QToolButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

def fix_algorithm_indentation(algorithm_text):
    """
    Fix indentation in pseudo-code based on French algorithm structure.
    - Algorithme/Var/Const/Debut/Fin → level 0
    - Lines between Var/Const and Debut → level 1
    - Lines inside Debut → base level 1 + control structure nesting
    - Control blocks: si/pour/tantque increase indent, finsi/etc. align with opener
    - Sinon aligns with matching si
    """
    lines = algorithm_text.split('\n')
    result = []

    structure_keywords = ['algorithme', 'var', 'const', 'debut', 'fin']
    control_open = ['si', 'pour', 'tantque']
    control_close = {'finsi': 'si', 'finpour': 'pour', 'fintantque': 'tantque'}

    control_stack = []  # (keyword, indent_level)
    in_main_body = False
    in_var_or_const = False

    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            result.append('')
            continue

        lower = cleaned.lower()
        keyword = lower.split()[0]

        # Structure keywords
        if keyword in structure_keywords:
            if keyword in ['var', 'const']:
                in_var_or_const = True
            elif keyword == 'debut':
                in_main_body = True
                in_var_or_const = False
            elif keyword == 'fin':
                in_main_body = False
            result.append(cleaned)
            continue

        # Handle content in Var/Const sections
        if in_var_or_const and not in_main_body:
            result.append(' ' * 4 + cleaned)
            continue

        # Determine base indent for main body
        base_indent = 1 if in_main_body else 0
        indent_level = base_indent + len(control_stack)

        # Handle closing control structures
        if keyword in control_close:
            if control_stack and control_stack[-1][0] == control_close[keyword]:
                _, level = control_stack.pop()
                result.append(' ' * (4 * level) + cleaned)
                continue

        # Handle sinon
        if keyword == 'sinon':
            for i in range(len(control_stack) - 1, -1, -1):
                if control_stack[i][0] == 'si':
                    indent_level = control_stack[i][1]
                    break
            result.append(' ' * (4 * indent_level) + cleaned)
            continue

        # Handle new control openings
        if keyword in control_open and ('alors' in lower or 'faire' in lower):
            control_stack.append((keyword, indent_level))
            result.append(' ' * (4 * indent_level) + cleaned)
            continue

        # Default body line
        result.append(' ' * (4 * indent_level) + cleaned)

    return '\n'.join(result)




class ToolbarManager:
    def __init__(self, parent):
        """Initialize the toolbar manager with a parent (main window)"""
        self.parent = parent
        
    def create_toolbar(self):
        """Create the main toolbar with improved icons and a prominent run button"""
        toolbar = QToolBar("Barre d'outils principale")
        toolbar.setObjectName("mainToolBar")
        toolbar.setIconSize(QSize(16, 16))
        self.parent.addToolBar(toolbar)
        
        # File operations group
        new_action = QAction(self.parent.style().standardIcon(self.parent.style().SP_FileIcon), "Nouveau", self.parent)
        new_action.setShortcut("Ctrl+N")
        new_action.setToolTip("Nouveau (Ctrl+N)")
        new_action.triggered.connect(self.parent.new_file)
        toolbar.addAction(new_action)
        
        open_action = QAction(self.parent.style().standardIcon(self.parent.style().SP_DialogOpenButton), "Ouvrir", self.parent)
        open_action.setShortcut("Ctrl+O")
        open_action.setToolTip("Ouvrir (Ctrl+O)")
        open_action.triggered.connect(self.parent.open_file)
        toolbar.addAction(open_action)
        
        save_action = QAction(self.parent.style().standardIcon(self.parent.style().SP_DialogSaveButton), "Enregistrer", self.parent)
        save_action.setShortcut("Ctrl+S")
        save_action.setToolTip("Enregistrer (Ctrl+S)")
        save_action.triggered.connect(self.parent.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Editing operations group
        undo_action = QAction(QIcon("icons/undo.png"), "Annuler", self.parent)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setToolTip("Annuler (Ctrl+Z)")
        undo_action.triggered.connect(self.parent.editor.undo)
        toolbar.addAction(undo_action)
        
        redo_action = QAction(QIcon("icons/redo.png"), "Rétablir", self.parent)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.setToolTip("Rétablir (Ctrl+Y)")
        redo_action.triggered.connect(self.parent.editor.redo)
        toolbar.addAction(redo_action)
        
        toolbar.addSeparator()
        
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
        
        # Add the indentation fixer action here
        indent_action = QAction(QIcon("icons/indent.png"), "Corriger Indentation", self.parent)
        indent_action.setShortcut("Ctrl+I")
        indent_action.setToolTip("Corriger l'indentation (Ctrl+I)")
        indent_action.triggered.connect(self.fix_indentation)
        toolbar.addAction(indent_action)
        
        toolbar.addSeparator()
        
        # Execution group
        compile_action = QAction(self.parent.style().standardIcon(self.parent.style().SP_FileDialogDetailedView), "Compiler", self.parent)
        compile_action.setShortcut("F5")
        compile_action.setToolTip("Compiler (F5)")
        compile_action.triggered.connect(self.parent.compile_algorithm)
        toolbar.addAction(compile_action)
        
        run_button = QToolButton(self.parent)
        run_action = QAction(self.parent.style().standardIcon(self.parent.style().SP_MediaPlay), "Exécuter", self.parent)
        run_action.setShortcut("F6")
        run_action.setToolTip("Exécuter (F6)")
        run_action.triggered.connect(self.parent.run_algorithm)
        
        run_button.setDefaultAction(run_action)
        run_button.setIconSize(QSize(16, 16))
        
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
        
        toolbar.addWidget(run_button)
        
        print_action = QAction(QIcon("icons/printer.png"), "Imprimer code", self.parent)
        print_action.setToolTip("Imprimer code")
        print_action.triggered.connect(self.parent.print_code)
        toolbar.addAction(print_action)
        
        toolbar.addSeparator()
        
        font_plus_action = QAction("A+", self.parent)
        font_plus_action.setToolTip("Augmenter la taille de la police")
        font_plus_action.triggered.connect(self.parent.increase_font_size)
        toolbar.addAction(font_plus_action)
        
        font_minus_action = QAction("A-", self.parent)
        font_minus_action.setToolTip("Diminuer la taille de la police")
        font_minus_action.triggered.connect(self.parent.decrease_font_size)
        toolbar.addAction(font_minus_action)
        
        return toolbar
    
    def fix_indentation(self):
        """
        Get the current text from the editor, fix indentation, and update the editor
        """
        # Get the current text from the editor
        current_text = self.parent.editor.toPlainText()
        
        # Fix the indentation
        indented_text = fix_algorithm_indentation(current_text)
        
        # Update the editor with the indented text
        self.parent.editor.setPlainText(indented_text)
        
        # Optionally show a status message
        if hasattr(self.parent, 'statusbar'):
            self.parent.statusbar.showMessage("Indentation corrigée", 3000)  # Show for 3 seconds