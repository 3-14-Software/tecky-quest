"""
Lisière : ce qui borde la carte (version web), dessiné dans la marge que la caméra montre au-delà des bords
(EDGE.cam dans game.js) : des fourrés devant une rangée d'arbres (des sapins le long de la forêt ; arbres, sapins et
fourrés sont ceux de nature.py, un modèle par position) et, aux deux bouts de la grande route, l'entrée d'un tunnel
où les voitures disparaissent. Ce ne sont pas des obstacles : Tecky s'arrête au
bord de la carte (BOUND dans game.js), juste devant. Le sol de la marge (RING tuiles autour de la carte) prolonge celui
du bord : pack_web.build_map.
"""
import math
import random

import nature
from spritelib import Drawing, path, rect, line

RING = 2                      # tuiles de sol autour de la carte (la caméra en montre une)
OMBRE = '#16323C'             # teinte des ombres (celle des ombres portées de la nature : nature.OMBRE_TEINTE)


def tunnel(est=False):
    """Entrée du tunnel de la grande route au bord ouest de la carte : une butte boisée que la route traverse ; la
    bouche, cerclée de pierres, s'ouvre vers la carte et la route s'y enfonce dans le noir. Rend un nature.Sprite
    (butte, pierres, touffes : chacune avec le contour de sa teinte, comme la nature).
    Pied (56, 208) : au bas de la butte, sur le bord de la carte ; la route passe entre v 64 et v 192 (ligne du
    milieu en v 128). On n'en voit que la partie droite (u > 24) : la caméra ne déborde que d'une tuile.
    est : le tunnel du bord est, que le jeu dessine en miroir. Le soleil venant d'en haut à gauche, son flanc tourné
    vers la carte est éclairé (celui de l'ouest est dans l'ombre) : il est dessiné éclairé de la droite."""
    w, h = 72, 216
    # --- la butte : une herbe un peu plus soutenue que le pré, un flanc tourné vers la carte
    b = Drawing(w, h)
    # (pas d'ombre posée devant la bouche : c'était une bande sombre aux bords nets, juste devant la voiture qui entre,
    # « comme un cheveu sur la soupe » ; l'ombre du tunnel est le dégradé de la bouche, qui part de rien : _portail())
    b.under.append(f'<path d="M4,213 C20,220 56,220 70,214 L70,210 L4,210 Z" fill="{OMBRE}" opacity="0.3"/>')
    # (entaillée à la place de la bouche : la route, et la voiture qui entre, se voient au travers de son ombre)
    hill = path("M0,12 C10,4 26,2 40,6 C54,10 64,18 66,32 C67,40 64,46 62,50 L63,56 A20,72 0 0 0 63,200 L62,206 "
                "C66,207 68,211 64,214 L0,214 Z")
    b.clip("tunnel_hill", [hill])
    b.add(hill, "#74BF62")
    b.add(path("M50,0 C64,12 72,30 64,48 L62,52 L62,214 L53,214 C55,150 55,80 53,40 C52,24 52,10 50,0 Z"),
          "#93D67A" if est else "#57A04F", sil=False, clip="tunnel_hill")
    if not est:                                                  # le haut de la butte, face au soleil
        b.add(path("M0,14 C12,6 28,4 42,9 C32,9 16,13 0,24 Z"), "#93D67A", sil=False, clip="tunnel_hill")
    for x, y in ((14, 40), (30, 66), (22, 150), (34, 182), (10, 100), (38, 86), (36, 164), (30, 120)):   # brins d'herbe
        b.raw(line(f"M{x - 2},{y} Q{x - 1.4},{y - 2.2} {x - 1},{y - 3.4} M{x},{y} L{x + 0.2},{y - 4.2} "
                   f"M{x + 2},{y} Q{x + 1.6},{y - 2} {x + 1.4},{y - 3}", "#4C9A4C", 1.0))
    # --- la bouche : un arc de pierres ; dedans, la route s'enfonce dans le noir
    p = Drawing(w, h)
    _portail(p)
    # --- la butte est boisée, comme la lisière : des touffes en haut et en bas, par-dessus son contour
    t = Drawing(w, h)
    nature._touffes(t, [(48, 15, 8.5), (30, 9, 9.5), (60, 29, 7)], "buisson", "th")
    nature._touffes(t, [(22, 205, 8.5), (60, 208, 7), (41, 206, 9.5)], "buisson", "tb")
    return nature.Sprite([(b, "#2F6B3A", nature.TRAIT), (p, "#5E574C", nature.TRAIT),
                          (t, nature.FEUILLAGES["buisson"][3], nature.TRAIT)], w, h, (56, 208))


def _portail(p):
    """La bouche du tunnel : un arc de pierres taillées dont les deux pieds reposent sur un socle. Dedans, pas de
    route peinte : la butte est entaillée, et une ombre de plus en plus dense (un dégradé, du bord de la bouche vers
    le fond) couvre la vraie route et la voiture qui entre — elle s'enfonce dans le noir au lieu d'être coupée net
    (demande de Christophe : « de la transparence au niveau de la zone sombre »). Rien ne barre plus l'ouverture : il
    y avait là une bande de pierre, « le dessus du mur de tête », sous laquelle les voitures passaient."""
    cx, cy = 63, 128
    arc = path(f"M{cx},40 A31,88 0 0 0 {cx},216 L{cx},200 A20,72 0 0 1 {cx},56 Z")           # l'anneau seul, sans la bouche
    p.clip("tunnel_arc", [arc])
    p.add(arc, "#C2BAAB")
    p.add(rect(28, 36, 40, 62), "#DAD3C6", sil=False, clip="tunnel_arc")                    # pierres du haut, au soleil
    p.add(rect(28, 160, 40, 60), "#A49C8E", sil=False, clip="tunnel_arc")                   # celles du bas, à l'ombre
    for k in range(1, 12):                                                                 # joints des claveaux
        a = math.pi / 2 + k * math.pi / 12
        x0, y0 = cx + 20 * math.cos(a), cy + 72 * math.sin(a)
        x1, y1 = cx + 31 * math.cos(a), cy + 88 * math.sin(a)
        p.raw(line(f"M{x0:.1f},{y0:.1f} L{x1:.1f},{y1:.1f}", "#7E766B", 0.9))
    p.defs.append(f'<linearGradient id="tunnel_nuit" gradientUnits="userSpaceOnUse" x1="{cx}" y1="0" x2="{cx - 17}" y2="0">'
                  '<stop offset="0" stop-color="#17100C" stop-opacity="0"/>'
                  '<stop offset="0.45" stop-color="#17100C" stop-opacity="0.62"/>'
                  '<stop offset="1" stop-color="#17100C" stop-opacity="1"/></linearGradient>')
    p.raw(f'<path d="M{cx},56 A20,72 0 0 0 {cx},200 Z" fill="url(#tunnel_nuit)"/>')         # la nuit du tunnel
    p.raw(line(f"M{cx},56 A20,72 0 0 0 {cx},200", "#6A6257", 0.9))                         # arête de la voûte
    for y0, haut, ton in ((38, 12, "#DAD3C6"), (205, 9, "#A49C8E")):                       # les socles, aux deux pieds de l'arc
        p.add(rect(58.5, y0, 8.5, haut, 1.6), ton)
        p.raw(line(f"M59.5,{y0 + haut / 2} L66,{y0 + haut / 2}", "#7E766B", 0.8))


PORCHE = (20, 95)             # le porche : u de sa bouche, u de son pied (le milieu du bâtiment), dans son cadre


def porche():
    """Le porche du parking, sur la côte de l'été : là où la route s'arrête, les voitures entrent sous un parking
    couvert et en ressortent, comme elles le font au tunnel (« rien de neuf à dessiner pour elles »). Un bâtiment de
    béton vu d'en haut, son toit plat, son mur du sud, un grand « P » ; à gauche, la bouche, tournée vers la route :
    le même arc que celui du tunnel, et la même ombre en dégradé où la voiture s'enfonce. La route passe entre v 64
    et v 192, comme au tunnel ; pied (95, 208) : sous le mur du sud, au milieu du bâtiment."""
    w, h = 176, 220
    cx, x1 = PORCHE[0], 170
    b = Drawing(w, h)
    b.under.append(f'<path d="M{cx + 4},213 L{x1 + 3},213 L{x1 + 3},40 L{x1},40 L{x1},210 L{cx + 4},210 Z" fill="{OMBRE}" opacity="0.3"/>')
    # (le toit est entaillé à la place de la bouche : la route, et la voiture qui entre, se voient au travers de l'ombre)
    toit = f"M{cx},26 L{x1},26 L{x1},200 L{cx},200 A20,72 0 0 0 {cx},56 Z"
    b.add(path(f"M{cx},200 L{x1},200 L{x1},212 L{cx},212 Z"), "#959BA6")                    # le mur du sud
    for x in range(cx + 18, x1 - 6, 24):                                                   # ses jours
        b.add(rect(x, 203.5, 13, 5, 1), "#5E636D", sil=False)
    b.clip("porche_toit", [path(toit)])
    b.add(path(toit), "#C9CED6")
    b.add(rect(cx, 26, x1 - cx, 7), "#E2E6EC", sil=False, clip="porche_toit")              # l'acrotère, au soleil
    b.add(rect(x1 - 7, 26, 7, 172), "#AEB4BE", sil=False, clip="porche_toit")              # celui de droite, à l'ombre
    b.add(rect(cx, 193, x1 - cx, 7), "#B4BAC4", sil=False, clip="porche_toit")
    for x in (cx + 50, cx + 100):                                                          # joints des dalles
        b.raw(line(f"M{x},34 L{x},188", "#B4BAC4", 0.9))
    b.raw(line(f"M{cx + 22},111 L{x1 - 8},111", "#B4BAC4", 0.9))
    # le « P » du parking, peint sur le toit
    px0, py0, c = 78, 60, 44
    b.add(rect(px0, py0, c, c, 5), "#2F6FD1", sil=False, edge=True)
    b.add(path(f"M{px0 + 13},{py0 + 8} L{px0 + 24},{py0 + 8} Q{px0 + 34},{py0 + 8} {px0 + 34},{py0 + 17} Q{px0 + 34},{py0 + 26} {px0 + 24},{py0 + 26} "
               f"L{px0 + 19.5},{py0 + 26} L{px0 + 19.5},{py0 + 36} L{px0 + 13},{py0 + 36} Z "
               f"M{px0 + 19.5},{py0 + 13.5} L{px0 + 19.5},{py0 + 20.5} L{px0 + 24},{py0 + 20.5} Q{px0 + 27.6},{py0 + 20.5} {px0 + 27.6},{py0 + 17} "
               f"Q{px0 + 27.6},{py0 + 13.5} {px0 + 24},{py0 + 13.5} Z").replace("/>", ' fill-rule="evenodd"/>'), "#FFFFFF", sil=False)
    for x, y in ((132, 140), (144, 150)):                                                  # deux bouches d'aération
        b.add(rect(x, y, 14, 9, 1.5), "#8B93A0", sil=False, edge=True)
        b.raw(line(f"M{x + 2},{y + 3} L{x + 12},{y + 3} M{x + 2},{y + 6} L{x + 12},{y + 6}", "#5E636D", 0.7))
    # la bouche : l'arc de pierres du tunnel, en miroir (elle regarde vers l'ouest, d'où vient la route)
    p = Drawing(w, h)
    arc = path(f"M{cx},40 A31,88 0 0 1 {cx},216 L{cx},200 A20,72 0 0 0 {cx},56 Z")
    p.clip("porche_arc", [arc])
    p.add(arc, "#D3D7DE")
    p.add(rect(cx, 36, 40, 62), "#EDF0F4", sil=False, clip="porche_arc")
    p.add(rect(cx, 160, 40, 60), "#A9AFB9", sil=False, clip="porche_arc")
    for k in range(1, 12):
        a = -math.pi / 2 + k * math.pi / 12
        x0, y0 = cx + 20 * math.cos(a), 128 + 72 * math.sin(a)
        xb, yb = cx + 31 * math.cos(a), 128 + 88 * math.sin(a)
        p.raw(line(f"M{x0:.1f},{y0:.1f} L{xb:.1f},{yb:.1f}", "#8B93A0", 0.9))
    p.defs.append(f'<linearGradient id="porche_nuit" gradientUnits="userSpaceOnUse" x1="{cx}" y1="0" x2="{cx + 17}" y2="0">'
                  '<stop offset="0" stop-color="#17100C" stop-opacity="0"/>'
                  '<stop offset="0.45" stop-color="#17100C" stop-opacity="0.62"/>'
                  '<stop offset="1" stop-color="#17100C" stop-opacity="1"/></linearGradient>')
    p.raw(f'<path d="M{cx},56 A20,72 0 0 1 {cx},200 Z" fill="url(#porche_nuit)"/>')
    p.raw(line(f"M{cx},56 A20,72 0 0 1 {cx},200", "#6A6F7A", 0.9))
    return nature.Sprite([(b, "#4A4F5A", nature.TRAIT), (p, "#4A4F5A", nature.TRAIT)], w, h, (PORCHE[1], 208))


DECOR = {   # nom : fonction qui rend un nature.Sprite ; dessinés dans l'atlas sous decor/<nom>, à leur taille
    "tunnel": tunnel,
    "tunnel_est": lambda: tunnel(est=True),
    "porche": porche,
}

# encombrement à l'écran (demi-largeur, hauteur au-dessus du pied), en tuiles : rien d'important ne doit être caché
SIZE = {"thicket": (0.84, 0.95), "thicket_dark": (0.84, 0.95), "tree": (0.8, 1.75), "fir": (0.9, 2.3)}
TUNNEL_H = 6.6                # hauteur de la butte du tunnel au-dessus de son pied (tuiles)
# terrains du bord de la carte où la lisière ne pousse pas : l'eau et la route continuent au-delà ; sur la côte, la
# plage, les planches et la paroi de la falaise aussi (un arbre planté dans le sable ou sur la roche)
LIBRES = ("water", "sea", "road", "sand", "planks", "chalk", "stairs")


def decor(g, mw, mh, keep, forest, tunnels):
    """Décors de la lisière, hors de la carte : liste de (nom, x, y en tuiles, miroir). g : grille des coins de
    pack_web (l'eau et la route continuent au-delà du bord : on les laisse libres) ; keep : points (x, y) à ne jamais
    cacher (objets, personnages, panneaux…) ; forest(x, y) : au bord de la forêt (sapins) ? tunnels : (x, y du pied,
    miroir) des tunnels de la route."""
    rnd = random.Random(29)
    j = lambda a: rnd.uniform(-a, a)
    out = [("tunnel", x, y, f) for x, y, f in tunnels]

    def corner(x, y):
        return g[min(max(int(round(y)), 0), mh)][min(max(int(round(x)), 0), mw)]

    def put(n, x, y):
        if any(corner(x + dx, y + dy) in LIBRES for dx in (-0.8, 0, 0.8) for dy in (-0.8, 0, 0.8)):
            return                                  # la rivière, le ruisseau et la route passent ; la plage aussi
        if any(abs(x - tx) < 1.5 and ty - TUNNEL_H < y < ty + 0.8 for tx, ty, _ in tunnels):
            return                                  # la butte du tunnel
        hw, h = SIZE[n]
        if any(abs(kx - x) < hw + 0.3 and y - h - 0.3 < ky < y + 0.2 for kx, ky in keep):
            return
        out.append((n, round(x, 2), round(y, 2), False))

    def row(y, x0, x1, step, kind):                 # le long du bord nord ou sud (y : nombre, ou selon le décor)
        x = x0
        while x < x1:
            n = kind(x)
            put(n, x + j(0.15), (y(n) if callable(y) else y) + j(0.05))
            x += step + j(0.12)

    def column(x, y0, y1, step, kind):              # le long du bord ouest ou est
        y = y0
        while y < y1:
            n = kind(y)
            put(n, x + j(0.06), y + j(0.15))
            y += step + j(0.1)

    tall = lambda x, y: "fir" if forest(x, y) else "tree"
    low = lambda x, y: "thicket_dark" if forest(x, y) else "thicket"
    # nord : les arbres juste sur le bord, les fourrés devant (Tecky passe toujours devant eux)
    row(0.04, -0.7, mw + 0.8, 1.7, lambda x: "tree")
    row(0.16, -1.0, mw + 1.0, 1.05, lambda x: "thicket")
    # sud : les fourrés, puis les arbres ou les sapins (plus hauts, un peu plus loin), dont on voit le haut
    row(mh + 0.72, -1.0, mw + 1.0, 1.05, lambda x: low(x, mh))
    row(lambda n: mh + (2.05 if n == "fir" else 1.75), -0.6, mw + 0.8, 1.6, lambda x: tall(x, mh))
    # ouest et est : les arbres au fond, les fourrés devant (la rivière et le tunnel restent libres)
    for side, sgn in ((0, -1), (mw, 1)):
        column(side + sgn * 0.98, 0.9, mh - 0.4, 1.45, lambda y: tall(side, y))
        column(side + sgn * 0.5, 0.5, mh - 0.3, 0.74, lambda y: low(side, y))
    return out
