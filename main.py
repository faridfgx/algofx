import sys
import time
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QProgressBar, QDesktopWidget
)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QTimer
from algorithm_ide import AlgorithmIDE
from real_time_execution import patched_execute
from FrenchAlgorithmCompiler import FrenchAlgorithmCompiler

class SplashScreen(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Load splash image
        pixmap = QPixmap(image_path)
        image = pixmap.toImage()
        self.image_width = pixmap.width()
        self.image_height = pixmap.height()
        
        # Find bottom-most visible pixel
        visible_bottom = self.find_visible_bottom(image)+10
        
        # Set size up to bottom of visible part + space for progress bar
        self.setFixedSize(self.image_width, visible_bottom + 16 )
        
        # Image label
        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setFixedSize(self.image_width, self.image_height)
        self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        # Progress bar
        self.progress = QProgressBar(self)
        self.progress.setFixedHeight(10)
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        bar_width = int(self.image_width * 0.8)
        self.progress.setFixedWidth(bar_width)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #cccccc;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #2980b9;
                border-radius: 3px;
            }
        """)
        
        # Position progress bar under the visible part of the image
        x = int((self.image_width - bar_width) / 2)
        y = visible_bottom
        self.progress.move(x, y)
        
        self.center()
        
    def find_visible_bottom(self, image: QImage) -> int:
        """Find bottom-most visible (non-transparent) pixel row."""
        for y in range(image.height() - 1, -1, -1):
            for x in range(image.width()):
                if image.pixelColor(x, y).alpha() > 0:
                    return y + 1
        return image.height()
        
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        x = int((screen.width() - self.width()) / 2)
        y = int((screen.height() - self.height()) / 2)
        self.move(x, y)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setWindowIcon(QIcon("fxlogo.png"))
    
    # Check for file path in command line arguments
    file_to_open = None
    if len(sys.argv) > 1:
        # Take the first file argument
        potential_file = sys.argv[1]
        if os.path.isfile(potential_file):
            file_to_open = os.path.abspath(potential_file)
    
    # Show splash screen
    splash = SplashScreen("icons/fxlogospls.png")
    splash.show()
    app.processEvents()
    
    # Patch compiler method
    FrenchAlgorithmCompiler._original_execute = FrenchAlgorithmCompiler.execute
    FrenchAlgorithmCompiler.execute = patched_execute
    
    # Simulate loading (2s to 15s based on arbitrary metric)
    start_time = time.perf_counter()
    load_duration = 2000 + int((sys.getsizeof(app) % 13000))  # milliseconds
    
    def update_progress():
        elapsed = int(time.perf_counter() * 1000) - int(start_time * 1000)
        progress = min(100, int((elapsed / load_duration) * 100))
        splash.progress.setValue(progress)
        if progress >= 100:
            timer.stop()
            load_ide(file_to_open)
    
    def load_ide(filepath=None):
        ide = AlgorithmIDE()
        splash.close()
        ide.show()
        
        # If a file was specified, open it after a brief delay to ensure the UI is ready
        if filepath:
            QTimer.singleShot(100, lambda: ide.open_file(filepath))
    
    timer = QTimer()
    timer.timeout.connect(update_progress)
    timer.start(30)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()