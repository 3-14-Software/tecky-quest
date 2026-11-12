"""
Les chiens du jeu web, version 2 (PLAN_V2.md, lot 3) : roquet, bouledogue, molosse (doberman), berger (border collie).

Ils sont de la famille du Tecky de tecky2.py, lui-même relevé sur la planche de Christophe : la même tête (crâne
rond, grand œil, truffe, gueule qui s'ouvre sous la lèvre), dont le museau est allongé, raccourci ou épaissi selon
la race (`museau`), les mêmes pattes dodues, le même contour. Ce qui change d'un chien à l'autre est écrit dans
CHIENS : couleurs, corps, pattes, queue, oreilles, taches, collier.

Les formes sont écrites en pixels du jeu (x2), autour du milieu des pieds : x vers la droite, y vers le bas, le sol
à y = 0 ; le dessin est réduit de ECH dans le cadre de 48 x 48 des chiens (origine aux pieds, comme avant).
Mêmes tailles que les chiens de la v1 : tout ce que le jeu règle sur eux (barres de vie, cœurs, aboiement du
doberman) reste juste.

    python3 chiens2.py      # reference/v2/chiens_v2.png (les quatre chiens, les trois vues, à côté de Tecky)
"""
import math
import os

import tecky2 as tk
from tecky2 import _trace, _ovale, _tourne, _membre, _cerne, _foulee, pose
from spritelib import Drawing, circle, ellipse, path, poly, line, OUTLINE

W = H = 96
SOL = 86.0               # ligne du sol dans le dessin
AXE = 48.0               # milieu des pieds
ECH = 0.47               # réduction dans le jeu : les chiens gardent la taille de ceux d'avant (à 0,5, une unité
                         # du dessin vaudrait un pixel du jeu, mais ils seraient 6 % plus grands)
TRAIT = 1.8 / ECH
CADRE = (48, 48, 24, 44)     # largeur, hauteur, origine : le cadre des chiens d'avant
COLLIER, CLOU = "#2F3340", "#D4D8E0"
BLANC_OEIL, IRIS = "#FFFFFF", "#3E1B0F"

# Tête de face : oreilles (à gauche de l'image ; la droite est son miroir), autour du centre de la tête, en pixels.
POINTUE_F = "M-9.5,-4 C-11.5,-10 -11,-17 -8.5,-21.5 C-5.5,-18 -3,-13.5 -2,-8.5 Z"
POINTUE_F_DEDANS = "M-8.6,-6 C-9.8,-10.5 -9.6,-15 -8.4,-18 C-6.6,-15 -5.2,-11.5 -4.6,-8.5 Z"
DROITE_F = "M-8.5,-4 C-10,-11 -9.5,-19 -7,-24 C-4.5,-19.5 -2.5,-13.5 -1.5,-8.5 Z"
DROITE_F_DEDANS = "M-7.6,-6.5 C-8.5,-11.5 -8.2,-17 -7,-20.5 C-5.4,-17 -4.2,-12.5 -3.6,-8.8 Z"
ROSE_F = "M-12.5,-5.5 C-16.5,-8.5 -18,-12.5 -15,-13.5 C-11.5,-14 -8,-12.5 -5.5,-10.5 C-8,-8 -10,-6.5 -12.5,-5.5 Z"
ROSE_F_DEDANS = "M-12.8,-7.8 C-14.8,-9.6 -15.6,-11.6 -14.2,-12.0 C-12.4,-11.6 -10.6,-10.4 -9.4,-9.2 Z"
PLIEE_F = ("M-10,-3.5 C-12.5,-8.5 -12.5,-13.5 -10.5,-16.5 C-9.5,-18 -7.5,-18 -6.5,-16.5 C-5,-14 -3.5,-11 -2.5,-8 Z")
PLIEE_F_BOUT = "M-10.5,-16.5 C-13.5,-16 -15.5,-13 -15,-10 C-13,-11.5 -11,-13.5 -6.8,-16.2 C-8,-17.6 -9.6,-17.8 -10.5,-16.5 Z"

CHIENS = {
    # --- petit roquet nerveux : blanc à taches fauves, oreilles dressées, queue en fouet
    "roquet": dict(
        fur="#F4EFE5", ombre="#CFC6B6", clair="#FFFFFF", tache="#D99A5B", oreille="#C98A4B", oreille2="#A9713A", dedans="#EDB7A0",
        sourcil="#6B4A2E", bas=None,
        corps=("M-16,-33 C-8,-35 2,-36 10,-35 C16,-34 19,-29 18,-24 C17,-19 12,-16 7,-16 C0,-16 -6,-17 -12,-18 "
               "C-18,-19 -22,-23 -21,-28 C-20,-31 -18,-33 -16,-33 Z"),
        cuisse=(-14, -23, 7, 8), dos=-34,
        queue="M-19,-29 C-25,-33 -28,-42 -26,-51 C-25.5,-53.5 -22,-53.5 -22,-51 C-22,-44 -20,-38 -14,-33 Z",
        queue_pivot=(-18, -31), queue_bout=None, queue_ko=-80,
        pattes=(-15, -9, 8, 13.5), hanche=-19, large=(5.6, 4.8), pied=(4.3, 2.6), foulee=(4.4, 3.0),
        taches=[("M-14,-36 C-8,-37 0,-37 4,-36 C3,-30 -3,-27 -9,-28 C-13,-29 -15,-32 -14,-36 Z", "tache")],
        ventre=None,
        epaule=(4, -35), gorge=(17.5, -26),
        collier="M3.5,-37.5 L8.5,-41 L21,-31.5 L17.5,-27 Z", clous=((8.5, -36.5), (12.2, -33.8), (15.8, -31)),
        tete=(15, -45, 10.5), museau=(0.72, 0.86), truffe=(0.27, 0.23), oeil=0.86, masque="clair",
        oreilles=[dict(forme="M-0.10,-0.90 C-0.25,-1.45 -0.10,-1.95 0.18,-2.15 C0.42,-1.85 0.62,-1.40 0.62,-0.95 Z",
                       couleur="oreille2", devant=False),
                  dict(forme="M-0.80,-0.62 C-1.02,-1.25 -0.92,-1.80 -0.62,-2.08 C-0.36,-1.80 -0.06,-1.35 0.04,-0.96 Z",
                       dedans="M-0.70,-0.86 C-0.82,-1.25 -0.76,-1.62 -0.60,-1.82 C-0.44,-1.60 -0.28,-1.30 -0.20,-1.02 Z",
                       couleur="oreille", devant=True)],
        oreille_pivot=(-0.40, -0.95),
        tete_taches=[("M-0.30,-1.20 C0.30,-1.25 0.85,-0.80 0.95,-0.20 C0.80,0.25 0.40,0.50 0.00,0.45 C-0.40,0.35 -0.60,-0.30 -0.30,-1.20 Z", "tache")],
        croc=True,
        # face et dos
        f_tete=(-43, 11.9, 13.1), f_corps=(-35, -18, 10.4), f_pattes=(5.6, 5.6), f_oeil=1.12, f_croupe=-0.05,
        f_oreille=(POINTUE_F, POINTUE_F_DEDANS, (-6.5, -7), "oreille", False),
        f_taches=[("M-12,-12 L-1.5,-12 C-0.5,-7 -1,-1 -3,2.5 C-6,4 -10,3 -12,0 Z", "tache")],
        d_tete=(-44, 10.6, 12.2), d_queue="fouet", d_taches=[("M-9,-33 C-4,-36 4,-36 8,-32 C7,-26 -6,-25 -9,-33 Z", "tache")],
    ),
    # --- bouledogue : gris, trapu, face plate, bajoues claires, deux crocs qui dépassent, queue en moignon
    "bouledogue": dict(
        fur="#8C8F99", ombre="#6A6D78", clair="#E4E1DA", tache=None, oreille="#6A6D78", dedans="#B98F94",
        sourcil="#3F4149", bas=None,
        corps=("M-19,-36 C-10,-39 2,-39 10,-37 C18,-35 21,-28 20,-21 C19,-14 13,-10 6,-10 C-2,-10 -10,-11 -17,-12 "
               "C-24,-13 -27,-20 -26,-27 C-25,-32 -23,-35 -19,-36 Z"),
        cuisse=(-17, -20, 8.5, 9.5), dos=-38,
        queue="M-22,-36 C-27,-40 -32,-37 -30,-32 C-29,-29.5 -25.5,-29.5 -23,-31 Z",
        queue_pivot=(-23, -33), queue_bout=None,
        pattes=(-18, -11, 8, 14.5), hanche=-15, large=(8.2, 7.2), pied=(5.4, 3.0), foulee=(3.6, 2.6),
        taches=[],
        ventre="M-12,-17 C-4,-15 6,-15 14,-19 C19,-22 22,-27 23,-33 L28,-33 L28,-4 L-12,-4 Z",
        epaule=(2, -38), gorge=(19.5, -24),
        collier="M2,-36 L7,-40.5 L23,-27.5 L19.5,-22.5 Z", clous=((8, -35.2), (12.4, -31.6), (16.8, -28)),
        tete=(12.5, -39, 13.5), museau=(0.40, 1.22), truffe=(0.22, 0.17), oeil=0.80, masque="clair",
        oreilles=[dict(forme="M-0.72,-0.78 C-1.02,-1.12 -0.86,-1.42 -0.50,-1.34 C-0.26,-1.24 -0.10,-1.06 -0.02,-0.90 C-0.26,-0.74 -0.50,-0.70 -0.72,-0.78 Z",
                       dedans="M-0.66,-0.92 C-0.80,-1.10 -0.72,-1.24 -0.52,-1.20 C-0.40,-1.14 -0.30,-1.04 -0.24,-0.94 Z",
                       couleur="oreille", devant=True)],
        oreille_pivot=(-0.40, -0.90),
        tete_taches=[],
        croc="dessous",
        f_tete=(-36.5, 15.3, 16.4), f_corps=(-28, -13, 16.0), f_pattes=(10.0, 8.4), f_oeil=1.30, f_croupe=0.22,
        f_oreille=(ROSE_F, ROSE_F_DEDANS, (-8, -9), "oreille", True),
        f_taches=[],
        d_tete=(-37.5, 13.6, 15.2), d_queue="moignon", d_taches=[],
    ),
    # --- molosse (doberman) : grand, noir et feu, oreilles droites, long museau, longues pattes
    "molosse": dict(
        fur="#34302F", ombre="#1F1B1B", clair="#CC7F3D", tache=None, oreille="#262222", dedans="#8A5A3A",
        sourcil="#CC7F3D", bas="#CC7F3D",
        corps=("M-22,-43 C-12,-45 0,-46 10,-45 C17,-44 20,-38 19,-33 C18,-27 13,-24 7,-24 C0,-24 -6,-27 -13,-30 "
               "C-19,-31 -27,-32 -28,-37 C-28,-40 -26,-43 -22,-43 Z"),
        cuisse=(-19, -33, 8, 10), dos=-44,
        queue="M-24,-42 C-30,-43 -35,-40 -37.5,-34 C-38.2,-32 -36,-31 -35,-32.8 C-33,-36.5 -29.5,-38.6 -24,-38.6 Z",
        queue_pivot=(-24, -39.5), queue_bout=None,
        pattes=(-19, -12, 8.5, 14.5), hanche=-28, large=(6.6, 5.2), pied=(4.8, 2.8), foulee=(6.0, 3.6),
        taches=[],
        ventre="M13,-44 C18,-41 21,-37 20.5,-32 C20,-28 17,-25 12.5,-24 C14.5,-29 14.8,-37 13,-44 Z",
        epaule=(2, -45), gorge=(18.5, -34),
        collier="M4,-48.5 L9.5,-52.5 L22,-42 L18,-37.5 Z", clous=((9.2, -48.2), (12.6, -45.4), (16, -42.6)),
        tete=(22.5, -55, 9.6), museau=(1.16, 0.90), truffe=(0.30, 0.25), oeil=0.80, masque="clair",
        oreilles=[dict(forme="M-0.05,-0.92 C-0.12,-1.40 0.06,-1.78 0.30,-1.96 C0.46,-1.70 0.58,-1.34 0.56,-0.98 Z",
                       couleur="ombre", devant=False),
                  dict(forme="M-0.74,-0.66 C-0.88,-1.22 -0.72,-1.72 -0.48,-1.95 C-0.26,-1.68 -0.04,-1.30 0.02,-0.98 Z",
                       dedans="M-0.62,-0.90 C-0.70,-1.26 -0.62,-1.54 -0.48,-1.72 C-0.36,-1.52 -0.24,-1.28 -0.18,-1.06 Z",
                       couleur="oreille", devant=True)],
        oreille_pivot=(-0.36, -0.95),
        tete_taches=[("M0.22,-0.80 C0.34,-0.90 0.56,-0.86 0.62,-0.72 C0.52,-0.62 0.30,-0.66 0.22,-0.80 Z", "clair")],
        croc=True,
        f_tete=(-52.4, 10.8, 12.0), f_corps=(-45, -27, 10.6), f_pattes=(5.8, 6.4), f_oeil=0.98, f_croupe=-0.05,
        f_oreille=(DROITE_F, DROITE_F_DEDANS, (-5.5, -7), "oreille", False),
        f_taches=[],
        d_tete=(-53.4, 9.6, 11.2), d_queue="fouet", d_taches=[], queue_w=(5.0, 3.0), queue_l=14.0,
    ),
    # --- chien de berger (border collie) : noir et blanc, liste sur le front, poitrail blanc, queue en panache
    "berger": dict(
        fur="#33313A", ombre="#1F1E24", clair="#F6F3EC", tache=None, oreille="#26252B", dedans="#5A5560",
        sourcil="#A29EAC", bas="#F6F3EC",
        corps=("M-20,-35 C-10,-37 2,-37 10,-36 C18,-35 22,-29 21,-23 C20,-17 14,-13 7,-13 C0,-13 -7,-15 -13,-16 "
               "C-20,-17 -26,-21 -26,-27 C-26,-31 -24,-34 -20,-35 Z"),
        cuisse=(-17, -22, 8, 9), dos=-36,
        queue="M-22,-33 C-30,-35 -38,-29 -39,-19 C-39,-13 -34,-10.5 -31,-14 C-28,-18 -25,-23 -19,-26 Z",
        queue_pivot=(-21, -30), queue_bout="M-41,-22 L-28,-19 L-28,-8 L-41,-8 Z",
        pattes=(-17, -10, 8.5, 14.5), hanche=-17, large=(6.6, 5.6), pied=(4.9, 2.8), foulee=(4.8, 3.0),
        taches=[],
        ventre=("M5,-40 C8,-34 9,-26 6,-19 C4,-16 0,-14.5 -6,-15 L-6,-8 L26,-8 L26,-40 Z"),
        epaule=(3, -36), gorge=(20.5, -26),
        collier="M5,-38.5 L10,-42 L23.5,-31 L20,-26.5 Z", clous=((10.5, -37.4), (14.4, -34.3), (18.3, -31.2)),
        tete=(18.5, -42, 10.5), museau=(0.90, 0.92), truffe=(0.30, 0.25), oeil=0.84, masque="clair",
        oreilles=[dict(forme="M-0.05,-0.92 C-0.15,-1.25 0.00,-1.52 0.26,-1.58 C0.50,-1.50 0.62,-1.25 0.62,-0.95 Z",
                       couleur="ombre", devant=False),
                  dict(forme="M-0.80,-0.62 C-0.98,-1.12 -0.80,-1.52 -0.46,-1.58 C-0.18,-1.50 0.00,-1.24 0.04,-0.96 Z",
                       dedans="M-0.48,-1.58 C-0.20,-1.62 0.12,-1.46 0.26,-1.16 C0.00,-1.22 -0.24,-1.34 -0.48,-1.58 Z",
                       couleur="oreille", devant=True)],
        oreille_pivot=(-0.40, -0.95),
        tete_taches=[("M0.62,-0.96 C0.72,-0.60 0.86,-0.30 1.00,-0.12 L1.40,0.10 L1.30,-0.30 C1.10,-0.55 0.90,-0.80 0.62,-0.96 Z", "clair")],
        croc=True,
        f_tete=(-40.2, 11.9, 13.1), f_corps=(-33, -16, 12.0), f_pattes=(6.8, 6.6), f_oeil=1.12, f_croupe=0.34,
        f_oreille=(PLIEE_F, PLIEE_F_BOUT, (-6.5, -6.5), "oreille", False),
        f_taches=[("M-1.9,-10.6 C-1.5,-6 -2.4,-1 -3.4,2.6 L3.4,2.6 C2.4,-1 1.5,-6 1.9,-10.6 Z", "clair")],
        d_tete=(-41.2, 10.6, 12.2), d_queue="panache", d_taches=[],
    ),
}
DOGS = CHIENS


def _ici(x, y):
    """Coordonnées d'un chien (autour du milieu des pieds, sol à 0) -> dessin."""
    return AXE + x, SOL + y


# ====================================================================== PROFIL
def _torse(S, p):
    """Où va un point du torse (écrit pour le chien debout), selon l'attitude."""
    b = p["rebond"]
    if p["attitude"] == "dos":       # retourné, le dos au sol
        return lambda x, y: (x, SOL - (y - SOL - S["dos"]) - 1.5 + b)
    return _tourne(p["tangage"], AXE, SOL + S["dos"] * 0.5, lambda x, y: (x + p["elan"], y + b))


def _patte(d, S, haut, fx, lever, couleur, bas, coussin):
    """Une patte, de son attache au sol : un fût arrondi en haut et un pied dodu tourné vers l'avant. bas : la
    couleur du bas de la patte (les chaussettes du doberman et du border collie)."""
    x, y = haut
    w1, w2 = S["large"]
    rx, ry = S["pied"]
    fy = SOL - 1.0 - lever
    fut = (f"M{x - w1 / 2:.2f},{y:.2f} C{x - w1 / 2:.2f},{y - w1 * 0.65:.2f} {x + w1 / 2:.2f},{y - w1 * 0.65:.2f} {x + w1 / 2:.2f},{y:.2f} "
           f"L{fx + w2 / 2:.2f},{fy - 0.6:.2f} L{fx - w2 / 2:.2f},{fy - 0.6:.2f} Z")
    d.add(path(fut), couleur)
    pied = ellipse(fx + 1.0, fy - 0.2, rx, ry)
    d.add(pied, bas or couleur)
    if bas:                          # la chaussette : la moitié basse du fût
        my, mx = (y + fy) / 2, (x + fx) / 2
        d.add(path(f"M{mx - w1 / 2 - 0.4:.2f},{my:.2f} L{mx + w1 / 2 + 0.4:.2f},{my:.2f} L{fx + w2 / 2 + 0.4:.2f},{fy:.2f} "
                   f"L{fx - w2 / 2 - 0.4:.2f},{fy:.2f} Z"), bas, sil=False)
        d.add(pied, bas, sil=False)
    if coussin:
        d.add(ellipse(fx + 2.2, fy + 0.2, rx * 0.62, ry * 0.68), coussin, sil=False)
    d.raw(line(f"M{fx + 1.4:.2f},{fy - 1.0:.2f} L{fx + 1.6:.2f},{fy + 1.0:.2f} "
               f"M{fx + 3.0:.2f},{fy - 0.6:.2f} L{fx + 3.1:.2f},{fy + 0.8:.2f}", OUTLINE, 0.5))


def _cou(S, T, hx, hy, r, sens=1):
    """Le cou, des épaules à la tête (centre du crâne en hx, hy)."""
    (ax, ay), (ex, ey) = T(*_ici(*S["epaule"])), T(*_ici(*S["gorge"]))
    bx, by = hx - 0.92 * r, hy + 0.30 * r * sens            # nuque
    cx, cy = hx + 0.16 * r, hy + 1.10 * r * sens            # gorge
    return (f"M{ax:.2f},{ay:.2f} C{ax + 1:.2f},{ay - 3 * sens:.2f} {bx - 2:.2f},{by + 2 * sens:.2f} {bx:.2f},{by:.2f} "
            f"L{cx:.2f},{cy:.2f} C{cx + 0.6:.2f},{cy + 2 * sens:.2f} {ex + 0.8:.2f},{ey - 3 * sens:.2f} {ex:.2f},{ey:.2f} Z")


def profil(S, p=None):
    """Un chien de profil, tourné vers la droite : debout, ou sur le dos (KO)."""
    p = p or pose()
    d = Drawing(W, H)
    T0 = _torse(S, p)
    T = lambda x, y: T0(*_ici(x, y))                      # des coordonnées du chien au dessin
    F = lambda s: path(_trace(T, s))
    ko = p["attitude"] == "dos"
    sens = -1 if ko else 1
    tx, ty, r = S["tete"]
    AR, AR2, AV, AV2 = S["pattes"]
    hanche = S["hanche"]
    sombre, bas = S["ombre"], S["bas"]

    if ko:
        hx, hy = AXE + tx + 3, SOL - r * 1.08 - 0.5
    else:
        hx, hy = T(tx, ty)
    hx, hy = hx + p["tete"][0], hy + p["tete"][1]

    # pattes du côté caché, plus sombres
    A, B = _foulee(p, *S["foulee"])
    av = p["pattes"] or (A, B)
    longueur = -hanche
    if not ko:
        _patte(d, S, T(AR2, hanche), AXE + AR2 + B[0], B[1], sombre, bas and S["bas_ombre"], None)
        _patte(d, S, T(AV2, hanche), AXE + AV2 + av[0][0], av[0][1], sombre, bas and S["bas_ombre"], None)
    else:
        for x, dx in ((AR2, -1.5), (AV2, 3.0)):
            px, py = T(x, hanche)
            d.add(_membre(px, py, px + dx, py - longueur * 0.62, S["large"][0], S["large"][1]), sombre)
            d.add(ellipse(px + dx + 1.0, py - longueur * 0.62 - 0.8, S["pied"][0] * 0.9, S["pied"][1]), bas and S["bas_ombre"] or sombre)

    # queue
    q = p["queue"] + (S.get("queue_ko", -50) if ko else 0)
    pv = S["queue_pivot"]
    Tq = _tourne(q, pv[0], pv[1], T)
    queue = path(_trace(Tq, S["queue"]))
    d.add(queue, S["fur"])
    if S["queue_bout"]:
        d.clip("queue", [queue])
        d.add(path(_trace(Tq, S["queue_bout"])), S["clair"], sil=False, clip="queue")

    # corps
    corps, cuisse = F(S["corps"]), path(_ovale(T, *S["cuisse"]))
    cou = path(_cou(S, T0, hx, hy, r, sens))
    d.clip("corps", [corps, cuisse, cou])
    d.add(cou, S["fur"])
    d.add(corps, S["fur"])
    d.add(cuisse, S["fur"])
    if S["ventre"]:
        d.add(F(S["ventre"]), S["clair"], sil=False, clip="corps")
    for forme, couleur in S["taches"]:
        d.add(F(forme), S[couleur], sil=False, clip="corps")
    d.add(cuisse, S["fur"], sil=False, clip="corps")
    cx, cy, rx, ry = S["cuisse"]
    d.raw(line(_trace(T, f"M{cx + rx * 0.8:.2f},{cy - ry * 0.75:.2f} C{cx + rx * 1.25:.2f},{cy - ry * 0.2:.2f} "
                         f"{cx + rx * 1.2:.2f},{cy + ry * 0.5:.2f} {cx + rx * 0.7:.2f},{cy + ry * 0.95:.2f}"), sombre, 0.9))

    # collier à clous, en travers du cou
    d.add(F(S["collier"]), COLLIER, sil=False, clip="corps")
    for x, y in S["clous"]:
        ax, ay = T(x, y)
        d.add(circle(ax, ay, 1.15), CLOU, sil=False, clip="corps")

    # pattes du côté visible
    if not ko:
        _patte(d, S, T(AR, hanche), AXE + AR + A[0], A[1], S["fur"], bas, S["clair"] if not bas else None)
        _patte(d, S, T(AV, hanche), AXE + AV + av[1][0], av[1][1], S["fur"], bas, S["clair"] if not bas else None)
    else:
        for x, dx in ((AR, -2.6), (AV, 2.2)):
            px, py = T(x, hanche)
            patte = _membre(px, py, px + dx, py - longueur * 0.7, S["large"][0] + 0.4, S["large"][1] + 0.2)
            pied = ellipse(px + dx + 1.2, py - longueur * 0.7 - 0.9, S["pied"][0] * 0.95, S["pied"][1])
            _cerne(d, patte, pied)
            d.add(patte, S["fur"])
            d.add(pied, bas or S["fur"])

    tete(d, S, p, hx, hy, r, sens)
    return d


# ====================================================================== TÊTE DE PROFIL
def _museau(S):
    """La tête de Tecky, le museau allongé (mx) et épaissi (my) autour de son départ : toutes les formes de la
    tête y passent, la gueule et les lèvres suivent."""
    mx, my = S["museau"]

    def deforme(x, y):
        w = min(1.0, max(0.0, (x - 0.6) / 0.6))
        return x + max(0.0, x - 0.9) * (mx - 1), y + w * (y - 0.55) * (my - 1)
    return deforme


def tete(d, S, p, cx, cy, r, sens=1):
    """La tête d'un chien de profil : celle de tecky2.tete(), le museau déformé, ses oreilles et ses taches."""
    sourcils, yeux, bouche, ouverte, releve = tk._visage(p)
    brut = tk._repere(cx, cy, r, releve, sens)
    deforme = _museau(S)
    place = lambda x, y: brut(*deforme(x, y))
    T = lambda s: _trace(place, s)
    ep = max(0.75, r * 0.085)
    pv = S["oreille_pivot"]

    def oreille(o):
        bascule = _tourne(p["oreille"] * S.get("oreille_k", 0.5), pv[0], pv[1], brut)
        if sens < 0:
            libre = bascule
            bascule = lambda x, y: (libre(x, y)[0], min(libre(x, y)[1], SOL - 0.6))
        d.add(path(_trace(bascule, o["forme"])), S[o["couleur"]], edge=o["devant"])
        if o.get("dedans"):
            d.add(path(_trace(bascule, o["dedans"])), S["dedans"], sil=False)

    for o in S["oreilles"]:
        if not o["devant"]:
            oreille(o)

    if ouverte:
        machoire, dedans, langue, sillon = tk._gueule(place, ouverte)
        d.clip("gueule", [path(dedans)])
        d.add(path(machoire), S[S["masque"]])
        d.add(path(dedans), tk.PAL["mouth"], sil=False, edge=True)
        d.add(path(langue), tk.PAL["tongue"], sil=False, clip="gueule")
        d.raw('<g clip-path="url(#gueule)">' + line(sillon, tk.PAL["tongue_dk"], ep * 0.8) + "</g>")

    contour = T(tk.OUVERTE if ouverte else tk.FERMEE)
    d.clip("tete", [path(contour)])
    d.add(path(contour), S["fur"])
    for forme, couleur in S["tete_taches"]:
        d.add(path(_trace(brut, forme)), S[couleur], sil=False, clip="tete")
    d.add(path(T(tk.CLAIR)), S[S["masque"]], sil=False, clip="tete")

    # truffe
    nx, ny = deforme(tk.TRUFFE[0], tk.TRUFFE[1])
    rx, ry = S["truffe"]
    nx -= (tk.TRUFFE[2] - rx) * 0.7
    d.add(path(_ovale(brut, nx, ny, rx, ry, 12)), tk.PAL["nose"])
    d.add(path(_ovale(brut, nx - rx * 0.2, ny - ry * 0.4, rx * 0.3, ry * 0.17, 6)), "#FFFFFF", sil=False, opacity=0.9)

    # bouche et crocs
    if ouverte:
        d.raw(line(T(tk.LEVRE), OUTLINE, ep))
    else:
        d.raw(line(T(f"M0.34,0.90 C0.50,1.06 0.85,1.15 {tk.MENTON:.2f},1.15"), OUTLINE, ep))
    if S["croc"] == "dessous":       # les deux crocs du bouledogue, plantés dans la lèvre du bas
        for x in (0.70, 1.00):
            a, b_, c_ = place(x - 0.075, 1.10 + (x - 0.6) * 0.1), place(x + 0.075, 1.12 + (x - 0.6) * 0.1), place(x, 0.92)
            d.add(poly([a, b_, c_]), "#FFFFFF", sil=False, edge=True)
    elif S["croc"] and not ouverte:  # un petit croc sous la babine
        a, b_, c_ = place(0.84, 1.13), place(1.04, 1.15), place(0.95, 1.40)
        d.add(poly([a, b_, c_]), "#FFFFFF", sil=False, edge=True)

    # l'œil
    ex, ey, erx, ery = tk.OEIL
    k = S["oeil"]
    erx, ery = erx * k, ery * k
    P = lambda s: _trace(brut, s)
    if yeux == "fermes":
        d.raw(line(P(f"M{ex - erx * 0.95:.2f},{ey:.2f} Q{ex:.2f},{ey + ery * 0.7:.2f} {ex + erx * 0.95:.2f},{ey:.2f}"), OUTLINE, ep))
    elif yeux == "croix":
        s = erx * 0.7
        d.raw(line(P(f"M{ex - s:.2f},{ey - s:.2f} L{ex + s:.2f},{ey + s:.2f} M{ex - s:.2f},{ey + s:.2f} L{ex + s:.2f},{ey - s:.2f}"),
                   S.get("croix", OUTLINE), ep * 1.3))
    elif yeux == "plisses":
        d.raw(line(P(f"M{ex - erx * 0.8:.2f},{ey - ery * 0.6:.2f} L{ex + erx * 0.65:.2f},{ey:.2f} L{ex - erx * 0.8:.2f},{ey + ery * 0.6:.2f}"),
                   S.get("croix", OUTLINE), ep * 1.3))
    else:
        d.add(path(_ovale(brut, ex, ey, erx, ery)), BLANC_OEIL, sil=False)
        d.raw(line(_ovale(brut, ex, ey, erx, ery), OUTLINE, ep))
        d.add(path(_ovale(brut, ex + erx * 0.22, ey + ery * 0.04, erx * 0.70, ery * 0.72)), IRIS, sil=False)
        d.add(path(_ovale(brut, ex + erx * 0.44, ey - ery * 0.30, erx * 0.25, ery * 0.22)), "#FFFFFF", sil=False)
    # sourcil froncé : il descend vers le museau
    if yeux not in ("croix",):
        d.raw(line(P(f"M{ex - erx * 0.95:.2f},{ey - ery * 1.42:.2f} L{ex + erx * 0.95:.2f},{ey - ery * 0.92:.2f}"), S["sourcil"], ep * 1.5))

    for o in S["oreilles"]:
        if o["devant"]:
            oreille(o)

    if p["traits"]:
        d.raw(line(T("M1.80,1.22 L2.30,1.12 M1.78,1.50 L2.30,1.58 M1.64,1.76 L2.04,2.06"), OUTLINE, ep * 1.3))


# ====================================================================== FACE ET DOS
def _oreilles_f(d, S, p, place, devant):
    """Les deux oreilles, de face ou de dos. f_oreille : (forme, intérieur, attache, couleur, devant la tête ?) ;
    l'intérieur du border collie est le bout de l'oreille, replié vers l'avant (il dépasse : il a son contour)."""
    forme, dedans, pivot, couleur, dv = S["f_oreille"]
    if dv != devant:
        return
    replie = dedans is PLIEE_F_BOUT
    for s in (-1, 1):
        a = (p["oreille"] - s * p["penche"]) * S.get("oreille_k", 0.5)
        pl = _tourne(a, pivot[0], pivot[1], lambda x, y, s=s: place(-s * x, y))
        d.add(path(_trace(pl, forme)), S[couleur], edge=devant)
        d.add(path(_trace(pl, dedans)), S["ombre" if replie else "dedans"], sil=replie, edge=replie)


def tete_face(d, S, p, hx, hy):
    """La tête d'un chien vue de face : celle de tecky2.tete_face(), à ses mesures (f_tete : demi-largeur et
    demi-hauteur), avec ses oreilles, ses taches et ses crocs. S["gentil"] : les sourcils doux et le sourire de
    Tecky au lieu de l'air grognon (Iris) ; S["ep"] : l'épaisseur des traits du visage."""
    sourcils, yeux, bouche, m, _ = tk._visage(p)
    _, hw, hv = S["f_tete"]
    fx, fy = hw / 8.9, hv / 10.0
    ep = S.get("ep", 0.82)
    gentil = S.get("gentil", False)
    rot = _tourne(p["incline"], hx, hy + hv * 0.9)
    brut = lambda x, y: rot(hx + x, hy + y)               # en pixels autour du centre
    place = lambda x, y: rot(hx + x * fx, hy + y * fy)    # les formes de Tecky, à la mesure de cette tête
    T = lambda s: _trace(place, s)

    _oreilles_f(d, S, p, brut, False)
    crane = path(T(tk.CRANE_F))
    formes = [crane]
    if m:
        formes.append(path(_ovale(place, 0, 7.0 + m * 1.7, 4.6, 2.9 + m * 1.7)))
    _cerne(d, *formes)
    d.clip("tetef", formes)
    for f in formes[::-1]:
        d.add(f, S[S["masque"]] if f is not crane else S["fur"])
    for forme, couleur in S["f_taches"]:
        d.add(path(_trace(brut, forme)), S[couleur], sil=False, clip="tetef")
    d.add(path(T(tk.MASQUE_F)), S[S["masque"]], sil=False, clip="tetef")

    ex0, ey, rx, ry = tk.OEIL_F
    k = S["f_oeil"]
    rx, ry = rx * k, ry * k
    ey = ey * fy
    for s in (-1, 1):
        ex = s * ex0 * fx
        if yeux == "fermes":
            d.raw(line(_trace(brut, f"M{ex - rx:.2f},{ey:.2f} Q{ex:.2f},{ey + ry * 0.75:.2f} {ex + rx:.2f},{ey:.2f}"), OUTLINE, ep))
        elif yeux == "croix":
            d.raw(line(_trace(brut, f"M{ex - 1.8:.2f},{ey - 1.8:.2f} L{ex + 1.8:.2f},{ey + 1.8:.2f} "
                                    f"M{ex - 1.8:.2f},{ey + 1.8:.2f} L{ex + 1.8:.2f},{ey - 1.8:.2f}"), S.get("croix", OUTLINE), ep * 1.3))
        elif yeux == "plisses":
            d.raw(line(_trace(brut, f"M{ex + s * 2.0:.2f},{ey - 1.8:.2f} L{ex - s * 1.7:.2f},{ey:.2f} L{ex + s * 2.0:.2f},{ey + 1.8:.2f}"),
                       S.get("croix", OUTLINE), ep * 1.3))
        else:
            d.add(path(_ovale(brut, ex, ey, rx, ry)), BLANC_OEIL, sil=False)
            d.raw(line(_ovale(brut, ex, ey, rx, ry), OUTLINE, ep))
            ix = ex - s * 0.25
            d.add(path(_ovale(brut, ix, ey + 0.35 * k, 1.8 * k, 2.2 * k)), IRIS, sil=False)
            d.add(path(_ovale(brut, ix + 0.35, ey - 0.65 * k, 0.68 * k, 0.68 * k)), "#FFFFFF", sil=False)
        if gentil:                   # sourcils doux (inquiets : le bout vers la truffe remonte)
            a, b_, e = (1.9, 1.75, 1.35) if sourcils == "inquiets" else (1.45, 1.75, 1.4)
            d.raw(line(_trace(brut, f"M{ex - s * rx * 0.6:.2f},{ey - ry * a:.2f} Q{ex:.2f},{ey - ry * b_:.2f} {ex + s * rx * 0.6:.2f},{ey - ry * e:.2f}"),
                       S["sourcil"], ep * 1.2))
        elif yeux != "croix":        # sourcils froncés : ils descendent vers la truffe
            d.raw(line(_trace(brut, f"M{ex + s * rx * 1.1:.2f},{ey - ry * 1.55:.2f} L{ex - s * rx * 0.9:.2f},{ey - ry * 1.02:.2f}"),
                       S["sourcil"], ep * 1.5))

    if m:
        g = path(T(f"M-2.9,6.5 Q0,7.6 2.9,6.5 Q3.4,{6.8 + m * 3.6:.2f} 0,{7.0 + m * 3.7:.2f} Q-3.4,{6.8 + m * 3.6:.2f} -2.9,6.5 Z"))
        d.clip("gueulef", [g])
        d.add(g, tk.PAL["mouth"], sil=False, edge=True)
        d.add(path(_ovale(place, 0, 7.2 + m * 3.2, 2.0, 0.5 + m * 1.2)), tk.PAL["tongue"], sil=False, clip="gueulef")
        d.raw(line(T("M0,5.7 L0,6.8"), OUTLINE, ep))
    elif gentil:                     # le sourire de Tecky (inquiet : une moue)
        d.raw(line(T("M0,5.7 L0,6.6 M-3.0,8.5 Q0,6.3 3.0,8.5" if bouche == "moue"
                     else "M0,5.7 L0,7.7 M-4.7,6.1 Q-2.6,8.4 0,7.7 Q2.6,8.4 4.7,6.1"), OUTLINE, ep))
    else:                            # la bouche des grognons : les coins tombent, deux petits crocs
        d.raw(line(T("M0,5.7 L0,6.9 M-4.2,8.3 Q-2.2,6.6 0,6.9 Q2.2,6.6 4.2,8.3"), OUTLINE, ep))
        if S["croc"]:
            haut = S["croc"] == "dessous"
            for s in (-1, 1):
                a, b_ = place(s * 1.5, 7.0 + (1.0 if haut else 0)), place(s * 3.1, 7.5 + (1.0 if haut else 0))
                c_ = place(s * 2.3, 5.6 if haut else 9.2)
                d.add(poly([a, b_, c_]), "#FFFFFF", sil=False, edge=True)
    d.add(path(_ovale(place, 0, 3.7, 2.9 * S["truffe"][0] / 0.36, 2.05 * S["truffe"][0] / 0.36)), tk.PAL["nose"], sil=False)
    d.add(path(_ovale(place, -0.8, 3.1, 0.8, 0.34)), "#FFFFFF", sil=False, opacity=0.9)
    _oreilles_f(d, S, p, brut, True)


def _corps_f(S, B):
    """Le corps vu de face ou de dos : celui de Tecky, à la largeur et à la hauteur de pattes du chien."""
    haut, bas, bw = S["f_corps"]

    def place(x, y):                 # tk.CORPS_F : x de -9,6 à 9,6, y de 23 à 41,1
        return B(x * bw / 9.6, haut + (y - 23) / 18.1 * (bas - haut))
    return place


def _patte_f(d, S, B, s, lever, avance, couleur, bas, coussin, bx):
    haut, bas_y, bw = S["f_corps"]
    ecart, lw = S["f_pattes"]
    rx, ry = S["pied"]
    tx, ty = B(s * ecart, bas_y - 2.5)
    k = 1 + 0.06 * avance
    fx, fy = AXE + s * ecart + bx * 0.25, SOL - 1.0 - lever + 0.45 * avance
    fut = path(f"M{tx - lw / 2:.2f},{ty:.2f} L{tx + lw / 2:.2f},{ty:.2f} L{fx + lw / 2 * k:.2f},{fy - 0.6:.2f} L{fx - lw / 2 * k:.2f},{fy - 0.6:.2f} Z")
    d.add(fut, couleur)
    pied = ellipse(fx + s * 0.3, fy - 0.1, (rx - 0.4) * k, ry * k)
    d.add(pied, bas or couleur)
    if bas:
        my = (ty + fy) / 2
        d.add(path(f"M{(tx + fx) / 2 - lw / 2 - 0.4:.2f},{my:.2f} L{(tx + fx) / 2 + lw / 2 + 0.4:.2f},{my:.2f} "
                   f"L{fx + lw / 2 * k + 0.4:.2f},{fy:.2f} L{fx - lw / 2 * k - 0.4:.2f},{fy:.2f} Z"), bas, sil=False)
        d.add(pied, bas, sil=False)
    if coussin:
        d.add(ellipse(fx + s * 0.3, fy + 0.4, (rx - 1.3) * k, (ry - 0.8) * k), coussin, sil=False)
        d.raw(line(f"M{fx + s * 0.3 - 1.0 * k:.2f},{fy - 0.6:.2f} L{fx + s * 0.3 - 0.9 * k:.2f},{fy + 1.1:.2f} "
                   f"M{fx + s * 0.3 + 1.0 * k:.2f},{fy - 0.6:.2f} L{fx + s * 0.3 + 0.9 * k:.2f},{fy + 1.1:.2f}", OUTLINE, 0.5))
    return fx + s * 0.3, fy - 0.1, k


def _fouet(S, y0):
    """Une queue en fouet vue de face ou de dos, plantée en (0, y0) : celle de tecky2._queue_dressee(), aux mesures
    du chien. Rend (la forme fermée, le tracé de ses deux bords, sans la base)."""
    (w0, w1), L, c = S.get("queue_w", (5.6, 3.4)), S.get("queue_l", 15.0), S.get("queue_c", 3.2)
    return tk._queue_dressee(y0, w0, w1, L, c)


def _arriere_f(d, S, p, bx, b):
    """Ce qu'on voit d'un chien derrière sa tête, face à nous : sa croupe, au loin, qui dépasse un peu au-dessus du
    crâne, et sa queue (comme tecky2._arriere_face : la vue de dos à l'envers). Plus étroite que le crâne, sans pattes
    arrière : plus grosse, elle se lirait comme un bonnet."""
    hh, hw, hv = S["f_tete"]
    cx, cy = AXE - bx * 0.9, SOL + hh - hv * S.get("f_croupe", 0.42) + b * 0.6      # f_croupe : de combien elle dépasse
    rx, ry = hw * 0.60, hv * 0.92
    croupe = ellipse(cx, cy, rx, ry)
    d.clip("croupef", [croupe])
    genre = S["d_queue"]
    Tq = _tourne(p["queue"] * (0.5 if genre == "moignon" else 1) + (24 if genre == "panache" else 0), cx, cy - ry + 2)
    place = lambda x, y: Tq(cx + x, cy - ry + y)                # autour du sommet de la croupe
    if genre == "fouet":
        d.add(path(_trace(place, _fouet(S, 3.0)[0])), S["fur"])
    elif genre == "moignon":
        d.add(path(_ovale(place, 0, 0.2, 2.5, 2.2)), S["fur"])
    else:                             # panache : touffu, penché de côté, le bout blanc
        forme = path(_ovale(place, 0, -3.2, 3.7, 5.8))
        d.add(forme, S["ombre"])
        d.clip("panachef", [forme])
        d.add(path(_ovale(place, 0, -8.2, 4.2, 3.0)), S["clair"], sil=False, clip="panachef")
    d.add(croupe, S["fur"])
    d.add(ellipse(cx, cy - ry * 0.5, rx * 0.66, ry * 0.4), S["ombre"], sil=False, clip="croupef", opacity=0.3)


def face(S, p=None):
    """Un chien de face, vers la caméra."""
    p = p or pose()
    d = Drawing(W, H)
    b, bx = p["rebond"], p["balance"]
    (aA, lA), (aB, lB) = _foulee(p, 1.0, 2.8)
    if p["pattes"]:
        (aA, lA), (aB, lB) = (0.0, p["pattes"][0][1]), (0.0, p["pattes"][1][1])
    haut, bas_y, bw = S["f_corps"]
    hh = S["f_tete"][0]
    B = lambda x, y: (AXE + x + bx * (-y) / 30, SOL + y + b)      # le haut du corps se balance, les pieds restent
    hx = AXE + bx * (-hh) / 30 + p["tete"][0]
    hy = SOL + hh + b + p["tete"][1]

    _arriere_f(d, S, p, bx, b)
    for s, lv, a in ((-1, lA, aA), (1, lB, aB)):
        _patte_f(d, S, B, s, lv, a, S["fur"], S["bas"], S["clair"] if not S["bas"] else None, bx)
    C = _corps_f(S, B)
    poitrail = path(_trace(C, tk.CORPS_F))
    d.clip("poitrailf", [poitrail])
    d.add(poitrail, S["fur"])
    d.add(path(_ovale(C, 0, 35.0, 4.2 if S["ventre"] else 3.0, 8.5)), S["clair"] if S["ventre"] or S["fur"] == S["clair"] else S["fur"],
          sil=False, clip="poitrailf")
    # le collier, sous le menton
    yc = SOL + hh + S["f_tete"][2] * 0.95 + b
    d.add(path(f"M{AXE - 30:.2f},{yc - 1.2:.2f} L{AXE + 30:.2f},{yc - 1.2:.2f} L{AXE + 30:.2f},{yc + 3.4:.2f} L{AXE - 30:.2f},{yc + 3.4:.2f} Z"),
          COLLIER, sil=False, clip="poitrailf")
    for k in (-2, -1, 0, 1, 2):
        if abs(k) * 3.6 < bw * 0.72:
            d.add(circle(hx * 0.3 + (AXE + bx * (-hh) / 30) * 0.7 + k * 3.6, yc + 1.5, 1.15), CLOU, sil=False)
    tete_face(d, S, p, hx, hy)
    return d


def dos(S, p=None):
    """Un chien de dos : la croupe et la queue devant nous, l'arrière de la tête et ses oreilles."""
    p = p or pose()
    d = Drawing(W, H)
    b, bx = p["rebond"], p["balance"]
    (aA, lA), (aB, lB) = _foulee(p, 1.0, 2.8)
    if p["pattes"]:
        (aA, lA), (aB, lB) = (0.0, p["pattes"][0][1]), (0.0, p["pattes"][1][1])
    haut, bas_y, bw = S["f_corps"]
    hh, hw, hv = S["d_tete"]
    B = lambda x, y: (AXE + x + bx * (-y) / 30, SOL + y + b)

    for s, lv, a in ((-1, lB, aB), (1, lA, aA)):
        fx, fy, k = _patte_f(d, S, B, s, lv, -a, S["fur"], S["bas"], None, bx)
        d.add(ellipse(fx, fy + 0.5, 2.6 * k, 1.4 * k + 0.5 * min(lv, 1.6)), S["ombre"] if not S["bas"] else "#D9D2C4", sil=False)

    hx, hy = AXE + bx * (-hh) / 30 + p["tete"][0], SOL + hh + b + p["tete"][1]
    rot = _tourne(p["incline"], hx, hy + hv * 0.9)
    brut = lambda x, y: rot(hx + x, hy + y)
    _oreilles_f(d, S, p, brut, False)
    crane = path(_ovale(brut, 0, 0, hw, hv))
    d.add(crane, S["fur"])

    C = _corps_f(S, B)
    corps = path(_trace(C, tk.CORPS_D.replace("M-4.6,21", "M-4.6,23").replace("4.6,21 Z", "4.6,23 Z")))
    d.clip("corpsd", [corps])
    d.add(corps, S["fur"])
    for forme, couleur in S["d_taches"]:
        d.add(path(_trace(B, forme)), S[couleur], sil=False, clip="corpsd")
    # le collier, sous la tête
    yc = SOL + hh + hv * 0.86 + b
    d.add(path(f"M{AXE - 30:.2f},{yc - 1.2:.2f} L{AXE + 30:.2f},{yc - 1.2:.2f} L{AXE + 30:.2f},{yc + 3.4:.2f} L{AXE - 30:.2f},{yc + 3.4:.2f} Z"),
          COLLIER, sil=False, clip="corpsd")

    # la queue, devant nous
    qy = bas_y - 7                    # son attache, sur la croupe
    genre = S["d_queue"]
    if genre == "fouet":
        Tq = _tourne(p["queue"], 0, qy, B)
        forme, bords = _fouet(S, qy)
        d.add(path(_trace(Tq, forme)), S["fur"])
        d.raw(line(_trace(Tq, bords), OUTLINE, 1.3))
    elif genre == "moignon":          # un petit bout de queue posé sur la croupe : un arc, pas un rond cerné
        Tq = _tourne(p["queue"] * 0.5, 0, qy + 3, B)
        d.raw(line(_trace(Tq, f"M-3.4,{qy + 1.6:.2f} C-3.6,{qy - 3.4:.2f} 3.6,{qy - 3.4:.2f} 3.4,{qy + 1.6:.2f}"), OUTLINE, 1.3))
    else:                             # panache : une grosse queue touffue qui pend, le bout blanc
        Tq = _tourne(p["queue"] * 0.7, 0, qy - 2, B)
        forme = _ovale(Tq, 0, qy + 6, 4.6, 9.5)
        d.add(path(forme), S["ombre"])
        d.raw(line(forme, OUTLINE, 1.2))
        d.clip("panache", [path(forme)])
        d.add(path(_ovale(Tq, 0, qy + 14.5, 5, 4.2)), S["clair"], sil=False, clip="panache")

    _oreilles_f(d, S, p, brut, True)
    return d


# ====================================================================== IMAGES ET ANIMATIONS
VUES = {"right": profil, "down": face, "up": dos}


def image(dog, view, p, tr=""):
    """SVG d'une image du jeu : le chien `dog`, la pose p, dans la vue donnée."""
    S = CHIENS[dog]
    w, h, ox, oy = CADRE
    d = VUES[view](S, p)
    d.w, d.h = w, h
    if view == "right":
        rx, dx = (S["tete"][0] - S["queue_pivot"][0]) * 0.56 + 6, 2
    else:
        rx, dx = S["f_corps"][2] + 4, 0
    d.under.append(f'<ellipse cx="{ox + dx * ECH:.2f}" cy="{oy + 0.2:.2f}" rx="{rx * ECH:.2f}" ry="{2.9 * ECH:.2f}" fill="#000" opacity="0.2"/>')
    return d.svg(f"translate({ox - AXE * ECH:.2f} {oy - SOL * ECH:.2f}) scale({ECH}) {tr}".strip(), outline_w=TRAIT)


def a_idle(view):
    wag = [-6, 0, 6, 0] if view == "right" else [-12, 0, 12, 0]
    bob = [0, 0.4, 0.7, 0.4]
    return [(pose(rebond=bob[i], queue=wag[i], yeux="fermes" if i == 3 else None), "") for i in range(4)]


def a_walk(view):
    """Le trot, en 8 images, comme celui de Tecky."""
    out = []
    for i in range(8):
        a = i / 8 * 2 * math.pi
        q = dict(pas=i / 8, rebond=-1.0 * abs(math.sin(a)))
        if view == "right":
            q.update(tangage=1.4 * math.sin(2 * a + 0.6), tete=(0, 0.6 * math.sin(2 * a - 0.9)),
                     oreille=6 * math.sin(2 * a - 1.4), queue=-3 + 8 * math.sin(a))
        else:
            k = -1 if view == "down" else 1
            q.update(balance=1.2 * k * math.sin(a), incline=3.5 * k * math.sin(a - 0.6), tete=(0, 0.6 * math.sin(2 * a - 0.9)),
                     oreille=5 * math.sin(2 * a - 1.4), penche=5 * k * math.sin(a - 1.0), queue=16 * k * math.sin(a - 0.5))
        out.append((pose(**q), ""))
    return out


def a_bark(view):
    ms = [0.25, 0.8, 1.0, 0.45]
    up = [0, 6, 10, 3]
    out = []
    for i in range(4):
        if view == "right":
            out.append((pose(gueule=ms[i], releve=up[i], oreille=up[i] * 0.9, queue=-12, tete=(0.05 * up[i], -0.08 * up[i])), ""))
        else:
            out.append((pose(gueule=ms[i], tete=(0, -up[i] / 4), oreille=up[i] * 0.8, queue=12), ""))
    return out


def a_bite(view):
    lunge = [-2.0, 4.0, 7.0, 5.0, 0.8]
    ms = [0.35, 1.0, 1.0, 0.0, 0.0]
    out = []
    for i in range(5):
        L, m = lunge[i], ms[i]
        if view == "right":
            out.append((pose(elan=L * 0.5, tete=(L * 0.7, 0.1 * L), gueule=m, oreille=max(0, L) * 2.5, queue=-10,
                             releve=2 if m else -2), f"translate({L * 0.5:.2f} 0)"))
        elif view == "down":
            out.append((pose(gueule=m, tete=(0, L * 0.6), oreille=max(0, L) * 2.0), f"translate(0 {L * 0.4:.2f})"))
        else:
            out.append((pose(tete=(0, -L * 0.6), oreille=max(0, L) * 2.0), f"translate(0 {-L * 0.35:.2f})"))
    return out


def a_hurt(view):
    dx, dy = {"right": (-3.0, 0), "down": (0, -3.2), "up": (0, 3.2)}[view]
    return [(pose(yeux="plisses", oreille=16, queue=-16), f"translate({dx} {dy})"),
            (pose(yeux="plisses", oreille=9, queue=-10), f"translate({dx / 2} {dy / 2})")]


def a_ko(view):
    """Profil uniquement : il titube, bascule, et finit sur le dos, les quatre fers en l'air."""
    return [
        (pose(yeux="fermes", oreille=-8), f"rotate(-7 {AXE} {SOL})"),
        (pose(yeux="croix", oreille=18, queue=-24, gueule=0.4), f"translate(4 0) rotate(-20 {AXE} {SOL}) translate(0 -2)"),
        (pose(attitude="dos", yeux="croix", gueule=0.7, oreille=40, queue=0), ""),
        (pose(attitude="dos", yeux="croix", gueule=0.7, oreille=44, queue=4, rebond=0.8), ""),
    ]


ANIMS = {   # nom : (fonction, images par seconde, vues) — mêmes noms et mêmes nombres d'images qu'avant, sauf la marche
    "idle": (a_idle, 6, ("down", "up", "right")),
    "walk": (a_walk, 16, ("down", "up", "right")),
    "bark": (a_bark, 10, ("down", "up", "right")),
    "bite": (a_bite, 14, ("down", "up", "right")),
    "hurt": (a_hurt, 10, ("down", "up", "right")),
    "ko":   (a_ko, 6, ("right",)),
}


def frames(dog, anim, view):
    """Liste de SVG (chaînes) pour un chien, une animation et une vue ('right', 'down', 'up')."""
    return [image(dog, view, p, tr) for p, tr in ANIMS[anim][0](view)]


for _S in CHIENS.values():           # le bas des pattes du côté caché, un peu plus sombre
    _S["bas_ombre"] = {"#CC7F3D": "#A8632B", "#F6F3EC": "#D9D2C4"}.get(_S["bas"])
    if _S["fur"] in ("#34302F", "#33313A"):
        _S["croix"] = "#F6F3EC"      # yeux en croix et plissés : clairs sur un pelage noir


if __name__ == "__main__":
    from spritelib import render_svg, PAD
    from PIL import Image
    racine = os.path.dirname(os.path.abspath(__file__))
    fond = (126, 200, 100, 255)
    k = 8
    lignes = []
    for dog in CHIENS:
        ims = [render_svg(image(dog, v, pose()), 48, 48, k, PAD) for v in ("right", "down", "up")]
        ims.append(render_svg(frames(dog, "bark", "right")[2], 48, 48, k, PAD))
        ims.append(render_svg(frames(dog, "ko", "right")[2], 48, 48, k, PAD))
        lignes.append(ims)
    w, h = lignes[0][0].size
    out = Image.new("RGBA", (w * 6, h * len(lignes)), fond)
    tecky = [render_svg(tk.image(v, pose()), *tk.CADRE[v][:2], k, PAD) for v in ("right", "down", "up")]
    for j, ims in enumerate(lignes):
        for i, im in enumerate(ims):
            out.alpha_composite(im, (i * w, j * h))
        if j < 3:
            out.alpha_composite(tecky[j], (5 * w, j * h))
    fn = os.path.join(racine, "reference", "v2", "chiens_v2.png")
    out.convert("RGB").save(fn)
    print(fn, out.size)
