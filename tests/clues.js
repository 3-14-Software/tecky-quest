// simulation : les trois indices d'Alice guident Tecky (flèche, répliques) ; Alice ne sort de la cabane qu'après
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; P.inv = 99;');
  const item = n => 'items.find(i => i.n === "' + n + '")';
  ok(run('alice.hidden') && run('arrowTarget() === ' + item('hairclip')), 'au départ : Alice cachée, la flèche montre la barrette');
  // la flèche : quelques secondes après l'intro, pas en permanence, rappel si on tourne en rond
  ok(run('arrowT') > 7, 'après l\\'intro, la flèche s\\'affiche (' + run('arrowT').toFixed(1) + ' s)');
  run('var calls = []; var drawSpr0 = drawSpr; drawSpr = function (k, f, x, y, o) { if (k.startsWith("hud/arrow")) calls.push([k, f, !!(o && o.angle)]); return drawSpr0.apply(this, arguments); };');
  run('calls = []; drawHUD();');
  ok(JSON.stringify(run('calls')) === JSON.stringify([['hud/arrow', run('calls[0] && calls[0][1]'), true], ['hud/arrow_icon', 0, false]]),
     'la pointe tourne, l\\'icône (la barrette) reste droite : ' + JSON.stringify(run('calls')));
  step(60 * 9);
  run('calls = []; drawHUD();');
  ok(run('arrowT') === 0 && run('calls.length') === 0, 'puis elle disparaît');
  step(60 * 37);
  ok(run('arrowT') > 0, 'elle revient en rappel quand Tecky tourne en rond (45 s sans indice)');
  step(60 * 6);
  ok(run('arrowT') === 0, 'et repart aussitôt');
  // devant la cachette trop tôt
  run('P.x = alice.x - 100; P.y = alice.y + 10; P.mode = "free";'); step(2);
  ok(run('state') === 'dialog' && /il me manque des indices/i.test(run('dialog.lines[0].text')), 'devant la cabane trop tôt : « il me manque des indices »');
  ok(!run('alice.found'), 'pas de fin sans les indices');
  advanceDialog(); step(30);
  ok(run('state') === 'play', 'la remarque ne revient pas en boucle');
  // la barrette
  const take = n => { run('var it = ' + item(n) + '; P.x = it.x; P.y = it.y + 30; P.mode = "free";'); step(2); };
  take('hairclip');
  ok(run('clues[0]') && run('dialog.lines[0].text') === run('CLUE_FOUND[0]') && run('dialog.lines[1].text') === run('CLUE_NEXT[1]'),
     'barrette : Tecky la reconnaît et dit où chercher ensuite (la forêt)');
  advanceDialog();
  ok(run('arrowTarget() === ' + item('shoe')) && run('arrowT') > 7, 'la flèche se montre à nouveau, vers la chaussure');
  run('calls = []; P.x = 5*64; P.y = 5*64; updateCamera(9); drawHUD();');
  ok(run('calls[1] && calls[1][1]') === 1, 'avec l\\'icône de la chaussure');
  // le doudou avant la chaussure : l'indice suivant reste la chaussure
  take('plush');
  ok(run('clues[2]') && run('dialog.lines[1].text') === run('CLUE_NEXT[1]'), 'doudou trouvé avant la chaussure : on renvoie vers la chaussure');
  advanceDialog();
  ok(run('alice.hidden'), 'Alice reste cachée avec deux indices');
  take('shoe');
  ok(!run('alice.hidden') && run('dialog.lines[1].text') === run('CLUE_NEXT[3]'), 'troisième indice : Alice sort de sa cachette');
  advanceDialog();
  ok(run('arrowTarget() === alice') && run('arrowT') > 7, 'la flèche montre Alice');
  run('calls = []; P.x = 5*64; P.y = 5*64; updateCamera(9); drawHUD(); drawSpr = drawSpr0;');
  ok(run('calls[1] && calls[1][1]') === 3, 'avec la tête d\\'Alice, à l\\'endroit');
  run('drawHUD()'); ok(true, 'HUD des indices');
  run('P.x = alice.x - 100; P.y = alice.y + 10; P.mode = "free";'); step(2);
  ok(run('alice.found') && run('Music.cur') === 'win', 'retrouvailles et fanfare');
}, 50);`);
