# 📈 BVMAC Analyst Pro

**Application web d'analyse technique pour les données de la Bourse des Valeurs Mobilières d'Afrique Centrale (BVMAC)**

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Fonctionnalités

### 📊 Visualisations Avancées
- **Graphiques interactifs** avec Plotly
- **Analyse technique complète** :
  - Moyennes mobiles (SMA 20 & 50)
  - Bandes de Bollinger
  - RSI (Relative Strength Index)
  - MACD avec signal line et histogramme
- **Échelle logarithmique** optionnelle
- **Sous-graphiques dynamiques** selon les indicateurs sélectionnés

### 🤖 Prévisions Intelligentes
- **Prophet (IA)** : Prévisions précises avec saisonnalité
- **Régression linéaire** : Fallback léger sans dépendances lourdes
- **Marges d'erreur** avec zones de confiance
- Horizon de prévision configurable (30-180 jours)

### 📥 Chargement de Données Robuste
- Support **XLSX** et **CSV**
- Gestion automatique des séparateurs (`,` `;` ou auto-détection)
- Conversion des virgules décimales (format FCFA)
- Nettoyage automatique des données manquantes

### 📈 Statistiques Clés
- Prix actuel, min, max, moyenne
- Variation en pourcentage depuis le début
- Nombre de jours analysés

---

## 🚀 Installation

### Prérequis
- Python 3.9 ou supérieur
- pip ou conda

### Étapes

1. **Cloner le repository**
   ```bash
   git clone https://github.com/Kmfranck/BVMAC.git
   cd BVMAC
   ```

2. **Créer un environnement virtuel** (recommandé)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

   **Note** : Si vous rencontrez des problèmes avec Prophet, installez scikit-learn uniquement :
   ```bash
   pip install streamlit pandas plotly numpy openpyxl scikit-learn
   ```

---

## 💻 Utilisation

### Lancer l'application

```bash
streamlit run viz.py
```

L'application s'ouvrira automatiquement dans votre navigateur à `http://localhost:8501`

### Workflow Utilisateur

1. 📂 **Charger un fichier** : Cliquez sur "Charger votre fichier" dans la barre latérale
2. 🔎 **Sélectionner une action** : Choisissez le mnémonique de l'action à analyser
3. ⚙️ **Configurer les options** :
   - Échelle logarithmique
   - Affichage des indicateurs (Bollinger, RSI, MACD)
4. 📊 **Consulter les graphiques** :
   - Analyse technique avec indicateurs
   - Statistiques clés (prix, min, max, variation)
5. 🔮 **Générer des prévisions** (optionnel) :
   - Cochez "Afficher les prévisions"
   - Sélectionnez l'horizon (jours)
   - Consultez les prévisions avec marges d'erreur

---

## 📊 Format des Données

Votre fichier doit contenir les colonnes suivantes :

| Colonne      | Type     | Description                        |
|--------------|----------|------------------------------------|
| `Date`       | datetime | Date (format DD/MM/YYYY accepté)  |
| `Mnemo`      | string   | Mnémonique de l'action (ex: "ORBNRW") |
| `Cours_rfrnc`| float    | Prix de fermeture (virgule ou point)|

### Exemple CSV
```
Date,Mnemo,Cours_rfrnc
01/01/2024,ORBNRW,1500.50
02/01/2024,ORBNRW,1505.75
03/01/2024,ORBNRW,1502.30
```

---

## 🔧 Détails Techniques

### Indicateurs Techniques

#### Moyennes Mobiles (SMA)
- **SMA 20** : Tendance court terme
- **SMA 50** : Tendance moyen terme

#### Bandes de Bollinger
```
Upper Band = SMA_20 + (2 × STD_20)
Lower Band = SMA_20 - (2 × STD_20)
```
Utilisées pour identifier les zones de suracheté/survendu.

#### RSI (14 périodes)
```
RS = Gain Moyen / Perte Moyenne
RSI = 100 - (100 / (1 + RS))
```
- RSI > 70 : Suracheté 🔴
- RSI < 30 : Survendu 🟢

#### MACD
```
MACD = EMA_12 - EMA_26
Signal Line = EMA_9(MACD)
Histogram = MACD - Signal Line
```

### Méthodes de Prévision

#### Option 1 : Prophet (Recommandé)
- Décomposition de séries chronologiques
- Gestion de la saisonnalité hebdomadaire & annuelle
- Marges d'erreur natives
- ⚠️ Nécessite `pystan` (lourd à installer)

#### Option 2 : Régression Linéaire
- Simple et rapide
- Pas de saisonnalité
- Idéal pour une tendance générale

---

## 🐛 Bugfix & Améliorations (v2.0)

### ✅ Corrections
- **Syntaxe Plotly** : Correction des appels `fig.add_trace()` pour les Bandes de Bollinger
- **Division par zéro** : Gestion du cas limite dans le calcul RSI
- **Validation données** : Vérification de l'existence de colonnes requises

### ✨ Améliorations
- Affichage des **statistiques clés** (min, max, moyenne, variation %)
- **Documentation complète** avec docstrings
- **Type hints** pour meilleure maintenabilité
- **Fonction réutilisable** pour les sous-graphiques
- **Meilleure UX** : Messages clairs, icônes, couleurs

---

## 📦 Dépendances

| Paquet | Version | Utilité |
|--------|---------|---------|
| streamlit | 1.40.1+ | Framework Web |
| pandas | 2.2.3+ | Manipulation de données |
| plotly | 5.24.1+ | Graphiques interactifs |
| numpy | 1.26.4+ | Calculs numériques |
| openpyxl | 3.11.0+ | Lecture Excel |
| prophet | 1.1.6+ | **(Optionnel)** Prévisions IA |
| scikit-learn | 1.5.2+ | **(Optionnel)** Régression |

---

## 🤝 Contribution

Les contributions sont bienvenues! Voici comment :

1. Fork le repository
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📋 Roadmap

- [ ] Export des graphiques en PNG/PDF
- [ ] Comparaison multi-actions
- [ ] Points pivots (Support/Résistance)
- [ ] Volume tradé (si données disponibles)
- [ ] Alertes automatiques (seuils personnalisés)
- [ ] Historique des analyses
- [ ] API REST

---

## 📄 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---

## 👤 Auteur

**Franck KM**  
GitHub: [@Kmfranck](https://github.com/Kmfranck)

---

## 📞 Support

Pour les questions ou problèmes, veuillez :
1. Vérifier les [issues existantes](https://github.com/Kmfranck/BVMAC/issues)
2. Créer une nouvelle [issue](https://github.com/Kmfranck/BVMAC/issues/new)
3. Consulter la documentation Streamlit : https://docs.streamlit.io

---

**Dernière mise à jour** : Décembre 2025  
**Statut** : ✅ Production-Ready
