"""Extrait le script du jeu de web/index.html vers tests/game_full.js (utilisé par les tests Node)."""
import os, re
here = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(here, "..", "web", "index.html"), encoding="utf-8").read()
code = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
open(os.path.join(here, "game_full.js"), "w", encoding="utf-8").write(code)
print("tests/game_full.js régénéré")
