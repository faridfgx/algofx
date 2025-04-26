from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QTextEdit, QCompleter
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QPainter, QTextFormat
from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal, QStringListModel, QRegExp, QSettings, QTimer
import weakref

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.background_color = QColor("#F0F0F0")
        self.number_color = QColor("#606060")
        # Create a bold font for line numbers
        self.line_number_font = QFont("Courier New", 13)
        self.line_number_font.setBold(True)
       
        
    def sizeHint(self):
        return QSize(self.editor.getLineNumberAreaWidth() if self.editor else 0, 0)
        
    def paintEvent(self, event):
        # The critical fix: prevent painting if parent is gone
        parent = self.parent()
        if not parent or not isinstance(parent, QWidget) or not parent.isVisible():
            return
            
        # Proceed only if we're still connected to a valid editor
        if hasattr(self, 'editor') and self.editor and self.editor.isVisible():
            try:
                self.editor.lineNumberAreaPaintEvent(event)
            except Exception as e:
                # We're likely in the middle of editor destruction
                print(f"Safe paint handling: {e}")
                pass
        
    def update_colors(self, dark_mode=False):
        if dark_mode:
            self.background_color = QColor("#2D2D30")
            self.number_color = QColor("#AAAAAA")
        else:
            self.background_color = QColor("#F0F0F0")
            self.number_color = QColor("#606060")
            
    def setParent(self, parent):
        if not parent and hasattr(self, 'editor'):
            # Parent is being removed, clear editor reference
            self.editor = None
        super().setParent(parent)

class CodeEditor(QPlainTextEdit):
    errorSignal = pyqtSignal(str, int)  # Error message and line number
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Flag to indicate editor is being destroyed
        self.is_being_destroyed = False
        
        # Initialize colors first
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
            '(': ')'
            
            
        }
        
        # Load settings
        self.settings = QSettings("AlgoFX", "AlgoFX")
        self.autocomplete_enabled = self.settings.value("autocomplete_enabled", True, type=bool)
        
        # Define keywords and snippets (to be used by autocomplete if enabled)
        self.setup_keywords_and_snippets()
        
        # Initialize autocomplete based on settings
        self.completer = None
        if self.autocomplete_enabled:
            self.setup_completer()
        
        # Connect signals
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        
        # Delay connecting textChanged signal until everything is set up
        # to avoid crashes during initialization
        self.textChanged.connect(self.safe_on_text_changed)
        
        # Initialize line number area
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
    
    def __del__(self):
        """Cleanup when the object is deleted"""
        self.is_being_destroyed = True
    
    def setup_keywords_and_snippets(self):
        """Set up keywords and snippets lists"""
        # Customize these keywords for your specific language
        self.keywords = [
            "Lire();", "Ecrire();", "Si", "Sinon",
            "Finsi", "Pour", "faire", "Finpour", "Tantque", "Fintantque",
            "Entier", "Reel", "Chaine de caractere", "Character",
            "Booleen","Sortir;","div","mod","racine()"
        ]
        
        # Common snippets with descriptions
        self.snippets = {
            "Pour faire": "Pour var de val1 a val2 faire\n",
            "Si alors": "Si condition alors\n",
            "Tantque faire": "Tantque condition faire\n",
            "Pour faire avec pas": "Pour var de val1 a val2 pas valpas faire\n"
        }
    
    def setup_completer(self):
        """Set up the completer object"""
        try:
            # Combine keywords and snippets for the completer
            completion_words = self.keywords + list(self.snippets.keys())
            
            # Create a QCompleter with our word list
            self.completer = QCompleter(completion_words, self)
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.completer.setCompletionMode(QCompleter.PopupCompletion)
            
            # Connect signals for completion
            self.completer.activated.connect(self.insert_completion)
            
            # Set the text document on the completer
            self.completer.setWidget(self)
        except Exception as e:
            print(f"Error setting up completer: {e}")
            self.completer = None
    
    def getLineNumberAreaWidth(self):
        """Calculate the width needed for the line number area"""
        try:
            digits = 1
            max_block = max(1, self.document().blockCount())
            while max_block >= 10:
                max_block //= 10
                digits += 1
            
            # Increase width slightly to accommodate the bold font
            space = 20 + self.fontMetrics().width('9') * digits
            return space
        except Exception:
            return 35  # Slightly larger default width for bold numbers
    
    def updateLineNumberAreaWidth(self, _=0):
        """Update the margin width to accommodate line numbers"""
        if self.is_being_destroyed:
            return
            
        try:
            self.setViewportMargins(self.getLineNumberAreaWidth(), 0, 0, 0)
        except Exception as e:
            print(f"Error updating line number width: {e}")
    
    def updateLineNumberArea(self, rect, dy):
        """Update the line number area when the text viewport updates"""
        if self.is_being_destroyed:
            return
            
        try:
            if not hasattr(self, 'lineNumberArea'):
                return
                
            line_number_area = getattr(self, 'lineNumberArea')
            if not line_number_area:
                return
                
            if dy:
                line_number_area.scroll(0, dy)
            else:
                line_number_area.update(0, rect.y(), line_number_area.width(), rect.height())
                
            if rect.contains(self.viewport().rect()):
                self.updateLineNumberAreaWidth()
        except Exception as e:
            print(f"Error updating line number area: {e}")
    
    def resizeEvent(self, event):
        """Handle resize events to adjust the line number area"""
        if self.is_being_destroyed:
            super().resizeEvent(event)
            return
            
        try:
            super().resizeEvent(event)
            
            # Safety check to ensure lineNumberArea still exists
            if hasattr(self, 'lineNumberArea') and self.lineNumberArea:
                cr = self.contentsRect()
                self.lineNumberArea.setGeometry(
                    QRect(cr.left(), cr.top(), self.getLineNumberAreaWidth(), cr.height())
                )
        except Exception as e:
            print(f"Error in resize event: {e}")
            super().resizeEvent(event)
    
    def lineNumberAreaPaintEvent(self, event):
        """Paint the line number area"""
        if self.is_being_destroyed:
            return
            
        try:
            # Safety check
            if not hasattr(self, 'lineNumberArea') or not self.lineNumberArea:
                return
                
            painter = QPainter(self.lineNumberArea)
            painter.fillRect(event.rect(), self.lineNumberArea.background_color)
            
            # Set the bold font for line numbers
            painter.setFont(self.lineNumberArea.line_number_font)
            
            block = self.firstVisibleBlock()
            if not block.isValid():
                return
                
            block_number = block.blockNumber()
            top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
            bottom = top + self.blockBoundingRect(block).height()
            
            while block.isValid() and top <= event.rect().bottom():
                if block.isVisible() and bottom >= event.rect().top():
                    number = str(block_number + 1)
                    painter.setPen(self.lineNumberArea.number_color)
                    # Make the text a bit darker for more emphasis
                    if not self.lineNumberArea.number_color.value() < 100:  # If not already dark
                        painter.setPen(self.lineNumberArea.number_color.darker(120))
                    painter.drawText(0, int(top), self.lineNumberArea.width() - 5, 
                                    self.fontMetrics().height(),
                                    Qt.AlignRight, number)
                
                block = block.next()
                if not block.isValid():
                    break
                    
                top = bottom
                bottom = top + self.blockBoundingRect(block).height()
                block_number += 1
        except Exception as e:
            print(f"Error painting line numbers: {e}")
    
    def highlightCurrentLine(self):
        """Highlight the line containing the cursor"""
        if self.is_being_destroyed:
            return
            
        try:
            extra_selections = []
            
            if not self.isReadOnly():
                selection = QTextEdit.ExtraSelection()
                selection.format.setBackground(self.current_line_color)
                selection.format.setProperty(QTextFormat.FullWidthSelection, True)
                selection.cursor = self.textCursor()
                selection.cursor.clearSelection()
                extra_selections.append(selection)
            
            self.setExtraSelections(extra_selections)
        except Exception as e:
            print(f"Error highlighting current line: {e}")
    
    def update_colors(self, dark_mode=False):
        """Update colors for dark mode or light mode"""
        if self.is_being_destroyed:
            return
            
        try:
            if dark_mode:
                self.current_line_color = QColor("#2D2D50")  # Dark blue
                if hasattr(self, 'lineNumberArea') and self.lineNumberArea:
                    self.lineNumberArea.update_colors(dark_mode=True)
                    # Make dark mode line numbers bolder with higher contrast
                    self.lineNumberArea.number_color = QColor("#CCCCCC")
                
                # Update completion popup style
                if hasattr(self, 'completer') and self.completer and self.completer.popup():
                    self.completer.popup().setStyleSheet("""
                        background-color: #2D2D30;
                        color: #FFFFFF;
                        border: 1px solid #555555;
                    """)
            else:
                self.current_line_color = QColor("#FAFAD2")  # Light yellow
                if hasattr(self, 'lineNumberArea') and self.lineNumberArea:
                    self.lineNumberArea.update_colors(dark_mode=False)
                    # Make light mode line numbers darker for better contrast
                    self.lineNumberArea.number_color = QColor("#404040")
                
                # Update completion popup style
                if hasattr(self, 'completer') and self.completer and self.completer.popup():
                    self.completer.popup().setStyleSheet("""
                        background-color: #FFFFFF;
                        color: #000000;
                        border: 1px solid #C0C0C0;
                    """)
            
            self.highlightCurrentLine()
        except Exception as e:
            print(f"Error updating colors: {e}")
    
    def set_autocomplete_enabled(self, enabled):
        """Enable or disable autocomplete functionality"""
        if self.is_being_destroyed:
            return
            
        try:
            # Update the setting
            self.autocomplete_enabled = enabled
            
            # Clean up the existing completer if it exists
            if hasattr(self, 'completer') and self.completer:
                # Hide popup if visible
                if self.completer.popup() and self.completer.popup().isVisible():
                    self.completer.popup().hide()
                
                if not enabled:
                    # Fully destroy the completer when disabling
                    try:
                        self.completer.activated.disconnect(self.insert_completion)
                    except (TypeError, RuntimeError):
                        # Already disconnected
                        pass
                    self.completer.setWidget(None)
                    self.completer = None
            
            # Recreate the completer if enabling
            if enabled and not self.completer:
                self.setup_completer()
        except Exception as e:
            print(f"Error setting autocomplete: {e}")
    
    def safe_on_text_changed(self):
        """Safe wrapper for on_text_changed to catch any exceptions"""
        if self.is_being_destroyed:
            return
            
        try:
            self.on_text_changed()
        except Exception as e:
            print(f"Error handling text change: {e}")
    
    def on_text_changed(self):
        """Handle text changes, including auto-completion"""
        if self.is_being_destroyed:
            return
            
        # Prevent recursion
        if getattr(self, '_handling_text_change', False):
            return
        
        self._handling_text_change = True
        try:
            # Only try to show completions if autocomplete is enabled
            if (getattr(self, 'autocomplete_enabled', False) and 
                hasattr(self, 'completer') and self.completer):
                self.try_show_completions()
            
            # We'll handle auto brackets in keyPressEvent instead
        finally:
            self._handling_text_change = False
    
    def try_show_completions(self):
        """Check current text and show completions if appropriate"""
        if self.is_being_destroyed:
            return
            
        if (not hasattr(self, 'completer') or not self.completer or 
            not getattr(self, 'autocomplete_enabled', False)):
            return

        try:
            # Minimum characters to trigger autocompletion
            MIN_CHARS = 2

            # Get current word under cursor
            cursor = self.textCursor()
            text_before_cursor = self.get_text_before_cursor(cursor)

            # Extract current word using regex
            import re
            match = re.search(r'(\w+)$', text_before_cursor)

            if not match:
                if self.completer.popup() and self.completer.popup().isVisible():
                    QTimer.singleShot(0, self.completer.popup().hide)
                return

            current_word = match.group(1)

            if len(current_word) >= MIN_CHARS:
                # Set the prefix for completion
                self.completer.setCompletionPrefix(current_word)

                # If there are no completions, hide the popup
                if self.completer.completionCount() == 0:
                    if self.completer.popup() and self.completer.popup().isVisible():
                        QTimer.singleShot(0, self.completer.popup().hide)
                    return

                # Get the popup and show it at the correct position
                popup = self.completer.popup()
                rect = self.cursorRect(cursor)
                rect.setWidth(300)  # Optional: adjust width

                QTimer.singleShot(0, lambda: self.completer.complete(rect))
            else:
                if self.completer.popup() and self.completer.popup().isVisible():
                    QTimer.singleShot(0, self.completer.popup().hide)

        except Exception as e:
            print(f"[Autocomplete Error] {e}")
    
    def get_text_before_cursor(self, cursor):
        """Get text from the start of the line up to the cursor position"""
        try:
            # Get the current block of text (line)
            block = cursor.block()
            # Get position of cursor in the block
            pos_in_block = cursor.positionInBlock()
            # Return text from start of block to cursor position
            return block.text()[:pos_in_block]
        except Exception:
            return ""
    
    def insert_completion(self, completion_text):
        """Insert the selected completion text"""
        if self.is_being_destroyed:
            return
            
        if not completion_text:
            return
        
        try:
            self._handling_text_change = True
            
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
                if completion_text == "Pour faire":
                    cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 3)
                elif completion_text == "Tantque faire" or completion_text == "Si alors":
                    # Move to after "condition"
                    cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 
                                      len(" faire\n") if completion_text == "Tantque faire" else
                                      len(" alors\n"))
            else:
                cursor.insertText(completion_text)
        except Exception as e:
            print(f"Error inserting completion: {e}")
        finally:
            self._handling_text_change = False
    
    def keyPressEvent(self, event):
        """Handle key press events including autocomplete handling and bracket matching"""
        if self.is_being_destroyed:
            super().keyPressEvent(event)
            return
            
        try:
            # If completer is visible and handles the key, don't process it further
            if (hasattr(self, 'completer') and self.completer and 
                self.completer.popup() and self.completer.popup().isVisible()):
                # Define keys that will be handled by the completer popup
                if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, 
                                 Qt.Key_Tab, Qt.Key_Backtab, 
                                 Qt.Key_Up, Qt.Key_Down):
                    event.ignore()
                    return
            
            # Handle auto-brackets directly in key press event
            if (getattr(self, 'auto_brackets', False) and 
                not getattr(self, '_handling_text_change', False) and
                event.text() in self.matching_pairs):
                
                cursor = self.textCursor()
                if not cursor.hasSelection():
                    char = event.text()
                    # Let the character be inserted normally
                    super().keyPressEvent(event)
                    # Then add the closing bracket
                    self._handling_text_change = True
                    try:
                        cursor = self.textCursor()
                        cursor.insertText(self.matching_pairs[char])
                        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
                        self.setTextCursor(cursor)
                    finally:
                        self._handling_text_change = False
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
                
                # Set flag to avoid triggering text changed handling
                self._handling_text_change = True
                try:
                    # Detect if we need to increase indentation (after a colon)
                    if text.strip().endswith(':'):
                        cursor.insertText("\n" + indent + "    ")  # Add 4 spaces indentation
                        self.setTextCursor(cursor)
                        return
                    
                    # Standard indentation follows the previous line
                    cursor.insertText("\n" + indent)
                    self.setTextCursor(cursor)
                finally:
                    self._handling_text_change = False
                return
                    
            # Process the event normally
            super().keyPressEvent(event)
        except Exception as e:
            print(f"Error in key press event: {e}")
            # Make sure we still process the event if there's an error
            try:
                super().keyPressEvent(event)
            except Exception:
                pass
    
    def closeEvent(self, event):
        """Properly handle close events to avoid deletion issues"""
        # Set flag to prevent other operations during destruction
        self.is_being_destroyed = True
        
        try:
            # Clean up resources before closing
            if hasattr(self, 'completer') and self.completer:
                try:
                    if self.completer.popup() and self.completer.popup().isVisible():
                        self.completer.popup().hide()
                    self.completer.setWidget(None)
                    self.completer = None
                except Exception:
                    pass
                    
            # Disconnect signals to prevent crashes
            try:
                self.blockCountChanged.disconnect(self.updateLineNumberAreaWidth)
                self.updateRequest.disconnect(self.updateLineNumberArea)
                self.cursorPositionChanged.disconnect(self.highlightCurrentLine)
                self.textChanged.disconnect(self.safe_on_text_changed)
            except Exception:
                pass
        except Exception as e:
            print(f"Error in close event: {e}")
            
        super().closeEvent(event)
    def __del__(self):
        # Critical: Set the lineNumberArea to None to prevent further painting
        if hasattr(self, 'lineNumberArea') and self.lineNumberArea:
            self.lineNumberArea.editor = None
            self.lineNumberArea = None