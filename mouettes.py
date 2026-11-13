"""
Les mouettes voleuses du village de pêcheurs (la côte de l'été) et les poissons qu'elles ont chipés à Suzanne, la
poissonnière.

- La mouette rieuse, de profil vers la droite (la vue gauche est le miroir, fait par le jeu) : cadre 32 x 32, pattes
  en (16, 28). Corps blanc, dos et ailes gris perle, pointes des ailes noires, capuchon chocolat (sa tête d'été),
  œil cerclé de blanc, bec et pattes rouges. Dessinée grande, puis réduite de `SCALE` autour de ses pattes, le
  contour compensé (comme les bêtes de critters.py) : un peu plus petite que Tecky.
  Animations (`ANIMS` : nom -> (poses, images par seconde, en boucle) ; `frames(anim)` -> SVG) :
  idle (elle se dandine), walk (elle trottine), taunt (elle nargue : tête renversée, ailes entrouvertes — une
  mouette rieuse « rit »), cry (elle crie, le bec grand ouvert : elle vient de lâcher son poisson), fly (en vol,
  les pattes repliées ; le jeu remonte le sprite et couche son ombre au sol).
  `bec(anim)` : où est le bout de son bec à chaque image, à partir de ses pattes — le jeu y pose le poisson qu'elle
  tient en travers (dessiné avant elle : le bec passe par-dessus).
- Les trois poissons (`POISSONS`, `poisson_frames()` : une image chacun, cadre 32 x 32, origine au centre) : un
  maquereau, un rouget, une dorade. Posés au sol comme les objets d'items.py : du relief (lumière d'en haut à
  gauche), pas d'ovale.

    python3 mouettes.py      # reference/v2/mouettes.png (les mouettes, les poissons, Suzanne)
"""
import math
import os

from spritelib import Drawing, circle, ellipse, path, leg, line, render_svg, PAD, OUTLINE, OUTLINE_W

W = H = 32
G = 28                 # la ligne des pattes
SCALE = 0.78
C = dict(blanc="#FFFFFF", ombre="#D5DDE6", gris="#A9B6C4", gris_c="#C6D0DB", gris_f="#7E8C9C", noir="#2B2A30",
         capuchon="#5E3F2E", capuchon_c="#7C5540", bec="#D8402F", bec_f="#A82A20", patte="#D8402F", langue="#F2A0A0")


def _dans(d, cid, forme, couleur, opacity=None):
    op = f' opacity="{opacity}"' if opacity is not None else ""
    d.raw(f'<g clip-path="url(#{cid})"{op}>' + forme.replace('fill="%F%"', f'fill="{couleur}"') + "</g>")


def _lisse(pts):
    """Chemin fermé lissé passant par le milieu des côtés (les sommets servent de points de contrôle)."""
    n = len(pts)
    mil = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    s = f"M{mil[-1][0]:.2f},{mil[-1][1]:.2f} "
    for i in range(n):
        s += f"Q{pts[i][0]:.2f},{pts[i][1]:.2f} {mil[i][0]:.2f},{mil[i][1]:.2f} "
    return path(s + "Z")


def _aile(theta, envergure, attache, corde=1.0):
    """Une aile ouverte, longue et pointue : theta = sa direction (degrés ; -90 vers le haut, 90 vers le bas),
    envergure = sa longueur apparente. Renvoie la forme et un repère A(u, v) : u de l'attache (0) à la pointe (1),
    v vers le bord de fuite (en unités du dessin)."""
    t = math.radians(theta)
    e1 = (math.cos(t) * envergure, math.sin(t) * envergure)
    e2 = (math.sin(t) * corde, -math.cos(t) * corde)
    if e2[0] > 0:
        e2 = (-e2[0], -e2[1])
    ox, oy = attache
    A = lambda u, v: (ox + e1[0] * u + e2[0] * v, oy + e1[1] * u + e2[1] * v)
    pts = [(-0.06, -1.5), (0.34, -2.6), (0.72, -1.9), (1.08, -0.2), (0.86, 1.3), (0.62, 2.6), (0.4, 3.6), (0.16, 4.3), (-0.06, 3.4)]
    return _lisse([A(u, v) for u, v in pts]), A


def _tete(d, hx, hy, ouvert=0.0, clin=False):
    """La tête : capuchon chocolat, nuque blanche, œil cerclé de blanc, bec rouge (ouvert : 0 fermé -> 1 grand
    ouvert). Renvoie le bout du bec."""
    bx, by = hx + 3.0, hy + 0.7                      # la racine du bec
    a = ouvert * 24
    if ouvert > 0.05:                                # l'intérieur du bec, la mandibule du bas
        d.add(path(f"M{bx - 0.4:.2f},{by + 0.2:.2f} L{bx + 4.6:.2f},{by + 0.9:.2f} L{bx - 0.4:.2f},{by + 1.6:.2f} Z",
                   f"rotate({a * 0.9:.1f} {bx:.2f} {by + 0.6:.2f})"), C["bec_f"])
    d.add(path(f"M{bx - 0.6:.2f},{by - 1.3:.2f} Q{bx + 3.4:.2f},{by - 1.4:.2f} {bx + 5.6:.2f},{by + 0.5:.2f} "
               f"Q{bx + 5.4:.2f},{by + 1.5:.2f} {bx + 4.4:.2f},{by + 1.1:.2f} L{bx - 0.6:.2f},{by + 1.2:.2f} Z",
               f"rotate({-a * 0.5:.1f} {bx:.2f} {by:.2f})"), C["bec"])
    tete = circle(hx, hy, 4.0)
    d.add(tete, C["blanc"])
    d.clip("tete", [tete])
    _dans(d, "tete", circle(hx + 1.5, hy - 0.5, 4.3), C["capuchon"])
    _dans(d, "tete", ellipse(hx + 0.4, hy - 2.6, 2.6, 1.1, f"rotate(-18 {hx:.2f} {hy - 2.6:.2f})"), C["capuchon_c"], 0.8)
    ex, ey = hx + 1.3, hy - 0.5
    if clin:
        d.raw(line(f"M{ex - 1.1:.2f},{ey:.2f} Q{ex:.2f},{ey + 0.9:.2f} {ex + 1.1:.2f},{ey:.2f}", C["blanc"], 0.7))
    else:
        d.add(circle(ex, ey, 1.35), C["blanc"], sil=False)
        d.add(circle(ex + 0.15, ey, 0.9), OUTLINE, sil=False)
        d.add(circle(ex + 0.45, ey - 0.3, 0.3), "#FFFFFF", sil=False)
    return bx + 4.6, by + 0.5


def _debout(bob=0.0, pas=0.0, dx=0.0, dy=0.0, ouvert=0.0, aile=0.0, saut=0.0, clin=False):
    """Posée. bob : elle s'abaisse ; pas : -1..1, la marche ; (dx, dy) : la tête avance, se lève (dy < 0) ;
    ouvert : le bec ; aile : 0 repliée -> 1 entrouverte, levée ; saut : elle décolle du sol."""
    d = Drawing(W, H)
    d.under.append(f'<ellipse cx="{16 - SCALE:.2f}" cy="{G}" rx="{(9 - saut) * SCALE:.2f}" ry="{2.2 * SCALE:.2f}" fill="#000" opacity="0.18"/>')   # (déjà à l'échelle)
    y = bob - saut
    for x, ph in ((13.4, 1), (16.6, -1)):                                                  # pattes rouges, palmes
        fx, fy = x + pas * ph * 2.4, G - 0.5 - saut - (1.2 if pas * ph < -0.5 else 0)
        d.add(leg(x, 21.5 + y, fx, fy, 1.25), C["patte"])
        d.add(path(f"M{fx - 0.7:.2f},{fy - 0.7:.2f} L{fx + 3.0:.2f},{fy + 0.3:.2f} L{fx - 0.7:.2f},{fy + 0.6:.2f} Z"), C["patte"])
    d.add(path(f"M8.4,{17.0 + y:.2f} L1.6,{19.4 + y:.2f} L8.0,{21.4 + y:.2f} Z"), C["blanc"])     # la queue
    if aile < 0.5:                                                                            # les pointes noires des ailes repliées
        d.add(path(f"M10.6,{15.6 + y:.2f} L1.0,{17.6 + y:.2f} L10.0,{19.6 + y:.2f} Z"), C["noir"])
    corps = ellipse(14.2, 18.4 + y, 8.3, 5.2, f"rotate(-9 14.2 {18.4 + y:.2f})")
    cou = ellipse(19.8 + dx * 0.5, 14.8 + y + dy * 0.4, 3.5, 5.0, f"rotate(28 {19.8 + dx * 0.5:.2f} {14.8 + y + dy * 0.4:.2f})")
    d.add(corps, C["blanc"])
    d.add(cou, C["blanc"])
    d.clip("corps", [corps, cou])
    _dans(d, "corps", ellipse(13.4, 22.8 + y, 9.0, 2.6, f"rotate(-9 13.4 {22.8 + y:.2f})"), C["ombre"])     # le ventre à l'ombre
    if aile < 0.5:                                                                            # l'aile repliée, grise
        dos = _lisse([(20.4, 14.6 + y), (15.0, 12.6 + y), (8.0, 14.6 + y), (4.6, 17.6 + y), (9.6, 19.6 + y), (16.0, 20.0 + y), (20.6, 17.8 + y)])
        d.clip("dos", [dos])
        d.add(dos, C["gris"], sil=False, edge=True)
        _dans(d, "dos", ellipse(14.0, 14.4 + y, 6.0, 1.5, f"rotate(-8 14 {14.4 + y:.2f})"), C["gris_c"], 0.9)
        d.raw(line(f"M8.6,{17.6 + y:.2f} Q13.0,{19.0 + y:.2f} 18.4,{17.6 + y:.2f}", C["gris_f"], 0.6))
    else:                                                                                     # l'aile entrouverte, levée
        forme, A = _aile(-128 + (1 - aile) * 30, 12.5, (17.4, 15.6 + y), 1.0)
        d.clip("aile", [forme])
        d.add(forme, C["gris"])
        _dans(d, "aile", _lisse([A(0.66, -3.4), A(1.3, -1.0), A(1.1, 2.6), A(0.66, 3.6)]), C["noir"])
        a, b = A(0.02, 2.4), A(0.6, 2.2)
        d.raw('<g clip-path="url(#aile)">' + line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", C["blanc"], 0.9) + "</g>")
    d.bec = _tete(d, 22.6 + dx, 10.6 + y + dy, ouvert, clin)
    return d


def _vol(theta=-70.0, envergure=13.0, bob=0.0, ouvert=0.0):
    """En vol : le corps à l'horizontale, centré vers (15, 17), la queue en éventail, les pattes repliées, les
    ailes qui battent (theta, envergure : voir _aile)."""
    d = Drawing(W, H)
    y = bob
    loin, _ = _aile(theta - 8, envergure * 0.92, (17.6, 15.2 + y), 0.9)                       # l'aile du fond, plus sombre
    d.add(loin, C["gris_f"])
    d.add(path(f"M8.4,{15.6 + y:.2f} L0.8,{14.4 + y:.2f} L1.6,{18.0 + y:.2f} L1.0,{20.4 + y:.2f} L8.6,{19.4 + y:.2f} Z"), C["blanc"])   # la queue
    d.add(path(f"M10.2,{19.4 + y:.2f} L5.4,{20.6 + y:.2f} L5.0,{22.0 + y:.2f} L7.2,{21.8 + y:.2f} L11.0,{20.4 + y:.2f} Z"), C["patte"])  # les pattes repliées
    corps = ellipse(14.4, 17.4 + y, 8.4, 4.0, f"rotate(-3 14.4 {17.4 + y:.2f})")
    cou = ellipse(21.0, 15.6 + y, 3.6, 3.4, f"rotate(20 21 {15.6 + y:.2f})")
    d.add(corps, C["blanc"])
    d.add(cou, C["blanc"])
    d.clip("corps", [corps, cou])
    _dans(d, "corps", ellipse(14.0, 20.6 + y, 9.0, 2.0), C["ombre"])
    forme, A = _aile(theta, envergure, (16.6, 15.8 + y), 1.0)
    d.clip("aile", [forme])
    d.add(forme, C["gris"], edge=True)
    _dans(d, "aile", _lisse([A(0.66, -3.4), A(1.3, -1.0), A(1.1, 2.6), A(0.66, 3.6)]), C["noir"])
    _dans(d, "aile", _lisse([A(0.0, -2.4), A(0.5, -3.2), A(0.7, -2.2), A(0.3, -1.2)]), C["gris_c"], 0.9)
    a, b = A(0.02, 2.6), A(0.62, 2.3)
    d.raw('<g clip-path="url(#aile)">' + line(f"M{a[0]:.2f},{a[1]:.2f} L{b[0]:.2f},{b[1]:.2f}", C["blanc"], 0.9) + "</g>")
    d.bec = _tete(d, 24.0, 13.4 + y, ouvert)
    return d


_BAT = [(-104, 15.0, 0.6), (-136, 9.0, 0.0), (112, 13.0, -0.7), (-150, 8.0, -0.1)]             # un battement : (theta, envergure, bob)
ANIMS = {   # nom : (poses, images par seconde, en boucle)
    "idle": ([dict(), dict(bob=0.3, dy=0.3), dict(dx=0.4, dy=-0.4), dict(bob=0.3, dy=0.3, clin=True)], 4, True),
    "walk": ([dict(pas=1, dx=0.6), dict(pas=0.2, bob=-0.4), dict(pas=-1, dx=0.6), dict(pas=-0.2, bob=-0.4)], 10, True),
    "taunt": ([dict(aile=0.7, dx=-1.0, dy=-1.6, saut=0.6), dict(aile=1, dx=-1.6, dy=-2.6, saut=1.8),
               dict(aile=0.8, dx=-1.2, dy=-2.0, saut=1.0), dict(aile=0.6, dx=-0.6, dy=-1.0)], 9, True),
    "cry": ([dict(ouvert=0.5, dy=-0.8), dict(ouvert=1, dx=0.6, dy=-1.6, aile=0.6), dict(ouvert=0.7, dx=0.4, dy=-1.2, aile=0.8),
             dict(ouvert=1, dx=0.6, dy=-1.6, aile=0.6)], 9, True),
    "fly": ([dict(vol=b) for b in _BAT], 12, True),
}


def pose(vol=None, **kw):
    if vol is not None:
        return _vol(*vol[:2], bob=vol[2], **kw)
    return _debout(**kw)


def frames(anim):
    """SVG des images d'une animation (vue de droite), réduites de SCALE autour des pattes."""
    tr = f"translate(16 {G}) scale({SCALE}) translate(-16 -{G})"
    out = []
    for p in ANIMS[anim][0]:
        d = pose(**p)
        out.append(d.svg(tr, outline_w=OUTLINE_W / SCALE))
    return out


def bec(anim):
    """Le bout du bec à chaque image, à partir des pattes (16, G), en unités du cadre."""
    return [[round((b[0] - 16) * SCALE, 2), round((b[1] - G) * SCALE, 2)] for b in (pose(**p).bec for p in ANIMS[anim][0])]


# ---------------------------------------------------------------------- les poissons de Suzanne
POISSONS = ("maquereau", "rouget", "dorade")
_P = {   # dos, flanc, ventre, reflet, nageoires, rayures
    "maquereau": dict(dos="#2F7F8E", flanc="#8FD0C8", ventre="#EEF4F2", clair="#FFFFFF", nag="#3E6F86", trait="#1F4E5E"),
    "rouget": dict(dos="#E2604E", flanc="#F59A82", ventre="#FDE3D6", clair="#FFFFFF", nag="#F2B23E", trait="#B8402F"),
    "dorade": dict(dos="#8E9BAE", flanc="#D5DCE6", ventre="#FBFBF6", clair="#FFFFFF", nag="#6E7C92", trait="#F2C230"),
}
_FORME = {   # demi-longueur, demi-hauteur du corps, queue (longueur, demi-ouverture)
    "maquereau": (10.0, 3.4, 4.0, 3.6), "rouget": (8.6, 3.9, 3.8, 3.4), "dorade": (8.4, 5.4, 3.6, 4.0),
}


def _poisson(d, nom):
    """Un poisson couché sur le flanc, la tête à droite, un peu de biais."""
    c = _P[nom]
    a, b, ql, qo = _FORME[nom]
    tr = "rotate(-14 16 16)"
    cx, cy = 16.8, 16.0
    x0 = cx - a                                                                               # la racine de la queue
    d.add(path(f"M{x0 + 1.4:.2f},{cy:.2f} L{x0 - ql:.2f},{cy - qo:.2f} Q{x0 - ql + 1.6:.2f},{cy:.2f} {x0 - ql:.2f},{cy + qo:.2f} Z", tr), c["nag"])
    d.add(path(f"M{cx - a * 0.2:.2f},{cy - b + 0.4:.2f} Q{cx + a * 0.1:.2f},{cy - b - 2.6:.2f} {cx + a * 0.45:.2f},{cy - b + 0.8:.2f} Z", tr), c["nag"])   # la dorsale
    corps = path(f"M{x0:.2f},{cy:.2f} Q{cx - a * 0.5:.2f},{cy - b * 1.25:.2f} {cx + a * 0.3:.2f},{cy - b:.2f} "
                 f"Q{cx + a * 0.9:.2f},{cy - b * 0.7:.2f} {cx + a:.2f},{cy + 0.2:.2f} "
                 f"Q{cx + a * 0.9:.2f},{cy + b * 0.8:.2f} {cx + a * 0.3:.2f},{cy + b:.2f} "
                 f"Q{cx - a * 0.5:.2f},{cy + b * 1.2:.2f} {x0:.2f},{cy:.2f} Z", tr)
    d.clip(nom, [corps])
    d.add(corps, c["flanc"])
    _dans(d, nom, ellipse(cx, cy - b * 0.95, a + 2, b * 0.75, tr), c["dos"])
    _dans(d, nom, ellipse(cx, cy + b * 1.05, a + 2, b * 0.6, tr), c["ventre"])
    if nom == "maquereau":                                                                    # ses rayures de tigre, sur le dos
        d.raw(f'<g clip-path="url(#{nom})"><g transform="{tr}">' + line(" ".join(
            f"M{cx - 7 + i * 2.3:.2f},{cy - b - 1:.2f} q0.9,{b * 0.5:.2f} -0.3,{b * 0.95:.2f}" for i in range(6)), c["trait"], 0.8) + "</g></g>")
    elif nom == "rouget":                                                                     # une bande jaune le long du flanc
        d.raw(f'<g clip-path="url(#{nom})"><g transform="{tr}">' + line(f"M{x0 + 1:.2f},{cy + 0.4:.2f} L{cx + a * 0.5:.2f},{cy + 0.4:.2f}", c["nag"], 0.9) + "</g></g>")
    else:                                                                                     # la dorade : un bandeau doré entre les yeux, des écailles
        d.raw(f'<g clip-path="url(#{nom})"><g transform="{tr}">' + line(" ".join(
            f"M{cx - 5 + i * 2.6:.2f},{cy - 1.6:.2f} q1.3,1.6 0,3.2" for i in range(4)), c["dos"], 0.6)
            + line(f"M{cx + a * 0.56:.2f},{cy - b * 0.72:.2f} q1.2,0.4 2.0,1.6", c["trait"], 1.1) + "</g></g>")
    d.raw(f'<g clip-path="url(#{nom})"><g transform="{tr}">' + line(f"M{cx + a * 0.42:.2f},{cy - b * 0.8:.2f} Q{cx + a * 0.26:.2f},{cy:.2f} {cx + a * 0.42:.2f},{cy + b * 0.8:.2f}",
                                                                   c["trait"] if nom != "dorade" else c["dos"], 0.6) + "</g></g>")   # l'ouïe
    d.add(path(f"M{cx + a * 0.2:.2f},{cy + 0.6:.2f} L{cx - a * 0.12:.2f},{cy + b * 0.75:.2f} L{cx + a * 0.3:.2f},{cy + b * 0.45:.2f} Z", tr), c["nag"], sil=False, opacity=0.9)
    ex, ey = cx + a * 0.68, cy - b * 0.22
    d.add(circle(ex, ey, 1.25, tr), "#FFFFFF", sil=False, edge=True)
    d.add(circle(ex + 0.15, ey, 0.6, tr), OUTLINE, sil=False)
    d.add(ellipse(cx - a * 0.1, cy - b * 0.55, a * 0.45, 0.7, tr), c["clair"], sil=False, opacity=0.55)


def poisson_frames():
    out = []
    for nom in POISSONS:
        d = Drawing(32, 32)
        _poisson(d, nom)
        out.append(d.svg())
    return out


if __name__ == "__main__":
    from PIL import Image
    import npcs
    rangs = [[render_svg(sv, W, H, 8, PAD) for sv in frames(a)] for a in ANIMS]
    rangs.append([render_svg(sv, 32, 32, 8, PAD) for sv in poisson_frames()])
    rangs.append([render_svg(npcs.frames("suzanne", a)[i], npcs.W, npcs.H, 8, PAD) for a, i in (("idle", 0), ("talk", 1), ("wave", 0), ("cheer", 2), ("worry", 0))])
    pl = Image.new("RGBA", (max(sum(i.width for i in r) for r in rangs), sum(r[0].height for r in rangs)), (222, 201, 140, 255))
    y = 0
    for r in rangs:
        x = 0
        for im in r:
            pl.alpha_composite(im, (x, y))
            x += im.width
        y += r[0].height
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference", "v2", "mouettes.png")
    pl.convert("RGB").save(fn)
    print(fn, pl.size)
