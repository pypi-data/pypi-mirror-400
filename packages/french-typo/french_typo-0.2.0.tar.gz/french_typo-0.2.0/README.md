# French Typo 🇫🇷

*French Typo* est un moteur **agnostique** de correction typographique française, écrit en Python.

Il applique automatiquement des règles linguistiques françaises **sans dépendre d’un format**, d’une interface graphique ou d’un moteur de rendu particulier.

Il est conçu pour être utilisé aussi bien :
- comme **bibliothèque Python**
- que comme **brique interne** d’outils (éditeur, script, addon Anki, pipeline de traitement de texte, etc.)

---

## 🎯 Objectifs du projet

French Typo repose sur quelques principes forts :

- **Agnostique du format**  
  Aucun HTML, Markdown, LaTeX ou autre format spécifique

- **Aucune dépendance UI**  
  Pas de GUI, pas de framework graphique

- **Règles linguistiques françaises uniquement**  
  Pas de mise en forme stylistique arbitraire

- **Entrée / sortie en Unicode simple**  
  Une chaîne de caractères en entrée, une chaîne corrigée en sortie

---

## ✨ Fonctionnalités actuelles

### Espaces

- Suppression des espaces multiples
- Suppression des espaces avant les points
- Nettoyage des espaces en début et fin de ligne

### Unités

- Normalisation des unités courantes :
  - `KM`, `Km`, `kms` → `km`
  - `KG`, `kgs` → `kg`
- Normalisation de certaines notations :
  - `kg/m3` → `kg/m³`
  - `km/h` (insensible à la casse)

### Nombres

- Préservation des ordinaux français :
  - `1er`, `2e`, `3e`, `2d`
- Base prête pour extensions futures (`n°`, séparateurs, etc.)

---

## 📦 Installation

### Depuis PyPI

```bash
pip install french-typo
```

### Depuis le dépôt

```bash
git clone https://github.com/dhrions/french-typo.git
cd french-typo
pip install .
```

### Mode développement

```bash
pip install -e .
```

---

## 🚀 Utilisation

### Exemple simple

```python
from french_typo.formatter import format_text

text = "Article 5 : 10  KM ."
result = format_text(text)
print(result)
```

Résultat attendu :

```text
Article 5 : 10 km.
```

---

## 🔄 Pipeline typographique

Les règles sont appliquées dans l’ordre suivant :

1. Normalisation des espaces
2. Normalisation des unités
3. Normalisation des nombres

```python
def format_text(text: str) -> str:
    text = normalize_spaces(text)
    text = normalize_units(text)
    text = normalize_numbers(text)
    return text
```

Cet ordre est volontaire et peut évoluer.

---

## 🧪 Tests

Les tests utilisent **pytest**.

```bash
pytest
```

Structure :

```text
tests/
└── core/
    ├── test_formatter.py
    ├── test_spaces.py
    ├── test_units.py
    └── test_numbers.py
```

Chaque règle est testée **indépendamment**, garantissant :

- une bonne couverture
- une maintenance simple
- une détection rapide des régressions

---

## 🧱 Architecture

```text
french_typo/
├── formatter.py        # Point d’entrée principal
└── rules/
    ├── spaces.py       # Règles sur les espaces
    ├── units.py        # Règles sur les unités
    └── numbers.py      # Règles sur les nombres
```

Chaque règle est :

- pure
- sans effet de bord
- testable indépendamment

---

## 🔌 Cas d’usage

French Typo peut être intégré dans :

- Addons Anki
- Éditeurs de texte
- Outils NLP
- Scripts de nettoyage de corpus
- Pipelines CI de qualité rédactionnelle

Un addon Anki est déjà fourni :  
`french-typo.ankiaddon.zip`

---

## 🗺️ Roadmap (idées)

- Espaces insécables françaises (`; : ! ?`)
- Guillemets français (« »)
- Normalisation de `n°`
- Séparateurs de milliers (`1 000`)
- Dates et heures
- Configuration optionnelle des règles

---

## 📄 Licence

Ce projet est distribué sous licence **MIT**.  
Voir le fichier `LICENSE` pour plus de détails.

---

## 🤝 Contributions

Les contributions sont les bienvenues :

- nouvelles règles typographiques
- amélioration des regex existantes
- ajout de tests
- retours d’usage réel

Les PR propres, testées et documentées sont fortement appréciées.
