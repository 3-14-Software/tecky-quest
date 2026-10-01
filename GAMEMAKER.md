# Tecky Quest — graphismes pour GameMaker Studio 2

> **Kit en pause.** Le développement avance sur la version web. `python3 build.py` produit toujours tout ce qui est
> décrit ici, mais les dernières nouveautés du jeu web (fermier et quête des poules, écureuils et chats, terriers,
> flair, os dorés, carte de la pause, ambiances par zone) n'y sont pas encore décrites.

Style aplats + contour, vue de dessus 3/4. Tout est généré par code :
`python3 build.py` reconstruit l'ensemble en quelques secondes
(dépendances : `pip install cairosvg pillow numpy` ; la police Fredoka est fournie dans `fonts/`).

- `out/sample_map.png` : tout le décor assemblé (campagne, étang, route, village, zone industrielle).
- `out/hud_mockup.png` : un écran de jeu complet en 1920×1080 avec le HUD.

## Contenu

| Dossier | Taille | Usage |
|---|---|---|
| `out/x2/` | personnages 96×96, tuiles et petits objets 64×64 | **conseillé** : caméra 960×540 en fenêtre 1920×1080, GUI 1920×1080 |
| `out/x1/` | personnages 48×48, tuiles 32×32 | caméra 480×270 |
| `out/previews/` | GIF d'aperçu + légende numérotée du tileset | — |

Les valeurs ci-dessous sont données **en x2** (divise par 2 pour x1).

---

## Personnages

Nom : `spr_<perso>_<anim>_<dir>`, avec `<dir>` = `down`, `up`, `left`, `right`.
**Origine de tous les personnages : (48, 88)**, sous les pieds, au centre.
**Masque de collision** conseillé : rectangle bas (≈ 50 × 20 px) autour des pattes,
pour que les personnages passent « devant » ou « derrière » le décor.

### Tecky (`tecky/`) et chiens ennemis (`enemies/`)
Mêmes animations pour Tecky (`spr_tecky_…`) et les trois ennemis :

| Ennemi | Sprite | Suggestion de gameplay |
|---|---|---|
| Roquet (petit, blanc tacheté) | `spr_roquet_…` | rapide, 1 PV, aboie de loin |
| Bouledogue (gris, trapu) | `spr_bouledogue_…` | lent, 3 PV, mord fort |
| Molosse (doberman noir et feu) | `spr_molosse_…` | mini-boss, 5 PV, insensible aux aboiements : il faut le mordre |
| Berger (border collie noir et blanc) | `spr_berger_…` | garde la ferme, 3 PV : s'accroupit (« ! », sprite écrasé verticalement), charge en ligne droite, puis souffle 1 s |

| Anim | Images | FPS | Remarque |
|---|---|---|---|
| idle | 4 | 6 | respiration, queue, clignement |
| walk | 6 | 12 | |
| bark | 4 | 10 | à combiner avec `spr_fx_bark` |
| bite | 5 | 14 | élan + fermeture de la gueule |
| hurt | 2 | 10 | image 1 en flash blanc |
| dig  | 6 | 14 | **Tecky seulement** : gratter le sol (à boucler ~1 s, avec `spr_fx_dirt`) |
| ko   | 4 | 6 | `right` et `left` seulement ; rester sur la dernière image |

### Poules (`hens/`) — rousse `spr_hen_…` et blanche `spr_hen_white_…`
Vues `_right` et `_left` (miroir). **Origine : (32, 56)**, sous les pattes. Pas de collision : elles s'écartent.

| Anim | Images | FPS | Remarque |
|---|---|---|---|
| idle | 4 | 4 | petits mouvements de tête |
| peck | 7 | 10 | picore (le cou plonge jusqu'au sol), une fois puis retour à idle |
| walk | 4 | 10 | quelques pas autour de sa place, en hochant la tête |
| flap | 4 | 14 | fuite en battant des ailes (aboiement de Tecky dans le cône, ou Tecky trop près) |

### Véhicules (`vehicles/`) — `spr_car_red_…` (et `_blue`, `_yellow`, `_green`), `spr_van_…`, `spr_bus_…`
Vues `_right` et `_left` (miroir), 4 images (les enjoliveurs tournent : vitesse d'image proportionnelle à la vitesse).

| Sprite | Taille x2 | Origine x2 | Suggestion de gameplay |
|---|---|---|---|
| `spr_car_<couleur>` | 128×80 | (64, 77) | rapide (~215 px/s) |
| `spr_van` (camionnette de boulangerie) | 160×96 | (80, 89) | ~185 px/s |
| `spr_bus` | 256×112 | (128, 105) | lent (~140 px/s) |

Circulation à droite sur la route horizontale. Un véhicule qui touche Tecky le projette sur le bas-côté, sans
dégâts (il klaxonne avant) ; aux passages piétons, les véhicules s'arrêtent toujours pour Tecky.

### Papillons (`butterflies/`) — `spr_butterfly_yellow` / `_blue` / `_pink` / `_orange`
Vus de dessus, tête vers le haut : à tourner dans le sens du vol (`image_angle = direction - 90`). **Origine : (24, 24)**,
au centre. 4 images : ailes ouvertes, mi-closes, presque fermées, mi-closes (environ 14 FPS en vol, 3 FPS posé).
Dans le jeu web, ils volettent en zigzag à environ 36 px du sol (petite ombre en dessous, à 80 % de leur taille),
surtout au parc mais aussi près de la niche, au village, à la ferme et dans la clairière ; ils se posent sur les
fleurs, et s'envolent quand Tecky s'approche ou aboie.

### Alice (`alice/`)
| Anim | Images | FPS | Remarque |
|---|---|---|---|
| idle | 4 | 6 | |
| walk | 6 | 10 | |
| happy | 4 | 8 | saut de joie, pour la fin (retrouvailles avec Tecky) |

---

## Objets et effets

### Objets (`items/`) — 6 images, 8 FPS, origine (32, 32)
| Sprite | Effet proposé |
|---|---|
| `spr_item_bone` | rend 1 os perdu (sans dépasser le maximum) |
| `spr_item_sausage` | +1 os au maximum (le nouvel os est plein), jusqu'à 8 |
| `spr_item_medal` | score +100 |
| `spr_item_squeaky` (canard pouic-pouic) | score +50 |
| `spr_item_ball` | score +20 |
| `spr_item_hairclip` (barrette) | indice 1 : semé par Alice à la ferme |
| `spr_item_shoe` (chaussure) | indice 2 : dans la forêt |
| `spr_item_plush` (doudou lapin) | indice 3 : au parc ; avec les trois, Alice sort de sa cachette |

### Effets (`fx/`) — origine au centre, sauf `spr_fx_bark` : (12, 48)
| Sprite | Images | FPS |
|---|---|---|
| `spr_fx_bark` | 4 | 12 — orienté vers la droite, tourner avec `image_angle` |
| `spr_fx_bite` | 4 | 14 |
| `spr_fx_hit` | 4 | 14 |
| `spr_fx_heal` | 5 | 10 |
| `spr_fx_pickup` | 5 | 14 |
| `spr_fx_dirt` | 5 | 14 — mottes de terre projetées quand Tecky gratte (origine en bas au centre : (32, 56)) |
| `spr_fx_ripple` | 8 | 3 — petit arc qui naît, s'étire et s'efface : à semer avec parcimonie sur l'eau profonde, loin des berges (le jeu web en met une par tuile d'eau, un cycle de 2,4 s sur deux, à un endroit qui change à chaque cycle) |
| `spr_fx_glint` | 8 | 8 — mini-étoile qui scintille : en plus des vaguelettes, avec sa propre cadence (le jeu web : une par tuile, cycle de 2,8 s, 4 cycles sur 10, éclat d'environ 1 s au milieu du cycle) |
| `spr_fx_heart` | 6 | 10 — petit cœur qui gonfle, monte et s'efface : au-dessus d'un chien qui veut jouer (mode balade) |
| `spr_fx_leaf` | 4 | 0 — feuille qui tombe (16×16 en x1) : une image par couleur (vert, vert tendre, jaune, orange), `image_speed = 0` ; la faire tourner (`image_angle`) et basculer (`image_yscale`) en descendant |

---

## Décor

### Sol : tileset `tiles/ts_ground.png` (tuiles 64×64, 16 colonnes × 16 lignes)
Crée un *Tile Set* avec cette image (tuiles 64×64, sans marge). La tuile 0 est vide, comme
GameMaker l'exige. La planche numérotée est dans `previews/ts_ground_legend.png`.

| Ligne | Index | Contenu |
|---|---|---|
| 0 | 1–4 | herbe : unie, brins, fleurs, cailloux |
| 0 | 5–8 | route pleine avec marquage : ligne médiane H, ligne V, passage piéton (route H), passage piéton (route V) |
| 0 | 9–15 | variantes pleines : terre ×2, route ×2, pavés, béton ×2 |
| 1 | 16–31 | chemin de terre / herbe |
| 2 | 32–47 | route / herbe (bordure de trottoir) |
| 3 | 48–63 | pavés / herbe |
| 4 | 64–79 | béton / herbe |
| 5 | 80–95 | trottoir / herbe |
| 6 | 96–111 | route / trottoir |
| 7 | 112–127 | eau / herbe (avec berge sableuse) |
| 8 | 128–143 | pavés / trottoir |
| 9 | 144–159 | route / chemin de terre |
| 10 | 160–175 | route / béton |
| 11 | 176–191 | béton / trottoir |
| 12 | 192–207 | champ labouré / herbe (sillons et jeunes pousses) |
| 13 | 208–223 | sous-bois / herbe (herbe sombre, aiguilles de pin) |
| 14 | 224–239 | chemin de terre / sous-bois |
| 15 | 240–255 | **détails transparents** (à poser sur un 2e calque de tuiles) |

**Transitions** : dans chaque ligne de paire, la colonne indique les coins recouverts par le
terrain « du dessus » : **haut-gauche = 1, haut-droite = 2, bas-gauche = 4, bas-droite = 8**.
Exemples : 15 = tout recouvert, 3 = moitié haute, 1 = coin haut-gauche arrondi.

**Détails** (ligne 15, dans l'ordre) : ligne d'arrêt H, ligne d'arrêt V, flèche au sol,
plaque d'égout, grille d'évacuation, flaque, tache d'huile, fissures, feuilles mortes, fleurs,
touffe d'herbe, cailloux, ligne de parking, bande de danger jaune et noire, traces de pattes,
trou creusé (pour un trésor enterré). Les tuiles peuvent être tournées ou retournées dans
l'éditeur de room.

#### Génération automatique du sol
Tu peux peindre à la main, ou générer le sol par code à partir d'une grille de coins
(un coin = un terrain). La fonction choisit toute seule la bonne tuile et la bonne paire :

```gml
// Terrains, du plus bas au plus haut (l'ordre compte : le plus haut passe dessus)
enum TER { herbe, foret, champ, terre, eau, trottoir, beton, paves, route }

/// Ligne du tileset pour la paire (dessus, dessous), ou -1 si elle n'existe pas
function ground_pair_row(_up, _lo) {
    static _rows = undefined;
    if (_rows == undefined) {
        _rows = array_create(9 * 9, -1);
        var _p = [[TER.terre, TER.herbe], [TER.route, TER.herbe], [TER.paves, TER.herbe],
                  [TER.beton, TER.herbe], [TER.trottoir, TER.herbe], [TER.route, TER.trottoir],
                  [TER.eau, TER.herbe], [TER.paves, TER.trottoir], [TER.route, TER.terre],
                  [TER.route, TER.beton], [TER.beton, TER.trottoir], [TER.champ, TER.herbe],
                  [TER.foret, TER.herbe], [TER.terre, TER.foret]];
        for (var _i = 0; _i < array_length(_p); _i++) _rows[_p[_i][0] * 9 + _p[_i][1]] = _i + 1;
    }
    return _rows[_up * 9 + _lo];
}

/// @param _tm       tilemap (ex. layer_tilemap_get_id(layer_get_id("Sol")))
/// @param _corners  ds_grid de (largeur+1) x (hauteur+1) coins, valeurs TER.*
function ground_autotile(_tm, _corners) {
    var _w = ds_grid_width(_corners) - 1;
    var _h = ds_grid_height(_corners) - 1;
    for (var _y = 0; _y < _h; _y++) {
        for (var _x = 0; _x < _w; _x++) {
            var _k = [_corners[# _x, _y], _corners[# _x + 1, _y],
                      _corners[# _x, _y + 1], _corners[# _x + 1, _y + 1]];
            // terrain du dessus = le plus haut des 4 coins
            var _up = max(_k[0], _k[1], _k[2], _k[3]);
            if (_up == TER.herbe) { tilemap_set(_tm, choose(1, 1, 1, 2, 2, 3, 4), _x, _y); continue; }
            // terrain du dessous = le plus fréquent parmi les autres coins (à égalité, le plus bas)
            var _lo = -1, _best = 0;
            for (var _t = 0; _t < _up; _t++) {
                var _n = 0;
                for (var _i = 0; _i < 4; _i++) if (_k[_i] == _t) _n++;
                if (_n > _best) { _best = _n; _lo = _t; }
            }
            if (_lo == -1) _lo = TER.herbe;                       // tuile pleine
            var _row = ground_pair_row(_up, _lo);
            if (_row == -1) _row = ground_pair_row(_up, TER.herbe);
            var _bits = 0;
            for (var _i = 0; _i < 4; _i++) if (_k[_i] == _up) _bits |= (1 << _i);
            tilemap_set(_tm, _row * 16 + _bits, _x, _y);
        }
    }
}
```

**Limites** : une tuile ne montre que deux terrains. Là où trois terrains se touchent
(un chemin qui rejoint une route à travers l'herbe, par exemple), le rendu est approximatif ;
laisse plutôt une rangée d'herbe ou de trottoir entre eux, comme sur la carte d'exemple.
Les paires absentes (eau / route…) retombent sur « terrain / herbe ».

### Objets de décor (`decor/`) — une image chacun
Ce sont des sprites à poser comme instances (triées avec `depth = -y`), pas des tuiles.
L'origine est au pied de l'objet.

| Sprite | Taille | Origine |
|---|---|---|
| `spr_decor_tree` | 128×128 | (64, 116) |
| `spr_decor_bush` | 64×64 | (32, 56) |
| `spr_decor_hay` (botte de foin) | 64×64 | (32, 56) |
| `spr_decor_rock` | 64×64 | (32, 54) |
| `spr_decor_fence_wood_h` / `_v` | 64×64 | (0, 56) / (32, 64) |
| `spr_decor_signpost` | 64×96 | (32, 90) |
| `spr_decor_cone` | 64×64 | (32, 56) |
| `spr_decor_road_sign` (attention chiens) | 64×96 | (32, 90) |
| `spr_decor_lamppost` | 64×128 | (32, 122) |
| `spr_decor_house_red` / `house_blue` | 192×192 | (96, 184) |
| `spr_decor_doghouse` (niche de Tecky) | 96×96 | (48, 88) |
| `spr_decor_bench` | 96×64 | (48, 56) |
| `spr_decor_mailbox` | 64×64 | (32, 58) |
| `spr_decor_hedge` | 64×64 | (0, 56) |
| `spr_decor_flower_pot` | 64×64 | (32, 56) |
| `spr_decor_warehouse` | 256×192 | (128, 184) |
| `spr_decor_container` | 192×96 | (96, 88) |
| `spr_decor_pallet` | 64×64 | (32, 54) |
| `spr_decor_barrel_blue` / `barrel_red` | 64×64 | (32, 58) |
| `spr_decor_crate` | 64×64 | (32, 56) |
| `spr_decor_fence_metal_h` / `_v` | 64×64 | (0, 56) / (32, 64) |
| `spr_decor_barn` (grange) | 256×224 | (128, 216) |
| `spr_decor_chicken_coop` (poulailler) | 128×128 | (64, 120) |
| `spr_decor_tractor` | 128×96 | (64, 88) |
| `spr_decor_scarecrow` (épouvantail) | 64×128 | (32, 120) |
| `spr_decor_bridge` (pont, **à plat**) | 192×320 | (96, 320) |
| `spr_decor_reeds` (roseaux) | 64×64 | (32, 56) |
| `spr_decor_boat` (barque) | 128×64 | (64, 52) |
| `spr_decor_fir` (sapin) | 128×160 | (64, 152) |
| `spr_decor_stump` (souche) | 64×64 | (32, 54) |
| `spr_decor_log` (tronc couché) | 128×64 | (64, 54) |
| `spr_decor_mushrooms` / `fern` (champignons / fougère, traversables) | 64×64 | (32, 56) |
| `spr_decor_slide` / `swing` (toboggan / balançoire) | 128×128 | (64, 120) |
| `spr_decor_sandbox` (bac à sable, **à plat**) | 128×96 | (64, 88) |
| `spr_decor_fountain_strip8` (fontaine **animée** : jet, gouttes, ronds dans le bassin ; 10 FPS) | 128×128 | (64, 116) |
| `spr_decor_playhouse` (cabane de jeu, cachette d'Alice) | 128×128 | (64, 120) |

Les clôtures et la haie `_h` se répètent tous les 64 px ; les `_v` se posent en colonne.
Les décors **à plat** (pont, bac à sable) se dessinent sous les personnages : profondeur fixe, pas `depth = -y`.
Le pont enjambe une rivière de 4 tuiles (256 px) : son tablier (x de −64 à +64 autour de l'origine) doit être
praticable, ses garde-corps (de ±64 à ±80) bloquent.

---

## HUD (`hud/`)

Pensé pour l'event **Draw GUI** avec `display_set_gui_size(1920, 1080)` et les sprites **x2**
(avec x1, utilise une GUI de 960×540). Voir `out/hud_mockup.png`.

| Sprite | Images | Origine | Usage |
|---|---|---|---|
| `spr_hud_bone` | 3 | (0, 0) | os de vie : 0 plein, 1 moitié, 2 vide |
| `spr_hud_portrait_tecky` | 4 | (0, 0) | normal, clignement, aboie, KO |
| `spr_hud_portrait_alice` | 3 | (0, 0) | normal, clignement, joyeuse (dialogues) |
| `spr_hud_panel` | 1 | (0, 0) | boîte claire **9-slice** (dialogues, menus) |
| `spr_hud_panel_dark` | 1 | (0, 0) | fond sombre translucide **9-slice** (vie, score) |
| `spr_hud_name_tag` | 1 | (0, 0) | étiquette rouge pour le nom de celui qui parle |
| `spr_hud_next` | 4 | (0, 0) | flèche « suite » qui rebondit |
| `spr_hud_digits` | 16 | (0, 0) | police en sprite : `0123456789+-x/:%` |
| `spr_hud_key` | 11 | (0, 0) | touches : X, C, E, Z, ↑, ↓, ←, →, Esc, Entrée, R |
| `spr_hud_pad` | 5 | (0, 0) | boutons de manette, même cadre que les touches : A, B, X, Y, Start |
| `spr_hud_action` | 12 | (0, 0) | boutons : aboyer, aboyer grisé, mordre, mordre grisé, gratter, gratter grisé, lire, lire grisé, jouer (cœur, mode balade), jouer grisé, flairer, flairer grisé |
| `spr_hud_cooldown` | 8 | (0, 0) | voile de recharge à poser sur un bouton (0 = vient d'être utilisé) |
| `spr_hud_enemy_bar_bg` / `_fill` | 1 | (28, 0) / (0, 0) | barre de vie au-dessus d'un ennemi |
| `spr_hud_arrow` | 4 | centre (40, 40) | flèche au bord de l'écran (pointe à droite, pastille vide) : seule elle tourne |
| `spr_hud_arrow_icon` | 4 | centre (22, 22) | contenu de la pastille, toujours droit : barrette, chaussure, doudou, tête d'Alice |
| `spr_title_logo` | 1 | centre | logo « Tecky Quest » pour l'écran titre |

**9-slice** : dans l'éditeur de sprite, active *Nine Slice* avec 32 px de chaque côté (16 en x1),
puis dessine-les à n'importe quelle taille avec `draw_sprite_stretched`.
Pour la barre ennemie, mets l'origine de `_bg` à (28, 0), au milieu en haut, pour la centrer
sur le chien ; `_fill` est dessinée avec `draw_sprite_part`, qui ignore l'origine.

**Texte des dialogues** : installe `fonts/Fredoka.ttf` sur ton système, puis crée dans GameMaker
une police `fnt_dialog` (Fredoka, graisse Medium, taille 32–38 pour une GUI 1920×1080).

### Exemple — `obj_hud` (objet persistant)

**Create**
```gml
display_set_gui_size(1920, 1080);
global.hp_max = 6;     // 3 os au départ (2 PV par os) ; +2 par saucisse, jusqu'à 16 (8 os)
global.hp = global.hp_max;
global.points = 0;
fnt_digits = font_add_sprite_ext(spr_hud_digits, "0123456789+-x/:%", true, 2);
dialog_text = "";      // texte affiché ; "" = pas de dialogue
dialog_name = "Alice";
dialog_face = 2;       // image de spr_hud_portrait_alice
```

**Draw GUI**
```gml
// --- vie
draw_sprite_stretched(spr_hud_panel_dark, 0, 24, 24, 174 + global.hp_max / 2 * 64, 132);
var _face = (global.hp <= 0) ? 3 : (obj_tecky.state == "bark") ? 2 : 0;
draw_sprite(spr_hud_portrait_tecky, _face, 36, 42);
for (var i = 0; i < global.hp_max / 2; i++) {          // 1 os = 2 PV
    var _f = (global.hp >= (i + 1) * 2) ? 0 : (global.hp == i * 2 + 1) ? 1 : 2;
    draw_sprite(spr_hud_bone, _f, 150 + i * 64, 58);
}

// --- score
draw_sprite_stretched(spr_hud_panel_dark, 0, 1566, 24, 330, 104);
draw_sprite_ext(spr_item_medal, 0, 1616, 76, 1, 1, 0, c_white, 1);
draw_set_font(fnt_digits);
draw_text(1666, 36, string_replace_all(string_format(global.points, 5, 0), " ", "0"));

// --- actions + recharge (bite_cd : temps restant, bite_cd_max : durée totale, en étapes)
draw_sprite(spr_hud_action, 0, 1690, 890);
draw_sprite(spr_hud_key, 0, 1690, 976);
draw_sprite(spr_hud_action, 2, 1800, 890);
if (obj_tecky.bite_cd > 0) {
    var _f = floor((1 - obj_tecky.bite_cd / obj_tecky.bite_cd_max) * 8);
    draw_sprite(spr_hud_cooldown, _f, 1800, 890);
}
draw_sprite(spr_hud_key, 1, 1800, 976);

// --- dialogue
if (dialog_text != "") {
    draw_sprite_stretched(spr_hud_panel, 0, 330, 840, 1160, 210);
    draw_sprite(spr_hud_portrait_alice, dialog_face, 364, 898);
    draw_sprite(spr_hud_name_tag, 0, 480, 824);
    draw_set_font(fnt_dialog);
    draw_set_halign(fa_center); draw_set_colour(c_white);
    draw_text(544, 830, dialog_name);
    draw_set_halign(fa_left); draw_set_colour(make_colour_rgb(58, 30, 18));
    draw_text_ext(480, 884, dialog_text, 52, 960);
    draw_sprite(spr_hud_next, current_time div 120, 1426, 990);
}

// --- flèche vers la cible (prochain indice, puis Alice) si elle est hors de l'écran, pendant arrow_time
// (quelques secondes après chaque indice, pas en permanence). _target : instance visée, _icon : 0..2 indice, 3 Alice.
var _cam = view_camera[0];
var _cx = camera_get_view_x(_cam), _cy = camera_get_view_y(_cam);
var _cw = camera_get_view_width(_cam), _ch = camera_get_view_height(_cam);
if (arrow_time > 0) with (_target) {
    if (x < _cx || x > _cx + _cw || y < _cy || y > _cy + _ch) {
        var _k = 1920 / _cw;                              // monde -> GUI
        var _ax = clamp((x - _cx) * _k, 80, 1840);
        var _ay = clamp((y - _cy) * _k, 300, 1000);
        var _dir = point_direction(960, 540, (x - _cx) * _k, (y - _cy) * _k);
        var _a = min(1, other.arrow_time);                // fondu sur la dernière seconde
        draw_sprite_ext(spr_hud_arrow, current_time div 150, _ax, _ay, 1, 1, _dir, c_white, _a);
        // l'icône ne tourne pas : centre de la pastille, 6 px derrière le centre de rotation
        draw_sprite_ext(spr_hud_arrow_icon, _icon, _ax - lengthdir_x(6, _dir), _ay - lengthdir_y(6, _dir),
                        1, 1, 0, c_white, _a);
    }
}
```

**Barre de vie d'un ennemi** (event *Draw* de l'ennemi, après `draw_self()`) :
```gml
if (hp < hp_max) {
    draw_sprite(spr_hud_enemy_bar_bg, 0, x, y - 110);
    draw_sprite_part(spr_hud_enemy_bar_fill, 0, 0, 0, 48 * hp / hp_max, 8, x - 24, y - 106);
}
```

---

## Musique (`out/audio/`)

`music_tecky.wav` : « Promenade de Tecky », morceau chiptune original (140 BPM, 55 s, 4 parties A-B-C-A') qui boucle
sans coupure. Importe-le comme *Sound* (type *Music*, compressé), puis :

```gml
audio_play_sound(snd_music_tecky, 10, true);   // true = en boucle
audio_sound_gain(snd_music_tecky, 0.65, 0);     // thème discret : la fanfare et les bruitages passent devant
```

`music_victoire.wav` : fanfare de victoire (3 mesures, environ 7 s : une montée qui finit sur l'accord final). Elle ne boucle pas :
à jouer une seule fois quand Tecky retrouve Alice, en coupant la musique de fond.

```gml
audio_stop_sound(snd_music_tecky);
audio_play_sound(snd_music_victoire, 10, false);
```

`music_defaite.wav` : musique de défaite, même durée que la fanfare (3 mesures à 140 BPM, environ 7 s), en la mineur :
une mélodie qui descend doucement et se pose sur un accord tenu. À jouer une seule fois quand Tecky n'a plus de vie.

```gml
audio_stop_sound(snd_music_tecky);
audio_play_sound(snd_music_defaite, 10, false);
```

La partition est dans `music.py` (mélodie, accords, batterie ; `fanfare_events()` pour la victoire, `defeat_events()` pour la défaite) : modifie-la puis relance
`python3 music.py` pour regénérer les WAV. Le jeu web joue exactement la même partition.

## Ambiance, modes et options (version web)

Ces fonctions de la version web n'ont pas besoin de nouveaux assets (ou seulement ceux listés plus haut) ; voici
comment les retrouver dans GameMaker. Les réglages exacts sont dans `web_src/game.js` (`SUN`, `DUST`, `LEAF`,
`CLOUD`, `PLAY`, `PAD_MAP`).

- **Coucher de soleil** : un cran de lumière par indice (plein jour, après-midi, fin d'après-midi, soleil couchant),
  plus chaud encore aux retrouvailles. Une teinte multipliée sur la vue, après le monde et avant la GUI :
  ```gml
  gpu_set_blendmode_ext(bm_dest_colour, bm_zero);   // multiplication
  draw_rectangle_colour(cam_x, cam_y, cam_x + 960, cam_y + 540, teinte, teinte, teinte, teinte, false);
  gpu_set_blendmode(bm_normal);
  ```
  Teintes du jeu web : `#FFFFFF`, `#FFF1DC`, `#FFDEB6`, `#EEB496`, puis `#FFC8A0` aux retrouvailles. Les lampadaires
  s'allument à partir du deuxième indice (halo additif autour de la lanterne, 93 px au-dessus de l'origine en x2).
- **Poussière** : petits disques crème (`#F1E7D0`) semés derrière Tecky toutes les 0,12 s quand il avance, qui
  grossissent et s'effacent en 0,45 s (un *particle system* fait très bien l'affaire).
- **Feuilles** : chaque arbre ou sapin visible lâche de temps en temps une `spr_fx_leaf` (aiguilles vertes pour les
  sapins) qui tombe en se balançant avec une petite ombre, se pose, puis s'efface.
- **Ombres de nuages** : quelques grandes taches floues très transparentes (10 %) qui glissent lentement sur la carte.
- **Mode balade** : personne ne se fait mal. Les chiens ne mordent, n'aboient ni ne chargent : ils viennent attendre
  près de Tecky en sautillant (8 s, puis ils rentrent). Près d'un chien, le bouton de morsure devient « Jouer »
  (`spr_hud_action` 8) : Tecky et le chien sautillent 2,2 s en semant des `spr_fx_heart`, et le chien devient un copain
  (ses points, « Copains de jeu » à la fin) qui ne le poursuit plus mais lui fait la fête. L'aboiement ne blesse
  personne : il appelle les chiens, qui accourent pour jouer.
- **Sauvegarde et records** : la version web enregistre position, vie, score, temps, indices, trésors, objets au sol et
  chiens restants (toutes les 4 s hors de danger, à chaque indice ou trésor, en quittant la page), et garde le meilleur
  score et le meilleur temps de chaque mode. En GML : `json_stringify` d'une struct, écrite avec `file_text_write_string`.
- **Manette** : A mord (ou gratte, ou lit) et valide, X ou B aboie, Y lit, Start met en pause, Select coupe le son :
  ```gml
  gamepad_set_axis_deadzone(0, 0.25);
  var mx = gamepad_axis_value(0, gp_axislh), my = gamepad_axis_value(0, gp_axislv);
  if (gamepad_button_check_pressed(0, gp_face1)) { /* mordre */ }
  if (gamepad_button_check_pressed(0, gp_face3) || gamepad_button_check_pressed(0, gp_face2)) { /* aboyer */ }
  ```

## Import dans GameMaker

1. Glisse les PNG d'un dossier dans l'*Asset Browser* : chaque fichier devient un sprite,
   et le suffixe `_stripN` le découpe en N images automatiquement.
2. Règle l'origine et la vitesse (FPS) selon les tableaux ci-dessus. Astuce : sélectionne
   plusieurs sprites d'un même dossier pour leur appliquer la même origine.

## Exemple de code — `obj_tecky`

**Create**
```gml
spd = 2;
dir = "down";
state = "idle";
```

**Step**
```gml
var h = keyboard_check(vk_right) - keyboard_check(vk_left);
var v = keyboard_check(vk_down)  - keyboard_check(vk_up);

if (state == "idle" || state == "walk") {
    if (h != 0 || v != 0) {
        var len = point_distance(0, 0, h, v);
        x += h / len * spd;
        y += v / len * spd;
        if (abs(h) >= abs(v)) dir = (h > 0) ? "right" : "left";
        else                  dir = (v > 0) ? "down"  : "up";
        state = "walk";
    } else {
        state = "idle";
    }

    if (keyboard_check_pressed(ord("X"))) {          // aboiement
        state = "bark";
        var fx = instance_create_depth(x, y - 40, depth - 1, obj_fx);
        fx.sprite_index = spr_fx_bark;
        fx.image_angle = (dir == "right") ? 0 : (dir == "up") ? 90 : (dir == "left") ? 180 : 270;
    }
    if (keyboard_check_pressed(ord("C"))) {
        // C fait gratter près d'un trésor (obj_dig), lire près d'un panneau (obj_sign), sinon mordre ;
        // mordre d'abord si un chien (obj_dog, parent de tous les chiens) est tout près.
        // Le bouton suit la même règle : image 2 (mordre), 4 (gratter) ou 6 (lire) de spr_hud_action.
        var _spot = instance_nearest(x, y, obj_dig);
        var _sign = instance_nearest(x, y, obj_sign);
        var _dog = instance_nearest(x, y, obj_dog);
        var _threat = _dog != noone && point_distance(x, y, _dog.x, _dog.y) < 240;
        if (!_threat && _spot != noone && !_spot.dug && point_distance(x, y, _spot.x, _spot.y) < 86) {
            state = "dig"; dig_timer = room_speed; dig_spot = _spot;
        } else if (!_threat && _sign != noone && point_distance(x, y, _sign.x, _sign.y) < 95) {
            obj_hud.dialog_text = _sign.text; obj_hud.dialog_name = "";
        } else state = "bite";
    }
}

if (state == "dig") {                                // gratter : ~1 s, de la terre vole
    dig_timer--;
    if (dig_timer mod 10 == 0)
        instance_create_depth(dig_spot.x, dig_spot.y, depth - 1, obj_fx, { sprite_index: spr_fx_dirt });
    if (dig_timer <= 0) { dig_spot.dug = true; global.points += 100; state = "idle"; }
}

var spr = asset_get_index("spr_tecky_" + state + "_" + dir);
if (sprite_index != spr) { sprite_index = spr; image_index = 0; }
depth = -y;   // tri par profondeur : ce qui est plus bas passe devant
```

**Animation End**
```gml
if (state == "bark" || state == "bite" || state == "hurt") state = "idle";
if (state == "ko") { image_index = image_number - 1; image_speed = 0; }
```

`obj_fx` : un objet sans sprite dont l'event *Animation End* contient `instance_destroy();`.
Pour `ko`, n'utilise que `right`/`left` (si le chien regardait vers le haut ou le bas,
choisis l'un des deux). Le même code marche pour un ennemi en remplaçant `"spr_tecky_"`
par `"spr_roquet_"`, etc., et les touches par une petite IA.

## Modifier les dessins

| Fichier | Contenu |
|---|---|
| `tecky.py` | Tecky : `PAL` (couleurs), `HARNESS`, une fonction par animation (une ligne de paramètres par image) |
| `enemies.py` | `DOGS` : gabarit, oreilles, museau, queue et couleurs de chaque ennemi ; ajouter une ligne = un nouveau chien |
| `alice.py` | Alice : `PAL`, animations |
| `items.py` | objets et effets |
| `tiles.py` | textures et couleurs des sols, disposition du tileset |
| `decor.py` | un dessin par objet de décor, registre `DECOR` |
| `sample_map.py` | la carte d'exemple |
| `music.py` | la musique (partition + rendu WAV) |
| `pack_web.py`, `web_src/` | la version web jouable (niveau, moteur, page) |
| `hud.py` | éléments du HUD, logo |
| `hud_mockup.py` | la maquette d'écran |
| `spritelib.py` | rendu SVG, contour, export des strips |
