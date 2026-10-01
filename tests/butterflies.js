// simulation : les papillons volettent dans le parc, se posent sur les fleurs, s'envolent quand Tecky approche
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; P.x = 5 * 64; P.y = 5 * 64; P.inv = 1e9;');
  ok(run('butterflies.length') === 7 && run('butterflies.every(b => b.x < 40 * 64 && b.y > 30 * 64)'), '7 papillons dans le parc');
  run('var rested = new Set(), frames = new Set(), far = 0;');
  for (let i = 0; i < 60 * 60; i++) {
    step(1);
    if (i % 6 === 0) run('butterflies.forEach((b, k) => { if (b.mode === "rest" && dist(b.x, b.y, b.perch[0], b.perch[1]) < 10) rested.add(k);' +
                         ' frames.add(Math.floor(b.flap) % 4); far = Math.max(far, dist(b.x, b.y, b.hx, b.hy)); })');
  }
  ok(run('rested.size') >= 3, run('rested.size') + ' papillons se sont posés sur une fleur en une minute');
  ok(run('frames.size') === 4, 'ils battent des ailes (4 images)');
  ok(run('far') < run('BFLY.roam') * 1.6, 'ils restent dans leur coin du parc (au plus ' + Math.round(run('far')) + ' px de leur place)');
  // Tecky s'approche : il s'envole, plus haut, puis revient
  run('var B = butterflies[1]; B.mode = "fly"; B.x = B.hx; B.y = B.hy; B.tx = B.x + 1; B.ty = B.y; P.x = B.x - 60; P.y = B.y; P.mode = "free";');
  step(1);
  ok(run('B.mode') === 'flee', 'Tecky trop près : le papillon s\\'envole');
  run('P.x = 5 * 64; P.y = 5 * 64;'); step(40);
  ok(run('B.alt') > run('BFLY.alt') * 1.4 && run('dist(B.x, B.y, B.hx, B.hy)') > 100, 'plus haut et plus loin');
  step(60 * 8);
  ok(run('B.mode') !== 'flee' && run('dist(B.x, B.y, B.hx, B.hy)') < run('BFLY.roam') * 1.6, 'puis il revient dans son coin');
  // aboiement dans sa direction
  run('B.mode = "fly"; B.x = B.hx; B.y = B.hy; P.x = B.x - 200; P.y = B.y; P.dir = "right"; P.cdBark = 0; P.mode = "free"; pressed.bark = true;');
  step(1);
  ok(run('B.mode') === 'flee', 'un aboiement le fait s\\'envoler');
  run('render()'); ok(true, 'dessin des papillons et de leurs ombres');
}, 50);`);
