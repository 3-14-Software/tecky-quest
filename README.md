# Tecky Quest

Mini RPG en vue de dessus : **Tecky**, le teckel au harnais rouge, part à la recherche d'**Alice**, qui joue à
cache-cache. Il suit les affaires qu'elle a semées (sa barrette, sa chaussure, son doudou) : chacune indique où chercher
ensuite, et Alice ne sort de sa cachette qu'une fois les trois retrouvées. En chemin, Tecky aboie pour repousser les
chiens (dont les chiens de berger, qui chargent), gratte la terre pour déterrer des trésors, ramasse des os (qui rendent
de la vie) et des saucisses (qui ajoutent un os de vie maximum). Il traverse campagne, route (gare aux voitures :
mieux vaut passer par les passages piétons), village, zone industrielle, ferme, rivière (un seul pont), forêt et parc.

Tout est généré par du code : sprites en SVG (aplats + contour), tileset, décors, HUD, musique chiptune, niveau.

- **Jouer** : https://3-14-software.github.io/tecky-quest/ (clavier : flèches/ZQSD, X aboyer, C mordre (ou gratter, ou lire un panneau), P pause, F plein écran, M son ; tactile sur téléphone).
- **Kit GameMaker Studio 2** (sprites en strips x1/x2, tileset, décor, HUD, sons) : voir [GAMEMAKER.md](GAMEMAKER.md).

## Construire

Prérequis : Python 3 avec `cairosvg`, `Pillow`, `numpy` ; Node 18+ pour les tests.

```bash
pip install -r requirements.txt

python3 pack_web.py      # version web  -> web/index.html (une seule page) + web/tecky_quest_web/ (autonome, PWA)
python3 build.py         # kit GameMaker -> out/ (sprites, tileset, HUD, audio, aperçus)
python3 music.py         # WAV de la musique et de la fanfare -> out/audio/
./publish_docs.sh        # copie la version autonome dans docs/ (servie par GitHub Pages)
```

Jouer en local : `cd web/tecky_quest_web && ./serve.sh` (serveur sur le réseau local, pratique pour tester sur téléphone).

## Tests

```bash
./tests/run_all.sh
```

Simulation sans navigateur (Node, canvas et audio simulés) : déroulé complet de la partie, collisions, combat, grattage,
règles de vie, immunité du doberman aux aboiements, onde montrant la portée des aboiements, bouton « Lire »,
morsure prioritaire sur le grattage quand un chien menace, contournement des obstacles par les chiens, placement des
objets (rien dans l'eau, tout atteignable à pied depuis la niche), indices d'Alice, charge du chien de berger, poules,
papillons, circulation (bousculade, passages piétons), pont, eau animée, séquenceur musical, fanfare et musique de
défaite. `tests/edges.py` détecte les sprites dont des pixels touchent le bord du cadre.

## Organisation

| Fichier | Rôle |
|---|---|
| `spritelib.py` | boîte à outils de dessin SVG, rendu, strips, GIF |
| `tecky.py`, `alice.py`, `enemies.py`, `hens.py`, `vehicles.py`, `butterflies.py`, `items.py`, `decor.py`, `tiles.py`, `hud.py` | dessin des personnages, poules, véhicules, papillons, objets, décor, tileset, HUD |
| `music.py` | partition chiptune (thème en boucle, fanfare de victoire, musique de défaite), export WAV |
| `sample_map.py`, `hud_mockup.py` | carte d'exemple et maquette du HUD |
| `build.py` | export du kit GameMaker dans `out/` |
| `pack_web.py` | atlas, niveau, version web et paquet autonome dans `web/` |
| `web_src/` | moteur du jeu (`game.js`), gabarits HTML, service worker, vérificateur de placement |
| `fonts/` | police Fredoka (licence OFL) |
| `reference/` | illustrations de référence d'Alice et de Tecky |
| `docs/` | version publiée (GitHub Pages) |
| `tests/` | batterie de tests |
