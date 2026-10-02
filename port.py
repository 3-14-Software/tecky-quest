"""
Le port (zone industrielle agrandie) : ce qui sert aux quêtes de ses habitants.

- Les gros ballons de Léon (quête : les pousser dans le filet) : ballons de plage, une image par couleur, vus de
  dessus (le jeu les fait tourner quand ils roulent). Cadre 32 x 32, origine conseillée au centre (16, 16).
- Les trois jouets de Nestor, le vieux chien du gardien (quête : les lui rapporter un par un dans la gueule) :
  canard en caoutchouc (tourné vers la gauche), anneau, corde à nœuds. Cadre 32 x 32, origine au centre.
"""
import math

from spritelib import Drawing, circle, ellipse, path, poly, line, OUTLINE

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


TOYS = ["duck", "ring", "rope"]


def rubber_duck(d, dx=0.0, dy=0.0):
    """Canard en caoutchouc jaune, tourné vers la gauche (aussi l'icône du badge de Nestor)."""
    d.add(path(f"M{6 + dx},{19 + dy} Q{6 + dx},{27 + dy} {16 + dx},{27 + dy} L{22 + dx},{27 + dy} "
               f"Q{29 + dx},{26.5 + dy} {28 + dx},{18.5 + dy} Q{27 + dx},{14 + dy} {23.5 + dx},{16.5 + dy} "
               f"L{15 + dx},{17 + dy} Z"), "#F7D154")
    d.add(circle(12 + dx, 12.5 + dy, 5.6), "#F7D154")
    d.add(path(f"M{6.8 + dx},{12.2 + dy} Q{2.2 + dx},{12.6 + dy} {2.8 + dx},{14.6 + dy} Q{4.5 + dx},{16 + dy} {7.6 + dx},{15 + dy} Z"),
          "#F28C28")
    d.add(circle(11 + dx, 11.2 + dy, 1.1), OUTLINE, sil=False)
    d.add(circle(11.4 + dx, 10.8 + dy, 0.35), "#FFFFFF", sil=False)
    d.raw(line(f"M{15.5 + dx},{21 + dy} Q{19.5 + dx},{24 + dy} {23.5 + dx},{20.5 + dy}", "#D9A92F", 1.2))


def toy_frames():
    """Les trois jouets de Nestor (dans l'ordre de TOYS)."""
    out = []
    d = Drawing(32, 32)
    rubber_duck(d)
    out.append(d.svg())
    d = Drawing(32, 32)                      # anneau rouge à bandes bleues
    ring = path("M5,16 a11,11 0 1,0 22,0 a11,11 0 1,0 -22,0 Z M10.6,16 a5.4,5.4 0 1,0 10.8,0 a5.4,5.4 0 1,0 -10.8,0 Z")
    d.add(ring.replace("<path ", '<path fill-rule="evenodd" '), "#E24B4B")
    for a in (20, 140, 260):                 # bandes bleues, posées dans l'épaisseur de l'anneau
        pts = []
        for r, da in ((5.9, -11), (5.9, 11), (10.5, 8), (10.5, -8)):
            t = math.radians(a + da)
            pts.append((16 + r * math.cos(t), 16 + r * math.sin(t)))
        d.add(poly(pts), "#4A90D9", sil=False)
    d.add(ellipse(11.5, 9.6, 2.4, 1.2), "#FFFFFF", sil=False, opacity=0.6)
    out.append(d.svg())
    d = Drawing(32, 32)                      # corde à nœuds : torsades en pointillé, un nœud à chaque bout
    rope = "M8,21.5 Q16,11.5 25,17"
    d.raw(line(rope, OUTLINE, 7.0) + line(rope, "#E3C995", 4.6)
          + line(rope, "#C9A26D", 4.6).replace("/>", ' stroke-dasharray="1.3 2.4"/>'))
    for cx, cy in ((7.2, 22.2), (25.4, 17.4)):
        d.add(circle(cx, cy, 3.6), "#D4B47A")
        d.raw(line(f"M{cx - 2:.1f},{cy - 1:.1f} Q{cx},{cy + 1.5} {cx + 2:.1f},{cy - 1:.1f}", "#B8955E", 0.8))
    out.append(d.svg())
    return out
