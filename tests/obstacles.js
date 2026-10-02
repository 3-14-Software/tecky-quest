// Un chien doit contourner un panneau, un arbre ou une botte de foin au lieu de trembler dessus
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  const cases = [['road_sign', 'bouledogue'], ['road_sign', 'roquet'], ['tree', 'bouledogue'], ['hay', 'molosse'], ['lamppost', 'roquet']];
  for (const [obst, kind] of cases) {
    for (const side of [1, -1]) {
      run(\`var O = decor.filter(o => o.n === "\${obst}").find(o => o.x > 300 && o.y > 300 && o.x < MAP.w * TS - 300 && !blockedFeet(o.x - 70, o.y - 4, 14) && !blockedFeet(o.x + 70, o.y - 4, 14) &&
        !calmAt(o.x - 200, o.y) && !calmAt(o.x + 200, o.y));   // (hors des zones calmes : on n'y poursuit pas Tecky)
        var K = dogs.find(d => d.kind === "\${kind}") || dogs[0];
        dogs = [K]; K.mode = "chase"; K.detT = 0; K.detSide = undefined; K.cd = 99; K.barkCd = 99;
        K.x = O.x + \${side} * -70; K.y = O.y - 4; K.hx = K.x; K.hy = K.y;
        P.x = O.x + \${side} * 200; P.y = O.y + 2; P.mode = "free"; P.inv = 99; P.hp = 99;\`);
      let flips = 0, lastBehind = null, maxProg = 0;
      for (let i = 0; i < 240; i++) {
        step(1);
        const behind = run('K.y < O.y');
        if (lastBehind !== null && behind !== lastBehind) flips++;
        lastBehind = behind;
        maxProg = Math.max(maxProg, run(\`(K.x - O.x) * \${side}\`));
        run('P.x = O.x + ' + side + ' * 200; P.y = O.y + 2;');
      }
      ok(maxProg > 40 && flips <= 4, \`\${kind} contourne \${obst} (\${side > 0 ? 'vers la droite' : 'vers la gauche'}) : passé de \${Math.round(maxProg)} px, \${flips} passages devant/derrière\`);
    }
  }
}, 50);`);
