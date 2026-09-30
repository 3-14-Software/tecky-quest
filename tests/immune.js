// simulation : aboyer sur le doberman ne lui fait rien, la morsure oui
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('var M = dogs.find(d => d.kind === "molosse"); P.x = M.x - 150; P.y = M.y; P.dir = "right"; P.mode = "free"; P.inv = 99; P.cdBark = 0; pressed.bark = true;');
  const hp = run('M.hp'); step(2);
  ok(run('M.hp') === hp && run('M.mode') !== 'hurt', 'aboiement sans effet sur le doberman (PV ' + hp + ' -> ' + run('M.hp') + ')');
  ok(run('pops.some(p => p.word)'), 'bulle « Même pas peur ! »');
  step(60);
  ok(run('state') === 'dialog', 'Tecky explique qu\\'il faut le mordre');
  advanceDialog();
  run('var R = dogs.find(d => d.kind === "roquet"); P.x = R.x - 150; P.y = R.y; P.dir = "right"; P.mode = "free"; P.cdBark = 0; pressed.bark = true;');
  const rh = run('R.hp'); step(2);
  ok(run('R.hp') < rh, 'l\\'aboiement marche toujours sur le roquet');
  run('P.x = M.x - 60; P.y = M.y; P.dir = "right"; P.mode = "free"; P.cdBite = 0; pressed.bite = true;');
  const mh = run('M.hp'); step(20);
  ok(run('M.hp') < mh, 'la morsure blesse le doberman (PV ' + mh + ' -> ' + run('M.hp') + ')');
}, 50);`);
