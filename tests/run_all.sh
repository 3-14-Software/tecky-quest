#!/usr/bin/env bash
# Reconstruit la version web puis lance toute la batterie de tests (Node >= 18 + Python 3).
set -e
cd "$(dirname "$0")/.."
python3 carte.py --verifier          # carte.json : correct, et au format de l'éditeur
python3 episodes.py                  # episodes.json : des cartes qui existent et se rejoignent
python3 pack_web.py
python3 tests/regen.py
fail=0
for t in sim immune threat read ring clues berger map nettete hens traffic butterflies save balade pad glyphs effects farm cows villagers hud leon iris train piquette tunnel edge world music sfx ducks textes cartes episodes voyage hortense anatole zoe nage theo yvon suzanne adversaires ete_finitions titre cote_sons saisons rest options quests badges weather calm ending obstacles fence fence_scan placement editeur_sol; do
  echo "== $t"
  out=$(node tests/$t.js 2>&1) || fail=1
  echo "$out" | grep -E "ÉCHEC|^PB |problèmes [1-9]|Error" && fail=1 || true
  echo "$out" | grep -c "^ok" | sed 's/^/   ok : /'
done
out=$(python3 tests/edges.py) || fail=1         # aucun sprite coupé par son cadre
echo "$out" | tail -3
out=$(python3 tests/surcharges.py) || fail=1  # cartes changées par un épisode (carte.py, enregistrement de l'éditeur)
echo "$out" | grep -E "ÉCHEC|^surcharges"
python3 tests/nettete.py || fail=1     # images x4 : mêmes places que les images x2
python3 tests/saisons.py || fail=1     # images des saisons : mêmes formes et mêmes cadres qu'au printemps
out=$(python3 tests/heros.py) || fail=1       # Tecky et Alice (tecky2.py, alice2.py) : noms, pieds, cadres
echo "$out" | grep -E "ÉCHEC|^héros"
# répliques pour la synthèse vocale : la liste voix/repliques.csv est-elle à jour (et complète) ?
out=$(node tools/export_voix.js --check 2>&1) || fail=1
echo "$out"
echo "$out" | grep -qE "^PB |Error" && fail=1
exit $fail
