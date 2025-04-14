import re
import ast
import tempfile
import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QTextCursor


class AlgorithmCompiler:
    def __init__(self, editor, output_viewer, python_viewer, status_bar):
        """
        Initialize the compiler with necessary UI components.
        
        Args:
            editor: The code editor widget
            output_viewer: The output display widget
            python_viewer: The Python code display widget
            status_bar: The status bar widget for displaying messages
        """
        self.editor = editor
        self.output_viewer = output_viewer
        self.python_viewer = python_viewer
        self.status_bar = status_bar
        self.python_code_loaded = False
        self.temp_py_file = None
        self.compiler = None  # Will be set by the main class

    def check_common_syntax_errors(self, algorithm_code):
        """Check for common syntax errors in the algorithm code and provide helpful error messages."""
        errors = []
        algo_lines = algorithm_code.strip().split('\n')
        
        # Track variable declarations
        declared_vars = set()
        declared_consts = set()  # Track constants separately
        in_var_section = False
        in_const_section = False
        in_main_section = False
        
        used_vars = set()
        control_structure_stack = []
        
        # Add mathematical functions to the list of recognized keywords
        math_functions = ["racine", "abs", "sin", "cos", "tan", "ln", "exp", "power", "sqrt","sortir","pas"]
        
        for i, line in enumerate(algo_lines):
            line_num = i + 1
            original_line = line  # Keep original for error reporting
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Skip comment lines (starting with //)
            if line.startswith("//"):
                continue
                
            # For lines with inline comments, strip the comment part
            if "//" in line:
                line = line.split("//")[0].strip()
                if not line:  # Skip if line is empty after removing comment
                    continue
                
            line_lower = line.lower()
            
            # Track sections - case insensitive
            if re.match(r'^var\b', line_lower):
                in_var_section = True
                in_const_section = False
                in_main_section = False
                continue
            elif re.match(r'^const\b', line_lower):
                in_var_section = False
                in_const_section = True
                in_main_section = False
                continue
            elif re.match(r'^debut\b', line_lower):
                in_var_section = False
                in_const_section = False
                in_main_section = True
                continue
                
            # Parse variable declarations in VAR section (only if there's content)
            if in_var_section and ":" in line:
                var_names = line.split(':')[0].split(',')
                for var_name in var_names:
                    var_name = var_name.strip()
                    if var_name:
                        declared_vars.add(var_name.lower())
            
            # Parse constant declarations in CONST section
            if in_const_section and "=" in line:
                parts = line.split("=")[0].strip()
                # Handle multiple constants on one line (e.g., "CONST_A, CONST_B = 5;")
                const_names = parts.split(',')
                for const_name in const_names:
                    const_name = const_name.strip()
                    if const_name:
                        declared_consts.add(const_name.lower())
                        # Also add to declared_vars to simplify usage checking
                        declared_vars.add(const_name.lower())
            
            # Check for missing semicolons in main section
            if in_main_section:
                # Case-insensitive check for statements requiring semicolons
                contains_lire = re.search(r'\blire\s*\(', line_lower)
                contains_ecrire = re.search(r'\becrire\s*\(', line_lower)
                contains_assignment = "<-" in line_lower
                
                # Check if the line should end with semicolon but doesn't
                if (contains_lire or contains_ecrire or contains_assignment) and not line_lower.rstrip().endswith(";"):
                    if contains_lire:
                        errors.append((line_num, original_line, "Il manque un point-virgule (;) à la fin de l'instruction 'lire'. Format correct: lire(variable1, variable2, ...);"))
                    elif contains_ecrire:
                        errors.append((line_num, original_line, "Il manque un point-virgule (;) à la fin de l'instruction 'ecrire'. Format correct: ecrire(expression1, expression2, ...);"))
                    else:
                        errors.append((line_num, original_line, "Il manque un point-virgule (;) à la fin de cette instruction d'affectation. Format correct: variable <- valeur;"))
            
            # Check control structures - si/alors
            if re.match(r'^\bsi\b\s', line_lower):
                if "alors" not in line_lower:
                    errors.append((line_num, original_line, "Instruction 'si' sans le mot-clé 'alors'. Format correct: 'si condition alors'"))
                control_structure_stack.append(("si", line_num))
                
            # Check for 'pour' loop structure with multiple valid formats
            if re.match(r'^\bpour\b\s', line_lower):
                # Check for required 'faire' keyword
                if "faire" not in line_lower:
                    errors.append((line_num, original_line, "Boucle 'pour' sans le mot-clé 'faire'. Format attendu: 'pour variable de/allant de valeur1 a/allant a valeur2 faire'"))
                
                # Check for valid 'pour' loop syntax variations
                has_valid_pour_syntax = (
                    # pour var de val1 a val2 faire
                    (re.search(r'\bde\b', line_lower) and re.search(r'\ba\b', line_lower)) or
                    # pour var allant de val1 a val2 faire
                    (re.search(r'\ballant\s+de\b', line_lower) and re.search(r'\ba\b', line_lower)) or
                    # pour var de val1 allant a val2 faire
                    (re.search(r'\bde\b', line_lower) and re.search(r'\ballant\s+a\b', line_lower))
                )
                
                if not has_valid_pour_syntax:
                    errors.append((line_num, original_line, "Syntaxe incorrecte pour la boucle 'pour'. Formats valides: 'pour var de val1 a val2 faire', 'pour var allant de val1 a val2 faire', 'pour var de val1 allant a val2 faire'"))
                    
                control_structure_stack.append(("pour", line_num))
                
            # Check for 'tantque' loop structure
            if re.match(r'^\btantque\b\s', line_lower):
                if "faire" not in line_lower:
                    errors.append((line_num, original_line, "Boucle 'tantque' sans le mot-clé 'faire'. Format correct: 'tantque condition faire'"))
                control_structure_stack.append(("tantque", line_num))
                
            # Check for closing control structures - case insensitive
            if re.match(r'^\bfinsi\b', line_lower):
                if not control_structure_stack or control_structure_stack[-1][0] != "si":
                    errors.append((line_num, original_line, "'finsi' sans 'si' correspondant."))
                elif control_structure_stack:
                    control_structure_stack.pop()
                    
            if re.match(r'^\bfinpour\b', line_lower):
                if not control_structure_stack or control_structure_stack[-1][0] != "pour":
                    errors.append((line_num, original_line, "'finpour' sans 'pour' correspondant."))
                elif control_structure_stack:
                    control_structure_stack.pop()
                    
            if re.match(r'^\bfintantque\b', line_lower):
                if not control_structure_stack or control_structure_stack[-1][0] != "tantque":
                    errors.append((line_num, original_line, "'fintantque' sans 'tantque' correspondant."))
                elif control_structure_stack:
                    control_structure_stack.pop()
                    
            # Extract variable usage in main section
            if in_main_section:
                # First, handle math function calls to exclude their parameters from variable checking
                math_function_pattern = '|'.join(math_functions)
                
                # Skip analyzing variables inside string literals
                line_without_strings = re.sub(r'"[^"]*"', '', line)
                
                # Pre-processing to ignore all math functions
                # Find and replace all math functions with their parameters
                for func in math_functions:
                    # Replace func(whatever) with a marker
                    func_pattern = rf'\b{func}\s*\([^)]*\)'
                    line_without_strings = re.sub(func_pattern, f"__{func}_CALL__", line_without_strings, flags=re.IGNORECASE)
                
                # Simple regex-free variable usage detection
                potential_vars = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', line_without_strings)
                for var in potential_vars:
                    var_lower = var.lower()
                    # Ignore keywords, function names, and math functions - all lowercase for case insensitivity
                    keywords = ["si", "alors", "sinon", "finsi", "pour", "allant", "a", "faire", 
                               "finpour", "tantque", "fintantque", "lire", "ecrire", "de",
                               "et", "ou", "non", "mod", "div", "power", "vrai", "faux"]
                    
                    # Add math functions to the ignored keywords
                    all_keywords = keywords + math_functions
                    
                    # Ignore function call markers and keywords
                    if (var_lower not in all_keywords and 
                        not re.match(rf'^{re.escape(var_lower)}:', line_lower) and 
                        not var_lower in ["algorithme", "var", "const", "debut", "fin"] and
                        not var_lower.startswith("__") and not var_lower.endswith("_call__")):
                        used_vars.add(var_lower)
        
        # Check for unclosed control structures at the end
        for struct_type, line_num in control_structure_stack:
            end_keyword = "fin" + struct_type
            errors.append((line_num, algo_lines[line_num-1], 
                          f"Structure '{struct_type}' non fermée. Il manque '{end_keyword}'."))
        
        # Check for variables used but not declared (in either Var or Const sections)
        undeclared_vars = used_vars - declared_vars
        if undeclared_vars and len(undeclared_vars) <= 10:  # Limit to avoid excessive errors
            for var in undeclared_vars:
                # Don't report errors for literals that might be used inside math functions
                if var.isdigit() or var in ["256", "true", "false"]:
                    continue
                    
                # Find line where the variable is first used
                for i, line in enumerate(algo_lines):
                    # Skip comment lines
                    if line.strip().startswith("//"):
                        continue
                        
                    # Remove comment part from lines with inline comments
                    if "//" in line:
                        line = line.split("//")[0]
                        
                    line_without_strings = re.sub(r'"[^"]*"', '', line)
                    
                    # Pre-processing to ignore all math functions in the search
                    temp_line = line_without_strings
                    for func in math_functions:
                        func_pattern = rf'\b{func}\s*\([^)]*\)'
                        temp_line = re.sub(func_pattern, f"__{func}_CALL__", temp_line, flags=re.IGNORECASE)
                    
                    if var.lower() in temp_line.lower():
                        # Check if var is part of a math function call
                        in_math_func = False
                        for func in math_functions:
                            if re.search(rf'\b{func}\s*\([^)]*{var}[^)]*\)', line_without_strings, re.IGNORECASE):
                                in_math_func = True
                                break
                        
                        # Skip numeric literals that may have been wrongly identified as variables
                        if not in_math_func and not var.isdigit():
                            errors.append((i+1, line, 
                                        f"Variable '{var}' utilisée mais non déclarée dans la section 'Var' ou 'Const'."))
                            break
        
        return errors
    
    def compile_algorithm(self, switch_tab=True):
        algorithm_code = self.editor.toPlainText()
        
        if not algorithm_code.strip():
            QMessageBox.warning(None, "Compilation", "L'éditeur est vide. Rien à compiler.")
            return None
        
        # Check for common syntax errors before compilation
        syntax_errors = self.check_common_syntax_errors(algorithm_code)
        if syntax_errors:
            # Show the first error and highlight it in the editor
            line_num, line, error_msg = syntax_errors[0]
            
            # Set cursor to the error line
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            for _ in range(line_num - 1):
                cursor.movePosition(QTextCursor.Down)
            
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
            
            self.editor.setTextCursor(cursor)
            self.editor.ensureCursorVisible()
            
            # Show detailed error message with line information
            full_error_msg = f"Erreur de syntaxe à la ligne {line_num}:\n\n\"{line}\"\n\n{error_msg}"
            
            # If there are multiple errors, indicate this
            if len(syntax_errors) > 1:
                full_error_msg += f"\n\nIl y a {len(syntax_errors)} erreurs au total. Corrigez celle-ci et recompilez."
            
            QMessageBox.critical(None, "Erreur de syntaxe", full_error_msg)
            self.status_bar.showMessage("Erreur de compilation - Syntaxe invalide")
            return None
        
        # MODIFICATION: Prétraiter le code pour remplacer racine par sqrt avant compilation
        # Cette modification n'affecte pas le code de l'algorithme original
        original_code = algorithm_code  # Garder l'original intact
        processed_algorithm_code = algorithm_code
        
        # Remplacer racine(...) par sqrt(...) pour la compilation
        if "racine" in processed_algorithm_code:
            processed_algorithm_code = re.sub(r'racine\s*\(', r'math.sqrt(', processed_algorithm_code)
        
        try:
            # Try to compile the algorithm to Python, using the processed code
            python_code = self.compiler.compile_to_python(processed_algorithm_code)
            
            # Store mapping between Python lines and algorithm lines
            if hasattr(self.compiler, 'line_mapping'):
                line_mapping = self.compiler.line_mapping
            else:
                # If no mapping is available, we'll try to infer it
                line_mapping = self._generate_line_mapping(original_code, python_code)  # Utiliser original_code ici
            
            # Check if the generated Python code is valid Python syntax
            try:
                ast.parse(python_code)
            except SyntaxError as py_syntax_error:
                py_error_line = py_syntax_error.lineno
                error_offset = py_syntax_error.offset
                error_text = py_syntax_error.text if py_syntax_error.text else "Unknown"
                
                # Try to map the Python error line back to the algorithm line
                algo_line_num = self._map_python_to_algo_line(py_error_line, line_mapping)
                
                # Find the offending algorithm line
                algo_lines = original_code.strip().split('\n')  # Utiliser original_code ici
                if 0 <= algo_line_num - 1 < len(algo_lines):
                    algo_line_text = algo_lines[algo_line_num - 1]
                    
                    # Highlight the algorithm line in the editor
                    cursor = self.editor.textCursor()
                    cursor.movePosition(QTextCursor.Start)
                    for _ in range(algo_line_num - 1):
                        cursor.movePosition(QTextCursor.Down)
                    
                    cursor.movePosition(QTextCursor.StartOfLine)
                    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                    
                    self.editor.setTextCursor(cursor)
                    self.editor.ensureCursorVisible()
                    
                    # Display error message with algorithm line information
                    error_msg = f"Erreur de syntaxe dans votre algorithme à la ligne {algo_line_num}:\n\n\"{algo_line_text}\"\n\n"
                    error_msg += f"Cette erreur a généré un code Python invalide."
                else:
                    error_msg = f"Erreur de syntaxe Python générée à la ligne {py_error_line}:\n{error_text}\n"
                    error_msg += f"Cette erreur indique probablement un problème dans votre algorithme original."
                
                QMessageBox.critical(None, "Erreur de syntaxe", error_msg)
                self.status_bar.showMessage("Erreur de compilation - Syntaxe invalide")
                return None
            
            # MODIFICATION: Ajout du module math si sqrt est utilisé
            if "sqrt(" in python_code and "import math" not in python_code:
                python_code = "import math\n" + python_code
            
            # Update Python code viewer
            self.python_viewer.setPlainText(python_code)
            self.python_code_loaded = True
            
            # Show success message
            self.status_bar.showMessage("Compilation réussie")
            QMessageBox.information(None, "Compilation", "Compilation réussie! Aucune erreur détectée.")
            
            # Save Python code to temporary file
            self.temp_py_file = tempfile.NamedTemporaryFile(suffix='.py', delete=False)
            with open(self.temp_py_file.name, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            return python_code
            
        except Exception as e:
            # Si une erreur se produit spécifiquement avec la fonction racine
            error_msg = str(e)
            if "racine" in error_msg or "sqrt" in error_msg:
                error_msg = f"Erreur lors de la compilation: Le compilateur ne reconnaît pas la fonction 'racine'.\n\n"
                error_msg += "Solution possible: Utilisez 'racine' ou 'sqrt' et assurez-vous que le compilateur supporte cette fonction."
            else:
                error_msg = f"Erreur lors de la compilation: {str(e)}"
            
            QMessageBox.critical(None, "Erreur de compilation", error_msg)
            self.status_bar.showMessage("Erreur de compilation")
            return None
            
        except Exception as e:
            # Create a more detailed error message with line information if available
            error_msg = f"Erreur lors de la compilation: {str(e)}"
            
            # Check for specific error patterns in the original algorithm code
            algo_lines = algorithm_code.strip().split('\n')
            for i, line in enumerate(algo_lines):
                line_lower = line.lower().strip()
                
                # Check for common syntax errors
                if (line_lower.startswith("pour ") and "faire" not in line_lower) or \
                   (line_lower.startswith("tantque ") and "faire" not in line_lower) or \
                   (line_lower.startswith("si ") and "alors" not in line_lower):
                    # Highlight this line as it's likely the problem
                    cursor = self.editor.textCursor()
                    cursor.movePosition(QTextCursor.Start)
                    for _ in range(i):
                        cursor.movePosition(QTextCursor.Down)
                    
                    cursor.movePosition(QTextCursor.StartOfLine)
                    cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
                    
                    self.editor.setTextCursor(cursor)
                    self.editor.ensureCursorVisible()
                    
                    # Create a specific error message based on the line's structure
                    if line_lower.startswith("pour "):
                        specific_error = "Il manque probablement le mot clé 'faire' dans cette boucle."
                    elif line_lower.startswith("tantque "):
                        specific_error = "Il manque probablement le mot clé 'faire' dans cette boucle."
                    elif line_lower.startswith("si "):
                        specific_error = "Il manque probablement le mot clé 'alors' dans cette condition."
                    else:
                        specific_error = "Structure de contrôle incomplète."
                    
                    error_msg = f"Erreur de syntaxe à la ligne {i+1}:\n\n\"{line}\"\n\n{specific_error}"
                    break
            
            QMessageBox.critical(None, "Erreur de compilation", error_msg)
            self.status_bar.showMessage("Erreur de compilation")
            return None

    def _generate_line_mapping(self, algorithm_code, python_code):
        """Generate a basic mapping between algorithm lines and Python code lines.
        This is a fallback when the compiler doesn't provide a mapping."""
        algo_lines = algorithm_code.strip().split('\n')
        python_lines = python_code.strip().split('\n')
        
        mapping = {}
        algo_line_num = 1
        
        # Simple heuristic mapping - this is a basic implementation
        # A more sophisticated algorithm would use pattern matching or annotations
        for py_line_num, py_line in enumerate(python_lines, 1):
            # Look for Python comments that might reference algorithm line numbers
            if "# Algorithm line" in py_line:
                try:
                    algo_line_ref = int(re.search(r"# Algorithm line (\d+)", py_line).group(1))
                    mapping[py_line_num] = algo_line_ref
                except (AttributeError, ValueError):
                    # If no valid line reference, use incremental mapping
                    mapping[py_line_num] = algo_line_num
                    algo_line_num += 1
            else:
                # Basic incremental mapping as fallback
                mapping[py_line_num] = min(algo_line_num, len(algo_lines))
                
                # Advance algo line for non-empty Python lines that appear to be statements
                if py_line.strip() and not py_line.strip().startswith('#'):
                    algo_line_num = min(algo_line_num + 1, len(algo_lines))
        
        return mapping

    def _map_python_to_algo_line(self, python_line_num, line_mapping):
        """Map a Python code line number back to the corresponding algorithm line number."""
        # Direct lookup if available
        if python_line_num in line_mapping:
            return line_mapping[python_line_num]
        
        # Find the closest match if exact line not found
        closest_line = 1
        closest_distance = float('inf')
        
        for py_line, algo_line in line_mapping.items():
            distance = abs(py_line - python_line_num)
            if distance < closest_distance:
                closest_distance = distance
                closest_line = algo_line
        
        return closest_line

    def run_algorithm(self, tabs, python_tab_added):
        # First compile the algorithm
        python_code = self.compile_algorithm(switch_tab=False)
        
        if not python_code:
            return
        
        # Switch to output tab before running
        # Find the correct index of the output tab which depends on whether Python tab is visible
        output_tab_index = 2 if python_tab_added else 1
        tabs.setCurrentIndex(output_tab_index)
        
        # Clear output
        self.clear_output()
        
        try:
            result = self.compiler.execute(python_code)
            
            # No need to update output viewer here as it's done in real-time now
            if result["success"]:
                self.status_bar.showMessage("Exécution réussie")
            else:
                self.status_bar.showMessage("Erreur d'exécution")
        except Exception as e:
            # Only display exceptions not caught by the execution
            self.output_viewer.setPlainText(f"Erreur d'exécution: {str(e)}")
            self.status_bar.showMessage("Erreur d'exécution")

    def handle_execution_result(self, result):
        # Clear previous output
        self.output_viewer.clear()
        
        # Update output viewer with appropriate color
        if result["success"]:
            self.append_colored_text(result["output"], "#000000")  # Black text
            self.status_bar.showMessage("Exécution réussie")
        else:
            self.append_colored_text(f"Erreur d'exécution: {result['error']}", "#FF0000")  # Red for errors
            self.status_bar.showMessage("Erreur d'exécution")
    
    def clear_output(self):
        self.output_viewer.clear()
        cursor = self.output_viewer.textCursor()
        cursor.movePosition(cursor.Start)
        self.output_viewer.setTextCursor(cursor)
        
    def append_colored_text(self, text, color="#E0E0E0"):
        from PyQt5.QtGui import QTextCharFormat, QColor
        cursor = self.output_viewer.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        cursor.mergeCharFormat(format)
        cursor.insertText(text)
        self.output_viewer.setTextCursor(cursor)