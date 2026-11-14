"""Planches de propositions pour les reports de l'été (13 novembre 2026) : python3 v2/ete_options.py [planche]."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import alice2
import mobilier
import npcs
from spritelib import render_svg, PAD

K = 8                                    # pixels par unité du jeu
REF = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reference", "v2")
SABLE, HERBE, DALLE = (240, 214, 150, 255), (126, 196, 108, 255), (205, 208, 214, 255)


def police(t):
    for f in ("/usr/share/fonts/open-sans/OpenSans-Semibold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, t)
    return ImageFont.load_default()


def sprite(sp, ech=1.0, k=K):
    """Image d'un nature.Sprite (pas encore au catalogue) et la place de son origine."""
    out = None
    w, h = int(sp.w * ech + 1), int(sp.h * ech + 1)
    for d, contour, ep, *reste in sp.calques:
        d.w, d.h = w, h
        im = render_svg(d.svg(f"scale({ech})", outline=contour, outline_w=ep / ech), w, h, k, PAD)
        out = im if out is None else Image.alpha_composite(out, im)
    return out, ((sp.pied[0] * ech + PAD) * k, (sp.pied[1] * ech + PAD) * k)


def alice(view="down", tenue=None, pal=None, nu=False, k=K):
    garde, alice2.ETE = dict(alice2.PAL), tenue
    alice2.PAL.update(pal or {})
    w, h, ox, oy = alice2.CADRE
    im = render_svg(alice2.image(view, alice2.pose(nu=nu)), w, h, k, PAD)
    alice2.PAL.clear(); alice2.PAL.update(garde); alice2.ETE = None
    return im, ((ox + PAD) * k, (oy + PAD) * k)


def perso(kind, k=K):
    return render_svg(npcs.frames(kind, "idle")[0], npcs.W, npcs.H, k, PAD), ((24 + PAD) * k, (npcs.G + PAD) * k)


class Planche:
    def __init__(self, w, h, titre, fond=SABLE):
        self.im = Image.new("RGBA", (w, h), fond)
        self.dr = ImageDraw.Draw(self.im)
        self.dr.rectangle((0, 0, w, 70), fill=(58, 30, 18, 255))
        self.dr.text((24, 14), titre, font=police(36), fill="#FFFFFF")

    def fond(self, x0, y0, x1, y1, couleur):
        self.dr.rectangle((x0, y0, x1, y1), fill=couleur)

    def pose(self, img_org, x, y):
        im, (ox, oy) = img_org
        self.im.alpha_composite(im, (int(x - ox), int(y - oy)))

    def texte(self, x, y, t, taille=30, couleur="#3A1E12"):
        self.dr.text((x, y), t, font=police(taille), fill=couleur)

    def ecrit(self, nom):
        fn = os.path.join(REF, nom)
        self.im.convert("RGB").save(fn)
        print(fn, self.im.size)


TENUES = [
    ("A — robe turquoise", dict(tong="#F2C230"), dict(shirt="#5CC8C2", shirt_dk="#3FA9A6", skirt="#5CC8C2", skirt_dk="#3FA9A6")),
    ("B — marinière, jupe rouge", dict(tong="#2F6FC0", rayures="#2B4C8C"), dict(shirt="#FFFFFF", shirt_dk="#DDE3EC", skirt="#E0483C", skirt_dk="#B8322A")),
    ("C — jaune et rose", dict(tong="#EE6FA0"), {}),
]


def planche_alice():
    P = Planche(1920, 1080, "Alice en été : sa tenue, ses tongs (celle qu'elle a perdue : un pied nu)")
    for i, (nom, tenue, pal) in enumerate(TENUES):
        x = 60 + i * 400
        P.texte(x, 84, nom, 28)
        for j, (vue, nu) in enumerate((("down", False), ("right", False), ("up", False), ("down", True))):
            P.pose(alice(vue, tenue, pal, nu, 6 if j else 9), x + (90 if j == 0 else 60 + (j - 1) * 120), 480 if j == 0 else 780)
        P.texte(x, 800, "profil, dos, un pied nu", 20)
    P.pose(alice("down"), 1340, 480)
    P.texte(1260, 84, "aujourd'hui (printemps)", 28)
    P.ecrit("ete_options_alice.png")


def svg_img(svg, w, h, k):
    return render_svg(svg, w, h, k, PAD), ((w / 2 + PAD) * k, (h / 2 + PAD) * k)


def vehicule(d, k, w=48, h=40, sol=38.6):
    d.under = []
    return render_svg(d.svg(), w, h, k, PAD), ((w / 2 + PAD) * k, (sol + PAD) * k)


def planche_plage():
    import random
    import nature
    import vehicles
    P = Planche(1920, 1080, "L'été : chaise haute, deux-roues, voitures garées, sable, cultures")
    P.texte(40, 84, "Chaise haute de Théo : D blanche et rouge, E bleue et jaune, F bois", 24)
    for i, (c, o, t) in enumerate((("#FFFFFF", "#C9CDD4", "#D8362E"), ("#3E86D6", "#2A62A6", "#F2C230"), ("#D9A45C", "#B07E3C", "#FFFFFF"))):
        P.pose(sprite(mobilier.chaise_haute(c, o, t), 1.0, 4), 290 + i * 215, 540)
        P.texte(280 + i * 215, 548, "DEF"[i], 30)
    P.pose(perso("theo", 4), 110, 540)
    P.fond(860, 80, 1920, 600, DALLE)
    P.texte(880, 84, "Deux-roues : G scooters, H motos ; en route et garés", 24)
    for i, c in enumerate(("menthe", "corail", "creme")):
        P.pose(vehicule(vehicles.scooter(c), 5), 1000 + i * 300, 330)
        P.pose(vehicule(vehicles.scooter(c, pilote=False), 3), 1130 + i * 300, 330)
    for i, c in enumerate(("noir", "rouge", "bleu")):
        P.pose(vehicule(vehicles.moto(c), 5), 1000 + i * 300, 570)
        P.pose(vehicule(vehicles.moto(c, pilote=False), 3), 1130 + i * 300, 570)
    P.pose(alice("down", k=3), 1860, 570)
    P.fond(0, 600, 1920, 800, DALLE)
    P.texte(40, 606, "Voitures garées sur le parking : I les voitures de la route, sans conducteur (de profil, comme celle du papa)", 24)
    for i, c in enumerate(vehicles.CAR_COLORS):
        P.pose(vehicule(vehicles.car(c, vide=True), 4.5, 64, 40), 220 + i * 330, 790)
    d = vehicles.sport(0, passagers=())
    P.pose(vehicule(d, 4.5, 88, 40), 1600, 790)
    P.texte(40, 806, "J — ce que la mer laisse sur le sable (semé par le jeu)", 24)
    rnd = random.Random(4)
    sable = nature.sol_sable()
    for n in range(46):
        i = rnd.choice([0, 1, 2, 3, 4, 5, 6, 7, 7, 8, 8, 9, 4, 5, 1])
        P.pose(svg_img(sable[i], 12, 12, 5), rnd.randint(40, 900), rnd.randint(860, 1050))
    P.fond(960, 800, 1920, 1080, (196, 148, 92, 255))
    P.texte(980, 806, "K — cultures d'été du champ : blé, tournesols, maïs, tomates", 24, "#FFFFFF")
    cult = nature.sol_cultures_ete()
    for r in range(4):
        P.fond(960, 872 + r * 52, 1920, 880 + r * 52, (170, 124, 74, 255))
        for x in range(16):
            P.pose(svg_img(cult[r * 2 + x % 2], 12, 12, 5), 1010 + x * 58, 866 + r * 52)
    P.ecrit("ete_options_plage.png")


if __name__ == "__main__":
    qui = sys.argv[1] if len(sys.argv) > 1 else "alice"
    globals()["planche_" + qui]()
