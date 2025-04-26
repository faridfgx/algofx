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
syntax_help_text = """
# Guide d'Algorithmes en AlgoFX

## Structure de Base d'un Algorithme
Tout algorithme suit une structure standard composée de trois parties principales :

```
Algorithme NomAlgorithme;
Var
    // Déclarations de variables
    nom: Type;
    a, b, c: entier;  // Déclaration multiple
Const
    p=3.1415; // Déclaration des constantes
Debut
    // Instructions
Fin
```

## Types de Données
| Type | Description | Exemples |
|------|-------------|----------|
| entier | Nombres entiers | 42, -10, 0 |
| reel | Nombres à virgule flottante | 3.14, -0.5, 2.0 |
| chaine de caractere | Texte entre guillemets | "Bonjour", "2023", "" |
| caractere | Un seul caractère | "a", "5", "!" |
| booleen | Valeur logique | vrai, faux |

## Variables et Constantes

### Déclaration de Variables
```
var
    age: entier;
    nom: chaine;
    a, b, c: entier;  // Déclaration multiple
    estValide: booleen;
```

### Déclaration de Constantes
```
const
    PI = 3.14159;
    TAUX_TVA = 20.0;
    MESSAGE_BIENVENUE = "Bonjour !";
```

## Opérations et Expressions

### Opérateurs Arithmétiques
| Opérateur | Description | Exemple |
|-----------|-------------|---------|
| + | Addition | a + b |
| - | Soustraction | a - b |
| * | Multiplication | a * b |
| / | Division | a / b |
| mod | Modulo (reste de division) | a mod b |
| div | Division entière | a div b |
| Puissance | puissance | a puissance b |

### Opérateurs Relationnels
| Opérateur | Description | Exemple |
|-----------|-------------|---------|
| == | Égal à | a == b |
| <> ou != | Différent de | a <> b |
| < | Inférieur à | a < b |
| > | Supérieur à | a > b |
| <= | Inférieur ou égal à | a <= b |
| >= | Supérieur ou égal à | a >= b |

### Opérateurs Logiques
| Opérateur | Description | Exemple |
|-----------|-------------|---------|
| et | ET logique | (a > 0) et (b < 10) |
| ou | OU logique | (a == 0) ou (b == 0) |
| non | NON logique | non(a == b) |

Note sur la priorité des opérations : parenthèses, puis puissance, puis multiplication/division, puis addition/soustraction.

## Instructions de Base

### Affectation
```
variable <- valeur;
```
Exemple : somme <- a + b;

### Lecture (Entrée)
```
lire(variable);
lire(a, b, c);  // Lecture multiple
```

### Écriture (Sortie)
```
ecrire("Texte");
ecrire(a, b, "Résultat:", resultat);  // Sortie multiple
```

## Structures de Contrôle

### Condition Simple
```
si condition alors
    instructions
finsi
```

### Condition avec Alternative
```
si condition alors
    instructions1
sinon
    instructions2
finsi
```

### Conditions Imbriquées
```
si condition1 alors
    instructions1
sinon
    si condition2 alors
        instructions2
    sinon
        instructions3
    finsi
finsi
```

### Boucle TANT QUE
```
tantque condition faire
    instructions
fintantque
```

### Boucle POUR
```
pour variable de valeur1 a valeur2 faire
    instructions
finpour

// Avec un pas spécifique
pour variable de valeur1 a valeur2 pas n faire
    instructions
finpour
```

### Instruction SORTIR
Permet de sortir d'une boucle prématurément :

```
tantque condition faire
    si autreCondition alors
        sortir;  // Quitte la boucle
    finsi
    instructions
fintantque
```

## Fonctions Mathématiques
- racine(x) : Calcule la racine carrée de x
- puissance : Opérateur puissance (ex: 2 puissance 3 = 8)
- mod : Opérateur modulo (reste de la division)
- div : Division entière

## Exemples Complets

### Exemple 1 : Calcul de factorielle
```
Algorithme Factoriel;
Var
    n, fact, i: entier;
Debut
    ecrire("Entrez un nombre pour calculer sa factorielle:");
    lire(n);
    
    fact <- 1;
    
    pour i de 1 a n faire
        fact <- fact * i;
    finpour
    
    ecrire("La factorielle de", n, "est", fact);
Fin
```

### Exemple 2 : Vérification d'un palindrome
```
Algorithme VerificationPalindrome;
Var
    nombre, copie, inverse, chiffre: entier;
Debut
    ecrire("Entrez un nombre:");
    lire(nombre);
    
    copie <- nombre;
    inverse <- 0;
    
    tantque copie > 0 faire
        chiffre <- copie mod 10;
        inverse <- inverse * 10 + chiffre;
        copie <- copie div 10;
    fintantque
    
    si nombre == inverse alors
        ecrire(nombre, "est un palindrome");
    sinon
        ecrire(nombre, "n'est pas un palindrome");
    finsi
Fin
```

### Exemple 3 : Conversion de température
```
Algorithme ConversionTemperature;
Var
    choix: entier;
    celsius, fahrenheit: reel;
Debut
    ecrire("Conversion de température");
    ecrire("1- Celsius vers Fahrenheit");
    ecrire("2- Fahrenheit vers Celsius");
    ecrire("Entrez votre choix (1 ou 2):");
    
    lire(choix);
    
    si choix == 1 alors
        ecrire("Entrez la température en Celsius:");
        lire(celsius);
        fahrenheit <- (celsius * 9/5) + 32;
        ecrire(celsius, "°C équivaut à", fahrenheit, "°F");
    sinon
        si choix == 2 alors
            ecrire("Entrez la température en Fahrenheit:");
            lire(fahrenheit);
            celsius <- (fahrenheit - 32) * 5/9;
            ecrire(fahrenheit, "°F équivaut à", celsius, "°C");
        sinon
            ecrire("Choix invalide");
        finsi
    finsi
Fin
```

### Exemple 4 : Suite de Fibonacci
```
Algorithme SuiteFibonacci;
Var
    n, i, a, b, c: entier;
Debut
    ecrire("Combien de termes de la suite de Fibonacci voulez-vous?");
    lire(n);
    
    ecrire("Suite de Fibonacci:");
    
    si n >= 1 alors
        ecrire(0);
    finsi
    
    si n >= 2 alors
        ecrire(1);
    finsi
    
    a <- 0;
    b <- 1;
    
    pour i de 3 a n faire
        c <- a + b;
        ecrire(c);
        a <- b;
        b <- c;
    finpour
Fin
```

### Exemple 5 : Nombres premiers
```
Algorithme NombresPremiers;
var
    n, i, j, temp: entier;
    estPremier: booleen;
debut
    ecrire("Entrez la limite N:");
    lire(n);
    
    ecrire("Nombres premiers jusqu'à", n, ":");
    
    pour i de 2 a n faire
        estPremier <- vrai;
        
        pour j de 2 a i-1 faire
            temp <- i mod j;
            si temp == 0 alors
                estPremier <- faux;
                sortir;
            finsi
        finpour
        
        si estPremier == vrai alors
            ecrire(i);
        finsi
    finpour
Fin
```

## Bonnes Pratiques
- Utilisez des noms de variables descriptifs.
- Indentez correctement votre code pour améliorer la lisibilité.
- Ajoutez des commentaires pour expliquer la logique complexe.
- Décomposez les problèmes complexes en étapes plus simples.
- Testez votre algorithme avec différents cas d'entrée.
- Utilisez des constantes pour les valeurs qui ne changent pas.

**Note importante** : Cette syntaxe d'algorithme est un pseudocode en français utilisé principalement à des fins pédagogiques. Elle n'est pas directement exécutable sur un ordinateur sans être traduite dans un langage de programmation comme Python, Java, C++, etc. Toutefois, vous pouvez utiliser AlgoFX pour exécuter ces algorithmes à des fins d'apprentissage uniquement.

© 2025 Guide d'Algorithmes en Français
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
    Ecrire("Entrez trois notes:");
    Lire(note1, note2, note3);
    
    moyenne <- (note1 + note2 + note3) / 3;
    
    Ecrire("La moyenne est:", moyenne);
    
    Si moyenne >= 10 alors
        ecrire("Félicitations, vous avez réussi!");
    Sinon
        ecrire("Vous devez vous améliorer.");
    Finsi
Fin
""",
    "table": """Algorithme TableMultiplication;
Var
    nombre, i, resultat: Entier;
Debut
    Ecrire("Quelle table voulez-vous afficher?");
    Lire(nombre);
    
    Pour i de 1 a 10 faire
        resultat <- nombre * i;
        Ecrire(nombre, "x", i, "=", resultat);
    Finpour
Fin
""",
    "maximum": """Algorithme RechercheMaximum;
Var
    n, nombre, maximum, i: Entier;
Debut
    Ecrire("Combien de nombres voulez-vous comparer?");
    Lire(n);
    
    Ecrire("Entrez le nombre 1:");
    Lire(nombre);
    maximum <- nombre;
    i <- 2;
    Tantque i <= n faire
        Ecrire("Entrez le nombre", i, ":");
        Lire(nombre);
        
        Si nombre > maximum alors
            maximum <- nombre;
        Finsi
        
        i <- i + 1;
    Fintantque
    
    Ecrire("Le maximum est:", maximum);
Fin
""",
    "AfficherNombres": """Algorithme AfficherNombres;
Var
    nbLimite, i: Entier;
Debut
    Ecrire("Entrer un nombre limite :");
    Lire(nbLimite);
    
    Pour i de 1 a nbLimite faire
        Ecrire(i);
    Finpour
Fin
""",
    "Somme10": """Algorithme Somme10;
Var
    i, valeurEntree, somme: Entier;
Debut
    somme <- 0;
    
    Pour i de 1 a 10 faire
        Ecrire("Entrer un nombre :");
        Lire(valeurEntree);
        somme <- somme + valeurEntree;
    Finpour
    
    Ecrire("La somme est :", somme);
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
    Ecrire("Entrez le rayon du cercle:");
    Lire(rayon);

    surface <- PI * rayon * rayon;
    circonference <- 2 * PI * rayon;

    Ecrire("Surface du cercle:", surface);
    Ecrire("Circonférence du cercle:", circonference);
Fin
""",
    "CalculPGCD": """Algorithme CalculPGCD;
Var
    a, b, r: Entier;
Debut
    // Algorithme qui calcule le Plus Grand Commun Diviseur (PGCD)
    // de deux nombres à l'aide de l'algorithme d'Euclide
    Ecrire("Entrez le premier nombre:");
    Lire(a);
    Ecrire("Entrez le deuxième nombre:");
    Lire(b);

    // Assurer que a >= b
    Si a < b alors
        r <- a;
        a <- b;
        b <- r;
    Finsi

    // Algorithme d'Euclide
    Tantque b != 0 faire
        r <- a mod b;
        a <- b;
        b <- r;
    Fintantque

    Ecrire("Le PGCD est:", a);
Fin
""",
    "CalculPPCM": """Algorithme CalculPPCM;
Var
    a, b, pgcd, ppcm: Entier;
    temp_a, temp_b, r: Entier;
Debut
    // Algorithme qui calcule le Plus Petit Commun Multiple (PPCM)
    // de deux nombres en utilisant la relation: PPCM(a,b) = (a*b)/PGCD(a,b)
    Ecrire("Entrez le premier nombre:");
    Lire(a);
    Ecrire("Entrez le deuxième nombre:");
    Lire(b);

    // Sauvegarder les valeurs originales
    temp_a <- a;
    temp_b <- b;

    // Assurer que a >= b
    Si a < b alors
        r <- a;
        a <- b;
        b <- r;
    Finsi

    // Algorithme d'Euclide pour le PGCD
    Tantque b != 0 faire
        r <- a mod b;
        a <- b;
        b <- r;
    Fintantque

    pgcd <- a;
    // PPCM = (a * b) / PGCD
    ppcm <- (temp_a * temp_b) / pgcd;

    Ecrire("Le PPCM est:", ppcm);
Fin
""",
    "EquationPremierDegre": """Algorithme EquationPremierDegre;
Var
    a, b, x: Reel;
Debut
    // Algorithme qui résout une équation du premier degré de la forme ax + b = 0
    // et traite tous les cas particuliers (a=0, b=0)
    Ecrire("Résolution de l'équation ax + b = 0");
    Ecrire("Entrez la valeur de a:");
    Lire(a);
    Ecrire("Entrez la valeur de b:");
    Lire(b);

    Si a == 0 alors
        Si b == 0 alors
            Ecrire("L'équation admet une infinité de solutions");
        Sinon
            Ecrire("L'équation n'admet pas de solution");
        Finsi
    Sinon
        x <- -b / a;
        Ecrire("La solution est x =", x);
    Finsi
Fin
""",
    "EquationSecondDegre": """Algorithme EquationSecondDegre;
Var
    a, b, c, delta, x1, x2: Reel;
Debut
    // Algorithme qui résout une équation du second degré de la forme ax² + bx + c = 0
    // en calculant le discriminant delta et traitant tous les cas possibles
    Ecrire("Résolution de l'équation ax² + bx + c = 0");
    Ecrire("Entrez la valeur de a:");
    Lire(a);
    Ecrire("Entrez la valeur de b:");
    Lire(b);
    Ecrire("Entrez la valeur de c:");
    Lire(c);

    Si a == 0 alors
        // L'équation devient une équation du premier degré: bx + c = 0
        Si b == 0 alors
            Si c == 0 alors
                Ecrire("L'équation admet une infinité de solutions");
            Sinon
                Ecrire("L'équation n'admet pas de solution");
            Finsi
        Sinon
            x1 <- -c / b;
            Ecrire("L'équation est du premier degré, la solution est x =", x1);
        Finsi
    Sinon
        delta <- b * b - 4 * a * c;

        Si delta < 0 alors
            Ecrire("L'équation n'admet pas de solution réelle");
        Sinon
            Si delta == 0 alors
                x1 <- -b / (2 * a);
                Ecrire("L'équation admet une solution double: x =", x1);
            Sinon
                x1 <- (-b - racine(delta)) / (2 * a);
                x2 <- (-b + racine(delta)) / (2 * a);
                Ecrire("L'équation admet deux solutions:");
                Ecrire("x1 =", x1);
                Ecrire("x2 =", x2);
            Finsi
        Finsi
    Finsi
Fin
""",
    "NombresImpairs": """Algorithme NombresImpairs;
Var
    n, i: Entier;
Debut
    // Algorithme qui affiche tous les nombres pairs de 0 à n
    Ecrire("Entrez la valeur limite n:");
    Lire(n);

    Ecrire("Nombres pairs de 1 à", n, ":");
    
    Pour i de 1 allant a n pas 2 faire
        Ecrire(i);
        
    Finpour

Fin
""",
    "NombresPairs": """Algorithme NombresPairs;
Var
    n, i: Entier;
Debut
    // Algorithme qui affiche tous les nombres pairs de 0 à n
    Ecrire("Entrez la valeur limite n:");
    Lire(n);

    Ecrire("Nombres pairs de 0 à", n, ":");
    
    Pour i de 0 allant a n pas 2 faire
        Ecrire(i);
    Finpour

Fin
""",
    "SommeN": """Algorithme SommeN;
Var
    n, i, nombre, somme: Entier;
Debut
    // Algorithme qui calcule la somme de n nombres entrés par l'utilisateur
    Ecrire("Combien de nombres voulez-vous additionner?");
    Lire(n);

    somme <- 0;
    Pour i de 1 a n faire
        Ecrire("Entrez le nombre", i, ":");
        Lire(nombre);
        somme <- somme + nombre;
    Finpour

    Ecrire("La somme des", n, "nombres est:", somme);
Fin
"""
,
    "DecimalVersBinaire": """Algorithme DecimalVersBinaire;
Var
    nombreDecimal, binaire, reste, multiplicateur: entier;
Debut

    // Demander à l'utilisateur de saisir un nombre entier en base décimale
    Ecrire("Entrez un nombre entier en base décimale : ");
    Lire(nombreDecimal);

    // Initialiser le résultat binaire et le multiplicateur
    binaire <- 0;
    multiplicateur <- 1;

    // Convertir le nombre décimal en binaire
    Tantque nombreDecimal <> 0 faire
        reste <- nombreDecimal mod 2;              // Obtenir le bit le moins significatif
        binaire <- binaire + (reste * multiplicateur); // Ajouter le bit à la position correspondante
        nombreDecimal <- nombreDecimal div 2;      // Réduire le nombre décimal
        multiplicateur <- multiplicateur * 10;     // Passer à la position binaire suivante
    Fintantque

    // Afficher le résultat en binaire
    Ecrire("Représentation binaire : ", binaire);

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