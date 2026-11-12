"""
Ombres décollées : pour chaque décor qui a une ombre portée, couche sa silhouette comme le jeu (game.js :
groundShadows(), à partir de la ligne de contact de MAP.sols) et mesure le jour qui reste entre le pied de l'objet
et son ombre, dans les colonnes où l'objet touche presque le sol. Christophe a vu « pas mal d'ombres qui ont un
espace avant leur objet » : cet outil les liste.

    python3 tools/ombres_decollees.py [seuil en pixels du jeu, 3 par défaut]
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import decor      # noqa: E402
import nature     # noqa: E402
import batiments  # noqa: E402,F401
import mobilier   # noqa: E402,F401
from spritelib import render_svg, PAD  # noqa: E402

S = 2
SX, SY = nature.OMBRE


def jour(alpha, ox, oy, sol):
    """(jour maximal, nombre de colonnes décollées) : alpha = silhouette, (ox, oy) = origine en pixels de l'image,
    sol = points [u, b] de la ligne de contact à partir de l'origine."""
    H, W = alpha.shape
    ombre = np.zeros((H + int(H * SY) + 4, W + int(H * SX) + 4), dtype=bool)
    base = np.full(W, np.nan)
    for (ua, ba), (ub, bb) in zip(sol, sol[1:]):
        for c in range(max(0, int(np.floor(ua + ox))), min(W, int(np.ceil(ub + ox)))):
            t = 0 if ub == ua else (c - ox - ua) / (ub - ua)
            base[c] = oy + ba + (bb - ba) * min(1, max(0, t))
    for c in range(W):
        if np.isnan(base[c]):
            continue
        for y in np.where(alpha[:, c])[0]:
            h = base[c] - y
            if h > 0:
                ombre[min(ombre.shape[0] - 1, int(round(base[c] + SY * h))), min(ombre.shape[1] - 1, int(round(c + SX * h)))] = True
    pire, n = 0, 0
    for c in range(W):
        rangs = np.where(alpha[:, c])[0]
        if not len(rangs) or np.isnan(base[c]):
            continue
        bas = int(rangs[-1])
        if base[c] - bas > 3 or base[c] - bas < 0:         # (cette colonne ne touche pas le sol, ou passe dessous)
            continue
        sous = np.where(ombre[bas + 1:, c])[0]
        if len(sous) and sous[0] >= 1:
            pire, n = max(pire, int(sous[0])), n + (sous[0] >= 2)
    return pire, n


def images():
    for n in sorted({v for noms, _ in nature.VARIANTES.values() for v in noms}):
        sp, w, h, ox, oy = nature.cadre(n)
        if sp.sol:
            yield n, nature.image(n, S), ox, oy, nature.bandes(n, S)
    for n in decor.DECOR:
        if n in nature.VARIANTES or not decor.sol(n):
            continue
        w, h, ox, oy = decor.cadre(n)
        im = render_svg(decor.svgs(n)[0], w, h, S, PAD)
        yield n, im, ox, oy, nature.bandes_image(im, ox, oy, decor.sol(n), S)


if __name__ == "__main__":
    seuil = float(sys.argv[1]) if len(sys.argv) > 1 else 3
    pb = []
    for n, im, ox, oy, sol in images():
        a = np.asarray(im.getchannel("A")) > 128
        pire, cols = jour(a, (ox + PAD) * S, (oy + PAD) * S, sol)
        if pire >= seuil:
            pb.append((pire, cols, n))
    for pire, cols, n in sorted(pb, reverse=True):
        print(f"{n:24s} jour de {pire} px sur {cols} colonnes")
    print(len(pb), "ombres décollées (seuil", seuil, "px)")
