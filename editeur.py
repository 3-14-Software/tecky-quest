#!/usr/bin/env python3
"""
Éditeur de carte de Tecky Quest (outil de développement) : une page web locale pour modifier carte.json à la souris.

    python3 editeur.py              # puis ouvrir http://127.0.0.1:8770/
    python3 editeur.py --port 8771

Le serveur n'écoute que sur cette machine (127.0.0.1). Au démarrage, il dessine l'atlas des sprites et le tileset
(une dizaine de secondes), puis il sert :
  /                     la page de l'éditeur (dossier editeur/)
  /atlas.png, .json     les sprites du jeu ; /tiles.png : le tileset, sans les tuiles composées
  /tuile?c=NO,NE,SO,SE  une tuile composée (trois terrains ou plus), dessinée à la demande ; suivie de « ,x,y » : la
                        place de la tuile, pour les textures qui en dépendent (tiles.phase() : paroi, lande)
  /infos.json           ce que la page doit savoir du jeu (terrains, genres, sprites, collisions…)
  /carte.json           lecture (GET) et enregistrement (PUT, avec If-Match : refusé si le fichier a changé entre-temps) ;
                        ?carte=nom : une carte annexe ; &episode=id : la carte telle que cet épisode la joue (lue sous
                        sa surcharge cartes/<id>/<nom>.json ; enregistrer n'écrit que ce qui diffère de la carte de base)
  /verifier (POST)      construit le jeu (pack_web.py), vérifie les placements et la liste des voix
  /voix (POST)          met à jour la liste des voix (node tools/export_voix.js)
  /essai (POST)         prépare web/essai.html : le jeu, Tecky posé à l'endroit choisi ; /essai.html le sert
"""
import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(ROOT, "editeur")
WEB = os.path.join(ROOT, "web")
sys.path.insert(0, ROOT)

import carte  # noqa: E402
import episodes  # noqa: E402
import tiles  # noqa: E402

TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".png": "image/png", ".json": "application/json; charset=utf-8", ".svg": "image/svg+xml"}
BUILD = threading.Lock()       # une seule construction à la fois
S = 2                          # échelle du jeu web (pack_web.S)


def png(im):
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


def run(cmd, timeout=600):
    """Lance une commande dans le dépôt : (code de retour, sortie)."""
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr).strip()


class Donnees:
    """Ce que le serveur prépare une fois : atlas, tileset, infos sur le jeu."""

    def __init__(self):
        t = time.time()
        print("Éditeur de carte : dessin des sprites et des tuiles…", flush=True)
        try:
            import pack_web
        except ValueError as e:              # carte.json invalide (modifié à la main ?)
            raise SystemExit(f"{e}\nCorrige carte.json (python3 carte.py dit ce qui ne va pas), puis relance l'éditeur.")
        atlas, self.meta = pack_web.pack(pack_web.collect())
        self.atlas = png(atlas)
        self.tiles = png(tiles.tileset(S))
        self.tuiles = {}
        self.infos = infos()
        self.jeu = None                    # FOOT, RAILS… lus dans le jeu construit (jeu_infos)
        self.jeu_infos()
        print(f"Prêt en {time.time() - t:.0f} s.", flush=True)

    def jeu_infos(self):
        """Collisions des décors, décors plats, portées des actions : lues dans web/index.html (check_placement.js)."""
        if not os.path.exists(os.path.join(WEB, "index.html")):
            return
        code, out = run(["node", "web_src/check_placement.js", "web/index.html", "--infos"], 120)
        if code == 0:
            try:
                self.jeu = json.loads(out.splitlines()[-1])
            except (ValueError, IndexError):
                pass

    def tuile(self, cs):
        k = ",".join(str(c) for c in cs)
        if k not in self.tuiles:
            self.tuiles[k] = png(tiles.composite(list(cs), S, seed=tiles.composite_seed(cs)))
        return self.tuiles[k]


def infos():
    """Ce que la page doit savoir du jeu : terrains et tileset (pour calculer le sol comme pack_web), genres permis,
    sprites, listes fixes ou indexées par la sauvegarde, musiques des zones."""
    import pack_web
    return {
        "legende": carte.LEGENDE, "priority": tiles.PRIORITY, "pairs": tiles.PAIRS, "cols": tiles.COLS,
        "largeur": tiles.LARGEUR,
        "suivies": list(tiles.SUIVIES), "phases": list(tiles.PHASES),       # textures qui dépendent de la place de la tuile                     # colonnes de l'image du tileset (la tuile n° i : i % largeur, i // largeur)
        "overlays": [n for n, _ in tiles.OVERLAYS], "overlayRow": tiles.OVERLAY_ROW,
        "compositeBase": tiles.COMPOSITE_BASE, "fullVariants": pack_web.FULL_VARIANTS,
        "grassVariants": pack_web.GRASS_VARIANTS, "ts": pack_web.TS, "lisiere": pack_web.lisiere.RING,
        "genres": carte.genres(), "sprites": carte.SPRITES, "acteurs": carte.ACTEURS, "tailles": carte.TAILLES, "indexees": carte.INDEXEES,
        "indices": carte.INDICES, "musiques": carte.MUSIQUES, "decorsDeduits": carte.DECORS_DEDUITS,
        # décors redessinés (nature, bâtiments, mobilier) : nom du décor -> ses modèles et leur tirage (MAP.variants)
        "variants": {n: [noms, tirage] for n, (noms, tirage) in pack_web.nature.VARIANTES.items()},
        # les cartes du jeu (carte.noms()) : celle du monde, puis les annexes ; la page en ouvre une (?carte=nom)
        "cartes": carte.noms(),
        # les épisodes et leurs cartes : la page ouvre une carte telle qu'un épisode la joue (?carte=nom&episode=id)
        "episodes": [{"id": e["id"], "cartes": e["cartes"]} for e in episodes.charger()],
    }


def etag(b):
    return '"' + hashlib.sha1(b).hexdigest()[:16] + '"'


def a_jour():
    """web/index.html est-il plus récent que tout ce dont il dépend (carte, moteur, construction) ?"""
    out = os.path.join(WEB, "index.html")
    if not os.path.exists(out):
        return False
    t = os.path.getmtime(out)
    src = [carte.chemin(n) for n in carte.noms()] + [carte.surcharge(n, ep) for ep, n in carte.surcharges()]
    src.append(episodes.FICHIER)
    src += [os.path.join(ROOT, "web_src", "game.js"), os.path.join(ROOT, "web_src", "index.template.html")]
    src += [os.path.join(ROOT, f) for f in os.listdir(ROOT) if f.endswith(".py")]
    return all(os.path.getmtime(f) <= t for f in src if os.path.exists(f))


def construire(force=True):
    """pack_web.py (jeu, puis vérification des placements), tests/regen.py : (ok, sortie)."""
    if not force and a_jour():
        return True, "(jeu déjà à jour)"
    code, out = run([sys.executable, "pack_web.py"])
    built = os.path.exists(os.path.join(WEB, "index.html"))
    if built:
        run([sys.executable, "tests/regen.py"])
    return code == 0 or built, out


def carte_demandee(q):
    """Le nom de la carte d'une requête (?carte=nom, ou « carte » dans le corps) : une carte qui existe, sinon le monde."""
    nom = q.get("carte") if isinstance(q, dict) else None
    nom = nom[0] if isinstance(nom, list) else nom
    return nom if nom in carte.noms() else carte.MONDE


def episode_demande(q, nom):
    """L'épisode d'une requête (?episode=id, ou « episode » dans le corps) : un épisode qui a la carte `nom`, sinon
    None (la carte de base)."""
    ep = q.get("episode") if isinstance(q, dict) else None
    ep = ep[0] if isinstance(ep, list) else ep
    return ep if any(e["id"] == ep and nom in e["cartes"] for e in episodes.charger()) else None


def lire(nom, ep=None):
    """Le fichier servi à la page et son empreinte : la carte de base, ou — pour un épisode — la carte sous sa
    surcharge (l'empreinte couvre alors les deux fichiers : l'un ou l'autre a-t-il changé sur le disque ?)."""
    base = open(carte.chemin(nom), "rb").read()
    if not ep:
        return base, etag(base)
    f = carte.surcharge(nom, ep)
    sur = open(f, "rb").read() if os.path.exists(f) else b""
    c = carte.appliquer(json.loads(base), json.loads(sur)) if sur else json.loads(base)
    return carte.texte(c).encode("utf-8"), etag(base + b"\0" + sur)


def enregistrer_surcharge(c, nom, ep):
    """Écrit ce que la carte c (celle de la page) change à la carte de base : cartes/<ep>/<nom>.json ; plus rien à
    redire : le fichier est retiré. Renvoie les erreurs (vide : c'est écrit)."""
    base = carte.charger(carte.chemin(nom), verifier=False)
    s = carte.difference(c, base)
    err = [f"{k} : un épisode ne change pas cette clé de la carte" for k in carte.FIXES if c.get(k) != base.get(k)]
    err = err or carte.valider_surcharge(s, base)
    if err:
        return err
    f = carte.surcharge(nom, ep)
    if s:
        os.makedirs(os.path.dirname(f), exist_ok=True)
        carte.enregistrer(s, f)
    elif os.path.exists(f):
        os.remove(f)
        if not os.listdir(os.path.dirname(f)):
            os.rmdir(os.path.dirname(f))
    return []


def verifier(d, nom=carte.MONDE, ep=None):
    with BUILD:
        ok, out = construire()
        res = {"construction": out, "construit": ok, "problemes": [], "atteint": None, "voix": "", "voixAJour": True}
        if not ok:
            return res
        code, pl = run(["node", "web_src/check_placement.js", "web/index.html", "--json", "--carte", nom]
                       + (["--episode", ep] if ep else []), 300)
        try:
            j = json.loads(pl.splitlines()[-1])
            res["problemes"], res["atteint"], res["resume"] = j["problemes"], j["atteint"], j["resume"]
        except (ValueError, IndexError, KeyError):
            res["problemes"] = [{"texte": "vérification des placements impossible : " + pl[-400:]}]
        code, vx = run(["node", "tools/export_voix.js", "--check"], 300)
        res["voix"], res["voixAJour"] = vx, code == 0 and "PB" not in vx
        d.jeu_infos()
        res["jeu"] = d.jeu
        return res


def voix():
    with BUILD:
        ok, out = construire(force=False)
        if not ok:
            return {"ok": False, "sortie": out}
        code, vx = run(["node", "tools/export_voix.js"], 300)
        return {"ok": code == 0, "sortie": vx}


def essai(x, y, mode, nom=carte.MONDE, ep=None):
    with BUILD:
        ok, out = construire(force=False)
        if not ok:
            return {"ok": False, "sortie": out}
        html = open(os.path.join(WEB, "index.html"), encoding="utf-8").read()
        k = html.index("<script>") + len("<script>")
        html = html[:k] + f"\nconst ESSAI = {json.dumps([round(x, 2), round(y, 2), mode, nom, ep])};\n" + html[k:]
        with open(os.path.join(WEB, "essai.html"), "w", encoding="utf-8") as f:
            f.write(html)
        return {"ok": True, "url": "/essai.html?t=" + str(int(time.time()))}


class Handler(BaseHTTPRequestHandler):
    d = None
    port = 8770

    def log_message(self, fmt, *args):
        if not self.path.startswith(("/tuile", "/atlas", "/tiles")):
            sys.stderr.write("  " + fmt % args + "\n")

    def envoyer(self, code, body, ctype="application/json; charset=utf-8", extra=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False)
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def hote_ok(self):
        """Seulement les pages servies par l'éditeur lui-même (pas un autre site qui viserait 127.0.0.1)."""
        host = self.headers.get("Host", "")
        if host not in (f"127.0.0.1:{self.port}", f"localhost:{self.port}"):
            self.envoyer(403, {"erreur": "hôte refusé"})
            return False
        origin = self.headers.get("Origin")
        if origin and origin not in (f"http://127.0.0.1:{self.port}", f"http://localhost:{self.port}"):
            self.envoyer(403, {"erreur": "origine refusée"})
            return False
        return True

    def corps(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def do_GET(self):
        if not self.hote_ok():
            return
        u = urlparse(self.path)
        p, d = u.path, self.d
        if p == "/":
            p = "/index.html"
        if p == "/atlas.png":
            return self.envoyer(200, d.atlas, "image/png")
        if p == "/atlas.json":
            return self.envoyer(200, d.meta)
        if p == "/tiles.png":
            return self.envoyer(200, d.tiles, "image/png")
        if p == "/infos.json":
            return self.envoyer(200, dict(d.infos, jeu=d.jeu))
        if p == "/tuile":
            cs = (parse_qs(u.query).get("c") or [""])[0].split(",")
            if len(cs) == 6 and cs[4].isdigit() and cs[5].isdigit():      # (suivis de la place de la tuile : tiles.phase())
                cs = cs[:4] + [int(cs[4]), int(cs[5])]
            if len(cs) not in (4, 6) or any(c not in tiles.PRIORITY for c in cs[:4]):
                return self.envoyer(400, {"erreur": "c=NO,NE,SO,SE (noms de terrains), suivis au besoin de la place x,y"})
            return self.envoyer(200, d.tuile(cs), "image/png", {"Cache-Control": "max-age=3600"})
        if p == "/carte.json":
            q = parse_qs(u.query)
            nom = carte_demandee(q)
            b, e = lire(nom, episode_demande(q, nom))
            return self.envoyer(200, b, extra={"ETag": e})
        if p == "/essai.html":
            f = os.path.join(WEB, "essai.html")
            if os.path.exists(f):
                return self.envoyer(200, open(f, "rb").read(), TYPES[".html"])
            return self.envoyer(404, "Pas encore d'essai : clic droit sur la carte, « Essayer ici ».", "text/plain; charset=utf-8")
        name = p.lstrip("/")
        f = os.path.join(PAGE, name)
        if "/" not in name and os.path.splitext(name)[1] in TYPES and os.path.isfile(f):
            return self.envoyer(200, open(f, "rb").read(), TYPES[os.path.splitext(name)[1]])
        self.envoyer(404, {"erreur": "introuvable"})

    def do_PUT(self):
        if not self.hote_ok():
            return
        u = urlparse(self.path)
        if u.path != "/carte.json":
            return self.envoyer(404, {"erreur": "introuvable"})
        nom = carte_demandee(parse_qs(u.query))
        ep = episode_demande(parse_qs(u.query), nom)
        fichier = carte.surcharge(nom, ep) if ep else carte.chemin(nom)
        actuel, empreinte = lire(nom, ep)
        if self.headers.get("If-Match") != empreinte:
            return self.envoyer(409, {"erreur": os.path.basename(fichier) + " a changé sur le disque depuis son chargement (autre éditeur, "
                                                "git…) : recharge la page pour repartir de la version du disque."})
        try:
            c = json.loads(self.corps().decode("utf-8"))
        except ValueError as e:
            return self.envoyer(400, {"erreur": f"JSON illisible : {e}"})
        if ep:                                # la carte d'un épisode : n'écrire que ce qu'elle change à la carte de base
            err = enregistrer_surcharge(c, nom, ep) if isinstance(c, dict) else ["un objet JSON"]
            if err:
                return self.envoyer(400, {"erreur": "carte refusée", "details": err})
            b, e = lire(nom, ep)
            return self.envoyer(200, {"ok": True, "change": b != actuel}, extra={"ETag": e})
        err = carte.valider(c) if isinstance(c, dict) else ["un objet JSON"]
        if not err and (c.get("annexe") is True) != (nom != carte.MONDE):
            err = ["« annexe » : la carte du monde ne l'est pas, les autres le sont"]
        if err:
            return self.envoyer(400, {"erreur": "carte refusée", "details": err})
        b = carte.enregistrer(c, fichier).encode("utf-8")
        self.envoyer(200, {"ok": True, "change": b != actuel}, extra={"ETag": etag(b)})

    def do_POST(self):
        if not self.hote_ok():
            return
        p = urlparse(self.path).path
        try:
            q = json.loads(self.corps().decode("utf-8") or "{}")
        except ValueError:
            q = {}
        if p == "/verifier":
            return self.envoyer(200, verifier(self.d, carte_demandee(q), episode_demande(q, carte_demandee(q))))
        if p == "/voix":
            return self.envoyer(200, voix())
        if p == "/essai":
            try:
                x, y = float(q["x"]), float(q["y"])
            except (KeyError, TypeError, ValueError):
                return self.envoyer(400, {"erreur": "x, y en tuiles"})
            return self.envoyer(200, essai(x, y, "balade" if q.get("mode") == "balade" else "aventure", carte_demandee(q),
                                            episode_demande(q, carte_demandee(q))))
        self.envoyer(404, {"erreur": "introuvable"})


def main():
    ap = argparse.ArgumentParser(description="Éditeur de carte de Tecky Quest")
    ap.add_argument("--port", type=int, default=8770)
    ap.add_argument("--infos", action="store_true", help="écrit /infos.json sur la sortie (pour les tests) et s'arrête")
    a = ap.parse_args()
    if a.infos:
        print(json.dumps(infos(), ensure_ascii=False))
        return
    Handler.d = Donnees()
    Handler.port = a.port
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print(f"Éditeur de carte : http://127.0.0.1:{a.port}/   (Ctrl+C pour arrêter)", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
