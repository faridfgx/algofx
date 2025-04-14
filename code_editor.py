from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QTextEdit, QCompleter
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QPainter, QTextFormat
from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal, QStringListModel, QRegExp

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.background_color = QColor("#F0F0F0")
        self.number_color = QColor("#606060")
        
    def sizeHint(self):
        return QSize(self.editor.getLineNumberAreaWidth(), 0)
        
    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)
        
    def update_colors(self, dark_mode=False):
        if dark_mode:
            self.background_color = QColor("#2D2D30")
            self.number_color = QColor("#AAAAAA")
        else:
            self.background_color = QColor("#F0F0F0")
            self.number_color = QColor("#606060")


class CodeEditor(QPlainTextEdit):
    errorSignal = pyqtSignal(str, int)  # Error message and line number
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize colors first (fix for the error)
        self.current_line_color = QColor("#FAFAD2")  # Light yellow
        
        # Flag to prevent recursive text changes
        self._handling_text_change = False
        
        # Set monospaced font
        font = QFont("Courier New", 12)
        self.setFont(font)
        
        # Create line number area
        self.lineNumberArea = LineNumberArea(self)
        
        # Set line wrapping
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        
        # Set tab width (4 spaces)
        self.setTabStopWidth(4 * self.fontMetrics().width(' '))
        
        # Error highlighting
        self.error_lines = set()
        self.error_format = QTextCharFormat()
        self.error_format.setBackground(QColor("#FFE0E0"))  # Light red
        self.error_format.setForeground(QColor("#AA0000"))  # Dark red
        
        # Setup bracket matching
        self.auto_brackets = True
        self.matching_pairs = {
            '(': ')',
            '"': '"'
        }
        
        # Initialize autocomplete
        self.setup_autocomplete()
        
        # Connect signals
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.textChanged.connect(self.on_text_changed)
        
        # Initialize line number area
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
    
    def setup_autocomplete(self):
        """Set up autocomplete with keywords and snippets using QCompleter"""
        # Customize these keywords for your specific language
        self.keywords = [
            "lire", "Lire", "Ecrire", "ecrire", "écrire", "crire", "si", "sinon",
            "finsi", "pour", "faire", "finpour", "tantque", "fintantque", "Entier",
            "entier", "reel", "réel", "chaine de caractere", "char", "character",
            "boolean"
        ]
        
        # Common snippets with descriptions
        self.snippets = {
            "pour": "pour var de val1 a val2 faire\n",
            "si": "si condition alors\n",
            "tantque": "tantque condition faire\n"
        }
        
        # Combine keywords and snippets for the completer
        completion_words = self.keywords + list(self.snippets.keys())
        
        # Create a QCompleter with our word list
        self.completer = QCompleter(completion_words, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        
        # Connect signals
        self.completer.activated.connect(self.insert_completion)
        
        # Set the text document on the completer
        self.completer.setWidget(self)
    
    def getLineNumberAreaWidth(self):
        """Calculate the width needed for the line number area"""
        digits = 1
        max_block = max(1, self.document().blockCount())
        while max_block >= 10:
            max_block //= 10
            digits += 1
        
        space = 15 + self.fontMetrics().width('9') * digits
        return space
    
    def updateLineNumberAreaWidth(self, _=0):
        """Update the margin width to accommodate line numbers"""
        self.setViewportMargins(self.getLineNumberAreaWidth(), 0, 0, 0)
    
    def updateLineNumberArea(self, rect, dy):
        """Update the line number area when the text viewport updates"""
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
    
    def resizeEvent(self, event):
        """Handle resize events to adjust the line number area"""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.getLineNumberAreaWidth(), cr.height()))
    
    def lineNumberAreaPaintEvent(self, event):
        """Paint the line number area"""
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), self.lineNumberArea.background_color)
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(self.lineNumberArea.number_color)
                painter.drawText(0, int(top), self.lineNumberArea.width() - 5, 
                                self.fontMetrics().height(),
                                Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
    
    def highlightCurrentLine(self):
        """Highlight the line containing the cursor"""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(self.current_line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def update_colors(self, dark_mode=False):
        """Update colors for dark mode or light mode"""
        if dark_mode:
            self.current_line_color = QColor("#2D2D50")  # Dark blue
            self.lineNumberArea.update_colors(dark_mode=True)
            
            # Update completion popup style
            if hasattr(self, 'completer') and self.completer.popup():
                self.completer.popup().setStyleSheet("""
                    background-color: #2D2D30;
                    color: #FFFFFF;
                    border: 1px solid #555555;
                """)
        else:
            self.current_line_color = QColor("#FAFAD2")  # Light yellow
            self.lineNumberArea.update_colors(dark_mode=False)
            
            # Update completion popup style
            if hasattr(self, 'completer') and self.completer.popup():
                self.completer.popup().setStyleSheet("""
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #C0C0C0;
                """)
        
        self.highlightCurrentLine()
    
    def on_text_changed(self):
        """Handle text changes, including auto-completion and bracket matching"""
        # Prevent recursion
        if hasattr(self, '_handling_text_change') and self._handling_text_change:
            return
        
        self._handling_text_change = True
        try:
            # Try to show completions
            self.try_show_completions()
            
            # Auto-close brackets
            if self.auto_brackets:
                self.handle_auto_brackets()
        finally:
            self._handling_text_change = False
    
    def try_show_completions(self):
        """Check current text and show completions if appropriate"""
        # Minimum characters to trigger autocompletion
        MIN_CHARS = 2
        
        # Get current word under cursor
        cursor = self.textCursor()
        text_before_cursor = self.get_text_before_cursor(cursor)
        
        # Extract current word (assuming words contain only alphanumeric and underscore)
        import re
        match = re.search(r'(\w+)$', text_before_cursor)
        
        if not match:
            if hasattr(self, 'completer') and self.completer.popup():
                self.completer.popup().hide()
            return
            
        current_word = match.group(1)
        
        # Show completions only if the word is long enough
        if len(current_word) >= MIN_CHARS:
            # Set the prefix for completion
            self.completer.setCompletionPrefix(current_word)
            
            # If there are no completions, hide the popup
            if self.completer.completionCount() == 0:
                self.completer.popup().hide()
                return
                
            # Get the popup
            popup = self.completer.popup()
            
            # Calculate position to show the popup
            rect = self.cursorRect(cursor)
            rect.setWidth(300)  # Set a reasonable width for the popup
            
            # Show the completion popup at the right position
            self.completer.complete(rect)
        else:
            if hasattr(self, 'completer') and self.completer.popup():
                self.completer.popup().hide()
    
    def get_text_before_cursor(self, cursor):
        """Get text from the start of the line up to the cursor position"""
        # Get the current block of text (line)
        block = cursor.block()
        # Get position of cursor in the block
        pos_in_block = cursor.positionInBlock()
        # Return text from start of block to cursor position
        return block.text()[:pos_in_block]
    
    def insert_completion(self, completion_text):
        """Insert the selected completion text"""
        if not completion_text:
            return
            
        cursor = self.textCursor()
        
        # Delete the current word (that we're completing)
        text_before_cursor = self.get_text_before_cursor(cursor)
        import re
        match = re.search(r'(\w+)$', text_before_cursor)
        
        if match:
            # Calculate how many characters to delete
            chars_to_delete = len(match.group(1))
            
            # Delete those characters
            for _ in range(chars_to_delete):
                cursor.deletePreviousChar()
        
        # Insert either the snippet or normal text
        if completion_text in self.snippets:
            # Insert the snippet
            cursor.insertText(self.snippets[completion_text])
            
            # Position cursor appropriately within the snippet
            if completion_text == "pour":
                cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 3)
            elif completion_text == "tantque" or completion_text == "si":
                # Move to after "condition"
                cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 
                                   len(" faire\n  // Instructions \nfintantque \n   "))
        else:
            cursor.insertText(completion_text)
    
    def handle_auto_brackets(self):
        """Auto-close brackets and quotes"""
        cursor = self.textCursor()
        
        # Don't auto-close if there's selected text
        if cursor.hasSelection():
            return
            
        # Get the current character (what was just typed)
        block = cursor.block()
        block_pos = cursor.positionInBlock()
        block_text = block.text()
        
        # If at the end of the block, we can't get the current char
        if block_pos <= 0 or block_pos > len(block_text):
            return

        prev_char = block_text[block_pos - 1] if block_pos > 0 else ""
        
        # If the character is an opening bracket or quote, auto-close it
        if prev_char in self.matching_pairs:
            # Check if we should close it (based on surrounding context)
            should_close = True
            
            # Check what follows the cursor
            if block_pos < len(block_text):
                next_char = block_text[block_pos]
                if (next_char.isalnum() or next_char.isspace() or 
                    next_char == self.matching_pairs[prev_char]):
                    should_close = False
            
            if should_close:
                cursor.insertText(self.matching_pairs[prev_char])
                cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
                self.setTextCursor(cursor)
    
    def keyPressEvent(self, event):
        """Handle key press events including autocomplete handling"""
        # If completer is visible and handles the key, don't process it further
        if hasattr(self, 'completer') and self.completer.popup() and self.completer.popup().isVisible():
            # Define keys that will be handled by the completer popup
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, 
                             Qt.Key_Tab, Qt.Key_Backtab, 
                             Qt.Key_Up, Qt.Key_Down):
                event.ignore()
                return
                
        # Auto-indentation handling
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            
            # Auto-indent based on the previous line
            indent = ""
            for char in text:
                if char == ' ':
                    indent += ' '
                else:
                    break
            
            # Detect if we need to increase indentation (after a colon)
            if text.strip().endswith(':'):
                cursor.insertText("\n" + indent + "    ")  # Add 4 spaces indentation
                self.setTextCursor(cursor)
                return
            
            # Standard indentation follows the previous line
            cursor.insertText("\n" + indent)
            self.setTextCursor(cursor)
            return
                
        # Process the event normally
        super().keyPressEvent(event)