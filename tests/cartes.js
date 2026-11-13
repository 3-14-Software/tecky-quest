// plusieurs cartes : Tecky prend le tunnel de la route, arrive sur la côte (cartes/cote.json), y marche, revient ; chaque carte
// garde son état ; une partie enregistrée là-bas reprend là-bas (sauvegarde v3 ; une v2 se reprend dans le monde).
// Se joue dans l'épisode de l'été, encore en chantier : c'est lui qui a la deuxième carte (au printemps, le tunnel
// est fermé : tests/episodes.js)
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  // (l'été part en voiture, et ses tunnels sont fermés à pied : tests/voyage.js ; ici, le moteur des passages à pied,
  // gardé pour d'autres cartes : on retire le voyage de l'épisode)
  run('delete EPISODES[1].voyage;');
  run('episode = "ete"; audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs.forEach(d => { d.x = d.hx; d.y = d.hy; }); cars = []; P.inv = 99;');
  ok(run('Object.keys(CARTES).join()') === 'monde,cote' && run('MAP.id') === 'monde' && run('MAP.ts') === 64 && run('MAP.w') === 96,
     'deux cartes ; la carte courante est celle du monde, et hérite des données du jeu (MAP.ts)');
  ok(run('JSON.stringify(MAP.passages)') === '[[1,"cote",0]]' && run('JSON.stringify(CARTES.cote.passages)') === '[[0,"monde",1]]',
     'le tunnel de l\'est du monde mène au tunnel de l\'ouest de la deuxième carte, et retour');
  // l'état du monde avant de partir : un os ramassé, un trésor déterré, un chien de moins, Pompon qui suit
  run('items.splice(0, 1); digs[2].dug = true; treasures = 1; dogs.splice(3, 1); rose.state = "asked"; pompon.mode = "follow"; pompon.x = 5000; pompon.y = 1500;');
  run('farm.state = "asked"; score = 321; var avant = JSON.stringify(mapState()), nItems = items.length, nDogs = dogs.length;');
  // le tunnel de l'ouest n'a pas de passage : Tecky dit que c'est pour les voitures
  run('var T0 = MAP.roadTunnels[0], T1 = MAP.roadTunnels[1]; P.x = T0[0] + 60; P.y = T0[1] - 100; P.mode = "free"; P.edgeAt = -99; pops = [];');
  step(60, 'held.left = true; cars = [];'); run('held.left = false;');
  ok(run('MAP.id') === 'monde' && run('pops.some(p => p.text === txt("bord.tunnel"))'), 'tunnel sans passage : « ' + run('txt("bord.tunnel")') + ' »');
  // celui de l'est mène ailleurs : Tecky pousse dedans
  // contre la butte, à côté de la route : rien ne se passe
  run('P.x = T1[0] - 60; P.y = T1[1] + 30; P.mode = "free"; pops = [];');
  step(60, 'held.right = true; cars = [];'); run('held.right = false;');
  ok(run('MAP.id') === 'monde' && run('pops.length') === 0, 'contre la butte du tunnel, hors de la route : on ne passe pas');
  run('P.x = T1[0] - 60; P.y = MAP.traffic.road[0] + 70; P.mode = "free"; pops = []; var yEntree = P.y - MAP.traffic.road[0];');
  step(45, 'held.right = true; if (MAP.id === "monde") cars = [];'); run('held.right = false;');
  ok(run('MAP.id') === 'cote' && run('state') === 'play' && run('MAP.w') === 96 && run('MAP.h') === 64, 'Tecky pousse dans le tunnel de l\'est : il est sur la côte (96 x 64)');
  ok(run('(() => { const [x, , d] = arrivalAt(0), [r0, r1] = MAP.traffic.road; return P.x - x >= 0 && P.x - x < 200 && P.y > r0 && P.y < r1 && d === "right"; })()') && run('!blockedFeet(P.x, P.y, 16)'),
     'il ressort sur la route, devant la bouche du tunnel de l\'ouest');
  ok(Math.abs(run('P.y - MAP.traffic.road[0]') - run('yEntree')) < 30, 'à la hauteur où il est entré : ' + Math.round(run('yEntree')) + ' px sous le bord de la chaussée, ' + Math.round(run('P.y - MAP.traffic.road[0]')) + ' à la sortie');
  ok(run('score') === 321 && run('farm.state') === 'asked' && run('treasures') === 1 && run('P.hp') > 0, 'la partie continue : score, quêtes et trésors le suivent');
  ok(run('dogs.length') === run('MAP.enemies.length') && run('dogs.length') > 3 && run('items.length') > 15 && run('npcList().map(n => n.look).join()') === 'anatole,zoe,hortense'
     && run('decor.length') > 150 && run('butterflies.length') === 7 && run('cars.length') === 3 && run('alice.hidden') && run('ici("alice")')
     && !run('ici("track")') && run('ici("traffic")'),
     'la côte a ses décors, ses chiens, ses objets, ses papillons et ses voitures, Alice dans sa cachette, Madame Hortense devant le casino, Anatole sur la falaise, Zoé sur la plage ; pas de voie ferrée');
  // la route sans issue : une voiture entre sous le porche du parking, s'y gare, repart par l'autre voie ; au tunnel, de même
  ok(run('MAP.traffic.end') === 30 * 64 && run('CARTES.monde.traffic.end') === null && run('MAP.decor.filter(d => d[0] === "porche").length') === 1
     && run('blockedFeet(MAP.traffic.end + 60, 8 * TS, 16)') && !run('blockedFeet(MAP.traffic.end - 60, 8 * TS, 16)'),
     'la route s\'arrête au porche du parking : Tecky n\'y entre pas');
  run('var pxA = P.x, pyA = P.y; P.x = 60 * TS; P.y = 30 * TS; dogs = [];');
  run('var V = cars[0]; cars = [V]; Object.assign(V, { lane: 1, dir: 1, y: MAP.traffic.lanes[1], hidden: 0, x: MAP.traffic.end - 100, v: V.T.spd });');
  step(120);
  ok(run('V.lane') === 0 && run('V.dir') === -1 && run('V.hidden') > 0 && run('V.x') > run('MAP.traffic.end + V.T.len / 2'), 'une voiture entre sous le porche : elle y disparaît et s\'y gare');
  run('V.hidden = 0.01;'); step(240);
  ok(run('V.hidden') <= 0 && run('V.x') < run('MAP.traffic.end - 200') && run('V.y') === run('MAP.traffic.lanes[0]'), 'puis elle repart vers le tunnel, par la voie du haut');
  run('V.x = -V.T.len;'); step(3);
  ok(run('V.lane') === 1 && run('V.hidden') > 0 && run('V.x') < 0, 'au tunnel, elle sort de la carte et fait demi-tour hors de vue');
  run('V.hidden = 0.01;'); step(150);
  ok(run('V.dir') === 1 && run('V.x') > 100 && run('V.y') === run('MAP.traffic.lanes[1]'), 'et revient par la voie du bas');
  run('P.x = pxA; P.y = pyA; cars = [];');     // (pour la suite : Tecky s'y promène sans qu'une voiture ni un chien s'en mêle)
  ok(run('ZONES.length') === 7 && run('ZONES[0].name') === 'Le port' && run('ZONES[6].name') === 'La Côte Fleurie'
     && run('EDGE_DECOR.filter(d => d.n === "tunnel").length') === 1
     && run('EDGE_DECOR.filter(d => d.n !== "tunnel").every(d => offMap(d.x, d.y - 12, d.x, d.y))'),
     'ses zones et sa lisière sont les siennes (' + run('EDGE_DECOR.length') + ' fourrés et arbres autour, un seul tunnel : la route finit au parking)');
  // la route s'arrête au parking : ses marquages aussi ; au bord est, à sa hauteur, pas de tunnel « pour les voitures »
  ok(run('MAP.ground[7 * MAP.w + 10]') === 5 && run('MAP.ground[7 * MAP.w + 28]') === 5 && run('MAP.ground[7 * MAP.w + 7]') === 7 && run('MAP.ground[7 * MAP.w + 34]') !== 5
     && run('MAP.ground[7 * MAP.w + 60]') !== 5 && run('MAP.edge.ring.filter(([x, y, v]) => v === 5).every(([x, y]) => x < 0 && y === 7)'),
     'les marquages de la route vont du tunnel au parking, pas plus loin ; un passage piéton devant le chemin du port');
  run('var px0 = P.x, py0 = P.y; P.x = MAP.w * TS - 40; P.y = 7.5 * TS; P.mode = "free"; P.edgeAt = -99; pops = [];');
  step(60, 'held.right = true;'); run('held.right = false;');
  ok(run('MAP.id') === 'cote' && run('pops.some(p => p.text === txt("bord.carte"))') && !run('pops.some(p => p.text === txt("bord.tunnel"))'),
     'au bord est, à la hauteur de la route : le bord de la carte, pas un tunnel');
  // les terrains de la côte : sable, planches, mer, et la falaise (plateau, paroi, escalier)
  ok(run('CARTES.monde.cliff.length') === 0 && run('CARTES.monde.plateau.length') === 0 && run('MAP.cliff.length') === run('(MAP.w + 1) * (MAP.h + 1)')
     && run('cliffAt(82 * TS, 39.5 * TS)') && run('blockedFeet(82 * TS, 39.5 * TS, 16)') && !run('cliffAt(82 * TS, 42 * TS)') && !run('blockedFeet(82 * TS, 42 * TS, 16)'),
     'la paroi de la falaise : on ne marche pas sur la roche ; à son pied, sur le sable, si');
  ok(!run('blockedFeet(87 * TS, 30 * TS, 16)') && run('rimAt(85 * TS, 8.5 * TS)') && run('blockedFeet(85 * TS, 8.5 * TS, 16)')
     && run('rimAt(75.5 * TS, 15 * TS)') && !run('rimAt(85 * TS, 7.8 * TS)'),
     'le plateau : on y marche, mais son bord (le liséré de pierres) ne se franchit pas');
  ok(!run('blockedFeet(83 * TS, 39.5 * TS, 16)') && !run('blockedFeet(83 * TS, 40.5 * TS, 16)') && !run('blockedFeet(83 * TS, 37.5 * TS, 16)')
     && !run('blockedFeet(84 * TS, 39.5 * TS, 16)') && run('blockedFeet(85 * TS, 39.5 * TS, 16)') && run('blockedFeet(82 * TS, 39.5 * TS, 16)'),
     'l\'escalier franchit la paroi : libre du pied jusqu\'au plateau, la roche de chaque côté');
  run('P.x = 83 * TS; P.y = 41.6 * TS; P.mode = "free";');
  step(150, 'held.up = true;'); run('held.up = false;');
  ok(run('P.y') < run('38.2 * TS') && run('Math.abs(P.x - 83 * TS) < 40') && run('cornerVal(MAP.plateau, P.x, P.y)') > 0.9,
     'Tecky monte l\'escalier depuis la plage et arrive sur le plateau (y = ' + (run('P.y') / 64).toFixed(1) + ')');
  run('P.x = 90.6 * TS; P.y = 38 * TS;');
  step(150, 'held.down = true;'); run('held.down = false;');
  ok(run('P.y') > run('40 * TS') && run('P.y') < run('41.6 * TS') && run('cornerVal(MAP.plateau, P.x, P.y)') > 0.5,
     'du plateau, il ne saute pas dans le vide : le bord l\'arrête (y = ' + (run('P.y') / 64).toFixed(1) + ')');
  run('P.x = 77 * TS; P.y = 26.4 * TS;');
  step(150, 'held.up = true;'); run('held.up = false;');
  ok(run('P.y') < run('22 * TS') && run('cornerVal(MAP.plateau, P.x, P.y)') > 0.9, 'l\'autre escalier, côté ville, y monte aussi (y = ' + (run('P.y') / 64).toFixed(1) + ')');
  run('P.x = px0; P.y = py0;');
  ok(!run('blockedFeet(30 * TS, 48 * TS, 16)') && !run('blockedFeet(30 * TS, 43 * TS, 16)') && run('waterAt(30 * TS, 56 * TS)')
     && !run('blockedFeet(48.5 * TS, 58 * TS, 16)') && run('blockedFeet(46.5 * TS, 58 * TS, 16)')
     && !run('blockedFeet(42 * TS, 27 * TS, 16)') && run('blockedFeet(42 * TS, 24 * TS, 16)'),
     'on marche sur le sable, sur les planches, sur la jetée et sur le pont, pas dans la mer ni dans la rivière');
  ok(run('MAP.decor.some(d => d[0] === "bridge_h")') && run('FLAT.has("bridge_h")') && run('blockedFeet(42 * TS, 25.95 * TS, 16)')
     && run('blockedFeet(42 * TS, 28.2 * TS, 16)') && !run('blockedFeet(39.2 * TS, 27 * TS, 16)') && !run('blockedFeet(45.8 * TS, 27 * TS, 16)'),
     'le pont en travers : à plat sous Tecky, ses garde-corps du nord et du sud l\'arrêtent, ses deux bouts sont ouverts');
  ok(run('waterAt(60 * TS, 60 * TS)') && run('waterAt(42 * TS, 12 * TS)') && run('waterAt(28 * TS, 30 * TS)'), 'la mer, la rivière et le bassin sont de l\'eau pour les collisions');
  ok(run('MAP.sheet') === 32 && run('MAP.ground.every(i => i >= 0)') && run('MAP.ground[48 * MAP.w + 30] >> 4') === 15 && run('!!MAP.tileAlt[16]'),
     'le sable plein a sa rangée dans le tileset, le bord de mer ses variantes froissées');
  // il y marche, le jeu se dessine, rien ne casse
  run('var x0 = P.x, y0 = P.y;');
  step(90, 'held.right = true;'); run('held.right = false;');
  step(60, 'held.down = true;'); run('held.down = false;');
  ok(run('P.x - x0') > 150 && run('P.y - y0') > 60 && run('ground.size') >= 1 && run('zone && zone.id') === 'cote', 'il y marche (' + Math.round(run('P.x - x0')) + ' px vers l\'est, puis vers le sud)');
  run('state = "pause"; openPauseMenu(); render(); state = "play"; menu = null;');
  ok(run('mapImg !== null') && run('seenCells.length') === run('cellsW() * cellsH()') && run('seenCells.some(v => v)'), 'la carte de la pause est celle de cette carte');
  run('var b0 = JSON.stringify(badges); seenCells.fill(1); checkBadges();');
  ok(run('JSON.stringify(badges)') === run('b0'), 'pas de badge gagné parce que la carte est vide (bêtes, canards, os dorés, explorateur)');
  ok(run('arrowTarget().n') === 'hat' && run('clueNames().join()') === 'hat,spade,flipflop', 'la flèche et le flair mènent au premier indice de l\'été : le chapeau de paille');
  // partie enregistrée là-bas : elle reprend là-bas
  run('P.x = 700; P.y = 1100; saveGame(); var S = STORE.get(SAVE_KEY), chatAvant = S.ailleurs.monde.cat.slice();');
  ok(run('S.v') === 3 && run('S.ep') === 'ete' && run('S.carte') === 'cote' && run('!!S.ailleurs.monde') && run('(() => { const m = S.ailleurs.monde, a = JSON.parse(avant); return m.items.length === nItems && JSON.stringify(m.dogs) === JSON.stringify(a.dogs) && JSON.stringify(m.dug) === JSON.stringify(a.dug); })()'),
     'sauvegarde v3 : la carte courante, et l\'état du monde rangé sous « ailleurs »');
  run('toTitle();');
  ok(run('MAP.id') === 'monde' && run('state') === 'title' && run('EDGE_DECOR.length') > 300, 'retour à l\'écran titre : la carte du monde, sur la place du village');
  run('loadGame(STORE.get(SAVE_KEY), false);'); advanceDialog();
  ok(run('episode') === 'ete' && run('MAP.id') === 'cote' && run('P.x') === 700 && run('P.y') === 1100 && run('score') === 321 && run('farm.state') === 'asked' && run('dogs.length') === 0,
     'Continuer : la partie reprend sur la côte, là où elle a été enregistrée');
  // retour par le tunnel : le monde est comme il l'avait laissé
  run('{ const [x, y] = arrivalAt(0); P.x = x - 10; P.y = y; P.mode = "free"; cars = []; }');
  step(45, 'held.left = true; if (MAP.id === "cote") cars = [];'); run('held.left = false;');
  ok(run('MAP.id') === 'monde' && run('P.x') > run('MAP.w * TS - 300') && run('P.dir') === 'left', 'il repasse le tunnel : de retour dans le monde, côté est');
  ok(run('items.length') === run('nItems') && run('dogs.length') === run('nDogs') && run('digs[2].dug') && run('digs.filter(g => g.dug).length') === 1
     && run('pompon.mode') === 'wait' && run('pompon.x') === run("chatAvant[0]") && run('npcList().length') === 6 && run('ZONES.length') === 8,
     'le monde est comme il l\'avait laissé : l\'os ramassé, le trésor déterré, le chien parti ; Pompon, qui le suivait, l\'a attendu');
  ok(run('Object.keys(elsewhere).join()') === 'cote' && run('elsewhere.cote.seen.includes("1")'), 'et la deuxième carte garde à son tour ce qu\'il y a vu');
  // une sauvegarde d'avant les cartes multiples (v2) se reprend dans le monde
  run('saveGame(); var V2 = STORE.get(SAVE_KEY); V2.v = 2; delete V2.ep; delete V2.carte; delete V2.ailleurs; STORE.set(SAVE_KEY, V2); toTitle();');
  ok(run('!!loadSave()') && run('menu.items[0].id') === 'continue', 'une sauvegarde v2 est encore proposée (« Continuer »)');
  run('loadGame(loadSave(), false);'); advanceDialog();
  ok(run('episode') === 'printemps' && run('MAP.id') === 'monde' && run('items.length') === run('nItems') && run('Object.keys(elsewhere).length') === 0,
     'elle reprend dans le monde, sans autre carte, dans le premier épisode');
  // nouvelle partie depuis une autre carte : toujours à la niche
  run('travel("cote", 0); newGame("aventure", true);'); advanceDialog();
  ok(run('MAP.id') === 'monde' && run('Math.abs(P.x - MAP.start[0]) < 1') && run('Object.keys(elsewhere).length') === 0 && run('items.length') === run('MAP.items.length'),
     'nouvelle partie : à la niche, dans un monde neuf');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
