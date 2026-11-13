// la nage (été) : Tecky nage dans la mer près du bord. Il y entre et en sort par le sable, la ligne de bouées
// l'arrête, il ne monte pas sur la jetée depuis l'eau et ne saute pas d'un quai ; au printemps, rien ne change.
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('EPISODES[1].chantier = false; audioOn(); STORE.mem = {}; loadBadges(); episode = "ete"; newGame("balade", true);'); advanceDialog();
  run('cars = []; dogs = []; P.inv = 99; var T = MAP.ts; function va(x, y) { P.x = x * T; P.y = y * T; P.mode = "free"; for (const k in held) held[k] = false; syncSwim(true); }');
  ok(['nage/idle/down', 'nage/walk/right', 'nage/walk/up', 'nage/bark/right', 'nage/bite/down', 'nage/hurt/up', 'nage/ko/right', 'mer/bouee'].every(k => run(`!!ATLAS["${k}"]`))
     && run('ATLAS["nage/walk/right"].f.length') === run('ATLAS["tecky/walk/right"].f.length') && run('!MAP.cast.includes("nage")'),
     'Tecky a ses dessins de nage (mêmes animations, sans ombre portée) et la bouée');
  ok(run('swimCoins().any') && run('swimBuoys().length') > 40 && run('swimBuoys().every(b => seaAt(b.x, b.y))'),
     'la zone de baignade longe la plage ; ' + run('swimBuoys().length') + ' bouées en marquent la limite, toutes en mer');
  // de la plage vers le large
  run('va(60, 52.5);');
  ok(run('sandAt(P.x, P.y)') && !run('P.swim') && run('P.kind') === 'tecky', 'sur le sable : il marche');
  run('var x0 = P.x, fx0 = fxs.length; held.right = true;'); step(100);
  ok(run('P.swim') && run('P.kind') === 'nage' && run('P.anim') === 'walk' && run('seaAt(P.x, P.y - 6)') && run('!!P.swum'),
     'il entre dans l\'eau par le sable et nage (x ' + run('(P.x / T).toFixed(1)') + ')');
  ok(run('pops.some(p => p.text === txt("tecky.plouf"))'), 'la première fois, il le dit : « ' + run('txt("tecky.plouf")') + ' »');
  run('var xa = P.x;'); step(30); run('var v = (P.x - xa) / 0.5;');
  ok(Math.abs(run('v') - run('250 * SWIM.spd')) < 12, 'il nage moins vite qu\'il ne court (' + Math.round(run('v')) + ' px/s)');
  run('pops = []; held.right = false; held.down = true;');
  for (let i = 0; i < 600 && !run('pops.some(p => p.text === txt("tecky.large"))'); i++) step(1);
  ok(run('P.swim') && run('!deepAt(P.x, P.y - 6)') && run('swimBuoys().some(b => Math.hypot(b.x - P.x, b.y - P.y) < 110)')
     && run('pops.some(p => p.text === txt("tecky.large"))'),
     'la ligne de bouées l\'arrête (x ' + run('(P.x / T).toFixed(1)') + ') : « ' + run('txt("tecky.large")') + ' »');
  // dans l'eau : aboyer, oui ; flairer, gratter, s'asseoir, non
  run('for (const k in held) held[k] = false; pressed.bark = true;'); step(2);
  ok(run('P.mode') === 'bark' && run('P.key()') === 'nage/bark/down', 'il aboie dans l\'eau, avec son dessin de nageur');
  step(40); run('pressed.sniff = true;'); step(2);
  ok(run('P.mode') === 'free' && run('biteAction()') === 'bite', 'dans l\'eau, il ne flaire pas et ne gratte pas');
  step(60 * 8);
  ok(run('P.anim') === 'idle' && run('P.kind') === 'nage', 'sans rien faire, il fait du surplace : il ne s\'assoit pas dans l\'eau');
  // sauvegarde : repris dans l'eau
  run('saveGame(); var S = loadSave(); loadGame(S);'); advanceDialog();
  ok(run('P.swim') && run('P.kind') === 'nage' && run('!!P.swum'), 'partie reprise dans l\'eau : il y nage encore');
  // retour sur la plage : il s'ébroue
  run('cars = []; dogs = []; held.up = true;');
  let shook = false;
  for (let i = 0; i < 900 && !shook; i++) { step(1); advanceDialog(); shook = !run('P.swim') && run('P.mode') === 'shake'; }
  ok(!run('P.swim') && run('P.kind') === 'tecky' && run('sandAt(P.x, P.y)') && shook, 'il ressort par le sable et s\'ébroue');
  // un nageur ne monte pas sur la jetée (planches), et l'on n'y saute pas à l'eau
  run('va(51.5, 57.5);');
  ok(run('P.swim'), 'à côté de la jetée, dans la zone de baignade');
  run('held.left = true;'); step(200);
  ok(run('P.swim') && run('P.x / T') > 49.6, 'depuis l\'eau, il ne monte pas sur la jetée (x ' + run('(P.x / T).toFixed(2)') + ')');
  run('va(49, 57.5); held.right = true;'); step(200);
  ok(!run('P.swim') && run('P.x / T') < 50.2, 'depuis la jetée, il ne saute pas à l\'eau (x ' + run('(P.x / T).toFixed(2)') + ')');
  // l'eau douce et le quai du port : comme avant
  run('va(40, 47.5); held.right = true;'); step(200);
  ok(!run('P.swim') && !run('waterAt(P.x, P.y - 6)'), 'la rivière ne se nage pas');
  run('for (const k in held) held[k] = false; va(8, 50.5); held.down = true;'); step(200);
  ok(!run('P.swim') && run('P.y / T') < 51.2, 'on ne saute pas du quai du port (y ' + run('(P.y / T).toFixed(2)') + ')');
  // les chiens ne nagent pas
  run('for (const k in held) held[k] = false; var D = { x: 60 * T, y: 52.5 * T }; for (let i = 0; i < 400; i++) moveActor(D, 3, 0, 14);');
  ok(run('!waterAt(D.x, D.y)'), 'un chien s\'arrête au bord de l\'eau');
  // au printemps, rien ne change
  run('episode = "printemps"; newGame("balade", true);'); advanceDialog();
  ok(run('!swimCoins().any') && run('swimBuoys().length') === 0 && run('swimBlock(80 * T, 43.6 * T) === waterAt(80 * T, 43.6 * T)') && !run('P.swim'),
     'dans le monde : pas de mer, pas de baignade, l\'eau arrête Tecky comme avant');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
