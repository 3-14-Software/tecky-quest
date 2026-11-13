"""
La plage (la côte de l'été) : ce qui sert à la quête de Zoé, la petite fille au château de sable.

- Les cinq coquillages qu'elle a perdus, enfouis dans le sable (quête : Tecky gratte, le coquillage sort, il le
  ramasse) : coquille Saint-Jacques, bulot, coque, moule, bigorneau. Posés au sol comme les objets d'items.py :
  cadre 32 x 32, origine au centre, du relief (lumière d'en haut à gauche), pas d'ovale.
- La petite butte de sable qui signale un coquillage enfoui : un bourrelet de sable d'où dépasse un bout de coquille.

    python3 plage.py      # reference/v2/plage_coquillages.png
"""
import math

from spritelib import Drawing, circle, ellipse, path, line, OUTLINE

COQUILLAGES = ["saint_jacques", "bulot", "coque", "moule", "bigorneau"]


def _dans(d, cid, forme, couleur, opacity=None):
    op = f' opacity="{opacity}"' if opacity is not None else ""
    d.raw(f'<g clip-path="url(#{cid})"{op}>' + forme.replace('fill="%F%"', f'fill="{couleur}"') + "</g>")


def saint_jacques(d):
    """Coquille Saint-Jacques : un éventail rose orangé à côtes, ses deux oreilles à la charnière."""
    eventail = path("M16,25.6 L5.4,15.4 Q5.6,6.6 16,6.2 Q26.4,6.6 26.6,15.4 Z")
    for s in (-1, 1):
        d.add(path(f"M16,25.8 L{16 + s * 5.4},22.6 L{16 + s * 5.0},26.8 Z"), "#F2B79A")
    d.clip("sj", [eventail])
    d.add(eventail, "#F7A98C")
    _dans(d, "sj", path("M15,24.6 L4.4,14.4 Q4.6,5.6 15,5.2 Q25.4,5.6 25.6,14.4 Z"), "#FCC7AE")       # (ombre en bas à droite)
    for a in (-52, -34, -17, 0, 17, 34, 52):                                                          # les côtes
        r = math.radians(a - 90)
        d.raw('<g clip-path="url(#sj)">' + line(f"M16,25.6 L{16 + 21 * math.cos(r):.2f},{25.6 + 21 * math.sin(r):.2f}", "#D97A62", 0.8) + "</g>")
    d.raw('<g clip-path="url(#sj)">' + line("M7,13.4 Q16,8.4 25,13.4 M9.6,17.6 Q16,14 22.4,17.6", "#FFE3D2", 0.9) + "</g>")
    d.add(ellipse(11.6, 10.4, 2.6, 1.2, "rotate(-30 11.6 10.4)"), "#FFFFFF", sil=False, opacity=0.6)


def bulot(d):
    """Bulot : une spirale crème et brune, la pointe en haut à droite, l'ouverture en bas."""
    corps = path("M9.4,24.6 Q4.6,19.4 8.2,13.6 Q11.6,8.6 17.4,8.8 Q20.4,6.4 24.6,4.6 Q25.0,9.6 23.2,13.0 Q26.2,19.4 21.6,24.4 Q15.6,29.0 9.4,24.6 Z")
    d.clip("bu", [corps])
    d.add(corps, "#E9D3A8")
    _dans(d, "bu", path("M8.4,23.6 Q3.6,18.4 7.2,12.6 Q10.6,7.6 16.4,7.8 Q19.4,5.4 23.6,3.6 Q24.0,8.6 22.2,12.0 Q25.2,18.4 20.6,23.4 Q14.6,28.0 8.4,23.6 Z"), "#F6E8C8")
    d.raw('<g clip-path="url(#bu)">' + line("M6,17 Q14,12.4 25,17.4 M9,10.6 Q15,8.4 23.4,11.6 M17,7 Q20.6,6.4 24.4,7.4 M7.4,22.6 Q15,18.8 24,23", "#B98A5A", 1.0) + "</g>")
    d.add(ellipse(13.4, 23.2, 4.2, 2.6, "rotate(-18 13.4 23.2)"), "#8A5A3A", sil=False, edge=True)   # l'ouverture
    d.add(ellipse(12.6, 22.6, 2.6, 1.3, "rotate(-18 12.6 22.6)"), "#F4B9A0", sil=False)
    d.add(ellipse(11.4, 13.6, 2.2, 1.1, "rotate(-35 11.4 13.6)"), "#FFFFFF", sil=False, opacity=0.6)


def coque(d):
    """Coque : une petite coquille ronde et bombée, blanche à bandes dorées."""
    rond = path("M16,25.4 Q6.0,24.6 6.6,15.6 Q7.4,7.4 16,7.2 Q24.6,7.4 25.4,15.6 Q26.0,24.6 16,25.4 Z")
    d.clip("co", [rond])
    d.add(rond, "#E8DCC0")
    _dans(d, "co", path("M15,24.4 Q5.0,23.6 5.6,14.6 Q6.4,6.4 15,6.2 Q23.6,6.4 24.4,14.6 Q25.0,23.6 15,24.4 Z"), "#FBF5E4")
    for a in (-60, -40, -20, 0, 20, 40, 60):
        r = math.radians(a - 90)
        d.raw('<g clip-path="url(#co)">' + line(f"M16,26.4 L{16 + 21 * math.cos(r):.2f},{26.4 + 21 * math.sin(r):.2f}", "#C9B58A", 0.7) + "</g>")
    d.raw('<g clip-path="url(#co)">' + line("M6,17.4 Q16,12 26,17.4", "#E2A94E", 1.6) + line("M7.6,12.2 Q16,7.6 24.4,12.2", "#E2A94E", 1.2) + "</g>")
    d.add(ellipse(11.8, 11.4, 2.4, 1.1, "rotate(-30 11.8 11.4)"), "#FFFFFF", sil=False, opacity=0.7)


def moule(d):
    """Moule : une coquille en goutte, bleu nuit, nacrée au bord, couchée en biais."""
    tr = "rotate(-32 16 16)"
    goutte = path("M16,4.6 Q23.6,10.6 22.6,19.4 Q21.6,27.0 16,27.4 Q10.4,27.0 9.4,19.4 Q8.4,10.6 16,4.6 Z", tr)
    d.clip("mo", [goutte])
    d.add(goutte, "#2F3F66")
    _dans(d, "mo", path("M15,3.6 Q22.6,9.6 21.6,18.4 Q20.6,26.0 15,26.4 Q9.4,26.0 8.4,18.4 Q7.4,9.6 15,3.6 Z", tr), "#46598A")
    d.raw('<g clip-path="url(#mo)">' + (line("M16,6 Q20.4,13 19.6,21 M16,6 Q12.4,13 12.6,22", "#8FA2CC", 0.8)
                                        + line("M10.4,21.4 Q16,26.4 21.6,21.4", "#B9C6E6", 1.2)).replace("<path", f'<path transform="{tr}"') + "</g>")
    d.add(ellipse(13.2, 12.6, 1.3, 3.0, tr), "#FFFFFF", sil=False, opacity=0.55)


def bigorneau(d):
    """Bigorneau : un petit escargot de mer rond, gris-vert, sa spirale au milieu."""
    rond = path("M8.0,20.4 Q5.6,12.2 13.0,9.0 Q21.6,6.2 25.4,13.4 Q28.0,20.4 21.4,24.4 Q13.0,27.4 8.0,20.4 Z")
    d.clip("bi", [rond])
    d.add(rond, "#7F8F78")
    _dans(d, "bi", path("M7.0,19.4 Q4.6,11.2 12.0,8.0 Q20.6,5.2 24.4,12.4 Q27.0,19.4 20.4,23.4 Q12.0,26.4 7.0,19.4 Z"), "#A3B39A")
    d.raw('<g clip-path="url(#bi)">' + line("M18.6,14.6 Q16.4,12.8 14.6,14.6 Q13.2,17.2 15.8,18.6 Q19.6,19.6 21.2,16 Q22.0,11.4 17,10.4 Q10.6,10.2 9.6,16.6", "#56664F", 1.0) + "</g>")
    d.add(ellipse(11.0, 22.0, 3.4, 2.0, "rotate(20 11 22)"), "#3F4A3A", sil=False, edge=True)        # l'ouverture
    d.add(ellipse(12.4, 11.4, 2.0, 1.0, "rotate(-30 12.4 11.4)"), "#FFFFFF", sil=False, opacity=0.6)


_DESSINS = dict(saint_jacques=saint_jacques, bulot=bulot, coque=coque, moule=moule, bigorneau=bigorneau)


def shell_frames():
    """Les cinq coquillages (dans l'ordre de COQUILLAGES) : une image chacun."""
    out = []
    for n in COQUILLAGES:
        d = Drawing(32, 32)
        _DESSINS[n](d)
        out.append(d.svg())
    return out


SABLE, SABLE_O, SABLE_C = "#E9CF8E", "#C9A960", "#FBEFC6"        # le sable remué, son ombre, ses grains au soleil
# Les sols où l'on gratte : (le tas remué, son bord, ses grains au soleil, son ombre portée, les trois tons du creux)
SOLS = {"sable": (SABLE, SABLE_O, SABLE_C, "#B9955A", ("#D9BC78", "#B9955A", "#9C7A46")),
        "terre": ("#B98F58", "#86603A", "#D9B684", "#5E7A3A", ("#A77E4C", "#86603A", "#6A4A2A"))}
# Ce qui dépasse de la butte : un bout de coquille, ou le bout d'un os doré
POINTES = {
    "coquillage": ('<path d="M14.2,15.4 L15.4,9.6 Q18.4,8.2 21.2,10.4 L21.6,15.8 Q17.8,17.4 14.2,15.4 Z" fill="#F7E6D2" stroke="#B98A6A" '
                   'stroke-width="0.7" stroke-linejoin="round"/>'
                   '<path d="M16.4,15.6 L16.8,10.2 M18.4,16 L18.6,9.6 M20.2,15.6 L20.2,10.6" stroke="#D9A98C" stroke-width="0.6" fill="none"/>'),
    "os": ('<g transform="rotate(18 18 12)"><path d="M16.2,16.4 L16.2,11.2 Q13.6,10.6 14.2,8.2 Q15.0,6.2 17.0,7.0 Q18.0,5.4 19.8,6.4 '
           'Q21.4,7.6 20.4,9.6 Q20.2,10.6 19.6,11.2 L19.6,16.4 Z" fill="#F2C14E" stroke="#A8761A" stroke-width="0.7" stroke-linejoin="round"/>'
           '<path d="M17.0,15.6 L17.0,10.6" stroke="#FFF4C4" stroke-width="0.8" stroke-linecap="round"/>'
           '<circle cx="16.0" cy="8.4" r="0.7" fill="#FFF7D6"/></g>'),
}


def mound_frames(sol="sable", pointe="coquillage"):
    """La butte d'un trésor enfoui (32 x 32, origine au centre) : trois images — le sol remué d'où dépasse un bout de
    ce qui est caché (POINTES : une coquille, un os doré), le creux laissé une fois le trésor sorti, et la butte nue
    (rien ne dépasse : le jeu ne montre le bout qu'en mode facile, à la demande de Christophe). Dans le
    sable ou dans la terre (SOLS). Pas de contour brun : c'est du sol (le même trait doux que les galets de la
    berge). Christophe a voulu les mêmes trous partout, sur le modèle de ceux des coquillages."""
    tas, bord, clair, ombre, (c0, c1, c2) = SOLS[sol]

    def svg(corps):
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">{corps}</svg>'
    def butte(dessus):
        return (f'<ellipse cx="17" cy="21.4" rx="10.6" ry="4.2" fill="{ombre}" opacity="0.5"/>'
             f'<path d="M6,21 Q7,13.6 16,13.2 Q25,13.6 26,21 Q16,24.6 6,21 Z" fill="{tas}" stroke="{bord}" stroke-width="0.8" stroke-linejoin="round"/>'
             f'<path d="M8.6,18.6 Q10.4,14.8 16,14.6 Q13,16.4 12,19.6 Z" fill="{clair}" opacity="0.9"/>'
             + dessus
             + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in
                       ((5.0, 22.6, 0.8, bord), (27.4, 21.6, 0.7, bord), (9.4, 24.2, 0.6, tas), (23.6, 24.0, 0.7, tas),
                        (22.4, 17.4, 0.5, clair), (11.4, 17.6, 0.5, clair))))
    # la butte nue (hors mode facile, rien ne dépasse) : le sol remué, fendillé là où il a été retourné
    nue = (f'<path d="M14.6,16.4 Q17.2,15.2 19.4,16.6 M17.4,18.6 Q19.6,17.8 21.6,19.0 M12.4,20.0 Q14.2,19.2 16.0,20.2" stroke="{bord}" '
           f'stroke-width="0.7" stroke-linecap="round" fill="none" opacity="0.85"/>'
           f'<circle cx="19.6" cy="14.6" r="0.9" fill="{tas}" stroke="{bord}" stroke-width="0.4"/>'
           f'<circle cx="15.2" cy="14.2" r="0.6" fill="{clair}"/>')
    creux = (f'<ellipse cx="16" cy="19.6" rx="9.6" ry="4.6" fill="{c0}"/>'
             f'<ellipse cx="16.6" cy="20.4" rx="6.8" ry="3.0" fill="{c1}"/>'
             f'<ellipse cx="17.2" cy="21.0" rx="4.4" ry="1.8" fill="{c2}"/>'
             f'<path d="M6.6,19 Q8,14.6 16,14.8 Q11.6,16 10,19.6 Z" fill="{clair}" opacity="0.8"/>'
             + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{tas}" stroke="{bord}" stroke-width="0.4"/>' for x, y, r in
                       ((5.4, 23.4, 1.3), (26.6, 22.6, 1.2), (24.0, 25.0, 0.9), (8.6, 25.2, 0.9))))
    return [svg(butte(POINTES[pointe])), svg(creux), svg(butte(nue))]


def fx_sand():
    """Gerbe de sable projetée quand Tecky gratte la plage (32 x 32, 5 images) : des grains clairs, plus nombreux
    et plus fins que les mottes de terre."""
    out = []
    grains = [(-8, 2.4, 1.1), (-5, 3.2, 0.8), (-2, 2.8, 1.2), (1, 3.6, 0.7), (3, 2.6, 1.0), (6, 3.0, 0.9), (8, 2.2, 1.1), (-6, 1.6, 0.7), (5, 1.8, 0.8)]
    for f in range(5):
        t = (f + 1) / 5
        d = Drawing(32, 32)
        for k, (vx, vy, r) in enumerate(grains):
            x, y = 16 + vx * t * 1.5, 28 - vy * 8 * t + 10 * t * t
            d.raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r * (1 - 0.3 * t):.2f}" fill="{(SABLE, SABLE_C, "#D9BC78")[k % 3]}" '
                  f'stroke="#A8864A" stroke-width="0.45"/>')                 # (un trait doux : des grains, pas des billes)
        if f < 2:
            d.raw(f'<ellipse cx="16" cy="28.5" rx="{7 - f * 2}" ry="1.6" fill="#C9A960" opacity="0.7"/>')
        out.append(d.svg())
    return out


if __name__ == "__main__":
    import os
    from PIL import Image
    from spritelib import render_svg, PAD
    ims = [render_svg(s, 32, 32, 8, PAD) for s in shell_frames() + mound_frames() + mound_frames("sable", "os") + mound_frames("terre", "os")
           + fx_sand()[1:4:2]]
    sh = Image.new("RGBA", (sum(i.width for i in ims) + 20, ims[0].height + 20), "#F2DFA8")
    x = 10
    for i in ims:
        sh.alpha_composite(i, (x, 10))
        x += i.width
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reference", "v2", "plage_coquillages.png")
    sh.save(dest)
    print(dest)
