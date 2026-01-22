# Consignes Permanentes de l'Agent

Ce document sert de référence pour toutes les interventions futures sur ce projet.

## 1. Style de Code et Sorties
- **AUCUN EMOJI** : Les sorties console (print) et les interfaces utilisateur doivent être strictement professionnelles et sobres. Pas de 🤖, 📊, ❌, ✅, etc.
- **Programmation Orientée Objet (POO)** : Privilégier l'architecture orientée objet pour la scalabilité et la maintenance, sauf si une approche fonctionnelle simple est nettement plus adaptée pour des scripts utilitaires.
- **Code Propre (Clean Code)** : 
  - Typage strict (Type Hinting) pour toutes les fonctions.
  - Docstrings pour les classes et méthodes publiques.
  - Gestion d'erreurs explicite (try/except ciblés).

## 2. Gestion des Fichiers
- **Fichiers Temporaires** : Les fichiers intermédiaires (comme les .tex générés avant le PDF) doivent être supprimés automatiquement après usage.
- **Pollution de la Racine** : Aucun fichier de test ou de log ne doit être créé à la racine du projet. Tout doit se faire dans le dossier `antigrav/` ou des dossiers dédiés (ex: `reports/`).

## 3. Structure du Projet
- Respecter l'arborescence définie dans le README.
- Les tests unitaires et scripts de validation doivent être placés dans `antigrav/tests/`.

## 4. Documentation
- Maintenir le README.md à jour avec les changements d'architecture.
