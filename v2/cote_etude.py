"""python3 v2/cote_etude.py sortie.png

Étude des terrains de la côte (sable, planches, jetée, mer, falaise de craie) : un bout de plage dessiné par le moteur
de tuiles (tiles.py), aux couleurs de l'été (saisons.py), avec le papa, Alice et Tecky pour l'échelle. Les terrains
sont dans tiles.py depuis que Christophe a choisi leurs teintes (reference/v2/cote_terrains_options.png)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import Image, ImageDraw, ImageFont                  # noqa: E402
import alice2, npcs, saisons, tecky2, tiles                  # noqa: E402
from spritelib import render_svg, PAD                        # noqa: E402

S, T = 2, tiles.T
MW, MH = 26, 15


def tuile(c, tx, ty):
    """La tuile de coins c à la place (tx, ty), comme pack_web.build_map() la demande au tileset."""
    if set(c) == {"grass"}:
        return tiles.grass_tile(S, 1 if (tx * 5 + ty * 3) % 4 == 0 else 0)
    return tiles.composite(tuple(c) + (tiles.phase(c, tx, ty) or ()), S, seed=tiles.composite_seed(c), variante=(tx * 3 + ty * 5) % 3)


def terrain(x, y):
    yb = 3.4 + round(1.6 * (1 - ((x - 11) / 12) ** 2))      # le haut des planches : le croissant
    ys = yb + 6.6 + (0.6 if 3 <= x <= 6 else 0)             # le bord de l'eau
    if x >= 19:                                              # la falaise, à l'est : un plateau, sa paroi, un escalier
        if 21 <= x <= 22 and 4 <= y <= 6:
            return "stairs"
        if y <= 4:
            return "heath"
        if y <= 6:
            return "chalk"
    if x <= 9 and y <= 1:
        return "paving"                                      # un bout de ville
    if 14 <= x <= 15 and yb + 1 <= y <= 13:
        return "planks"                                      # la jetée
    if y < yb:
        return "grass"
    if y < yb + 1.9:
        return "planks" if x <= 16 else "grass"              # (les planches s'arrêtent avant la falaise : jamais de jonction)
    return "sand" if y < ys else "sea"


def scene(titre):
    g = [[terrain(x, y) for x in range(MW + 1)] for y in range(MH + 1)]
    img = Image.new("RGBA", (MW * T * S, MH * T * S))
    for ty in range(MH):
        for tx in range(MW):
            img.paste(tuile((g[ty][tx], g[ty][tx + 1], g[ty + 1][tx], g[ty + 1][tx + 1]), tx, ty), (tx * T * S, ty * T * S))

    def pose(im, x, y, ox, oy):
        img.alpha_composite(im, (round((x - ox - PAD) * S), round((y - oy - PAD) * S)))
    d = npcs._papa(npcs.P(wave=1, wave_a=-10, happy=True))
    d.under = []
    pose(render_svg(d.svg(), 48, 64, S, PAD), 9.0 * T, 8.9 * T, 24, 60)
    w, h, ox, oy = alice2.CADRE
    pose(render_svg(alice2.frames("idle", "down")[0], w, h, S, PAD), 10.2 * T, 9.0 * T, ox, oy)
    w, h, ox, oy = tecky2.CADRE["right"]
    pose(render_svg(tecky2.frames("idle", "right")[0], w, h, S, PAD), 11.4 * T, 9.1 * T, ox, oy)
    dr = ImageDraw.Draw(img, "RGBA")
    font = ImageFont.truetype("/usr/share/fonts/google-noto/NotoSans-Bold.ttf", 30)
    dr.rectangle((0, 0, img.width, 50), fill=(40, 30, 20, 215))
    dr.text((16, 4), titre, fill=(255, 255, 255, 255), font=font)
    return img.convert("RGB")


if __name__ == "__main__":
    saisons.appliquer("ete")
    try:
        im = scene("La côte  —  sable doré, planches brunes, mer turquoise, falaise")
    finally:
        saisons.appliquer()
    im.save(sys.argv[1] if len(sys.argv) > 1 else os.path.join("reference", "v2", "cote_terrains.png"))
    print(im.size)
