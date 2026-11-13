#!/usr/bin/env python3
"""
Prépare la version web de Tecky Quest :
  web/atlas.png  + données de l'atlas (sprites x2, découpés au plus juste)
  web/tiles.png  tileset x2
  web/atlas_x4_N.png, web/tiles_x4.png  les mêmes images deux fois plus fines, chargées par le jeu sur grand écran
  web/saison_<nom>_*.png  le tileset et les sprites redessinés aux couleurs d'une saison (build_saisons)
  web/index.html page du jeu (web_src/index.template.html + game.js + données)
  web/map_preview.png  aperçu du niveau (contrôle)

    python3 pack_web.py              # tout
    python3 pack_web.py --sans-hd    # sans les images x4 (plus rapide ; le jeu reste en x2)
"""
import hashlib
import json
import math
import re
import os
import sys

from PIL import Image

import alice2
import batiments
import mobilier
import butterflies
import carte
import cows
import decor
import chiens2
import critters
import ducks
import episodes
import npcs
import saisons
import port
import spritelib
import herissons
import farmer
import hens
import hud
import items
import lisiere
import tecky2
import vehicles
import music
import nature
import tiles
import villageois
from spritelib import render_svg, flash, PAD

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web")
SRC = os.path.join(ROOT, "web_src")
S = 2
TS = 32 * S
HD = 2                 # images nettes : rendues à S * HD (x4), mêmes cadres et mêmes places que l'atlas x2
PAGE = 2048            # hauteur d'une page d'atlas, en pixels x2 : aucune image n'est à cheval sur deux pages, pour
                       # que l'atlas x4 se découpe en pages de 4096 px (la plus grande texture de bien des cartes)

# ====================================================================== NIVEAU
# La carte est dans carte.json (carte.py ; on la modifie avec l'éditeur de carte : python3 editeur.py), en tuiles.
# 96 x 64 tuiles. Au nord de la grande route : la niche de Tecky, le village, la ferme. Au sud : la campagne, la zone
# industrielle (le dépôt, et son port au bord de la rivière), le verger et les prés de la ferme. Une rivière coupe toute
# la carte (un seul pont, côté ferme) ; au-delà, le parc au sud-ouest, où Alice se cache, et la forêt au sud-est.
# Ici : les listes de la carte (en tuiles), et ce qui s'en déduit (poteaux des panneaux, terriers, clôtures de l'enclos,
# filet de Léon, rails et heurtoirs de la voie, coins du pont, lisière).
# (ces variables sont celles de la carte courante : charger_carte(nom), plus bas, les pose ; le jeu a plusieurs cartes)
_T = lambda cle: [tuple(e) for e in CARTE[cle]]
_P = lambda cle: tuple(CARTE[cle])


def corner_grid():
    """Grille des coins [y][x] (MH+1 x MW+1) : le terrain de chaque coin ; une tuile se dessine d'après ses quatre coins."""
    return carte.terrain_grid(CARTE)


def derived_decor():
    """Décors qui se déduisent de la carte : poteau de chaque panneau, filet de Léon, heurtoirs et rails de la voie de
    Titine, clôture de l'enclos (barrière ouverte en bas), les deux bouts de chaque terrier."""
    la = lambda cle: cle not in CARTE["absents"]              # (une carte annexe n'a pas forcément filet, voie, enclos)
    out = [("signpost", x, y) for x, y, _ in SIGNS] + ([("goal_net", *GOAL)] if la("goal") else [])
    if TRACK:
        x0, x1, y = TRACK
        out += [("buffer_stop", x0, y + 0.1), ("buffer_stop", x1, y + 0.1)]
        out += [("rail", x, y) for x in range(math.floor(x0), math.ceil(x1))]
    if la("pen"):
        px0, py0, px1, py1 = PEN
        for x in range(px0, px1):
            out.append(("fence_wood_h", x, py0))
            if not PEN_GATE[0] <= x < PEN_GATE[1]:
                out.append(("fence_wood_h", x, py1))
        ys = [py0 + k for k in range(1, math.ceil(py1 - py0)) if py0 + k < py1] + [py1]
        for y in ys:
            out += [("fence_wood_v", px0, y), ("fence_wood_v", px1, y)]
    out += [("burrow", x, y) for a, b in TUNNELS for x, y in (a, b)]
    if ROAD_FIN is not None:                                  # la route s'arrête : le porche du parking (lisiere.porche)
        out.append(("porche", ROAD_FIN + (lisiere.PORCHE[1] - lisiere.PORCHE[0]) / 32, ROAD + 4))
    return out




def sols():
    """Où chaque décor touche le sol (nature.bandes_image) : le jeu en tire son ombre portée. Clé : le sprite
    (« decor/<clé> ») ; les décors plats ou sur l'eau n'y sont pas."""
    out = {n: nature.bandes(n, S) for n in sorted({v for noms, _ in nature.VARIANTES.values() for v in noms})
           if nature.CATALOGUE[n]().sol}                 # (sol = None : à plat ou sur l'eau, pas d'ombre portée)
    for n in decor.DECOR:
        if n in nature.VARIANTES or not decor.sol(n):
            continue
        w, h, ox, oy = decor.cadre(n)
        out[n] = nature.bandes_image(render_svg(decor.svgs(n)[0], w, h, S, PAD), ox, oy, decor.sol(n), S)
    return out


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


def charger_carte(nom=carte.MONDE, episode=None):
    """Fait de la carte `nom` la carte courante : ses listes (en tuiles) et ce qui s'en déduit (décors, pont, lisière).
    Une carte annexe (cartes/<nom>.json) n'a que ce qu'elle déclare : carte.completer() met le reste hors de la carte.
    episode : la carte telle que cet épisode la joue (sa surcharge cartes/<épisode>/<nom>.json par-dessus)."""
    global NOM, CARTE, MW, MH, ITEMS, ENEMIES, DIG, SIGNS, HENS, DUCKS, COWS, CRITTERS, BUTTERFLIES, VILLAGERS
    global LETTERS, BALLS, TOYS, BABIES, TUNNELS, START, ALICE, TITLE, FARMER, POSTMAN, NEIGHBOR, POMPON
    global LEON, GOAL, IRIS, PIQUETTE, PEN, PEN_GATE, TRACK, CALM, ROAD_TUNNELS, ROAD, CROSSINGS, TRAFFIC
    global DETAILS, FLOWER_BEDS, DECOR, BRIDGES, EDGE, ROAD_FIN
    NOM = nom
    CARTE = carte.completer(carte.charger_episode(nom, episode))
    MW, MH = CARTE["w"], CARTE["h"]
    ITEMS, ENEMIES, DIG, SIGNS = _T("items"), _T("enemies"), _T("dig"), _T("signs")
    HENS, DUCKS, COWS, CRITTERS, BUTTERFLIES, VILLAGERS = (_T(k) for k in ("hens", "ducks", "cows", "critters", "butterflies", "villagers"))
    LETTERS, BALLS, TOYS, BABIES = _T("letters"), _T("balls"), _T("toys"), _T("babies")
    TUNNELS = [((ax, ay), (bx, by)) for ax, ay, bx, by in CARTE["tunnels"]]
    START, ALICE, TITLE = _P("start"), _P("alice"), _P("title")
    FARMER, POSTMAN, NEIGHBOR, POMPON = _P("farmer"), _P("postman"), _P("neighbor"), _P("pompon")
    LEON, GOAL, IRIS, PIQUETTE = _P("leon"), _P("goal"), _P("iris"), _P("piquette")
    PEN, PEN_GATE = _P("pen"), _P("penGate")
    TRACK = _P("track") if CARTE["track"] else None           # (None : pas de voie ferrée sur cette carte)
    CALM = _T("calm")
    ROAD_TUNNELS = _T("roadTunnels")      # tunnels aux deux bouts de la grande route (lisiere.py) : x, y du pied, miroir
    route = CARTE["traffic"] or {"y": None, "crossings": [], "vehicles": []}      # (pas de grande route : y = None)
    ROAD = route["y"]                     # première rangée de la grande route (4 rangées ; marquage sur la 2e)
    ROAD_FIN = route.get("fin")           # le x où elle s'arrête, devant le porche du parking (None : elle traverse la carte)
    CROSSINGS = tuple(route["crossings"])                     # passages piétons : première des deux tuiles
    TRAFFIC = [tuple(v) for v in route["vehicles"]]           # véhicules : voie 0 (en haut, vers l'ouest) ou 1, x de départ
    DETAILS = _T("details")
    FLOWER_BEDS = [(tx, ty) for n, tx, ty in DETAILS if n == "fleurs"]      # massifs de fleurs : perchoirs des papillons
    DECOR = _T("decor") + derived_decor()
    # pont : coins (x0, y0, x1, y1) qui ne sont plus de l'eau, sous le tablier de chaque décor « bridge » (5 tuiles de haut)
    BRIDGES = [(round(x) - 1, round(y) - 5, round(x) + 1, round(y)) for n, x, y in DECOR if n == "bridge"]
    # (le pont en travers, « bridge_h », posé sur un milieu de tuile : sept coins de large, trois de haut)
    BRIDGES += [(math.floor(x) - 3, math.floor(y) - 2, math.floor(x) + 4, math.floor(y)) for n, x, y in DECOR if n == "bridge_h"]
    EDGE = edge_decor(corner_grid(), edge_keep())


charger_carte()
# variantes des tuiles : terrains pleins (35 % des tuiles), choisies d'après la
# position de la tuile (hash3) : modifier un coin de la carte ne change rien ailleurs, et l'éditeur fait le même choix
GRASS_VARIANTS = [1]        # herbe unie : brins et fleurs sont semés par le jeu (game.js : groundDetails())
FULL_VARIANTS = {"dirt": [9, 10], "road": [11, 12], "paving": [13], "concrete": [14, 15]}


def hash3(a, b, c):
    """Nombre pseudo-aléatoire dans [0, 1[ tiré de trois entiers : même calcul que hash3 de game.js et editeur/sol.js."""
    M = 0xFFFFFFFF
    h = ((a * 374761393) ^ (b * 668265263) ^ (c * 1274126177)) & M
    h = ((h ^ (h >> 13)) * 1103515245) & M
    return (h ^ (h >> 16)) / 4294967296
OV = {n: i for i, (n, _) in enumerate(tiles.OVERLAYS)}


COMPOSITES = []       # tuiles composées (trois terrains : bout de chemin sur la route…), ajoutées au tileset web


def build_map():
    """Les données de la carte courante (charger_carte), pour le jeu : CARTES[nom]. Les tuiles composées qu'elle
    demande s'ajoutent à COMPOSITES, commun à toutes les cartes : le vider avant de les construire toutes."""
    g = corner_grid()
    ground = []

    def pick(cs, tx, ty):                             # tuile (tx, ty) d'après ses quatre coins (NO, NE, SO, SE)
        up, lo, bits = tiles.resolve(cs)
        if tiles.needs_composite(cs):               # (suivie de sa place si sa texture en dépend : tiles.phase())
            cle = tuple(cs) + (tiles.phase(cs, tx, ty) or ())
            if cle not in COMPOSITES:
                COMPOSITES.append(cle)
            return tiles.COMPOSITE_BASE + COMPOSITES.index(cle)
        if up == "grass":
            return GRASS_VARIANTS[int(hash3(tx, ty, 1) * len(GRASS_VARIANTS))]
        idx = tiles.tile_index(up, bits, "grass" if bits == 15 else lo)
        v = FULL_VARIANTS.get(up)
        if bits == 15 and v and hash3(tx, ty, 2) < 0.35:
            idx = v[int(hash3(tx, ty, 3) * len(v))]
        return idx
    for ty in range(MH):
        for tx in range(MW):
            ground.append(pick([g[ty][tx], g[ty][tx + 1], g[ty + 1][tx], g[ty + 1][tx + 1]], tx, ty))
    # marquages de la route (sur sa deuxième rangée), tant qu'elle dure : sur la côte, elle s'arrête au parking
    at = lambda x, y: g[min(max(y, 0), MH)][min(max(x, 0), MW)]
    chaussee = lambda tx: ROAD is not None and all(at(tx + i, ROAD + 1 + j) == "road" for i in (0, 1) for j in (0, 1))
    for tx in range(MW):
        if chaussee(tx):
            ground[(ROAD + 1) * MW + tx] = 5 if tx % 2 == 0 else tiles.tile_index("road", 15)
    # sol de la lisière : lisiere.RING tuiles autour de la carte, qui prolongent celles du bord (coins ramenés sur le
    # bord : la route, ses marquages, la rivière et le ruisseau continuent tout droit)
    R, ring = lisiere.RING, []
    for ty in range(-R, MH + R):
        for tx in range(-R, MW + R):
            if not (0 <= tx < MW and 0 <= ty < MH):
                idx = pick([at(tx, ty), at(tx + 1, ty), at(tx, ty + 1), at(tx + 1, ty + 1)], tx, ty)
                ring.append([tx, ty, (5 if tx % 2 == 0 else tiles.tile_index("road", 15)) if ty == (ROAD or 0) + 1 and chaussee(tx) else idx])
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
    water = [1 if g[y][x] in tiles.EAUX else 0 for y in range(MH + 1) for x in range(MW + 1)]      # (eau douce et mer)
    # la falaise : les coins de craie, où l'on ne marche pas (game.js : cliffAt()) ; rien si la carte n'en a pas
    cliff = [1 if g[y][x] == "chalk" else 0 for y in range(MH + 1) for x in range(MW + 1)]
    # le plateau (la lande et l'escalier qui y monte) : on ne franchit son bord que par l'escalier (rimAt())
    plateau = [1 if g[y][x] in ("heath", "stairs") else 0 for y in range(MH + 1) for x in range(MW + 1)]
    stairs = [1 if g[y][x] == "stairs" else 0 for y in range(MH + 1) for x in range(MW + 1)]
    px = lambda v: round(v * TS, 1)
    hors = px(carte.HORS)
    m = {
        "w": MW, "h": MH, "ground": ground, "over": over, "water": water, "cliff": cliff if any(cliff) else [],
        "plateau": plateau if any(plateau) else [], "stairs": stairs if any(stairs) else [],
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
        "track": [px(v) for v in TRACK] if TRACK else [hors, hors + 1, hors],
        "piquette": [px(PIQUETTE[0]), px(PIQUETTE[1])], "babies": [[px(x), px(y)] for x, y in BABIES],
        "critters": [[n, px(x), px(y)] for n, x, y in CRITTERS],
        "ducks": [[n, px(x), px(y), f] for n, x, y, f in DUCKS],
        "cows": [[n, px(x), px(y)] for n, x, y in COWS],
        "villagers": [[n, px(x), px(y)] for n, x, y in VILLAGERS],
        "tunnels": [[px(a[0]), px(a[1]), px(b[0]), px(b[1])] for a, b in TUNNELS],
        "butterflies": [[c, px(x), px(y)] for c, x, y in BUTTERFLIES],
        # où les papillons se posent : (x, y au sol, hauteur) — sur les pots de fleurs, ou sur les massifs
        "flowers": [[px(x), px(y) + 2, 44] for n, x, y in DECOR if n == "flower_pot"]
                   + [[px(tx + 0.5), px(ty + 0.5), 4] for tx, ty in FLOWER_BEDS],
        # la grande route : voies 0 et 1, bords de la chaussée (pour les chiens, Tecky, les poules)
        # (pas de grande route sur cette carte : rien n'y roule, personne ne la touche)
        "traffic": {"lanes": [px(ROAD + 0.95), px(ROAD + 2.95)], "road": [px(ROAD - 0.5), px(ROAD + 3.5)],
                    "crossings": [[px(tx), px(tx + 2)] for tx in CROSSINGS],
                    # end : là où la route s'arrête, à la bouche du porche (null : elle traverse la carte)
                    "end": px(ROAD_FIN) if ROAD_FIN is not None else None,
                    "vehicles": [[n, lane, px(x)] for n, lane, x in TRAFFIC]} if ROAD is not None
        else {"lanes": [hors, hors], "road": [hors, hors], "crossings": [], "end": None, "vehicles": []},
        "dig": [[px(x), px(y)] for x, y in DIG],
        "start": [px(START[0]), px(START[1])],
        "alice": [px(ALICE[0]), px(ALICE[1])],
        "title": [px(TITLE[0]), px(TITLE[1])],
        "signs": [[px(x), px(y), t] for x, y, t in SIGNS],
        "farmRoadY": px(ROAD - 0.7) if ROAD is not None else hors,     # les poules ne descendent jamais plus bas (la grande route)
        "ballBox": CARTE["ballBox"],                  # en tuiles : là où roulent les ballons de Léon
        # zones (en tuiles) : la première dont un rectangle contient le point ; un bord de rectangle posé sur le bord
        # de la carte n'a pas de limite (game.js : zoneAt) ; music : variation du thème, sinon celle de son id
        "zones": CARTE["zones"], "landmarks": CARTE["landmarks"],
        "ending": {k: [px(v[0]), px(v[1])] for k, v in CARTE["ending"].items()},   # scène de fin : Alice, Tecky
    }
    # ce que la carte n'a pas (carte annexe), ses tunnels de route et où ils mènent : [n° du tunnel, carte, n° d'arrivée]
    m.update(id=NOM, absents=CARTE["absents"], passages=CARTE["passages"],
             roadTunnels=[[px(x), px(y), f] for x, y, f in ROAD_TUNNELS])
    return m


def build_jeu():
    """Les données du jeu qui ne dépendent d'aucune carte (dessins, ombres, cadences) : JEU dans game.js, dont hérite
    la carte courante (MAP)."""
    ovrow = tiles.OVERLAY_ROW * tiles.COLS
    return {
        "ts": TS,
        "hole": ovrow + OV["trou creusé (trésor)"],
        "shore": tiles.tile_index("water", 0),        # la rangée des tuiles eau / herbe (la 16e : l'eau pleine)
        "sheet": tiles.LARGEUR,                       # colonnes de l'image du tileset
        "tileAlt": tiles.alternees(),                 # bords naturels : rangée du tileset -> rangées de ses variantes
        "wood": tiles.tile_index("forest", 15),       # le sous-bois plein (game.js : woodDetails())
        "fieldRow": tiles.tile_index("field", 0),     # la rangée des tuiles champ / herbe (fieldDetails())
        "furrows": [y * TS // tiles.T for y in tiles.SILLONS],          # les crêtes des buttes, en px dans la tuile
        "wild": {n: list(v) for n, v in nature.SOUS_BOIS.items()},      # détail du sous-bois -> [première image, nombre]
        "crops": len(nature.CULTURES),
        "babyFps": {a: fps for a, (_, fps, _) in herissons.ANIMS.items()},
        "npcFps": dict({"farmer": {a: v[1] for a, v in farmer.ANIMS.items()}},
                       **{k: {a: v[1] for a, v in npcs.ANIMS[k].items()} for k in npcs.KINDS}),
        "rest": {a: [fps, loop] for a, (_, fps, _, loop) in tecky2.REST_ANIMS.items()},
        "teckyFps": {a: fps for a, (_, fps, _) in tecky2.ANIMS.items()},     # cadences propres à Tecky (marche en 8 images)
        "aliceFps": {a: fps for a, (_, fps) in alice2.ANIMS.items()},
        "dogFps": {a: fps for a, (_, fps, _) in chiens2.ANIMS.items()},      # celles des chiens (chiens2.py)
        "badges": hud.BADGES,
        "keys": hud.KEYS, "pads": [k for k, _ in hud.PAD_BUTTONS],   # noms des images de hud/key et hud/pad
        "villagerFps": {k: {a: v[1] for a, v in villageois.ANIMS[k].items()} for k in villageois.KINDS},
        "cowFps": {k: {a: fps for a, (_, fps, _) in cows.anims(k).items()} for k in cows.KINDS},
        "duckFps": {k: {a: fps for a, (_, fps, _) in ducks.anims(k).items()} for k in ducks.KINDS},
        "duckLoop": {k: {a: loop for a, (_, _, loop) in ducks.anims(k).items()} for k in ducks.KINDS},
        "critterFps": {k: {a: fps for a, (_, fps, _) in critters.anims(k).items()} for k in critters.KINDS},
        "decorFps": {n: fps for n, (_, fps) in decor.ANIMATED.items()},
        # variantes de la nature (nature.py) : décor -> [sprites, tirage] ; le jeu en choisit un d'après la position
        "variants": {n: [noms, tirage] for n, (noms, tirage) in nature.VARIANTES.items()},
        # ombres portées : le décalage d'un point par unité de hauteur, et la ligne de contact de chaque sprite
        "shadow": list(nature.OMBRE), "sols": sols(),
        "itemBase": bases()[0], "toyBase": bases()[1],   # objets posés au sol : le bas de leur dessin
        "cast": portees(),                            # familles de sprites à ombre portée (personnages, bêtes, véhicules)
        "perches": {**batiments.perchoirs(S), **mobilier.perchoirs(S)},   # où un chat se réfugie : toits, conteneurs
        # décors agrandis (bâtiments, camion, tracteur, chariot) : leur obstacle (FOOT) grandit d'autant
        "grow": {**batiments.agrandis(), **mobilier.agrandis(), **decor.ECH},
        "vehicleScale": vehicles.ECH,
    }


# ====================================================================== ATLAS
def sans_ovale(svg):
    """Le même dessin sans ce qui est posé dessous (Drawing.under : l'ovale d'ombre des personnages et des bêtes).
    Le jeu leur donne une ombre portée, la silhouette couchée sur le sol (game.js : castShadow())."""
    return re.sub(r"</defs>.*?<g transform=", "</defs><g transform=", svg, count=1, flags=re.S)


def portees():
    """Familles de sprites qui ont une ombre portée dans le jeu (le début de leur clé dans l'atlas)."""
    return (["tecky", "alice", "alice1", "farmer", "hedgehog", "vehicle", "item", "port"] + list(chiens2.CHIENS) + list(npcs.KINDS)
            + list(villageois.KINDS) + list(critters.KINDS) + list(cows.KINDS) + list(hens.COLORS))


def icone(svg, ancien, nouveau):
    """Le même dessin à une autre réduction (contour compensé de même)."""
    a, w = f"scale({ancien})", f'stroke-width="{spritelib.OUTLINE_W / ancien}"'
    assert a in svg and w in svg, (a, w)
    return svg.replace(a, f"scale({nouveau})").replace(w, f'stroke-width="{spritelib.OUTLINE_W / nouveau}"')


def bases():
    """Objets posés au sol (game.js : drawPosed()) : de combien le bas de chaque dessin descend sous son origine, en
    pixels du jeu. Rend (objets et lettre, jouets d'Iris dans l'ordre de port.TOYS)."""
    import numpy as np

    def bas(svg, oy):                     # (l'assise de l'objet, pas son point le plus bas : nature.assise())
        return nature.assise(np.asarray(render_svg(svg, 32, 32, S, PAD).getchannel("A")) > 128) - oy
    m = PAD * S
    out = {n: bas(items.item_frames(n)[0], 32 + m) for n in items.ITEMS}
    out["letter"] = bas(npcs.letter_frames()[0], 32 + m)
    return out, [bas(sv, 16 * S + m) for sv in port.toy_frames()]


def collect(r=1):
    """(clé, liste d'images, origine, découpe ?). r : facteur de rendu (1 : pixels x2, ceux de l'atlas du jeu ;
    HD : les mêmes dessins deux fois plus fins). Les origines restent en pixels x2."""
    out = []
    R = S * r                        # échelle du rendu
    dirs = ("down", "up", "right")
    M = PAD * S                      # décalage d'origine dû à la marge
    CH_O = (48 + M, 88 + M)

    def char(kind, fn):              # les chiens (chiens2.py), cadre de 48 x 48
        for a, (_, _, vues) in chiens2.ANIMS.items():
            for v in vues:
                ims = [render_svg(sans_ovale(s), 48, 48, R, PAD) for s in fn(a, v)]
                if a == "hurt":
                    ims[0] = flash(ims[0])
                out.append((f"{kind}/{a}/{v}", ims, CH_O, True))

    # Tecky (tecky2.py) : un cadre par vue, plus large de profil ; puis ses poses de repos (assis, bâille, se
    # gratte, dort, s'ébroue)
    for a, fn in [(a, tecky2.frames) for a in tecky2.ANIMS] + [(a, tecky2.rest_frames) for a in tecky2.REST_ANIMS]:
        for v in (tecky2.ANIMS.get(a) or tecky2.REST_ANIMS[a])[2]:
            w, h, ox, oy = tecky2.CADRE[v]
            ims = [render_svg(sans_ovale(sv), w, h, R, PAD) for sv in fn(a, v)]
            if a == "hurt":
                ims[0] = flash(ims[0])
            out.append((f"tecky/{a}/{v}", ims, (ox * S + M, oy * S + M), True))
    for dog in chiens2.CHIENS:
        char(dog, lambda a, v, dog=dog: chiens2.frames(dog, a, v))
    w, h, ox, oy = alice2.CADRE                         # Alice (alice2.py)
    for a in alice2.ANIMS:
        for v in dirs:
            out.append((f"alice/{a}/{v}", [render_svg(sans_ovale(s), w, h, R, PAD) for s in alice2.frames(a, v)], (ox * S + M, oy * S + M), True))
            # « alice1 » : un pied nu, tant que Tecky ne lui a pas rapporté sa chaussure (les retrouvailles)
            out.append((f"alice1/{a}/{v}", [render_svg(sans_ovale(s), w, h, R, PAD) for s in alice2.frames(a, v, True)], (ox * S + M, oy * S + M), True))
    for a, (_, fps, _) in farmer.ANIMS.items():          # le fermier Gaston, vu de face, pieds en (24, 60)
        out.append((f"farmer/{a}", [render_svg(sans_ovale(sv), farmer.W, farmer.H, R, PAD) for sv in farmer.frames(a)], (24 * S + M, 60 * S + M), True))
    for kind in npcs.KINDS:                             # le facteur et la voisine, vus de face, pieds en (24, 60)
        for a in npcs.ANIMS[kind]:
            out.append((f"{kind}/{a}", [render_svg(sans_ovale(sv), npcs.W, npcs.H, R, PAD) for sv in npcs.frames(kind, a)], (24 * S + M, 60 * S + M), True))
    for kind in villageois.KINDS:                       # les villageois, vus de face, pieds en (24, 60)
        for a in villageois.ANIMS[kind]:
            out.append((f"{kind}/{a}", [render_svg(sans_ovale(sv), npcs.W, npcs.H, R, PAD) for sv in villageois.frames(kind, a)], (24 * S + M, 60 * S + M), True))
    out.append(("item/letter", [render_svg(sv, 32, 32, R, PAD) for sv in npcs.letter_frames()], (32 + M, 32 + M), True))
    out.append(("port/balloon", [render_svg(sv, 32, 32, R, PAD) for sv in port.balloon_frames()], (16 * S + M, 16 * S + M), True))
    out.append(("port/toy", [render_svg(sv, 32, 32, R, PAD) for sv in port.toy_frames()], (16 * S + M, 16 * S + M), True))
    out.append(("ballon/relief", [render_svg(sv, 32, 32, R, PAD) for sv in port.balloon_relief()], (16 * S + M, 16 * S + M), True))
    # icônes des compteurs du HUD : le dessin du jeu à la taille du compteur (agrandir le sprite, réduit pour le
    # jeu, le rendait flou : vu par Christophe sur le compteur des petits hérissons)
    for n, sv, k0, k in (("hedgehog", herissons.frames("idle")[0], herissons.SCALE, 1.04), ("hen", hens.frames("hen", "idle")[0], hens.SCALE, 0.86),
                         ("cat_white", critters.frames("cat_white", "idle")[0], critters.SCALE["cat"], 0.89)):
        out.append((f"icone/{n}", [render_svg(icone(sans_ovale(sv), k0, k), 32, 32, R, PAD)], (16 * S + M, 28 * S + M), True))
    for a in herissons.ANIMS:                           # les bébés hérissons, de profil, pieds en (16, 28)
        out.append((f"hedgehog/{a}", [render_svg(sans_ovale(sv), 32, 32, R, PAD) for sv in herissons.frames(a)], (16 * S + M, 28 * S + M), True))
    for kind in critters.KINDS:                         # écureuil, chats : de profil vers la droite, pieds en (16, 28)
        for a in critters.anims(kind):
            out.append((f"{kind}/{a}", [render_svg(sans_ovale(sv), 32, 32, R, PAD) for sv in critters.frames(kind, a)], (16 * S + M, 28 * S + M), True))
    for kind in ducks.KINDS:                            # canards : de profil vers la droite, ligne d'eau en (16, 24)
        for a in ducks.anims(kind):
            out.append((f"{kind}/{a}", [render_svg(sv, 32, 32, R, PAD) for sv in ducks.frames(kind, a)], (16 * S + M, 24 * S + M), True))
    for kind in cows.KINDS:                             # vaches : de profil vers la droite, pieds en (32, 44)
        for a in cows.anims(kind):
            out.append((f"{kind}/{a}", [render_svg(sans_ovale(sv), 64, 48, R, PAD) for sv in cows.frames(kind, a)], (32 * S + M, 44 * S + M), True))
    for c in butterflies.COLORS:
        out.append((f"butterfly/{c}", [render_svg(sv, 24, 24, R, PAD) for sv in butterflies.frames(c)], (12 * S + M, 12 * S + M), True))
    for n in vehicles.VEHICLES:
        w, h, ox, oy = vehicles.cadre(n)
        out.append((f"vehicle/{n}", [render_svg(sv, w, h, R, PAD) for sv in vehicles.frames(n)], (ox * S + M, oy * S + M), True))
    for kind in hens.COLORS:
        for anim in hens.ANIMS:
            out.append((f"{kind}/{anim}/right", [render_svg(sans_ovale(s), 32, 32, R, PAD) for s in hens.frames(kind, anim)],
                        (16 * S + M, 28 * S + M), True))
    for n in items.ITEMS:
        out.append((f"item/{n}", [render_svg(s, 32, 32, R, PAD) for s in items.item_frames(n)], (32 + M, 32 + M), True))
    for n, (fn, size, _) in items.EFFECTS.items():
        o = (12 + M, 48 + M) if n == "bark" else (size + M, size + M)
        out.append((f"fx/{n}", [render_svg(s, size, size, R, PAD) for s in fn()], o, True))
    for n, fn, t in (("fleur", nature.sol_fleurs, nature.SOL_T), ("brins", nature.sol_brins, nature.SOL_T),      # détails
                     ("galet", nature.sol_galets, nature.SOL_T), ("nenuphar", nature.sol_nenuphars, nature.EAU_T),    # du sol
                     ("sousbois", nature.sol_sousbois, nature.BOIS_T), ("culture", nature.sol_cultures, nature.SOL_T)):
        out.append((f"sol/{n}", [render_svg(sv, t, t, R, PAD) for sv in fn()], (t // 2 * S + M, t // 2 * S + M), True))
    for n in sorted({v for noms, _ in nature.VARIANTES.values() for v in noms}):       # la nature et les bâtiments
        _, w, h, ox, oy = nature.cadre(n)
        out.append((f"decor/{n}", [nature.image(n, R)], (ox * S + M, oy * S + M), True))
    for n in decor.DECOR:
        if n in nature.VARIANTES:                                   # redessiné (nature, bâtiments, mobilier) : l'ancien
            continue                                                # dessin ne sert plus (l'éditeur montre le nouveau)
        w, h, ox, oy = decor.cadre(n)
        out.append((f"decor/{n}", [render_svg(sv, w, h, R, PAD) for sv in decor.svgs(n)], (ox * S + M, oy * S + M), True))
    for n in batiments.ECLAIRES:                                    # les fenêtres des bâtiments, allumées le soir
        _, w, h, ox, oy = nature.cadre("nuit_" + n)
        out.append((f"nuit/{n}", [nature.image("nuit_" + n, R)], (ox * S + M, oy * S + M), True))
    for n, fn in lisiere.DECOR.items():                             # la lisière : les tunnels de la grande route
        sp = fn()
        out.append((f"decor/{n}", [nature.rendre(sp, R)], (sp.pied[0] * S + M, sp.pied[1] * S + M), True))
    for n, ims in hud.all_sprites(R).items():
        key = "hud/" + n.replace("spr_hud_", "").replace("spr_", "")
        o = {"spr_hud_arrow": (40, 40), "spr_hud_arrow_icon": (22, 22)}.get(n, (0, 0))
        if n == "spr_title_logo":
            o = (ims[0].width // 2 // r, ims[0].height // 2 // r)
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
    """Range les images en étagères, de la plus haute à la plus basse. Aucune étagère ne franchit un multiple de PAGE
    (sa hauteur est celle de sa première image)."""
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
        if x == 0 and y // PAGE != (y + im.height - 1) // PAGE:      # l'étagère déborderait de la page : page suivante
            y = (y // PAGE + 1) * PAGE
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


def source_stamp():
    """Empreinte de tout ce dont dépendent les images x4 : les modules de dessin, et les tuiles composées (la carte)."""
    h = hashlib.sha1()
    for fn in sorted(f for f in os.listdir(ROOT) if f.endswith(".py")):
        h.update(open(os.path.join(ROOT, fn), "rb").read())
    h.update(json.dumps(COMPOSITES).encode())
    return h.hexdigest()[:10]


def pack_hd(entries, meta, height, width=2048):
    """Atlas net : les images de collect(HD), chacune à la place et dans le cadre de sa jumelle de l'atlas x2 (la
    méta ne change pas), puis l'ensemble découpé en pages de PAGE pixels x2 de haut."""
    big = Image.new("RGBA", (width * HD, height * HD), (0, 0, 0, 0))
    for key, ims, _, _ in entries:
        for i, im in enumerate(ims):
            x, y, w, h, dx, dy = meta[key]["f"][i]
            big.paste(im.crop((dx * HD, dy * HD, (dx + w) * HD, (dy + h) * HD)), (x * HD, y * HD))
    return [big.crop((0, p * PAGE * HD, big.width, min(big.height, (p + 1) * PAGE * HD)))
            for p in range(-(-height // PAGE))]


def build_hd(meta, height):
    """Écrit web/atlas_x4_N.png et web/tiles_x4.png, et rend ce que le jeu doit en savoir (HD_SRC). Rien n'est
    redessiné si les sources n'ont pas changé depuis la dernière fois (web/hd.json)."""
    stamp = source_stamp()
    info = os.path.join(WEB, "hd.json")
    try:
        old = json.load(open(info, encoding="utf-8"))
    except (OSError, ValueError):
        old = {}
    names = [f"atlas_x{S * HD}_{p}.png" for p in range(-(-height // PAGE))] + [f"tiles_x{S * HD}.png"]
    if not (old.get("stamp") == stamp and old.get("files") == names
            and all(os.path.exists(os.path.join(WEB, n)) for n in names)):
        pages = pack_hd(collect(HD), meta, height)
        for n, im in zip(names, pages + [tiles.tileset(S * HD, composites=COMPOSITES)]):
            im.save(os.path.join(WEB, n), optimize=True)
        json.dump({"stamp": stamp, "files": names}, open(info, "w", encoding="utf-8"))
        print("images x%d :" % (S * HD), ", ".join(f"{n} {os.path.getsize(os.path.join(WEB, n)) // 1024} Ko" for n in names))
    else:
        print("images x%d : à jour" % (S * HD))
    # ?v= : une page et ses images x4 vont ensemble (mêmes places dans l'atlas) ; jamais une vieille image en cache
    return {"k": HD, "page": PAGE, "atlas": [n + "?v=" + stamp for n in names[:-1]], "tiles": names[-1] + "?v=" + stamp,
            "files": names}


SAISON_Y = 1 << 20     # y d'un cadre de saison dans ATLAS : celui de l'image de la saison, décalé d'autant (game.js : blit())
SAISON_W = 1024        # largeur de l'image des sprites d'une saison, en pixels x2


def build_saisons(base, meta, avec_hd):
    """Les images des saisons que jouent les épisodes (episodes.json ; le printemps est dans la page) : le tileset
    redessiné avec la palette de la saison (saisons.py), et les sprites qui en changent — trouvés en redessinant
    tout l'atlas et en le comparant à celui du printemps (`base` : collect()). Fichiers à côté de la page :
    saison_<nom>_tiles.png, saison_<nom>_atlas.png (ces sprites seuls, rangés à part) et, avec les images nettes,
    leurs jumeaux x4. Rend { saison: ce que le jeu doit en savoir } (SAISONS de game.js : les adresses, et « meta »,
    les entrées d'ATLAS à remplacer, y décalés de SAISON_Y) et la liste des fichiers. Rien n'est redessiné si les
    sources n'ont pas changé (web/saisons.json)."""
    stamp = source_stamp()
    info = os.path.join(WEB, "saisons.json")
    try:
        old = json.load(open(info, encoding="utf-8"))
    except (OSError, ValueError):
        old = {}
    out, fichiers, garde = {}, [], {}
    printemps = {k: ims for k, ims, _, _ in base}
    for nom in dict.fromkeys(e["saison"] for e in episodes.charger()):
        if nom == "printemps":
            continue
        o = old.get(nom) or {}
        if not (o.get("stamp") == stamp and o.get("hd") == avec_hd
                and all(os.path.exists(os.path.join(WEB, n)) for n in o.get("files", []))):
            saisons.appliquer(nom)
            try:
                change = [e for e in collect()
                          if any(a.size != b.size or a.tobytes() != b.tobytes() for a, b in zip(e[1], printemps[e[0]]))]
                img, m = pack(change, width=SAISON_W)
                for k, v in m.items():                # mêmes cadres qu'au printemps : seules les couleurs changent
                    if v["o"] != meta[k]["o"] or [f[2:] for f in v["f"]] != [f[2:] for f in meta[k]["f"]]:
                        raise SystemExit(f"saison « {nom} » : le sprite {k} n'a plus la forme du printemps (ombres, "
                                         "lignes de contact et perchoirs sont ceux du printemps)")
                files = [f"saison_{nom}_tiles.png", f"saison_{nom}_atlas.png"]
                tiles.tileset(S, composites=COMPOSITES).save(os.path.join(WEB, files[0]), optimize=True)
                img.save(os.path.join(WEB, files[1]), optimize=True)
                hd = None
                if avec_hd:
                    pages = pack_hd([e for e in collect(HD) if e[0] in m], m, img.height, SAISON_W)
                    hd = [f"saison_{nom}_tiles_x{S * HD}.png"] + [f"saison_{nom}_atlas_x{S * HD}_{p}.png" for p in range(len(pages))]
                    tiles.tileset(S * HD, composites=COMPOSITES).save(os.path.join(WEB, hd[0]), optimize=True)
                    for n, im in zip(hd[1:], pages):
                        im.save(os.path.join(WEB, n), optimize=True)
            finally:
                saisons.appliquer()                   # (toujours revenir au printemps)
            for v in m.values():
                for f in v["f"]:
                    f[1] += SAISON_Y
            o = {"stamp": stamp, "hd": avec_hd, "files": files + (hd or []), "x2": files, "x4": hd, "meta": m}
            print(f"saison « {nom} » : {len(m)} sprites,", ", ".join(f"{n} {os.path.getsize(os.path.join(WEB, n)) // 1024} Ko" for n in o["files"]))
        else:
            print(f"saison « {nom} » : à jour")
        garde[nom] = o
        v = lambda n: n + "?v=" + stamp
        out[nom] = {"tiles": v(o["x2"][0]), "atlas": v(o["x2"][1]), "meta": o["meta"],
                    "hd": o["x4"] and {"tiles": v(o["x4"][0]), "atlas": [v(n) for n in o["x4"][1:]]}}
        fichiers += o["files"]
    json.dump(garde, open(info, "w", encoding="utf-8"))
    return out, fichiers


def preview(m, atlas, meta, tileset):
    e = m["edge"]
    o = e["r"] * TS                       # la marge de la lisière, autour de la carte
    img = Image.new("RGBA", (MW * TS + 2 * o, MH * TS + 2 * o))
    L = tiles.LARGEUR                     # (colonnes de l'image du tileset)
    tile = lambda idx: tileset.crop(((idx % L) * TS, (idx // L) * TS, (idx % L + 1) * TS, (idx // L + 1) * TS))
    alt = tiles.alternees()

    def look(idx, tx, ty):                # comme tileLook() de game.js : une variante du bord, tirée de la position
        a, bits = alt.get(idx // 16), idx % 16
        v = int(hash3(tx, ty, 61) * (len(a) + 1)) if a and 0 < bits < 15 else 0
        return a[v - 1] * 16 + bits if v else idx
    for i, idx in enumerate(m["ground"]):
        img.paste(tile(look(idx, i % MW, i // MW)), ((i % MW) * TS + o, (i // MW) * TS + o))
        if m["over"][i]:
            img.alpha_composite(tile(m["over"][i]), ((i % MW) * TS + o, (i // MW) * TS + o))
    for tx, ty, idx in e["ring"]:
        img.paste(tile(idx), (tx * TS + o, ty * TS + o))
    def cle(n, x, y):                     # comme decorKey() de game.js
        if n not in nature.VARIANTES:
            return "decor/" + n
        noms, tirage = nature.VARIANTES[n]
        return "decor/" + noms[tirage[int(hash3(round(x), round(y), 7) * len(tirage))]]
    things = [(cle(n, x, y), x, y, False) for n, x, y in m["decor"]]
    things += [(cle(n, x, y), x, y, f and n not in nature.VARIANTES) for n, x, y, f in e["decor"]]
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


def ecoute(game):
    """web/musique.html, la salle d'écoute : les morceaux de music.py joués par le séquenceur de game.js (sa
    section « musique chiptune »), pour les écouter un par un, essayer le passage d'une zone à l'autre et
    mesurer leurs niveaux ; et les bruitages (sa section « bruitages »), à comparer avec ceux d'avant la v2.
    À ouvrir depuis le disque ; elle n'est pas publiée."""
    a = game.index("/* ------------------------------------------------------------------ musique chiptune */")
    b = game.index("/* ------------------------------------------------------------------ ambiance sonore des zones */")
    tpl = open(os.path.join(SRC, "musique.template.html"), encoding="utf-8").read()
    page = tpl.replace("/*__SONGS__*/", "const SONGS = " + json.dumps(music.songs(), separators=(",", ":")) + ";")
    c = game.index("/* ------------------------------------------------------------------ bruitages */")
    page = page.replace("/*__SFX__*/", game[c:a]).replace("/*__MUSIC__*/", game[a:b])
    open(os.path.join(WEB, "musique.html"), "w", encoding="utf-8").write(page)


def main():
    os.makedirs(WEB, exist_ok=True)
    COMPOSITES.clear()
    cartes = {}
    for nom in carte.noms():                          # chaque carte du jeu ; puis retour à celle du monde
        charger_carte(nom)
        cartes[nom] = build_map()
    # les cartes changées par un épisode (cartes/<épisode>/<nom>.json) : la page n'en garde que ce qui diffère de
    # la carte de base (game.js : SURCHARGES, carteOf())
    surcharges = {}
    for ep, nom in carte.surcharges():
        charger_carte(nom, ep)
        v = build_map()
        surcharges.setdefault(ep, {})[nom] = {k: x for k, x in v.items() if x != cartes[nom][k]}
    for nom, c in list(cartes.items()) + [(f"{nom} ({ep})", dict(cartes[nom], **d)) for ep, q in surcharges.items() for nom, d in q.items()]:
        for t, vers, arrivee in c["passages"]:
            if vers not in cartes or not 0 <= arrivee < len(cartes[vers]["roadTunnels"]):
                raise SystemExit(f"carte « {nom} » : le passage du tunnel {t} mène à « {vers} », tunnel {arrivee}, qui n'existe pas")
    pb = episodes.valider(episodes.charger())         # les épisodes : leurs cartes existent et se rejoignent
    if pb:
        raise SystemExit("episodes.json : " + " ; ".join(pb))
    charger_carte()
    m = cartes[carte.MONDE]
    base = collect()
    atlas, meta = pack(base)
    atlas.save(os.path.join(WEB, "atlas.png"), optimize=True)
    tileset = tiles.tileset(S, composites=COMPOSITES)   # eau unie : le jeu anime ses vaguelettes
    tileset.save(os.path.join(WEB, "tiles.png"), optimize=True)
    preview(m, atlas, meta, tileset)
    hd = None if "--sans-hd" in sys.argv else build_hd(meta, atlas.height)
    sais, sais_files = build_saisons(base, meta, hd is not None)
    tpl = open(os.path.join(SRC, "index.template.html"), encoding="utf-8").read()
    game = open(os.path.join(SRC, "game.js"), encoding="utf-8").read()
    import base64
    b64 = lambda p: "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
    data = ("const ATLAS_SRC = \"" + b64(os.path.join(WEB, "atlas.png")) + "\";\n"
            "const TILES_SRC = \"" + b64(os.path.join(WEB, "tiles.png")) + "\";\n"
            "const ATLAS = " + json.dumps(meta, separators=(",", ":")) + ";\n"
            # images nettes, à côté de la page (game.js : loadHD) ; null : construit sans elles
            "const HD_SRC = " + json.dumps(hd and {k: v for k, v in hd.items() if k != "files"}, separators=(",", ":")) + ";\n"
            # les images des saisons, à côté de la page elles aussi (game.js : askSeason) ; le printemps est dans la page
            "const SAISONS = " + json.dumps(sais, separators=(",", ":")) + ";\n"
            "const SONGS = " + json.dumps(music.songs(), separators=(",", ":")) + ";\n"
            # les textes du jeu, par langue (game.js : txt()) ; la source est textes/fr.json
            "const TEXTES = " + json.dumps({"fr": json.load(open(os.path.join(ROOT, "textes", "fr.json"), encoding="utf-8"))},
                                           separators=(",", ":"), ensure_ascii=False) + ";\n"
            # les données du jeu, puis celles de chaque carte (game.js : MAP = la carte courante, qui hérite de JEU)
            "const JEU = " + json.dumps(build_jeu(), separators=(",", ":"), ensure_ascii=False) + ";\n"
            "const CARTES = " + json.dumps(cartes, separators=(",", ":"), ensure_ascii=False) + ";\n"
            # ce qu'un épisode change à une carte : { épisode: { carte: les données qui diffèrent } }
            "const SURCHARGES = " + json.dumps(surcharges, separators=(",", ":"), ensure_ascii=False) + ";\n"
            # les épisodes, dans l'ordre où ils s'ouvrent (game.js : episode, EP())
            "const EPISODES = " + json.dumps(episodes.charger(), separators=(",", ":"), ensure_ascii=False) + ";\n"
            "const VERSION = " + json.dumps(version(), ensure_ascii=False) + ";\n")
    html = tpl.replace("/*__DATA__*/", data).replace("/*__GAME__*/", game)
    open(os.path.join(WEB, "index.html"), "w", encoding="utf-8").write(html)
    ecoute(game)
    print("atlas", atlas.size, "| html", len(html) // 1024, "Ko")
    build_standalone(data, game, (hd["files"] if hd else []) + sais_files)
    check_placement()


def check_placement():
    """Vérifie (avec Node.js, s'il est installé) que rien n'est dans l'eau ou dans un obstacle."""
    import shutil
    import subprocess
    if not shutil.which("node"):
        print("(Node.js absent : vérification des placements ignorée)")
        return
    # chaque carte : celle du monde, puis les annexes ; puis chaque carte changée par un épisode
    for ep, nom in [(None, n) for n in carte.noms()] + carte.surcharges():
        r = subprocess.run(["node", os.path.join(SRC, "check_placement.js"), os.path.join(WEB, "index.html"), "--carte", nom]
                           + (["--episode", ep] if ep else []), capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())
        if r.returncode:
            raise SystemExit(f"Corrige les placements signalés dans {os.path.relpath(carte.surcharge(nom, ep) if ep else carte.chemin(nom), ROOT)} "
                             "(éditeur de carte : python3 editeur.py)")


def build_standalone(data, game, hd_files=()):
    """Version autonome à servir soi-même : plein écran, installable comme une app. hd_files : les images x4 et
    celles des saisons, copiées à côté de la page."""
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
    for fn in os.listdir(out):                         # images x4 et de saison d'une construction précédente
        if ("_x4" in fn or fn.startswith("saison_")) and fn not in hd_files:
            os.remove(os.path.join(out, fn))
    for fn in hd_files:
        shutil.copy(os.path.join(WEB, fn), os.path.join(out, fn))
    os.chmod(os.path.join(out, "serve.sh"), 0o755)
    shutil.copy(os.path.join(SRC, "LISEZMOI.txt"), os.path.join(out, "LISEZMOI.txt"))
    print("version autonome ->", out)


if __name__ == "__main__":
    main()
