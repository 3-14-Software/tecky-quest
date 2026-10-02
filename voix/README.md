# Voix des répliques

Toutes les répliques du jeu, à faire lire par une synthèse vocale (une voix par personnage), pour qu'Alice puisse
jouer sans savoir lire : les dialogues, et les petites bulles (exclamations des personnages quand Tecky arrive, de
Tecky quand il ramasse quelque chose, cris des animaux, annonces comme « But ! »). La liste est produite par le jeu
lui-même :

```bash
python3 pack_web.py && node tools/export_voix.js
```

- `repliques.csv` (séparateur `;`, UTF-8) : une ligne par fichier audio à générer.
  - **fichier** : le nom à donner au fichier audio ;
  - **personnage** ;
  - **type** : `dialogue` (dans le panneau de dialogue) ou `bulle` (petite bulle au-dessus de quelqu'un) ;
  - **appareil** : `clavier` ou `manette` pour les aides qui citent une touche ou un bouton (deux versions), vide
    sinon (les aides au toucher sont des répliques à part) ;
  - **ton** : `joyeux` ou `inquiet` quand le personnage l'est (d'après son portrait) ;
  - **texte à dire** : les touches y sont écrites en toutes lettres (« la touche C », « le bouton A ») ;
  - **contexte** : quand la réplique est dite.
- `repliques.json` : la même chose, avec la voix conseillée pour chaque personnage.

## Voix

| Personnage | Voix conseillée |
|---|---|
| Tecky | petit teckel joyeux, courageux et un peu espiègle |
| Alice | petite fille de 5 ans, enjouée |
| Narrateur | aides et panneaux : voix calme, claire et posée |
| Gaston | le fermier : jovial, voix grave et chaleureuse |
| Marcel | le facteur : enjoué, un peu pressé |
| Mamie Rose | la voisine : douce vieille dame |
| Léon | le cariste du port : sympathique, voix forte |
| Nestor | le vieux chien du gardien : voix lente, grave et bonhomme |
| Le doberman | gros chien bourru, voix grave |
| Les chiens du coin | chiens grognons (« Grrr… »), ou contents en balade (« Copain ! ») |
| Les chats | Pompon et les chats du coin : miaulements, feulements |
| Les écureuils | petite voix aiguë et rapide |
| Les canards | coin-coin |
| Titine | la petite locomotive du port : voix joyeuse et chantante |
| Maman Piquette | la maman hérisson de la forêt : douce, tendre, un peu inquiète |
| Les bébés hérissons | toute petite voix aiguë (« Couic ! ») |

## Fichiers audio

Un fichier par ligne, déposé dans ce dossier `voix/` sous le nom de la colonne **fichier** : `tecky-88f6c3c3.mp3`, par
exemple. MP3 de préférence (lu par tous les navigateurs, iPhone compris) ; WAV et OGG sont reconnus aussi.

Le nom d'un fichier vient du personnage et du texte à dire : si une réplique change, son nom change. Il suffit alors de
relancer l'export et de générer les nouveaux noms ; `node tools/export_voix.js` dit combien de répliques sont déjà
enregistrées et quels fichiers sont en trop (répliques modifiées ou retirées, à supprimer).
