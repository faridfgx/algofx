from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import QRegExp

class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode = False
        self.init_highlighting_rules()
        
    def init_highlighting_rules(self):
        """Initialize highlighting rules with appropriate colors"""
        self.highlighting_rules = []
        
        # Define formats for different syntax elements
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(120, 40, 180) if not self.dark_mode else QColor(197, 134, 192))
        keyword_format.setFontWeight(QFont.Bold)
        
        keywords = [
            r'\bAlgorithme\b', r'\bVar\b', r'\bvar\b', r'\ballant\b', r'\bpas\b', r'\bSortir\b', r'\bDebut\b', r'\bFin\b', 
            r'\bsi\b', r'\balors\b', r'\bsinon\b', r'\bfinsi\b', r'\bTantque\b', r'\bFintantque\b',
            r'\btantque\b', r'\bfaire\b', r'\bfintantque\b', r'\bFinpour\b', r'\bPour\b',
            r'\bpour\b', r'\bde\b', r'\ba\b', r'\bfinpour\b', r'\bLire\b', r'\bEcrire\b',
            r'\bEntier\b', r'\bReel\b', r'\bRéel\b', r'\bChaine de caractere\b',r'\bConst\b'
        ]
        
        for keyword in keywords:
            pattern = QRegExp(keyword)
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Function calls
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(60, 120, 180) if not self.dark_mode else QColor(86, 156, 214))
        pattern = QRegExp(r'\b(lire|ecrire|Lire|Ecrire)\s*\([^\)]*\)\s*;')
        self.highlighting_rules.append((pattern, function_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(180, 80, 80) if not self.dark_mode else QColor(206, 145, 120))
        pattern = QRegExp(r'"[^"]*"')
        self.highlighting_rules.append((pattern, string_format))
        pattern = QRegExp(r"'[^']*'")
        self.highlighting_rules.append((pattern, string_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(110, 110, 110) if not self.dark_mode else QColor(87, 166, 74))
        pattern = QRegExp(r'//.*')
        self.highlighting_rules.append((pattern, comment_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(0, 120, 0) if not self.dark_mode else QColor(181, 206, 168))
        pattern = QRegExp(r'\b[0-9]+(\.[0-9]+)?\b')
        self.highlighting_rules.append((pattern, number_format))
        
        # Assignment
        assignment_format = QTextCharFormat()
        assignment_format.setForeground(QColor(180, 100, 30) if not self.dark_mode else QColor(215, 186, 125))
        pattern = QRegExp(r'<-')
        self.highlighting_rules.append((pattern, assignment_format))

    def update_colors(self, dark_mode=False):
        """Update colors based on theme"""
        self.dark_mode = dark_mode
        self.init_highlighting_rules()
        self.rehighlight()

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)