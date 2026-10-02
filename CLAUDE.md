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
  `ducks.py` (colvert, cane, caneton, de profil, 32x32, ligne d'eau en (16, 24)),
  `cows.py` (vaches pie noire et pie rouge, veau, de profil, 64x48, pieds en (32, 44)),
  `villageois.py` (villageois sans quête, vus de face comme ceux de npcs.py, dont il réutilise les outils),
  `npcs.py` (le facteur Marcel et la voisine Mamie Rose, comme `farmer.py` ; `letter_frames()` : la lettre),
  `critters.py` (écureuil, chats roux et noir, de profil, 32x32), `vehicles.py` (voitures, camionnette, bus),
  `butterflies.py` (papillons, vus de dessus), `lisiere.py` (le bord de la carte : fourrés, tunnel de la route, et
  `decor()`, le placement de la lisière), `items.py`, `decor.py`, `tiles.py`, `hud.py` :
  dessins et animations. `tiles.py` : tileset Wang/marching squares de 16 tuiles par transition (bits NO=1, NE=2, SO=4, SE=8),
  tuile 0 vide, 16 colonnes, `PAIRS`, `PRIORITY`, `resolve()`. Là où trois terrains se rencontrent (ou deux sans
  paire), `needs_composite()` : la version web pose une tuile composée (`composite()` : chaque terrain par-dessus le
  précédent ; `COMPOSITES` dans pack_web, ajoutées au tileset à partir de `COMPOSITE_BASE`) au lieu de remplacer un
  terrain par un autre (encoches carrées au bout des chemins et des trottoirs). Un chemin s'arrête au bord de la
  route (coins de la route intacts) : sinon il mord sur la chaussée, sous le passage piéton.
- `music.py` : **source unique** de la musique (thème « Promenade de Tecky », 32 mesures, boucle ; fanfare de victoire et
  musique de défaite, 3 mesures chacune à 140 BPM, même durée). Génère les WAV GameMaker et les données
  `SONGS`/`WINSONG`/`LOSESONG` jouées par le séquenceur WebAudio du jeu (`Music.start('main' | 'win' | 'lose')`).
  Variations du thème par zone (`STYLES`, `events(style)` : `_lead`, `_bass`, `_arp`, `_drums`) : même mélodie, mêmes
  accords, même grille de phrases, tempo propre ; « base » (niche, campagne) = le thème d'origine et le WAV GameMaker.
  Village plus entraînant (152), ferme country (136 : basse alternée, rouleaux de banjo, notes glissées = 6e champ),
  forêt calme (108 : basse tenue, écho), parc boîte à musique (126, sans batterie), industrie mécanique (140) ; et la
  berceuse de la fin (84, sans batterie, timbre `TIMBRE.end`).
- `pack_web.py` : atlas (frames rognées), niveau (`MW=96`, `MH=64` tuiles, positions des décors/objets/chiens/trésors `DIG`),
  `index.html` à partir de `web_src/index.template.html` + `game.js`, paquet autonome (manifest, service worker, icônes, `serve.sh`).
  Lance `web_src/check_placement.js` : rien dans l'eau ou un obstacle (canards : dans l'eau), et tout (personnages,
  lettres, Pompon compris) atteignable **à pied depuis la niche**
  (parcours en largeur sur une grille de 16 px ; c'est lui qui garantit que le pont et les sentiers suffisent).
  **Règle d'espacement** : deux actions de genres différents (personnage, panneau, os doré, bout de terrier, indice,
  lettre, Pompon) ne se recouvrent jamais (portées `NPC.talk`, `REACH`, `TUNNEL.reach`, `POST.pick`, `CAT.find` + 60 px),
  aucun objet n'est à portée de parole d'un personnage, les personnages vivent en zone calme et aucun chien n'y habite.
- Carte (96 x 64, agrandie depuis 80 x 48 : colonnes ajoutées en x 15 et x 30, rangées en y 10,4 et y 25 ; sauvegarde
  v2) : au nord de la route (y 18..21), la niche et son jardin, le village (place, fontaine, marché `stall_*`, terrasse
  `cafe_table`, boulangerie `bakery`, maisons `house_red` / `house_blue` / `house_timber` / `house_tall`, rue et
  ruelle), la ferme ;
  au sud, la campagne (mare aux canards au bord de l'eau), la zone industrielle, le verger (pommiers `apple_tree` en
  rangées, panier d'Iris) et les prés de la ferme (champ, mare, pâture au bord de la rivière).
  Rivière d'un bord à l'autre (y 42..45) avec **un seul pont** (`BRIDGES`, x 79..81 : coins rendus non-eau ;
  garde-corps = `RAILS` dans game.js), forêt au sud-est (sous-bois, sapins générés par `forest_firs()` hors des sentiers),
  parc au sud-ouest (cabane d'Alice). Les coordonnées des zones (`ZONES`, `RIVER_MID`), de la route (marquages,
  `MAP.traffic`, `FARM.roadY`) et des ballons (`BALL.box`) sont écrites en dur : à suivre si la carte change. Zone industrielle au sud de la route : le dépôt (x 30..56) et, en dessous, le port au bord
  de la rivière (x 30..64) : chariot élévateur, camion,
  conteneurs sous le portique (pieds dans `RAILS`), cabane du gardien, voie ferrée du quai (`rail`, à plat), bittes,
  péniche. Terrains ajoutés : `field` (champ), `forest` (sous-bois).
- Bord de la carte (pas de mur invisible muet) : la caméra déborde de `EDGE.cam` (une tuile) au-delà de la carte
  (`camClampX()` / `camClampY()`, partout sauf le cadrage fixe de la scène de fin) et montre une lisière
  (`MAP.edge.decor` = `EDGE_DECOR`, générée par `edge_decor(corner_grid(), edge_keep())` dans pack_web : fourrés et
  arbres, sapins le long de la forêt, jamais par-dessus ce que liste `edge_keep()`) sur un sol qui prolonge celui du
  bord (`MAP.edge.ring`, `lisiere.RING` tuiles : `pick()` de `build_map()` avec les coins ramenés sur le bord ; la
  route, la rivière et le ruisseau continuent, `waterAt()` aussi). Aux deux bouts de la grande route, un tunnel
  (`ROAD_TUNNELS`, sprite `decor/tunnel`, en miroir à l'est) où les voitures disparaissent ; sa butte est un obstacle
  (`FOOT.tunnel`, `EDGE_SOLIDS`) : Tecky s'arrête devant la bouche. La lisière n'est pas un obstacle : c'est `BOUND`
  (`offMap()`, dans `blockedFeet()`) qui arrête au bord. Tecky qui y pousse sans avancer le dit (`edgeBump()`,
  `EDGE.push` s, au plus une fois toutes les `EDGE.again` s). Les bulles de mots restent dans l'écran. Test : `edge.js`.
- `web_src/game.js` : tout le moteur. Monde en pixels x2 (tuile = 64), caméra 960x540, interface 1920x1080 (`GW`/`GH`).
  Sol pré-rendu en blocs de 16 tuiles (`groundChunks`, 1024 px ; `buildChunk()`, `groundTile()`, plus des bandes
  pour la marge de la lisière) : une seule image de la carte dépasserait la taille de canevas permise sur certains
  téléphones. Décors `FLAT` (pont, bac à sable) dessinés sous les personnages.
  Décors animés (`decor.ANIMATED`, ex. la fontaine : la fonction reçoit la phase 0..1 ; fps dans `MAP.decorFps`).
  Eau animée : le tileset web a une eau unie (`tiles.tileset(S, water_marks=False)`) et `drawWater()` y sème des
  vaguelettes `fx/ripple` légères (une par tuile, un cycle sur deux, position tirée par `hash3`) et, en plus, des
  scintillements `fx/glint` (mini-étoiles, cadence propre), seulement en eau profonde (`deepWater()` : tout le contour plus une
  marge, sinon ils mordent sur le liseré des berges).
- Ambiance (`game.js`, section « petits effets ») : poussière sous les pattes (`dusts`, `DUST`), feuilles qui tombent des
  arbres et sapins visibles (`leaves`, `LEAF`, sprite `fx/leaf` : une image par couleur), ombres de nuages pré-rendues
  (`clouds`, `CLOUD`, `buildClouds()`), du jour à la nuit (`sun`, `SUN`, `drawLight()` : teinte multipliée sur le
  monde seulement ; vignette et halo pré-rendus en petit par `buildLight()` ; lampadaires et lumière des retrouvailles
  par `glowSpot()`, `hug`). `sun` suit `sunGoal()` = nombre d'indices (3 aux retrouvailles, 4 pendant la scène de fin
  et l'écran de victoire) : il est donc restauré avec la sauvegarde. 0 plein jour, 1 fin d'après-midi, 2 coucher
  orangé, 3 (troisième indice) toujours le coucher, un peu plus rouge, lampadaires allumés (passé `SUN.lamp`,
  `lampsOn()` : plus d'arc-en-ciel), 4 la nuit bleutée (lampadaires plus forts), qui tombe quand Tecky et Alice
  rentrent à la niche.
- Version (`VERSION`, écrite par `version()` de pack_web : la date de construction) en bas à droite de l'écran titre.
- Menus (`menu`, `openTitleMenu()`, `openOverMenu()`, `openPauseMenu()`, `menuInput()`, `menuHit()`, `chooseMenu()`) :
  écran titre (Continuer s'il y a une sauvegarde, Nouvelle aventure, Nouvelle balade, Options, Badges, records du
  mode choisi),
  pause (sous la carte, en ligne : Reprendre, Options, Menu principal ; P reprend directement) et KO (Reprendre la
  partie, Recommencer, Menu principal). La victoire ramène au menu (`toTitle()`). Changement d'écran en fondu par le
  noir (`transition()`, appelée par `newGame()`, `loadGame()`, `toTitle()` : l'état change tout de suite, une image de
  l'écran quitté s'assombrit, `FADE`, `updateFade()`, `drawFade()`). Pause automatique (`autoPause()`,
  `onLeave()`) quand la fenêtre perd le focus, que l'onglet est caché ou que la manette dont on jouait est débranchée
  (`pad.n`) ; seulement en jeu (un dialogue attend déjà). Tests : `save.js`, `pad.js`.
- Options (`opts`, `OPT_DEF`, `OPTIONS_KEY`, lues avant le premier `resize()` ; écran `state === 'options'`, `optRows()`,
  `changeOpt()`, `optionsTap()`, retour vers `optReturn`) : volumes Musique (`Music.level()`) et Bruitages
  (`sfxGain()`, ambiance comprise), Difficulté (facile : `gameDiff`, `facile()`, 5 os, morsures moitié moins fortes,
  chiens `d.id % 3 === 2` retirés ; fixée à la nouvelle partie et sauvegardée ; records à part `aventure-facile`),
  Texte des dialogues (grand : 46 px, 4 lignes), Image (fluide = `MAX_PIXELS`, nette = sans plafond), Plein écran
  (dans les événements clavier / toucher : il faut un geste de l'utilisateur ; un bouton de manette en vaut un pour
  Chromium, pas pour Firefox : `fsRefusedAt`, la ligne dit alors « touche F, ou un clic » ; en sortir est toujours permis), Vibrations, Météo. Test : `options.js`.
- Badges (`MAP.badges` = `hud.BADGES`, image i de `hud/badge`, la dernière = verrouillé ; `BADGE_INFO`, `BADGES_KEY`,
  gardés d'une partie à l'autre) : `checkBadges()` toutes les demi-secondes, `winBadges()` à la victoire (aventure,
  sans morsure = `bitten` faux, sauvegardé ; moins de 10 min). `unlockBadge()` : annonce « Nouveau badge ! »
  (`toasts`), rappel sur l'écran de victoire (`newBadges`), écran « Badges » depuis le menu principal
  (`state === 'badges'`). Un nouveau badge : l'ajouter à `hud.BADGES` (dessin), `BADGE_INFO` et une condition.
  Test : `badges.js`.
- Météo (`weather`, `WEATHER`, option `opts.weather` : auto / soleil / pluie / neige ; `december()`) : en auto, une averse
  de temps en temps (neige en décembre). `weather.k` = force (monte et descend en `WEATHER.ramp` s). Pluie : gouttes
  (traits, `drops`), `fx/splash`, teinte gris-bleu (dans le remplissage de `drawLight()`, `weatherTint()`), flaques
  (`puddles` : places tirées une fois par `hash3`, remplies selon `weather.wet`), plouf (`puddleSplash()`), crépitement
  (`Ambience.startRain()`, les oiseaux se taisent). Fin d'averse : arc-en-ciel (`drawRainbow()`, repère GUI ;
  jamais une fois les lampadaires allumés, il s'efface quand ils s'allument) et Tecky
  s'ébroue (`shakePending`, mode `shake` : deux secousses, 0,75 s ; gouttes `fx/drop` à chacune, `shakeDrops()`). Neige : flocons (`flakes`, dessinés directement depuis
  l'atlas), sol blanchi (`weather.cover`). Rien n'est sauvegardé. Test : `weather.js`.
- Vibrations (`rumble(kind)`, `RUMBLE`) : manette (`vibrationActuator.playEffect('dual-rumble')`) si `pad.on`, sinon
  téléphone (`navigator.vibrate`) en mode tactile ; morsure reçue, KO, choc de voiture, morsure qui porte, os doré.
  Rien si l'option est à « non ». Test : `options.js`.

## Règles de jeu (à ne pas casser)

- Vie : 2 PV par os ; départ **3 os** (`START_BONES`), plafond 8. Un **os** rend un os perdu *jusqu'au maximum courant* (inutile à
  vie pleine, il reste au sol). Une **saucisse** ajoute un os au maximum et soigne tout.
- Actions : X aboie (repousse) ; C (`biteAction()`) **gratte** près d'un trésor enterré (traces de pattes), **lit** près
  d'un panneau (E aussi), sinon **mord** ; le bouton tactile et les bulles « Gratter » / « Lire » suivent la même règle.
  **Mordre passe avant tout** si un chien menace Tecky (`threatened()` : chien « engagé » — `ENGAGED` : chasse,
  attaque, aboiement, sonné, accroupi, charge, essoufflé — à moins de `THREAT_R` = 240 px) ; C interrompt alors aussi un grattage en cours. Tests : `threat.js`, `read.js`.
  Le **doberman est immunisé aux aboiements** (`barkImmune`) : il faut le mordre (Tecky l'explique, bulle « Même pas peur ! »).
- Zones calmes (`MAP.calm` = `CALM` dans pack_web : le village au nord de la route, trottoir compris — on parle à
  Marcel depuis le trottoir —, la cour de la ferme ; `calmAt()`),
  comme les villes d'un RPG, en aventure : aucun chien n'y habite, un chien qui poursuit Tecky renonce quand il y
  entre (« Grrr… ») et rentre chez lui, `hurtPlayer()` n'y fait rien, `threatened()` y est faux. En balade, les
  copains peuvent y suivre Tecky. Répit de `GRACE` (1,5 s, `graceT`) après chaque dialogue : aucune morsure ne porte.
  Les personnages qui donnent des quêtes vivent dans ces zones. Test : `calm.js`.
- Aboiement : touche dans un cône devant soi, jusqu'à `BARK` (Tecky, 300 px) ou `DOG_BARK` (doberman, 320 px).
  Une onde au sol (`addBarkRing` / `drawRings`, crème ou rouge) montre exactement cette zone : toujours passer par ces
  constantes pour changer une portée. Test : `tests/ring.js`.
- Son : thème à 0,35 (`Music.level()`), fanfare de victoire et musique de défaite à 0,55 (jouées une seule fois) ;
  bruitages multipliés par `SFX_VOL` (1,4). KO de Tecky → `Music.start('lose')` ; rejouer relance le thème.
- Trésors (médaille 100, jouet pouic-pouic 50, balle 20) : jamais dans l'eau — `check_placement.js` le vérifie.
- Indices (`CLUES` : barrette à la ferme, chaussure dans la forêt, doudou au parc) : chacun dit où chercher ensuite
  (`CLUE_NEXT`), la flèche du HUD vise le prochain indice puis Alice (`arrowTarget()`). Elle n'est **pas permanente** :
  `showArrow()` l'affiche 12 s après l'intro et chaque indice, et 8 s en rappel après 45 s sans progrès (`ARROW` ; taille
  `ARROW.sc`). Seule la
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
- Villageois (`villagers`, `VILLAGER`, `VILLAGER_LINES`, `MAP.villagers`, villageois.py) : Bernard le boulanger,
  Josette la marchande de fruits, Lili la fleuriste, Lucas et son ballon. Sans quête : ils ne sont pas dans
  `npcList()` (ni « ! », ni « Parler »), mais saluent Tecky qui passe d'une bulle (une phrase après l'autre, au plus
  une fois toutes les `VILLAGER.again` s) et de la main (Lucas sautille : `hop`). Obstacles comme les personnages.
  Test : `villagers.js`.
- Vaches (`cows`, `COW`, `MAP.cows`, cows.py) : trois dans le grand pré de la campagne (le veau reste près de sa
  mère, `cowMother()`). Elles broutent, se promènent autour de leur place, lèvent la tête vers Tecky, meuglent de temps
  en temps quand il est dans les parages (`cowMoo()`, `SFX.moo`) ; un aboiement les fait trotter plus loin
  (`scareCow()`, le veau suit). Obstacles sans toucher à `blockedFeet()` : une boîte de `solids` par vache (`c.box`),
  déplacée avec elle et vidée le temps de son propre pas (`cowStep()`, qui refuse aussi un pas sur Tecky). Rien n'est
  sauvegardé. Test : `cows.js`.
- Poules (`hens`, `HEN`) : picorent et se promènent autour de leur place ; un aboiement dans le cône (`BARK`) ou Tecky
  trop près les fait fuir en battant des ailes (« cot-cot »). Pas de collision. Test : `hens.js`.
- Chien de berger (`berger`, `CHARGE`) : s'accroupit (« ! », sprite écrasé), charge en ligne droite si `clearPath()`,
  puis souffle (`tired`) ; un aboiement pendant l'accroupissement annule la charge. Tests : `clues.js`, `berger.js`, `map.js`.
- Fin : retrouver Alice → dialogue + fanfare (`Music.start('win')`, une seule fois, le thème ne repart pas) → scène de fin
  (`state === 'ending'`, `ending`, `ENDING`, `startEnding()`, `updateEnding()`, `drawEnding()`) : fondu au noir, Tecky et
  Alice remontent le chemin de la niche au coucher du soleil, la nuit tombe et les lucioles s'allument
  (`drawFireflies()`, avec la lumière), Tecky s'endort
  à ses pieds (`snooze()`, partagé avec le repos), iris qui se referme, « Fin » ; berceuse (`Music.start('end')`, en
  boucle jusqu'au menu). Un bouton la passe après `ENDING.skip` s (`endingDone()`) → écran de victoire, qui sort du noir
  (`fadeFrom()` : fondu de l'écran entier, `drawFade()`), avec le pourcentage de complétion (`completion()` : os dorés,
  quêtes `QUESTS_DONE`, petites bêtes, canards, carte, copains en balade ; une nouvelle quête s'ajoute à `QUESTS_DONE`).
  Test : `ending.js`.
- Sauvegarde (`STORE` : localStorage, repli en mémoire si refusé ; clés `tecky-quest-save` v2 (`SAVE_V`) et `tecky-quest-records`) :
  `saveGame()` toutes les `SAVE_EVERY` (4) s de jeu si `safeToSave()` (aucun chien engagé à moins de 600 px), à chaque
  indice et trésor (fin de réplique), en quittant la page (`pagehide`, onglet caché) ; jamais KO ni après la victoire.
  Contenu : mode, place, os, score, temps, indices, trésors, objets au sol, chiens restants (`d.id` = index dans
  `MAP.enemies`). `loadGame(s, rested)` : Continuer, ou reprise après KO (`rested` = vie pleine). La victoire efface la
  sauvegarde et met à jour les records du mode (`recordRun()` : meilleur score, meilleur temps, meilleure complétion
  `done`, calculée une fois `winDone`, nombre de victoires ; `newRecord` pour les étiquettes « Record ! »). Toute nouvelle donnée de partie doit entrer dans `saveGame()` /
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
  Le fermier ne parle que si Tecky vient le voir (voir « Personnages ») : `talkFarmer()` (demande, rappel « Il en
  reste n », merci). Une poule poussée garde sa nouvelle place (`hx`), `funnelHen()` la guide vers la barrière,
  `keepHen()` la compte (`penned`) et la garde dans l'enclos, jamais sur la route. Toutes rentrées : le fermier appelle
  Tecky (« Bravo ! Viens me voir ! ») et, quand Tecky lui parle, `finishFarm()` (saucisse, points). Sauvegardé
  (`farm`, `hens`). Test : `farm.js`.
- Le facteur Marcel (`post`, `POST`, `letters`, `MAP.postman`, `MAP.letters`) : cinq lettres emportées par le vent autour
  du village ; Tecky les ramasse en passant dessus (même avant d'avoir parlé à Marcel), compteur dans le HUD pendant
  la quête (comme Pompon), puis Marcel remercie (os + points). La voisine Mamie Rose (`rose`, `neighbor`, `MAP.neighbor`) a perdu son
  chat Pompon (`pompon`, `CAT`, `MAP.pompon`, sprites `cat_white/*`) : une fois la quête acceptée, Pompon suit Tecky
  sur ses traces (`crumbAt()`, terriers compris), s'assoit s'il est trop loin (`wait`), et reste chez elle une fois
  arrivé (`home`) ; elle remercie (saucisse + points). Un aboiement le fait feuler. Sauvegardés (`post`, `letters`,
  `rose`, `cat`). Test : `quests.js`.
- Léon, le cariste du port (`fete`, `leon`, `LEON`, `MAP.leon`, npcs.py « leon ») : ses cinq gros ballons (`balls`,
  `BALL`, `MAP.balls`, sprites `port/balloon` de port.py) ont roulé partout dans la zone industrielle ; Tecky les pousse
  en fonçant dedans (`kickBall()`, orienté par sa direction) ou en aboyant (cône) dans le grand filet (`MAP.goal`, décor
  `goal_net`, côtés et fond dans `RAILS`, intérieur `GOAL_IN`) ; ils roulent, rebondissent (`moveBall()`, jamais hors de
  `BALL.box`), sont guidés vers l'ouverture (`funnelBall()`) et restent dans le filet (`checkGoal()`). Léon remercie
  (os + points), badge « ballons ». Sauvegardés (`fete`, `balls`). Test : `leon.js`.
- Iris, le vieux Jack Russell, ami et mentor de Tecky (`jouets`, `iris`, `IRIS`, `MAP.iris`, npcs.py « iris », mince, sans
  bandana, réduit par `npcs.SCALE` — pas son portrait : un personnage, pas un chien de `dogs` ; bulle plus basse : `n.markY`, `markY()` ; il « parle » en jappant, `n.woof`) :
  sur son panier (décor `dog_bed`, à plat) au milieu du verger, zone calme. Pour entraîner Tecky, il a caché ses trois
  jouets (`toys`, `MAP.toys`, sprites `port/toy`) dans les prés de la ferme. Tecky en prend un dans la gueule en
  passant dessus (un seul à la fois, `carried()`, dessiné à `MOUTH[dir]`), le lâche s'il aboie, mord ou est KO
  (`dropToy()`, `IRIS.regrab`), le donne en arrivant près d'Iris (`giveToy()`). Saucisse + points, badge « iris ».
  Ensuite, un conseil de vieux chien à chaque visite, à tour de rôle (`IRIS_TIPS` : des fonctions, pour le texte
  tactile sans icônes ; `iris.tip`). Sauvegardés (`jouets`, `toys` ; un jouet porté l'est aux pieds de Tecky). Test :
  `iris.js`.
- Maman Piquette, la maman hérisson (`piq`, `piquette`, `BABY`, `MAP.piquette`, npcs.py « piquette ») : dans une
  clairière de la forêt (`CLEARING` dans pack_web : herbe, pas de sapins, sentier depuis le chemin ouest, nid
  `leaf_nest` ; zone calme). Ses trois petits (`babies`, `MAP.babies`, herissons.py, sprites `hedgehog/*`) se cachent
  sous des fougères (« Couic ? » quand Tecky passe) ; une fois la quête demandée, un petit trouvé (`BABY.find`) suit
  Tecky sur ses traces, en file indienne dans l'ordre où ils ont été trouvés (`seq`, après Pompon), attend s'il va
  trop vite, se roule en boule à un aboiement, et rejoint sa maman (`babyHome()`, places `BABY.slots`). Os + points,
  badge « herissons ». Sauvegardés (`piq`, `babies`). Test : `piquette.js`.
- Titine, le petit train du port (`train`, `TRAIN`, `MAP.track`, sprites `vehicle/loco` et `vehicle/wagon_*`,
  `fx/steam`) : aller-retour sur la voie du quai, pause à chaque heurtoir, la locomotive à l'est (elle tire, puis
  pousse). Elle s'arrête devant Tecky (« Tut-tut ! »), un chien, Pompon, un chat (`trainBlocker()`), écarte un ballon
  posé sur les rails ; c'est un obstacle mobile (`trainHit()` dans `blockedFeet()`) qui n'avance que la voie libre.
  Un aboiement vers elle la fait siffler (`barkAtTrain()`) : points la première fois (`train.scored`, sauvegardé),
  badge « train ». Test : `train.js`.
- Personnages (`NPC`, `npcList()`, `NPC_DO` : par personnage `mark` / `greet` / `talk` ; `newNpc()`, `updateNpcAnim()` :
  parle, se réjouit (`cheerT`), salue (`waveT`), s'inquiète (`worried`) ; fps dans `MAP.npcFps`) : comme dans un RPG, ils ne
  parlent que sur C (« Parler », `biteAction()` → `'talk'`, E aussi). Bulle `hud/talk` au-dessus de la tête : « ! »
  (une demande ou une récompense à donner), « ? » (demande en cours), remplacée par « Parler » tout près. Quand Tecky
  arrive près d'eux : petite exclamation (`npcShout()`, bulle de mots + `SFX.hey`), sans bloquer le jeu. Une seule
  bulle à la fois par personnage (la nouvelle remplace l'ancienne) ; le salut se tait quand Tecky ramène quelque chose
  (jouet dans la gueule, Pompon ou petits hérissons qui le suivent) : c'est l'arrivée qui parle. Des petits hérissons
  arrivés ensemble n'ont droit qu'à un cri de leur maman (`piquetteCall()`, `BABY.call` s après le dernier).
- Voix des répliques (`voix/`, `tools/export_voix.js`) : l'outil fait tourner le jeu sans affichage, appelle chaque
  dialogue dans tous ses cas et relève les répliques écrites en dur ; de même pour les bulles (`addWordPop(texte, x,
  y, qui)` : le 4e argument dit qui parle, personnage, 'tecky', 'info' ou animal ; `npcShout()` le passe tout seul) ; il écrit `voix/repliques.csv` / `.json` (une
  ligne par fichier audio : nom = `voiceKey()` du jeu, personnage + empreinte du texte à dire ; texte à dire =
  `spokenText()`, les [action] en mots selon l'appareil, `GLYPH_SPOKEN`). Une nouvelle réplique dont le texte est
  calculé : la produire dans l'outil et ajuster `DYNAMIC_SITES` (`DYNAMIC_POPS` pour une bulle). `run_all.sh` vérifie que la liste est à jour
  (`--check`) : après toute modification d'une réplique, relancer `node tools/export_voix.js`.
- Dialogues : `say()` pendant un dialogue **met la réplique à la suite** (`dialog.queue`) au lieu de le remplacer
  (le fermier parle et Tecky ramasse la barrette dans la même image).
- Terriers (`MAP.tunnels`, décor `burrow` à plat, `TUNNEL`) : près d'un bout, C fait « Passer » (`startTunnel()`,
  `updateTunnel()` : gratte, disparaît, ressort de l'autre côté ; `afterTunnel()` fait passer les copains). Les chiens
  font le tour. Priorité de C : menace > jouer > parler > trésor > terrier > panneau. Test : `tunnel.js`.
- Flair (R, Y à la manette, bouton à truffe au toucher ; `SNIFF`) : piste de pieds nus (`fx/footprint`) vers
  `arrowTarget()`, le long d'un vrai chemin à pied (`buildWalkGrid()` : grille de 16 px rasterisée une fois,
  `fieldTo()` : distances par parcours en largeur, `scentPath()`). Les trésors proches scintillent. Test : `tunnel.js`.
- Os dorés : le trésor sous les traces de pattes (`item/goldbone`, `treasures` = os dorés trouvés, HUD et victoire).
- Compteurs du HUD (`hudCounters()`) : empilés à droite sous le score, dans l'ordre os dorés (dès le premier trouvé),
  poules rentrées, lettres retrouvées, Pompon retrouvé (0/1, 1/1) ; ceux des quêtes seulement pendant la quête
  (`asked`). Au toucher, les boutons Pause (`PAUSE_BTN`) et Plein écran (`FS_BTN`) sont en haut, à gauche du score.
- Petites bêtes (`critters`, `CRITTER`, `REFUGES`, `MAP.critters`) : écureuils et chats flânent ; Tecky trop près ou
  qui aboie les fait filer vers un refuge pas de son côté (arbre/sapin : l'écureuil grimpe et disparaît ; toit ou
  conteneur : le chat saute et feule), ils redescendent quand il est loin. Points la première fois (`scored`, sauvegardé).
- Repos (`restPose()`, `REST`, `tecky.REST_ANIMS` → `MAP.rest`, ajoutés à `FPS` / `LOOP`) : sans geste du joueur, Tecky
  s'assoit (6 s ; de dos, il se tourne vers nous), bâille et se gratte à tour de rôle, puis s'endort (24 s) avec des
  « z » (`fx/zzz`, effets à durée de vie : `life`, `vx`/`vy`, `grow`). Tout geste le réveille ; jamais si un chien menace.
  `REST_ANIMS` est à part de `ANIMS` (les chiens ennemis réutilisent `ANIMS`). Test : `rest.js`.
- Canards (`ducks`, `DUCK`, `MAP.ducks` : [espèce, x, y, famille], `ducks.py`) : nagent près de leur place sans quitter
  l'eau (`duckWater()`, vérifié aussi par `check_placement.js`), cancanent, plongent. Tecky trop près ou qui aboie :
  les adultes s'envolent vers un autre coin d'eau loin de lui (`pickLanding()`), ombre au sol, et s'y posent ; la cane
  suivie de canetons (même famille, `lead`) s'éloigne à la nage avec eux en file. Points la première fois (`scored`,
  sauvegardé dans `ducks`). Test : `ducks.js`.
- Zones (`ZONES`, `zoneAt()`, `updateZone()` ; huit, dont « Le verger » au sud de la route, qui reprend la musique de
  la ferme : champ `music` d'une zone) : bandeau à l'arrivée (`banner`), étiquettes de la carte, ambiance sonore
  (`Ambience`, `AMB_EVENTS`, `ambSound()` : oiseaux, coq, sonnette, cliquetis ; clapotis selon l'eau autour) et timbre
  de la musique (`TIMBRE` et variation du thème `SONGS`, `Music.zone`). Changement (`MUSIC_ZONE`) : Tecky doit
  rester `settle` (2 s) dans la zone (`tuneT` ; un passage éclair ne change rien), puis `Music.setZone()` le demande
  (`Music.want`) et le séquenceur fait un fondu enchaîné pendant la dernière mesure d'une phrase (4 mesures) : une
  couche de gain par zone (`Music.layers` : sa variation, ses instruments ; `fadeTo()`, `ramp()`), et le tempo glisse
  de l'une à l'autre pendant ce fondu (`Music.glide`, `stepLen()`). Nouvelle partie, Continuer : fondu rapide (`cut`),
  nouveau tempo tout de suite. Test : `music.js`. La rivière n'est pas une zone : celles du nord et du sud vont jusqu'à son
  milieu (`RIVER_MID`), pour que rien ne change en la longeant ou en passant le pont ; elle garde son étiquette sur la
  carte de la pause (`LANDMARKS`). Test : `world.js`.
- Carte de la pause (`drawPauseMap()`, `mapImg` pré-rendue au quart, `seenCells` : cases de 4 tuiles vues à l'écran,
  sauvegardées) : brouillard, noms des zones vues, Tecky, indices, os dorés, Alice, enclos pendant la quête, « ! » /
  « ? » des personnages déjà vus (`NPC_DO[…].mark()`, taille `MAPV.mark`).
- Copains qui suivent (balade, `FOLLOW`, `crumbs`, mode `follow`) : après avoir joué, le chien suit Tecky en file
  indienne sur ses traces pendant 30 s, puis rentre. Test : `world.js`.
- Manette (`pollPad()` appelé par `frame()` avant `update()`, `PAD_MAP`, `pad.on` → indices `hud/pad` au lieu de
  `hud/key`) : un appui = une impulsion dans `pressed`, la croix et le stick (sur son axe principal) donnent
  `pressed.up/down/left/right` pour les menus (la pause est en ligne) et les options,
  le stick gauche fait marcher (zone morte `PAD_DEAD`, vitesse selon l'inclinaison). Le clavier donne aussi
  `pressed.up/down/left/right`. Test : `pad.js` (dans les tests, appeler `pollPad()` avant `update()`).
- Icônes dans les textes d'aide (`GLYPH`, `richParts()`, `drawRich()`) : un texte écrit `[ok] pour valider`,
  `[bite]`, `[walk]`… et `text()` (donc `para()` et les dialogues) dessine à la place la touche (`hud/key`, noms
  `MAP.keys` = `hud.KEYS`) ou le bouton de manette (`hud/pad`, `MAP.pads`) selon `pad.on` ; `wrap()` les mesure,
  `typed()` ne coupe jamais une [action] pendant la frappe d'une réplique. Ne plus écrire « C » ou « A » en toutes
  lettres : une seule phrase pour le clavier et la manette (le texte tactile reste à part, sans icône). Une nouvelle
  touche : l'ajouter **à la fin** de `hud.KEYS` / `PAD_BUTTONS` (les images existantes gardent leur numéro), puis
  dans `GLYPH`. `hud/key` et `hud/pad` sont rognées dans l'atlas (largeur exacte de chaque icône). Test : `glyphs.js`.

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
- Dialogues : 3 lignes maximum affichées (4 en texte grand) ; chaîne longue = la découper en plusieurs répliques.
- Tests : isoler la scène (`dogs = []`, `cars = []`, autres chiens renvoyés chez eux) ; un chien qui flâne ou une voiture
  qui passe rendent sinon un test aléatoire. Relancer un nouveau test plusieurs fois avant de le valider. Pour qu'une
  morsure porte : hors zone calme, et `graceT = 0` (sinon le répit qui suit un dialogue l'annule).
- Le service worker de `docs/` est réseau d'abord avec repli cache : pas de version à incrémenter à chaque livraison.
- Canvas simulé des tests (`sim.js`, `check_placement.js`) : il doit renvoyer un objet pour `createRadialGradient` /
  `createLinearGradient` (nuages, lumière) ; tout nouvel appel de canvas qui renvoie un objet doit y être ajouté.
- **Performances (Firefox)** : Firefox dessine souvent le canvas avec le processeur. Rien de plein écran recalculé à
  chaque image : pas de dégradé ni de mode de fusion autre qu'un remplissage uni (la lumière pré-rend ses dégradés en
  petit, `buildLight()`) ; canvas plafonné à `MAX_PIXELS` (1920 x 1080), le navigateur agrandit au-delà (sinon
  216 ms par image en 4K au coucher de soleil). Mesurer dans Firefox sans fenêtre : `firefox --headless` avec un
  profil où `browser.dom.window.dump.enabled` est vrai, la page mesure `render()` et écrit le résultat avec `dump()`.
- Placer un nouvel élément interactif : `check_placement.js` refuse la construction s'il chevauche une autre action
  (règle d'espacement). Ne pas réduire les portées pour le faire passer : le déplacer. Une nouvelle action : l'ajouter à
  la liste de la règle, avec sa portée (constante partagée avec game.js, comme `REACH`).
- Tests sans `localStorage` : `STORE` passe en mémoire. Après un KO dans un test, le menu propose d'abord
  « Reprendre la partie » : choisir `menu.sel` explicitement pour « Recommencer ».

## Reste à faire

- Kit GameMaker **en pause** (choix de Christophe : on avance sur la version web). `build.py` doit continuer à
  tourner, mais les nouveautés (fermier, petites bêtes, terriers, flair, carte, ambiances…) n'y sont pas documentées.
- Piste en réflexion : dialogues lus à voix haute (pour qu'Alice joue sans savoir lire).
