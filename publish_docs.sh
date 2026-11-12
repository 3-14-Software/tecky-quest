#!/usr/bin/env bash
# Reconstruit le jeu et copie la version autonome (PWA, hors ligne) dans docs/ pour GitHub Pages.
set -e
cd "$(dirname "$0")"
python3 pack_web.py
# (docs/glitch/ : la démo de Glitch, le fork pour adultes, publiée depuis ../glitch : on n'y touche pas)
mkdir -p docs
find docs -mindepth 1 -maxdepth 1 ! -name glitch -exec rm -rf {} +
cp web/tecky_quest_web/{index.html,manifest.webmanifest,sw.js,icon-180.png,icon-192.png,icon-512.png} docs/
cp web/tecky_quest_web/*_x4*.png docs/      # images x4, chargées sur grand écran (pack_web.py : build_hd)
cp web/tecky_quest_web/saison_*.png docs/   # images des saisons (pack_web.py : build_saisons ; les x4 sont déjà copiées)
touch docs/.nojekyll
echo "docs/ à jour ($(du -sh docs | cut -f1))"
