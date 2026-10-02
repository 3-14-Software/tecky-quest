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
import math
import os
import random

from PIL import Image

import alice
import butterflies
import carte
import cows
import decor
import enemies
import critters
import ducks
import npcs
import port
import herissons
import farmer
import hens
import hud
import items
import lisiere
import tecky
import vehicles
import music
import tiles
import villageois
from spritelib import render_svg, flash, PAD

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web")
SRC = os.path.join(ROOT, "web_src")
S = 2
TS = 32 * S

# ====================================================================== NIVEAU
# La carte est dans carte.json (carte.py ; on la modifie avec l'éditeur de carte : python3 editeur.py), en tuiles.
# 96 x 64 tuiles. Au nord de la grande route : la niche de Tecky, le village, la ferme. Au sud : la campagne, la zone
# industrielle (le dépôt, et son port au bord de la rivière), le verger et les prés de la ferme. Une rivière coupe toute
# la carte (un seul pont, côté ferme) ; au-delà, le parc au sud-ouest, où Alice se cache, et la forêt au sud-est.
# Ici : les listes de la carte (en tuiles), et ce qui s'en déduit (poteaux des panneaux, terriers, clôtures de l'enclos,
# filet de Léon, rails et heurtoirs de la voie, coins du pont, lisière).
CARTE = carte.charger()
MW, MH = CARTE["w"], CARTE["h"]
_T = lambda cle: [tuple(e) for e in CARTE[cle]]
_P = lambda cle: tuple(CARTE[cle])


def corner_grid():
    """Grille des coins [y][x] (MH+1 x MW+1) : le terrain de chaque coin ; une tuile se dessine d'après ses quatre coins."""
    return carte.terrain_grid(CARTE)


ITEMS, ENEMIES, DIG, SIGNS = _T("items"), _T("enemies"), _T("dig"), _T("signs")
HENS, DUCKS, COWS, CRITTERS, BUTTERFLIES, VILLAGERS = (_T(k) for k in ("hens", "ducks", "cows", "critters", "butterflies", "villagers"))
LETTERS, BALLS, TOYS, BABIES = _T("letters"), _T("balls"), _T("toys"), _T("babies")
TUNNELS = [((ax, ay), (bx, by)) for ax, ay, bx, by in CARTE["tunnels"]]
START, ALICE, TITLE = _P("start"), _P("alice"), _P("title")
FARMER, POSTMAN, NEIGHBOR, POMPON = _P("farmer"), _P("postman"), _P("neighbor"), _P("pompon")
LEON, GOAL, IRIS, PIQUETTE = _P("leon"), _P("goal"), _P("iris"), _P("piquette")
PEN, PEN_GATE, TRACK = _P("pen"), _P("penGate"), _P("track")
CALM = _T("calm")
ROAD_TUNNELS = _T("roadTunnels")      # tunnels aux deux bouts de la grande route (lisiere.py) : x, y du pied, miroir
ROAD = CARTE["traffic"]["y"]          # première rangée de la grande route (4 rangées ; marquage sur la 2e)
CROSSINGS = tuple(CARTE["traffic"]["crossings"])          # passages piétons : première des deux tuiles
TRAFFIC = [tuple(v) for v in CARTE["traffic"]["vehicles"]]   # véhicules : voie 0 (en haut, vers l'ouest) ou 1, x de départ
DETAILS = _T("details")
FLOWER_BEDS = [(tx, ty) for n, tx, ty in DETAILS if n == "fleurs"]      # massifs de fleurs : perchoirs des papillons


def derived_decor():
    """Décors qui se déduisent de la carte : poteau de chaque panneau, filet de Léon, heurtoirs et rails de la voie de
    Titine, clôture de l'enclos (barrière ouverte en bas), les deux bouts de chaque terrier."""
    out = [("signpost", x, y) for x, y, _ in SIGNS] + [("goal_net", *GOAL)]
    x0, x1, y = TRACK
    out += [("buffer_stop", x0, y + 0.1), ("buffer_stop", x1, y + 0.1)]
    out += [("rail", x, y) for x in range(math.floor(x0), math.ceil(x1))]
    px0, py0, px1, py1 = PEN
    for x in range(px0, px1):
        out.append(("fence_wood_h", x, py0))
        if not PEN_GATE[0] <= x < PEN_GATE[1]:
            out.append(("fence_wood_h", x, py1))
    ys = [py0 + k for k in range(1, math.ceil(py1 - py0)) if py0 + k < py1] + [py1]
    for y in ys:
        out += [("fence_wood_v", px0, y), ("fence_wood_v", px1, y)]
    out += [("burrow", x, y) for a, b in TUNNELS for x, y in (a, b)]
    return out


DECOR = _T("decor") + derived_decor()
# pont : coins (x0, y0, x1, y1) qui ne sont plus de l'eau, sous le tablier de chaque décor « bridge » (5 tuiles de haut)
BRIDGES = [(round(x) - 1, round(y) - 5, round(x) + 1, round(y)) for n, x, y in DECOR if n == "bridge"]


def edge_keep():
    """Ce que la lisière ne doit jamais cacher : objets, personnages, bêtes, panneaux, terriers…"""
    return ([(x, y) for _, x, y, *_ in ITEMS + ENEMIES + HENS + DUCKS + CRITTERS + BUTTERFLIES + COWS + VILLAGERS]
            + list(DIG)
            + LETTERS + TOYS + BALLS + BABIES + [p for ab in TUNNELS for p in ab] + [(x, y) for x, y, _ in SIGNS]
            + [FARMER, POSTMAN, NEIGHBOR, POMPON, LEON, IRIS, PIQUETTE, START, ALICE])


def edge_decor(g, keep):
    """Lisière (lisiere.py) : fourrés, arbres, sapins et tunnels de la route dans la marge autour de la carte.
    g : grille des coins (corner_grid) ; keep : points (x, y) à ne pas cacher (edge_keep)."""
    forest = lambda x, y: g[min(max(round(y), 0), MH)][min(max(round(x), 0), MW)] == "forest"
    return lisiere.decor(g, MW, MH, keep, forest, ROAD_TUNNELS)


EDGE = edge_decor(corner_grid(), edge_keep())
FULL_VARIANTS = {"dirt": [9, 10], "road": [11, 12], "paving": [13], "concrete": [14, 15]}
OV = {n: i for i, (n, _) in enumerate(tiles.OVERLAYS)}


COMPOSITES = []       # tuiles composées (trois terrains : bout de chemin sur la route…), ajoutées au tileset web


def build_map():
    g = corner_grid()
    rnd = random.Random(7)
    ground = []
    COMPOSITES.clear()

    def pick(cs, rnd):                                # tuile pour ses quatre coins (NO, NE, SO, SE)
        up, lo, bits = tiles.resolve(cs)
        if tiles.needs_composite(cs):
            if tuple(cs) not in COMPOSITES:
                COMPOSITES.append(tuple(cs))
            return tiles.COMPOSITE_BASE + COMPOSITES.index(tuple(cs))
        if up == "grass":
            return rnd.choice([1, 1, 1, 1, 2, 2, 3, 4])
        idx = tiles.tile_index(up, bits, "grass" if bits == 15 else lo)
        if bits == 15 and up in FULL_VARIANTS and rnd.random() < 0.35:
            idx = rnd.choice(FULL_VARIANTS[up])
        return idx
    for ty in range(MH):
        for tx in range(MW):
            ground.append(pick([g[ty][tx], g[ty][tx + 1], g[ty + 1][tx], g[ty + 1][tx + 1]], rnd))
    # marquages de la route (sur sa deuxième rangée)
    for tx in range(MW):
        ground[(ROAD + 1) * MW + tx] = 5 if tx % 2 == 0 else tiles.tile_index("road", 15)
    # sol de la lisière : lisiere.RING tuiles autour de la carte, qui prolongent celles du bord (coins ramenés sur le
    # bord : la route, ses marquages, la rivière et le ruisseau continuent tout droit)
    R, rr, ring = lisiere.RING, random.Random(13), []
    at = lambda x, y: g[min(max(y, 0), MH)][min(max(x, 0), MW)]
    for ty in range(-R, MH + R):
        for tx in range(-R, MW + R):
            if not (0 <= tx < MW and 0 <= ty < MH):
                idx = pick([at(tx, ty), at(tx + 1, ty), at(tx, ty + 1), at(tx + 1, ty + 1)], rr)
                ring.append([tx, ty, (5 if tx % 2 == 0 else tiles.tile_index("road", 15)) if ty == ROAD + 1 else idx])
    for tx in CROSSINGS:                              # passages piétons (dont chemin de la ferme et du pont)
        for ty in (ROAD, ROAD + 1, ROAD + 2):
            ground[ty * MW + tx] = ground[ty * MW + tx + 1] = 7
    # détails
    over = [0] * (MW * MH)
    ovrow = tiles.OVERLAY_ROW * tiles.COLS

    def put(name, tx, ty):
        over[ty * MW + tx] = ovrow + OV[name]
    for n, tx, ty in DETAILS:                         # (dans l'ordre : le dernier posé sur une tuile l'emporte)
        put(n, tx, ty)
    # traces de pattes des trésors (par-dessus)
    for x, y in DIG:
        over[int(y) * MW + int(x)] = ovrow + OV["traces de pattes"]
    for x0, y0, x1, y1 in BRIDGES:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                g[y][x] = "bridge"           # n'est plus de l'eau pour les collisions (le sol a déjà été choisi)
    water = [1 if g[y][x] == "water" else 0 for y in range(MH + 1) for x in range(MW + 1)]
    px = lambda v: round(v * TS, 1)
    return {
        "w": MW, "h": MH, "ts": TS, "ground": ground, "over": over, "water": water,
        "hole": ovrow + OV["trou creusé (trésor)"],
        "decor": [[n, px(x), px(y)] for n, x, y in DECOR],
        # lisière (lisiere.py) : sol de la marge autour de la carte (tx, ty, tuile) et ses décors (nom, x, y, miroir)
        "edge": {"r": R, "ring": ring, "decor": [[n, px(x), px(y), f] for n, x, y, f in EDGE]},
        "items": [[n, px(x), px(y)] for n, x, y in ITEMS],
        "enemies": [[n, px(x), px(y)] for n, x, y in ENEMIES],
        "hens": [[n, px(x), px(y), q] for n, x, y, q in HENS],
        "pen": [px(v) for v in PEN], "penGate": [px(v) for v in PEN_GATE],
        "farmer": [px(FARMER[0]), px(FARMER[1])],
        "calm": [[px(a), px(b), px(c), px(d)] for a, b, c, d in CALM],
        "postman": [px(POSTMAN[0]), px(POSTMAN[1])], "neighbor": [px(NEIGHBOR[0]), px(NEIGHBOR[1])],
        "pompon": [px(POMPON[0]), px(POMPON[1])], "letters": [[px(x), px(y)] for x, y in LETTERS],
        "leon": [px(LEON[0]), px(LEON[1])], "goal": [px(GOAL[0]), px(GOAL[1])], "balls": [[px(x), px(y)] for x, y in BALLS],
        "iris": [px(IRIS[0]), px(IRIS[1])], "toys": [[px(x), px(y)] for x, y in TOYS],
        "track": [px(TRACK[0]), px(TRACK[1]), px(TRACK[2])],
        "piquette": [px(PIQUETTE[0]), px(PIQUETTE[1])], "babies": [[px(x), px(y)] for x, y in BABIES],
        "babyFps": {a: fps for a, (_, fps, _) in herissons.ANIMS.items()},
        "npcFps": dict({"farmer": {a: v[1] for a, v in farmer.ANIMS.items()}},
                       **{k: {a: v[1] for a, v in npcs.ANIMS[k].items()} for k in npcs.KINDS}),
        "critters": [[n, px(x), px(y)] for n, x, y in CRITTERS],
        "rest": {a: [fps, loop] for a, (_, fps, _, loop) in tecky.REST_ANIMS.items()},
        "badges": hud.BADGES,
        "keys": hud.KEYS, "pads": [k for k, _ in hud.PAD_BUTTONS],   # noms des images de hud/key et hud/pad
        "ducks": [[n, px(x), px(y), f] for n, x, y, f in DUCKS],
        "cows": [[n, px(x), px(y)] for n, x, y in COWS],
        "villagers": [[n, px(x), px(y)] for n, x, y in VILLAGERS],
        "villagerFps": {k: {a: v[1] for a, v in villageois.ANIMS[k].items()} for k in villageois.KINDS},
        "cowFps": {k: {a: fps for a, (_, fps, _) in cows.anims(k).items()} for k in cows.KINDS},
        "duckFps": {k: {a: fps for a, (_, fps, _) in ducks.anims(k).items()} for k in ducks.KINDS},
        "duckLoop": {k: {a: loop for a, (_, _, loop) in ducks.anims(k).items()} for k in ducks.KINDS},
        "critterFps": {k: {a: fps for a, (_, fps, _) in critters.anims(k).items()} for k in critters.KINDS},
        "tunnels": [[px(a[0]), px(a[1]), px(b[0]), px(b[1])] for a, b in TUNNELS],
        "butterflies": [[c, px(x), px(y)] for c, x, y in BUTTERFLIES],
        # où les papillons se posent : (x, y au sol, hauteur) — sur les pots de fleurs, ou sur les massifs
        "flowers": [[px(x), px(y) + 2, 44] for n, x, y in DECOR if n == "flower_pot"]
                   + [[px(tx + 0.5), px(ty + 0.5), 4] for tx, ty in FLOWER_BEDS],
        # la grande route : voies 0 et 1, bords de la chaussée (pour les chiens, Tecky, les poules)
        "traffic": {"lanes": [px(ROAD + 0.95), px(ROAD + 2.95)], "road": [px(ROAD - 0.5), px(ROAD + 3.5)],
                    "crossings": [[px(tx), px(tx + 2)] for tx in CROSSINGS],
                    "vehicles": [[n, lane, px(x)] for n, lane, x in TRAFFIC]},
        "dig": [[px(x), px(y)] for x, y in DIG],
        "start": [px(START[0]), px(START[1])],
        "alice": [px(ALICE[0]), px(ALICE[1])],
        "title": [px(TITLE[0]), px(TITLE[1])],
        "decorFps": {n: fps for n, (_, fps) in decor.ANIMATED.items()},
        "signs": [[px(x), px(y), t] for x, y, t in SIGNS],
        "farmRoadY": px(ROAD - 0.7),                  # les poules ne descendent jamais plus bas (la grande route)
        "ballBox": CARTE["ballBox"],                  # en tuiles : là où roulent les ballons de Léon
        # zones (en tuiles) : la première dont un rectangle contient le point ; un bord de rectangle posé sur le bord
        # de la carte n'a pas de limite (game.js : zoneAt) ; music : variation du thème, sinon celle de son id
        "zones": CARTE["zones"], "landmarks": CARTE["landmarks"],
        "ending": {k: [px(v[0]), px(v[1])] for k, v in CARTE["ending"].items()},   # scène de fin : Alice, Tecky
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
    for a, (_, fps, views, loop) in tecky.REST_ANIMS.items():    # poses de repos (assis, bâille, se gratte, dort, s'ébroue)
        for v in views:
            out.append((f"tecky/{a}/{v}", [render_svg(sv, 48, 48, S, PAD) for sv in tecky.rest_frames(a, v)], CH_O, True))
    for dog in enemies.DOGS:
        char(dog, lambda a, v, dog=dog: enemies.frames(dog, a, v))
    for a in alice.ANIMS:
        for v in dirs:
            out.append((f"alice/{a}/{v}", [render_svg(s, 48, 48, S, PAD) for s in alice.frames(a, v)], CH_O, True))
    for a, (_, fps, _) in farmer.ANIMS.items():          # le fermier Gaston, vu de face, pieds en (24, 60)
        out.append((f"farmer/{a}", [render_svg(sv, farmer.W, farmer.H, S, PAD) for sv in farmer.frames(a)], (24 * S + M, 60 * S + M), True))
    for kind in npcs.KINDS:                             # le facteur et la voisine, vus de face, pieds en (24, 60)
        for a in npcs.ANIMS[kind]:
            out.append((f"{kind}/{a}", [render_svg(sv, npcs.W, npcs.H, S, PAD) for sv in npcs.frames(kind, a)], (24 * S + M, 60 * S + M), True))
    for kind in villageois.KINDS:                       # les villageois, vus de face, pieds en (24, 60)
        for a in villageois.ANIMS[kind]:
            out.append((f"{kind}/{a}", [render_svg(sv, npcs.W, npcs.H, S, PAD) for sv in villageois.frames(kind, a)], (24 * S + M, 60 * S + M), True))
    out.append(("item/letter", [render_svg(sv, 32, 32, S, PAD) for sv in npcs.letter_frames()], (32 + M, 32 + M), True))
    out.append(("port/balloon", [render_svg(sv, 32, 32, S, PAD) for sv in port.balloon_frames()], (16 * S + M, 16 * S + M), True))
    out.append(("port/toy", [render_svg(sv, 32, 32, S, PAD) for sv in port.toy_frames()], (16 * S + M, 16 * S + M), True))
    for a in herissons.ANIMS:                           # les bébés hérissons, de profil, pieds en (16, 28)
        out.append((f"hedgehog/{a}", [render_svg(sv, 32, 32, S, PAD) for sv in herissons.frames(a)], (16 * S + M, 28 * S + M), True))
    for kind in critters.KINDS:                         # écureuil, chats : de profil vers la droite, pieds en (16, 28)
        for a in critters.anims(kind):
            out.append((f"{kind}/{a}", [render_svg(sv, 32, 32, S, PAD) for sv in critters.frames(kind, a)], (16 * S + M, 28 * S + M), True))
    for kind in ducks.KINDS:                            # canards : de profil vers la droite, ligne d'eau en (16, 24)
        for a in ducks.anims(kind):
            out.append((f"{kind}/{a}", [render_svg(sv, 32, 32, S, PAD) for sv in ducks.frames(kind, a)], (16 * S + M, 24 * S + M), True))
    for kind in cows.KINDS:                             # vaches : de profil vers la droite, pieds en (32, 44)
        for a in cows.anims(kind):
            out.append((f"{kind}/{a}", [render_svg(sv, 64, 48, S, PAD) for sv in cows.frames(kind, a)], (32 * S + M, 44 * S + M), True))
    for c in butterflies.COLORS:
        out.append((f"butterfly/{c}", [render_svg(sv, 24, 24, S, PAD) for sv in butterflies.frames(c)], (12 * S + M, 12 * S + M), True))
    for n, (_, (w, h), (ox, oy)) in vehicles.VEHICLES.items():
        out.append((f"vehicle/{n}", [render_svg(sv, w, h, S, PAD) for sv in vehicles.frames(n)], (ox * S + M, oy * S + M), True))
    for kind in hens.COLORS:
        for anim in hens.ANIMS:
            out.append((f"{kind}/{anim}/right", [render_svg(s, 32, 32, S, PAD) for s in hens.frames(kind, anim)],
                        (16 * S + M, 28 * S + M), True))
    for n in items.ITEMS:
        out.append((f"item/{n}", [render_svg(s, 32, 32, S, PAD) for s in items.item_frames(n)], (32 + M, 32 + M), True))
    for n, (fn, size, _) in items.EFFECTS.items():
        o = (12 + M, 48 + M) if n == "bark" else (size + M, size + M)
        out.append((f"fx/{n}", [render_svg(s, size, size, S, PAD) for s in fn()], o, True))
    for n, (fn, (w, h), (ox, oy)) in decor.DECOR.items():
        out.append((f"decor/{n}", [render_svg(dr.svg(), w, h, S, PAD) for dr in decor.frames(n)], (ox * S + M, oy * S + M), True))
    for n, (fn, (w, h), (ox, oy)) in lisiere.DECOR.items():        # la lisière, au bord de la carte
        out.append((f"decor/{n}", [render_svg(fn().svg(), w, h, S, PAD)], (ox * S + M, oy * S + M), True))
    for n, ims in hud.all_sprites(S).items():
        key = "hud/" + n.replace("spr_hud_", "").replace("spr_", "")
        o = {"spr_hud_arrow": (40, 40), "spr_hud_arrow_icon": (22, 22)}.get(n, (0, 0))
        if n == "spr_title_logo":
            o = (ims[0].width // 2, ims[0].height // 2)
        # rognées : chiffres ; touches et boutons (largeur exacte de chacun, pour les icônes dans les textes)
        out.append((key, ims, o, n in ("spr_hud_digits", "spr_hud_key", "spr_hud_pad")))
    return out


MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre",
          "décembre"]


def version():
    """Version affichée sur l'écran titre : la date de construction (pour savoir si un téléphone a la dernière)."""
    import datetime
    d = datetime.datetime.now()
    return f"version du {d.day}{'er' if d.day == 1 else ''} {MONTHS[d.month - 1]} {d.year}, {d.hour} h {d.minute:02d}"


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
    e = m["edge"]
    o = e["r"] * TS                       # la marge de la lisière, autour de la carte
    img = Image.new("RGBA", (MW * TS + 2 * o, MH * TS + 2 * o))
    tile = lambda idx: tileset.crop(((idx % 16) * TS, (idx // 16) * TS, (idx % 16 + 1) * TS, (idx // 16 + 1) * TS))
    for i, idx in enumerate(m["ground"]):
        img.paste(tile(idx), ((i % MW) * TS + o, (i // MW) * TS + o))
        if m["over"][i]:
            img.alpha_composite(tile(m["over"][i]), ((i % MW) * TS + o, (i // MW) * TS + o))
    for tx, ty, idx in e["ring"]:
        img.paste(tile(idx), (tx * TS + o, ty * TS + o))
    things = [("decor/" + n, x, y, False) for n, x, y in m["decor"]]
    things += [("decor/" + n, x, y, f) for n, x, y, f in e["decor"]]
    things += [("item/" + n, x, y, False) for n, x, y in m["items"]]
    things += [(f"{n}/idle/down", x, y, False) for n, x, y in m["enemies"]]
    things += [(f"{n}/idle/right", x, y, False) for n, x, y, *_ in m["hens"]]
    things += [("tecky/idle/down", *m["start"], False), ("alice/idle/down", *m["alice"], False)]
    for key, x, y, flip in sorted(things, key=lambda t: t[2]):
        sp = meta[key]
        sx, sy, sw, sh, dx, dy = sp["f"][0]
        im = atlas.crop((sx, sy, sx + sw, sy + sh))
        if flip:                          # comme drawSpr(…, { flip: true }) : miroir autour de l'origine
            im, x0 = im.transpose(Image.FLIP_LEFT_RIGHT), x + sp["o"][0] - dx - sw
        else:
            x0 = x - sp["o"][0] + dx
        img.alpha_composite(im, (int(x0) + o, int(y - sp["o"][1] + dy) + o))
    img.convert("RGB").resize((img.width // 2, img.height // 2), Image.LANCZOS).save(os.path.join(WEB, "map_preview.png"))


def main():
    os.makedirs(WEB, exist_ok=True)
    m = build_map()
    atlas, meta = pack(collect())
    atlas.save(os.path.join(WEB, "atlas.png"), optimize=True)
    tileset = tiles.tileset(S, water_marks=False, composites=COMPOSITES)   # eau unie : le jeu anime ses vaguelettes
    tileset.save(os.path.join(WEB, "tiles.png"), optimize=True)
    preview(m, atlas, meta, tileset)
    tpl = open(os.path.join(SRC, "index.template.html"), encoding="utf-8").read()
    game = open(os.path.join(SRC, "game.js"), encoding="utf-8").read()
    import base64
    b64 = lambda p: "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
    data = ("const ATLAS_SRC = \"" + b64(os.path.join(WEB, "atlas.png")) + "\";\n"
            "const TILES_SRC = \"" + b64(os.path.join(WEB, "tiles.png")) + "\";\n"
            "const ATLAS = " + json.dumps(meta, separators=(",", ":")) + ";\n"
            "const SONGS = " + json.dumps({k: dict(zip(("total", "ev"), music.events(k)), bpm=st["bpm"], bar=music.STEPS_PER_BAR)
                                           for k, st in music.STYLES.items()}, separators=(",", ":")) + ";\n"
            "const WINSONG = " + json.dumps(dict(zip(("total", "ev"), music.fanfare_events()), bpm=music.FANFARE_BPM, bar=music.STEPS_PER_BAR), separators=(",", ":")) + ";\n"
            "const LOSESONG = " + json.dumps(dict(zip(("total", "ev"), music.defeat_events()), bpm=music.DEFEAT_BPM, bar=music.STEPS_PER_BAR), separators=(",", ":")) + ";\n"
            "const MAP = " + json.dumps(m, separators=(",", ":"), ensure_ascii=False) + ";\n"
            "const VERSION = " + json.dumps(version(), ensure_ascii=False) + ";\n")
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
        raise SystemExit("Corrige les placements signalés dans carte.json (éditeur de carte : python3 editeur.py)")


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
