"""
Les bébés hérissons de Maman Piquette (quête de la forêt) : de profil, tournés vers la droite (la vue gauche est le
miroir, faite par le jeu). Cellule 32 x 32, pieds à y = 28 : origine conseillée (16, 28), comme critters.py.

Ils sont dessinés grands, à la mesure de la cellule (c'est ce dessin-là que prend l'icône de leur badge, hud.py :
draw_baby()), puis réduits de SCALE autour de l'origine par frames(), comme les bêtes de critters.py : le contour
garde l'épaisseur de celui des autres sprites. Leur taille se juge à côté de Tecky (34 x 22 unités depuis la v2) et
d'un chat (21 x 19) : un petit hérisson fait 13 x 9, il tient sous le museau de Tecky. À l'échelle 1, il était
presque aussi long que lui.

Le dessin suit celui de Tecky et des chiens v2 : formes rondes, grosse tête, grand œil sombre à reflet, truffe ronde
au bout d'un petit museau pointu, piquants en grosses dents régulières, ventre et visage clairs. Pas de rond cerné
posé sur le corps : l'oreille et les pattes font partie de la silhouette.

Animations (ANIMS[nom] = (poses, fps, boucle)) : idle (il renifle, petit museau qui monte et descend, un
clignement), walk (petites pattes qui trottinent, le corps balance), ball (roulé en boule, piquants dehors : un
aboiement lui a fait peur).
Maman Piquette, elle, est un personnage vu de face (npcs.py, « piquette »).
"""
import math

from spritelib import Drawing, circle, ellipse, path, line, OUTLINE, OUTLINE_W

W = H = 32
G = 28
SCALE = 0.40             # réduction dans le jeu, autour de l'origine (16, G)
C = dict(spike="#7C5536", spike_lt="#A57A50", face="#F6E3C6", face_dk="#DDBE94", leg="#C9A77C", leg_dk="#A88458",
         nose="#2A1611", eye="#3E1B0F", blush="#F2A0A0")


def _spiky(cx, cy, rx, ry, a0, a1, n, out=1.3):
    """Contour hérissé : n grosses dents le long de l'ellipse (cx, cy, rx, ry) entre les angles a0 et a1 (degrés,
    sens de l'écran), refermé par le centre."""
    pts = []
    for k in range(2 * n + 1):
        a = math.radians(a0 + (a1 - a0) * k / (2 * n))
        r = out if k % 2 else 1.0
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + f" L{cx},{cy} Z"


def baby(p):
    """Bébé hérisson. p : sniff (0..1, museau qui monte), blink, step (-1..1, pattes), bob, ball (roulé en boule)."""
    d = Drawing(W, H)
    draw_baby(d, p)
    return d


def draw_baby(d, p):
    """Dessine le bébé hérisson dans d, à la mesure de la cellule (aussi l'icône de son badge)."""
    d.under.append(f'<ellipse cx="16" cy="{G + 0.3}" rx="10" ry="1.9" fill="#000" opacity="0.2"/>')
    if p.get("ball"):                # roulé en boule : des piquants tout autour, le bout du nez qui dépasse
        x, y = 16 + p.get("wob", 0), 20.4
        d.add(path(_spiky(x, y, 7.6, 7.2, 0, 360, 8, 1.36)), C["spike"])
        d.add(circle(x, y, 5.4), C["spike_lt"], sil=False)
        for a in (205, 255, 305, 350, 40):               # quelques piquants sur le dessus de la boule
            r = math.radians(a)
            d.raw(line(f"M{x + 2.2 * math.cos(r):.2f},{y + 2.2 * math.sin(r):.2f} "
                       f"L{x + 4.6 * math.cos(r):.2f},{y + 4.6 * math.sin(r):.2f}", C["spike"], 1.1))
        d.add(ellipse(x + 5.4, y + 3.4, 2.5, 2.0, f"rotate(30 {x + 5.4:.2f} {y + 3.4:.2f})"), C["face"], sil=False)
        d.add(circle(x + 6.9, y + 4.3, 1.25), C["nose"], sil=False)
        return
    b, st, s = p.get("bob", 0), p.get("step", 0), p.get("sniff", 0)
    Y = lambda v: v + b

    # pattes : celles du fond, plus sombres, puis celles de notre côté ; elles trottinent deux à deux
    for x, k, col in ((10.6, -1, C["leg_dk"]), (19.4, 1, C["leg_dk"])):
        d.add(ellipse(x + st * k * 0.9, G - 1.1 - max(0, st * k) * 1.5, 2.0, 1.5), col)
    # le dos : un dôme de piquants, plus clair au milieu
    d.add(path(_spiky(13.4, Y(21.4), 8.6, 8.0, 166, 360, 6, 1.38)), C["spike"])
    d.add(ellipse(13.0, Y(19.6), 6.0, 4.6), C["spike_lt"], sil=False, opacity=0.85)
    for x in (8.8, 12.6, 16.2):                          # trois piquants dessinés sur le dos
        d.raw(line(f"M{x:.2f},{Y(18.6):.2f} L{x - 1.5:.2f},{Y(15.8):.2f}", C["spike"], 1.1))
    # ventre clair, sous le dôme
    d.add(ellipse(14.6, Y(24.6), 8.4, 2.8), C["face"])
    for x, k, col in ((8.2, 1, C["leg"]), (17.0, -1, C["leg"])):
        d.add(ellipse(x + st * k * 0.9, G - 1.0 - max(0, st * k) * 1.5, 2.1, 1.6), col)

    # la tête : grosse, ronde, le museau pointu qui se relève quand il renifle
    hy = Y(21.4) - s * 0.5
    tete = path(f"M16.8,{hy - 0.4:.2f} C16.8,{hy - 4.6:.2f} 20.4,{hy - 5.6:.2f} 23.4,{hy - 4.4:.2f} "
                f"C26.2,{hy - 3.4:.2f} 29.0,{hy - 1.4 - s * 0.9:.2f} 30.6,{hy + 0.4 - s * 1.2:.2f} "
                f"C31.2,{hy + 1.4 - s * 1.2:.2f} 30.6,{hy + 2.4 - s * 1.0:.2f} 29.4,{hy + 2.8 - s * 0.8:.2f} "
                f"C27.0,{hy + 4.4:.2f} 23.6,{hy + 5.2:.2f} 20.6,{hy + 4.8:.2f} C18.2,{hy + 4.4:.2f} 16.8,{hy + 2.6:.2f} 16.8,{hy - 0.4:.2f} Z")
    d.add(circle(18.6, hy - 4.6, 2.2), C["face_dk"])                 # l'oreille, au bord des piquants
    d.add(tete, C["face"])
    d.add(circle(18.9, hy - 4.3, 1.1), C["blush"], sil=False, opacity=0.75)
    d.add(circle(30.2, hy + 0.9 - s * 1.2, 1.6), C["nose"])           # la truffe, ronde, au bout du museau
    d.add(ellipse(29.8, hy + 0.3 - s * 1.2, 0.55, 0.32), "#FFFFFF", sil=False, opacity=0.85)
    d.raw(line(f"M27.2,{hy + 3.4 - s * 0.5:.2f} Q25.6,{hy + 4.0:.2f} 24.4,{hy + 3.2:.2f}", OUTLINE, 0.9))      # le sourire
    ex, ey = 23.4, hy - 0.9
    if p.get("blink"):
        d.raw(line(f"M{ex - 1.6:.2f},{ey:.2f} Q{ex:.2f},{ey + 1.5:.2f} {ex + 1.6:.2f},{ey:.2f}", OUTLINE, 1.0))
    else:                            # un grand œil sombre, deux reflets
        d.add(ellipse(ex, ey, 1.75, 2.1), C["eye"], sil=False)
        d.add(circle(ex + 0.55, ey - 0.75, 0.68), "#FFFFFF", sil=False)
        d.add(circle(ex - 0.5, ey + 0.95, 0.3), "#FFFFFF", sil=False, opacity=0.85)
    d.add(ellipse(21.0, hy + 2.5, 1.6, 0.95), C["blush"], sil=False, opacity=0.7)


ANIMS = {
    "idle": ([dict(), dict(sniff=0.6), dict(sniff=1.0, bob=0.2), dict(sniff=0.3, blink=1)], 5, True),
    "walk": ([dict(step=1, bob=-0.4), dict(step=0), dict(step=-1, bob=-0.4), dict(step=0)], 10, True),
    "ball": ([dict(ball=1, wob=-0.5), dict(ball=1, wob=0.5)], 8, True),
}


def frames(anim):
    """SVG des images d'une animation du bébé hérisson, réduit de SCALE autour de l'origine (16, G)."""
    tr = f"translate(16 {G}) scale({SCALE}) translate(-16 -{G})"
    out = []
    for p in ANIMS[anim][0]:
        d = baby(p)
        d.under = [f'<g transform="{tr}">{u}</g>' for u in d.under]
        out.append(d.svg(tr, outline_w=OUTLINE_W / SCALE))
    return out
