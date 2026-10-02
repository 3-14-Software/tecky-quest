// quête de Léon (le port) : ses cinq gros ballons ont roulé partout ; Tecky les pousse (en fonçant dedans ou en
// aboyant) dans le grand filet
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999;');
  ok(run('balls.length') === 5 && run('ballsLeft()') === 5 && run('fete.state') === 'new', 'cinq ballons, aucun dans le filet');
  ok(run('calmAt(leon.x, leon.y)') && run('zoneAt(leon.x, leon.y).id') === 'industrie', 'Léon vit au port, en zone calme');
  // Léon : il ne parle que si Tecky vient le voir
  run('P.x = leon.x; P.y = leon.y + 110; P.mode = "free"; pops = [];'); step(2);
  ok(run('pops.some(p => /mes ballons/.test(p.text))') && run('leonMark()') === 0, 'Tecky arrive : « Oh non, mes ballons ! », bulle « ! »');
  step(1); run('updateCamera(10)');
  ok(run('biteAction()') === 'talk', 'près de lui : C fait « Parler »');
  run('P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('state') === 'dialog' && run('dialog.lines[0].who') === 'leon' && /ballons/.test(run('dialog.lines[0].text')), 'il demande de l’aide');
  ok(run('WHO.leon.name') === 'Léon' && run('!!ATLAS[WHO.leon.portrait]'), 'son nom et son portrait');
  advanceDialog();
  ok(run('fete.state') === 'asked' && run('leonMark()') === 1, 'quête acceptée, bulle « ? »');
  run('var used = [], ds0 = drawSpr; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; drawHUD(); drawSpr = ds0;');
  ok(run('used.includes("port/balloon")'), 'compteur de ballons dans le HUD');
  // en fonçant dedans : le ballon roule devant Tecky… jusque dans le filet
  run('var B = balls[0], G = MAP.goal; B.x = G[0] + 40; B.y = G[1] + 100; P.x = G[0] + 40; P.y = G[1] + 170; P.dir = "up"; P.mode = "free"; graceT = 9;');
  let t = 0; while (!run('B.inNet') && t < 60 * 4) { step(1, 'held.up = true'); t++; }
  run('held.up = false;');
  ok(run('B.inNet'), 'Tecky pousse un ballon devant lui : but ! (' + (t / 60).toFixed(1) + ' s)');
  ok(run('pops.some(p => p.text === "But !")') && run('score') >= run('LEON.perBall'), '« But ! » et des points');
  step(60 * 2);
  ok(run('Math.abs(B.x - G[0]) < GOAL_IN[0] + 9 && B.y > G[1] + GOAL_IN[1] - 1 && B.y < G[1] + GOAL_IN[2] + 1'), 'il reste dans le filet');
  run('P.x = B.x; P.y = B.y + 8;'); step(30);
  ok(run('B.inNet') && Math.abs(run('B.vx')) + Math.abs(run('B.vy')) < 200, 'même si Tecky entre dans le filet');
  // en aboyant derrière : il part loin, guidé vers l'ouverture
  run('var C = balls[1]; C.x = G[0] - 130; C.y = G[1] + 110; P.x = G[0] - 150; P.y = G[1] + 180; P.dir = "up"; P.mode = "free"; P.cdBark = 0; P.inv = 999;');
  run('pressed.bark = true'); step(1);
  ok(run('C.vy') < -150, 'un aboiement derrière lui le fait rouler');
  step(60 * 3);
  ok(run('C.inNet'), 'jusque dans le filet (guidé vers l’ouverture)');
  // jamais sur la route, et il rebondit sur les obstacles
  run('var D = balls[2]; D.x = 30.5 * 64; D.y = 17.0 * 64; D.vx = 0; D.vy = -600; D.inNet = false; P.x = 10 * 64; P.y = 5 * 64;'); step(60);
  ok(run('D.y') > 16.5 * 64, 'il ne roule jamais sur la grande route');
  const bx = run('MAP.decor.find(d => d[0] === "truck")');
  run(`D.x = ${bx[1]}; D.y = ${bx[2]} + 60; D.vx = 0; D.vy = -500;`); step(20);
  ok(run('D.vy') > 0 || run('D.y') > bx[2], 'il rebondit sur le camion');
  // sauvegarde : positions et ballons rentrés
  run('saveGame(); var sv = STORE.get(SAVE_KEY);');
  ok(run('sv.fete') === 'asked' && run('sv.balls[0][2]') === 1 && run('sv.balls[2][2]') === 0, 'sauvegardés (quête, ballons rentrés)');
  run('var dx2 = D.x, dy2 = D.y; toTitle(); loadGame(STORE.get(SAVE_KEY), false);'); advanceDialog();
  ok(run('fete.state') === 'asked' && run('balls[0].inNet') && Math.abs(run('balls[2].x - dx2')) < 1, 'Continuer : tout est à sa place');
  // tous dans le filet : Léon appelle, puis remercie (un os, des points), badge
  run('dogs = []; cars = []; P.inv = 999; balls.forEach(b => { if (!b.inNet) { b.x = MAP.goal[0]; b.y = MAP.goal[1] - 20; b.vx = 0; b.vy = -40; } }); pops = [];');
  step(2);
  ok(run('ballsLeft()') === 0 && run('pops.some(p => /Viens me voir/.test(p.text))'), 'le dernier ballon rentré : « Bravo, champion ! Viens me voir ! »');
  run('P.x = leon.x; P.y = leon.y + 110; P.mode = "free"; var sc0 = score, n0 = items.length;'); step(2);
  run('P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('state') === 'dialog' && /Cinq buts/.test(run('dialog.lines[0].text')), 'Léon remercie Tecky');
  advanceDialog();
  ok(run('fete.state') === 'done' && run('score') === run('sc0 + LEON.reward') && run('items.length') === run('n0 + 1'), 'un os et des points');
  ok(run('leonMark()') === -1, 'plus de bulle au-dessus de sa tête');
  step(40);
  ok(run('!!badges.ballons'), 'badge « Champion du ballon »');
  ok(run('QUESTS_DONE.length') >= 4 && run('QUESTS_DONE[3]()'), 'compté dans la complétion');
  run('P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('state') === 'dialog' && /Merci encore/.test(run('dialog.lines[0].text')), 'ensuite : « Merci encore, champion ! »');
  advanceDialog();
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
