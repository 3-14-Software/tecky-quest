// plusieurs cartes : Tecky prend le tunnel de la route, arrive sur une deuxième carte, y marche, revient ; chaque carte
// garde son état ; une partie enregistrée là-bas reprend là-bas (sauvegarde v3 ; une v2 se reprend dans le monde)
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs.forEach(d => { d.x = d.hx; d.y = d.hy; }); cars = []; P.inv = 99;');
  ok(run('Object.keys(CARTES).join()') === 'monde,pre' && run('MAP.id') === 'monde' && run('MAP.ts') === 64 && run('MAP.w') === 96,
     'deux cartes ; la carte courante est celle du monde, et hérite des données du jeu (MAP.ts)');
  ok(run('JSON.stringify(MAP.passages)') === '[[1,"pre",0]]' && run('JSON.stringify(CARTES.pre.passages)') === '[[0,"monde",1]]',
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
  ok(run('MAP.id') === 'pre' && run('state') === 'play' && run('MAP.w') === 40 && run('MAP.h') === 24, 'Tecky pousse dans le tunnel de l\'est : il est sur la deuxième carte (40 x 24)');
  ok(run('(() => { const [x, , d] = arrivalAt(0), [r0, r1] = MAP.traffic.road; return P.x - x >= 0 && P.x - x < 200 && P.y > r0 && P.y < r1 && d === "right"; })()') && run('!blockedFeet(P.x, P.y, 16)'),
     'il ressort sur la route, devant la bouche du tunnel de l\'ouest');
  ok(Math.abs(run('P.y - MAP.traffic.road[0]') - run('yEntree')) < 30, 'à la hauteur où il est entré : ' + Math.round(run('yEntree')) + ' px sous le bord de la chaussée, ' + Math.round(run('P.y - MAP.traffic.road[0]')) + ' à la sortie');
  ok(run('score') === 321 && run('farm.state') === 'asked' && run('treasures') === 1 && run('P.hp') > 0, 'la partie continue : score, quêtes et trésors le suivent');
  ok(run('dogs.length') === 0 && run('items.length') === 0 && run('npcList().length') === 0 && run('decor.length') > 10 && run('butterflies.length') === 2
     && run('cars.length') === 2 && run('alice.hidden') && !run('ici("alice")') && !run('ici("track")') && run('ici("traffic")'),
     'cette carte a ses décors, ses papillons et ses voitures, mais ni chiens, ni personnages, ni Alice, ni voie ferrée');
  ok(run('ZONES.length') === 1 && run('ZONES[0].name') === 'Au-delà du tunnel' && run('EDGE_DECOR.filter(d => d.n === "tunnel").length') === 2
     && run('EDGE_DECOR.filter(d => d.n !== "tunnel").every(d => offMap(d.x, d.y - 12, d.x, d.y))'),
     'ses zones et sa lisière sont les siennes (' + run('EDGE_DECOR.length') + ' fourrés et arbres autour, deux tunnels)');
  // il y marche, le jeu se dessine, rien ne casse
  run('var x0 = P.x, y0 = P.y; cars = [];');
  step(90, 'held.right = true;'); run('held.right = false;');
  step(60, 'held.down = true;'); run('held.down = false;');
  ok(run('P.x - x0') > 150 && run('P.y - y0') > 60 && run('ground.size') >= 1 && run('zone && zone.id') === 'campagne', 'il y marche (' + Math.round(run('P.x - x0')) + ' px vers l\'est, puis vers le sud)');
  run('state = "pause"; openPauseMenu(); render(); state = "play"; menu = null;');
  ok(run('mapImg !== null') && run('seenCells.length') === run('cellsW() * cellsH()') && run('seenCells.some(v => v)'), 'la carte de la pause est celle de cette carte');
  run('var b0 = JSON.stringify(badges); seenCells.fill(1); checkBadges();');
  ok(run('JSON.stringify(badges)') === run('b0'), 'pas de badge gagné parce que la carte est vide (bêtes, canards, os dorés, explorateur)');
  ok(run('(() => { const a = arrowTarget(), [x, y] = arrivalAt(0); return a.x === x && a.y === y; })()'), 'la flèche et le flair ramènent au tunnel : l\'indice suivant n\'est pas ici');
  // partie enregistrée là-bas : elle reprend là-bas
  run('P.x = 700; P.y = 1100; saveGame(); var S = STORE.get(SAVE_KEY), chatAvant = S.ailleurs.monde.cat.slice();');
  ok(run('S.v') === 3 && run('S.carte') === 'pre' && run('!!S.ailleurs.monde') && run('(() => { const m = S.ailleurs.monde, a = JSON.parse(avant); return m.items.length === nItems && JSON.stringify(m.dogs) === JSON.stringify(a.dogs) && JSON.stringify(m.dug) === JSON.stringify(a.dug); })()'),
     'sauvegarde v3 : la carte courante, et l\'état du monde rangé sous « ailleurs »');
  run('toTitle();');
  ok(run('MAP.id') === 'monde' && run('state') === 'title' && run('EDGE_DECOR.length') > 300, 'retour à l\'écran titre : la carte du monde, sur la place du village');
  run('loadGame(STORE.get(SAVE_KEY), false);'); advanceDialog();
  ok(run('MAP.id') === 'pre' && run('P.x') === 700 && run('P.y') === 1100 && run('score') === 321 && run('farm.state') === 'asked' && run('dogs.length') === 0,
     'Continuer : la partie reprend sur la deuxième carte, là où elle a été enregistrée');
  // retour par le tunnel : le monde est comme il l'avait laissé
  run('{ const [x, y] = arrivalAt(0); P.x = x - 10; P.y = y; P.mode = "free"; cars = []; }');
  step(45, 'held.left = true; if (MAP.id === "pre") cars = [];'); run('held.left = false;');
  ok(run('MAP.id') === 'monde' && run('P.x') > run('MAP.w * TS - 300') && run('P.dir') === 'left', 'il repasse le tunnel : de retour dans le monde, côté est');
  ok(run('items.length') === run('nItems') && run('dogs.length') === run('nDogs') && run('digs[2].dug') && run('digs.filter(g => g.dug).length') === 1
     && run('pompon.mode') === 'wait' && run('pompon.x') === run("chatAvant[0]") && run('npcList().length') === 6 && run('ZONES.length') === 8,
     'le monde est comme il l\'avait laissé : l\'os ramassé, le trésor déterré, le chien parti ; Pompon, qui le suivait, l\'a attendu');
  ok(run('Object.keys(elsewhere).join()') === 'pre' && run('elsewhere.pre.seen.includes("1")'), 'et la deuxième carte garde à son tour ce qu\'il y a vu');
  // une sauvegarde d'avant les cartes multiples (v2) se reprend dans le monde
  run('saveGame(); var V2 = STORE.get(SAVE_KEY); V2.v = 2; delete V2.carte; delete V2.ailleurs; STORE.set(SAVE_KEY, V2); toTitle();');
  ok(run('!!loadSave()') && run('menu.items[0].id') === 'continue', 'une sauvegarde v2 est encore proposée (« Continuer »)');
  run('loadGame(loadSave(), false);'); advanceDialog();
  ok(run('MAP.id') === 'monde' && run('items.length') === run('nItems') && run('Object.keys(elsewhere).length') === 0, 'elle reprend dans le monde, sans autre carte');
  // nouvelle partie depuis une autre carte : toujours à la niche
  run('travel("pre", 0); newGame("aventure", true);'); advanceDialog();
  ok(run('MAP.id') === 'monde' && run('Math.abs(P.x - MAP.start[0]) < 1') && run('Object.keys(elsewhere).length') === 0 && run('items.length') === run('MAP.items.length'),
     'nouvelle partie : à la niche, dans un monde neuf');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
