# Tecky Quest — contexte pour Claude Code

Mini RPG en vue de dessus, fait pour Christophe (3.14 Software, développeur Java, Fedora, il parle français) :
Tecky, le teckel au harnais rouge, cherche Alice (la fille de Christophe, 5 ans). Deux livrables issus des mêmes sources :
une **version web** (Canvas, une seule page HTML, PWA) et un **kit d'assets GameMaker Studio 2** (`GAMEMAKER.md`).
Langue : tout en français (interface du jeu, commentaires, README, messages de commit). Style visuel : aplats de couleurs,
contour brun `#3A1E12`, lignes simples, ambiance mignonne. Les photos de référence de Tecky et d'Alice ne sont pas dans le dépôt
(vie privée) : ne pas redessiner les personnages sans les demander à Christophe.

## Commandes

```bash
pip install -r requirements.txt           # cairosvg, pillow, numpy (+ Node 18+ pour les tests)
python3 pack_web.py                       # web/index.html, web/tecky_quest_web/ (autonome), atlas, niveau
python3 build.py                          # kit GameMaker -> out/
./tests/run_all.sh                        # reconstruit puis lance tous les tests (doit finir avec exit=0)
./publish_docs.sh                         # copie la version autonome dans docs/ (GitHub Pages)
```

Jeu en ligne : https://cgerardin.github.io/tecky-quest/ — publié par `.github/workflows/pages.yml` à chaque push touchant `docs/`.
Pour livrer une modification : `./tests/run_all.sh && ./publish_docs.sh`, commit (docs/ inclus), push sur `main`.
`web/` et `out/` sont générés et ignorés par Git ; `docs/` est commité.

## Architecture

- `spritelib.py` : classe `Drawing` (parts SVG, silhouette dessinée en premier avec un trait épais = contour propre),
  `render_svg(svg, w, h, scale, pad)`, strips `_stripN`. Les vues gauches sont le miroir des vues droites.
- `tecky.py`, `alice.py`, `enemies.py` (roquet, bouledogue, molosse/doberman), `items.py`, `decor.py`, `tiles.py`, `hud.py` :
  dessins et animations. `tiles.py` : tileset Wang/marching squares de 16 tuiles par transition (bits NO=1, NE=2, SO=4, SE=8),
  tuile 0 vide, 16 colonnes, `PAIRS`, `PRIORITY`, `resolve()`.
- `music.py` : **source unique** de la musique (thème « Promenade de Tecky », 32 mesures, boucle ; fanfare de victoire de 3 mesures).
  Génère les WAV GameMaker et les données `SONG`/`WINSONG` jouées par le séquenceur WebAudio du jeu.
- `pack_web.py` : atlas (frames rognées), niveau (`MW=40`, `MH=24` tuiles, positions des décors/objets/chiens/trésors `DIG`),
  `index.html` à partir de `web_src/index.template.html` + `game.js`, paquet autonome (manifest, service worker, icônes, `serve.sh`).
  Lance `web_src/check_placement.js` : rien dans l'eau ou un obstacle, trésors atteignables.
- `web_src/game.js` : tout le moteur. Monde en pixels x2 (tuile = 64), caméra 960x540, interface 1920x1080 (`GW`/`GH`).

## Règles de jeu (à ne pas casser)

- Vie : 2 PV par os ; départ **3 os** (`START_BONES`), plafond 8. Un **os** rend un os perdu *jusqu'au maximum courant* (inutile à
  vie pleine, il reste au sol). Une **saucisse** ajoute un os au maximum et soigne tout.
- Actions : X aboie (repousse), C **gratte** près d'un trésor enterré (traces de pattes), sinon C **mord**.
  Le **doberman est immunisé aux aboiements** (`barkImmune`) : il faut le mordre (Tecky l'explique, bulle « Même pas peur ! »).
- Trésors (médaille 100, jouet pouic-pouic 50, balle 20) : jamais dans l'eau — `check_placement.js` le vérifie.
- Fin : retrouver Alice → dialogue + fanfare (`Music.start('win')`, une seule fois, le thème ne repart pas) → écran de victoire.

## Pièges connus

- **Marge de sécurité `PAD`** (spritelib, 6 unités) : tout sprite est rendu avec un cadre agrandi, sinon les contours et animations
  (rebond de la médaille, chiffres, queue du KO) se font couper au bord. Les origines dans `pack_web.py` ajoutent `M = PAD * S`.
  Tout nouveau sprite passe par `render_svg(..., PAD)` ; `tests/edges.py` détecte ceux qui touchent encore le bord
  (seul `hud/enemy_bar_fill` est volontairement concerné).
- **Panneaux 9-slice** (`drawNine`) : assemblés une fois en canvas hors écran puis posés d'un bloc, sinon des jointures
  apparaissent sur fond translucide. Texte long : `para()` / `wrap()` (régler `ctx.font` avant de mesurer), jamais `text()` seul.
- **KO des chiens/Tecky** : la vue « sur le dos » est un retournement vertical calculé (`enemies.py`) ; la queue de Tecky est
  dessinée avant le corps pour que sa base soit cachée (sinon elle se détache).
- **IA des chiens** : `steer()` contourne les obstacles en choisissant le côté le plus court (simulation avec `moveActor`) et
  garde ce côté tant que la route directe est barrée (grillages longs). Ne pas revenir à un détour de durée fixe : tremblement.
  Tests : `tests/obstacles.js`, `fence.js`, `fence_scan.js` (210 cas, 0 clignotement de direction).
- Les tests Node exécutent le script de `web/index.html` dans un `vm` avec canvas/audio simulés ; `tests/game_full.js` est une
  copie générée (`tests/regen.py`) — la régénérer après toute modif de `game.js` (fait par `run_all.sh`).
- Dialogues : 3 lignes maximum affichées ; chaîne longue = la découper en plusieurs répliques.
- Le service worker de `docs/` est réseau d'abord avec repli cache : pas de version à incrémenter à chaque livraison.

## Reste à faire

Aucune demande en attente à la date du dernier commit.
