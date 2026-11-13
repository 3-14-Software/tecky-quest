"""
Les moutons de pré salé d'Anatole, le gardien du phare (la côte de l'été) : les poules de Gaston, en plus gros.
De profil vers la droite, cadre de 48 x 40, pieds en (24, 36). Mêmes animations que les poules (hens.py : idle,
peck = il broute, walk, flap = il détale), aux mêmes nombres d'images : le jeu les traite comme des poules
(game.js : newHen, genre « sheep » de la liste hens d'une carte).

    python3 moutons.py      # reference/v2/moutons.png
"""
import os

from spritelib import Drawing, circle, ellipse, leg, line, render_svg, PAD, OUTLINE

W, H, G = 48, 40, 36
LAINE, LAINE_O, TETE, TETE_C = "#FBF7EC", "#D9D1BF", "#4A3F38", "#6A5C52"


def pose(peck=0.0, step=0.0, hop=0.0, head=0.0, wing=None):
    """peck : 0 la tête haute -> 1 le nez dans l'herbe ; step : -1..1, le pas ; hop : il décolle ; head : petit
    mouvement de tête ; wing (le battement d'ailes des poules) : ici, les oreilles en arrière quand il détale."""
    d = Drawing(W, H)
    d.under.append(f'<ellipse cx="24" cy="{G}" rx="{15 - hop}" ry="2.6" fill="#000" opacity="0.18"/>')
    y = -hop
    for x, ph in ((14.5, 1), (18.5, -1), (29.5, -1), (33.5, 1)):                 # quatre pattes sombres
        d.add(leg(x, 26 + y, x + step * ph * 2.6, G - (hop * 0.6 if ph * step < 0 else 0), 2.5), TETE)
    d.add(circle(9.2, 19.5 + y, 3.2), LAINE)                                    # la queue
    laine = [(14, 20.5, 6.6), (19, 16.6, 6.6), (25.5, 15.4, 7.2), (31.5, 17.2, 6.6), (34, 21.6, 6.0), (29, 24.6, 6.6),
             (22, 25.4, 7.0), (16, 24.6, 6.0)]
    d.clip("laine", [circle(cx, cy + y, r) for cx, cy, r in laine])
    for cx, cy, r in laine:
        d.add(circle(cx, cy + y, r), LAINE)
    d.raw('<g clip-path="url(#laine)">' + ellipse(24, 29.5 + y, 16, 5).replace('fill="%F%"', f'fill="{LAINE_O}"') + "</g>")
    d.raw(line(f"M17,{19 + y} q2,-2.2 4,0 M24,{17.4 + y} q2.2,-2.4 4.4,0 M20.6,{23 + y} q2,-2 4,0 M28.6,{21.6 + y} q2,-2 4,0",
               LAINE_O, 0.9))
    hx, hy = 38.4 + peck * 1.6, 15.6 + y + peck * 12.5 - head * 0.8              # la tête : elle descend pour brouter
    rot = peck * 58 - head * 6
    tr = f"rotate({rot:.1f} {hx:.2f} {hy:.2f})"
    back = -34 if wing is not None else 0
    d.add(ellipse(hx - 3.6, hy - 1.6, 3.4, 1.7, f"{tr} rotate({-22 + back} {hx - 2:.2f} {hy - 1.6:.2f})"), TETE)      # l'oreille
    d.add(ellipse(hx + 0.6, hy + 1.2, 3.9, 5.2, f"{tr} rotate(-18 {hx:.2f} {hy:.2f})"), TETE)                        # le chanfrein
    d.add(ellipse(hx + 2.0, hy + 4.4, 2.2, 1.6, tr), TETE_C, sil=False)
    for cx, cy, r in ((-1.6, -3.4, 3.6), (1.4, -4.2, 2.8), (-3.6, -1.2, 2.6)):                                      # le toupet de laine
        d.add(circle(hx + cx, hy + cy, r, tr), LAINE)
    d.add(circle(hx + 1.6, hy - 0.2, 1.0, tr), "#FFFFFF", sil=False)
    d.add(circle(hx + 1.9, hy - 0.1, 0.55, tr), OUTLINE, sil=False)
    return d


ANIMS = {   # nom : (poses, fps, boucle) — mêmes noms et mêmes nombres d'images que hens.ANIMS
    "idle": ([dict(), dict(head=0.5), dict(), dict(head=-0.4)], 4, True),
    "peck": ([dict(), dict(peck=0.55), dict(peck=1.0), dict(peck=0.85), dict(peck=1.0), dict(peck=0.5), dict()], 10, False),
    "walk": ([dict(step=1, head=0.6), dict(step=0, hop=0.5), dict(step=-1, head=0.6), dict(step=0, hop=0.5)], 10, True),
    "flap": ([dict(wing=1, hop=2.2, step=1), dict(wing=1, hop=3.6, step=0.2), dict(wing=1, hop=2.4, step=-1), dict(wing=1, hop=0.8, step=-0.2)],
             14, True),
}


def frames(anim):
    return [pose(**p).svg() for p in ANIMS[anim][0]]


if __name__ == "__main__":
    from PIL import Image
    ims = [render_svg(sv, W, H, 6, PAD) for a in ANIMS for sv in frames(a)]
    pl = Image.new("RGBA", (sum(i.width for i in ims[:10]), 2 * ims[0].height), (196, 198, 88, 255))
    for i, im in enumerate(ims):
        pl.alpha_composite(im, ((i % 10) * im.width, (i // 10) * im.height))
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference", "v2", "moutons.png")
    pl.convert("RGB").save(fn)
    print(fn, pl.size)
