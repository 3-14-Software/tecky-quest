"""
Les bébés hérissons de Maman Piquette (quête de la forêt) : de profil, tournés vers la droite (la vue gauche est le
miroir, faite par le jeu). Cellule 32 x 32, pieds à y = 28 : origine conseillée (16, 28), comme critters.py.

Animations (ANIMS[nom] = (poses, fps, boucle)) : idle (il renifle, petit museau qui monte et descend, un
clignement), walk (petites pattes qui trottinent, le corps balance), ball (roulé en boule, piquants dehors : un
aboiement lui a fait peur).
Maman Piquette, elle, est un personnage vu de face (npcs.py, « piquette »).
"""
import math

from spritelib import Drawing, circle, ellipse, path, line, OUTLINE

W = H = 32
G = 28
C = dict(spike="#7C5536", spike_lt="#A57A50", face="#F3DFC0", face_dk="#DCC19A", leg="#5A3C24", nose="#2A1E1A",
         blush="#F2A0A0")


def _spiky(cx, cy, rx, ry, a0, a1, n, out=1.32):
    """Contour hérissé : n pointes le long de l'ellipse (cx, cy, rx, ry) entre les angles a0 et a1 (degrés, sens de
    l'écran), refermé par le centre."""
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
    """Dessine le bébé hérisson dans d (aussi l'icône de son badge)."""
    d.under.append(f'<ellipse cx="16" cy="{G + 0.3}" rx="8.5" ry="1.7" fill="#000" opacity="0.2"/>')
    if p.get("ball"):
        wob = p.get("wob", 0)
        d.add(path(_spiky(16 + wob, 21.4, 7.2, 6.6, 0, 360, 11, 1.28)), C["spike"])
        d.add(circle(16 + wob, 21.4, 5.2), C["spike_lt"], sil=False)
        for a in (200, 250, 300, 340):
            r = math.radians(a)
            d.raw(line(f"M{16 + wob + 2 * math.cos(r):.2f},{21.4 + 2 * math.sin(r):.2f} "
                       f"L{16 + wob + 5 * math.cos(r):.2f},{21.4 + 5 * math.sin(r):.2f}", C["spike"], 0.8))
        d.add(circle(21.6 + wob, 24.6, 0.9), C["nose"], sil=False)          # le bout du museau qui dépasse
        return
    b, st = p.get("bob", 0), p.get("step", 0)
    for x, k in ((10.5, 1), (13.5, -1), (18.5, -1), (21.5, 1)):            # pattes
        lift = max(0, st * k) * 1.4
        d.add(ellipse(x + st * k * 0.6, G - 0.9 - lift, 1.5, 1.2), C["leg"])
    d.add(path(_spiky(14.5, 22.2 + b, 9.2, 6.6, 180, 355, 7)), C["spike"])   # dos hérissé
    d.add(ellipse(14.2, 21.0 + b, 6.4, 3.6), C["spike_lt"], sil=False, opacity=0.8)
    for x in (9.5, 13, 16.5):
        d.raw(line(f"M{x},{18.6 + b} L{x - 1.4},{16.4 + b}", C["spike"], 0.8))
    d.add(ellipse(15.5, 24.8 + b, 7.6, 2.6), C["face"])                      # ventre
    s = p.get("sniff", 0)
    d.add(ellipse(22.4, 22.6 + b, 4.6, 3.6), C["face"])                      # tête
    d.add(path(f"M24.6,{20.6 + b - s * 0.6} Q29.6,{21.4 + b - s * 1.2} 29.2,{23.0 + b - s * 1.0} "
               f"Q27.2,{25.2 + b - s * 0.4} 23.8,{25.0 + b} Z"), C["face"])  # museau pointu
    d.add(circle(29.0, 22.4 + b - s * 1.1, 1.15), C["nose"], sil=False)
    d.add(circle(20.6, 19.4 + b, 1.35), C["face_dk"], sil=False, edge=True)  # oreille
    if p.get("blink"):
        d.raw(line(f"M22.6,{21.6 + b} Q23.5,{22.4 + b} 24.4,{21.6 + b}", C["nose"], 0.7))
    else:
        d.add(circle(23.5, 21.6 + b, 0.95), C["nose"], sil=False)
        d.add(circle(23.8, 21.3 + b, 0.32), "#FFFFFF", sil=False)
    d.add(ellipse(24.2, 23.6 + b, 1.1, 0.65), C["blush"], sil=False, opacity=0.7)


ANIMS = {
    "idle": ([dict(), dict(sniff=0.6), dict(sniff=1.0, bob=0.2), dict(sniff=0.3, blink=1)], 5, True),
    "walk": ([dict(step=1, bob=-0.3), dict(step=0), dict(step=-1, bob=-0.3), dict(step=0)], 10, True),
    "ball": ([dict(ball=1, wob=-0.4), dict(ball=1, wob=0.4)], 8, True),
}


def frames(anim):
    """SVG des images d'une animation du bébé hérisson."""
    return [baby(p).svg() for p in ANIMS[anim][0]]
