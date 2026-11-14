"""Planche de propositions pour l'écran titre (14 novembre 2026) : python3 v2/titre_options.py fond_printemps.png fond_ete.png

Les deux fonds sont des captures du jeu (v2/capture.py) : la niche au printemps, la plage en été. Trois pistes,
chacune au printemps et en été -> reference/v2/titre_options.png. Ce sont des maquettes : rien n'est dans le jeu."""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import alice2
import hud
import nature
import batiments   # noqa : inscrit ses sprites au catalogue
import mobilier    # noqa
import tecky2
from spritelib import render_svg, PAD
from ete_options import police, REF

W, H = 1920, 1080
BRUN = (58, 30, 18, 255)


def tecky(k, view="down", **kw):
    w, h, ox, oy = tecky2.CADRE[view]
    return render_svg(tecky2.image(view, tecky2.pose(**kw)), w, h, k, PAD), ((ox + PAD) * k, (oy + PAD) * k)


def alice(k, ete=False, **kw):
    w, h, ox, oy = alice2.CADRE
    sv = alice2._vetue("ete" if ete else None, lambda: alice2.image("down", alice2.pose(**kw)))
    return render_svg(sv, w, h, k, PAD), ((ox + PAD) * k, (oy + PAD) * k)


def decor(nom, k):
    sp, w, h, ox, oy = nature.cadre(nom)
    return nature.image(nom, k), ((ox + PAD) * k, (oy + PAD) * k)


def pose(im, img_org, x, y, miroir=False):
    s, (ox, oy) = img_org
    if miroir:
        s, ox = s.transpose(Image.FLIP_LEFT_RIGHT), s.width - ox
    im.alpha_composite(s, (int(x - ox), int(y - oy)))


def degrade(haut, bas, w=W, h=H):
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / (h - 1)
        d.line((0, y, w, y), fill=tuple(int(a + (b - a) * t) for a, b in zip(haut, bas)) + (255,))
    return im


def nuage(d, x, y, s, c=(255, 255, 255, 235)):
    for dx, dy, r in ((0, 0, 60), (70, -22, 76), (150, -6, 64), (214, 10, 46), (-52, 14, 40)):
        d.ellipse((x + (dx - r) * s, y + (dy - r * 0.62) * s, x + (dx + r) * s, y + (dy + r * 0.62) * s), fill=c)
    d.rounded_rectangle((x - 88 * s, y + 4 * s, x + 258 * s, y + 42 * s), 20 * s, fill=c)


def colline(d, x, y, rx, ry, c):
    d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=c)


def heros(im, x, y, k, ete):
    """Alice et Tecky au premier plan, une ombre sous eux."""
    o = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(o)
    d.ellipse((x - 25 * k, y - 3 * k, x + 1 * k, y + 3 * k), fill=(0, 0, 0, 50))
    d.ellipse((x + 8 * k, y - 2.6 * k, x + 32 * k, y + 2.6 * k), fill=(0, 0, 0, 50))
    im.alpha_composite(o)
    pose(im, alice(k, ete, bras=0.0, rire=True), x - 12 * k, y)
    pose(im, tecky(k * 1.0, "down", attitude="assis", expr="joyeux", queue=18), x + 20 * k, y + 1 * k)


def illustration(ete):
    """Piste B : un paysage dessiné pour la saison."""
    if not ete:
        im = degrade((142, 205, 245), (232, 246, 250))
        d = ImageDraw.Draw(im, "RGBA")
        d.ellipse((1460, 90, 1640, 270), fill=(255, 244, 190, 255))
        nuage(d, 240, 190, 1.2); nuage(d, 1040, 130, 0.9); nuage(d, 1560, 330, 0.7)
        colline(d, 420, 900, 900, 330, (140, 205, 132, 255))
        colline(d, 1500, 940, 1000, 330, (124, 196, 116, 255))
        for nom, k, x, y in (("maison_rouge", 3.2, 1180, 668), ("maison_bleue", 3.2, 1420, 690), ("boulangerie", 3.2, 1660, 720),
                             ("chene", 3.4, 990, 690), ("bouleau", 3.2, 1820, 760), ("sapin", 3.2, 180, 650), ("chene_sombre", 3.4, 330, 640)):
            pose(im, decor(nom, k), x, y)
        d.rectangle((0, 760, W, H), fill=(126, 196, 108, 255))
        d.ellipse((-300, 700, 2220, 900), fill=(126, 196, 108, 255))
        d.polygon([(700, H), (1010, 800), (1130, 800), (1160, H)], fill=(222, 184, 128, 255))            # le chemin
        pose(im, decor("cerisier", 8), 250, 930)
        pose(im, decor("niche_gamelle", 7), 1500, 900)
        pose(im, decor("buisson_fleuri", 6), 1790, 980)
        pose(im, decor("pot_de_fleurs", 6), 1250, 990)
        for i in range(46):                                                                             # des fleurs dans l'herbe
            x, y = (i * 397) % W, 820 + (i * 211) % 250
            c = ((255, 255, 255), (251, 216, 74), (249, 168, 196), (169, 200, 242))[i % 4]
            for a in range(5):
                d.ellipse((x + math.cos(a * 1.257) * 9 - 7, y + math.sin(a * 1.257) * 9 - 7, x + math.cos(a * 1.257) * 9 + 7, y + math.sin(a * 1.257) * 9 + 7), fill=c + (255,))
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(246, 201, 69, 255))
    else:
        im = degrade((70, 170, 238), (196, 236, 250), h=560).resize((W, H))
        im.paste(degrade((70, 170, 238), (200, 238, 250), h=560), (0, 0))
        d = ImageDraw.Draw(im, "RGBA")
        d.ellipse((1380, 60, 1620, 300), fill=(255, 236, 150, 255))
        d.ellipse((1340, 20, 1660, 340), fill=(255, 240, 170, 70))
        nuage(d, 200, 170, 1.1); nuage(d, 900, 110, 0.8)
        d.rectangle((0, 520, W, 800), fill=(64, 192, 200, 255))                                         # la mer
        d.rectangle((0, 520, W, 580), fill=(48, 168, 190, 255))
        for i in range(60):
            x, y = (i * 331) % W, 560 + (i * 97) % 200
            d.arc((x, y, x + 70, y + 20), 200, 340, fill=(255, 255, 255, 190), width=4)
        d.polygon([(1500, 520), (1560, 420), (1920, 400), (1920, 640), (1700, 640)], fill=(226, 226, 214, 255))   # la falaise
        d.polygon([(1560, 420), (1920, 400), (1920, 440), (1580, 452)], fill=(190, 196, 120, 255))
        pose(im, decor("phare", 4.2), 1770, 436)
        pose(im, decor("bateau_de_peche", 3.4), 520, 610)
        pose(im, decor("bateau_de_peche_rouge", 2.6), 1180, 566)
        d.rectangle((0, 780, W, H), fill=(240, 214, 150, 255))                                          # le sable
        for i in range(24):                                                                             # l'écume
            x = i * 84
            d.ellipse((x - 20, 758, x + 110, 806), fill=(255, 255, 255, 255))
        d.rectangle((0, 792, W, 812), fill=(250, 236, 196, 255))
        for nom, x in (("cabine_bleue", 150), ("cabine_rouge", 330), ("cabine_jaune", 510)):
            pose(im, decor(nom, 6), x, 930)
        pose(im, decor("chateau_de_sable_fini", 7), 1560, 1010)
        pose(im, decor("chaise_haute", 6), 1810, 960)
        for x, y in ((420, 250), (700, 330), (1100, 240)):                                              # des mouettes
            d.arc((x - 40, y, x, y + 30), 190, 350, fill=BRUN, width=6)
            d.arc((x, y, x + 40, y + 30), 190, 350, fill=BRUN, width=6)
    return im


def monde(fond, flou=0.0, voile=0.0):
    im = Image.open(fond).convert("RGBA").resize((W, H))
    if flou:
        im = im.filter(ImageFilter.GaussianBlur(flou))
    if voile:
        im = Image.alpha_composite(im, Image.new("RGBA", (W, H), (27, 18, 12, int(255 * voile))))
    return im


def vignette(im, force=150):
    v = Image.new("L", (W // 8, H // 8), 0)
    d = ImageDraw.Draw(v)
    for i in range(60):
        t = i / 59
        d.ellipse((W / 16 - (1 - t) * W / 10 - 30, H / 16 - (1 - t) * H / 10 - 16, W / 16 + (1 - t) * W / 10 + 30, H / 16 + (1 - t) * H / 10 + 16), fill=int(255 * t))
    v = Image.eval(v.resize((W, H), Image.BILINEAR), lambda a: (255 - a) * force // 255)
    noir = Image.new("RGBA", (W, H), (27, 18, 12, 255))
    noir.putalpha(v)
    return Image.alpha_composite(im, noir)


def interface(im, ete, cx, y0, logo_x=None, logo_y=None, lg=560, fond_menu=False):
    """Le logo, le choix de l'épisode, le menu (maquette : des cartouches arrondis)."""
    d = ImageDraw.Draw(im, "RGBA")
    logo = hud.logo(8)
    logo = logo.resize((int(logo.width * 0.36), int(logo.height * 0.36)), Image.LANCZOS)
    lx, ly = (cx if logo_x is None else logo_x), (y0 - 370 if logo_y is None else logo_y)
    if fond_menu:
        o = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(o).rounded_rectangle((cx - lg / 2 - 40, y0 - 96, cx + lg / 2 + 40, y0 + 4 * 104 + 14), 36, fill=(27, 18, 12, 110))
        im.alpha_composite(o)
    im.alpha_composite(logo, (int(lx - logo.width / 2), int(ly)))
    nom = "‹  L'été · Tecky à la mer  ›" if ete else "◀  Le printemps · Tecky cherche Alice  ▶"
    f = police(38)
    tw = d.textlength(nom, font=f)
    d.text((cx - tw / 2, y0 - 66), nom, font=f, fill=(242, 193, 78, 255), stroke_width=5, stroke_fill=BRUN)
    for i, (t, s) in enumerate((("Nouvelle aventure", "Gare aux chiens du coin !"), ("Nouvelle balade", "Les chiens veulent seulement jouer"),
                                ("Options", "Son, difficulté, texte, météo…"), ("Badges", "0 sur 22 gagnés"))):
        y = y0 + i * 104
        sel = i == 0
        d.rounded_rectangle((cx - lg / 2, y, cx + lg / 2, y + 88), 22, fill=(255, 247, 230, 255) if sel else (58, 40, 30, 225), outline=BRUN, width=5)
        f1, f2 = police(34), police(22)
        d.text((cx - d.textlength(t, font=f1) / 2, y + 6), t, font=f1, fill=BRUN if sel else (255, 247, 230, 255))
        d.text((cx - d.textlength(s, font=f2) / 2, y + 50), s, font=f2, fill=(107, 90, 78, 255) if sel else (233, 220, 200, 255))


def piste_a(fond, ete):
    """A : le monde vivant, cadré sur un lieu de la saison, sous une vignette au lieu d'un voile uni."""
    im = vignette(monde(fond), 175)
    interface(im, ete, W / 2, 600, fond_menu=True)
    return im


def piste_b(fond, ete):
    """B : un paysage dessiné, Alice et Tecky au premier plan, le menu à droite."""
    im = illustration(ete)
    heros(im, 700, 1010, 9, ete)
    interface(im, ete, 1440, 600, lg=520, fond_menu=True)
    return im


def piste_c(fond, ete):
    """C : le monde vivant, adouci, Alice et Tecky dessinés en grand devant, le menu à droite."""
    im = vignette(monde(fond, flou=5, voile=0.12), 120)
    heros(im, 560, 1010, 11, ete)
    interface(im, ete, 1400, 600, lg=540, fond_menu=True)
    return im


def planche(fond_pr, fond_et):
    marge, tw, th = 20, 940, 529
    out = Image.new("RGBA", (2 * tw + 3 * marge, 70 + 3 * (th + 64) + marge), BRUN)
    d = ImageDraw.Draw(out)
    d.text((24, 14), "Écran titre : trois pistes, au printemps (à gauche) et en été (à droite) — maquettes", font=police(36), fill="#FFFFFF")
    noms = ("A — le monde vivant, cadré sur un lieu de la saison (la niche, la plage), vignette douce",
            "B — un paysage dessiné pour chaque saison, Alice et Tecky au premier plan",
            "C — le monde vivant adouci, Alice et Tecky en grand devant, menu à droite")
    for j, f in enumerate((piste_a, piste_b, piste_c)):
        y = 70 + j * (th + 64)
        d.text((marge, y + 8), noms[j], font=police(30), fill=(242, 193, 78, 255))
        for i, (fond, ete) in enumerate(((fond_pr, False), (fond_et, True))):
            im = f(fond, ete)
            out.paste(im.resize((tw, th), Image.LANCZOS).convert("RGB"), (marge + i * (tw + marge), y + 56))
    fn = os.path.join(REF, "titre_options.png")
    out.convert("RGB").save(fn)
    print(fn, out.size)


if __name__ == "__main__":
    planche(sys.argv[1], sys.argv[2])
