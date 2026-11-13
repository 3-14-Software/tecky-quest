"""python3 v2/falaise_etude.py [sortie.png]

La falaise du jeu, façon RPG Maker XP, dessinée par le moteur de tuiles (tiles.py : BLOC) aux couleurs de l'été : un
plateau de lande au liséré de pierres, sa paroi de roche, un escalier, l'ombre du bloc. La scène est celle de la
maquette que Christophe a validée (reference/v2/falaise_rpg.png, dessinée à la main avant d'entrer dans le moteur) :
les deux images doivent se ressembler."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import Image, ImageDraw, ImageFont                  # noqa: E402
import alice2, saisons, tecky2, tiles                        # noqa: E402
from spritelib import render_svg, PAD                        # noqa: E402

S, T = 2, tiles.T
MW, MH = 26, 14


def coin(x, y):
    if 19 <= x <= 20 and 8 <= y <= 10:
        return "stairs"                                      # l'escalier : deux colonnes de coins, du bord du plateau au pied
    if (x >= 13 and y <= 6) or (17 <= x <= 21 and y <= 8):
        return "heath"                                       # le plateau
    if (17 <= x <= 21 and y <= 10) or (x >= 13 and y <= 8):
        return "chalk"                                       # deux rangées de paroi sous chaque bord du bas
    if (x >= 23 and y >= 9) or y >= 13:
        return "water"
    if y >= 11:
        return "sand"
    return "planks" if x <= 5 and 8 <= y <= 9 else "grass"


def tuile(c, tx, ty):
    """La tuile de coins c à la place (tx, ty), comme pack_web.build_map() la demande au tileset."""
    if set(c) == {"grass"}:
        return tiles.grass_tile(S, 1 if (tx * 5 + ty * 3) % 4 == 0 else 0)
    return tiles.composite(tuple(c) + (tiles.phase(c, tx, ty) or ()), S, seed=tiles.composite_seed(c), variante=(tx * 3 + ty * 5) % 3)


def scene(titre, coin=coin, persos=((9.4, 10.2, "alice"), (15.5, 4.4, "alice"), (10.5, 10.4, "tecky"))):
    g = [[coin(x, y) for x in range(MW + 1)] for y in range(MH + 1)]
    img = Image.new("RGBA", (MW * T * S, MH * T * S))
    for ty in range(MH):
        for tx in range(MW):
            img.paste(tuile((g[ty][tx], g[ty][tx + 1], g[ty + 1][tx], g[ty + 1][tx + 1]), tx, ty), (tx * T * S, ty * T * S))
    for x, y, qui in persos:
        if qui == "alice":
            (w, h, ox, oy), sv = alice2.CADRE, alice2.frames("idle", "down")[0]
        else:
            (w, h, ox, oy), sv = tecky2.CADRE["right"], tecky2.frames("idle", "right")[0]
        img.alpha_composite(render_svg(sv, w, h, S, PAD), (round((x * T - ox - PAD) * S), round((y * T - oy - PAD) * S)))
    dr = ImageDraw.Draw(img, "RGBA")
    dr.rectangle((0, 0, img.width, 46), fill=(40, 30, 20, 215))
    dr.text((14, 3), titre, fill=(255, 255, 255, 255), font=ImageFont.truetype("/usr/share/fonts/google-noto/NotoSans-Bold.ttf", 28))
    return img.convert("RGB")


if __name__ == "__main__":
    saisons.appliquer("ete")
    try:
        im = scene("La falaise dans le moteur  —  plateau de lande, liséré de pierres, paroi de roche, escalier")
    finally:
        saisons.appliquer()
    im.save(sys.argv[1] if len(sys.argv) > 1 else os.path.join("reference", "v2", "falaise.png"))
    print(im.size)
