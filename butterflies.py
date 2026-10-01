"""
Papillons du parc (24x24, vus de dessus, tête vers le haut ; le jeu les fait tourner dans le sens du vol).
4 images de battement : ailes ouvertes, mi-closes, presque fermées, mi-closes.
"""
from spritelib import Drawing, circle, ellipse, line, OUTLINE

W = H = 24
COLORS = {   # nom : (ailes, bordure / taches, motif)
    "yellow": ("#F7D154", "#E2A72E", "#FFF1B8"),     # citron
    "blue": ("#7CC3EE", "#2E6FD1", "#D8F0FC"),
    "pink": ("#F4A7C3", "#DE85A8", "#FFFFFF"),
    "orange": ("#F28C28", "#3A1E12", "#FFF7E6"),     # façon monarque
}
SPANS = (1.0, 0.62, 0.22, 0.62)


def butterfly(color, span=1.0):
    wing, dark, spot = COLORS[color]
    d = Drawing(W, H)
    tr = f"translate(12 0) scale({span:.2f} 1) translate(-12 0)"       # les ailes se replient vers le corps
    for s in (-1, 1):
        d.add(ellipse(12 + s * 5.4, 9.2, 5.2, 4.2, f"{tr} rotate({s * -18} {12 + s * 5.4} 9.2)"), wing)    # aile avant
        d.add(ellipse(12 + s * 4.2, 15.6, 3.6, 3.4, f"{tr} rotate({s * 20} {12 + s * 4.2} 15.6)"), wing)   # aile arrière
    for s in (-1, 1):
        d.add(ellipse(12 + s * 7.4, 8.2, 2.2, 1.7, tr), dark, sil=False)          # bout des ailes
        d.add(circle(12 + s * 4.8, 9.8, 1.2, tr), spot, sil=False)
        d.add(circle(12 + s * 4.4, 16.2, 1.0, tr), dark, sil=False, opacity=0.8)
    # corps, tête, antennes (ne bougent pas)
    d.add(ellipse(12, 13, 1.25, 5), "#4A3A30")
    d.add(circle(12, 7.4, 1.5), "#4A3A30")
    d.raw(line("M11.4,6.4 Q10.2,3.4 8.8,2.6 M12.6,6.4 Q13.8,3.4 15.2,2.6", OUTLINE, 0.6))
    for x in (8.8, 15.2):
        d.add(circle(x, 2.6, 0.55), OUTLINE, sil=False)
    return d


def frames(color):
    return [butterfly(color, s).svg() for s in SPANS]
