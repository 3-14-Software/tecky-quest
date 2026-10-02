// petites bêtes (écureuils, chats), zones (bandeau, ambiance sonore, timbre de la musique), carte de la pause,
// copains qui suivent Tecky en balade
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999; farm.state = "done";');

  // ---- petites bêtes
  ok(run('critters.filter(c => c.kind === "squirrel").length') >= 4 && run('critters.some(c => c.kind === "cat")') &&
     run('critters.some(c => c.kind === "cat_black")'), run('critters.length') + ' petites bêtes : écureuils et chats');
  run('var S = critters.find(c => c.kind === "squirrel"); P.x = S.x - 600; P.y = S.y; P.mode = "free";');
  step(60 * 5);
  ok(run('S.mode') === 'roam' && run('dist(S.x, S.y, S.hx, S.hy)') < run('CRITTER.roam') + 10, 'l’écureuil flâne près de son coin');
  run('var sc0 = score; P.x = S.x - 120; P.y = S.y;'); step(1);
  ok(run('S.mode') === 'flee' && run('S.ref && (S.ref.deco.n === "tree" || S.ref.deco.n === "fir")'), 'Tecky approche : il file vers un arbre');
  // (s'il n'y en a aucun à portée, il prend le plus proche)
  ok(run('dist(P.x, P.y, S.ref.x, S.ref.y) >= dist(S.x, S.y, S.ref.x, S.ref.y) || !decor.some(d => (d.n === "tree" || d.n === "fir") && ' +
         'dist(S.x, S.y, d.x, d.y + 6) < 900 && dist(P.x, P.y, d.x, d.y) >= dist(S.x, S.y, d.x, d.y + 6))'), 'un arbre qui n’est pas du côté de Tecky');
  { let k = 0; while (run('S.mode') !== 'perched' && k++ < 400) step(1); }
  ok(run('S.mode') === 'perched' && !run('critterVisible(S)'), 'il grimpe et disparaît dans le feuillage');
  ok(run('score') === run('sc0') + run('CRITTER.pts') && run('pops.some(p => /Tchic/.test(p.text))'), 'premier écureuil surpris : +' + run('CRITTER.pts') + ' et « Tchic tchic ! »');
  step(60 * 3);
  ok(run('S.mode') === 'perched', 'il reste perché tant que Tecky est là');
  run('P.x = S.x - 800;'); step(60 * 7);
  ok(run('S.mode') === 'roam' && run('S.h') === 0, 'Tecky parti : il redescend');
  run('sc0 = score; P.x = S.x - 120; P.y = S.y;'); { let k = 0; while (run('S.mode') !== 'perched' && k++ < 500) step(1); }
  ok(run('score') === run('sc0'), 'la deuxième fois : plus de points');
  // aboyer de loin fait aussi fuir ; le chat saute sur un toit et feule
  run('var C = critters.find(c => c.kind === "cat"); C.x = C.hx; C.y = C.hy; C.mode = "roam"; P.x = C.x - 260; P.y = C.y; P.dir = "right"; P.mode = "free"; P.cdBark = 0; pressed.bark = true');
  step(1);
  ok(run('C.mode') === 'flee', 'aboiement : le chat file');
  ok(run('C.ref && /house|container|bakery/.test(C.ref.deco.n)'), 'vers un toit (' + run('C.ref.deco.n') + ')');
  { let k = 0; while (run('C.mode') !== 'perched' && k++ < 400) step(1); }
  ok(run('C.mode') === 'perched' && run('C.h') > 50 && run('critterVisible(C)'), 'il saute sur le toit et y reste, bien visible');
  run('P.x = C.x; P.y = C.y + 100;'); step(5);
  ok(run('C.anim') === 'hiss', 'Tecky tout près : il feule');
  run('var used = []; var ds0 = drawSpr; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; render(); drawSpr = ds0;');
  run('camX = C.x - VW / 2; camY = C.y - VH / 2; used = []; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; render(); drawSpr = ds0;');
  ok(run('used.includes("cat/hiss")'), 'sprite du chat qui feule dessiné');
  run('saveGame(); var SV = loadSave();');
  ok(run('SV.critters.split("").filter(x => x === "1").length') === 2, 'la sauvegarde retient les bêtes déjà surprises');

  // ---- zones : bandeau, ambiance
  run('P.x = 76 * 64; P.y = 56 * 64;'); step(70);   // d'abord ailleurs (Tecky était au village, près du chat)
  run('P.x = 46 * 64; P.y = 5 * 64; banner = null;'); step(70);
  ok(run('zone.id') === 'village' && run('banner && banner.text') === 'Le village', 'en arrivant au village : bandeau « Le village »');
  run('P.x = 76 * 64; P.y = 56 * 64;'); step(70);
  ok(run('zone.id') === 'foret' && run('TIMBRE.foret.lead') === 'triangle', 'dans la forêt : flûte (onde triangle ; transitions : music.js)');
  ok(run('zoneAt(80.5 * 64, 43.2 * 64).id') === 'verger' && run('zoneAt(80.5 * 64, 44 * 64).id') === 'foret', 'sur le pont : le verger jusqu’au milieu de la rivière, puis la forêt');
  ok(run('JSON.stringify(ZONES.map(z => z.id))') === '["foret","parc","verger","ferme","industrie","village","campagne","niche"]', 'huit zones (la rivière n’en est pas une)');
  ok(run('zoneAt(70 * 64, 17 * 64).id') === 'ferme' && run('zoneAt(70 * 64, 23 * 64).id') === 'verger', 'la route sépare la ferme (au nord) du verger (au sud)');
  ok(run('[2, 23, 46, 66, 91].every(x => zoneAt(x * 64, 41.2 * 64) === zoneAt(x * 64, 43.4 * 64) && zoneAt(x * 64, 43.8 * 64) === zoneAt(x * 64, 46 * 64))'),
     'en longeant la rivière, d’un côté ou de l’autre, on reste dans la même zone');
  run('P.x = 46 * 64; P.y = 5 * 64;'); step(30); run('P.x = 46.3 * 64;'); step(30);
  run('banner = null; P.x = 27.7 * 64; P.y = 5 * 64;'); step(20); run('P.x = 27.3 * 64;'); step(20); run('P.x = 27.7 * 64;'); step(20);
  ok(run('banner') === null, 'pas de bandeau en longeant une frontière');
  // ambiance : oiseaux en forêt, clapotis près de l'eau, rien en pause
  run('P.x = 76 * 64; P.y = 56 * 64; Ambience.played = 0;'); step(60 * 10);
  ok(run('Ambience.played') >= 2, 'des oiseaux chantent en forêt (' + run('Ambience.played') + ' en 10 s)');
  run('P.x = 80.5 * 64; P.y = 43.6 * 64;'); step(30);
  const lv = run('Ambience.level');
  run('P.x = 46 * 64; P.y = 26 * 64;'); step(30);
  ok(lv > 0.02 && run('Ambience.level') < lv / 3, 'clapotis sur le pont (' + lv.toFixed(3) + '), presque rien dans la zone industrielle');
  run('pressed.pause = true'); step(1); run('var pl = Ambience.played;'); step(60 * 3);
  ok(run('Ambience.played') === run('pl') && run('Ambience.level') === 0, 'en pause : silence');
  // ---- carte de la pause
  ok(run('seenCells.filter(Boolean).length') > 10 && !run('seenCells[seenCells.length - 1]'), 'les coins vus sont marqués, pas les autres');
  run('drawPauseMap()');
  ok(run('mapImg && mapImg.width') === run('MAP.w * TS / 4'), 'carte pré-rendue au quart');
  run('used = []; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; render(); drawSpr = ds0;');
  ok(run('used.includes("hud/portrait_tecky")'), 'Tecky sur la carte');
  run('pressed.pause = true'); step(1);
  run('saveGame(); SV = loadSave(); var nseen = seenCells.filter(Boolean).length;');
  run('loadGame(SV, false)'); advanceDialog();
  ok(run('seenCells.filter(Boolean).length') >= run('nseen'), 'Continuer : les coins déjà vus le restent');

  // ---- balade : les copains suivent Tecky en file indienne
  run('newGame("balade", true)'); advanceDialog();
  run('cars = []; var A = dogs.filter(d => d.kind === "roquet")[0], B2 = dogs.filter(d => d.kind === "roquet")[1]; dogs = [A, B2];');
  run('P.x = 8 * 64; P.y = 5 * 64 + 32; P.mode = "free"; A.x = P.x + 60; A.y = P.y; B2.x = P.x + 70; B2.y = P.y + 40; A.mode = B2.mode = "idle";');
  for (const D of ['A', 'B2']) {
    run(`${D}.x = P.x + 60; ${D}.y = P.y; ${D}.mode = "wait"; ${D}.wait = 0; ${D}.timer = 0; P.cdBite = 0; P.mode = "free"; pressed.bite = true;`);
    step(1); step(Math.ceil(60 * run('PLAY.time')) + 2);
  }
  ok(run('A.mode') === 'follow' && run('B2.mode') === 'follow', 'après avoir joué, les copains suivent Tecky');
  // Tecky se promène : ils restent derrière lui, l'un après l'autre
  step(60 * 2, 'held.right = true'); step(60 * 1, 'held.down = true'); run('held.right = false; held.down = false;'); step(60);
  const dA = run('dist(A.x, A.y, P.x, P.y)'), dB = run('dist(B2.x, B2.y, P.x, P.y)');
  ok(dA < 120 && dB < 180 && dB > dA, 'en file indienne derrière lui (' + Math.round(dA) + ' px, puis ' + Math.round(dB) + ' px)');
  // par le terrier : ils passent aussi
  run('var TN = MAP.tunnels[0]; P.x = TN[0]; P.y = TN[1]; P.mode = "free"; P.cdBite = 0; pressed.bite = true'); step(90); advanceDialog(); step(60);
  ok(run('dist(A.x, A.y, P.x, P.y)') < 150 && run('A.x') > run('TN[0]') + 20, 'ils passent le terrier avec lui');
  step(60 * 31);
  ok(run('A.mode') !== 'follow' && run('B2.mode') !== 'follow', 'au bout d’un moment, ils rentrent chez eux');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
