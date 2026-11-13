"""
Les épisodes du jeu (lot 6 de PLAN_V2.md) : un par saison, joués l'un après l'autre.

episodes.json en donne la liste, dans l'ordre où ils s'ouvrent :

    id        son nom dans le jeu (sauvegarde, records, textes `episodes.<id>.nom` / `.note` de textes/fr.json)
    saison    printemps, ete, automne ou hiver (palette : saisons.py)
    cartes    les cartes où il se joue (carte.noms()) ; un passage vers une carte qui n'en fait pas partie est fermé ;
              cartes/<id>/<carte>.json, s'il existe, dit ce que l'épisode change à cette carte (carte.py : surcharge)
    depart    celle où la partie commence (elle a la niche : `start`)
    voyage    (facultatif) la carte où l'on part en voiture dès le début : la partie commence par une cinématique
              sur la carte de départ, la voiture prend le tunnel, et le jeu se joue sur cette carte-là, à partir
              de son point `start` ; à pied, les tunnels restent « pour les voitures » (game.js : startTrip())
    chantier  vrai tant qu'il n'est pas jouable : le jeu ne le propose pas (sauf avec ?chantier dans l'adresse)

    python3 episodes.py       # vérifie episodes.json

pack_web.py embarque la liste dans la page (EPISODES de game.js).
"""
import json
import os
import sys

import carte

ROOT = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ROOT, "episodes.json")
SAISONS = ("printemps", "ete", "automne", "hiver")
CHAMPS = ("id", "saison", "cartes", "depart", "voyage", "chantier")


def charger(chemin=FICHIER):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)["episodes"]


def valider(eps, cartes=None):
    """Les problèmes d'une liste d'épisodes (vide : tout va bien). cartes : { nom: carte chargée } ; par défaut,
    celles du dépôt."""
    if cartes is None:
        cartes = {n: carte.charger(carte.chemin(n), verifier=False) for n in carte.noms()}
    pb = []
    if not eps:
        return ["aucun épisode"]
    vus = set()
    for i, e in enumerate(eps):
        nom = e.get("id") or f"n° {i + 1}"
        for k in e:
            if k not in CHAMPS:
                pb.append(f"épisode « {nom} » : champ inconnu « {k} »")
        if not isinstance(e.get("id"), str) or not e["id"].isidentifier():
            pb.append(f"épisode « {nom} » : il lui faut un id simple (lettres, chiffres, _)")
        if e.get("id") in vus:
            pb.append(f"épisode « {nom} » : id en double")
        vus.add(e.get("id"))
        if e.get("saison") not in SAISONS:
            pb.append(f"épisode « {nom} » : saison « {e.get('saison')} » inconnue ({', '.join(SAISONS)})")
        les = e.get("cartes") or []
        for c in les:
            if c not in cartes:
                pb.append(f"épisode « {nom} » : la carte « {c} » n'existe pas")
        dep = e.get("depart")
        if dep not in les:
            pb.append(f"épisode « {nom} » : la carte de départ « {dep} » n'est pas dans ses cartes")
        elif dep in cartes and "start" not in cartes[dep]:
            pb.append(f"épisode « {nom} » : la carte de départ « {dep} » n'a pas de niche (start)")
        if "voyage" in e:
            v = e["voyage"]
            if v not in les or v == dep:
                pb.append(f"épisode « {nom} » : le voyage mène à une autre de ses cartes, pas à « {v} »")
            elif v in cartes and "start" not in cartes[v]:
                pb.append(f"épisode « {nom} » : la carte du voyage « {v} » n'a pas de point de départ (start)")
            elif not any(q[1] == v for q in cartes.get(dep, {}).get("passages", ())):
                pb.append(f"épisode « {nom} » : aucun tunnel de « {dep} » ne mène à « {v} »")
        if "chantier" in e and not isinstance(e["chantier"], bool):
            pb.append(f"épisode « {nom} » : chantier vaut true ou false")
        # chaque carte de l'épisode se rejoint depuis celle du départ, par les passages qui restent dans l'épisode
        atteintes, pile = {dep}, [dep]
        while pile:
            for _, vers, _ in cartes.get(pile.pop(), {}).get("passages", ()):
                if vers in les and vers not in atteintes:
                    atteintes.add(vers)
                    pile.append(vers)
        for c in les:
            if c in cartes and c not in atteintes:
                pb.append(f"épisode « {nom} » : aucun passage ne mène à la carte « {c} » depuis « {dep} »")
    # les surcharges (cartes/<épisode>/<carte>.json) : d'un épisode qui existe, pour une de ses cartes
    for ep, c in carte.surcharges():
        e = next((e for e in eps if e.get("id") == ep), None)
        if e is None:
            pb.append(f"cartes/{ep}/{c}.json : pas d'épisode « {ep} »")
        elif c not in (e.get("cartes") or []):
            pb.append(f"cartes/{ep}/{c}.json : la carte « {c} » n'est pas de l'épisode « {ep} »")
    if eps and eps[0].get("chantier"):
        pb.append("le premier épisode ne peut pas être en chantier : c'est par lui que le jeu commence")
    return pb


if __name__ == "__main__":
    pb = valider(charger())
    for p in pb:
        print("PB", p)
    if pb:
        sys.exit(1)
    print("episodes.json : " + ", ".join(e["id"] + (" (en chantier)" if e.get("chantier") else "") for e in charger()))
