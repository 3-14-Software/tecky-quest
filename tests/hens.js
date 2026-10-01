// simulation : les poules picorent et se promènent ; un aboiement les fait fuir en battant des ailes
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; P.x = 5*64; P.y = 5*64; P.inv = 99;');
  ok(run('hens.length') >= 4 && run('hens.every(h => h.kind === "hen" || h.kind === "hen_white")'), run('hens.length') + ' poules à la ferme');
  // au calme : elles picorent et font quelques pas, sans s'éloigner ni entrer dans un obstacle
  run('var seen = {}; hens.forEach(h => seen[h.kind + h.hx] = new Set());');
  for (let i = 0; i < 60 * 25; i++) { step(1); if (i % 5 === 0) run('hens.forEach(h => seen[h.kind + h.hx].add(h.anim))'); }
  ok(run('Object.values(seen).every(s => s.has("peck"))'), 'chaque poule picore');
  ok(run('Object.values(seen).some(s => s.has("walk"))'), 'elles se promènent');
  ok(run('hens.every(h => dist(h.x, h.y, h.hx, h.hy) < HEN.roam + 20 && !blockedFeet(h.x, h.y, 8))'), 'elles restent près de leur place, hors des obstacles');
  // aboiement vers une poule : elle s'enfuit en battant des ailes, puis se calme
  run('var H = hens[0]; H.x = H.hx; H.y = H.hy; H.mode = "idle"; H.timer = 9; P.x = H.x - 150; P.y = H.y; P.dir = "right"; P.mode = "free"; P.cdBark = 0;');
  const n0 = nodes;
  run('pressed.bark = true'); step(1);
  ok(run('H.mode') === 'flee' && run('H.anim') === 'flap' && run('H.dir') === 'right', 'aboiement : elle s\\'enfuit en battant des ailes, à l\\'opposé de Tecky');
  ok(nodes - n0 > 4, 'avec un « cot-cot »');
  const d0 = run('dist(H.x, H.y, P.x, P.y)');
  step(50);
  const d1 = run('dist(H.x, H.y, P.x, P.y)');
  ok(d1 > d0 + 60, 'de quelques pas (' + Math.round(d0) + ' -> ' + Math.round(d1) + ' px)');
  ok(run('H.mode') !== 'flee', 'puis elle se calme');
  // aboiement dans l'autre sens : rien
  run('H.mode = "idle"; H.timer = 9; P.x = H.x - 150; P.y = H.y; P.dir = "left"; P.cdBark = 0; P.mode = "free"; pressed.bark = true;'); step(1);
  ok(run('H.mode') === 'idle', 'aboyer dans l\\'autre sens ne lui fait rien');
  // Tecky lui fonce dessus : elle s'écarte (elle ne bloque pas le passage)
  run('H.mode = "idle"; H.timer = 9; P.x = H.x - 20; P.y = H.y; P.mode = "free";'); step(1);
  ok(run('H.mode') === 'flee', 'Tecky trop près : elle s\\'écarte');
}, 50);`);
