// le voyage en voiture de l'été : la partie commence par une cinématique (le papa, Alice et Tecky montent en voiture
// devant le chemin de la niche, la voiture prend le tunnel, arrive sur la côte, entre sous le porche du parking), puis
// Tecky a la main sur le parking ; la partie y est enregistrée et y reprend ; à pied, les tunnels restent fermés
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  const jusqua = (cond, max) => { let k = 0; while (!run(cond) && k++ < max) step(1); return run(cond); };
  ok(run('EPISODES[1].voyage') === 'cote' && run('CARTES.cote.start[0]') > 0 && run('CARTES.cote.papa[0]') > 0
     && run('CARTES.monde.absents.includes("papa")') && !run('CARTES.cote.absents.includes("papa")') && !run('CARTES.cote.absents.includes("start")'),
     'l\'été voyage vers la côte, qui a son point de départ (le parking) et le papa d\'Alice');
  run('EPISODES[1].chantier = false; audioOn(); episode = "ete"; toTitle(); resetProgress(); episode = "ete";');
  // 1. nouvelle aventure : la cinématique, sur la carte de départ
  run('newGame("aventure");'); step(2);
  ok(run('state') === 'trip' && run('MAP.id') === 'monde' && run('trip.car.name') === 'sport_vide' && run('!alice.hidden') && run('alice.kind') === 'alice_ete'
     && run('cars.length') === 0 && !run('loadSave()'),
     'nouvelle aventure d\'été : la cinématique commence dans le monde, la voiture du papa garée au bas du chemin de la niche');
  ok(jusqua('state === "dialog"', 900) && run('dialog.lines[0].who') === 'papa' && run('dialog.lines.length') === 3
     && run('Math.abs(alice.y - trip.car.y) < 60 && Math.abs(P.y - trip.car.y) < 60'),
     'Alice et Tecky descendent jusqu\'à la voiture ; le papa : « ' + run('dialog.lines[0].text') + ' »');
  ok(run('trip.papa.anim') === 'talk', 'le papa parle pendant sa réplique');
  run('var pt = trip.papa.t; pressed.ok = true;'); step(1); run('pressed.ok = true;'); step(20);
  ok(run('state') === 'dialog' && run('dialog.lines[dialog.i].who') === 'alice' && run('trip.papa.anim') === 'idle' && run('trip.papa.t') > 0.2,
     'pendant celle d\'Alice, il se tait mais ne se fige pas');
  advanceDialog();
  ok(run('state') === 'trip' && jusqua('trip.aboard', 600) && run('alice.hidden') && run('trip.car.name') === 'sport_vide' && run('trip.papa') !== null,
     'Alice et Tecky montent ; le papa est encore dehors');
  run('var px0 = trip.papa.x;'); step(20);
  ok(run('trip.papa.anim') === 'walk' && run('trip.papa.x') > run('px0') + 20 && !!run('ATLAS["papa/walk"]'), 'il marche jusqu\'à sa portière');
  ok(jusqua('trip.step === "route"', 300) && run('trip.car.name') === 'sport' && run('trip.papa') === null,
     'il monte à son tour : la voiture a ses passagers, plus personne à côté');
  run('var noir = 0, cam0 = camX;');
  ok(jusqua('(noir = Math.max(noir, trip.a), trip.car.x > MAP.w * TS - 200)', 1500) && run('MAP.id') === 'monde' && run('noir') === 0
     && run('camX') > run('cam0') + 3000 && run('camX') > run('MAP.w * TS - VW') && run('trip.step') === 'route',
     'la voiture traverse toute la carte, la caméra la suit, sans fondu, jusqu\'au tunnel de l\'est');
  ok(jusqua('MAP.id === "cote"', 900) && run('state') === 'trip' && run('trip.step') === 'arrivee' && run('trip.car.x') < 0,
     'elle s\'enfonce dans le tunnel ; au noir, la côte : elle en ressort');
  ok((run('Music.want') || run('Music.zone')) === 'cote', 'la musique de la côte commence quand la voiture sort du tunnel');
  run('var vus = []; var dv0 = drawVillager; drawVillager = function (v) { vus.push(v.kind); return dv0.apply(this, arguments); }; camX = camClampX(MAP.papa[0] - VW / 2); camY = camClampY(MAP.papa[1] - VH / 2); render();');
  ok(run('!vus.includes("papa")'), 'pendant que la voiture roule vers le parking, le papa n\'est pas déjà dehors : il est au volant');
  ok(jusqua('state === "dialog"', 1500) && run('dialog.lines[0].who') === 'alice' && run('trip.car') === null
     && run('Math.abs(P.x - MAP.start[0]) < 1 && Math.abs(P.y - MAP.start[1]) < 1') && run('!alice.hidden') && run('villagers.some(v => v.kind === "papa")'),
     'elle roule jusqu\'au porche et y entre ; sur le parking, Alice : « ' + run('dialog.lines[0].text') + ' »');
  run('vus = []; render(); drawVillager = dv0;');
  ok(run('vus.includes("papa")'), 'une fois garés, le papa est descendu');
  run('pressed.ok = true;'); step(1); run('pressed.ok = true;'); step(10);
  ok(run('dialog.lines[dialog.i].who') === 'papa' && run('villagers.find(v => v.kind === "papa").anim') === 'talk', 'sur le parking, le papa parle à son tour');
  advanceDialog(); step(20);
  ok(run('state') === 'trip' && run('trip.step') === 'cache' && run('villagers.find(v => v.kind === "papa").anim') === 'wave' && run('villagers.find(v => v.kind === "papa").t') > 0.1,
     'Alice file : il lui fait signe, il n\'est pas figé');
  ok(jusqua('state === "play"', 400) && run('trip') === null && run('alice.hidden') && run('cars.length') === 5 && run('P.mode') === 'free'
     && run('(() => { const s = loadSave(); return !!s && s.ep === "ete" && s.carte === "cote" && Math.abs(s.x - MAP.start[0]) < 1; })()'),
     'Alice file se cacher : Tecky a la main sur le parking, la partie y est enregistrée');
  run('pops = [];'); step(60);
  ok(run('!pops.some(p => p.who === "papa" || /trouv/.test(p.text))') && run('villagers.find(v => v.kind === "papa").anim') === 'idle',
     'Tecky a la main : le papa, juste à côté, ne lui demande pas déjà s\'il a trouvé Alice');
  ok(run('!/trouv/.test(txt("villageois.papa.0"))'), 'et sa première phrase, quand Tecky revient, n\'est pas cette question');
  // 2. le papa salue comme un villageois ; à pied, le tunnel est pour les voitures
  run('cars = []; dogs = []; pops = []; var V = villagers.find(v => v.kind === "papa"); V.near = false; V.cd = 0; P.x = V.x - 60; P.y = V.y + 60;'); step(2);
  ok(run('pops.some(p => p.text === txt("villageois.papa.0"))') && run('V.anim') === 'wave', 'le papa, resté près du parking : « ' + run('txt("villageois.papa.0")') + ' »');
  run('{ const [x, y] = arrivalAt(0); P.x = x - 10; P.y = y; P.mode = "free"; P.edgeAt = -99; pops = []; }');
  step(70, 'held.left = true; cars = [];'); run('held.left = false;');
  ok(run('MAP.id') === 'cote' && run('passageHere()') === null && run('pops.some(p => p.text === txt("bord.tunnel"))'),
     'à pied, le tunnel est pour les voitures : rien ne ramène au monde');
  // 3. Continuer reprend sur la côte ; recommencer aussi, sans la cinématique
  run('P.x = MAP.start[0] + 200; score = 44; saveGame(); toTitle();');
  ok(run('MAP.id') === 'monde' && run('menu.items[0].id') === 'continue', 'retour au titre : « Continuer »');
  run('loadGame(loadSave(), false);'); advanceDialog();
  ok(run('MAP.id') === 'cote' && run('state') === 'play' && run('score') === 44 && run('Math.abs(P.x - MAP.start[0] - 200) < 1'), 'Continuer : sur la côte, là où la partie a été enregistrée');
  run('newGame("balade", true);');
  ok(run('MAP.id') === 'cote' && run('state') === 'dialog' && run('trip') === null && run('Math.abs(P.x - MAP.start[0]) < 1'), 'recommencer : directement sur le parking');
  advanceDialog();
  // 4. passer la scène ; une partie enregistrée pendant la scène reprend sur la côte
  run('newGame("aventure");'); step(30); run('pressed.ok = true'); step(1);
  ok(run('state') === 'trip', 'la première seconde, on ne passe pas la scène');
  step(45); run('pressed.ok = true'); step(1);
  ok(run('state') === 'play' && run('MAP.id') === 'cote' && run('trip') === null && run('alice.hidden') && run('Math.abs(P.x - MAP.start[0]) < 1') && run('cars.length') === 5,
     'ensuite, un bouton la passe : Tecky est sur le parking');
  run('newGame("aventure");'); step(20); run('saveGame(); var S = loadSave();');
  ok(run('S.carte') === 'monde' && run('S.ep') === 'ete', 'une partie enregistrée pendant la scène est encore dans le monde');
  run('toTitle(); loadGame(loadSave(), false);'); advanceDialog();
  ok(run('MAP.id') === 'cote' && run('state') === 'play' && run('Math.abs(P.x - MAP.start[0]) < 1 && Math.abs(P.y - MAP.start[1]) < 1'),
     'elle reprend sur la côte, au parking : en été, on ne joue pas dans le monde');
  // 5. les indices de l'été, la cachette d'Alice, la fin
  run('episode = "ete"; newGame("aventure");'); step(70); run('pressed.ok = true'); step(1);
  run('cars = []; dogs = []; P.inv = 99;');
  ok(run('state') === 'play' && run('clueNames().join()') === 'hat,spade,flipflop' && run('arrowTarget().n') === 'hat' && run('alice.hidden') && run('alice.kind') === 'alice_ete1'
     && run('Math.abs(alice.x - MAP.alice[0]) < 1') && run('MAP.alice[0]') > run('90 * TS') && run('MAP.alice[1]') < run('MAP.ending.alice[1] - 15 * TS'),
     'en été : trois autres indices (chapeau, pelle, tong), la flèche montre le chapeau ; Alice est cachée tout en haut des falaises, bien au-dessus du phare');
  const ramasser = n => { run(`{ const it = items.find(i => i.n === "${n}"); P.x = it.x; P.y = it.y + 8; P.mode = "free"; }`); step(3); };
  ramasser('hat');
  ok(run('state') === 'dialog' && run('dialog.lines[0].text') === run('txt("indices_ete.trouve.0")') && run('dialog.lines[1].text') === run('txt("indices_ete.ensuite.1")')
     && run('clues[0]') === true, 'le chapeau de paille : « ' + run('dialog.lines[0].text') + ' »');
  advanceDialog();
  ok(run('arrowTarget().n') === 'spade', 'la flèche montre la pelle, en ville');
  ramasser('spade'); advanceDialog(); ramasser('flipflop');
  ok(run('state') === 'dialog' && run('dialog.lines[1].text') === run('txt("indices_ete.ensuite.3")') && run('!alice.hidden'), 'la tong : Alice sort de sa cachette — « ' + run('dialog.lines[1].text') + ' »');
  advanceDialog();
  ok(run('arrowTarget() === alice') && run('sunGoal()') === 3, 'la flèche mène à Alice, le soleil se couche');
  run('P.x = alice.x - 70; P.y = alice.y + 20; P.mode = "free";'); step(3);
  ok(run('state') === 'dialog' && run('alice.found') && run('dialog.lines[0].text') === run('txt("retrouvailles_ete.0")') && run('dialog.lines.length') === 4,
     'les retrouvailles en haut des falaises : « ' + run('dialog.lines[0].text') + ' »');
  advanceDialog();
  ok(run('state') === 'ending', 'puis la scène de fin');
  step(90);
  ok(run('ending.home') && run('alice.y') < run('MAP.ending.alice[1]') && run('alice.dir') === 'down' && run('Math.abs(alice.x - MAP.ending.alice[0]) < 1'),
     'au noir : Alice et Tecky redescendent du haut du plateau vers le pied du phare');
  step(420);
  ok(run('Math.abs(alice.y - MAP.ending.alice[1]) < 1') && run('Math.abs(P.x - MAP.ending.tecky[0]) < 1') && ['sit', 'yawn', 'sleep'].includes(run('P.anim')) && run('sun') > 3,
     'ils sont au pied du phare, Tecky s\'installe, la nuit tombe (le phare s\'allume)');
  run('endingDone();');
  ok(run('state') === 'win' && run('recs["ete:aventure"].wins') === 1 && !run('loadSave()'), 'la victoire de l\'été : ses records à part, plus de partie à continuer');
  run('pressed.ok = true'); step(1);
  // 6. le printemps n'a pas de voyage
  run('episode = "printemps"; newGame("aventure");'); advanceDialog();
  ok(run('state') === 'play' && run('MAP.id') === 'monde' && run('trip') === null && run('!villagers.some(v => v.kind === "papa")'), 'au printemps : pas de voyage, la partie commence à la niche');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
