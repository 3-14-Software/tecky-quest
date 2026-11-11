"""
Capture du jeu en 1920 x 1080, avec les images nettes (x4), dans Chromium sans fenêtre.

Il faut d'abord construire le jeu (python3 pack_web.py) et servir web/tecky_quest_web sur le port 8765
(./serve.sh 8765, ou l'aperçu « tecky-web »). Puis, depuis la racine du dépôt :

    python3 v2/capture.py sortie.png "x,y,mode" ["js"] [--hud]

x, y : la case où placer Tecky ; mode : aventure ou balade (la partie démarre là, comme « Essayer ici » de
l'éditeur). js : du JavaScript lancé une fois, la partie démarrée (il a accès à tout le jeu : P, alice, dogs,
update()…). Pour figer une scène, finir par « update = function () {}; ». --hud : garder l'interface.

Une étiquette, en bas à gauche, dit ce que le jeu lisait au moment de la capture : « HD.k = 2 » = images x4.
Sans elle, rien ne prouve que la capture n'a pas été prise avant leur chargement (c'est arrivé).

Pièges : un profil Chromium jetable (sinon il s'adresse à l'instance déjà ouverte et ne rend jamais la main) ;
--timeout plutôt que --virtual-time-budget (qui bloque) ; les deux <img> des pages x4 retardent la fin du chargement
de la page, donc la capture, le temps que le jeu charge les siennes.
"""
import os
import shutil
import subprocess
import sys
import tempfile

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER = os.path.join(RACINE, "web", "tecky_quest_web")
PORT = 8765


def capturer(sortie, x, y, mode="balade", js="", hud=False):
    base = open(os.path.join(DOSSIER, "index.html"), encoding="utf-8").read()
    k = base.index("<script>") + len("<script>")
    page = (base[:k] + f"\nconst ESSAI = [{x}, {y}, '{mode}'];\n" + base[k:]
            + '<img src="atlas_x4_0.png" style="display:none"><img src="atlas_x4_1.png" style="display:none">'
            + '<div id="etiquette" style="position:fixed;left:8px;bottom:8px;font:20px monospace;color:#fff;'
              'background:#000;padding:2px 8px;z-index:9">?</div>\n<script>\n'
            + ("" if hud else "drawHUD = function () {}; drawBanner = function () {}; drawFsButton = function () {};\n")
            + "let fait = false;\nsetInterval(function () {\n"
              "  document.getElementById('etiquette').textContent = 'HD.k = ' + HD.k + ', echelle ' + scale;\n"
              "  if (!fait && state === 'play') { fait = true; " + js + " }\n}, 50);\n</script>\n")
    fichier = os.path.join(DOSSIER, "_capture.html")
    open(fichier, "w", encoding="utf-8").write(page)
    profil = tempfile.mkdtemp(prefix="capture-")
    try:
        subprocess.run(["chromium-browser", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1920,1080", f"--user-data-dir={profil}",
                        "--timeout=12000", f"--screenshot={os.path.abspath(sortie)}",
                        f"http://localhost:{PORT}/_capture.html"], capture_output=True, timeout=90)
    finally:
        os.remove(fichier)
        shutil.rmtree(profil, ignore_errors=True)
    return os.path.exists(sortie)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--hud"]
    if len(args) < 2:
        sys.exit(__doc__)
    x, y, mode = args[1].split(",")
    ok = capturer(args[0], x, y, mode, args[2] if len(args) > 2 else "", "--hud" in sys.argv)
    print(args[0] if ok else "capture manquée : le jeu est-il servi sur le port %d ?" % PORT)
