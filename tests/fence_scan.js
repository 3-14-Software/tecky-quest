const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  const fences = run('decor.filter(o => o.n === "fence_metal_h").map(o => [o.x, o.y])');
  const fx0 = Math.min(...fences.map(f => f[0])), fy = fences[0][1];
  let bad = 0, tot = 0;
  for (const dx of [-60, -40, -25, -15, -5, 5, 20]) for (const dy of [14, 20, 30, 50, 90])
  for (const [tx, ty] of [[60, -120], [0, -200], [-80, -150], [300, -200], [-200, -60], [100, -40]]) {
    run(\`var K = dogs.find(d => d.kind === "molosse") || dogs[0]; dogs = [K];
      K.mode = "chase"; K.detT = 0; K.detSide = undefined; K.detTot = 0; K.cd = 99; K.barkCd = 99;
      K.x = \${fx0 + dx}; K.y = \${fy + dy}; K.hx = K.x; K.hy = K.y; P.mode = "free"; P.inv = 99; P.hp = 99;\`);
    if (run('blockedFeet(K.x, K.y, 14)')) continue;
    tot++;
    let flips = 0, last = null, reached = -1, maxflipsSec = 0;
    const px = fx0 + tx, py = fy + ty;
    let win = [];
    for (let i = 0; i < 1100; i++) {
      run(\`P.x = \${px}; P.y = \${py};\`);
      step(1);
      const dir = run('K.dir');
      if (last !== null && dir !== last) win.push(i);
      last = dir;
      if (reached < 0 && run('Math.hypot(K.x - P.x, K.y - P.y) < 110')) { reached = i; break; }
    }
    // clignotement : >= 6 changements de direction en 1 s
    let flick = 0;
    for (let a = 0; a < win.length; a++) { let n = 0; for (let b = a; b < win.length && win[b] < win[a] + 60; b++) n++; flick = Math.max(flick, n); }
    if (reached < 0 || flick >= 5) { bad++; console.log('PB', dx, dy, tx, ty, reached < 0 ? 'bloqué' : 'atteint ' + reached, 'chgts dir/s max', flick); }
  }
  console.log('cas', tot, 'problèmes', bad);
}, 50);`);
