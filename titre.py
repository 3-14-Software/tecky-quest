"""
L'écran titre : un paysage dessiné par saison, Alice et Tecky au premier plan (choix de Christophe sur
reference/v2/titre_options.png, 14 novembre 2026 : piste B, « un paysage dessiné pour chaque saison »).

Tout est à la taille de l'interface du jeu (1920 x 1080 : un pixel de l'image = un pixel de l'écran en 1080p).

- fond(saison) : le paysage, immobile (ciel, soleil, lointains, décors, sol) — le printemps : la prairie, le
  village sur sa colline, le cerisier en fleurs, la niche ; l'été : la mer, la falaise et son phare, les bateaux,
  la plage, ses cabines, un transat. Composé avec les dessins du jeu (nature.CATALOGUE), agrandis.
- sprites() : ce que le jeu anime par-dessus (game.js : drawTitleArt()) — les nuages, Alice dans la tenue de la
  saison et Tecky assis (leurs animations du jeu, en grand), un papillon, une mouette.
  { nom: (images RGBA, origine x, origine y, images par seconde) }
- pack_web.build_titre() en fait des fichiers à côté de la page : titre_<saison>.png, titre_sprites.png.

    python3 titre.py      # reference/v2/titre_printemps.png, titre_ete.png (le fond, les héros et les nuages posés)
"""
import math
import os

from PIL import Image, ImageDraw

import alice2
import batiments   # noqa : inscrit ses dessins dans nature.CATALOGUE
import butterflies
import mobilier    # noqa
import mouettes
import nature
import tecky2
from spritelib import render_svg, PAD

W, H = 1920, 1080
SAISONS = ("printemps", "ete")
K = 9.0                              # pixels par unité des héros (dans le jeu, en 1080p : 2)
SOL = 1004                           # la ligne des pieds d'Alice et de Tecky
ALICE, TECKY = (560, SOL), (800, SOL + 10)      # où le jeu les pose (game.js : ART)
SS = 2                               # suréchantillonnage des formes dessinées avec PIL (bords lissés)
BRUN = (58, 30, 18)


# ---------------------------------------------------------------------- outils
def _toile(couleur=(0, 0, 0, 0)):
    im = Image.new("RGBA", (W * SS, H * SS), couleur)
    return im, ImageDraw.Draw(im)


def _pose_toile(fond, toile):
    fond.alpha_composite(toile.resize((W, H), Image.LANCZOS))


def _s(*v):
    return tuple(x * SS for x in v)


def _degrade(haut, bas, y0, y1):
    """Une bande de ciel, de y0 à y1, en dégradé vertical."""
    im = Image.new("RGBA", (W, y1 - y0))
    d = ImageDraw.Draw(im)
    for y in range(y1 - y0):
        t = y / max(1, y1 - y0 - 1)
        d.line((0, y, W, y), fill=tuple(round(a + (b - a) * t) for a, b in zip(haut, bas)) + (255,))
    return im


def _decor(nom, k):
    sp, w, h, ox, oy = nature.cadre(nom)
    return nature.image(nom, k), ((ox + PAD) * k, (oy + PAD) * k)


def _pose(im, img_org, x, y, miroir=False):
    s, (ox, oy) = img_org
    if miroir:
        s, ox = s.transpose(Image.FLIP_LEFT_RIGHT), s.width - ox
    im.alpha_composite(s, (round(x - ox), round(y - oy)))


def _ombre(im, x, y, rx, ry, a=46):
    o, d = _toile()
    d.ellipse(_s(x - rx, y - ry, x + rx, y + ry), fill=(22, 50, 60, a))
    _pose_toile(im, o)


def _fleur(d, x, y, r, petales, coeur):
    for a in range(5):
        cx, cy = x + math.cos(a * 1.257 - 0.5) * r, y + math.sin(a * 1.257 - 0.5) * r
        d.ellipse(_s(cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78), fill=petales)
    d.ellipse(_s(x - r * 0.6, y - r * 0.6, x + r * 0.6, y + r * 0.6), fill=coeur)


def _touffe(d, x, y, h, c):
    for dx, k in ((-9, 0.7), (0, 1.0), (9, 0.75)):
        d.line(_s(x + dx, y, x + dx * 1.5, y - h * k), fill=c, width=5 * SS)


def _hasard(i, n):
    """Un tirage stable (les fleurs ne changent pas de place d'une construction à l'autre)."""
    x = math.sin(i * 127.1 + n * 311.7) * 43758.5453
    return x - math.floor(x)


# ---------------------------------------------------------------------- le printemps
def _printemps():
    im = _degrade((120, 196, 244), (226, 244, 250), 0, H)
    t, d = _toile()
    d.ellipse(_s(214, 60, 466, 312), fill=(255, 250, 214, 90))                        # le soleil : sa couronne, puis le disque
    d.ellipse(_s(250, 96, 430, 276), fill=(255, 244, 178, 255))
    # les lointains : trois rangs de collines
    d.ellipse(_s(-500, 470, 900, 1200), fill=(170, 220, 168, 255))
    d.ellipse(_s(520, 520, 2500, 1300), fill=(156, 213, 152, 255))
    d.ellipse(_s(-300, 610, 1500, 1500), fill=(139, 204, 130, 255))
    _pose_toile(im, t)
    for nom, k, x, y in (("sapin_haut", 2.6, 90, 628), ("sapin", 2.6, 170, 640), ("chene", 2.6, 1010, 668),
                         ("maison_haute", 2.5, 1160, 640), ("maison_rouge", 2.5, 1330, 660), ("maison_colombages", 2.5, 1500, 650),
                         ("boulangerie", 2.5, 1690, 672), ("bouleau", 2.6, 1850, 690), ("chene_sombre", 2.6, 880, 664)):
        _pose(im, _decor(nom, k), x, y)
    t, d = _toile()
    d.ellipse(_s(-400, 640, 2400, 1500), fill=(124, 195, 107, 255))                   # le pré du premier plan
    # le chemin de la niche, qui descend vers nous en s'élargissant
    d.polygon(_s(980, 700, 1060, 700, 1100, 800, 1050, 900, 1130, H, 730, H, 900, 900, 990, 800), fill=(217, 180, 122, 255))
    d.line(_s(980, 700, 990, 800, 900, 900, 730, H), fill=(194, 154, 98, 255), width=5 * SS)
    d.line(_s(1060, 700, 1100, 800, 1050, 900, 1130, H), fill=(194, 154, 98, 255), width=5 * SS)
    for i in range(22):                                                               # des plages d'herbe plus claire, plus sombre
        x, y, r = _hasard(i, 1) * W, 760 + _hasard(i, 2) * 320, 70 + _hasard(i, 3) * 90
        d.ellipse(_s(x - r, y - r * 0.28, x + r, y + r * 0.28), fill=((134, 204, 116, 255), (114, 186, 100, 255))[i % 2])
    for i in range(70):
        x, y = _hasard(i, 4) * W, 730 + _hasard(i, 5) * 340
        if 700 < x < 1150:
            continue
        _touffe(d, x, y, 16 + 14 * (y - 730) / 340, (95, 168, 82, 255))
    for i in range(64):                                                               # les fleurs du printemps
        x, y = _hasard(i, 6) * W, 740 + _hasard(i, 7) * 330
        if 690 < x < 1160:
            continue
        r = 5 + 6 * (y - 740) / 330
        pet, cœur = (((255, 255, 255, 255), (246, 201, 69, 255)), ((251, 216, 74, 255), (232, 147, 46, 255)),
                     ((249, 168, 196, 255), (255, 241, 184, 255)), ((169, 200, 242, 255), (255, 241, 184, 255)))[i % 4]
        _fleur(d, x, y, r, pet, cœur)
    _pose_toile(im, t)
    _ombre(im, 250, 930, 190, 30)
    _pose(im, _decor("cerisier", 8.5), 230, 934)
    _ombre(im, 1190, 880, 120, 22)
    _pose(im, _decor("niche_gamelle", 6.5), 1150, 884)
    _pose(im, _decor("buisson_fleuri", 6), 1820, 1010)
    _pose(im, _decor("pot_de_fleurs", 5.5), 1010, 1040)
    _pose(im, _decor("buisson_baies", 5.5), 40, 1050)
    return im


# ---------------------------------------------------------------------- l'été
HORIZON, RIVAGE = 540, 800           # où la mer rencontre le ciel, où elle rencontre le sable


def _ete():
    im = _degrade((58, 160, 236), (190, 232, 250), 0, H)
    t, d = _toile()
    d.ellipse(_s(776, 26, 1084, 334), fill=(255, 244, 190, 100))                      # le soleil : sa couronne, puis le disque
    d.ellipse(_s(820, 70, 1040, 290), fill=(255, 236, 140, 255))
    d.rectangle(_s(0, HORIZON, W, RIVAGE + 30), fill=(58, 190, 196, 255))             # la mer : le large, puis les hauts-fonds
    d.rectangle(_s(0, HORIZON, W, HORIZON + 70), fill=(44, 164, 186, 255))
    d.rectangle(_s(0, RIVAGE - 90, W, RIVAGE + 30), fill=(110, 214, 208, 255))
    for i in range(46):                                                               # le soleil sur l'eau
        x, y = _hasard(i, 8) * W, HORIZON + 26 + _hasard(i, 9) * 200
        l = 30 + 50 * (y - HORIZON) / 230
        d.line(_s(x, y, x + l, y), fill=(255, 255, 255, 120), width=3 * SS)
    # la falaise, à gauche : la roche claire, la lande dessus
    d.polygon(_s(0, 380, 330, 366, 430, 392, 520, 470, 560, HORIZON + 90, 0, HORIZON + 130), fill=(232, 228, 214, 255))
    d.polygon(_s(330, 366, 430, 392, 520, 470, 560, HORIZON + 90, 470, HORIZON + 100, 440, 480, 360, 420), fill=(204, 198, 180, 255))
    d.polygon(_s(0, 352, 330, 340, 436, 388, 330, 398, 0, 404), fill=(178, 196, 106, 255))
    d.line(_s(0, 404, 330, 398, 436, 388), fill=(150, 168, 86, 255), width=4 * SS)
    for x, y, l in ((60, 450, 70), (190, 520, 90), (300, 470, 60), (120, 590, 80), (380, 560, 50)):   # des fissures
        d.line(_s(x, y, x + l * 0.4, y + 26, x + l, y + 34), fill=(190, 184, 166, 255), width=3 * SS)
    _pose_toile(im, t)
    _pose(im, _decor("phare", 2.3), 190, 372)
    _pose(im, _decor("bateau_de_peche", 3.2), 700, 640)
    _pose(im, _decor("bateau_de_peche_rouge", 2.2), 1130, 588)
    t, d = _toile()
    d.rectangle(_s(0, RIVAGE, W, H), fill=(240, 214, 150, 255))                       # le sable, mouillé au bord
    d.rectangle(_s(0, RIVAGE, W, RIVAGE + 40), fill=(226, 196, 132, 255))
    for i in range(30):                                                               # l'écume, en festons
        x = i * 70 - 20
        d.ellipse(_s(x, RIVAGE - 22, x + 100, RIVAGE + 22), fill=(255, 255, 255, 255))
    for i in range(18):                                                               # des plages de sable plus clair
        x, y, r = _hasard(i, 10) * W, 870 + _hasard(i, 11) * 200, 80 + _hasard(i, 12) * 90
        d.ellipse(_s(x - r, y - r * 0.22, x + r, y + r * 0.22), fill=(247, 226, 170, 255))
    for i in range(40):                                                               # galets, coquillages
        x, y = _hasard(i, 13) * W, 860 + _hasard(i, 14) * 210
        r = 4 + 5 * _hasard(i, 15)
        d.ellipse(_s(x - r, y - r * 0.6, x + r, y + r * 0.6), fill=((214, 186, 126, 255), (255, 244, 226, 255), (232, 160, 140, 255))[i % 3])
    _pose_toile(im, t)
    for nom, x, y in (("cabine_bleue", 1010, 906), ("cabine_rouge", 1150, 912), ("cabine_jaune", 1290, 904), ("cabine_verte", 1430, 910)):
        _ombre(im, x + 60, y - 4, 76, 14)
        _pose(im, _decor(nom, 5), x, y)
    _ombre(im, 250, 990, 150, 22)
    _pose(im, _decor("transat", 6.5), 230, 996)
    _ombre(im, 1090, 1040, 120, 16)
    _pose(im, _decor("chateau_de_sable_fini", 5.5), 1070, 1046)
    _pose(im, _decor("chaise_haute", 5.5), 1800, 1000)
    return im


def fond(saison):
    return (_ete if saison == "ete" else _printemps)().convert("RGB")


# ---------------------------------------------------------------------- ce qui bouge
def _nuage(l, h, bosses):
    """Un nuage blanc, le dessous à peine gris."""
    im = Image.new("RGBA", (l * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for c, dy in (((226, 236, 246, 255), 8), ((255, 255, 255, 255), 0)):
        d.rounded_rectangle((0, (h * 0.52 + dy * 0.5) * SS, l * SS, (h - 8 + dy) * SS), h * 0.24 * SS, fill=c)
        for x, y, r in bosses:
            d.ellipse(((x - r) * SS, (y - r * 0.8 + dy * 0.3) * SS, (x + r) * SS, (y + r * 0.8 + dy * 0.3) * SS), fill=c)
    return im.resize((l, h), Image.LANCZOS)


def _heros(svgs, w, h, ox, oy, k=K):
    return [render_svg(sv, w, h, k, PAD) for sv in svgs], (ox + PAD) * k, (oy + PAD) * k


def sprites():
    """{ nom: (images, origine x, origine y, images par seconde) } : ce que le jeu anime sur le paysage."""
    out = {
        "nuage": ([_nuage(420, 150, ((110, 82, 62), (200, 60, 78), (300, 78, 58))), _nuage(300, 110, ((80, 62, 46), (160, 46, 56), (228, 62, 40))),
                   _nuage(520, 170, ((120, 96, 66), (230, 70, 88), (350, 84, 74), (440, 104, 50)))], 0, 0, 0),
    }
    w, h, ox, oy = alice2.CADRE
    for saison, tenue in (("printemps", None), ("ete", "ete")):
        out["alice_" + saison] = (*_heros(alice2.frames("idle", "down", tenue=tenue), w, h, ox, oy), alice2.ANIMS["idle"][1])
    w, h, ox, oy = tecky2.CADRE["down"]
    out["tecky"] = (*_heros(tecky2.rest_frames("sit", "down"), w, h, ox, oy), tecky2.REST_ANIMS["sit"][1])
    out["papillon"] = ([render_svg(sv, butterflies.W, butterflies.H, 5, PAD) for sv in butterflies.frames(list(butterflies.COLORS)[0])],
                       (12 + PAD) * 5, (12 + PAD) * 5, 12)
    out["mouette"] = ([render_svg(sv, mouettes.W, mouettes.H, 5, PAD) for sv in mouettes.frames("fly")], (16 + PAD) * 5, (16 + PAD) * 5, 12)
    return out


def planche(sp):
    """Les images des sprites rangées en une planche : (image, { nom: { f: [[x, y, w, h]…], ox, oy, fps } })."""
    meta, x, y, rang, cases = {}, 0, 0, 0, []
    for nom, (ims, ox, oy, fps) in sp.items():
        meta[nom] = dict(f=[], ox=round(ox, 1), oy=round(oy, 1), fps=fps)
        for im in ims:
            if x + im.width > 4096:
                x, y, rang = 0, y + rang, 0
            cases.append((im, x, y))
            meta[nom]["f"].append([x, y, im.width, im.height])
            x, rang = x + im.width, max(rang, im.height)
    out = Image.new("RGBA", (max(c[1] + c[0].width for c in cases), y + rang), (0, 0, 0, 0))
    for im, x, y in cases:
        out.paste(im, (x, y))
    return out, meta


if __name__ == "__main__":
    sp = sprites()
    for saison in SAISONS:
        im = fond(saison).convert("RGBA")
        for i, (x, y) in enumerate(((180, 150), (980, 96), (1500, 250))):
            im.alpha_composite(sp["nuage"][0][i], (x, y))
        for nom, (x, y) in (("alice_" + saison, ALICE), ("tecky", TECKY)):
            ims, ox, oy, _ = sp[nom]
            ImageDraw.Draw(im, "RGBA")
            _ombre(im, x, y, (150, 110)[nom == "tecky"], 20)
            im.alpha_composite(ims[0], (round(x - ox), round(y - oy)))
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference", "v2", f"titre_{saison}.png")
        im.convert("RGB").save(fn)
        print(fn)
