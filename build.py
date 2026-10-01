#!/usr/bin/env python3
"""
Construit tous les graphismes de "Tecky Quest" pour GameMaker Studio 2.

    pip install cairosvg pillow numpy   (police Fredoka fournie dans fonts/)
    python3 build.py

Sorties :
  out/x1/...  taille native (personnages 48x48, tuiles et objets 32x32)
  out/x2/...  double résolution  <- conseillé
  out/previews/*.gif   aperçus animés
  out/sample_map.png   carte d'exemple
Les sprites animés sont des strips <sprite>_stripN.png : GameMaker les découpe
automatiquement en N images à l'import.
"""
import os

from PIL import Image, ImageDraw

import alice
import decor
import enemies
import hud
import hud_mockup
import items
import music
import sample_map
import tecky
import tiles
from spritelib import render_svg, mirror, flash, save_strip, save_gif

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out")
SCALES = {"x1": 1, "x2": 2}
DIRS = ("down", "up", "right")


def _four_dirs(frames_fn, anims, folder, prefix, scale, flash_hurt=True):
    """Rend les vues down/up/right, en déduit left par miroir, écrit les strips."""
    result = {}
    for anim, dirs in anims.items():
        for view in dirs:
            imgs = [render_svg(s, 48, 48, scale) for s in frames_fn(anim, view)]
            if anim == "hurt" and flash_hurt:
                imgs[0] = flash(imgs[0])
            save_strip(imgs, folder, f"{prefix}_{anim}_{view}")
            result[(anim, view)] = imgs
            if view == "right":
                left = [mirror(i) for i in imgs]
                save_strip(left, folder, f"{prefix}_{anim}_left")
                result[(anim, "left")] = left
    return result


def build_tecky(scale, folder):
    anims = {a: dirs for a, (_, _, dirs) in tecky.ANIMS.items()}
    return _four_dirs(tecky.frames, anims, folder, "spr_tecky", scale)


def build_enemies(scale, folder):
    anims = {a: dirs for a, (_, _, dirs) in tecky.ANIMS.items() if a != "dig"}
    return {dog: _four_dirs(lambda a, v, dog=dog: enemies.frames(dog, a, v), anims, folder, f"spr_{dog}", scale)
            for dog in enemies.DOGS}


def build_alice(scale, folder):
    anims = {a: DIRS for a in alice.ANIMS}
    return _four_dirs(alice.frames, anims, folder, "spr_alice", scale)


def build_items(scale, folder):
    res = {}
    for name in items.ITEMS:
        imgs = [render_svg(s, 32, 32, scale) for s in items.item_frames(name)]
        save_strip(imgs, folder, f"spr_item_{name}")
        res[name] = imgs
    return res


def build_fx(scale, folder):
    res = {}
    for name, (fn, size, _) in items.EFFECTS.items():
        imgs = [render_svg(s, size, size, scale) for s in fn()]
        save_strip(imgs, folder, f"spr_fx_{name}")
        res[name] = imgs
    return res


def build_decor(scale, folder):
    os.makedirs(folder, exist_ok=True)
    for name, (fn, (w, h), _) in decor.DECOR.items():
        render_svg(fn().svg(), w, h, scale).save(os.path.join(folder, f"spr_decor_{name}.png"))


def build_tiles(scale, folder):
    os.makedirs(folder, exist_ok=True)
    sheet = tiles.tileset(scale)
    sheet.save(os.path.join(folder, "ts_ground.png"))
    return sheet


def build_hud(scale, folder):
    os.makedirs(folder, exist_ok=True)
    for name, frames in hud.all_sprites(scale).items():
        if len(frames) == 1:
            frames[0].save(os.path.join(folder, f"{name}.png"))
        else:
            save_strip(frames, folder, name)


def tile_legend(sheet, fn):
    """Planche annotée : index GameMaker de chaque tuile + bits de coins."""
    ts = sheet.width // tiles.COLS
    lg = sheet.copy()
    d = ImageDraw.Draw(lg)
    for i in range((sheet.height // ts) * tiles.COLS):
        x, y = (i % tiles.COLS) * ts, (i // tiles.COLS) * ts
        d.rectangle([x, y, x + ts - 1, y + ts - 1], outline=(0, 0, 0, 90))
        d.rectangle([x + 2, y + 2, x + 22, y + 14], fill=(0, 0, 0, 170))
        d.text((x + 4, y + 3), str(i), fill=(255, 255, 255, 255))
    lg.save(fn)


def main():
    prev = os.path.join(OUT, "previews")
    os.makedirs(prev, exist_ok=True)
    for tag, sc in SCALES.items():
        base = os.path.join(OUT, tag)
        t = build_tecky(sc, os.path.join(base, "tecky"))
        en = build_enemies(sc, os.path.join(base, "enemies"))
        al = build_alice(sc, os.path.join(base, "alice"))
        it = build_items(sc, os.path.join(base, "items"))
        fx = build_fx(sc, os.path.join(base, "fx"))
        build_decor(sc, os.path.join(base, "decor"))
        sheet = build_tiles(sc, os.path.join(base, "tiles"))
        build_hud(sc, os.path.join(base, "hud"))
        if tag == "x2":
            tile_legend(sheet, os.path.join(prev, "ts_ground_legend.png"))
            for anim, (_, fps, _) in tecky.ANIMS.items():
                order = [v for v in ("down", "up", "right", "left") if (anim, v) in t]
                save_gif([t[(anim, v)] for v in order], os.path.join(prev, f"tecky_{anim}.gif"), fps, zoom=1)
            for dog, res in en.items():
                save_gif([res[("walk", v)] for v in ("down", "up", "right", "left")] + [res[("bite", "right")]],
                         os.path.join(prev, f"{dog}_walk_bite.gif"), 12, zoom=1)
            save_gif([al[("walk", v)] for v in ("down", "up", "right", "left")] + [al[("happy", "down")]],
                     os.path.join(prev, "alice.gif"), 10, zoom=1)
            save_gif(list(it.values()), os.path.join(prev, "items.gif"), 8, zoom=1)
            small = {k: v for k, v in fx.items() if k != "bark"}
            save_gif(list(small.values()), os.path.join(prev, "fx.gif"), 10, zoom=1, bg=(120, 160, 110, 255))
            save_gif([fx["bark"]], os.path.join(prev, "fx_bark.gif"), 10, zoom=1, bg=(120, 160, 110, 255))
    sample_map.main()
    hud_mockup.main()
    music.render_wav(os.path.join(OUT, "audio", "music_tecky.wav"), loops=1)
    music.render_wav(os.path.join(OUT, "audio", "music_victoire.wav"), loops=1,
                     song=music.fanfare_events(), bpm=music.FANFARE_BPM, tail=1.5)
    music.render_wav(os.path.join(OUT, "audio", "music_defaite.wav"), loops=1,
                     song=music.defeat_events(), bpm=music.DEFEAT_BPM, tail=1.5)
    print("OK ->", OUT)


if __name__ == "__main__":
    main()
