"""
Planche à options : la disposition de l'écran « Options » (demande de Christophe, 14 novembre 2026 : dix lignes
empilées, c'est serré ; « deux colonnes ? ou par groupe son / image / contrôles… »).

    python3 v2/options_menu_options.py      # -> reference/v2/options_menu_options.png

Des maquettes, pas le jeu : les mêmes lignes, les mêmes couleurs, dessinées à 2/3 de l'interface (1280 x 720).
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POLICE = os.path.join(ROOT, "fonts", "Fredoka.ttf")
W, H = 1280, 720
BRUN, CREME, DOUX, OR, ROUGE = "#3A1E12", "#FFF7E6", "#E9DCC8", "#F2C14E", "#A3261F"
FOND, CASE = "#3D5560", "#2E2420"

SON = [("Musique", "niveau", 7, ""), ("Bruitages", "niveau", 8, "")]
IMAGE = [("Image", "Fluide", 0, "Plus légère sur les grands écrans"), ("Plein écran", "Non", -1, ""),
         ("Météo", "Auto", 0, "Une averse de temps en temps"), ("Texte des dialogues", "Normal", 0, "")]
JEU = [("Difficulté", "Normale", 0, "Pour les nouvelles parties"), ("Vibrations", "Oui", 0, "Manette et téléphone")]
RESET = ("Réinitialiser la progression", "rouge", 0, "Efface la partie en cours, les records et les badges")
RETOUR = ("Retour", "retour", 0, "")


def police(t, gras=600):
    f = ImageFont.truetype(POLICE, t)
    try:
        f.set_variation_by_axes([gras])
    except Exception:
        pass
    return f


def ligne(d, x, y, w, h, r, choisie=False):
    nom, val, n, note = r
    fond = CREME if choisie else CASE
    encre = BRUN if choisie else CREME
    d.rounded_rectangle([x, y, x + w, y + h], 14, fill=fond, outline=DOUX, width=2)
    cy = y + h // 2
    if val == "retour":
        d.text((x + w // 2, cy), nom, font=police(24, 700), fill=encre, anchor="mm")
        return
    if val == "rouge":
        d.rounded_rectangle([x + 6, y + 6, x + w - 6, y + h - 6], 9, fill=ROUGE)
        encre = CREME
    petit = h < 52
    if note and not petit:
        d.text((x + 26, cy - 9), nom, font=police(22), fill=encre, anchor="lm")
        d.text((x + 26, cy + 13), note, font=police(13, 500), fill="#FBDAD3" if val == "rouge" else ("#6B5A4E" if choisie else DOUX), anchor="lm")
    else:
        d.text((x + 26, cy), nom, font=police(22), fill=encre, anchor="lm")
    vx = x + w - 28
    if val == "niveau":
        pas = 23 if w > 600 else 17
        for k in range(10):
            d.rectangle([vx - 10 * pas + k * pas, cy - 10, vx - 10 * pas + k * pas + pas - 6, cy + 10],
                        fill=(OR if k < n else "#5A4E48"))
        d.text((vx - 10 * pas - 14, cy), str(n), font=police(21), fill=encre, anchor="rm")
    elif val not in ("rouge",):
        d.text((vx - (22 if n == 0 else 0), cy), val, font=police(22), fill=encre, anchor="rm")
        if n == 0:
            d.polygon([(vx, cy), (vx - 11, cy - 8), (vx - 11, cy + 8)], fill=encre)
            lg = d.textlength(val, font=police(22))
            gx = vx - 22 - lg - 16
            d.polygon([(gx - 11, cy), (gx, cy - 8), (gx, cy + 8)], fill=encre)


def titre_groupe(d, x, y, nom):
    d.text((x + 6, y), nom.upper(), font=police(17, 700), fill=OR, anchor="lm")
    lg = d.textlength(nom.upper(), font=police(17, 700))
    return lg


def cadre(nom, sous):
    im = Image.new("RGB", (W, H + 70), "#1E1A18")
    d = ImageDraw.Draw(im)
    d.text((24, 22), nom, font=police(30, 700), fill=OR, anchor="lm")
    d.text((24, 52), sous, font=police(17, 500), fill=DOUX, anchor="lm")
    d.rectangle([0, 70, W, H + 70], fill=FOND)
    d.text((W // 2, 70 + 62), "Options", font=police(46, 700), fill=CREME, anchor="mm", stroke_width=4, stroke_fill=BRUN)
    return im, d


def option_actuelle():
    im, d = cadre("Aujourd'hui", "Une colonne, dix lignes serrées")
    x, w, h, gap, y = 270, 740, 42, 8, 70 + 132
    for i, r in enumerate(SON + [JEU[0], IMAGE[3], IMAGE[0], JEU[1], IMAGE[2], IMAGE[1], RESET, RETOUR]):
        ligne(d, x, y + i * (h + gap), w, h, r, i == 3)
    return im


def option_a():
    im, d = cadre("A — Deux colonnes", "Les mêmes lignes côte à côte, plus hautes ; haut / bas descend une colonne puis l'autre")
    w, h, gap, y = 560, 62, 12, 70 + 126
    xs = (60, 660)
    gauche = SON + [JEU[0], IMAGE[3]]
    droite = [IMAGE[0], JEU[1], IMAGE[2], IMAGE[1]]
    for c, col in enumerate((gauche, droite)):
        for i, r in enumerate(col):
            ligne(d, xs[c], y + i * (h + gap), w, h, r, c == 0 and i == 3)
    yb = y + 4 * (h + gap) + 14
    ligne(d, 60, yb, 1160, h, RESET)
    ligne(d, 60, yb + h + gap, 1160, 52, RETOUR)
    return im


def option_b():
    im, d = cadre("B — Une colonne, par groupes", "Son / Image / Jeu : un intertitre par groupe ; les lignes restent serrées")
    x, w, h, gap, y = 270, 740, 38, 5, 70 + 110
    for nom, col in (("Son", SON), ("Image", IMAGE), ("Jeu", JEU)):
        titre_groupe(d, x, y + 9, nom)
        y += 22
        for r in col:
            ligne(d, x, y, w, h, r, r[0] == "Texte des dialogues")
            y += h + gap
        y += 5
    ligne(d, x, y + 4, w, h, RESET)
    ligne(d, x, y + 4 + h + gap, w, h, RETOUR)
    return im


def option_c():
    im, d = cadre("C — Deux colonnes, par groupes", "Son et Jeu à gauche, Image à droite ; lignes hautes, notes lisibles")
    w, h, gap, y0 = 560, 60, 10, 70 + 112
    for x, groupes in ((60, (("Son", SON), ("Jeu", JEU))), (660, (("Image", IMAGE),))):
        y = y0
        for nom, col in groupes:
            titre_groupe(d, x, y + 10, nom)
            y += 26
            for r in col:
                ligne(d, x, y, w, h, r, r[0] == "Texte des dialogues")
                y += h + gap
            y += 8
    yb = y0 + 2 * 26 + 4 * (h + gap) + 8 + 16
    ligne(d, 60, yb, 1160, 58, RESET)
    ligne(d, 60, yb + 58 + gap, 1160, 48, RETOUR)
    return im


def main():
    ims = [option_actuelle(), option_a(), option_b(), option_c()]
    hh = ims[0].height
    out = Image.new("RGB", (W * 2 + 30, hh * 2 + 30), "#1E1A18")
    for i, im in enumerate(ims):
        out.paste(im, ((i % 2) * (W + 30), (i // 2) * (hh + 30)))
    dest = os.path.join(ROOT, "reference", "v2", "options_menu_options.png")
    out.save(dest)
    print(dest)


if __name__ == "__main__":
    main()
