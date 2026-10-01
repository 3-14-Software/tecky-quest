// simulation : le chien de berger s'accroupit (« ! »), charge en ligne droite, puis souffle ; on peut l'esquiver
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  // terrain dégagé : la route principale, à l'est du village
  run('var B = dogs.find(d => d.kind === "berger"); dogs = [B];');
  const setup = 'P.x = 46*64; P.y = 13.5*64; P.mode = "free"; P.inv = 0; P.hp = P.hpMax; P.kx = P.ky = 0;' +
                'B.x = B.hx = P.x + 230; B.y = B.hy = P.y; B.mode = "chase"; B.chargeCd = 0; B.cd = 9; B.kx = B.ky = 0;';
  run(setup); step(1);
  ok(run('B.mode') === 'crouch' && run('pops.some(p => p.text === "!")'), 'à bonne distance : il s\\'accroupit et prévient « ! »');
  let modes = new Set(), hp0 = run('P.hp');
  for (let i = 0; i < 90; i++) { step(1); modes.add(run('B.mode')); }
  ok(modes.has('charge') && modes.has('tired'), 'puis il charge et souffle (' + [...modes].join(', ') + ')');
  ok(run('P.hp') < hp0, 'Tecky resté sur la trajectoire est touché (PV ' + hp0 + ' -> ' + run('P.hp') + ')');
  // esquive : Tecky s'écarte pendant que le chien s'accroupit
  run(setup); step(1);
  ok(run('B.mode') === 'crouch', 'nouvelle charge annoncée');
  run('P.y -= 110; P.inv = 0;'); hp0 = run('P.hp');
  let hit = false;
  for (let i = 0; i < 40; i++) { step(1); if (run('P.hp') < hp0) hit = true; }
  ok(!hit, 'en s\\'écartant à temps, Tecky esquive la charge');
  // un aboiement pendant qu'il s'accroupit l'interrompt
  run(setup + 'P.dir = "right";'); step(1);
  run('P.cdBark = 0; pressed.bark = true'); step(1);
  ok(run('B.mode') === 'hurt', 'aboyer sur le berger accroupi annule sa charge');
  // pas de charge à travers un obstacle
  run('P.x = 56*64; P.y = 10.8*64; P.mode = "free"; B.x = B.hx = 56*64; B.y = B.hy = 1.8*64; B.mode = "chase"; B.chargeCd = 0; B.cd = 9;');
  ok(!run('clearPath(B.x, B.y, P.x, P.y)'), 'la grange bloque la ligne droite');
}, 50);`);
