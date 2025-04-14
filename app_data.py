# app_data.py

# Données pour la boîte de dialogue "À propos"
about_text = (
            "<h2>À propos de l'application</h2>"
            "<p><strong>AlgoFX</strong> est un environnement de développement dédié à "
            "l'écriture, la compilation et l'exécution d'algorithmes en <em>langage naturel français</em>, "
            "les traduisant automatiquement en Python.</p>"
            "<p>Conçu pour l'enseignement, cet outil permet aux étudiants de se concentrer sur la logique "
            "algorithmique sans se heurter immédiatement à la syntaxe d'un langage de programmation classique.</p>"
            "<hr>"
            "<h3>À propos de l'auteur</h3>"
            "<p><strong>Farid Mezane</strong> — Enseignant en Informatique & Développeur de Logiciels</p>"
            "<p>Avec une solide expérience dans l'enseignement, le développement d'applications éducatives, "
            "et le support technique, je m'efforce de rendre les concepts informatiques plus accessibles "
            "et intuitifs pour tous les niveaux.</p>"
            "<p><strong>Spécialisation :</strong> création d'outils pédagogiques, développement multiplateforme, "
            "et applications sécurisées orientées apprentissage.</p>"
            "<p>Visitez mon site web pour en savoir plus : "
            "<a href='https://faridmezane.space' style='color:#88CCFF;'>faridmezane.space</a></p>"
)

# Aide sur la syntaxe
syntax_help_text = """Syntaxe d'algorithme:
Structure de base:
--------------------------------
Algorithme NomAlgorithme;
Var
    // Déclarations de variables
    nom: Type;
    a, b, c: Entier;  // Déclaration multiple
Debut
    // Instructions
Fin
Types de données:
--------------------------------
- Entier: nombres entiers (ex: 42, -10)
- Reel (ou Réel): nombres à virgule flottante (ex: 3.14, -0.5)
- Chaine de caractere: texte entre guillemets (ex: "Bonjour")
- Char : un caractere (ex: "a")
- Booleen :vrai ou faux
Variables et constantes:
--------------------------------
- Variables: a, b, resultat, etc.
- Déclaration multiple: a, b, c: Entier;
- Constantes:
  Const
  PI = 3.14159;
  TAUX_TVA = 19.6;
Opérations et expressions:
--------------------------------
- Arithmétiques: +, -, *, /, mod (modulo), div (div entier)
- Relationnels: ==, <> ou !=, <, >, <=, >=
- Logiques: et, ou, non
- Priorité standard: parenthèses, puis *, /, puis +, -
- support : sortir; /sortir de boucle (replcer break de language de programmation
Instructions de base:
--------------------------------
- Affectation: variable <- valeur;
- Lecture (une ou plusieurs valeurs): 
  lire(variable);
  lire(a, b, c);
- Écriture (une ou plusieurs valeurs): 
  ecrire("Texte");
  ecrire(a, b, "Résultat:", resultat);
Structures de contrôle:
--------------------------------
1. Condition simple:
   si condition alors
       instructions
   finsi
2. Condition avec alternative:
   si condition alors
       instructions1
   sinon
       instructions2
   finsi
3. Boucle TANT QUE:
   tantque condition faire
       instructions
   fintantque
4. Boucle POUR v1:
   pour variable de valeur1 a valeur2 faire
       instructions
   finpour
   Boucle POUR v2:
   pour variable de valeur1 allant a valeur2 faire
       instructions
   finpour
   Boucle POUR v3:
   pour variable allant de valeur1 a valeur2 faire
       instructions
   finpour
   
   Boucle POUR v4:
   pour variable de valeur1 a valeur2  pas n faire (increment de n)
       instructions
   finpour
   
Exemples complets:
--------------------------------
Exemple 1: Calcul de moyenne
--------------------------
Algorithme CalculMoyenne;
Var
    note1, note2, note3, moyenne: Reel;
Debut
    ecrire("Entrez trois notes:");
    lire(note1, note2, note3);
    
    moyenne <- (note1 + note2 + note3) / 3;
    
    ecrire("La moyenne est:", moyenne);
    
    si moyenne >= 10 alors
        ecrire("Félicitations, vous avez réussi!");
    sinon
        ecrire("Vous devez vous améliorer.");
    finsi
Fin
Exemple 2: Table de multiplication
--------------------------
Algorithme TableMultiplication;
Var
    nombre, i, resultat: Entier;
Debut
    ecrire("Quelle table voulez-vous afficher?");
    lire(nombre);
    
    pour i de 1 a 10 faire
        resultat <- nombre * i;
        ecrire(nombre, "x", i, "=", resultat);
    finpour
Fin
Exemple 3: Recherche du maximum
--------------------------
Algorithme RechercheMaximum;
Var
    n, nombre, maximum, i: Entier;
Debut
    ecrire("Combien de nombres voulez-vous comparer?");
    lire(n);
    
    ecrire("Entrez le nombre 1:");
    lire(nombre);
    maximum=nombre;
    i <- 2;
    tantque i <= n faire
        ecrire("Entrez le nombre", i, ":");
        lire(nombre);
        
        si nombre > maximum alors
            maximum <- nombre;
        finsi
        
        i <- i + 1;
    fintantque
    
    ecrire("Le maximum est:", maximum);
Fin
"""

templates = {
    "empty": """Algorithme MonAlgorithme;
Var

Const

Debut

    
Fin
""",
    "moyenne": """Algorithme CalculMoyenne;
Var
    note1, note2, note3, moyenne: Reel;
Debut
    ecrire("Entrez trois notes:");
    lire(note1, note2, note3);
    
    moyenne <- (note1 + note2 + note3) / 3;
    
    ecrire("La moyenne est:", moyenne);
    
    si moyenne >= 10 alors
        ecrire("Félicitations, vous avez réussi!");
    sinon
        ecrire("Vous devez vous améliorer.");
    finsi
Fin
""",
    "table": """Algorithme TableMultiplication;
Var
    nombre, i, resultat: Entier;
Debut
    ecrire("Quelle table voulez-vous afficher?");
    lire(nombre);
    
    pour i de 1 a 10 faire
        resultat <- nombre * i;
        ecrire(nombre, "x", i, "=", resultat);
    finpour
Fin
""",
    "maximum": """Algorithme RechercheMaximum;
Var
    n, nombre, maximum, i: Entier;
Debut
    ecrire("Combien de nombres voulez-vous comparer?");
    lire(n);
    
    ecrire("Entrez le nombre 1:");
    lire(nombre);
    maximum <- nombre;
    i <- 2;
    tantque i <= n faire
        ecrire("Entrez le nombre", i, ":");
        lire(nombre);
        
        si nombre > maximum alors
            maximum <- nombre;
        finsi
        
        i <- i + 1;
    fintantque
    
    ecrire("Le maximum est:", maximum);
Fin
""",
    "AfficherNombres": """Algorithme AfficherNombres;
Var
    nbLimite, i: Entier;
Debut
    ecrire("Entrer un nombre limite :");
    lire(nbLimite);
    
    pour i de 1 a nbLimite faire
        ecrire(i);
    finpour
Fin
""",
    "Somme10": """Algorithme Somme10;
Var
    i, valeurEntree, somme: Entier;
Debut
    somme <- 0;
    
    pour i de 1 a 10 faire
        ecrire("Entrer un nombre :");
        lire(valeurEntree);
        somme <- somme + valeurEntree;
    finpour
    
    ecrire("La somme est :", somme);
Fin
""",
    "CalculCercle": """Algorithme CalculCercle;
Var
    rayon, surface, circonference: Reel;
Const
    PI = 3.14159;
Debut
    // Algorithme qui calcule la surface et la circonférence d'un cercle
    // à partir du rayon entré par l'utilisateur
    ecrire("Entrez le rayon du cercle:");
    lire(rayon);

    surface <- PI * rayon * rayon;
    circonference <- 2 * PI * rayon;

    ecrire("Surface du cercle:", surface);
    ecrire("Circonférence du cercle:", circonference);
Fin
""",
    "CalculPGCD": """Algorithme CalculPGCD;
Var
    a, b, r: Entier;
Debut
    // Algorithme qui calcule le Plus Grand Commun Diviseur (PGCD)
    // de deux nombres à l'aide de l'algorithme d'Euclide
    ecrire("Entrez le premier nombre:");
    lire(a);
    ecrire("Entrez le deuxième nombre:");
    lire(b);

    // Assurer que a >= b
    si a < b alors
        r <- a;
        a <- b;
        b <- r;
    finsi

    // Algorithme d'Euclide
    tantque b != 0 faire
        r <- a mod b;
        a <- b;
        b <- r;
    fintantque

    ecrire("Le PGCD est:", a);
Fin
""",
    "CalculPPCM": """Algorithme CalculPPCM;
Var
    a, b, pgcd, ppcm: Entier;
    temp_a, temp_b, r: Entier;
Debut
    // Algorithme qui calcule le Plus Petit Commun Multiple (PPCM)
    // de deux nombres en utilisant la relation: PPCM(a,b) = (a*b)/PGCD(a,b)
    ecrire("Entrez le premier nombre:");
    lire(a);
    ecrire("Entrez le deuxième nombre:");
    lire(b);

    // Sauvegarder les valeurs originales
    temp_a <- a;
    temp_b <- b;

    // Assurer que a >= b
    si a < b alors
        r <- a;
        a <- b;
        b <- r;
    finsi

    // Algorithme d'Euclide pour le PGCD
    tantque b != 0 faire
        r <- a mod b;
        a <- b;
        b <- r;
    fintantque

    pgcd <- a;
    // PPCM = (a * b) / PGCD
    ppcm <- (temp_a * temp_b) / pgcd;

    ecrire("Le PPCM est:", ppcm);
Fin
""",
    "EquationPremierDegre": """Algorithme EquationPremierDegre;
Var
    a, b, x: Reel;
Debut
    // Algorithme qui résout une équation du premier degré de la forme ax + b = 0
    // et traite tous les cas particuliers (a=0, b=0)
    ecrire("Résolution de l'équation ax + b = 0");
    ecrire("Entrez la valeur de a:");
    lire(a);
    ecrire("Entrez la valeur de b:");
    lire(b);

    si a == 0 alors
        si b == 0 alors
            ecrire("L'équation admet une infinité de solutions");
        sinon
            ecrire("L'équation n'admet pas de solution");
        finsi
    sinon
        x <- -b / a;
        ecrire("La solution est x =", x);
    finsi
Fin
""",
    "EquationSecondDegre": """Algorithme EquationSecondDegre;
Var
    a, b, c, delta, x1, x2: Reel;
Debut
    // Algorithme qui résout une équation du second degré de la forme ax² + bx + c = 0
    // en calculant le discriminant delta et traitant tous les cas possibles
    ecrire("Résolution de l'équation ax² + bx + c = 0");
    ecrire("Entrez la valeur de a:");
    lire(a);
    ecrire("Entrez la valeur de b:");
    lire(b);
    ecrire("Entrez la valeur de c:");
    lire(c);

    si a == 0 alors
        // L'équation devient une équation du premier degré: bx + c = 0
        si b == 0 alors
            si c == 0 alors
                ecrire("L'équation admet une infinité de solutions");
            sinon
                ecrire("L'équation n'admet pas de solution");
            finsi
        sinon
            x1 <- -c / b;
            ecrire("L'équation est du premier degré, la solution est x =", x1);
        finsi
    sinon
        delta <- b * b - 4 * a * c;

        si delta < 0 alors
            ecrire("L'équation n'admet pas de solution réelle");
        sinon
            si delta == 0 alors
                x1 <- -b / (2 * a);
                ecrire("L'équation admet une solution double: x =", x1);
            sinon
                x1 <- (-b - racine(delta)) / (2 * a);
                x2 <- (-b + racine(delta)) / (2 * a);
                ecrire("L'équation admet deux solutions:");
                ecrire("x1 =", x1);
                ecrire("x2 =", x2);
            finsi
        finsi
    finsi
Fin
""",
    "NombresImpairs": """Algorithme NombresImpairs;
Var
    n, i: Entier;
Debut
    // Algorithme qui affiche tous les nombres pairs de 0 à n
    ecrire("Entrez la valeur limite n:");
    lire(n);

    ecrire("Nombres pairs de 1 à", n, ":");
    
    pour i de 1 allant a n pas 2 faire
        ecrire(i);
        
    finpour

Fin
""",
    "NombresPairs": """Algorithme NombresPairs;
Var
    n, i: Entier;
Debut
    // Algorithme qui affiche tous les nombres pairs de 0 à n
    ecrire("Entrez la valeur limite n:");
    lire(n);

    ecrire("Nombres pairs de 0 à", n, ":");
    
    pour i de 0 allant a n pas 2 faire
        ecrire(i);
        
    finpour

Fin
""",
    "SommeN": """Algorithme SommeN;
Var
    n, i, nombre, somme: Entier;
Debut
    // Algorithme qui calcule la somme de n nombres entrés par l'utilisateur
    ecrire("Combien de nombres voulez-vous additionner?");
    lire(n);

    somme <- 0;
    pour i de 1 a n faire
        ecrire("Entrez le nombre", i, ":");
        lire(nombre);
        somme <- somme + nombre;
    finpour

    ecrire("La somme des", n, "nombres est:", somme);
Fin
"""
,
    "DecimalVersBinaire": """Algorithme DecimalVersBinaire;
Var
    nombreDecimal, binaire, reste, multiplicateur: entier;
Debut

    // Demander à l'utilisateur de saisir un nombre entier en base décimale
    écrire("Entrez un nombre entier en base décimale : ");
    lire(nombreDecimal);

    // Initialiser le résultat binaire et le multiplicateur
    binaire <- 0;
    multiplicateur <- 1;

    // Convertir le nombre décimal en binaire
    tantque nombreDecimal <> 0 faire
        reste <- nombreDecimal mod 2;              // Obtenir le bit le moins significatif
        binaire <- binaire + (reste * multiplicateur); // Ajouter le bit à la position correspondante
        nombreDecimal <- nombreDecimal div 2;      // Réduire le nombre décimal
        multiplicateur <- multiplicateur * 10;     // Passer à la position binaire suivante
    fintantque

    // Afficher le résultat en binaire
    écrire("Représentation binaire : ", binaire);

Fin"""
}

# Position du curseur après insertion pour le template vide
empty_template_cursor_position = 49  # Position après "// Déclaration des variables"

# Vous pouvez ajouter d'autres données ici
app_name = "Algorithme IDE"
app_version = "1.0.0"
app_copyright = "© 2025 Farid Mezane"

# Vous pouvez aussi ajouter des dictionnaires, des listes, etc.
supported_languages = ["Algorithme", "Python", "JavaScript"]