#!/usr/bin/env python3
"""
La musique de Tecky Quest (v2) : des morceaux chiptune originaux, un par zone.

songs() -> les morceaux joués par le séquenceur WebAudio du jeu (pack_web.py les écrit dans la page : SONGS).
python3 music.py -> contrôle des partitions (notes des temps hors de l'accord, notes hors de la gamme, étendue).

Chaque zone a son morceau, dans son ton, à son tempo, avec ses instruments ; le jeu passe de l'un à l'autre par
un fondu vers le silence (game.js : Music). « Promenade de Tecky » (la niche, l'écran titre) est le thème du
jeu ; son premier motif (mi sol do sol mi – ré mi) revient dans les autres morceaux, comme une signature.

  niche      do majeur, 140      le thème : « Promenade de Tecky »
  village    sol majeur, 152     polka du marché : basse et accords en contretemps, notes piquées
  campagne   fa majeur, 12/8     trot : rythme ternaire, flûte, harpe
  ferme      la majeur, 132      violon et banjo, « boum-tchac », sabots
  foret      la mineur, 96       flûte et harpe, avec de l'écho
  parc       ré majeur, 3/4      valse de boîte à musique, sans batterie
  industrie  mi mineur, 138      mécanique : basse martelée, engrenages, coups de métal
  berceuse   do majeur, 84       le thème, lent et à l'octave : la nuit à la niche (scène de fin)
  win, lose  fanfare de victoire et musique de défaite (3 mesures, jouées une fois)

Canaux : lead (mélodie), harm (deuxième voix : contre-chant écrit, ou tierces sous la mélodie), arp (arpèges,
accords), bass, pad (nappe), drums. Les instruments (INST, réglés par morceau) font partie des données : forme
d'onde, volume, enveloppe, vibrato, écho.
"""
import sys

NOTE_IDX = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
GAMMES = {"": [0, 2, 4, 5, 7, 9, 11], "m": [0, 2, 3, 5, 7, 8, 10]}       # majeure, mineure naturelle


def midi(nom):
    """« C#5 », « Bb4 » -> numéro MIDI."""
    n, octv = nom[:-1], int(nom[-1])
    return 12 * (octv + 1) + NOTE_IDX[n[0]] + n.count("#") - n.count("b")


def _fond(nom):
    """Fondamentale (0..11) d'un nom de note ou d'accord, et le reste du nom."""
    r, reste = NOTE_IDX[nom[0]], nom[1:]
    if reste[:1] in ("#", "b"):
        r += 1 if reste[0] == "#" else -1
        reste = reste[1:]
    return r % 12, reste


def accord(nom):
    """« Am », « D7 », « Bb » -> (fondamentale, notes de l'accord de 0 à 11, tierce en demi-tons)."""
    r, reste = _fond(nom)
    t = 3 if reste.startswith("m") else 4
    iv = [0, t, 7] + ([10] if reste.endswith("7") else [])
    return r, [(r + i) % 12 for i in iv], t


def gamme(ton):
    r, reste = _fond(ton)
    return {(r + i) % 12 for i in GAMMES[reste]}


def basse(r):
    """La fondamentale dans le registre de la basse (fa 1 .. mi 2)."""
    return 29 + (r - 5) % 12


def tons(nom):
    """Les trois notes de l'accord dans la 4e octave, de la plus grave à la plus aiguë, la plus grave redoublée."""
    t = sorted(60 + p for p in accord(nom)[1][:3])
    return t + [t[0] + 12]


def voix(texte, bar):
    """Une voix écrite mesure par mesure (séparées par « | » ou un retour à la ligne), chaque mesure découpée en
    autant de temps égaux qu'elle a de jetons : une note, « - » tenue, « . » silence, « / » devant une note =
    glissée depuis un ton en dessous. -> ([(pas, midi, durée en pas, glissé)], nombre de mesures)"""
    mesures = [m.split() for m in texte.replace("\n", "|").split("|") if m.strip()]
    jetons = []
    for i, m in enumerate(mesures):
        assert bar % len(m) == 0, (i, m)
        d = bar // len(m)
        jetons += [(i * bar + k * d, t, d) for k, t in enumerate(m)]
    out, i = [], 0
    while i < len(jetons):
        st, t, ln = jetons[i]
        i += 1
        if t in "-.":
            continue
        while i < len(jetons) and jetons[i][1] == "-":
            ln += jetons[i][2]
            i += 1
        out.append((st, midi(t.lstrip("/")), ln, -2 if t[0] == "/" else 0))
    return out, len(mesures)


def bat(**instruments):
    """Motif de batterie : par instrument, ses pas dans la mesure, ou des (pas, volume)."""
    out = []
    for nom, pas in instruments.items():
        out += [(x[0], nom, x[1]) if isinstance(x, tuple) else (x, nom, 1.0) for x in pas]
    return sorted(out)


# Instruments : w = rapport cyclique d'une onde carrée, ou forme d'onde ; v = volume ; s = tenue (part du volume
# gardée après l'attaque) ; a, r = attaque et relâchement (s) ; pl = note pincée, qui s'éteint d'elle-même (constante
# de temps, s) ; vib = vibrato des notes longues (centièmes de demi-ton) ; lp = filtre passe-bas (Hz) ; echo = 1 :
# passe par l'écho du morceau (Morceau.echo = pas de retard, réinjection, volume).
INST = {
    "lead": dict(w=0.25, v=0.16, s=0.65),
    "harm": dict(w=0.5, v=0.055, s=0.6),
    "arp": dict(w=0.125, v=0.045, s=0.4),
    "bass": dict(w="triangle", v=0.2, s=0.8),
    "pad": dict(w="triangle", v=0.04, s=1.0, a=0.2, r=0.25),
}
ROULE = [(13, "snare", 0.6), (14, "snare", 0.75), (15, "snare", 0.9)]          # roulement de fin de phrase
TOMS = [(8, "tomH", 0.8), (10, "tomH", 0.7), (11, "tomM", 0.8), (12, "tomM", 0.9), (13, "tomL", 0.8),
        (14, "tomL", 1.0), (15, "snare", 0.9)]                                 # descente de toms


class Morceau:
    """Un morceau = des parties jouées à la suite. tempo : temps par minute ; bar : pas par mesure ; beat : pas
    par temps (4 : binaire, 3 : ternaire). Les parties `intro` ne sont jouées qu'une fois ; les autres bouclent."""

    def __init__(self, nom, tempo, ton, bar=16, beat=4, inst=None, echo=None, boucle=True):
        self.nom, self.tempo, self.bar, self.beat = nom, tempo, bar, beat
        self.gamme = gamme(ton)
        self.inst = {c: dict(INST[c], **(inst or {}).get(c, {})) for c in INST}
        self.echo, self.boucle, self.parties = echo, boucle, []

    def partie(self, accords, lead=None, harm=None, bass=None, arp=None, pad=None, drums=None, fin=None,
               crash=False, entree=True, intro=False, v=1.0, hv=1.0, coupe=(0.3, 0.3), tenue=None, octave=0,
               extra=()):
        """accords : un par mesure (« C,D » : deux dans la mesure). lead : la mélodie (voix()) ; harm : un
        contre-chant écrit, ou "tierces" (sous la mélodie, dans l'accord). bass, arp, drums : un motif d'une
        mesure, ou une liste de motifs joués à tour de rôle (None : silence).
          bass : (pas, quoi, durée, volume) ; quoi = demi-tons depuis la fondamentale, "q" quinte, "3" tierce,
                 "a" note d'approche de la fondamentale suivante
          arp  : (pas, rang ou rangs dans tons(), durée, volume[, décalage en demi-tons])
          drums : bat() ; fin : motif qui remplace la fin de la dernière mesure ; crash : cymbale au début
        pad : volume d'une nappe tenue. entree : le jeu peut reprendre le morceau au début de cette partie.
        v, hv : volume de la mélodie, de la deuxième voix ; coupe : pas retirés aux notes (brèves, longues) ;
        tenue : durée maximale d'une note ; octave : décalage de la mélodie ; extra : événements en plus."""
        acc = [m.split(",") for m in accords.split()]
        self.parties.append(dict(acc=acc, lead=lead, harm=harm, bass=bass, arp=arp, pad=pad, drums=drums, fin=fin,
                                 crash=crash, entree=entree, intro=intro, v=v, hv=hv, coupe=coupe, tenue=tenue,
                                 octave=octave, extra=extra))
        return self

    def tierce(self, m, nom):
        """La note à jouer sous m : une tierce plus bas dans la gamme ; si m est dans l'accord et pas elle, la
        note de l'accord juste en dessous."""
        pcs = accord(nom)[1]
        t, n = m, 0
        while n < 2:
            t -= 1
            n += t % 12 in self.gamme
        if m % 12 in pcs and t % 12 not in pcs:
            return next(c for c in range(m - 3, m - 10, -1) if c % 12 in pcs)
        return t

    def _basse(self, quoi, nom, suivant, seul):
        r, _, t = accord(nom)
        b = basse(r)
        if quoi == "q":                 # deux accords dans la mesure : pas le temps d'une quinte
            return (b + 7 if b + 7 <= 43 else b - 5) if seul else b
        if quoi == "3":
            return b + t
        if quoi == "a":
            c = basse(accord(suivant)[0])
            if c == b:
                return self._basse("q", nom, suivant, True)
            a = c - 1
            while a % 12 not in self.gamme:
                a -= 1
            return a if a >= 28 else a + 12
        return b + quoi

    def construire(self):
        """-> le morceau pour le jeu : total (pas), bar, bpm, spb (secondes par pas), loop (pas où reprendre
        après le dernier ; None : joué une fois), entries (pas où le jeu peut reprendre le morceau), inst, echo,
        ev = [pas, canal, midi | instrument de batterie, durée en pas, volume(, glissé en demi-tons)]."""
        bar, ev, entrees, s0, k = self.bar, [], [], 0, 0
        plat = [(p, i) for p in self.parties for i in range(len(p["acc"]))]
        n_intro = sum(len(p["acc"]) for p in self.parties if p["intro"])
        motif = lambda x, i: [] if not x else x if isinstance(x[0], tuple) else (x[i % len(x)] or [])
        self.grille, self.melodie = [], []                    # pour controle()
        for p in self.parties:
            n = len(p["acc"])
            if p["entree"] and not p["intro"]:
                entrees.append(s0)

            def en(st, p=p):                                  # l'accord au pas st de la partie
                a = p["acc"][st // bar]
                return a[(st % bar) * len(a) // bar]
            notes = []
            if p["lead"]:
                notes, nb = voix(p["lead"], bar)
                assert nb == n, (self.nom, "mélodie", nb, n)
                for st, m, ln, gl in notes:
                    d = ln - p["coupe"][0 if ln <= 2 else 1]
                    ev.append([s0 + st, "lead", m + p["octave"], round(min(d, p["tenue"] or d), 2), p["v"]] + ([gl] if gl else []))
                    self.melodie.append((s0 + st, m, en(st)))
            if p["harm"] == "tierces":
                ev += [[s0 + st, "harm", self.tierce(m + p["octave"], en(st)), round(ln - 0.3, 2), p["hv"]] for st, m, ln, _ in notes]
            elif p["harm"]:
                contre, nb = voix(p["harm"], bar)
                assert nb == n, (self.nom, "contre-chant", nb, n)
                ev += [[s0 + st, "harm", m, round(ln - 0.3, 2), p["hv"]] for st, m, ln, _ in contre]
            for i, acc in enumerate(p["acc"]):
                b0 = s0 + i * bar
                apres = plat[k + 1] if k + 1 < len(plat) else plat[n_intro]
                apres = apres[0]["acc"][apres[1]][0]
                k += 1
                rang = lambda st: st * len(acc) // bar
                self.grille += [(b0 + j * bar // len(acc), nom) for j, nom in enumerate(acc)]
                for st, quoi, ln, v in motif(p["bass"], i):
                    j = rang(st)
                    suivant = acc[j + 1] if j + 1 < len(acc) else apres
                    ev.append([b0 + st, "bass", self._basse(quoi, acc[j], suivant, len(acc) == 1), ln, v])
                for st, rangs, ln, v, *dec in motif(p["arp"], i):
                    t = tons(acc[rang(st)])
                    for r in (rangs if isinstance(rangs, tuple) else (rangs,)):
                        ev.append([b0 + st, "arp", t[r % 4] + (dec[0] if dec else 0), ln, v])
                if p["pad"]:
                    d = bar // len(acc)
                    ev += [[b0 + j * d, "pad", m, d - 0.4, p["pad"]] for j, nom in enumerate(acc) for m in tons(nom)[:3]]
                dr = motif(p["drums"], i)
                if i == n - 1 and p["fin"]:
                    dr = [x for x in dr if x[0] < min(f[0] for f in p["fin"])] + p["fin"]
                if i == 0 and p["crash"]:
                    dr = dr + [(0, "crash", 1.0)]
                ev += [[b0 + st, "drums", nom, 1, v] for st, nom, v in dr]
            ev += [[s0 + e[0]] + list(e[1:]) for e in p["extra"]]
            s0 += n * bar
        ev.sort(key=lambda e: e[0])
        joues = {e[1] for e in ev}
        return dict(total=s0, bar=bar, bpm=self.tempo, spb=round(60 / (self.tempo * self.beat), 5),
                    loop=n_intro * bar if self.boucle else None, entries=entrees or [n_intro * bar],
                    inst={c: self.inst[c] for c in INST if c in joues}, echo=self.echo, ev=ev)


# ------------------------------------------------------------------ « Promenade de Tecky » : la niche, l'écran titre
# Mélodie en croches. Quatre phrases de huit mesures : A le thème, B le pont, C un passage plus doux, D la reprise.
THEME = """
E5 G5 C6 G5 E5 -  D5 E5 | C5 -  A4 C5 E5 -  D5 C5 | A4 C5 F5 A5 G5 F5 E5 C5 | D5 -  B4 D5 G5 -  .  .
E5 G5 C6 G5 E5 G5 A5 G5 | E5 -  C5 E5 A5 -  G5 E5 | F5 E5 D5 C5 A4 C5 F5 A5 | G5 -  F5 -  D5 -  B4 -
A5 -  A5 G5 F5 -  A5 -  | B5 -  B5 A5 G5 -  B5 -  | G5 -  E5 G5 B5 -  A5 G5 | A5 -  E5 -  C5 -  E5 -
F5 A5 C6 A5 F5 A5 C6 D6 | B5 -  G5 -  D5 -  G5 A5 | C6 -  G5 E5 C5 E5 G5 -  | C6 -  -  -  .  .  G5 -
E5 -  E5 D5 C5 -  A4 C5 | B4 -  B4 C5 D5 -  E5 G5 | A5 -  G5 F5 E5 -  F5 A5 | G5 -  E5 -  C5 -  D5 E5
F5 -  F5 E5 D5 -  F5 A5 | E5 -  C5 E5 A5 -  G5 E5 | D5 G5 B5 G5 D5 G5 B5 D6 | B5 -  A5 -  G5 -  .  .
E5 G5 C6 G5 E5 -  D5 E5 | C5 -  A4 C5 E5 -  D5 C5 | A4 C5 F5 A5 G5 F5 E5 C5 | D5 -  B4 D5 G5 -  .  .
E5 G5 C6 G5 E5 G5 A5 G5 | E5 -  C5 E5 A5 -  G5 E5 | F5 E5 D5 C5 D5 F5 A5 C6 | B5 -  A5 -  G5 -  D5 -
"""
THEME_ACCORDS = ["C Am F G C Am F G", "F G Em Am F G C C", "Am Em F C Dm Am G G", "C Am F G C Am Dm G"]
# contre-chant du pont : des notes longues, une sixte sous la mélodie, qui redescendent vers le passage doux
THEME_CONTRE = """
C5 -  -  -  A4 -  C5 -  | D5 -  -  -  B4 -  D5 -  | B4 -  -  -  G4 -  B4 -  | C5 -  -  -  A4 -  -  -
A4 -  -  -  C5 -  -  -  | G4 -  -  -  B4 -  D5 -  | E5 -  -  -  G4 -  C5 -  | E5 -  D5 -  C5 -  B4 -
"""


def _phrases(texte, n=2):
    lignes = texte.strip().split("\n")
    return ["\n".join(lignes[i:i + n]) for i in range(0, len(lignes), n)]


def niche():
    m = Morceau("niche", 140, "C", inst=dict(lead=dict(vib=8)))
    A, B, C, D = _phrases(THEME)
    arp16 = [(k, k % 4, 0.8, 1.0) for k in range(16)]
    arp8 = [(k * 2, r, 1.8, 1.0) for k, r in enumerate([0, 1, 2, 3, 2, 1, 2, 1])]
    bond = lambda *iv: [(k * 2, x, 1.6, 1.0) for k, x in enumerate(iv)]        # basse sautillante, en croches
    croches = [(k, 0.9 if k % 4 == 0 else 0.6) for k in range(0, 16, 2)]
    rock = bat(kick=[0, 8], snare=[4, 12], hat=croches)
    doux = [bat(kick=[0, 8], snare=[(4, 0.8), (12, 0.8)], hat=[(k, 0.6) for k in (0, 4, 8, 12)]),
            bat(kick=[0], snare=[(4, 0.8), (12, 0.8)], hat=[(k, 0.6) for k in (0, 4, 8, 12)])]
    plein = bat(kick=[0, 8, 10], snare=[4, 12], hat=croches + [(k, 0.6) for k in (3, 7, 11, 15)], ohat=[(14, 0.8)])
    # deux mesures d'entrée (jouées une fois) : les arpèges seuls, puis la basse et une descente de toms
    m.partie("C", arp=[(k, r, ln, 0.8) for k, r, ln, _ in arp16], drums=bat(hat=[(k, 0.5) for k in range(0, 16, 2)]),
             intro=True)
    m.partie("G", arp=arp16, bass=bond(0, 12, 0, 12, 0, 12, 7, 12), drums=bat(kick=[0, 8], hat=croches), fin=TOMS,
             intro=True)
    m.partie(THEME_ACCORDS[0], lead=A, bass=bond(0, 12, 0, 12, 0, 12, 7, 12), arp=arp16, drums=rock, fin=ROULE, crash=True)
    m.partie(THEME_ACCORDS[1], lead=B, harm=THEME_CONTRE, hv=1.2, bass=bond(0, 12, 0, 12, 0, 12, 7, "a"), arp=arp16,
             drums=bat(kick=[0, 8, 10], snare=[4, 12], hat=croches), fin=ROULE)
    m.partie(THEME_ACCORDS[2], lead=C, pad=1.0, arp=arp8, drums=doux, fin=TOMS,
             bass=[(0, 0, 3.6, 1.0), (4, 12, 1.6, 0.8), (8, 0, 3.6, 1.0), (12, 7, 1.6, 0.9), (14, "a", 1.6, 0.9)])
    m.partie(THEME_ACCORDS[3], lead=D, harm="tierces", arp=arp16, fin=TOMS, crash=True,
             bass=[bond(0, 12, 7, 12, 0, 12, 7, 12), bond(0, 12, 7, 12, 0, 12, 7, 10)],
             drums=[plein, plein + [(14, "kick", 1.0)]])
    return m


def berceuse():
    """La nuit à la niche : le thème, lent, à l'octave, des notes tenues, pas de batterie."""
    m = Morceau("berceuse", 84, "C", echo=(4, 0.3, 0.22),
                inst=dict(lead=dict(w="sine", v=0.29, vib=10, a=0.02, echo=1), arp=dict(w="triangle", v=0.08),
                          harm=dict(w="sine", v=0.1, s=0.8, a=0.03), pad=dict(v=0.035)))
    berce = [(k * 2, r, 2.4, 0.55) for k, r in enumerate([0, 2, 3, 2, 1, 2, 3, 2])]      # accords brisés, lents
    for i, (acc, ph) in enumerate(zip(THEME_ACCORDS, _phrases(THEME))):
        m.partie(acc, lead=ph, octave=12, v=0.75, coupe=(0.2, 0.2), tenue=5.5, bass=[(0, 0, 15.5, 0.45)], arp=berce,
                 pad=1.0 if i >= 2 else None, harm="tierces" if i == 3 else None, hv=0.7)
    return m


# ------------------------------------------------------------------ le village : polka du marché
VILLAGE_A = """
D5 -  G5 A5 B5 -  G5 -  | A5 -  F#5 G5 A5 -  D5 -  | G5 -  E5 F#5 G5 -  B5 -  | C6 B5 A5 G5 A5 -  .  .
D5 -  G5 A5 B5 -  D6 -  | C6 -  A5 B5 C6 -  A5 -  | G5 E5 C5 E5 A5 F#5 D5 F#5 | G5 -  .  D5 G5 -  .  .
"""
VILLAGE_A_FIN = """
D5 -  G5 A5 B5 -  G5 -  | A5 -  F#5 G5 A5 -  D5 -  | G5 -  E5 F#5 G5 -  B5 -  | C6 B5 A5 G5 A5 -  .  .
D5 -  G5 A5 B5 -  D6 -  | C6 -  A5 B5 C6 -  A5 -  | G5 E5 C5 E5 A5 F#5 A5 C6 | B5 -  D6 -  G6 -  .  .
"""
VILLAGE_B = """
E5 G5 C6 G5 E5 -  D5 E5 | G5 -  E5 G5 C6 -  B5 C6 | D6 -  B5 G5 D5 -  G5 B5 | A5 -  G5 -  D5 -  .  .
C5 E5 A5 E5 C5 -  B4 C5 | E5 -  C5 E5 A5 -  G5 E5 | F#5 -  A5 -  D6 -  C6 A5 | B5 A5 F#5 A5 D5 -  .  .
"""


def village():
    m = Morceau("village", 152, "G", inst=dict(lead=dict(vib=6), arp=dict(w=0.25, v=0.036, s=0.5)))
    acc = "G D Em C,D G D7 C,D G"
    polka = [(0, 0, 2.6, 1.0), (4, "q", 2.6, 0.9), (8, 0, 2.6, 1.0), (12, "q", 2.6, 0.9)]
    monte = polka[:2] + [(8, 0, 1.6, 1.0), (10, "3", 1.6, 0.9), (12, "q", 1.6, 0.9), (14, "a", 1.6, 1.0)]
    pah = [(k, (1, 2, 3), 1.0, 1.0) for k in (2, 6, 10, 14)]                   # accords en contretemps
    doubles = [(k, 0.8 if k % 2 == 0 else 0.4) for k in range(16)]
    marche = bat(kick=[0, 6, 8], snare=[4, 12], hat=doubles)
    marche = [marche, marche + [(15, "snare", 0.35)]]
    piquee = dict(coupe=(0.7, 0.3))
    m.partie(acc, lead=VILLAGE_A, bass=[polka, polka, polka, monte], arp=pah, drums=marche, fin=ROULE, **piquee)
    m.partie(acc, lead=VILLAGE_A, harm="tierces", bass=[polka, polka, polka, monte], arp=pah, fin=ROULE, crash=True,
             drums=[d + [(14, "ohat", 0.7)] for d in marche], **piquee)
    # le pont : plus chantant, la basse marche en noires, et le motif de Tecky passe (do majeur, puis la mineur)
    m.partie("C C G G Am Am D7 D7", lead=VILLAGE_B, pad=0.8, fin=TOMS,
             bass=[(0, 0, 3.2, 1.0), (4, "3", 3.2, 0.9), (8, "q", 3.2, 0.9), (12, "a", 3.2, 0.9)],
             arp=[(k * 2, r, 1.6, 1.0) for k, r in enumerate([0, 1, 2, 1, 3, 1, 2, 1])],
             drums=bat(kick=[0, 8], rim=[4, 12], hat=[(k, 0.6) for k in range(0, 16, 2)]))
    m.partie(acc, lead=VILLAGE_A_FIN, harm="tierces", bass=[polka, polka, polka, monte], arp=pah, fin=TOMS, crash=True,
             drums=[d + [(14, "ohat", 0.7)] for d in marche], **piquee)
    return m


# ------------------------------------------------------------------ la campagne : au trot (12/8)
CAMPAGNE_A = """
C5 - F5  A5 - G5  F5 - A5  C6 - -   | D6 - C6  A5 - F5  G5 - A5  F5 - -    | D5 - F5  Bb5 - A5  G5 - Bb5  D6 - - | C6 - A5  F5 - G5  A5 - -  . . .
A5 - D5  F5 - A5  D6 - C6  A5 - -   | Bb5 - D5  F5 - Bb5  D6 - C6  Bb5 - - | G5 - C5  E5 - G5  C6 - Bb5  G5 - E5 | G5 - -  E5 - C5  E5 - G5  C6 - -
"""
CAMPAGNE_A2 = """
C5 - F5  A5 - G5  F5 - A5  C6 - -   | D6 - C6  A5 - F5  G5 - A5  F5 - -    | D5 - F5  Bb5 - A5  G5 - Bb5  D6 - - | C6 - A5  F5 - G5  A5 - -  . . .
A5 - D5  F5 - A5  D6 - C6  A5 - -   | Bb5 - D5  F5 - Bb5  C6 - G5  E5 - G5 | A5 - G5  F5 - C5  F5 - A5  C6 - -   | F5 - -  - - -  . . .  . . .
"""
CAMPAGNE_B = """
D6 - -  Bb5 - -  F5 - G5  Bb5 - -   | A5 - C6  F6 - C6  A5 - -  G5 - A5    | Bb5 - -  D6 - -  F6 - D6  Bb5 - -   | C6 - -  G5 - -  E5 - G5  C6 - -
D6 - -  A5 - -  F5 - A5  D6 - -     | D6 - C6  Bb5 - -  F5 - Bb5  D6 - -   | Bb5 - A5  G5 - -  D5 - G5  Bb5 - -  | C6 - -  Bb5 - -  G5 - -  E5 - -
"""


def campagne():
    m = Morceau("campagne", 104, "F", bar=12, beat=3,
                inst=dict(lead=dict(w="triangle", v=0.27, s=0.75, vib=12, a=0.015), arp=dict(w="triangle", v=0.075, pl=0.14),
                          harm=dict(v=0.06)))
    trot = [(0, 0, 2.5, 1.0), (5, 0, 0.8, 0.7), (6, "q", 2.5, 0.9), (11, "a", 0.8, 0.8)]
    sautille = (0, 2, 3, 5, 6, 8, 9, 11)                                      # longue-brève, quatre fois
    harpe = [(k, r, 0.9, 1.0) for k, r in zip(sautille, (0, 1, 2, 1, 3, 2, 1, 2))]
    balais = bat(kick=[0, 6], rim=[(3, 0.8), (9, 0.8)], hat=[(k, 0.6 if k % 3 == 0 else 0.35) for k in sautille])
    toms = [(6, "tomH", 0.7), (8, "tomM", 0.8), (9, "tomM", 0.8), (11, "tomL", 0.9)]
    m.partie("F F Bb F Dm Bb C C7", lead=CAMPAGNE_A, bass=trot, arp=harpe, drums=balais)
    m.partie("F F Bb F Dm Bb,C F F", lead=CAMPAGNE_A2, harm="tierces", bass=trot, arp=harpe, drums=balais, fin=toms)
    # le pont : des notes longues sur une nappe ; à la deuxième mesure, le motif de Tecky
    m.partie("Bb F Bb C Dm Bb Gm C7", lead=CAMPAGNE_B, pad=1.0, fin=toms,
             bass=[(0, 0, 5.5, 1.0), (6, "q", 4.5, 0.9), (11, "a", 0.8, 0.8)],
             arp=[(k, [0, 1, 2, 3, 2, 1][k % 6], 0.9, 0.85) for k in range(12)],
             drums=bat(kick=[(0, 0.8)], rim=[(9, 0.6)], hat=[(k, 0.4 if k % 3 == 0 else 0.25) for k in sautille]))
    return m


# ------------------------------------------------------------------ la ferme : violon et banjo
FERME_A = """
E5 F#5 A5 B5 /C#6 -  A5 -  | B5 A5 F#5 A5 E5 -  .  E5 | F#5 A5 D6 A5 F#5 -  D5 F#5 | E5 -  C#5 E5 A5 -  .  .
E5 F#5 A5 B5 /C#6 -  E6 -  | C#6 B5 A5 F#5 A5 -  .  A5 | G#5 B5 E6 B5 G#5 -  F#5 G#5 | B5 -  G#5 -  E5 -  .  .
"""
FERME_A2 = """
E5 F#5 A5 B5 /C#6 -  A5 -  | B5 A5 F#5 A5 E5 -  .  E5 | F#5 A5 D6 A5 F#5 -  D5 F#5 | E5 -  C#5 E5 A5 -  .  .
E5 F#5 A5 B5 /C#6 -  E6 -  | D6 C#6 B5 G#5 B5 -  E5 -
"""
FERME_CODA = "A5 -  E5 E5 F#5 -  E5 -  | .  .  G#5 -  A5 -  .  ."        # « toc, toc-toc, toc, toc… toc, toc ! »
FERME_B = """
/F#5 -  -  A5 D6 -  -  .  | D6 C#6 B5 A5 F#5 -  .  .  | /E5 -  -  A5 C#6 -  -  .  | C#6 B5 A5 F#5 E5 -  .  .
/G#5 -  -  B5 E6 -  -  .  | E6 D6 B5 G#5 E5 -  F#5 G#5 | A5 -  C#6 -  E6 -  C#6 A5 | B5 -  G#5 B5 E5 -  .  .
"""


def ferme():
    m = Morceau("ferme", 132, "A",
                inst=dict(lead=dict(w="sawtooth", lp=2600, v=0.15, s=0.7, vib=10, a=0.012), arp=dict(w=0.25, v=0.05, pl=0.08),
                          harm=dict(w="sawtooth", lp=2000, v=0.07, s=0.7)))
    boum = [(0, 0, 3.0, 1.0), (4, "q", 3.0, 0.9), (8, 0, 3.0, 1.0), (12, "q", 3.0, 0.9)]      # fondamentale, quinte
    monte = boum[:2] + [(8, 0, 1.6, 1.0), (10, "3", 1.6, 0.9), (12, "q", 1.6, 0.9), (14, "a", 1.6, 1.0)]
    rouleau = [(k, (2, 3, 1)[k % 3], 0.8, 1.1, 12 if k % 3 == 2 else 0) for k in range(16)]   # trois cordes de banjo
    tchac = bat(kick=[(0, 0.9), (8, 0.9)], snare=[(4, 0.5), (12, 0.5)], hat=[(k, 0.9) for k in (2, 6, 10, 14)])
    sabots = bat(kick=[(0, 0.8), (8, 0.8)], snare=[(4, 0.35), (12, 0.35)], woodH=[(k, 0.7) for k in (0, 4, 8, 12)],
                 woodL=[(k, 0.6) for k in (2, 6, 10, 14)])
    m.partie("A A D A A A E E", lead=FERME_A, bass=[boum, boum, boum, monte], arp=rouleau, drums=tchac)
    m.partie("A A D A A E7", lead=FERME_A2, harm="tierces", bass=boum, arp=rouleau, drums=tchac)
    # tout le monde s'arrête et frappe avec le violon
    m.partie("A E,A", lead=FERME_CODA, harm="tierces", entree=False,
             bass=[[(0, 0, 1.6, 1.0), (4, 0, 0.8, 0.9), (6, 0, 0.8, 0.9), (8, "q", 1.6, 1.0), (12, 0, 1.6, 1.0)],
                   [(4, 0, 1.6, 1.0), (8, 0, 3.0, 1.0)]],
             drums=[bat(kick=[0, 8], snare=[4, 6, 12]), bat(snare=[4], kick=[8], crash=[8])])
    m.partie("D D A A E E7 A E", lead=FERME_B, bass=[boum, boum, boum, monte], drums=sabots, fin=ROULE,
             arp=[(k, r, ln, 1.3, *d) for k, r, ln, _, *d in rouleau])
    return m


# ------------------------------------------------------------------ la forêt : flûte, harpe et écho
FORET_A = """
E5 -  A5 -  B5 C6 -  -  | A5 -  F5 -  C5 -  -  .  | E5 G5 C6 G5 E5 -  D5 E5 | D5 -  -  -  B4 -  D5 -
E5 -  A5 -  B5 C6 -  -  | D6 C6 A5 -  F5 -  A5 -  | B5 -  G5 -  D5 -  G5 B5 | A5 -  -  -  -  -  .  .
"""
FORET_B = """
C6 -  -  A5 F5 -  A5 -  | B5 -  -  G5 D5 -  G5 -  | G5 -  -  E5 B4 -  E5 G5 | A5 -  E5 -  C5 -  -  .
F5 -  A5 -  D6 -  C6 A5 | C6 -  A5 -  E5 -  -  .  | E5 G#5 B5 -  E6 -  D6 B5 | C6 B5 G#5 -  E5 -  -  .
"""


def foret():
    m = Morceau("foret", 96, "Am", echo=(3, 0.35, 0.3),
                inst=dict(lead=dict(w="triangle", v=0.27, s=0.75, vib=14, a=0.02, echo=1),
                          arp=dict(w="triangle", v=0.08, pl=0.25, echo=1), harm=dict(w="sine", v=0.09, s=0.8, a=0.03),
                          pad=dict(v=0.035)))
    acc = "Am F C G Am F G Am"
    tenue = [(0, 0, 7.6, 0.9), (8, "q", 7.6, 0.8)]
    harpe = [(k * 2, r, 1.8, 1.0) for k, r in enumerate([0, 1, 2, 3, 2, 1, 2, 1])]
    bois = bat(kick=[(0, 0.45)], hat=[(4, 0.25), (12, 0.25)])
    liee = dict(coupe=(0.1, 0.1))
    m.partie("Am Am", arp=harpe, bass=[None, tenue], intro=True)             # la harpe seule, une fois
    m.partie(acc, lead=FORET_A, bass=tenue, arp=harpe, drums=bois, **liee)   # 3e mesure : le motif de Tecky
    m.partie("F G Em Am Dm Am E7 E7", lead=FORET_B, pad=1.0, bass=tenue, drums=bat(hat=[(4, 0.2), (12, 0.2)]),
             arp=[(k * 2, r, 1.8, 0.9) for k, r in enumerate([0, 2, 1, 3, 2, 1, 3, 2])], **liee)
    m.partie(acc, lead=FORET_A, harm="tierces", bass=tenue, arp=harpe, **liee,
             drums=bois + [(6, "woodL", 0.5), (14, "woodH", 0.4)])
    return m


# ------------------------------------------------------------------ le parc : valse de boîte à musique
PARC_A = """
F#5 - A5 - D6 -  | A5 - F#5 - E5 F#5 | G5 - B5 - D6 -   | A5 - - - F#5 -
G5 - B5 - E6 -   | C#6 - A5 - E5 -   | F#5 A5 D6 - F#6 - | E6 - - - . .
"""
PARC_A2 = """
F#5 - A5 - D6 -  | A5 - F#5 - E5 F#5 | G5 - B5 - D6 -   | A5 - - - F#5 -
G5 - B5 - E6 -   | E6 - C#6 - E5 -   | D5 F#5 A5 D6 F#6 - | D6 - - - . .
"""
PARC_B = """
B5 - D6 - B5 -   | A5 - F#5 - D5 -   | E5 - A5 - C#6 -  | D6 - - - A5 -
B5 - D6 - G6 -   | F#6 - D6 - A5 -   | G#5 - B5 - E6 -  | E6 - C#6 - A5 -
"""


def parc():
    m = Morceau("parc", 132, "D", bar=12, echo=(3, 0.3, 0.22),
                inst=dict(lead=dict(w="sine", v=0.3, pl=0.32, echo=1), harm=dict(w="sine", v=0.11, pl=0.28),
                          arp=dict(w="triangle", v=0.08, pl=0.2), bass=dict(v=0.13)))
    a1, a2 = "D D G D Em A D A", "D D G D Em A7 D D"
    valse = [(0, 0, 3.6, 1.0)]                                                # un temps de basse…
    accords = [(4, (1, 2), 1.5, 0.9, 12), (8, (1, 2), 1.5, 0.8, 12)]          # … et deux d'accords
    perles = [(k * 2, r, 1.6, 0.8, 12) for k, r in enumerate([0, 1, 2, 3, 2, 1])]
    m.partie(a1, lead=PARC_A, bass=valse, arp=accords)
    m.partie(a2, lead=PARC_A2, bass=valse, arp=accords)
    m.partie("G D A D G D E A7", lead=PARC_B, bass=valse, arp=perles)
    m.partie(a1, lead=PARC_A, harm="tierces", bass=valse + [(8, "q", 3.0, 0.6)], arp=accords + perles[1::2])
    m.partie(a2, lead=PARC_A2, harm="tierces", bass=valse + [(8, "q", 3.0, 0.6)], arp=accords + perles[1::2])
    return m


# ------------------------------------------------------------------ la zone industrielle : mécanique
INDUSTRIE_A = """
E5 E5 G5 E5 B5 -  A5 G5 | E5 E5 G5 E5 B5 -  D6 B5 | C6 -  G5 E5 G5 -  E5 C5 | D5 F#5 A5 F#5 D6 -  .  .
E5 E5 G5 E5 B5 -  A5 G5 | E5 E5 G5 E5 B5 -  D6 E6 | E6 -  C6 G5 D6 -  A5 F#5 | E5 -  .  B4 E5 -  .  .
"""
INDUSTRIE_B = """
A5 -  E5 A5 C6 -  B5 A5 | G5 -  E5 G5 B5 -  .  .  | A5 -  E5 A5 C6 -  E6 C6 | B5 -  F#5 B5 D#6 -  .  .
E5 G5 C6 G5 E5 -  D5 E5 | F#5 A5 D6 A5 F#5 -  E5 F#5 | B5 -  A5 -  F#5 -  D#5 -  | B4 D#5 F#5 B5 D#6 -  .  .
"""


def industrie():
    m = Morceau("industrie", 138, "Em",
                inst=dict(lead=dict(w=0.125, v=0.15, s=0.52), arp=dict(w=0.0625, v=0.043, s=0.32), harm=dict(w=0.25, v=0.05)))
    acc = "Em Em C D Em Em C,D Em"
    martele = [(k, 12 if k % 4 == 2 else 0, 0.7, 0.8) for k in range(16)]
    engrenage = [(k, [0, 0, 2, 0, 3, 0, 2, 0][k % 8], 0.6, 0.9) for k in range(16)]      # un motif qui tourne en rond
    usine = bat(kick=[(k, 0.9) for k in (0, 4, 8, 12)], snare=[(4, 0.9), (12, 0.9)],
                hat=[(k, 1.0 if k % 4 == 2 else 0.3) for k in range(16) if k % 2 or k % 4 == 2])
    metal = usine + [(6, "metal", 0.6), (14, "metal", 0.6)]
    piquee = dict(coupe=(0.5, 0.3))
    m.partie(acc, lead=INDUSTRIE_A, bass=martele, arp=engrenage, drums=usine, fin=ROULE, **piquee)
    m.partie(acc, lead=INDUSTRIE_A, harm="tierces", bass=martele, arp=engrenage, drums=metal, fin=ROULE, **piquee)
    # le pont : la machine ralentit (batterie à mi-temps, basse syncopée) ; mesures 5 et 6, le motif de Tecky
    m.partie("Am Em Am B C D B7 B7", lead=INDUSTRIE_B, arp=engrenage, pad=0.8, fin=TOMS, **piquee,
             bass=[(0, 0, 1.6, 1.0), (3, 0, 0.8, 0.8), (6, 0, 1.6, 0.9), (8, 0, 1.6, 1.0), (11, 12, 0.8, 0.8), (14, "a", 1.6, 0.9)],
             drums=bat(kick=[0, (10, 0.8)], snare=[8], hat=[(k, 0.5) for k in range(0, 16, 2)], metal=[(4, 0.7), (12, 0.5)]))
    m.partie(acc, lead=INDUSTRIE_A, harm="tierces", bass=martele, arp=engrenage, drums=metal, fin=TOMS, crash=True, **piquee)
    return m


# ------------------------------------------------------------------ fanfare de victoire, musique de défaite
# Trois mesures à 140, jouées une fois. La défaite est en la mineur : la mélodie descend doucement, passe par la
# tension de mi majeur (sol dièse) et se pose sur un la grave tenu. Triste mais tendre, pas moqueuse.
def fanfare():
    m = Morceau("win", 140, "C", boucle=False)
    croches = [(k, 0.9 if k % 4 == 0 else 0.6) for k in range(0, 16, 2)]
    m.partie("F G", lead="A5 -  C6 -  F6 -  E6 D6 | B5 -  D6 -  G6 -  F6 D6", harm="tierces", hv=1.3,
             bass=[(k * 2, x, 1.6, 1.0) for k, x in enumerate([0, 12, 0, 12, 0, 12, 7, 12])],
             arp=[(k, k % 4, 0.8, 1.3) for k in range(16)], drums=bat(kick=[0, 8], snare=[4, 12], hat=croches),
             fin=[(k, "snare", 0.55 + 0.15 * (k - 12)) for k in (12, 13, 14, 15)])
    m.partie("C", lead="C6 -  -  -  -  -  -  -", coupe=(0, 0),               # l'accord final, tenu
             extra=[(0, "bass", 36, 16, 1.0), (0, "bass", 48, 16, 0.6), (0, "lead", midi("E5"), 16, 0.45),
                    (0, "lead", midi("G5"), 16, 0.45), (0, "drums", "kick", 1, 1.0), (0, "drums", "snare", 1, 0.9),
                    (0, "drums", "crash", 1, 1.0)])
    return m


def defaite():
    m = Morceau("lose", 140, "Am", boucle=False)
    m.partie("Am E", lead="E5 -  D5 -  C5 -  B4 -  | A4 -  C5 -  B4 -  G#4 -", v=0.9, coupe=(0.4, 0.4),
             bass=[(0, 0, 7.6, 1.0), (8, 7, 7.6, 0.9)], arp=[(k * 2, (k * 3) % 4, 1.6, 1.1) for k in range(8)],
             drums=bat(kick=[(0, 0.6)], hat=[(8, 0.5)]))
    m.partie("Am", lead="A4 -  -  -  -  -  -  -", v=0.9, coupe=(0, 0),       # la grave, do et mi en écho
             extra=[(0, "bass", 33, 16, 1.0), (0, "bass", 45, 16, 0.5), (0, "lead", midi("C5"), 16, 0.3),
                    (0, "lead", midi("E5"), 16, 0.3), (0, "drums", "kick", 1, 0.7)])
    return m


MORCEAUX = dict(niche=niche, village=village, campagne=campagne, ferme=ferme, foret=foret, parc=parc,
                industrie=industrie, berceuse=berceuse, win=fanfare, lose=defaite)


def songs():
    """Tous les morceaux, pour le jeu (SONGS)."""
    return {k: f().construire() for k, f in MORCEAUX.items()}


# ------------------------------------------------------------------ contrôle des partitions
def controle():
    """Ce qu'une oreille entendrait tout de suite : une note longue ou posée sur un temps qui n'est pas dans
    l'accord, une note hors de la gamme, un saut de plus d'une octave."""
    noms = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    for k, f in MORCEAUX.items():
        m = f()
        s = m.construire()
        temps = [x for x in m.melodie if x[0] % m.beat == 0]
        hors = [x for x in temps if x[1] % 12 not in accord(x[2])[1]]
        etrangeres = sorted({noms[x[1] % 12] for x in m.melodie if x[1] % 12 not in m.gamme})
        sauts = [(a[0] // m.bar + 1) for a, b in zip(m.melodie, m.melodie[1:]) if abs(a[1] - b[1]) > 12]
        notes = [x[1] for x in m.melodie]
        canaux = {c: sum(e[1] == c for e in s["ev"]) for c in ("lead", "harm", "arp", "bass", "pad", "drums")}
        print(f"{k:10s} {s['total'] // m.bar:3d} mesures, {s['total'] * s['spb']:5.1f} s, reprise au pas {s['loop']}, "
              f"entrées {[e // m.bar for e in s['entries']]}, notes {canaux}")
        print(f"           mélodie {noms[min(notes) % 12]}{min(notes) // 12 - 1} à {noms[max(notes) % 12]}{max(notes) // 12 - 1}, "
              f"sur les temps : {100 - 100 * len(hors) // max(1, len(temps))} % dans l'accord ; hors gamme : {etrangeres or 'rien'} ; "
              f"sauts de plus d'une octave : {sauts or 'aucun'}")
        for st, n, acc in hors:
            print(f"             mesure {st // m.bar + 1}, pas {st % m.bar} : {noms[n % 12]} sur {acc}")
        assert all(e[0] < s["total"] for e in s["ev"]), k


if __name__ == "__main__":
    controle()
    if "--json" in sys.argv:
        import json
        print(len(json.dumps(songs(), separators=(",", ":"))) // 1024, "Ko")
