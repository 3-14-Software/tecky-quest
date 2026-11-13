"""
Les goélands de la côte de l'été, adversaires de l'aventure : ils tournent dans le ciel, piquent sur Tecky, et un
aboiement les fait repartir. Partout sur la carte, pas seulement à la plage (Christophe : « ça permettra de varier
des chiens »).

Un goéland argenté, de profil vers la droite (la vue gauche est le miroir, fait par le jeu) : cadre 48 x 40, pattes
en (24, 36). Bien plus gros que la mouette rieuse de mouettes.py (dont il reprend les outils de dessin, pas les
poses) : tête blanche, œil jaune sous un sourcil froncé, gros bec jaune crochu à tache rouge, dos gris, pointes des
ailes noires à miroirs blancs, pattes roses.

Animations (`ANIMS` : nom -> (poses, images par seconde, en boucle) ; `frames(anim)` -> SVG) :
- glide : il plane, les ailes tendues, à peine un frémissement (le jeu remonte le sprite et couche son ombre au sol) ;
- flap : il bat des ailes (il reprend de la hauteur, il s'enfuit) ;
- cry : il plane en criant, le bec grand ouvert — il a repéré Tecky ;
- dive : le piqué — le corps penché vers le sol, les ailes ramenées en arrière, le bec en avant ;
- idle : posé (en balade, il se pose et regarde passer Tecky).

    python3 goelands.py      # reference/v2/goelands.png
"""
import os

from spritelib import Drawing, circle, ellipse, path, leg, line, render_svg, PAD, OUTLINE
from mouettes import _aile, _lisse, _dans

W, H, G = 48, 40, 36
C = dict(blanc="#FFFFFF", ombre="#D5DDE6", gris="#8D9BAB", gris_c="#B2BECB", gris_f="#66758A", noir="#2B2A30",
         bec="#F2C230", bec_f="#C9981C", tache="#D8402F", patte="#F0A6A0", iris="#F6E27A", langue="#E98A8A")


def _tete(d, hx, hy, ouvert=0.0, clin=False):
    """Tête blanche, œil jaune, sourcil froncé, gros bec jaune crochu (ouvert : 0 fermé -> 1 grand ouvert)."""
    bx, by = hx + 3.4, hy + 0.8
    a = ouvert * 26
    d.add(path(f"M{bx - 0.6:.2f},{by + 0.2:.2f} L{bx + 5.6:.2f},{by + 1.0:.2f} Q{bx + 3.0:.2f},{by + 2.6:.2f} {bx - 0.6:.2f},{by + 2.2:.2f} Z",
               f"rotate({a * 0.9:.1f} {bx:.2f} {by + 0.8:.2f})"), C["bec_f"])                                   # la mandibule du bas
    d.add(circle(bx + 3.4, by + 1.5, 0.75, f"rotate({a * 0.9:.1f} {bx:.2f} {by + 0.8:.2f})"), C["tache"], sil=False)
    d.add(path(f"M{bx - 0.8:.2f},{by - 1.7:.2f} Q{bx + 4.0:.2f},{by - 2.0:.2f} {bx + 6.6:.2f},{by + 0.2:.2f} "
               f"Q{bx + 7.2:.2f},{by + 1.8:.2f} {bx + 6.0:.2f},{by + 2.2:.2f} Q{bx + 5.6:.2f},{by + 1.0:.2f} {bx + 4.4:.2f},{by + 0.9:.2f} "
               f"L{bx - 0.8:.2f},{by + 0.9:.2f} Z", f"rotate({-a * 0.5:.1f} {bx:.2f} {by:.2f})"), C["bec"])    # celle du haut, crochue
    d.add(circle(hx, hy, 4.7), C["blanc"])
    ex, ey = hx + 1.5, hy - 0.5
    if clin:
        d.raw(line(f"M{ex - 1.2:.2f},{ey:.2f} Q{ex:.2f},{ey + 0.9:.2f} {ex + 1.2:.2f},{ey:.2f}", OUTLINE, 0.8))
    else:
        d.add(circle(ex, ey, 1.35), C["iris"], sil=False, edge=True)
        d.add(circle(ex + 0.25, ey, 0.6), OUTLINE, sil=False)
    d.raw(line(f"M{ex - 2.0:.2f},{ey - 2.3:.2f} L{ex + 2.0:.2f},{ey - 1.2:.2f}", OUTLINE, 1.0))                # le sourcil
    return bx + 6.0, by + 1.0


def _pointe(d, A, cid):
    """La pointe noire d'une aile et ses deux miroirs blancs."""
    _dans(d, cid, _lisse([A(0.68, -3.6), A(1.3, -1.0), A(1.1, 2.8), A(0.68, 3.8)]), C["noir"])
    for u, v in ((0.84, 0.6), (0.93, -0.5)):
        x, y = A(u, v)
        d.raw(f'<g clip-path="url(#{cid})"><circle cx="{x:.2f}" cy="{y:.2f}" r="0.7" fill="#FFFFFF"/></g>')


def _vol(theta=-112.0, envergure=20.0, bob=0.0, ouvert=0.0, corde=1.25):
    """En vol, le corps à l'horizontale, centré vers (22, 22)."""
    d = Drawing(W, H)
    y = bob
    loin, _ = _aile(theta - 7, envergure * 0.92, (25.0, 19.4 + y), corde * 0.9)
    d.add(loin, C["gris_f"])
    d.add(path(f"M13.4,{20.0 + y:.2f} L3.6,{18.4 + y:.2f} L4.6,{22.4 + y:.2f} L3.8,{25.6 + y:.2f} L13.6,{24.6 + y:.2f} Z"), C["blanc"])     # la queue
    d.add(path(f"M15.4,{24.8 + y:.2f} L9.4,{26.2 + y:.2f} L8.8,{28.0 + y:.2f} L11.6,{27.8 + y:.2f} L16.4,{26.2 + y:.2f} Z"), C["patte"])     # les pattes repliées
    corps = ellipse(21.4, 22.2 + y, 10.6, 5.0, f"rotate(-3 21.4 {22.2 + y:.2f})")
    cou = ellipse(29.6, 20.0 + y, 4.6, 4.4, f"rotate(20 29.6 {20.0 + y:.2f})")
    d.add(corps, C["blanc"])
    d.add(cou, C["blanc"])
    d.clip("corps", [corps, cou])
    _dans(d, "corps", ellipse(21.0, 26.2 + y, 11.4, 2.6), C["ombre"])
    forme, A = _aile(theta, envergure, (23.6, 20.2 + y), corde)
    d.clip("aile", [forme])
    d.add(forme, C["gris"], edge=True)
    _pointe(d, A, "aile")
    _dans(d, "aile", _lisse([A(0.0, -2.6), A(0.5, -3.4), A(0.7, -2.4), A(0.3, -1.4)]), C["gris_c"], 0.9)
    a, b = A(0.02, 3.0), A(0.62, 2.6)
    d.raw('<g clip-path="url(#aile)">' + line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", C["blanc"], 1.0) + "</g>")
    _tete(d, 33.4, 17.6 + y, ouvert)
    return d


def _pique(k=0.0, ouvert=1.0):
    """Le piqué : le même oiseau penché vers le sol, les ailes ramenées en arrière (k : un frémissement)."""
    d = _vol(theta=-158 + k * 6, envergure=15.0, ouvert=ouvert, corde=1.1)
    d.tr = f"rotate(36 24 22) translate({k * 0.6:.2f} 0)"
    return d


def _pose(bob=0.0, dx=0.0, dy=0.0, ouvert=0.0, clin=False):
    """Posé, les ailes repliées."""
    d = Drawing(W, H)
    d.under.append(f'<ellipse cx="22" cy="{G}" rx="11" ry="2.8" fill="#000" opacity="0.18"/>')
    y = bob
    for x in (20.0, 24.2):
        d.add(leg(x, 29.5 + y, x, G - 0.7, 1.6), C["patte"])
        d.add(path(f"M{x - 0.9:.2f},{G - 1.4:.2f} L{x + 3.8:.2f},{G - 0.1:.2f} L{x - 0.9:.2f},{G + 0.3:.2f} Z"), C["patte"])
    d.add(path(f"M12.6,{23.6 + y:.2f} L4.2,{26.6 + y:.2f} L12.2,{29.0 + y:.2f} Z"), C["blanc"])
    d.add(path(f"M15.2,{21.8 + y:.2f} L3.2,{24.4 + y:.2f} L14.6,{26.8 + y:.2f} Z"), C["noir"])
    for x, yy in ((6.4, 24.6), (9.0, 25.4)):
        d.add(circle(x, yy + y, 0.6), "#FFFFFF", sil=False)
    corps = ellipse(20.6, 25.4 + y, 10.4, 6.6, f"rotate(-9 20.6 {25.4 + y:.2f})")
    cou = ellipse(27.8 + dx * 0.5, 20.4 + y + dy * 0.4, 4.6, 6.4, f"rotate(26 {27.8 + dx * 0.5:.2f} {20.4 + y + dy * 0.4:.2f})")
    d.add(corps, C["blanc"])
    d.add(cou, C["blanc"])
    d.clip("corps", [corps, cou])
    _dans(d, "corps", ellipse(19.6, 30.8 + y, 11.4, 3.2, f"rotate(-9 19.6 {30.8 + y:.2f})"), C["ombre"])
    dos = _lisse([(28.4, 20.6 + y), (21.6, 18.0 + y), (12.6, 20.6 + y), (8.2, 24.4 + y), (14.6, 27.0 + y), (22.8, 27.4 + y), (28.6, 24.6 + y)])
    d.clip("dos", [dos])
    d.add(dos, C["gris"], sil=False, edge=True)
    _dans(d, "dos", ellipse(20.4, 20.2 + y, 7.6, 1.8, f"rotate(-8 20.4 {20.2 + y:.2f})"), C["gris_c"], 0.9)
    d.raw(line(f"M13.4,{24.4 + y:.2f} Q19.0,{26.2 + y:.2f} 25.8,{24.4 + y:.2f}", C["gris_f"], 0.7))
    _tete(d, 31.0 + dx, 14.6 + y + dy, ouvert, clin)
    return d


ANIMS = {   # nom : (poses, images par seconde, en boucle)
    "glide": ([dict(vol=(-130, 20.0, 0.0)), dict(vol=(-128, 20.2, 0.3)), dict(vol=(-130, 20.0, 0.5)), dict(vol=(-132, 19.8, 0.3))], 5, True),
    "flap": ([dict(vol=(-104, 20.0, 0.7)), dict(vol=(-138, 12.0, 0.0)), dict(vol=(112, 17.0, -0.8)), dict(vol=(-150, 11.0, -0.1))], 11, True),
    "cry": ([dict(vol=(-130, 20.0, 0.0), ouvert=1.0), dict(vol=(-127, 20.2, 0.4), ouvert=0.6)], 7, True),
    "dive": ([dict(pique=0.0), dict(pique=1.0)], 12, True),
    "idle": ([dict(), dict(bob=0.4, dy=0.3), dict(dx=0.5, dy=-0.5), dict(bob=0.4, dy=0.3, clin=True)], 4, True),
}


def pose(vol=None, pique=None, **kw):
    if pique is not None:
        return _pique(pique)
    if vol is not None:
        return _vol(vol[0], vol[1], vol[2], **kw)
    return _pose(**kw)


def frames(anim):
    """SVG des images d'une animation (vue de droite)."""
    return [(lambda d: d.svg(getattr(d, "tr", "")))(pose(**p)) for p in ANIMS[anim][0]]


if __name__ == "__main__":
    from PIL import Image
    rangs = [[render_svg(sv, W, H, 8, PAD) for sv in frames(a)] for a in ANIMS]
    cw, ch = rangs[0][0].size
    pl = Image.new("RGBA", (4 * cw, len(rangs) * ch), (150, 200, 232, 255))
    for j, r in enumerate(rangs):
        for i, im in enumerate(r):
            pl.alpha_composite(im, (i * cw, j * ch))
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference", "v2", "goelands.png")
    pl.convert("RGB").save(fn)
    print(fn, pl.size)
