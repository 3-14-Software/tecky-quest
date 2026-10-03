// canards : ils nagent sans quitter l'eau, s'envolent quand Tecky approche ou aboie, se reposent plus loin ;
// la cane et ses canetons s'éloignent à la nage, en file
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999; farm.state = "done";');
  ok(run('ducks.length') >= 8 && run('ducks.some(d => d.kind === "duck") && ducks.some(d => d.kind === "duck_f")') &&
     run('ducks.filter(d => d.kind === "duckling").length') >= 3, run('ducks.length') + ' canards, dont des canetons');
  ok(run('ducks.filter(d => d.kind === "duckling").every(d => d.lead)'), 'chaque caneton suit quelqu’un');
  ok(run('ducks.every(d => duckWater(d, d.x, d.y))'), 'tous sur l’eau au départ');
  // Tecky loin de tout : ils nagent, cancanent, plongent, sans jamais quitter l'eau
  run('P.x = 46 * 64; P.y = 26 * 64; P.mode = "free"; var anims = {}, dry = 0;');
  for (let i = 0; i < 60 * 25; i++) {
    step(1);
    if (i % 10 === 0) run('for (const d of ducks) { anims[d.anim] = 1; if (!duckWater(d, d.x, d.y)) dry++; }');
  }
  ok(run('dry') === 0, 'en 25 s, aucun ne quitte l’eau');
  ok(run('anims.quack') && run('anims.dive'), 'ils cancanent et plongent');
  ok(run('ducks.filter(d => !d.lead).every(d => dist(d.x, d.y, d.hx, d.hy) < DUCK.roam + 40)'), 'ils restent près de leur place');
  ok(run('ducks.filter(d => d.lead).every(d => dist(d.x, d.y, d.lead.x, d.lead.y) < DUCK.gap * 2 + 12)'), 'les canetons suivent en file');

  // un canard seul sur la rivière : Tecky approche, il s'envole
  run('var D = ducks.find(d => d.kind === "duck" && !d.hasKids && d.y > 42 * 64 && d.y < 45 * 64); var s0 = score;');
  run('P.x = D.x; P.y = 41.4 * 64; P.mode = "free";');
  ok(!run('blockedFeet(P.x, P.y, 16)'), 'Tecky sur la berge');
  step(30);
  ok(run('D.mode') === 'fly' && run('D.h') > 20, 'Tecky approche : le canard s’envole (' + Math.round(run('D.h')) + ' px)');
  ok(run('D.scored') && run('score') >= run('s0') + run('DUCK.pts') && run('pops.some(p => /Coin coin/.test(p.text))'), '+' + run('DUCK.pts') + ' et « Coin coin ! »');
  run('var used = []; var ds0 = drawSpr; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; render(); drawSpr = ds0;');
  ok(run('used.includes("duck/fly")'), 'sprite en vol dessiné');
  { let k = 0; while (run('D.mode') !== 'swim' && k++ < 60 * 10) step(1); }
  ok(run('D.mode') === 'swim' && run('D.h') === 0 && run('duckWater(D, D.x, D.y)'), 'il se repose sur l’eau');
  ok(run('dist(D.x, D.y, P.x, P.y)') > run('DUCK.scare'), 'loin de Tecky (' + Math.round(run('dist(D.x, D.y, P.x, P.y)')) + ' px)');
  run('s0 = score; P.x = D.x; P.y = D.y - 150;'); if (run('blockedFeet(P.x, P.y, 16)')) run('P.y = D.y + 150');
  { let k = 0; while (run('D.mode') === 'swim' && k++ < 60) step(1); }
  ok(run('score') === run('s0'), 'la deuxième fois : plus de points');

  // la cane et ses canetons : à la nage, pas d'envol
  run('P.x = 46 * 64; P.y = 26 * 64;'); step(60 * 12);
  run('var M = ducks.find(d => d.hasKids); var kids = ducks.filter(d => d.lead && d.fam === M.fam); P.x = M.x; P.y = M.y + 150; P.mode = "free";');
  if (run('blockedFeet(P.x, P.y, 16)')) run('P.y = M.y - 150');
  step(20);
  ok(run('M.mode') === 'flee' && run('M.h') === 0, 'la cane s’éloigne à la nage, sans s’envoler');
  run('var k0 = dist(M.x, M.y, P.x, P.y);'); step(60 * 2);
  ok(run('dist(M.x, M.y, P.x, P.y)') > run('k0') + 20 && run('kids.every(k => k.mode === "flee")'), 'ses petits la suivent');
  ok(run('[M].concat(kids).every(d => duckWater(d, d.x, d.y))'), 'toujours dans l’eau');
  run('P.x = 46 * 64; P.y = 26 * 64;'); step(60 * 5);
  ok(run('M.mode') === 'swim' && run('kids.every(k => k.mode === "swim")'), 'Tecky parti : ils se calment');
  // coincée contre la rive de la petite mare de la niche : toute la famille s'envole vers une autre mare (les canetons en
  // file, ailerons battants) et s'y pose, au lieu de tourner sur place
  run('var F = MAP.ducks.find(d => d[0] === "duck_f" && d[3] === 1), M1 = ducks.find(d => d.hasKids && d.fam === F[3]), kids1 = ducks.filter(d => d.lead && d.fam === F[3]);');
  run('M1.mode = "swim"; M1.h = 0; M1.chk = null; M1.x = M1.hx = F[1]; M1.y = M1.hy = F[2]; kids1.forEach(k => { k.mode = "swim"; k.h = 0; k.x = M1.x; k.y = M1.y; }); P.x = M1.x + 80; P.y = M1.y + 60; P.mode = "free";');
  let flew = false, kidsFlew = false, turns = [], maxTurns = 0, fl0 = run('M1.flip');
  for (let i = 0; i < 60 * 14; i++) {
    if (!flew) run('var dd = dist(M1.x, M1.y, P.x, P.y); if (dd > 110) { P.x += (M1.x - P.x) / dd * 3; P.y += (M1.y - P.y) / dd * 3; }');
    step(1);
    if (run('M1.mode') === 'fly') flew = true;
    if (run('kids1.every(k => k.mode === "fly" && k.anim === "fly")')) kidsFlew = true;
    const f = run('M1.flip'); turns.push(f !== fl0 ? 1 : 0); fl0 = f; if (turns.length > 60) turns.shift();
    if (!flew) maxTurns = Math.max(maxTurns, turns.reduce((a, v) => a + v, 0));
  }
  ok(maxTurns <= 3, 'coincée, elle ne tourne plus sur place (' + maxTurns + ' demi-tours par seconde au plus)');
  ok(flew && kidsFlew, 'elle s’envole, ses canetons derrière elle');
  ok(run('M1.mode') === 'swim' && run('M1.h') === 0 && run('duckWater(M1, M1.x, M1.y)') && run('dist(M1.x, M1.y, F[1], F[2])') > 300,
     'et se pose sur une autre mare (' + Math.round(run('dist(M1.x, M1.y, F[1], F[2])')) + ' px plus loin)');
  ok(run('kids1.every(k => k.h === 0 && duckWater(k, k.x, k.y) && dist(k.x, k.y, M1.x, M1.y) < 140)'), 'ses petits se posent avec elle');

  // aboyer de loin fait aussi s'envoler
  run('var E = ducks.find(d => d.kind === "duck" && !d.hasKids && d !== D && d.mode === "swim"); P.x = E.x - 280; P.y = E.y; P.dir = "right"; P.mode = "free"; P.cdBark = 0;');
  if (run('blockedFeet(P.x, P.y, 16)')) run('P.x = E.x; P.y = E.y - 280; P.dir = "down";');
  if (run('blockedFeet(P.x, P.y, 16)')) run('P.x = E.x; P.y = E.y + 280; P.dir = "up";');
  run('pressed.bark = true'); step(2);
  ok(run('E.mode') === 'fly', 'aboiement : il s’envole');

  // sauvegarde
  run('saveGame(); var SV = loadSave();');
  ok(run('SV.ducks.split("").filter(x => x === "1").length') === run('ducks.filter(d => d.scored).length') && run('ducks.filter(d => d.scored).length') >= 3,
     'la sauvegarde retient les canards déjà envolés');
  run('loadGame(SV, false)'); advanceDialog();
  ok(run('ducks.filter(d => d.scored).length') >= 3, 'Continuer : ils restent comptés');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
