import re

class RealTimeStream:
    """Custom stream that sends output in real-time to a QTextEdit widget."""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""
        
    def write(self, text):
        from PyQt5.QtCore import QCoreApplication
        # Append text to the output widget
        self.buffer += text
        self.text_widget.append(text)
        # Ensure UI updates immediately
        QCoreApplication.processEvents()
        return len(text)
        
    def flush(self):
        pass
        
class FrenchAlgorithmCompiler:
    def __init__(self, max_steps=None):
        # Make type mappings more flexible with lowercase keys - Added boolean and char types
        self.type_mapping = {
            "entier": "int",
            "reel": "float",
            "réel": "float",
            "chaine de caractere": "str",
            "chaine de caractères": "str",
            "chaîne de caractère": "str",
            "chaîne de caractères": "str",
            "booleen": "bool",
            "booléen": "bool",
            "boolean": "bool",
            "caractere": "char",
            "caractère": "char",
            "char": "char"
        }
        
        # Add logical operator translations
        self.logical_operators = {
            " mod ": " % ",
            " div ": " // ",
            " et ": " and ",
            " ou ": " or ",
            " non ": " not ",
            "non(": "not(",  # Handle the case without space
            "non (": "not ("  # Handle the case with space
        }
        
        # Add comparison operator translations
        self.comparison_operators = {
            "<>": "!="
            
        }
        
        # Maximum execution steps to prevent infinite loops
        if max_steps is not None:
            self.max_execution_steps = max_steps
        else:
            # Try to get from settings
            from PyQt5.QtCore import QSettings
            settings = QSettings("AlgoFX", "AlgoFX")
            self.max_execution_steps = settings.value("algorithm_execution_steps", 1000, type=int)
        
        
        self.indentation_level = 0
        self.current_variables = {}
        self.constants = {}
        
    def parse_variables(self, var_section):
        """Parse variable declarations"""
        variables = {}
        lines = var_section.strip().split('\n')
        i = 0
        
        # Parse regular variables
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            
            if not line or line.startswith('//'):
                continue
                
            # Check if we've reached the constants section - case insensitive
            if line.lower() == "const":
                break
                
            if ':' in line:
                var_names, var_type = line.split(':', 1)
                var_names = var_names.strip()
                var_type = var_type.strip().rstrip(';').lower()  # Ensure lowercase for comparison
                
                # Handle multiple variables separated by commas
                for var_name in var_names.split(','):
                    var_name = var_name.strip()
                    # Check if type exists in our mapping (case-insensitive)
                    if var_name:
                        for k, v in self.type_mapping.items():
                            if k.lower() == var_type.lower():
                                variables[var_name] = v
                                break
        
        # Parse constants if we found the const keyword
        if i < len(lines):
            self.parse_constants(lines[i:])
            
        return variables
        
    def parse_constants(self, const_lines):
        """Parse constant declarations"""
        self.constants = {}
        for line in const_lines:
            line = line.strip()
            
            if not line or line.startswith('//'):
                continue
                
            if '=' in line:
                const_name, const_value = line.split('=', 1)
                const_name = const_name.strip()
                const_value = const_value.strip().rstrip(';')
                
                # Try to determine the constant type - case insensitive check for vrai/faux
                if const_value.lower() in ["vrai", "true"]:
                    self.constants[const_name] = ("bool", "True")
                elif const_value.lower() in ["faux", "false"]:
                    self.constants[const_name] = ("bool", "False")
                elif const_value.isdigit():
                    self.constants[const_name] = ("int", const_value)
                elif const_value.replace('.', '', 1).isdigit() and const_value.count('.') == 1:
                    self.constants[const_name] = ("float", const_value)
                elif (const_value.startswith('"') and const_value.endswith('"')) or \
                     (const_value.startswith("'") and const_value.endswith("'")):
                    # Single character in quotes is char type
                    if len(const_value) == 3 and const_value[0] in ["'", '"'] and const_value[2] in ["'", '"']:
                        self.constants[const_name] = ("char", const_value)
                    else:
                        self.constants[const_name] = ("str", const_value)
                else:
                    # Default to string if type can't be determined
                    self.constants[const_name] = ("str", f'"{const_value}"')
    
    def translate_logical_operators(self, condition):
        """Translate French logical operators to Python equivalents"""
        result = condition
        
        # First handle the "non" operator specially when inside parentheses
        if "non (" in result.lower():
            result = result.replace("non (", "not (")
            result = result.replace("Non (", "not (")
            result = result.replace("NON (", "not (")
        
        # Then handle the regular "non" operator when it's a standalone word
        result = result.replace(" non ", " not ")
        result = result.replace(" Non ", " not ")
        result = result.replace(" NON ", " not ")
        
        # Handle other logical operators
        for fr_op, py_op in self.logical_operators.items():
            # Handle case insensitivity in all forms: lowercase, uppercase, title case
            result = result.replace(fr_op.lower(), py_op)
            result = result.replace(fr_op.upper(), py_op)
            result = result.replace(fr_op.title(), py_op)
            
        # Handle French boolean values - with word boundary checks
        result = result.replace(" vrai ", " True ")
        result = result.replace(" VRAI ", " True ")
        result = result.replace(" Vrai ", " True ")
        result = result.replace(" faux ", " False ")
        result = result.replace(" FAUX ", " False ")
        result = result.replace(" Faux ", " False ")
        
        # Handle vrai/faux at beginning of string or condition
        if result.startswith("vrai "):
            result = "True" + result[4:]
        elif result.startswith("VRAI "):
            result = "True" + result[5:]
        elif result.startswith("Vrai "):
            result = "True" + result[5:]
        elif result.startswith("faux "):
            result = "False" + result[5:]
        elif result.startswith("FAUX "):
            result = "False" + result[5:]
        elif result.startswith("Faux "):
            result = "False" + result[5:]
        
        # Handle vrai/faux at end of string or condition
        if result.endswith(" vrai"):
            result = result[:-5] + " True"
        elif result.endswith(" VRAI"):
            result = result[:-5] + " True"
        elif result.endswith(" Vrai"):
            result = result[:-5] + " True"
        elif result.endswith(" faux"):
            result = result[:-5] + " False"
        elif result.endswith(" FAUX"):
            result = result[:-5] + " False"
        elif result.endswith(" Faux"):
            result = result[:-5] + " False"
        
        # Handle standalone vrai/faux
        if result == "vrai":
            result = "True"
        elif result == "VRAI":
            result = "True"
        elif result == "Vrai":
            result = "True"
        elif result == "faux":
            result = "False"
        elif result == "FAUX":
            result = "False"
        elif result == "Faux":
            result = "False"
        
        # Handle comparison operators
        for fr_op, py_op in self.comparison_operators.items():
            result = result.replace(fr_op, py_op)
            
        return result
    
    def translate_instruction(self, line):
        """Translate a single instruction from French to Python"""
        # Remove comments
        if '//' in line:
            line = line.split('//', 1)[0]
                
        line = line.strip()
        if not line:
            return ""
                
        # Case-insensitive check for keywords
        line_lower = line.lower()
        
        # Check for the 'sortir' keyword (with or without semicolon)
        if line_lower == "sortir" or line_lower == "sortir;":
            return ' ' * 4 * self.indentation_level + "break"
            
        # Translate comparison operators
        for fr_op, py_op in self.comparison_operators.items():
            line = line.replace(fr_op, py_op)
            
        # Import math module for square root if needed
        if 'racine(' in line_lower:
            # We'll prepend the import at the beginning of the translated code
            self.needs_math_import = True
            
        # Translate mathematical operations
        if ' div ' in line_lower:
            line = line.replace(line[line_lower.find(' div '):line_lower.find(' div ')+5], ' // ')
        
        if ' mod ' in line_lower:
            line = line.replace(line[line_lower.find(' mod '):line_lower.find(' mod ')+5], ' % ')
        
        if ' puissance ' in line_lower:
            line = line.replace(line[line_lower.find(' puissance '):line_lower.find(' puissance ')+11], ' ** ')
            
        # Handle square root function - find all instances case-insensitively
        racine_variants = ['racine(', 'RACINE(', 'Racine(']
        for variant in racine_variants:
            if variant.lower() in line_lower:
                # Find actual position in original string
                pos = line_lower.find(variant.lower())
                # Replace in original string preserving case
                actual_variant = line[pos:pos+len(variant)]
                line = line.replace(actual_variant, 'math.sqrt(')
                
        # Input function handling - case insensitive and with accents
        input_variants = ['lire(', 'Lire(', 'LIRE(']
        for variant in input_variants:
            # Check without comparing case
            if variant.lower() in line_lower and line.endswith(');'):
                # Extract the actual variant used in the line
                start_pos = line_lower.find(variant.lower())
                end_pos = line.find('(', start_pos) + 1
                actual_variant = line[start_pos:end_pos]
                
                var_names = line[line.find("(")+1:line.find(")")].strip().split(',')
                python_code = []
                
                for var_name in var_names:
                    var_name = var_name.strip()
                    # Look up the variable type and add appropriate conversion
                    if var_name in self.current_variables:
                        var_type = self.current_variables[var_name]
                        if var_type == "int":
                            python_code.append(f"{var_name} = int(input(\"Entrez {var_name}: \"))")
                        elif var_type == "float":
                            python_code.append(f"{var_name} = float(input(\"Entrez {var_name}: \"))")
                        elif var_type == "bool":
                            python_code.append(f"_input = input(\"Entrez {var_name} (vrai/faux): \").lower()")
                            python_code.append(f"{var_name} = _input in ['vrai', 'true', '1']")
                        elif var_type == "char":
                            python_code.append(f"_input = input(\"Entrez {var_name}: \")")
                            python_code.append(f"{var_name} = _input[0] if _input else ''")
                        else:
                            python_code.append(f"{var_name} = input(\"Entrez {var_name}: \")")
                    else:
                        python_code.append(f"{var_name} = input(\"Entrez {var_name}: \")")
                
                return '\n'.join([' ' * 4 * self.indentation_level + line for line in python_code])
                
        # Output function handling - case insensitive and with accents
        output_variants = ['ecrire(', 'Ecrire(', 'ECRIRE(', 'écrire(', 'Écrire(', 'ÉCRIRE(']
        for variant in output_variants:
            # Check without comparing case
            if variant.lower() in line_lower and line.endswith(');'):
                # Extract the actual variant used in the line
                start_pos = line_lower.find(variant.lower())
                end_pos = line.find('(', start_pos) + 1
                actual_variant = line[start_pos:end_pos]
                
                content = line[line.find("(")+1:line.find(")")].strip()
                
                # Process each item for printing
                if ',' in content:
                    items = [item.strip() for item in content.split(',')]
                    processed_items = []
                    
                    for item in items:
                        # Check if this is a variable that's a boolean
                        if item in self.current_variables and self.current_variables[item] == "bool":
                            processed_items.append(f"'vrai' if {item} else 'faux'")
                        else:
                            processed_items.append(item)
                    
                    return ' ' * 4 * self.indentation_level + f"print({', '.join(processed_items)})"
                else:
                    # Single item
                    if content in self.current_variables and self.current_variables[content] == "bool":
                        return ' ' * 4 * self.indentation_level + f"print('vrai' if {content} else 'faux')"
                    else:
                        return ' ' * 4 * self.indentation_level + f"print({content})"
                
        # Assignment statements
        if "<-" in line:
            return ' ' * 4 * self.indentation_level + line.replace("<-", "=").rstrip(';')
                
        # Skip end statements for control structures - case insensitive
        if line_lower in ["finsi", "fintantque", "finpour"]:
            return ""
                
        # Control structures - these will be handled in parse_instructions
        return ' ' * 4 * self.indentation_level + line
    
    def parse_instructions(self, instruction_section):
        """Parse the instruction section and translate to Python"""
        lines = instruction_section.strip().split('\n')
        python_code = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            line_lower = line.lower()  # Convert to lowercase for case-insensitive matching
            
            # Skip empty lines and comments
            if not line or line.startswith('//'):
                i += 1
                continue
                
            # If-then-else structure - now fully case insensitive
            # Match "si" followed by " alors" in any case
            if line_lower.startswith("si ") and " alors" in line_lower:
                # Find the indices in the lowercase version
                alors_idx = line_lower.find(" alors")
                # Use the original line with the indices from the lowercase version
                condition = line[3:alors_idx].strip()
                
                # Translate logical operators
                python_condition = self.translate_logical_operators(condition)
                python_code.append(' ' * 4 * self.indentation_level + f"if {python_condition}:")
                
                self.indentation_level += 1
                j = i + 1
                nesting_level = 1
                
                # Find the matching finsi or sinon, accounting for nested structures
                while j < len(lines) and nesting_level > 0:
                    curr_line = lines[j].strip().lower()  # Convert to lowercase for comparison
                    if curr_line.startswith("si ") and " alors" in curr_line:
                        nesting_level += 1
                    # Improved to check if the line contains finsi rather than exact match
                    elif "finsi" in curr_line:
                        nesting_level -= 1
                    # Improved to check if the line contains sinon rather than exact match
                    elif "sinon" in curr_line and nesting_level == 1:
                        # Only break at "sinon" if we're at the same nesting level
                        break
                    j += 1
                
                # Process if block
                if_block = '\n'.join(lines[i+1:j])
                python_code.extend(self.parse_instructions(if_block))
                
                # Check for else block - case insensitive
                if j < len(lines) and "sinon" in lines[j].strip().lower():
                    self.indentation_level -= 1
                    python_code.append(' ' * 4 * self.indentation_level + "else:")
                    self.indentation_level += 1
                    
                    k = j + 1
                    nesting_level = 1
                    while k < len(lines) and nesting_level > 0:
                        curr_line = lines[k].strip().lower()  # Convert to lowercase for comparison
                        if curr_line.startswith("si ") and " alors" in curr_line:
                            nesting_level += 1
                        # Improved to check if the line contains finsi rather than exact match
                        elif "finsi" in curr_line:
                            nesting_level -= 1
                        k += 1
                    
                    else_block = '\n'.join(lines[j+1:k-1])  # -1 to exclude the finsi
                    python_code.extend(self.parse_instructions(else_block))
                    i = k  # Update i to continue after the else block
                else:
                    i = j  # Update i to continue after the if block
                
                self.indentation_level -= 1
                continue
            
            # While loop - now fully case insensitive
            # Match "tantque" followed by " faire" in any case
            if line_lower.startswith("tantque ") and " faire" in line_lower:
                # Find the indices in the lowercase version
                faire_idx = line_lower.find(" faire")
                # Extract condition using the original line with indices from lowercase version
                condition = line[line_lower.find("tantque ")+8:faire_idx].strip()
                
                # Translate logical operators
                python_condition = self.translate_logical_operators(condition)
                
                # Add counter to prevent infinite loops
                loop_counter_var = f"_loop_counter_{self.indentation_level}"
                python_code.append(' ' * 4 * self.indentation_level + f"{loop_counter_var} = 0")
                python_code.append(' ' * 4 * self.indentation_level + f"while {python_condition}:")
                
                self.indentation_level += 1
                # Add counter increment and check
                python_code.append(' ' * 4 * self.indentation_level + f"{loop_counter_var} += 1")
                python_code.append(' ' * 4 * self.indentation_level + 
                                  f"if {loop_counter_var} > {self.max_execution_steps}:")
                python_code.append(' ' * 4 * (self.indentation_level+1) + 
                                  "raise RuntimeError(\"Possible infinite loop detected!\")")
                
                j = i + 1
                nesting_level = 1
                while j < len(lines) and nesting_level > 0:
                    curr_line = lines[j].strip().lower()  # Convert to lowercase for comparison
                    if curr_line.startswith("tantque ") and " faire" in curr_line:
                        nesting_level += 1
                    # Improved to check if the line contains fintantque rather than exact match
                    elif "fintantque" in curr_line:
                        nesting_level -= 1
                    j += 1
                    
                loop_block = '\n'.join(lines[i+1:j-1])  # -1 to exclude the fintantque
                python_code.extend(self.parse_instructions(loop_block))
                
                self.indentation_level -= 1
                i = j
                continue
            
            # For loop - now fully case insensitive with step support
            # Match "pour" variants, including those with "pas" (step) parameter
            if line_lower.startswith("pour ") and " faire" in line_lower:
                # Common pattern checking
                has_de = " de " in line_lower
                has_allant = " allant " in line_lower
                has_a = " a " in line_lower
                has_à = " à " in line_lower
                has_pas = " pas " in line_lower
                
                # Determine a_pos and a_separator for later use
                if has_a:
                    a_separator = " a "
                    a_pos = line_lower.find(" a ")
                elif has_à:
                    a_separator = " à "
                    a_pos = line_lower.find(" à ")
                else:
                    # If neither "a" nor "à" is found, we can't parse this
                    python_code.append(' ' * 4 * self.indentation_level + f"# Could not parse: {line}")
                    i += 1
                    continue
                
                # Get the original case of the separator from the original line
                orig_a_separator = line[a_pos:a_pos+len(a_separator)]
                
                # Extract variable name, start value, end value, and step value (if present)
                faire_pos = line_lower.find(" faire")
                pas_pos = line_lower.find(" pas ") if has_pas else -1
                
                # Default step value if no "pas" is found
                step_val = "1"
                
                # Extract step value if present, range end is different depending on if pas exists
                if pas_pos != -1:
                    step_val = line[pas_pos+5:faire_pos].strip()
                    range_end = pas_pos
                else:
                    range_end = faire_pos
                
                # Format 1: pour variable de valeur1 a valeur2 [pas valeur3] faire
                if has_de and (has_a or has_à) and not has_allant:
                    de_pos = line_lower.find(" de ")
                    var_name = line[5:de_pos].strip()
                    start_val = line[de_pos+4:a_pos].strip()
                    end_val = line[a_pos+len(orig_a_separator):range_end].strip()
                
                # Format 2: pour variable allant de valeur1 a valeur2 [pas valeur3] faire
                elif has_allant and " allant de " in line_lower and (has_a or has_à):
                    allant_de_pos = line_lower.find(" allant de ")
                    var_name = line[5:allant_de_pos].strip()
                    start_val = line[allant_de_pos+11:a_pos].strip()  # +11 for " allant de "
                    end_val = line[a_pos+len(orig_a_separator):range_end].strip()
                
                # Format 3: pour variable de valeur1 allant a valeur2 [pas valeur3] faire
                elif has_de and has_allant and (has_a or has_à) and " allant " in line_lower:
                    de_pos = line_lower.find(" de ")
                    allant_pos = line_lower.find(" allant ")
                    var_name = line[5:de_pos].strip()
                    start_val = line[de_pos+4:allant_pos].strip()
                    end_val = line[a_pos+len(orig_a_separator):range_end].strip()
                
                # Format 4: pour variable allant a valeur2 [pas valeur3] faire (implied starting from 0)
                elif has_allant and not has_de and (has_a or has_à):
                    allant_pos = line_lower.find(" allant ")
                    var_name = line[5:allant_pos].strip()
                    start_val = "0"  # Default starting value
                    end_val = line[a_pos+len(orig_a_separator):range_end].strip()
                
                else:
                    # If format doesn't match any of the expected patterns
                    python_code.append(' ' * 4 * self.indentation_level + f"# Could not parse: {line}")
                    i += 1
                    continue
                
                # Add counter to prevent infinite loops
                loop_counter_var = f"_loop_counter_{self.indentation_level}"
                python_code.append(' ' * 4 * self.indentation_level + f"{loop_counter_var} = 0")
                
                # Include step parameter in range if specified
                if has_pas:
                    python_code.append(' ' * 4 * self.indentation_level + 
                                    f"for {var_name} in range({start_val}, {end_val} + 1, {step_val}):")
                else:
                    python_code.append(' ' * 4 * self.indentation_level + 
                                    f"for {var_name} in range({start_val}, {end_val} + 1):")
                
                self.indentation_level += 1
                # Add counter increment and check
                python_code.append(' ' * 4 * self.indentation_level + f"{loop_counter_var} += 1")
                python_code.append(' ' * 4 * self.indentation_level + 
                                  f"if {loop_counter_var} > {self.max_execution_steps}:")
                python_code.append(' ' * 4 * (self.indentation_level+1) + 
                                  "raise RuntimeError(\"Possible infinite loop detected!\")")
                
                j = i + 1
                nesting_level = 1
                while j < len(lines) and nesting_level > 0:
                    curr_line = lines[j].strip().lower()  # Convert to lowercase for comparison
                    if curr_line.startswith("pour ") and " faire" in curr_line:
                        nesting_level += 1
                    # Improved to check if the line contains finpour rather than exact match
                    elif "finpour" in curr_line:
                        nesting_level -= 1
                    j += 1
                    
                loop_block = '\n'.join(lines[i+1:j-1])  # -1 to exclude the finpour
                python_code.extend(self.parse_instructions(loop_block))
                
                self.indentation_level -= 1
                i = j
                continue
            
            # Normal instruction
            translated = self.translate_instruction(line)
            if translated:
                python_code.append(translated)
            
            i += 1
            
        return python_code
        
    def compile_to_python(self, french_code):
        """Convert French algorithm to Python code"""
        # Extract main sections - case insensitive
        self.needs_math_import = False
        french_code_lower = french_code.lower()
        
        # Check for essential structure - case insensitive
        if 'algorithme' not in french_code_lower or 'debut' not in french_code_lower or 'fin' not in french_code_lower:
            return "Error: Missing essential algorithm structure"
            
        algorithm_name = None
        var_section = ""
        instruction_section = ""
        
        # Extract algorithm name - case insensitive
        algo_header = french_code
        var_index = -1
        
        # Find the var keyword position - truly case insensitive
        var_match = re.search(r'\bvar\b', french_code_lower)
        if var_match:
            var_index = var_match.start()
            var_keyword = french_code[var_match.start():var_match.end()]
                    
        if var_index != -1:
            algo_header = french_code[:var_index]
            
        # Find algorithm keyword and extract name - case insensitive
        algo_match = re.search(r'\balgorithme\b', algo_header.lower())
        if algo_match:
            algo_keyword = algo_header[algo_match.start():algo_match.end()]
            algo_name_part = algo_header.split(algo_keyword, 1)[1]
            if ';' in algo_name_part:
                algorithm_name = algo_name_part.split(';', 1)[0].strip()
            else:
                algorithm_name = algo_name_part.strip()
        
        # Extract variable section - case insensitive
        debut_match = re.search(r'\bdebut\b', french_code_lower)
        var_match = re.search(r'\bvar\b', french_code_lower)
        
        var_start = -1
        debut_start = -1
        
        if var_match:
            var_start = var_match.end()
            var_keyword = french_code[var_match.start():var_match.end()]
        
        if debut_match:
            debut_start = debut_match.start()
            debut_keyword = french_code[debut_match.start():debut_match.end()]
            
        if var_start != -1 and debut_start != -1:
            var_section = french_code[var_start:debut_start]
            
        # Extract instruction section - case insensitive
        fin_match = re.search(r'\bfin\b', french_code_lower)
        
        debut_end = -1
        fin_start = -1
        
        if debut_match:
            debut_end = debut_match.end()
        
        if fin_match:
            fin_start = fin_match.start()
            fin_keyword = french_code[fin_match.start():fin_match.end()]
            
        if debut_end != -1 and fin_start != -1:
            instruction_section = french_code[debut_end:fin_start]
        
        # Parse variables and store as an instance variable for use in translation
        self.current_variables = self.parse_variables(var_section)
        
        # Generate Python code
        python_code = [f"# Generated from algorithm: {algorithm_name}\n"]
        
        if self.needs_math_import or 'racine(' in french_code.lower():
            python_code.append("import math")
            python_code.append("") 
        
        # Define helper function for boolean display
        python_code.append("# Define French boolean literals")
        python_code.append("vrai = True")
        python_code.append("faux = False")
        python_code.append("")
        
        # Add constant declarations
        if self.constants:
            python_code.append("# Constants:")
            for const_name, (const_type, const_value) in self.constants.items():
                python_code.append(f"{const_name} = {const_value}")
            python_code.append("")
        
        # Add variable declarations as comments
        python_code.append("# Variable declarations:")
        for var_name, var_type in self.current_variables.items():
            python_code.append(f"# {var_name}: {var_type}")
        python_code.append("")
        
        # Initialize variables with default values
        for var_name, var_type in self.current_variables.items():
            if var_type == "int":
                python_code.append(f"{var_name} = 0")
            elif var_type == "float":
                python_code.append(f"{var_name} = 0.0")
            elif var_type == "str":
                python_code.append(f"{var_name} = \"\"")
            elif var_type == "bool":
                python_code.append(f"{var_name} = False")
            elif var_type == "char":
                python_code.append(f"{var_name} = \"\"")
        
        if self.current_variables:
            python_code.append("")  # Add empty line after variable initializations
        
        # Add global execution counter
        python_code.append("# Initialize global execution counter to prevent infinite loops")
        python_code.append("_global_execution_counter = 0")
        python_code.append("_MAX_EXECUTION_STEPS = 1000")
        python_code.append("")
        
        # Translate instructions
        python_code.extend(self.parse_instructions(instruction_section))
                
        return '\n'.join(python_code)
    
    def execute(self, python_code):
        """Execute the generated Python code and return output"""
        import sys
        from io import StringIO
        import tkinter as tk
        from tkinter import simpledialog
        import queue
        
        # Create a queue for input operations
        input_queue = queue.Queue()
        
        # Redirect stdout to capture output
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output
        
        # Reference to the root Tkinter window
        root = tk._default_root
        
        # Create a custom input function that uses the main thread
        def custom_input(prompt=""):
            # Print the prompt to the redirected output
            print(prompt, end="")
            
            # Function to run in main thread to get input
            def ask_input():
                result = simpledialog.askstring("Input", prompt, parent=root)
                # If cancel was pressed, provide empty string to avoid hanging
                if result is None:
                    result = ""
                input_queue.put(result)
            
            # Schedule the dialog to run in the main thread
            root.after(0, ask_input)
            
            # Wait for input from the queue
            result = input_queue.get()
            print(result)  # Show the input in the output
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
        
    def patched_execute(self, python_code):
        """Execute the generated Python code and update output in real-time"""
        import sys
        from PyQt5.QtWidgets import QApplication
        
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
        
        # Set WHITE background color directly
        main_window.output_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                color: #000000;
                font-family: 'Courier New';
                font-size: 10pt;
                border: 1px solid #CCCCCC;
                padding: 4px;
            }
        """)
        
        # Create our real-time output stream
        real_time_stream = RealTimeStream(main_window.output_viewer)
        
        # Redirect stdout to our real-time stream
        old_stdout = sys.stdout
        sys.stdout = real_time_stream
        
        # Input handling with our dialog
        def custom_input(prompt=""):
            # Print the prompt to the output
            print(prompt, end="")
            
            # Create input dialog and show it
            from input_dialog import InputDialog
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
        
    def update_max_execution_steps(self, steps=None):
        """Update the maximum execution steps, either with provided value or from settings"""
        if steps is not None:
            self.max_execution_steps = steps
        else:
            from PyQt5.QtCore import QSettings
            settings = QSettings("AlgoFX", "AlgoFX")
            self.max_execution_steps = settings.value("algorithm_execution_steps", 1000, type=int)

# Patching function for the application
def patch_real_time_execution():
    """Patch the FrenchAlgorithmCompiler to use real-time execution."""
    FrenchAlgorithmCompiler._original_execute = FrenchAlgorithmCompiler.execute
    # Replace with our patched method
    FrenchAlgorithmCompiler.execute = FrenchAlgorithmCompiler.patched_execute
    return True