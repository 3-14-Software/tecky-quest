"""
Carte d'exemple 24x14 tuiles : campagne, route, village, zone industrielle.
Sert à vérifier que tout s'assemble ; dans GameMaker, la même carte se construit
dans la room (calque de tuiles + instances).

    python3 sample_map.py   -> out/sample_map.png
"""
import os

import alice
import decor
import enemies
import items
import tecky
import tiles
from spritelib import render_svg

MW, MH = 24, 14
SCALE = 2
TS = 32 * SCALE


def corner_grid():
    g = [["grass"] * (MW + 1) for _ in range(MH + 1)]

    def paint(t, x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                g[y][x] = t

    paint("road", 0, 6, MW, 9)                 # route horizontale (3 tuiles de large)
    paint("dirt", 4, 0, 5, 4)                  # chemin qui descend de la niche vers la route
    paint("dirt", 1, 3, 5, 4)
    paint("dirt", 5, 11, 6, MH)                # chemin de campagne au sud
    paint("water", 8, 11, 11, 13)              # étang
    paint("sidewalk", 10, 5, MW, 5)            # trottoir côté village
    paint("paving", 11, 2, 19, 4)              # place du village
    paint("sidewalk", 15, 10, MW, 10)          # trottoir côté zone industrielle
    paint("concrete", 16, 11, MW, MH)          # zone industrielle
    paint("road", 20, 10, 21, 11)              # accès à l'entrepôt
    return g


def ground():
    from PIL import Image
    g = corner_grid()
    img = Image.new("RGBA", (MW * TS, MH * TS))
    cache = {}
    for ty in range(MH):
        for tx in range(MW):
            cs = [g[ty][tx], g[ty][tx + 1], g[ty + 1][tx], g[ty + 1][tx + 1]]
            up, lo, bits = tiles.resolve(cs)
            if up == "grass":
                v = (tx * 7 + ty * 13) % 11
                key = ("grass", {0: 1, 3: 2, 7: 1, 9: 3}.get(v, 0))
                if key not in cache:
                    cache[key] = tiles.grass_tile(SCALE, key[1])
            else:
                seed = (tx + ty) % 3 if bits == 15 else bits
                key = (up, lo, bits, seed)
                if key not in cache:
                    cache[key] = tiles.transition(up, bits, SCALE, seed=seed, lower=lo)
            img.paste(cache[key], (tx * TS, ty * TS))
    # marquages de la route (ligne médiane + passage piéton)
    dash = tiles.road_marking(SCALE, "dash_h")
    zebra = tiles.road_marking(SCALE, "zebra_h")
    plain = tiles.road_marking(SCALE, None)
    for tx in range(MW):
        img.paste(zebra if tx in (14, 15) else dash if tx % 2 == 0 else plain, (tx * TS, 7 * TS))
    for tx in (14, 15):
        for ty in (6, 8):
            img.paste(zebra, (tx * TS, ty * TS))
    # détails (2e calque de tuiles dans GameMaker)
    names = [n for n, _ in tiles.OVERLAYS]
    for name, tx, ty in (("plaque d'égout", 8, 8), ("plaque d'égout", 19, 6), ("flaque", 4, 1),
                         ("traces de pattes", 4, 2), ("traces de pattes", 4, 4), ("fleurs", 7, 3),
                         ("touffe d'herbe", 1, 9), ("feuilles mortes", 9, 1), ("cailloux", 13, 10),
                         ("fissures", 12, 5), ("grille d'évacuation", 17, 5), ("tache d'huile", 23, 12),
                         ("bande de danger", 20, 11), ("bande de danger", 21, 11), ("trou creusé (trésor)", 2, 13),
                         ("fleurs", 22, 1)):
        img.alpha_composite(tiles.overlay(SCALE, names.index(name)), (tx * TS, ty * TS))
    return img


def main():
    img = ground()
    sprites = []   # (y_pied, image, x_origine, y_origine)

    def put_decor(name, tx, ty):
        fn, (w, h), (ox, oy) = decor.DECOR[name]
        im = render_svg(fn().svg(), w, h, SCALE)
        x, y = tx * TS, ty * TS
        sprites.append((y, im, x - ox * SCALE, y - oy * SCALE))

    def put_svg(svg, w, h, tx, ty, ox, oy):
        im = render_svg(svg, w, h, SCALE)
        x, y = tx * TS, ty * TS
        sprites.append((y, im, x - ox * SCALE, y - oy * SCALE))

    # campagne
    put_decor("doghouse", 5.5, 1.1)
    for tx, ty in ((1, 1.6), (9, 2), (2.3, 5.4), (8.5, 5.3), (1.2, 12.5), (3.2, 13.8), (12, 13.6)):
        put_decor("tree", tx, ty)
    for tx, ty in ((7.3, 1.2), (0.7, 3.3), (13.6, 11.2)):
        put_decor("bush", tx, ty)
    for tx, ty in ((2, 11.2), (3.2, 11), (7.3, 13.6)):
        put_decor("hay", tx, ty)
    for tx in range(0, 5):
        put_decor("fence_wood_h", tx, 10.4)
    put_decor("rock", 7.6, 4.2)
    put_decor("signpost", 6.7, 10.3)
    # route
    put_decor("road_sign", 3.4, 6.05)
    for tx in (18.3, 19.3):
        put_decor("cone", tx, 9.4)
    # village
    put_decor("house_red", 12.5, 2.7)
    put_decor("house_blue", 17.5, 2.7)
    put_decor("lamppost", 16.5, 5.35)
    put_decor("bench", 15, 4.3)
    put_decor("mailbox", 11.2, 5.35)
    put_decor("flower_pot", 20, 4.6)
    for tx in range(21, 24):
        put_decor("hedge", tx, 4.4)
    # zone industrielle
    put_decor("warehouse", 20, 12.4)
    put_decor("container", 17.8, 13.9)
    for tx, name in ((16.6, "barrel_blue"), (17.3, "barrel_red"), (23, "barrel_blue")):
        put_decor(name, tx, 11.8 if tx < 20 else 13.8)
    put_decor("pallet", 22.6, 12.9)
    put_decor("crate", 21.8, 13.8)
    for tx in (16, 17, 18, 19, 22, 23):
        put_decor("fence_metal_h", tx, 11.2)
    put_decor("fence_metal_v", 16, 12.2)

    # personnages et objets
    put_svg(tecky.frames("walk", "down")[1], 48, 48, 5, 3.6, 24, 44)
    put_svg(enemies.frames("roquet", "bark", "right")[2], 48, 48, 9.5, 7.8, 24, 44)
    put_svg(enemies.frames("bouledogue", "idle", "down")[0], 48, 48, 14.2, 12.8, 24, 44)
    put_svg(enemies.frames("molosse", "walk", "right")[2], 48, 48, 15.4, 12.4, 24, 44)
    put_svg(alice.frames("idle", "down")[0], 48, 48, 14, 4.7, 24, 44)
    for name, tx, ty in (("bone", 5.5, 5.5), ("sausage", 12.3, 12.6), ("medal", 23.3, 11.5),
                         ("squeaky", 2.6, 9.9), ("ball", 8.6, 3.4)):
        put_svg(items.item_frames(name)[0], 32, 32, tx, ty, 16, 16)
    put_svg(items.EFFECTS["bark"][0]()[1], 48, 48, 10.4, 7.2, 6, 24)

    for _, im, x, y in sorted(sprites, key=lambda s: s[0]):
        img.alpha_composite(im, (int(x), int(y)))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
    os.makedirs(out, exist_ok=True)
    img.save(os.path.join(out, "sample_map.png"))
    print("OK")


if __name__ == "__main__":
    main()
