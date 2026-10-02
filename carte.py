#!/usr/bin/env python3
"""
La carte du jeu (carte.json) : terrain, détails au sol, décors, éléments de jeu et zones, en tuiles.

pack_web.py la lit pour construire le niveau ; l'éditeur de carte (editeur.py) la lit et l'enregistre. Ce module la
charge, la vérifie et l'écrit dans un format stable (une entrée par ligne : des différences Git lisibles).

    python3 carte.py        # vérifie carte.json et le réécrit au format normalisé

Ce qui ne figure pas dans le fichier est déduit par pack_web.build_map() : poteaux des panneaux (signs), terriers
(tunnels), clôtures de l'enclos (pen, penGate), filet de Léon (goal), rails et heurtoirs (track), coins du pont (un
par décor « bridge »), traces de pattes (dig), perchoirs des papillons, marquages de la route, lisière.
"""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ROOT, "carte.json")
FORMAT = 1

# une lettre par terrain dans les lignes de « terrain » (une ligne par rangée de coins)
LEGENDE = {".": "grass", "t": "dirt", "r": "road", "p": "paving", "b": "concrete", "s": "sidewalk", "~": "water",
           "c": "field", "f": "forest"}

# ordre des clés dans le fichier (une clé inconnue est gardée, à la fin)
ORDRE = ["format", "w", "h", "legende", "terrain", "details", "decor",
         "items", "dig", "enemies", "signs", "tunnels",
         "hens", "ducks", "cows", "critters", "butterflies", "villagers",
         "start", "alice", "title", "ending",
         "farmer", "postman", "neighbor", "pompon", "leon", "iris", "piquette",
         "letters", "balls", "toys", "babies", "goal", "ballBox", "pen", "penGate", "track",
         "roadTunnels", "traffic", "calm", "zones", "landmarks"]

# listes de taille fixe : « cinq lettres » et « cinq ballons » dans les dialogues (une couleur par ballon,
# port.BALL_COLORS), les jouets d'Iris (port.TOYS : canard, anneau, corde, dans cet ordre), les places des petits
# hérissons auprès de leur maman (BABY.slots)
TAILLES = {"letters": 5, "balls": 5, "toys": 3, "babies": 3}
# listes dont la sauvegarde retient les éléments par leur rang : en ajouter à la fin, et ne pas en retirer au milieu
# sans changer SAVE_V dans game.js (sinon une partie en cours retrouve ses chiens, trésors… mélangés)
INDEXEES = ["enemies", "dig", "critters", "ducks", "letters", "hens", "balls", "toys", "babies"]
# les indices d'Alice (CLUES dans game.js) : exactement un de chaque, parmi les objets
INDICES = ("hairclip", "shoe", "plush")
# variations de la musique et ambiances d'une zone (TIMBRE dans game.js)
MUSIQUES = ("niche", "village", "campagne", "ferme", "industrie", "foret", "parc")
# détails au sol déduits d'autres données (jamais dans « details »)
DETAILS_DEDUITS = ("traces de pattes", "trou creusé (trésor)")
# décors déduits d'autres données (jamais dans « decor »)
DECORS_DEDUITS = ("signpost", "burrow", "goal_net", "rail", "buffer_stop")

# personnages et repères : un point (x, y) chacun
POINTS = ["start", "alice", "title", "farmer", "postman", "neighbor", "pompon", "leon", "iris", "piquette", "goal"]
# listes [genre, x, y] (genres() dit lesquels existent)
NOMMEES = ["decor", "items", "enemies", "cows", "critters", "butterflies", "villagers"]
# listes de points [x, y]
POSITIONS = ["dig", "letters", "balls", "toys", "babies"]

# image de l'atlas qui représente un élément dans l'éditeur ({} : son genre ; [clé, n° d'image] pour les listes dont
# chaque élément a son image)
SPRITES = {
    "decor": "decor/{}", "items": "item/{}", "enemies": "{}/idle/down", "hens": "{}/idle/right", "ducks": "{}/swim",
    "cows": "{}/graze", "critters": "{}/idle", "butterflies": "butterfly/{}", "villagers": "{}/idle",
    "vehicles": "vehicle/{}", "dig": "item/goldbone", "signs": "decor/signpost", "tunnels": "decor/burrow",
    "letters": "item/letter", "balls": ["port/balloon"], "toys": ["port/toy"], "babies": "hedgehog/idle",
    "start": "tecky/idle/down", "alice": "alice/idle/down", "farmer": "farmer/idle", "postman": "postman/idle",
    "neighbor": "neighbor/idle", "pompon": "cat_white/idle", "leon": "leon/idle", "iris": "iris/idle",
    "piquette": "piquette/idle", "goal": "decor/goal_net", "roadTunnels": "decor/tunnel",
}


def genres():
    """Genres permis pour chaque liste nommée (ceux que pack_web.collect() dessine dans l'atlas)."""
    import butterflies
    import cows
    import critters
    import decor
    import ducks
    import enemies
    import hens
    import items
    import tiles
    import vehicles
    import villageois
    return {
        "decor": [n for n in decor.DECOR if n not in DECORS_DEDUITS],
        "items": [n for n in items.ITEMS if n != "goldbone"],
        "enemies": list(enemies.DOGS),
        "hens": list(hens.COLORS),
        "ducks": list(ducks.KINDS),
        "cows": list(cows.KINDS),
        "critters": [k for k in critters.KINDS if k != "cat_white"],      # (le chat blanc, c'est Pompon)
        "butterflies": list(butterflies.COLORS),
        "villagers": list(villageois.KINDS),
        "vehicles": [n for n in vehicles.VEHICLES if n not in ("loco",) and not n.startswith("wagon")],
        "details": [n for n, _ in tiles.OVERLAYS if n not in DETAILS_DEDUITS],
    }


# ------------------------------------------------------------------ lecture, vérification
def charger(chemin=FICHIER, verifier=True):
    with open(chemin, encoding="utf-8") as f:
        c = json.load(f)
    if verifier:
        err = valider(c)
        if err:
            raise ValueError(f"{os.path.basename(chemin)} : " + " ; ".join(err[:12])
                             + (f" (et {len(err) - 12} autres)" if len(err) > 12 else ""))
    return c


def terrain_grid(c):
    """Grille des coins [y][x] -> nom du terrain."""
    return [[LEGENDE[ch] for ch in ligne] for ligne in c["terrain"]]


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _pt(v):
    return isinstance(v, list) and len(v) == 2 and all(_num(a) for a in v)


def valider(c, avec_genres=True):
    """Liste des erreurs (vide si la carte est correcte)."""
    err = []
    if c.get("format") != FORMAT:
        return [f"format {c.get('format')!r} inconnu (attendu : {FORMAT})"]
    w, h = c.get("w"), c.get("h")
    if not (isinstance(w, int) and isinstance(h, int) and w > 0 and h > 0):
        return ["w et h : nombres de tuiles entiers"]
    if c.get("legende") != LEGENDE:
        err.append("legende : doit être " + json.dumps(LEGENDE, ensure_ascii=False))
    t = c.get("terrain")
    if not (isinstance(t, list) and len(t) == h + 1 and all(isinstance(s, str) and len(s) == w + 1 for s in t)):
        err.append(f"terrain : {h + 1} lignes de {w + 1} coins")
    else:
        bad = sorted({ch for s in t for ch in s if ch not in LEGENDE})
        if bad:
            err.append("terrain : lettres inconnues " + " ".join(bad))
    g = genres() if avec_genres else None

    def liste(cle, forme, nom):
        v = c.get(cle)
        if not isinstance(v, list):
            err.append(f"{cle} : une liste")
            return []
        for i, e in enumerate(v):
            if not forme(e):
                err.append(f"{cle}[{i}] : {nom} attendu, pas {json.dumps(e, ensure_ascii=False)}")
        return v
    nomme = lambda e: isinstance(e, list) and len(e) == 3 and isinstance(e[0], str) and _num(e[1]) and _num(e[2])
    for cle in NOMMEES:
        for i, e in enumerate(liste(cle, nomme, "[genre, x, y]")):
            if g and nomme(e) and e[0] not in g[cle]:
                err.append(f"{cle}[{i}] : genre inconnu « {e[0]} »")
    for cle in POSITIONS:
        v = liste(cle, _pt, "[x, y]")
        if cle in TAILLES and len(v) != TAILLES[cle]:
            err.append(f"{cle} : exactement {TAILLES[cle]} (il y en a {len(v)})")
    for i, (x, y) in enumerate(e for e in c.get("dig", []) if _pt(e)):
        if (x % 1, y % 1) != (0.5, 0.5):
            err.append(f"dig[{i}] ({x}, {y}) : un trésor est au centre d'une tuile (x,5 ; y,5)")
    for cle in POINTS:
        if not _pt(c.get(cle)):
            err.append(f"{cle} : un point [x, y]")
    det = lambda e: isinstance(e, list) and len(e) == 3 and isinstance(e[0], str) and all(isinstance(a, int) for a in e[1:])
    for i, e in enumerate(liste("details", det, "[nom, tx, ty] (tuile entière)")):
        if det(e):
            if g and e[0] not in g["details"]:
                err.append(f"details[{i}] : détail inconnu « {e[0]} »")
            if not (0 <= e[1] < w and 0 <= e[2] < h):
                err.append(f"details[{i}] : hors de la carte")
    poule = lambda e: isinstance(e, list) and len(e) == 4 and nomme(e[:3]) and e[3] in (0, 1)
    canard = lambda e: isinstance(e, list) and len(e) == 4 and nomme(e[:3]) and isinstance(e[3], int)
    for cle, forme, nom in (("hens", poule, "[genre, x, y, quête 0/1]"), ("ducks", canard, "[genre, x, y, famille]")):
        for i, e in enumerate(liste(cle, forme, nom)):
            if g and forme(e) and e[0] not in g[cle]:
                err.append(f"{cle}[{i}] : genre inconnu « {e[0]} »")
    liste("signs", lambda e: isinstance(e, list) and len(e) == 3 and _num(e[0]) and _num(e[1]) and isinstance(e[2], str) and e[2].strip(),
          "[x, y, texte]")
    liste("tunnels", lambda e: isinstance(e, list) and len(e) == 4 and all(_num(a) for a in e), "[ax, ay, bx, by]")
    liste("roadTunnels", lambda e: isinstance(e, list) and len(e) == 3 and _num(e[0]) and _num(e[1]) and isinstance(e[2], bool),
          "[x, y, miroir]")
    rect = lambda e: isinstance(e, list) and len(e) == 4 and all(_num(a) for a in e) and e[0] < e[2] and e[1] < e[3]
    liste("calm", rect, "[x0, y0, x1, y1]")
    for cle in ("ballBox", "pen"):
        if not rect(c.get(cle)):
            err.append(f"{cle} : un rectangle [x0, y0, x1, y1]")
    if rect(c.get("pen")) and not all(isinstance(a, int) for a in (c["pen"][0], c["pen"][2])):
        err.append("pen : x0 et x1 entiers (une clôture par tuile)")
    pg = c.get("penGate")
    if not (isinstance(pg, list) and len(pg) == 2 and all(isinstance(a, int) for a in pg) and pg[0] < pg[1]):
        err.append("penGate : [x0, x1] entiers")
    tr = c.get("track")
    if not (isinstance(tr, list) and len(tr) == 3 and all(_num(a) for a in tr) and tr[0] < tr[1]):
        err.append("track : [x ouest, x est, y]")
    e = c.get("ending")
    if not (isinstance(e, dict) and _pt(e.get("alice")) and _pt(e.get("tecky"))):
        err.append("ending : {alice: [x, y], tecky: [x, y]}")
    r = c.get("traffic")
    if not (isinstance(r, dict) and isinstance(r.get("y"), int) and 0 < r["y"] < h - 3
            and isinstance(r.get("crossings"), list) and all(isinstance(x, int) for x in r["crossings"])
            and isinstance(r.get("vehicles"), list)):
        err.append("traffic : {y: première rangée de la route, crossings: [x], vehicles: [[véhicule, voie, x]]}")
    else:
        for i, v in enumerate(r["vehicles"]):
            if not (isinstance(v, list) and len(v) == 3 and v[1] in (0, 1) and _num(v[2])
                    and (not g or v[0] in g["vehicles"])):
                err.append(f"traffic.vehicles[{i}] : [véhicule, voie 0/1, x]")
    zs = c.get("zones")
    if not (isinstance(zs, list) and zs):
        err.append("zones : une liste")
    else:
        ids = set()
        for i, z in enumerate(zs):
            ok = (isinstance(z, dict) and isinstance(z.get("id"), str) and isinstance(z.get("name"), str)
                  and isinstance(z.get("label"), str) and _pt(z.get("at")) and isinstance(z.get("rects"), list)
                  and z["rects"] and all(rect(q) for q in z["rects"]))
            if not ok:
                err.append(f"zones[{i}] : {{id, name, label, at, rects, music?}}")
                continue
            if z["id"] in ids:
                err.append(f"zones[{i}] : id « {z['id']} » en double")
            ids.add(z["id"])
            if z.get("music", z["id"]) not in MUSIQUES:
                err.append(f"zones[{i}] ({z['id']}) : music parmi {', '.join(MUSIQUES)}")
        last = zs[-1]
        if isinstance(last, dict) and not any(isinstance(q, list) and q[:2] <= [0, 0] and q[2] >= w and q[3] >= h
                                              for q in last.get("rects", [])):
            err.append("zones : la dernière couvre toute la carte (rectangle [0, 0, w, h])")
    liste("landmarks", lambda z: isinstance(z, dict) and isinstance(z.get("label"), str) and _pt(z.get("at")), "{label, at}")
    if isinstance(c.get("items"), list):
        for n in INDICES:
            k = sum(1 for it in c["items"] if isinstance(it, list) and it and it[0] == n)
            if k != 1:
                err.append(f"items : exactement un indice « {n} » (il y en a {k})")
    for i, d in enumerate(c.get("decor", [])):
        if nomme(d) and d[0] == "bridge" and not (float(d[1]).is_integer() and float(d[2]).is_integer()):
            err.append(f"decor[{i}] : le pont se pose sur une position entière")
    return err


# ------------------------------------------------------------------ écriture
def _norme(v):
    """Nombres au plus court : 80.0 -> 80, 12.300000000000001 -> 12.3 (relire puis réécrire ne change rien)."""
    if isinstance(v, dict):
        return {k: _norme(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_norme(x) for x in v]
    if isinstance(v, float):
        v = round(v, 6)
        return int(v) if v.is_integer() else v
    return v


def _compact(v):
    return json.dumps(v, ensure_ascii=False, separators=(", ", ": "))


def _bloc(v, ind):
    pad = "  " * (ind + 1)
    if isinstance(v, list) and v and all(isinstance(x, (list, dict, str)) for x in v):
        return "[\n" + ",\n".join(pad + _compact(x) for x in v) + "\n" + "  " * ind + "]"
    if isinstance(v, dict) and len(_compact(v)) > 100:
        return ("{\n" + ",\n".join(pad + json.dumps(k, ensure_ascii=False) + ": " + _bloc(x, ind + 1) for k, x in v.items())
                + "\n" + "  " * ind + "}")
    return _compact(v)


def texte(c):
    """Le fichier : une clé par ligne dans l'ordre de ORDRE, un élément de liste par ligne."""
    c = _norme(c)
    cles = [k for k in ORDRE if k in c] + [k for k in c if k not in ORDRE]
    return "{\n" + ",\n".join("  " + json.dumps(k, ensure_ascii=False) + ": " + _bloc(c[k], 1) for k in cles) + "\n}\n"


def enregistrer(c, chemin=FICHIER):
    """Écrit la carte (atomiquement : un fichier temporaire, puis renommé). Renvoie le texte écrit."""
    t = texte(c)
    tmp = chemin + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(t)
    os.replace(tmp, chemin)
    return t


if __name__ == "__main__":
    c = charger(verifier=False)
    err = valider(c)
    if err:
        raise SystemExit("carte.json :\n  " + "\n  ".join(err))
    avant = open(FICHIER, encoding="utf-8").read()
    if texte(c) != avant:
        enregistrer(c)
        print("carte.json réécrit au format normalisé")
    else:
        print("carte.json : ok")
