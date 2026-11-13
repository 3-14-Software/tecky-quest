"""
Les cartes changées par un épisode (carte.py : cartes/<épisode>/<nom>.json, une surcharge qui ne redit que ce qui
change) : poser une surcharge, retrouver la surcharge à partir de la carte, les refus, et l'enregistrement de
l'éditeur (editeur.enregistrer_surcharge), essayé sur une copie des cartes.

    python3 tests/surcharges.py
"""
import copy
import json
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import carte      # noqa: E402
import editeur    # noqa: E402
import episodes   # noqa: E402

echecs = 0


def ok(c, m):
    global echecs
    if not c:
        echecs += 1
        print("ÉCHEC :", m)


base = carte.charger()
# 1. poser, puis retrouver
s = {"items": base["items"][:5], "alice": None, "signs": base["signs"][:1] + [[3, 3, "Un panneau d'été"]]}
v = carte.appliquer(base, s)
ok("alice" not in v and len(v["items"]) == 5 and v["terrain"] == base["terrain"] and "alice" in base,
   "appliquer : les clés de la surcharge remplacent, null retire, le reste (et la carte de base) ne bouge pas")
ok(carte.difference(v, base) == s, "difference : la surcharge retrouvée à partir de la carte")
ok(carte.difference(base, base) == {} and carte.difference(json.loads(json.dumps(base)), base) == {}, "une carte inchangée : rien à redire")
w = copy.deepcopy(base)
w["enemies"][0][1] = float(w["enemies"][0][1])
ok(carte.difference(w, base) == {}, "6 et 6.0 : pas une différence")
ok(carte.valider_surcharge(s, base) == [], "une surcharge correcte passe (sans Alice, sans les trois indices)")
# 2. les refus
e = carte.valider_surcharge({"w": 3, "dig": base["dig"], "truc": None}, base)
ok(len(e) == 3 and "w :" in e[0] and "identique" in e[1] and "null" in e[2], "refus : taille de la carte, clé redite à l'identique, null sans objet")
ok(any("farmer" in x for x in carte.valider_surcharge({"farmer": [1]}, base)), "refus : la carte posée doit rester correcte")
ok(any("indice" in x for x in carte.valider(carte.appliquer(base, {"items": base["items"][:5]})))
   and not carte.valider(carte.appliquer(base, {"items": base["items"][:5]}), variante=True),
   "sans les indices : refusé pour une carte de base, permis pour la carte d'un épisode")
# les planches (à plat) et la falaise (un mur) ne se touchent jamais
t = [list(r) for r in base["terrain"]]
t[5][5], t[5][6] = "l", "k"
e = carte.valider(dict(base, terrain=["".join(r) for r in t]), avec_genres=False)
ok(len(e) == 1 and "les planches et la falaise" in e[0] and "5, 4" in e[0], "refus : une tuile qui mêle planches et falaise")
t[5][6], t[5][7] = ".", "k"
ok(carte.valider(dict(base, terrain=["".join(r) for r in t]), avec_genres=False) == [], "un coin d'herbe entre les deux : permis")
# 3. les surcharges du dépôt : d'un épisode qui a la carte, minimales, et la carte posée est correcte
eps = {e["id"]: e for e in episodes.charger()}
for ep, nom in carte.surcharges():
    b = carte.charger(carte.chemin(nom))
    with open(carte.surcharge(nom, ep), encoding="utf-8") as f:
        s = json.load(f)
    ok(ep in eps and nom in eps[ep]["cartes"], f"cartes/{ep}/{nom}.json : un épisode qui a cette carte")
    ok(carte.valider_surcharge(s, b) == [] and carte.difference(carte.charger_episode(nom, ep), b) == s,
       f"cartes/{ep}/{nom}.json : correcte, et ne redit que ce qui change")
ok(carte.charger_episode("monde", "printemps") == base and carte.charger_episode("monde") == base, "un épisode sans surcharge : la carte de base")
ok(episodes.valider(episodes.charger()) == [], "episodes.json : correct")
# 4. l'enregistrement de l'éditeur, sur une copie
tmp = tempfile.mkdtemp(prefix="surcharges-")
try:
    shutil.copytree(carte.DOSSIER, os.path.join(tmp, "cartes"))
    shutil.copy(carte.FICHIER, tmp)
    vrai = (carte.DOSSIER, carte.FICHIER)
    carte.DOSSIER, carte.FICHIER = os.path.join(tmp, "cartes"), os.path.join(tmp, "carte.json")
    f = carte.surcharge("pre", "ete")
    pre = carte.charger(carte.chemin("pre"))
    c = copy.deepcopy(pre)
    c["signs"][0][2] += " !"
    ok(editeur.enregistrer_surcharge(c, "pre", "ete") == [] and json.load(open(f, encoding="utf-8")) == {"signs": c["signs"]},
       "éditeur : enregistrer la carte d'un épisode n'écrit que ce qu'elle change")
    ok(open(carte.chemin("pre"), encoding="utf-8").read() == open(os.path.join(vrai[0], "pre.json"), encoding="utf-8").read(),
       "éditeur : la carte de base n'est pas touchée")
    ok(editeur.lire("pre", "ete")[1] != editeur.lire("pre")[1] and json.loads(editeur.lire("pre", "ete")[0]) == c,
       "éditeur : la carte relue est celle de l'épisode")
    ok(editeur.enregistrer_surcharge(pre, "pre", "ete") == [] and not os.path.exists(f), "éditeur : plus rien à redire, la surcharge est retirée")
    ok(editeur.enregistrer_surcharge(dict(pre, w=3), "pre", "ete") != [] and not os.path.exists(f), "éditeur : un épisode ne change pas la taille de la carte")
finally:
    carte.DOSSIER, carte.FICHIER = vrai
    shutil.rmtree(tmp, ignore_errors=True)

print("surcharges : " + ("ok" if not echecs else f"{echecs} échec(s)"))
sys.exit(1 if echecs else 0)
