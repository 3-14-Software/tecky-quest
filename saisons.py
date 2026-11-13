"""
Les saisons (lot 6 de PLAN_V2.md : un épisode par saison, dans un monde qui change).

Une saison est d'abord une palette : celle des feuillages (nature.FEUILLAGES), de l'herbe (tiles.GRASS) et de
quelques terrains (tiles.TERRAINS : sous-bois, champ, eau, chemins). Tout le reste du décor est dessiné à partir de
ces couleurs : changer la palette redonne les tuiles et les arbres de la saison, sans un dessin de plus.

    python3 saisons.py        # étude : le même coin du monde aux quatre saisons -> reference/v2/saisons_etude.png

appliquer(saison) pose la palette d'une saison dans nature.py et tiles.py (« printemps » : celle d'origine). Ce
n'est pour l'instant qu'une étude : le jeu ne connaît que le printemps. Restent à dessiner, au-delà des couleurs :
la neige sur les toits et les branches nues de l'hiver, les feuilles au sol de l'automne.
"""
import copy
import os
import sys

import nature
import tiles

NOMS = {"printemps": "Printemps (aujourd'hui)", "ete": "Été", "automne": "Automne", "hiver": "Hiver"}
_F0, _G0, _T0 = copy.deepcopy(nature.FEUILLAGES), copy.deepcopy(tiles.GRASS), copy.deepcopy(tiles.TERRAINS)

# par saison : feuillages (ombre, base, clair, contour), herbe (fond, brins, fleurs), terrains (fond, liseré, trait)
SAISONS = {
    "printemps": dict(),
    "ete": dict(
        feuillages={"chene": ("#2F8436", "#4BA63C", "#86CB4C", "#1F5226"), "sombre": ("#256F39", "#388A3E", "#5AA648", "#184326"),
                    "bouleau": ("#6AA63A", "#8FC348", "#BEDD68", "#3A6428"), "jeune": ("#2A8554", "#41A069", "#79C68D", "#1B503B"),
                    "buisson": ("#358A3C", "#55AB43", "#8CCF55", "#205327"), "cerisier": ("#2F8A46", "#4FAE56", "#8FD46A", "#1F5A2E")},
        herbe=dict(fill="#A5CB62", blade="#86AE4A"), terrains={"field": dict(fill="#DDB851", edge="#C59E3E", out="#8E6E26"),
                                                                 # (l'eau de l'été est la mer turquoise de la côte, choisie par Christophe sur reference/v2/cote_terrains_options.png)
                                                                 "water": dict(fill="#2F9CCB", out="#1C6A96"), "forest": dict(fill="#5F9B48", edge="#538C40", out="#427534")}),
    "automne": dict(
        feuillages={"chene": ("#C2611F", "#E48A2A", "#F6BD4C", "#6E3612"), "sombre": ("#96381F", "#BE5128", "#DF7E3A", "#571F10"),
                    "bouleau": ("#D29E1C", "#EEC636", "#FAE584", "#775612"), "jeune": ("#B8502A", "#DA7434", "#F0A458", "#6A2A14"),
                    "buisson": ("#A8782A", "#CC9A38", "#E8C660", "#654616"), "cerisier": ("#9A3048", "#C24C5E", "#E48A8C", "#5A1A2A"),
                    "fond": ("#3C4A2A", "#55602F", "#7E7A3C", "#262E1A")},
        herbe=dict(fill="#AEBE66", blade="#8E9F4E", flower=("#E8922E", "#D9A520", "#C1532A")),
        terrains={"forest": dict(fill="#9C8648", edge="#8B763F", out="#6C5A2E"), "water": dict(fill="#6CA9CC", out="#3A769C"),
                  "field": dict(fill="#9A6A3C", edge="#865A30", out="#5E3E22")}),
    "hiver": dict(
        feuillages={"chene": ("#B4C4D6", "#DAE5EF", "#FFFFFF", "#6C7E94"), "sombre": ("#A9BACD", "#D0DCE8", "#F6FAFD", "#66788E"),
                    "bouleau": ("#BECCDB", "#E2EBF3", "#FFFFFF", "#74869A"), "jeune": ("#B0C2D4", "#D6E2EC", "#FBFDFF", "#6A7C92"),
                    "buisson": ("#B6C6D7", "#DCE6F0", "#FFFFFF", "#6E8096"), "cerisier": ("#B8C7D8", "#DEE7F0", "#FFFFFF", "#708298"),
                    "sapin": ("#1F6B45", "#2F8A55", "#E6EFF6", "#17432C"), "sapin_bleu": ("#1E6660", "#2C857A", "#E6EFF6", "#143F3C"),
                    "fond": ("#5C7088", "#8296AC", "#C6D3E0", "#3E4E62")},
        herbe=dict(fill="#EDF2F7", blade="#C7D4E1", flower=("#FFFFFF", "#DCE6F0", "#FFFFFF")),
        terrains={"forest": dict(fill="#C6D2DE", edge="#B4C2D0", out="#8FA0B2"), "water": dict(fill="#BFE2F1", out="#7DB0CA"),
                  "dirt": dict(fill="#D3C2A6", edge="#BBA98C", out="#8A7A60"), "field": dict(fill="#D9D5CC", edge="#C2BDB2", out="#8E897E")}),
}




def appliquer(saison="printemps"):
    """Pose la palette d'une saison dans nature.FEUILLAGES, tiles.GRASS et tiles.TERRAINS (en place : les modules
    de dessin les lisent au moment de dessiner)."""
    p = SAISONS[saison]
    nature.FEUILLAGES.clear()
    nature.FEUILLAGES.update(copy.deepcopy(_F0))
    nature.FEUILLAGES.update(p.get("feuillages", {}))
    tiles.GRASS.clear()
    tiles.GRASS.update(copy.deepcopy(_G0))
    tiles.GRASS.update(p.get("herbe", {}))
    for k in _T0:
        tiles.TERRAINS[k].clear()
        tiles.TERRAINS[k].update(copy.deepcopy(_T0[k]))
        tiles.TERRAINS[k].update(p.get("terrains", {}).get(k, {}))


def etude(sortie, region=(1, 0, 35, 17)):
    """La région (x0, y0, x1, y1, en tuiles) de la carte du monde aux quatre saisons, dessinée par pack_web."""
    from PIL import Image, ImageDraw, ImageFont
    import pack_web
    font = ImageFont.truetype("/usr/share/fonts/google-noto/NotoSans-Bold.ttf", 30)
    x0, y0, x1, y1 = region
    panneaux = []
    apercu = os.path.join(pack_web.WEB, "map_preview.png")
    garde = open(apercu, "rb").read() if os.path.exists(apercu) else None
    try:
        for saison in SAISONS:
            appliquer(saison)
            pack_web.COMPOSITES.clear()
            pack_web.charger_carte()
            m = pack_web.build_map()
            atlas, meta = pack_web.pack(pack_web.collect())
            pack_web.preview(m, atlas, meta, tiles.tileset(pack_web.S, composites=pack_web.COMPOSITES))
            k, o = 32, m["edge"]["r"] * 32
            im = Image.open(apercu).convert("RGB").crop((x0 * k + o, y0 * k + o, x1 * k + o, y1 * k + o))
            d = ImageDraw.Draw(im, "RGBA")
            d.rectangle((0, 0, im.width, 46), fill=(40, 30, 20, 215))
            d.text((14, 3), NOMS[saison], fill=(255, 255, 255), font=font)
            panneaux.append(im)
            print(NOMS[saison], flush=True)
    finally:
        appliquer()                                  # (toujours revenir au printemps : le jeu se construit avec)
        if garde:
            open(apercu, "wb").write(garde)          # l'aperçu de la carte reste celui du jeu
    w, h = panneaux[0].size
    out = Image.new("RGB", (w * 2 + 12, h * 2 + 12), (40, 30, 20))
    for i, im in enumerate(panneaux):
        out.paste(im, ((i % 2) * (w + 12), (i // 2) * (h + 12)))
    out.save(sortie)
    return out.size


if __name__ == "__main__":
    print(etude(sys.argv[1] if len(sys.argv) > 1 else os.path.join("reference", "v2", "saisons_etude.png")))
