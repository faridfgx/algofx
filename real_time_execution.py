from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QSettings
import sys
import os
import time
import threading
import subprocess
import tempfile

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
    """Execute the generated Python code with support for real console execution"""
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QSettings
    import importlib.util
    import os
    import time
    import threading
    
    # Get reference to the output widget from the main window
    main_window = None
    for widget in QApplication.topLevelWidgets():
        if hasattr(widget, 'output_viewer'):
            main_window = widget
            break
    
    if not main_window:
        return {"success": False, "error": "Could not find main window"}
    
    # Check input type setting
    settings = QSettings("AlgoFX", "AlgoFX")
    input_type = settings.value("input_type", 1, type=int)  # 1 = Console, 2 = Dialog
    
    # OPTION 1: Real console execution
    if input_type == 1:  # Console
        return execute_in_real_console(python_code, main_window)
    
    # OPTION 2: In-app dialog execution
    else:  # Dialog
        return execute_with_dialog(python_code, main_window)

def execute_in_real_console(python_code, main_window):
    """Execute Python code in a real system console"""
    # First create a temporary Python file with the code
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w', encoding='utf-8') as temp_file:
        temp_file_path = temp_file.name
        # Write the Python code to execute
        temp_file.write(python_code)
    
    # Create different wrapper scripts based on the platform
    if sys.platform.startswith('win'):
        # Windows batch script
        with tempfile.NamedTemporaryFile(suffix='.bat', delete=False, mode='w') as batch_file:
            batch_file_path = batch_file.name
            batch_file.write(f'''@echo off
python "{temp_file_path}"
echo.
echo Appuyez sur n'importe quelle touche pour quitter...
pause > nul
''')
        execute_path = batch_file_path
    else:
        # Unix/Mac shell script
        with tempfile.NamedTemporaryFile(suffix='.sh', delete=False, mode='w') as shell_file:
            shell_file_path = shell_file.name
            shell_file.write(f'''#!/bin/bash
python3 "{temp_file_path}"
echo ""
echo "Appuyez sur n'importe quelle touche pour quitter..."
read -n 1 -s
''')
            # Make the script executable
            os.chmod(shell_file_path, 0o755)
        execute_path = shell_file_path
    
    result = {"success": True, "output": "", "error": ""}
    
    try:
        # Determine the appropriate command to open a console window based on OS
        if sys.platform.startswith('win'):
            # Windows - use our batch file
            cmd = ['start', 'cmd', '/c', execute_path]
            subprocess.run(' '.join(cmd), shell=True)
        elif sys.platform.startswith('darwin'):
            # macOS
            # AppleScript to open Terminal and run the script
            applescript = f'''
            tell application "Terminal"
                do script "'{execute_path}'"
                activate
            end tell
            '''
            subprocess.run(['osascript', '-e', applescript])
        else:
            # Linux/Unix
            # Check for common terminal emulators
            terminal_cmds = [
                ['gnome-terminal', '--', execute_path],
                ['xterm', '-e', execute_path],
                ['konsole', '--', execute_path],
                ['xfce4-terminal', '--', execute_path]
            ]
            
            success = False
            for cmd in terminal_cmds:
                try:
                    subprocess.run(['which', cmd[0]], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    subprocess.Popen(cmd)
                    success = True
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
                    
            if not success:
                # If no terminal emulator is found, show error and fallback to dialog mode
                QMessageBox.warning(main_window, "Terminal Not Found", 
                                    "Could not find a terminal emulator. Using in-app execution instead.")
                return execute_with_dialog(python_code, main_window)
        
        # Update output viewer with message about external execution
        main_window.output_viewer.clear()


        
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        # Show the error in the output view
        main_window.output_viewer.append(f"\nError launching console: {str(e)}")
        # Fallback to dialog mode
        return execute_with_dialog(python_code, main_window)
    
    return result

def execute_with_dialog(python_code, main_window):
    """Execute Python code in the app with dialog input"""
    import sys
    import time
    import threading
    
    # Clear the output view before execution
    main_window.output_viewer.clear()
    
    # Create our real-time output stream
    real_time_stream = RealTimeStream(main_window.output_viewer)
    
    # Redirect stdout to our real-time stream
    old_stdout = sys.stdout
    sys.stdout = real_time_stream
    
    # Store the original input function
    original_input = __builtins__["input"]
    
    # Import or create InputDialog class
    try:
        # First check if we can import directly
        from input_dialog import InputDialog
    except ImportError:
        # If not, try to find and import it from the current directory
        try:
            import importlib.util
            import os
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
                    
                    # Add cancel button
                    self.cancel_button = QPushButton("Cancel")
                    self.cancel_button.clicked.connect(self.reject)
                    self.layout.addWidget(self.cancel_button)
                    
                def get_input(self):
                    return self.input_field.text()
    
    # Custom input function for dialog input
    def dialog_style_input(prompt=""):
        # Check if execution should stop
        if not main_window.is_executing:
            raise KeyboardInterrupt("Exécution interrompue par l'utilisateur")
            
        # Print the prompt to the output
        print(prompt, end="")
        
        # Create input dialog and show it
        dialog = InputDialog(prompt, main_window)
        result = dialog.exec_()
        
        # If dialog was rejected (Cancel button or closed), stop execution
        if result != dialog.Accepted:
            main_window.is_executing = False
            raise KeyboardInterrupt("Exécution interrompue par l'utilisateur")
            
        user_input = dialog.get_input()
            
        # Check again if execution was stopped while dialog was open
        if not main_window.is_executing:
            raise KeyboardInterrupt("Exécution interrompue par l'utilisateur")
            
        print(user_input)  # Echo input in output
        return user_input
    
    # Use dialog-style input
    __builtins__["input"] = dialog_style_input
    
    # Function to periodically check if execution should be stopped
    def check_stop_execution():
        while main_window.is_executing:
            if not main_window.is_executing:
                break
            time.sleep(0.1)  # Check every 100ms
    
    # Start a monitoring thread
    stop_checker = threading.Thread(target=check_stop_execution)
    stop_checker.daemon = True
    stop_checker.start()
    
    # Execute code
    result = {"success": True, "output": "", "error": ""}
    try:
        # Execute the Python code
        exec(python_code)
        result["output"] = real_time_stream.buffer
    except KeyboardInterrupt:
        result["success"] = False
        result["error"] = "Exécution interrompue par l'utilisateur"
        main_window.output_viewer.append("\n\n[Exécution interrompue par l'utilisateur]")
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        # Show the error in the output view
        main_window.output_viewer.append(f"\nError: {str(e)}")
    finally:
        # Restore stdout and the original input function
        sys.stdout = old_stdout
        __builtins__["input"] = original_input
        
        # Make sure the output viewer is read-only again
        main_window.output_viewer.setReadOnly(True)
        
        # Ensure execution flag is reset
        main_window.is_executing = False
    
    return result

def patch_real_time_execution():
    """Patch the FrenchAlgorithmCompiler to use real-time execution."""
    from FrenchAlgorithmCompiler import FrenchAlgorithmCompiler
    # Save original method reference for potential restoration
    FrenchAlgorithmCompiler._original_execute = FrenchAlgorithmCompiler.execute
    # Replace with our patched method
    FrenchAlgorithmCompiler.execute = patched_execute
    return True

class ConsoleInput:
    """Handles console-style input in the output tab"""
    def __init__(self, output_widget):
        self.output_widget = output_widget
        self.input_buffer = ""
        self.input_ready = False
        self.current_prompt = ""
        
        # Connect to key press events of the output widget
        self.output_widget.keyPressEvent = self.handle_key_press
        # Make output widget editable temporarily when input is requested
        self.output_widget.setReadOnly(False)
        
    def handle_key_press(self, event):
        """Custom key press handler for the output widget"""
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QTextEdit
        
        # Only process keys if we're waiting for input
        if not self.input_ready:
            # Pass the event to the parent class
            QTextEdit.keyPressEvent(self.output_widget, event)
            return
            
        # Get cursor position
        cursor = self.output_widget.textCursor()
        
        # Check if Enter/Return key is pressed
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Extract the text from the current line
            cursor.movePosition(cursor.EndOfLine)
            self.input_buffer = self.get_current_line().strip()
            
            # Move to the next line
            cursor.insertText("\n")
            self.output_widget.setTextCursor(cursor)
            
            # Signal that input is complete
            self.input_ready = False
            self.output_widget.setReadOnly(True)
            
        # Handle backspace only if we're in the input area
        elif event.key() == Qt.Key_Backspace:
            # Check if we're past the prompt position
            line = self.get_current_line()
            if len(line) > len(self.current_prompt):
                # Allow backspace
                QTextEdit.keyPressEvent(self.output_widget, event)
            
        # Regular character input - only allow if we're in the input zone
        elif event.text():
            # Only allow typing at the end of the document
            cursor.movePosition(cursor.End)
            self.output_widget.setTextCursor(cursor)
            QTextEdit.keyPressEvent(self.output_widget, event)
            
        # Other keys (navigation, etc.)
        else:
            QTextEdit.keyPressEvent(self.output_widget, event)
    
    def get_current_line(self):
        """Get the text in the current line"""
        cursor = self.output_widget.textCursor()
        cursor.movePosition(cursor.StartOfLine)
        end_cursor = self.output_widget.textCursor()
        end_cursor.movePosition(end_cursor.EndOfLine)
        return self.output_widget.toPlainText()[cursor.position():end_cursor.position()]
    
    def get_input(self, prompt=""):
        """Get input from the user with a prompt"""
        from PyQt5.QtCore import QEventLoop, QCoreApplication
        
        # Store the prompt
        self.current_prompt = prompt
        
        # Display the prompt in the output widget
        cursor = self.output_widget.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(prompt)
        self.output_widget.setTextCursor(cursor)
        
        # Allow editing and set flag that we're waiting for input
        self.output_widget.setReadOnly(False)
        self.input_ready = True
        
        # Create an event loop to wait for input
        loop = QEventLoop()
        
        # Function to check if input is ready
        def check_input():
            if not self.input_ready:
                loop.quit()
                return True
            return False
        
        # Check periodically if input is ready
        while self.input_ready:
            QCoreApplication.processEvents()
            if check_input():
                break
        
        return self.input_buffer