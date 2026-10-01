// simulation : près d'un trésor, si un chien menace Tecky, C mord au lieu de gratter
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('var gd = digs[1], R = dogs.find(d => d.kind === "roquet"), all = dogs;');
  const place = 'P.x = gd.x; P.y = gd.y - 20; P.dir = "right"; P.mode = "free"; P.inv = 99; P.cdBite = 0; ';
  run(place + 'dogs = [];'); step(1);
  ok(run('digHint') !== null, 'sans chien : bulle « gratter » près du trésor');
  // chien lancé contre Tecky, tout proche (niche à côté, sinon il rentre chez lui) : C mord
  run(place + 'dogs = [R]; R.x = R.hx = P.x + 70; R.y = R.hy = P.y; R.mode = "chase"; R.hp = R.T.hp;'); step(1);
  ok(run('biteAction()') === 'bite' && run('digHint') === null, 'chien menaçant : ni bouton ni bulle « gratter »');
  run('pressed.bite = true'); step(1);
  ok(run('P.mode') === 'bite', 'chien menaçant près du trésor : C mord (mode ' + run('P.mode') + ')');
  step(20);
  ok(run('R.hp') < run('R.T.hp'), 'la morsure touche le chien (PV ' + run('R.T.hp') + ' -> ' + run('R.hp') + ')');
  ok(!run('gd.dug'), 'le trésor n\\'est pas gratté');
  // grattage commencé, puis un chien arrive : C interrompt le grattage pour mordre
  run(place + 'dogs = []; pressed.bite = true;'); step(1);
  ok(run('P.mode') === 'dig', 'sans chien : C gratte');
  step(10);
  run('dogs = [R]; R.x = R.hx = P.x + 70; R.y = R.hy = P.y; R.mode = "chase"; pressed.bite = true;'); step(1);
  ok(run('P.mode') === 'bite', 'un chien arrive pendant le grattage : C mord (mode ' + run('P.mode') + ')');
  // chien KO juste à côté : plus de menace, C gratte
  run(place + 'R.x = P.x + 70; R.y = P.y; R.mode = "ko"; R.timer = 0; pressed.bite = true;'); step(1);
  ok(run('P.mode') === 'dig', 'chien KO à côté : C gratte');
  step(70);
  ok(run('gd.dug'), 'trésor déterré une fois la menace écartée');
  run('dogs = all;');
}, 50);`);
