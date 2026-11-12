# Tecky Quest — plan de la v2

But : une version qui tienne sa place sur une page de magasin (Steam d'abord, puis Xbox, puis Nintendo) et sur un
écran de télévision. Le point de départ est le diagnostic du 10 novembre 2026, fait sur le jeu construit : les
graphismes sont le premier point faible, la durée et la langue viennent ensuite.

## Diagnostic

Graphismes, par ordre d'effet sur une page de magasin :

1. **Tecky est le personnage le moins réussi du jeu.** Son profil est comprimé pour tenir dans 48 unités (`BASE`
   de `tecky.py`) : corps court, pattes longues, il ne ressemble pas à un teckel. Ses yeux sont minuscules, la vue de
   dos se lit mal. Les personnages de `npcs.py` et les portraits sont nettement au-dessus.
2. **L'image est floue sur grand écran.** L'atlas est rendu à l'échelle x2 (`S = 2` dans `pack_web.py`) : chaque
   pixel est agrandi 2 fois en 1080p, 4 fois en 4K. Les sources sont du SVG : la netteté ne coûte aucun dessin.
3. **Le monde ressemble à un plan plus qu'à un paysage.** Un seul modèle d'arbre (posé 72 fois), un sapin (55), un
   buisson (41) ; quatre variantes d'herbe, dont les fleurs dessinent un quadrillage ; route et rivière droites d'un
   bord à l'autre, étangs rectangulaires.
4. **Le dessin n'a pas de profondeur.** Aucun dégradé dans les dessins, des ombres toutes ovales, des maisons en
   façade pure, une eau en aplat. La lumière du soir est une teinte globale.
5. **Aucune image « vitrine ».** L'écran titre est le jeu plus un logo : ni illustration pour la vignette, ni
   bande-annonce.

Le reste :

- **Durée.** Une carte, trois indices, six quêtes ; un badge récompense une victoire en moins de dix minutes. Une
  première partie n'a pas été chronométrée, mais elle est courte pour un jeu payant.
- **Langue.** Français seulement ; les textes sont écrits en dur dans `game.js` (et les panneaux dans `carte.json`).
- **Voix.** Les répliques sont inventoriées (`voix/`, `tools/export_voix.js`, 226 fichiers attendus), le jeu sait
  nommer chaque fichier (`voiceKey()`), mais il n'en lit aucun et aucun n'est enregistré.

À garder tels quels : l'interface, les portraits, les personnages de `npcs.py`, la vie du monde (bêtes, météo,
lumière), la musique.

## Principes

- **Garder le style** : aplats de couleurs, contour brun `#3A1E12`, ambiance mignonne. C'est l'exécution qui pèche,
  pas le style.
- **Tout dessiner dans le pipeline Python.** Il ne dépend pas du moteur : le travail graphique survit à un éventuel
  portage console.
- **Rester sur le moteur web pour la v2** (et pour Steam, dans une enveloppe de bureau). Un portage console ne se
  décide qu'après.
- **Ne rien casser** : les règles du jeu ne changent pas dans les lots graphiques, `./tests/run_all.sh` reste vert à
  chaque lot, et chaque lot se livre seul.
- **Juger sur pièce** : chaque lot graphique se compare à l'écran témoin, en 1920 x 1080.

## Lots

| Lot | Contenu | Taille | État |
|---|---|---|---|
| 1. Écran témoin | Une scène du jeu redessinée à la qualité visée : la référence de tout le reste | petit | direction validée le 10 novembre 2026 ; second témoin (village) à faire avant les bâtiments |
| 2. Netteté | Atlas et tuiles à plusieurs échelles, affichage net en 1080p et au-delà | petit | fait dans le moteur ; reste à voir sur une télévision et sur téléphone |
| 3. Tecky et Alice | Les deux héros redessinés et animés ; puis les chiens | moyen | dans le jeu : Tecky et Alice le 10 novembre 2026, Tecky redessiné d'après la planche et les chiens le 11 ; à voir en jouant |
| 4. Paysage | Variantes, sol, eau, ombres portées, bâtiments, habillage des zones | gros | en cours : nature, ombres, herbe, eau, lisière, bords arrondis et bâtiments dans le jeu le 12 novembre 2026 |
| 5. Textes et anglais | Tous les textes en données, jeu jouable en anglais | moyen | à faire |
| 6. Durée | Plusieurs cartes dans le moteur, puis de nouveaux épisodes | très gros | à cadrer |
| 7. Voix | Répliques lues dans le jeu, en français et en anglais | moyen | à faire |
| 8. Vitrine | Écran titre illustré, vignette, captures, bande-annonce | moyen | à faire |

L'ordre a ses raisons : les textes passent en données (5) avant le nouveau contenu (6), pour l'écrire directement
dans les deux langues ; les voix (7) viennent quand les textes ne bougent plus ; la vitrine (8) montre le jeu fini,
mais une page Steam peut ouvrir dès la fin du lot 4.

### 1. Écran témoin

Le jardin de la niche (le premier écran du jeu), cadré comme au début d'une partie, redessiné par le pipeline.
C'est une image fixe, pas le jeu : rien dans `game.js` ni dans `pack_web.py` ne s'en sert.

```bash
python3 v2/temoin.py            # reference/v2/temoin_niche.png (1920 x 1080) et avant_apres.png
python3 v2/temoin.py --avant    # refait d'abord avant_niche.png : une capture du jeu actuel (après pack_web.py)
python3 tecky2.py               # reference/v2/tecky_v2.png et tecky_v2_anims.png : les planches du nouveau Tecky
python3 nature.py               # reference/v2/nature_v2.png : arbres, buissons, rocher, niche
```

- `tecky2.py` (à la racine depuis le lot 3 : c'est le Tecky du jeu) : Tecky en vrai teckel, et ses expressions.
- `nature.py` : chêne, bouleau, cerisier en fleurs, jeune arbre, buissons, roseaux, rocher, niche de trois
  quarts et sa gamelle.
- `v2/temoin.py` : le sol calculé d'après les coins de `carte.json`, ce qui est posé à plat (brins, fleurs,
  cailloux, nénuphars), les ombres portées, puis les sprites triés par leur pied.

Le témoin ne montre pas encore : les bâtiments, les personnages, les chiens (le roquet du coin est retiré de
l'image), l'interface, la lumière du soir. Les objets, les canards et les papillons sont ceux du jeu actuel, tels
quels : ils tiennent déjà le niveau.

Christophe a validé la direction le 10 novembre 2026 : on continue par code. Un second témoin, la place du
village, suivra pour les bâtiments et les personnages (avant le lot 4).

Ce qu'on retient des deux pistes générées avec ChatGPT (`reference/v2/chat_gpt/`) :

- **La scène** : un feuillage au bord festonné, en trois tons, plutôt que des boules brillantes, et des verts plus
  chauds. Les deux sont repris dans `nature.py` et `v2/temoin.py`. Non repris : le pelage moucheté de Tecky et le
  contour uniforme (le témoin garde le brun pour les personnages, une teinte foncée pour le paysage).
- **La planche de Tecky** : elle confirme le corps du témoin (long, harnais à anneau, grande oreille), et ses
  expressions sont plus réussies que celles du premier témoin. `v2/tecky2.py` en reprend la grosse truffe, le bas
  du visage clair et les six expressions (`EXPRESSIONS` : content, inquiet, fier, surpris, endormi, aboie), plus
  « joyeux », la gueule entrouverte du trot. Non repris : la tête tournée d'un quart, avec ses deux yeux. Essayée,
  elle ne va pas avec le museau allongé du teckel ; la tête reste de profil, avec un seul œil.
  Règles sorties des retouches du 10 novembre, écrites dans le module : la bouche, ouverte ou fermée, s'arrête au
  menton, bien en retrait de la truffe (`MENTON`) ; fermée, la mâchoire n'est qu'une fine bande sous la lèvre, pour
  laisser au museau sa longueur. Christophe a validé la gueule. Restent pour le lot 3 : la face et le dos.
  (Le 11 novembre, il a jugé cette tête « encore vraiment moche » une fois dans le jeu : elle est redessinée d'après
  la planche, voir le lot 3. La règle du menton reste.)

### 2. Netteté

Fait le 10 novembre 2026 (détail dans `CLAUDE.md`, « Images nettes ») :

- `pack_web.py` rend l'atlas et le tileset une seconde fois en x4 (`web/atlas_x4_0.png`, `atlas_x4_1.png`,
  `tiles_x4.png`, 8 Mo en tout), aux mêmes places que les images x2 : la page reste autonome en x2, les images x4
  sont à côté.
- Sur un grand écran, `game.js` les charge et lit l'atlas deux fois plus fin (`blit()`) ; le sol est peint à la
  demande, par blocs, à l'échelle chargée. Téléphones, tablettes et page ouverte depuis le disque restent en x2.
- Les unités du monde ne changent pas : ni les collisions ni les règles du jeu.
- Vérifié sur deux captures du jeu en 1920 x 1080 (Chromium), l'une tenue en x2, l'autre où une étiquette confirme
  que le jeu lit les images x4 : `reference/v2/nettete_avant_apres.png`. Une première comparaison était fausse : la
  capture « après » avait été prise avant la fin du chargement des images x4, et montrait donc du x2.
- Pour comparer soi-même : servir `web/tecky_quest_web` (`./serve.sh`), ouvrir le jeu dans une fenêtre d'au moins
  1440 px de large, puis la même adresse suivie de `?x2`. L'écran titre affiche « images x4 » à côté de la version
  quand elles sont chargées. Une page ouverte depuis le disque reste en x2.
- Mesuré dans Firefox sans fenêtre, qui dessine le canvas avec le processeur, sur un canevas de 1920 x 1080 : une
  image coûte 6 à 12 ms avec les images x4, contre 11 à 17 ms en x2 (une copie à l'identique au lieu d'un
  agrandissement). À une échelle intermédiaire (1,33), c'était l'inverse, jusqu'à 45 % de plus : les images x4 ne
  sont donc chargées qu'à partir de 1,5 pixel de canevas par pixel de monde (`HD_MIN`).

Reste à faire :

- regarder le jeu sur une télévision, et vérifier qu'un téléphone garde son débit d'images (il reste en x2, mais le
  sol est maintenant peint à la demande) ;
- la 4K : le canvas reste plafonné à 1920 x 1080 (`MAX_PIXELS`) puis agrandi par le navigateur. Une image nette en
  4K demanderait un atlas x8 (huit pages) : à décider plus tard, si le besoin se confirme ;
- la publication : `docs/` pèse 8 Mo de plus, renvoyés à chaque livraison où un dessin a changé.

### 3. Tecky et Alice

Fait le 10 novembre 2026, dans le jeu ; Tecky redessiné le 11 (voir « Taille » et « La tête ») :

- **Tecky** (`tecky2.py`) : les trois vues sont **relevées sur la planche** de `reference/v2/chat_gpt/` (profil,
  face, dos : mêmes proportions, mêmes formes, au contour du jeu près) : gros crâne rond, museau court qui remonte
  vers une grosse truffe, grands yeux, oreilles immenses, corps en saucisse, harnais en Y sur le poitrail.
  Toutes les animations du jeu sont refaites, sous les mêmes noms : attente, trot en 8 images (le dos ondule, la
  tête, les oreilles et la queue suivent avec un temps de retard), aboiement, morsure, « aïe »,
  grattage, KO (il finit sur le dos, les quatre fers en l'air), et le repos : assis, bâillement, il se gratte, il
  dort, il s'ébroue. De face et de dos, il se dandine : le poids passe d'une patte à l'autre, la tête penche, les
  oreilles et la queue battent (`reference/v2/tecky_v2_marche.gif`).
- **La tête** : mes deux premières versions, dessinées de mémoire (museau en coin, petit œil, crâne aplati), ont
  été jugées « vraiment moches » par Christophe, et la marche de face et de dos aussi (seules les pattes
  bougeaient). La planche qu'il a générée est le modèle : on la suit, on ne l'interprète pas.
- **Alice** (`alice2.py`) : d'après `reference/alice_tecky.png`. Carré mi-long et frange en mèches, grands yeux à
  cils, t-shirt à manches courtes, jupe plissée, mains et pieds nus ; marche en 8 images, saut de joie les bras
  en l'air.
- **Portraits** : celui de Tecky a sept visages (`FACE` dans `game.js`) ; l'inquiet, le surpris et le fier servent
  dans une dizaine de répliques (« elle n'est pas rentrée ! », un indice trouvé, « je m'en occupe ! »). La liste
  des voix (`voix/repliques.csv`) donne le ton correspondant.
- **Taille** : Tecky est réduit de 0,5 dans le jeu (`tecky2.ECH`), Alice de 0,7. De profil il mesure 34 x 22
  unités (l'ancien Tecky : 40 x 28 ; le roquet : 32 x 34) : plus petit que tous les chiens, la tête sous la jupe
  d'Alice. À 0,8 (le premier témoin), à 0,7, puis à 0,58 (la taille de l'ancien Tecky), Christophe l'a trouvé
  « énorme », puis « encore trop gros » : sa taille se juge à côté d'Alice et des chiens, pas seul, et pas d'après
  l'ancien sprite. Le décor du témoin (`nature.py`), dessiné pour un Tecky bien plus grand, sera à réduire
  d'autant au lot 4.
- **Règles du jeu** : rien ne change. La boîte de collision (les pieds) est la même, et la morsure porte au même
  endroit ; seuls l'aboiement, les « z » et le jouet dans la gueule ont été recalés sur le nouveau dessin.
- **Les chiens** (`chiens2.py`, le 11 novembre 2026) : roquet, bouledogue, doberman, border collie, redessinés dans
  la famille de Tecky. Sans planche de référence : ils reprennent sa tête relevée sur la planche (crâne, œil,
  truffe, gueule), dont le museau est allongé, raccourci ou épaissi selon la race, avec leurs oreilles, leurs
  taches, des sourcils froncés, un croc et le collier à clous ; les mêmes pattes dodues, le même contour. Mêmes
  tailles qu'avant (rien à régler dans le jeu, sauf l'aboiement du doberman), mêmes animations, marche en 8
  images, KO sur le dos. Planche : `reference/v2/chiens_v2.png` ; dans le jeu : `chiens_en_jeu.png` ; en
  mouvement : `chiens_v2_marche.gif`. Si Christophe préfère un modèle, le prompt pour ChatGPT est dans « Visuels
  générés » ; les planches se relèveraient comme celle de Tecky.
- `tecky.py`, `alice.py` et `enemies.py` (les dessins de la v1) ont été retirés le 12 novembre 2026 avec le kit
  GameMaker, abandonné par Christophe : le jeu web est le seul livrable. `tests/heros.py` garde, écrit en dur, ce
  que le moteur attend des animations (noms, vues, nombres d'images).

```bash
python3 tecky2.py     # reference/v2/tecky_v2.png (têtes, vues, poses) et tecky_v2_anims.png (toutes les images)
python3 alice2.py     # reference/v2/alice_v2.png
python3 v2/capture.py sortie.png "4.5,4.2,balade" "P.dir = 'right';"    # une capture du jeu en 1920 x 1080
```

Captures du jeu : `reference/v2/lot3_en_jeu.png` (prises avec `v2/capture.py`, qui servira aux lots suivants : il
place Tecky sur une case, lance du JavaScript dans la partie, et étiquette la capture avec ce que le jeu lisait).
Test : `tests/heros.py` (mêmes noms d'animations qu'avant, pieds sur l'origine, rien hors du cadre).

Reste à faire :

- **Les personnages secondaires** : passe du 11 novembre 2026, après que Christophe a joué (« c'est ok ») :
  - les chats (roux, noir, Pompon) et l'écureuil dépassaient le nouveau Tecky : réduits (`critters.SCALE`), un chat
    est maintenant un peu plus petit que lui ;
  - Alice : petites chaussures rouges à bride et socquettes (choisies parmi trois sur
    `reference/v2/humains_temoin.png`), et rapetissée (`alice2.ECH` 0,59 : 41 unités, une enfant de 5 ans à côté
    des adultes) ; la chaussure qu'elle perd dans la forêt est du même rouge ; elle a donc un pied nu quand Tecky la
    retrouve (sprites `alice1`), et la piste du flair alterne une empreinte de chaussure et une de pied nu ; elle
    remet sa chaussure pour la scène de fin ;
  - les autres humains (fermier, facteur, Mamie Rose, Léon, villageois) : grands yeux à deux reflets, comme ceux
    d'Alice, et petit nez sans contour ; épaules en pente douce au lieu de boules ; tabliers de la fleuriste et de
    la marchande refaits (bretelles, bavette) ;
  - après ses remarques sur les captures : les cuisses des chats et de l'écureuil ne sont plus des ronds cernés
    (fondues dans le corps, un pli, comme Tecky) ; Alice a un cou, et ses cheveux de derrière, assombris, ne font
    plus une barre sous son menton.
  - les animaux (le même jour, trois sous-agents en parallèle, un par module, relus puis intégrés) : vaches et veau
    redessinés (`cows.py` : vraies proportions, tête de profil, grands yeux, pis, cloche) ; poules redessinées et
    réduites, canards réduits et retouchés (`hens.py`, `ducks.py`) ; Maman Piquette redessinée et ramenée à 26
    unités de haut, ses petits à 14 x 9 (`npcs.py`, `herissons.py`) ; bulles, compteurs du HUD, file des petits et
    boîtes des vaches réglés dans `game.js`.
  - de face, Tecky et les chiens montrent un peu de leur croupe et leur queue derrière la tête (sans elles, ils
    paraissaient plats et assis) ; Iris est redessiné avec la tête des nouveaux chiens et un air amical.
  Restent dans leur dessin d'avant : les papillons, les véhicules. À côté du nouveau
  Tecky, Alice paraît maintenant petite : il lui arrive à la taille.
- **Le museau dans les murs** : de profil, Tecky dépasse sa boîte de collision de 22 px (20 avant). Collé à un mur
  ou à un tronc, son museau passe dessus, un peu plus qu'avant. À revoir avec les obstacles du lot 4.
- Vu par Christophe sur des captures en 1920 x 1080 et sur les GIF (`reference/v2/tecky_v2_marche.gif`,
  `tecky_v2_animations.gif`), pas encore en jouant.

### 4. Paysage

- **Variantes** : 4 ou 5 arbres, 3 sapins, 4 buissons, rochers, choisis d'après la position (`hash3`, comme les
  tuiles) : rien à changer dans `carte.json`.
- **Sol** : grandes nuances de vert, brins et fleurs semés sans quadrillage, bords de chemin irréguliers.
- **Eau** : berge, bande peu profonde, fond plus sombre, nénuphars et roseaux.
- **Ombres portées** : la silhouette de chaque sprite, couchée du côté opposé au soleil ; elles s'allongent quand
  le jour baisse (`sun`).
- **Contours** : brun pour les personnages et ce qu'on peut toucher, teinte foncée du décor pour le reste, pour
  que les personnages se détachent.
- **Bâtiments** : un toit en volume, un mur dans l'ombre, des fenêtres éclairées la nuit.
- **Habillage** : chaque zone reprise à l'éditeur (bouquets plutôt que semis réguliers, un repère fort par zone),
  rivière et chemins moins droits.

Fini quand chaque zone a sa capture comparée à l'écran témoin.

Fait le 12 novembre 2026, dans le jeu :

- **Variantes** (`nature.py`, à la racine : c'est le décor du jeu) : un arbre de `carte.json` devient un chêne, un
  chêne sombre, un bouleau, un jeune arbre ou un cerisier en fleurs ; un buisson, l'un de cinq (fleuri, à baies,
  sombre…) ; un sapin, l'un de trois ; pommiers, rocher, roseaux et niche de trois quarts redessinés. Le modèle
  est tiré de la position du décor (`nature.VARIANTES`, `MAP.variants`, `decorLook()` dans `game.js`) : rien ne
  change dans la carte, ni les obstacles. Les sprites du témoin sont réduits (`nature.ECH`) à la taille des décors
  qu'ils remplacent.
- **Ombres portées** : la silhouette de chaque sprite de la nature, couchée vers la droite (`nature.ombre()`,
  sprites `ombre/…`), peinte une fois dans le sol (`groundShadows()`) : deux ombres qui se recouvrent ne se
  cumulent pas, et rien n'est recalculé à chaque image.
- **Herbe** : tuile unie, puis, peints dans le sol d'après la position (`groundDetails()`) : de grandes plages
  plus claires ou plus sombres au milieu des prés, des touffes de brins, des bouquets de petites fleurs.

- **Eau** (`tiles.py` : `_shore()` ; `game.js` : `waterDetails()`) : une berge de sable, des hauts-fonds clairs,
  une eau moyenne puis le fond, l'ombre de la berge du haut et de gauche, de l'écume en bas et à droite ; au
  large, des fonds plus sombres ; près des rives, des nénuphars par bouquets ; sur le sable, des galets.
  Captures : `reference/v2/lot4_eau.png`, `lot4_niche.png`.
- **Lisière** : ses fourrés sont ceux de la nature (`nature.fourre()`, cinq modèles, plus sombres le long de la
  forêt, avec leur ombre portée) ; le tunnel de la route est redessiné en calques, celui de l'est éclairé du bon
  côté. Captures : `lot4_lisiere.png`, `lot4_tunnel.png`.
- **Angles arrondis** (demande de Christophe : « une cassure visible à chaque angle » des mares et des chemins) :
  le champ qui dessine tous les bords est interpolé en douceur (`tiles._ease()`), les courbes repartent dans
  l'axe des bords droits. La collision de l'eau suit le même tracé (`waterVal()`).
- Les ombres des buissons et des rochers étaient hachurées vues de près : bouchées (`nature.ombre()`).
- **Bâtiments** (`batiments.py`) : Christophe a choisi sur planche (`reference/v2/maisons_options.png`) le trois
  quarts de la niche, « B et C mélangés » : façade longue devant (maison rouge, maison haute à lucarne et balcon,
  boulangerie, entrepôts, guérite) ou pignon devant (maison bleue, colombages, grange à toit brisé, cabane
  d'Alice, et l'une des deux maisons rouges). Mur de droite dans l'ombre, toit en volume, ombre portée ; chaque
  dessin tient dans l'emprise de l'ancien (obstacles et carte inchangés). Le soir, quand les lampadaires
  s'allument, les fenêtres aussi ; un personnage devant une maison reste devant ses fenêtres. Les chats ont leurs
  perchoirs sur les nouveaux toits. Planche : `reference/v2/batiments_v2.png` ; dans le jeu : `lot4_village.png`,
  `lot4_village_soir.png`, `lot4_ferme.png`.
- **Tailles** (demande de Christophe, le même jour : maisons puis véhicules « trop petits ») : bâtiments agrandis
  de 1,2 à 1,3 (`batiments.ECH`), voitures, camionnette et bus de 1,5 (`vehicles.ECH`), camion, tracteur et chariot
  élévateur de 1,4 à 1,5 (`decor.ECH`) ; les obstacles et les longueurs des véhicules suivent (`MAP.grow`,
  `MAP.vehicleScale`). Le doberman de l'entrepôt est décalé de 0,8 tuile dans `carte.json` : il se retrouvait
  derrière le bâtiment. Captures : `lot4_route.png`, `lot4_port.png`. Les véhicules gardent leur dessin de la v1.
- **Marché et basse-cour** : les trois étals (comptoir, cagettes, store rayé qui fuit) et le poulailler sur pieds
  (rampe, nichoir) sont de trois quarts eux aussi, agrandis de 1,25. Christophe a donné carte blanche pour
  déplacer ce qui passe derrière un décor agrandi ou sort de l'écran : l'os derrière l'étal de légumes est remonté
  de 0,7 tuile, la maison haute descendue de 0,4 (sa cheminée était coupée). Captures : `lot4_marche.png`,
  `lot4_poulailler.png`.
- **Ombres des bâtiments** (remarque de Christophe : « une marge entre le poulailler et son ombre, pareil pour
  les maisons ») : l'ombre partait d'une ligne posée juste sous les murs, d'où un liseré clair ; elle part
  maintenant de dessous le contour (`batiments.CONTACT`, et la niche de `nature.py`). Les ombres restent
  détaillées (il les préfère à une silhouette pleine, essayée puis retirée).

- **Ombres calculées par le jeu** : plus d'images d'ombres dans l'atlas. Le jeu couche la silhouette de chaque
  décor à partir de la ligne où il touche le sol (`MAP.sols`, `groundShadows()`), ce qui donne une ombre portée à
  tous les décors (bancs, lampadaires, bottes de foin, clôtures, tracteur, camion… : plus d'ovale) et permet de
  les allonger quand le soleil baisse (`SHADOW.len` : 1 en plein jour, 1,5 au coucher du soleil, 1,85 ensuite).
  Les blocs de sol sont alors repeints un par image. Captures : `lot4_ombres.png`, `lot4_ombres_soir.png`.

- **Ombres des personnages, des bêtes et des véhicules** : leur ovale est retiré des dessins, le jeu couche leur
  silhouette sous eux à chaque image, dans le même sens et de la même longueur que celle des décors
  (`castShadow()`). Un saut laisse l'ombre au sol. Captures : `lot4_ombres_personnages.png`, `lot4_ombres_route.png`.

- **Ombres fusionnées** (question de Christophe : « y a pas moyen de fusionner les ombres ? ») : l'ombre d'un
  personnage ne s'ajoute plus à celle d'un arbre ou d'une maison, ni à celle d'un autre personnage. Chaque bloc
  de sol garde le masque de ses ombres ; la silhouette d'un personnage y est gommée avant d'être posée
  (`drawCastShadows()`). Capture : `lot4_ombres_fusion.png`.

- **Sous-bois et champ** : tuiles calmes (un vert uni ; deux buttes par tuile) et habillage semé par le jeu,
  comme l'herbe. Sous-bois : taches de soleil, plages d'ombre, fougères, mousse, champignons, pommes de pin,
  brindilles, feuilles mortes, quelques fleurs blanches (`nature.sol_sousbois()`, `woodDetails()`). Champ : un
  potager, des rangs de pousses, de salades, de carottes et de poireaux sur les buttes
  (`nature.sol_cultures()`, `fieldDetails()`). Captures : `lot4_sous_bois.png`, `lot4_champ.png`.

- **Petit mobilier** (`mobilier.py`, planche `mobilier_v2.png`) : conteneurs, caisses, palettes, tonneaux,
  bottes de foin (carrées ou rondes), cagette de pommes, banc, boîte aux lettres, haie, de trois quarts comme
  les étals ; table de terrasse sous son parasol, pots de fleurs (trois bouquets) ; souche, tronc couché,
  champignons (amanites ou bolets) et fougères au contour de la nature. Tailles (remarque de Christophe :
  « les containers et la grue sont très petits ») : conteneurs et portique à 1,5, table de terrasse 1,35,
  lampadaire 1,3, foin 1,3, tonneaux 1,35, banc 1,2. Au port, déplacés dans `carte.json` : le portique et la
  pile de conteneurs (vers l'est), le conteneur vert (à droite du portique), le second conteneur orange (en bas
  à gauche du quai), un entrepôt, une palette, deux tonneaux, un lampadaire, un chat et un ballon de Léon.
  Captures : `lot4_port.png`, `lot4_terrasse.png`, `lot4_foret_mobilier.png`.

- **Gros objets et suite du mobilier** (demande de Christophe : « il faut redessiner le nid de maman Piquette
  aussi et vérifier qu'il ne reste pas d'autres objets du même type ») : portique du port (chevalets en A,
  poutre-caisson, cabine, chariot, crochet), péniche (1,4), bitte, heurtoir, toboggan et balançoire (1,3), nid
  de feuilles de Maman Piquette, panier d'Iris, lampadaire, cône, panneau indicateur, panneau routier. Le
  lampadaire du quai est passé à gauche du portique. Planche de ce qui reste dans son dessin de la v1 :
  `mobilier_reste_v1.png` (18 décors, à trancher avec Christophe).

- **Véhicules** : voitures, camionnette de boulangerie et bus de la route, tracteur, chariot élévateur et camion
  garés, redessinés sans changer leurs cadres : lumière d'en haut (juste aussi en miroir), passages de roue,
  jantes, pare-chocs, rétroviseurs, et du monde derrière les vitres (conducteurs, boulanger, passagers du bus).
  Planche `vehicules_v2.png`, capture `lot4_route.png`.

Reste : les objets (os, lettres, ballons), les canards et les papillons, qui gardent leur petit ovale ; des bords de chemin et de rive moins réguliers (ils sont lisses, mais droits) ; l'habillage des zones (dont : la forme des mares, encore rectangulaire ; un cerisier en
fleurs au milieu des sapins de la forêt). L'éditeur de carte montre encore les anciens arbres (il lit
`decor/tree`…), pas les variantes.

### 5. Textes et anglais

- Tous les textes sortent de `game.js` : `textes/fr.json` (la source) et `textes/en.json`, une fonction
  `t('clé', {n})` avec les pluriels. Les `[action]` restent telles quelles.
- Panneaux, noms de zones et de lieux de `carte.json` : des clés.
- Option « Langue » (celle du navigateur ou de Steam par défaut).
- Tests : chaque clé existe dans chaque langue ; chaque réplique tient en 3 lignes (4 en texte grand) dans chaque
  langue ; `export_voix.js` produit une liste par langue.
- Traduction : noms des personnages et jeux de mots à trancher (Mamie Rose, « Tut-tut ! »…), relecture par un
  anglophone avant toute sortie.

Fini quand une partie complète se joue en anglais sans un mot de français, et qu'ajouter une langue ne demande plus
aucun code.

### 6. Durée

Objectif à chiffrer après mesure (une première partie complète, jouée par quelqu'un qui découvre le jeu). Cible
proposée : deux à trois heures pour tout voir.

Proposition : **quatre épisodes, un par saison**, dans un monde qui change.

- **Moteur** : plusieurs cartes (`MAP` est aujourd'hui une constante unique, 135 références), passages d'une carte à
  l'autre (les tunnels de la route, des portes), sauvegarde v3 (épisode, carte, progression de chaque épisode),
  éditeur qui ouvre la carte choisie.
- **Chaque épisode** : une grande recherche (trois indices, une cachette), le monde aux couleurs de la saison (une
  palette par saison, générée par le pipeline, décor et météo assortis), deux nouvelles quêtes de personnages, un
  lieu nouveau, une idée de jeu propre.
  - Printemps : l'aventure actuelle.
  - Été : un lieu au-delà du tunnel de la route (le lac ou la plage), Tecky nage.
  - Automne : tas de feuilles où gratter, brouillard dans la forêt, pommes du verger.
  - Hiver : la neige existe déjà ; rivière gelée où l'on glisse, traces dans la neige.
- **Rejouer** : la cachette d'Alice et les indices tirés au sort parmi plusieurs ; un album d'autocollants (bêtes,
  personnages, objets rencontrés).
- **Intérieurs** (boulangerie, grange, cabane), une fois les cartes multiples en place.

Fini quand la durée mesurée atteint la cible, et que la sauvegarde d'une partie en cours passe d'un épisode à l'autre.

### 7. Voix

- Lecture dans le jeu : un fichier par réplique, chargé à la demande (ils ne tiennent pas dans la page unique),
  mis en cache par le service worker ; le texte s'affiche au rythme de la voix.
- Options : volume « Voix », et les menus lus à voix haute pour qui ne sait pas lire.
- Production, par langue : synthèse vocale ou comédiens. Le nom d'un fichier dépend du texte : une réplique
  modifiée se voit tout de suite (`node tools/export_voix.js` dit ce qui manque et ce qui est en trop).

Fini quand une partie complète se joue sans lire, dans les deux langues.

### 8. Vitrine

Écran titre illustré, vignette et captures composées par le pipeline avec les sprites du jeu (mêmes dessins, à
n'importe quelle taille), bande-annonce d'une minute.

## Décisions à prendre

| Quand | Décision |
|---|---|
| Fin du lot 1 | La direction de l'écran témoin : on continue par code, ou un illustrateur fait la planche de style |
| Avant le lot 6 | La structure du contenu : épisodes par saison, monde plus grand, ou intérieurs d'abord |
| Avant le lot 7 | Synthèse vocale (licence commerciale, voix d'enfant crédible) ou comédiens ; qui prête sa voix à Alice |
| Avant le lot 5 | Les langues au lancement (français et anglais proposés) |

## Après la v2

Enveloppe de bureau pour Steam (succès à partir des badges, sauvegarde dans le nuage, Steam Deck), page de
magasin, puis la question du portage console. (Le kit GameMaker a été abandonné le 12 novembre 2026.)

## Visuels générés (ChatGPT)

Christophe peut générer des images avec ChatGPT. Elles servent de **pistes** (idées de formes, de couleurs, de
composition) ; les sprites du jeu restent dessinés par le pipeline, pour l'animation, la netteté à toute taille et la
cohérence. Les images retenues vont dans `reference/v2/`.

Les pistes A et B ont été générées le 10 novembre 2026 (`reference/v2/chat_gpt/`) ; ce qu'on en retient est noté
au lot 1.

**Piste A — la scène du témoin, finie par un illustrateur.** Joindre `reference/v2/temoin_niche.png` et
`reference/alice_tecky.png`.

> Voici une capture d'un jeu vidéo 2D vu de dessus, pour des enfants de 3 à 7 ans, et la planche de ses deux héros.
> Redessine exactement cette scène, comme l'illustrateur d'un jeu vendu sur console la finirait : même cadrage 16:9,
> mêmes éléments aux mêmes endroits (niche rouge, teckel, chemin de terre, mare avec une cane et ses canetons,
> arbres, fourrés en bordure). Style imposé : dessin vectoriel en aplats de couleurs, contour brun foncé régulier
> autour des personnages, ni texture d'aquarelle, ni 3D, ni pixel art, ni texte, ni interface. Lumière de fin de
> matinée venue d'en haut à gauche, ombres portées vers le bas à droite. Le chien reste un teckel roux à poil ras :
> corps très long, pattes très courtes, harnais rouge. Je cherche des idées pour la variété des arbres, la matière
> de l'herbe et du chemin, la profondeur de l'eau et la niche.

**Piste B — la planche de Tecky.** Joindre `reference/alice_tecky.png` et `reference/v2/tecky_v2.png`.

> Planche de personnage pour un jeu vidéo 2D : le teckel de la première image, dans le style de la seconde (dessin
> vectoriel en aplats, contour brun foncé régulier). Proportions mignonnes, tête un peu grosse, mais corps très long
> et pattes très courtes ; harnais rouge avec un anneau doré sur le dos. Sur fond blanc, à la même taille, alignés
> sur une ligne de sol : profil vers la droite, face, dos, trois quarts. En dessous, six expressions de la tête :
> content, inquiet, fier, surpris, endormi, en train d'aboyer. Ni texte, ni ombre, ni décor.

**Piste D — une planche par chien** (proposée le 11 novembre 2026, pas encore générée). Joindre la « Planche
d'expressions d'un teckel cartoon » et lancer le prompt une fois par chien :

> Dans exactement le même style que la planche jointe (aplats de couleur, contour brun épais, grands yeux, grosses
> pattes rondes), dessine un autre chien pour le même jeu vidéo : [CHIEN]. Trois vues alignées sur une ligne de sol,
> fond blanc : profil tourné vers la droite, face, dos. Il porte un collier noir à clous argentés. Air grognon mais
> mignon, pas effrayant.

Les chiens : un petit roquet blanc à taches fauves, oreilles pointues dressées, queue fine relevée ; un bouledogue
gris, trapu, face plate, bajoues claires, deux petits crocs qui dépassent, queue en moignon ; un doberman, grand,
noir et feu, oreilles droites en pointe, long museau, longues pattes ; un border collie noir et blanc, liste
blanche sur le front, poitrail blanc, queue touffue à bout blanc.

**Piste C — l'illustration de la vignette** (lot 8) : à écrire quand les héros de la v2 existent.
