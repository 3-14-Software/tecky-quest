"""
Premier jet de la carte de la côte (été, lot 6 de PLAN_V2.md), d'après le plan reference/v2/ete_plan.png : 96 x 64
tuiles, une tuile pour 20 px du plan.

    python3 v2/cote_carte.py --apercu   # reference/v2/cote_carte.png : la carte du dépôt, dessinée comme le jeu

Ce script n'a servi qu'à poser le terrain et les premiers décors (13 novembre 2026). Depuis, **la carte est celle
du fichier cartes/cote.json**, que Christophe retouche dans l'éditeur (http://127.0.0.1:8770/?carte=cote) : ce
qui est écrit ici n'est plus à jour et ne doit plus l'écraser. --ecrire refuse donc de remplacer une carte qui
existe (il faudrait la supprimer d'abord, en connaissance de cause).
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import carte  # noqa: E402

W, H = 96, 64
NOM = "cote"


# ------------------------------------------------------------------ outils
def ligne(pts):
    """Fonction x -> y le long d'une ligne brisée (constante au-delà de ses bouts)."""
    def f(x):
        if x <= pts[0][0]:
            return pts[0][1]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x <= x1:
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return pts[-1][1]
    return f


def dedans(poly, x, y):
    """Le coin (x, y) est-il dans le polygone (bord compris) ?"""
    cx, cy = sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)
    x, y = x + (cx - x) * 1e-6, y + (cy - y) * 1e-6
    k = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (x1 - x0) * (y - y0) / (y1 - y0):
            k = not k
    return k


G = [["."] * (W + 1) for _ in range(H + 1)]


def coin(x, y, c):
    if 0 <= x <= W and 0 <= y <= H:
        G[y][x] = c


def rect(x0, y0, x1, y1, c):          # bornes comprises
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            coin(x, y, c)


def poly(pts, c):
    for y in range(H + 1):
        for x in range(W + 1):
            if dedans(pts, x, y):
                G[y][x] = c


# ------------------------------------------------------------------ le terrain
# les planches : une bande de trois rangées de coins qui suit la baie, de part et d'autre de la rivière
PLANCHES_O = ligne([(13, 40), (24, 42), (38, 45)])
PLANCHES_E = ligne([(47, 45.5), (52, 46), (62, 44), (72, 39.5), (73, 39)])
planches = lambda x: PLANCHES_O(x) if x < 43 else PLANCHES_E(x)
# le bord de la mer : le quai du port à l'ouest, la baie, le pied de la falaise à l'est
MER = ligne([(0, 51), (9, 51), (10, 48), (22, 50.5), (36, 54.5), (41, 55.5), (52, 55.5), (62, 53.5), (72, 48.5),
             (80, 45.5), (88, 46.5), (96, 47.5)])
# la rivière : son milieu, du nord à la mer ; elle s'élargit à l'embouchure
RIVIERE = ligne([(0, 42), (12, 40.5), (24, 42.5), (36, 41.5), (46, 43), (56, 44)])      # y -> x
large = lambda y: 1.75 if y <= 44 else 1.75 + (y - 44) / 11

PORT = [(2, 24), (13, 24), (14, 40), (12, 40), (10, 48), (10, 50), (2, 50)]
VILLAGE = [(16, 16), (36, 16), (37, 37), (17, 37)]
BASSIN = (23, 27, 33, 33)
VILLE = [(49, 14), (70, 14), (72, 34), (64, 40), (50, 40)]
JARDINS = (53, 29, 66, 35)
PARKING = (24, 4, 36, 13)
ROUTE = 6                              # première rangée de coins de la route (4 rangées), du tunnel au parking
ROUTE_FIN = 30


def terrain():
    # le sable : sous les planches ; à l'est, jusqu'au pied de la falaise
    for x in range(10, W + 1):
        haut = round(planches(x)) + 2 if x <= 73 else 38
        rect(x, haut, x, H, "a")
    # chemins de terre (ce qui est bâti passe par-dessus leurs bouts)
    rect(30, 13, 31, 16, "t")          # du parking au village de pêcheurs
    rect(7, 10, 8, 24, "t")            # de la route au port
    rect(13, 30, 17, 31, "t")          # du port au village
    rect(27, 36, 28, 42, "t")          # du village aux planches
    rect(36, 26, 40, 28, "t")          # les abords du pont (le décor bridge_h, posé sur la rivière)
    rect(45, 26, 49, 28, "t")
    rect(58, 40, 59, 45, "t")          # de la ville aux planches
    rect(60, 9, 61, 14, "t")           # de la ville à la campagne
    rect(47, 8, 73, 9, "t")            # le chemin de la campagne
    rect(72, 25, 79, 26, "t")          # de la ville à l'escalier de la falaise
    # le port, le village et son bassin, la ville et ses jardins, le parking
    poly(PORT, "b")
    poly(VILLAGE, "p")
    rect(*BASSIN, "m")
    poly(VILLE, "s")
    rect(*JARDINS, ".")
    rect(*PARKING, "b")
    rect(0, ROUTE, ROUTE_FIN, ROUTE + 3, "r")
    # les planches
    for x in range(13, 74):
        r = round(planches(x))
        rect(x, r - 1, x, r + 1, "l")
    coin(12, 41, "l")                  # (entre le port, les planches et le sable : pas un rond d'herbe)
    # la rivière (de l'eau douce), puis la mer, où elle se jette
    for y in range(0, 57):
        for x in range(W + 1):
            if abs(x - RIVIERE(y)) <= large(y):
                G[y][x] = "~"
    for x in range(W + 1):
        rect(x, math.ceil(MER(x)), x, H, "m")
    rect(42, 56, 46, 56, "~")          # (l'eau douce avance un peu dans la mer, en langue : pas une ligne droite)
    rect(43, 57, 45, 57, "~")
    coin(44, 58, "~")
    # la jetée (des planches sur la mer)
    rect(48, round(planches(48)) + 2, 49, 61, "l")
    # la falaise : le plateau (lande), sa paroi sous ses bords du bas, ses deux escaliers
    rect(76, 9, W, 22, "h")
    rect(81, 23, W, 38, "h")
    rect(86, 39, W, 41, "h")
    rect(76, 23, 80, 24, "k")
    rect(81, 39, 85, 40, "k")
    rect(86, 42, W, 43, "k")
    rect(77, 22, 78, 24, "e")          # depuis la ville
    rect(83, 38, 84, 40, "e")          # depuis la plage
    return ["".join(r) for r in G]


# ------------------------------------------------------------------ ce qu'on y pose
DECOR = [
    # --- la route, le parking
    ["road_sign", 3.2, 5.35], ["lamppost", 24.6, 4.9], ["lamppost", 35.4, 4.9], ["lamppost", 24.6, 13.2],
    ["lamppost", 35.4, 13.2], ["hedge", 25, 4.2], ["hedge", 26, 4.2], ["hedge", 27, 4.2], ["hedge", 32, 4.2],
    ["hedge", 33, 4.2], ["hedge", 34, 4.2], ["cone", 33.5, 11.2], ["bench", 27.4, 13.6],
    # --- le nord-ouest : des arbres le long de la route
    ["tree", 5.5, 3.2], ["tree", 11.4, 2.6], ["tree", 17.6, 3.6], ["tree", 22, 2.4], ["bush", 8.4, 4.4],
    ["bush", 14.6, 4.6], ["tree", 3.4, 14.4], ["tree", 12.4, 12.8], ["tree", 19.4, 12.4], ["bush", 16.2, 11.6],
    ["tree", 4.6, 20.6], ["bush", 11.2, 17.6], ["tree", 13.6, 21.6], ["bush", 22.4, 14.2], ["rock", 10.4, 14.6],
    ["tree", 36.4, 2.6], ["bush", 38.2, 12.6],
    # --- le port
    ["warehouse", 6.4, 28.4], ["guard_hut", 11.4, 26.2], ["truck", 6.2, 31.6], ["container", 10.4, 34.2],
    ["container_blue", 5, 35], ["container_stack", 7.6, 38.6], ["crane", 7.6, 39.1], ["container_green", 5.2, 43],
    ["container", 7.6, 46.4], ["forklift", 4.6, 48.6], ["pallet", 9.4, 43.6], ["crate", 10.2, 42.2],
    ["barrel_blue", 3.2, 45.2], ["barrel_red", 3.9, 45.5], ["lamppost", 12.6, 30.6], ["lamppost", 2.8, 40.6],
    ["bollard", 3.5, 50.3], ["bollard", 6.5, 50.3], ["bollard", 9.3, 50.3], ["cargo", 6, 54.7], ["cone", 9.4, 30.4],
    # --- le village de pêcheurs
    # (maisons et cabanes de pêcheurs : le modèle se tire de la position, au dixième de tuile près — volets bleus,
    # pignon aux volets rouges, volets verts ; cabane rouge, bleue, jaune ou verte)
    ["house_fisher", 19.4, 19.6], ["house_fisher", 23.5, 19.4], ["house_fisher", 27.7, 19.5], ["house_fisher", 34.1, 19.5],
    ["house_fisher", 19.4, 25.2], ["hut_fisher", 19.5, 29.4], ["hut_fisher", 19.6, 33.6],
    ["hut_fisher", 22.2, 36.7], ["hut_fisher", 25.1, 36.7], ["hut_fisher", 30.7, 36.6], ["hut_fisher", 33.5, 36.7],
    ["flower_pot", 21.4, 19.9], ["flower_pot", 25.7, 19.9],
    ["flower_pot", 21.2, 25.5], ["mailbox", 29.6, 19.8], ["cafe_table", 24.4, 23.6], ["cafe_table", 26.8, 24.2],
    ["bollard", 24, 26.4], ["bollard", 27, 26.4], ["bollard", 30, 26.4], ["bollard", 33, 26.4],
    ["boat", 26, 30.2], ["boat", 30.6, 31.6], ["lamppost", 22, 26.4], ["lamppost", 34.6, 34.6],
    ["crate", 34.8, 30.2], ["barrel_blue", 35.6, 30.5], ["barrel_red", 35, 32.2], ["pallet", 36, 28.4],
    ["crate", 34.5, 27.9], ["bench", 28.2, 34.7], ["bicycle", 31.8, 20], ["stall_fish", 35.3, 25],
    # --- la rivière et son pont
    ["bridge_h", 42.5, 28.5],
    ["reeds", 39, 8.4], ["reeds", 44.2, 15.2], ["reeds", 39.6, 21.4], ["reeds", 44.4, 32.4], ["reeds", 39, 37.6],
    ["rock", 44.6, 3.6], ["bush", 38.6, 31.6], ["tree", 46.2, 21.6], ["tree", 46.6, 36.4], ["bush", 46.2, 31.4],
    # --- la ville : la place du casino (à venir), les jardins (le manège à venir), le front de mer
    ["house_tall", 51.4, 19.6], ["house_blue", 51.4, 24.6], ["house_red", 68.6, 19.4], ["house_timber", 68.8, 24.6],
    ["house_tall", 69.4, 30.2], ["house_blue", 52.6, 39.7], ["bakery", 56.2, 39.6], ["house_red", 62.6, 39.3],
    ["house_timber", 66.2, 37.7], ["lamppost", 53.6, 17.6], ["lamppost", 64.4, 17.6], ["lamppost", 53.6, 26.4],
    ["lamppost", 64.4, 26.4], ["flower_pot", 54.6, 26.2], ["flower_pot", 63.4, 26.2], ["cafe_table", 56.4, 27.4],
    ["cafe_table", 58.8, 27.8], ["cafe_table", 61.6, 27.4], ["stall_ice", 66.6, 28], ["stall_flower", 51.8, 30.2],
    ["bicycle", 66.6, 22.2], ["mailbox", 53.6, 24.9], ["casino", 59, 25.4], ["carousel", 62.4, 33.5],
    ["hedge", 53, 29.3], ["hedge", 54, 29.3], ["hedge", 55, 29.3], ["hedge", 56, 29.3], ["hedge", 57, 29.3],
    ["hedge", 61, 29.3], ["hedge", 62, 29.3], ["hedge", 63, 29.3], ["hedge", 64, 29.3], ["hedge", 65, 29.3],
    ["hedge", 53, 35.6], ["hedge", 54, 35.6], ["hedge", 55, 35.6], ["hedge", 56, 35.6], ["hedge", 57, 35.6],
    ["hedge", 61, 35.6], ["hedge", 62, 35.6], ["hedge", 63, 35.6], ["hedge", 64, 35.6], ["hedge", 65, 35.6],
    ["fountain", 56.6, 32.8], ["bench", 54.6, 34.4], ["bench", 59.6, 30.8], ["flower_pot", 58.4, 34.6],
    ["flower_pot", 60.6, 34.6],
    # --- les planches et la plage
    ["bench", 18, 40.6], ["lamppost", 22, 41.2], ["bench", 32, 43.2], ["lamppost", 36, 44.1], ["lamppost", 48, 45.2],
    ["bench", 54, 45.2], ["lamppost", 60, 43.8], ["bench", 65, 42.2], ["lamppost", 70, 39.8], ["flower_pot", 16.4, 40.4],
    ["flower_pot", 56.4, 45], ["stall_ice", 51.4, 46.7],
    # (les cabines de plage, au pied des planches : une couleur par position, comme les cabanes)
    ["beach_hut", 52.4, 49.5], ["beach_hut", 54.2, 49.5], ["beach_hut", 55.8, 49.4], ["beach_hut", 57.5, 49.4],
    ["beach_hut", 59.1, 49.3], ["beach_hut", 60.5, 49.4], ["beach_hut", 18.5, 45.1], ["beach_hut", 20.3, 45.1],
    ["beach_hut", 21.8, 45.1], ["beach_hut", 23.3, 45.1],
    # (les bateaux de pêche, au large : dans le petit bassin fermé, ils étaient « bizarres » — Christophe)
    ["fishing_boat", 26.1, 58.4], ["fishing_boat", 64.4, 59.6], ["fishing_boat", 83.9, 55.6], ["rock", 75.4, 41.6], ["rock", 79.2, 43.6], ["rock", 93.4, 45.8], ["boat", 14.6, 46.6],
    # --- la campagne normande
    ["apple_tree", 63.5, 3], ["apple_tree", 66.5, 3], ["apple_tree", 69.5, 3], ["apple_tree", 72.5, 3],
    ["apple_tree", 63.5, 6], ["apple_tree", 66.5, 6], ["apple_tree", 69.5, 6], ["apple_tree", 72.5, 6],
    ["apple_crate", 65, 7.2], ["fallen_apples", 68, 4.4], ["fallen_apples", 71, 7], ["ladder", 70.4, 5.8],
    ["tree", 47.4, 2.4], ["tree", 59.6, 2.6], ["hay", 47.6, 11.4], ["hay", 48.8, 11.7], ["tree", 58.4, 12],
    ["tree", 64.4, 11.6], ["bush", 67.6, 12.4], ["tree", 71.6, 11.4], ["tree", 74.2, 13.4], ["bush", 56.4, 2.2],
    ["scarecrow", 57.4, 6.6], ["tree", 79.4, 3.4], ["tree", 85.6, 2.8], ["tree", 91.4, 4.2], ["bush", 82.6, 5.6],
    ["bush", 88.6, 6.4], ["tree", 94.4, 2.6], ["tree", 74.2, 19.6], ["bush", 73.6, 29.6], ["tree", 75.2, 33.6],
    ["bush", 47.4, 39.4],
    # --- le plateau de la falaise, le phare au bout
    ["lighthouse", 90.5, 31.5],
    ["rock", 84.4, 14.2], ["rock", 93.2, 20.4], ["bush", 82.6, 28.4], ["bush", 94.2, 34.6], ["rock", 88.4, 36.8],
    ["bench", 91.4, 39.8], ["bush", 79.4, 12.6], ["rock", 80.6, 19.4], ["bush", 89.6, 23.6], ["stump", 86.2, 18.6],
]
DETAILS = [
    ["ligne de parking", 25, 11], ["ligne de parking", 27, 11], ["ligne de parking", 29, 11], ["ligne de parking", 31, 11],
    ["ligne de parking", 33, 11], ["ligne de parking", 35, 11],
    ["fleurs", 55, 30], ["fleurs", 65, 33], ["fleurs", 65, 30], ["fleurs", 58, 31], ["fleurs", 64, 4], ["fleurs", 67, 7],
    ["fleurs", 50, 11], ["fleurs", 54, 2], ["fleurs", 19, 3], ["fleurs", 12, 13], ["fleurs", 82, 4],
    ["touffe d'herbe", 9, 19], ["touffe d'herbe", 52, 6], ["touffe d'herbe", 49, 3], ["cailloux", 45, 12],
    ["plaque d'égout", 60, 16], ["tache d'huile", 5, 33], ["bande de danger", 4, 49], ["bande de danger", 5, 49],
    ["fissures", 9, 27],
]
ITEMS = [
    ["bone", 20.5, 12.4], ["bone", 33.4, 22.6], ["bone", 5, 22.2], ["bone", 48, 30.4], ["bone", 66, 12.4],
    ["bone", 79.4, 30.4], ["bone", 90, 12.4], ["bone", 25, 46.4], ["bone", 70.5, 45.2], ["bone", 66, 20.6],
    ["sausage", 3.4, 30.6], ["sausage", 93.6, 26.2], ["sausage", 48.5, 60.2],
    ["medal", 35.2, 12.2], ["medal", 94.4, 45.4], ["medal", 61.5, 2.4],
    ["squeaky", 12.4, 45.5], ["squeaky", 55, 50.4], ["squeaky", 45.4, 5.6],
    ["ball", 39.2, 48.4], ["ball", 64.2, 49.6], ["ball", 18.4, 11.6], ["ball", 86.6, 34.2],
]
DIG = [[17.5, 46.5], [32.5, 50.5], [58.5, 50.5], [75.5, 43.5], [91.5, 45.5], [55.5, 11.5]]
ENEMIES = [
    ["roquet", 11, 29.6], ["molosse", 5.6, 36.6], ["bouledogue", 4.4, 46.2], ["roquet", 73.8, 31.4],
    ["bouledogue", 47.2, 33.6], ["berger", 56.6, 4.4], ["roquet", 67.6, 10.8],
]
SIGNS = [
    [3, 11.2, "Par le tunnel, à l'ouest : le village de Tecky et la ferme des Tilleuls."],
    [32.6, 14.8, "Le village de pêcheurs est juste en bas. Pour la plage, suivez le quai jusqu'aux planches."],
    [37.6, 29.6, "Le pont de la rivière. En face : la ville, son casino et ses jardins."],
    [75.4, 27.6, "Sentier des falaises. Le phare est tout au bout. Attention au bord !"],
    [61.4, 42.6, "Les Planches : la promenade du bord de mer. La jetée est à l'embouchure de la rivière."],
]
DUCKS = [["duck", 41.4, 5, 0], ["duck_f", 41.6, 18.2, 1], ["duckling", 41.3, 18.5, 1], ["duckling", 41, 18.8, 1],
         ["duck", 27.6, 28.6, 0], ["duck_f", 31, 29.6, 0]]
COWS = [["cow_bw", 50, 4.4], ["cow_brown", 54, 5.8], ["calf", 51, 6]]
CRITTERS = [["squirrel", 59, 3.2], ["squirrel", 22.6, 3], ["cat", 25.4, 22.6], ["cat_black", 33.4, 26],
            ["squirrel", 64.8, 12.4], ["cat", 60.4, 37.6]]
BUTTERFLIES = [["yellow", 56, 31.4], ["pink", 65.4, 32.6], ["blue", 65.5, 5.2], ["orange", 50.5, 10.6],
               ["yellow", 19.6, 3.6], ["blue", 12.6, 13.4], ["pink", 82.4, 4.6]]
ZONES = [
    {"id": "industrie", "name": "Le port", "label": "Port", "at": [7.5, 25.2], "rects": [[0, 22.5, 14.5, 64]]},
    {"id": "village", "name": "Le village de pêcheurs", "label": "Village de pêcheurs", "at": [27, 22.4], "rects": [[14.5, 14.5, 39, 39.5]]},
    {"id": "ville", "music": "parc", "name": "La ville", "label": "Ville", "at": [60, 15.6], "rects": [[47.5, 13, 75.5, 42.5]]},
    {"id": "falaises", "music": "foret", "name": "Les falaises", "label": "Falaises", "at": [87, 15], "rects": [[75.5, 8.5, 96, 41.5]]},
    {"id": "plage", "music": "campagne", "name": "La plage", "label": "Plage", "at": [30, 48.6], "rects": [[0, 38.5, 96, 64]]},
    {"id": "ferme", "name": "La campagne normande", "label": "Campagne normande", "at": [60, 1.4], "rects": [[44.5, 0, 96, 13]]},
    {"id": "campagne", "name": "La Côte Fleurie", "label": "Côte Fleurie", "at": [14, 1.4], "rects": [[0, 0, 96, 64]]},
]
LANDMARKS = [
    {"label": "Rivière", "at": [42, 20]}, {"label": "Jetée", "at": [48.5, 58]}, {"label": "Phare", "at": [90.5, 30]},
    {"label": "Casino", "at": [59, 21.5]}, {"label": "Bassin", "at": [28, 30.4]}, {"label": "Parking", "at": [30, 5]},
    {"label": "Les Planches", "at": [64, 44.6]},
]
CALM = [[23.5, 3.5, 36.5, 14.5], [15.5, 15.5, 37.5, 38.5], [52, 26, 67, 36.6], [84, 25, 96, 38.5]]


def faire():
    return {
        "format": carte.FORMAT, "annexe": True, "w": W, "h": H, "legende": carte.LEGENDE, "terrain": terrain(),
        "details": DETAILS, "decor": DECOR, "items": ITEMS, "dig": DIG, "enemies": ENEMIES, "signs": SIGNS,
        "ducks": DUCKS, "cows": COWS, "critters": CRITTERS, "butterflies": BUTTERFLIES,
        "roadTunnels": [[0, ROUTE + 4, False]], "passages": [[0, "monde", 1]],
        "traffic": {"y": ROUTE, "crossings": [], "vehicles": []},
        "calm": CALM, "zones": ZONES, "landmarks": LANDMARKS,
    }


def apercu(sortie):
    """La carte entière, sol, lisière et décors, par les fonctions de pack_web (comme web/map_preview.png), aux
    couleurs de l'été."""
    import shutil
    import pack_web
    import saisons
    import tiles
    pack_web.COMPOSITES.clear()
    pack_web.charger_carte(NOM)
    m = pack_web.build_map()
    saisons.appliquer("ete")
    try:
        atlas, meta = pack_web.pack(pack_web.collect())
        pack_web.preview(m, atlas, meta, tiles.tileset(pack_web.S, composites=pack_web.COMPOSITES))
    finally:
        saisons.appliquer()
    shutil.move(os.path.join(pack_web.WEB, "map_preview.png"), sortie)
    print(sortie, ":", len(pack_web.COMPOSITES), "tuiles composées")


if __name__ == "__main__":
    c = faire()
    err = carte.valider(c)
    for e in err:
        print("PB", e)
    print(f"{NOM} : {W} x {H}, {len(DECOR)} décors, {len(ITEMS)} objets, {len(ENEMIES)} chiens")
    if "--ecrire" in sys.argv and not err:
        if os.path.exists(carte.chemin(NOM)) and "--premier-jet" not in sys.argv:
            sys.exit("refusé : cartes/cote.json existe, et c'est lui qui fait foi (retouché dans l'éditeur de carte)")
        carte.enregistrer(c, carte.chemin(NOM))
        print("écrit :", os.path.relpath(carte.chemin(NOM), ROOT))
    if "--apercu" in sys.argv:
        apercu(os.path.join(ROOT, "reference", "v2", "cote_carte.png"))
