#!/usr/bin/env python3
"""
Prépare la version web de Tecky Quest :
  web/atlas.png  + données de l'atlas (sprites x2, découpés au plus juste)
  web/tiles.png  tileset x2
  web/index.html page du jeu (web_src/index.template.html + game.js + données)
  web/map_preview.png  aperçu du niveau (contrôle)

    python3 pack_web.py
"""
import json
import os
import random

from PIL import Image

import alice
import decor
import enemies
import hud
import items
import tecky
import music
import tiles
from spritelib import render_svg, flash, PAD

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web")
SRC = os.path.join(ROOT, "web_src")
S = 2
TS = 32 * S

# ====================================================================== NIVEAU
MW, MH = 40, 24


def corner_grid():
    g = [["grass"] * (MW + 1) for _ in range(MH + 1)]

    def paint(t, x0, y0, x1, y1):
        for y in range(max(0, y0), min(MH, y1) + 1):
            for x in range(max(0, x0), min(MW, x1) + 1):
                g[y][x] = t

    # campagne nord-ouest
    paint("dirt", 3, 4, 4, 10)          # chemin depuis la niche
    paint("dirt", 4, 7, 14, 8)          # vers l'est
    paint("water", 8, 1, 11, 4)         # étang
    # ruisseau qui sépare la campagne du village (on passe par la route)
    paint("water", 17, 0, 18, 9)
    paint("water", 16, 2, 19, 5)
    # route principale
    paint("road", 0, 12, MW, 15)
    # village
    paint("sidewalk", 20, 11, MW, 11)
    paint("paving", 23, 3, 38, 10)
    # campagne sud-ouest
    paint("dirt", 6, 17, 7, MH)
    paint("dirt", 7, 20, 14, 21)
    paint("water", 1, 18, 4, 22)
    # zone industrielle
    paint("sidewalk", 22, 16, MW, 16)
    paint("concrete", 22, 17, MW, MH)
    paint("road", 30, 16, 31, 17)
    return g


DECOR = [
    # campagne nord-ouest
    ("doghouse", 3.5, 3.2),
    ("tree", 1, 1.4), ("tree", 6.5, 1.2), ("tree", 13.5, 1.6), ("tree", 1.2, 7), ("tree", 14.8, 5.2),
    ("tree", 7.2, 10.8), ("tree", 12.8, 4.3),
    ("bush", 5.8, 3.4), ("bush", 12.2, 1.1), ("bush", 0.8, 10.6), ("bush", 15.5, 9.6),
    ("rock", 7.6, 5.3), ("rock", 15.4, 3),
    ("hay", 10.5, 9.8), ("hay", 11.7, 10.2), ("hay", 13, 9.6),
    ("signpost", 5.6, 11.1),
    # berges du ruisseau
    ("tree", 20.5, 1.5), ("bush", 20.2, 7.4),
    # route
    ("road_sign", 2.5, 11.35), ("road_sign", 21.2, 16.1), ("cone", 16.6, 14.7), ("cone", 17.5, 14.7),
    # village
    ("house_red", 25.5, 3.4), ("house_blue", 30.5, 3.4), ("house_red", 35.5, 3.4),
    ("tree", 23.3, 9.4), ("tree", 38.6, 9.4), ("tree", 39, 2.4),
    ("bench", 28, 8.4), ("bench", 33, 8.4), ("flower_pot", 30.5, 6.4), ("flower_pot", 25.3, 6.2),
    ("lamppost", 24.5, 11.35), ("lamppost", 30.5, 11.35), ("lamppost", 36.5, 11.35),
    ("mailbox", 27.2, 11.35), ("hedge", 20, 9.8), ("hedge", 21, 9.8), ("hedge", 20, 4), ("hedge", 21, 4),
    # zone industrielle
    ("warehouse", 26, 22), ("warehouse", 35.5, 22.2), ("container", 25.5, 18.9), ("container", 38.3, 23.9),
    ("barrel_blue", 29.2, 19.6), ("barrel_red", 29.9, 19.8), ("barrel_blue", 33.4, 19),
    ("crate", 22.9, 22.6), ("crate", 23.6, 23.4), ("pallet", 31.2, 22.9), ("pallet", 39.3, 19.6),
    ("cone", 29.8, 17.9),
    # campagne sud-ouest
    ("tree", 0.9, 16.8), ("tree", 9.8, 17.3), ("tree", 15.8, 17.8), ("tree", 3, 23.8), ("tree", 12.2, 23.6),
    ("tree", 18.8, 22.4), ("bush", 5.2, 16.6), ("bush", 17.3, 19.8), ("bush", 9.2, 23.4),
    ("hay", 12.2, 18.7), ("hay", 13.4, 19), ("rock", 19.6, 17.6),
    ("signpost", 7.3, 16.6),
]
for x in range(9, 16):
    DECOR.append(("fence_wood_h", x, 11.25))
for x in list(range(22, 30)) + list(range(32, 40)):
    DECOR.append(("fence_metal_h", x, 17.3))
for x in range(8, 16):
    DECOR.append(("fence_wood_h", x, 16.35))

ITEMS = [
    ("bone", 6, 7.5), ("bone", 12, 17.6), ("bone", 28.5, 7.2), ("bone", 23.5, 19.8), ("bone", 19.5, 11.3),
    ("sausage", 14.5, 22.5), ("sausage", 37.5, 19.2),
    ("medal", 1.4, 9.4), ("medal", 38.6, 18.3),
    ("squeaky", 9.5, 6.2), ("squeaky", 2.5, 16.9), ("squeaky", 33, 5.2),
    ("ball", 6.3, 5.4), ("ball", 15, 6.3), ("ball", 19.5, 20), ("ball", 25, 13.8), ("ball", 36.8, 9.4),
]
ENEMIES = [
    ("roquet", 9, 6.4), ("roquet", 14, 3.5), ("roquet", 10.5, 19.2), ("roquet", 27, 6.5),
    ("bouledogue", 20, 13.6), ("bouledogue", 15.5, 22.2),
    ("molosse", 33.5, 20.2),
]
# trésors enterrés : au centre de la tuile des traces de pattes (scintillement et trou creusé s'y alignent)
DIG = [(12.5, 6.5), (5.5, 19.5), (21.5, 18.5)]
START = (4.5, 4.2)
ALICE = (33.5, 7.3)
SIGNS = [
    (5.6, 11.1, "Niche de Tecky : en haut. Village : suivre la route vers l'est."),
    (7.3, 16.6, "Les champs du Père Gaston. Attention, chiens pas commodes !"),
]
FULL_VARIANTS = {"dirt": [9, 10], "road": [11, 12], "paving": [13], "concrete": [14, 15]}
OV = {n: i for i, (n, _) in enumerate(tiles.OVERLAYS)}


def build_map():
    g = corner_grid()
    rnd = random.Random(7)
    ground = []
    for ty in range(MH):
        for tx in range(MW):
            cs = [g[ty][tx], g[ty][tx + 1], g[ty + 1][tx], g[ty + 1][tx + 1]]
            up, lo, bits = tiles.resolve(cs)
            if up == "grass":
                idx = rnd.choice([1, 1, 1, 1, 2, 2, 3, 4])
            else:
                idx = tiles.tile_index(up, bits, "grass" if bits == 15 else lo)
                if bits == 15 and up in FULL_VARIANTS and rnd.random() < 0.35:
                    idx = rnd.choice(FULL_VARIANTS[up])
            ground.append(idx)
    # marquages de la route
    for tx in range(MW):
        ground[13 * MW + tx] = 5 if tx % 2 == 0 else tiles.tile_index("road", 15)
    for tx in (10, 11, 34, 35):
        for ty in (12, 13, 14):
            ground[ty * MW + tx] = 7
    # détails
    over = [0] * (MW * MH)
    ovrow = tiles.OVERLAY_ROW * tiles.COLS

    def put(name, tx, ty):
        over[ty * MW + tx] = ovrow + OV[name]
    for tx, ty in ((6, 13), (22, 14), (38, 12)):
        put("plaque d'égout", tx, ty)
    put("grille d'évacuation", 26, 11)
    put("fissures", 33, 11)
    put("flaque", 3, 9)
    put("feuilles mortes", 1, 2)
    put("feuilles mortes", 13, 2)
    put("fleurs", 7, 4)
    put("fleurs", 15, 8)
    put("fleurs", 3, 14 + 3)
    put("touffe d'herbe", 9, 10)
    put("touffe d'herbe", 18, 18)
    put("cailloux", 20, 10)
    put("tache d'huile", 34, 18)
    put("tache d'huile", 27, 23)
    put("bande de danger", 30, 18)
    put("bande de danger", 31, 18)
    put("ligne de parking", 36, 19)
    put("ligne de parking", 37, 19)
    put("feuilles mortes", 23, 8)
    for x, y in DIG:
        over[int(y) * MW + int(x)] = ovrow + OV["traces de pattes"]
    water = [1 if g[y][x] == "water" else 0 for y in range(MH + 1) for x in range(MW + 1)]
    px = lambda v: round(v * TS, 1)
    return {
        "w": MW, "h": MH, "ts": TS, "ground": ground, "over": over, "water": water,
        "hole": ovrow + OV["trou creusé (trésor)"],
        "decor": [[n, px(x), px(y)] for n, x, y in DECOR],
        "items": [[n, px(x), px(y)] for n, x, y in ITEMS],
        "enemies": [[n, px(x), px(y)] for n, x, y in ENEMIES],
        "dig": [[px(x), px(y)] for x, y in DIG],
        "start": [px(START[0]), px(START[1])],
        "alice": [px(ALICE[0]), px(ALICE[1])],
        "signs": [[px(x), px(y), t] for x, y, t in SIGNS],
    }


# ====================================================================== ATLAS
def collect():
    """(clé, liste d'images, origine, découpe ?)"""
    out = []
    dirs = ("down", "up", "right")
    M = PAD * S                      # décalage d'origine dû à la marge
    CH_O = (48 + M, 88 + M)
    char_anims = ("idle", "walk", "bark", "bite", "hurt", "dig")

    def char(kind, fn):
        for a in char_anims:
            if a == "dig" and kind != "tecky":
                continue
            for v in dirs:
                ims = [render_svg(s, 48, 48, S, PAD) for s in fn(a, v)]
                if a == "hurt":
                    ims[0] = flash(ims[0])
                out.append((f"{kind}/{a}/{v}", ims, CH_O, True))
        out.append((f"{kind}/ko/right", [render_svg(s, 48, 48, S, PAD) for s in fn("ko", "right")], CH_O, True))

    char("tecky", tecky.frames)
    for dog in enemies.DOGS:
        char(dog, lambda a, v, dog=dog: enemies.frames(dog, a, v))
    for a in alice.ANIMS:
        for v in dirs:
            out.append((f"alice/{a}/{v}", [render_svg(s, 48, 48, S, PAD) for s in alice.frames(a, v)], CH_O, True))
    for n in items.ITEMS:
        out.append((f"item/{n}", [render_svg(s, 32, 32, S, PAD) for s in items.item_frames(n)], (32 + M, 32 + M), True))
    for n, (fn, size, _) in items.EFFECTS.items():
        o = (12 + M, 48 + M) if n == "bark" else (size + M, size + M)
        out.append((f"fx/{n}", [render_svg(s, size, size, S, PAD) for s in fn()], o, True))
    for n, (fn, (w, h), (ox, oy)) in decor.DECOR.items():
        out.append((f"decor/{n}", [render_svg(fn().svg(), w, h, S, PAD)], (ox * S + M, oy * S + M), True))
    for n, ims in hud.all_sprites(S).items():
        key = "hud/" + n.replace("spr_hud_", "").replace("spr_", "")
        o = (40, 40) if n == "spr_hud_alice_arrow" else (0, 0)
        if n == "spr_title_logo":
            o = (ims[0].width // 2, ims[0].height // 2)
        out.append((key, ims, o, n in ("spr_hud_digits",)))
    return out


def pack(entries, width=2048, pad=2):
    frames = []
    for key, ims, o, trim in entries:
        for i, im in enumerate(ims):
            bb = im.getbbox() if trim else (0, 0, im.width, im.height)
            if bb is None:
                bb = (0, 0, 1, 1)
            frames.append((key, i, im.crop(bb), bb[0], bb[1]))
    order = sorted(range(len(frames)), key=lambda k: -frames[k][2].height)
    pos = {}
    x = y = shelf = 0
    for k in order:
        im = frames[k][2]
        if x + im.width > width:
            x, y, shelf = 0, y + shelf + pad, 0
        pos[k] = (x, y)
        x += im.width + pad
        shelf = max(shelf, im.height)
    H = y + shelf
    atlas = Image.new("RGBA", (width, H), (0, 0, 0, 0))
    meta = {}
    for key, ims, o, trim in entries:
        meta[key] = {"o": list(o), "f": [None] * len(ims)}
    for k, (key, i, im, dx, dy) in enumerate(frames):
        px_, py_ = pos[k]
        atlas.paste(im, (px_, py_))
        meta[key]["f"][i] = [px_, py_, im.width, im.height, dx, dy]
    return atlas, meta


def preview(m, atlas, meta, tileset):
    img = Image.new("RGBA", (MW * TS, MH * TS))
    for i, idx in enumerate(m["ground"]):
        tile = tileset.crop(((idx % 16) * TS, (idx // 16) * TS, (idx % 16 + 1) * TS, (idx // 16 + 1) * TS))
        img.paste(tile, ((i % MW) * TS, (i // MW) * TS))
        o = m["over"][i]
        if o:
            ov = tileset.crop(((o % 16) * TS, (o // 16) * TS, (o % 16 + 1) * TS, (o // 16 + 1) * TS))
            img.alpha_composite(ov, ((i % MW) * TS, (i // MW) * TS))
    things = [("decor/" + n, x, y) for n, x, y in m["decor"]]
    things += [("item/" + n, x, y) for n, x, y in m["items"]]
    things += [(f"{n}/idle/down", x, y) for n, x, y in m["enemies"]]
    things += [("tecky/idle/down", *m["start"]), ("alice/idle/down", *m["alice"])]
    for key, x, y in sorted(things, key=lambda t: t[2]):
        e = meta[key]
        sx, sy, sw, sh, dx, dy = e["f"][0]
        img.alpha_composite(atlas.crop((sx, sy, sx + sw, sy + sh)), (int(x - e["o"][0] + dx), int(y - e["o"][1] + dy)))
    img.convert("RGB").resize((img.width // 2, img.height // 2), Image.LANCZOS).save(os.path.join(WEB, "map_preview.png"))


def main():
    os.makedirs(WEB, exist_ok=True)
    m = build_map()
    atlas, meta = pack(collect())
    atlas.save(os.path.join(WEB, "atlas.png"), optimize=True)
    tileset = tiles.tileset(S)
    tileset.save(os.path.join(WEB, "tiles.png"), optimize=True)
    preview(m, atlas, meta, tileset)
    tpl = open(os.path.join(SRC, "index.template.html"), encoding="utf-8").read()
    game = open(os.path.join(SRC, "game.js"), encoding="utf-8").read()
    import base64
    b64 = lambda p: "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
    data = ("const ATLAS_SRC = \"" + b64(os.path.join(WEB, "atlas.png")) + "\";\n"
            "const TILES_SRC = \"" + b64(os.path.join(WEB, "tiles.png")) + "\";\n"
            "const ATLAS = " + json.dumps(meta, separators=(",", ":")) + ";\n"
            "const SONG = " + json.dumps(dict(zip(("total", "ev"), music.events()), bpm=music.BPM), separators=(",", ":")) + ";\n"
            "const WINSONG = " + json.dumps(dict(zip(("total", "ev"), music.fanfare_events()), bpm=music.FANFARE_BPM), separators=(",", ":")) + ";\n"
            "const MAP = " + json.dumps(m, separators=(",", ":"), ensure_ascii=False) + ";\n")
    html = tpl.replace("/*__DATA__*/", data).replace("/*__GAME__*/", game)
    open(os.path.join(WEB, "index.html"), "w", encoding="utf-8").write(html)
    print("atlas", atlas.size, "| html", len(html) // 1024, "Ko")
    build_standalone(data, game)
    check_placement()


def check_placement():
    """Vérifie (avec Node.js, s'il est installé) que rien n'est dans l'eau ou dans un obstacle."""
    import shutil
    import subprocess
    if not shutil.which("node"):
        print("(Node.js absent : vérification des placements ignorée)")
        return
    r = subprocess.run(["node", os.path.join(SRC, "check_placement.js"), os.path.join(WEB, "index.html")],
                       capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    if r.returncode:
        raise SystemExit("Corrige les placements signalés dans pack_web.py (listes ITEMS, DIG, ENEMIES…)")


def build_standalone(data, game):
    """Version autonome à servir soi-même : plein écran, installable comme une app."""
    import base64
    import shutil
    out = os.path.join(WEB, "tecky_quest_web")
    os.makedirs(out, exist_ok=True)
    font = "data:font/ttf;base64," + base64.b64encode(
        open(os.path.join(ROOT, "fonts", "Fredoka.ttf"), "rb").read()).decode()
    tpl = open(os.path.join(SRC, "standalone.template.html"), encoding="utf-8").read()
    html = tpl.replace("/*__FONT__*/", font).replace("/*__DATA__*/", data).replace("/*__GAME__*/", game)
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
    # icônes : portrait de Tecky sur fond crème (zone sûre pour les icônes "maskable")
    face = hud.tecky_portrait(8)[0]
    for size in (180, 192, 512):
        ic = Image.new("RGBA", (size, size), (242, 193, 78, 255))
        f = face.resize((int(size * 0.74), int(size * 0.74)), Image.LANCZOS)
        ic.alpha_composite(f, ((size - f.width) // 2, (size - f.height) // 2))
        ic.convert("RGB").save(os.path.join(out, f"icon-{size}.png"))
    manifest = {
        "name": "Tecky Quest", "short_name": "Tecky Quest", "lang": "fr",
        "description": "Aide Tecky le teckel à retrouver Alice.",
        "start_url": "./", "scope": "./", "display": "fullscreen", "display_override": ["fullscreen", "standalone"],
        "orientation": "landscape", "background_color": "#16100C", "theme_color": "#16100C",
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
                  {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}],
    }
    json.dump(manifest, open(os.path.join(out, "manifest.webmanifest"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for fn in ("sw.js", "serve.sh"):
        shutil.copy(os.path.join(SRC, fn), os.path.join(out, fn))
    os.chmod(os.path.join(out, "serve.sh"), 0o755)
    shutil.copy(os.path.join(SRC, "LISEZMOI.txt"), os.path.join(out, "LISEZMOI.txt"))
    print("version autonome ->", out)


if __name__ == "__main__":
    main()
