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
import butterflies
import decor
import enemies
import critters
import ducks
import farmer
import hens
import hud
import items
import tecky
import vehicles
import music
import tiles
from spritelib import render_svg, flash, PAD

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web")
SRC = os.path.join(ROOT, "web_src")
S = 2
TS = 32 * S

# ====================================================================== NIVEAU
# 80 x 48 tuiles. Le quart nord-ouest (40 x 24) est la carte d'origine : départ, campagne, village, route,
# zone industrielle. Puis la ferme à l'est, une rivière qui coupe toute la carte (un seul pont, côté ferme),
# la forêt au sud-est et le parc au sud-ouest, où Alice se cache.
MW, MH = 80, 48


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
    paint("sidewalk", 20, 11, 40, 11)
    paint("paving", 23, 3, 38, 10)
    # campagne sud-ouest : le chemin descend jusqu'à la rivière (barque, pas de pont)
    paint("dirt", 6, 17, 7, 26)
    paint("dirt", 7, 20, 14, 21)
    paint("water", 1, 18, 4, 22)
    # zone industrielle
    paint("sidewalk", 22, 16, 40, 16)
    paint("concrete", 22, 17, 40, 24)
    paint("road", 30, 16, 31, 17)
    # ferme (nord-est) : cour en terre, chemin vers la route, champs labourés
    paint("dirt", 50, 5, 62, 10)
    paint("dirt", 55, 10, 56, 12)
    paint("field", 43, 2, 48, 9)
    paint("field", 65, 2, 77, 9)
    paint("field", 52, 18, 60, 23)
    paint("water", 70, 18, 74, 21)          # mare
    paint("dirt", 63, 16, 65, 25)           # chemin de la route au pont
    # rivière d'est en ouest ; le pont (BRIDGES) la franchit en x 63..65
    paint("water", 0, 26, MW, 29)
    # forêt (sud-est) : sous-bois, sentier sinueux du pont vers le parc, clairière et recoins à l'est
    paint("forest", 40, 31, MW, MH)
    paint("dirt", 63, 30, 65, 35)
    paint("dirt", 50, 33, 65, 35)
    paint("dirt", 50, 33, 52, 41)
    paint("dirt", 42, 39, 52, 41)
    paint("dirt", 65, 39, 72, 40)
    paint("dirt", 44, 33, 50, 34)           # recoin ouest (trésor)
    paint("dirt", 72, 39, 77, 40)           # vers la chaussure d'Alice et le recoin est
    paint("dirt", 76, 40, 77, 44)
    # parc (sud-ouest) : allée, place de la fontaine, aire de jeux (séparée de l'allée par l'herbe)
    paint("paving", 13, 39, 38, 40)
    paint("paving", 16, 34, 28, 44)
    paint("dirt", 3, 35, 11, 45)
    return g


# pont : coins (x0, y0, x1, y1) qui ne sont plus de l'eau, sous le tablier du décor « bridge »
BRIDGES = [(63, 25, 65, 30)]


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
    # bord de la rivière, au bout du chemin : barque, roseaux, panneau « pas de pont ici »
    ("boat", 6.6, 27.7), ("reeds", 4.6, 25.8), ("reeds", 9.2, 25.9), ("reeds", 2.2, 25.7), ("signpost", 8.8, 24.8),
    ("tree", 1.2, 25.2), ("bush", 11.5, 25), ("tree", 16, 25.3), ("reeds", 20.5, 25.8), ("bush", 26, 25.2),
    ("reeds", 31.4, 25.9), ("tree", 36.5, 25.3), ("reeds", 45, 25.8), ("bush", 50, 25.2), ("reeds", 57, 25.9),
    ("reeds", 69, 25.8), ("tree", 75, 25.3), ("reeds", 78.5, 25.9),

    # ================= FERME (nord-est)
    ("barn", 56, 4.9), ("chicken_coop", 60.8, 6.4),
    ("tractor", 52, 8.7), ("hay", 50.8, 5.6), ("hay", 52, 6), ("hay", 61.5, 4.2),
    ("scarecrow", 70.5, 6), ("scarecrow", 45.5, 5.6),
    ("tree", 41.5, 2), ("tree", 49.5, 1.3), ("tree", 63, 1.3), ("tree", 78.6, 1.6), ("tree", 41.5, 10.8),
    ("tree", 78.8, 10.6), ("bush", 63.6, 10.6), ("bush", 49, 10.5), ("rock", 66, 10.8),
    ("signpost", 57.6, 11.2),
    # au sud de la route : verger, champ, mare, chemin du pont
    ("tree", 43, 18.6), ("tree", 46.4, 18.4), ("tree", 49.8, 18.6), ("tree", 43.2, 21.8), ("tree", 46.6, 22),
    ("tree", 50, 21.8), ("tree", 76.5, 17.6), ("tree", 78.5, 22.6), ("bush", 61.6, 17.4), ("bush", 67.4, 23.3),
    ("reeds", 69.6, 18.6), ("reeds", 74.6, 21.4), ("hay", 61.8, 21.4), ("scarecrow", 56, 21.4),
    ("signpost", 62, 24.6),
    ("bridge", 64, 30),

    # ================= FORÊT (sud-est)
    ("tree", 52.4, 46.8), ("tree", 61.2, 47.4), ("tree", 46.4, 37.2), ("tree", 58.4, 37.2),
    ("stump", 53.8, 36.6), ("stump", 67.6, 42.2), ("stump", 44.6, 42.6), ("log", 59.6, 40.8), ("log", 73.4, 35.6),
    ("mushrooms", 54.4, 38.4), ("mushrooms", 69.8, 36.8), ("mushrooms", 47.2, 42), ("mushrooms", 76.2, 42.6),
    ("mushrooms", 62.8, 33), ("fern", 49.4, 37.6), ("fern", 60.4, 35.6), ("fern", 66.2, 38.2), ("fern", 43.4, 38),
    ("fern", 71.6, 46.6), ("fern", 57.2, 43.8), ("signpost", 53.2, 32.6),

    # ================= PARC (sud-ouest), Alice dans la cabane
    ("playhouse", 5, 37.3), ("slide", 9, 37.6), ("swing", 5.6, 42.4), ("sandbox", 9.6, 44.4),
    ("fountain", 22, 39.9), ("bench", 18, 35.9), ("bench", 26, 35.9), ("bench", 18, 43.9), ("bench", 26, 43.9),
    ("flower_pot", 16.6, 34.6), ("flower_pot", 27.6, 34.6), ("flower_pot", 16.6, 44.6), ("flower_pot", 27.6, 44.6),
    ("lamppost", 13, 38.7), ("lamppost", 31, 38.7), ("lamppost", 37, 41.6),
    ("tree", 2, 31.6), ("tree", 8, 31.2), ("tree", 14, 31.6), ("tree", 30.6, 31.6), ("tree", 36.6, 31.2),
    ("tree", 33.4, 35.4), ("tree", 13.2, 47.4), ("tree", 33.6, 46.6), ("tree", 1.6, 46.8), ("tree", 38.4, 46.8),
    ("bush", 12.4, 34.2), ("bush", 31.6, 43.4), ("bush", 36.2, 35.6), ("bush", 2.2, 34.2),
    ("bush", 38.6, 37.6), ("bush", 38.6, 42.6), ("signpost", 36.6, 38.4),
    ("tree", 33.2, 38.2), ("tree", 35.8, 43.6), ("tree", 30.2, 46.6), ("tree", 9, 33.6), ("bush", 30.4, 33.8),
    ("bush", 34.2, 45.6), ("bush", 12.6, 46.2), ("flower_pot", 14.4, 38.2), ("flower_pot", 14.4, 42.2),
    ("bench", 35, 33.9), ("tree", 24.2, 47.4), ("bush", 20.4, 31.4), ("bush", 27, 31.6),
]
for x in range(9, 16):
    DECOR.append(("fence_wood_h", x, 11.25))
for x in list(range(22, 30)) + list(range(32, 40)):
    DECOR.append(("fence_metal_h", x, 17.3))
for x in range(8, 16):
    DECOR.append(("fence_wood_h", x, 16.35))
for x in list(range(64, 70)) + list(range(72, 77)):   # clôture du grand champ, avec une barrière ouverte
    DECOR.append(("fence_wood_h", x, 10.3))
for y in range(17, 24):                               # entre la zone industrielle et le verger
    DECOR.append(("fence_metal_v", 40.6, y + 1))
# enclos des poules (quête du fermier) : clôture en bois autour du poulailler, barrière ouverte au sud
PEN = (59, 5.2, 64, 9.0)            # lignes de clôture, en tuiles : x0, y0, x1, y1
PEN_GATE = (60, 62)                 # ouverture dans la clôture du bas
for x in range(PEN[0], PEN[2]):
    DECOR.append(("fence_wood_h", x, PEN[1]))
    if not PEN_GATE[0] <= x < PEN_GATE[1]:
        DECOR.append(("fence_wood_h", x, PEN[3]))
for y in (6.2, 7.2, 8.2, PEN[3]):
    DECOR.append(("fence_wood_v", PEN[0], y))
    DECOR.append(("fence_wood_v", PEN[2], y))
FARMER = (57.9, 8.4)                # le fermier Gaston, contre la clôture ouest de l’enclos
# terriers sous les grillages : Tecky passe d'une extrémité à l'autre (raccourcis)
TUNNELS = [((40.0, 21.0), (41.25, 21.0)),        # zone industrielle <-> verger de la ferme
           ((36.5, 16.75), (36.5, 18.0)),        # trottoir <-> zone industrielle
           ((14.5, 10.75), (14.5, 11.95)),       # pré de la niche <-> grande route
           ((67.5, 9.75), (67.5, 10.95))]        # grand champ de la ferme <-> bord de route
for a, b in TUNNELS:
    for x, y in (a, b):
        DECOR.append(("burrow", x, y))

ITEMS = [
    ("bone", 6, 7.5), ("bone", 12, 17.6), ("bone", 28.5, 7.2), ("bone", 23.5, 19.8), ("bone", 19.5, 11.3),
    ("sausage", 14.5, 22.5), ("sausage", 37.5, 19.2),
    ("medal", 1.4, 9.4), ("medal", 38.6, 18.3),
    ("squeaky", 9.5, 6.2), ("squeaky", 2.5, 16.9), ("squeaky", 33, 5.2),
    ("ball", 6.3, 5.4), ("ball", 15, 6.3), ("ball", 19.5, 20), ("ball", 25, 13.8), ("ball", 36.8, 9.4),
    # ferme
    ("bone", 53.6, 7.4), ("bone", 66.4, 21.6), ("sausage", 78.4, 4.6), ("medal", 78.2, 19.6),
    ("squeaky", 72.4, 22.6), ("ball", 44.8, 20.2), ("ball", 59, 11.3),
    # forêt
    ("bone", 63.6, 36.6), ("bone", 51, 44.4), ("sausage", 74.4, 38.6), ("medal", 43.2, 47),
    ("squeaky", 69.6, 41.2), ("ball", 56.6, 39.8),
    # parc
    ("bone", 30.4, 41.6), ("sausage", 20.4, 46.4), ("squeaky", 24.6, 33.2), ("ball", 12.6, 42.6),
    ("medal", 35.6, 44.6),
    # indices d'Alice : barrette à la ferme, chaussure dans la clairière de la forêt, doudou au parc
    ("hairclip", 58.4, 9.4), ("shoe", 73.6, 41.2), ("plush", 29.6, 37.4),
]
ENEMIES = [
    # le 1er roquet est assez loin de la niche pour ne pas attaquer dès la fin de l'intro
    ("roquet", 12, 8.8), ("roquet", 14, 3.5), ("roquet", 10.5, 19.2), ("roquet", 27, 6.5),
    ("bouledogue", 19.6, 16.9), ("bouledogue", 15.5, 22.2),
    ("molosse", 33.5, 20.2),
    # ferme : les chiens de berger gardent la cour et les prés
    ("berger", 52.6, 10.6), ("berger", 66, 19.5), ("berger", 72, 6.5), ("bouledogue", 47.5, 20.4), ("roquet", 60.5, 23),
    # forêt
    ("roquet", 57, 34), ("roquet", 69, 39.6), ("bouledogue", 46.5, 40.4), ("molosse", 74.5, 40.6),
    # parc
    ("roquet", 26.5, 37.2), ("bouledogue", 15, 41.6), ("berger", 33, 40),
]
# trésors enterrés : au centre de la tuile des traces de pattes (scintillement et trou creusé s'y alignent)
# grande route : passages piétons (première des deux tuiles) et circulation (voie 0 en haut vers l'ouest,
# voie 1 en bas vers l'est ; x de départ en tuiles). Les véhicules s'arrêtent aux passages quand Tecky y est.
CROSSINGS = (10, 34, 55, 63)
# massifs de fleurs au sol (tuiles) : dessinés en détail sur le sol, et perchoirs des papillons
FLOWER_BEDS = ((7, 4), (15, 8), (3, 17), (10, 5), (6, 9), (16, 20), (44, 20), (46, 22), (77, 15), (68, 41),
               (14, 36), (30, 36), (14, 43), (31, 45), (35, 33), (2, 40), (12, 46), (24, 31), (36, 45), (19, 46),
               (6, 33), (8, 46))
TRAFFIC = [("car_red", 0, 10), ("bus", 0, 40), ("car_yellow", 0, 66),
           ("car_blue", 1, 20), ("van", 1, 50), ("car_green", 1, 72)]
# papillons (couleur, coin où ils volettent) : surtout au parc, mais aussi près de la niche, sur la place du village,
# dans la campagne sud-ouest, au verger de la ferme et dans la clairière de la forêt
BUTTERFLIES = [("yellow", 20, 33), ("blue", 24.5, 36.5), ("pink", 13, 40), ("orange", 30, 43),
               ("blue", 34, 34), ("yellow", 6.5, 44.5), ("pink", 10, 33.6),
               ("yellow", 9, 5.6), ("orange", 6, 8.6),
               ("pink", 28, 6.4), ("blue", 33, 5.4),
               ("blue", 4.5, 16.8), ("yellow", 14.5, 19.8),
               ("orange", 46, 21), ("yellow", 44, 19.6),
               ("blue", 69.5, 40.6)]
# poules (animées : elles picorent, se promènent, et s'enfuient quand Tecky aboie). Les cinq premières se sont
# échappées de l'enclos : c'est la quête du fermier (quest = 1) ; les deux du sud de la route vivent leur vie.
HENS = [("hen", 53.6, 9.6, 1), ("hen_white", 55.2, 7.0, 1), ("hen", 66.6, 6.8, 1), ("hen_white", 58.8, 11.0, 1),
        ("hen", 49.6, 7.6, 1), ("hen_white", 66.6, 18.4, 0), ("hen", 65.4, 20.2, 0)]
# canards (espèce, x, y en tuiles, famille) : une même famille = la cane et ses canetons, qui la suivent en file
DUCKS = [("duck_f", 9.9, 2.4, 1), ("duckling", 9.4, 2.55, 1), ("duckling", 9.0, 2.7, 1), ("duckling", 8.6, 2.85, 1),
         ("duck", 72.6, 19.4, 0), ("duck_f", 71.6, 19.9, 0),
         ("duck", 30.5, 27.4, 0), ("duck_f", 31.6, 27.8, 0), ("duck", 48.0, 27.6, 0), ("duck", 2.6, 20.0, 0)]
# petites bêtes que Tecky peut poursuivre : écureuils (forêt, parc) qui grimpent aux arbres, chats (village, zone
# industrielle) qui sautent sur les toits et les conteneurs
CRITTERS = [("squirrel", 57.4, 37.9), ("squirrel", 66.2, 36.9), ("squirrel", 48.6, 44.4), ("squirrel", 71.2, 44.4),
            ("squirrel", 10.6, 32.6), ("cat", 29.6, 9.0), ("cat_black", 31.6, 19.4)]
DIG = [(12.5, 6.5), (5.5, 19.5), (21.5, 18.5),
       (47.5, 20.5), (68.5, 11.5), (44.5, 33.5), (76.5, 44.5), (34.5, 33.5)]
START = (4.5, 4.2)
ALICE = (5, 37.3 + 14 / 64)   # juste devant la porte de la cabane du parc (cachée jusqu'aux trois indices)
TITLE = (33.5, 7.3)        # caméra de l'écran titre : la place du village
SIGNS = [
    (5.6, 11.1, "Niche de Tecky : en haut. Village : suivre la route vers l'est."),
    (7.3, 16.6, "Les champs du Père Gaston. Attention, chiens pas commodes !"),
    (8.8, 24.8, "Pas de pont ici ! Le seul pont est loin à l'est, après la ferme."),
    (57.6, 11.2, "Ferme des Tilleuls. Attention aux chiens de berger : quand ils s'accroupissent, ils vont charger !"),
    (62, 24.6, "Pont de la rivière. Au sud : la grande forêt."),
    (53.2, 32.6, "Sentier de la forêt. Le parc des enfants est à l'ouest."),
    (36.6, 38.4, "Parc des enfants : toboggan, balançoire, bac à sable et cabane !"),
]


def forest_firs():
    """Sapins serrés dans la forêt (sud-est) : en quinconce un peu désordonné, hors des sentiers et à l'écart des
    objets, chiens, trésors, panneaux et autres décors (check_placement.js vérifie que tout reste atteignable)."""
    g = corner_grid()
    rnd = random.Random(11)
    keep = ([(x, y) for _, x, y in ITEMS] + [(x, y) for _, x, y in ENEMIES] + list(DIG)
            + [(x, y) for x, y, _ in SIGNS] + [(x, y) for n, x, y in DECOR if x > 39 and y > 30])

    def near_path(px, py):
        return any(g[cy][cx] == "dirt" for cy in range(int(py - 1.8), int(py + 1.4) + 1)
                   for cx in range(int(px - 1.3), int(px + 1.3) + 2) if 0 <= cy <= MH and 0 <= cx <= MW)
    out = []
    y, row = 31.6, 0
    while y < MH:
        x = 40.8 + (row % 2) * 1.0
        while x < MW - 0.4:
            px, py = x + rnd.uniform(-0.4, 0.4), min(MH - 0.1, y + rnd.uniform(-0.25, 0.25))
            if not near_path(px, py) and all((px - kx) ** 2 + (py - ky) ** 2 > 1.8 ** 2 for kx, ky in keep):
                out.append(("fir", round(px, 2), round(py, 2)))
            x += 2.0
        y += 1.55
        row += 1
    return out


DECOR += forest_firs()
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
    for tx in CROSSINGS:                              # passages piétons (dont chemin de la ferme et du pont)
        for ty in (12, 13, 14):
            ground[ty * MW + tx] = ground[ty * MW + tx + 1] = 7
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
    # nouvelles zones
    for tx, ty in ((44, 33), (47, 38), (53, 31), (58, 36), (61, 41), (66, 33), (70, 43), (74, 39), (77, 34),
                   (45, 46), (55, 45), (63, 46), (49, 42), (68, 37)):
        put("feuilles mortes", tx, ty)
    for tx, ty in ((57, 40), (72, 45), (43, 41)):
        put("touffe d'herbe", tx, ty)
    for tx, ty in FLOWER_BEDS:
        put("fleurs", tx, ty)
    for tx, ty in ((51, 9), (58, 6), (64, 22)):
        put("cailloux", tx, ty)
    put("flaque", 53, 9)
    put("flaque", 60, 34)
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
        "items": [[n, px(x), px(y)] for n, x, y in ITEMS],
        "enemies": [[n, px(x), px(y)] for n, x, y in ENEMIES],
        "hens": [[n, px(x), px(y), q] for n, x, y, q in HENS],
        "pen": [px(v) for v in PEN], "penGate": [px(v) for v in PEN_GATE],
        "farmer": [px(FARMER[0]), px(FARMER[1])],
        "critters": [[n, px(x), px(y)] for n, x, y in CRITTERS],
        "rest": {a: [fps, loop] for a, (_, fps, _, loop) in tecky.REST_ANIMS.items()},
        "ducks": [[n, px(x), px(y), f] for n, x, y, f in DUCKS],
        "duckFps": {k: {a: fps for a, (_, fps, _) in ducks.anims(k).items()} for k in ducks.KINDS},
        "duckLoop": {k: {a: loop for a, (_, _, loop) in ducks.anims(k).items()} for k in ducks.KINDS},
        "critterFps": {k: {a: fps for a, (_, fps, _) in critters.anims(k).items()} for k in critters.KINDS},
        "tunnels": [[px(a[0]), px(a[1]), px(b[0]), px(b[1])] for a, b in TUNNELS],
        "butterflies": [[c, px(x), px(y)] for c, x, y in BUTTERFLIES],
        # où les papillons se posent : (x, y au sol, hauteur) — sur les pots de fleurs, ou sur les massifs
        "flowers": [[px(x), px(y) + 2, 44] for n, x, y in DECOR if n == "flower_pot"]
                   + [[px(tx + 0.5), px(ty + 0.5), 4] for tx, ty in FLOWER_BEDS],
        "traffic": {"lanes": [px(12.95), px(14.95)], "road": [px(11.5), px(15.5)],
                    "crossings": [[px(tx), px(tx + 2)] for tx in CROSSINGS],
                    "vehicles": [[n, lane, px(x)] for n, lane, x in TRAFFIC]},
        "dig": [[px(x), px(y)] for x, y in DIG],
        "start": [px(START[0]), px(START[1])],
        "alice": [px(ALICE[0]), px(ALICE[1])],
        "title": [px(TITLE[0]), px(TITLE[1])],
        "decorFps": {n: fps for n, (_, fps) in decor.ANIMATED.items()},
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
    for kind in critters.KINDS:                         # écureuil, chats : de profil vers la droite, pieds en (16, 28)
        for a in critters.anims(kind):
            out.append((f"{kind}/{a}", [render_svg(sv, 32, 32, S, PAD) for sv in critters.frames(kind, a)], (16 * S + M, 28 * S + M), True))
    for kind in ducks.KINDS:                            # canards : de profil vers la droite, ligne d'eau en (16, 24)
        for a in ducks.anims(kind):
            out.append((f"{kind}/{a}", [render_svg(sv, 32, 32, S, PAD) for sv in ducks.frames(kind, a)], (16 * S + M, 24 * S + M), True))
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
    for n, ims in hud.all_sprites(S).items():
        key = "hud/" + n.replace("spr_hud_", "").replace("spr_", "")
        o = {"spr_hud_arrow": (40, 40), "spr_hud_arrow_icon": (22, 22)}.get(n, (0, 0))
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
    things += [(f"{n}/idle/right", x, y) for n, x, y, *_ in m["hens"]]
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
    tileset = tiles.tileset(S, water_marks=False)          # eau unie : le jeu anime ses vaguelettes
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
            "const LOSESONG = " + json.dumps(dict(zip(("total", "ev"), music.defeat_events()), bpm=music.DEFEAT_BPM), separators=(",", ":")) + ";\n"
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
