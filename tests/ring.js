// simulation : les aboiements (Tecky et doberman) dessinent une onde qui montre leur portée réelle
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('var all = dogs; dogs = []; P.x = 5*64; P.y = 9*64; P.dir = "right"; P.mode = "free"; P.cdBark = 0; P.inv = 99; pressed.bark = true;');
  step(1);
  ok(run('rings.length') === 1 && run('rings[0].range') === run('BARK.range') && run('rings[0].ang') === 0,
     'Tecky aboie : une onde vers la droite, portée ' + run('rings[0] && rings[0].range'));
  ok(Math.abs(run('Math.cos(rings[0].half)') - run('BARK.cos')) < 1e-9, 'l\\'onde couvre exactement le cône touché');
  step(6);
  ok(run('rings.length') === 1, 'l\\'onde est encore là pendant qu\\'elle s\\'étend');
  step(30);
  ok(run('rings.length') === 0, 'puis elle disparaît');
  // le doberman aboie quand Tecky est à distance moyenne
  run('var M = all.find(d => d.kind === "molosse"); dogs = [M]; M.x = M.hx; M.y = M.hy; M.mode = "chase"; M.barkCd = 0; M.cd = 9; P.x = M.x - 220; P.y = M.y; P.inv = 99; P.mode = "free";');
  let seen = false;
  for (let i = 0; i < 60 && !seen; i++) { step(1); seen = run('rings.some(r => r.range === DOG_BARK.range)'); }
  ok(seen, 'le doberman aboie : onde rouge à sa portée (' + run('DOG_BARK.range') + ' px)');
  ok(run('rings.find(r => r.range === DOG_BARK.range).color') === '#D7332B', 'onde ennemie en rouge');
  run('dogs = all;');
}, 50);`);
