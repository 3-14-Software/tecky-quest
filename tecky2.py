"""
Tecky, version 2 — le teckel du jeu web (PLAN_V2.md, lot 3).

Les trois vues (profil tourné vers la droite, dont la gauche est le miroir ; face, vers la caméra ; dos) sont relevées
sur la planche générée par Christophe (reference/v2/chat_gpt/, « Planche d'expressions ») : un gros crâne rond, un
museau court qui remonte vers une grosse truffe, de grands yeux, des oreilles immenses qui descendent plus bas que le
menton, un corps en saucisse sur des pattes très courtes, le harnais rouge à anneau. Mes deux premières têtes,
dessinées de mémoire (museau en coin, petit œil), ont été jugées « vraiment moches » : en cas de retouche, repartir
de la planche, pas de l'imagination. De profil, la tête n'a qu'un œil, comme sur la planche.

Le dessin est plus grand que les 48 x 48 des autres personnages : il est réduit de ECH dans le jeu (CADRE).
Les noms et les vues des animations (ANIMS, REST_ANIMS) sont ceux que le moteur appelle : tests/heros.py les garde.

    python3 tecky2.py      # reference/v2/tecky_v2.png (têtes, vues, poses) et tecky_v2_anims.png (toutes les images)
"""
import math
import os
import re

from spritelib import Drawing, circle, ellipse, path, poly, line, OUTLINE

W, H = 80, 52            # cadre du dessin (le profil, la vue la plus large)
SOL = 46                 # ligne du sol, dans les trois vues
ECH = 0.5                # réduction du dessin dans le jeu. Sa taille se juge à côté d'Alice et des chiens, pas seul :
                         # à 0,8 puis 0,7, Christophe l'a trouvé « énorme », à 0,58 (la taille de l'ancien Tecky)
                         # « encore trop gros ». Ici : plus petit que tous les chiens, la tête sous la jupe d'Alice.
TRAIT = 1.8 / ECH        # contour : une fois réduit, la même épaisseur que celui des autres personnages
X0 = 30.0                # axe des vues de face et de dos
TETE = (52.7, 15.1, 7.86)    # profil : centre du crâne et son rayon (les formes de la tête sont en rayons du crâne)

# Le jeu : vue -> (largeur, hauteur, origine x, origine y) du cadre, en unités de l'atlas (celles des 48 x 48 des
# autres personnages), et x du dessin posé sur cette origine. L'origine est aux pieds, comme avant.
CADRE = {"right": (48, 48, 24, 44), "down": (48, 48, 24, 44), "up": (48, 48, 24, 44)}
AXE = {"right": 33.0, "down": X0, "up": X0}

PAL = dict(
    fur="#D0672C", dark="#A64A20", ombre="#B4571F", light="#F2A968", ventre="#E28C4E",
    nose="#2A1611", white="#FFFFFF", iris="#3E1B0F", sourcil="#6B2F14",
    mouth="#7C1F1F", tongue="#F58A98", tongue_dk="#E0667A",
    harness="#DB352C", harness_dk="#B02620", ring="#F5C651",
)

# nom : (sourcils, yeux, bouche, tête relevée en degrés)
EXPRESSIONS = {
    "content": ("doux", "ouverts", "sourire", 0),
    "inquiet": ("inquiets", "ouverts", "moue", 0),
    "fier":    ("doux", "fermes", "grand_sourire", 20),
    "surpris": ("hauts", "ronds", "oh", 0),
    "endormi": ("bas", "fermes", "petit_oh", -4),
    "aboie":   ("doux", "ouverts", "ouverte", 9),
    "joyeux":  ("doux", "ouverts", "haletante", 3),      # gueule entrouverte, langue : il trotte, content
}
GUEULES = {"ouverte": 1.0, "haletante": 0.6, "oh": 0.44, "petit_oh": 0.28}     # ouverture de la gueule (0..1)


def pose(**kw):
    """Réglages d'une image.
    pas : avancée du cycle de marche (0..1) ; pattes : à la place, ((dx, levée) des pattes avant loin, proche) ;
    queue, oreille (vers l'arrière ; de face : vers l'extérieur), penche (de face : les deux oreilles du même côté),
    releve (tête relevée), tangage (le torse pique du nez) : degrés ; tete : (dx, dy) ; rebond, elan : le corps
    monte, avance ; expr : une des EXPRESSIONS, que yeux ("fermes", "croix", "plisses", "mi_clos", "ronds") et
    gueule (ouverture 0..1,3) remplacent ; traits : les petits traits de l'aboiement ;
    attitude : "debout", "assis", "couche", "dos" (sur le dos, KO) ; souffle : respiration du dormeur (0..1) ;
    gratte : (x, y) de la patte arrière qui gratte (assis de profil), vite : ses traits de vitesse (0 ou 1) ;
    herisse : hauteur des poils ébouriffés, poils : leur phase ; de face et de dos : balance (le haut du corps part
    de côté, en unités), incline (la tête penche, en degrés)."""
    base = dict(pas=None, pattes=None, queue=0.0, expr="content", tete=(0.0, 0.0), oreille=0.0, penche=0.0,
                rebond=0.0, elan=0.0, releve=0.0, tangage=0.0, traits=False, yeux=None, gueule=None,
                attitude="debout", souffle=0.0, gratte=None, vite=0, herisse=0.0, poils=0.0, balance=0.0, incline=0.0)
    base.update(kw)
    return base


# ====================================================================== OUTILS
def _trace(place, d):
    """Tracé SVG dont les points « x,y » passent par la fonction place (pas d'arcs : leurs rayons y passeraient)."""
    def f(m):
        x, y = place(float(m.group(1)), float(m.group(2)))
        return f"{x:.2f},{y:.2f}"
    return re.sub(r"(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)", f, d)


def _ovale(place, cx, cy, rx, ry, rot=0.0):
    """Ellipse (centre, rayons, inclinaison en degrés) rendue en tracé, ses points passés par place."""
    a = math.radians(rot)
    k = 0.5523

    def pt(u, v):
        x, y = place(cx + u * rx * math.cos(a) - v * ry * math.sin(a), cy + u * rx * math.sin(a) + v * ry * math.cos(a))
        return f"{x:.2f},{y:.2f}"
    return (f"M{pt(1, 0)} C{pt(1, k)} {pt(k, 1)} {pt(0, 1)} C{pt(-k, 1)} {pt(-1, k)} {pt(-1, 0)} "
            f"C{pt(-1, -k)} {pt(-k, -1)} {pt(0, -1)} C{pt(k, -1)} {pt(1, -k)} {pt(1, 0)} Z")


def _ici(x, y):
    return x, y


def _tourne(a, cx, cy, puis=_ici):
    """Fonction de placement : rotation de a degrés autour de (cx, cy) (sens de rotate() en SVG), puis `puis`."""
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
    return lambda x, y: puis(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca)


def _membre(x1, y1, x2, y2, w1, w2):
    """Patte en biais : de (x1, y1), largeur w1, à (x2, y2), largeur w2."""
    L = math.hypot(x2 - x1, y2 - y1) or 1
    nx, ny = -(y2 - y1) / L, (x2 - x1) / L
    return poly([(x1 + nx * w1 / 2, y1 + ny * w1 / 2), (x2 + nx * w2 / 2, y2 + ny * w2 / 2),
                 (x2 - nx * w2 / 2, y2 - ny * w2 / 2), (x1 - nx * w1 / 2, y1 - ny * w1 / 2)])


def _cerne(d, *formes):
    """Contour de formes posées par-dessus d'autres (la tête devant le poitrail), aussi épais que le contour extérieur."""
    for f in formes:
        d.raw(f.replace('fill="%F%"', f'fill="{OUTLINE}" stroke="{OUTLINE}" stroke-width="{TRAIT:.2f}" stroke-linejoin="round"'))


def _pics(pts, k, ph):
    """Poils ébouriffés : dents de hauteur ~k le long d'une suite de (x, y, nx, ny) (point, direction des pics).
    À ajouter en silhouette AVANT la forme hérissée : seules les dents dépassent."""
    out = []
    for i, (x, y, nx, ny) in enumerate(pts):
        s = k * (0.75 + 0.35 * math.sin(ph + i * 2.3)) if i % 2 else -1.0
        out.append((x + nx * s, y + ny * s))
    return out


def _pics_arc(cx, cy, rx, ry, k, ph, a0, a1, n):
    """Les mêmes dents sur l'arc a0..a1 (degrés) d'une ellipse ; le polygone se referme par son centre."""
    pts = []
    for i in range(2 * n + 1):
        t = math.radians(a0 + (a1 - a0) * i / (2 * n))
        pts.append((cx + rx * math.cos(t), cy + ry * math.sin(t), math.cos(t), math.sin(t)))
    return [(cx, cy)] + _pics(pts, k, ph)


def _foulee(p, ampli=3.0, levee=2.4):
    """Cycle de marche : (avancée, levée) de la paire A (arrière proche + avant loin) et de la paire B (l'inverse).
    Une patte posée recule sous le corps ; elle se lève pour revenir vers l'avant."""
    if p["pas"] is None:
        return (0.0, 0.0), (0.0, 0.0)
    a = p["pas"] * 2 * math.pi
    return ((ampli * math.cos(a), max(0.0, -math.sin(a)) * levee),
            (ampli * math.cos(a + math.pi), max(0.0, -math.sin(a + math.pi)) * levee))


def _doigts(d, x, y, s=1):
    """Les deux petits traits des doigts, sur le bout clair d'une patte."""
    d.raw(line(f"M{x - 0.7 * s:.2f},{y - 0.9:.2f} L{x - 0.5 * s:.2f},{y + 0.9:.2f} "
               f"M{x + 0.8 * s:.2f},{y - 0.5:.2f} L{x + 0.9 * s:.2f},{y + 0.7:.2f}", OUTLINE, 0.45))


# ====================================================================== LA PLANCHE
# Les trois vues sont relevées sur la planche de Christophe (reference/v2/chat_gpt/, « Planche d'expressions ») : les
# tracés ci-dessous sont écrits en pixels de cette image (le sol y est à y = 506), 7 pixels pour une unité du dessin.
def _pt(x, y, x0=45.0, ax=6.0):
    """Point de la planche -> unités du dessin (x0, en pixels, posé en ax)."""
    return (x - x0) / 7 + ax, SOL - (506 - y) / 7


def _pl(d):
    """Tracé relevé sur la vue de profil de la planche -> unités du dessin."""
    return _trace(_pt, d)


# ====================================================================== PROFIL
CORPS = _pl("M120,378 C150,369 200,365 250,366 C290,366 325,366 345,368 C368,372 380,395 376,420 "
            "C372,445 358,465 338,474 L285,476 C240,478 190,474 150,468 C122,472 100,462 92,445 "
            "C83,425 88,398 104,385 C109,381 114,379 120,378 Z")
CUISSE = (17.7, 36.6, 5.9, 6.1)                     # la cuisse arrière : centre et rayons
QUEUE = _pl("M90,404 C68,390 50,360 48,322 C47,300 52,287 63,284 C73,282 80,290 78,302 C75,330 86,356 120,380 Z")
QUEUE_PIVOT = _pt(102, 392)
VENTRE = _pl("M150,446 C190,452 240,458 290,452 L305,452 L305,500 L150,500 Z")      # elle finit derrière la patte avant
POITRAIL = _pl("M352,350 L388,366 C382,395 382,420 372,440 C364,456 350,468 338,474 "
               "C348,455 354,430 352,405 C350,385 348,366 352,350 Z")
PLI_CUISSE = _pl("M165,418 C173,435 171,455 160,468")
SANGLE = _pl("M242,355 L270,355 L272,482 L244,482 Z")                    # sangle du ventre
SANGLE_OMBRE = _pl("M262,355 L270,355 L272,482 L264,482 Z")
DORSALE = _pl("M226,355 L288,355 L288,381 L226,381 Z")
BRETELLE = _pl("M292,362 L320,362 C332,395 352,422 378,440 L362,466 C336,446 310,410 292,362 Z")      # poitrail
ANNEAU = _pt(252, 369)
PATTES = (17.0, 22.2, 43.4, 47.4)                   # x des pattes : arrière proche, arrière loin, avant proche, avant loin
HANCHE = 38.5                                       # hauteur de leur attache, cachée dans le corps
EPAULE, GORGE = _pt(296, 366), _pt(374, 408)        # où le cou quitte le torse
ASSIS = -18              # inclinaison du torse assis (degrés)


def _torse(p):
    """Où va un point du torse (écrit pour Tecky debout), selon l'attitude."""
    att, b = p["attitude"], p["rebond"]
    if att == "couche":      # le ventre au sol ; le dos monte et descend avec la respiration
        k = 1 + 0.045 * p["souffle"]
        return lambda x, y: (x, SOL - (SOL - (y + 4.7)) * k)
    if att == "dos":         # retourné, le dos au sol
        return lambda x, y: (x, 72.0 - y + b)
    if att == "assis":       # le derrière au sol, le poitrail relevé
        return _tourne(ASSIS, 17.0, 41.0, lambda x, y: (x, y + 3.6 + b))
    return _tourne(p["tangage"], 32.0, 33.0, lambda x, y: (x + p["elan"], y + b))


def _patte(d, haut, fx, lever, couleur, coussin):
    """Une patte courte et dodue, de son attache au sol : un fût trapu et un gros pied arrondi tourné vers l'avant."""
    x, y = haut
    fy = SOL - 1.0 - lever
    d.add(path(f"M{x - 3.2:.2f},{y:.2f} C{x - 3.2:.2f},{y - 4.2:.2f} {x + 3.2:.2f},{y - 4.2:.2f} {x + 3.2:.2f},{y:.2f} "
               f"L{fx + 2.9:.2f},{fy - 0.6:.2f} L{fx - 2.9:.2f},{fy - 0.6:.2f} Z"), couleur)       # épaule arrondie
    _pied(d, fx + 1.0, fy - 0.2, couleur, coussin)


def _pied(d, x, y, couleur, coussin):
    d.add(ellipse(x, y, 4.0, 2.4), couleur)
    d.add(ellipse(x + 1.2, y + 0.4, 2.6, 1.7), coussin, sil=False)        # bout de la patte, plus clair
    _doigts(d, x + 1.7, y + 0.3)


def _cou(T, hx, hy, r, sens=1):
    """Le cou, des épaules à la tête (centre du crâne en hx, hy) : court, épais, il suit la tête où qu'elle aille."""
    (ax, ay), (ex, ey) = T(*EPAULE), T(*GORGE)
    bx, by = hx - 0.95 * r, hy + 0.30 * r * sens            # nuque
    cx, cy = hx + 0.14 * r, hy + 1.40 * r * sens            # gorge
    return (f"M{ax:.2f},{ay:.2f} C{ax + 1:.2f},{ay - 3 * sens:.2f} {bx - 2:.2f},{by + 2 * sens:.2f} {bx:.2f},{by:.2f} "
            f"L{cx:.2f},{cy:.2f} C{cx + 0.6:.2f},{cy + 2 * sens:.2f} {ex + 0.8:.2f},{ey - 3 * sens:.2f} {ex:.2f},{ey:.2f} Z")


def profil(p=None):
    """Tecky de profil, tourné vers la droite : debout, assis, couché ou sur le dos (p["attitude"])."""
    p = p or pose()
    c = PAL
    att = p["attitude"]
    d = Drawing(W, H)
    T = _torse(p)
    F = lambda s: path(_trace(T, s))
    sens = -1 if att == "dos" else 1
    r = TETE[2]
    AR, AR2, AV, AV2 = PATTES

    # la tête : attachée au torse (debout, assis) ou posée (couché, sur le dos), puis déplacée par la pose
    hx, hy = {"couche": (55.0, 34.0), "dos": (56.0, 37.4)}.get(att) or T(TETE[0], TETE[1])
    if att == "assis":       # il la tient droite, un peu en avant du cou incliné
        hx, hy = hx + 4.2, hy + 2.2
    hx, hy = hx + p["tete"][0], hy + p["tete"][1]

    # pattes du côté caché, plus sombres
    A, B = _foulee(p)
    av = p["pattes"] or (A, B)                                # pattes avant : loin, proche
    if att == "debout":
        _patte(d, T(AR2, HANCHE), AR2 + B[0], B[1], c["dark"], c["ombre"])
        _patte(d, T(AV2, HANCHE), AV2 + av[0][0], av[0][1], c["dark"], c["ombre"])
    elif att == "assis":
        _pied(d, 29.0, SOL - 1.2, c["dark"], c["ombre"])
        _patte(d, T(AV2, HANCHE), T(AV2, HANCHE)[0] + 0.8, 0, c["dark"], c["ombre"])
    elif att == "couche":
        _pied(d, 28.5, SOL - 1.2, c["dark"], c["ombre"])
        d.add(_membre(47, 43.4, 61.5, 44.0, 4.8, 4.2), c["dark"])
        _pied(d, 63.5, 44.2, c["dark"], c["ombre"])
    else:                    # sur le dos : les quatre fers en l'air
        for x, dx in ((AR2, -1.2), (AV2, 3.0)):
            hxp, hyp = T(x, 40)
            d.add(_membre(hxp, hyp, hxp + dx, hyp - 6.5, 5.6, 4.8), c["dark"])
            d.add(ellipse(hxp + dx + 1.0, hyp - 7.4, 3.6, 2.5), c["dark"])

    # queue : relevée en virgule (debout), ou qui traîne au sol
    q = p["queue"] + {"assis": -80, "couche": -74, "dos": -66}.get(att, 0)
    d.add(path(_trace(_tourne(q, QUEUE_PIVOT[0], QUEUE_PIVOT[1], T), QUEUE)), c["fur"])

    if p["herisse"]:         # poils ébouriffés le long du dos (il s'ébroue)
        k = p["herisse"]
        dents = [(17 + i * 30 / 22, 26.4, 0, -1) for i in range(23)]
        d.add(poly([T(x, y) for x, y in _pics(dents, k, p["poils"])] + [T(47, 31), T(17, 31)]), c["fur"])

    # corps : une longue saucisse, poitrail bombé à l'avant, ventre clair
    corps, cuisse = F(CORPS), path(_ovale(T, *CUISSE))
    cou = path(_cou(T, hx, hy, r, sens))
    d.clip("corps2", [corps, cuisse, cou])
    d.add(cou, c["fur"])
    d.add(corps, c["fur"])
    d.add(cuisse, c["fur"])
    d.add(F(VENTRE), c["light"], sil=False, clip="corps2")
    d.add(F(POITRAIL), c["light"], sil=False, clip="corps2")
    # la cuisse, par-dessus : elle arrondit l'arrière-train et cache le départ de la bande claire du ventre
    d.add(cuisse, c["fur"], sil=False, clip="corps2")
    d.raw(line(_trace(T, PLI_CUISSE), c["dark"], 0.8))

    # harnais rouge : sangle du ventre, sangle du poitrail, pièce du dos, anneau
    d.add(F(SANGLE), c["harness"], sil=False, clip="corps2")
    d.add(F(SANGLE_OMBRE), c["harness_dk"], sil=False, clip="corps2", opacity=0.6)
    d.add(F(BRETELLE), c["harness"], sil=False, clip="corps2")
    d.add(F(DORSALE), c["harness"], sil=False, clip="corps2")
    ax, ay = T(*ANNEAU)
    d.add(circle(ax, ay, 1.7), c["ring"], sil=False, edge=True)
    d.add(circle(ax, ay, 0.65), c["harness_dk"], sil=False)

    # pattes du côté visible
    if att == "debout":
        _patte(d, T(AR, HANCHE), AR + A[0], A[1], c["fur"], c["light"])
        _patte(d, T(AV, HANCHE), AV + av[1][0], av[1][1], c["fur"], c["light"])
    elif att == "assis":
        if p["gratte"] is None:
            _pied(d, 24.0, SOL - 1.2, c["fur"], c["light"])
        _patte(d, T(AV, HANCHE), T(AV, HANCHE)[0] + 1.2, 0, c["fur"], c["light"])
    elif att == "couche":
        _pied(d, 24.0, SOL - 1.2, c["fur"], c["light"])
        d.add(_membre(48, 44.0, 63.5, 44.6, 5.0, 4.4), c["fur"])
        _pied(d, 65.5, 44.6, c["fur"], c["light"])
    else:
        for x, dx in ((AR, -2.4), (AV, 2.0)):
            hxp, hyp = T(x, 40)
            patte, pied = _membre(hxp, hyp, hxp + dx, hyp - 7.5, 5.8, 5.0), ellipse(hxp + dx + 1.2, hyp - 8.4, 3.9, 2.6)
            _cerne(d, patte, pied)
            d.add(patte, c["fur"])
            d.add(pied, c["fur"])
            d.add(ellipse(hxp + dx + 2.3, hyp - 8.6, 2.2, 1.6), c["light"], sil=False)

    tete(d, p, hx, hy, r, sens)

    if p["gratte"] is not None:      # la patte arrière se lève et gratte derrière l'oreille, par-dessus elle
        gx, gy = p["gratte"]
        kx, ky = T(24.5, 35.5)                # le genou, remonté contre le ventre
        patte = _membre(kx, ky, gx, gy, 5.6, 4.2)
        pied = ellipse(gx, gy, 3.5, 2.3, f"rotate({math.degrees(math.atan2(gy - ky, gx - kx)):.1f} {gx:.2f} {gy:.2f})")
        _cerne(d, patte, pied)
        d.add(patte, c["fur"])
        d.add(pied, c["fur"])
        d.add(cuisse, c["fur"], sil=False)
        d.raw(line(_trace(T, PLI_CUISSE), c["dark"], 0.8))
        for k in (0, 1):             # petits traits de vitesse
            rr = 5.2 + 2.0 * k
            a0, a1 = math.radians(160 + 30 * p["vite"]), math.radians(225 + 30 * p["vite"])
            d.raw(line(f"M{gx + rr * math.cos(a0):.2f},{gy + rr * math.sin(a0):.2f} "
                       f"Q{gx + rr * 1.08 * math.cos((a0 + a1) / 2):.2f},{gy + rr * 1.08 * math.sin((a0 + a1) / 2):.2f} "
                       f"{gx + rr * math.cos(a1):.2f},{gy + rr * math.sin(a1):.2f}", OUTLINE, 0.9))
    return d


# ====================================================================== TÊTE DE PROFIL
# Les formes de la tête sont écrites dans son propre repère : origine au centre du crâne, unité = son rayon, x vers
# la truffe, y vers le bas. `_repere` les place dans le dessin (et relève la tête autour de la nuque).
# Relevées sur la planche : un gros crâne rond, un museau court qui part du bas du visage et remonte vers une grosse
# truffe, un grand œil, une oreille immense qui descend plus bas que le menton.
NUQUE = (-0.5, 0.9)


def _repere(cx, cy, r, releve, sens=1):
    """sens = -1 : la tête est à l'envers (Tecky sur le dos)."""
    a = math.radians(-releve)
    ca, sa = math.cos(a), math.sin(a)

    def place(x, y):
        dx, dy = x - NUQUE[0], y - NUQUE[1]
        return cx + (NUQUE[0] + dx * ca - dy * sa) * r, cy + sens * (NUQUE[1] + dx * sa + dy * ca) * r
    return place


# Contours de la tête. Gueule fermée : crâne, museau et menton d'un seul tenant. Gueule ouverte : le bas du museau
# devient la lèvre, et la mâchoire (_gueule) est une forme à part, dessinée avant.
# Le museau avance, le bas du visage recule : la mâchoire s'arrête à MENTON, bien en retrait de la truffe (qui va
# jusqu'à 2,1), et la bouche, ouverte ou fermée, ne dépasse jamais ce point. Sinon la gueule pend sous le museau.
MENTON = 1.20
HAUT = ("M-0.80,-0.90 C-0.56,-1.05 -0.20,-1.08 0.10,-1.00 C0.46,-0.90 0.76,-0.62 0.90,-0.22 "
        "C0.93,-0.15 0.97,-0.12 1.04,-0.10 C1.22,-0.06 1.40,0.00 1.54,0.05 "
        "C1.76,0.10 1.98,0.32 1.98,0.58 C1.95,0.76 1.86,0.88 1.75,0.96 C1.62,1.05 1.42,1.12 1.20,1.16 ")
ARRIERE = "C-0.30,1.42 -0.72,1.16 -0.94,0.70 C-1.14,0.25 -1.10,-0.50 -0.80,-0.90 Z"
FERMEE = HAUT + "C1.00,1.24 0.75,1.32 0.50,1.37 C0.36,1.40 0.22,1.42 0.12,1.42 " + ARRIERE
OUVERTE = HAUT + "C0.90,1.15 0.55,1.06 0.34,0.90 C0.26,1.10 0.18,1.30 0.12,1.42 " + ARRIERE
LEVRE = "M1.20,1.16 C0.90,1.15 0.55,1.06 0.34,0.90"
CLAIR = "M2.4,0.38 L1.60,0.38 C1.40,0.43 1.10,0.46 0.60,0.54 C0.20,0.63 -0.15,0.82 -0.42,1.12 L-0.7,2.4 L2.4,2.4 Z"
OREILLE = ("M-0.76,-0.95 C-1.13,-0.80 -1.49,-0.33 -1.67,0.03 C-1.81,0.50 -1.86,0.94 -1.79,1.33 "
           "C-1.68,1.68 -1.40,1.86 -1.10,1.88 C-0.80,1.86 -0.52,1.62 -0.40,1.30 C-0.33,1.00 -0.31,0.50 -0.31,0.03 "
           "C-0.31,-0.20 -0.31,-0.42 -0.32,-0.55 C-0.40,-0.85 -0.58,-0.98 -0.76,-0.95 Z")
OREILLE_PLI = "M-0.98,-0.50 C-1.36,0.00 -1.56,0.70 -1.46,1.36 C-1.22,0.80 -1.02,0.20 -0.98,-0.50 Z"
OREILLE_PIVOT = (-0.56, -0.82)
OEIL = (0.30, -0.04, 0.39, 0.46)                   # centre et rayons de l'œil
TRUFFE = (1.78, 0.32, 0.36, 0.31, 12)


def _gueule(place, o):
    """Mâchoire, intérieur et langue d'une gueule ouverte de o (0..1,3). La mâchoire pend sous la lèvre, de la
    commissure (près de la joue) jusqu'à MENTON : plus courte que le museau, elle ne vient jamais sous la truffe."""
    m = MENTON
    machoire = (f"M0.22,0.86 L{m + 0.02:.2f},1.13 C{m + 0.12:.2f},{1.15 + 0.42 * o:.2f} {m + 0.04:.2f},{1.22 + 0.74 * o:.2f} "
                f"{m - 0.22:.2f},{1.28 + 0.78 * o:.2f} C{m - 0.48:.2f},{1.32 + 0.80 * o:.2f} 0.36,{1.26 + 0.70 * o:.2f} "
                f"0.26,{1.14 + 0.46 * o:.2f} C0.18,{1.06 + 0.20 * o:.2f} 0.18,0.96 0.22,0.86 Z")
    dedans = (f"M0.40,0.93 L{m - 0.07:.2f},1.15 C{m - 0.02:.2f},{1.16 + 0.34 * o:.2f} {m - 0.10:.2f},{1.17 + 0.60 * o:.2f} "
              f"{m - 0.28:.2f},{1.19 + 0.66 * o:.2f} C{m - 0.48:.2f},{1.20 + 0.70 * o:.2f} 0.50,{1.12 + 0.60 * o:.2f} "
              f"0.44,{1.04 + 0.40 * o:.2f} C0.40,{1.00 + 0.20 * o:.2f} 0.38,0.97 0.40,0.93 Z")
    langue = (f"M0.56,{1.14 + 0.50 * o:.2f} C0.66,{1.06 + 0.34 * o:.2f} 0.94,{1.10 + 0.30 * o:.2f} {m - 0.14:.2f},{1.16 + 0.36 * o:.2f} "
              f"C{m - 0.12:.2f},{1.20 + 0.50 * o:.2f} {m - 0.24:.2f},{1.22 + 0.62 * o:.2f} 0.80,{1.22 + 0.66 * o:.2f} "
              f"C0.66,{1.22 + 0.66 * o:.2f} 0.54,{1.20 + 0.60 * o:.2f} 0.56,{1.14 + 0.50 * o:.2f} Z")
    sillon = f"M0.74,{1.12 + 0.42 * o:.2f} C0.82,{1.16 + 0.48 * o:.2f} 0.86,{1.18 + 0.54 * o:.2f} 0.88,{1.20 + 0.60 * o:.2f}"
    return _trace(place, machoire), _trace(place, dedans), _trace(place, langue), _trace(place, sillon)


def _visage(p):
    """(sourcils, yeux, bouche, ouverture de la gueule, tête relevée) d'une pose : son expression, puis ce que la
    pose remplace."""
    sourcils, yeux, bouche, releve = EXPRESSIONS[p["expr"]]
    ouverte = GUEULES.get(bouche, 0)
    if p["gueule"] is not None:
        ouverte = p["gueule"] if p["gueule"] > 0.08 else 0
        if not ouverte and bouche in GUEULES:
            bouche = "sourire"
    return sourcils, p["yeux"] or yeux, bouche, ouverte, releve + p["releve"]


def tete(d, p, cx, cy, r, sens=1):
    """La tête de Tecky de profil, centre du crâne en (cx, cy), rayon r, avec l'expression de la pose."""
    c = PAL
    sourcils, yeux, bouche, ouverte, releve = _visage(p)
    place = _repere(cx, cy, r, releve, sens)
    T = lambda s: _trace(place, s)
    ep = r * 0.105                                    # épaisseur des traits du visage

    if p["herisse"]:                                   # poils ébouriffés sur le haut du crâne
        dents = [(-0.05 + 1.0 * math.cos(math.radians(a)), -0.05 + 1.0 * math.sin(math.radians(a)),
                  math.cos(math.radians(a)), math.sin(math.radians(a))) for a in range(200, 331, 13)]
        k = p["herisse"] / r
        d.add(poly([place(0, 0)] + [place(x, y) for x, y in _pics(dents, k, p["poils"] + 4)]), c["fur"])

    if ouverte:
        machoire, dedans, langue, sillon = _gueule(place, ouverte)
        d.clip("gueule", [path(dedans)])
        d.add(path(machoire), c["light"])
        d.add(path(dedans), c["mouth"], sil=False, edge=True)
        d.add(path(langue), c["tongue"], sil=False, clip="gueule")
        d.raw(f'<g clip-path="url(#gueule)">' + line(sillon, c["tongue_dk"], ep * 0.8) + "</g>")

    contour = T(OUVERTE if ouverte else FERMEE)
    d.clip("tete", [path(contour)])
    d.add(path(contour), c["fur"])
    d.add(path(T(CLAIR)), c["light"], sil=False, clip="tete")

    # truffe : grosse, au bout du museau, qu'elle dépasse
    d.add(path(_ovale(place, *TRUFFE)), c["nose"])
    d.add(path(_ovale(place, 1.70, 0.20, 0.10, 0.05, 6)), c["white"], sil=False, opacity=0.9)

    # bouche
    if ouverte:                                        # la lèvre : le bas du museau, au-dessus de la gueule ouverte
        d.raw(line(T(LEVRE), OUTLINE, ep))
    elif bouche == "moue":
        d.raw(line(T(f"M0.46,1.12 C0.60,0.97 0.90,0.99 {MENTON:.2f},1.15"), OUTLINE, ep))            # le coin tombe
    else:
        # le sourire suit la lèvre, entre le museau et la mâchoire, et son coin remonte dans la joue
        coin = (0.24, 0.80) if bouche == "grand_sourire" else (0.34, 0.90)
        d.raw(line(T(f"M{coin[0]:.2f},{coin[1]:.2f} C{coin[0] + 0.16:.2f},1.06 0.85,1.15 {MENTON:.2f},1.15"), OUTLINE, ep))
        d.add(path(_ovale(place, coin[0], coin[1], 0.055, 0.055)), OUTLINE, sil=False)

    # l'œil : un seul, la tête est de profil. Grand, haut et ovale, l'iris tourné vers l'avant.
    ex, ey, rx, ry = OEIL
    if yeux == "fermes":                               # paupière close : un arc qui pend, comme un sourire
        d.raw(line(T(f"M{ex - rx * 0.95:.2f},{ey:.2f} Q{ex:.2f},{ey + ry * 0.7:.2f} {ex + rx * 0.95:.2f},{ey:.2f}"), OUTLINE, ep))
    elif yeux == "croix":                              # KO
        s = rx * 0.66
        d.raw(line(T(f"M{ex - s:.2f},{ey - s:.2f} L{ex + s:.2f},{ey + s:.2f} M{ex - s:.2f},{ey + s:.2f} L{ex + s:.2f},{ey - s:.2f}"),
                   OUTLINE, ep * 1.15))
    elif yeux == "plisses":                            # « > » : serré très fort, la pointe vers le museau
        d.raw(line(T(f"M{ex - rx * 0.8:.2f},{ey - ry * 0.6:.2f} L{ex + rx * 0.65:.2f},{ey:.2f} L{ex - rx * 0.8:.2f},{ey + ry * 0.6:.2f}"),
                   OUTLINE, ep * 1.15))
    else:
        g = 1.1 if yeux == "ronds" else 1.0            # surpris : l'œil s'agrandit, la pupille non
        d.add(path(_ovale(place, ex, ey, rx * g, ry * g)), c["white"], sil=False)
        d.raw(line(_ovale(place, ex, ey, rx * g, ry * g), OUTLINE, ep))
        haut = -0.05 if sourcils == "inquiets" else 0.04
        # l'iris, grand et sombre, tourné vers l'avant : le blanc se voit en croissant, derrière et dessous
        d.add(path(_ovale(place, ex + rx * 0.22, ey + ry * haut, rx * 0.70, ry * 0.72)), c["iris"], sil=False)
        d.add(path(_ovale(place, ex + rx * 0.44, ey - ry * 0.30, rx * 0.25, ry * 0.22)), c["white"], sil=False)
        d.add(path(_ovale(place, ex - rx * 0.02, ey + ry * 0.36, rx * 0.10, ry * 0.09)), c["white"], sil=False, opacity=0.8)
        if yeux == "mi_clos":                          # paupière à demi baissée, de plaisir
            Rx, Ry, bas = rx * 1.14, ry * 1.14, ey + ry * 0.10
            kx, ky = 0.5523 * Rx, 0.5523 * Ry
            d.add(path(T(f"M{ex - Rx:.2f},{bas:.2f} C{ex - Rx:.2f},{bas - ky * 1.4:.2f} {ex - kx:.2f},{ey - Ry:.2f} {ex:.2f},{ey - Ry:.2f} "
                         f"C{ex + kx:.2f},{ey - Ry:.2f} {ex + Rx:.2f},{bas - ky * 1.4:.2f} {ex + Rx:.2f},{bas:.2f} Z")), c["fur"], sil=False)
            d.raw(line(T(f"M{ex - Rx:.2f},{bas:.2f} Q{ex:.2f},{bas + ry * 0.2:.2f} {ex + Rx:.2f},{bas:.2f}"), OUTLINE, ep))

    # sourcil, au-dessus de l'œil (inquiet : le bout tourné vers le museau remonte)
    d.raw(line(T({
        "doux":     "M0.04,-0.62 Q0.14,-0.75 0.36,-0.73",
        "inquiets": "M0.02,-0.58 Q0.18,-0.70 0.42,-0.80",
        "hauts":    "M0.04,-0.70 Q0.16,-0.84 0.36,-0.80",
        "bas":      "M0.04,-0.54 Q0.18,-0.62 0.38,-0.58",
    }[sourcils]), c["sourcil"], ep * 1.1))

    # oreille : immense, accrochée tout en haut à l'arrière du crâne, plus sombre que le pelage
    bascule = _tourne(p["oreille"], OREILLE_PIVOT[0], OREILLE_PIVOT[1], place)     # elle part en arrière autour de son attache
    if sens < 0:                                       # sur le dos : elle s'étale sur le sol, sans passer dessous
        libre = bascule
        bascule = lambda x, y: (libre(x, y)[0], min(libre(x, y)[1], SOL - 0.6))
    d.add(path(_trace(bascule, OREILLE)), c["dark"], edge=True)
    d.add(path(_trace(bascule, OREILLE_PLI)), c["fur"], sil=False, opacity=0.28)

    if p["traits"]:                                    # « ouaf ! »
        d.raw(line(T("M1.80,1.22 L2.30,1.12 M1.78,1.50 L2.30,1.58 M1.64,1.76 L2.04,2.06"), OUTLINE, ep * 1.3))


# ====================================================================== FACE (vers la caméra)
# La tête de face, autour de son centre (unités du dessin) : plus large aux joues qu'au front.
CRANE_F = ("M0,-9.9 C5,-9.9 8.9,-5.7 8.9,0 C8.9,4.3 8.3,7.1 6.9,8.6 C5,9.9 2.6,10.1 0,10.1 "
           "C-2.6,10.1 -5,9.9 -6.9,8.6 C-8.3,7.1 -8.9,4.3 -8.9,0 C-8.9,-5.7 -5,-9.9 0,-9.9 Z")
MASQUE_F = "M-9.5,6.2 C-6.4,4.3 -4.3,3.3 -2.9,3.1 L2.9,3.1 C4.3,3.3 6.4,4.3 9.5,6.2 L9.5,11 L-9.5,11 Z"
# Oreille gauche (à gauche de l'image) ; la droite est son miroir.
OREILLE_F = ("M-6.4,-7.7 C-7.4,-7.8 -8.2,-7.6 -8.75,-7.3 C-10.4,-6.4 -11.6,-5.4 -12.5,-4.3 C-13.8,-2.8 -14.6,-1.2 -15.0,0.4 "
             "C-15.6,2.2 -15.9,4.0 -15.9,5.7 C-15.9,7.6 -15.4,9.2 -14.5,10.4 C-13.7,11.6 -12.6,12.5 -11.4,12.9 "
             "C-10.4,13.1 -9.5,12.8 -8.9,12.1 C-8.2,11.2 -7.8,10.1 -7.8,8.9 C-7.9,7.4 -8.3,6.0 -8.4,4.6 "
             "C-8.6,2.2 -8.6,-0.4 -8.6,-2.9 C-8.3,-4.8 -7.5,-6.4 -6.4,-7.7 Z")
OREILLE_F_PLI = "M-10.6,-4.0 C-13.0,-1.4 -14.4,3.0 -13.8,8.0 C-12.2,4.6 -11.0,0.2 -10.6,-4.0 Z"
OREILLE_F_PIVOT = (-7.6, -6.6)
SOURCILS_F = {       # (dedans, milieu, dehors) : hauteur du sourcil au-dessus de l'œil
    "doux": (5.3, 6.4, 4.8), "inquiets": (6.5, 6.0, 4.3), "hauts": (6.2, 7.3, 5.7), "bas": (4.6, 5.2, 4.2),
}
OEIL_F = (4.8, -0.7, 2.5, 3.1)                     # écart à l'axe, hauteur, rayons


def _oreilles(d, p, place, forme, pli, pivot, devant=False):
    """Les deux grandes oreilles, de face ou de dos (place : fonction de placement de la tête)."""
    c = PAL
    for s in (-1, 1):                                  # s = -1 : l'oreille à gauche de l'image
        a = p["oreille"] - s * p["penche"]
        pl = _tourne(a, pivot[0], pivot[1], lambda x, y, s=s: place(-s * x, y))
        d.add(path(_trace(pl, forme)), c["dark"], edge=devant)
        d.add(path(_trace(pl, pli)), c["fur"], sil=False, opacity=0.28)


def tete_face(d, p, hx, hy):
    """La tête de Tecky vue de face, centre en (hx, hy) ; p["incline"] la penche de côté."""
    c = PAL
    sourcils, yeux, bouche, m, _ = _visage(p)
    ep = 0.82
    rot = _tourne(p["incline"], hx, hy + 9.0)
    place = lambda x, y: rot(hx + x, hy + y)
    T = lambda s: _trace(place, s)

    _oreilles(d, p, place, OREILLE_F, OREILLE_F_PLI, OREILLE_F_PIVOT)
    if p["herisse"]:
        d.add(poly([rot(x, y) for x, y in _pics_arc(hx, hy, 8.9, 9.9, p["herisse"], p["poils"] + 4, 200, 340, 6)]), c["fur"])
    crane = path(T(CRANE_F))
    formes = [crane]
    if m:                                              # la mâchoire descend sous la tête
        formes.append(path(_ovale(place, 0, 7.0 + m * 1.7, 4.6, 2.9 + m * 1.7)))
    _cerne(d, *formes)
    d.clip("tetef", formes)
    for f in formes[::-1]:
        d.add(f, c["light"] if f is not crane else c["fur"])
    d.add(path(T(MASQUE_F)), c["light"], sil=False, clip="tetef")

    ex0, ey, rx, ry = OEIL_F
    for s in (-1, 1):
        ex = s * ex0
        if yeux == "fermes":
            d.raw(line(T(f"M{ex - 2.4:.2f},{ey:.2f} Q{ex:.2f},{ey + 2.3:.2f} {ex + 2.4:.2f},{ey:.2f}"), OUTLINE, ep))
        elif yeux == "croix":
            d.raw(line(T(f"M{ex - 1.9:.2f},{ey - 1.9:.2f} L{ex + 1.9:.2f},{ey + 1.9:.2f} "
                         f"M{ex - 1.9:.2f},{ey + 1.9:.2f} L{ex + 1.9:.2f},{ey - 1.9:.2f}"), OUTLINE, ep * 1.15))
        elif yeux == "plisses":                        # « > < » : les pointes vers la truffe
            d.raw(line(T(f"M{ex + s * 2.1:.2f},{ey - 1.9:.2f} L{ex - s * 1.8:.2f},{ey:.2f} L{ex + s * 2.1:.2f},{ey + 1.9:.2f}"),
                       OUTLINE, ep * 1.15))
        else:
            g = 1.1 if yeux == "ronds" else 1.0
            d.add(path(_ovale(place, ex, ey, rx * g, ry * g)), c["white"], sil=False)
            d.raw(line(_ovale(place, ex, ey, rx * g, ry * g), OUTLINE, ep))
            ix = ex - s * 0.25                         # les iris louchent un rien vers la truffe : il nous regarde
            d.add(path(_ovale(place, ix, ey + 0.35, 1.8, 2.2)), c["iris"], sil=False)
            d.add(path(_ovale(place, ix + 0.35, ey - 0.65, 0.68, 0.68)), c["white"], sil=False)
            d.add(path(_ovale(place, ix - 0.65, ey + 1.25, 0.28, 0.28)), c["white"], sil=False, opacity=0.8)
            if yeux == "mi_clos":
                Rx, Ry, bas = rx * 1.14, ry * 1.14, ey + 0.4
                d.add(path(T(f"M{ex - Rx:.2f},{bas:.2f} C{ex - Rx:.2f},{bas - 2.4:.2f} {ex - 1.6:.2f},{ey - Ry:.2f} {ex:.2f},{ey - Ry:.2f} "
                             f"C{ex + 1.6:.2f},{ey - Ry:.2f} {ex + Rx:.2f},{bas - 2.4:.2f} {ex + Rx:.2f},{bas:.2f} Z")), c["fur"], sil=False)
                d.raw(line(T(f"M{ex - Rx:.2f},{bas:.2f} Q{ex:.2f},{bas + 0.7:.2f} {ex + Rx:.2f},{bas:.2f}"), OUTLINE, ep))
        a, b, e = SOURCILS_F[sourcils]
        d.raw(line(T(f"M{ex - s * 1.5:.2f},{ey - a:.2f} Q{ex:.2f},{ey - b:.2f} {ex + s * 1.2:.2f},{ey - e:.2f}"), c["sourcil"], ep * 1.1))

    # gueule : sous la truffe, dans le bas clair du visage
    if m:
        g = path(T(f"M-2.9,6.5 Q0,7.6 2.9,6.5 Q3.4,{6.8 + m * 3.6:.2f} 0,{7.0 + m * 3.7:.2f} Q-3.4,{6.8 + m * 3.6:.2f} -2.9,6.5 Z"))
        d.clip("gueulef", [g])
        d.add(g, c["mouth"], sil=False, edge=True)
        d.add(path(_ovale(place, 0, 7.2 + m * 3.2, 2.0, 0.5 + m * 1.2)), c["tongue"], sil=False, clip="gueulef")
        d.raw(line(T("M0,5.7 L0,6.8"), OUTLINE, ep))
    elif bouche == "moue":
        d.raw(line(T("M0,5.7 L0,6.6 M-3.0,8.5 Q0,6.3 3.0,8.5"), OUTLINE, ep))
    else:
        k = 1.12 if bouche == "grand_sourire" else 1.0
        d.raw(line(T(f"M0,5.7 L0,7.7 M{-4.7 * k:.2f},6.1 Q{-2.6 * k:.2f},{7.0 + 1.4 * k:.2f} 0,7.7 "
                     f"Q{2.6 * k:.2f},{7.0 + 1.4 * k:.2f} {4.7 * k:.2f},6.1"), OUTLINE, ep))
    # truffe
    d.add(path(_ovale(place, 0, 3.7, 2.9, 2.05)), c["nose"], sil=False)
    d.add(path(_ovale(place, -0.95, 3.0, 0.9, 0.38)), c["white"], sil=False, opacity=0.9)


# Le corps de face : le poitrail, plus étroit aux épaules, et les deux pattes avant.
CORPS_F = ("M-5.2,23 L5.2,23 C6,27.5 9,30.5 9.6,34.8 C9.9,37.6 9.4,39.8 8.9,41.1 L-8.9,41.1 "
           "C-9.4,39.8 -9.9,37.6 -9.6,34.8 C-9,30.5 -6,27.5 -5.2,23 Z")
ECART = 5.9                                         # écart des pattes à l'axe, de face et de dos


def _pied_face(d, x, y, couleur, coussin, k=1.0):
    d.add(ellipse(x, y, 3.8 * k, 2.4 * k), couleur)
    if coussin:
        d.add(ellipse(x, y + 0.5 * k, 2.9 * k, 1.7 * k), coussin, sil=False)
        d.raw(line(f"M{x - 1.0 * k:.2f},{y - 0.5:.2f} L{x - 0.9 * k:.2f},{y + 1.2:.2f} "
                   f"M{x + 1.0 * k:.2f},{y - 0.5:.2f} L{x + 0.9 * k:.2f},{y + 1.2:.2f}", OUTLINE, 0.5))


def _patte_face(d, B, s, lever, avance, couleur, coussin, bx):
    """Une patte vue de face ou de dos : elle se lève, et avance (vers le bas de l'image, un rien plus grosse) ou
    recule (vers le haut, plus petite)."""
    tx, ty = B(s * ECART, 39.5)
    k = 1 + 0.06 * avance
    fx, fy = X0 + s * ECART + bx * 0.25, SOL - 1.0 - lever + 0.45 * avance
    d.add(path(f"M{tx - 3.1:.2f},{ty:.2f} L{tx + 3.1:.2f},{ty:.2f} L{fx + 2.9 * k:.2f},{fy - 0.6:.2f} L{fx - 2.9 * k:.2f},{fy - 0.6:.2f} Z"), couleur)
    _pied_face(d, fx + s * 0.3, fy - 0.1, couleur, coussin, k)
    return fx + s * 0.3, fy - 0.1, k


def _harnais_face(d, B, clip):
    """Deux bretelles qui descendent des épaules, se rejoignent sur le poitrail, puis filent entre les pattes."""
    c = PAL
    for s in (-1, 1):
        d.add(path(_trace(B, f"M{s * 10.2:.2f},30.2 L{s * 7.4:.2f},27.8 L0,33.0 L0,36.6 Z")), c["harness"], sil=False, clip=clip)
    d.add(path(_trace(B, "M-1.7,34.6 L1.7,34.6 L1.7,42 L-1.7,42 Z")), c["harness"], sil=False, clip=clip)


def _queue_dressee(y0, w0, w1, L, c):
    """Une queue dressée vue de face ou de dos, plantée en (0, y0) : large à la base (w0), effilée (w1 au bout),
    longue de L, le bout déporté de c — pas un bâton droit (Christophe). Rend (la forme fermée, le tracé de ses deux
    bords, sans la base). Sert aussi aux chiens (chiens2._fouet)."""
    bords = (f"M{-w0 / 2:.2f},{y0 + 1:.2f} Q{-w0 / 2 - 0.4:.2f},{y0 - L * 0.5:.2f} {c - w1 / 2:.2f},{y0 - L:.2f} "
             f"C{c - w1 / 2:.2f},{y0 - L - w1 * 0.75:.2f} {c + w1 / 2:.2f},{y0 - L - w1 * 0.75:.2f} {c + w1 / 2:.2f},{y0 - L:.2f} "
             f"Q{w0 / 2 + c * 0.8:.2f},{y0 - L * 0.5:.2f} {w0 / 2:.2f},{y0 + 1:.2f}")
    return bords + " Z", bords


def _arriere_face(d, c, p, bx, b):
    """Ce qu'on voit de Tecky derrière sa tête quand il est debout, face à nous : sa croupe, au loin, qui dépasse un
    peu au-dessus du crâne, et sa queue dressée. C'est la vue de dos à l'envers : là-bas, c'est la tête, plus petite,
    qui dépasse derrière la croupe. Sans eux, il paraissait plat, et assis (Christophe). Pas de pattes arrière : la
    croupe doit rester petite, plus étroite que le crâne (plus grosse, elle se lisait comme un bonnet)."""
    cx, cy = X0 - bx * 0.9, 11.4 + b * 0.6
    croupe = ellipse(cx, cy, 7.0, 9.0)
    d.clip("croupef", [croupe])
    Tq = _tourne(p["queue"], cx, cy - 7.0)
    place = lambda x, y: Tq(cx + x, cy + y)
    d.add(path(_trace(place, _queue_dressee(-6.0, 5.4, 3.4, 8.0, 2.2)[0])), c["fur"])
    d.add(croupe, c["fur"])
    d.add(ellipse(cx, cy - 4.6, 4.6, 3.6), c["ombre"], sil=False, clip="croupef", opacity=0.3)


def face(p=None):
    """Tecky de face, vers la caméra : debout, assis ou couché."""
    p = p or pose()
    c = PAL
    att = p["attitude"]
    d = Drawing(60, H)
    b, bx = p["rebond"], p["balance"]
    (aA, lA), (aB, lB) = _foulee(p, 1.0, 2.6)
    if p["pattes"]:
        (aA, lA), (aB, lB) = (0.0, p["pattes"][0][1]), (0.0, p["pattes"][1][1])
    B = lambda x, y: (X0 + x + bx * (SOL - y) / 22, y + b)      # le haut du corps se balance, les pieds restent
    hx = X0 + bx * 1.25 + p["tete"][0]
    hy = {"assis": 15.0, "couche": 34.8}.get(att, 15.9) + b + p["tete"][1]

    if att == "couche":      # le dos en dôme derrière la tête, les pattes arrière qui dépassent de chaque côté
        k = p["souffle"]
        for s in (-1, 1):
            _pied_face(d, X0 + s * 12.4, SOL - 1.4, c["fur"], None)
        dos_ = ellipse(X0, 33.6 - k * 0.5, 12.2 + k * 0.3, 11.2 + k * 0.6)
        d.clip("dosf", [dos_])
        d.add(dos_, c["fur"])
        d.add(path(f"M{X0 - 13:.2f},{28.6 - k * 0.5:.2f} Q{X0:.2f},{21.6 - k:.2f} {X0 + 13:.2f},{28.6 - k * 0.5:.2f} "
                   f"L{X0 + 13:.2f},{31.6 - k * 0.5:.2f} Q{X0:.2f},{24.6 - k:.2f} {X0 - 13:.2f},{31.6 - k * 0.5:.2f} Z"),
              c["harness"], sil=False, clip="dosf")
        for s in (-1, 1):    # les pattes avant, allongées sous le menton
            _pied_face(d, X0 + s * 6.2, SOL - 1.3, c["fur"], c["light"])
        tete_face(d, p, hx, hy)
        return d

    if att == "assis":       # la queue balaie le sol sur le côté, les cuisses posées de part et d'autre
        d.add(path(f"M{X0 + 6:.2f},{43.2:.2f} C{X0 + 11:.2f},{43.6:.2f} {X0 + 15:.2f},{42.4:.2f} {X0 + 17.6:.2f},{39.4:.2f} "
                   f"C{X0 + 18.6:.2f},{38.2:.2f} {X0 + 20.2:.2f},{39.4:.2f} {X0 + 19.4:.2f},{40.8:.2f} "
                   f"C{X0 + 16.6:.2f},{45.2:.2f} {X0 + 11:.2f},{46.4:.2f} {X0 + 6:.2f},{45.8:.2f} Z",
                   f"rotate({p['queue']:.1f} {X0 + 6:.2f} {44.5:.2f})"), c["fur"])
        for s in (-1, 1):
            _pied_face(d, X0 + s * 11.6, SOL - 1.3, c["fur"], None)
            d.add(ellipse(X0 + s * 9.0, 40.6 + b, 4.6, 5.2), c["fur"])

    if att == "debout":
        _arriere_face(d, c, p, bx, b)

    # pattes avant et poitrail
    for s, lv, a in ((-1, lA, aA), (1, lB, aB)):
        _patte_face(d, B, s * (0.9 if att == "assis" else 1), lv, a, c["fur"], c["light"], bx)
    poitrail = path(_trace(B, CORPS_F))
    if p["herisse"]:
        for a0, a1 in ((-60, 20), (160, 240)):
            d.add(poly(_pics_arc(X0 + bx * 0.5, 33.5 + b, 9.4, 8.0, p["herisse"], p["poils"] + a0, a0, a1, 3)), c["fur"])
    d.clip("poitrailf", [poitrail])
    d.add(poitrail, c["fur"])
    d.add(path(_ovale(B, 0, 34.0, 3.3, 8.5)), c["light"], sil=False, clip="poitrailf")
    _harnais_face(d, B, "poitrailf")

    tete_face(d, p, hx, hy)
    return d


# ====================================================================== DOS
CORPS_D = ("M-4.6,21 C-6.2,25.6 -9.0,30.5 -9.6,34.6 C-9.9,37.6 -9.4,39.8 -8.9,41.1 L8.9,41.1 "
           "C9.4,39.8 9.9,37.6 9.6,34.6 C9.0,30.5 6.2,25.6 4.6,21 Z")
QUEUE_D = _queue_dressee(32.4, 6.2, 3.8, 12.6, 2.6)     # la queue vue de dos : (forme, bords)
HARNAIS_D = ("M-10.5,33.2 C-6.5,29.6 -2.6,27.6 0,27.3 C2.6,27.6 6.5,29.6 10.5,33.2 L10.5,36.0 "
             "C6.5,32.2 2.6,30.2 0,29.9 C-2.6,30.2 -6.5,32.2 -10.5,36.0 Z")
# Oreille gauche vue de derrière, autour du centre du crâne ; la droite est son miroir.
OREILLE_D = ("M-6.1,-7.6 C-8.5,-7.0 -10.4,-5.2 -11.9,-3.3 C-13.4,-1.4 -14.4,0.8 -14.7,3.1 C-15.0,4.8 -15.0,6.6 -14.7,8.1 "
             "C-14.4,9.8 -13.6,11.0 -12.6,11.7 C-11.7,12.4 -10.6,12.6 -9.7,12.4 C-8.6,12.0 -7.7,11.3 -7.2,10.3 "
             "C-6.6,9.4 -6.3,8.4 -6.1,7.4 C-6.6,4.9 -7.3,2.2 -7.4,-0.5 C-7.4,-3.0 -6.9,-5.4 -6.1,-7.6 Z")
OREILLE_D_PLI = "M-9.6,-4.0 C-12.2,-1.4 -13.6,3.0 -13.0,7.6 C-11.4,4.4 -10.2,0.2 -9.6,-4.0 Z"
OREILLE_D_PIVOT = (-6.8, -6.4)


def dos(p=None):
    """Tecky de dos : la croupe et la queue devant nous, l'arrière de la tête entre ses deux grandes oreilles."""
    p = p or pose()
    c = PAL
    d = Drawing(60, H)
    b, bx = p["rebond"], p["balance"]
    (aA, lA), (aB, lB) = _foulee(p, 1.0, 2.6)
    if p["pattes"]:
        (aA, lA), (aB, lB) = (0.0, p["pattes"][0][1]), (0.0, p["pattes"][1][1])
    B = lambda x, y: (X0 + x + bx * (SOL - y) / 22, y + b)

    # pattes arrière : celle qui avance s'éloigne (vers le haut), et on voit ses coussinets quand elle se lève
    for s, lv, a in ((-1, lB, aB), (1, lA, aA)):
        fx, fy, k = _patte_face(d, B, s, lv, -a, c["fur"], None, bx)
        d.add(ellipse(fx, fy + 0.5, 2.5 * k, 1.4 * k + 0.5 * min(lv, 1.6)), c["ombre"], sil=False)

    # la tête, vue de derrière, plus haut : elle dépasse devant la croupe
    hx, hy = X0 + bx * 1.25 + p["tete"][0], 15.6 + b + p["tete"][1]
    rot = _tourne(p["incline"], hx, hy + 9.0)
    place = lambda x, y: rot(hx + x, hy + y)
    crane = path(_ovale(place, 0, 0, 7.2, 9.3))
    if p["herisse"]:
        d.add(poly([rot(x, y) for x, y in _pics_arc(hx, hy, 7.2, 9.3, p["herisse"], p["poils"] + 4, 200, 340, 6)]), c["fur"])
    d.add(crane, c["fur"])

    corps = path(_trace(B, CORPS_D))
    d.clip("corpsd", [corps])
    d.add(corps, c["fur"])
    d.add(path(_ovale(B, 0, 39.0, 4.3, 3.0)), c["light"], sil=False, clip="corpsd")
    d.add(path(_trace(B, HARNAIS_D)), c["harness"], sil=False, clip="corpsd")

    # la queue, dressée devant nous
    place_q = _tourne(p["queue"], 0, 32.5, B)
    d.add(path(_trace(place_q, QUEUE_D[0])), c["fur"])
    d.raw(line(_trace(place_q, QUEUE_D[1]), OUTLINE, 1.3))

    _oreilles(d, p, place, OREILLE_D, OREILLE_D_PLI, OREILLE_D_PIVOT, devant=True)
    return d


def portrait(p=None):
    """Le buste de Tecky de face, pour son portrait (hud.py) : cadre de 48 x 48, la tête et ses oreilles au milieu."""
    p = p or pose()
    c = PAL
    d = Drawing(48, 48)
    B = lambda x, y: (24 + x, y + 5.5)
    poitrail = path(_trace(B, CORPS_F))
    d.clip("poitrailp", [poitrail])
    d.add(poitrail, c["fur"])
    d.add(path(_ovale(B, 0, 34.0, 3.3, 8.5)), c["light"], sil=False, clip="poitrailp")
    _harnais_face(d, B, "poitrailp")
    tete_face(d, p, 24 + p["tete"][0], 20 + p["tete"][1])
    return d


VUES = {"right": profil, "down": face, "up": dos}
OMBRES = {      # ombre au sol : (demi-largeur, demi-hauteur, décalage en x), par vue puis par attitude
    "right": {"debout": (20, 2.6, -1.5), "assis": (19, 2.6, -3), "couche": (30, 2.6, 5.5), "dos": (29, 2.6, 5)},
    "down": {"debout": (10.5, 2.8, 0), "assis": (13.5, 3.0, 1), "couche": (15.5, 3.1, 0)},
    "up": {"debout": (10.5, 2.8, 0)},
}


def base(view):
    """Transformation qui pose le dessin dans le cadre du jeu : réduit de ECH, ses pieds sur l'origine."""
    w, h, ox, oy = CADRE[view]
    return f"translate({ox - AXE[view] * ECH:.2f} {oy - SOL * ECH:.2f}) scale({ECH})"


def image(view, p, tr=""):
    """SVG d'une image du jeu : la pose p dans la vue donnée, tr = transformation de plus (unités du dessin)."""
    w, h, ox, oy = CADRE[view]
    d = VUES[view](p)
    d.w, d.h = w, h
    rx, ry, dx = OMBRES[view][p["attitude"]]
    d.under.append(f'<ellipse cx="{ox + dx * ECH:.2f}" cy="{oy + 0.2:.2f}" rx="{rx * ECH:.2f}" ry="{ry * ECH:.2f}" fill="#000" opacity="0.2"/>')
    return d.svg(f"{base(view)} {tr}".strip(), outline_w=TRAIT)


# ====================================================================== ANIMATIONS
# chaque animation : fonction(view) -> liste de (pose, transformation de plus)
def a_idle(view):
    """Il attend : la queue bat, il respire, un clignement."""
    wag = [-7, 0, 7, 0] if view == "right" else [-14, 0, 14, 0]
    bob = [0, 0.3, 0.5, 0.3]
    return [(pose(rebond=bob[i], queue=wag[i], yeux="fermes" if i == 3 else None), "") for i in range(4)]


def a_walk(view):
    """Le trot, en 8 images : les pattes en diagonale, le dos qui ondule, la tête, les oreilles et la queue qui
    suivent avec un temps de retard, la langue au vent."""
    out = []
    for i in range(8):
        a = i / 8 * 2 * math.pi
        q = dict(pas=i / 8, rebond=-0.8 * abs(math.sin(a)))
        if view == "right":
            q.update(tangage=1.3 * math.sin(2 * a + 0.6), tete=(0, 0.5 * math.sin(2 * a - 0.9)),
                     oreille=4 + 6 * math.sin(2 * a - 1.4), queue=-4 + 8 * math.sin(a))
        else:                # de face, de dos : il se dandine, le poids sur la patte posée, la tête et les oreilles suivent
            k = -1 if view == "down" else 1
            q.update(balance=0.9 * k * math.sin(a), incline=4 * k * math.sin(a - 0.6), tete=(0, 0.5 * math.sin(2 * a - 0.9)),
                     oreille=4 + 5 * math.sin(2 * a - 1.4), penche=6 * k * math.sin(a - 1.0), queue=18 * k * math.sin(a - 0.5))
        out.append((pose(**q), ""))
    return out


def a_bark(view):
    """Ouaf : la tête se relève d'un coup, la gueule grande ouverte."""
    ms = [0.25, 0.8, 1.0, 0.45]
    up = [0, 6, 10, 3]
    out = []
    for i in range(4):
        if view == "right":
            out.append((pose(gueule=ms[i], releve=up[i], oreille=up[i] * 0.9, queue=-12, tete=(0.04 * up[i], -0.06 * up[i])), ""))
        else:
            out.append((pose(gueule=ms[i], tete=(0, -up[i] / 5), oreille=up[i] * 0.8, queue=12), ""))
    return out


def a_bite(view):
    """Morsure : recul, détente vers l'avant gueule ouverte, les mâchoires claquent, retour."""
    lunge = [-1.5, 3.0, 5.5, 4.0, 0.6]
    ms = [0.35, 1.0, 1.0, 0.0, 0.0]
    out = []
    for i in range(5):
        L, m = lunge[i], ms[i]
        if view == "right":
            out.append((pose(elan=L * 0.5, tete=(L * 0.7, 0.1 * L), gueule=m, oreille=max(0, L) * 3.2, queue=-10,
                             releve=2 if m else -2), f"translate({L * 0.5:.2f} 0)"))
        elif view == "down":
            out.append((pose(gueule=m, tete=(0, L * 0.6), oreille=max(0, L) * 2.2), f"translate(0 {L * 0.4:.2f})"))
        else:
            out.append((pose(tete=(0, -L * 0.7), oreille=max(0, L) * 2.2), f"translate(0 {-L * 0.35:.2f})"))
    return out


def a_hurt(view):
    """Aïe : les yeux serrés, les oreilles en arrière, un sursaut."""
    dx, dy = {"right": (-2.0, 0), "down": (0, -2.4), "up": (0, 2.4)}[view]
    return [(pose(expr="inquiet", yeux="plisses", oreille=16, queue=-16), f"translate({dx} {dy})"),
            (pose(expr="inquiet", yeux="plisses", oreille=9, queue=-10), f"translate({dx / 2} {dy / 2})")]


def a_ko(view):
    """Profil uniquement : il titube, bascule, et finit sur le dos, les quatre fers en l'air."""
    return [
        (pose(expr="inquiet", yeux="fermes", oreille=-8), "rotate(-7 30 46)"),
        (pose(expr="inquiet", yeux="croix", oreille=18, queue=-24, gueule=0.4), "translate(3 0) rotate(-20 30 46) translate(0 -1)"),
        (pose(attitude="dos", yeux="croix", gueule=0.7, oreille=60, queue=0), ""),
        (pose(attitude="dos", yeux="croix", gueule=0.7, oreille=63, queue=4, rebond=0.5), ""),
    ]


def a_dig(view):
    """Gratter le sol : la truffe au ras du sol, les pattes avant qui moulinent, la queue qui frétille."""
    out = []
    for i in range(6):
        a = i / 3 * 2 * math.pi             # deux cycles de pattes sur 6 images
        wag = 14 * math.sin(i / 6 * 4 * math.pi)
        mouline = ((4.5 + 3.4 * math.cos(a + math.pi), max(0.0, math.sin(a + math.pi)) * 3.4),
                   (4.5 + 3.4 * math.cos(a), max(0.0, math.sin(a)) * 3.4))
        if view == "right":
            out.append((pose(pattes=mouline, tangage=7, rebond=0.6, tete=(4.2, 9.5 + 0.5 * math.sin(a)), releve=-34,
                             oreille=-8 + 5 * math.sin(a), queue=-16 + wag), ""))
        elif view == "down":
            out.append((pose(pattes=mouline, rebond=0.5, tete=(0, 3.4 + 0.4 * math.sin(a)), oreille=5, queue=wag * 1.4), ""))
        else:
            out.append((pose(pattes=mouline, rebond=0.5, tete=(0, 2.0 + 0.4 * math.sin(a)), oreille=4, queue=wag * 1.4), ""))
    return out


ANIMS = {   # nom : (fonction, images par seconde, vues)
    "idle": (a_idle, 6, ("down", "up", "right")),
    "walk": (a_walk, 16, ("down", "up", "right")),
    "bark": (a_bark, 10, ("down", "up", "right")),
    "bite": (a_bite, 14, ("down", "up", "right")),
    "hurt": (a_hurt, 10, ("down", "up", "right")),
    "dig":  (a_dig, 14, ("down", "up", "right")),
    "ko":   (a_ko, 6, ("right",)),
}


def frames(anim, view):
    """Liste de SVG (chaînes) pour une animation et une vue ('right', 'down', 'up')."""
    return [image(view, p, tr) for p, tr in ANIMS[anim][0](view)]


# ---------------------------------------------------------------------- poses de repos
# Jouées quand le joueur ne touche à rien : même cadre et mêmes pieds que les animations ci-dessus.
def a_sit(view):
    """Assis : la queue balaie doucement le sol, petite respiration, un clignement sur 8 images."""
    out = []
    for i in range(8):
        a = i / 8 * 2 * math.pi
        out.append((pose(attitude="assis", queue=(7 if view == "right" else 10) * math.sin(a),
                         rebond=0.15 * (1 - math.cos(a)), yeux="fermes" if i == 5 else None), ""))
    return out


def a_yawn(view):
    """Assis, il bâille : les yeux fermés, la tête levée, la gueule grande ouverte, puis il referme."""
    ms = [0.0, 0.3, 0.8, 1.2, 1.3, 1.05, 0.4, 0.0]
    up = [0.0, 0.3, 0.7, 1.0, 1.0, 0.8, 0.3, 0.0]
    out = []
    for i in range(8):
        k = up[i]
        q = dict(attitude="assis", gueule=ms[i], yeux="plisses" if 2 <= i <= 5 else "fermes" if 0 < i < 7 else None)
        if view == "right":
            q.update(releve=20 * k, oreille=12 * k, tete=(-0.6 * k, -0.8 * k))
        else:
            q.update(tete=(0, -1.8 * k), oreille=6 * k)
        out.append((pose(**q), ""))
    return out


def a_scratch(view):
    """Assis de profil, il se gratte derrière l'oreille : la patte arrière mouline, l'œil mi-clos de plaisir."""
    out = []
    for i in range(4):
        a = i / 4 * 2 * math.pi
        out.append((pose(attitude="assis", gratte=(35.4 + 1.3 * math.cos(a), 27.4 + 1.3 * math.sin(a)), vite=i % 2,
                         tete=(-9.0, 7.6), releve=10, yeux="fermes", gueule=0.5, oreille=-6 + 6 * math.sin(a),
                         queue=6 * math.sin(2 * a), rebond=0.25 * math.sin(a)), ""))
    return out


def a_sleep(view):
    """Endormi : couché, les yeux fermés, la respiration lente. Le jeu ajoute les « Z »."""
    return [(pose(attitude="couche", expr="endormi", gueule=0, souffle=s, oreille=42 if view == "right" else 16,
                  releve=-2), "") for s in (0, 0.5, 1, 0.5)]


def a_shake(view):
    """Il s'ébroue : le corps se tord d'un côté puis de l'autre (deux bonnes secousses), les oreilles au vent, les
    poils hérissés, puis il se calme."""
    ks = [0.6, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -0.8, 0.5, -0.2]
    fl = [1.6, 2.4, 2.4, 2.4, 2.4, 2.4, 2.4, 2.2, 2.0, 1.7, 1.2, 0.8]
    out = []
    for i, k in enumerate(ks):
        q = dict(herisse=fl[i], poils=i * 1.9, yeux="plisses" if i < len(ks) - 1 else None, gueule=0.5 if i % 2 else 0.25)
        if view == "right":
            q.update(releve=8 * k, oreille=(34 if k > 0 else 78) * abs(k), queue=-10 - 16 * k, rebond=-0.4 * abs(k),
                     tangage=1.5 * k)
            tr = f"translate({0.9 * k:.2f} 0)"
        else:
            q.update(tete=(-1.6 * k, 0), oreille=22, penche=32 * k, queue=30 * k, balance=1.2 * k)
            tr = ""
        out.append((pose(**q), tr))
    return out


REST_ANIMS = {   # nom : (fonction, images par seconde, vues, boucle)
    "sit":     (a_sit, 6, ("down", "right"), True),
    "yawn":    (a_yawn, 8, ("down", "right"), False),
    "scratch": (a_scratch, 14, ("right",), True),
    "sleep":   (a_sleep, 3, ("down", "right"), True),
    "shake":   (a_shake, 16, ("down", "right"), False),
}


def rest_frames(anim, view):
    """Liste de SVG d'une pose de repos ('right' ou 'down' ; la gauche est le miroir de la droite)."""
    return [image(view, p, tr) for p, tr in REST_ANIMS[anim][0](view)]


# ---------------------------------------------------------------------- la nage
# Dans la mer, Tecky nage : le corps sous l'eau, la tête dressée, le haut du dos et la queue qui dépassent. Ce sont
# ses poses à lui (il pagaie, la truffe en l'air), dessinées enfoncées de ENFONCE et coupées à la ligne d'eau
# (LIGNE, en unités du cadre, au-dessus de l'origine), puis cerclées d'écume. Mêmes noms et mêmes nombres d'images
# que les animations de la terre ferme : le jeu ne change que la famille du sprite (« nage/… », sans ombre portée).
LIGNE = 5.0              # la ligne d'eau, au-dessus de l'origine du cadre
ENFONCE = {"right": 4.6, "down": 5.2, "up": 6.2}      # de combien le dessin descend sous l'eau
ECUME = ("#FFFFFF", "#DDF6F4")
ANNEAUX = {"right": (25.5, 15.0, 2.6), "down": (24.0, 9.6, 2.3), "up": (24.0, 9.6, 2.3)}     # écume : centre x, rayons


def _eau(view, i, n, fort=1.0):
    """L'écume autour du nageur, image i sur n : un rond qui s'élargit et s'efface derrière lui, le liseré contre
    son corps, et les éclaboussures de ses pattes avant, l'une après l'autre."""
    w, h, ox, oy = CADRE[view]
    y = oy - LIGNE
    cx, rx, ry = ANNEAUX[view]
    u = (i / n) % 1.0
    out = []
    for k in (0.0, 0.5):                    # deux ronds, décalés d'un demi-cycle
        v = (u + k) % 1.0
        out.append(f'<ellipse cx="{cx:.2f}" cy="{y + 0.6:.2f}" rx="{rx * (0.86 + 0.42 * v):.2f}" ry="{ry * (0.86 + 0.5 * v):.2f}" '
                   f'fill="none" stroke="{ECUME[1]}" stroke-width="{0.9 - 0.4 * v:.2f}" opacity="{0.75 * (1 - v) * fort:.2f}"/>')
    devant = (f'<path d="M{cx - rx * 0.8:.2f},{y + 0.5:.2f} Q{cx:.2f},{y + ry * 0.95:.2f} {cx + rx * 0.8:.2f},{y + 0.5:.2f}" fill="none" '
              f'stroke="{ECUME[0]}" stroke-width="1.1" stroke-linecap="round" opacity="0.9"/>')
    gouttes = ""
    if fort >= 1.0:                         # il pagaie : une gerbe à chaque coup de patte
        a = 2 * math.pi * u
        for sens, ph in ((1, 0.0), (-1, math.pi)):
            f = max(0.0, math.sin(a + ph))
            if f < 0.25:
                continue
            if view == "right":
                bx, by = cx + rx * (0.62 + 0.1 * sens), y + 0.6
            else:
                bx, by = cx + sens * rx * 0.78, y + (1.0 if view == "down" else -0.4)
            gouttes += "".join(f'<circle cx="{bx + dx:.2f}" cy="{by - dy * f:.2f}" r="{r:.2f}" fill="{ECUME[0]}" opacity="{0.9 * f:.2f}"/>'
                               for dx, dy, r in ((-1.2, 1.6, 0.55), (0.4, 2.6, 0.7), (1.7, 1.2, 0.5)))
    return "".join(out), devant + gouttes


def image_nage(view, p, tr="", i=0, n=8, fort=1.0):
    """SVG d'une image de nage : la pose p enfoncée dans l'eau et coupée à la ligne d'eau, l'écume autour."""
    w, h, ox, oy = CADRE[view]
    d = VUES[view](p)
    d.w, d.h = w, h
    svg = d.svg(f"{base(view)} {tr}".strip(), outline_w=TRAIT)
    dedans = svg[svg.index(">") + 1:svg.rindex("</svg>")]
    derriere, devant = _eau(view, i, n, fort)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<defs><clipPath id="hors_eau"><rect x="-20" y="-20" width="{w + 40}" height="{oy - LIGNE + 20:.2f}"/></clipPath></defs>'
            f'{derriere}<g clip-path="url(#hors_eau)"><g transform="translate(0 {ENFONCE[view]})">{dedans}</g></g>{devant}</svg>')


def n_walk(view):
    """Il nage : il pagaie, le corps roule un peu, la truffe en l'air, les oreilles qui flottent, la queue en gouvernail."""
    out = []
    for i in range(8):
        a = i / 8 * 2 * math.pi
        q = dict(pas=i / 8, rebond=0.5 * math.sin(a), gueule=0.0 if i % 4 else 0.3)
        if view == "right":
            q.update(releve=13 + 2 * math.sin(a), tangage=-3 + 1.2 * math.sin(a + 0.6), tete=(0.6, -1.4 + 0.4 * math.sin(a)),
                     oreille=16 + 6 * math.sin(a - 1.2), queue=-34 + 10 * math.sin(2 * a))
        else:
            k = -1 if view == "down" else 1
            q.update(balance=0.7 * k * math.sin(a), incline=3 * k * math.sin(a - 0.6), tete=(0, -1.0 + 0.4 * math.sin(a)),
                     oreille=20 + 5 * math.sin(a - 1.2), penche=4 * k * math.sin(a - 1.0), queue=14 * k * math.sin(a - 0.5))
        out.append((pose(**q), ""))
    return out


def n_idle(view):
    """Il fait du surplace : il monte et descend avec l'eau, cligne des yeux."""
    out = []
    for i in range(4):
        a = i / 4 * 2 * math.pi
        q = dict(rebond=0.7 * math.sin(a), yeux="fermes" if i == 3 else None, gueule=0.0)
        if view == "right":
            q.update(releve=10, tangage=-2, tete=(0.4, -1.0), oreille=14, queue=-30 + 6 * math.sin(a))
        else:
            q.update(tete=(0, -0.8), oreille=18, queue=10 * math.sin(a))
        out.append((pose(**q), ""))
    return out


def n_bark(view):
    """Ouaf, dans l'eau : la tête sort d'un coup, la gueule grande ouverte."""
    out = []
    for (p, tr), haut in zip(a_bark(view), (0.0, 1.2, 1.8, 0.6)):
        p["rebond"] = p["rebond"] + haut
        out.append((p, tr))
    return out


def n_hurt(view):
    """Aïe : il boit la tasse, les yeux plissés."""
    return [(pose(yeux="plisses", gueule=0.5, rebond=-0.8 + 0.6 * i, releve=6 if view == "right" else 0, oreille=30), "")
            for i in range(2)]


def n_ko(view):
    """KO dans l'eau : il flotte, les yeux en croix."""
    return [(pose(yeux="croix", gueule=0.35, rebond=0.4 * math.sin(i / 4 * 2 * math.pi), oreille=34, queue=-40), "")
            for i in range(4)]


def n_bite(view):
    """Il mord, dans l'eau : le coup de gueule de la terre ferme, sans l'élan des pattes."""
    return [(dict(p, elan=p["elan"] * 0.5), tr) for p, tr in a_bite(view)]


NAGE = {    # nom (celui de l'animation de la terre ferme) : (fonction, vues, force de l'écume)
    "idle": (n_idle, ("down", "up", "right"), 0.6),
    "walk": (n_walk, ("down", "up", "right"), 1.0),
    "bark": (n_bark, ("down", "up", "right"), 0.8),
    "bite": (n_bite, ("down", "up", "right"), 0.9),
    "hurt": (n_hurt, ("down", "up", "right"), 0.8),
    "ko":   (n_ko, ("right",), 0.5),
}


def nage_frames(anim, view):
    """Liste de SVG d'une animation de nage."""
    fn, _, fort = NAGE[anim]
    poses = fn(view)
    return [image_nage(view, p, tr, i, len(poses), fort) for i, (p, tr) in enumerate(poses)]


if __name__ == "__main__":
    from spritelib import render_svg, PAD
    from PIL import Image, ImageDraw, ImageFont
    racine = os.path.dirname(os.path.abspath(__file__))
    fond = (126, 200, 100, 255)
    police = ImageFont.truetype(os.path.join(racine, "fonts", "Fredoka.ttf"), 26)
    encre = (58, 30, 18, 255)

    def rangee(images, etiquettes=None, marge=28):
        h = max(i.height for i in images) + (marge if etiquettes else 0)
        im = Image.new("RGBA", (sum(i.width for i in images), h), fond)
        dessin = ImageDraw.Draw(im)
        x = 0
        for k, i in enumerate(images):
            im.alpha_composite(i, (x, h - i.height))
            if etiquettes:
                dessin.text((x + i.width / 2, 16), etiquettes[k], font=police, fill=encre, anchor="mm")
            x += i.width
        return im

    def planche(rangees, fichier):
        out = Image.new("RGBA", (max(r.width for r in rangees), sum(r.height for r in rangees)), fond)
        y = 0
        for r in rangees:
            out.alpha_composite(r, ((out.width - r.width) // 2, y))
            y += r.height
        fn = os.path.join(racine, "reference", "v2", fichier)
        out.convert("RGB").save(fn)
        print(fn, out.size)

    def vue(view, p, k=8):
        w, h, _, _ = CADRE[view]
        return render_svg(image(view, p), w, h, k, PAD)

    # 1. les six expressions (la tête seule, en grand), les trois vues, les poses de repos
    noms = ("content", "inquiet", "fier", "surpris", "endormi", "aboie")
    tetes = []
    for n in noms:
        d = Drawing(60, 52)
        tete(d, pose(expr=n, traits=n == "aboie"), 26, 20, 11)
        tetes.append(render_svg(d.svg(), 60, 52, 7, PAD))
    vues = [vue("right", pose()), vue("down", pose()), vue("up", pose()),
            vue("right", pose(pas=0.12, expr="joyeux", oreille=6, rebond=-0.6))]
    repos = [vue("right", a_sit("right")[0][0]), vue("down", a_sit("down")[0][0]),
             vue("right", a_sleep("right")[0][0]), vue("down", a_sleep("down")[0][0])]
    planche([rangee(tetes, noms), rangee(vues), rangee(repos)], "tecky_v2.png")

    # 2. toutes les images du jeu, à la taille d'un écran de 1920 x 1080 (x4)
    lignes = []
    for nom, (fn, _, views) in list(ANIMS.items()) + [(n, v[:3]) for n, v in REST_ANIMS.items()]:
        for v in views:
            w, h, _, _ = CADRE[v]
            src = frames(nom, v) if nom in ANIMS else rest_frames(nom, v)
            lignes.append(rangee([render_svg(s, w, h, 4, PAD) for s in src]))
    planche(lignes, "tecky_v2_anims.png")
