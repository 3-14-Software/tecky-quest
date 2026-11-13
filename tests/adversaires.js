// les adversaires de la côte, avec les chiens : les crabes de la plage (ils pincent si Tecky leur marche dessus, ils
// s'enterrent quand il aboie) et les goélands (ils piquent du ciel, un aboiement les fait repartir).
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('EPISODES[1].chantier = false; audioOn(); STORE.mem = {}; loadBadges(); episode = "ete"; newGame("aventure", true);'); advanceDialog();
  run('cars = []; dogs = []; critters = []; ducks = []; items = []; var T = MAP.ts; function va(x, y) { P.x = x; P.y = y; P.mode = "free"; P.inv = 0; P.kx = P.ky = 0; graceT = 0; syncSwim(true); }');
  run('function seul(a) { crabs.forEach(c => { if (c !== a) { c.x = c.hx = -9999; } }); seagulls.forEach(g => { if (g !== a) { g.hx = g.x = -9999; g.cd = 999; } }); }');
  ok(run('crabs.length') === run('MAP.crabs.length') && run('crabs.length') >= 5 && run('seagulls.length') >= 4
     && run('crabs.every(c => sandAt(c.x, c.y) && !calmAt(c.x, c.y) && !waterAt(c.x, c.y))') && run('seagulls.every(g => !calmAt(g.hx, g.hy) && g.mode === "soar" && g.h === SEAGULL.alt)'),
     'la côte a ' + run('crabs.length') + ' crabes sur le sable et ' + run('seagulls.length') + ' goélands dans le ciel, aucun en zone calme');
  ok(Object.keys(run('MAP.crabAnims')).every(a => run(`ATLAS["crab/${a}"].f.length === MAP.crabAnims["${a}"][2]`))
     && ['glide', 'flap', 'cry', 'dive', 'idle'].every(a => run(`!!ATLAS["seagull/${a}"] && MAP.seagullFps["${a}"] > 0`))
     && ['idle', 'walk', 'menace', 'pinch', 'wave', 'bury', 'unbury', 'buried'].every(a => run(`!!ATLAS["crab/${a}"]`)),
     'ils ont leurs dessins : le crabe (huit animations), le goéland (plané, battement, cri, piqué, posé)');
  // ---- un crabe
  run('var c = crabs[0]; seul(c); va(c.x - 400, c.y); var x0 = c.x; c.timer = 0.01;'); step(60 * 4);
  ok(run('c.mode') === 'roam' && run('Math.abs(c.y - c.hy) < 0.01') && run('Math.abs(c.x - c.hx) <= CRAB.range + 1') && run('sandAt(c.x, c.y)') && run('c.x !== x0'),
     'loin de Tecky, un crabe va et vient en crabe (de côté), sur le sable');
  run('pops = []; pendingSay = null; va(c.x - 100, c.y);'); step(3);
  ok(run('c.mode') === 'menace' && run('c.anim') === 'menace' && run('pops.some(p => p.text === txt("crabe.clac") && p.who === "crab")') && run('crabSeen'),
     'Tecky approche : il lève ses pinces et les fait claquer (« ' + run('txt("crabe.clac")') + ' »)');
  step(40);
  ok(run('state') === 'dialog' && run('dialog.lines[0].text') === run('txt("tecky.crabe")'), 'la première fois, Tecky explique : « ' + run('dialog.lines[0].text') + ' »');
  advanceDialog();
  run('var hp = P.hp; va(c.x - 20, c.y); pops = [];'); step(2);
  ok(run('P.hp') === run('hp - CRAB.dmg') && run('c.anim') === 'pinch' && run('!bitten') && run('pops.some(p => p.text === txt("tecky.pince"))'),
     'il lui marche dessus : le crabe pince (un demi-os, « ' + run('txt("tecky.pince")') + ' ») — ce n\'est pas une morsure');
  step(60 * 2);
  // un aboiement : il s'enterre
  run('va(c.x - 150, c.y); P.dir = "right"; var sc0 = score; pressed.bark = true;'); step(2);
  ok(run('c.mode') === 'bury' && run('c.scored') && run('score') === run('sc0 + CRAB.pts'), 'un aboiement : il s\'enterre dans le sable, des points la première fois');
  step(40);
  run('hp = P.hp; va(c.x - 10, c.y);'); step(30);
  ok(run('c.mode') === 'buried' && run('c.anim') === 'buried' && run('P.hp') === run('hp'), 'enterré, il ne pince plus : Tecky lui passe dessus sans mal');
  step(60 * 8);
  ok(run('c.mode') === 'buried', 'il reste caché tant que Tecky est là');
  run('va(c.x - 500, c.y);'); step(60 * 2);
  ok(run('c.mode') === 'roam', 'Tecky parti, il ressort');
  run('va(c.x - 150, c.y); P.dir = "right"; sc0 = score; pressed.bark = true;'); step(60);
  ok(run('c.mode') === 'buried' && run('score') === run('sc0'), 'la deuxième fois, plus de points');
  // sauvegarde
  run('saveGame(); var S = loadSave(); loadGame(S);'); advanceDialog();
  ok(run('crabs[0].scored') && run('crabSeen') && run('S.crabs[0]') === '1', 'sauvegardé : le crabe déjà enterré, l\'explication déjà donnée');
  // ---- un goéland
  run('cars = []; dogs = []; items = []; var g = seagulls[0]; seul(g); va(g.hx + 600, g.hy); g.cd = 0;'); step(60);
  ok(run('g.mode') === 'soar' && run('g.anim') === 'glide' && run('Math.abs(dist(g.x, g.y, g.hx, g.hy)) <= SEAGULL.orbit + 1'), 'loin de Tecky, le goéland tourne dans le ciel au-dessus de sa place');
  run('pops = []; pendingSay = null; va(g.hx + 60, g.hy + 40);'); step(2);
  ok(run('g.mode') === 'warn' && run('g.anim') === 'cry' && run('pops.some(p => p.text === txt("goeland.cri") && p.who === "seagull")') && run('seagullSeen'),
     'Tecky entre dans son domaine : il crie (« ' + run('txt("goeland.cri")') + ' ») et vient au-dessus de lui');
  step(30);
  ok(run('state') === 'dialog' && run('dialog.lines[0].text') === run('txt("tecky.goeland")'), 'la première fois, Tecky explique : « ' + run('dialog.lines[0].text') + ' »');
  advanceDialog(); run('graceT = 0;');
  // il pique : Tecky ne bouge pas, il est touché
  run('hp = P.hp; g.cd = 0; g.mode = "soar";'); step(2);
  let vu = false; for (let i = 0; i < 60 * 4 && run('g.mode') !== 'dive'; i++) step(1);
  vu = run('g.mode') === 'dive' && run('dist(g.tx, g.ty, P.x, P.y) < 2') && run('g.anim') === 'dive';
  ok(vu, 'puis il pique sur l\'endroit où est Tecky');
  for (let i = 0; i < 60 * 2 && run('g.mode') === 'dive'; i++) step(1);
  ok(run('P.hp') === run('hp - SEAGULL.dmg') && run('g.mode') === 'climb' && run('!bitten'), 'Tecky n\'a pas bougé : touché (un demi-os), et le goéland remonte');
  // il pique : Tecky s'écarte, il n'a rien
  step(60 * 2); run('va(g.hx + 60, g.hy + 40); hp = P.hp; g.cd = 0; g.mode = "soar";');
  for (let i = 0; i < 60 * 4 && run('g.mode') !== 'dive'; i++) step(1);
  run('P.x += 90;');
  for (let i = 0; i < 60 * 2 && run('g.mode') === 'dive'; i++) step(1);
  ok(run('P.hp') === run('hp') && run('g.mode') === 'climb', 'Tecky s\'écarte pendant le piqué : le goéland le manque');
  // un aboiement le fait repartir
  step(60 * 2); run('va(g.hx + 60, g.hy + 40); g.cd = 0; g.mode = "soar";'); step(20);
  run('P.dir = g.x < P.x ? "left" : "right"; if (Math.abs(g.y - P.y) > Math.abs(g.x - P.x)) P.dir = g.y < P.y ? "up" : "down"; sc0 = score; pops = []; pressed.bark = true;'); step(2);
  ok(run('g.mode') === 'climb' && run('g.scored') && run('score') === run('sc0 + SEAGULL.pts') && run('g.cd >= SEAGULL.gone[0] - 1') && run('pops.some(p => p.text === txt("goeland.fuite"))'),
     'un aboiement vers son ombre : il repart (« ' + run('txt("goeland.fuite")') + ' »), des points, et laisse Tecky tranquille un bon moment');
  run('hp = P.hp;'); step(60 * 6);
  ok(run('g.mode') === 'soar' && run('P.hp') === run('hp'), 'il a repris sa ronde, sans attaquer');
  // zone calme et nage : pas d'attaque
  run('g.cd = 0; var cz = MAP.calm[0]; g.hx = (cz[0] + cz[2]) / 2; g.hy = (cz[1] + cz[3]) / 2; va(g.hx + 30, g.hy);'); step(60 * 2);
  ok(run('g.mode') === 'soar', 'en zone calme, un goéland n\'attaque pas');
  // en balade : personne ne fait mal
  run('newGame("balade", true);'); advanceDialog();
  run('cars = []; dogs = []; c = crabs[0]; g = seagulls[0]; seul(c); va(c.x - 20, c.y); hp = P.hp;'); step(30);
  ok(run('c.anim') === 'wave' && run('P.hp') === run('hp') && run('state') === 'play', 'en balade, le crabe salue d\'une pince et ne pince pas');
  ok(run('seagulls.every(s => s.mode === "perch" && s.h === 0)'), 'en balade, les goélands sont posés');
  run('g = seagulls[1]; g.hx = g.x = P.x + 400; g.hy = g.y = P.y; va(g.x - 90, g.y);'); step(3);
  ok(run('g.mode') === 'climb' || run('g.mode') === 'soar', 'Tecky approche : il s\'envole');
  step(60 * 3); run('va(g.hx - 900, g.hy);'); step(60 * 12);
  ok(run('g.mode') === 'perch' && run('g.h') === 0 && run('dist(g.x, g.y, g.hx, g.hy) < 2') && run('P.hp') === run('hp'), 'puis il revient se poser à sa place');
  // au printemps, rien
  run('episode = "printemps"; newGame("aventure", true);'); advanceDialog();
  ok(run('crabs.length') === 0 && run('seagulls.length') === 0, 'dans le monde du printemps : ni crabes ni goélands');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
