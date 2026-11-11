"""Images x4 (web/atlas_x4_N.png, web/tiles_x4.png) : mêmes dessins aux mêmes places que l'atlas et le tileset x2.
Réduites de moitié, elles doivent redonner les images x2 (à l'anticrénelage près) ; sinon le jeu lirait de travers."""
import json
import os
import sys

import numpy as np
from PIL import Image

WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web")
echecs = 0


def ok(cond, msg):
    global echecs
    print(("ok : " if cond else "ÉCHEC : ") + msg)
    echecs += not cond


def ecart(grand, petit):
    """Part des pixels dont l'opacité diffère nettement entre l'image x4 réduite et l'image x2."""
    a = np.asarray(grand.resize(petit.size, Image.BOX).convert("RGBA"), dtype=np.int16)
    b = np.asarray(petit.convert("RGBA"), dtype=np.int16)
    return float((np.abs(a[..., 3] - b[..., 3]) > 96).mean())


if not os.path.exists(os.path.join(WEB, "hd.json")):
    print("ok : pas d'images x4 (jeu construit avec --sans-hd)")
    sys.exit(0)
noms = json.load(open(os.path.join(WEB, "hd.json"), encoding="utf-8"))["files"]
atlas, tuiles = Image.open(os.path.join(WEB, "atlas.png")), Image.open(os.path.join(WEB, "tiles.png"))
pages = [Image.open(os.path.join(WEB, n)) for n in noms[:-1]]
ok(all(p.width == 2 * atlas.width and p.height <= 4096 for p in pages) and sum(p.height for p in pages) == 2 * atlas.height,
   f"{len(pages)} pages d'atlas x4 de 4096 px au plus, deux fois la taille de l'atlas x2 ({atlas.width} x {atlas.height})")
grand = Image.new("RGBA", (2 * atlas.width, 2 * atlas.height))
y = 0
for p in pages:
    grand.paste(p, (0, y))
    y += p.height
e = ecart(grand, atlas)
ok(e < 0.004, f"atlas x4 réduit de moitié = atlas x2 ({e * 100:.2f} % de pixels qui diffèrent)")
t4 = Image.open(os.path.join(WEB, noms[-1]))
ok(t4.size == (2 * tuiles.width, 2 * tuiles.height), f"tileset x4 : {t4.width} x {t4.height}, deux fois le tileset x2")
e = ecart(t4, tuiles)
ok(e < 0.004, f"tileset x4 réduit de moitié = tileset x2 ({e * 100:.2f} % de pixels qui diffèrent)")
sys.exit(1 if echecs else 0)
