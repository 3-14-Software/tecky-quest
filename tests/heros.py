"""
Tecky, Alice et les chiens du jeu web (tecky2.py, alice2.py, chiens2.py) :
- les animations et les vues que le moteur appelle par leur nom (ATTENDU), avec leurs nombres d'images : le jeu
  attend la fin d'un aboiement, d'une morsure ;
- debout, les pieds sont posés sur l'origine du cadre (c'est là que le jeu place le personnage) : ils la dépassent
  d'une à deux unités, contour compris ;
- rien ne sort du cadre et de sa marge (sinon l'atlas le couperait).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import alice2  # noqa: E402
import chiens2  # noqa: E402
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


# --- ce que le moteur attend (game.js les appelle par leur nom ; ne changer qu'avec lui)
TROIS, PROFIL, DEUX = ("down", "up", "right"), ("right",), ("down", "right")
ATTENDU = {
    "tecky": {"idle": TROIS, "walk": TROIS, "bark": TROIS, "bite": TROIS, "hurt": TROIS, "dig": TROIS, "ko": PROFIL},
    # repos : (vues, en boucle)
    "repos": {"sit": (DEUX, True), "yawn": (DEUX, False), "scratch": (PROFIL, True), "sleep": (DEUX, True),
              "shake": (DEUX, False)},
    # nage : les animations de la terre ferme que Tecky joue aussi dans l'eau, leurs vues
    "nage": {"idle": TROIS, "walk": TROIS, "bark": TROIS, "bite": TROIS, "hurt": TROIS, "ko": PROFIL},
    "alice": {"idle", "walk", "happy"},
    "chiens": ["roquet", "bouledogue", "molosse", "berger"],
    # chiens : (nombre d'images, vues)
    "chien": {"idle": (4, TROIS), "walk": (8, TROIS), "bark": (4, TROIS), "bite": (5, TROIS), "hurt": (2, TROIS),
              "ko": (4, PROFIL)},
}
ok({n: v[2] for n, v in tecky2.ANIMS.items()} == ATTENDU["tecky"],
   "Tecky : les animations et les vues que le moteur appelle (" + ", ".join(tecky2.ANIMS) + ")")
ok({n: tuple(v[2:]) for n, v in tecky2.REST_ANIMS.items()} == ATTENDU["repos"],
   "Tecky : les poses de repos, leurs vues, leurs boucles (" + ", ".join(tecky2.REST_ANIMS) + ")")
ok({n: v[1] for n, v in tecky2.NAGE.items()} == ATTENDU["nage"]
   and all(len(tecky2.nage_frames(n, v)) == len(tecky2.frames(n, v)) for n, w in tecky2.NAGE.items() for v in w[1]),
   "Tecky qui nage : les mêmes animations, les mêmes nombres d'images que sur la terre ferme (" + ", ".join(tecky2.NAGE) + ")")
for nom, (_, vues, _) in tecky2.NAGE.items():
    for v in vues:
        w, h, ox, oy = tecky2.CADRE[v]
        for s in tecky2.nage_frames(nom, v):
            a = alpha(s, w, h)
            if not dans_le_cadre(a) or pieds(a) > oy - tecky2.LIGNE + 4:
                ok(False, f"nage/{nom}/{v} : hors du cadre, ou quelque chose dépasse sous la ligne d'eau")
ok(True, "Tecky qui nage : rien sous la ligne d'eau, rien hors du cadre")
ok(set(alice2.ANIMS) == ATTENDU["alice"], "Alice : les animations que le moteur appelle (" + ", ".join(alice2.ANIMS) + ")")
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
            ok(pose_au_sol(bas, oy), f"Tecky debout ({v}) : le bas des pattes {bas - oy:.1f} sous l'origine")
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
nus = [alpha(s, w, h) for nom in alice2.ANIMS for v in ("down", "up", "right") for s in alice2.frames(nom, v, True)]
ok(len(nus) == images and all(dans_le_cadre(a) for a in nus), f"Alice à un pied nu (alice1) : {len(nus)} images, dans leur cadre")
diff = sum(int((alpha(a, w, h) != alpha(b, w, h)).any())
           for v in ("down", "up", "right") for a, b in zip(alice2.frames("idle", v), alice2.frames("idle", v, True)))
ok(diff == 12, "son pied nu se voit dans les trois vues")
haut = [pieds(alpha(s, w, h)) for s in alice2.frames("happy", "down")]
ok(min(haut) < oy - 2.5, f"saut de joie : elle décolle ({oy - min(haut):.1f} unités)")

# --- les chiens : les noms, les vues et les durées que le jeu attend (la fin d'un aboiement, d'une morsure) ; les
# pieds sur l'origine, rien hors du cadre, le KO posé au sol
ok(list(chiens2.CHIENS) == ATTENDU["chiens"], "chiens : ceux de carte.json et de game.js (" + ", ".join(chiens2.CHIENS) + ")")
apres = {n: (len(v[0]("right")), v[2]) for n, v in chiens2.ANIMS.items()}
ok(apres == ATTENDU["chien"], "chiens : les animations, les vues et les nombres d'images attendus (la marche en a 8)")
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
