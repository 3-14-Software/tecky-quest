// terriers sous les grillages, flair (piste de pieds nus vers le prochain indice), os dorés dans les trous
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; P.inv = 999; farm.state = "done";');
  ok(run('MAP.tunnels.length') >= 3 && run('ATLAS["decor/burrow"] !== undefined'), run('MAP.tunnels.length') + ' terriers, chacun marqué aux deux bouts');
  // terrier zone industrielle <-> verger : le grillage bloque le passage direct
  run('var TN = MAP.tunnels[0]; P.x = TN[0]; P.y = TN[1]; P.mode = "free"; var x0 = P.x;');
  step(60, 'held.right = true'); run('held.right = false');
  ok(run('P.x') < run('TN[2]') - 20, 'le grillage bloque Tecky (' + Math.round(run('P.x - x0')) + ' px)');
  run('P.x = TN[0]; P.y = TN[1]; P.mode = "free";'); step(1);
  ok(run('biteAction()') === 'tunnel' && run('tunnelHint !== null'), 'près du terrier : « Passer »');
  run('P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('P.mode') === 'tunnel', 'Tecky gratte le terrier');
  let hidden = false;
  for (let i = 0; i < 90 && run('P.mode') === 'tunnel'; i++) { step(1); if (run('P.alpha') === 0) hidden = true; }
  ok(hidden, 'il disparaît sous le grillage');
  ok(Math.abs(run('P.x') - run('TN[2]')) < 1 && Math.abs(run('P.y') - run('TN[3]')) < 1, 'et ressort de l’autre côté');
  ok(run('state') === 'dialog' && /terrier/.test(run('dialog.lines[0].text')), 'la première fois, Tecky explique');
  advanceDialog();
  ok(run('P.alpha') === 1 && run('P.sy') === undefined && run('P.mode') === 'free', 'il repart normalement');
  run('P.cdBite = 0; pressed.bite = true'); step(80);
  ok(Math.abs(run('P.x') - run('TN[0]')) < 1 && run('state') === 'play', 'retour par le même terrier, sans nouvelle explication');
  // tous les terriers, dans les deux sens (trois d'entre eux sont verticaux : même x aux deux bouts)
  const nT = run('MAP.tunnels.length');
  run('var dug0 = digs.map(g => g.dug); digs.forEach(g => g.dug = true);');   // (un trésor près d'un bout passerait avant)
  for (let k = 0; k < nT; k++) for (const [a, b] of [[0, 2], [2, 0]]) {
    run(`var T2 = MAP.tunnels[${k}]; P.x = T2[${a}]; P.y = T2[${a + 1}]; P.mode = "free"; P.cdBite = 0; state = "play"; dialog = null; pressed.bite = true`);
    step(80); if (run('state') === 'dialog') advanceDialog();
    ok(Math.abs(run(`P.x - T2[${b}]`)) < 1 && Math.abs(run(`P.y - T2[${b + 1}]`)) < 1 && run('P.mode') === 'free',
       'terrier ' + (k + 1) + (a ? ' (retour)' : ' (aller)') + ' : Tecky ressort de l’autre côté');
  }
  run('digs.forEach((g, i) => g.dug = dug0[i]);');
  // un chien qui le poursuit doit faire le tour
  run('var D = new Actor("roquet", TN[0] - 60, TN[1]); Object.assign(D, { id: 99, T: DOGS.roquet, hp: 2, mode: "chase", timer: 0, hx: D.x, hy: D.y, vx: 0, vy: 0, kx: 0, ky: 0, cd: 9, barkCd: 9, chargeCd: 9, hitDone: false, fade: 0 }); dogs = [D];');
  run('P.x = TN[0]; P.y = TN[1]; P.mode = "free"; P.cdBite = 0; pressed.bite = true'); step(80);
  ok(run('D.x') < run('TN[2]') - 30, 'le chien reste de son côté du grillage');
  run('dogs = []');
  // priorités du bouton : trésor > terrier > panneau
  run('var g0 = digs[0]; P.x = g0.x; P.y = g0.y; MAP.tunnels.push([g0.x + 20, g0.y, g0.x + 20, g0.y + 300]);');
  ok(run('biteAction()') === 'dig', 'près d’un trésor et d’un terrier : on gratte le trésor d’abord');
  run('MAP.tunnels.pop()');

  // flair : piste de pieds nus vers le prochain indice (la barrette, à la ferme)
  run('P.x = MAP.start[0]; P.y = MAP.start[1] + 40; P.mode = "free"; P.cdSniff = 0; trail = []; pressed.sniff = true'); step(1);
  ok(run('P.mode') === 'sniff' && run('pops.some(p => /Snif/.test(p.text))'), 'R : Tecky flaire (« Snif snif… »)');
  step(50);
  const n = run('trail.length');
  ok(n > 20, 'une piste apparaît (' + n + ' empreintes)');
  ok(run('trail.every(f => !blockedPoint(f.x, f.y))'), 'jamais dans l’eau ni dans un obstacle');
  ok(run('dist(trail[0].x, trail[0].y, P.x, P.y)') < 80, 'elle part des pattes de Tecky');
  ok(run('trail.every((f, i) => i === 0 || dist(f.x, f.y, trail[i - 1].x, trail[i - 1].y) < 60)'), 'empreintes régulières, sans saut');
  ok(run('trail.some(f => f.foot === 0) && trail.some(f => f.foot === 1)'), 'pied gauche, pied droit');
  run('var fd = fieldTo(arrowTarget().x, arrowTarget().y), W = walkGrid.W; var cell = (x, y) => fd[Math.floor(y / 16) * W + Math.floor(x / 16)];');
  ok(run('cell(trail[trail.length - 1].x, trail[trail.length - 1].y) < cell(P.x, P.y)'), 'elle se rapproche de la barrette (par un vrai chemin)');
  ok(run('trail.some(f => f.t < 0)'), 'les empreintes apparaissent une à une');
  run('pressed.sniff = true'); step(1);
  ok(run('P.mode') === 'free', 'pas de nouveau flair tout de suite (recharge)');
  step(60 * 9);
  ok(run('trail.length') === 0, 'la piste s’efface');
  // trésors proches : ils scintillent
  run('var g1 = digs.find(g => !g.dug); P.x = g1.x + 200; P.y = g1.y; P.cdSniff = 0; fxs = []; pressed.sniff = true'); step(50);
  ok(run('fxs.some(f => f.key === "fx/pickup" && f.x === g1.x)'), 'flairer fait scintiller les trésors proches');
  // après les trois indices : vers Alice
  run('clues = [true, true, true]; revealAlice(); P.x = 30 * 64; P.y = 36 * 64; P.cdSniff = 0; pressed.sniff = true'); step(50);
  ok(run('arrowTarget() === alice') && run('trail.length') > 5, 'trois indices : la piste mène à Alice');
  run('var fa = fieldTo(alice.x, alice.y);');
  ok(run('fa[Math.floor(trail[trail.length - 1].y / 16) * W + Math.floor(trail[trail.length - 1].x / 16)] < fa[Math.floor(P.y / 16) * W + Math.floor(P.x / 16)]'),
     'elle se rapproche de la cabane');
  run('drawTrail()');

  // os dorés : le trésor sous les traces de pattes
  ok(run('treasures') > 0 || !run('hudCounters().some(c => c[0] === "item/goldbone")'), 'pas de compteur d’os dorés avant le premier');
  run('clues = [false, false, false]; var g2 = digs.find(g => !g.dug); P.x = g2.x; P.y = g2.y - 20; P.mode = "free"; P.cdBite = 0; P.dir = "down"; var t0 = treasures, s0 = score; pressed.bite = true;');
  step(70);
  ok(run('treasures') === run('t0') + 1 && run('items.some(i => i.n === "goldbone")') || run('score') > run('s0') + 100,
     'un os doré jaillit du trou');
  ok(run('state') === 'dialog' && /os doré/.test(run('dialog.lines[0].text')), 'Tecky : « Un os doré était enterré ! »');
  advanceDialog(); step(40);
  ok(!run('items.some(i => i.n === "goldbone")') && run('score') === run('s0') + 200, 'ramassé : +200 en tout');
  run('var used = []; var ds0 = drawSpr; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; drawHUD(); drawSpr = ds0;');
  ok(run('used.includes("item/goldbone")') && run('hudCounters()[0][0]') === 'item/goldbone', 'compteur d’os dorés dans le HUD, en haut de la colonne');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
