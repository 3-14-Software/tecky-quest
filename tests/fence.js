const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  const fences = run('decor.filter(o => o.n === "fence_metal_h").map(o => [o.x, o.y])');
  console.log('clôtures', fences.length, JSON.stringify(fences.slice(0, 2)));
  const fx0 = Math.min(...fences.map(f => f[0])), fy = fences[0][1];
  const cases = [
    ['bord gauche, Tecky en haut à droite', fx0 - 40, fy + 30, fx0 + 200, fy - 160],
    ['bord gauche, Tecky juste au-dessus', fx0 - 10, fy + 20, fx0 + 40, fy - 120],
    ['milieu du grillage', fx0 + 256, fy + 40, fx0 + 256, fy - 200],
    ['sous le bord gauche, Tecky au-dessus à gauche', fx0 + 20, fy + 30, fx0 - 60, fy - 200],
  ];
  for (const kind of ['molosse', 'bouledogue', 'roquet']) for (const [name, x, y, px, py] of cases) {
    run(\`var K = dogs.find(d => d.kind === "\${kind}") || dogs[0]; dogs = [K]; K.kind = "\${kind}";
      K.mode = "chase"; K.detT = 0; K.detSide = undefined; K.detTot = 0; K.cd = 99; K.barkCd = 99;
      K.x = \${x}; K.y = \${y}; K.hx = K.x; K.hy = K.y;
      P.mode = "free"; P.inv = 99; P.hp = 99;\`);
    let reached = -1, xs = [];
    for (let i = 0; i < 900; i++) {
      run(\`P.x = \${px}; P.y = \${py};\`);
      step(1);
      if (reached < 0 && run('K.y < ' + (fy - 20))) reached = i;
      if (i % 30 === 0) xs.push(Math.round(run('K.x')));
    }
    ok(reached >= 0, \`\${kind} / \${name} : a franchi le grillage en \${reached >= 0 ? (reached / 60).toFixed(1) + ' s' : 'jamais (x: ' + xs.slice(0, 12) + ')'}\`);
  }
}, 50);`);
