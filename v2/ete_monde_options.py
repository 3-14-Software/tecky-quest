"""Planche de propositions : l'été plus marqué sur la carte du monde (14 novembre 2026).

    python3 v2/ete_monde_options.py      # -> reference/v2/ete_monde_options.png (quatre minutes)

Le même coin du monde (le verger, le champ, la rivière, la forêt) au printemps, dans l'été d'aujourd'hui et dans
deux palettes plus franches. Dessiné par pack_web.preview() : sans l'habillage que le jeu sème dans le sol."""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pack_web
import saisons
import tiles
from ete_options import police, REF

PISTES = {
    "A — plein été : herbe vert-jaune chaude, feuillages profonds, chemins clairs": dict(
        feuillages={"chene": ("#1F6E33", "#33903A", "#6DBB45", "#17431F"), "sombre": ("#1B5C33", "#2A7638", "#4A9440", "#12381F"),
                    "bouleau": ("#5F9A34", "#84B840", "#B4D65C", "#335A22"), "jeune": ("#1F7448", "#35905C", "#69B880", "#164432"),
                    "buisson": ("#2A7636", "#44983C", "#7AC04A", "#1A4520"), "cerisier": ("#267A3C", "#42A04C", "#7CCB5E", "#184A26"),
                    "sapin": ("#1A5C3C", "#297A4A", "#4F9E5E", "#123A26"), "fond": ("#144E32", "#1E6540", "#37834F", "#0E301E")},
        herbe=dict(fill="#B4CE5C", blade="#8FAE40", flower=("#FFFFFF", "#E8483A", "#5B8FE0")),
        terrains={"field": dict(fill="#E2BC50", edge="#C9A03C", out="#8E6E26"), "forest": dict(fill="#4E8C40", edge="#447E38", out="#35682C"),
                  "dirt": dict(fill="#E6CB92", edge="#CFB178", out="#96784A")}),
    "B — été brûlé : herbe paille, feuillages olive, terre pâle, coquelicots": dict(
        feuillages={"chene": ("#3C7A2C", "#5C9A34", "#98C24A", "#26481C"), "sombre": ("#2E6630", "#467F36", "#6E9E44", "#1C3E20"),
                    "bouleau": ("#7C9E34", "#A2BC44", "#CCD866", "#485C22"), "jeune": ("#3C7C44", "#58985A", "#8CBE7A", "#244A2C"),
                    "buisson": ("#4A7E30", "#6A9E3A", "#A0C450", "#2C4A1E"), "cerisier": ("#3E8038", "#5EA246", "#98CA5C", "#264C22"),
                    "sapin": ("#1F6040", "#2F7C4C", "#58A060", "#163C28"), "fond": ("#1E5434", "#2C6A40", "#4A8650", "#143420")},
        herbe=dict(fill="#D6D07A", blade="#B4A850", flower=("#FFFFFF", "#E8483A", "#5B8FE0")),
        terrains={"field": dict(fill="#E8C458", edge="#CDA642", out="#927028"), "forest": dict(fill="#74984A", edge="#688A42", out="#527034"),
                  "dirt": dict(fill="#EEDCAE", edge="#D6C08C", out="#9C845A")}),
}


def vue(nom, region):
    saisons.appliquer(nom)
    pack_web.COMPOSITES.clear()
    pack_web.charger_carte()
    m = pack_web.build_map()
    atlas, meta = pack_web.pack(pack_web.collect())
    pack_web.preview(m, atlas, meta, tiles.tileset(pack_web.S, composites=pack_web.COMPOSITES))
    x0, y0, x1, y1 = region
    k, o = 32, m["edge"]["r"] * 32
    return Image.open(os.path.join(pack_web.WEB, "map_preview.png")).convert("RGB").crop((x0 * k + o, y0 * k + o, x1 * k + o, y1 * k + o))


def planche(region=(60, 22, 94, 41)):
    apercu = os.path.join(pack_web.WEB, "map_preview.png")
    garde = open(apercu, "rb").read() if os.path.exists(apercu) else None
    noms = ["Printemps", "Été d'aujourd'hui"] + list(PISTES)
    for i, (t, p) in enumerate(PISTES.items()):
        saisons.SAISONS[f"piste{i}"] = p
    vues = []
    try:
        for nom in ("printemps", "ete", "piste0", "piste1"):
            vues.append(vue(nom, region))
            print(nom, flush=True)
    finally:
        saisons.appliquer()
        if garde:
            open(apercu, "wb").write(garde)
    w, h = vues[0].size
    out = Image.new("RGB", (2 * w + 36, 70 + 2 * (h + 60) + 12), (58, 30, 18))
    d = ImageDraw.Draw(out)
    d.text((24, 14), "Le monde en été : jusqu'où marquer la saison ? (palette seule ; le jeu sème en plus fleurs et cultures)", font=police(32), fill="#FFFFFF")
    for i, im in enumerate(vues):
        x, y = 12 + (i % 2) * (w + 12), 70 + (i // 2) * (h + 60)
        d.text((x + 4, y + 8), noms[i], font=police(28), fill=(242, 193, 78))
        out.paste(im, (x, y + 52))
    fn = os.path.join(REF, "ete_monde_options.png")
    out.save(fn)
    print(fn, out.size)


if __name__ == "__main__":
    planche()
