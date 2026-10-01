// simulation : près d'un panneau, le bouton de morsure (C) devient « lire » ; mordre reste prioritaire si un chien menace
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  // on note les images du bouton de morsure dessinées par le HUD
  run('var frames = []; var drawSpr0 = drawSpr; drawSpr = function (k, f) { if (k === "hud/action") frames.push(f); return drawSpr0.apply(this, arguments); };');
  run('var S = MAP.signs[0], R = dogs.find(d => d.kind === "roquet"), all = dogs;');
  const place = 'P.x = S[0]; P.y = S[1] + 80; P.dir = "up"; P.mode = "free"; P.inv = 99; P.cdBite = 0; ';
  run(place + 'dogs = [];'); step(1);
  ok(run('biteAction()') === 'read' && run('hintText') !== null, 'près du panneau : C sert à lire, bulle « lire »');
  run('frames = []; drawHUD();');
  ok(run('frames.includes(6)') && !run('frames.includes(2)'), 'le bouton montre l\\'icône « lire » (images ' + run('JSON.stringify(frames)') + ')');
  run('document.documentElement = {}; touchMode = true; frames = []; drawHUD(); touchMode = false;');   // HUD tactile (le faux navigateur n'a pas de plein écran)
  ok(run('frames.includes(6)'), 'tactile : le bouton montre aussi l\\'icône « lire »');
  run('pressed.bite = true'); step(1);
  ok(run('state') === 'dialog' && run('dialog.lines[0].text') === run('S[2]'), 'C lit le panneau');
  ok(run('P.mode') === 'free', 'Tecky ne mord pas en lisant');
  advanceDialog(); step(5);
  ok(run('state') === 'play', 'fermer le panneau ne le rouvre pas');
  run('P.cdBite = 0.4; pressed.bite = true'); step(1);
  ok(run('state') === 'dialog', 'on peut lire même juste après une morsure');
  advanceDialog(); step(5);
  run('pressed.act = true'); step(1);
  ok(run('state') === 'dialog', 'E lit toujours le panneau');
  advanceDialog(); step(5);
  // loin du panneau : C mord
  run('P.x = S[0] + 400; P.mode = "free"; P.cdBite = 0;'); step(1);
  ok(run('biteAction()') === 'bite' && run('hintText') === null, 'loin du panneau : C mord');
  // chien menaçant près du panneau : C mord, pas de bulle « lire »
  run(place + 'dogs = [R]; R.x = R.hx = P.x + 70; R.y = R.hy = P.y; R.mode = "chase"; R.hp = R.T.hp; P.dir = "right";'); step(1);
  ok(run('biteAction()') === 'bite' && run('hintText') === null, 'chien menaçant : ni bouton ni bulle « lire »');
  run('pressed.bite = true'); step(1);
  ok(run('P.mode') === 'bite' && run('state') === 'play', 'chien menaçant près du panneau : C mord (mode ' + run('P.mode') + ')');
  run('dogs = all; drawSpr = drawSpr0;');
}, 50);`);
