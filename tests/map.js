// carte agrandie : sol en blocs, rivière infranchissable sauf par le pont, garde-corps
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; P.inv = 99;');
  ok(run('MAP.w') === 80 && run('MAP.h') === 48, 'carte de 80 x 48 tuiles');
  ok(run('groundChunks.length') === 15 && run('groundChunks.every(k => k.w <= 1024 + 2 * CM && k.h <= 1024 + 2 * CM)'),
     'sol pré-rendu en 15 blocs de 1024 px au plus');
  const walkDown = (x, n) => { run('P.x = ' + x + '; P.y = 24.4*64; P.mode = "free";'); step(n, 'held.down = true'); run('held.down = false'); return run('P.y') / 64; };
  ok(walkDown('64*64', 200) > 31, 'on traverse la rivière par le pont');
  ok(walkDown('60*64', 200) < 26.2, 'ailleurs, la rivière bloque');
  ok(walkDown('7*64', 200) < 26.2, 'au bout du chemin de la barque aussi');
  run('P.x = 64*64; P.y = 27.5*64; P.mode = "free";'); step(120, 'held.right = true'); run('held.right = false');
  ok(run('P.x') / 64 < 65.1, 'le garde-corps retient Tecky sur le pont (x = ' + (run('P.x') / 64).toFixed(2) + ')');
  ok(run('MAP.decor.some(d => d[0] === "bridge")') && run('FLAT.has("bridge")'), 'le pont est dessiné à plat, sous les personnages');
}, 50);`);
