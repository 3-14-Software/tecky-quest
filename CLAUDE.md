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

## Vocabulaire : lieux et épisodes

Demande de Christophe (14 novembre 2026) : ne plus dire « le monde » ni « la côte » pour les cartes — ces mots
poussaient à des raccourcis (« si la carte est le monde… »). **Un épisode = un lieu à une saison** :

| Épisode | Nom | Lieu (carte) |
|---|---|---|
| `printemps` | La région de Tecky (printemps) | `region` — `carte.json` |
| `ete` | Les vacances à la plage (été) | `plage` — `cartes/plage.json` |
| automne (à faire) | La région de Tecky (automne) | `region`, la même carte : d'autres couleurs, quêtes et indices (une surcharge) |
| hiver (à faire) | Les vacances à la montagne (hiver) | `montagne` (à faire) |

- Ces noms sont ceux du travail (comptes rendus, documentation, code) ; le joueur voit toujours « Le printemps »,
  « L'été » : quatre épisodes, un par saison.
- `episodes.json` : `lieu` = la carte où l'épisode se joue (ses indices, Alice, ses badges). `game.js` :
  `EP().lieu`, `auLieu()`. **Rien dans le moteur ne doit dépendre du nom d'une carte** : ce qui est propre à un
  épisode se décide d'après l'épisode (`episode`, `EP()`), pas d'après `MAP.id`. Les badges d'un épisode se
  gagnent dans son lieu, pendant cet épisode ; l'écran titre montre la carte de départ de l'épisode
  (`EP().depart`).
- La région de Tecky reste la carte de départ des voyages, pour une raison pratique seulement. Idée de
  Christophe, pas décidée : une petite carte « la maison d'Alice » (jeux bonus), qui servirait de point de
  départ aux cinématiques (voir `PLAN_V2.md`).
- Les cartes s'appelaient `monde` et `cote` jusqu'au 14 novembre 2026 : `loadSave()` lit encore une sauvegarde
  à ces noms (`OLD_MAPS`). Dans la suite de ce fichier, « le monde » = la région de Tecky, « la côte » = la
  plage (la zone « La Côte Fleurie », son morceau et son ambiance gardent l'identifiant `cote`).

## Commandes

```bash
pip install -r requirements.txt           # cairosvg, pillow, numpy (+ Node 18+ pour les tests)
python3 pack_web.py                       # web/index.html, web/tecky_quest_web/ (autonome), atlas, niveau, images x4
python3 pack_web.py --sans-hd             # la même chose sans les images x4 (le jeu reste en x2)
python3 editeur.py                        # éditeur de carte : http://127.0.0.1:8770/ (modifie carte.json)
python3 episodes.py                       # vérifie episodes.json (les épisodes, leurs cartes)
python3 music.py                          # contrôle des partitions ; écoute : web/musique.html (après pack_web.py)
./tests/run_all.sh                        # TOUS les tests : seulement dans les trois cas de « Quand lancer les tests »
./publish_docs.sh                         # copie la version autonome dans docs/ (GitHub Pages)
python3 tools/mesure_firefox.py           # coût du rendu dans Firefox sans fenêtre (jeu servi sur le port 8765)
```

Jeu en ligne : https://3-14-software.github.io/tecky-quest/ — publié par `.github/workflows/pages.yml` à chaque push touchant `docs/`.
Pour livrer une modification : `./tests/run_all.sh && ./publish_docs.sh`, commit (docs/ inclus), push sur `main`.
`web/` est généré et ignoré par Git ; `docs/` est commité.
`docs/glitch/` : la démo de **Glitch**, fork pour adultes (dossier `../glitch`, son propre `CLAUDE.md`), publiée là
par son `publish_docs.sh` (https://3-14-software.github.io/tecky-quest/glitch/) ; `publish_docs.sh` d'ici l'épargne.

## Quand lancer les tests

**Ne pas lancer `./tests/run_all.sh` à la moindre modification** (demande de Christophe, 14 novembre 2026) : la
batterie entière est longue. Elle ne se lance que dans trois cas :

1. **avant de pousser en ligne** (`./tests/run_all.sh && ./publish_docs.sh`, puis commit et push) ;
2. **à la demande de Christophe** ;
3. **après un gros refactoring** : un changement qui traverse le moteur (collisions, sauvegarde, cartes, boucle
   de jeu, format de `carte.json`, atlas ou tileset), pas une retouche, même étendue, d'un seul sujet.

Le reste du temps, ne vérifier que ce que la modification touche :

```bash
python3 pack_web.py --sans-hd && python3 tests/regen.py   # une fois, après une modif de game.js, d'une carte ou d'un dessin
node tests/zoe.js                                         # puis le ou les tests du sujet (deux ou trois au plus)
```

- Un dessin seul : la planche du module (`python3 tecky2.py`…), `python3 tests/heros.py` ou `tests/edges.py` s'il
  est concerné, une capture (`v2/capture.py`) ; pas de tests Node.
- Un texte ou une réplique : `node tests/textes.js`, `node tools/export_voix.js` (puis `--check`).
- Une carte : `python3 carte.py --verifier` ; `pack_web.py` lance déjà `check_placement.js`.
- Un test qui échoue : le relancer seul, pas la batterie.
- Ne pas relancer la batterie « pour être sûr » à la fin d'une tâche, ni avant un commit qui n'est pas poussé.
  Dans le compte rendu, dire quels tests ont été lancés, et que la batterie entière ne l'a pas été.

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
  (`ECLAIRES` = ceux qui en ont). `decor.py` garde les anciens dessins, qui ne servent plus : l'éditeur de carte montre ceux du jeu (`ED.cle()`).
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
  Les quinze décors restés dans `decor.py` (terrier, pommes tombées, vélo, échelle, clôtures, grillages, voie
  ferrée, barque, bac à sable, filet de Léon, épouvantail, fontaine — animée : le catalogue ne sait qu'une image
  par sprite —, pont) gardent leur dessin, relooké sur place (`decor._dans()` : une plage claire à gauche, de
  l'ombre à droite). Planche de ces retouches, des objets et de Titine : `reference/v2/relooke_24.png`.
  **Véhicules** (`vehicles.py` : voitures, camionnette, bus ; `decor.py` : tracteur, chariot élévateur, camion
  garés) : redessinés pour la v2 sans changer ni cadre, ni silhouette, ni roues (le jeu ne voit rien). Ils
  restent de profil, et la lumière vient d'en haut (dessus clairs `_clair()`, bas de caisse à l'ombre, passages
  de roue `_passage()`) : elle reste juste quand le véhicule roule vers la gauche, en miroir — une lumière de
  gauche ou une vue de trois quarts ne le seraient pas. Du monde derrière les vitres (`_tete()` : conducteurs,
  boulanger en toque, passagers du bus). Planche : `reference/v2/vehicules_v2.png`.
  Titine et ses wagons : même lumière (chaudière, cabine, roues, conteneurs).
  **Le papa d'Alice et sa voiture** (été ; 12 novembre 2026) : dessinés d'après ce que Christophe a donné, un
  dessin de lui et une photo de sa voiture — à relever de près, pas à interpréter. Le papa (`npcs._papa()`,
  genre `papa` de `npcs.KINDS` : sprites `papa/idle|talk|wave|cheer`, portrait `hud/portrait_papa`, `WHO.papa`,
  texte `noms.papa`) : cheveux ras très bruns aux tempes plus claires, sourcils épais, bouc le long de la
  mâchoire, tee-shirt rouge « 3.14 » à manches courtes, jean (son choix sur
  `reference/v2/papa_voiture_options.png` ; `tenue="bermuda"` et `lunettes=True` existent pour la plage).
  Manches courtes : une palette qui a la clé `bras` (la couleur du bras nu) fait s'arrêter la manche avant le
  coude dans `npcs._arm()`. La voiture (`vehicles.sport()`, véhicules `sport` — le papa au volant, Alice et
  Tecky à l'arrière, `_passager()` — et `sport_vide`, garée) : une berline sportive rouge à hayon, **sans marque
  ni logo**, dont le profil est relevé sur la photo (`_PX`, `_PY` convertissent ses pixels ; `_lisse()` : un
  contour lisse qui passe entre les points), étirée de `SPORT_K` (1,15) en hauteur — « un peu rehaussée », son
  choix, pour qu'on voie les passagers ; grandes roues à étrier rouge (`_roue_sport()`), agrandie comme les
  autres (`ECH`), `VEHICLE.sport` dans game.js. Ni l'un ni l'autre n'est encore placé sur une carte : ils
  serviront à la cinématique du départ (essai dans le jeu : `reference/v2/lot6_papa_voiture.png`).
  **Ombres** : la ligne de contact (`Sprite.sol`) passe un peu au-dessus du bas des murs (`CONTACT`), pour que
  l'ombre parte de dessous le contour : posée juste sous le mur, elle laissait un liseré clair entre le bâtiment
  et son ombre. Christophe tient aux ombres détaillées (les jours entre les pieds du poulailler, sous le store
  d'un étal) : ne pas les boucher.
  `butterflies.py` (papillons, vus de dessus), `lisiere.py` (le bord de la carte : `decor()`, le placement de la
  lisière, et `tunnel()`, le tunnel de la route, un `nature.Sprite` en calques : butte, pierres, touffes ;
  `tunnel(est=True)` = le même, éclairé de la droite, que le jeu pose en miroir au bord est : la lumière vient
  toujours d'en haut à gauche ; `_portail()` : un arc de pierres sur deux socles, choisi par Christophe sur
  `reference/v2/tunnel_options.png` ; la butte est entaillée à la place de la bouche, et une ombre en dégradé y
  couvre la vraie route et la voiture qui entre — elle s'enfonce dans le noir au lieu d'être coupée net ; ne pas
  remettre de bande de pierre en travers de l'ouverture : les voitures passaient dessous, « visuellement
  incohérent »), `items.py`, `decor.py`, `tiles.py`, `hud.py` :
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
  **Bords froissés** (`_froisse()`, `TREMBLE`, `NATURELS`) : les bords naturels (chemins de terre, rives, sous-bois,
  champ ; pas la voirie ni l'eau le long d'un quai) ne sont plus tirés à la règle : le champ des coins est ondulé,
  l'ondulation nulle et à plat sur les quatre bords de la tuile pour que les contours se raccordent toujours.
  `FROISSES` (3) froissements du même bord : la tuile de base et deux variantes (`ALTERNEES`, `ALT_ROW`, rangées
  ajoutées avant `COMPOSITE_BASE`). La carte ne connaît que la tuile de base ; le jeu tire la variante de la
  position en peignant le sol (`tileLook()`, `MAP.tileAlt` ; `pack_web.preview()` fait de même) : la même
  ondulation répétée à chaque tuile faisait une dentelle le long de la rivière. `waterVal()` n'est pas froissé
  (l'écart, 3 px, est sous la marge `WATER_EDGE`).
  **Eau** (`_shore()`, `SHORE`, `BANKS`) : sur la rive de terre, lèvre d'herbe, sable, sable mouillé ; dans l'eau,
  hauts-fonds clairs, eau moyenne, puis le fond (la couleur des tuiles pleines) ; ombre de la berge du haut et de
  gauche, écume en tirets le long de celle du bas et de droite (motif périodique : il se raccorde d'une tuile à
  l'autre). Les limites des bandes larges suivent le champ (continu entre tuiles), pas la distance approchée.
  **Côte** (été ; 12 novembre 2026) : cinq terrains de plus (lettres de `carte.LEGENDE`) : `sand` (sable, `a`),
  `planks` (planches et jetée, `l`), et la falaise — `heath` (la lande du plateau, `h`), `chalk` (sa paroi de
  roche, `k`), `stairs` (l'escalier, `e`). Teintes choisies par Christophe sur
  `reference/v2/cote_terrains_options.png` : le sable doré et les planches brunes de A, la mer turquoise de B —
  la mer est le terrain `water` aux couleurs de l'été (`saisons.py`). Sable uni (le jeu l'habillera, comme
  l'herbe), lames de 4 px qui se raccordent. Là où l'eau recouvre le sable, `_shore()` dessine le bord de mer
  (`PLAGE` : sable mouillé, hauts-fonds, écume tout le long, une vague plus loin) au lieu de la berge d'herbe ;
  `RIVES` = où le bord de l'eau est froissé. Deux paires de plus (sable / herbe, eau / sable) ont leur rangée
  et leurs variantes froissées ; les planches et la falaise n'en ont pas : leurs tuiles sont des tuiles
  composées (`needs_composite()`). `_GRAINES` garde l'ordre d'avant pour la graine des tuiles composées (celles
  du monde n'ont pas bougé). **Image du tileset** : `LARGEUR` (32) colonnes, la tuile n° i en (i % 32, i // 32)
  — deux fois moins haute, pour rester sous 4096 px en x4 ; les index, eux, restent « rangée x 16 + coins »
  (`COLS`). `MAP.sheet` dans game.js, `infos.largeur` dans l'éditeur. Étude : `python3 v2/cote_etude.py`
  (`reference/v2/cote_terrains.png`).
  **Falaise, façon RPG Maker XP** (12 novembre 2026). Il a fallu six planches pour y arriver : une bande de
  craie peinte comme un terrain (staircases, lèvre d'herbe, ombre au pied) n'allait « pas du tout » ; Christophe
  a fini par donner une carte de RPG Maker en modèle (« il faut s'inspirer des tilesets de RPG Maker XP »), puis
  a réglé le détail : bords arrondis, paroi « plus naturelle et irrégulière » (les pans réguliers puis les blocs
  façon pavage ont été refusés), pas de touffes d'herbe au bord (« moches ») mais un liséré de pierres, et
  l'herbe du plateau « jaunie façon bruyère », caillouteuse. Maquette validée : `reference/v2/falaise_rpg.png` ;
  le moteur : `reference/v2/falaise.png` (`python3 v2/falaise_etude.py`). Ne pas revenir à la bande de craie.
  Le principe (`tiles.BLOC`) : **le plateau est un bloc surélevé**. On peint la lande (`heath`) là où est le
  plateau, la paroi (`chalk`) sous ses bords du bas — sa hauteur est le nombre de rangées de coins, deux
  d'ordinaire —, et l'escalier (`stairs`) en colonnes de coins du bord du plateau jusqu'au pied (deux colonnes :
  avec une seule, ses bouts sont des demi-ronds ; il commence dans la dernière rangée de lande, pour entailler
  le liséré). `PRIORITY` les empile paroi, lande, escalier : la paroi prend la forme du bloc entier, la lande
  se pose dessus. `_layer()` : la paroi s'assombrit vers son pied (`FALAISE["pied"]`) ; la lande reçoit son
  liséré de petites pierres (`_pierres()`, d'après ses seuls coins, `propres`) ; le premier terrain du bloc posé
  dans la tuile en dessine l'ombre sur le sol d'en bas, le long des bords du bas et de droite (`_ombre_bloc()`,
  `bloc`). Pas de froissement, mais les **bords debout ondulent** (Christophe : « rendre moins droite et rigide
  la bordure verticale ») : `_ondule()`, `ONDES`, `ONDULES` — une ondulation du champ qui ne dépend que de la
  hauteur dans la tuile, nulle et à plat en haut et en bas (les contours se raccordent), appliquée seulement
  près du contour et là où le bord est debout (un bord couché ondulé se dédoublait ; loin du contour, la
  distance approchée s'affolait : ombres en barbes) ; la variante se tire de la place de la tuile. Les collisions
  ne la connaissent pas (quelques pixels). **Texture suivie** (`SUIVIES`, `PHASES`, `phase()`) : la paroi (de grandes
  masses de roche fendues, `_dessin_roche()`, cellules de Voronoï `_cellules()`) est découpée dans une grande
  image qui ne se répète que toutes les 24 x 4 tuiles (plus large qu'un écran : à 6 x 4, la répétition se
  voyait) : une tuile qui en contient est toujours composée, et sa clé porte sa
  place — `COMPOSITES` contient des tuples de 4 coins, ou de 4 coins et de la place (px, py) ; `composite()`
  accepte les deux ; l'éditeur fait de même (`sol.js`, `/tuile?c=…,px,py`, `infos.suivies` / `phases`). Sans
  cela, la même roche se répétait à chaque tuile. **La lande** (herbe de la saison jaunie de moitié par
  `LANDE`) est une tuile unie : c'est le jeu qui y sème ses cailloux, une fois dans le sol et d'après la
  position, comme l'habillage de l'herbe (`heathDetails()`, `HEATH`, `heathTile()` : la lande pleine, sans
  escalier ; sprites `sol/caillou` de `nature.sol_cailloux()`, `MAP.pebbles` = `nature.CAILLOUX` : gros, moyens,
  graviers ; par petits groupes, jamais sur le liséré du bord). Dessinés dans la texture, ils revenaient
  toutes les six tuiles — un raccourci corrigé le 13 novembre 2026.
  **Collisions** (game.js) : `MAP.cliff` (coins de paroi) → `cliffAt()` : on ne marche pas sur la roche ;
  `MAP.plateau` (coins de lande et d'escalier) et `MAP.stairs` → `rimAt()` (`RIM`) : le bord du plateau est une
  bande infranchissable autour de la ligne où le champ passe à 0,5, ouverte là où il y a de l'escalier ;
  `cornerVal()` = l'interpolation commune à l'eau, à la paroi et au plateau. Tous trois sont vides sur une
  carte sans falaise. **Planches et falaise ne se touchent jamais** (Christophe : « il ne faut pas de liaison
  possible entre les planches (horizontal) et les falaises (vertical) ») : `carte.INCOMPATIBLES` (planches /
  paroi, planches / plateau), `valider()` refuse toute tuile qui a un coin de l'un et un coin de l'autre —
  l'éditeur aussi, à l'enregistrement. La carte de la côte éprouve tout cela (`tests/cartes.js` : Tecky monte
  les deux escaliers, le bord du plateau l'arrête). Pas encore fait : l'habillage du sable par le jeu, la nage,
  les vagues animées.
  **La carte de la côte** (`cartes/plage.json`, 96 x 64, carte annexe de l'été ; 13 novembre 2026), d'après le
  plan `reference/v2/ete_plan.png` (une tuile pour 20 px du plan) ; aperçu de la carte entière :
  `reference/v2/cote_carte.png`. La route sort du tunnel de l'ouest et **finit au parking** (x 24..36, y 4..13) ;
  la rivière descend du nord à la mer (x 39..45), franchie par **un pont en travers** (décor `bridge_h`, voir
  plus bas) ; à l'ouest le port (béton, x 2..13, y 24..50, quai sur la mer) et le village de pêcheurs autour de
  son bassin (pavés ; maisons `house_fisher`, cabanes `hut_fisher`, poissonnerie `stall_fish`) ; à l'est la ville
  (dalles : la place du casino en haut, les jardins au milieu, les maisons du front de mer en bas) ; au
  nord-est la campagne normande (pommiers, vaches) ; à l'est le plateau des falaises (deux escaliers : côté
  ville en x 77..78, côté plage en x 83..84 ; le phare ira en 90,5 ; 31,5) ; en bas les planches (une bande de
  trois rangées de coins qui suit la baie, de part et d'autre de la rivière), la plage, la jetée (x 48..49) et
  la mer. Zones (chacune son id, son ambiance `AMB_EVENTS` et son morceau) : le port (`port`), le village
  de pêcheurs (`pecheurs`, le morceau du port), la ville (`ville`), les falaises (`falaises`), la plage
  (`plage`), la campagne normande (`bocage`, le morceau de la ferme : violon et banjo, sans ses poules ni son
  coq) et « La Côte Fleurie » pour le reste (`cote`). **Musique et ambiance de la côte** (13 novembre 2026 ;
  au début elle empruntait celles du printemps) : cinq morceaux dans `music.py` — `cote` (l'air des vacances,
  si bémol, ukulélé en contretemps), `port` (chant de marins en ré mineur, 12/8, accordéon), `ville` (valse
  musette en sol), `falaises` (un air du large en ré, lent, flûte et bourdon, de l'écho), `plage` (calypso en
  do, tambour d'acier, claves) —, le motif de Tecky dans chacun ; bruitages `gull` (mouettes, chacune sa
  voix), `rigging` (les drisses qui tintent au port), `gust` (rafales sur la falaise) ; le **ressac**, son
  continu `surf` (`Ambience.salt` : la part de mer sur trois cercles autour de Tecky, `AMB.surfR` ;
  `surfSwell()` : il enfle et retombe comme une vague). `seaAt()` : la mer ; le clapotis (`Ambience.wet`) et
  les grenouilles ne comptent plus que l'eau douce. Les sons continus sont construits par `ambLoop()`
  (`AMB_LOOPS`), dans la section des bruitages : la salle d'écoute les fait entendre (« Les sons continus »).
  Pendant le voyage, la musique de la côte commence quand la voiture sort du tunnel (`tripCoast()`).
  Test : `cote_sons.js`. Elle n'a pour l'instant que des décors déjà dessinés, des objets, des os
  dorés, sept chiens, des canards, des vaches, des petites bêtes et des papillons : **pas encore** de voitures
  garées, aucun personnage, ni indices ni Alice.
  **Route sans issue** (13 novembre 2026) : `traffic.fin` (un x entier, 30 sur la côte) dit où la route
  s'arrête. `pack_web.py` en déduit le décor `porche` (`lisiere.porche()` : un parking couvert vu d'en haut,
  son « P », et la bouche du tunnel en miroir, tournée vers la route ; `lisiere.PORCHE` ; sprite
  `decor/porche` ; obstacle `FOOT.porche` ; l'éditeur le montre, `ED.deduits`) et `MAP.traffic.end` (null
  quand la route traverse la carte). `game.js` : `turnBack(v, dt)` — un véhicule qui s'enfonce sous le porche
  (`TRAFFIC.porch`), ou qui sort par le tunnel, fait demi-tour hors de vue : il change de voie, attend
  (`v.hidden`, `TRAFFIC.park` / `away`), puis repart dès que la voie est libre devant sa sortie ; les autres
  ne gardent pas leurs distances avec un véhicule caché. Le porche couvre 4,7 tuiles : pas de bus sur une
  route sans issue (il dépasserait). Sur la côte : trois voitures, un passage piéton devant le chemin du
  port. Test : `cartes.js`.
  **Le voyage en voiture** (13 novembre 2026 ; `game.js`, section « le voyage en voiture ») : un épisode
  qui a un champ `voyage` dans `episodes.json` (l'été : `"voyage": "plage"`) commence par une cinématique et
  se joue sur cette carte-là. `newGame()` → `startTrip()` : `state === 'trip'`, `trip` (étape `step`, la
  voiture `car`, le papa `papa`, `aboard`, le noir `a` / `fade` / `then`), `TRIP` (durées, vitesses, places à
  partir de l'arrière de la voiture). Étapes de `updateTrip()` : `descente` (Alice et Tecky descendent le
  chemin de la niche jusqu'à la voiture garée sur la voie du bas, `tripWalk()`), les répliques du départ
  (`tripDepartLines()`), `embarque` (Alice puis Tecky disparaissent à la portière), `installe` (le papa fait le
  tour jusqu'à sa portière — sprite `papa/walk`, pose `step` de `npcs.P` —, monte, la voiture passe de
  `sport_vide` à `sport`), `route` (**la caméra suit la voiture d'un bout à l'autre de la grande route**,
  `TRIP.cruise`, jusqu'au tunnel où elle s'enfonce : Christophe n'a pas voulu du fondu au milieu de la route),
  le noir (`tripCoast` : `useMap(voyage)`, la voiture sort du tunnel),
  `arrivee` (la caméra la suit jusqu'au porche), `garee`, le noir (`tripParking`), les répliques de
  l'arrivée (`tripArrivalLines()` : Alice propose le cache-cache), `cache` (elle file), puis `tripDone()` :
  Tecky a la main en `MAP.start` de la carte du voyage (le parking), la partie est enregistrée. Un bouton
  passe la scène après `TRIP.skip` s ; « Recommencer » va droit au parking. Pendant la scène, le monde est
  figé, le HUD caché (les dialogues restent), Tecky n'est pas dessiné quand il est à bord. Le papa, lui, vit pendant
  toute la scène, répliques comprises (`tripPapa()` : il parle à son tour, salue Alice qui file ; figé, Christophe
  l'a tout de suite vu) ; `tripDone()` le laisse muet tant que Tecky ne s'est pas éloigné (il demandait « tu l'as
  trouvée ? » alors qu'Alice venait de partir : cette phrase est sa dernière, pas sa première). Avec un voyage :
  `passageHere()` rend toujours null (à pied, les tunnels sont « pour les voitures » — les passages de la
  carte ne servent qu'à dire où mène le tunnel) ; `loadGame()` ramène au point de départ de la carte du
  voyage une partie enregistrée ailleurs (pendant la scène, par exemple) ; `reset()` et `toTitle()` vident
  `trip`. Données : `start` de `cartes/plage.json` (le parking), et le point libre `papa`
  (`carte.POINTS_LIBRES` : jamais exigé) — le papa d'Alice y attend et **salue comme un villageois**
  (il n'est pas dessiné tant que la voiture roule vers le porche, étapes `arrivee` et `garee` : il est au
  volant ; `newVillager(['papa', …])` dans `resetWorld()`, `VILLAGER_LINES.papa`, textes `villageois.papa.<i>`,
  `MAP.villagerFps.papa`). Textes : `voyage.<qui>.depart` / `.arrivee`. `tools/export_voix.js` produit ces
  répliques (voix « Papa »). `tests/voyage.js` ; `cartes.js` et `episodes.js` retirent le voyage de
  l'épisode (`delete EPISODES[1].voyage`) pour éprouver les passages à pied et les surcharges, qui restent
  dans le moteur.
  **Indices, cachette et fin par épisode** (13 novembre 2026) : `episodes.json` → `indices` (trois objets de
  `items.py`, dans l'ordre ; sans ce champ, ceux du printemps). L'été : `hat` (le chapeau de paille, au
  village de pêcheurs), `spade` (la pelle, dans les jardins de la ville), `flipflop` (la tong, sur la plage),
  dessinés dans `items.py` (`CLUES_ETE`) ; Alice est cachée **tout en haut des falaises**, au nord du plateau
  (`alice` de `cartes/plage.json`, entre un rocher et un buisson) — pas au phare : Christophe l'a voulue « plus
  haut dans les falaises, puisque la cinématique la fait redescendre vers le phare ».
  `episodes.py` vérifie que la carte où l'épisode se joue a exactement un de chaque indice, et Alice.
  `game.js` : `clueNames()` (ceux de l'épisode ; `CLUES` reste la liste du printemps), `CLUE_ICON` (l'image de
  `hud/arrow_icon` : 0 à 2 le printemps, 3 la tête d'Alice, 4 à 6 l'été — `hud.arrow_icons()` les ajoute à la
  fin), `CLUE_TXT[épisode]` (les textes : `indices_ete.trouve.<i>` / `.ensuite.<i>`, `retrouvailles_ete.<i>` ;
  le premier épisode garde `indices.…` et `retrouvailles.…` ; chaque `txt()` a son début de clé écrit en
  toutes lettres, pour `tests/textes.js`), `clueFound()`, `clueNext()`, `reunionLine()`. Alice a ses deux
  chaussures hors du printemps (`resetWorld()`). **Scène de fin** : `ending.from` d'une carte (facultatif :
  d'où Alice et Tecky arrivent, à partir de leur place ; sans cela, d'en bas de l'écran, comme au printemps),
  `ENDING.start`, `endingWalk()` (un pas tout droit vers sa place). Sur la côte, ils arrivent par le haut du
  plateau (depuis la cachette) au pied du phare, la nuit tombe et la lanterne s'allume avec les fenêtres. Voix : les cas de l'été
  sont produits par `tools/export_voix.js` (`DYNAMIC_SITES` = 23). Tests : `voyage.js` joue l'été du départ à
  la victoire. Pas encore fait : (la tenue d'été d'Alice et sa tong perdue sont faites : voir les finitions de l'été).
  **Quêtes rejouées avec d'autres acteurs : les rôles** (13 novembre 2026). Chaque quête de la côte reprend une
  mécanique du printemps ; plutôt que de la recopier, la carte **distribue le rôle** à d'autres acteurs :
  `"roles": { rôle: acteur }` dans la carte (`carte.ROLES` : les acteurs permis ; `MAP.roles`, vide ailleurs).
  Un personnage a son rôle (`n.kind` : sa quête, `NPC_DO`, `npcList()`, sa place `MAP.<rôle>`) et celui qui le
  tient (`n.look` : dessins, portrait `WHO`, voix `VOICE`, celui qui parle dans les dialogues et les bulles) ;
  `newNpc(kind, place, pitch, look)`. Première quête : **le caniche de Madame Hortense** = la quête de Pompon
  (`rose`, `pompon`, `CAT`, `talkNeighbor()`… inchangés) avec `"neighbor": "hortense"` et `"pompon": "poodle"` :
  Madame Hortense (`npcs._neighbor(p, "hortense")` : le modèle de Mamie Rose en plus grande, capeline, veste
  turquoise, collier ; portrait `hud/portrait_hortense`) attend devant le casino, en zone calme ; Praline
  (`critters` « poodle », une espèce à part avec ses poses : `_poodle_stand()`, `_poodle_sit()`,
  `_poodle_walk()`, `_poodle_run()`, `_poodle_yap()` — haute sur pattes, crinière, pompons aux chevilles, à la
  hanche et au bout de la queue, houppette à nœud rose ; elle jappe quand Tecky aboie ; icône `icone/poodle`) est dans les jardins. Textes : mêmes clés sous `hortense` que sous `neighbor`
  (`nbTxt(k)`), sous `caniche` que sous `chat` (`petTxt(k)`), `tecky.praline` ; `petWho()`, `petCry()`. Le
  badge « Ami des chats » reste celui de Pompon, Praline a le sien (« Ami des caniches », `caniche`) ; la complétion ne compte que les quêtes de la carte où l'on
  joue (`questsHere()`, `QUEST_GIVER`). Sauvegarde : les champs de la quête de Pompon (`rose`, `cat`). Voix :
  `tools/export_voix.js` joue les deux distributions (`DYNAMIC_SITES` = 24). Test : `hortense.js`. Pour la
  quête suivante : ajouter ses acteurs à `carte.ROLES`, leurs dessins, leurs textes sous les mêmes clés, et
  un `xxTxt()` comme `nbTxt()`.
  Deuxième quête : **les moutons d'Anatole** = la quête des poules (`farm`, `hens`, `pen`, `penGate`,
  `talkFarmer()`… inchangés) avec `"farmer": "anatole"` et des moutons dans la liste `hens` de la carte
  (genre `sheep`). Anatole, le gardien du phare (`npcs._postman(p, "anatole")` : le modèle du facteur sans
  sacoche ni cravate, ciré jaune, casquette de marin, moustache blanche), est près de son enclos, en haut du
  plateau, en zone calme ; cinq moutons (`moutons.py` : cadre 48 x 40, pieds en (24, 36), les animations des
  poules aux mêmes noms — `peck` = il broute, `flap` = il détale ; sprites `sheep/<anim>/right`, famille à
  ombre) sont éparpillés sur la lande, un sixième est dans l'enclos. Textes : mêmes clés sous `anatole` que
  sous `farmer` (`fmTxt(k, params)`), sous `moutons` que sous `poules` (`flockTxt(k)`) ; `flockKey()` (le
  sprite du compteur et de la carte de la pause), `henCry()` (ils bêlent : `SFX.baa`, une voix nasillarde qui chevrote ; d'abord c'était le meuglement des vaches joué aigu, clochette comprise — un raccourci que Christophe a relevé). Le badge des
  poules reste celui de Gaston, les moutons ont le leur (« Berger des falaises », `moutons`). `MAP.farmRoadY` n'est une limite que si l'enclos est au nord de la grande
  route (sinon 10^7 : sur la côte, les moutons ne sont pas retenus à la hauteur de la route). Voix :
  Test : `anatole.js`.
  Troisième quête : **les coquillages de Zoé** = la quête des lettres (`post`, `letters`, `talkPostman()`…
  inchangés) avec `"postman": "zoe"`. Zoé (`npcs._zoe()` : une enfant, réduite par `npcs.SCALE`, maillot corail
  à pois, couettes blondes, sa pelle à la main ; palette `sans_manche` : bras nus dans `npcs._arm()`) bâtit son
  château de sable sur la plage de l'ouest (décor `sandcastle`, `mobilier.chateau_de_sable()`), en zone calme.
  Ses cinq coquillages (`plage.py` : Saint-Jacques, bulot, coque, moule, bigorneau, sprite `item/shell`, une
  image chacun ; `MAP.shellBase`) sont **enfouis** : la liste `letters` de la carte donne leurs places, et
  `shells()` (= la carte a ce rôle) en fait des coquillages (`l.shell`, `l.dug`). Une butte de sable d'où
  dépasse un bout de coquille (`butte/coquillage`, image 0 — en mode facile seulement, sinon la butte nue, image 2 ; image 1 : le creux qui reste) signale chacun ; un
  coquillage enfoui ne se ramasse pas en passant : `nearDig()` le rend comme un trésor, Tecky gratte (gerbe de
  sable `fx/sand` — aussi pour un os doré enterré dans le sable, `sandAt()`, `MAP.sand`), il saute du sable
  (`uncoverShell()`, `POST.wait` / `jump`) puis se ramasse (`SFX.shell`). La quête finie, le château prend son
  second dessin, paré des coquillages (`dressCastle()` : `chateau_de_sable_fini`, même silhouette ; jamais
  tiré de la position). Textes : mêmes clés sous `zoe` que sous `postman` (`pmTxt()`), sous `coquillages` que
  sous `lettres` (`lostTxt()`). Badge « Chercheur de coquillages » (`coquillages`). Sauvegarde : la chaîne
  `letters` (0 enfoui, 2 sorti du sable, 1 ramassé). `check_placement.js` : un coquillage enfoui a la portée
  d'un grattage. Test : `zoe.js`.
  Quatrième quête : **les jouets de plage de Théo** = la quête d'Iris (`jouets`, `toys`, `talkIris()`… inchangés)
  avec `"iris": "theo"`. Théo, le maître-nageur (`npcs._theo()` : bronzé, mèches blondes, lunettes de soleil
  relevées, débardeur à croix rouge, short de bain, sifflet ; il parle, il ne jappe pas : pas de `woof`), est sur
  la plage de l'est, en zone calme. Trois jouets (`plage.beach_toy_frames()` : ballon, bouée, voilier) flottent
  dans la zone de baignade (`seaToys()` ; sprite `mer/jouet` à flot, `plage/jouet` posé sur le sable — la famille
  « plage » a une ombre portée ; `MAP.beachToyBase`) : Tecky nage dessus, les rapporte un par un ; lâché en
  nageant (il aboie), le jouet flotte là. Ensuite Théo donne un conseil de plage à chaque visite (`THEO_TIPS`).
  Textes : mêmes clés sous `theo` que sous `iris` (`irTxt()`). Badge « Chien sauveteur » (`nageur`). Test :
  `theo.js`.
  Cinquième quête : **les bouées d'Yvon** = la quête de Léon (`fete`, `balls`, `goal`, `talkLeon()`… inchangés)
  avec `"leon": "yvon"`. Yvon, le pêcheur (`npcs._yvon()` : bonnet rouge, barbe grise, pull marin, cotte de ciré
  jaune), est sur la plage de l'ouest, en zone calme. Ses cinq bouées de casier (`plage.casier_frames()`, sprite
  `mer/casier`) flottent dans la zone de baignade (`floats()`) : Tecky les pousse à la nage ou en aboyant
  jusqu'au **parc à bouées** planté dans l'eau (`decor.buoy_pen()`, décor `buoy_pen` déduit de `goal` à la place
  du filet quand la carte a ce rôle ; mêmes mesures : `RAILS.buoy_pen`, `GOAL_IN`). Sur l'eau une bouée ne saute
  pas, glisse moins loin (`FLOAT`), penche quand elle file et ne quitte jamais la zone de baignade
  (`ballBlocked()` : `swimAt()`). Textes : mêmes clés sous `yvon` que sous `leon` (`lnTxt()`), sous `bouees` que
  sous `ballons` (`ballTxt()`). Badge « Mousse » (`bouees`). `check_placement.js` : jouets, bouées et parc
  dans la zone de baignade. Test : `yvon.js`. Captures :
  `reference/v2/lot6_quete_theo.png`, `lot6_quete_yvon.png` ; planche : `cote_theo_yvon.png`.
  Sixième quête : **les mouettes voleuses de Suzanne** = la quête de Maman Piquette (`piq`, `babies`,
  `talkPiquette()`… ; état et sauvegarde inchangés, mécanique nouvelle) avec `"piquette": "suzanne"`. Suzanne, la
  poissonnière (`npcs._suzanne()` : chignon roux, fichu rouge à pois, anneaux d'or, marinière aux manches
  retroussées, tablier ciré vert, bottes jaunes ; les poings sur les hanches), est à côté de son étal
  (`stall_fish`), au village de pêcheurs, en zone calme. Trois mouettes rieuses (`mouettes.py` : cadre 32 x 32,
  pattes en (16, 28), réduites de `SCALE` ; animations idle, walk, taunt, cry, fly ; sprites `gull/<anim>`,
  famille à ombre ; `bec(anim)` → `MAP.gullBeak` : le bout du bec à chaque image) lui ont chipé trois poissons
  (`mouettes.poisson_frames()` : maquereau, rouget, dorade ; sprite `plage/poisson`, `MAP.fishBase`). Sur une
  carte qui a ce rôle (`gulls()`), chaque entrée de `babies` est **un poisson** (`b.mode` : `held` au bec,
  `fall`, `ground`, `carried` dans la gueule de Tecky, `home` rendu — `babiesLeft()` marche donc tel quel) **et
  sa mouette** (`b.g`, mode `perch`, `hop`, `away`, `gone`) : `newGull()`, `updateGull()`, `gullList()` (ce
  qu'elle ajoute à la liste triée de `drawWorld()` ; une mouette en vol passe par-dessus tout). La mouette fait
  quelques pas quand Tecky est loin, le nargue quand il est dans les parages (`gullLaugh()`, « Kia-ha-ha ! »,
  `SFX.laugh`) et s'envole plus loin dès qu'il approche (`GULL.shy` ; `gullSpot()` : un sol libre où Tecky peut
  aller à pied — `gullOpen()`, d'après `fieldTo()` depuis sa place —, loin de lui, à moins de `GULL.roam` de sa
  place) ; **un aboiement dans le cône lui fait lâcher son poisson** (`scareGull()`, « Kiaaa ! », `SFX.squawk` ;
  en vol au-dessus d'un toit ou de l'eau, il tombe là où elle allait se poser ; `SFX.flop`), elle file et
  disparaît. Tecky prend le poisson en passant dessus (un seul objet dans la gueule : `fishCarried()`, ni deux
  poissons ni un poisson et un jouet de Théo), le lâche s'il aboie, mord ou est KO (`dropToy()` appelle
  `dropFish()`), le rend près de Suzanne (`fishHome()`). Tout marche avant de lui avoir parlé. Textes : mêmes
  clés sous `suzanne` que sous `piquette` (`pqTxt()` ; une réplique de plus, `demande.3`), `mouette.rire` /
  `.cri`, `suzanne.poisson.<i>`, `tecky.poisson`. Badge « Chasse-mouettes » (`mouettes`). Sauvegarde : la liste
  `babies` (`gullState()` : un poisson au bec est à la place de sa mouette, un poisson porté est par terre aux
  pieds de Tecky ; `gullRestore()`). `check_placement.js` : la place de chaque mouette est libre et atteignable.
  Test : `suzanne.js`. Planche : `reference/v2/mouettes.png` ; dans le jeu : `reference/v2/lot6_quete_suzanne.png`.
  **Voix** : `DYNAMIC_SITES` = 23, `DYNAMIC_POPS` = 31 — toute bulle dont le texte passe par un `xxTxt()` de
  rôle compte comme calculée et doit être jouée par `tools/export_voix.js` dans ses deux distributions (avant,
  elles laissaient dans la liste des lignes parasites : « tous », « salut »… et « But ! » n'y était pas).
  **Éditeur de carte** : `carte.ACTEURS` (acteur → image et nom de ce qu'il tient ; `infos.acteurs`,
  `ED.acteur()`, `ED.nom()`) : sur la côte, l'éditeur montre Anatole, Zoé, les coquillages, les mouettes… et
  plus Gaston, Marcel, les lettres, les hérissons. Un nouvel acteur : l'y ajouter.
  **Les adversaires de la côte : crabes et goélands** (13 novembre 2026 ; `game.js`, section « les crabes et les
  goélands »), en plus des chiens. Deux listes de points de la carte, facultatives (`carte.LISTES_LIBRES` : le
  monde n'en a pas), retenues par leur rang dans la sauvegarde : `crabs`, `seagulls` (`MAP.crabs`,
  `MAP.seagulls`). Comme pour les chiens, rien ne fait mal en balade, en zone calme ni pendant le répit d'un
  dialogue (`hurtPlayer(…, false)` : ce ne sont pas des morsures). **Crabes** (`crabes.py` : de face, cadre
  32 x 32, pattes en (16, 26), réduits de `SCALE` ; animations idle, walk, menace, pinch, wave, bury, unbury,
  buried ; sprites `crab/<anim>`, `MAP.crabAnims` = [cadence, en boucle, images]) : sur le sable, ils vont et
  viennent de côté autour de leur place (`CRAB.range`) ; Tecky à moins de `CRAB.near` : pinces levées, « Clac
  clac ! » (`SFX.clack`) ; il leur marche dessus (`CRAB.pinch`) : ils pincent (`SFX.pinch`, un demi-os) ; un
  aboiement dans le cône, ou une morsure : `buryCrab()`, ils s'enterrent (`SFX.burrow` ; une butte d'où
  dépassent leurs yeux), ne pincent plus, et ressortent quand Tecky s'est éloigné (`CRAB.peek`) ; des points la
  première fois (`scored`). En balade, ils saluent d'une pince. **Goélands** (`goelands.py` : de profil, cadre
  48 x 40, pattes en (24, 36) ; animations glide, flap, cry, dive, idle ; sprites `seagull/<anim>`,
  `MAP.seagullFps` ; il reprend les outils de `mouettes.py`, pas ses poses) : ils tournent dans le ciel autour
  de leur place (`soar`, `SEAGULL.orbit`, `alt`) ; leur ombre est **à l'aplomb** (`drawSeagullShadow()`, pas
  couchée par le soleil : elle dit où ils sont). Tecky entre dans leur domaine (`SEAGULL.see`, hors zone calme,
  pas à la nage) : « Kiaaak ! » (`SFX.keow`), ils viennent au-dessus de lui (`warn`), puis piquent sur
  l'endroit où il était (`dive`, `SFX.swoop`, une cible rouge au sol) : il suffit de bouger. Un aboiement vers
  leur ombre (`scareSeagull()`, portée `SEAGULL.bark`) les fait repartir pour `SEAGULL.gone` s ; des points la
  première fois qu'on en repousse un qui attaquait. En mode facile, ils préviennent et piquent plus lentement
  (`warnEasy`, `diveEasy`). En balade, ils sont posés (`perch`), s'envolent si Tecky approche et reviennent
  (`land`). La première rencontre de chacun : Tecky explique (`crabSeen`, `seagullSeen`, sauvegardés ; textes
  `tecky.crabe`, `tecky.goeland`). `check_placement.js` : un crabe sur le sable, ni crabe ni goéland en zone
  calme. Éditeur : « Crabe », « Goéland » (calque des chiens, outil Poser). Test : `adversaires.js`. Planches :
  `reference/v2/crabes.png`, `goelands.png` ; dans le jeu : `reference/v2/lot6_adversaires.png`.
  **Les finitions de l'été** (13 novembre 2026 ; choix de Christophe sur `reference/v2/ete_options_alice.png` et
  `ete_options_plage.png`, dessinées par `python3 v2/ete_options.py alice|plage`). **Tenue d'Alice** :
  `alice2.TENUES` (une tenue = `ETE`, tongs et rayures, et les couleurs de `PAL` qui changent ; `_vetue()`,
  `frames(…, tenue=)`, `portrait(…, tenue=)`) ; l'été : marinière, jupe rouge, tongs bleues, sans socquettes.
  Sprites `alice_ete/*` et `alice_ete1/*` (une tong perdue), portrait `hud/portrait_alice_ete` ; `game.js` :
  `aliceKind(nu)` (la famille de la saison ; `nu` : il lui manque une chaussure ou une tong) et
  `WHO.alice.portrait` suivent `EP().saison` ; elle a ses deux tongs au départ du voyage, une seule dès
  qu'elle est cachée, les deux à la scène de fin. La tong-indice (`items.flipflop`) est bleue comme les
  siennes ; la passagère de la voiture porte la marinière. **Chaise haute** de Théo : `mobilier.chaise_haute()`,
  décor `lifeguard_chair`. **Deux-roues** (`vehicles.scooter()`, `moto()`, `_pilote()`, `MOTO_COLORS`) :
  véhicules `scooter_<couleur>`, `moto_<couleur>` de la route (`VEHICLE.scooter`, son klaxon `SFX.meep` par
  `T.horn` ; `VEHICLE.moto`). **Véhicules garés** : des décors (`parked_car`, `parked_scooter`,
  `parked_moto` ; `mobilier._gare()` : le dessin de `vehicles.py` sans personne, la couleur tirée de la
  position), donc obstacle `FOOT`, ombre portée et éditeur sans rien de plus. **Sable** : `nature.sol_sable()`
  (`SABLE`, sprite `sol/sable`), semé une fois dans le sol par `sandDetails()` (`SAND`, `sandTile()` : le
  sable plein). **Cultures d'été** : `nature.sol_cultures_ete()` (blé, tournesols, maïs, tomates ; sprite
  `sol/culture_ete`, mêmes cadres), que `fieldDetails()` plante quand `EP().saison` est l'été. **Vagues** :
  `shoreLine()` relève une fois par carte (`shoreDots`, vidé par `useMap()`) les points du bord de mer là où
  la mer touche le sable, et leur normale ; `drawSurf()` trace à chaque image deux lignes d'écume qui montent
  et se retirent (`WAVE`), d'un seul tracé chacune, dans le repère du monde. **Manège** : `batiments.manege()`
  reste le dessin entier (ombre, éditeur) ; `manege(partie)` et `manege_cheval(i)` en donnent les morceaux
  (`MANEGE_PIECES`, sprites `decor/manege_socle|mat|chapiteau|cheval_<i>`) que `drawCarousel()` remonte à
  chaque image, quatre chevaux tournant autour du mât (`CAROUSEL`) ; sa zone `manege` (la première de la
  carte, dans la ville) joue sa valse d'orgue (`music.manege()`, fa majeur, le motif de Tecky). **Chenal** :
  le bassin du village s'ouvre à l'est sur la rivière (coins de mer puis d'eau douce, en langue comme à
  l'embouchure), franchi par le pont de bois du monde (décor `bridge` en 35 ; 34). Test : `ete_finitions.js`.
  Je n'ai vu les vagues et le manège qu'en images fixes ; la valse et le klaxon ne sont jugés que par
  Christophe. **Vaches** : le veau distancé de plus de `COW.calfFar` rattrape sa mère sans attendre, un peu
  plus vite (`calfHurry`) — c'était le test instable de `cows.js`. Premier jet posé par
  `v2/cote_carte.py`, **gelé depuis** : Christophe retouche la carte dans l'éditeur, c'est
  `cartes/plage.json` qui fait foi (le script refuse d'écraser une carte qui existe ; ses listes ne sont plus
  à jour ; `python3 v2/cote_carte.py --apercu` redessine l'aperçu à partir du fichier). Rien ne dépend de
  la place exacte du casino ni du phare (il les a déplacés : le casino en haut de sa place, le phare à la
  pointe du plateau), sauf la zone calme autour du phare, les étiquettes « Casino » et
  « Phare » de la carte de la pause (`landmarks`) et `tests/cartes.js`, qui marche en (87 ; 30) sur le
  plateau, monte les escaliers et longe le bord : à suivre si la carte change. Ce que la côte a demandé au moteur : les marquages de la
  route ne sont posés que sur les tuiles de pleine chaussée (`chaussee()` dans `pack_web.build_map()` et
  `editeur/sol.js`) ; `edgeBump()` ne parle du tunnel que du côté où il y en a un ; la lisière ne pousse ni
  sur le sable, ni sur les planches, ni sur la paroi (`lisiere.LIBRES`).
  **Retours de Christophe sur le premier jet** (13 novembre 2026 : « le tracé général est excellent », mais
  les décors repris du printemps ne sont que des bouche-trous en attendant les dessins de l'été) :
  - **La mer est un terrain à part** (`sea`, lettre `m`) : la rivière « doit avoir une couleur moins prononcée
    que la mer ». La mer garde le turquoise choisi, l'eau douce (`water`) son bleu, été compris (`saisons.py`
    ne change plus l'eau). `tiles.EAUX` = les deux : de l'eau pour les collisions (`MAP.water`), froissées le
    long d'une rive. La paire qui a sa rangée est (mer, sable) — le bord de mer `PLAGE` — à la place de (eau,
    sable) ; la mer pleine, la mer le long d'un quai ou de l'herbe sont des tuiles composées (hauts-fonds de
    `PLAGE`) ; là où la rivière traverse la plage, du sable mouillé. À l'embouchure, la mer se fond sur l'eau
    douce sans rive (voir « Jointures de l'eau »), et la carte y avance l'eau douce en langue dans la mer. L'habillage de l'eau par le jeu (nénuphars, galets, fonds sombres :
    `MAP.shore`) ne concerne que l'eau douce, et ses fonds sombres ne sont pas posés à moins de `POND.sea`
    tuiles de la mer (`MAP.sea`, `seaNear()` : ils faisaient une tache dans l'embouchure). Le bassin du village est de la mer.
  - **Le pont en travers** (`decor.bridge_h()`, décor `bridge_h`) : le pont de bois du monde, dans l'autre
    sens, pour une rivière qui descend du nord au sud ; 224 x 96 (sept tuiles sur trois), tablier de deux
    tuiles, garde-corps au nord et au sud (`RAILS.bridge_h`), à plat (`FLAT`), sans ombre portée. Il se pose
    au milieu d'une tuile (x,5 ; y,5 : `carte.valider()`, contrainte « centre » dans l'éditeur) ; les coins
    sous son tablier ne sont plus de l'eau (`BRIDGES` dans `pack_web.charger_carte()`).
  - **Étals de la côte** (`batiments.etal()`, `STORES`, `PEINTS`) : la poissonnerie (`stall_fish` : store
    bleu, comptoir blanc, bacs de glace pilée, poissons, rougets, moules ; un poisson en enseigne) et le
    marchand de glaces (`stall_ice` : store vert d'eau, comptoir crème, bacs de boules ; un cornet en
    enseigne).
  - **Village de pêcheurs** (`batiments.py`) : `maison_pecheur()` (basse, chaulée, toit d'ardoises, volets et
    porte bleus ou verts, une bouée `_bouee()`), sa variante à pignon aux volets rouges, et
    `cabane_pecheur(couleur)` (planches peintes debout, rives et angles blancs, porte de remise, toit
    goudronné ; rouge, bleue, jaune, verte). Décors `house_fisher` et `hut_fisher` : le modèle se tire de la
    position **en pixels** (`decorLook()` : un dixième de tuile suffit à en changer — c'est ainsi que la carte
    alterne les modèles). Planche : `reference/v2/cote_pecheurs.png`.
  - **Bord de mer** (même jour, après son « c'est parfait, tu peux continuer ») : dans `batiments.py`, le phare
    (`phare()`, décor `lighthouse` : tour blanche à bandes rouges, galerie, lanterne vitrée — ses vitres sont
    des `vitres`, elle s'allume donc le soir avec les fenêtres : c'est le phare de la scène de fin), le casino
    (`casino()`, décor `casino` : façade crème à fenêtres cintrées, avant-corps à fronton dessiné **après** le
    toit, marquise rouge, ampoules), le manège (`manege()`, décor `carousel` : plateau, mât, chevaux de bois
    `_cheval()`, chapiteau à quartiers ; ses ampoules s'allument le soir ; il ne tourne pas encore) et les
    cabines de plage (`cabine_plage(couleur)`, décor `beach_hut` : quatre couleurs tirées de la position) ;
    dans `mobilier.py`, le cargo (`cargo()`, décor `cargo`) qui remplace la péniche au port — « la péniche
    n'a rien à faire dans la mer » — et les bateaux de pêche (`bateau_de_peche(couleur)`, décor
    `fishing_boat`, trois couleurs), sur l'eau comme la péniche (`Sprite.sol = None`, pas de collision) ;
    ils sont **au large** : dans le « minuscule bassin qui n'est même pas relié à la mer », Christophe les
    a trouvés « bizarres » (le bassin n'a que des barques).
    Planche : `reference/v2/cote_bord_de_mer.png`. La barque (`boat`) reste une barque de rivière.
- `music.py` : **source unique** de la musique (v2 : **un morceau par zone**, dans son ton, à son tempo, avec ses
  instruments). `songs()` → `SONGS` du jeu ; `python3 music.py` contrôle les partitions (notes des temps hors de
  l'accord, hors de la gamme, étendue). Niche et écran titre : « Promenade de Tecky », le thème (do, 140 ; 32
  mesures après 2 mesures d'entrée jouées une fois) ; village : polka (sol, 152) ; campagne : trot en 12/8 (fa) ;
  ferme et verger : violon et banjo (la, 132, notes glissées = 6e champ) ; forêt : flûte, harpe, écho (la mineur,
  96) ; parc : valse de boîte à musique (ré, 3/4, sans batterie) ; industrie : mécanique (mi mineur, 138) ;
  `berceuse` de la fin (le thème, lent, à l'octave, sans batterie) ; `win`, `lose` (3 mesures à 140, jouées une
  fois). Le premier motif du thème (mi sol do sol mi – ré mi) revient dans les autres morceaux : le garder.
  Un `Morceau` = des `partie()` : accords (un par mesure, « C,D » = deux), mélodie écrite en texte (`voix()` :
  autant de jetons que de temps dans la mesure, « - » tenue, « . » silence, « / » glissée), deuxième voix `harm`
  (contre-chant écrit, ou `"tierces"` : sous la mélodie, dans l'accord), motifs d'une mesure pour `bass` (« q »
  quinte, « 3 » tierce, « a » note d'approche), `arp`, `drums` (`bat()`), nappe `pad`, `fin` (remplace la fin de
  la dernière mesure : roulement, toms), `crash`. Une reprise se joue arrangée autrement (tierces, batterie plus
  fournie) plutôt qu'à l'identique. Canaux : lead, harm, arp, bass, pad, drums ; instruments `INST`, réglés par
  morceau (onde, volume, tenue, note pincée `pl`, vibrato `vib`, passe-bas `lp`, `echo`) : ils font partie des
  données (`SONGS[k].inst`), game.js n'a plus de `TIMBRE`. `bar` / `beat` : pas par mesure et par temps (12 et
  3 : ternaire ; 12 et 4 : valse) ; `spb` : secondes par pas ; `loop` : où reprendre après le dernier pas (`null` :
  joué une fois) ; `entries` : débuts de partie. Batterie : recettes `DRUMS` de game.js (kick, snare, hat, ohat,
  crash, rim, toms, wood, metal).
  **Salle d'écoute** : `web/musique.html` (écrite par `pack_web.ecoute()`, `web_src/musique.template.html` ; à
  ouvrir depuis le disque, pas publiée) : les morceaux joués par le séquenceur du jeu (sa section « musique
  chiptune », copiée telle quelle), le passage d'une zone à l'autre comme dans le jeu, et « Mesurer les niveaux »
  (rendu hors ligne : crête et niveau moyen par morceau et par canal ; lent, une minute par morceau). Je ne peux
  pas écouter : c'est Christophe qui juge à l'oreille, les niveaux et le contrôle des partitions sont mes seuls
  garde-fous. `key` : le ton du morceau (0 = do ; un ton mineur donne son relatif majeur), pour les bruitages.
- **Bruitages** (v2 ; `game.js`, section « bruitages », avant la musique) : chaque son est une recette de `SOUNDS`,
  des sons superposés faits avec `tone()` (une onde dont la hauteur suit une courbe : `[f0, f1, …]` ; options
  `at`, `a` attaque, `h` tenue, `lp` passe-bas, `vib`, `trem`), `noise()` (un souffle filtré, tampon de bruit
  partagé) et `cry()` (une voix : dents de scie dans des formants `[fréquence, étroitesse, force]`, pour « ouaf »,
  « meuh », « coin », « miaou », « hé-ho » ; voyelles `VOWEL`) ; `chime()` (carillon), `ding()` (cloche). On joue
  par `SFX.nom(p, d'où)` : `p` = hauteur (`T.pitch` d'un chien, `VEHICLE.pitch`, `n.pitch`), `d'où` = ce qui fait
  le bruit (`{ x, y }` du monde) : `sfxPlace()` le sort de son côté de l'écran (`SOUND.pan`) et l'affaiblit avec
  la distance au milieu de l'écran (`SOUND.near` / `far` ; trop loin : rien n'est créé). Sans `d'où` : au centre
  (Tecky, menus). La hauteur change un peu à chaque fois (`SOUND.vary`), sauf les petits airs (`TUNED` : objet
  ramassé, trésor, os, badge, but, menus), écrits en do et joués dans le ton du morceau en cours (`sfxKey()`,
  `SONGS[…].key`). `SFX.nom()` vérifie déjà `AC` et `muted` : ne plus écrire `if (!muted)` devant. **Babil des
  dialogues** (`talkSound()`, `VOICE` : une hauteur par personnage, `SOUND.talk`) : une syllabe `talk` tous les 4
  caractères, des « wouf » `wuf` pour Tecky et Iris, « tic » `blip` pour une information, rien sur un espace ou
  la ponctuation ; à retirer quand les vraies voix (lot 7) arriveront. Menus : `blip` (déplacement), `ok`,
  `back`, `pause`, `erase`. Bêtes et gens qui n'avaient qu'une bulle ont leur son (`meow`, `hiss`, `chitter`,
  `squeak`, `growl`, `alert`, `dash`, `pouic` du poulet et du canard, `paper` des lettres, `tunnel` / `pop`,
  `bump`, `splash`, `puff` de Titine). Un nouveau bruitage : sa recette dans `SOUNDS`, son bouton dans `BRUITS`
  de `web_src/musique.template.html` ; `tests/sfx.js` refuse un `SFX.x` sans recette et une recette jamais jouée.
  **Salle d'écoute** : `web/musique.html` a une partie « Les bruitages » (la section du jeu, copiée telle
  quelle) : chaque son, ses variantes de hauteur, sa place (gauche, droite, au loin), le babil de chaque
  personnage ; « avant » rejoue le bruitage d'avant la v2 (`AVANT`, gardé dans la page seulement) ; « Mesurer les
  bruitages » : crête et niveau moyen du nouveau et de l'ancien. Les niveaux ont été calés sur les anciens (0 à
  + 4 dB, les sons d'ambiance bien plus bas) ; comme pour la musique, je ne peux pas écouter.
- **Objets à ramasser** (`items.py` ; lettres de Marcel `npcs.letter_frames()` ; jouets d'Iris `port.toy_frames()`) :
  ils détonnaient dans le décor de la v2 (à plat, flottants au-dessus d'un ovale). Choix de Christophe sur
  `reference/v2/objets_options.png` : **posés au sol, avec leur ombre portée**, réduits à **50 %** (`POSED.sc` ;
  à 85 % d'abord, il les a trouvés encore trop gros à côté de Tecky : `reference/v2/objets_tailles.png`). Les
  jouets d'Iris sont un poulet en caoutchouc (c'était un canard jaune, trop proche du canard pouic-pouic des
  trésors : choix sur `reference/v2/jouets_iris_options.png`), un anneau et une corde torsadée posée en S
  (`port.poulet()`, `anneau()`, `corde()` ; la corde d'avant, une tige entre deux boules, « ressemblait à un
  piercing », et droite il l'a voulue « plus organique »). Os, saucisse, médaille,
  canard, balle, os doré, les trois indices, la lettre et les jouets d'Iris ont du relief (`items._dans()` : un croissant d'ombre, une plage claire) ; plus
  d'ovale, de rebond ni d'étoile dans le dessin (une image par objet, sauf le canard pouic-pouic et la lettre).
  Le jeu les pose avec `drawPosed()` (`POSED` : taille, hauteur du sol sous `it.y`, cadence du scintillement
  `fx/glint`) ; `MAP.itemBase` / `MAP.toyBase` (`pack_web.bases()`) = où le dessin s'assoit ; les familles
  « item » et « port » sont dans `MAP.cast`. Les sprites restent centrés dans leur cadre : le HUD ne bouge pas.
  Les gros ballons de Léon tournent : leur relief est une image à part, `ballon/relief`, posée dessus sans
  tourner. **Compteurs du HUD** : jamais un sprite du jeu agrandi (flou : vu sur les petits hérissons) ; les
  icônes `icone/hedgehog`, `icone/hen`, `icone/cat_white` sont le même dessin rendu à la taille du compteur
  (`pack_web.icone()`).
- **Ombres collées à l'objet** (Christophe : « des ombres qui ont un espace avant leur objet ») : une ombre part
  de la ligne de contact ; pour « contour », cette ligne est `nature.assise()`, la rangée où le bord droit de la
  silhouette cesse de s'écarter (le bout d'un socle rond), pas son point le plus bas, sinon un coin de sol reste
  éclairé à droite. Ce qui tient sur des pieds à des profondeurs différentes (banc, chevalets du portique et de
  la balançoire, toboggan, heurtoir) a une ligne en marches d'escalier (`mobilier._marches()`).
  `python3 tools/ombres_decollees.py [seuil]` couche chaque ombre comme le jeu et liste celles qui se décollent
  (le jour se mesure à la verticale et le long de l'ombre, on garde le plus petit : sous un pied mince, le sol
  est éclairé à la verticale sans que rien soit décollé ; au seuil de 5 px il ne reste que deux colonnes de la
  table de terrasse, à 3 px le liseré connu le long du mur qui fuit des maisons) : à relancer après
  tout nouveau décor.
- **Saisons** (lot 6 ; 12 novembre 2026) : chaque épisode a la sienne (`episodes.json`, `EP().saison`).
  `saisons.py` — une saison est d'abord une palette (feuillages `nature.FEUILLAGES`, herbe `tiles.GRASS`, quelques
  terrains `tiles.TERRAINS`) ; `appliquer(saison)` la pose (en place : les modules de dessin la lisent en
  dessinant ; toujours revenir au printemps, `appliquer()`), `python3 saisons.py` redessine l'étude
  `reference/v2/saisons_etude.png`. **Images d'une saison** (`pack_web.build_saisons()`) : le printemps est dans
  la page ; pour chaque autre saison d'un épisode, le tileset entier est redessiné avec sa palette, et tout
  l'atlas aussi, comparé à celui du printemps : seuls les sprites qui changent (21 en été : arbres, buissons,
  fourrés, haie, buttes des tunnels) sont rangés dans une image à part. Fichiers à côté de la page, comme les
  images x4 : `saison_<nom>_tiles.png`, `saison_<nom>_atlas.png` et leurs jumeaux `_x4` (été : 0,7 Mo en x2,
  1,7 Mo en x4), redessinés seulement si un module de dessin a changé (`web/saisons.json`), copiés dans la
  version autonome et publiés par `publish_docs.sh`. La page embarque `SAISONS[nom]` : les adresses (`?v=`) et
  `meta`, les entrées d'`ATLAS` à remplacer, dont les y sont décalés de `SAISON_Y` (2^20). Pour l'instant une
  saison ne change que des couleurs : `build_saisons()` refuse un sprite qui n'a plus le cadre du printemps
  (ombres, lignes de contact, perchoirs sont ceux du printemps) — à lever pour la neige de l'hiver.
  `game.js` : `update()` demande la saison de l'épisode dès qu'elle change (`askSeason()`, `seasonAsked`) ;
  `seasonFiles()` charge ses images (les nettes aussi quand `HD.k > 1` — pas `HD.on`, que le dessin de
  l'interface éteint à chaque image), gardées dans `seasons` ; `setSeason()` remplace les entrées d'`ATLAS`
  (`springFrames` : celles du printemps, rendues au retour), puis le sol et la carte de la pause se repeignent.
  `blit()` et `blitCols()` reconnaissent un cadre de saison à son y (`>= SEASON_Y`) et le lisent dans l'image
  de la saison (`season.img`, ou `season.pages` en images nettes) ; `groundTiles()` = le tileset du moment.
  Règle : une saison posée a toujours ses images nettes quand le jeu lit les images nettes (`setHD()` retire
  une saison qui ne les a pas, elle est redemandée ; `loadHD()` les charge d'avance). Tant que les images ne
  sont pas là, ou si elles manquent, le monde garde les couleurs d'avant. Un sprite de saison n'a pas d'ombre
  de `castShadow()` (il n'est pas dans la copie sombre de l'atlas : aujourd'hui ce ne sont que des décors, dont
  l'ombre est peinte dans le sol). Les couleurs écrites dans `game.js` (plages de l'herbe `MEADOW`, du sous-bois
  `WOOD`, fonds des mares `POND`) sont des voiles : elles n'ont pas eu besoin de changer en été ; les plants du
  champ et les brins d'herbe gardent leur vert. L'éditeur de carte montre toujours le printemps. Captures :
  `python3 v2/capture.py sortie.png "70,30,balade,region,ete"` (`--x2` : sans images nettes) ;
  `reference/v2/lot6_ete_jeu.png`. Tests : `saisons.js` (bascule, images nettes, fichiers absents),
  `saisons.py` (fichiers : mêmes formes, mêmes cadres, x4 = x2). Décisions de Christophe : épisodes l'un après
  l'autre, Alice à chaque saison, l'été d'abord (découpage dans `PLAN_V2.md`, lot 6).
- **Jointures de l'eau** (14 novembre 2026 ; Christophe : « les jointures ne sont pas bien faites » aux bords de la
  mer et de la rivière). Deux défauts des tuiles composées (`tiles.py`). **Mer et eau douce** : dans une tuile qui
  a les deux, elles ne font plus qu'une seule eau, posée d'un coup (`composite()` retire `sea` de ses terrains et
  donne à `_layer()` la part de mer en chaque point, `_part_mer()` : les seuls coins d'eau, pesés en ligne
  droite — le long d'un bord de tuile elle ne dépend que des deux coins de ce bord, donc elle se raccorde à la
  voisine, mêlée, toute de mer ou toute d'eau douce) ; `_shore()` reçoit cette part (`mer` : vrai, faux ou un
  tableau) et tout ce qui distingue les deux rives passe de l'une à l'autre en continu (`_teinte()`, `_eaux()`).
  Avant, la tuile posait la rive d'eau douce puis un voile de mer : elle ne se raccordait à aucune voisine
  (coupures nettes le long des berges du chenal et de l'embouchure). **Eau en pointe contre un quai ou des
  planches** (`vrai` de `_shore()` = les coins qui sont vraiment de l'eau) : la rive (sable mouillé, lèvre,
  écume) s'amincit avec l'eau au lieu d'être coupée net au bord de la tuile. Les tuiles à deux terrains n'ont
  pas changé. Sur la carte, la jonction mer / eau douce du chenal est une ligne droite, sous le pont ; en eau
  libre, le fondu ne fait qu'une tuile de large (pour l'allonger, il faudrait un terrain d'eau intermédiaire).
  Capture : `reference/v2/lot6_jointures_eau.png`.
- **L'été plus marqué sur le monde** (14 novembre 2026 ; Christophe : « augmenter la différence visuelle entre le
  printemps et l'été », choix sur `reference/v2/ete_monde_options.png`, `python3 v2/ete_monde_options.py`).
  **Palette « plein été »** (`saisons.SAISONS["ete"]`) : herbe vert-jaune chaude, feuillages profonds (sapins et
  fond de forêt compris), chemins de terre clairs, sous-bois plus sombre ; la première palette ne se distinguait
  pas assez. Une saison porte aussi `fleurs` (`nature.FLEURS` : en été marguerite, bouton d'or, coquelicot,
  bleuet — **les formes du printemps, d'autres couleurs** : `build_saisons()` refuse un cadre qui change),
  `brins` (`nature.BRINS`) et `fruits` (`nature.FRUITS` : des cerises sur le cerisier, à la place des cœurs de
  fleurs). **Lumière d'été** (`game.js` : `SUMMER()` = la saison de l'épisode) : `SHADOW.len` et `.alpha` sont
  des accesseurs (`lenEte`, `alphaEte` : ombres plus courtes et plus franches en plein jour), `SUN.tints` aussi
  (`tintsEte` : une teinte dorée dès le plein jour — `drawLight()` fait donc son remplissage toute la journée
  en été, le même que le soir ou sous la pluie). **Décors d'été posés** : la liste `extras` d'une carte
  (`carte.LISTES_LIBRES`, mêmes genres que `decor`) s'ajoute à ses décors (`pack_web.charger_carte()`), pour
  qu'une surcharge n'ait pas à redire toute la liste `decor` ; `cartes/ete/region.json` y pose une corde à linge
  (`clothesline`), une pataugeoire (`paddling_pool`), trois transats sous parasol (`deckchair`) et des bottes
  de foin — dessins `mobilier.corde_a_linge()`, `pataugeoire()`, `transat()` (`_parasol()`), obstacles `FOOT`.
  L'éditeur les montre et les déplace (type « Décor de saison », calque des décors). Test : `titre.js`.
  Captures : `reference/v2/lot6_ete_monde.png`.
- **Écran titre dessiné** (14 novembre 2026 ; choix sur `reference/v2/titre_options.png`, piste B : « un paysage
  dessiné pour chaque saison »). `titre.py` : `fond(saison)` — 1920 x 1080, un pixel par pixel d'interface ; le
  printemps : prairie, village sur sa colline, cerisier en fleurs, niche ; l'été : mer, falaise et phare,
  bateaux, plage, cabines, transat —, composé avec les dessins du jeu agrandis (`nature.CATALOGUE`) et des
  formes PIL suréchantillonnées (`SS`) ; `sprites()` — ce que le jeu anime dessus : nuages, Alice dans la tenue
  de la saison et Tecky assis (leurs animations du jeu, à `K` = 9 px par unité), papillon, mouette ;
  `planche()` les range. `python3 titre.py` : `reference/v2/titre_printemps.png`, `titre_ete.png`.
  `pack_web.build_titre()` : fichiers à côté de la page (`titre_<saison>.png`, `titre_sprites.png`, 1 Mo en
  tout ; `web/titre.json` ; copiés dans la version autonome et par `publish_docs.sh`) et `TITRE` dans la page
  (adresses, cadres de la planche, places d'Alice et de Tecky, horizon et rivage). `game.js` :
  `loadTitleArt()` au démarrage, `titleArt`, `artOn()` (titre, et Options ou Badges ouverts depuis le titre),
  `drawTitleArt()` à la place de `drawWorld()` (`ART` : nuages qui passent, papillons au printemps, mouettes et
  éclats de soleil sur la mer en été, fondu d'un paysage à l'autre quand on change d'épisode), `titleCX()` :
  sur le paysage, le logo, le choix de l'épisode et le menu passent à droite (`ART.cx`), sur un cartouche
  sombre ; `menuBox()` et `episodeTap()` suivent. **Sans les images** (page seule ouverte depuis le disque,
  tests : pas de `location`) : l'écran titre d'avant, le monde vivant sous son voile, le menu au milieu — les
  tests des menus n'ont donc pas changé. Une saison de plus : son paysage dans `titre.py` (`SAISONS`). Je n'ai
  vu les animations qu'en images fixes. Test : `titre.js`. Capture : `reference/v2/lot6_titre.png`.
- **Épisodes** (lot 6, le moteur ; 12 novembre 2026) : `episodes.json` (`episodes.py` : `charger()`,
  `valider()`, `python3 episodes.py`) donne les épisodes dans l'ordre où ils s'ouvrent : `id`, `saison`, `cartes`
  (un passage vers une carte qui n'en fait pas partie est fermé : `passageHere()`), `depart` (la carte de la
  niche), `chantier` (pas encore jouable). Aujourd'hui : `printemps` (le monde seul : le tunnel y est « pour les
  voitures ») et `ete` (la région et la plage, `plage`), **sorti du chantier le 14 novembre 2026** : il s'ouvre quand le printemps a été gagné. `pack_web.py` les embarque (`EPISODES`). `game.js` :
  `episode` = celui de la partie en cours et, sur l'écran titre, celui que le joueur a choisi ; `EP()` ses
  données ; `epOpen()` : le premier, ou un épisode prêt dont le précédent a été gagné (`epWon()` lit les
  records : pas d'autre donnée gardée ; n'importe quel mode ouvre le suivant) ; `openEpisodes()`, `lastOpen()`.
  Un épisode en chantier n'est ni proposé ni ouvert, sauf avec `?chantier` à la fin de l'adresse ou quand le jeu est
  servi par localhost (127.0.0.1, [::1], *.localhost) — `CHANTIER` : tous les
  épisodes sont alors ouverts, sans avoir à gagner le précédent (les records sont gardés par adresse, et
  Christophe ne retrouvait pas l'été sur un autre port). Le champ `chantier` reste pour les épisodes à venir. Chaque épisode est une partie neuve et
  a ses records (`recKey(mode, diff, ep)` : le premier garde les clés d'avant, les autres « ete:aventure »). La
  sauvegarde nomme son épisode (`ep` ; sans lui, le premier : `epOfSave()`) ; si sa carte n'est plus de
  l'épisode, la partie reprend à la niche. Écran titre : dès que deux épisodes sont ouverts, l'accroche devient
  le choix de l'épisode (`drawEpisodePick()`, `stepEpisode()` : gauche / droite ; `episodeTap()` au toucher ;
  textes `episodes.<id>.nom` / `.note`). La victoire qui ouvre un épisode l'annonce sous le tableau (`opened`,
  « Nouvel épisode : L'été ! ») et le titre le propose ensuite. La saison (`EP().saison`) ne change encore rien
  à l'image. Un nouvel épisode : une entrée dans `episodes.json`, ses deux textes. Dans un test, `CHANTIER` est faux (pas
  de `location`) : l'été ne s'ouvre qu'après une victoire au printemps, ou en choisissant `episode = "ete"`. Tests : `episodes.js` ; `cartes.js` se joue en été.
  **Ce qu'un épisode change à une carte** (les données d'un épisode) : `cartes/<épisode>/<carte>.json`, la
  surcharge, ne redit que les clés de la carte qui changent (objets, chiens, panneaux, place d'Alice… chaque clé
  remplace celle de la carte de base, en entier) ; une clé à `null` est retirée : la carte n'a plus ce
  personnage, cette liste, comme une carte annexe (`absents`). Aujourd'hui : `cartes/ete/region.json` (le monde
  sans les trois indices du printemps ni Alice dans sa cabane : en été, ils seront sur la côte ; la flèche mène
  donc au tunnel). `carte.py` : `surcharge()`, `surcharges()`, `appliquer()`, `difference()` (l'inverse, pour
  l'éditeur), `valider_surcharge()` (refuse une clé redite à l'identique, la taille de la carte, et vérifie la
  carte posée avec `valider(…, variante=True)` : comme une carte annexe, elle peut ne pas tout avoir, et n'a pas
  à porter les trois indices), `charger_episode(nom, episode)` ; `python3 carte.py` vérifie aussi les
  surcharges. `pack_web.py` : `charger_carte(nom, episode)` ; la page n'embarque de chaque carte changée que les
  données construites qui diffèrent (`SURCHARGES = { épisode: { carte: … } }` : 1 Ko pour l'été) ;
  `check_placement.js --carte nom --episode id` vérifie chacune. `game.js` : `carteOf(id, ep)` pose la surcharge
  par-dessus, `MAP.variante` la nomme (null : la carte de base), `onMap(id)` dit si la carte courante est bien
  celle de l'épisode en cours — à tester avant `useMap()` partout où l'épisode peut avoir changé (`newGame()`,
  `titleScene()` : l'écran titre montre le monde de l'épisode choisi, `stepEpisode()` le change sur place).
  Éditeur : `?carte=region&episode=ete`, ou le choix « Épisode » ; il ouvre la carte sous sa surcharge et
  n'enregistre que ce qui diffère de la carte de base (`editeur.lire()`, `enregistrer_surcharge()` ; une
  surcharge qui ne redit plus rien est retirée) ; retirer un personnage (`null`) se fait dans le fichier ;
  « Essayer ici » passe l'épisode (`ESSAI[4]`). À venir avec le contenu : les indices propres à chaque épisode
  (`CLUES` est encore celui du printemps). Tests : `tests/surcharges.py`, `episodes.js`.
- **Plusieurs cartes** (lot 6, jalon « deux cartes », 12 novembre 2026). Le jeu a la carte du monde (`carte.json`,
  « region » : toute l'aventure du printemps) et des **cartes annexes** (`cartes/<nom>.json`, `"annexe": true` ; aujourd'hui
  `cartes/plage.json`, la côte de l'été, 96 x 64 ; la petite carte d'essai `pre` qui a prouvé le moteur a été retirée). `carte.noms()`, `carte.chemin(nom)`. Une
  carte annexe n'a que ce qu'elle déclare : `carte.completer()` met le reste hors de la carte (`HORS`, loin de
  tout) ou vide, et en donne la liste (`absents`) ; `valider()` ne l'exige pas. On passe d'une carte à l'autre par
  un tunnel de la grande route : `"passages": [[n° du tunnel dans roadTunnels, carte, n° du tunnel d'arrivée]]`
  (le tunnel de l'est du monde mène à celui de l'ouest de `plage`, et retour ; `pack_web.py` refuse un passage
  vers une carte ou un tunnel qui n'existe pas ; le passage n'est ouvert que dans un épisode qui a les deux
  cartes : l'été).
  `pack_web.py` : `charger_carte(nom)` fait d'une carte la carte courante (ses variables de module : `MW`,
  `DECOR`, `EDGE`… ; « region » à l'import, pour l'éditeur) ; `build_map()` rend ses données, `build_jeu()` celles
  du jeu, les mêmes partout (dessins, ombres, cadences) ; la page embarque `JEU` et `CARTES = { region, plage }`. Les
  tuiles composées (`COMPOSITES`) sont numérotées à la suite pour toutes les cartes.
  `game.js` : **`MAP` est la carte courante**, qui hérite de `JEU` (`carteOf(id)` : `MAP.w` comme `MAP.ts`) ;
  `useMap(id)` en change et refait ce qui se calcule une fois par carte (`EDGE_DECOR`, `EDGE_SOLIDS`, `ZONES`,
  `LANDMARKS`, le sol, l'eau, la carte de la pause, la grille du parcours à pied) ; `ici('farmer')` dit si la
  carte courante a ce personnage, l'enclos, la voie… (`npcList()` ne rend que ceux qui sont là ; `updateTrain()`
  ne fait rien sans voie). `reset()` = la partie (Tecky, quêtes, compteurs), puis `resetWorld()` = les habitants de
  la carte courante. **Voyage** : Tecky pousse contre un tunnel qui a un passage (`edgeBump()`, `passageHere()`) →
  `travel(carte, tunnel)` : fondu, la carte quittée range son état dans `elsewhere[id]` (`mapState()` : objets,
  trésors, chiens, poules, lettres, Pompon, ballons, jouets, hérissons, cases vues), `useMap()`, `resetWorld()`,
  la carte d'arrivée retrouve le sien (`applyMapState()`), Tecky ressort **sur la route, devant la bouche du
  tunnel, à la hauteur où il est entré** (`arrivalAt(i, dy)`, `PASSAGE` ; au début il ressortait dans l'herbe sous
  le tunnel : « les entrées-sorties ne sont pas alignées »), les voitures toutes proches sont envoyées plus loin,
  sauvegarde. On n'entre que par la chaussée : contre la butte, à côté, rien ne se passe. Ce qui le suivait (Pompon, hérissons, copains) l'attend ; un jouet d'Iris porté reste
  devant le tunnel. Sur une carte qui n'a ni l'indice suivant ni Alice, la flèche et le flair ramènent au
  tunnel (`arrowTarget()`). Les badges qui comptent ce que porte la carte (bêtes, canards, os dorés,
  explorateur, copains) ne se gagnent que dans le lieu de l'épisode (`auLieu()`) : une carte vide les donnerait tous. Écran titre et
  nouvelle partie : toujours le monde. **Pièges** : une carte annexe ne doit jamais avoir à tester « null » — ce
  qu'elle n'a pas est en `HORS`, inerte ; un nouveau champ de carte lu par le moteur doit avoir sa valeur neutre
  dans `carte.completer()` et `build_map()` ; un cache construit à partir de la carte doit être vidé par
  `useMap()`. `check_placement.js --carte nom` vérifie chaque carte (sur une annexe, Tecky part de la sortie du
  tunnel, et chaque sortie de tunnel doit être praticable). Éditeur : `http://127.0.0.1:8770/?carte=plage`, ou le
  choix « Carte » en haut à droite ; les passages se modifient dans le fichier. Tests : `cartes.js`
  (aller-retour, état gardé, reprise sur la deuxième carte, sauvegarde v2), `editeur_sol.js` (sol de `plage`).
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
  `editeur/` : `sol.js` = le sol calculé comme `build_map()`, et `ED.cle(clé, x, y)` = le sprite d'un décor
  redessiné, le modèle que le jeu tire de sa position (`decorLook()`, `infos.variants` = `MAP.variants` ; sans
  position, pour la palette : le premier modèle) — test `editeur_sol.js` —, `etat.js` (carte, historique,
  objets), `vue.js` (dessin), `outils.js` (souris, clavier), `panneaux.js` (interface)). Terrain au pinceau sur les
  coins, détails, décors et éléments à la souris, zones et rectangles à poignées. « Vérifier » : `pack_web.py`, puis
  `check_placement.js --json` (problèmes avec leur position, grille du parcours à pied) et `export_voix.js --check`.
  Le porche du parking (objet `porche`, calque « route ») se déplace le long de la route : il règle
  `traffic.fin` (`ED.PORCHE_DX` : du x où la route s'arrête au pied du porche) ; la chaussée se repeint au pinceau.
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
- **Textes** (lot 5, le mécanisme ; 12 novembre 2026) : `textes/fr.json` est la source de tous les textes du jeu,
  embarquée par `pack_web.py` (`TEXTES = { fr: … }`, `LANG`). `game.js` ne connaît que des clés :
  `txt('farmer.merci.0')`, `txt('farmer.encore', { n })` (les `{mots}` sont remplacés ; une entrée `{ one, other }`
  se choisit d'après `n`, selon le pluriel de la langue, `plural()` : en français 0 et 1 sont au singulier),
  `txtDev('badges.retour')` (variante `.tactile` ou `.touches` d'un texte d'aide), `txtAt()` (la valeur brute,
  ou rien). Clés rangées par celui qui parle (`farmer`, `postman`, `neighbor`, `leon`, `iris`, `piquette`,
  `tecky`, `chat`…) ou par écran (`menu`, `options`, `badges`, `victoire`, `pause`…) ; `noms` (personnages),
  `dites` (les touches à dire à voix haute). La fonction ne s'appelle pas `t` : trop de variables locales
  portent ce nom (une boucle `for (const t of toys)` l'aurait masquée) ; de même, un test ne doit pas déclarer
  de variable `txt` dans le jeu (c'est arrivé dans `nettete.js`). Un texte nouveau : une clé dans
  `textes/fr.json`, jamais une phrase dans `game.js` — `tests/textes.js` le refuse (aucun littéral qui ressemble
  à une phrase), et vérifie que chaque clé citée existe et que chaque texte sert. Ne sont pas encore des clés :
  les panneaux, les noms de zones et de lieux de `carte.json`, la version (`pack_web.version()`), les touches
  dessinées (`hud.KEYS` : « Entrée », « Échap »), le titre de la page et le manifeste. Pas encore d'anglais ni
  d'option « Langue » : c'est la suite du lot 5.
- `web_src/game.js` : tout le moteur. Monde en pixels x2 (tuile = 64), caméra 960x540, interface 1920x1080 (`GW`/`GH`).
  Sol pré-rendu en blocs de 1024 px de canevas (`ground`, `groundChunk()`, `buildChunk()`, `groundTile()`, marge de
  la lisière comprise) : une seule image de la carte dépasserait la taille de canevas permise sur certains
  téléphones. Un bloc n'est peint que quand la caméra l'atteint ou s'en approche, et seuls les `GROUND_MAX`
  derniers sont gardés. **Blocs d'avance** (`prepareGround()`, `GROUND_AHEAD`, `groundBuilt`) : peindre un bloc
  coûte 15 à 30 ms à Firefox ; une image qui n'a rien peint prépare donc un bloc à moins de 128 px de l'écran,
  pour que la caméra n'en atteigne plus deux ou trois d'un coup (pas toute la couronne autour de l'écran : deux
  fois plus de blocs peints pour rien ; pas les ombres du soir tant que le soleil descend).
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
  et, depuis l'écran titre seulement, « Réinitialiser la progression », un bouton rouge (`resetAsk` : confirmation, « Non » d'abord ;
  au toucher, deux cases `resetPills()` ; `resetProgress()` efface sauvegarde, records et badges, pas les options ;
  `optBox(i)`). **Disposition** (14 novembre 2026, choix de Christophe sur
  `reference/v2/options_menu_options.png`, piste C ; `python3 v2/options_menu_options.py`) : deux colonnes, par
  groupes sous un intertitre — Son et Jeu à gauche, Image à droite (`r.g`, `OPT_COL`, `optLayout()`, `OPTV`,
  textes `options.groupes.*`) —, puis la remise à zéro et « Retour » sur toute la largeur ; haut / bas parcourt
  les lignes dans l'ordre d'`optRows()` (gauche / droite règlent les valeurs). Dans le jeu :
  `reference/v2/options_colonnes.png`. Test : `options.js`.
- Badges (`MAP.badges` = `hud.BADGES`, image i de `hud/badge`, la dernière = verrouillé ; textes `badges.<id>.nom` / `.but` (`badgeName()`, `badgeGoal()`), `BADGES_KEY`,
  gardés d'une partie à l'autre) : `checkBadges()` toutes les demi-secondes, `winBadges()` à la victoire (aventure,
  sans morsure = `bitten` faux, sauvegardé : seules les vraies morsures comptent, `hurtPlayer(…, bite)` — l'aboiement du
  doberman et la charge du chien de berger font mal sans être des morsures ; moins de 10 min). `unlockBadge()` : annonce « Nouveau badge ! »
  (`toasts`), rappel sur l'écran de victoire (`newBadges`), écran « Badges » depuis le menu principal
  (`state === 'badges'`). Un nouveau badge : l'ajouter à `hud.BADGES` (dessin), à `textes/fr.json` (`badges.<id>`) et lui donner une condition.
  **Badges d'un épisode** (`hud.BADGE_EP` → `MAP.badgeEp` ; sans cela, un badge est rangé avec le premier
  épisode) : l'écran des badges a une page par épisode (`badgePages()`, `badgeIds(ep)`, `badgePage`,
  `stepBadges()` : gauche / droite, `badgesTap()` au toucher, « ◀ L'été ▶ » sous le titre), seulement ceux qui
  sont ouverts ou dont un badge est déjà gagné ; `shownBadges()` = ceux qu'on montre et qu'on compte (tant que
  l'été n'est pas ouvert — le printemps pas encore gagné —, seize badges et l'écran d'avant). **L'été en a seize
  aussi** (14 novembre 2026 ; Christophe : « très peu de badges pour l'été ») : ses six quêtes (`checkBadges()`
  donne le badge de celui qui tient le rôle, `MAP.roles`) et les pendants des dix autres, gagnés sur la côte
  seulement (pendant l'épisode de l'été, dans son lieu : `auLieu()`) : `aventure_ete`, `copains_ete`, `os_dores_ete`, `intact_ete` (aucun coup :
  `scratched`, levé par tout `hurtPlayer()` qui porte, pince et piqué compris, sauvegardé), `rapide_ete`,
  `explorateur_ete`, `sieste_ete` (endormi sur le sable : `beachNap`), `crabes` et `goelands` (tous `scored`,
  donc en aventure) à la place des bêtes et des canards, `bain` (`P.swum`) à la place de Titine. Une victoire
  sur la côte donne les badges de l'été, pas ceux du printemps (`winBadges()`). `hud.BADGE_ORDRE` →
  `MAP.badgeOrdre` : l'ordre d'une page (`badgeIds()`), les pendants à la place de ceux du printemps. Une
  icône peut rendre le dessin d'un module (`_ic_crabes`, `_ic_goelands`). Planche : `reference/v2/badges_ete.png`.
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
- Son : musique des zones à 0,15 (`MUSIC_VOL`, `Music.level()` ; à 0,35, Christophe l'a trouvée « bien trop forte » : elle
  couvrait les bruitages), fanfare de victoire et musique de défaite à 0,3 (jouées une seule fois) ; sons continus de
  l'ambiance (`AMB` : pluie, clapotis, fontaine) très en dessous, eux aussi baissés à sa demande ;
  bruitages multipliés par `SFX_VOL` (1,4). KO de Tecky → `Music.start('lose')` ; rejouer relance le thème.
- Trésors (médaille 100, jouet pouic-pouic 50, balle 20) : jamais dans l'eau — `check_placement.js` le vérifie.
- Indices (`CLUES` : barrette à la ferme, chaussure dans la forêt, doudou au parc) : chacun dit où chercher ensuite
  (`clueNext()`, textes `indices.ensuite`), la flèche du HUD vise le prochain indice puis Alice (`arrowTarget()`). Elle n'est **pas permanente** :
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
- Villageois (`villagers`, `VILLAGER`, `VILLAGER_LINES` = combien de phrases chacun, textes `villageois.<qui>.<i>`, `MAP.villagers`, villageois.py) : Bernard le boulanger,
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
- Sauvegarde (`STORE` : localStorage, repli en mémoire si refusé ; clés `tecky-quest-save` v3 (`SAVE_V` ; une v2 se reprend : mêmes champs, dans le monde) et `tecky-quest-records`) :
  `saveGame()` toutes les `SAVE_EVERY` (4) s de jeu si `safeToSave()` (aucun chien engagé à moins de 600 px), à chaque
  indice et trésor (fin de réplique), en quittant la page (`pagehide`, onglet caché) ; jamais KO ni après la victoire.
  Contenu : l'épisode (`ep`), la carte courante (`carte`) et l'état des autres (`ailleurs` : `elsewhere`), puis, à plat pour la carte
  courante, mode, place, os, score, temps, indices, trésors, objets au sol, chiens restants (`d.id` = index dans
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
  dialogue dans tous ses cas et relève les répliques à clé fixe (un `txt('clé')` sans paramètre est remis en clair
  d'après `textes/fr.json`, puis lu comme une phrase écrite là) ; de même pour les bulles (`addWordPop(texte, x,
  y, qui)` : le 4e argument dit qui parle, personnage, 'tecky', 'info' ou animal ; `npcShout()` le passe tout seul) ; il écrit `voix/repliques.csv` / `.json` (une
  ligne par fichier audio : nom = `voiceKey()` du jeu, personnage + empreinte du texte à dire ; texte à dire =
  `spokenText()`, les [action] en mots selon l'appareil, textes `dites.<action>`). Une nouvelle réplique dont le texte est
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
- **La nage** (été ; 13 novembre 2026) : Tecky nage dans la mer, près du bord. `swimCoins()` calcule une fois par
  carte la **zone de baignade** — les coins de mer à moins de `SWIM.far` (4) coins d'un coin de sable —, l'eau
  où l'on ne nage pas (`deep` : le large et l'eau douce ; `deepAt()`) et la **ligne de bouées** qui marque la
  limite (`swimBuoys()`, sprite `mer/bouee` de `plage.bouee()`, elles dansent). Tout est vide sur une carte sans
  mer : le printemps n'a pas changé. Seul Tecky nage : `moveTecky()` lève `swimmer` le temps de son pas, et
  `blockedFeet()` demande alors `swimBlock()` au lieu de `waterAt()` — on n'entre dans l'eau et on n'en sort que
  par le sable (un nageur ne monte ni sur un quai ni sur la jetée, on ne saute pas d'un quai). `syncSwim()` :
  `P.swim`, et la famille du dessin, `P.kind` = `nage` au lieu de `tecky` (`tecky2.NAGE`, `nage_frames()`,
  `image_nage()` : ses poses de nageur, enfoncées de `ENFONCE`, coupées à la ligne d'eau `LIGNE`, cerclées d'écume
  `_eau()` ; mêmes noms d'animations et mêmes nombres d'images que sur la terre ferme — idle, walk, bark, bite,
  hurt, ko ; pas dans `MAP.cast` : pas d'ombre portée). Gerbe et `SFX.splash` en entrant et en sortant, il
  s'ébroue en sortant (`shakePending`), « Plouf ! » la première fois (`P.swum`, sauvegardé `swum`). Dans l'eau :
  plus lent (`SWIM.spd`), un coup de patte `SFX.paddle` et un rond `fx/ripple` (`swimStroke()`), il aboie et mord
  mais ne flaire pas, ne gratte pas, ne s'assoit pas ; s'il pousse vers le large, il le dit (`tecky.large`). Les
  autres (chiens, suiveurs) s'arrêtent au bord. Un panneau sur les planches l'annonce. Test : `nage.js` ;
  `tests/heros.py` (`ATTENDU["nage"]`). Planche : `reference/v2/tecky_v2_nage.png` ; dans le jeu :
  `reference/v2/lot6_nage.png`. Deux quêtes s'en servent : Théo et Yvon (voir les rôles).
- Os dorés : le trésor enterré (`item/goldbone`, `treasures` = os dorés trouvés, HUD et victoire). **Buttes et
  creux** (13 novembre 2026 ; Christophe : « uniformiser les trous », sur le modèle de ceux des coquillages de
  Zoé) : un trésor enfoui est signalé par une butte d'où dépasse un bout de ce qui est caché, et laisse un creux
  une fois gratté — `drawMound()`, sprites `butte/os_terre`, `butte/os_sable` (un os doré dans le sable :
  `g.sand`), `butte/coquillage` (`plage.mound_frames(sol, pointe)`, `SOLS`, `POINTES` : image 0 la butte et son bout qui dépasse, image 1
  le creux, image 2 la butte nue). **Le bout qui dépasse et son reflet ne sont montrés qu'en mode facile**
  (`facile()` ; demande de Christophe) : en mode normal, la butte nue, à repérer ; les textes ne parlent donc
  que de « butte » et de « bosses », jamais du bout qui dépasse. Il n'y a plus de traces de pattes ni de trou dans le tileset (les tuiles restent, inutilisées : les
  index n'ont pas bougé). Pour une autre saison (la neige) : un sol de plus dans `plage.SOLS`.
  **Le temps de le voir** (14 novembre 2026 ; Christophe : « on a à peine le temps de le voir qu'il l'a déjà
  ramassé ») : un os doré ou un coquillage qui sort de terre n'est pas ramassé tant que Tecky ne bouge pas,
  pendant `UNEARTH.hold` s (`admire()`, `admired()`) ; dès qu'il fait un pas (`UNEARTH.move` px), il le prend.
  Tests : `tunnel.js`, `zoe.js`.
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
  (`Ambience`, `AMB_EVENTS` : [son, intervalle min, max, 'jour' ou 'soir'], `ambSound()` : oiseaux (gazouillis,
  trille, mésange, coucou), coq, sonnette, ferraille, corne de péniche ; le soir, `lampsOn()`, les oiseaux se
  taisent : grillons, chouette, grenouilles près de l'eau, `AMB_NIGHT` ; chacun sort d'un côté tiré au hasard ;
  sons continus `Ambience.set()` / `start()` : clapotis selon l'eau autour, pluie, glouglou de la fontaine quand
  Tecky s'en approche, `AMB.fountainR`) et
  musique (le morceau de la zone, `SONGS`, `Music.zone`). **Changement de morceau** (`MUSIC_ZONE`) : Tecky doit
  rester `settle` (1,5 s) dans la zone (`tuneT` ; un passage éclair ne change rien), puis `Music.setZone()` : le
  morceau en cours **s'éteint** (`ramp()`, fondu vers le silence de `out` s ; `Music.want`, `Music.swap`), et après
  un silence (`gap`) celui de la nouvelle zone commence (`change()`, `open()`), à son début la première fois,
  ensuite au début de la partie la plus proche de l'endroit où on l'avait quitté (`Music.pos`, `entries`) : on ne réentend pas
  toujours les mêmes mesures en repassant dans une petite zone. Si Tecky revient pendant le fondu, le morceau
  remonte tout de suite (`back`). Christophe a trouvé « très étranges » les fondus enchaînés d'avant (deux
  variations superposées, tempo qui glisse), surtout avec des zones aussi petites : ne pas y revenir. Nouvelle
  partie, Continuer : fondu rapide (`cut`). L'écran titre joue toujours le thème depuis son début
  (`TITLE_MUSIC`, `toTitle()` vide `Music.pos`). Test : `music.js`. La rivière n'est pas une zone : celles du nord et du sud vont jusqu'à son
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
  De même pour le son : `FakeAC` de `sim.js` (`createDelay` pour l'écho, `createStereoPanner` pour les bruitages) ; tout nouveau nœud audio doit y être ajouté.
- **Performances (Firefox)** : Firefox dessine souvent le canvas avec le processeur. Rien de plein écran recalculé à
  chaque image : pas de dégradé ni de mode de fusion autre qu'un remplissage uni (la lumière pré-rend ses dégradés en
  petit, `buildLight()`) ; canvas plafonné à `MAX_PIXELS` (1920 x 1080), le navigateur agrandit au-delà (sinon
  216 ms par image en 4K au coucher de soleil). Mesurer dans Firefox sans fenêtre : `python3 tools/mesure_firefox.py`
  (`firefox --headless`, un profil où `browser.dom.window.dump.enabled` est vrai, canevas forcé à 1920 x 1080 ; la
  page chronomètre `render()` lieu par lieu, de jour et le soir, puis en traversant la carte, et écrit le résultat
  avec `dump()` ; `--detail` : les sprites les plus chers ; `--sans-avance` : sans `prepareGround()`). D'une mesure
  à l'autre, les chiffres bougent de 30 à 40 % : comparer deux mesures faites à la suite, pas à une heure d'écart.
  Lot 4 (12 novembre 2026) : 6 à 13 ms par image de jour, 9 à 17 le soir (la lumière : 3 à 6 ms ; les ombres de ce
  qui bouge : 0,3 à 2,6 ms ; les nuages : jusqu'à 3 ms) ; le point dur est la peinture d'un bloc de sol.
  **Images gardées décodées** (`keepDecoded()`, `atlasPx`, `tilesPx` ; 13 novembre 2026) : un navigateur ne
  décode une image qu'à son premier dessin — 56 à 134 ms d'un coup pour une page de 4096 px, mesuré dans Firefox
  — et peut jeter ce qu'il a décodé. Sur la côte, chaque zone touchait une image pas encore utilisée (la page
  des décors de la côte, les images de l'été) : Christophe a eu de « sérieux drops de frames en changeant de
  zones ». Toutes les images (atlas et tileset x2, pages x4, images des saisons) deviennent des `ImageBitmap`
  au chargement : 1 ms au premier dessin. Toute nouvelle image à dessiner doit passer par `keepDecoded()`.
  `python3 tools/mesure_firefox.py --carte plage` mesure la côte (en été).
  Images nettes : sur un canevas de 1920 x 1080 (échelle 2), Firefox va plus vite avec les images x4 (copie à
  l'identique : 6 à 12 ms par image) qu'en agrandissant les x2 (11 à 17 ms) ; à une échelle intermédiaire (1,33),
  réduire les x4 coûtait jusqu'à 45 % de plus, d'où le seuil `HD_MIN` (1,5). La fenêtre sans tête n'est pas en
  1080p : forcer dans la page `cv.width = 1920; cv.height = 1080; scale = 2` avant de mesurer.
- **Listes de carte.json et sauvegarde** : la sauvegarde retient chiens (`d.id`), trésors, petites bêtes, canards,
  lettres, poules de quête, ballons, jouets et petits hérissons par leur rang (`carte.INDEXEES`) : en ajouter à la fin,
  et ne pas en retirer au milieu sans augmenter `SAVE_V` (l'éditeur prévient). Tailles fixes (`carte.TAILLES`) : 5
  lettres, 5 ballons, 3 jouets (poulet, anneau, corde), 3 petits hérissons ; un seul de chaque indice ; un trésor au
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
  portique du port), véhicules, objets à ramasser posés au sol, mares en haricot faits ; rives et
  bords de chemin froissés, ombre de ce qui vole (`flyShadow()` : canards en vol, papillons), objets réduits à
  50 %, jouets d'Iris refaits, coût mesuré dans Firefox sans fenêtre faits ; Christophe l'a relu en mouvement
  dans un vrai Firefox (« ok, fluide »). Depuis : les filets d'ombre revus (le pied de la glissière du toboggan était à la mauvaise profondeur ; les
  autres étaient des artefacts de la mesure) et l'éditeur de carte montre les décors de la v2 : **le lot 4 est fini**, le suivant est
  le lot 5 (textes en données et anglais). Les études graphiques sont dans `v2/` (`python3 v2/temoin.py` écrit l'écran
  témoin dans `reference/v2/`) : des images fixes, que ni `game.js` ni `pack_web.py` n'utilisent encore (le décor
  de `nature.py` est dans le jeu depuis le lot 4). Les pistes générées par Christophe avec ChatGPT sont dans
  `reference/v2/chat_gpt/`.
- Piste en réflexion : dialogues lus à voix haute (pour qu'Alice joue sans savoir lire).
