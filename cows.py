"""
Les vaches du grand pré de la campagne, version 2 : de profil, tournées vers la droite (la vue gauche est le miroir,
faite par le jeu). Cellule 64 x 48, pieds à y = 44 : origine conseillée (32, 44).

Elles sont de la famille du Tecky et des chiens de la v2 (tecky2.py, chiens2.py, dont elles reprennent les outils) :
aplats, grosse tête ronde, grand œil à iris sombre et reflet, pattes dodues, contour de l'épaisseur des autres sprites.
Et de vraies proportions de vache, en version mignonne : un gros corps en tonneau (garrot, croupe), des pattes courtes
et solides sur des sabots, un pis rose, une queue à toupet, de petites cornes, une oreille en feuille, un large mufle
rose, des taches, une cloche au cou. La cuisse est fondue dans le corps, avec un pli (pas de rond cerné).

Les formes sont écrites en pixels du jeu (x2) autour du milieu des pieds — x vers la droite, y vers le bas, le sol à
y = 0 — puis réduites de ECH ; le veau est la même vache réduite de VEAU autour de ses pieds, avec une tête plus grosse
en proportion, des bourgeons de cornes, ni pis ni cloche.

Espèces (KINDS) : cow_bw (pie noire), cow_brown (pie rouge, façon montbéliarde), calf (le veau).
Animations (anims(kind)[nom] = (poses, fps, boucle)) : idle (elle chasse les mouches avec la queue, bouge une oreille,
cligne), graze (la tête dans l'herbe, elle mâche), walk (les pattes en diagonale ; une patte posée recule, elle se
lève pour revenir vers l'avant), moo (tête levée, gueule ouverte : « Meuh ! »).

    python3 cows.py      # reference/v2/vaches_v2.png (les trois, toutes les images, et à la taille du jeu)
"""
import math
import os

from tecky2 import _trace, _ovale, _tourne, _foulee
from spritelib import Drawing, circle, ellipse, path, poly, line, OUTLINE

W, H = 64, 48
G = 44
KINDS = ("cow_bw", "cow_brown", "calf")
ECH = 0.5                # réduction du dessin dans le jeu : une unité du dessin = un pixel du jeu
TRAIT = 1.8 / ECH        # contour : une fois réduit, celui des autres sprites
VEAU = 0.64              # le veau : la vache réduite d'autant autour de ses pieds (sa tête, de VEAU_TETE seulement)
VEAU_TETE = 0.80
C = dict(white="#FFFDF7", white_dk="#E3DACB", muzzle="#F6B9B3", muzzle_dk="#D98C86", hoof="#5A4636", hoof_dk="#463528",
         horn="#F3E5C2", horn_dk="#D6C294", bell="#F2C14E", bell_dk="#C9962E", strap="#B9452F", iris="#3E1B0F",
         udder="#F6B9B3", mouth="#7C1F1F", tongue="#F58A98", blush="#F29A9A", pli="#A89E90")
SPOTS = {"cow_bw": ("#322D2E", "#211D1E"), "cow_brown": ("#B0602F", "#8A4722"), "calf": ("#CF9150", "#A9713A")}   # tache, pli

# --- le corps (vache adulte) : un tonneau, la croupe à gauche, le garrot et le poitrail à droite
CORPS = ("M-45,-57 C-36,-63 -20,-62 -6,-60 C3,-59 10,-63 18,-61 C26,-58 30,-49 29,-39 C28,-29 22,-22 12,-21 "
         "C0,-19.5 -14,-19 -27,-20 C-39,-21 -49,-27 -51,-38 C-52,-47 -50,-54 -45,-57 Z")
CUISSE = (-37, -33, 12.5, 16.5)                     # la cuisse arrière : centre et rayons
QUEUE = "M-44,-57.5 C-51.5,-59 -56,-52 -55.6,-41 L-54.8,-27 L-51.6,-27 L-52.4,-41 C-52.8,-50 -50,-54.5 -44,-54 Z"
QUEUE_PIVOT = (-46, -56)
TOUPET = (-53.2, -21.5, 3.4, 6.4)
PIS = "M-31,-23 C-32,-14 -27,-10 -21,-10 C-15,-10 -11,-14 -12,-22 Z"
TETINES = ((-25.5, -10.2), (-18.5, -10.4))
PATTES = (-37.0, -25.0, 10.0, 21.5)                 # x des pattes : arrière proche, arrière loin, avant proche, avant loin
HANCHE = -27.0                                      # hauteur de leur attache, cachée dans le corps
PATTE_L = (10.0, 8.8)                               # largeur d'une patte : en haut, au sabot
GARROT, POITRAIL = (9.0, -61.0), (26.0, -33.0)      # où l'encolure quitte le corps
TACHES = {
    "cow_bw": ("M-52,-62 C-40,-68 -25,-66 -19,-58 C-17,-48 -23,-41 -33,-41 C-44,-41 -54,-47 -52,-62 Z",
               "M-9,-47 C-1,-53 11,-51 13,-41 C14,-31 5,-25 -5,-28 C-13,-31 -15,-41 -9,-47 Z",
               "M-14,-64 C-8,-66 0,-65 3,-60 C-1,-55 -10,-55 -14,-59 Z",
               "M-30,-26 C-24,-28 -18,-26 -17,-21 L-17,-15 L-31,-15 Z"),
    "cow_brown": ("M-54,-50 C-50,-66 -34,-68 -22,-62 C-12,-56 -10,-44 -18,-38 C-28,-32 -42,-34 -54,-50 Z",
                  "M0,-66 C10,-68 22,-66 30,-58 C30,-48 24,-42 14,-44 C4,-46 -2,-56 0,-66 Z",
                  "M-6,-34 C0,-38 8,-36 9,-30 C8,-24 0,-22 -5,-24 C-9,-27 -9,-31 -6,-34 Z"),
}
TACHES["calf"] = TACHES["cow_brown"]

# --- la tête, de profil, dans son repère : origine au centre du crâne, unité = son rayon, x vers le mufle
TETE = (33.0, -55.0, 16.0)                          # centre du crâne et rayon (vache adulte, tête au repos)
PENTE = 24.0                                        # au repos, le mufle pointe vers le bas de PENTE degrés
HAUT = ("M-0.78,-0.80 C-0.42,-1.06 0.20,-1.06 0.56,-0.88 C0.86,-0.74 1.14,-0.56 1.42,-0.40 "
        "C1.70,-0.26 1.86,0.02 1.86,0.36 C1.86,0.52 1.84,0.64 1.80,0.74 ")
LEVRE = "C1.58,0.90 1.30,0.92 1.02,0.80 "
CONTOUR = HAUT + LEVRE + "C0.94,0.94 0.82,1.04 0.66,1.08 C0.30,1.14 -0.22,1.12 -0.62,0.88 C-1.02,0.58 -1.12,-0.38 -0.78,-0.80 Z"
MACHOIRE = ("M0.98,0.76 C1.30,0.92 1.58,0.90 1.80,0.74 C1.84,1.00 1.72,1.18 1.46,1.20 C1.20,1.22 0.96,1.16 0.78,1.06 "
            "C0.88,0.98 0.94,0.88 0.98,0.76 Z")
MACHOIRE_PIVOT = (0.84, 0.94)
BOUCHE = "M1.02,0.80 C1.30,0.92 1.58,0.90 1.80,0.74"
MUFLE = "M1.06,-0.9 C0.94,-0.2 0.94,0.5 1.04,1.4 L2.2,1.4 L2.2,-0.9 Z"
TACHE_TETE = "M-1.3,-1.3 L0.62,-1.3 C0.92,-0.62 0.86,0.02 0.42,0.28 C0.00,0.48 -0.60,0.32 -1.3,0.46 Z"
OREILLE = "M-0.50,-0.52 C-0.80,-0.98 -1.40,-1.08 -1.92,-0.70 C-1.62,-0.36 -1.10,-0.22 -0.60,-0.26 Z"
OREILLE_DEDANS = "M-0.76,-0.56 C-0.98,-0.80 -1.36,-0.84 -1.66,-0.68 C-1.44,-0.50 -1.10,-0.42 -0.82,-0.42 Z"
OREILLE_PIVOT = (-0.55, -0.40)
CORNE = "M-0.36,-0.94 C-0.50,-1.36 -0.30,-1.70 0.06,-1.80 C-0.04,-1.52 0.00,-1.24 0.10,-1.00 Z"
CORNE_LOIN = "M0.20,-1.00 C0.14,-1.34 0.32,-1.62 0.62,-1.70 C0.52,-1.44 0.54,-1.20 0.64,-0.94 Z"
BOURGEON = "M-0.30,-0.94 C-0.34,-1.16 -0.20,-1.28 -0.02,-1.26 C0.06,-1.16 0.08,-1.06 0.08,-0.98 Z"
OEIL = (0.40, -0.26, 0.33, 0.40)
NASEAU = (1.56, 0.06)
JOUE = (0.82, 0.44)


def cow(kind, p):
    """Une vache dans la pose p : head (0 tête au repos -> 1 dans l'herbe ; négatif : levée), chew (mâchoire, 0..1),
    pas (avancée du cycle de marche, 0..1), bob (balancement du corps), tail (angle de la queue, °), ear (oreille
    relevée, 0..1), blink, moo (gueule ouverte, 0..1)."""
    veau = kind == "calf"
    k = VEAU if veau else 1.0
    tache, pli = SPOTS[kind]
    d = Drawing(128, 96)
    AXE, SOL = 64.0, 88.0
    b = p.get("bob", 0.0)
    ici = lambda x, y: (AXE + x * k, SOL + y * k)                 # coordonnées de la vache -> dessin
    haut = 5.0 if veau else 0.0                                   # le veau est haut sur pattes
    T = lambda x, y: (AXE + x * k, SOL + (y + b) * k - haut)      # le corps se balance, pas les sabots
    F = lambda s: path(_trace(T, s))
    # (l'ombre, hors de la réduction : en unités du cadre)
    d.under.append(f'<ellipse cx="{32 - 4 * k:.2f}" cy="{G + 0.2:.2f}" rx="{22 * k:.2f}" ry="{2.8 * k:.2f}" fill="#000" opacity="0.2"/>')

    # --- la tête : où est-elle, et comment est-elle tournée ?
    h = p.get("head", 0.0)
    tx, ty, r = TETE
    if veau:
        r *= VEAU_TETE / VEAU                                     # une tête plus grosse en proportion
        tx, ty = tx - 2, ty + 3
    if h >= 0:           # du repos à l'herbe : elle descend devant le poitrail, le mufle vers le sol
        cx, cy, a = tx + 6.0 * h, ty + (21.5 if not veau else 20.0) * h, PENTE + 36.0 * h
    else:                # levée pour meugler
        cx, cy, a = tx + 2.0 * h, ty + 9.0 * h, PENTE + 46.0 * h
    hx, hy = T(cx, cy)
    place = _tourne(a, hx, hy, lambda x, y: (hx + (x - hx), hy + (y - hy)))
    tete = lambda x, y: place(hx + x * r * k, hy + y * r * k)     # repère de la tête -> dessin
    Th = lambda s: _trace(tete, s)

    # --- pattes du côté caché, plus sombres
    A, B = _foulee({"pas": p.get("pas")}, 5.0, 4.0)
    AR, AR2, AV, AV2 = PATTES

    def patte(x, pas, couleur, sabot):
        dx, lever = pas
        px, py = T(x, HANCHE)
        fx, fy = AXE + (x + dx) * k, SOL - (1.0 + lever) * k
        w1, w2 = PATTE_L[0] * k, PATTE_L[1] * k
        hs = 5.6 * k                                              # hauteur du sabot
        d.add(path(f"M{px - w1 / 2:.2f},{py:.2f} C{px - w1 / 2:.2f},{py - w1 * 0.6:.2f} {px + w1 / 2:.2f},{py - w1 * 0.6:.2f} "
                   f"{px + w1 / 2:.2f},{py:.2f} L{fx + w2 / 2:.2f},{fy - hs:.2f} L{fx - w2 / 2:.2f},{fy - hs:.2f} Z"), couleur)
        # le sabot : un peu plus large que la patte, arrondi devant
        d.add(path(f"M{fx - w2 / 2 - 0.5 * k:.2f},{fy - hs:.2f} L{fx + w2 / 2 + 0.3 * k:.2f},{fy - hs:.2f} "
                   f"C{fx + w2 / 2 + 2.2 * k:.2f},{fy - hs * 0.5:.2f} {fx + w2 / 2 + 2.2 * k:.2f},{fy + 1.0 * k:.2f} {fx + w2 / 2 - 0.4 * k:.2f},{fy + 1.0 * k:.2f} "
                   f"L{fx - w2 / 2 - 0.2 * k:.2f},{fy + 1.0 * k:.2f} C{fx - w2 / 2 - 1.2 * k:.2f},{fy + 1.0 * k:.2f} {fx - w2 / 2 - 1.2 * k:.2f},{fy - hs * 0.6:.2f} "
                   f"{fx - w2 / 2 - 0.5 * k:.2f},{fy - hs:.2f} Z"), sabot)

    patte(AR2, B, C["white_dk"], C["hoof_dk"])
    patte(AV2, A, C["white_dk"], C["hoof_dk"])

    # --- la queue et son toupet, derrière la croupe : elle chasse les mouches
    Tq = _tourne(p.get("tail", 0.0), QUEUE_PIVOT[0], QUEUE_PIVOT[1], T)
    d.add(path(_trace(Tq, QUEUE)), C["white"])
    d.add(path(_ovale(Tq, TOUPET[0], TOUPET[1], TOUPET[2], TOUPET[3], 6)), tache)

    # --- la corne et l'oreille du côté caché
    if not veau:
        d.add(path(Th(CORNE_LOIN)), C["horn_dk"])

    # --- le pis, devant la patte du fond
    if not veau:
        d.add(F(PIS), C["udder"])
        for x, y in TETINES:
            ax, ay = T(x, y)
            d.add(ellipse(ax, ay, 1.9, 2.6), C["udder"])

    # --- le corps, l'encolure, la cuisse ; les taches, gardées dans le corps
    corps, cuisse = F(CORPS), path(_ovale(T, *CUISSE))
    (gx, gy), (px_, py_) = T(*GARROT), T(*POITRAIL)
    (nx, ny), (jx, jy) = tete(-0.92, -0.30), tete(-0.30, 1.02)                  # nuque, gorge
    cou = path(f"M{gx:.2f},{gy:.2f} C{gx + 6 * k:.2f},{gy - 3 * k:.2f} {nx - 5 * k:.2f},{ny - 1 * k:.2f} {nx:.2f},{ny:.2f} "
               f"L{jx:.2f},{jy:.2f} C{jx - 1 * k:.2f},{jy + 6 * k:.2f} {px_ + 4 * k:.2f},{py_ - 5 * k:.2f} {px_:.2f},{py_:.2f} Z")
    cid = "vache" + kind
    d.clip(cid, [corps, cuisse, cou])
    d.add(cou, C["white"])
    d.add(corps, C["white"])
    d.add(cuisse, C["white"])
    for s in TACHES[kind]:
        d.add(F(s), tache, sil=False, clip=cid)
    cx_, cy_, rx_, ry_ = CUISSE                                   # le pli de la cuisse, du côté de l'avant
    d.raw(line(_trace(T, f"M{cx_ + rx_ * 0.62:.2f},{cy_ - ry_ * 0.80:.2f} C{cx_ + rx_ * 1.12:.2f},{cy_ - ry_ * 0.25:.2f} "
                         f"{cx_ + rx_ * 1.10:.2f},{cy_ + ry_ * 0.45:.2f} {cx_ + rx_ * 0.66:.2f},{cy_ + ry_ * 0.86:.2f}"),
               C["pli"], 1.2))

    # --- le collier et la cloche, au bas de l'encolure
    if not veau:
        (c1x, c1y), (c2x, c2y) = T(21.5, -62.0), T(30.0, -36.0)
        ux, uy = c2x - c1x, c2y - c1y
        L = math.hypot(ux, uy)
        ux, uy = ux / L, uy / L
        d.add(poly([(c1x - uy * 2.0, c1y + ux * 2.0), (c2x - uy * 2.0, c2y + ux * 2.0), (c2x + uy * 2.0, c2y - ux * 2.0),
                    (c1x + uy * 2.0, c1y - ux * 2.0)]), C["strap"], sil=False, clip=cid)

    # --- pattes du côté visible
    patte(AR, A, C["white"], C["hoof"])
    patte(AV, B, C["white"], C["hoof"])
    if not veau:                                                  # la cloche pend devant le poitrail
        bx, by = T(28.6, -30.0)
        d.add(path(f"M{bx - 3.2:.2f},{by - 4.6:.2f} L{bx + 3.2:.2f},{by - 4.6:.2f} L{bx + 4.6:.2f},{by + 3.4:.2f} L{bx - 4.6:.2f},{by + 3.4:.2f} Z"),
              C["bell"], sil=False, edge=True)
        d.add(path(f"M{bx - 4.2:.2f},{by + 1.2:.2f} L{bx + 4.2:.2f},{by + 1.2:.2f} L{bx + 4.6:.2f},{by + 3.4:.2f} L{bx - 4.6:.2f},{by + 3.4:.2f} Z"),
              C["bell_dk"], sil=False)
        d.add(circle(bx, by + 4.6, 1.5), C["bell_dk"], sil=False, edge=True)

    # --- la tête : la mâchoire d'abord (elle s'ouvre autour de sa charnière), puis le crâne et le mufle
    m = max(p.get("moo", 0.0), 0.0)
    chew = p.get("chew", 0.0)
    ouvre = m * 30.0 + chew * 6.0                                 # degrés
    jaw = _tourne(ouvre, MACHOIRE_PIVOT[0], MACHOIRE_PIVOT[1], tete)
    ep = r * k * 0.085
    if ouvre > 6:                                                 # la gueule : le fond, la langue
        a0, a1 = tete(1.00, 0.78), tete(1.78, 0.74)
        b0, b1 = jaw(1.78, 0.78), jaw(1.00, 0.82)
        fond = poly([a0, a1, b0, b1])
        d.clip("gueule" + kind, [fond])
        d.add(fond, C["mouth"])
        d.add(path(_ovale(jaw, 1.36, 0.90, 0.34, 0.13, 2)), C["tongue"], sil=False, clip="gueule" + kind)
    d.add(path(_trace(jaw, MACHOIRE)), C["muzzle"])
    contour = path(Th(CONTOUR))
    hid = "tete" + kind
    d.clip(hid, [contour])
    d.add(contour, C["white"])
    d.add(path(Th(TACHE_TETE)), tache, sil=False, clip=hid)
    d.add(path(Th(MUFLE)), C["muzzle"], sil=False, clip=hid)
    d.raw(line(Th(BOUCHE), OUTLINE, ep))                                                      # la lèvre
    d.add(path(_ovale(tete, NASEAU[0], NASEAU[1], 0.10, 0.15, -12)), C["muzzle_dk"], sil=False)
    d.add(path(_ovale(tete, JOUE[0], JOUE[1], 0.19, 0.12)), C["blush"], sil=False, opacity=0.55)

    # l'œil : celui de Tecky, avec deux cils
    ex, ey, erx, ery = OEIL
    if p.get("blink"):
        d.raw(line(Th(f"M{ex - erx * 0.95:.2f},{ey:.2f} Q{ex:.2f},{ey + ery * 0.7:.2f} {ex + erx * 0.95:.2f},{ey:.2f}"), OUTLINE, ep))
    else:
        d.add(path(_ovale(tete, ex, ey, erx, ery)), "#FFFFFF", sil=False)
        d.raw(line(_ovale(tete, ex, ey, erx, ery), OUTLINE, ep))
        d.add(path(_ovale(tete, ex + erx * 0.20, ey + ery * 0.05, erx * 0.70, ery * 0.72)), C["iris"], sil=False)
        d.add(path(_ovale(tete, ex + erx * 0.42, ey - ery * 0.30, erx * 0.25, ery * 0.22)), "#FFFFFF", sil=False)
        d.raw(line(Th(f"M{ex - erx * 0.78:.2f},{ey - ery * 0.74:.2f} L{ex - erx * 1.30:.2f},{ey - ery * 1.14:.2f} "
                      f"M{ex - erx * 1.02:.2f},{ey - ery * 0.28:.2f} L{ex - erx * 1.62:.2f},{ey - ery * 0.50:.2f}"),
                   OUTLINE if kind != "cow_bw" else "#FFFDF7", ep * 0.8))

    # la corne (ou son bourgeon) et l'oreille, par-dessus
    if veau:
        d.add(path(Th(BOURGEON)), C["horn"], edge=True)
    else:
        d.add(path(Th(CORNE)), C["horn"], edge=True)
    # (elle pend un peu sur le côté ; elle se redresse quand la vache écoute)
    bascule = _tourne(-30.0 + 28.0 * p.get("ear", 0.0), OREILLE_PIVOT[0], OREILLE_PIVOT[1], tete)
    d.add(path(_trace(bascule, OREILLE)), tache, edge=True)
    d.add(path(_trace(bascule, OREILLE_DEDANS)), C["muzzle"], sil=False)
    return d


def anims(kind):
    """{animation : (poses, fps, boucle)}."""
    return {
        "idle": ([dict(), dict(tail=-9, bob=0.5), dict(tail=-16, ear=1, bob=0.8), dict(tail=-7, blink=1, bob=0.5),
                  dict(tail=8, head=-0.06), dict(head=-0.03)], 4, True),
        "graze": ([dict(head=1, chew=0), dict(head=0.97, chew=1, tail=-8), dict(head=1, chew=0.2, tail=-15),
                   dict(head=0.97, chew=1, tail=-6)], 4, True),
        "walk": ([dict(pas=0.0, bob=0.0, head=0.05, tail=-6), dict(pas=0.25, bob=-1.2, tail=4),
                  dict(pas=0.5, bob=0.0, head=0.05, tail=8), dict(pas=0.75, bob=-1.2, tail=-3)], 6, True),
        "moo": ([dict(head=-0.45, moo=0.5, ear=1), dict(head=-0.8, moo=1, ear=1), dict(head=-0.8, moo=1, ear=1, tail=-12),
                 dict(head=-0.4, moo=0.45, ear=1)], 5, False),
    }


def image(kind, p):
    """SVG d'une image du jeu : la pose p, réduite de ECH, les sabots sur l'origine du cadre."""
    d = cow(kind, p)
    d.w, d.h = W, H
    return d.svg(f"translate({32 - 64 * ECH:.2f} {G - 88 * ECH:.2f}) scale({ECH})", outline_w=TRAIT)


def frames(kind, anim):
    """SVG des images d'une animation."""
    return [image(kind, p) for p in anims(kind)[anim][0]]


if __name__ == "__main__":
    from spritelib import render_svg, PAD
    from PIL import Image
    racine = os.path.dirname(os.path.abspath(__file__))
    fond = (126, 200, 100, 255)
    k = 6
    lignes = []
    for kind in KINDS:
        for a in anims(kind):
            lignes.append([render_svg(s, W, H, k, PAD) for s in frames(kind, a)])
    w, h = lignes[0][0].size
    out = Image.new("RGBA", (w * 6, h * len(lignes)), fond)
    for j, ims in enumerate(lignes):
        for i, im in enumerate(ims):
            out.alpha_composite(im, (i * w, j * h))
    fn = os.path.join(racine, "reference", "v2", "vaches_v2.png")
    out.convert("RGB").save(fn)
    print(fn, out.size)
