"""
spritelib — petite boîte à outils commune pour générer des sprites
en SVG (aplats + contour) et les rendre en images.

Principe : un dessin est une liste de "parts". Chaque part est une forme
SVG dont la couleur est remplacée par %F%. Les parts marquées `sil=True`
forment la silhouette, dessinée d'abord en couleur de contour avec un
trait épais : on obtient ainsi un contour extérieur propre, sans traits
parasites à l'intérieur du personnage.
"""
import io
import re

import cairosvg
from PIL import Image

OUTLINE = "#3A1E12"
OUTLINE_W = 1.8


# ------------------------------------------------------------------ formes
def _t(tr):
    return f' transform="{tr}"' if tr else ""


def ellipse(cx, cy, rx, ry, tr=""):
    return f'<ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="%F%"{_t(tr)}/>'


def circle(cx, cy, r, tr=""):
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="%F%"{_t(tr)}/>'


def rect(x, y, w, h, rx=0, tr=""):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx:.2f}" fill="%F%"{_t(tr)}/>'


def path(d, tr=""):
    return f'<path d="{d}" fill="%F%"{_t(tr)}/>'


def poly(pts, tr=""):
    p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return f'<polygon points="{p}" fill="%F%"{_t(tr)}/>'


def leg(hx, hy, fx, fy, w):
    """Patte = quadrilatère de la hanche (hx,hy) au pied (fx,fy)."""
    h = w / 2
    return poly([(hx - h, hy), (hx + h, hy), (fx + h, fy), (fx - h, fy)])


def line(d, color, w=1.0):
    """Trait décoratif (non rempli), jamais dans la silhouette."""
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


# ------------------------------------------------------------------ dessin
class Drawing:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.parts = []      # (xml, fill, sil, extra_attrs)
        self.defs = []
        self.under = []      # éléments bruts dessinés sous tout (ombres)

    def add(self, xml, fill, sil=True, clip=None, opacity=None, edge=False):
        extra = ""
        if clip:
            extra += f' clip-path="url(#{clip})"'
        if opacity is not None:
            extra += f' opacity="{opacity}"'
        if edge:
            extra += f' stroke="{OUTLINE}" stroke-width="0.9" stroke-linejoin="round"'
        self.parts.append((xml, fill, sil, extra))

    def raw(self, xml):
        self.parts.append((xml, None, False, ""))

    def clip(self, cid, shapes_xml):
        inner = "".join(s.replace('fill="%F%"', 'fill="#000"') for s in shapes_xml)
        self.defs.append(f'<clipPath id="{cid}">{inner}</clipPath>')

    def svg(self, transform="", outline=OUTLINE, outline_w=OUTLINE_W):
        sil = []
        col = []
        for xml, fill, is_sil, extra in self.parts:
            if fill is None:
                col.append(xml)
                continue
            if is_sil:
                sil.append(xml.replace('fill="%F%"',
                           f'fill="{outline}" stroke="{outline}" stroke-width="{outline_w}" stroke-linejoin="round"'))
            col.append(xml.replace('fill="%F%"', f'fill="{fill}"{extra}'))
        body = "".join(sil) + "".join(col)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}"><defs>{"".join(self.defs)}</defs>'
                f'{"".join(self.under)}<g transform="{transform}">{body}</g></svg>')


PAD = 6   # marge de sécurité (unités 1x) autour des sprites : rien ne touche le bord du cadre


def render_svg(svg, w, h, scale, pad=0):
    """Rend un SVG w x h. Avec pad > 0, le cadre est agrandi de pad unités de chaque côté
    (l'origine du sprite se décale donc de pad * scale pixels)."""
    if pad:
        svg = re.sub(r'viewBox="0 0 ([\d.]+) ([\d.]+)"',
                     lambda m: f'viewBox="{-pad} {-pad} {float(m.group(1)) + 2 * pad} {float(m.group(2)) + 2 * pad}"',
                     svg, count=1)
        svg = re.sub(r'width="[\d.]+" height="[\d.]+"', f'width="{w + 2 * pad}" height="{h + 2 * pad}"', svg, count=1)
    W, H = int((w + 2 * pad) * scale), int((h + 2 * pad) * scale)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=W, output_height=H)
    return Image.open(io.BytesIO(png)).convert("RGBA")


# ------------------------------------------------------------------ post-traitements
def flash(im, amount=0.75):
    """Version 'touchée' : teinte blanche en conservant l'alpha."""
    white = Image.new("RGBA", im.size, (255, 255, 255, 255))
    out = Image.blend(im, white, amount)
    out.putalpha(im.getchannel("A"))
    return out
