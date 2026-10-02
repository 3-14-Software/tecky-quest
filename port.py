"""
Le port (zone industrielle agrandie) : ce qui sert aux quêtes de ses habitants.

- Les gros ballons de Léon (quête : les pousser dans le filet) : ballons de plage, une image par couleur, vus de
  dessus (le jeu les fait tourner quand ils roulent). Cadre 32 x 32, origine conseillée au centre (16, 16).
"""
import math

from spritelib import Drawing, circle, ellipse, path

BALL_COLORS = ["#E24B4B", "#F2C14E", "#4A90D9", "#5DBB63", "#A070D0"]   # rouge, jaune, bleu, vert, violet


def beach_ball(d, cx, cy, r, color):
    """Ballon de plage : six quartiers, couleur et blanc en alternance, pastille au centre, reflet."""
    d.add(circle(cx, cy, r), color)
    for k in range(1, 6, 2):
        a0, a1 = math.radians(k * 60 - 90), math.radians((k + 1) * 60 - 90)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        d.add(path(f"M{cx},{cy} L{x0:.2f},{y0:.2f} A{r},{r} 0 0 1 {x1:.2f},{y1:.2f} Z"), "#FFFFFF", sil=False)
    d.add(circle(cx, cy, r * 0.22), color, sil=False, edge=True)
    d.add(ellipse(cx - r * 0.42, cy - r * 0.46, r * 0.24, r * 0.15), "#FFFFFF", sil=False, opacity=0.75)


def balloon_frames():
    """Les cinq ballons de Léon (une image par couleur, dans l'ordre de BALL_COLORS)."""
    out = []
    for col in BALL_COLORS:
        d = Drawing(32, 32)
        beach_ball(d, 16, 16, 13, col)
        out.append(d.svg())
    return out
