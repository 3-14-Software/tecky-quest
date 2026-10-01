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
import items
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


def _crop_face(svg, cx, cy, half, scale):
    big = render_svg(svg, 48, 48, scale * 4)
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
KEYS = ["X", "C", "E", "Z", "up", "down", "left", "right", "Esc", "Entrée"]


def key_frames(scale):
    out = []
    for k in KEYS:
        wide = len(k) > 2 and k not in ("up", "down", "left", "right")
        w = 40 if wide else 24
        d = Drawing(w, 24)
        d.add(rect(1.5, 1.5, w - 3, 21, 5), "#DADCE2")
        d.add(rect(1.5, 1.5, w - 3, 17, 5), "#FFFFFF", sil=False)
        arrows = {"up": [(12, 5), (18, 13), (6, 13)], "down": [(12, 14), (18, 6), (6, 6)],
                  "left": [(6, 10), (15, 4.5), (15, 15.5)], "right": [(18, 10), (9, 4.5), (9, 15.5)]}
        if k in arrows:
            d.add(poly(arrows[k]), "#3A3F4A", sil=False)
        im = render_svg(d.svg(), w, 24, scale)
        if k not in arrows:
            dr = ImageDraw.Draw(im)
            f = font((13 if not wide else 10) * scale)
            bb = dr.textbbox((0, 0), k, font=f)
            dr.text(((im.width - (bb[2] - bb[0])) / 2 - bb[0], (18 * scale - (bb[3] - bb[1])) / 2 - bb[1]),
                    k, font=f, fill=rgb("#3A3F4A"))
        # toutes les images d'un sprite GameMaker ont la même taille : on centre dans 40x24
        cell = Image.new("RGBA", (40 * scale, 24 * scale), (0, 0, 0, 0))
        cell.alpha_composite(im, ((cell.width - im.width) // 2, 0))
        out.append(cell)
    return out


def action_frames(scale):
    """Boutons ronds 40x40 : aboyer, mordre, gratter, lire (+ versions grisées)."""
    out = []
    for kind in ("bark", "bite", "dig", "read"):
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
    """Contenu de la pastille (20x20, rond) : barrette, chaussure, doudou (indices dans l'ordre), puis tête d'Alice."""
    n = 20 * scale
    mask = Image.new("L", (n, n), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, n - 1, n - 1], fill=255)
    out = []
    for name in items.CLUES:
        d = Drawing(32, 32)
        items.ITEMS[name][0](d)
        im = render_svg(d.svg(), 32, 32, scale).resize((int(21 * scale), int(21 * scale)), Image.LANCZOS)
        cell = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        cell.alpha_composite(im, ((n - im.width) // 2, (n - im.height) // 2))
        out.append(cell)
    face = _crop_face(alice.front(alice.A()).svg(), 24, 16.5, 12, scale).resize((n, n), Image.LANCZOS)
    out.append(Image.composite(face, Image.new("RGBA", (n, n), (0, 0, 0, 0)), Image.composite(face.getchannel("A"), mask, mask)))
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
        "spr_hud_digits": digit_frames(scale),
        "spr_hud_key": key_frames(scale),
        "spr_hud_action": action_frames(scale),
        "spr_hud_cooldown": cooldown_frames(scale),
        "spr_hud_enemy_bar_bg": [bar_bg],
        "spr_hud_enemy_bar_fill": [bar_fill],
        "spr_hud_arrow": arrow(scale),
        "spr_hud_arrow_icon": arrow_icons(scale),
        "spr_title_logo": [logo(scale)],
    }
