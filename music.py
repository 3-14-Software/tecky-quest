#!/usr/bin/env python3
"""
« Promenade de Tecky » — morceau chiptune original, en boucle ; fanfare de victoire et musique de défaite.

Une seule source pour les deux versions :
  - events() -> liste de notes utilisée par le jeu web (WebAudio)
  - render_wav() -> fichier WAV pour GameMaker (out/audio/music_tecky.wav)

Canaux, façon console 8 bits :
  lead  : onde carrée 25 %      (mélodie)
  arp   : onde carrée 12,5 %    (arpèges rapides, discrets)
  bass  : triangle              (basse sautillante)
  drums : bruit + sinus         (grosse caisse, caisse claire, charleston)

    python3 music.py   -> out/audio/music_tecky.wav
"""
import math
import os
import struct

import numpy as np

BPM = 140
STEPS_PER_BAR = 16          # doubles-croches

# Grille d'accords, une mesure chacun (A : couplet, B : pont)
CHORDS = ["C", "Am", "F", "G", "C", "Am", "F", "G",          # A : thème
          "F", "G", "Em", "Am", "F", "G", "C", "C",          # B : pont
          "Am", "Em", "F", "C", "Dm", "Am", "G", "G",        # C : passage plus doux
          "C", "Am", "F", "G", "C", "Am", "Dm", "G"]         # D : reprise du thème
CHORD_NOTES = {"C": ["C", "E", "G"], "Am": ["A", "C", "E"], "F": ["F", "A", "C"],
               "G": ["G", "B", "D"], "Em": ["E", "G", "B"], "Dm": ["D", "F", "A"], "E": ["E", "G#", "B"]}
ROOT_BASS = {"C": "C2", "Am": "A1", "F": "F1", "G": "G1", "Em": "E2", "Dm": "D2", "E": "E2"}

# Mélodie en croches : note, "-" = tenue, "." = silence
LEAD = """
E5 G5 C6 G5 E5 -  D5 E5 | C5 -  A4 C5 E5 -  D5 C5 | A4 C5 F5 A5 G5 F5 E5 C5 | D5 -  B4 D5 G5 -  .  .
E5 G5 C6 G5 E5 G5 A5 G5 | E5 -  C5 E5 A5 -  G5 E5 | F5 E5 D5 C5 A4 C5 F5 A5 | G5 -  F5 -  D5 -  B4 -
A5 -  A5 G5 F5 -  A5 -  | B5 -  B5 A5 G5 -  B5 -  | G5 -  E5 G5 B5 -  A5 G5 | A5 -  E5 -  C5 -  E5 -
F5 A5 C6 A5 F5 A5 C6 D6 | B5 -  G5 -  D5 -  G5 A5 | C6 -  G5 E5 C5 E5 G5 -  | C6 -  -  -  .  .  G5 -
E5 -  E5 D5 C5 -  A4 C5 | B4 -  B4 C5 D5 -  E5 G5 | A5 -  G5 F5 E5 -  F5 A5 | G5 -  E5 -  C5 -  D5 E5
F5 -  F5 E5 D5 -  F5 A5 | E5 -  C5 E5 A5 -  G5 E5 | D5 G5 B5 G5 D5 G5 B5 D6 | B5 -  A5 -  G5 -  .  .
E5 G5 C6 G5 E5 -  D5 E5 | C5 -  A4 C5 E5 -  D5 C5 | A4 C5 F5 A5 G5 F5 E5 C5 | D5 -  B4 D5 G5 -  .  .
E5 G5 C6 G5 E5 G5 A5 G5 | E5 -  C5 E5 A5 -  G5 E5 | F5 E5 D5 C5 D5 F5 A5 C6 | B5 -  A5 -  G5 -  D5 -
"""

NOTE_IDX = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(name):
    n, octv = name[:-1], int(name[-1])
    return 12 * (octv + 1) + NOTE_IDX[n[0]] + (1 if "#" in n else 0)


def freq(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# Variations du thème selon la zone : même mélodie, mêmes accords, même grille de phrases (elles se superposent pendant
# le fondu enchaîné du jeu, qui fait glisser le tempo de l'une à l'autre pendant la mesure de fondu).
STYLES = {
    "base": dict(bpm=140),          # niche, campagne : le thème tel quel (et le WAV GameMaker)
    "village": dict(bpm=152),       # plus entraînant : basse syncopée, charleston en doubles-croches, notes piquées
    "ferme": dict(bpm=136),         # country : basse alternée fondamentale-quinte, rouleaux de banjo, notes glissées
    "foret": dict(bpm=108),         # calme : basse tenue, arpèges lents, presque pas de batterie, écho sur la mélodie
    "parc": dict(bpm=126),          # boîte à musique : mélodie à l'octave, notes courtes, pas de batterie
    "industrie": dict(bpm=140),     # mécanique : basse martelée, grosse caisse à chaque temps, cliquetis
    "berceuse": dict(bpm=84),       # la fin, la nuit à la niche : lente, mélodie à l'octave tenue, pas de batterie
}


def _melody():
    """Notes de la mélodie : (pas, midi, durée en pas)."""
    toks = LEAD.replace("|", " ").split()
    assert len(toks) == len(CHORDS) * 8, len(toks)
    out, i = [], 0
    while i < len(toks):
        if toks[i] in "-.":
            i += 1
            continue
        j = i + 1
        while j < len(toks) and toks[j] == "-":
            j += 1
        out.append((i * 2, midi(toks[i]), (j - i) * 2))
        i = j
    return out


def _lead(style, st, n, ln, total):
    if style == "village":              # notes brèves piquées
        return [[st, "lead", n, ln - (0.7 if ln <= 2 else 0.3), 1.0]]
    if style == "ferme":                # notes longues glissées depuis un ton en dessous (6e champ)
        return [[st, "lead", n, ln - 0.3, 1.0] + ([-2] if ln >= 4 else [])]
    if style == "foret":                # liée, avec un écho une croche pointée plus tard
        return [[st, "lead", n, ln - 0.1, 1.0], [(st + 3) % total, "lead", n, max(0.8, min(ln, 4) - 0.3), 0.28]]
    if style == "parc":                 # à l'octave, notes courtes de boîte à musique
        return [[st, "lead", n + 12, min(ln - 0.3, 3.2), 0.9]]
    if style == "berceuse":             # à l'octave, notes tenues, douce
        return [[st, "lead", n + 12, min(ln - 0.2, 5.5), 0.75]]
    return [[st, "lead", n, ln - 0.3, 1.0]]


def _bass(style, bar, sec):
    """(pas dans la mesure, intervalle depuis la fondamentale, durée, volume)."""
    if style == "village":
        last = (10 if bar % 2 else 12) if sec == 3 else 12
        return [(0, 0, 2.6, 1.0), (3, 12, 1.4, 1.0), (6, 0, 1.4, 1.0), (8, 12, 1.4, 1.0), (10, 7, 1.4, 1.0),
                (11, 12, 0.8, 0.8), (12, 0, 1.4, 1.0), (14, last, 1.4, 1.0)]
    if style == "ferme":                # « boum » sur les temps : fondamentale, quinte
        return [(0, 0, 3.0, 1.0), (4, 7, 3.0, 0.9), (8, 0, 3.0, 1.0), (12, 7, 3.0, 0.9)]
    if style == "foret":
        return [(0, 0, 7.6, 0.9), (8, 7, 7.6, 0.8)]
    if style == "parc":
        return [(0, 0, 3.4, 0.6), (8, 7, 3.4, 0.55)]
    if style == "industrie":
        return [(k, 12 if k % 4 == 2 else 0, 0.7, 0.8) for k in range(16)]
    if style == "berceuse":             # une ronde par mesure
        return [(0, 0, 15.5, 0.45)]
    # basse : fondamentale / octave, quinte en fin de mesure
    pattern = [0, 12, 0, 12, 0, 12, 7, 12] if sec != 3 else [0, 12, 7, 12, 0, 12, 7, 10 if bar % 2 else 12]
    return [(k * 2, iv, 1.6, 1.0) for k, iv in enumerate(pattern)]


def _arp(style, tones):
    """(pas dans la mesure, note, durée, volume) ; tones : accord en 4e octave, fondamentale doublée à l'octave."""
    if style == "village":              # monte et redescend
        pat = [0, 1, 2, 3, 2, 1]
        return [(k, tones[pat[k % 6]], 0.8, 1.0) for k in range(16)]
    if style == "ferme":                # rouleau de banjo : trois cordes, trois contre quatre
        roll = [tones[2], tones[3], tones[1] + 12]
        return [(k, roll[k % 3], 0.8, 1.1) for k in range(16)]
    if style == "foret":                # accords brisés en croches
        pat = [0, 1, 2, 3, 2, 1, 2, 1]
        return [(k * 2, tones[pat[k]], 1.8, 1.0) for k in range(8)]
    if style == "parc":
        pat = [0, 2, 3, 2, 1, 2, 3, 2]
        return [(k * 2, tones[pat[k]] + 12, 1.5, 0.9) for k in range(8)]
    if style == "berceuse":             # accords brisés lents, comme un bercement
        pat = [0, 2, 3, 2, 1, 2, 3, 2]
        return [(k * 2, tones[pat[k]], 2.4, 0.55) for k in range(8)]
    if style == "industrie":            # motif qui tourne en rond
        pat = [0, 0, 2, 0, 3, 0, 2, 0]
        return [(k, tones[pat[k % 8]], 0.6, 0.9) for k in range(16)]
    # arpèges en doubles-croches
    return [(k, tones[k % 4], 0.8, 1.0) for k in range(16)]


def _drums(style, bar, sec):
    """(pas dans la mesure, instrument, volume)."""
    out = []
    roll = bar in (7, 15, 23, 31)       # fin de phrase longue
    if style == "village":
        for k in range(16):
            if k in (0, 6, 8) or (sec == 3 and k == 11):
                out.append((k, "kick", 1.0))
            if k in (4, 12):
                out.append((k, "snare", 1.0))
            out.append((k, "hat", 0.8 if k % 2 == 0 else 0.4))
        if bar % 2:
            out.append((15, "snare", 0.35))
    elif style == "ferme":              # « tchac » sur les contretemps, caisse claire balayée
        out += [(0, "kick", 0.9), (8, "kick", 0.9), (4, "snare", 0.5), (12, "snare", 0.5)]
        out += [(k, "hat", 0.9) for k in (2, 6, 10, 14)]
        roll = False
    elif style == "foret":
        out += [(0, "kick", 0.45), (4, "hat", 0.25), (12, "hat", 0.25)]
        roll = False
    elif style in ("parc", "berceuse"):
        return []
    elif style == "industrie":
        out += [(k, "kick", 0.9) for k in (0, 4, 8, 12)] + [(4, "snare", 0.9), (12, "snare", 0.9)]
        out += [(k, "hat", 1.0 if k % 4 == 2 else 0.3) for k in range(16) if k % 2 or k % 4 == 2]
    else:                               # batterie : varie selon la section (A, B, C doux, D plus nerveux)
        for k in range(16):
            kick = k in (0, 8) or (sec in (1, 3) and k == 10) or (sec == 3 and k == 14 and bar % 2)
            if sec == 2:
                kick = k == 0 or (k == 8 and bar % 2 == 0)
            if kick:
                out.append((k, "kick", 1.0))
            if k in (4, 12):
                out.append((k, "snare", 0.8 if sec == 2 else 1.0))
            if sec == 2:
                if k % 4 == 0:
                    out.append((k, "hat", 0.6))
            elif k % 2 == 0 or (sec == 3 and k % 4 == 3):
                out.append((k, "hat", 0.9 if k % 4 == 0 else 0.6))
    if roll:                            # petit roulement de fin de phrase
        out += [(k, "snare", 0.6 + 0.15 * (k - 13)) for k in (13, 14, 15)]
    return out


def events(style="base"):
    """Retourne (pas total, liste d'événements [pas, canal, midi|type, durée_en_pas, volume(, glissé)]) du thème,
    dans la variation `style` (STYLES). glissé : la note part de ce nombre de demi-tons et glisse vers la sienne."""
    ev = []
    total = len(CHORDS) * STEPS_PER_BAR
    for st, n, ln in _melody():
        ev += _lead(style, st, n, ln, total)
    for bar, ch in enumerate(CHORDS):
        s0 = bar * STEPS_PER_BAR
        sec = bar // 8
        r = midi(ROOT_BASS[ch])
        ev += [[s0 + k, "bass", r + iv, ln, v] for k, iv, ln, v in _bass(style, bar, sec)]
        tones = sorted(midi(n + "4") for n in CHORD_NOTES[ch])
        tones.append(tones[0] + 12)
        ev += [[s0 + k, "arp", n, ln, v] for k, n, ln, v in _arp(style, tones)]
        ev += [[s0 + k, "drums", d, 1, v] for k, d, v in _drums(style, bar, sec)]
    ev.sort(key=lambda e: e[0])
    return total, ev


# ------------------------------------------------------------------ fanfare de victoire
FANFARE_BPM = 140
FANFARE_CHORDS = ["F", "G", "C"]
FANFARE_LEAD = """
A5 -  C6 -  F6 -  E6 D6 | B5 -  D6 -  G6 -  F6 D6 | C6 -  -  -  -  -  -  -
"""


def fanfare_events():
    """Fanfare de victoire (3 mesures : la montée finale, ne boucle pas) : retourne (pas total, événements)."""
    ev = []
    total = len(FANFARE_CHORDS) * STEPS_PER_BAR
    toks = FANFARE_LEAD.replace("|", " ").split()
    assert len(toks) == len(FANFARE_CHORDS) * 8, len(toks)
    i = 0
    while i < len(toks):
        t = toks[i]
        if t in "-.":
            i += 1
            continue
        j = i + 1
        while j < len(toks) and toks[j] == "-":
            j += 1
        last = j >= len(toks)
        ev.append([i * 2, "lead", midi(t), (j - i) * 2 - (0.3 if not last else 0.0), 1.0])
        i = j
    for bar, ch in enumerate(FANFARE_CHORDS):
        s0 = bar * STEPS_PER_BAR
        final = bar == len(FANFARE_CHORDS) - 1
        r = midi(ROOT_BASS[ch])
        if final:
            ev.append([s0, "bass", r, 16, 1.0])
            ev.append([s0, "bass", r + 12, 16, 0.6])
            for n in ("E5", "G5"):
                ev.append([s0, "lead", midi(n), 16, 0.45])
            ev.append([s0, "drums", "kick", 1, 1.0])
            ev.append([s0, "drums", "snare", 1, 0.9])
            ev.append([s0, "drums", "hat", 1, 1.0])
            continue
        for k, iv in enumerate([0, 12, 0, 12, 0, 12, 7, 12]):
            ev.append([s0 + k * 2, "bass", r + iv, 1.6, 1.0])
        tones = sorted(midi(n + "4") for n in CHORD_NOTES[ch])
        tones = tones + [tones[0] + 12]
        for k in range(16):
            ev.append([s0 + k, "arp", tones[k % 4], 0.8, 1.3])
        for k in range(16):
            if k in (0, 8):
                ev.append([s0 + k, "drums", "kick", 1, 1.0])
            if k in (4, 12):
                ev.append([s0 + k, "drums", "snare", 1, 1.0])
            if k % 2 == 0:
                ev.append([s0 + k, "drums", "hat", 1, 0.9 if k % 4 == 0 else 0.6])
        if bar == len(FANFARE_CHORDS) - 2:      # roulement vers l'accord final
            for k in (12, 13, 14, 15):
                ev.append([s0 + k, "drums", "snare", 1, 0.55 + 0.15 * (k - 12)])
    ev.sort(key=lambda e: e[0])
    return total, ev


# ------------------------------------------------------------------ musique de défaite
# Même forme et même durée que la fanfare (3 mesures à 140 BPM), mais en la mineur : la mélodie descend doucement,
# passe par la tension de mi majeur (sol dièse) et se pose sur un la grave tenu. Triste mais tendre, pas moqueuse.
DEFEAT_BPM = FANFARE_BPM
DEFEAT_CHORDS = ["Am", "E", "Am"]
DEFEAT_LEAD = """
E5 -  D5 -  C5 -  B4 -  | A4 -  C5 -  B4 -  G#4 - | A4 -  -  -  -  -  -  -
"""


def defeat_events():
    """Musique de défaite (3 mesures, ne boucle pas) : retourne (pas total, événements)."""
    ev = []
    total = len(DEFEAT_CHORDS) * STEPS_PER_BAR
    toks = DEFEAT_LEAD.replace("|", " ").split()
    assert len(toks) == len(DEFEAT_CHORDS) * 8, len(toks)
    i = 0
    while i < len(toks):
        t = toks[i]
        if t in "-.":
            i += 1
            continue
        j = i + 1
        while j < len(toks) and toks[j] == "-":
            j += 1
        last = j >= len(toks)
        ev.append([i * 2, "lead", midi(t), (j - i) * 2 - (0.4 if not last else 0.0), 0.9])
        i = j
    for bar, ch in enumerate(DEFEAT_CHORDS):
        s0 = bar * STEPS_PER_BAR
        r = midi(ROOT_BASS[ch])
        if bar == len(DEFEAT_CHORDS) - 1:
            # accord final tenu, tout doux : la grave, do et mi en écho, un dernier petit coup de grosse caisse
            ev.append([s0, "bass", r, 16, 1.0])
            ev.append([s0, "bass", r + 12, 16, 0.5])
            for n in ("C5", "E5"):
                ev.append([s0, "lead", midi(n), 16, 0.3])
            ev.append([s0, "drums", "kick", 1, 0.7])
            continue
        # basse en blanches (fondamentale, quinte) : plus lente et posée que dans le thème
        ev.append([s0, "bass", r, 7.6, 1.0])
        ev.append([s0 + 8, "bass", r + 7, 7.6, 0.9])
        # arpège en croches, discret
        tones = sorted(midi(n + "4") for n in CHORD_NOTES[ch])
        tones = tones + [tones[0] + 12]
        for k in range(8):
            ev.append([s0 + k * 2, "arp", tones[(k * 3) % 4], 1.6, 1.1])
        # batterie à peine présente : un temps sur deux
        ev.append([s0, "drums", "kick", 1, 0.6])
        ev.append([s0 + 8, "drums", "hat", 1, 0.5])
    ev.sort(key=lambda e: e[0])
    return total, ev


VOL = {"lead": 0.16, "arp": 0.045, "bass": 0.2, "kick": 0.5, "snare": 0.2, "hat": 0.07}


# ------------------------------------------------------------------ rendu WAV
def render_wav(fn, loops=2, sr=44100, song=None, bpm=None, tail=0.0):
    """song = (total, events) ; tail > 0 : pas de bouclage, on ajoute `tail` s de silence pour laisser sonner la fin."""
    total, ev = song or events()
    step = 60 / (bpm or BPM) / 4
    n = int((total * step * loops + tail) * sr)
    buf = np.zeros(n, dtype=np.float64)
    rng = np.random.default_rng(3)

    def env(length, a=0.004, d=0.05, s=0.65, r=0.03):
        t = np.arange(length) / sr
        dur = length / sr
        e = np.where(t < a, t / a, np.where(t < a + d, 1 - (1 - s) * (t - a) / d, s))
        rel = np.clip((dur - t) / r, 0, 1)
        return e * rel

    for lp in range(loops):
        off = lp * total
        for e in ev:
            st, ch, note, ln, vol = e[:5]
            i0 = int((st + off) * step * sr)
            if ch in ("lead", "arp", "bass"):
                L = int(ln * step * sr)
                t = np.arange(L) / sr
                ph = (t * freq(note)) % 1.0
                if ch == "lead":
                    w = np.where(ph < 0.25, 1.0, -1.0)
                    # léger vibrato après l'attaque
                    w = w * env(L)
                elif ch == "arp":
                    w = np.where(ph < 0.125, 1.0, -1.0) * env(L, d=0.02, s=0.4)
                else:
                    w = (4 * np.abs(ph - 0.5) - 1) * env(L, d=0.08, s=0.8)
                seg = w * VOL[ch] * vol
            else:
                if note == "kick":
                    L = int(0.14 * sr)
                    t = np.arange(L) / sr
                    f = 150 * np.exp(-t * 28) + 45
                    seg = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t * 22)
                elif note == "snare":
                    L = int(0.12 * sr)
                    t = np.arange(L) / sr
                    seg = rng.uniform(-1, 1, L) * np.exp(-t * 30) * 0.9 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 40) * 0.4
                else:
                    L = int(0.035 * sr)
                    t = np.arange(L) / sr
                    x = rng.uniform(-1, 1, L)
                    x = np.diff(np.concatenate([[0], x]))       # passe-haut grossier
                    seg = x * np.exp(-t * 90) * 0.6
                seg = seg * VOL[note] * vol
            # les queues de notes qui dépassent la fin reviennent au début : boucle sans coupure
            idx = (np.arange(len(seg)) + i0) % n if not tail else np.arange(len(seg)) + i0
            keep = idx < n
            np.add.at(buf, idx[keep], seg[keep])
    buf = np.tanh(buf * 1.1) * 0.9
    data = (buf * 32767).astype("<i2").tobytes()
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    with open(fn, "wb") as f:
        f.write(b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVEfmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, 1, sr, sr * 2, 2, 16))
        f.write(b"data" + struct.pack("<I", len(data)) + data)
    return n / sr


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "audio", "music_tecky.wav")
    dur = render_wav(out, loops=1)
    print(f"OK -> {out} ({dur:.1f} s, boucle parfaite)")
    out2 = os.path.join(os.path.dirname(out), "music_victoire.wav")
    dur = render_wav(out2, loops=1, song=fanfare_events(), bpm=FANFARE_BPM, tail=1.5)
    print(f"OK -> {out2} ({dur:.1f} s, ne boucle pas)")
    out3 = os.path.join(os.path.dirname(out), "music_defaite.wav")
    dur = render_wav(out3, loops=1, song=defeat_events(), bpm=DEFEAT_BPM, tail=1.5)
    print(f"OK -> {out3} ({dur:.1f} s, ne boucle pas)")
