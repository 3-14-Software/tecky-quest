# Tecky Quest — contexte pour Claude Code

Mini RPG en vue de dessus, fait pour Christophe (3.14 Software, développeur Java, Fedora, il parle français) :
Tecky, le teckel au harnais rouge, cherche Alice (la fille de Christophe, 5 ans). Un seul livrable : la **version web**
(Canvas, une seule page HTML, PWA). Le kit d'assets GameMaker des débuts a été abandonné (12 novembre 2026) et retiré
du dépôt avec les dessins de la v1 (`tecky.py`, `alice.py`, `enemies.py`) : ne pas le refaire.
Langue : tout en français (interface du jeu, commentaires, README, messages de commit). Style visuel : aplats de couleurs,
contour brun `#3A1E12`, lignes simples, ambiance mignonne. Référence des personnages : `reference/alice_tecky.png`
(illustrations générées par IA, fournies par Christophe). Tecky : teckel roux, harnais rouge en vrai ; Alice : cheveux châtains
mi-longs avec frange, t-shirt jaune, jupe rose, et dans le jeu de petites chaussures rouges à bride avec des socquettes
blanches (elle est pieds nus sur l'illustration : Christophe a préféré la chausser). Elle perd une chaussure dans la
forêt (l'indice) : tant que Tecky ne la lui a pas rapportée, elle a un pied nu (sprites `alice1/*`, `alice2.frames(…, nu=True)` ;
`endingHome()` lui rend sa chaussure, au noir). Garder ces traits en cas de retouche des sprites.

## Commandes

```bash
pip install -r requirements.txt           # cairosvg, pillow, numpy (+ Node 18+ pour les tests)
python3 pack_web.py                       # web/index.html, web/tecky_quest_web/ (autonome), atlas, niveau, images x4
python3 pack_web.py --sans-hd             # la même chose sans les images x4 (le jeu reste en x2)
python3 editeur.py                        # éditeur de carte : http://127.0.0.1:8770/ (modifie carte.json)
./tests/run_all.sh                        # reconstruit puis lance tous les tests (doit finir avec exit=0)
./publish_docs.sh                         # copie la version autonome dans docs/ (GitHub Pages)
```

Jeu en ligne : https://3-14-software.github.io/tecky-quest/ — publié par `.github/workflows/pages.yml` à chaque push touchant `docs/`.
Pour livrer une modification : `./tests/run_all.sh && ./publish_docs.sh`, commit (docs/ inclus), push sur `main`.
`web/` est généré et ignoré par Git ; `docs/` est commité.
`docs/glitch/` : la démo de **Glitch**, fork pour adultes (dossier `../glitch`, son propre `CLAUDE.md`), publiée là
par son `publish_docs.sh` (https://3-14-software.github.io/tecky-quest/glitch/) ; `publish_docs.sh` d'ici l'épargne.

## Architecture

- `spritelib.py` : classe `Drawing` (parts SVG, silhouette dessinée en premier avec un trait épais = contour propre),
  `render_svg(svg, w, h, scale, pad)`, `flash()`. Les vues gauches sont le miroir des vues droites.
- `tecky2.py` et `alice2.py` : **Tecky et Alice du jeu web** (v2, lot 3 de `PLAN_V2.md`). Dessinés plus grand que
  les autres personnages puis réduits de `ECH` (Tecky 0,5, Alice 0,59 : 41 unités de haut,
  elle a 5 ans ; les adultes en font 55 à 60, le petit Lucas 45) : traits plus fins, mêmes contours (`TRAIT`).
  Tecky est **relevé sur la planche de Christophe** (`reference/v2/chat_gpt/`, « Planche d'expressions » : `_pl()`
  convertit ses pixels) : gros crâne rond, museau court, grands yeux, oreilles immenses, corps en saucisse. Mes têtes
  dessinées de mémoire ont été refusées deux fois (« vraiment moche ») : toute retouche repart de la planche. Sa
  taille se juge à côté d'Alice et des chiens (à 0,8, 0,7 puis 0,58, Christophe l'a trouvé « énorme », « encore trop
  gros ») : plus petit que tous les chiens (34 x 22 unités de profil ; l'ancien : 40 x 28), la tête sous la jupe
  d'Alice. Trois vues (`profil`, `face`, `dos`), attitudes debout / assis / couché / sur le dos, un cadre par vue
  (`CADRE` : 48 x 48, origine aux pieds), `pose()` (réglages d'une image), `EXPRESSIONS`, `ANIMS` et `REST_ANIMS`
  aux mêmes noms qu'avant ; les formes passent par une fonction de placement (`_trace`, `_torse`, `_repere`) plutôt
  que par des `transform` (cairosvg et les découpes). La mâchoire s'arrête à `MENTON`, en retrait de la truffe
  (sinon la gueule pend sous le museau). Tête de profil = un seul œil. Marche (`_foulee()` : une patte posée recule,
  elle se lève pour revenir vers l'avant) ; de face et de dos, il se dandine (`balance`, `incline`, oreilles, queue).
  Planches : `python3 tecky2.py`, `python3 alice2.py` (`reference/v2/`, dont `tecky_v2_marche.gif`). Cadences propres : `MAP.teckyFps`, `MAP.aliceFps` (marche en 8 images).
  Test : `tests/heros.py` (mêmes noms d'animations qu'avant, pieds sur l'origine, rien hors du cadre). Pour voir
  le résultat dans le jeu : `python3 v2/capture.py sortie.png "x,y,mode" "js"` (1920 x 1080, images x4, le jeu
  servi sur le port 8765).
- `chiens2.py` : **les chiens du jeu web** (v2 : roquet, bouledogue, molosse / doberman, berger / border collie),
  de la famille du Tecky de `tecky2.py` dont ils reprennent les outils et la tête : même crâne, même œil, même
  gueule, le museau allongé, raccourci ou épaissi selon la race (`museau`, `_museau()`), des sourcils froncés, un
  croc. Ce qui change d'un chien à l'autre est dans `CHIENS` (couleurs, corps, pattes, chaussettes `bas`, queue,
  oreilles, taches, collier à clous ; mesures de la tête et du corps de face et de dos : `f_tete`, `f_corps`,
  `d_tete`), écrit en pixels du jeu autour du milieu des pieds, puis réduit de `ECH` (0,47 : la taille des chiens
  d'avant, que règlent les barres de vie, les cœurs et l'aboiement du doberman dans game.js). Mêmes animations et
  mêmes nombres d'images qu'avant (le jeu attend la fin d'un aboiement, d'une morsure), sauf la marche en 8 images
  (`MAP.dogFps`, `d.fps`). KO : une vraie attitude « dos », comme Tecky. De face, Tecky et les chiens montrent un peu
  de leur croupe et leur queue derrière la tête (`tecky2._arriere_face`, `chiens2._arriere_f` : la vue de dos à
  l'envers) ; la croupe reste plus étroite que le crâne et sans pattes arrière (plus grosse, c'est un bonnet). De
  face comme de dos, une queue dressée est effilée et un peu courbée (`tecky2._queue_dressee`, `chiens2._fouet`) :
  droite et étroite, c'est un bâton ; `f_croupe` règle de combien la croupe, donc la queue, dépasse de la tête. Iris
  (`npcs._iris`) a la tête de `chiens2.tete_face()` avec `gentil` (sourcils doux, sourire). Planche : `python3 chiens2.py`
  (`reference/v2/chiens_v2.png`). Test : `tests/heros.py`.
- Ce que le moteur attend de ces trois modules (noms des animations, vues, nombres d'images, liste des chiens) est
  écrit en dur dans `tests/heros.py` (`ATTENDU`) : ne le changer qu'avec game.js. `carte.py` lit les chiens permis
  dans `chiens2.CHIENS`.
- `hens.py` (poules animées, redessinées pour la v2 et réduites autour de leurs pieds : plus petites que Tecky),
  `farmer.py` (le fermier Gaston, vu de face, 48x64, pieds en (24, 60) ; `FACE` pour son portrait ; le visage des
  humains est commun : `npcs._eyes()`, grands yeux à deux reflets comme ceux d'Alice, et `npcs._nez()`, petit nez sans
  contour — choisis par Christophe sur `reference/v2/humains_temoin.png` ; leurs épaules sont une pente douce,
  `npcs._epaule()`, et un bras croisé devant le buste ne trace son contour que sous l'épaule),
  `ducks.py` (colvert, cane, caneton, de profil, 32x32, ligne d'eau en (16, 24) ; réduits de `SCALE` autour de la
  ligne d'eau, ronds et éclaboussures compris),
  `cows.py` (vaches pie noire et pie rouge, veau, de profil, 64x48, pieds en (32, 44) ; redessinées pour la v2 dans
  la famille de Tecky, dessin réduit de `ECH` ; le veau est la même vache réduite de `VEAU`),
  `villageois.py` (villageois sans quête, vus de face comme ceux de npcs.py, dont il réutilise les outils),
  `npcs.py` (le facteur Marcel et la voisine Mamie Rose, comme `farmer.py` ; `letter_frames()` : la lettre ; Iris et
  Maman Piquette y sont réduits autour de leurs pieds, `SCALE`, pas dans leur portrait ; `CONTOUR` : ceux dont le
  contour est compensé), `herissons.py` (les petits hérissons, réduits de `SCALE`),
  `critters.py` (écureuil, chats roux et noir, de profil, 32x32, réduits de `SCALE` : un chat est un peu plus petit que
  Tecky, un écureuil bien plus petit qu'un chat ; leurs cuisses, `_cuisse()`, sont fondues dans le corps avec un pli,
  comme celles de Tecky), `vehicles.py` (voitures, camionnette, bus),
  `nature.py` (**la nature du jeu web**, v2 : chêne, bouleau, cerisier, jeune arbre, pommiers, sapins, buissons,
  roseaux, rocher, niche de trois quarts ; contour de la teinte du décor, lumière d'en haut à gauche, pas d'ombre
  ovale ; `VARIANTES` : un décor de carte.json -> ses modèles, tirés de la position ; `ECH` / `ECHELLES` : la taille
  dans le jeu ; `image()` ; `bandes()` / `bandes_image()` : la ligne où un sprite touche le sol, d'où part son ombre portée ; `sol_fleurs()`, `sol_brins()` : les détails semés dans l'herbe ; `sol_sousbois()` (`SOUS_BOIS`) : ceux du
  sous-bois ; `sol_cultures()` (`CULTURES`) : les plants du champ ;
  `sol_nenuphars()`, `sol_galets()` : ceux de l'eau et de la berge ; `fourre()` : les fourrés de la lisière, décors
  `thicket` / `thicket_dark` de `VARIANTES`, plus sombres le long de la forêt),
  `batiments.py` (**les bâtiments du jeu web**, v2 : maisons, boulangerie, grange, entrepôts, guérite, cabane
  d'Alice ; de trois quarts comme la niche, choix de Christophe sur `reference/v2/maisons_options.png` : « B et C
  mélangés », façade longue devant (`_murs_facade()`, `_toit_long()`) ou pignon devant (`_toit_pignon()`), le mur
  de droite qui fuit dans l'ombre (`FUITE`) ; ce sont des `nature.Sprite` à leur taille, inscrits dans
  `nature.CATALOGUE` / `VARIANTES` : atlas, ombre portée et choix par position comme la nature, `d.n` reste le
  décor de carte.json et son obstacle `FOOT`, dans l'emprise duquel chaque dessin tient ; `lumieres()` : les vitres
  enregistrées par `_fenetre()` → sprites `nuit/…` ; `PERCHOIRS` → `MAP.perches`, où un chat se réfugie sur chaque
  toit ; planche : `python3 batiments.py`). **Tailles** : Christophe a trouvé les maisons puis les véhicules trop
  petits à côté des villageois ; ils sont agrandis par `batiments.ECH` (maisons 1,3), `decor.ECH` (camion,
  tracteur 1,5 ; chariot 1,4 : `decor.cadre()`, `decor.svgs()`) et `vehicles.ECH` (voitures, camionnette, bus 1,5 ;
  Titine reste petite). Le jeu suit sans réglage à la main : `MAP.grow` agrandit d'autant les obstacles `FOOT`,
  `MAP.vehicleScale` les longueurs de `VEHICLE`, `MAP.perches` est déjà à l'échelle. Après un changement
  d'échelle : regarder ce qui se retrouve derrière un bâtiment ou coupé par le bord, et déplacer l'élément dans
  `carte.json` (Christophe : « n'hésite pas à adapter le positionnement sur la carte ») : le doberman de
  l'entrepôt, l'os derrière l'étal de légumes, la maison haute (sa cheminée sortait de l'écran) l'ont été.
  Les étals du marché (`etal()`) et le poulailler sur pieds (`poulailler()`) y sont aussi, sans fenêtres
  (`ECLAIRES` = ceux qui en ont). `decor.py` garde les anciens dessins, que seul l'éditeur de carte montre encore.
  `mobilier.py` (**le mobilier du jeu web**, v2, inscrit dans `nature.CATALOGUE` / `VARIANTES` comme les
  bâtiments) : conteneurs, caisses, palettes, tonneaux, bottes de foin (carrée ou ronde), cagette, banc, boîte
  aux lettres, haie, cône, heurtoir, de trois quarts comme les étals (`_boite()`, `_boite_p()` : flanc, face,
  dessus ; `_sol_boite()` : la ligne de contact) ; portique du port et balançoire sur des chevalets en A dans le
  plan qui fuit (`_chevalet()`), péniche, bitte, toboggan ; table de terrasse sous son parasol, pots de fleurs
  (trois bouquets), lampadaire, panneaux ; souche, tronc couché, champignons (amanites ou bolets), fougères, nid
  de feuilles de Maman Piquette, au contour doux de la nature ; panier d'Iris. `Sprite.sol = None` : à plat ou
  sur l'eau, pas d'ombre portée (péniche, panier). `ECH` : conteneurs et portique 1,5 (Christophe : « les
  containers et la grue sont très petits »), péniche 1,4, table 1,35, lampadaire, toboggan, balançoire et foin
  1,3, tonneaux 1,35, banc 1,2 ; le halo d'un lampadaire suit `MAP.grow.lamppost`. `MAP.grow` agrandit aussi
  `RAILS` (pieds du portique) ; `PERCHOIRS` : où un chat se pose sur un conteneur (`MAP.perches`). Un décor
  redessiné n'a plus son ancien dessin dans l'atlas (`pack_web.collect()`). Planche : `python3 mobilier.py`.
  Restent dans leur dessin de `decor.py` (planche `reference/v2/mobilier_reste_v1.png`) : terrier, pommes
  tombées, vélo, échelle, clôtures, grillages, voie ferrée, barque, bac à sable, filet de Léon, épouvantail,
  fontaine (animée : le catalogue ne sait qu'une image par sprite), pont : gardés tels quels.
  **Véhicules** (`vehicles.py` : voitures, camionnette, bus ; `decor.py` : tracteur, chariot élévateur, camion
  garés) : redessinés pour la v2 sans changer ni cadre, ni silhouette, ni roues (le jeu ne voit rien). Ils
  restent de profil, et la lumière vient d'en haut (dessus clairs `_clair()`, bas de caisse à l'ombre, passages
  de roue `_passage()`) : elle reste juste quand le véhicule roule vers la gauche, en miroir — une lumière de
  gauche ou une vue de trois quarts ne le seraient pas. Du monde derrière les vitres (`_tete()` : conducteurs,
  boulanger en toque, passagers du bus). Planche : `reference/v2/vehicules_v2.png`.
  **Ombres** : la ligne de contact (`Sprite.sol`) passe un peu au-dessus du bas des murs (`CONTACT`), pour que
  l'ombre parte de dessous le contour : posée juste sous le mur, elle laissait un liseré clair entre le bâtiment
  et son ombre. Christophe tient aux ombres détaillées (les jours entre les pieds du poulailler, sous le store
  d'un étal) : ne pas les boucher.
  `butterflies.py` (papillons, vus de dessus), `lisiere.py` (le bord de la carte : `decor()`, le placement de la
  lisière, et `tunnel()`, le tunnel de la route, un `nature.Sprite` en calques : butte, pierres, touffes ;
  `tunnel(est=True)` = le même, éclairé de la droite, que le jeu pose en miroir au bord est : la lumière vient
  toujours d'en haut à gauche), `items.py`, `decor.py`, `tiles.py`, `hud.py` :
  dessins et animations. `tiles.py` : tileset Wang/marching squares de 16 tuiles par transition (bits NO=1, NE=2, SO=4, SE=8),
  tuile 0 vide, 16 colonnes, `PAIRS`, `PRIORITY`, `resolve()`. Là où trois terrains se rencontrent (ou deux sans
  paire), `needs_composite()` : la version web pose une tuile composée (`composite()` : chaque terrain par-dessus le
  précédent ; `COMPOSITES` dans pack_web, ajoutées au tileset à partir de `COMPOSITE_BASE`) au lieu de remplacer un
  terrain par un autre (encoches carrées au bout des chemins et des trottoirs). Un chemin s'arrête au bord de la
  route (coins de la route intacts) : sinon il mord sur la chaussée, sous le passage piéton.
  **Bords arrondis** : le champ des coins est interpolé en douceur (`_ease()`, 3t² - 2t³), il arrive à plat sur les
  bords de la tuile : un contour les traverse toujours d'équerre, la courbe d'un angle repart dans l'axe du bord
  droit voisin. Avec une interpolation linéaire, il y avait une cassure à chaque angle de mare, de chemin, de
  place (Christophe l'a vue tout de suite) : ne pas y revenir. `waterVal()` de game.js fait le même calcul.
  **Eau** (`_shore()`, `SHORE`, `BANKS`) : sur la rive de terre, lèvre d'herbe, sable, sable mouillé ; dans l'eau,
  hauts-fonds clairs, eau moyenne, puis le fond (la couleur des tuiles pleines) ; ombre de la berge du haut et de
  gauche, écume en tirets le long de celle du bas et de droite (motif périodique : il se raccorde d'une tuile à
  l'autre). Les limites des bandes larges suivent le champ (continu entre tuiles), pas la distance approchée.
- `music.py` : **source unique** de la musique (thème « Promenade de Tecky », 32 mesures, boucle ; fanfare de victoire et
  musique de défaite, 3 mesures chacune à 140 BPM, même durée). Génère les données
  `SONGS`/`WINSONG`/`LOSESONG` jouées par le séquenceur WebAudio du jeu (`Music.start('main' | 'win' | 'lose')`).
  Variations du thème par zone (`STYLES`, `events(style)` : `_lead`, `_bass`, `_arp`, `_drums`) : même mélodie, mêmes
  accords, même grille de phrases, tempo propre ; « base » (niche, campagne) = le thème d'origine.
  Village plus entraînant (152), ferme country (136 : basse alternée, rouleaux de banjo, notes glissées = 6e champ),
  forêt calme (108 : basse tenue, écho), parc boîte à musique (126, sans batterie), industrie mécanique (140) ; et la
  berceuse de la fin (84, sans batterie, timbre `TIMBRE.end`).
- **La carte est une donnée** : `carte.json` (en tuiles ; `carte.py` : `charger()`, `valider()`, `enregistrer()`, format
  stable, une entrée par ligne ; `python3 carte.py --verifier` dans `run_all.sh`). Terrain = 65 lignes de 97 coins (une
  lettre par terrain, `LEGENDE`), `details` (détails au sol, tuile entière ; « fleurs » = massifs, perchoirs des
  papillons), `decor` (sapins de la forêt et clôtures compris), listes d'éléments (`items`, `dig`, `enemies`, `signs`,
  `tunnels`, bêtes, villageois), personnages et repères (`start`, `alice`, `title`, `ending`), quêtes (`letters`,
  `balls`, `toys`, `babies`, `goal`, `ballBox`, `pen`, `penGate`, `track`), route (`traffic` : `y` = première rangée,
  passages, véhicules ; `roadTunnels`), `calm`, `zones` (rectangles), `landmarks`. Se déduisent de la carte, dans
  `pack_web.py` (`derived_decor()`, `build_map()`) : poteaux des panneaux, terriers, clôtures de l'enclos, filet de Léon,
  rails et heurtoirs, coins du pont (sous chaque décor `bridge`, posé sur une position entière), traces de pattes,
  perchoirs des papillons, marquages et passages de la route, lisière. Une nouvelle donnée de carte : dans
  `carte.json`, `carte.py` (`ORDRE`, `valider()`), `pack_web.py`, et l'éditeur (`editeur/etat.js` : `objets()`).
- Éditeur de carte (`editeur.py` : serveur local 127.0.0.1:8770, atlas et tileset dessinés au démarrage, tuiles
  composées à la demande `/tuile`, `PUT /carte.json` refusé si le fichier a changé entre-temps (ETag) ; page
  `editeur/` : `sol.js` = le sol calculé comme `build_map()` (test `editeur_sol.js`), `etat.js` (carte, historique,
  objets), `vue.js` (dessin), `outils.js` (souris, clavier), `panneaux.js` (interface)). Terrain au pinceau sur les
  coins, détails, décors et éléments à la souris, zones et rectangles à poignées. « Vérifier » : `pack_web.py`, puis
  `check_placement.js --json` (problèmes avec leur position, grille du parcours à pied) et `export_voix.js --check`.
  « Essayer ici » : `web/essai.html` = le jeu précédé de `const ESSAI = [x, y, mode]` ; `startEssai()` lance la partie
  à cet endroit, sans titre, intro ni sauvegarde.
- `pack_web.py` : atlas (frames rognées), niveau (lu dans `carte.json`, `MW=96`, `MH=64` tuiles ; variantes des tuiles
  choisies d'après la position, `hash3` = celui de game.js, et texture d'une tuile composée d'après ses coins,
  `tiles.composite_seed()` : modifier un coin ne change rien ailleurs),
  `index.html` à partir de `web_src/index.template.html` + `game.js`, paquet autonome (manifest, service worker, icônes, `serve.sh`).
  **Images nettes** (`HD`, `PAGE`, `collect(r)`, `pack_hd()`, `build_hd()`) : l'atlas et le tileset embarqués dans la
  page sont en pixels x2 ; `web/atlas_x4_N.png` et `web/tiles_x4.png` sont les mêmes dessins rendus deux fois plus
  fins, **aux mêmes places et dans les mêmes cadres** (`ATLAS` ne change pas), l'atlas découpé en pages de 4096 px :
  `pack()` ne met jamais une image à cheval sur un multiple de `PAGE` (2048 px x2). Ils ne sont redessinés que si
  un module de dessin a changé (`web/hd.json`), sont copiés à côté de la page autonome et publiés par
  `publish_docs.sh` ; leur adresse porte une version (`?v=`) pour qu'une page n'aille jamais avec de vieilles images.
  Tests : `nettete.js`, `nettete.py` (les images x4 réduites de moitié redonnent les images x2).
  Lance `web_src/check_placement.js` (`--json`, `--infos` pour l'éditeur) : rien dans l'eau ou un obstacle (canards : dans l'eau), chaque papillon a des fleurs, et tout (personnages,
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
  Rivière d'un bord à l'autre (y 42..45) avec **un seul pont** (décor `bridge` en x 80 ; `BRIDGES` déduits : coins
  x 79..81 rendus non-eau ; garde-corps = `RAILS` dans game.js), forêt au sud-est (sous-bois, sapins hors des sentiers,
  placés une fois par l'ancien `forest_firs()` et figés dans `carte.json`), parc au sud-ouest (cabane d'Alice). Zones
  (`MAP.zones`), route (`traffic.y` : marquages, voies, `FARM.roadY` = `MAP.farmRoadY`), terrain des ballons
  (`BALL.box` = `MAP.ballBox`) et places de la scène de fin (`ENDING.alice` / `.tecky` = `MAP.ending`) viennent de
  `carte.json`. Restent écrites en dur dans des tests, à suivre si la carte change : `map.js` (pont, rivière),
  `world.js`, `music.js`, `traffic.js`, `calm.js`, `farm.js`, `leon.js`, `sim.js` (étang), `effects.js`. Zone industrielle au sud de la route : le dépôt (x 30..56) et, en dessous, le port au bord
  de la rivière (x 30..64) : chariot élévateur, camion,
  conteneurs sous le portique (pieds dans `RAILS`), cabane du gardien, voie ferrée du quai (`rail`, à plat), bittes,
  péniche. Terrains ajoutés : `field` (champ), `forest` (sous-bois).
  **Sous-bois et champ** (v2) : leurs tuiles sont calmes (`tiles.tex_forest()` : un vert uni ; `tex_field()` :
  deux buttes par tuile, les mêmes partout, crêtes en `tiles.SILLONS` → `MAP.furrows`) et le jeu les habille une
  fois dans le sol, comme l'herbe : `woodDetails()` (`WOOD` : taches de soleil et plages d'ombre, puis fougères,
  mousse, champignons, pommes de pin, brindilles, feuilles mortes, `sol/sousbois`, `MAP.wild`, dans les tuiles de
  sous-bois plein `MAP.wood`) et `fieldDetails()` (`FIELD` : des rangs de plants `sol/culture` sur les crêtes,
  pousses, salades, carottes, poireaux ; la culture change toutes les `FIELD.band` buttes, la même d'un bout à
  l'autre du rang ; les tuiles du bord du champ sont plantées là où le champ est assez loin de son bord,
  `fieldBits()`). L'ancien semis d'aiguilles du sous-bois (des traits en tous sens) faisait du bruit à côté des
  aplats de la v2 : ne pas y revenir. Test : `map.js`.
- Bord de la carte (pas de mur invisible muet) : la caméra déborde de `EDGE.cam` (une tuile) au-delà de la carte
  (`camClampX()` / `camClampY()`, partout sauf le cadrage fixe de la scène de fin) et montre une lisière
  (`MAP.edge.decor` = `EDGE_DECOR`, générée par `edge_decor(corner_grid(), edge_keep())` dans pack_web : fourrés et
  arbres, sapins le long de la forêt, jamais par-dessus ce que liste `edge_keep()`) sur un sol qui prolonge celui du
  bord (`MAP.edge.ring`, `lisiere.RING` tuiles : `pick()` de `build_map()` avec les coins ramenés sur le bord ; la
  route, la rivière et le ruisseau continuent, `waterAt()` aussi). Aux deux bouts de la grande route, un tunnel
  (`ROAD_TUNNELS`, sprite `decor/tunnel` ; à l'est, `decor/tunnel_est` en miroir) où les voitures disparaissent ; sa butte est un obstacle
  (`FOOT.tunnel`, `EDGE_SOLIDS`) : Tecky s'arrête devant la bouche. La lisière n'est pas un obstacle : c'est `BOUND`
  (`offMap()`, dans `blockedFeet()`) qui arrête au bord. Tecky qui y pousse sans avancer le dit (`edgeBump()`,
  `EDGE.push` s, au plus une fois toutes les `EDGE.again` s ; axe par axe : au joystick, il glisse le long du bord ou de
  la butte, et ça compte ; près de la butte, `EDGE.tunnelY`, c'est le message du tunnel). Les bulles de mots restent dans l'écran. Test : `edge.js`.
- `web_src/game.js` : tout le moteur. Monde en pixels x2 (tuile = 64), caméra 960x540, interface 1920x1080 (`GW`/`GH`).
  Sol pré-rendu en blocs de 1024 px de canevas (`ground`, `groundChunk()`, `buildChunk()`, `groundTile()`, marge de
  la lisière comprise) : une seule image de la carte dépasserait la taille de canevas permise sur certains
  téléphones. Un bloc n'est peint que quand la caméra l'atteint, et seuls les `GROUND_MAX` derniers sont gardés.
  Décors `FLAT` (pont, bac à sable) dessinés sous les personnages.
  **Nature** : `decorLook(n, x, y)` choisit le modèle d'un arbre, d'un sapin, d'un buisson d'après sa position
  (`MAP.variants`, `hash3`) ; `d.n` reste le nom du décor (obstacle `FOOT`, refuge, feuilles), `d.key` son sprite,
  `d.look` le nom du sprite (ombre, perchoirs) ; jamais en miroir (ils sont éclairés de la gauche). Peints une fois dans chaque bloc de sol
  (`buildChunk()`) : l'habillage de l'herbe (`groundDetails()`, `MEADOW` : plages claires ou sombres là où toutes les
  tuiles sont de l'herbe pleine `GRASS_FULL`, touffes `sol/brins`, bouquets `sol/fleur`, chacun dans sa tuile) et les
  ombres portées (`groundShadows()`, `SHADOW`). **Ombres** : il n'y a pas d'image d'ombre dans l'atlas ; le jeu couche
  la silhouette de chaque décor du côté opposé au soleil à partir de sa ligne de contact (`MAP.sols[look]`, des
  points [u, b] écrits par `pack_web.sols()` : « pied » = une horizontale à l'origine, « contour » = au point le
  plus bas, ou les murs d'un bâtiment), d'un bloc là où cette ligne est horizontale, colonne par colonne là où
  elle monte (`blitCols()`). Les silhouettes passent, opaques, par un canevas à part, teinté d'un coup
  (`source-in`) puis posé avec `SHADOW.alpha` : deux ombres ne se cumulent pas. Tous les décors en ont une, sauf
  ceux qui sont à plat ou sur l'eau (`decor.SANS_OMBRE` ; `decor.SUR_PIED` = « pied ») ; leur ancien ovale n'est
  plus dessiné. Elles s'allongent le soir : `shadowLen()` suit `sun` (`SHADOW.len`, par paliers de `step`), et
  les blocs de sol périmés sont repeints un par image (`groundRepaint`), sans à-coup. Pièges rencontrés : des
  bandes sans recouvrement laissent des liserés ; une ligne de contact qui suit le bas d'une silhouette arrondie
  effiloche l'ombre. **Personnages, bêtes et véhicules** (`MAP.cast` = `pack_web.portees()`, le début de leur clé
  dans l'atlas) : leur ovale est retiré à la construction (`pack_web.sans_ovale()` enlève `Drawing.under` ;
  `vehicles.frames()` aussi) et le jeu couche leur silhouette à chaque image (`castShadow()`, depuis
  `shadowAtlas`, une copie sombre de l'atlas x2 faite une fois). `drawCastShadows(list, cx, cy)` rejoue la liste triée de
  `drawWorld()` avec `ctx` remplacé par `NULL_CTX` (qui ne dessine rien) : seuls les `drawSpr()` des familles à
  ombre posent leur silhouette, sous tous les sprites. Donc : une fonction de dessin de la liste est appelée deux
  fois par image (trois devant un bâtiment le soir), elle ne doit rien modifier ; `opt.lift` = hauteur d'un saut
  ou d'une grimpette (l'ombre reste au sol). Les canards (sur l'eau), les objets et les papillons gardent leur
  dessin. **Ombres fusionnées** (demande de Christophe : un seul soleil, un endroit est à l'ombre ou ne l'est
  pas) : les silhouettes vont, opaques, dans un canevas à part (`shadowLayer`) ; là où le sol porte déjà l'ombre
  d'un décor, elles sont gommées (`destination-out`) par le masque du bloc de sol (`ch.m` : les ombres peintes par
  `groundShadows()`, gardées à demi-taille, `SHADOW.mask`) ; le reste est posé avec `SHADOW.alpha`. Tout se fait
  dans l'emprise de chaque silhouette (`shadowRects`, en pixels entiers), jamais sur tout l'écran (Firefox) ; une
  emprise traitée est effacée, donc deux ombres de personnages qui se recouvrent ne se cumulent pas non plus.
  Test : `map.js`.
  **Images nettes** (`HD`, `HD_SRC`, `wantHD()`, `loadHD()`, `setHD()`, `blit()`) : sur un grand écran (au moins
  `HD_MIN` pixels de canevas par pixel de monde, pas un téléphone ni une tablette, pas une page ouverte depuis le
  disque), le jeu charge les images x4 à côté de la page et lit l'atlas par `blit()` (même cadre, deux fois plus de
  pixels, dans la bonne page) ; le sol passe à des blocs de 8 tuiles. Sinon, ou si le chargement échoue, tout reste
  en x2. Tout dessin depuis l'atlas passe par `blit()` (sauf les panneaux 9-slice et la carte de la pause, en x2).
  `HD.on` : vrai pour le monde ; pour l'interface, seulement si elle est agrandie (ses sprites x2 sont à leur
  taille en 1080p). Pour comparer : la même adresse suivie de `?x2` reste en x2 ; l'écran titre affiche
  « images x4 » à côté de la version quand elles sont chargées. `drawSpr()` pose l'origine sur la grille des pixels du canevas : un sprite immobile entre deux
  pixels serait lissé.
  Décors animés (`decor.ANIMATED`, ex. la fontaine : la fonction reçoit la phase 0..1 ; fps dans `MAP.decorFps`).
  Eau animée : le tileset a une eau unie (`tiles.tex_water()`) et `drawWater()` y sème des
  vaguelettes `fx/ripple` légères (une par tuile, un cycle sur deux, position tirée par `hash3`) et, en plus, des
  scintillements `fx/glint` (mini-étoiles, cadence propre), seulement en eau profonde (`deepWater()` : tout le contour plus une
  marge, sinon ils mordent sur le liseré des berges).
  **Eau** : `waterVal(x, y)` = présence de l'eau (0..1), interpolée entre les coins comme le dessin des tuiles
  (`soften()` = `tiles._ease()`) : la rive dessinée passe à 0,5 ; `waterAt()` = au-delà de `WATER_EDGE` (les pieds
  s'arrêtent un peu avant la rive). Habillage peint une fois dans le sol (`waterDetails()`, `POND`) : fonds plus
  sombres au large (là où tout est eau pleine, `fullWater()`), nénuphars `sol/nenuphar` par bouquets entre les
  hauts-fonds et le large (`lilyAt()` ; les vaguelettes évitent leur tuile), galets `sol/galet` sur le sable
  (`shorePoint()` : un point de la tuile ramené sur une ligne de niveau de `waterVal`). Seulement dans les tuiles
  eau / herbe (`shoreTile()`, `MAP.shore`) : rien le long d'un quai. Test : `map.js`.
- Ambiance (`game.js`, section « petits effets ») : poussière sous les pattes (`dusts`, `DUST`), feuilles qui tombent des
  arbres et sapins visibles (`leaves`, `LEAF`, sprite `fx/leaf` : une image par couleur), ombres de nuages pré-rendues
  (`clouds`, `CLOUD`, `buildClouds()`), du jour à la nuit (`sun`, `SUN`, `drawLight()` : teinte multipliée sur le
  monde seulement ; vignette et halo pré-rendus en petit par `buildLight()` ; lampadaires et lumière des retrouvailles
  par `glowSpot()`, `hug` ; fenêtres des bâtiments allumées avec les lampadaires : `drawWindows()`, `WINDOWS`, sprites
  `nuit/…` posés après la teinte ; ce qui est devant un bâtiment y est redessiné en gomme dans un petit canevas à
  part, `ctx` remplacé le temps du dessin, pour rester devant ses fenêtres). `sun` suit `sunGoal()` = nombre d'indices (3 aux retrouvailles, 4 pendant la scène de fin
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
  Chromium, pas pour Firefox : `fsRefusedAt`, la ligne dit alors « touche F, ou un clic » ; en sortir est toujours permis), Vibrations, Météo,
  et, depuis l'écran titre seulement, « Réinitialiser la progression » (`resetAsk` : confirmation, « Non » d'abord ;
  au toucher, deux cases `resetPills()` ; `resetProgress()` efface sauvegarde, records et badges, pas les options ;
  lignes plus serrées au-delà de 9, `optBox(i, n)`). Test : `options.js`.
- Badges (`MAP.badges` = `hud.BADGES`, image i de `hud/badge`, la dernière = verrouillé ; `BADGE_INFO`, `BADGES_KEY`,
  gardés d'une partie à l'autre) : `checkBadges()` toutes les demi-secondes, `winBadges()` à la victoire (aventure,
  sans morsure = `bitten` faux, sauvegardé : seules les vraies morsures comptent, `hurtPlayer(…, bite)` — l'aboiement du
  doberman et la charge du chien de berger font mal sans être des morsures ; moins de 10 min). `unlockBadge()` : annonce « Nouveau badge ! »
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
- Zones calmes (`MAP.calm` = `calm` de carte.json, bornes comprises : le village au nord de la route, trottoir compris — on parle à
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
- Circulation (`cars`, `VEHICLE`, `TRAFFIC`, données `MAP.traffic` : voies, passages `traffic.crossings`) : à droite sur la
  grande route, retour par l'autre bord de la carte, distances de sécurité. Un choc projette Tecky sur le bas-côté
  (klaxon avant, « Ouf ! ») **sans dégâts** ; aux passages piétons, arrêt systématique. Les chiens sont aussi
  écartés. Test : `traffic.js`.
- Papillons (`butterflies`, `BFLY`, `MAP.flowers`) : 16, surtout au parc, mais aussi niche, village (visibles dès
  l'écran titre), campagne sud-ouest, verger de la ferme, clairière. Volettent en zigzag avec une ombre au sol, se
  posent sur les pots de fleurs ou les massifs (détails « fleurs » de carte.json, `FLOWER_BEDS`), s'envolent si Tecky approche
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
  clairière de la forêt (herbe, pas de sapins, une zone de `calm`, sentier depuis le chemin ouest, nid
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
- Flair (R, Y à la manette, bouton à truffe au toucher ; `SNIFF`) : piste des empreintes d'Alice (`fx/footprint` : une chaussure, un pied nu) vers
  `arrowTarget()`, le long d'un vrai chemin à pied (`buildWalkGrid()` : grille de 16 px rasterisée une fois,
  `fieldTo()` : distances par parcours en largeur, `scentPath()`). Les trésors proches scintillent. Test : `tunnel.js`.
- Os dorés : le trésor sous les traces de pattes (`item/goldbone`, `treasures` = os dorés trouvés, HUD et victoire).
- Compteurs du HUD (`hudCounters()`) : empilés à droite sous le score, dans l'ordre os dorés (dès le premier trouvé),
  poules rentrées, lettres retrouvées, Pompon retrouvé (0/1, 1/1) ; ceux des quêtes seulement pendant la quête
  (`asked`). Quand ils descendraient jusqu'aux boutons d'action (au toucher, le bouton du flair ; sinon, les aides de
  touches du bas), ils passent sur une colonne de plus, à gauche (`COUNTER`, `counterBox()`). Test : `hud.js`.
  Au toucher, les boutons Pause (`PAUSE_BTN`) et Plein écran (`FS_BTN`) sont en haut, à gauche du score.
- Petites bêtes (`critters`, `CRITTER`, `REFUGES`, `MAP.critters`) : écureuils et chats flânent ; Tecky trop près ou
  qui aboie les fait filer vers un refuge pas de son côté (arbre/sapin : l'écureuil grimpe et disparaît ; toit ou
  conteneur : le chat saute et feule), ils redescendent quand il est loin. Points la première fois (`scored`, sauvegardé).
- Repos (`restPose()`, `REST`, `tecky2.REST_ANIMS` → `MAP.rest`, ajoutés à `FPS` / `LOOP`) : sans geste du joueur, Tecky
  s'assoit (6 s ; de dos, il se tourne vers nous), bâille et se gratte à tour de rôle, puis s'endort (24 s) avec des
  « z » (`fx/zzz`, effets à durée de vie : `life`, `vx`/`vy`, `grow`). Tout geste le réveille ; jamais si un chien menace.
  Badge « Roi de la sieste » : seulement
  ce sommeil-là (`napped`), pas celui de la scène de fin. Test : `rest.js`.
- Canards (`ducks`, `DUCK`, `MAP.ducks` : [espèce, x, y, famille], `ducks.py`) : nagent près de leur place sans quitter
  l'eau (`duckWater()`, vérifié aussi par `check_placement.js`), cancanent, plongent. Tecky trop près ou qui aboie :
  les adultes s'envolent vers un autre coin d'eau loin de lui (`pickLanding()`, dans la carte : l'eau continue
  au-delà du bord), ombre au sol, et s'y posent ; la cane suivie de canetons (même famille, `lead`) s'éloigne à la nage
  avec eux en file, en gardant son cap (`fleeDa`). Coincée contre la rive (`DUCK.cornered`, `stuckMove`, ou un recoin où
  il faudrait repartir de l'autre côté), toute la famille s'envole vers une autre mare (`DUCK.familyFar`), les
  canetons en file derrière elle (animation `fly` de ducks.py : petit aileron qui bat), et s'y pose. Points la première fois (`scored`,
  sauvegardé dans `ducks`). Test : `ducks.js`.
- Zones (`ZONES` = `MAP.zones` : rectangles en tuiles, la première zone dont un rectangle contient le point, un bord
  posé sur le bord de la carte sans limite, la dernière couvre tout ; `zoneAt()`, `updateZone()` ; huit, dont « Le verger » au sud de la route, qui reprend la musique de
  la ferme : champ `music` d'une zone) : bandeau à l'arrivée (`banner`), étiquettes de la carte, ambiance sonore
  (`Ambience`, `AMB_EVENTS`, `ambSound()` : oiseaux, coq, sonnette, cliquetis ; clapotis selon l'eau autour) et timbre
  de la musique (`TIMBRE` et variation du thème `SONGS`, `Music.zone`). Changement (`MUSIC_ZONE`) : Tecky doit
  rester `settle` (2 s) dans la zone (`tuneT` ; un passage éclair ne change rien), puis `Music.setZone()` le demande
  (`Music.want`) et le séquenceur fait un fondu enchaîné pendant la dernière mesure d'une phrase (4 mesures) : une
  couche de gain par zone (`Music.layers` : sa variation, ses instruments ; `fadeTo()`, `ramp()`), et le tempo glisse
  de l'une à l'autre pendant ce fondu (`Music.glide`, `stepLen()`). Nouvelle partie, Continuer : fondu rapide (`cut`),
  nouveau tempo tout de suite. L'écran titre joue toujours le thème d'origine (`TITLE_MUSIC`, remis par `toTitle()`
  après une partie, la scène de fin ou une défaite). Test : `music.js`. La rivière n'est pas une zone : celles du nord et du sud vont jusqu'à son
  milieu (y 43,6), pour que rien ne change en la longeant ou en passant le pont ; elle garde son étiquette sur la
  carte de la pause (`LANDMARKS` = `MAP.landmarks`). Test : `world.js`.
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
- **KO** : Tecky et les chiens ont une vraie attitude « dos » (`_torse` retourne le torse, la tête est posée à
  l'envers, l'oreille reste au sol) ; une queue dressée doit se coucher (`queue_ko`), sinon elle passe sous le sol
  (`tests/heros.py` le voit).
- **Taille de Tecky** : son sprite de profil dépasse sa boîte de collision (pieds, demi-largeur 16 px) de 22 px vers
  l'avant ; ce qui part de sa gueule (`MOUTH`, `doBark()`, `snooze()`) est réglé sur le dessin. Changer `ECH` :
  revoir ces réglages, `CADRE`, et regarder Tecky à côté d'Alice et des chiens (`v2/capture.py`).
- **Ronds cernés** : Christophe ne veut plus de formes rondes posées sur un corps avec leur contour complet (les
  cuisses en cercle des chats, les épaules en boule des humains : « des cercles moches »). Une articulation se fond
  dans la silhouette, avec au plus un pli du côté visible. De même, Alice de face a un cou (`alice2.COU`) : sans
  lui, ses cheveux de derrière faisaient une barre sous le menton.
- **Portraits** (`hud.tecky_portrait`, `FACE` dans game.js) : une réplique désigne le visage par son numéro ; en
  ajouter à la fin. `tools/export_voix.js` en tire le ton (`TONE`).
- **IA des chiens** : `steer()` contourne les obstacles en choisissant le côté le plus court (simulation avec `moveActor`) et
  garde ce côté tant que la route directe est barrée (grillages longs). Ne pas revenir à un détour de durée fixe : tremblement.
  Tests : `tests/obstacles.js`, `fence.js`, `fence_scan.js` (210 cas, 0 clignotement de direction). Ces deux
  derniers se jouent au premier grillage du dépôt et comptent sur le conteneur posé juste en dessous
  (`["container", 33.5, 25.4]`) : il barre le chemin de droite et laisse un couloir sous le grillage. Le
  déplacer ou le rapprocher du grillage les fait échouer (c'est arrivé en l'agrandissant).
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
  Images nettes : sur un canevas de 1920 x 1080 (échelle 2), Firefox va plus vite avec les images x4 (copie à
  l'identique : 6 à 12 ms par image) qu'en agrandissant les x2 (11 à 17 ms) ; à une échelle intermédiaire (1,33),
  réduire les x4 coûtait jusqu'à 45 % de plus, d'où le seuil `HD_MIN` (1,5). La fenêtre sans tête n'est pas en
  1080p : forcer dans la page `cv.width = 1920; cv.height = 1080; scale = 2` avant de mesurer.
- **Listes de carte.json et sauvegarde** : la sauvegarde retient chiens (`d.id`), trésors, petites bêtes, canards,
  lettres, poules de quête, ballons, jouets et petits hérissons par leur rang (`carte.INDEXEES`) : en ajouter à la fin,
  et ne pas en retirer au milieu sans augmenter `SAVE_V` (l'éditeur prévient). Tailles fixes (`carte.TAILLES`) : 5
  lettres, 5 ballons, 3 jouets (canard, anneau, corde), 3 petits hérissons ; un seul de chaque indice ; un trésor au
  centre d'une tuile (x,5 ; y,5). Le premier roquet reste assez loin de la niche (pas d'attaque dès la fin de l'intro).
  Le texte d'un panneau change : `node tools/export_voix.js` (l'éditeur le propose après « Vérifier »).
- Placer un nouvel élément interactif : `check_placement.js` refuse la construction s'il chevauche une autre action
  (règle d'espacement). Ne pas réduire les portées pour le faire passer : le déplacer. Une nouvelle action : l'ajouter à
  la liste de la règle, avec sa portée (constante partagée avec game.js, comme `REACH`).
- Tests sans `localStorage` : `STORE` passe en mémoire. Après un KO dans un test, le menu propose d'abord
  « Reprendre la partie » : choisir `menu.sel` explicitement pour « Recommencer ».

## Reste à faire

- **V2 en cours** : le plan et son avancement sont dans `PLAN_V2.md` (graphismes d'abord, puis textes en données et
  anglais, durée, voix, vitrine). Lots 2 (images nettes) et 3 (Tecky, Alice et les chiens : `tecky2.py`, `alice2.py`,
  `chiens2.py`) faits ; lot 4 (paysage) en cours : nature, ombres portées, herbe, eau, lisière, bords
  arrondis, bâtiments (étals et poulailler compris), ombres portées de tout (décors, personnages, bêtes,
  véhicules) allongées le soir et fusionnées, sous-bois et champ, mobilier (`mobilier.py` : du pot de fleurs au
  portique du port) et véhicules faits ; reste l'habillage des zones. Les études graphiques sont dans `v2/` (`python3 v2/temoin.py` écrit l'écran
  témoin dans `reference/v2/`) : des images fixes, que ni `game.js` ni `pack_web.py` n'utilisent encore (le décor
  de `nature.py` est dans le jeu depuis le lot 4). Les pistes générées par Christophe avec ChatGPT sont dans
  `reference/v2/chat_gpt/`.
- Piste en réflexion : dialogues lus à voix haute (pour qu'Alice joue sans savoir lire).
