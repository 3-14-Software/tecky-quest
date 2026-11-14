"""
Mesure le coût du rendu dans Firefox, sans fenêtre : le pire cas, il dessine le canevas avec le processeur.

Il faut d'abord construire le jeu (python3 pack_web.py) et servir web/tecky_quest_web sur le port 8765
(./serve.sh 8765, ou l'aperçu « tecky-web »). Puis, depuis la racine du dépôt :

    python3 tools/mesure_firefox.py [--x2] [--detail] [--sans-avance] [--carte plage] [--dossier sous-dossier] [--json sortie.json]

Le canevas est forcé à 1920 x 1080 (échelle 2), avec les images x4 (--x2 : rester en x2). La page ne fait plus
tourner le jeu : elle place la caméra, règle le soleil et chronomètre render() image par image.

- Lieux : 90 images à chaque endroit, de jour (soleil 0) et le soir (soleil 3 : ombres longues, lampadaires,
  fenêtres allumées). Moyenne et pire image, et ce que coûte chaque partie : sol, eau, ombres de ce qui bouge,
  lumière, interface, le reste (les sprites).
  --detail : en plus, les six sprites qui coûtent le plus à chaque endroit (drawSpr, par clé de l'atlas).
- Traversées : la caméra file d'ouest en est à 240 px/s sur trois bandes de la carte ; chaque bloc de sol est
  peint quand elle l'atteint ou s'en approche (buildChunk) : c'est là que naissent les à-coups. La première
  image n'est pas comptée : elle peint tout l'écran d'un coup, comme une arrivée dans une partie, sous le fondu.
  --sans-avance : sans les blocs préparés en avance (prepareGround), pour voir ce qu'ils évitent.
- Tombée du soir : sur la place du village, le soleil passe de 0 à 3 en 6 s ; les blocs de sol sont repeints
  un par image à chaque palier d'ombre.

Repère : 16,7 ms par image à 60 images par seconde. --dossier : mesurer une autre construction, copiée dans
web/tecky_quest_web/<sous-dossier> (pour comparer avec une version d'avant).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB = os.path.join(RACINE, "web", "tecky_quest_web")
PORT = 8765
LIEUX = [("niche", 4.5, 4.2), ("place du village", 49.5, 7.3), ("marché, rue", 40, 14), ("ferme", 73.9, 8.4),
         ("grande route", 30, 20), ("pré des vaches", 20, 28), ("port", 50, 35), ("verger", 62, 27),
         ("pont, rivière", 80, 43), ("parc", 20, 55), ("forêt", 78, 58)]
BANDES = [("nord (y 8)", 8), ("milieu (y 30)", 30), ("sud (y 54)", 54)]
# --carte plage : la côte de l'été (ses lieux, ses bandes ; la partie démarre là, en été)
AILLEURS = {"plage": dict(essai=[31.4, 11.9, "balade", "plage", "ete"],
                         lieux=[("parking", 31, 11), ("port", 8, 36), ("village de pêcheurs", 27, 27), ("casino", 60, 20),
                                ("jardins", 62, 30), ("plage ouest", 30, 49), ("plage est", 62, 49), ("falaises", 86, 24),
                                ("phare", 91, 37), ("campagne normande", 62, 6)],
                         bandes=[("nord (y 9)", 9), ("milieu (y 30)", 30), ("sud (y 48)", 48)])}
PREFS = {"browser.dom.window.dump.enabled": True, "privacy.reduceTimerPrecision": False,
         "privacy.resistFingerprinting": False, "browser.shell.checkDefaultBrowser": False,
         "browser.aboutwelcome.enabled": False, "datareporting.policy.dataSubmissionEnabled": False,
         "toolkit.telemetry.reportingpolicy.firstRun": False, "app.update.enabled": False,
         "browser.startup.homepage_override.mstone": "ignore", "media.autoplay.default": 0}

MESURE = r"""
(function () {
  const dire = o => dump('MESURE ' + JSON.stringify(o) + '\n');
  const pause = ms => new Promise(r => setTimeout(r, ms));
  const LIEUX = __LIEUX__, BANDES = __BANDES__, X2 = __X2__, DETAIL = __DETAIL__, SANS_AVANCE = __SANS_AVANCE__;
  const T = {}, blocs = [];
  function chrono(nom, f) {
    return function () { const t = performance.now(); const r = f.apply(this, arguments); T[nom] = (T[nom] || 0) + performance.now() - t; return r; };
  }
  function stats(v) {
    const s = v.slice().sort((a, b) => a - b), n = s.length;
    return { n, moy: v.reduce((a, b) => a + b, 0) / n, p95: s[Math.floor(n * 0.95)], max: s[n - 1] };
  }
  async function attendre(test, ms) { const t = performance.now(); while (!test() && performance.now() - t < ms) await pause(50); return test(); }

  async function tout() {
    if (!await attendre(() => typeof state !== 'undefined' && state === 'play', 30000)) { dire({ erreur: 'la partie ne démarre pas' }); return; }
    if (__ATTENTE__) await pause(__ATTENTE__);                 // (les images de la saison se chargent)
    const rendre = render;
    render = function () {}; update = function () {};          // la boucle du jeu tourne à vide
    cv.width = 1920; cv.height = 1080; scale = 2; offX = 0; offY = 0;
    ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
    if (!X2) {                                                   // (un chargement raté laisse le jeu en x2 sans rien dire)
      for (let essai = 0; essai < 3 && HD.k === 1; essai++) { HD.asked = false; loadHD(); await attendre(() => HD.k > 1, 15000); }
      if (HD.k === 1) { dire({ erreur: 'les images x4 ne se chargent pas' }); return; }
    }
    resetGround();
    dire({ debut: { hd: HD.k, canevas: [cv.width, cv.height], echelle: scale, agent: navigator.userAgent } });

    const parts = { sol: 'drawGround', avance: 'prepareGround', eau: 'drawWater', ombres: 'drawCastShadows', nuages: 'drawClouds', lumiere: 'drawLight', interface: 'drawHUD' };
    if (typeof drawClouds === 'function') drawClouds = chrono('nuages', drawClouds);
    const S = {};
    if (DETAIL) { const d0 = drawSpr; drawSpr = function (key) { const t = performance.now(); const r = d0.apply(this, arguments); S[key] = (S[key] || 0) + performance.now() - t; return r; }; }
    if (typeof drawGround === 'function') drawGround = chrono('sol', drawGround);
    if (typeof drawWater === 'function') drawWater = chrono('eau', drawWater);
    if (typeof prepareGround === 'function') prepareGround = SANS_AVANCE ? function () {} : chrono('avance', prepareGround);
    if (typeof drawCastShadows === 'function') drawCastShadows = chrono('ombres', drawCastShadows);
    if (typeof drawLight === 'function') drawLight = chrono('lumiere', drawLight);
    if (typeof drawHUD === 'function') drawHUD = chrono('interface', drawHUD);
    const peindre = buildChunk;
    buildChunk = function () { const t = performance.now(); const r = peindre.apply(this, arguments); blocs.push(performance.now() - t); return r; };

    function viser(x, y) { P.x = x; P.y = y; camX = camClampX(x - VW / 2); camY = camClampY(y - VH / 2); }
    function image() { const t = performance.now(); rendre(); return performance.now() - t; }

    // 1. lieux, de jour et le soir
    for (const s of [0, 3]) for (const [nom, tx, ty] of LIEUX) {
      sun = s; viser(tx * TS, ty * TS);
      for (let i = 0; i < 40; i++) image();                     // le sol se peint, les ombres se remettent à la longueur
      await pause(0);
      for (const k in T) delete T[k];
      for (const k in S) delete S[k];
      blocs.length = 0;
      const v = [];
      for (let i = 0; i < 90; i++) v.push(image());
      const gros = Object.entries(S).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([k, t]) => [k, t / v.length]);
      const r = stats(v), part = {};
      for (const k in parts) part[k] = (T[k] || 0) / v.length;
      part.reste = r.moy - Object.values(part).reduce((a, b) => a + b, 0);
      dire({ lieu: nom, soleil: s, image: r, part, gros });
      await pause(0);
    }

    // 2. traversées : la caméra file d'ouest en est, les blocs de sol se peignent en route
    for (const s of [0, 3]) for (const [nom, ty] of BANDES) {
      sun = s; resetGround(); blocs.length = 0;
      const v = [];
      for (let x = 8 * TS, i = 0; x < 88 * TS; x += 4, i++) {
        viser(x, ty * TS); v.push(image());
        if (i % 120 === 119) await pause(0);
      }
      v.shift();                                               // (la première image peint tout l'écran d'un coup)
      dire({ traversee: nom, soleil: s, image: stats(v), lentes: v.filter(t => t > 16.7).length, tres_lentes: v.filter(t => t > 33.3).length,
        blocs: blocs.length ? stats(blocs) : null });
      await pause(0);
    }

    // 3. la tombée du soir sur la place : les blocs de sol sont repeints à chaque palier d'ombre
    {
      const [, tx, ty] = LIEUX[1];
      sun = 0; viser(tx * TS, ty * TS);
      for (let i = 0; i < 40; i++) image();
      blocs.length = 0;
      const v = [];
      for (let i = 0; i < 360; i++) { sun = 3 * i / 359; v.push(image()); if (i % 120 === 119) await pause(0); }
      dire({ soir: 'place du village', image: stats(v), lentes: v.filter(t => t > 16.7).length, tres_lentes: v.filter(t => t > 33.3).length,
        blocs: blocs.length ? stats(blocs) : null });
    }
    dire({ fin: true });
  }
  tout().catch(e => dire({ erreur: String(e && e.stack || e) }));
})();
"""


def page(dossier, x2, detail=False, sans_avance=False, carte=None):
    base = open(os.path.join(dossier, "index.html"), encoding="utf-8").read()
    k = base.index("<script>") + len("<script>")
    a = AILLEURS.get(carte)
    js = (MESURE.replace("__LIEUX__", json.dumps(a["lieux"] if a else LIEUX, ensure_ascii=False))
          .replace("__BANDES__", json.dumps(a["bandes"] if a else BANDES, ensure_ascii=False)).replace("__ATTENTE__", "8000" if a else "0").replace("__X2__", "true" if x2 else "false")
          .replace("__DETAIL__", "true" if detail else "false")
          .replace("__SANS_AVANCE__", "true" if sans_avance else "false"))
    return base[:k] + "\nconst ESSAI = " + json.dumps(a["essai"] if a else [4.5, 4.2, "balade"]) + ";\n" + base[k:] + "<script>\n" + js + "</script>\n"


def mesurer(sous_dossier="", x2=False, detail=False, sans_avance=False, delai=600, carte=None):
    dossier = os.path.join(WEB, sous_dossier) if sous_dossier else WEB
    fichier = os.path.join(dossier, "_mesure.html")
    open(fichier, "w", encoding="utf-8").write(page(dossier, x2, detail, sans_avance, carte))
    profil = tempfile.mkdtemp(prefix="mesure-")
    with open(os.path.join(profil, "user.js"), "w") as f:
        for k, v in PREFS.items():
            f.write(f'user_pref("{k}", {json.dumps(v)});\n')
    adresse = f"http://localhost:{PORT}/{sous_dossier + '/' if sous_dossier else ''}_mesure.html"
    p = subprocess.Popen(["firefox", "--headless", "--no-remote", "--profile", profil, "--window-size", "1920,1080", adresse],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    lignes, t0 = [], time.time()
    try:
        os.set_blocking(p.stdout.fileno(), False)
        reste = ""
        while time.time() - t0 < delai and p.poll() is None:
            try:
                bout = os.read(p.stdout.fileno(), 65536)
            except BlockingIOError:
                bout = b""
            if not bout:
                time.sleep(0.2)
                continue
            reste += bout.decode("utf-8", "replace")
            *finies, reste = reste.split("\n")
            for ligne in finies:
                if ligne.startswith("MESURE "):
                    lignes.append(json.loads(ligne[7:]))
                    print(".", end="", flush=True, file=sys.stderr)
            if lignes and ("fin" in lignes[-1] or "erreur" in lignes[-1]):
                break
    finally:
        p.terminate()
        try:
            p.wait(10)
        except subprocess.TimeoutExpired:
            p.kill()
        os.remove(fichier)
        shutil.rmtree(profil, ignore_errors=True)
    print(file=sys.stderr)
    return lignes


def ms(v):
    return f"{v:5.1f}".replace(".", ",")


def rapport(lignes):
    out = []
    for o in lignes:
        if "erreur" in o:
            out.append("ERREUR : " + o["erreur"])
        elif "debut" in o:
            d = o["debut"]
            out.append(f"Firefox, canevas {d['canevas'][0]} x {d['canevas'][1]}, échelle {d['echelle']}, "
                       f"images x{2 * d['hd']} — millisecondes par image (16,7 = 60 images par seconde)")
            out.append(f"{'lieu':<20}{'soleil':>7}{'moy.':>7}{'pire':>7} |{'sol':>6}{'eau':>6}{'ombres':>7}{'nuages':>7}{'lumière':>8}"
                       f"{'interf.':>8}{'reste':>7}")
        elif "lieu" in o:
            i, q = o["image"], o["part"]
            out.append(f"{o['lieu']:<20}{o['soleil']:>7}{ms(i['moy']):>7}{ms(i['max']):>7} |{ms(q['sol'] + q.get('avance', 0)):>6}{ms(q['eau']):>6}"
                       f"{ms(q['ombres']):>7}{ms(q.get('nuages', 0)):>7}{ms(q['lumiere']):>8}{ms(q['interface']):>8}{ms(q['reste']):>7}")
            if o.get("gros"):
                out.append("    " + ", ".join(f"{k} {ms(t).strip()}" for k, t in o["gros"]))
        elif "traversee" in o or "soir" in o:
            i, b = o["image"], o["blocs"]
            nom = ("traversée " + o["traversee"] + f", soleil {o['soleil']}") if "traversee" in o else "tombée du soir, " + o["soir"]
            out.append(f"{nom} : {i['n']} images, moy. {ms(i['moy']).strip()}, 95 % sous {ms(i['p95']).strip()}, pire "
                       f"{ms(i['max']).strip()} ; {o['lentes']} au-delà de 16,7 ms, {o['tres_lentes']} au-delà de 33,3 ms"
                       + (f" ; {b['n']} blocs de sol peints, moy. {ms(b['moy']).strip()}, pire {ms(b['max']).strip()}" if b else ""))
    return "\n".join(out)


if __name__ == "__main__":
    args = sys.argv[1:]
    sous = args[args.index("--dossier") + 1] if "--dossier" in args else ""
    lignes = mesurer(sous, "--x2" in args, "--detail" in args, "--sans-avance" in args,
                     carte=args[args.index("--carte") + 1] if "--carte" in args else None)
    if "--json" in args:
        json.dump(lignes, open(args[args.index("--json") + 1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(rapport(lignes))
    if not lignes or "fin" not in lignes[-1]:
        sys.exit("mesure incomplète")
