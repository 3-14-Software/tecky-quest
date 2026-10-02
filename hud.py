"""
HUD de Tecky Quest (à dessiner dans l'event Draw GUI).
Tailles en 1x ; build.py exporte aussi en x2.

Police : Fredoka (SIL Open Font License, voir fonts/OFL.txt), utilisée pour
les chiffres en sprite-font, les touches, le logo et la maquette.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

import alice
import farmer
import items
import npcs
import port
import tecky
from spritelib import Drawing, circle, ellipse, rect, poly, path, line, render_svg, OUTLINE

FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Fredoka.ttf")
CREAM = "#FFF7E6"
CREAM_DK = "#F1DFBF"
BROWN = "#3A1E12"


def font(size, weight="Bold"):
    f = ImageFont.truetype(FONT, int(size))
    f.set_variation_by_name(weight)
    return f


def rgb(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


# ------------------------------------------------------------------ vie : os plein / moitié / vide
def bone_frames(scale):
    out = []
    for state in ("full", "half", "empty"):
        d = Drawing(32, 32)
        tr = "rotate(-25 16 16)"
        fill = "#F3E7CF" if state != "empty" else "#6B5A4E"
        for x, y in ((9, 13.4), (9, 18.6), (23, 13.4), (23, 18.6)):
            d.add(circle(x, y, 3.2, tr), fill)
        d.add(rect(8.5, 13.3, 15, 5.4, 2, tr), fill)
        if state == "half":
            # moitié droite "vide"
            d.defs.append('<clipPath id="half"><rect x="16" y="0" width="16" height="32"/></clipPath>')
            for x, y in ((23, 13.4), (23, 18.6)):
                d.add(circle(x, y, 3.2, tr), "#6B5A4E", sil=False, clip="half")
            d.add(rect(8.5, 13.3, 15, 5.4, 2, tr), "#6B5A4E", sil=False, clip="half")
        if state != "empty":
            d.add(rect(10, 16.6, 6, 1.6, 0.8, tr) if state == "half" else rect(10, 16.6, 12, 1.6, 0.8, tr),
                  "#D9C8A2", sil=False)
        out.append(render_svg(d.svg(), 32, 32, scale))
    return out


# ------------------------------------------------------------------ panneaux 9-slice
def panel(scale, w=48, h=48, fill=CREAM, border=CREAM_DK, r=10):
    d = Drawing(w, h)
    d.raw(f'<rect x="1.5" y="2.5" width="{w - 3}" height="{h - 3}" rx="{r}" fill="#000" opacity="0.25"/>')
    d.add(rect(1.5, 1.5, w - 3, h - 4, r), fill)
    d.raw(f'<rect x="4.5" y="4.5" width="{w - 9}" height="{h - 10}" rx="{r - 3}" fill="none" '
          f'stroke="{border}" stroke-width="1.5"/>')
    return render_svg(d.svg(), w, h, scale)


def panel_dark(scale, w=48, h=48, r=12):
    d = Drawing(w, h)
    d.raw(f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{r}" fill="#2A1A12" opacity="0.72"/>')
    d.raw(f'<rect x="3" y="3" width="{w - 6}" height="{h - 6}" rx="{r - 2}" fill="none" '
          f'stroke="#FFF7E6" stroke-opacity="0.35" stroke-width="1.2"/>')
    return render_svg(d.svg(), w, h, scale)


def name_tag(scale):
    d = Drawing(64, 20)
    d.add(rect(2, 2, 60, 16, 8), "#D7332B")
    d.add(rect(4, 4, 56, 5, 3), "#E85A4F", sil=False)
    return render_svg(d.svg(), 64, 20, scale)


def next_arrow(scale):
    out = []
    for i in range(4):
        dy = [0, 1.5, 2.5, 1.5][i]
        d = Drawing(16, 16)
        d.add(poly([(3, 4 + dy), (13, 4 + dy), (8, 11 + dy)]), "#D7332B")
        out.append(render_svg(d.svg(), 16, 16, scale))
    return out


# ------------------------------------------------------------------ portraits
def _portrait(scale, face_img, bg="#8FD0F0"):
    """Cadre rond 48x48 + visage recadré."""
    S = 48 * scale
    d = Drawing(48, 48)
    d.add(circle(24, 24, 21.5), bg)
    frame = render_svg(d.svg(outline_w=3.0), 48, 48, scale)
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([4.2 * scale, 4.2 * scale, 43.8 * scale, 43.8 * scale], fill=255)
    face = face_img.resize((S, S), Image.LANCZOS)
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    layer.paste(face, (0, 0), Image.composite(face.getchannel("A"), Image.new("L", (S, S), 0), mask))
    frame.alpha_composite(layer)
    ring = Drawing(48, 48)
    ring.raw(f'<circle cx="24" cy="24" r="21.5" fill="none" stroke="{OUTLINE}" stroke-width="2.4"/>'
             f'<circle cx="24" cy="24" r="19.6" fill="none" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="1"/>')
    frame.alpha_composite(render_svg(ring.svg(), 48, 48, scale))
    return frame


def _crop_face(svg, cx, cy, half, scale, w=48, h=48):
    big = render_svg(svg, w, h, scale * 4)
    k = scale * 4
    return big.crop((int((cx - half) * k), int((cy - half) * k), int((cx + half) * k), int((cy + half) * k)))


def tecky_portrait(scale):
    states = [tecky.P(), tecky.P(blink=1), tecky.P(mouth=0.8), tecky.P(xeyes=True, ear=20)]
    out = []
    for p in states:
        svg = tecky.down(p).svg()
        out.append(_portrait(scale, _crop_face(svg, 24, 28, 12.5, scale), bg="#BFE3F5"))
    return out


def alice_portrait(scale):
    states = [alice.A(), alice.A(blink=1), alice.A(happy=True)]
    out = []
    for p in states:
        svg = alice.front(p).svg()
        out.append(_portrait(scale, _crop_face(svg, 24, 16.5, 12.5, scale), bg="#FAD4E3"))
    return out


def farmer_portrait(scale):
    """Le fermier Gaston (dialogues de la quête des poules) : normal, clignement, joyeux."""
    cx, cy, half = farmer.FACE
    return [_portrait(scale, _crop_face(farmer.front(p).svg(), cx, cy, half, scale, farmer.W, farmer.H), bg="#CFE8B0")
            for p in farmer.portrait_states()]


def npc_portrait(kind, scale):
    """Le facteur Marcel et la voisine Mamie Rose : normal, clignement, joyeux, inquiet."""
    cx, cy, half = npcs.FACES[kind]
    return [_portrait(scale, _crop_face(npcs.front(kind, p).svg(), cx, cy, half, scale, npcs.W, npcs.H), bg=npcs.PORTRAIT_BG[kind])
            for p in npcs.portrait_states(kind)]


# ------------------------------------------------------------------ texte en sprite : chiffres
DIGITS = "0123456789+-x/:%"


def digit_frames(scale, w=22, h=28, size=19):
    out = []
    f = font(size * scale)
    for ch in DIGITS:
        im = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        bb = d.textbbox((0, 0), ch, font=f, stroke_width=int(2 * scale))
        x = (im.width - (bb[2] - bb[0])) / 2 - bb[0]
        y = (im.height - (bb[3] - bb[1])) / 2 - bb[1]
        d.text((x, y + scale), ch, font=f, fill=rgb("#000000", 90), stroke_width=int(2 * scale), stroke_fill=rgb("#000000", 90))
        d.text((x, y), ch, font=f, fill=rgb(CREAM), stroke_width=int(2 * scale), stroke_fill=rgb(BROWN))
        out.append(im)
    return out


# ------------------------------------------------------------------ touches et actions
# « arrows » et « zqsd » : les quatre touches de déplacement en T renversé, dans une seule image (textes d'aide)
KEYS = ["X", "C", "E", "Z", "up", "down", "left", "right", "Échap", "Entrée", "R", "P", "M", "F", "arrows", "zqsd"]
CLUSTERS = {"arrows": ("up", "left", "down", "right"), "zqsd": ("Z", "Q", "S", "D")}
ARROWS = {"up": [(12, 5), (18, 13), (6, 13)], "down": [(12, 14), (18, 6), (6, 6)],
          "left": [(6, 10), (15, 4.5), (15, 15.5)], "right": [(18, 10), (9, 4.5), (9, 15.5)]}


def key_cluster(k, scale):
    """Quatre petites touches en T renversé (haut au milieu, puis gauche, bas, droite), cadre 40x24."""
    m, g = 1.5, 1.3                         # marge des autres touches : le contour ne touche pas le bord
    kw, kh = (40 - 2 * m - 2 * g) / 3, (24 - 2 * m - g) / 2
    spots = [(m + kw + g, m)] + [(m + i * (kw + g), m + kh + g) for i in range(3)]
    d = Drawing(40, 24)
    for x, y in spots:
        d.add(rect(x, y, kw, kh, 2.6), "#DADCE2")
        d.add(rect(x, y, kw, kh - 2, 2.6), "#FFFFFF", sil=False)
    for (x, y), c in zip(spots, CLUSTERS[k]):
        if c in ARROWS:   # la flèche d'une grande touche, réduite à la petite
            pts = [(x + (px - 12) * 0.42 + kw / 2, y + (py - 9.5) * 0.42 + (kh - 2) / 2) for px, py in ARROWS[c]]
            d.add(poly(pts), "#3A3F4A", sil=False)
    im = render_svg(d.svg(), 40, 24, scale)
    dr = ImageDraw.Draw(im)
    f = font(7.5 * scale)
    for (x, y), c in zip(spots, CLUSTERS[k]):
        if c not in ARROWS:
            bb = dr.textbbox((0, 0), c, font=f)
            dr.text(((x + kw / 2) * scale - (bb[2] - bb[0]) / 2 - bb[0], (y + (kh - 2) / 2) * scale - (bb[3] - bb[1]) / 2 - bb[1]),
                    c, font=f, fill=rgb("#3A3F4A"))
    return im


def key_frames(scale):
    out = []
    for k in KEYS:
        if k in CLUSTERS:
            out.append(key_cluster(k, scale))
            continue
        wide = len(k) > 2 and k not in ARROWS
        w = 40 if wide else 24
        d = Drawing(w, 24)
        d.add(rect(1.5, 1.5, w - 3, 21, 5), "#DADCE2")
        d.add(rect(1.5, 1.5, w - 3, 17, 5), "#FFFFFF", sil=False)
        arrows = ARROWS
        if k in arrows:
            d.add(poly(arrows[k]), "#3A3F4A", sil=False)
        im = render_svg(d.svg(), w, 24, scale)
        if k not in arrows:
            dr = ImageDraw.Draw(im)
            f = font((13 if not wide else 10.5) * scale)
            bb = dr.textbbox((0, 0), k, font=f)
            dr.text(((im.width - (bb[2] - bb[0])) / 2 - bb[0], (18 * scale - (bb[3] - bb[1])) / 2 - bb[1]),
                    k, font=f, fill=rgb("#3A3F4A"))
        # toutes les images d'un sprite GameMaker ont la même taille : on centre dans 40x24
        cell = Image.new("RGBA", (40 * scale, 24 * scale), (0, 0, 0, 0))
        cell.alpha_composite(im, ((cell.width - im.width) // 2, 0))
        out.append(cell)
    return out


# boutons de manette (disposition Xbox : A en bas, B à droite, X à gauche, Y en haut), même cadre 40x24 que les touches ;
# « croix » (croix directionnelle) et « stick » (stick gauche) sont dessinés sans lettre
PAD_BUTTONS = [("A", "#5DBB63"), ("B", "#E24B4B"), ("X", "#4A90D9"), ("Y", "#F2C14E"), ("Start", "#5E636C"),
               ("Select", "#5E636C"), ("croix", "#4A4F59"), ("stick", "#4A4F59")]


def pad_frames(scale):
    out = []
    for k, col in PAD_BUTTONS:
        if k == "croix":
            d = Drawing(24, 24)
            d.add(path("M9,1.5 H15 V9 H22.5 V15 H15 V22.5 H9 V15 H1.5 V9 H9 Z"), col)
            for pts in ([(12, 3.5), (14.6, 7), (9.4, 7)], [(12, 20.5), (14.6, 17), (9.4, 17)],
                        [(3.5, 12), (7, 9.4), (7, 14.6)], [(20.5, 12), (17, 9.4), (17, 14.6)]):
                d.add(poly(pts), "#C9CDD4", sil=False)
            d.add(circle(12, 12, 2.2), "#3B3F48", sil=False)
            im = render_svg(d.svg(), 24, 24, scale)
        elif k == "stick":
            d = Drawing(24, 24)
            d.add(circle(12, 12, 10.5), "#2F333B")
            d.add(circle(12, 11, 7.6), col, sil=False)
            d.add(circle(12, 11, 5.2), "#5C616C", sil=False)
            d.add(ellipse(10.5, 8.6, 3, 1.8), "#FFFFFF", sil=False, opacity=0.25)
            im = render_svg(d.svg(), 24, 24, scale)
        if k in ("croix", "stick"):
            cell = Image.new("RGBA", (40 * scale, 24 * scale), (0, 0, 0, 0))
            cell.alpha_composite(im, ((cell.width - im.width) // 2, 0))
            out.append(cell)
            continue
        wide = len(k) > 1
        w = 40 if wide else 24
        d = Drawing(w, 24)
        if wide:
            d.add(rect(1.5, 2.5, w - 3, 19, 9.5), col)
            d.add(rect(3, 3.5, w - 6, 13, 6.5), "#FFFFFF", sil=False, opacity=0.18)
        else:
            d.add(circle(12, 12, 10.5), col)
            d.add(ellipse(12, 9.5, 8, 6), "#FFFFFF", sil=False, opacity=0.22)
        im = render_svg(d.svg(), w, 24, scale)
        dr = ImageDraw.Draw(im)
        f = font((13 if not wide else 10.5) * scale)
        bb = dr.textbbox((0, 0), k, font=f)
        ink = BROWN if k == "Y" else "#FFFFFF"
        dr.text(((im.width - (bb[2] - bb[0])) / 2 - bb[0], (24 * scale - (bb[3] - bb[1])) / 2 - bb[1]),
                k, font=f, fill=rgb(ink))
        cell = Image.new("RGBA", (40 * scale, 24 * scale), (0, 0, 0, 0))
        cell.alpha_composite(im, ((cell.width - im.width) // 2, 0))
        out.append(cell)
    return out


def action_frames(scale):
    """Boutons ronds 40x40 : aboyer, mordre, gratter, lire, jouer (mode balade), flairer, parler (+ versions grisées)."""
    out = []
    for kind in ("bark", "bite", "dig", "read", "play", "sniff", "talk"):
        for dim in (False, True):
            d = Drawing(40, 40)
            d.add(circle(20, 20, 17.5), "#F2C14E" if not dim else "#8A8F99")
            d.add(circle(20, 18, 15), "#F7D67A" if not dim else "#A2A7B0", sil=False)
            ink = BROWN if not dim else "#5E636C"
            if kind == "bark":
                d.add(circle(13, 20, 5), ink, sil=False)
                for r in (8, 13):
                    a = math.radians(40)
                    x0, y0 = 13 + r * math.cos(-a), 20 + r * math.sin(-a)
                    x1, y1 = 13 + r * math.cos(a), 20 + r * math.sin(a)
                    d.raw(line(f"M{x0:.1f},{y0:.1f} A{r},{r} 0 0 1 {x1:.1f},{y1:.1f}", ink, 2.4))
            elif kind == "dig":
                # empreinte de patte + mottes de terre
                pad = "#FFFFFF" if not dim else "#D9DBE0"
                d.add(ellipse(17, 23.5, 5.2, 4.4), pad, sil=False, edge=True)
                for x, y in ((11.2, 17.6), (14.6, 14.2), (19.4, 14.2), (22.8, 17.6)):
                    d.add(ellipse(x, y, 1.9, 2.3), pad, sil=False, edge=True)
                for x, y, r in ((27, 27, 2.4), (30.5, 22.5, 1.8), (26, 19.5, 1.4)):
                    d.add(circle(x, y, r), "#9C6B3F" if not dim else "#7D8189", sil=False, edge=True)
                d.raw(line("M24,31 L33,31", ink, 1.6))
            elif kind == "read":
                # panneau en bois (comme le décor) avec deux lignes de texte
                d.add(rect(18.5, 20, 3, 12, 1), "#8A5A3A" if not dim else "#6E727A", sil=False, edge=True)
                d.add(poly([(7.5, 9.5), (27, 9.5), (32.5, 15.25), (27, 21), (7.5, 21)]),
                      "#C98A4B" if not dim else "#8A8F99", sil=False, edge=True)
                for x1, y in ((24, 13.4), (21, 17.1)):
                    d.raw(line(f"M11,{y} L{x1},{y}", ink, 1.6))
            elif kind == "sniff":
                # truffe de teckel et trois volutes d'odeur
                d.add(ellipse(13, 24, 7, 5.4), ink, sil=False)
                d.add(ellipse(11, 22.6, 2.2, 1.3), "#FFFFFF" if not dim else "#C9CCD2", sil=False, opacity=0.7)
                for k, (x, y) in enumerate(((22, 12), (26.5, 17.5), (21, 23))):
                    d.raw(line(f"M{x},{y + 4} q2.2,-1.6 0,-3.2 q-2.2,-1.6 0,-3.2", ink, 1.7))
            elif kind == "talk":
                # bulle de dialogue (queue en bas à gauche) et trois petits points
                bubble = ("M14,8 H26 A6,6 0 0 1 32,14 V19 A6,6 0 0 1 26,25 H19 L12,31 L13.5,25 H14 "
                          "A6,6 0 0 1 8,19 V14 A6,6 0 0 1 14,8 Z")
                d.add(path(bubble), "#FFFFFF" if not dim else "#D9DBE0", sil=False, edge=True)
                for x in (14.5, 20, 25.5):
                    d.add(circle(x, 16.5, 1.9), ink, sil=False)
            elif kind == "play":
                # cœur (comme fx/heart) : jouer avec un chien en mode balade
                heart = ("M16,23.5 C9,18.6 7,15.2 7,12.6 C7,9.9 9.1,8 11.6,8 C13.6,8 15.1,9.2 16,10.9 "
                         "C16.9,9.2 18.4,8 20.4,8 C22.9,8 25,9.9 25,12.6 C25,15.2 23,18.6 16,23.5 Z")
                tr = "translate(20 20.5) scale(1.12) translate(-16 -16)"
                d.add(path(heart, tr), "#F2607E" if not dim else "#C9CCD2", sil=False, edge=True)
                d.add(ellipse(11.8, 11.6, 2.2, 1.5, tr + " rotate(-30 11.8 11.6)"), "#FFFFFF", sil=False, opacity=0.8)
            else:
                d.add(poly([(9, 11), (31, 11), (31, 17.5), (28.8, 21.5), (26.6, 17.5), (24.4, 21.5), (22.2, 17.5),
                            (20, 21.5), (17.8, 17.5), (15.6, 21.5), (13.4, 17.5), (11.2, 21.5), (9, 17.5)]),
                      "#FFFFFF", sil=False, edge=True)
                d.add(poly([(9, 30), (31, 30), (31, 23.5), (28.8, 19.8), (26.6, 23.5), (24.4, 19.8), (22.2, 23.5),
                            (20, 19.8), (17.8, 23.5), (15.6, 19.8), (13.4, 23.5), (11.2, 19.8), (9, 23.5)]),
                      "#FFFFFF", sil=False, edge=True)
            out.append(render_svg(d.svg(), 40, 40, scale))
    return out


def cooldown_frames(scale, n=8):
    """Voile de recharge 40x40 : image 0 = plein (vient d'être utilisé), dernière = presque fini."""
    out = []
    for i in range(n):
        frac = 1 - i / n
        a0 = -math.pi / 2
        a1 = a0 + frac * 2 * math.pi
        large = 1 if frac > 0.5 else 0
        x1, y1 = 20 + 17.5 * math.cos(a1), 20 + 17.5 * math.sin(a1)
        if frac >= 0.999:
            shape = '<circle cx="20" cy="20" r="17.5" fill="#1B120C" opacity="0.6"/>'
        else:
            shape = (f'<path d="M20,20 L20,2.5 A17.5,17.5 0 {large} 1 {x1:.2f},{y1:.2f} Z" '
                     f'fill="#1B120C" opacity="0.6"/>')
        d = Drawing(40, 40)
        d.raw(shape)
        out.append(render_svg(d.svg(), 40, 40, scale))
    return out


# ------------------------------------------------------------------ jauges et indicateurs
def talk_frames(scale):
    """Bulle au-dessus d'un personnage qui a quelque chose à dire, comme dans un RPG : « ! » (il a une demande),
    « ? » (demande en cours), « … » (rien de neuf). 28x32, pointe en bas au centre (14, 28)."""
    out = []
    for glyph, col in (("!", "#E24B4B"), ("?", "#4A90D9"), ("…", "#3A3F4A")):
        d = Drawing(28, 32)
        d.add(rect(3, 3, 22, 20, 8), CREAM)
        d.add(poly([(10, 21), (18, 21), (14, 28)]), CREAM)
        im = render_svg(d.svg(), 28, 32, scale)
        dr = ImageDraw.Draw(im)
        f = font(17 * scale)
        bb = dr.textbbox((0, 0), glyph, font=f)
        dr.text(((im.width - (bb[2] - bb[0])) / 2 - bb[0], (26 * scale - (bb[3] - bb[1])) / 2 - bb[1]),
                glyph, font=f, fill=rgb(col))
        out.append(im)
    return out


def enemy_bar(scale):
    bg = Drawing(30, 10)
    bg.add(rect(2, 2, 26, 6, 3), "#2B1C14")
    fill = Drawing(24, 4)
    fill.raw('<rect x="0" y="0" width="24" height="4" rx="2" fill="#E24B4B"/>'
             '<rect x="1" y="0.6" width="22" height="1.2" rx="0.6" fill="#FF8A80"/>')
    return render_svg(bg.svg(outline_w=1.2), 30, 10, scale), render_svg(fill.svg(), 24, 4, scale)


def arrow(scale):
    """Flèche 40x40 (pointe à droite) : pointe rouge et pastille blanche, 4 images de pulsation.
    Elle tourne vers la cible ; son contenu (spr_hud_arrow_icon) se dessine à part, toujours droit."""
    out = []
    for i in range(4):
        k = 1 + 0.08 * math.sin(i / 4 * 2 * math.pi)
        d = Drawing(40, 40)
        tr = f"translate(20 20) scale({k:.3f}) translate(-20 -20)"
        d.add(poly([(23, 10), (35.5, 20), (23, 30)], tr), "#D7332B")
        d.add(circle(17, 20, 12, tr), "#FFFFFF")
        out.append(render_svg(d.svg(), 40, 40, scale))
    return out


def arrow_icons(scale):
    """Contenu de la pastille (disque de 20 dans un cadre de 22, marge comprise) : barrette, chaussure, doudou
    (indices dans l'ordre), puis tête d'Alice."""
    n, m = 20 * scale, 22 * scale
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, n - 1, n - 1], fill=255)
    out = []
    for name in items.CLUES:
        d = Drawing(32, 32)
        items.ITEMS[name][0](d)
        im = render_svg(d.svg(), 32, 32, scale).resize((int(21 * scale), int(21 * scale)), Image.LANCZOS)
        cell = Image.new("RGBA", (m, m), (0, 0, 0, 0))
        cell.alpha_composite(im, ((m - im.width) // 2, (m - im.height) // 2))
        out.append(cell)
    face = _crop_face(alice.front(alice.A()).svg(), 24, 16.5, 12, scale).resize((n, n), Image.LANCZOS)
    disc = Image.composite(face, Image.new("RGBA", (n, n), (0, 0, 0, 0)), Image.composite(face.getchannel("A"), mask, mask))
    cell = Image.new("RGBA", (m, m), (0, 0, 0, 0))
    cell.alpha_composite(disc, (scale, scale))
    out.append(cell)
    return out


# ------------------------------------------------------------------ badges (succès)
BADGES = ["aventure", "copains", "os_dores", "intact", "rapide", "poules",
          "facteur", "chat", "betes", "canards", "explorateur", "sieste", "ballons", "nestor"]
BADGE_C = (24, 20.5)      # centre de la médaille dans le cadre 48x48
_HEART = ("M16,23.5 C9,18.6 7,15.2 7,12.6 C7,9.9 9.1,8 11.6,8 C13.6,8 15.1,9.2 16,10.9 "
          "C16.9,9.2 18.4,8 20.4,8 C22.9,8 25,9.9 25,12.6 C25,15.2 23,18.6 16,23.5 Z")   # même cœur que fx/heart


def _arc(cx, cy, r, a0, a1):
    """Arc de cercle (angles en degrés, sens horaire à l'écran), pour un trait."""
    p = lambda a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
    (x0, y0), (x1, y1) = p(a0), p(a1)
    return f"M{x0:.2f},{y0:.2f} A{r},{r} 0 {1 if a1 - a0 > 180 else 0} 1 {x1:.2f},{y1:.2f}"


def _sparkle(d, x, y, s):
    """Petite étoile blanche cernée de brun (comme l'éclat des objets)."""
    pts = " ".join(f"{px:.2f},{py:.2f}" for px, py in items.star_pts(x, y, s, s * 0.36))
    d.raw(f'<polygon points="{pts}" fill="#FFFFFF" stroke="{OUTLINE}" stroke-width="0.7" stroke-linejoin="round"/>')


def _zee(x, y, s, fill, w=1.5):
    """Lettre « z » arrondie de côté s centrée en (x, y) : trait épais brun, puis trait de couleur par-dessus."""
    dd = (f"M{x - s / 2:.2f},{y - s / 2:.2f} L{x + s / 2:.2f},{y - s / 2:.2f} L{x - s / 2:.2f},{y + s / 2:.2f} "
          f"L{x + s / 2:.2f},{y + s / 2:.2f}")
    return line(dd, OUTLINE, w + 1.8) + line(dd, fill, w)


def _medal(scale, locked=False):
    """Médaille sans icône : deux rubans (rouge et bleu, comme la médaille trésor), anneau doré (gris si
    verrouillé) avec reflet et ombre, disque crème au centre."""
    cx, cy = BADGE_C
    ring, hi, lo = ("#A2A7B0", "#C9CCD2", "#8A8F99") if locked else ("#F2C14E", "#FFE9A0", "#D99A26")
    rib = ("#8A8F99", "#6E727A") if locked else ("#D7332B", "#2E6FD1")
    d = Drawing(48, 48)
    for s, col in ((-1, rib[0]), (1, rib[1])):
        x = lambda v: cx + s * v
        d.add(poly([(x(3.5), 30), (x(11), 28), (x(13.2), 44.6), (x(10.2), 42.4), (x(6.8), 45.4)]), col)
        d.add(poly([(x(7.2), 31), (x(8.6), 30.6), (x(10.4), 42.8), (x(9.3), 42.4)]), "#FFFFFF", sil=False,
              opacity=0.3)
    d.add(circle(cx, cy, 17.5), ring)
    d.raw(line(_arc(cx, cy, 15.85, 200, 265), hi, 1.4))
    d.raw(line(_arc(cx, cy, 15.85, 20, 85), lo, 1.4))
    d.add(circle(cx, cy, 14.1), lo, sil=False)
    d.add(circle(cx, cy, 13.3), "#E4E6EA" if locked else CREAM, sil=False, edge=True)
    return render_svg(d.svg(), 48, 48, scale)


# --- icônes : dessinées dans un carré 32x32 autour de (16, 16), comme les objets, puis posées sur le disque
def _ic_aventure(d):
    """Cœur rouge : Tecky a retrouvé Alice."""
    d.add(path(_HEART, "translate(16 16.4) scale(1.04) translate(-16 -15.7)"), "#E2332B")
    d.add(ellipse(11.9, 11.6, 2.5, 1.6, "rotate(-30 11.9 11.6)"), "#FFFFFF", sil=False, opacity=0.8)


def _ic_copains(d):
    """Patte de Tecky (roux) et petit cœur rose : copain de tous les chiens."""
    fur, light = tecky.PAL["fur"], tecky.PAL["light"]
    px, py = 14.2, 20.6
    d.add(ellipse(px, py, 5.8, 4.8), fur)
    for x, y in ((-6.4, -6.0), (-2.6, -9.6), (2.6, -9.6), (6.4, -6.0)):
        d.add(ellipse(px + x, py + y, 2.1, 2.6, f"rotate({x * 3:.0f} {px + x} {py + y})"), fur)
    d.add(ellipse(px - 1.6, py - 1.4, 2.2, 1.3), light, sil=False)
    d.add(path(_HEART, "translate(23.6 10.0) scale(0.48) translate(-16 -15.7)"), "#F2607E")
    d.add(ellipse(22.0, 8.6, 1.1, 0.75, "rotate(-30 22.0 8.6)"), "#FFFFFF", sil=False, opacity=0.8)


def _ic_os_dores(d):
    """Os doré (le même que le trésor) et deux éclats."""
    items.goldbone(d)
    _sparkle(d, 25.6, 7.4, 3.4)
    _sparkle(d, 6.4, 24.6, 2.2)


def _ic_intact(d):
    """Bouclier bleu frappé d'un cœur, un éclat : sans une égratignure."""
    shield = path("M16,4.2 C19.4,6.2 22.6,6.8 26,6.8 C26.2,16.6 22.8,23.8 16,28.2 C9.2,23.8 5.8,16.6 6,6.8 "
                  "C9.4,6.8 12.6,6.2 16,4.2 Z")
    d.clip("bshield", [shield])
    d.add(shield, "#4A90D9")
    d.add(rect(16, 0, 14, 30), "#3A7CC4", sil=False, clip="bshield")
    d.add(path(_HEART, "translate(16 15.8) scale(0.55) translate(-16 -15.7)"), CREAM, sil=False, edge=True)
    _sparkle(d, 24.6, 7.0, 3.2)


def _ic_rapide(d):
    """Chronomètre rouge (temps écoulé en rose) et traits de vitesse : moins de 10 minutes."""
    cx, cy = 17.8, 17.6
    d.add(rect(cx - 1.8, 4.4, 3.6, 2.6, 1), "#C9CED6")
    d.add(rect(cx - 1.1, 6.2, 2.2, 3, 0.5), "#C9CED6")
    d.add(rect(cx + 6.4, 7.0, 2.6, 3.4, 0.8, f"rotate(45 {cx + 7.7} 8.7)"), "#C9CED6")
    d.add(circle(cx, cy, 9.0), "#E24B4B")
    d.add(circle(cx, cy, 6.8), "#FFFFFF", sil=False, edge=True)
    arc = _arc(cx, cy, 6.3, -90, 0)
    d.add(path(f"M{cx},{cy} L{cx},{cy - 6.3} {arc[arc.index('A'):]} Z"), "#FFC9C2", sil=False)
    for a in range(0, 360, 90):
        r = math.radians(a)
        d.raw(line(f"M{cx + 5.0 * math.cos(r):.2f},{cy + 5.0 * math.sin(r):.2f} "
                   f"L{cx + 6.2 * math.cos(r):.2f},{cy + 6.2 * math.sin(r):.2f}", OUTLINE, 0.9))
    d.raw(line(f"M{cx},{cy} L{cx + 3.4:.2f},{cy - 2.8:.2f}", OUTLINE, 1.4))
    d.add(circle(cx, cy, 1.1), OUTLINE, sil=False)
    for y, x0, w in ((13.6, 4.6, 3.0), (17.6, 3.6, 3.6), (21.6, 4.6, 3.0)):
        d.raw(line(f"M{x0},{y} L{x0 + w},{y}", OUTLINE, 1.3))


def _ic_poules(d):
    """Poule rousse de profil (couleurs de hens.py) : les poules de Gaston."""
    body, wing = "#D9772B", "#B9601E"
    d.add(path("M9.5,19 Q2.8,15.5 4.2,7.6 Q7.6,10.4 8.6,9.4 Q9.8,13.2 12.6,15 Z"), "#A3502A")
    d.add(ellipse(15.5, 19.5, 9, 7), body)
    d.add(circle(21.2, 10.6, 5), body)
    for cx, cy, r in ((18.4, 6.2, 2.0), (21, 5.1, 2.3), (23.6, 6.2, 1.8)):
        d.add(circle(cx, cy, r), "#E2332B")
    d.add(ellipse(25, 15, 1.5, 2.2), "#E2332B")
    d.add(poly([(25.4, 9.4), (29.8, 11.2), (25.4, 13)]), "#F2C14E")
    d.add(path("M9.5,17.5 Q15,14.6 20.6,17.4 Q19,23.4 13,22.8 Q9.6,21.2 9.5,17.5 Z"), wing, sil=False, edge=True)
    d.add(circle(22, 10, 1.15), OUTLINE, sil=False)
    d.add(circle(22.35, 9.6, 0.4), "#FFFFFF", sil=False)
    d.add(circle(23.4, 12.6, 1.1), "#F28CB8", sil=False, opacity=0.7)
    d.raw(line("M13,26 L12.4,28.6 M17.6,26 L18.2,28.6", "#E8A33A", 1.4))


def _ic_facteur(d):
    """Enveloppe blanche et timbre rouge : le courrier du facteur."""
    tr = "rotate(-8 16 16)"
    d.add(rect(4.5, 8.5, 23, 16, 2, tr), "#FFFFFF")
    d.add(path("M5.2,9.4 L16,18 L26.8,9.4 Z", tr), "#E3EEF8", sil=False)
    d.raw(f'<g transform="{tr}">' + line("M5.4,9.4 L16,18 L26.6,9.4", OUTLINE, 1.0)
          + line("M5.6,23.6 L13,17 M26.4,23.6 L19,17", "#B9C6D3", 0.9) + "</g>")
    d.add(rect(19.4, 4.6, 7.2, 8.2, 0.6, "rotate(6 23 8.7)"), "#FFFFFF", sil=False, edge=True)
    d.add(rect(20.6, 5.8, 4.8, 5.8, 0.4, "rotate(6 23 8.7)"), "#E24B4B", sil=False)
    d.add(path(_HEART, "translate(23 8.7) rotate(6) scale(0.17) translate(-16 -15.7)"), "#FFFFFF", sil=False)


def _ic_chat(d):
    """Tête du chat blanc de la voisine (couleurs de critters.py) : taches grises, yeux bleus, collier rose à grelot."""
    fur, patch, ear, eye, collar = "#FBF8F3", "#9D9BA8", "#F4A3A8", "#6DB8EA", "#F2729E"
    d.add(poly([(6.2, 12.6), (7.6, 3.2), (14.4, 8.4)]), patch)          # oreille gauche grise
    d.add(poly([(25.8, 12.6), (24.4, 3.2), (17.6, 8.4)]), fur)
    head = ellipse(16, 15.6, 10.2, 8.6)
    d.clip("bcat", [head])
    d.add(head, fur)
    d.add(poly([(8.4, 10.6), (8.8, 6.0), (12.4, 8.8)]), ear, sil=False)
    d.add(poly([(23.6, 10.6), (23.2, 6.0), (19.6, 8.8)]), ear, sil=False)
    d.add(ellipse(10.2, 11.6, 5.6, 4.8, "rotate(-20 10.2 11.6)"), patch, sil=False, clip="bcat")
    d.add(ellipse(23.8, 20.6, 3.4, 2.6), patch, sil=False, clip="bcat")
    for x in (11.6, 20.4):
        d.add(ellipse(x, 15.2, 1.9, 2.2), eye, sil=False, edge=True)
        d.add(ellipse(x, 15.4, 0.8, 1.5), OUTLINE, sil=False)
        d.add(circle(x + 0.6, 14.4, 0.5), "#FFFFFF", sil=False)
    d.add(poly([(14.6, 18.4), (17.4, 18.4), (16, 19.8)]), "#EE97A8", sil=False, edge=True)
    d.raw(line("M16,19.8 Q15.2,21.4 13.8,20.8 M16,19.8 Q16.8,21.4 18.2,20.8", OUTLINE, 0.8))
    d.raw(line("M3.2,17.6 L9,18.4 M3.6,21 L9,19.8 M28.8,17.6 L23,18.4 M28.4,21 L23,19.8", "#ABA49B", 0.7))
    d.add(path("M8.6,22.2 Q16,26.2 23.4,22.2 L23.8,24.6 Q16,28.8 8.2,24.6 Z"), collar, sil=False, edge=True)
    d.add(circle(16, 27.4, 2.2), "#F2C14E")
    d.raw(line("M14.6,27.6 L17.4,27.6", OUTLINE, 0.7))


def _ic_betes(d):
    """Écureuil roux assis, queue en panache, un gland entre les pattes : toutes les petites bêtes surprises."""
    fur, dark, belly = "#C8642E", "#9E4A22", "#F6DDB8"
    for x, y, r in ((9.6, 25.2, 3.4), (6.8, 21.4, 4.0), (5.8, 16.2, 4.4), (7, 11, 4.4), (9.4, 6.8, 3.8),
                    (13, 4.8, 3.0)):
        d.add(circle(x, y, r), fur)
    d.raw(line("M8.6,22 Q6.6,16 8.4,10.6 Q10,7.6 12.6,6.4", dark, 1.0))
    d.add(ellipse(17.4, 21.6, 5.4, 6.6, "rotate(10 17.4 21.6)"), fur)
    d.add(ellipse(20, 22.6, 2.8, 5, "rotate(10 17.4 21.6)"), belly, sil=False)
    d.add(ellipse(18.8, 28, 3.8, 1.3), fur)
    d.add(ellipse(14.6, 24.8, 4.2, 3.2, "rotate(-28 14.6 24.8)"), fur, sil=False, edge=True)
    d.add(poly([(17.4, 11.8), (18.6, 10.6), (17.2, 7.4)]), dark)
    d.add(circle(20.6, 13.4, 4.8), fur)
    d.add(ellipse(23.6, 14.8, 3.4, 2.7), fur)
    d.add(ellipse(23, 16.4, 2.6, 1.5), belly, sil=False)
    d.add(poly([(17.8, 10.6), (21.6, 9.4), (18.6, 4.8)]), fur)
    d.add(circle(22.4, 12.8, 1.8), belly, sil=False)
    d.add(circle(22.6, 12.8, 1.25), OUTLINE, sil=False)
    d.add(circle(23.0, 12.3, 0.45), "#FFFFFF", sil=False)
    d.add(ellipse(26.8, 14.4, 0.9, 0.75), OUTLINE, sil=False)
    d.add(ellipse(24.4, 21.4, 2.2, 2.5), "#D9A15E", sil=False, edge=True)
    d.add(path("M21.8,20.6 Q24.4,17.2 27,20.6 Z"), "#8A5A2E", sil=False, edge=True)
    d.add(ellipse(22.4, 21.4, 1.2, 1.0), fur, sil=False, edge=True)


def _ic_canards(d):
    """Colvert qui nage, de profil (couleurs de ducks.py) : tête verte, collier blanc, poitrine brun-roux."""
    green, sheen, bill, chest = "#2E8A55", "#5BBB84", "#F2CB45", "#A9552F"
    body = path("M4.2,17.4 Q6.6,15.6 9,17 Q14,14.8 20.6,15.4 Q28.2,16.4 27.6,21.6 Q26.4,26.6 16.4,26.6 "
                "Q7.6,26.6 5.6,22 Q4.6,19.8 4.2,17.4 Z")
    d.clip("bduck", [body])
    d.add(rect(16.6, 6.6, 7.4, 12, 3.4, "rotate(8 20.3 12.6)"), green)
    d.add(body, "#DCD7CD")
    d.add(ellipse(24.2, 20, 5.4, 5.6), chest, sil=False, clip="bduck")
    d.add(path("M8.6,18.6 Q14,16.6 19.4,18.8 Q18.4,23.2 12.6,23.2 Q9,22.4 8.6,18.6 Z"), "#AFA392", sil=False, edge=True)
    d.add(path("M4.2,17.4 Q6.6,15.6 9,17 Q7.6,19.6 5.6,22 Q4.6,19.8 4.2,17.4 Z"), "#2B2A30", sil=False)
    d.add(circle(21.4, 7.8, 5.4), green)
    d.add(path("M25.6,6.8 Q30.4,6.6 31.2,9.4 Q30.2,11 26,10.4 Z"), bill)
    d.add(rect(17.4, 13.0, 8.2, 2.2, 1.1, "rotate(8 21.5 14.1)"), "#FFFFFF", sil=False, edge=True)
    d.add(path("M18,4.4 Q21,2.8 24.4,4.2 Q21.2,4.6 19.4,6.6 Z"), sheen, sil=False)
    d.add(circle(23.2, 6.8, 1.15), OUTLINE, sil=False)
    d.add(circle(23.55, 6.4, 0.4), "#FFFFFF", sil=False)
    d.raw(line("M9.4,28.6 Q11.6,27.4 13.8,28.6 Q16,29.8 18.2,28.6 Q20.4,27.4 22.6,28.6", "#4A90D9", 1.2))


def _ic_explorateur(d):
    """Boussole verte, aiguille rouge (nord) et grise : toute la carte explorée."""
    cx, cy = 16, 17
    d.add(circle(cx, 5.4, 2.6), "#C9CED6")
    d.add(circle(cx, 5.4, 1.1), CREAM, sil=False, edge=True)
    d.add(circle(cx, cy, 10.2), "#5DBB63")
    d.add(circle(cx, cy, 7.8), "#FFFFFF", sil=False, edge=True)
    for a in range(0, 360, 90):
        r = math.radians(a)
        d.raw(line(f"M{cx + 6.0 * math.cos(r):.2f},{cy + 6.0 * math.sin(r):.2f} "
                   f"L{cx + 7.2 * math.cos(r):.2f},{cy + 7.2 * math.sin(r):.2f}", OUTLINE, 0.9))
    tr = f"rotate(35 {cx} {cy})"
    d.add(poly([(cx, cy - 6.6), (cx + 2.3, cy), (cx - 2.3, cy)], tr), "#E2332B", sil=False, edge=True)
    d.add(poly([(cx, cy + 6.6), (cx + 2.3, cy), (cx - 2.3, cy)], tr), "#C9CED6", sil=False, edge=True)
    d.add(circle(cx, cy, 1.2), "#F2C14E", sil=False, edge=True)


def _ic_sieste(d):
    """Croissant de lune (deux arcs entre les mêmes pointes) et deux « z » : Tecky a fait la sieste."""
    d.add(path("M14.6,6.2 A10.4,10.4 0 1 0 24.6,21.4 A8.2,8.2 0 0 1 14.6,6.2 Z"), "#F7D67A")
    d.add(path("M11.8,10.2 A7.6,7.6 0 0 0 9.8,22"), "#FFF1B8", sil=False)
    d.add(circle(11.6, 22.4, 1.15), "#E0B84A", sil=False)
    d.add(circle(8.8, 15.8, 0.85), "#E0B84A", sil=False)
    d.raw(_zee(21.2, 11.8, 4.4, "#4A90D9", 1.6))
    d.raw(_zee(25.2, 7.4, 2.8, "#4A90D9", 1.3))


def _ic_ballons(d):
    """Un ballon de plage de Léon."""
    port.beach_ball(d, 16, 16, 11.5, port.BALL_COLORS[0])


def _ic_nestor(d):
    """Le canard en caoutchouc de Nestor."""
    port.rubber_duck(d, 0.5, -1)


BADGE_ICONS = {   # nom : (dessin, échelle, point de l'icône posé au centre du disque)
    "aventure": (_ic_aventure, 0.95, 16, 16), "copains": (_ic_copains, 0.92, 16, 16),
    "os_dores": (_ic_os_dores, 0.95, 16, 16), "intact": (_ic_intact, 0.92, 16, 16),
    "rapide": (_ic_rapide, 0.9, 16, 16), "poules": (_ic_poules, 0.8, 16.6, 16.6),
    "facteur": (_ic_facteur, 0.86, 16, 16.4), "chat": (_ic_chat, 0.9, 16, 16),
    "betes": (_ic_betes, 0.82, 15.2, 16.4), "canards": (_ic_canards, 0.84, 17, 16.4),
    "explorateur": (_ic_explorateur, 0.9, 16, 16), "sieste": (_ic_sieste, 0.86, 16.4, 15.8),
    "ballons": (_ic_ballons, 0.95, 16, 16), "nestor": (_ic_nestor, 0.9, 15.8, 17),
}


def badge_frames(scale):
    """Badges de succès : médailles rondes 48x48 (même cadre, origine (0, 0), rien ne touche le bord), une image
    par badge dans l'ordre de BADGES, puis une de plus à la fin : le badge verrouillé (médaille grise, « ? »).
    L'icône est un calque à part (son propre contour brun), posé au centre du disque crème."""
    cx, cy = BADGE_C
    base = _medal(scale)
    out = []
    for name in BADGES:
        fn, k, ix, iy = BADGE_ICONS[name]
        d = Drawing(48, 48)
        fn(d)
        im = base.copy()
        im.alpha_composite(render_svg(d.svg(f"translate({cx} {cy}) scale({k}) translate({-ix} {-iy})"), 48, 48, scale))
        out.append(im)
    d = Drawing(48, 48)
    q = (f"M{cx - 3.6:.2f},{cy - 3.4:.2f} Q{cx - 3.6:.2f},{cy - 7.6:.2f} {cx:.2f},{cy - 7.6:.2f} "
         f"Q{cx + 3.8:.2f},{cy - 7.6:.2f} {cx + 3.8:.2f},{cy - 4:.2f} Q{cx + 3.8:.2f},{cy - 1.4:.2f} {cx:.2f},{cy + 0.4:.2f} "
         f"L{cx:.2f},{cy + 2.4:.2f}")
    d.raw(line(q, OUTLINE, 5.0) + line(q, "#FFFFFF", 2.8))
    d.add(circle(cx, cy + 6.6, 1.9), "#FFFFFF")
    im = _medal(scale, locked=True)
    im.alpha_composite(render_svg(d.svg(), 48, 48, scale))
    out.append(im)
    return out


# ------------------------------------------------------------------ logo
def logo(scale):
    W, H = 240, 96
    im = Image.new("RGBA", (W * scale, H * scale), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f1, f2 = font(46 * scale), font(26 * scale, "SemiBold")
    for txt, f, y, fill in (("TECKY", f1, 4, "#D7332B"), ("QUEST", f2, 56, "#F2C14E")):
        bb = d.textbbox((0, 0), txt, font=f, stroke_width=int(4 * scale))
        x = (im.width - (bb[2] - bb[0])) / 2 - bb[0]
        d.text((x, (y + 3) * scale), txt, font=f, fill=rgb("#000000", 80), stroke_width=int(4 * scale), stroke_fill=rgb("#000000", 80))
        d.text((x, y * scale), txt, font=f, fill=rgb(fill), stroke_width=int(4 * scale), stroke_fill=rgb(BROWN))
    # os décoratif
    bone = items.bone
    bd = Drawing(32, 32)
    bone(bd)
    b = render_svg(bd.svg(), 32, 32, scale)
    im.alpha_composite(b, (int(14 * scale), int(58 * scale)))
    im.alpha_composite(b.transpose(Image.FLIP_LEFT_RIGHT), (int((W - 46) * scale), int(58 * scale)))
    return im


def all_sprites(scale):
    """nom -> liste d'images (strips) ou image seule."""
    bar_bg, bar_fill = enemy_bar(scale)
    return {
        "spr_hud_bone": bone_frames(scale),
        "spr_hud_panel": [panel(scale)],
        "spr_hud_panel_dark": [panel_dark(scale)],
        "spr_hud_name_tag": [name_tag(scale)],
        "spr_hud_next": next_arrow(scale),
        "spr_hud_portrait_tecky": tecky_portrait(scale),
        "spr_hud_portrait_alice": alice_portrait(scale),
        "spr_hud_portrait_farmer": farmer_portrait(scale),
        "spr_hud_portrait_postman": npc_portrait("postman", scale),
        "spr_hud_portrait_neighbor": npc_portrait("neighbor", scale),
        "spr_hud_portrait_leon": npc_portrait("leon", scale),
        "spr_hud_portrait_nestor": npc_portrait("nestor", scale),
        "spr_hud_digits": digit_frames(scale),
        "spr_hud_key": key_frames(scale),
        "spr_hud_pad": pad_frames(scale),
        "spr_hud_action": action_frames(scale),
        "spr_hud_cooldown": cooldown_frames(scale),
        "spr_hud_talk": talk_frames(scale),
        "spr_hud_enemy_bar_bg": [bar_bg],
        "spr_hud_enemy_bar_fill": [bar_fill],
        "spr_hud_arrow": arrow(scale),
        "spr_hud_arrow_icon": arrow_icons(scale),
        "spr_hud_badge": badge_frames(scale),
        "spr_title_logo": [logo(scale)],
    }
