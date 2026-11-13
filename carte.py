#!/usr/bin/env python3
"""
La carte du jeu (carte.json) : terrain, détails au sol, décors, éléments de jeu et zones, en tuiles.

pack_web.py la lit pour construire le niveau ; l'éditeur de carte (editeur.py) la lit et l'enregistre. Ce module la
charge, la vérifie et l'écrit dans un format stable (une entrée par ligne : des différences Git lisibles).

    python3 carte.py              # vérifie carte.json et le réécrit au format normalisé
    python3 carte.py --verifier   # vérifie seulement (code de retour 1 si une erreur, ou si le format n'est pas le bon)

Ce qui ne figure pas dans le fichier est déduit par pack_web.build_map() : poteaux des panneaux (signs), terriers
(tunnels), clôtures de l'enclos (pen, penGate), filet de Léon (goal), rails et heurtoirs (track), coins du pont (un
par décor « bridge »), traces de pattes (dig), perchoirs des papillons, marquages de la route, lisière.
"""
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ROOT, "carte.json")
FORMAT = 1
# Le jeu a plusieurs cartes. Celle du monde (l'aventure : la niche, le village, la ferme…) reste carte.json ; les
# autres, les cartes annexes, sont dans cartes/<nom>.json. Une carte annexe ("annexe": true) n'a que ce qu'elle
# déclare : ni Alice, ni personnages, ni enclos si elle ne les cite pas (completer() met le reste hors de la carte).
# On passe d'une carte à l'autre par un tunnel de la grande route : "passages".
MONDE = "monde"
DOSSIER = os.path.join(ROOT, "cartes")
HORS = -2000          # en tuiles : la place de ce qu'une carte n'a pas, loin de tout
# Un épisode (episodes.json) peut changer une carte sans la recopier : cartes/<épisode>/<nom>.json, la surcharge, ne
# redit que les clés qui changent (les objets, les chiens, la place d'Alice…) ; une clé à null est retirée de la carte
# (plus d'Alice, plus de fermier : comme sur une carte annexe, completer() les met hors de la carte). Le terrain
# reste celui de la carte de base tant que la surcharge ne le redit pas.
FIXES = ("format", "annexe", "w", "h", "legende")       # ce qu'une surcharge ne change jamais

# une lettre par terrain dans les lignes de « terrain » (une ligne par rangée de coins)
LEGENDE = {".": "grass", "t": "dirt", "r": "road", "p": "paving", "b": "concrete", "s": "sidewalk", "~": "water",
           "c": "field", "f": "forest", "a": "sand", "l": "planks", "k": "chalk",      # (sable, lames, craie : la paroi de la falaise)
           "h": "heath", "e": "stairs",                    # (la lande du plateau, l'escalier qui franchit la paroi)
           "m": "sea"}                                     # (la mer : de l'eau, mais d'une autre couleur que l'eau douce)

# Terrains qui ne se touchent jamais. Les planches sont à plat, la falaise est un mur de craie vu de face : une
# promenade qui se fondrait dans la falaise n'a pas de sens (Christophe, 12 novembre 2026 : « il ne faut pas de
# liaison possible entre les planches et les falaises »). valider() refuse la carte, donc l'éditeur aussi.
INCOMPATIBLES = [("planks", "chalk"), ("planks", "heath")]
_DITS = {"planks": "les planches", "chalk": "la falaise", "heath": "le plateau"}

# ordre des clés dans le fichier (une clé inconnue est gardée, à la fin)
ORDRE = ["format", "annexe", "w", "h", "legende", "terrain", "details", "decor",
         "items", "dig", "enemies", "signs", "tunnels",
         "hens", "ducks", "cows", "critters", "butterflies", "villagers",
         "start", "alice", "title", "ending",
         "farmer", "postman", "neighbor", "pompon", "leon", "iris", "piquette", "papa",
         "letters", "balls", "toys", "babies", "goal", "ballBox", "pen", "penGate", "track",
         "roadTunnels", "passages", "traffic", "roles", "calm", "zones", "landmarks"]

# Les rôles qu'une carte distribue autrement (game.js : MAP.roles) : une quête du printemps rejouée avec d'autres
# acteurs. Sur la côte, le rôle de Mamie Rose (neighbor) est tenu par Madame Hortense, celui de Pompon par Praline,
# son caniche. { rôle : les acteurs permis }
ROLES = {"neighbor": ("hortense",), "pompon": ("poodle",), "farmer": ("anatole",), "postman": ("zoe",)}

# listes de taille fixe : « cinq lettres » et « cinq ballons » dans les dialogues (une couleur par ballon,
# port.BALL_COLORS), les jouets d'Iris (port.TOYS : poulet, anneau, corde, dans cet ordre), les places des petits
# hérissons auprès de leur maman (BABY.slots)
TAILLES = {"letters": 5, "balls": 5, "toys": 3, "babies": 3}
# listes dont la sauvegarde retient les éléments par leur rang : en ajouter à la fin, et ne pas en retirer au milieu
# sans changer SAVE_V dans game.js (sinon une partie en cours retrouve ses chiens, trésors… mélangés)
INDEXEES = ["enemies", "dig", "critters", "ducks", "letters", "hens", "balls", "toys", "babies"]
# les indices d'Alice (CLUES dans game.js) : exactement un de chaque, parmi les objets
INDICES = ("hairclip", "shoe", "plush")
# morceau (music.py : MORCEAUX) et ambiance d'une zone
MUSIQUES = ("niche", "village", "campagne", "ferme", "industrie", "foret", "parc",
            "cote", "port", "ville", "falaises", "plage")          # (les cinq derniers : la côte de l'été)
# détails au sol déduits d'autres données (jamais dans « details »)
DETAILS_DEDUITS = ("traces de pattes", "trou creusé (trésor)")
# décors déduits d'autres données (jamais dans « decor »)
DECORS_DEDUITS = ("signpost", "burrow", "goal_net", "rail", "buffer_stop")

# personnages et repères : un point (x, y) chacun
POINTS = ["start", "alice", "title", "farmer", "postman", "neighbor", "pompon", "leon", "iris", "piquette", "goal"]
# points qu'une carte peut avoir en plus (jamais exigés, même sur la carte du monde) : le papa d'Alice, qui attend
# au parking de la côte
POINTS_LIBRES = ["papa"]
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
    "piquette": "piquette/idle", "papa": "papa/idle", "goal": "decor/goal_net", "roadTunnels": "decor/tunnel",
}


def genres():
    """Genres permis pour chaque liste nommée (ceux que pack_web.collect() dessine dans l'atlas)."""
    import butterflies
    import chiens2
    import cows
    import critters
    import decor
    import ducks
    import hens
    import items
    import tiles
    import vehicles
    import villageois
    return {
        "decor": [n for n in decor.DECOR if n not in DECORS_DEDUITS],
        "items": [n for n in items.ITEMS if n != "goldbone"],
        "enemies": list(chiens2.CHIENS),
        "hens": list(hens.COLORS) + ["sheep"],            # (les moutons d'Anatole, sur la côte : moutons.py)
        "ducks": list(ducks.KINDS),
        "cows": list(cows.KINDS),
        "critters": [k for k in critters.KINDS if k not in ("cat_white", "poodle")],      # (le chat blanc, c'est Pompon ; le caniche, Praline)
        "butterflies": list(butterflies.COLORS),
        "villagers": list(villageois.KINDS),
        "vehicles": [n for n in vehicles.VEHICLES if n not in ("loco",) and not n.startswith("wagon")],
        "details": [n for n, _ in tiles.OVERLAYS if n not in DETAILS_DEDUITS],
    }


# ------------------------------------------------------------------ lecture, vérification
def chemin(nom):
    """Le fichier de la carte `nom`."""
    return FICHIER if nom == MONDE else os.path.join(DOSSIER, nom + ".json")


def noms():
    """Les cartes du jeu : celle du monde d'abord, puis les annexes par ordre alphabétique."""
    autres = sorted(f[:-5] for f in os.listdir(DOSSIER) if f.endswith(".json")) if os.path.isdir(DOSSIER) else []
    return [MONDE] + autres


def surcharge(nom, episode):
    """Le fichier de la surcharge de la carte `nom` pour un épisode (qu'il existe ou non)."""
    return os.path.join(DOSSIER, episode, nom + ".json")


def surcharges():
    """Les surcharges du dépôt : [(épisode, carte)], par ordre alphabétique."""
    out = []
    for ep in sorted(os.listdir(DOSSIER)) if os.path.isdir(DOSSIER) else []:
        d = os.path.join(DOSSIER, ep)
        if os.path.isdir(d):
            out += [(ep, f[:-5]) for f in sorted(os.listdir(d)) if f.endswith(".json")]
    return out


def appliquer(c, s):
    """La carte c changée par la surcharge s : chaque clé de s remplace celle de c, une clé à null est retirée."""
    c = dict(c)
    for k, v in s.items():
        if v is None:
            c.pop(k, None)
        else:
            c[k] = v
    return c


def difference(c, base):
    """La surcharge qui fait passer de la carte `base` à la carte c : les clés qui changent, null pour celles que c
    n'a plus (l'inverse d'appliquer(), pour l'éditeur)."""
    s = {k: v for k, v in c.items() if k not in FIXES and _norme(v) != _norme(base.get(k))}
    s.update({k: None for k in base if k not in c and k not in FIXES})
    return s


def valider_surcharge(s, base):
    """Les erreurs d'une surcharge posée sur la carte `base` (vide : tout va bien)."""
    if not isinstance(s, dict):
        return ["un objet JSON"]
    err = [f"{k} : une surcharge ne change pas cette clé" for k in s if k in FIXES]
    err += [f"{k} : identique à la carte de base (à retirer de la surcharge)" for k, v in s.items()
            if k in base and _norme(v) == _norme(base[k])]
    err += [f"{k} : null retire une clé que la carte de base n'a pas" for k, v in s.items() if v is None and k not in base]
    return err or valider(appliquer(base, s), variante=True)


def charger_episode(nom, episode=None, verifier=True):
    """La carte `nom` telle qu'un épisode la joue : la carte de base, changée par sa surcharge s'il y en a une."""
    c = charger(chemin(nom), verifier)
    f = surcharge(nom, episode) if episode else None
    if not f or not os.path.exists(f):
        return c
    with open(f, encoding="utf-8") as fd:
        s = json.load(fd)
    if verifier:
        err = valider_surcharge(s, c)
        if err:
            raise ValueError(f"{os.path.relpath(f, ROOT)} : " + " ; ".join(err[:12]))
    return appliquer(c, s)


# ce qu'une carte annexe peut ne pas avoir, et ce qui en tient lieu (hors de la carte, ou rien)
_LISTES = ["details", "decor", "items", "dig", "enemies", "signs", "tunnels", "hens", "ducks", "cows", "critters",
           "butterflies", "villagers", "letters", "balls", "toys", "babies", "roadTunnels", "passages", "calm", "landmarks"]
_RECT = [HORS, HORS, HORS + 1, HORS + 1]


def completer(c):
    """La carte avec tout ce que pack_web.py attend : ce qu'une carte annexe ne déclare pas est mis hors de la carte
    (un point en (HORS, HORS)) ou vide, et « absents » en donne la liste (personnages, enclos, voie, route, fin…)."""
    c = dict(c)
    absents = [k for k in POINTS + ["pen", "ballBox", "track", "traffic", "ending"] if k not in c]
    for k in _LISTES:
        c.setdefault(k, [])
    absents += [k for k in POINTS_LIBRES if k not in c]
    for k in POINTS + POINTS_LIBRES:
        c.setdefault(k, [HORS, HORS])
    c.setdefault("pen", list(_RECT))
    c.setdefault("ballBox", list(_RECT))
    c.setdefault("penGate", [HORS, HORS + 1])
    c.setdefault("track", None)
    c.setdefault("traffic", None)
    c.setdefault("ending", {"alice": [HORS, HORS], "tecky": [HORS, HORS]})
    c.setdefault("roles", {})
    c["absents"] = absents
    return c


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


def valider(c, avec_genres=True, variante=False):
    """Liste des erreurs (vide si la carte est correcte). variante : la carte d'un épisode (une carte de base sous
    sa surcharge), qui peut avoir perdu des personnages ou les indices."""
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
        # terrains qui ne se touchent jamais (INCOMPATIBLES) : aucune tuile n'a un coin de l'un et un coin de l'autre
        nom = {v: k for k, v in LEGENDE.items()}
        for a, b in INCOMPATIBLES:
            la, lb = nom[a], nom[b]
            ou = [(x, y) for y in range(h) for x in range(w)
                  if la in (q := t[y][x] + t[y][x + 1] + t[y + 1][x] + t[y + 1][x + 1]) and lb in q]
            if ou:
                err.append(f"terrain : {_DITS.get(a, a)} et {_DITS.get(b, b)} ne se touchent jamais ({len(ou)} tuile(s), la première en {ou[0][0]}, {ou[0][1]}) : "
                           "laisser entre eux au moins un coin d'un autre terrain")
    g = genres() if avec_genres else None
    annexe = c.get("annexe") is True
    if "annexe" in c and not annexe:
        err.append("annexe : true, ou rien (la carte du monde)")
    la = lambda cle: not (annexe or variante) or cle in c     # (une carte annexe n'a que ce qu'elle déclare)

    def liste(cle, forme, nom):
        if not la(cle) or (cle == "passages" and cle not in c):
            return []
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
        if cle in TAILLES and la(cle) and len(v) != TAILLES[cle]:
            err.append(f"{cle} : exactement {TAILLES[cle]} (il y en a {len(v)})")
    for i, (x, y) in enumerate(e for e in c.get("dig", []) if _pt(e)):
        if (x % 1, y % 1) != (0.5, 0.5):
            err.append(f"dig[{i}] ({x}, {y}) : un trésor est au centre d'une tuile (x,5 ; y,5)")
    for cle in POINTS:
        if la(cle) and not _pt(c.get(cle)):
            err.append(f"{cle} : un point [x, y]")
    for cle in POINTS_LIBRES:
        if cle in c and not _pt(c[cle]):
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
        if la(cle) and not rect(c.get(cle)):
            err.append(f"{cle} : un rectangle [x0, y0, x1, y1]")
    if rect(c.get("pen")) and not all(isinstance(a, int) for a in (c["pen"][0], c["pen"][2])):
        err.append("pen : x0 et x1 entiers (une clôture par tuile)")
    pg = c.get("penGate")
    if la("pen") and not (isinstance(pg, list) and len(pg) == 2 and all(isinstance(a, int) for a in pg) and pg[0] < pg[1]):
        err.append("penGate : [x0, x1] entiers")
    tr = c.get("track")
    if la("track") and not (isinstance(tr, list) and len(tr) == 3 and all(_num(a) for a in tr) and tr[0] < tr[1]):
        err.append("track : [x ouest, x est, y]")
    e = c.get("ending")
    if la("ending") and not (isinstance(e, dict) and _pt(e.get("alice")) and _pt(e.get("tecky")) and ("from" not in e or _pt(e["from"]))):
        err.append("ending : {alice: [x, y], tecky: [x, y], from?: [dx, dy] (d'où ils arrivent, à partir de leur place)}")
    r = c.get("traffic")
    if not la("traffic"):
        pass
    elif not (isinstance(r, dict) and isinstance(r.get("y"), int) and 0 < r["y"] < h - 3
            and isinstance(r.get("crossings"), list) and all(isinstance(x, int) for x in r["crossings"])
            and isinstance(r.get("vehicles"), list)):
        err.append("traffic : {y: première rangée de la route, crossings: [x], vehicles: [[véhicule, voie, x]]}")
    elif "fin" in r and not (isinstance(r["fin"], int) and 4 < r["fin"] < w - 6):
        err.append("traffic.fin : le x (entier) où la route s'arrête, devant le porche du parking")
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
    for role, acteur in (c.get("roles") or {}).items():
        if acteur not in ROLES.get(role, ()):
            err.append(f"roles : « {role} » ne peut pas être tenu par « {acteur} » ({', '.join(f'{k} : {v[0]}' for k, v in ROLES.items())})")
    # passages : [n° d'un tunnel de la route (roadTunnels), carte d'arrivée, n° de son tunnel d'arrivée]
    nt = len(c["roadTunnels"]) if isinstance(c.get("roadTunnels"), list) else 0
    for i, e in enumerate(liste("passages", lambda e: isinstance(e, list) and len(e) == 3 and isinstance(e[0], int)
                                and isinstance(e[1], str) and isinstance(e[2], int), "[n° du tunnel, carte, n° du tunnel d'arrivée]")):
        if isinstance(e, list) and len(e) == 3 and isinstance(e[0], int) and not 0 <= e[0] < nt:
            err.append(f"passages[{i}] : pas de tunnel n° {e[0]} sur cette carte")
    if annexe and not c.get("passages"):
        err.append("passages : une carte annexe a au moins un passage (sinon on n'y arrive jamais)")
    if isinstance(c.get("items"), list) and not annexe and not variante:
        for n in INDICES:
            k = sum(1 for it in c["items"] if isinstance(it, list) and it and it[0] == n)
            if k != 1:
                err.append(f"items : exactement un indice « {n} » (il y en a {k})")
    for i, d in enumerate(c.get("decor", [])):
        if nomme(d) and d[0] == "bridge" and not (float(d[1]).is_integer() and float(d[2]).is_integer()):
            err.append(f"decor[{i}] : le pont se pose sur une position entière")
        if nomme(d) and d[0] == "bridge_h" and (d[1] % 1, d[2] % 1) != (0.5, 0.5):
            err.append(f"decor[{i}] : le pont en travers se pose au milieu d'une tuile (x,5 ; y,5)")
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
    import sys
    for nom in noms():                    # chaque carte du jeu : correcte, et au format de l'éditeur
        f = chemin(nom)
        fichier = os.path.relpath(f, ROOT)
        c = charger(f, verifier=False)
        err = valider(c)
        if not err and (c.get("annexe") is True) != (nom != MONDE):
            err = ["« annexe » : la carte du monde ne l'est pas, les autres le sont"]
        if err:
            raise SystemExit(fichier + " :\n  " + "\n  ".join(err))
        avant = open(f, encoding="utf-8").read()
        if texte(c) == avant:
            print(fichier + " : ok")
        elif "--verifier" in sys.argv:
            raise SystemExit(fichier + " : pas au format normalisé (python3 carte.py le réécrit)")
        else:
            enregistrer(c, f)
            print(fichier + " réécrit au format normalisé")
    for ep, nom in surcharges():          # chaque surcharge d'épisode : pose une carte correcte, ne redit rien
        f = surcharge(nom, ep)
        fichier = os.path.relpath(f, ROOT)
        if nom not in noms():
            raise SystemExit(fichier + " : pas de carte « " + nom + " »")
        with open(f, encoding="utf-8") as fd:
            avant = fd.read()
        s = json.loads(avant)
        err = valider_surcharge(s, charger(chemin(nom), verifier=False))
        if err:
            raise SystemExit(fichier + " :\n  " + "\n  ".join(err))
        if texte(s) == avant:
            print(fichier + " : ok")
        elif "--verifier" in sys.argv:
            raise SystemExit(fichier + " : pas au format normalisé (python3 carte.py le réécrit)")
        else:
            enregistrer(s, f)
            print(fichier + " réécrit au format normalisé")
