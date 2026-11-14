"""Images des saisons (web/saison_<nom>_*.png, écrites par pack_web.build_saisons) : le tileset et les sprites
redessinés avec la palette d'une saison. Mêmes formes qu'au printemps (seules les couleurs changent), mêmes cadres ;
les images x4 réduites de moitié redonnent les images x2."""
import json
import os
import re
import sys

import numpy as np
from PIL import Image

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
WEB = os.path.join(RACINE, "web")
SAISON_Y = 1 << 20
echecs = 0


def ok(cond, msg):
    global echecs
    print(("ok : " if cond else "ÉCHEC : ") + msg)
    echecs += not cond


def alpha(a, b):
    """Part des pixels dont l'opacité diffère nettement entre deux images de même taille."""
    a, b = (np.asarray(im.convert("RGBA"), dtype=np.int16) for im in (a, b))
    return float((np.abs(a[..., 3] - b[..., 3]) > 96).mean())


def couleur(a, b):
    """Part des pixels opaques dont la couleur diffère nettement."""
    a, b = (np.asarray(im.convert("RGBA"), dtype=np.int16) for im in (a, b))
    return float(((np.abs(a[..., :3] - b[..., :3]).max(axis=-1) > 12) & (a[..., 3] > 128)).mean())


page = open(os.path.join(WEB, "index.html"), encoding="utf-8").read()
ATLAS = json.loads(re.search(r"const ATLAS = (\{.*?\});\n", page).group(1))
SAISONS = json.loads(re.search(r"const SAISONS = (\{.*?\});\n", page).group(1))
episodes = json.load(open(os.path.join(RACINE, "episodes.json"), encoding="utf-8"))["episodes"]
voulues = sorted({e["saison"] for e in episodes} - {"printemps"})
ok(sorted(SAISONS) == voulues, "une saison construite pour chaque saison d'épisode, hors le printemps : " + ", ".join(voulues))
atlas, tuiles = Image.open(os.path.join(WEB, "atlas.png")), Image.open(os.path.join(WEB, "tiles.png"))
fichier = lambda adresse: os.path.join(WEB, adresse.split("?")[0])
for nom, s in SAISONS.items():
    t = Image.open(fichier(s["tiles"]))
    ok(t.size == tuiles.size and alpha(t, tuiles) == 0, f"{nom} : son tileset a la taille et les formes de celui du printemps")
    c = couleur(t, tuiles)
    ok(c > 0.2, f"{nom} : ses tuiles ont d'autres couleurs ({c * 100:.0f} % des pixels)")
    a = Image.open(fichier(s["atlas"]))
    meta = s["meta"]
    ok(len(meta) >= 10 and all(k in ATLAS for k in meta), f"{nom} : {len(meta)} sprites redessinés, tous connus de l'atlas")
    memes = all(v["o"] == ATLAS[k]["o"] and [f[2:] for f in v["f"]] == [f[2:] for f in ATLAS[k]["f"]] for k, v in meta.items())
    dedans = all(f[1] >= SAISON_Y and f[0] + f[2] <= a.width and f[1] - SAISON_Y + f[3] <= a.height for v in meta.values() for f in v["f"])
    ok(memes and dedans, f"{nom} : mêmes cadres et mêmes origines qu'au printemps, rangés dans son image (y décalés de SAISON_Y)")
    formes = teintes = 0
    for k, v in meta.items():
        change = False                  # (un sprite change dès qu'une de ses images change : la marguerite et le
        for f, g in zip(v["f"], ATLAS[k]["f"]):      # bouton d'or de sol/fleur sont les mêmes en été)
            e = a.crop((f[0], f[1] - SAISON_Y, f[0] + f[2], f[1] - SAISON_Y + f[3]))
            p = atlas.crop((g[0], g[1], g[0] + g[2], g[1] + g[3]))
            formes += alpha(e, p) > 0
            change = change or couleur(e, p) > 0.01
        teintes += change
    ok(formes == 0 and teintes == len(meta), f"{nom} : chaque sprite a la forme de celui du printemps, et d'autres couleurs ({teintes} / {len(meta)})")
    if not s["hd"]:
        print(f"ok : {nom} : pas d'images x4 (jeu construit avec --sans-hd)")
        continue
    t4 = Image.open(fichier(s["hd"]["tiles"]))
    e = alpha(t4.resize(t.size, Image.BOX), t)
    ok(t4.size == (2 * t.width, 2 * t.height) and e < 0.004, f"{nom} : tileset x4 réduit de moitié = tileset x2 ({e * 100:.2f} %)")
    pages = [Image.open(fichier(n)) for n in s["hd"]["atlas"]]
    grand = Image.new("RGBA", (2 * a.width, 2 * a.height))
    y = 0
    for p in pages:
        grand.paste(p, (0, y))
        y += p.height
    e = alpha(grand.resize(a.size, Image.BOX), a)
    ok(y == 2 * a.height and all(p.width == 2 * a.width and p.height <= 4096 for p in pages) and e < 0.004,
       f"{nom} : {len(pages)} page(s) de sprites x4, réduites de moitié = l'image x2 ({e * 100:.2f} %)")
sys.exit(1 if echecs else 0)
