import sys
from io import StringIO
import queue
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QSettings

# Using the InputDialog class defined above

class PyQtInputFixer:
    @staticmethod
    def patch_compiler(compiler_instance):
        original_execute = compiler_instance.execute
        
        def new_execute(python_code):
            # Redirect stdout to capture output
            old_stdout = sys.stdout
            redirected_output = StringIO()
            sys.stdout = redirected_output
            
            # Create a queue for input operations
            input_queue = queue.Queue()
            
            # Create a custom input function
            def custom_input(prompt=""):
                # Print the prompt to the redirected output
                print(prompt, end="")
                
                # Create input dialog and show it
                dialog = InputDialog(prompt)
                if dialog.exec_() == QDialog.Accepted:
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
                exec(python_code)
                result["output"] = redirected_output.getvalue()
            except Exception as e:
                result["success"] = False
                result["error"] = str(e)
            finally:
                # Restore stdout and the original input function
                sys.stdout = old_stdout
                __builtins__["input"] = original_input
            
            return result
            
        # Replace the execute method
        compiler_instance.execute = new_execute
        return compiler_instance