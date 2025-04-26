import re
import ast
import re
import ast
import tempfile
import os
from PyQt5.QtWidgets import QMessageBox, QWidget, QLabel
from PyQt5.QtGui import QTextCursor, QPalette, QColor, QTextCursor
from PyQt5.QtCore import Qt, QSettings

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


    def check_common_syntax_errors(self, algorithm_code, language="french"):
        """
        Check for common syntax errors in the algorithm code and provide helpful error messages.
        
        Args:
            algorithm_code: The algorithm code to check
            language: The language for error messages ("french" or "arabic")
            
        Returns:
            List of tuples (line_number, line_content, error_message)
        """
        errors = []
        algo_lines = algorithm_code.strip().split('\n')
        error_messages = {
            "algo_missing": {
                "french": "L'en-tête de l'algorithme est manquant. L'algorithme doit commencer par 'algorithme nom_algo'.",
                "arabic": "عليك بكتابة رأس الخورازمية بطريقة صحيحة Algorithme ثم اسم الخوارزمية."
            },
            "algo_name_invalid": {
                "french": "Le nom de l'algorithme est invalide. Il doit suivre les règles de nommage des variables.",
                "arabic": "اسم الخوارزمية غير صالح. يجب أن يتبع قواعد تسمية المتغيرات."
            },
            "algo_name_starts_with_number": {
                "french": "Le nom de l'algorithme ne peut pas commencer par un chiffre.",
                "arabic": "لا يمكن أن يبدأ اسم الخوارزمية برقم."
            },
            "algo_name_has_spaces": {
                "french": "Le nom de l'algorithme ne peut pas contenir d'espaces.",
                "arabic": "لا يمكن أن يحتوي اسم الخوارزمية على مسافات."
            },
            "algo_name_special_chars": {
                "french": "Le nom de l'algorithme ne peut pas contenir de caractères spéciaux sauf '_'.",
                "arabic": "لا يمكن أن يحتوي اسم الخوارزمية على أحرف خاصة باستثناء '_'."
            },
            "algo_name_reserved": {
                "french": "Le nom de l'algorithme ne peut pas être un mot réservé.",
                "arabic": "لا يمكن أن يكون اسم الخوارزمية كلمة محجوزة."
            },
            "var_section_missing": {
                "french": "La section 'var' est manquante ou mal positionnée.",
                "arabic": "قسم التصريح عن المتغيرات 'var' مفقود, مكتوب بطريقة غير صحيحة أو في موضع غير صحيح."
            },
            "var_name_invalid": {
                "french": "Le nom de la variable '{}' est invalide. Il doit suivre les règles de nommage des variables.",
                "arabic": "  اسم المتغير '{}' خاطئ. يجب أن يتبع قواعد تسمية المتغيرات."
            },
            "var_name_reserved": {
                "french": "Le nom de la variable '{}' ne peut pas être un mot réservé.",
                "arabic": "لا يمكن أن يكون اسم المتغير '{}' كلمة محجوزة."
            },
            "var_type_invalid": {
                "french": "Le type '{}' n'est pas valide. Types valides: Entier, Reel, Chaine, Charactere, Boolean.",
                "arabic": "النوع '{}' خاطئ.<br> الأنواع الصالحة: Entier, Reel, Chaine de caractere, Charactere, Boolean."
            },
            "var_missing_semicolon": {
                "french": "Il manque un point-virgule (;) à la fin de la déclaration de variable.",
                "arabic": "نقطة الفاصلة المنقوطة (;) مفقودة في نهاية إعلان المتغير."
            },
            "const_value_missing": {
                "french": "La constante '{}' doit avoir une valeur assignée.",
                "arabic": "يجب أن يكون للثابت '{}' قيمة معينة."
            },
            "const_missing_semicolon": {
                "french": "Il manque un point-virgule (;) à la fin de la déclaration de constante.",
                "arabic": "نقطة الفاصلة المنقوطة (;) مفقودة في نهاية إعلان الثابت."
            },
            "debut_missing": {
                "french": "Le mot-clé 'debut' est manquant.",
                "arabic": "الكلمة المفتاحية 'debut' مفقودة."
            },
            "fin_missing": {
                "french": "Le mot-clé 'fin' est manquant.",
                "arabic": "الكلمة المفتاحية 'fin' مفقودة."
            },
            "statement_missing_semicolon": {
                "french": "Il manque un point-virgule (;) à la fin de cette instruction.",
                "arabic": " الفاصلة المنقوطة (;) مفقودة في نهاية هذه التعليمة."
            },
            "undeclared_variable": {
                "french": "La variable '{}' est utilisée mais n'a pas été déclarée.",
                "arabic": "المتغير '{}' مستخدم ولكن لم يتم إعلانه."
            },
            "assignment_missing_semicolon": {
                "french": "Il manque un point-virgule (;) à la fin de cette affectation.",
                "arabic": " الفاصلة المنقوطة (;) مفقودة في نهاية عملية الإسناد."
            },
            "read_missing_semicolon": {
                "french": "Il manque un point-virgule (;) à la fin de l'instruction 'lire'.",
                "arabic": " الفاصلة المنقوطة (;) مفقودة في نهاية تعليمة القراءة 'lire'."
            },
            "write_missing_semicolon": {
                "french": "Il manque un point-virgule (;) à la fin de l'instruction 'ecrire'.",
                "arabic": " الفاصلة المنقوطة (;) مفقودة في نهاية تعليمة الكتابة 'ecrire'."
            },
            "read_invalid_spacing": {
                "french": "Il ne doit pas y avoir d'espace entre 'lire' et '('.",
                "arabic": "يجب أن لا يكون هناك مسافة بين 'lire' و '('."
            },
            "write_invalid_spacing": {
                "french": "Il ne doit pas y avoir d'espace entre 'ecrire' et '('.",
                "arabic": "يجب أن لا يكون هناك مسافة بين 'ecrire' و '('."
            },
            "si_missing_finsi": {
                "french": "L'instruction 'si' n'a pas de 'finsi' correspondant.",
                "arabic": "تعليمة 'si' ليس لها 'finsi'."
            },
            "pour_missing_finpour": {
                "french": "L'instruction 'pour' n'a pas de 'finpour' correspondant.",
                "arabic": "تعليمة 'pour' ليس لها 'finpour' ."
            },
            "tantque_missing_fintantque": {
                "french": "L'instruction 'tantque' n'a pas de 'fintantque' correspondant.",
                "arabic": "تعليمة 'tantque' ليس لها 'fintantque' ."
            },
            # New error messages for si-alors, tantque-faire, pour-faire
            "si_missing_alors": {
                "french": "L'instruction 'si' doit être suivie par 'alors'.",
                "arabic": "تعليمة 'si' يجب أن تتبع بـ 'alors'."
            },
            "tantque_missing_faire": {
                "french": "L'instruction 'tantque' doit être suivie par 'faire'.",
                "arabic": "تعليمة 'tantque' يجب أن تتبع بـ 'faire'."
            },
            "pour_invalid_format": {
                "french": "Format de boucle 'pour' invalide. Formats valides: 'pour var de val1 a val2 faire', 'pour var de val1 allant a val2 faire', 'pour var allant de val1 a val2 faire', ou avec l'option 'pas'.",
                "arabic": "تنسيق حلقة 'pour' غير صالح.<br> التنسيقات الصالحة:<br> 'pour var de val1 a val2 faire'<br> 'pour var de val1 allant a val2 faire'<br> 'pour var allant de val1 a val2 faire'<br> أو مع خيار 'pas'."
            },
            "pour_missing_faire": {
                "french": "L'instruction 'pour' doit se terminer par 'faire'.",
                "arabic": "تعليمة 'pour' يجب أن تنتهي بـ 'faire'."
            },
            "invalid_instruction": {
                "french": "Instruction non reconnue dans le bloc principal. Les instructions valides sont: lire, ecrire, affectation (<-), si...alors, pour...faire, tantque...faire, sortir ou commentaire.",
                "arabic": "تعليمة غير معروفة في الكتلة الرئيسية. التعليمات الصالحة هي: lire, ecrire, affectation (<-), si...alors, pour...faire, tantque...faire, sortir أو تعليق."
            },
            "sortir_missing_semicolon": {
                "french": "Il manque un point-virgule (;) à la fin de l'instruction 'sortir'.",
                "arabic": "نقطة الفاصلة المنقوطة (;) مفقودة في نهاية تعليمة 'sortir'."
            },
            "var_format_invalid": {
                "french": "Format de déclaration de variable invalide. Format valide: 'var_name: type;'",
                "arabic": "تنسيق إعلان المتغير غير صالح. التنسيق الصالح: 'var_name: type;'"
            },
            "const_format_invalid": {
                "french": "Format de déclaration de constante invalide. Format valide: 'const_name=value;'",
                "arabic": "تنسيق إعلان الثابت غير صالح. التنسيق الصالح: 'const_name=value;'"
            },
            "duplicate_var": {
                "french": "Variable '{}' déjà déclarée. Les noms des variables doivent être uniques.",
                "arabic": "المتغير '{}' تم الإعلان عنه مسبقاً. أسماء المتغيرات يجب أن تكون فريدة."
            },
            "duplicate_const": {
                "french": "Constante '{}' déjà déclarée. Les noms des constantes doivent être uniques.",
                "arabic": "الثابت '{}' تم الإعلان عنه مسبقاً. أسماء الثوابت يجب أن تكون فريدة."
            },
            "var_const_name_conflict": {
                "french": "Le nom '{}' est déjà utilisé comme constante. Les noms des variables et constantes doivent être uniques.",
                "arabic": "الاسم '{}' مستخدم بالفعل كثابت. أسماء المتغيرات والثوابت يجب أن تكون فريدة."
            },
            "const_var_name_conflict": {
                "french": "Le nom '{}' est déjà utilisé comme variable. Les noms des variables et constantes doivent être uniques.",
                "arabic": "الاسم '{}' مستخدم بالفعل كمتغير. أسماء المتغيرات والثوابت يجب أن تكون فريدة."
            }
        }
        
        # Define keywords that cannot be used as identifiers - keep original keywords
        keywords = [
            "algorithme", "Algorithme", "ALGORITHME",
            "var", "Var", "VAR",
            "const", "Const", "CONST",
            "debut", "Debut", "DEBUT",
            "fin", "Fin", "FIN",
            "si", "Si", "SI",
            "alors", "Alors", "ALORS",
            "sinon", "Sinon", "SINON",
            "finsi", "Finsi", "FINSI",
            "pour", "Pour", "POUR",
            "faire", "Faire", "FAIRE",
            "finpour", "Finpour", "FINPOUR",
            "tantque", "Tantque", "TANTQUE",
            "fintantque", "Fintantque", "FINTANTQUE",
            "sortir", "Sortir", "SORTIR",
            "lire", "Lire", "LIRE",
            "ecrire", "Ecrire", "ECRIRE",
            "et", "Et", "ET",
            "ou", "Ou", "OU",
            "non", "Non", "NON",
            "mod", "Mod", "MOD",
            "div", "Div", "DIV",
            "entier", "Entier", "ENTIER",
            "reel", "Reel", "REEL",
            "chaine", "Chaine", "CHAINE",
            "charactere", "Charactere", "CHARACTERE",
            "boolean", "Boolean", "BOOLEAN","Booleen","booleen",
            "pas", "Pas", "PAS",
            "de", "De", "DE",
            "allant", "Allant", "ALLANT"
        ]
        
        # Check algorithm header (first non-comment, non-empty line)
        algo_header_found = False
        algo_header_line = 0
        
        for i, line in enumerate(algo_lines):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("//"):
                continue
                
            # Check if this is the algorithm header
            if not algo_header_found:
                match = re.match(r'^algorithme\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;?$', line, re.IGNORECASE)
                if not match:
                    # Check if it's an attempt at an algorithm header with an invalid name
                    invalid_match = re.match(r'^algorithme\s+([^\s;]+)\s*;?$', line, re.IGNORECASE)
                    if invalid_match:
                        algo_name = invalid_match.group(1)
                        errors.append((i + 1, line, error_messages["algo_name_invalid"][language]))
                        algo_header_found = True
                        algo_header_line = i
                    else:
                        errors.append((i + 1, line, error_messages["algo_missing"][language]))
                else:
                    algo_name = match.group(1)
                    algo_header_found = True
                    algo_header_line = i
                    
                    # Check algorithm name validity
                    if algo_name[0].isdigit():
                        errors.append((i + 1, line, error_messages["algo_name_starts_with_number"][language]))
                        
                    if ' ' in algo_name:
                        errors.append((i + 1, line, error_messages["algo_name_has_spaces"][language]))
                        
                    if re.search(r'[^a-zA-Z0-9_]', algo_name):
                        errors.append((i + 1, line, error_messages["algo_name_special_chars"][language]))
                        
                    if algo_name.lower() in keywords:
                        errors.append((i + 1, line, error_messages["algo_name_reserved"][language]))
        
        # Check section structure (var, const, debut, fin)
        var_section_found = False
        const_section_found = False
        debut_section_found = False
        fin_found = False
        
        # Variables to track current section
        in_var_section = False
        in_const_section = False
        in_main_section = False
        
        # Track declared variables and constants - updated for better duplication tracking
        declared_var_names = set()  # Just variable names
        declared_const_names = set()  # Just constant names
        all_identifiers = {}  # Maps identifier to its type ('var' or 'const')
        
        # Track used variables
        used_vars = set()
        
        # Track control structures to ensure they are properly closed
        open_si_statements = []
        open_pour_statements = []
        open_tantque_statements = []
        
        # Track si statements without alors
        si_without_alors = []
        
        # Track tantque statements without faire
        tantque_without_faire = []
        
        # Track pour statements without faire
        pour_without_faire = []
        
        # Valid variable types
        valid_types = ["entier", "reel", "chaine", "chainedecaractere", "charactere", "booleen", "boolean"]
        
        # Check the rest of the algorithm structure
        for i, line in enumerate(algo_lines):
            if i <= algo_header_line:
                continue
                
            original_line = line
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("//"):
                continue
                
            # Remove inline comments
            if "//" in line:
                line = line.split("//")[0].strip()
                if not line:  # Skip if line is empty after removing comment
                    continue
            
            line_lower = line.lower()
            
            # Check for section markers - case insensitive
            if line_lower == "var":
                var_section_found = True
                in_var_section = True
                in_const_section = False
                in_main_section = False
                continue
            elif line_lower == "const":
                const_section_found = True
                in_var_section = False
                in_const_section = True
                in_main_section = False
                continue
            elif line_lower == "debut":
                debut_section_found = True
                in_var_section = False
                in_const_section = False
                in_main_section = True
                continue
            elif line_lower == "fin":
                fin_found = True
                in_var_section = False
                in_const_section = False
                in_main_section = False
                continue
                
            # Process variable declarations - check for proper format
            if in_var_section:
                # Remove all whitespace for processing
                cleaned_line = re.sub(r'\s+', '', line)
                
                # Check if declaration ends with semicolon
                if not cleaned_line.endswith(';'):
                    errors.append((i + 1, original_line, error_messages["var_missing_semicolon"][language]))
                
                # Check if the variable declaration has proper format (var_name: type;)
                if ":" not in cleaned_line:
                    errors.append((i + 1, original_line, error_messages["var_format_invalid"][language]))
                    continue
                
                # Handle variable declarations (var_names : type;)
                parts = cleaned_line.split(":")
                if len(parts) == 2:
                    var_names_part = parts[0].strip()
                    type_part = parts[1].strip().rstrip(';')
                    
                    # Check if type is valid
                    type_lower = type_part.lower()
                    if type_lower not in valid_types:
                        errors.append((i + 1, original_line, error_messages["var_type_invalid"][language].format(type_part)))
                    
                    # Process variable names
                    var_names = var_names_part.split(',')
                    for var_name in var_names:
                        var_name = var_name.strip()
                        if var_name:
                            # Check variable naming rules
                            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
                                errors.append((i + 1, original_line, error_messages["var_name_invalid"][language].format(var_name)))
                            elif var_name.lower() in keywords:
                                errors.append((i + 1, original_line, error_messages["var_name_reserved"][language].format(var_name)))
                            else:
                                var_lower = var_name.lower()
                                # Check for duplicate variables
                                if var_lower in declared_var_names:
                                    errors.append((i + 1, original_line, error_messages["duplicate_var"][language].format(var_name)))
                                # Check for variable-constant conflicts
                                elif var_lower in declared_const_names:
                                    errors.append((i + 1, original_line, error_messages["var_const_name_conflict"][language].format(var_name)))
                                else:
                                    declared_var_names.add(var_lower)
                                    all_identifiers[var_lower] = "var"
            
            # Process constant declarations - check for proper format
            if in_const_section:
                # Remove all whitespace for processing
                cleaned_line = re.sub(r'\s+', '', line)
                
                # Check if the constant declaration has proper format (const_name=value;)
                if "=" not in cleaned_line:
                    errors.append((i + 1, original_line, error_messages["const_format_invalid"][language]))
                    continue
                    
                # Check if declaration ends with semicolon
                if not cleaned_line.endswith(';'):
                    errors.append((i + 1, original_line, error_messages["const_missing_semicolon"][language]))
                
                # Handle constant declarations (const_name = value;)
                parts = cleaned_line.split("=", 1)
                if len(parts) == 2:
                    const_name = parts[0].strip()
                    const_value = parts[1].strip().rstrip(';')
                    
                    # Check constant naming rules
                    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', const_name):
                        errors.append((i + 1, original_line, error_messages["var_name_invalid"][language].format(const_name)))
                    elif const_name.lower() in keywords:
                        errors.append((i + 1, original_line, error_messages["var_name_reserved"][language].format(const_name)))
                    else:
                        const_lower = const_name.lower()
                        # Check for duplicate constants
                        if const_lower in declared_const_names:
                            errors.append((i + 1, original_line, error_messages["duplicate_const"][language].format(const_name)))
                        # Check for constant-variable conflicts
                        elif const_lower in declared_var_names:
                            errors.append((i + 1, original_line, error_messages["const_var_name_conflict"][language].format(const_name)))
                        else:
                            declared_const_names.add(const_lower)
                            all_identifiers[const_lower] = "const"
                    
                    # Check if value is provided
                    if not const_value:
                        errors.append((i + 1, original_line, error_messages["const_value_missing"][language].format(const_name)))
            
            # Check statements in main section
            if in_main_section:
                # Check for valid instruction types in main section
                is_valid_instruction = False
                
                # Track 'si' statements and check for 'alors'
                if re.match(r'^si\b', line_lower):
                    open_si_statements.append(i + 1)
                    # Check if 'alors' is in the same line
                    if not re.search(r'\balors\b', line_lower, re.IGNORECASE):
                        si_without_alors.append((i + 1, original_line))
                    is_valid_instruction = True
                elif line_lower == "finsi":
                    if open_si_statements:
                        open_si_statements.pop()
                    is_valid_instruction = True
                
                # Track 'pour' statements and check for proper format and 'faire'
                if re.match(r'^pour\b', line_lower):
                    open_pour_statements.append(i + 1)
                    
                    # Check for valid pour loop formats
                    valid_pour_format = False
                    # Format 1: pour var de val1 a val2 faire
                    if re.search(r'^pour\s+\w+\s+de\s+\S+\s+a\s+\S+\s+faire\b', line_lower, re.IGNORECASE):
                        valid_pour_format = True
                    # Format 2: pour var de val1 allant a val2 faire
                    elif re.search(r'^pour\s+\w+\s+de\s+\S+\s+allant\s+a\s+\S+\s+faire\b', line_lower, re.IGNORECASE):
                        valid_pour_format = True
                    # Format 3: pour var allant de val1 a val2 faire
                    elif re.search(r'^pour\s+\w+\s+allant\s+de\s+\S+\s+a\s+\S+\s+faire\b', line_lower, re.IGNORECASE):
                        valid_pour_format = True
                    # Format 4: pour var de val1 a val2 pas val3 faire
                    elif re.search(r'^pour\s+\w+\s+de\s+\S+\s+a\s+\S+\s+pas\s+\S+\s+faire\b', line_lower, re.IGNORECASE):
                        valid_pour_format = True
                    # Format 5: pour var de val1 allant a val2 pas val3 faire
                    elif re.search(r'^pour\s+\w+\s+de\s+\S+\s+allant\s+a\s+\S+\s+pas\s+\S+\s+faire\b', line_lower, re.IGNORECASE):
                        valid_pour_format = True
                    # Format 6: pour var allant de val1 a val2 pas val3 faire
                    elif re.search(r'^pour\s+\w+\s+allant\s+de\s+\S+\s+a\s+\S+\s+pas\s+\S+\s+faire\b', line_lower, re.IGNORECASE):
                        valid_pour_format = True
                    
                    if not valid_pour_format:
                        errors.append((i + 1, original_line, error_messages["pour_invalid_format"][language]))
                    
                    # Check if 'faire' is at the end
                    if not re.search(r'\bfaire\b', line_lower, re.IGNORECASE):
                        pour_without_faire.append((i + 1, original_line))
                        
                    is_valid_instruction = True
                elif line_lower == "finpour":
                    if open_pour_statements:
                        open_pour_statements.pop()
                    is_valid_instruction = True
                
                # Track 'tantque' statements and check for 'faire'
                if re.match(r'^tantque\b', line_lower):
                    open_tantque_statements.append(i + 1)
                    # Check if 'faire' is in the same line
                    if not re.search(r'\bfaire\b', line_lower, re.IGNORECASE):
                        tantque_without_faire.append((i + 1, original_line))
                    is_valid_instruction = True
                elif line_lower == "fintantque":
                    if open_tantque_statements:
                        open_tantque_statements.pop()
                    is_valid_instruction = True
                    
                # Check for variable assignment
                if "<-" in line:
                    # Check if assignment ends with semicolon
                    if not line.rstrip().endswith(';'):
                        errors.append((i + 1, original_line, error_messages["assignment_missing_semicolon"][language]))
                    
                    # Extract variable being assigned to
                    var_name = line.split("<-")[0].strip()
                    
                    # Add to used variables
                    if var_name and re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
                        used_vars.add(var_name.lower())
                    
                    is_valid_instruction = True
                
                # Check for read statements
                if re.search(r'\blire\b', line_lower, re.IGNORECASE):
                    # Check for invalid spacing between lire and (
                    if re.search(r'\blire\s+\(', line, re.IGNORECASE):
                        errors.append((i + 1, original_line, error_messages["read_invalid_spacing"][language]))
                    
                    # Check if read statement ends with semicolon
                    if not line.rstrip().endswith(';'):
                        errors.append((i + 1, original_line, error_messages["read_missing_semicolon"][language]))
                    
                    # Extract variables being read
                    match = re.search(r'\blire\s*\(([^)]*)\)', line, re.IGNORECASE)
                    if match:
                        var_str = match.group(1)
                        read_vars = [v.strip() for v in var_str.split(',') if v.strip()]
                        for var in read_vars:
                            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var):
                                used_vars.add(var.lower())
                    
                    is_valid_instruction = True
                
                # Check for write statements
                if re.search(r'\becrire\b', line_lower, re.IGNORECASE):
                    # Check for invalid spacing between ecrire and (
                    if re.search(r'\becrire\s+\(', line, re.IGNORECASE):
                        errors.append((i + 1, original_line, error_messages["write_invalid_spacing"][language]))
                    
                    # Check if write statement ends with semicolon
                    if not line.rstrip().endswith(';'):
                        errors.append((i + 1, original_line, error_messages["write_missing_semicolon"][language]))
                    
                    # Extract potential variables in the write statement
                    match = re.search(r'\becrire\s*\(([^)]*)\)', line, re.IGNORECASE)
                    if match:
                        expr_str = match.group(1)
                        # Remove string literals
                        expr_str = re.sub(r'"[^"]*"', '', expr_str)
                        # Find potential variables
                        potential_vars = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expr_str)
                        for var in potential_vars:
                            var_lower = var.lower()
                            if var_lower not in keywords:
                                used_vars.add(var_lower)
                    
                    is_valid_instruction = True
                
                # Check for 'sinon' keyword
                if re.match(r'^sinon\b', line_lower):
                    is_valid_instruction = True
                
                # Check for 'sortir' statement
                if re.match(r'^sortir\b', line_lower):
                    # Check if sortir statement ends with semicolon
                    if not line.rstrip().endswith(';'):
                        errors.append((i + 1, original_line, error_messages["sortir_missing_semicolon"][language]))
                    is_valid_instruction = True
                
                # Check for valid instructions
                if not is_valid_instruction and not line.startswith("//"):
                    # Check if it might be a comment line
                    if "//" not in original_line:
                        errors.append((i + 1, original_line, error_messages["invalid_instruction"][language]))
        
        # Check for missing sections
        if not var_section_found:
            errors.append((algo_header_line + 1, "", error_messages["var_section_missing"][language]))
        
        if not debut_section_found:
            errors.append((len(algo_lines), "", error_messages["debut_missing"][language]))
        
        if not fin_found:
            errors.append((len(algo_lines), "", error_messages["fin_missing"][language]))
        
        # Check for undeclared variables
        all_declared_identifiers = declared_var_names.union(declared_const_names)
        for var in used_vars:
            if var not in all_declared_identifiers:
                # Find the line where the variable is first used
                for i, line in enumerate(algo_lines):
                    if var.lower() in line.lower():
                        errors.append((i + 1, line.strip(), error_messages["undeclared_variable"][language].format(var)))
                        break
        
        # Check for unclosed control structures
        for line_num in open_si_statements:
            errors.append((line_num, algo_lines[line_num - 1].strip(), error_messages["si_missing_finsi"][language]))
        
        for line_num in open_pour_statements:
            errors.append((line_num, algo_lines[line_num - 1].strip(), error_messages["pour_missing_finpour"][language]))
        
        for line_num in open_tantque_statements:
            errors.append((line_num, algo_lines[line_num - 1].strip(), error_messages["tantque_missing_fintantque"][language]))
        
        # Check for 'si' without 'alors'
        for line_num, line_content in si_without_alors:
            errors.append((line_num, line_content, error_messages["si_missing_alors"][language]))
        
        # Check for 'tantque' without 'faire'
        for line_num, line_content in tantque_without_faire:
            errors.append((line_num, line_content, error_messages["tantque_missing_faire"][language]))
        
        # Check for 'pour' without 'faire'
        for line_num, line_content in pour_without_faire:
            errors.append((line_num, line_content, error_messages["pour_missing_faire"][language]))
        
        return errors
    
    def compile_algorithm(self, switch_tab=True):
        algorithm_code = self.editor.toPlainText()
        
        # Get the current theme setting
        settings = QSettings("AlgoFX", "AlgoFX")
        dark_mode = settings.value("dark_mode", False, type=bool)
        
        # Get the language setting
        language_param = settings.value("error_language_param", "french", type=str)  # Default to french if not set
        
        # Get main window position and size for centering dialogs
        main_window_x = settings.value("main_window_x", 0, type=int)
        main_window_y = settings.value("main_window_y", 0, type=int)
        main_window_width = settings.value("main_window_width", 800, type=int)
        main_window_height = settings.value("main_window_height", 600, type=int)
        
        # Define error messages in both languages
        error_messages = {
            "empty_editor": {
                "french": "L'éditeur est vide. Rien à compiler.",
                "arabic": "المحرر فارغ. لا شيء للتجميع."
            },
            "compilation_success": {
                "french": "Compilation réussie! Aucune erreur détectée.",
                "arabic": "تم التجميع بنجاح! لم يتم اكتشاف أي أخطاء."
            },
            "syntax_error_line": {
                "french": "Erreur de syntaxe à la ligne {}:\n\n\"{}\"\n\n{}",
                "arabic": "خطأ في بناء الجملة في السطر {}:\n\n\"{}\"\n\n{}"
            },
            "multiple_errors": {
                "french": "\n\nIl y a {} erreurs au total. Corrigez celle-ci et recompilez.",
                "arabic": "\n\nهناك {} أخطاء في المجموع. قم بتصحيح هذا الخطأ وأعد التجميع."
            },
            "syntax_error_title": {
                "french": "Erreur de syntaxe",
                "arabic": "خطأ في بناء الجملة"
            },
            "compilation_error_title": {
                "french": "Erreur de compilation",
                "arabic": "الأخطاء"
            },
            "compilation_error": {
                "french": "Erreur lors de la compilation: {}",
                "arabic": "خطأ أثناء التجميع: {}"
            },
            "python_syntax_error_algo": {
                "french": "Erreur de syntaxe dans votre algorithme à la ligne {}:\n\n\"{}\"\n\nCette erreur a généré un code Python invalide.",
                "arabic": "خطأ في بناء الجملة في خوارزميتك في السطر {}:\n\n\"{}\"\n\nهذا الخطأ أدى إلى إنشاء كود Python غير صالح."
            },
            "python_syntax_error": {
                "french": "Erreur de syntaxe Python générée à la ligne {}:\n{}\n\nCette erreur indique probablement un problème dans votre algorithme original.",
                "arabic": "تم إنشاء خطأ في بناء جملة Python في السطر {}:\n{}\n\nيشير هذا الخطأ على الأرجح إلى مشكلة في خوارزميتك الأصلية."
            },
            "mod_operator_error": {
                "french": "Erreur lors de la compilation: Problème avec l'opérateur 'mod' dans une condition.\n\nSolution possible: Utilisez une variable intermédiaire pour stocker le résultat de l'opération mod avant de le comparer.\nExemple: Remplacez 'si i mod 2 == 0 alors' par:\nt <- i mod 2;\nsi t = 0 alors",
                "arabic": "خطأ أثناء التجميع: مشكلة مع عامل التشغيل 'mod' في شرط.\n\nالحل المحتمل: استخدم متغيرًا وسيطًا لتخزين نتيجة عملية mod قبل مقارنتها.\nمثال: استبدل 'si i mod 2 == 0 alors' بـ:\nt <- i mod 2;\nsi t = 0 alors"
            },
            "racine_function_error": {
                "french": "Erreur lors de la compilation: Le compilateur ne reconnaît pas la fonction 'racine'.\n\nSolution possible: Utilisez 'racine' ou 'sqrt' et assurez-vous que le compilateur supporte cette fonction.",
                "arabic": "خطأ أثناء التجميع: المترجم لا يتعرف على وظيفة 'racine'.\n\nالحل المحتمل: استخدم  'sqrt' وتأكد من أن المترجم يدعم هذه الوظيفة."
            },
            "status_compilation_error": {
                "french": "Erreur de compilation",
                "arabic": "خطأ في التجميع"
            },
            "status_syntax_error": {
                "french": "Erreur de compilation - Syntaxe invalide",
                "arabic": "خطأ في التجميع - بناء جملة غير صالح"
            },
            "status_compilation_success": {
                "french": "Compilation réussie",
                "arabic": "تم التجميع بنجاح"
            }
        }
        
        # Import necessary Qt modules (to ensure they're available in the local scope)
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QDialogButtonBox
        from PyQt5.QtGui import QFont
        from PyQt5.QtCore import Qt
        
        # Function to create a custom message dialog with fixed size and proper RTL/LTR support
        def create_custom_message_dialog(title, message, icon_type="info"):
            """
            Creates a custom message dialog with fixed size and proper RTL/LTR support
            
            Parameters:
                title (str): Dialog title
                message (str): Message to display
                icon_type (str): Type of icon to display ('info', 'warning', 'error', 'question')
            """
            # Create custom dialog
            dialog = QDialog()
            dialog.setWindowTitle(title)
            dialog.setModal(True)
            
            # Set fixed size
            DIALOG_WIDTH = 400
            DIALOG_HEIGHT = 250
            dialog.setFixedSize(DIALOG_WIDTH, DIALOG_HEIGHT)
            
            # Set layout direction based on language
            if language_param == "arabic":
                dialog.setLayoutDirection(Qt.RightToLeft)
            else:
                dialog.setLayoutDirection(Qt.LeftToRight)
            
            # Create layout
            layout = QVBoxLayout()
            
            # Create header with icon
            header_layout = QHBoxLayout()
            
            # Set icon based on type
            icon_label = QLabel()
            icon = QMessageBox.Information
            if icon_type == "warning":
                icon = QMessageBox.Warning
            elif icon_type == "error":
                icon = QMessageBox.Critical
            elif icon_type == "question":
                icon = QMessageBox.Question
            
            icon_label.setPixmap(QMessageBox.standardIcon(icon))
            header_layout.addWidget(icon_label)
            
            # Add title label
            title_label = QLabel(title)
            title_font = QFont()
            title_font.setBold(True)
            title_font.setPointSize(10)
            title_label.setFont(title_font)
            header_layout.addWidget(title_label, 1)  # Add stretch
            
            # Add header to main layout
            layout.addLayout(header_layout)
            
            # Add horizontal separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            layout.addWidget(separator)
            
            # Create message area with proper text alignment
            message_label = QLabel()
            
            # Use HTML for RTL/LTR support
            if language_param == "arabic":
                message_html = f'''
                <div dir="rtl" align="right" style="
                    margin: 8px;
                    line-height: 1.2;
                    font-family: 'Segoe UI', 'Tahoma', 'Arial', sans-serif;
                    font-size: 14px;
                ">
                    {message}
                </div>
                '''
            else:
                message_html = f'''
                <div dir="ltr" align="left" style="
                    margin: 8px;
                    line-height: 1.2;
                    font-family: 'Segoe UI', 'Tahoma', 'Arial', sans-serif;
                    font-size: 14px;
                ">
                    {message}
                </div>
                '''
            
            message_label.setText(message_html)
            message_label.setWordWrap(True)
            message_label.setTextFormat(Qt.RichText)
            
            # Create scroll area for long messages
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(message_label)
            scroll_area.setFrameShape(QFrame.NoFrame)
            
            # Set minimum height for message area
            scroll_area.setMinimumHeight(60)
            
            layout.addWidget(scroll_area, 1)  # Add stretch to take up available space
            
            # Add buttons
            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(dialog.accept)
            layout.addWidget(button_box)
            
            dialog.setLayout(layout)
            
            # Apply dark theme if needed
            if dark_mode:
                self.apply_dark_theme_to_dialog(dialog)
            
            # Center dialog on main window
            center_x = main_window_x + (main_window_width - DIALOG_WIDTH) // 2
            center_y = main_window_y + (main_window_height - DIALOG_HEIGHT) // 2
            dialog.move(center_x, center_y)
            
            return dialog
        
        # Configure status bar text direction based on language
        if language_param == "arabic":
            self.status_bar.setLayoutDirection(Qt.RightToLeft)
            # Use rich text format to force RTL alignment
            current_text = self.status_bar.currentMessage()
            formatted_text = f'''
            <div style="direction: rtl; text-align: right; line-height: 1.6; font-family: 'Segoe UI', 'Tahoma', 'Arial', sans-serif; font-size: 16px;">
                {current_text}
            </div>
            '''
            self.status_bar.showMessage("")  # Clear first
            self.status_bar.showMessage(formatted_text)
        else:
            self.status_bar.setLayoutDirection(Qt.LeftToRight)
            self.status_bar.setStyleSheet("")
        
        # Check if editor is empty
        if not algorithm_code.strip():
            dialog = create_custom_message_dialog(
                error_messages["compilation_error_title"][language_param],
                error_messages["empty_editor"][language_param],
                icon_type="warning"
            )
            dialog.exec_()
            return None
        
        # Check for common syntax errors before compilation - reuse existing method
        syntax_errors = self.check_common_syntax_errors(algorithm_code, language=language_param)
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
            full_error_msg = error_messages["syntax_error_line"][language_param].format(line_num, line, error_msg)
            
            # If there are multiple errors, indicate this
            if len(syntax_errors) > 1:
                full_error_msg += error_messages["multiple_errors"][language_param].format(len(syntax_errors))
            
            dialog = create_custom_message_dialog(
                error_messages["syntax_error_title"][language_param],
                full_error_msg,
                icon_type="error"
            )
            dialog.exec_()
            
            self.status_bar.showMessage(error_messages["status_syntax_error"][language_param])
            return None
        
        # Store original code for reference
        original_code = algorithm_code
        processed_algorithm_code = algorithm_code
        
        # Process certain constructs for better Python compatibility
        # Replace racine(...) with sqrt(...)
        if "racine" in processed_algorithm_code:
            processed_algorithm_code = re.sub(r'racine\s*\(', r'math.sqrt(', processed_algorithm_code)
        
        # Handle mod operator
        if "mod" in processed_algorithm_code:
            pattern = r'(\w+)\s+mod\s+(\d+|\w+)\s*==\s*(\d+|\w+)'
            replacement = r'\1 mod \2 == \3'
            processed_algorithm_code = re.sub(pattern, replacement, processed_algorithm_code)
        
        try:
            # Try to compile the algorithm to Python, using the processed code
            python_code = self.compiler.compile_to_python(processed_algorithm_code)
            
            # Store mapping between Python lines and algorithm lines
            if hasattr(self.compiler, 'line_mapping'):
                line_mapping = self.compiler.line_mapping
            else:
                # If no mapping is available, we'll try to infer it
                line_mapping = self._generate_line_mapping(original_code, python_code)
            
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
                algo_lines = original_code.strip().split('\n')
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
                    error_msg = error_messages["python_syntax_error_algo"][language_param].format(algo_line_num, algo_line_text)
                else:
                    error_msg = error_messages["python_syntax_error"][language_param].format(py_error_line, error_text)
                
                dialog = create_custom_message_dialog(
                    error_messages["syntax_error_title"][language_param],
                    error_msg,
                    icon_type="error"
                )
                dialog.exec_()
                
                self.status_bar.showMessage(error_messages["status_syntax_error"][language_param])
                return None
            
            # Add math module import if sqrt is used
            if "sqrt(" in python_code and "import math" not in python_code:
                python_code = "import math\n" + python_code
            
            # Update Python code viewer
            self.python_viewer.setPlainText(python_code)
            self.python_code_loaded = True
            
            # Show success message
            self.status_bar.showMessage(error_messages["status_compilation_success"][language_param])
            dialog = create_custom_message_dialog(
                error_messages["compilation_error_title"][language_param],
                error_messages["compilation_success"][language_param],
                icon_type="info"
            )
            dialog.exec_()
            
            # Save Python code to temporary file
            self.temp_py_file = tempfile.NamedTemporaryFile(suffix='.py', delete=False)
            with open(self.temp_py_file.name, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            return python_code
            
        except Exception as e:
            # Handle specific error cases with helpful messages
            error_msg = str(e)
            if "mod" in error_msg or "Unexpected token" in error_msg:
                error_msg = error_messages["mod_operator_error"][language_param]
            elif "racine" in error_msg or "sqrt" in error_msg:
                error_msg = error_messages["racine_function_error"][language_param]
            else:
                error_msg = error_messages["compilation_error"][language_param].format(str(e))
            
            dialog = create_custom_message_dialog(
                error_messages["compilation_error_title"][language_param],
                error_msg,
                icon_type="error"
            )
            dialog.exec_()
            
            self.status_bar.showMessage(error_messages["status_compilation_error"][language_param])
            return None

        # Helper method for applying dark theme to dialogs
    def apply_dark_theme_to_dialog(self, dialog):
        """Apply dark theme to a dialog box"""
        # Dark mode colors
        bg_color = QColor(45, 45, 45)
        text_color = QColor(255, 255, 255)
        disabled_text_color = QColor(150, 150, 150)
        
        # Setup palette
        palette = QPalette()
        palette.setColor(QPalette.Window, bg_color)
        palette.setColor(QPalette.WindowText, text_color)
        palette.setColor(QPalette.Base, bg_color.lighter(110))
        palette.setColor(QPalette.AlternateBase, bg_color.lighter(120))
        palette.setColor(QPalette.Text, text_color)
        palette.setColor(QPalette.Button, bg_color)
        palette.setColor(QPalette.ButtonText, text_color)
        palette.setColor(QPalette.Disabled, QPalette.Text, disabled_text_color)
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_text_color)
        
        # Apply palette to the dialog
        dialog.setPalette(palette)
        
        # Apply to all child widgets
        for child in dialog.findChildren(QWidget):
            child.setPalette(palette)
        
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
        
    def run_algorithm(self, tabs, python_tab_added, show_execution_tab=True):
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

