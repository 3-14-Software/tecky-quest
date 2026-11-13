"""
Les crabes de la plage (la côte de l'été), adversaires de l'aventure : ils pincent si Tecky leur marche dessus et
s'enterrent dans le sable quand il aboie.

Vu de face, un peu d'en haut : cadre 32 x 32, le bas des pattes en (16, 26). Carapace rouge orangé, deux yeux au
bout de leurs tiges, trois pattes de chaque côté, deux grosses pinces. Dessiné grand, puis réduit de `SCALE` autour
de ses pattes, le contour compensé (comme les bêtes de critters.py) : bien plus petit que Tecky.

Animations (`ANIMS` : nom -> (poses, images par seconde, en boucle) ; `frames(anim)` -> SVG) :
- idle : il respire, cligne des yeux ;
- walk : il marche en crabe, les pattes en alternance (le jeu le déplace de côté) ;
- menace : Tecky approche — pinces levées, qui claquent, sourcils froncés ;
- pinch : il pince (une pince en avant, refermée d'un coup) ;
- wave : en balade, il salue d'une pince ;
- bury : il s'enfonce dans le sable (une butte se forme) ; `unbury` : il en ressort ;
- buried : enterré — une butte de sable d'où dépassent ses deux yeux, qui clignent.

    python3 crabes.py      # reference/v2/crabes.png
"""
import math
import os

from spritelib import Drawing, circle, ellipse, rect, path, line, render_svg, PAD, OUTLINE, OUTLINE_W
from plage import SABLE, SABLE_O, SABLE_C

W = H = 32
G = 26                 # le bas des pattes
SCALE = 0.74
C = dict(corps="#E8623A", clair="#F79A6A", ombre="#BE4426", ventre="#F6C9A6", pince="#EE6E42", pince_c="#FBB08A",
         patte="#D4502C", blanc="#FFFFFF", bouche="#7A2A1A")


def _dans(d, cid, forme, couleur, opacity=None):
    op = f' opacity="{opacity}"' if opacity is not None else ""
    d.raw(f'<g clip-path="url(#{cid})"{op}>' + forme.replace('fill="%F%"', f'fill="{couleur}"') + "</g>")


def _pince(d, s, ex, ey, hx, hy, ouvert, taille=1.0):
    """Un bras et sa pince. s : -1 à gauche, 1 à droite ; (ex, ey) : l'attache sur la carapace ; (hx, hy) : le centre
    de la pince ; ouvert : 0 fermée -> 1 grande ouverte. La pince pointe vers le haut et un peu vers l'intérieur."""
    mx, my = (ex + hx) / 2 + s * 1.6, (ey + hy) / 2 + 1.0                        # le coude, vers l'extérieur
    d.add(path(f"M{ex:.2f},{ey:.2f} Q{mx:.2f},{my:.2f} {hx:.2f},{hy + 1.6:.2f} L{hx + s * 1.8:.2f},{hy + 2.4:.2f} "
               f"Q{mx + s * 1.8:.2f},{my + 1.4:.2f} {ex + s * 0.6:.2f},{ey + 2.0:.2f} Z"), C["patte"])
    k = taille
    rot = -s * 14
    tr = f"rotate({rot} {hx:.2f} {hy:.2f})"
    a = ouvert * 26
    # le doigt mobile (côté intérieur), puis la main et son doigt fixe
    d.add(path(f"M{hx - s * 1.2 * k:.2f},{hy:.2f} Q{hx - s * 3.4 * k:.2f},{hy - 2.4 * k:.2f} {hx - s * 1.4 * k:.2f},{hy - 5.6 * k:.2f} "
               f"Q{hx - s * 0.2 * k:.2f},{hy - 3.0 * k:.2f} {hx + s * 0.2 * k:.2f},{hy - 0.6 * k:.2f} Z",
               f"{tr} rotate({-s * a:.1f} {hx - s * 0.8 * k:.2f} {hy:.2f})"), C["pince"])
    main = path(f"M{hx - s * 2.0 * k:.2f},{hy + 1.6 * k:.2f} Q{hx - s * 2.6 * k:.2f},{hy - 1.0 * k:.2f} {hx - s * 0.2 * k:.2f},{hy - 1.4 * k:.2f} "
                f"Q{hx + s * 0.8 * k:.2f},{hy - 3.6 * k:.2f} {hx + s * 1.4 * k:.2f},{hy - 6.2 * k:.2f} "
                f"Q{hx + s * 4.6 * k:.2f},{hy - 2.4 * k:.2f} {hx + s * 3.2 * k:.2f},{hy + 1.4 * k:.2f} "
                f"Q{hx + s * 0.6 * k:.2f},{hy + 3.4 * k:.2f} {hx - s * 2.0 * k:.2f},{hy + 1.6 * k:.2f} Z", tr)
    d.add(main, C["pince"])
    d.add(ellipse(hx + s * 1.5 * k - 0.6, hy - 1.2 * k, 1.0 * k, 1.9 * k, f"{tr} rotate({s * 20} {hx:.2f} {hy:.2f})"), C["pince_c"], sil=False, opacity=0.9)


def _yeux(d, y, clin=False, fache=False, content=False, dx=0.0):
    """Les deux yeux au bout de leurs tiges (y : le haut de la carapace)."""
    for s in (-1, 1):
        bx, hx, hy = 16 + s * 3.0, 16 + s * 3.6 + dx, y - 5.2
        d.add(path(f"M{bx - 0.8:.2f},{y + 1:.2f} L{hx - 0.7:.2f},{hy:.2f} L{hx + 0.7:.2f},{hy:.2f} L{bx + 0.8:.2f},{y + 1:.2f} Z"), C["corps"])
        d.add(circle(hx, hy - 0.6, 2.2), C["blanc"])
        if clin or content:
            d.raw(line(f"M{hx - 1.3:.2f},{hy - 0.4:.2f} Q{hx:.2f},{hy - (1.8 if content else -0.6):.2f} {hx + 1.3:.2f},{hy - 0.4:.2f}", OUTLINE, 0.8))
        else:
            d.add(circle(hx + dx * 0.4 - s * 0.2, hy - 0.4, 1.05), OUTLINE, sil=False)
            d.add(circle(hx + dx * 0.4 - s * 0.2 + 0.35, hy - 0.8, 0.35), "#FFFFFF", sil=False)
        if fache:                                                                # un sourcil froncé, en travers de l'œil
            d.raw(line(f"M{hx - s * 2.2:.2f},{hy - 1.4:.2f} L{hx + s * 1.6:.2f},{hy - 3.2:.2f}", OUTLINE, 1.0))


def _crabe(bob=0.0, pas=0.0, dx=0.0, pinces=0.0, ouvert=0.0, avant=0.0, clin=False, fache=False, content=False, salut=None,
           enfonce=0.0):
    """bob : il s'abaisse ; pas : -1..1, les pattes ; dx : le corps se décale ; pinces : 0 basses -> 1 levées ;
    ouvert : les pinces ; avant : la pince droite part en avant (il pince) ; salut : angle de la pince gauche qui
    salue ; enfonce : 0 -> 1, il s'enfonce dans le sable (tout ce qui passe sous le sol est coupé, une butte monte)."""
    d = Drawing(W, H)
    if enfonce < 0.3:
        d.under.append(f'<ellipse cx="{16 + dx * SCALE:.2f}" cy="{G}" rx="{10 * SCALE:.2f}" ry="{2.4 * SCALE:.2f}" fill="#000" opacity="0.18"/>')
    y = bob + enfonce * 9.0
    cx = 16 + dx
    n0 = len(d.parts)
    for s in (-1, 1):                                                            # trois pattes de chaque côté
        for i, (ax, fx) in enumerate(((5.4, 9.6), (6.6, 11.6), (7.4, 12.6))):
            ph = pas * (1 if (i + (s > 0)) % 2 else -1)
            x0, y0 = cx + s * ax, 19.6 + y + i * 0.5
            x1, y1 = cx + s * (fx + ph * 1.2), G - (1.6 if ph > 0.5 else 0) - i * 0.9 + enfonce * 4
            mx, my = (x0 + x1) / 2 + s * 1.8, y0 - 2.2 - i * 0.3
            d.add(path(f"M{x0:.2f},{y0 - 1.0:.2f} L{mx + s * 0.5:.2f},{my - 1.0:.2f} L{x1 + s * 0.5:.2f},{y1:.2f} L{x1 - s * 0.9:.2f},{y1:.2f} L{mx - s * 0.9:.2f},{my + 1.2:.2f} L{x0:.2f},{y0 + 1.2:.2f} Z"), C["patte"])
    corps = path(f"M{cx - 8.6:.2f},{18.6 + y:.2f} Q{cx - 8.2:.2f},{13.2 + y:.2f} {cx:.2f},{13.0 + y:.2f} Q{cx + 8.2:.2f},{13.2 + y:.2f} {cx + 8.6:.2f},{18.6 + y:.2f} "
                 f"Q{cx + 7.0:.2f},{23.6 + y:.2f} {cx:.2f},{23.8 + y:.2f} Q{cx - 7.0:.2f},{23.6 + y:.2f} {cx - 8.6:.2f},{18.6 + y:.2f} Z")
    # les pinces : au repos, basses devant lui ; levées, de part et d'autre des yeux
    for s in (-1, 1):
        lev = pinces
        hx = cx + s * (10.6 - lev * 0.6)
        hy = 21.4 + y - lev * 10.0
        if s == 1 and avant:
            hx, hy = cx + 9.0 + avant * 1.6, 19.0 + y - (1 - avant) * 5.0
        if s == -1 and salut is not None:
            a = math.radians(salut)
            hx, hy = cx - 9.6 + math.sin(a) * 2.6, 11.0 + y - math.cos(a) * 1.0
        _pince(d, s, cx + s * 7.2, 18.4 + y, hx, hy, ouvert, 1.0)
    d.add(corps, C["corps"])
    d.clip("corps", [corps])
    _dans(d, "corps", ellipse(cx, 23.6 + y, 9.0, 3.0), C["ombre"])
    _dans(d, "corps", ellipse(cx - 2.6, 15.2 + y, 4.2, 1.4, f"rotate(-8 {cx - 2.6:.2f} {15.2 + y:.2f})"), C["clair"], 0.9)
    for px, py, r in ((-4.6, 18.0, 0.7), (4.2, 17.2, 0.6), (5.6, 19.6, 0.5), (-2.0, 20.4, 0.5)):
        d.add(circle(cx + px, py + y, r), C["ombre"], sil=False, opacity=0.7)
    if content:
        d.raw(line(f"M{cx - 2.0:.2f},{20.6 + y:.2f} Q{cx:.2f},{22.4 + y:.2f} {cx + 2.0:.2f},{20.6 + y:.2f}", C["bouche"], 0.8))
    elif fache:
        d.raw(line(f"M{cx - 1.8:.2f},{21.6 + y:.2f} Q{cx:.2f},{20.2 + y:.2f} {cx + 1.8:.2f},{21.6 + y:.2f}", C["bouche"], 0.8))
    else:
        d.raw(line(f"M{cx - 1.4:.2f},{21.0 + y:.2f} L{cx + 1.4:.2f},{21.0 + y:.2f}", C["bouche"], 0.8))
    _yeux(d, 13.6 + y, clin, fache, content, dx * 0.3)
    if enfonce > 0:                                                              # ce qui est sous le sol est coupé ; la butte monte
        sol = G - 1.0 - enfonce * 1.2
        d.clip("sol", [rect(0, 0, W, sol)])
        for i in range(n0, len(d.parts)):
            xml, fill, sil, extra = d.parts[i]
            d.parts[i] = (f'<g clip-path="url(#sol)">{xml}</g>', fill, sil, extra)
        _butte(d, enfonce)
    return d


def _butte(d, k):
    """La butte de sable où il s'enterre (k : 0 -> 1, elle monte). Pas de contour brun : c'est du sol."""
    rx, h = 12.4 + k * 0.4, 1.8 + k * 4.0
    d.raw(f'<ellipse cx="16.6" cy="{G + 0.4}" rx="{rx + 1.0:.2f}" ry="2.6" fill="#B9955A" opacity="0.45"/>'
          f'<path d="M{16 - rx:.2f},{G:.2f} Q{16 - rx * 0.9:.2f},{G - h:.2f} 16,{G - h - 0.3:.2f} Q{16 + rx * 0.9:.2f},{G - h:.2f} {16 + rx:.2f},{G:.2f} '
          f'Q16,{G + 2.4:.2f} {16 - rx:.2f},{G:.2f} Z" fill="{SABLE}" stroke="{SABLE_O}" stroke-width="0.8" stroke-linejoin="round"/>'
          f'<path d="M{16 - rx * 0.7:.2f},{G - h * 0.5:.2f} Q{16 - rx * 0.45:.2f},{G - h * 0.95:.2f} 16,{G - h:.2f} Q{16 - rx * 0.3:.2f},{G - h * 0.6:.2f} {16 - rx * 0.4:.2f},{G - h * 0.2:.2f} Z" '
          f'fill="{SABLE_C}" opacity="0.9"/>'
          + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in
                    ((16 - rx - 1.2, G + 1.0, 0.7, SABLE_O), (16 + rx + 1.0, G + 0.6, 0.6, SABLE_O), (13.0, G + 2.2, 0.5, SABLE))))


def _enterre(clin=False, dx=0.0, haut=0.0):
    """Enterré : la butte, et ses deux yeux qui dépassent (haut : ils se haussent pour regarder)."""
    d = Drawing(W, H)
    _yeux(d, G - 2.2 - haut, clin, dx=dx)
    _butte(d, 1.0)
    return d


_BURY = [dict(enfonce=k, pinces=0.3 * (1 - k), clin=k > 0.6) for k in (0.2, 0.45, 0.7, 0.9)]
ANIMS = {   # nom : (poses, images par seconde, en boucle)
    "idle": ([dict(), dict(bob=0.4), dict(bob=0.6), dict(bob=0.4, clin=True)], 4, True),
    "walk": ([dict(pas=1, dx=0.5), dict(pas=0.2, bob=0.4), dict(pas=-1, dx=-0.5), dict(pas=-0.2, bob=0.4)], 10, True),
    "menace": ([dict(pinces=1, ouvert=1, fache=True), dict(pinces=1, ouvert=0, fache=True, bob=-0.5),
                dict(pinces=0.9, ouvert=1, fache=True), dict(pinces=1, ouvert=0, fache=True, bob=-0.5)], 8, True),
    "pinch": ([dict(pinces=0.8, ouvert=1, avant=0.3, fache=True), dict(pinces=0.6, ouvert=0, avant=1, fache=True, dx=1.0),
               dict(pinces=0.6, ouvert=0.2, avant=0.7, fache=True, dx=0.5)], 12, False),
    "wave": ([dict(salut=-24, content=True), dict(salut=0, content=True, bob=0.3), dict(salut=24, content=True),
              dict(salut=0, content=True, bob=0.3)], 8, True),
    "bury": (_BURY, 12, False),
    "unbury": (_BURY[::-1], 12, False),
    "buried": ([dict(enterre=True), dict(enterre=True, dx=-0.8), dict(enterre=True, clin=True), dict(enterre=True, dx=0.8, haut=0.8)], 3, True),
}


def pose(enterre=False, **kw):
    return _enterre(**kw) if enterre else _crabe(**kw)


def frames(anim):
    """SVG des images d'une animation, réduites de SCALE autour des pattes."""
    tr = f"translate(16 {G}) scale({SCALE}) translate(-16 -{G})"
    return [pose(**p).svg(tr, outline_w=OUTLINE_W / SCALE) for p in ANIMS[anim][0]]


if __name__ == "__main__":
    from PIL import Image
    rangs = [[render_svg(sv, W, H, 8, PAD) for sv in frames(a)] for a in ANIMS]
    cw, ch = rangs[0][0].size
    pl = Image.new("RGBA", (4 * cw, len(rangs) * ch), (233, 207, 142, 255))
    for j, r in enumerate(rangs):
        for i, im in enumerate(r):
            pl.alpha_composite(im, (i * cw, j * ch))
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference", "v2", "crabes.png")
    pl.convert("RGB").save(fn)
    print(fn, pl.size)
