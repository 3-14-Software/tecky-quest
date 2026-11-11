"""
Tecky, Alice et les chiens du jeu web (tecky2.py, alice2.py, chiens2.py) :
- mêmes animations et mêmes vues que les dessins d'avant (tecky.py, alice.py) : le moteur les appelle par leur nom ;
- debout, les pieds sont posés sur l'origine du cadre (c'est là que le jeu place le personnage) : comme ceux des
  dessins d'avant, ils la dépassent d'une à deux unités, contour compris ;
- rien ne sort du cadre et de sa marge (sinon l'atlas le couperait).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import alice  # noqa: E402
import alice2  # noqa: E402
import chiens2  # noqa: E402
import enemies  # noqa: E402
import tecky  # noqa: E402
import tecky2  # noqa: E402
from spritelib import render_svg, PAD  # noqa: E402

S = 2
echecs = 0


def ok(vrai, texte):
    global echecs
    print(("ok : " if vrai else "ÉCHEC : ") + texte)
    echecs += 0 if vrai else 1


def alpha(svg, w, h):
    return np.asarray(render_svg(svg, w, h, S, PAD))[:, :, 3]


def pieds(a):
    """Dernière rangée où le dessin est opaque (l'ombre au sol, translucide, ne compte pas), en unités du cadre."""
    lignes = np.where((a > 200).any(axis=1))[0]
    return (lignes[-1] + 1) / S - PAD


def pose_au_sol(bas, oy):
    return 0.5 <= bas - oy <= 2.0


def dans_le_cadre(a):
    return not (a[0].any() or a[-1].any() or a[:, 0].any() or a[:, -1].any())


# --- mêmes noms qu'avant
ok({n: v[2] for n, v in tecky2.ANIMS.items()} == {n: v[2] for n, v in tecky.ANIMS.items()},
   "Tecky : mêmes animations et mêmes vues que tecky.py (" + ", ".join(tecky2.ANIMS) + ")")
ok({n: v[2:] for n, v in tecky2.REST_ANIMS.items()} == {n: v[2:] for n, v in tecky.REST_ANIMS.items()},
   "Tecky : mêmes poses de repos, mêmes vues, mêmes boucles (" + ", ".join(tecky2.REST_ANIMS) + ")")
ok(set(alice2.ANIMS) == set(alice.ANIMS), "Alice : mêmes animations que alice.py (" + ", ".join(alice2.ANIMS) + ")")
ok(len(tecky2.frames("walk", "right")) == 8 and len(alice2.frames("walk", "down")) == 8, "la marche a 8 images")

# --- Tecky : les pieds sur l'origine, rien hors du cadre
images = 0
for nom, (_, _, vues) in tecky2.ANIMS.items():
    for v in vues:
        w, h, ox, oy = tecky2.CADRE[v]
        rendus = [alpha(s, w, h) for s in tecky2.frames(nom, v)]
        images += len(rendus)
        if not all(dans_le_cadre(a) for a in rendus):
            ok(False, f"tecky/{nom}/{v} sort de son cadre")
        if nom == "idle":
            bas = pieds(rendus[0])
            avant = pieds(alpha(tecky.frames("idle", v)[0], 48, 48)) - 44
            ok(pose_au_sol(bas, oy), f"Tecky debout ({v}) : le bas des pattes {bas - oy:.1f} sous l'origine ({avant:.1f} avant)")
for nom, (_, _, vues, _) in tecky2.REST_ANIMS.items():
    for v in vues:
        w, h, ox, oy = tecky2.CADRE[v]
        rendus = [alpha(s, w, h) for s in tecky2.rest_frames(nom, v)]
        images += len(rendus)
        bas = max(pieds(a) for a in rendus)
        if not all(dans_le_cadre(a) for a in rendus) or not pose_au_sol(bas, oy):
            ok(False, f"tecky/{nom}/{v} : hors du cadre, ou pas posé au sol (bas à {bas:.1f}, origine à {oy})")
ok(True, f"Tecky : {images} images, toutes dans leur cadre ; au repos, il est posé au sol")
a = alpha(tecky2.frames("ko", "right")[-1], *tecky2.CADRE["right"][:2])
bas = pieds(a) - tecky2.CADRE["right"][3]
ok(0 <= bas <= 2.5, f"KO : sur le dos, il est posé au sol, ni en l'air ni dessous ({bas:.1f} sous l'origine)")

# --- Alice
w, h, ox, oy = alice2.CADRE
images = 0
for nom in alice2.ANIMS:
    for v in ("down", "up", "right"):
        rendus = [alpha(s, w, h) for s in alice2.frames(nom, v)]
        images += len(rendus)
        if not all(dans_le_cadre(a) for a in rendus):
            ok(False, f"alice/{nom}/{v} sort de son cadre")
        if nom == "idle":
            bas = pieds(rendus[0])
            ok(pose_au_sol(bas, oy), f"Alice debout ({v}) : le bas des pieds {bas - oy:.1f} sous l'origine")
ok(True, f"Alice : {images} images, toutes dans leur cadre")
haut = [pieds(alpha(s, w, h)) for s in alice2.frames("happy", "down")]
ok(min(haut) < oy - 2.5, f"saut de joie : elle décolle ({oy - min(haut):.1f} unités)")

# --- les chiens : mêmes noms, mêmes vues et mêmes durées qu'avant (le jeu attend la fin d'un aboiement, d'une
# morsure), sauf la marche en 8 images ; les pieds sur l'origine, rien hors du cadre, le KO posé au sol
ok(list(chiens2.CHIENS) == list(enemies.DOGS), "chiens : les mêmes qu'avant (" + ", ".join(chiens2.CHIENS) + ")")
avant = {n: (len(v[0]("right")), v[2]) for n, v in tecky.ANIMS.items() if n != "dig"}
apres = {n: (len(v[0]("right")), v[2]) for n, v in chiens2.ANIMS.items()}
avant["walk"] = (8, avant["walk"][1])
ok(apres == avant, "chiens : mêmes animations, mêmes vues, mêmes nombres d'images (la marche en a 8)")
w, h, ox, oy = chiens2.CADRE
for chien in chiens2.CHIENS:
    images, soucis = 0, []
    for nom, (_, _, vues) in chiens2.ANIMS.items():
        for v in vues:
            rendus = [alpha(s, w, h) for s in chiens2.frames(chien, nom, v)]
            images += len(rendus)
            if not all(dans_le_cadre(a) for a in rendus):
                soucis.append(f"{nom}/{v} sort du cadre")
            if nom == "idle" and not pose_au_sol(pieds(rendus[0]), oy):
                soucis.append(f"debout ({v}) : le bas des pattes {pieds(rendus[0]) - oy:.1f} sous l'origine")
    bas = pieds(alpha(chiens2.frames(chien, "ko", "right")[-1], w, h)) - oy
    if not 0 <= bas <= 2.5:
        soucis.append(f"KO : {bas:.1f} sous l'origine")
    ok(not soucis, f"{chien} : {images} images dans leur cadre, les pieds sur l'origine, le KO au sol" + "".join(" ; " + t for t in soucis))

print("héros :", "ÉCHEC" if echecs else "ok")
sys.exit(1 if echecs else 0)
