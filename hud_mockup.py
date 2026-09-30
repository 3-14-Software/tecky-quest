"""
Maquette d'écran 1920x1080 : caméra 960x540 sur la carte (assets x2, affichée x2)
+ HUD x2 dessiné en GUI 1920x1080.

    python3 hud_mockup.py   -> out/hud_mockup.png
"""
import os

from PIL import Image, ImageDraw

import hud
import items

ROOT = os.path.dirname(os.path.abspath(__file__))
S = 2   # HUD en x2


def nine_slice(img, w, h, b):
    """Étire une image 9-slice (bord b px) à w x h."""
    W, H = img.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    xs = [(0, b, 0, b), (b, W - b, b, w - b), (W - b, W, w - b, w)]
    ys = [(0, b, 0, b), (b, H - b, b, h - b), (H - b, H, h - b, h)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            part = img.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.LANCZOS)
            out.alpha_composite(part, (dx0, dy0))
    return out


def draw_digits(canvas, digits, text, x, y, spacing=-4):
    for ch in text:
        im = digits[hud.DIGITS.index(ch)]
        bbox = im.getbbox()
        canvas.alpha_composite(im, (int(x - bbox[0]), int(y)))
        x += (bbox[2] - bbox[0]) + spacing + 6


def main():
    world = Image.open(os.path.join(ROOT, "out", "sample_map.png")).convert("RGBA")
    cam = world.crop((170, 60, 170 + 960, 60 + 540)).resize((1920, 1080), Image.LANCZOS)
    sp = hud.all_sprites(S)
    d = ImageDraw.Draw(cam)

    # --- vie : portrait + os
    cam.alpha_composite(nine_slice(sp["spr_hud_panel_dark"][0], 470, 132, 16 * S), (24, 24))
    cam.alpha_composite(sp["spr_hud_portrait_tecky"][0], (36, 42))
    for i, state in enumerate((0, 0, 0, 1, 2)):
        cam.alpha_composite(sp["spr_hud_bone"][state], (150 + i * 64, 58))

    # --- score
    cam.alpha_composite(nine_slice(sp["spr_hud_panel_dark"][0], 330, 104, 16 * S), (1920 - 24 - 330, 24))
    medal = items.item_frames("medal")[0]
    from spritelib import render_svg
    cam.alpha_composite(render_svg(medal, 32, 32, S), (1920 - 24 - 330 + 18, 44))
    draw_digits(cam, sp["spr_hud_digits"], "01250", 1920 - 24 - 330 + 100, 36)

    # --- actions (en bas à droite)
    for i, (fr, key) in enumerate(((0, 0), (2, 1))):
        x = 1920 - 230 + i * 110
        y = 1080 - 190
        cam.alpha_composite(sp["spr_hud_action"][fr], (x, y))
        if i == 1:
            cam.alpha_composite(sp["spr_hud_cooldown"][3], (x, y))
        cam.alpha_composite(sp["spr_hud_key"][key], (x, y + 86))

    # --- barre de vie de l'ennemi (roquet, 2 PV sur 3)
    bx, by = 846, 728
    cam.alpha_composite(sp["spr_hud_enemy_bar_bg"][0], (bx, by))
    fill = sp["spr_hud_enemy_bar_fill"][0]
    fill = fill.crop((0, 0, int(fill.width * 2 / 3), fill.height))
    cam.alpha_composite(fill, (bx + 4, by + 4))

    # --- "+20" en ramassant la balle
    draw_digits(cam, sp["spr_hud_digits"], "+20", 760, 250)

    # --- boîte de dialogue
    box = nine_slice(sp["spr_hud_panel"][0], 1160, 210, 16 * S)
    bx, by = 330, 1080 - 240
    cam.alpha_composite(box, (bx, by))
    cam.alpha_composite(sp["spr_hud_portrait_alice"][2], (bx + 34, by + 58))
    tag = sp["spr_hud_name_tag"][0]
    cam.alpha_composite(tag, (bx + 150, by - 16))
    f_name, f_txt = hud.font(24), hud.font(38, "Medium")
    d.text((bx + 150 + 64, by - 16 + 20), "Alice", font=f_name, fill=(255, 255, 255, 255), anchor="mm")
    d.multiline_text((bx + 150, by + 44), "Tecky ! Je suis sur la place du village,\nviens vite me retrouver !",
                     font=f_txt, fill=hud.rgb(hud.BROWN), spacing=14)
    cam.alpha_composite(sp["spr_hud_next"][1], (bx + 1160 - 64, by + 210 - 60))

    out = os.path.join(ROOT, "out", "hud_mockup.png")
    cam.convert("RGB").save(out)
    print("OK", out)


if __name__ == "__main__":
    main()
