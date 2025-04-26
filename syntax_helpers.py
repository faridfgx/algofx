from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont

def get_formatted_syntax_help(parent, is_dark_theme=False):
    # Cette méthode renvoie le texte d'aide avec une mise en forme HTML adaptée au thème
    
    # Couleurs pour le thème clair
    if not is_dark_theme:
        text_color = "#2c3e50"
        bg_color = "#ffffff"
        heading_color = "#2980b9"
        subheading_color = "#3498db"
        border_color = "#bdc3c7"
        code_bg = "#f7f9fb"
        code_border = "#e1e4e8"
        table_header_bg = "#f2f6f9"
        note_bg = "#fff8dc"
        note_border = "#ffeb3b"
        copyright_color = "#7f8c8d"
    # Couleurs pour le thème sombre
    else:
        text_color = "#e0e0e0"
        bg_color = "#2d2d2d"
        heading_color = "#64b5f6"
        subheading_color = "#90caf9"
        border_color = "#555555"
        code_bg = "#383838"
        code_border = "#505050"
        table_header_bg = "#404040"
        note_bg = "#4d4d31"
        note_border = "#d4d434"
        copyright_color = "#a0a0a0"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.5;
                margin: 20px;
                color: {text_color};
                background-color: {bg_color};
            }}
            h1 {{
                color: {heading_color};
                border-bottom: 2px solid {heading_color};
                padding-bottom: 8px;
                font-size: 24px;
            }}
            h2 {{
                color: {heading_color};
                margin-top: 20px;
                font-size: 20px;
            }}
            h3 {{
                color: {subheading_color};
                margin-top: 16px;
                font-size: 16px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 15px 0;
            }}
            th, td {{
                border: 1px solid {border_color};
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: {table_header_bg};
            }}
            pre {{
                background-color: {code_bg};
                border: 1px solid {code_border};
                border-radius: 4px;
                padding: 12px;
                overflow-x: auto;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
            ul {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 5px;
            }}
            .note {{
                background-color: {note_bg};
                border-left: 4px solid {note_border};
                padding: 10px;
                margin: 15px 0;
            }}
            .copyright {{
                margin-top: 30px;
                font-style: italic;
                color: {copyright_color};
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <h1>Guide d'Algorithmes en AlgoFX</h1>
        
        <h2>Structure de Base d'un Algorithme</h2>
        <p>Tout algorithme suit une structure standard composée de trois parties principales :</p>
        
        <pre>Algorithme NomAlgorithme;
Var
    // Déclarations de variables
    // nom: Type;
    a, b, c: Entier;  // Déclaration multiple
Const
    p=3.1415; // Déclaration des constantes
Debut
    // Instructions
Fin</pre>
        
        <h2>Types de Données</h2>
        <table>
            <tr>
                <th>Type</th>
                <th>Description</th>
                <th>Exemples</th>
            </tr>
            <tr>
                <td>Entier</td>
                <td>Nombres entiers</td>
                <td>42, -10, 0</td>
            </tr>
            <tr>
                <td>Reel</td>
                <td>Nombres à virgule flottante</td>
                <td>3.14, -0.5, 2.0</td>
            </tr>
            <tr>
                <td>Chaine de caractere</td>
                <td>Texte entre guillemets</td>
                <td>"Bonjour", "2023", ""</td>
            </tr>
            <tr>
                <td>Caractere</td>
                <td>Un seul caractère</td>
                <td>"a", "5", "!"</td>
            </tr>
            <tr>
                <td>Booleen</td>
                <td>Valeur logique</td>
                <td>vrai, faux</td>
            </tr>
        </table>
        
        <h2>Variables et Constantes</h2>
        
        <h3>Déclaration de Variables</h3>
        <pre>var
    age: Entier;
    nom: Chaine de caractere;
    a, b, c: Entier;  // Déclaration multiple
    estValide: Booleen;</pre>
        
        <h3>Déclaration de Constantes</h3>
        <pre>Const
    PI = 3.14159;
    TAUX_TVA = 20.0;
    MESSAGE_BIENVENUE = "Bonjour !";</pre>
        
        <h2>Opérations et Expressions</h2>
        
        <h3>Opérateurs Arithmétiques</h3>
        <table>
            <tr>
                <th>Opérateur</th>
                <th>Description</th>
                <th>Exemple</th>
            </tr>
            <tr>
                <td>+</td>
                <td>Addition</td>
                <td>a + b</td>
            </tr>
            <tr>
                <td>-</td>
                <td>Soustraction</td>
                <td>a - b</td>
            </tr>
            <tr>
                <td>*</td>
                <td>Multiplication</td>
                <td>a * b</td>
            </tr>
            <tr>
                <td>/</td>
                <td>Division</td>
                <td>a / b</td>
            </tr>
            <tr>
                <td>mod</td>
                <td>Modulo (reste de division)</td>
                <td>a mod b</td>
            </tr>
            <tr>
                <td>div</td>
                <td>Division entière</td>
                <td>a div b</td>
            </tr>
            <tr>
                <td>Puissance</td>
                <td>puissance</td>
                <td>a puissance b</td>
            </tr>
        </table>
        
        <h3>Opérateurs Relationnels</h3>
        <table>
            <tr>
                <th>Opérateur</th>
                <th>Description</th>
                <th>Exemple</th>
            </tr>
            <tr>
                <td>==</td>
                <td>Égal à</td>
                <td>a == b</td>
            </tr>
            <tr>
                <td>&lt;&gt; ou !=</td>
                <td>Différent de</td>
                <td>a &lt;&gt; b</td>
            </tr>
            <tr>
                <td>&lt;</td>
                <td>Inférieur à</td>
                <td>a &lt; b</td>
            </tr>
            <tr>
                <td>&gt;</td>
                <td>Supérieur à</td>
                <td>a &gt; b</td>
            </tr>
            <tr>
                <td>&lt;=</td>
                <td>Inférieur ou égal à</td>
                <td>a &lt;= b</td>
            </tr>
            <tr>
                <td>&gt;=</td>
                <td>Supérieur ou égal à</td>
                <td>a &gt;= b</td>
            </tr>
        </table>
        
        <h3>Opérateurs Logiques</h3>
        <table>
            <tr>
                <th>Opérateur</th>
                <th>Description</th>
                <th>Exemple</th>
            </tr>
            <tr>
                <td>et</td>
                <td>ET logique</td>
                <td>(a &gt; 0) et (b &lt; 10)</td>
            </tr>
            <tr>
                <td>ou</td>
                <td>OU logique</td>
                <td>(a == 0) ou (b == 0)</td>
            </tr>
            <tr>
                <td>non</td>
                <td>NON logique</td>
                <td>non(a == b)</td>
            </tr>
        </table>
        
        <p>Note sur la priorité des opérations : parenthèses, puis puissance, puis multiplication/division, puis addition/soustraction.</p>
        
        <h2>Instructions de Base</h2>
        
        <h3>Affectation</h3>
        <pre>variable &lt;- valeur;</pre>
        <p>Exemple : somme &lt;- a + b;</p>
        
        <h3>Lecture (Entrée)</h3>
        <pre>lire(variable);
lire(a, b, c);  // Lecture multiple</pre>
        
        <h3>Écriture (Sortie)</h3>
        <pre>Ecrire("Texte");
Ecrire(a, b, "Résultat:", resultat);  // Sortie multiple</pre>
        
        <h2>Structures de Contrôle</h2>
        
        <h3>Condition Simple</h3>
        <pre>Si condition alors
    instructions
Finsi</pre>
        
        <h3>Condition avec Alternative</h3>
        <pre>Si condition alors
    instructions1
Sinon
    instructions2
Finsi</pre>
        
        <h3>Conditions Imbriquées</h3>
        <pre>Si condition1 alors
    instructions1
Sinon
    Si condition2 alors
        instructions2
    Sinon
        instructions3
    Finsi
Finsi</pre>
        
        <h3>Boucle TANT QUE</h3>
        <pre>Tantque condition faire
    instructions
Fintantque</pre>
        
        <h3>Boucle POUR</h3>
        <pre>Pour variable de valeur1 a valeur2 faire
    instructions
Finpour

// Avec un pas spécifique
Pour variable de valeur1 a valeur2 pas n faire
    instructions
Finpour</pre>
        
        <h3>Instruction SORTIR</h3>
        <p>Permet de sortir d'une boucle prématurément :</p>
        <pre>Tantque condition faire
    Si autreCondition alors
        Sortir;  // Quitte la boucle
    Finsi
    instructions
Fintantque</pre>
        
        <h2>Fonctions Mathématiques</h2>
        <ul>
            <li>racine(x) : Calcule la racine carrée de x</li>
            <li>puissance : Opérateur puissance (ex: 2 puissance 3 = 8)</li>
            <li>mod : Opérateur modulo (reste de la division)</li>
            <li>div : Division entière</li>
        </ul>
        
        <h2>Exemples Complets</h2>
        
        <h3>Exemple 1 : Calcul de factorielle</h3>
        <pre>Algorithme Factoriel;
Var
    n, fact, i: Entier;
Debut
    Ecrire("Entrez un nombre pour calculer sa factorielle:");
    Lire(n);
    
    fact &lt;- 1;
    
    Pour i de 1 a n faire
        fact &lt;- fact * i;
    Finpour
    
    Ecrire("La factorielle de", n, "est", fact);
Fin</pre>
        
        <h3>Exemple 2 : Vérification d'un palindrome</h3>
        <pre>Algorithme VerificationPalindrome;
Var
    nombre, copie, inverse, chiffre: Entier;
Debut
    Ecrire("Entrez un nombre:");
    Lire(nombre);
    
    copie &lt;- nombre;
    inverse &lt;- 0;
    
    Tantque copie > 0 faire
        chiffre &lt;- copie mod 10;
        inverse &lt;- inverse * 10 + chiffre;
        copie &lt;- copie div 10;
    Fintantque
    
    Si nombre == inverse alors
        Ecrire(nombre, "est un palindrome");
    Sinon
        Ecrire(nombre, "n'est pas un palindrome");
    Finsi
Fin</pre>
        
        <h3>Exemple 3 : Conversion de température</h3>
        <pre>Algorithme ConversionTemperature;
Var
    choix: Entier;
    celsius, fahrenheit: Reel;
Debut
    Ecrire("Conversion de température");
    Ecrire("1- Celsius vers Fahrenheit");
    Ecrire("2- Fahrenheit vers Celsius");
    Ecrire("Entrez votre choix [1 ou 2]:");
    
    Lire(choix);
    
    Si choix == 1 alors
        Ecrire("Entrez la température en Celsius:");
        Lire(celsius);
        fahrenheit &lt;- (celsius * 9/5) + 32;
        Ecrire(celsius, "°C équivaut à", fahrenheit, "°F");
    Sinon
        Si choix == 2 alors
            Ecrire("Entrez la température en Fahrenheit:");
            Lire(fahrenheit);
            celsius &lt;- (fahrenheit - 32) * 5/9;
            Ecrire(fahrenheit, "°F équivaut à", celsius, "°C");
        Sinon
            Ecrire("Choix invalide");
        Finsi
    Finsi
Fin</pre>
        
        <h3>Exemple 4 : Suite de Fibonacci</h3>
        <pre>Algorithme SuiteFibonacci;
    n, i, a, b, c: Entier;
Debut
    Ecrire("Combien de termes de la suite de Fibonacci voulez-vous?");
    Lire(n);
    
    Ecrire("Suite de Fibonacci:");
    
    Si n >= 1 alors
        Ecrire(0);
    Finsi
    
    Si n >= 2 alors
        Ecrire(1);
    Finsi
    
    a &lt;- 0;
    b &lt;- 1;
    
    Pour i de 3 a n faire
        c &lt;- a + b;
        Ecrire(c);
        a &lt;- b;
        b &lt;- c;
    Finpour
Fin</pre>
        
        <h3>Exemple 5 : Nombres premiers</h3>
        <pre>Algorithme NombresPremiers;
Var
    n, i, j: Entier;
    estPremier: Booleen;
debut
    Ecrire("Entrez la limite N:");
    Lire(n);
    
    Ecrire("Nombres premiers jusqu'à", n, ":");
    
    Pour i de 2 a n faire
        estPremier &lt;- vrai;
        
        Pour j de 2 a i-1 faire
            
            Si i mod j == 0 alors
                estPremier &lt;- faux;
                Sortir;
            Finsi
        Finpour
        
        Si estPremier == vrai alors
            Ecrire(i);
        Finsi
    Finpour
Fin</pre>
        
        <h2>Bonnes Pratiques</h2>
        <ul>
            <li>Utilisez des noms de variables descriptifs.</li>
            <li>Indentez correctement votre code pour améliorer la lisibilité.</li>
            <li>Ajoutez des commentaires pour expliquer la logique complexe.</li>
            <li>Décomposez les problèmes complexes en étapes plus simples.</li>
            <li>Testez votre algorithme avec différents cas d'entrée.</li>
            <li>Utilisez des constantes pour les valeurs qui ne changent pas.</li>
        </ul>
        
        <div class="note">
            <p><strong>Note importante</strong> : Cette syntaxe d'algorithme est un pseudocode en français utilisé principalement à des fins pédagogiques. Elle n'est pas directement exécutable sur un ordinateur sans être traduite dans un langage de programmation comme Python, Java, C++, etc. Toutefois, vous pouvez utiliser AlgoFX pour exécuter ces algorithmes à des fins d'apprentissage uniquement.</p>
        </div>
        
        <p class="copyright">© 2025 Guide d'Algorithmes en Français</p>
    </body>
    </html>
    """
    return html

def show_syntax_help(parent):
    # Création de la boîte de dialogue
    help_dialog = QDialog(parent)
    help_dialog.setWindowTitle("Aide sur la syntaxe")
    help_dialog.resize(850, 650)  # Dimensions légèrement augmentées
    
    # Configuration du layout principal
    main_layout = QVBoxLayout()
    help_dialog.setLayout(main_layout)
    
    # Création du widget de texte
    help_text_widget = QTextEdit()
    
    # Configuration de la police
    code_font = QFont("Consolas", 12)  # Police monospace moderne
    if not code_font.exactMatch():
        code_font = QFont("Courier New", 12)  # Fallback si Consolas n'est pas disponible
    
    help_text_widget.setFont(code_font)
    
    # Détecter le thème du système ou de l'application
    is_dark_theme = parent.is_dark_theme()
    
    # Appliquer le style de la scrollbar en fonction du thème
    if is_dark_theme:
        scrollbar_style = """
            QScrollBar:vertical {
                background: #2d2d30;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #777777;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: #2d2d30;
                height: 12px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #555555;
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #777777;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """
    else:
        scrollbar_style = """
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #cdcdcd;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background: #f0f0f0;
                height: 12px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #cdcdcd;
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """
    
    help_text_widget.setStyleSheet(scrollbar_style)
    
    # Définir le texte formaté en HTML et rendre en lecture seule
    help_text_widget.setHtml(get_formatted_syntax_help(parent, is_dark_theme))
    help_text_widget.setReadOnly(True)
    
    # Ajouter le widget au layout
    main_layout.addWidget(help_text_widget)
    
    # Boutons en bas
    button_layout = QHBoxLayout()
    
    # Bouton de fermeture
    close_button = QPushButton("Fermer")
    close_button.clicked.connect(help_dialog.accept)
    close_button.setFixedWidth(100)
    
    # Ajout de l'espacement et du bouton au layout
    button_layout.addStretch()
    button_layout.addWidget(close_button)
    main_layout.addLayout(button_layout)
    
    # Afficher la boîte de dialogue
    help_dialog.exec_()