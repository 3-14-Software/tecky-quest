// petits effets (poussière, feuilles, ombres de nuages) et coucher de soleil qui suit la progression
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  ok(run('clouds.length') === run('CLOUD.n') && run('cloudImgs.length') === 3, 'ombres de nuages prêtes (' + run('clouds.length') + ')');
  run('camX = 3500; camY = 2600;');            // l'écran titre vit aussi : feuilles et nuages
  run('var c0 = clouds[0].x;'); step(60 * 4);
  ok(run('clouds[0].x') > run('c0') + 40, 'les nuages glissent, même sur l’écran titre');
  run('clouds[0].x = MAP.w * TS + 1;'); step(1);
  ok(run('clouds[0].x') < 0, 'un nuage sorti de la carte revient de l’autre côté');
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; P.inv = 999;');
  ok(run('sun') === 0, 'plein jour au départ');

  // poussière
  run('P.x = 8 * 64; P.y = 5 * 64 + 32; P.mode = "free"; dusts = [];');
  step(60, 'held.right = true'); run('held.right = false');
  ok(run('dusts.length') > 0 && run('dusts.length') <= run('DUST.max'), 'Tecky marche : petits nuages de poussière (' + run('dusts.length') + ')');
  ok(run('dusts.every(d => d.x < P.x)'), 'la poussière reste derrière ses pattes');
  step(60);
  ok(run('dusts.length') === 0, 'à l’arrêt, elle se dissipe');
  // un mur juste devant lui, plus haut que ses pattes : il pousse sans avancer
  run('P.x = 8 * 64; P.y = 5 * 64 + 32; solids.push([P.x + 17, P.y - 60, P.x + 80, P.y + 60]); dusts = []; var xs = P.x, ys = P.y;');
  step(40, 'held.right = true'); run('held.right = false; solids.pop();');
  ok(run('P.x === xs && P.y === ys') && run('dusts.length') === 0, 'bloqué contre un obstacle : pas de poussière');

  // feuilles : caméra sur la forêt
  run('P.x = 86 * 64; P.y = 52 * 64; camX = P.x - VW / 2; camY = P.y - 40 - VH / 2; leaves = [];');   // (forêt dense, loin de la clairière)
  let most = 0, landed = 0;
  for (let i = 0; i < 60 * 20; i++) { step(1); most = Math.max(most, run('leaves.length')); if (i % 30 === 0) landed += run('leaves.filter(l => l.h === 0).length'); }
  ok(most > 5 && most <= run('LEAF.max'), 'les arbres de la forêt lâchent des feuilles (jusqu’à ' + most + ' à la fois)');
  ok(landed > 0, 'elles se posent au sol');
  ok(run('leaves.every(l => l.t < 20)'), 'puis s’effacent');
  ok(run('leaves.every(l => l.c >= 0 && l.c < ATLAS["fx/leaf"].f.length)'), 'couleurs prises dans fx/leaf');
  run('drawLeavesOnGround(); drawFallingLeaves();');

  // coucher de soleil : un cran par indice, transition douce, encore plus chaud aux retrouvailles
  const sunAfter = (s, setup) => { run(setup); step(Math.round(60 * s)); return run('sun'); };
  const s1 = sunAfter(1, 'clues = [true, false, false]');
  ok(s1 > 0.1 && s1 < 0.5, 'premier indice : la lumière commence à baisser (' + s1.toFixed(2) + ' après 1 s)');
  ok(Math.abs(sunAfter(4, '') - 1) < 1e-6, 'puis atteint l’après-midi (1)');
  ok(Math.abs(sunAfter(5, 'clues = [true, true, false]') - 2) < 1e-6 && !run('lampsOn()'), 'deux indices : le coucher de soleil (2), sans lampadaires');
  ok(Math.abs(sunAfter(5, 'clues = [true, true, true]') - 3) < 1e-6, 'trois indices : toujours le coucher (3)…');
  ok(run('lampsOn()') && run('decor.some(d => d.n === "lamppost")'), '… mais les lampadaires sont allumés');
  ok(run('sunAt(SUN.tints.map(t => t[2]), 3)') > 150, 'pas encore la nuit bleutée');
  run('render()');
  run('revealAlice(); P.x = alice.x - 100; P.y = alice.y + 10; P.mode = "free";'); step(2);
  ok(run('alice.found') && run('sunGoal()') === 3, 'retrouvailles : encore le coucher de soleil (3)');
  step(60 * 5);
  ok(Math.abs(run('sun') - 3) < 1e-6 && run('hug') === 1, 'la lumière chaude autour d’eux');
  advanceDialog(); step(60 * 6);
  ok(Math.abs(run('sun') - 4) < 1e-6, 'la nuit tombe pendant la scène de fin (4)');
  run('pressed.ok = true'); step(1); step(70);   // scène de fin passée, écran de victoire
  run('render()');
  run('pressed.ok = true'); step(1);
  ok(run('state') === 'title' && run('sun') === 0, 'retour au menu : plein jour');
  // voiture : nuage de poussière au choc
  run('pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; var v = cars.find(c => c.lane === 1); v.v = v.T.spd; P.x = v.x + 120; P.y = MAP.traffic.lanes[1] - 10; P.bumpT = 0; P.inv = 0; P.mode = "free"; dusts = [];');
  { let k = 0; while (run('P.bumpT') <= 0 && k++ < 120) step(1); }
  ok(run('P.bumpT') > 0 && run('dusts.length') >= 3, 'voiture : Tecky bousculé dans un nuage de poussière');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
