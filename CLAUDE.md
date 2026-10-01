# Tecky Quest — contexte pour Claude Code

Mini RPG en vue de dessus, fait pour Christophe (3.14 Software, développeur Java, Fedora, il parle français) :
Tecky, le teckel au harnais rouge, cherche Alice (la fille de Christophe, 5 ans). Deux livrables issus des mêmes sources :
une **version web** (Canvas, une seule page HTML, PWA) et un **kit d'assets GameMaker Studio 2** (`GAMEMAKER.md`).
Langue : tout en français (interface du jeu, commentaires, README, messages de commit). Style visuel : aplats de couleurs,
contour brun `#3A1E12`, lignes simples, ambiance mignonne. Référence des personnages : `reference/alice_tecky.png`
(illustrations générées par IA, fournies par Christophe). Tecky : teckel roux, harnais rouge en vrai ; Alice : cheveux châtains
mi-longs avec frange, t-shirt jaune, jupe rose, pieds nus. Garder ces traits en cas de retouche des sprites.

## Commandes

```bash
pip install -r requirements.txt           # cairosvg, pillow, numpy (+ Node 18+ pour les tests)
python3 pack_web.py                       # web/index.html, web/tecky_quest_web/ (autonome), atlas, niveau
python3 build.py                          # kit GameMaker -> out/ (efface d'abord ses anciennes sorties)
./tests/run_all.sh                        # reconstruit puis lance tous les tests (doit finir avec exit=0)
./publish_docs.sh                         # copie la version autonome dans docs/ (GitHub Pages)
```

Jeu en ligne : https://3-14-software.github.io/tecky-quest/ — publié par `.github/workflows/pages.yml` à chaque push touchant `docs/`.
Pour livrer une modification : `./tests/run_all.sh && ./publish_docs.sh`, commit (docs/ inclus), push sur `main`.
`web/` et `out/` sont générés et ignorés par Git ; `docs/` est commité.

## Architecture

- `spritelib.py` : classe `Drawing` (parts SVG, silhouette dessinée en premier avec un trait épais = contour propre),
  `render_svg(svg, w, h, scale, pad)`, strips `_stripN`. Les vues gauches sont le miroir des vues droites.
- `tecky.py`, `alice.py`, `enemies.py` (roquet, bouledogue, molosse/doberman, berger), `hens.py` (poules animées),
  `farmer.py` (le fermier Gaston, vu de face, 48x64, pieds en (24, 60) ; `FACE` pour son portrait),
  `critters.py` (écureuil, chats roux et noir, de profil, 32x32), `vehicles.py` (voitures, camionnette, bus),
  `butterflies.py` (papillons, vus de dessus), `items.py`, `decor.py`, `tiles.py`, `hud.py` :
  dessins et animations. `tiles.py` : tileset Wang/marching squares de 16 tuiles par transition (bits NO=1, NE=2, SO=4, SE=8),
  tuile 0 vide, 16 colonnes, `PAIRS`, `PRIORITY`, `resolve()`.
- `music.py` : **source unique** de la musique (thème « Promenade de Tecky », 32 mesures, boucle ; fanfare de victoire et
  musique de défaite, 3 mesures chacune à 140 BPM, même durée). Génère les WAV GameMaker et les données
  `SONG`/`WINSONG`/`LOSESONG` jouées par le séquenceur WebAudio du jeu (`Music.start('main' | 'win' | 'lose')`).
- `pack_web.py` : atlas (frames rognées), niveau (`MW=80`, `MH=48` tuiles, positions des décors/objets/chiens/trésors `DIG`),
  `index.html` à partir de `web_src/index.template.html` + `game.js`, paquet autonome (manifest, service worker, icônes, `serve.sh`).
  Lance `web_src/check_placement.js` : rien dans l'eau ou un obstacle, et tout atteignable **à pied depuis la niche**
  (parcours en largeur sur une grille de 16 px ; c'est lui qui garantit que le pont et les sentiers suffisent).
- Carte : le quart nord-ouest (40 x 24) est la carte d'origine (mêmes coordonnées, les tests s'y appuient). Ferme au
  nord-est, rivière d'un bord à l'autre (y 26..29) avec **un seul pont** (`BRIDGES`, x 63..65 : coins rendus non-eau ;
  garde-corps = `RAILS` dans game.js), forêt au sud-est (sous-bois, sapins générés par `forest_firs()` hors des sentiers),
  parc au sud-ouest (cabane d'Alice). Terrains ajoutés : `field` (champ), `forest` (sous-bois).
- `web_src/game.js` : tout le moteur. Monde en pixels x2 (tuile = 64), caméra 960x540, interface 1920x1080 (`GW`/`GH`).
  Sol pré-rendu en blocs de 16 tuiles (`groundChunks`, 1024 px) : une seule image de la carte dépasserait la taille
  de canevas permise sur certains téléphones. Décors `FLAT` (pont, bac à sable) dessinés sous les personnages.
  Décors animés (`decor.ANIMATED`, ex. la fontaine : la fonction reçoit la phase 0..1 ; fps dans `MAP.decorFps`).
  Eau animée : le tileset web a une eau unie (`tiles.tileset(S, water_marks=False)`) et `drawWater()` y sème des
  vaguelettes `fx/ripple` légères (une par tuile, un cycle sur deux, position tirée par `hash3`) et, en plus, des
  scintillements `fx/glint` (mini-étoiles, cadence propre), seulement en eau profonde (`deepWater()` : tout le contour plus une
  marge, sinon ils mordent sur le liseré des berges).
- Ambiance (`game.js`, section « petits effets ») : poussière sous les pattes (`dusts`, `DUST`), feuilles qui tombent des
  arbres et sapins visibles (`leaves`, `LEAF`, sprite `fx/leaf` : une image par couleur), ombres de nuages pré-rendues
  (`clouds`, `CLOUD`, `buildClouds()`), coucher de soleil (`sun`, `SUN`, `drawLight()` : teinte multipliée sur le
  monde seulement, halo, vignette, lampadaires, lumière des retrouvailles). `sun` suit `sunGoal()` = nombre d'indices
  (4 aux retrouvailles) : il est donc restauré avec la sauvegarde.
- Menus (`menu`, `openTitleMenu()`, `openOverMenu()`, `menuInput()`, `menuHit()`, `chooseMenu()`) : écran titre
  (Continuer s'il y a une sauvegarde, Nouvelle aventure, Nouvelle balade, records du mode choisi) et KO (Reprendre la
  partie, Recommencer, Menu principal). La victoire ramène au menu (`toTitle()`).

## Règles de jeu (à ne pas casser)

- Vie : 2 PV par os ; départ **3 os** (`START_BONES`), plafond 8. Un **os** rend un os perdu *jusqu'au maximum courant* (inutile à
  vie pleine, il reste au sol). Une **saucisse** ajoute un os au maximum et soigne tout.
- Actions : X aboie (repousse) ; C (`biteAction()`) **gratte** près d'un trésor enterré (traces de pattes), **lit** près
  d'un panneau (E aussi), sinon **mord** ; le bouton tactile et les bulles « Gratter » / « Lire » suivent la même règle.
  **Mordre passe avant tout** si un chien menace Tecky (`threatened()` : chien « engagé » — `ENGAGED` : chasse,
  attaque, aboiement, sonné, accroupi, charge, essoufflé — à moins de `THREAT_R` = 240 px) ; C interrompt alors aussi un grattage en cours. Tests : `threat.js`, `read.js`.
  Le **doberman est immunisé aux aboiements** (`barkImmune`) : il faut le mordre (Tecky l'explique, bulle « Même pas peur ! »).
- Aboiement : touche dans un cône devant soi, jusqu'à `BARK` (Tecky, 300 px) ou `DOG_BARK` (doberman, 320 px).
  Une onde au sol (`addBarkRing` / `drawRings`, crème ou rouge) montre exactement cette zone : toujours passer par ces
  constantes pour changer une portée. Test : `tests/ring.js`.
- Son : thème à 0,35 (`Music.level()`), fanfare de victoire et musique de défaite à 0,55 (jouées une seule fois) ;
  bruitages multipliés par `SFX_VOL` (1,4). KO de Tecky → `Music.start('lose')` ; rejouer relance le thème.
- Trésors (médaille 100, jouet pouic-pouic 50, balle 20) : jamais dans l'eau — `check_placement.js` le vérifie.
- Indices (`CLUES` : barrette à la ferme, chaussure dans la forêt, doudou au parc) : chacun dit où chercher ensuite
  (`CLUE_NEXT`), la flèche du HUD vise le prochain indice puis Alice (`arrowTarget()`). Elle n'est **pas permanente** :
  `showArrow()` l'affiche 8 s après l'intro et chaque indice, et en rappel après 45 s sans progrès (`ARROW`). Seule la
  pointe (`hud/arrow`) tourne ; l'icône de la cible (`hud/arrow_icon` : 3 indices + tête d'Alice) reste droite. Alice est **cachée**
  (`alice.hidden`, ni dessinée ni solide) jusqu'aux trois ; devant la cabane trop tôt, Tecky dit qu'il manque des indices.
- Circulation (`cars`, `VEHICLE`, `TRAFFIC`, données `MAP.traffic` : voies, passages `CROSSINGS`) : à droite sur la
  grande route, retour par l'autre bord de la carte, distances de sécurité. Un choc projette Tecky sur le bas-côté
  (klaxon avant, « Ouf ! ») **sans dégâts** ; aux passages piétons, arrêt systématique. Les chiens sont aussi
  écartés. Test : `traffic.js`.
- Papillons (`butterflies`, `BFLY`, `MAP.flowers`) : 16, surtout au parc, mais aussi niche, village (visibles dès
  l'écran titre), campagne sud-ouest, verger de la ferme, clairière. Volettent en zigzag avec une ombre au sol, se
  posent sur les pots de fleurs ou les massifs (`FLOWER_BEDS`, dessinés aussi au sol), s'envolent si Tecky approche
  ou aboie. Chacun doit avoir une fleur à portée (testé). Dessinés au-dessus de tout, sans collision. Test :
  `butterflies.js`.
- Poules (`hens`, `HEN`) : picorent et se promènent autour de leur place ; un aboiement dans le cône (`BARK`) ou Tecky
  trop près les fait fuir en battant des ailes (« cot-cot »). Pas de collision. Test : `hens.js`.
- Chien de berger (`berger`, `CHARGE`) : s'accroupit (« ! », sprite écrasé), charge en ligne droite si `clearPath()`,
  puis souffle (`tired`) ; un aboiement pendant l'accroupissement annule la charge. Tests : `clues.js`, `berger.js`, `map.js`.
- Fin : retrouver Alice → dialogue + fanfare (`Music.start('win')`, une seule fois, le thème ne repart pas) → écran de victoire.
- Sauvegarde (`STORE` : localStorage, repli en mémoire si refusé ; clés `tecky-quest-save` v1 et `tecky-quest-records`) :
  `saveGame()` toutes les `SAVE_EVERY` (4) s de jeu si `safeToSave()` (aucun chien engagé à moins de 600 px), à chaque
  indice et trésor (fin de réplique), en quittant la page (`pagehide`, onglet caché) ; jamais KO ni après la victoire.
  Contenu : mode, place, os, score, temps, indices, trésors, objets au sol, chiens restants (`d.id` = index dans
  `MAP.enemies`). `loadGame(s, rested)` : Continuer, ou reprise après KO (`rested` = vie pleine). La victoire efface la
  sauvegarde et met à jour les records du mode (`recordRun()` : meilleur score, meilleur temps, nombre de victoires ;
  `newRecord` pour les étiquettes « Record ! »). Toute nouvelle donnée de partie doit entrer dans `saveGame()` /
  `loadGame()` (test : `save.js`).
- Mode balade (`gameMode`, `balade()`, `PLAY`) : **personne ne se fait mal**. `hurtPlayer()` sans effet, `threatened()`
  toujours faux, `doBite()` ne blesse aucun chien ; pas d'aboiement (doberman) ni de charge (berger). Les chiens viennent
  attendre près de Tecky en sautillant (`wait`, patience `PLAY.patience`, puis ils rentrent, `d.calm`). Près d'un chien,
  C devient « Jouer » (`biteAction()` → `'play'`, `playTarget()` : un nouveau chien passe avant trésor et panneau, un
  copain après ; bulle « Jouer », icône `hud/action` 8) : `startPlay()`, Tecky et le chien sautillent (`fx/heart`), et le
  chien devient un copain (`d.friend`, points du chien, compté dans `fled` = « Copains de jeu » à la fin, sauvegardé
  dans `friends`). Un copain ne poursuit plus Tecky mais lui fait la fête quand il passe ; on peut rejouer sans points.
  L'aboiement n'éloigne personne : il appelle les chiens touchés (`callDog()` : bond, cœur, ils accourent). Test : `balade.js`.
- Quête des poules (`farm`, `FARM`, `farmer`, `MAP.pen` / `penGate` / `farmer`) : cinq poules `quest` hors de l'enclos.
  Le fermier parle quand Tecky arrive près de lui (`talkFarmer()` : demande, rappel « Encore n poules ! », merci).
  Une poule poussée garde sa nouvelle place (`hx`), `funnelHen()` la guide vers la barrière, `keepHen()` la compte
  (`penned`) et la garde dans l'enclos, jamais sur la route. Toutes rentrées : `finishFarm()` (saucisse, points).
  Sauvegardé (`farm`, `hens`). Test : `farm.js`.
- Dialogues : `say()` pendant un dialogue **met la réplique à la suite** (`dialog.queue`) au lieu de le remplacer
  (le fermier parle et Tecky ramasse la barrette dans la même image).
- Terriers (`MAP.tunnels`, décor `burrow` à plat, `TUNNEL`) : près d'un bout, C fait « Passer » (`startTunnel()`,
  `updateTunnel()` : gratte, disparaît, ressort de l'autre côté ; `afterTunnel()` fait passer les copains). Les chiens
  font le tour. Priorité de C : menace > jouer > trésor > terrier > panneau. Test : `tunnel.js`.
- Flair (R, Y à la manette, bouton à truffe au toucher ; `SNIFF`) : piste de pieds nus (`fx/footprint`) vers
  `arrowTarget()`, le long d'un vrai chemin à pied (`buildWalkGrid()` : grille de 16 px rasterisée une fois,
  `fieldTo()` : distances par parcours en largeur, `scentPath()`). Les trésors proches scintillent. Test : `tunnel.js`.
- Os dorés : le trésor sous les traces de pattes (`item/goldbone`, `treasures` = os dorés trouvés, HUD et victoire).
- Petites bêtes (`critters`, `CRITTER`, `REFUGES`, `MAP.critters`) : écureuils et chats flânent ; Tecky trop près ou
  qui aboie les fait filer vers un refuge pas de son côté (arbre/sapin : l'écureuil grimpe et disparaît ; toit ou
  conteneur : le chat saute et feule), ils redescendent quand il est loin. Points la première fois (`scored`, sauvegardé).
- Zones (`ZONES`, `zoneAt()`, `updateZone()`) : bandeau à l'arrivée (`banner`), étiquettes de la carte, ambiance sonore
  (`Ambience`, `AMB_EVENTS`, `ambSound()` : oiseaux, coq, sonnette, cliquetis ; clapotis selon l'eau autour) et timbre
  de la musique (`TIMBRE`, `Music.zone`). Test : `world.js`.
- Carte de la pause (`drawPauseMap()`, `mapImg` pré-rendue au quart, `seenCells` : cases de 4 tuiles vues à l'écran,
  sauvegardées) : brouillard, noms des zones vues, Tecky, indices, os dorés, Alice, enclos pendant la quête.
- Copains qui suivent (balade, `FOLLOW`, `crumbs`, mode `follow`) : après avoir joué, le chien suit Tecky en file
  indienne sur ses traces pendant 30 s, puis rentre. Test : `world.js`.
- Manette (`pollPad()` appelé par `frame()` avant `update()`, `PAD_MAP`, `pad.on` → indices `hud/pad` au lieu de
  `hud/key`) : un appui = une impulsion dans `pressed`, la croix et le stick donnent `pressed.up/down` pour les menus,
  le stick gauche fait marcher (zone morte `PAD_DEAD`, vitesse selon l'inclinaison). Le clavier donne aussi
  `pressed.up/down/left/right`. Test : `pad.js` (dans les tests, appeler `pollPad()` avant `update()`).

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
- Tests : isoler la scène (`dogs = []`, `cars = []`, autres chiens renvoyés chez eux) ; un chien qui flâne ou une voiture
  qui passe rendent sinon un test aléatoire. Relancer un nouveau test plusieurs fois avant de le valider.
- Le service worker de `docs/` est réseau d'abord avec repli cache : pas de version à incrémenter à chaque livraison.
- Canvas simulé des tests (`sim.js`, `check_placement.js`) : il doit renvoyer un objet pour `createRadialGradient` /
  `createLinearGradient` (nuages, lumière) ; tout nouvel appel de canvas qui renvoie un objet doit y être ajouté.
- Tests sans `localStorage` : `STORE` passe en mémoire. Après un KO dans un test, le menu propose d'abord
  « Reprendre la partie » : choisir `menu.sel` explicitement pour « Recommencer ».

## Reste à faire

- Kit GameMaker **en pause** (choix de Christophe : on avance sur la version web). `build.py` doit continuer à
  tourner, mais les nouveautés (fermier, petites bêtes, terriers, flair, carte, ambiances…) n'y sont pas documentées.
- Piste en réflexion : dialogues lus à voix haute (pour qu'Alice joue sans savoir lire).
