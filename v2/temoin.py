#!/usr/bin/env python3
"""
Écran témoin de la v2 (PLAN_V2.md, lot 1) : le jardin de la niche, cadré comme au début d'une partie, redessiné à
la qualité visée. Une image fixe, pas le jeu : elle sert de référence à tous les lots graphiques.

    python3 v2/temoin.py            # reference/v2/temoin_niche.png (1920 x 1080) et avant_apres.png
    python3 v2/temoin.py --avant    # refait d'abord reference/v2/avant_niche.png : une capture du jeu actuel
                                    # (il faut web/index.html, donc python3 pack_web.py, et chromium-browser)

Tout part de carte.json (terrain, décors, objets, canards) et rien de ce qui est dessiné ici ne demande au moteur
autre chose que ce qu'il sait déjà faire, ou ce que le plan prévoit (voir « Ce que le témoin engage ») :
- le sol est calculé d'après les coins de la carte (comme les tuiles), avec des bords qui ondulent : mêmes formes,
  mêmes collisions ; un bruit ancré dans le monde (hash3, celui du jeu) donne les nuances de l'herbe ;
- les ombres portées sont la silhouette de chaque sprite, couchée du côté opposé au soleil, et accrochée à la
  ligne où l'objet touche le sol (nature.Sprite.sol) ;
- les sprites sont posés par leur pied et triés en profondeur, comme dans le jeu.
"""
import io
import math
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)
sys.path.insert(0, ICI)

import cairosvg  # noqa: E402

import butterflies  # noqa: E402
import carte  # noqa: E402
import ducks  # noqa: E402
import items  # noqa: E402
import nature  # noqa: E402
import tecky2  # noqa: E402
from spritelib import render_svg, PAD  # noqa: E402

SORTIE = os.path.join(RACINE, "reference", "v2")
LARG, HAUT = 1920, 1080
K = 4                   # pixels par unité (une unité = un pixel du jeu en x1 ; la caméra du jeu voit 480 x 270 unités)
T = 32                  # unités par tuile
CAM = (-30.0, -20.5)    # coin haut-gauche de la caméra, en unités : celle du début de partie (camX -60, camY -41)
SOLEIL = (0.6, 0.8)     # sens de la lumière au sol : elle vient d'en haut à gauche
OMBRE = (0.45, 0.23)
CONTACT = 5              # « contour » : le bas de la silhouette compte comme sol jusqu'à 5 unités du point le plus bas    # ombre portée : décalage vers la droite et vers le bas, par unité de hauteur
TECKY = tecky2.ECH      # taille de Tecky à l'écran : celle du jeu

# Habillage : la mare perd trois de ses coins (elle était carrée). C'est une retouche de carte.json, à faire à
# l'éditeur au lot 4 ; ici, elle n'est appliquée qu'à l'image.
RETOUCHES = {(8, 1): "grass", (11, 1): "grass", (8, 4): "grass"}


def rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.float32)


def ecran(tx, ty):
    """Position à l'écran (pixels) d'un point de la carte (tuiles)."""
    return (tx * T - CAM[0]) * K, (ty * T - CAM[1]) * K


# ====================================================================== bruit ancré dans le monde
def h3(a, b, c):
    """hash3 de game.js et de pack_web.py, sur des tableaux d'entiers : nombre dans [0, 1[."""
    M = 0xFFFFFFFF
    a, b = np.asarray(a, dtype=np.int64), np.asarray(b, dtype=np.int64)
    h = ((a * 374761393) ^ (b * 668265263) ^ (c * 1274126177)) & M
    h = ((h ^ (h >> 13)) * 1103515245) & M
    return (h ^ (h >> 16)) / 4294967296.0


def bruit(X, Y, periode, graine):
    """Bruit de valeur lisse (0..1) : des valeurs tirées par h3 sur une grille de `periode` unités."""
    gx, gy = X / periode, Y / periode
    i, j = np.floor(gx).astype(np.int64), np.floor(gy).astype(np.int64)
    u, v = gx - i, gy - j
    u, v = u * u * (3 - 2 * u), v * v * (3 - 2 * v)
    return (h3(i, j, graine) * (1 - u) * (1 - v) + h3(i + 1, j, graine) * u * (1 - v)
            + h3(i, j + 1, graine) * (1 - u) * v + h3(i + 1, j + 1, graine) * u * v)


def hasard(a, b, c):
    return float(h3(a, b, c))


# ====================================================================== sol
def champ(g, terrain, X, Y):
    """Présence d'un terrain (0..1) en chaque pixel, interpolée entre les coins de la carte : le niveau 0,5 passe au
    milieu de deux coins différents, comme le bord des tuiles du jeu."""
    mh, mw = len(g) - 1, len(g[0]) - 1
    ind = np.array([[1.0 if v == terrain else 0.0 for v in ligne] for ligne in g], dtype=np.float32)
    fx, fy = X / T, Y / T
    i, j = np.floor(fx).astype(int), np.floor(fy).astype(int)
    u, v = fx - i, fy - j
    u, v = u * u * (3 - 2 * u), v * v * (3 - 2 * v)
    c = lambda a, b: ind[np.clip(b, 0, mh), np.clip(a, 0, mw)]
    return c(i, j) * (1 - u) * (1 - v) + c(i + 1, j) * u * (1 - v) + c(i, j + 1) * (1 - u) * v + c(i + 1, j + 1) * u * v


def bord(I):
    """Distance au bord d'un terrain, en unités (positive à l'intérieur), et éclairage du bord (-1..1 : positif quand
    l'intérieur est du côté de l'ombre, c'est-à-dire sur les bords du haut et de gauche)."""
    gy, gx = np.gradient(I)
    n = np.hypot(gx, gy) + 1e-6
    du = np.clip((I - 0.5) / (n * K), -60, 60)
    return du, (gx * SOLEIL[0] + gy * SOLEIL[1]) / n


def entre(v, a, b, flou=0.3):
    """1 quand a < v < b, avec des bords adoucis sur `flou`."""
    return np.clip((v - a) / flou + 0.5, 0, 1) * np.clip((b - v) / flou + 0.5, 0, 1)


def poser(img, couleur, alpha):
    img += (rgb(couleur) - img) * np.clip(alpha, 0, 1)[..., None]


def sol(g):
    """Le sol : herbe nuancée, chemin de terre, mare. Rend l'image (float, 0..255) et les champs utiles au semis."""
    xs = (np.arange(LARG) + 0.5) / K + CAM[0]
    ys = (np.arange(HAUT) + 0.5) / K + CAM[1]
    X, Y = np.meshgrid(xs, ys)
    onde = (bruit(X, Y, 22, 21) - 0.5) * 0.16 + (bruit(X, Y, 90, 22) - 0.5) * 0.2     # les bords ondulent

    # herbe : grandes plages un peu plus sombres, plus claires, plus chaudes
    img = np.empty((HAUT, LARG, 3), dtype=np.float32)
    img[:] = rgb("#78C657")
    m = 0.62 * bruit(X, Y, 150, 11) + 0.38 * bruit(X, Y, 58, 12)
    chaud = 0.6 * bruit(X, Y, 120, 13) + 0.4 * bruit(X, Y, 46, 14)
    e = 0.004
    poser(img, "#88D163", np.clip((m - 0.585) / e, 0, 1))
    poser(img, "#98D968", np.clip((m - 0.665) / e, 0, 1) * 0.85)
    poser(img, "#6CBC50", np.clip((0.43 - m) / e, 0, 1))
    poser(img, "#61B04A", np.clip((0.345 - m) / e, 0, 1) * 0.9)
    poser(img, "#A6DA62", np.clip((chaud - 0.69) / e, 0, 1) * 0.55)

    # chemin de terre : lèvre d'herbe sombre, bord, ombre du talus en haut et à gauche, liseré clair en bas à droite
    It = champ(g, "dirt", X, Y) + onde
    dt, lt = bord(It)
    poser(img, "#5FA550", entre(dt, -1.3, 0.2))
    poser(img, "#DDB980", np.clip(dt / 0.3 + 0.5, 0, 1))
    grain = bruit(X, Y, 34, 31)
    poser(img, "#E7C993", np.clip(dt / 0.3 - 20, 0, 1) * np.clip((grain - 0.52) / 0.01, 0, 1) * 0.8)
    poser(img, "#D2AB70", np.clip(dt / 0.3 - 12, 0, 1) * np.clip((0.3 - grain) / 0.01, 0, 1) * 0.7)
    poser(img, "#C29A5F", entre(dt, 0.0, 1.5))
    poser(img, "#B98F57", entre(dt, 0.0, 4.4) * np.clip(lt * 3 - 0.3, 0, 1))
    poser(img, "#EED6A6", entre(dt, 1.5, 3.0) * np.clip(-lt * 3 - 0.3, 0, 1))

    # mare : berge de sable, liseré, eau peu profonde, eau plus sombre au milieu, ombre de la berge, écume
    Ie = champ(g, "water", X, Y) + onde * 0.8
    de, le = bord(Ie)
    poser(img, "#93B35A", entre(de, -4.4, -3.2))
    poser(img, "#EDDFAE", entre(de, -3.6, 0.3))
    poser(img, "#D9C68C", entre(de, -1.2, 0.3))
    poser(img, "#9FDFF0", np.clip(de / 0.3 + 0.5, 0, 1))
    poser(img, "#78C9EC", np.clip((de - 4.6) / 0.3, 0, 1))
    poser(img, "#5FB5E5", np.clip((de - 9.5) / 0.3, 0, 1))
    fond = bruit(X, Y, 40, 41)
    poser(img, "#52A8DC", np.clip((de - 16) / 0.3, 0, 1) * np.clip((fond - 0.5) / 0.01, 0, 1))
    poser(img, "#69B4D8", entre(de, 0.9, 4.2) * np.clip(le * 3 - 0.4, 0, 1))
    ecume = np.clip((bruit(X, Y, 9, 42) - 0.36) / 0.02, 0, 1)
    poser(img, "#FFFFFF", entre(de, 1.5, 2.5) * np.clip(-le * 3 - 0.3, 0, 1) * ecume * 0.85)
    poser(img, "#2F7DAE", entre(de, 0.0, 0.85, 0.25))
    return img, dict(m=m, dt=dt, de=de)


def details(champs):
    """Ce qui est posé à plat sur le sol : brins d'herbe, fleurs en bouquets, cailloux du chemin, nénuphars, éclats de
    l'eau, pétales, traces de pattes. Un SVG en unités du monde ; tout est semé par hash3 sur la position."""
    m, dt, de = champs["m"], champs["dt"], champs["de"]
    out = []

    def lieu(x, y):                       # 'herbe', 'terre', 'eau' ou None (au bord), au point (x, y) en unités
        px, py = int((x - CAM[0]) * K), int((y - CAM[1]) * K)
        if not (0 <= px < LARG and 0 <= py < HAUT):
            return None
        if de[py, px] > 3:
            return "eau"
        if dt[py, px] > 2.5 and de[py, px] < -6:
            return "terre"
        if dt[py, px] < -2 and de[py, px] < -6:
            return "herbe"
        return None

    def teinte(x, y):
        px, py = int((x - CAM[0]) * K), int((y - CAM[1]) * K)
        v = m[py, px]
        return ("#4E9F43", 0.6) if v < 0.43 else (("#62B34C", 0.26) if v > 0.585 else ("#56A848", 0.4))

    x0, y0 = int(CAM[0] // 8) - 1, int(CAM[1] // 8) - 1
    nx, ny = LARG // K // 8 + 3, HAUT // K // 8 + 3

    def fleur(x, y, genre, k=1.0):
        petale, coeur = {"paquerette": ("#FFFFFF", "#F6C945"), "bouton": ("#FBD84A", "#EE9A2B"),
                         "rose": ("#F9A8C4", "#FFF1B8"), "bleue": ("#A9C4F5", "#FFF1B8")}[genre]
        s = [f'<circle cx="{x + 0.5:.2f}" cy="{y + 0.7:.2f}" r="{2.1 * k:.2f}" fill="#4F9647" opacity="0.55"/>']
        for i in range(5):
            a = i * 2 * math.pi / 5 + x
            s.append(f'<circle cx="{x + 1.3 * k * math.cos(a):.2f}" cy="{y + 1.3 * k * math.sin(a):.2f}" '
                     f'r="{1.0 * k:.2f}" fill="{petale}"/>')
        s.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{0.85 * k:.2f}" fill="{coeur}"/>')
        return "".join(s)

    # brins d'herbe : plus nombreux dans les plages sombres
    for j in range(ny):
        for i in range(nx):
            cx, cy = x0 + i, y0 + j
            x = (cx + hasard(cx, cy, 51)) * 8
            y = (cy + hasard(cx, cy, 52)) * 8
            if lieu(x, y) != "herbe":
                continue
            couleur, proba = teinte(x, y)
            r = hasard(cx, cy, 53)
            if r < proba:
                a = 2.6 + 1.4 * hasard(cx, cy, 54)
                out.append(f'<path d="M{x - 1.5:.2f},{y:.2f} l-0.9,{-a * 0.75:.2f} M{x:.2f},{y:.2f} l0.1,{-a:.2f} '
                           f'M{x + 1.5:.2f},{y:.2f} l1.1,{-a * 0.7:.2f}" stroke="{couleur}" stroke-width="0.8" '
                           f'stroke-linecap="round" fill="none"/>')
            elif r > 0.985:
                out.append(fleur(x, y, ("paquerette", "bouton", "paquerette", "rose")[int(hasard(cx, cy, 55) * 4)], 0.85))

    # bouquets de fleurs (ceux de carte.json, « fleurs », et quelques autres pour l'habillage)
    for n, (tx, ty, genre) in enumerate(((7.0, 4.25, "paquerette"), (10.3, 5.5, "bouton"), (1.95, 5.2, "rose"),
                                         (5.5, 6.05, "paquerette"), (12.0, 5.75, "bleue"), (2.1, 3.3, "bouton"),
                                         (13.4, 3.3, "paquerette"), (6.9, 2.5, "bouton"), (0.9, 9.3, "bouton"))):
        for k in range(11):
            a, r = hasard(n, k, 61) * 2 * math.pi, 3 + 13 * math.sqrt(hasard(n, k, 62))
            x, y = tx * T + r * math.cos(a) * 1.25, ty * T + r * math.sin(a) * 0.8
            if lieu(x, y) == "herbe":
                out.append(fleur(x, y, genre if hasard(n, k, 63) < 0.8 else "paquerette", 0.9 + 0.35 * hasard(n, k, 64)))

    # cailloux et grains du chemin
    for j in range(ny):
        for i in range(nx):
            cx, cy = x0 + i, y0 + j
            x, y = (cx + hasard(cx, cy, 71)) * 8, (cy + hasard(cx, cy, 72)) * 8
            if lieu(x, y) != "terre":
                continue
            r = hasard(cx, cy, 73)
            if r < 0.2:
                a = 0.5 + 0.9 * hasard(cx, cy, 74)
                out.append(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{a:.2f}" ry="{a * 0.62:.2f}" fill="#C39A5F"/>')
            elif r > 0.955:
                out.append(f'<ellipse cx="{x + 0.4:.2f}" cy="{y + 0.6:.2f}" rx="2.2" ry="1.3" fill="#B08A52" opacity="0.7"/>'
                           f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="2" ry="1.3" fill="#D8D2C6" stroke="#8D8577" stroke-width="0.5"/>')

    # galets sur la berge
    for tx, ty in ((7.55, 3.2), (9.2, 0.42), (11.62, 2.9), (10.4, 4.62), (11.1, 4.5), (8.3, 1.25), (7.6, 2.3)):
        x, y = tx * T, ty * T
        out.append(f'<ellipse cx="{x + 0.5:.2f}" cy="{y + 0.9:.2f}" rx="2.6" ry="1.5" fill="#B9A46F" opacity="0.8"/>'
                   f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="2.4" ry="1.6" fill="#C9CDD1" stroke="#7F868E" stroke-width="0.55"/>'
                   f'<ellipse cx="{x - 0.6:.2f}" cy="{y - 0.5:.2f}" rx="1" ry="0.5" fill="#FFFFFF" opacity="0.7"/>')

    # nénuphars
    for tx, ty, r, fl in ((10.75, 3.55, 4.6, True), (11.05, 3.2, 3.2, False), (8.75, 1.95, 3.8, False), (10.3, 3.85, 2.8, False)):
        x, y = tx * T, ty * T
        out.append(f'<ellipse cx="{x + 1:.2f}" cy="{y + 1.4:.2f}" rx="{r:.2f}" ry="{r * 0.78:.2f}" fill="#2F7DAE" opacity="0.35"/>'
                   f'<path d="M{x:.2f},{y:.2f} L{x + r:.2f},{y - r * 0.28:.2f} A{r:.2f},{r * 0.78:.2f} 0 1 0 {x + r * 0.86:.2f},{y + r * 0.4:.2f} Z" '
                   f'fill="#5DB257" stroke="#2C6E3C" stroke-width="0.6" stroke-linejoin="round"/>'
                   f'<path d="M{x - r * 0.7:.2f},{y - r * 0.2:.2f} Q{x - r * 0.3:.2f},{y - r * 0.6:.2f} {x + r * 0.3:.2f},{y - r * 0.55:.2f}" '
                   f'stroke="#8ED278" stroke-width="0.8" fill="none" stroke-linecap="round"/>')
        if fl:
            for i in range(6):
                a = i * math.pi / 3
                out.append(f'<ellipse cx="{x - 1.2 + 1.5 * math.cos(a):.2f}" cy="{y - 0.4 + 1.1 * math.sin(a):.2f}" rx="1.3" ry="0.9" '
                           f'fill="#FFC7DB" stroke="#C9698F" stroke-width="0.35" transform="rotate({math.degrees(a):.0f} '
                           f'{x - 1.2 + 1.5 * math.cos(a):.2f} {y - 0.4 + 1.1 * math.sin(a):.2f})"/>')
            out.append(f'<circle cx="{x - 1.2:.2f}" cy="{y - 0.4:.2f}" r="0.9" fill="#F6C945"/>')

    # éclats et vaguelettes de l'eau profonde
    for n in range(40):
        tx, ty = 7.6 + 4.2 * hasard(n, 1, 81), 0.5 + 4.2 * hasard(n, 2, 81)
        x, y = tx * T, ty * T
        px, py = int((x - CAM[0]) * K), int((y - CAM[1]) * K)
        if not (0 <= px < LARG and 0 <= py < HAUT) or de[py, px] < 9:
            continue
        if hasard(n, 3, 81) < 0.35:
            s = 1.3 + hasard(n, 4, 81)
            out.append(f'<path d="M{x:.2f},{y - s:.2f} Q{x:.2f},{y:.2f} {x + s:.2f},{y:.2f} Q{x:.2f},{y:.2f} {x:.2f},{y + s:.2f} '
                       f'Q{x:.2f},{y:.2f} {x - s:.2f},{y:.2f} Q{x:.2f},{y:.2f} {x:.2f},{y - s:.2f} Z" fill="#FFFFFF" opacity="0.9"/>')
        else:
            w = 2.4 + 2.4 * hasard(n, 5, 81)
            out.append(f'<path d="M{x - w:.2f},{y:.2f} q{w:.2f},-1.5 {2 * w:.2f},0" stroke="#C9EEF9" stroke-width="0.8" '
                       f'fill="none" stroke-linecap="round" opacity="0.9"/>')

    # pétales tombés au pied du cerisier
    for k in range(26):
        a, r = hasard(k, 7, 91) * 2 * math.pi, 5 + 30 * math.sqrt(hasard(k, 8, 91))
        x, y = 12.8 * T + 6 + r * math.cos(a) * 1.3, 4.3 * T + 3 + r * math.sin(a) * 0.55
        if lieu(x, y) == "herbe":
            out.append(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="1.25" ry="0.75" fill="#FBC3D7" '
                       f'transform="rotate({hasard(k, 9, 91) * 180:.0f} {x:.2f} {y:.2f})"/>')

    # traces de pattes : un trésor est enterré là (carte.json, « dig »)
    for dx, dy, a in ((-5, 2, -20), (2, -3, 10), (8, 3, 25)):
        x, y = 12.5 * T + dx, 6.5 * T - 9 + dy
        g = [f'<ellipse cx="0" cy="1" rx="1.9" ry="1.5"/>'] + [f'<circle cx="{u}" cy="{v}" r="0.8"/>'
                                                              for u, v in ((-2, -1.2), (-0.7, -2.2), (0.8, -2.2), (2.1, -1.2))]
        out.append(f'<g transform="translate({x:.2f} {y:.2f}) rotate({a})" fill="#7A5A34" opacity="0.62">{"".join(g)}</g>')

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{LARG}" height="{HAUT}" '
           f'viewBox="{CAM[0]} {CAM[1]} {LARG / K} {HAUT / K}">{"".join(out)}</svg>')
    return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=LARG,
                                                                  output_height=HAUT))).convert("RGBA")


# ====================================================================== scène
def scene():
    """Les sprites : (image, pied dans l'image, position en tuiles, sol, calque). sol : la ligne de contact d'où part
    l'ombre portée ("pied", "contour" ou des points en pixels de l'image ; None : pas d'ombre). Positions de
    carte.json pour la niche, les arbres, les buissons, le rocher, les objets et les canards ; la lisière autour."""
    out = []

    def nat(nom, tx, ty, k=1.0, miroir=False):
        sp = nature.CATALOGUE[nom]()
        im = nature.rendre(sp, K * k)
        px = lambda x, y: ((x + PAD) * K * k, (y + PAD) * K * k)
        pied, sol = px(*sp.pied), sp.sol if isinstance(sp.sol, str) else [px(x, y) for x, y in sp.sol]
        if miroir:
            im, pied = im.transpose(Image.FLIP_LEFT_RIGHT), (im.width - pied[0], pied[1])
            if not isinstance(sol, str):
                sol = [(im.width - x, y) for x, y in reversed(sol)]
        out.append((im, pied, tx, ty, sol, 0))

    def vieux(svg, w, h, origine, tx, ty, calque=0, miroir=False):        # un sprite du jeu actuel, tel quel
        im = render_svg(svg, w, h, K, PAD)
        pied = ((origine[0] + PAD) * K, (origine[1] + PAD) * K)
        if miroir:
            im, pied = im.transpose(Image.FLIP_LEFT_RIGHT), (im.width - pied[0], pied[1])
        out.append((im, pied, tx, ty, None, calque))

    # lisière : de grands arbres sombres hors de la carte, des fourrés devant
    for n in range(12):
        y = -0.9 + n * 0.88 + 0.3 * hasard(n, 1, 101)
        nat("chene_sombre", -1.12 + 0.25 * hasard(n, 2, 101), y, 0.86 + 0.2 * hasard(n, 3, 101), miroir=n % 2 == 0)
    for n in range(13):
        x = 0.4 + n * 1.22 + 0.4 * hasard(n, 4, 101)
        nat("chene_sombre", x, -0.52 + 0.3 * hasard(n, 5, 101), 0.86 + 0.2 * hasard(n, 6, 101), miroir=n % 2 == 1)
    for n in range(14):
        nat(("buisson_sombre", "buisson_sombre", "buisson_baies")[n % 3], 0.0 + 0.16 * hasard(n, 7, 101),
            0.2 + n * 0.66 + 0.2 * hasard(n, 8, 101), 0.92 + 0.22 * hasard(n, 9, 101))
    for n in range(21):
        nat(("buisson_sombre", "buisson", "buisson_sombre", "buisson_rose")[n % 4], 0.7 + n * 0.7 + 0.25 * hasard(n, 10, 101),
            0.22 + 0.2 * hasard(n, 11, 101), 1.0 + 0.25 * hasard(n, 12, 101))

    # décors de carte.json (même place, nouveaux dessins : un modèle par arbre)
    nat("niche", 3.5, 3.2, 1.12)
    nat("gamelle", 4.62, 3.28, 1.12)
    nat("buisson_fleuri", 5.8, 3.4, 1.05)
    nat("chene", 6.5, 1.2, 0.86)
    nat("chene", 1.0, 1.4, 0.8, miroir=True)
    nat("bouleau", 13.5, 1.6, 0.92)
    nat("buisson_baies", 12.2, 1.1)
    nat("cerisier", 12.8, 4.3, 0.9)
    nat("jeune_arbre", 14.8, 5.2, 1.0)
    nat("rocher", 7.6, 5.3, 1.05)
    nat("chene", 1.2, 7.0, 0.86)
    # habillage : roseaux au bord de la mare
    nat("roseaux", 8.02, 4.38, 1.0)
    nat("roseaux", 8.5, 4.6, 0.8, miroir=True)
    nat("roseaux", 11.55, 1.55, 0.9)

    # Tecky, de profil, en route vers sa balle
    p = tecky2.pose(pas=0.1, queue=-10, expr="joyeux", oreille=6, rebond=-0.5)
    k = K * TECKY
    im = render_svg(tecky2.profil(p).svg(outline_w=1.8 / TECKY), tecky2.W, tecky2.H, k, PAD)
    out.append((im, ((36 + PAD) * k, (tecky2.SOL + PAD) * k), 4.95, 5.3, "pied", 0))

    # sprites du jeu actuel, gardés tels quels : objets, canards, papillons
    for nom, tx, ty in (("ball", 6.3, 5.4), ("bone", 6.0, 7.5), ("squeaky", 9.5, 6.2)):
        vieux(items.item_frames(nom)[0], 32, 32, (16, 16), tx, ty)
    for kind, tx, ty in (("duck_f", 9.9, 2.4), ("duckling", 9.4, 2.55), ("duckling", 9.0, 2.7), ("duckling", 8.6, 2.85)):
        vieux(ducks.frames(kind, "swim")[0], 32, 32, ducks.ORIGIN, tx, ty)
    vieux(butterflies.frames("yellow")[0], 24, 24, (12, 12), 9.0, 5.6, calque=1)
    vieux(butterflies.frames("orange")[1], 24, 24, (12, 12), 6.25, 2.75, calque=1)
    return out


def ombre_portee(ombres, im, pied, place, sol):
    """Ajoute à `ombres` (tableau HAUT x LARG, 0..1) l'ombre portée d'un sprite posé à `place` (pixels de l'écran).
    Chaque colonne de la silhouette est couchée à partir du point où elle touche le sol : un pixel à la hauteur h
    au-dessus de ce point tombe h * OMBRE plus loin, à droite et vers le bas. L'ombre part donc du bas de l'objet,
    même quand ce bas n'est pas une horizontale (le mur de la niche qui fuit, le dessous d'un buisson)."""
    A = np.asarray(im.getchannel("A"), dtype=np.float32) / 255.0
    h, w = A.shape
    cols = np.arange(w)
    if sol == "pied":
        base = np.full(w, pied[1], dtype=np.float32)
    elif sol == "contour":
        plein = A > 0.5
        bas = np.where(plein.any(axis=0), h - 1 - np.argmax(plein[::-1], axis=0), 0)        # bas de chaque colonne
        base = np.maximum(bas, bas.max() - CONTACT * K).astype(np.float32)
    else:
        base = np.interp(cols, [x for x, _ in sol], [y for _, y in sol]).astype(np.float32)   # prolongée à plat
    x0, y0 = place[0] - pied[0], place[1] - pied[1]
    sx, sy = OMBRE
    for hh in range(int(base.max()) + 1):
        ys = np.round(base - hh).astype(int)
        ok = (ys >= 0) & (ys < h)
        a = np.where(ok, A[np.clip(ys, 0, h - 1), cols], 0.0)
        X = np.round(x0 + cols + hh * sx).astype(int)
        Y = np.round(y0 + base + hh * sy).astype(int)
        ok &= (a > 0.02) & (X >= 0) & (X < LARG) & (Y >= 0) & (Y < HAUT)
        np.maximum.at(ombres, (Y[ok], X[ok]), a[ok])


def coller(dest, im, x, y):
    """alpha_composite qui accepte un sprite dépassant de l'écran."""
    x0, y0 = max(0, -x), max(0, -y)
    x1, y1 = min(im.width, dest.width - x), min(im.height, dest.height - y)
    if x1 > x0 and y1 > y0:
        dest.alpha_composite(im.crop((x0, y0, x1, y1)), (x + x0, y + y0))


def temoin():
    c = carte.charger()
    g = carte.terrain_grid(c)
    for (x, y), terrain in RETOUCHES.items():
        g[y][x] = terrain
    fond, champs = sol(g)
    fond = np.asarray(Image.alpha_composite(
        Image.fromarray(np.clip(fond, 0, 255).astype(np.uint8), "RGB").convert("RGBA"), details(champs)).convert("RGB"),
        dtype=np.float32)
    sprites = scene()
    ombres = np.zeros((HAUT, LARG), dtype=np.float32)
    for im, pied, tx, ty, ligne, _ in sprites:
        if ligne is not None:
            ombre_portee(ombres, im, pied, ecran(tx, ty), ligne)
    masque = Image.fromarray((ombres * 255).astype(np.uint8), "L").filter(ImageFilter.MaxFilter(3))
    masque = masque.filter(ImageFilter.GaussianBlur(1.6))
    a = np.asarray(masque, dtype=np.float32) / 255.0 * 0.86
    a = (a * (1 - 0.62 * np.clip(champs["de"] / 0.5 + 0.5, 0, 1)))[..., None]            # plus légère sur l'eau
    fond = fond * (1 - a * (1 - np.array([0.66, 0.76, 0.84], dtype=np.float32)))        # une ombre froide, multipliée
    out = Image.fromarray(np.clip(fond, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    for im, pied, tx, ty, _, _ in sorted(sprites, key=lambda s: (s[5], s[3])):         # triés par leur pied
        ex, ey = ecran(tx, ty)
        coller(out, im, int(round(ex - pied[0])), int(round(ey - pied[1])))
    return out.convert("RGB")


# ====================================================================== avant / après
def capturer_avant(fichier):
    """Capture du jeu actuel au même endroit : le jeu lancé comme un essai de l'éditeur (ESSAI), sans l'interface.
    Chromium sans fenêtre, avec un profil jetable (sinon il s'adresse au Chromium déjà ouvert, et attend)."""
    html = open(os.path.join(RACINE, "web", "index.html"), encoding="utf-8").read()
    k = html.index("<script>") + len("<script>")
    html = html[:k] + "\nconst ESSAI = [4.5, 4.2, 'balade'];\n" + html[k:]
    html += "\n<script>drawHUD = function () {}; drawBanner = function () {}; drawFsButton = function () {};</script>\n"
    page = os.path.join(RACINE, "web", "temoin_avant.html")
    profil = tempfile.mkdtemp(prefix="temoin-")
    try:
        with open(page, "w", encoding="utf-8") as f:
            f.write(html)
        subprocess.run(["chromium-browser", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", f"--window-size={LARG},{HAUT}", f"--user-data-dir={profil}",
                        "--timeout=6000", f"--screenshot={fichier}", "file://" + page],
                       check=True, capture_output=True, timeout=60)
    finally:
        if os.path.exists(page):
            os.remove(page)
        shutil.rmtree(profil, ignore_errors=True)


def avant_apres(avant, apres, fichier):
    w, h, m, bandeau = 1280, 720, 16, 56
    out = Image.new("RGB", (2 * w + 3 * m, h + bandeau + m), (58, 30, 18))
    d = ImageDraw.Draw(out)
    police = ImageFont.truetype(os.path.join(RACINE, "fonts", "Fredoka.ttf"), 32)
    for i, (im, titre) in enumerate(((avant, "Aujourd'hui"), (apres, "Écran témoin de la v2"))):
        x = m + i * (w + m)
        out.paste(im.convert("RGB").resize((w, h), Image.LANCZOS), (x, bandeau))
        d.text((x + w / 2, bandeau / 2), titre, font=police, fill=(246, 235, 210), anchor="mm")
    out.save(fichier)


if __name__ == "__main__":
    os.makedirs(SORTIE, exist_ok=True)
    f_avant, f_apres = os.path.join(SORTIE, "avant_niche.png"), os.path.join(SORTIE, "temoin_niche.png")
    if "--avant" in sys.argv:
        capturer_avant(f_avant)
        print(f_avant)
    image = temoin()
    image.save(f_apres)
    print(f_apres, image.size)
    if os.path.exists(f_avant):
        avant_apres(Image.open(f_avant), image, os.path.join(SORTIE, "avant_apres.png"))
        print(os.path.join(SORTIE, "avant_apres.png"))
