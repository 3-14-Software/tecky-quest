// mode balade : personne ne se fait mal ; les chiens attendent qu'on joue avec eux, puis deviennent des copains
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); menu.sel = menu.items.findIndex(i => i.id === "balade"); pressed.ok = true'); step(1);
  ok(run('gameMode') === 'balade' && /envie de jouer/.test(run('dialog.lines[2].text')), 'nouvelle balade : l’intro annonce des chiens joueurs');
  ok(/C sert à jouer avec lui/.test(run('dialog.lines[5].text')), 'l’intro explique comment jouer avec un chien');
  advanceDialog();
  // aucun chien ne perd jamais de vie dans ce test
  run('var hurt = false; var hd0 = hurtDog; hurtDog = function (d) { hurt = true; return hd0.apply(this, arguments); };');
  const hp = run('P.hp');

  // (8, 5) : ligne droite dégagée sur 300 px de chaque côté
  run('P.x = 8 * 64; P.y = 5 * 64 + 32; P.mode = "free";');
  // un bouledogue vient, attend en sautillant, puis rentre si on ne joue pas
  run('var B = dogs.find(d => d.kind === "bouledogue"); B.hx = B.x = P.x + 220; B.hy = B.y = P.y; B.mode = "idle"; var modes = new Set(), hops = 0;');
  for (let i = 0; i < 60 * 12; i++) { step(1); run('modes.add(B.mode); if (B.hop > 4) hops++;'); }
  ok(run('P.hp') === hp, 'aucun dégât en 12 s collé au bouledogue');
  ok(run('modes.has("wait")') && !run('modes.has("attack")') && !run('modes.has("play")'),
     'il vient attendre que Tecky joue, sans mordre (' + run('[...modes].join(", ")') + ')');
  ok(run('hops') > 10, 'il sautille d’impatience');
  ok(run('modes.has("return")'), 'sans partie de jeu, il finit par rentrer chez lui');

  // aboyer appelle les chiens : pas de dégâts, pas de recul, un cœur, et il accourt
  run('B.x = B.hx = 3000; P.x = 8 * 64; P.y = 5 * 64 + 32;');
  // les autres chiens restent chez eux (un roquet qui flâne non loin viendrait sinon attendre lui aussi)
  run('dogs.forEach(d => { d.x = d.hx; d.y = d.hy; d.mode = "idle"; d.calm = 999; });');
  run('var R = dogs.find(d => d.kind === "roquet" && d !== B); R.hx = R.x = P.x + 230; R.hy = R.y = P.y; R.mode = "idle"; R.calm = 5;' +
      'P.dir = "right"; P.mode = "free"; P.cdBark = 0; fxs = []; pressed.bark = true');
  step(1);
  ok(run('R.hp') === run('R.T.hp') && run('Math.abs(R.kx)') < 1 && run('R.mode') === 'chase' && run('R.calm') === 0,
     'aboiement : le roquet n’est ni blessé ni repoussé, il accourt');
  ok(run('fxs.some(f => f.key === "fx/heart")'), 'il répond par un cœur');
  { let k = 0; while (run('R.mode') !== 'wait' && k++ < 180) step(1); }
  ok(run('R.mode') === 'wait', 'il arrive près de Tecky et attend');
  // C près de lui : « Jouer »
  ok(run('biteAction()') === 'play' && run('playDog() === R'), 'près d’un chien, le bouton de morsure devient « Jouer »');
  run('var sc0 = score, f0 = fled; P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('P.mode') === 'play' && run('R.mode') === 'play', 'Tecky et le roquet jouent ensemble');
  step(30);
  ok(run('P.hop') > 0 || run('R.hop') > 0, 'ils sautillent');
  step(Math.ceil(60 * run('PLAY.time')));
  ok(run('R.friend') && run('fled') === run('f0') + 1 && run('score') === run('sc0') + run('R.T.score'),
     'le roquet devient un copain (+' + run('R.T.score') + ' points)');
  ok(run('pops.some(p => p.word && p.text === "Copain !")'), 'bulle « Copain ! »');
  ok(run('P.mode') === 'free', 'Tecky peut repartir');
  // un copain ne poursuit plus Tecky, mais lui fait la fête quand il passe (les autres chiens restent chez eux)
  run('dogs.forEach(d => { if (d !== R) { d.x = d.hx; d.y = d.hy; d.mode = "idle"; d.calm = 99; } });');
  run('R.x = R.hx; R.y = R.hy; R.mode = "idle"; R.calm = 0; P.x = R.hx - 240; P.y = R.hy; var rm = new Set();');
  for (let i = 0; i < 60 * 12; i++) { step(1); run('rm.add(R.mode)'); }
  ok(!run('rm.has("chase")') && !run('rm.has("wait")'), 'un copain ne vient plus de lui-même (' + run('[...rm].join(", ")') + ')');
  run('R.x = R.hx; R.y = R.hy; R.mode = "idle"; P.x = R.hx - 100; P.y = R.hy; var nh = 0;');
  for (let i = 0; i < 60 * 3; i++) { step(1); run('nh = Math.max(nh, fxs.filter(f => f.key === "fx/heart").length)'); }
  ok(run('nh') > 0 && run('R.dir') === 'left', 'mais il lui fait la fête quand il passe');
  // rejouer avec un copain : pas de nouveaux points (canards et petites bêtes écartés : la 1re fois, ils en rapportent)
  run('ducks = []; critters = []; sc0 = score; P.mode = "free"; P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('R.mode') === 'play', 'on peut rejouer avec un copain');
  step(60 * 3);
  ok(run('score') === run('sc0'), 'sans regagner de points');

  // morsure dans le vide : jamais de dégâts, même avec un chien dans la gueule
  run('var Q = dogs.find(d => d.kind === "roquet" && !d.friend && d !== B); P.mode = "free"; Q.x = P.x + 60; Q.y = P.y; P.dir = "right"; doBite();');
  ok(run('Q.hp') === run('Q.T.hp'), 'doBite ne blesse personne en balade');

  // priorités : un nouveau chien passe avant le trésor, un copain après
  run('var gd = digs.find(g => !g.dug); P.x = gd.x; P.y = gd.y - 20; P.mode = "free"; Q.x = gd.x + 70; Q.y = gd.y; Q.mode = "wait"; Q.wait = 0; R.x = 9999;');
  ok(run('biteAction()') === 'play', 'chien pas encore copain près d’un trésor : « Jouer » d’abord');
  run('Q.friend = true');
  ok(run('biteAction()') === 'dig', 'copain près d’un trésor : « Gratter » d’abord');
  run('Q.friend = false; Q.x = Q.hx; Q.y = Q.hy; Q.mode = "idle";');

  // doberman : appelé, il vient sans « Même pas peur » ; il n'aboie pas ; berger : pas de charge
  run('var M = dogs.find(d => d.kind === "molosse"), G = dogs.find(d => d.kind === "berger"); var mm = new Set(), gm = new Set();');
  run('P.x = M.hx - 200; P.y = M.hy; M.x = M.hx; M.y = M.hy; M.mode = "idle"; M.barkCd = 0; P.dir = "right"; P.mode = "free"; P.cdBark = 0; pressed.bark = true; pops = [];');
  step(1);
  ok(!run('pops.some(p => p.text === "Même pas peur !")') && !run('pendingSay') && run('M.mode') === 'chase', 'doberman appelé : il accourt, sans « Même pas peur »');
  for (const [v, set] of [['M', 'mm'], ['G', 'gm']]) {
    run(`P.x = ${v}.hx - 220; P.y = ${v}.hy; P.mode = "free"; ${v}.x = ${v}.hx; ${v}.y = ${v}.hy; ${v}.mode = "idle"; ${v}.calm = 0; ${v}.barkCd = 0; ${v}.chargeCd = 0;`);
    for (let i = 0; i < 60 * 6; i++) { step(1); run(`${set}.add(${v}.mode)`); }
  }
  ok(!run('mm.has("bark")') && run('mm.has("wait")'), 'doberman : il vient sans aboyer (' + run('[...mm].join(", ")') + ')');
  ok(!run('gm.has("crouch")') && !run('gm.has("charge")') && run('gm.has("wait")'), 'berger : il vient sans charger (' + run('[...gm].join(", ")') + ')');
  ok(run('rings.every(r => r.color !== "#D7332B")'), 'aucune onde rouge d’aboiement de chien');
  ok(!run('threatened()'), 'pas de menace en balade');

  // les copains sont gardés dans la sauvegarde
  run('saveGame(); var s = loadSave(); loadGame(s, false);'); advanceDialog();
  ok(run('dogs.find(d => d.id === R.id).friend') && run('dogs.filter(d => d.friend).length') === 1 && run('gameMode') === 'balade',
     'Continuer : le roquet est toujours un copain');
  run('hurtPlayer(9, P.x + 10, P.y)');
  ok(run('P.hp') === hp, 'hurtPlayer est sans effet en balade');
  ok(!run('hurt'), 'aucun chien blessé de toute la balade');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
