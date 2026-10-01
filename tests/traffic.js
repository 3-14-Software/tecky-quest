// simulation : circulation sur la grande route ; un véhicule bouscule Tecky (sans dégâts) hors des passages piétons,
// où il s'arrête toujours
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  const q = String.fromCharCode(39);
  ok(run('cars.length') === 6 && run('cars.filter(v => v.lane === 0 && v.dir < 0).length') === 3, '6 véhicules, voie du haut vers l' + q + 'ouest');
  const x0 = run('JSON.stringify(cars.map(v => v.x))');
  step(60);
  ok(run('cars.every((v, i) => (v.x - ' + x0 + '[i]) * v.dir > 100)'), 'ils roulent déjà sur l' + q + 'écran titre, chacun dans son sens');
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('var dogs0 = dogs; dogs = []; P.inv = 1e9;');      // Tecky à l'abri pendant qu'on observe la circulation
  // distances : jamais de chevauchement dans une voie
  let overlap = false;
  for (let i = 0; i < 60 * 40; i++) {
    step(1);
    if (i % 10 === 0 && run('cars.some(a => cars.some(b => a !== b && a.lane === b.lane && Math.abs(a.x - b.x) < (a.T.len + b.T.len) / 2 - 2))')) overlap = true;
  }
  ok(!overlap, 'pas de chevauchement en 40 s de circulation');
  ok(run('cars.every(v => v.x > -400 && v.x < MAP.w * TS + 400)'), 'ils réapparaissent de l' + q + 'autre côté de la carte');
  // Tecky planté sur la voie du bas, loin des passages
  run('dogs = []; hens = []; var V = cars.find(v => v.name === "car_blue"); cars = [V];' +
      'P.x = 30 * 64; P.y = 940; P.mode = "free"; P.inv = 0; P.hp = P.hpMax; V.x = P.x - 520; V.v = V.T.spd;');
  const hp0 = run('P.hp'); let honked = false;
  for (let i = 0; i < 300 && !run('pops.some(p => p.text === "Ouf !")'); i++) { step(1); if (run('V.honkT') > 0) honked = true; }
  ok(honked, 'la voiture klaxonne avant');
  ok(run('pops.some(p => p.text === "Ouf !")') && run('P.hp') === hp0 && run('P.inv') === 0, 'le choc ne fait pas de dégâts (« Ouf ! », PV ' + run('P.hp') + ')');
  step(40);
  ok(!run('inLane(V, P.y)') && run('P.y') > 15 * 64, 'Tecky est projeté sur le bas-côté (y = ' + (run('P.y') / 64).toFixed(1) + ' tuiles)');
  // passage piéton : la voiture s'arrête avant et attend
  run('P.x = 35 * 64; P.y = 940; P.mode = "free"; P.inv = 0; P.hp = P.hpMax; P.kx = P.ky = 0; V.x = P.x - 700; V.v = V.T.spd;');
  step(60 * 6);
  ok(run('V.v') < 1 && run('V.x + V.T.len / 2') <= 34 * 64, 'au passage piéton, elle s' + q + 'arrête avant les bandes');
  ok(run('P.hp') === run('P.hpMax'), 'Tecky n' + q + 'y est pas blessé');
  run('P.y = 17 * 64;'); const xs = run('V.x'); step(60);
  ok(run('V.x') > xs + 50, 'elle repart quand Tecky a traversé');
  // un chien sur la route est seulement écarté
  run('var R = new Actor("roquet", 45 * 64, 940); Object.assign(R, { T: DOGS.roquet, hp: 2, mode: "idle", timer: 9, hx: R.x, hy: R.y, kx: 0, ky: 0, cd: 0, barkCd: 9, chargeCd: 9, fade: 0 });' +
      'dogs = [R]; P.x = 5 * 64; P.y = 5 * 64; V.x = R.x - 400; V.v = V.T.spd;');
  step(150);
  ok(!run('inLane(V, R.y)') && run('R.hp') === 2, 'un chien sur la route est écarté, sans perdre de vie');
}, 50);`);
