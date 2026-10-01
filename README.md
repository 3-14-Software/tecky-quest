# Tecky Quest

Mini RPG en vue de dessus : **Tecky**, le teckel au harnais rouge, part à la recherche d'**Alice**, qui joue à
cache-cache. Il suit les affaires qu'elle a semées (sa barrette, sa chaussure, son doudou) : chacune indique où chercher
ensuite, et Alice ne sort de sa cachette qu'une fois les trois retrouvées. En chemin, Tecky aboie pour repousser les
chiens (dont les chiens de berger, qui chargent), gratte la terre pour déterrer des trésors, ramasse des os (qui rendent
de la vie) et des saucisses (qui ajoutent un os de vie maximum). Il traverse campagne, route (gare aux voitures :
mieux vaut passer par les passages piétons), village, zone industrielle, ferme, rivière (un seul pont), forêt et parc.
La journée avance avec la recherche : la lumière baisse à chaque indice jusqu'au coucher du soleil.
En chemin : le fermier Gaston a besoin d'aide pour ramener ses poules dans l'enclos, des écureuils et des chats
filent se percher quand Tecky les poursuit, des terriers permettent de passer sous les grillages, et Tecky peut
flairer la piste d'Alice (de petits pieds nus apparaissent au sol). Les trésors enterrés sont des os dorés à
collectionner, et la pause montre la carte des coins déjà explorés. Chaque zone a son ambiance sonore et ses
instruments.

Deux modes au choix sur l'écran titre : **aventure** (les chiens mordent) et **balade**, pour les plus petits (personne ne
se fait mal : les chiens attendent qu'on joue avec eux et deviennent des copains). La partie est enregistrée automatiquement dans le navigateur
(« Continuer » sur l'écran titre, « Reprendre la partie » après un KO) et les records (meilleur score, meilleur temps)
sont gardés pour chaque mode.

Tout est généré par du code : sprites en SVG (aplats + contour), tileset, décors, HUD, musique chiptune, niveau.

- **Jouer** : https://3-14-software.github.io/tecky-quest/ (clavier : flèches/ZQSD, X aboyer, C mordre (ou gratter, lire, passer sous un grillage, jouer), R flairer, P pause, F plein écran, M son ; manette : stick ou croix, X/B aboyer, A mordre/gratter/lire et valider, Y flairer, Start pause, Select son ; tactile sur téléphone).
- **Kit GameMaker Studio 2** (sprites en strips x1/x2, tileset, décor, HUD, sons ; en pause pour l'instant) : voir [GAMEMAKER.md](GAMEMAKER.md).

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
papillons, fontaine animée, circulation (bousculade, passages piétons), pont, eau animée, séquenceur musical, fanfare
et musique de défaite, sauvegarde (continuer, reprise après KO, stockage refusé), records par mode, mode balade,
manette simulée, poussière, feuilles, ombres de nuages et coucher de soleil, quête des poules, terriers, flair,
os dorés, écureuils et chats, zones (bandeau, ambiance, timbre), carte de la pause, copains qui suivent Tecky. `tests/edges.py` détecte les sprites dont des pixels touchent le bord du cadre.

## Organisation

| Fichier | Rôle |
|---|---|
| `spritelib.py` | boîte à outils de dessin SVG, rendu, strips, GIF |
| `tecky.py`, `alice.py`, `enemies.py`, `hens.py`, `farmer.py`, `critters.py`, `vehicles.py`, `butterflies.py`, `items.py`, `decor.py`, `tiles.py`, `hud.py` | dessin des personnages, poules, fermier, écureuils et chats, véhicules, papillons, objets, décor, tileset, HUD |
| `music.py` | partition chiptune (thème en boucle, fanfare de victoire, musique de défaite), export WAV |
| `sample_map.py`, `hud_mockup.py` | carte d'exemple et maquette du HUD |
| `build.py` | export du kit GameMaker dans `out/` |
| `pack_web.py` | atlas, niveau, version web et paquet autonome dans `web/` |
| `web_src/` | moteur du jeu (`game.js`), gabarits HTML, service worker, vérificateur de placement |
| `fonts/` | police Fredoka (licence OFL) |
| `reference/` | illustrations de référence d'Alice et de Tecky |
| `docs/` | version publiée (GitHub Pages) |
| `tests/` | batterie de tests |
