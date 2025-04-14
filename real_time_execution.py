class RealTimeStream:
    """Custom stream that sends output in real-time to a QTextEdit widget."""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""
        
    def write(self, text):
        from PyQt5.QtCore import QCoreApplication
        
        # Append text to the buffer
        self.buffer += text
        
        # Use insertText instead of append to avoid extra line breaks
        cursor = self.text_widget.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.text_widget.setTextCursor(cursor)
        
        # Ensure UI updates immediately
        QCoreApplication.processEvents()
        return len(text)
        
    def flush(self):
        pass

def patched_execute(self, python_code):
    """Execute the generated Python code and update output in real-time"""
    import sys
    from PyQt5.QtWidgets import QApplication
    import importlib.util
    import os
    
    # Get reference to the output widget from the main window
    main_window = None
    for widget in QApplication.topLevelWidgets():
        if hasattr(widget, 'output_viewer'):
            main_window = widget
            break
    
    if not main_window:
        return {"success": False, "error": "Could not find main window"}
    
    # Clear the output view before execution
    main_window.output_viewer.clear()
    
    # Don't set a fixed style here - use the theme from main window
    # The theme will be managed by apply_theme in AlgorithmIDE class
    
    # Create our real-time output stream
    real_time_stream = RealTimeStream(main_window.output_viewer)
    
    # Redirect stdout to our real-time stream
    old_stdout = sys.stdout
    sys.stdout = real_time_stream
    
    # Try to dynamically import InputDialog
    try:
        # First check if we can import directly
        from input_dialog import InputDialog
    except ImportError:
        # If not, try to find and import it from the current directory
        try:
            spec = importlib.util.spec_from_file_location("input_dialog", 
                                                         os.path.join(os.path.dirname(__file__), "input_dialog.py"))
            input_dialog_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(input_dialog_module)
            InputDialog = input_dialog_module.InputDialog
        except Exception as e:
            # If all else fails, create a simple InputDialog class
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
    
    # Input handling with our dialog
    def custom_input(prompt=""):
        # Print the prompt to the output
        print(prompt, end="")
        
        # Create input dialog and show it
        dialog = InputDialog(prompt, main_window)
        if dialog.exec_() == dialog.Accepted:
            result = dialog.get_input()
        else:
            result = ""
        
        print(result)  # Echo input in output
        return result
    
    # Store the original input function
    original_input = __builtins__["input"]
    # Replace with our custom function
    __builtins__["input"] = custom_input
    
    # Execute code
    result = {"success": True, "output": "", "error": ""}
    try:
        # Execute the Python code
        exec(python_code)
        result["output"] = real_time_stream.buffer
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        # Show the error in the output view
        main_window.output_viewer.append(f"\nError: {str(e)}")
    finally:
        # Restore stdout and the original input function
        sys.stdout = old_stdout
        __builtins__["input"] = original_input
    
    return result

def patch_real_time_execution():
    """Patch the FrenchAlgorithmCompiler to use real-time execution."""
    from FrenchAlgorithmCompiler import FrenchAlgorithmCompiler
    # Save original method reference for potential restoration
    FrenchAlgorithmCompiler._original_execute = FrenchAlgorithmCompiler.execute
    # Replace with our patched method
    FrenchAlgorithmCompiler.execute = patched_execute
    return True