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
# 96 x 64 tuiles. Au nord de la grande route : la niche de Tecky, le village, la ferme. Au sud : la campagne, la zone
# industrielle (le dépôt, et son port au bord de la rivière), les prés de la ferme. Une rivière coupe toute la carte
# (un seul pont, côté ferme) ; au-delà, le parc au sud-ouest, où Alice se cache, et la forêt au sud-est.
MW, MH = 96, 64


def corner_grid():
    g = [["grass"] * (MW + 1) for _ in range(MH + 1)]

    def paint(t, x0, y0, x1, y1):
        for y in range(max(0, y0), min(MH, y1) + 1):
            for x in range(max(0, x0), min(MW, x1) + 1):
                g[y][x] = t

    # campagne nord-ouest
    paint("dirt", 3, 4, 4, 17)          # chemin depuis la niche, jusqu'à la route
    paint("dirt", 4, 7, 14, 8)          # vers l'est
    paint("water", 8, 1, 11, 4)         # étang
    # ruisseau qui sépare la campagne du village (on passe par la route)
    paint("water", 25, 0, 26, 9)
    paint("water", 24, 2, 27, 5)
    # route principale
    paint("road", 0, 18, MW, 21)
    # village
    paint("sidewalk", 28, 17, 56, 17)
    paint("paving", 31, 3, 54, 10)
    paint("paving", 43, 10, 45, 17)        # ruelle de la place jusqu'au trottoir, entre les maisons de la rue
    # campagne sud-ouest : le chemin descend jusqu'à la rivière (barque, pas de pont)
    paint("dirt", 6, 23, 7, 42)
    paint("dirt", 7, 26, 14, 27)
    paint("dirt", 7, 35, 18, 36)            # au bord de l'eau : un sentier vers la mare aux canards
    paint("water", 19, 33, 23, 37)
    paint("dirt", 14, 7, 21, 8)             # jardin de la niche : le chemin continue vers l'est
    paint("water", 1, 24, 4, 28)
    # zone industrielle : le dépôt (x 30..56) et, en dessous, le port au bord de la rivière (x 30..64)
    paint("sidewalk", 30, 22, 56, 22)
    paint("concrete", 30, 23, 56, 30)
    paint("concrete", 30, 30, 64, 40)
    paint("road", 46, 22, 47, 23)
    # ferme (nord-est) : cour en terre, chemin vers la route, champs labourés
    paint("dirt", 66, 5, 78, 10)
    paint("dirt", 71, 10, 72, 17)          # (s'arrête au bord de la route : rien sous le passage piéton)
    paint("field", 59, 2, 64, 9)
    paint("field", 81, 2, 93, 9)
    paint("field", 68, 24, 76, 29)          # au sud de la route : le champ, à côté du verger
    paint("water", 86, 24, 90, 27)          # mare
    paint("dirt", 79, 22, 81, 41)           # chemin de la route au pont
    # rivière d'est en ouest ; le pont (BRIDGES) la franchit en x 63..65
    paint("water", 0, 42, MW, 45)
    # forêt (sud-est) : sous-bois, sentier sinueux du pont vers le parc, clairière et recoins à l'est
    paint("forest", 56, 47, MW, MH)
    paint("dirt", 79, 46, 81, 51)
    paint("dirt", 66, 49, 81, 51)
    paint("dirt", 66, 49, 68, 57)
    paint("dirt", 58, 55, 68, 57)
    paint("dirt", 81, 55, 88, 56)
    paint("dirt", 60, 49, 66, 50)           # recoin ouest (trésor)
    paint("dirt", 88, 55, 93, 56)           # vers la chaussure d'Alice et le recoin est
    paint("dirt", 92, 56, 93, 60)
    paint("grass", 73, 58, 79, 62)          # clairière de Maman Piquette (la maman hérisson)
    paint("dirt", 67, 57, 68, 59)           # et son sentier, depuis le chemin ouest
    paint("dirt", 67, 58, 73, 59)
    # parc (sud-ouest) : allée, place de la fontaine, aire de jeux (séparée de l'allée par l'herbe)
    paint("paving", 13, 55, 54, 56)
    paint("paving", 24, 50, 36, 60)
    paint("dirt", 3, 51, 11, 61)
    return g


# pont : coins (x0, y0, x1, y1) qui ne sont plus de l'eau, sous le tablier du décor « bridge »
BRIDGES = [(79, 41, 81, 46)]


DECOR = [
    # campagne nord-ouest
    ("doghouse", 3.5, 3.2),
    ("tree", 1, 1.4), ("tree", 6.5, 1.2), ("tree", 13.5, 1.6), ("tree", 1.2, 7), ("tree", 14.8, 5.2),
    ("tree", 7.2, 16.8), ("tree", 12.8, 4.3),
    ("bush", 5.8, 3.4), ("bush", 12.2, 1.1), ("bush", 0.8, 16.6), ("bush", 23.5, 9.6),
    ("rock", 7.6, 5.3), ("rock", 23.4, 3),
    ("hay", 10.5, 9.8), ("hay", 11.7, 10.2), ("hay", 13, 9.6),
    ("signpost", 5.6, 17.1),
    # berges du ruisseau
    ("tree", 28.5, 1.5), ("bush", 28.2, 7.4),
    # route
    ("road_sign", 2.5, 17.35), ("road_sign", 29.2, 22.1), ("cone", 24.6, 20.7), ("cone", 25.5, 20.7),
    # village
    ("house_red", 33.5, 3.4), ("house_blue", 46.5, 3.4), ("house_red", 51.5, 3.4),
    ("tree", 31.3, 9.4), ("tree", 54.6, 9.4), ("tree", 55, 2.4),
    ("bench", 36, 8.4), ("bench", 49, 8.4), ("flower_pot", 46.5, 6.4), ("flower_pot", 33.3, 6.2),
    ("lamppost", 32.5, 17.35), ("lamppost", 46.5, 17.35), ("lamppost", 52.5, 17.35),
    ("mailbox", 35.2, 17.35), ("hedge", 28, 9.8), ("hedge", 29, 9.8), ("hedge", 28, 4), ("hedge", 29, 4),
    # jardin de la niche (à l'est du pré)
    ("tree", 17.5, 1.6), ("tree", 21.5, 3.6), ("tree", 18.2, 13.6), ("tree", 22.6, 11.8), ("tree", 1.4, 14.2),
    ("tree", 12.5, 13.8), ("bush", 16.5, 5.8), ("bush", 21.6, 9.6), ("bush", 9.4, 14.6), ("bush", 15.4, 12.0),
    ("rock", 19.4, 5.4), ("bench", 18.8, 10.2), ("flower_pot", 17.0, 10.0), ("flower_pot", 20.6, 10.0),
    # village : une maison de plus sur la place, la fontaine, la rue (deux maisons, la ruelle entre elles)
    ("house_red", 40.0, 3.4), ("fountain", 42.5, 7.8), ("flower_pot", 39.6, 6.2),
    ("house_blue", 38.6, 15.6), ("house_red", 49.6, 15.6), ("tree", 31.2, 14.6), ("tree", 55.0, 14.8),
    ("hedge", 41.6, 14.6), ("hedge", 46.0, 14.6), ("flower_pot", 41.2, 16.2), ("flower_pot", 47.8, 16.2),
    ("bench", 35.2, 12.4), ("bench", 52.6, 12.4),
    # zone industrielle
    ("container_blue", 42.0, 26.6), ("barrel_red", 44.8, 27.6), ("crate", 40.6, 29.0),
    ("warehouse", 34, 28), ("warehouse", 51.5, 28.2), ("container", 33.5, 24.9), ("container", 54.3, 29.9),
    ("barrel_blue", 37.2, 25.6), ("barrel_red", 37.9, 25.8), ("barrel_blue", 49.4, 25),
    ("crate", 30.9, 28.6), ("crate", 31.6, 29.4), ("pallet", 47.2, 28.9), ("pallet", 55.3, 25.6),
    ("cone", 37.8, 23.9),
    # le port, au bord de la rivière sous le dépôt : chariot élévateur, camion de livraison, parc à conteneurs sous le
    # portique, cabane du gardien, voie ferrée le long du quai (Titine), bittes d'amarrage, péniche
    ("forklift", 35.8, 33.4), ("crate", 31.8, 31.6), ("pallet", 31.9, 35.2), ("goal_net", 40.0, 35.2),
    ("truck", 46.5, 32.6),
    ("container_stack", 51.3, 35.6), ("container_green", 54.3, 35.6), ("crane", 52.8, 36.1),
    ("guard_hut", 61.9, 32.4), ("barrel_blue", 63.2, 34.6), ("barrel_red", 57.6, 31.3),
    ("lamppost", 43.0, 31.4), ("lamppost", 60.5, 38.0),
    ("bollard", 34.5, 40.9), ("bollard", 40.5, 40.9), ("bollard", 46.5, 40.9), ("bollard", 52.5, 40.9),
    ("bollard", 58.5, 40.9), ("barge", 44, 43.8),
    ("buffer_stop", 31.25, 38.7), ("buffer_stop", 63.75, 38.7),           # bouts de la voie (TRACK)
    # campagne sud-ouest
    ("tree", 0.9, 22.8), ("tree", 9.8, 23.3), ("tree", 23.8, 23.8), ("tree", 3, 29.8), ("tree", 12.2, 29.6),
    ("tree", 26.8, 28.4), ("bush", 5.2, 22.6), ("bush", 25.3, 25.8), ("bush", 9.2, 29.4),
    ("hay", 12.2, 24.7), ("hay", 13.4, 25), ("rock", 27.6, 23.6),
    ("signpost", 7.3, 22.6),
    # campagne, au bord de l'eau : la mare aux canards, un petit bois, du foin
    ("reeds", 18.6, 33.4), ("reeds", 23.4, 36.8), ("reeds", 22.6, 32.8),
    ("tree", 11.5, 32.4), ("tree", 14.6, 31.8), ("tree", 2.4, 33.2), ("tree", 25.8, 31.4), ("tree", 27.4, 38.6),
    ("tree", 3.4, 38.6), ("tree", 13.0, 39.4), ("tree", 25.4, 34.8), ("bush", 9.6, 31.4), ("bush", 16.6, 38.6),
    ("bush", 22.4, 39.6), ("bush", 1.4, 36.4), ("hay", 11.6, 37.4), ("hay", 12.9, 37.7), ("rock", 17.2, 31.4),
    # bord de la rivière, au bout du chemin : barque, roseaux, panneau « pas de pont ici »
    ("boat", 6.6, 43.7), ("reeds", 4.6, 41.8), ("reeds", 9.2, 41.9), ("reeds", 2.2, 41.7), ("signpost", 8.8, 40.8),
    ("tree", 1.2, 41.2), ("bush", 11.5, 41), ("tree", 24, 41.3), ("reeds", 28.5, 41.8), ("bush", 34, 41.2),
    ("reeds", 69, 41.8), ("bush", 66, 41.2),
    ("reeds", 85, 41.8), ("tree", 91, 41.3), ("reeds", 94.5, 41.9),

    # ================= FERME (nord-est)
    ("barn", 72, 4.9), ("chicken_coop", 76.8, 6.4), ("lamppost", 69.3, 5.1),
    ("tractor", 68, 8.7), ("hay", 66.8, 5.6), ("hay", 68, 6), ("hay", 77.5, 4.2),
    ("scarecrow", 86.5, 6), ("scarecrow", 61.5, 5.6),
    ("tree", 57.5, 2), ("tree", 65.5, 1.3), ("tree", 79, 1.3), ("tree", 94.6, 1.6), ("tree", 57.5, 16.8),
    ("tree", 94.8, 16.6), ("bush", 79.6, 16.6), ("bush", 65, 16.5), ("rock", 82, 16.8),
    ("signpost", 69.9, 17.2),
    # au nord de la route, entre la cour et la route
    ("tree", 60.4, 14.6), ("tree", 64.8, 13.0), ("tree", 90.2, 13.6), ("hay", 86.4, 14.2), ("hay", 87.6, 14.5),
    # les prés de la ferme, au bord de la rivière : foin, arbres, quelques poules
    ("tree", 68.5, 32.6), ("tree", 74.4, 34.0), ("tree", 85.6, 32.8), ("tree", 93.6, 34.4), ("tree", 88.8, 38.8),
    ("bush", 71.0, 38.6), ("bush", 84.0, 36.4), ("bush", 95.0, 31.6), ("hay", 75.6, 37.2), ("hay", 76.8, 37.5),
    ("rock", 90.6, 36.0),
    # au sud de la route : verger, champ, mare, chemin du pont
    # le verger : des pommiers en rangées, et au milieu, la petite clairière où Iris a son panier
    *[("apple_tree", x, y) for y in (24.0, 29.2) for x in (58.0, 60.4, 62.8, 65.2)],
    ("apple_tree", 58.0, 26.6), ("apple_tree", 65.2, 26.6), ("dog_bed", 61.6, 26.95), ("apple_crate", 66.7, 28.6),
    ("tree", 92.5, 23.6), ("tree", 94.5, 28.6), ("bush", 77.6, 23.4), ("bush", 83.4, 29.3),
    ("reeds", 85.6, 24.6), ("reeds", 90.6, 27.4), ("hay", 77.8, 27.4), ("scarecrow", 72, 27.4),
    ("signpost", 78, 40.6),
    ("bridge", 80, 46),

    # ================= FORÊT (sud-est)
    ("tree", 68.4, 62.8), ("tree", 77.2, 63.4), ("tree", 62.4, 53.2), ("tree", 74.4, 53.2),
    ("stump", 69.8, 52.6), ("stump", 83.6, 58.2), ("stump", 60.6, 58.6), ("log", 75.6, 56.8), ("log", 89.4, 51.6),
    ("mushrooms", 70.4, 54.4), ("mushrooms", 85.8, 52.8), ("mushrooms", 63.2, 58), ("mushrooms", 92.2, 58.6),
    ("mushrooms", 78.8, 49), ("fern", 65.4, 53.6), ("fern", 76.4, 51.6), ("fern", 82.2, 54.2), ("fern", 59.4, 54),
    ("fern", 87.6, 62.6), ("signpost", 69.2, 48.6),
    ("leaf_nest", 77.9, 59.4), ("mushrooms", 74.2, 61.6), ("stump", 78.6, 62.2),       # clairière de Maman Piquette

    # ================= PARC (sud-ouest), Alice dans la cabane
    ("playhouse", 5, 53.3), ("slide", 9, 53.6), ("swing", 5.6, 58.4), ("sandbox", 9.6, 60.4),
    ("fountain", 30, 55.9), ("bench", 26, 51.9), ("bench", 34, 51.9), ("bench", 26, 59.9), ("bench", 34, 59.9),
    ("flower_pot", 24.6, 50.6), ("flower_pot", 35.6, 50.6), ("flower_pot", 24.6, 60.6), ("flower_pot", 35.6, 60.6),
    ("lamppost", 13, 54.7), ("lamppost", 47, 54.7), ("lamppost", 53, 57.6),
    ("tree", 2, 47.6), ("tree", 8, 47.2), ("tree", 14, 47.6), ("tree", 46.6, 47.6), ("tree", 52.6, 47.2),
    ("tree", 49.4, 51.4), ("tree", 13.2, 63.4), ("tree", 49.6, 62.6), ("tree", 1.6, 62.8), ("tree", 54.4, 62.8),
    ("bush", 12.4, 50.2), ("bush", 47.6, 59.4), ("bush", 52.2, 51.6), ("bush", 2.2, 50.2),
    ("bush", 54.6, 53.6), ("bush", 54.6, 58.6), ("signpost", 52.6, 54.4),
    ("tree", 49.2, 54.2), ("tree", 51.8, 59.6), ("tree", 46.2, 62.6), ("tree", 9, 49.6), ("bush", 46.4, 49.8),
    ("bush", 50.2, 61.6), ("bush", 12.6, 62.2), ("flower_pot", 14.4, 54.2), ("flower_pot", 14.4, 58.2),
    ("bench", 51, 49.9), ("tree", 32.2, 63.4), ("bush", 28.4, 47.4), ("bush", 35, 47.6),
    ("tree", 41.0, 48.4), ("tree", 44.6, 61.6), ("bush", 40.2, 52.6), ("bench", 42.6, 58.4),
]
for x in range(9, 24):                                # pré de la niche, le long de la route
    DECOR.append(("fence_wood_h", x, 17.25))
for x in list(range(30, 46)) + list(range(48, 56)):   # dépôt, le long du trottoir (portail : 46..48)
    DECOR.append(("fence_metal_h", x, 23.3))
for x in range(57, 64):                               # entre le verger de la ferme et le port
    DECOR.append(("fence_metal_h", x, 30.3))
for x in range(31, 64):                               # voie ferrée du quai
    DECOR.append(("rail", x, 38.6))
for x in range(8, 24):                                # champs de la campagne, le long de la route
    DECOR.append(("fence_wood_h", x, 22.35))
for x in list(range(80, 86)) + list(range(88, 93)):   # clôture du grand champ, avec une barrière ouverte
    DECOR.append(("fence_wood_h", x, 10.3))
for y in range(23, 30):                               # entre le dépôt et le verger de la ferme
    DECOR.append(("fence_metal_v", 56.6, y + 1))
for y in range(30, 40):                               # entre le port et les prés de la ferme
    DECOR.append(("fence_metal_v", 64.6, y + 1))
# enclos des poules (quête du fermier) : clôture en bois autour du poulailler, barrière ouverte au sud
PEN = (75, 5.2, 80, 9.0)            # lignes de clôture, en tuiles : x0, y0, x1, y1
PEN_GATE = (76, 78)                 # ouverture dans la clôture du bas
for x in range(PEN[0], PEN[2]):
    DECOR.append(("fence_wood_h", x, PEN[1]))
    if not PEN_GATE[0] <= x < PEN_GATE[1]:
        DECOR.append(("fence_wood_h", x, PEN[3]))
for y in (6.2, 7.2, 8.2, PEN[3]):
    DECOR.append(("fence_wood_v", PEN[0], y))
    DECOR.append(("fence_wood_v", PEN[2], y))
FARMER = (73.9, 8.4)                # le fermier Gaston, contre la clôture ouest de l’enclos
POSTMAN = (34.4, 16.45)             # Marcel le facteur, près de la boîte aux lettres du village
NEIGHBOR = (48.4, 4.95)             # Mamie Rose, devant sa maison bleue
POMPON = (32.6, 29.6)               # son chat, caché entre les caisses, près des entrepôts
LEON = (37.6, 34.0)                 # Léon, le cariste du port, à côté de son chariot élévateur
GOAL = (40.0, 35.2)                 # son grand filet (pied du cadre avant, ouverture vers le bas)
# ses cinq gros ballons, qui ont roulé partout dans la zone industrielle (une couleur chacun, port.BALL_COLORS)
BALLS = [(38.6, 37.6), (44.4, 34.6), (57.2, 33.6), (54.2, 27.0), (50.6, 29.4)]
IRIS = (61.6, 26.9)                 # Iris, le vieux Jack Russell, sur son panier au milieu du verger
# ses trois jouets (port.TOYS : canard, anneau, corde), cachés dans les prés de la ferme : près de la mare, dans le
# champ, dans la pâture au bord de la rivière
TOYS = [(86.0, 29.8), (74.4, 25.2), (69.4, 37.0)]
TRACK = (31.25, 63.75, 38.6)        # voie de Titine, le petit train : x des heurtoirs ouest et est, y des rails
PIQUETTE = (76.4, 60.3)             # Maman Piquette, la maman hérisson, dans sa clairière (forêt)
CLEARING = (72.6, 57.6, 79.6, 62.6)  # la clairière : pas de sapins
# ses trois petits, cachés sous des fougères (juste à côté, un peu derrière : on voit dépasser leur museau)
BABIES = [(65.7, 53.48), (82.5, 54.08), (87.9, 62.48)]
# les lettres du facteur, emportées par le vent : campagne, village, zone industrielle, près de la niche
LETTERS = [(26.4, 16.8), (30.0, 6.6), (51.6, 9.2), (47.0, 29.6), (23.2, 27.4)]   # avant le village, … , campagne
# terriers sous les grillages : Tecky passe d'une extrémité à l'autre (raccourcis)
TUNNELS = [((56.0, 27.0), (57.25, 27.0)),        # dépôt <-> verger de la ferme
           ((52.5, 22.75), (52.5, 24.0)),        # trottoir <-> zone industrielle
           ((14.5, 16.75), (14.5, 17.95)),       # pré de la niche <-> grande route
           ((83.5, 9.75), (83.5, 10.95))]        # grand champ de la ferme <-> pré, vers la route
for a, b in TUNNELS:
    for x, y in (a, b):
        DECOR.append(("burrow", x, y))

ITEMS = [
    ("bone", 6, 7.5), ("bone", 12, 23.6), ("bone", 36.5, 7.2), ("bone", 31.5, 25.8), ("bone", 27.5, 17.3),
    ("sausage", 14.5, 28.5), ("sausage", 53.5, 25.2),
    ("medal", 1.4, 9.4), ("medal", 54.6, 24.3),
    ("squeaky", 9.5, 6.2), ("squeaky", 2.5, 22.9), ("squeaky", 52.8, 6.0),
    ("ball", 6.3, 5.4), ("ball", 23, 6.3), ("ball", 27.5, 26), ("ball", 33, 19.8), ("ball", 54.2, 7.0),
    # ferme
    ("bone", 69.6, 7.4), ("bone", 82.4, 27.6), ("sausage", 94.4, 4.6), ("medal", 94.2, 25.6),
    ("squeaky", 88.4, 28.6), ("ball", 66.8, 23.0), ("ball", 75, 17.3),
    # forêt
    ("bone", 79.6, 52.6), ("bone", 67, 60.4), ("sausage", 90.4, 54.6), ("medal", 59.2, 63),
    ("squeaky", 85.6, 57.2), ("ball", 72.6, 55.8),
    # parc
    ("bone", 46.4, 57.6), ("sausage", 28.4, 62.4), ("squeaky", 32.6, 49.2), ("ball", 12.6, 58.6),
    ("medal", 51.6, 60.6),
    # nouveaux coins : jardin de la niche, campagne au bord de l'eau, prés de la ferme, village, parc
    ("bone", 20.5, 6.6), ("squeaky", 17.2, 15.2), ("bone", 9.4, 34.0), ("ball", 25.4, 37.0), ("sausage", 4.8, 31.2),
    ("bone", 72.4, 35.8), ("ball", 92.4, 39.2), ("squeaky", 45.6, 12.6), ("ball", 40.0, 61.4),
    # indices d'Alice : barrette à la ferme, chaussure dans la clairière de la forêt, doudou au parc
    ("hairclip", 86.6, 3.6), ("shoe", 89.6, 57.2), ("plush", 37.6, 53.4),
]
# zones calmes (x0, y0, x1, y1 en tuiles) : comme les villes d'un RPG, aucun chien hostile n'y vit ni n'y poursuit
# Tecky. Le village, au nord de la grande route, et la cour de la ferme (Gaston, l'enclos).
CALM = [(27.6, 0, 56.4, 18), (65, 2.6, 81.4, 17.4),   # le village jusqu'au bord de la route (trottoir compris), la ferme
        (33.4, 30.6, 42.6, 36.6), (56.8, 22.4, 67.4, 30.2),   # au port, le coin de Léon ; le verger d'Iris
        CLEARING]                                     # la clairière de Maman Piquette
ENEMIES = [
    # le 1er roquet est assez loin de la niche pour ne pas attaquer dès la fin de l'intro
    ("roquet", 12, 8.8), ("roquet", 14, 3.5), ("roquet", 10.5, 25.2), ("roquet", 47.5, 24.0),   # (ce dernier, aux entrepôts)
    ("bouledogue", 27.6, 22.9), ("bouledogue", 23.5, 28.2),
    ("molosse", 49.5, 26.2),
    # ferme : les chiens de berger gardent les prés (la cour, elle, est une zone calme)
    ("berger", 61.6, 6.4), ("berger", 82, 25.5), ("berger", 88, 6.5), ("bouledogue", 70.6, 39.0), ("roquet", 76.5, 29),
    # forêt
    ("roquet", 73, 50), ("roquet", 85, 55.6), ("bouledogue", 62.5, 56.4), ("molosse", 90.5, 56.6),
    # parc
    ("roquet", 34.5, 53.2), ("bouledogue", 23, 57.6), ("berger", 49, 56),
    # nouveaux coins (à la fin : les autres gardent leur numéro) : le port, la campagne au bord de l'eau, les prés
    ("bouledogue", 46.6, 36.6), ("roquet", 24.0, 32.6), ("berger", 88.0, 34.4),
]
# trésors enterrés : au centre de la tuile des traces de pattes (scintillement et trou creusé s'y alignent)
# grande route : passages piétons (première des deux tuiles) et circulation (voie 0 en haut vers l'ouest,
# voie 1 en bas vers l'est ; x de départ en tuiles). Les véhicules s'arrêtent aux passages quand Tecky y est.
CROSSINGS = (10, 50, 71, 79)
# massifs de fleurs au sol (tuiles) : dessinés en détail sur le sol, et perchoirs des papillons
FLOWER_BEDS = ((7, 4), (23, 8), (3, 23), (10, 5), (6, 9), (24, 26), (59, 25), (63, 25), (93, 21), (84, 57),
               (14, 52), (46, 52), (14, 59), (47, 61), (51, 49), (2, 56), (12, 62), (32, 47), (52, 61), (27, 62),
               (6, 49), (8, 62),
               (18, 4), (21, 7), (16, 10), (10, 38), (26, 32), (4, 35), (70, 36), (92, 33), (36, 13), (53, 13), (40, 50))
TRAFFIC = [("car_red", 0, 10), ("bus", 0, 56), ("car_yellow", 0, 82),
           ("car_blue", 1, 28), ("van", 1, 66), ("car_green", 1, 88)]
# papillons (couleur, coin où ils volettent) : surtout au parc, mais aussi près de la niche, sur la place du village,
# dans la campagne sud-ouest, au verger de la ferme et dans la clairière de la forêt
BUTTERFLIES = [("yellow", 30.5, 47.8), ("blue", 34.8, 51.6), ("pink", 13, 56), ("orange", 46, 59),
               ("blue", 50, 50), ("yellow", 6.5, 60.5), ("pink", 7.5, 49.6),
               ("yellow", 9, 5.6), ("orange", 6, 8.6),
               ("pink", 36, 6.4), ("blue", 49, 5.4),
               ("blue", 4.5, 22.8), ("yellow", 22.6, 25.8),
               ("orange", 63.6, 25.4), ("yellow", 59.6, 25.4),
               ("blue", 85.5, 56.6),
               ("orange", 19.5, 5.5), ("pink", 16.5, 10.6), ("yellow", 10.5, 38.4), ("blue", 26.0, 32.6),
               ("orange", 70.5, 36.4), ("pink", 53.5, 13.4)]
# poules (animées : elles picorent, se promènent, et s'enfuient quand Tecky aboie). Les cinq premières se sont
# échappées de l'enclos : c'est la quête du fermier (quest = 1) ; les deux du sud de la route vivent leur vie.
HENS = [("hen", 69.6, 9.6, 1), ("hen_white", 71.2, 7.0, 1), ("hen", 82.6, 6.8, 1), ("hen_white", 74.8, 17.0, 1),
        ("hen", 65.6, 7.6, 1), ("hen_white", 82.6, 24.4, 0), ("hen", 81.4, 26.2, 0),
        ("hen", 73.6, 33.6, 0), ("hen_white", 75.2, 34.4, 0)]
# canards (espèce, x, y en tuiles, famille) : une même famille = la cane et ses canetons, qui la suivent en file
DUCKS = [("duck_f", 9.9, 2.4, 1), ("duckling", 9.4, 2.55, 1), ("duckling", 9.0, 2.7, 1), ("duckling", 8.6, 2.85, 1),
         ("duck", 88.6, 25.4, 0), ("duck_f", 87.6, 25.9, 0),
         ("duck", 46.5, 43.4, 0), ("duck_f", 47.6, 43.8, 0), ("duck", 64.0, 43.6, 0), ("duck", 2.6, 26.0, 0),
         ("duck", 20.4, 34.8, 0), ("duck_f", 21.6, 35.4, 0)]
# les vaches du grand pré de la campagne (cows.py) : la pie noire, la pie rouge et son veau
COWS = [("cow_bw", 19.5, 25.4), ("cow_brown", 21.2, 29.6), ("calf", 19.0, 30.0)]
# petites bêtes que Tecky peut poursuivre : écureuils (forêt, parc) qui grimpent aux arbres, chats (village, zone
# industrielle) qui sautent sur les toits et les conteneurs
CRITTERS = [("squirrel", 73.4, 53.9), ("squirrel", 82.2, 52.9), ("squirrel", 64.6, 60.4), ("squirrel", 87.2, 60.4),
            ("squirrel", 10.6, 48.6), ("cat", 37.6, 9.0), ("cat_black", 47.6, 25.4), ("cat", 52.6, 34.0),
            ("squirrel", 13.4, 33.6)]
DIG = [(12.5, 6.5), (11.5, 27.5), (29.5, 24.5),
       (82.0, 34.4), (90.5, 16.5), (60.5, 49.5), (92.5, 60.5), (11.5, 60.5),   # celui-ci : à côté du bac à sable
       (19.5, 12.5), (16.5, 39.5), (86.5, 39.5), (45.5, 40.5)]   # jardin de la niche, campagne, prés, quai du port
START = (4.5, 4.2)
ALICE = (5, 53.3 + 14 / 64)   # juste devant la porte de la cabane du parc (cachée jusqu'aux trois indices)
TITLE = (49.5, 7.3)        # caméra de l'écran titre : la place du village
SIGNS = [
    (5.6, 17.1, "Niche de Tecky : en haut. Village : suivre la route vers l'est."),
    (7.3, 22.6, "Les champs du Père Gaston. Attention, chiens pas commodes !"),
    (8.8, 40.8, "Pas de pont ici ! Le seul pont est loin à l'est, après la ferme."),
    (69.9, 17.2, "Ferme des Tilleuls. Attention aux chiens de berger : quand ils s'accroupissent, ils vont charger !"),
    (78, 40.6, "Pont de la rivière. Au sud : la grande forêt."),
    (69.2, 48.6, "Sentier de la forêt. Le parc des enfants est à l'ouest."),
    (52.6, 54.4, "Parc des enfants : toboggan, balançoire, bac à sable et cabane !"),
]


def forest_firs():
    """Sapins serrés dans la forêt (sud-est) : en quinconce un peu désordonné, hors des sentiers et à l'écart des
    objets, chiens, trésors, panneaux et autres décors (check_placement.js vérifie que tout reste atteignable)."""
    g = corner_grid()
    rnd = random.Random(11)
    keep = ([(x, y) for _, x, y in ITEMS] + [(x, y) for _, x, y in ENEMIES] + list(DIG)
            + [(x, y) for x, y, _ in SIGNS] + [(x, y) for n, x, y in DECOR if x > 55 and y > 46])

    def near_path(px, py):
        return any(g[cy][cx] == "dirt" for cy in range(int(py - 1.8), int(py + 1.4) + 1)
                   for cx in range(int(px - 1.3), int(px + 1.3) + 2) if 0 <= cy <= MH and 0 <= cx <= MW)
    out = []
    y, row = 47.6, 0
    while y < MH:
        x = 56.8 + (row % 2) * 1.0
        while x < MW - 0.4:
            px, py = x + rnd.uniform(-0.4, 0.4), min(MH - 0.1, y + rnd.uniform(-0.25, 0.25))
            in_clearing = CLEARING[0] - 0.8 < px < CLEARING[2] + 0.8 and CLEARING[1] - 0.6 < py < CLEARING[3] + 1.2
            if not near_path(px, py) and not in_clearing and all((px - kx) ** 2 + (py - ky) ** 2 > 1.8 ** 2 for kx, ky in keep):
                out.append(("fir", round(px, 2), round(py, 2)))
            x += 2.0
        y += 1.55
        row += 1
    return out


DECOR += forest_firs()
FULL_VARIANTS = {"dirt": [9, 10], "road": [11, 12], "paving": [13], "concrete": [14, 15]}
OV = {n: i for i, (n, _) in enumerate(tiles.OVERLAYS)}


COMPOSITES = []       # tuiles composées (trois terrains : bout de chemin sur la route…), ajoutées au tileset web


def build_map():
    g = corner_grid()
    rnd = random.Random(7)
    ground = []
    COMPOSITES.clear()
    for ty in range(MH):
        for tx in range(MW):
            cs = [g[ty][tx], g[ty][tx + 1], g[ty + 1][tx], g[ty + 1][tx + 1]]
            up, lo, bits = tiles.resolve(cs)
            if tiles.needs_composite(cs):
                if tuple(cs) not in COMPOSITES:
                    COMPOSITES.append(tuple(cs))
                idx = tiles.COMPOSITE_BASE + COMPOSITES.index(tuple(cs))
            elif up == "grass":
                idx = rnd.choice([1, 1, 1, 1, 2, 2, 3, 4])
            else:
                idx = tiles.tile_index(up, bits, "grass" if bits == 15 else lo)
                if bits == 15 and up in FULL_VARIANTS and rnd.random() < 0.35:
                    idx = rnd.choice(FULL_VARIANTS[up])
            ground.append(idx)
    # marquages de la route
    for tx in range(MW):
        ground[19 * MW + tx] = 5 if tx % 2 == 0 else tiles.tile_index("road", 15)
    for tx in CROSSINGS:                              # passages piétons (dont chemin de la ferme et du pont)
        for ty in (18, 19, 20):
            ground[ty * MW + tx] = ground[ty * MW + tx + 1] = 7
    # détails
    over = [0] * (MW * MH)
    ovrow = tiles.OVERLAY_ROW * tiles.COLS

    def put(name, tx, ty):
        over[ty * MW + tx] = ovrow + OV[name]
    for tx, ty in ((6, 19), (30, 20), (54, 18)):
        put("plaque d'égout", tx, ty)
    put("grille d'évacuation", 34, 17)
    put("fissures", 49, 17)
    put("flaque", 3, 9)
    put("feuilles mortes", 1, 2)
    put("feuilles mortes", 13, 2)
    put("touffe d'herbe", 9, 10)
    put("touffe d'herbe", 26, 24)
    put("cailloux", 28, 10)
    put("tache d'huile", 50, 24)
    put("tache d'huile", 35, 29)
    put("bande de danger", 46, 24)
    put("bande de danger", 47, 24)
    put("ligne de parking", 52, 25)
    put("ligne de parking", 53, 25)
    put("feuilles mortes", 31, 8)
    # nouvelles zones
    for tx, ty in ((60, 49), (63, 54), (69, 47), (74, 52), (77, 57), (82, 49), (86, 59), (90, 55), (93, 50),
                   (61, 62), (71, 61), (79, 62), (65, 58), (84, 53)):
        put("feuilles mortes", tx, ty)
    for tx, ty in ((73, 56), (88, 61), (59, 57)):
        put("touffe d'herbe", tx, ty)
    for tx, ty in FLOWER_BEDS:
        put("fleurs", tx, ty)
    for tx, ty in ((67, 9), (74, 6), (80, 28)):
        put("cailloux", tx, ty)
    put("flaque", 69, 9)
    put("flaque", 76, 50)
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
        "cowFps": {k: {a: fps for a, (_, fps, _) in cows.anims(k).items()} for k in cows.KINDS},
        "duckFps": {k: {a: fps for a, (_, fps, _) in ducks.anims(k).items()} for k in ducks.KINDS},
        "duckLoop": {k: {a: loop for a, (_, _, loop) in ducks.anims(k).items()} for k in ducks.KINDS},
        "critterFps": {k: {a: fps for a, (_, fps, _) in critters.anims(k).items()} for k in critters.KINDS},
        "tunnels": [[px(a[0]), px(a[1]), px(b[0]), px(b[1])] for a, b in TUNNELS],
        "butterflies": [[c, px(x), px(y)] for c, x, y in BUTTERFLIES],
        # où les papillons se posent : (x, y au sol, hauteur) — sur les pots de fleurs, ou sur les massifs
        "flowers": [[px(x), px(y) + 2, 44] for n, x, y in DECOR if n == "flower_pot"]
                   + [[px(tx + 0.5), px(ty + 0.5), 4] for tx, ty in FLOWER_BEDS],
        "traffic": {"lanes": [px(18.95), px(20.95)], "road": [px(17.5), px(21.5)],
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
    for kind in npcs.KINDS:                             # le facteur et la voisine, vus de face, pieds en (24, 60)
        for a in npcs.ANIMS[kind]:
            out.append((f"{kind}/{a}", [render_svg(sv, npcs.W, npcs.H, S, PAD) for sv in npcs.frames(kind, a)], (24 * S + M, 60 * S + M), True))
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
