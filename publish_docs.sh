#!/usr/bin/env bash
# Reconstruit le jeu et copie la version autonome (PWA, hors ligne) dans docs/ pour GitHub Pages.
set -e
cd "$(dirname "$0")"
python3 pack_web.py
# (docs/glitch/ : la démo de Glitch, le fork pour adultes, publiée depuis ../glitch : on n'y touche pas)
mkdir -p docs
find docs -mindepth 1 -maxdepth 1 ! -name glitch -exec rm -rf {} +
cp web/tecky_quest_web/{index.html,manifest.webmanifest,sw.js,icon-180.png,icon-192.png,icon-512.png} docs/
touch docs/.nojekyll
echo "docs/ à jour ($(du -sh docs | cut -f1))"
