#!/usr/bin/env bash
# Reconstruit la version web puis lance toute la batterie de tests (Node >= 18 + Python 3).
set -e
cd "$(dirname "$0")/.."
python3 pack_web.py
python3 tests/regen.py
fail=0
for t in sim immune threat read ring clues berger map hens traffic butterflies save balade pad effects farm tunnel world ducks rest options quests badges weather obstacles fence fence_scan placement; do
  echo "== $t"
  out=$(node tests/$t.js 2>&1) || fail=1
  echo "$out" | grep -E "ÉCHEC|^PB |problèmes [1-9]|Error" && fail=1 || true
  echo "$out" | grep -c "^ok" | sed 's/^/   ok : /'
done
python3 tests/edges.py | tail -3
exit $fail
