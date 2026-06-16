#!/bin/bash

# 1. Nettoyage et réinitialisation de Git
rm -rf .git
git init

# 2. Configuration de votre identité
git config user.name "afar-wq"
git config user.email "adamfar2802@gmail.com"

# 3. Ajout des fichiers actuels du Quiz
git add .

# 4. Création du commit avec la date exacte d'aujourd'hui
echo "Création du commit initial..."
GIT_AUTHOR_DATE="2026-06-16T20:23:41" GIT_COMMITTER_DATE="2026-06-16T20:23:41" git commit -m "feat: initial commit for Quizz Website"

# 5. Branche principale et liaison GitHub
git branch -M main
git remote add origin https://github.com/afar-wq/cineexplorer.git

echo "----------------------------------------------------"
echo "Terminé ! Votre projet Quizz_Website est prêt."
echo "Pour l'envoyer sur GitHub, tapez : git push -u origin main --force"
echo "----------------------------------------------------"
