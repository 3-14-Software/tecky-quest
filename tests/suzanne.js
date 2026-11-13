// la quête de Maman Piquette rejouée sur la côte (MAP.roles.piquette) : Suzanne, la poissonnière, s'est fait chiper
// trois poissons par des mouettes rieuses. Elles s'envolent quand Tecky approche ; un aboiement leur fait lâcher
// prise, Tecky rapporte les poissons un par un dans sa gueule.
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('EPISODES[1].chantier = false; audioOn(); STORE.mem = {}; loadBadges(); episode = "ete"; newGame("aventure", true);'); advanceDialog();
  run('cars = []; dogs = []; P.inv = 99; var T = MAP.ts; function va(x, y) { P.x = x; P.y = y; P.mode = "free"; syncSwim(true); }');
  run('function vise(g, d) { va(g.x - d, g.y); P.dir = "right"; }');       // Tecky à d px à l'ouest de la mouette, tourné vers elle
  ok(run('MAP.roles.piquette') === 'suzanne' && run('piquette.kind') === 'piquette' && run('piquette.look') === 'suzanne' && run('gulls()')
     && run('babies.length') === 3 && run('babies.every(b => b.mode === "held" && b.g.mode === "perch")') && run('npcList().length') === 6,
     'sur la côte, le rôle de Maman Piquette est tenu par Suzanne ; trois mouettes tiennent chacune un poisson');
  ok(['suzanne/idle', 'suzanne/talk', 'suzanne/wave', 'suzanne/cheer', 'suzanne/worry', 'hud/portrait_suzanne', 'gull/idle', 'gull/walk', 'gull/taunt',
      'gull/cry', 'gull/fly', 'plage/poisson'].every(k => run(`!!ATLAS[${JSON.stringify(k)}]`))
     && run('ATLAS["plage/poisson"].f.length') === 3 && run('MAP.fishBase.length') === 3
     && run('Object.keys(MAP.gullBeak).every(a => MAP.gullBeak[a].length === ATLAS["gull/" + a].f.length && MAP.gullFps[a] > 0)')
     && run('WHO.suzanne.name') === 'Suzanne' && run('calmAt(piquette.x, piquette.y)') && run('zoneAt(piquette.x, piquette.y).id') === 'pecheurs',
     'ils ont leurs dessins : Suzanne, son portrait, la mouette (cinq animations, le bout de son bec à chaque image), les trois poissons');
  ok(run('babies.every(b => !blockedFeet(b.x, b.y, 14) && !!gullSpot(b))'), 'chaque mouette est posée sur un sol libre, et a de la place pour s\'envoler plus loin');
  // loin de Tecky, une mouette fait quelques pas
  run('var bw = babies[2], gw = bw.g, wx0 = gw.x, wy0 = gw.y; va(piquette.x, piquette.y + 60); gw.strollT = 0.01; var marche = false;');
  for (let i = 0; i < 60 * 4 && !run('marche'); i++) { step(1); run('if (gw.anim === "walk") marche = true; if (gw.wx === null && gw.strollT > 0.6 && !marche) gw.strollT = 0.01;'); }
  step(60 * 3);
  ok(run('marche') && run('gw.mode') === 'perch' && run('bw.mode') === 'held' && run('dist(gw.x, gw.y, wx0, wy0) > 10') && run('gullOpen(bw, gw.x, gw.y)') && run('bw.x === gw.x'),
     'loin de Tecky, une mouette fait quelques pas, son poisson au bec');
  run('va(piquette.x - 60, piquette.y + 50); talkTo(piquette);');
  ok(run('state') === 'dialog' && run('dialog.lines.length') === 4 && run('dialog.lines[0].who') === 'suzanne' && run('dialog.lines[0].text') === run('txt("suzanne.demande.0")')
     && run('dialog.lines[3].text') === run('txt("suzanne.demande.3")'), 'Suzanne demande : « ' + run('dialog.lines[3].text') + ' »');
  advanceDialog();
  ok(run('piq.state') === 'asked' && run('piquette.worried') && run('hudCounters().some(c => c[0] === "plage/poisson" && c[4] === 0 && c[5] === 3)'),
     'quête en cours : elle s\'inquiète, compteur 0 / 3 avec un poisson');
  // une mouette nargue Tecky quand il est dans les parages
  run('var b0 = babies[0], g0 = b0.g; vise(g0, 260); g0.tauntT = 0.01; pops = [];'); step(3);
  ok(run('g0.mode') === 'perch' && run('g0.anim') === 'taunt' && run('pops.some(p => p.text === txt("mouette.rire") && p.who === "gull")'),
     'à distance, elle le nargue : « ' + run('txt("mouette.rire")') + ' »');
  // il approche : elle s'envole plus loin, son poisson au bec
  run('var x0 = g0.x, y0 = g0.y; vise(g0, 100);'); step(2);
  ok(run('g0.mode') === 'hop' && run('b0.mode') === 'held', 'il approche : elle s\'envole avec son poisson');
  step(8); const haut = run('g0.h'); step(60 * 3);
  ok(haut > 5 && run('g0.mode') === 'perch' && run('g0.h') === 0 && run('dist(g0.x, g0.y, x0, y0) > 150') && run('dist(g0.x, g0.y, P.x, P.y) >= GULL.safe - 1')
     && run('dist(g0.x, g0.y, b0.hx, b0.hy) <= GULL.roam') && run('!blockedFeet(g0.x, g0.y, 14)') && run('b0.x === g0.x && b0.y === g0.y'),
     'elle se pose plus loin, hors de portée, sur un sol où Tecky peut aller ; le poisson la suit');
  // sauvegarde : la mouette et son poisson sont là où elle s'est posée
  run('var gx = g0.x, gy = g0.y; saveGame(); var S = loadSave(); loadGame(S);'); advanceDialog();
  run('cars = []; dogs = []; P.inv = 99; b0 = babies[0]; g0 = b0.g;');
  ok(run('piq.state') === 'asked' && run('b0.mode') === 'held' && run('g0.mode') === 'perch' && run('Math.abs(g0.x - gx) < 1 && Math.abs(g0.y - gy) < 1'),
     'partie reprise : la mouette est là où elle s\'était posée');
  // un aboiement de loin : elle lâche son poisson et file
  run('vise(g0, 220); graceT = 0; pops = []; var px = g0.x, py = g0.y; pressed.bark = true;'); step(2);
  ok(run('b0.mode') === 'fall' && run('g0.mode') === 'away' && run('pops.some(p => p.text === txt("mouette.cri"))'),
     'il aboie de loin : elle lâche prise (« ' + run('txt("mouette.cri")') + ' »)');
  step(60);
  ok(run('b0.mode') === 'ground' && run('b0.up') === 0 && run('Math.abs(b0.x - px) < 1 && Math.abs(b0.y - py) < 1') && run('g0.h > 20 || g0.mode === "gone"'),
     'le poisson tombe par terre là où elle était ; elle s\'envole');
  step(60 * 6);
  ok(run('g0.mode') === 'gone' && run('(function () { var l = []; gullList(l, function () { return true; }); return l.length; })()') === 3,
     'elle disparaît dans le ciel : il reste le poisson par terre et les deux autres mouettes');
  // Tecky prend le poisson dans sa gueule
  run('va(b0.x - 20, b0.y); pops = [];'); step(3);
  ok(run('b0.mode') === 'carried' && run('fishCarried() === b0') && run('pops.some(p => p.text === txt("suzanne.poisson.0"))'),
     'Tecky passe dessus et le prend dans sa gueule : « ' + run('txt("suzanne.poisson.0")') + ' »');
  // il aboie : il le lâche
  step(60); run('pressed.bark = true;'); step(2);
  ok(run('b0.mode') === 'ground' && run('dist(b0.x, b0.y, P.x, P.y) < 40') && run('pops.some(p => p.text === txt("tecky.oups"))'), 's\'il aboie, il le lâche à ses pieds');
  step(60 * 2); run('va(b0.x - 20, b0.y);'); step(3);
  ok(run('b0.mode') === 'carried', 'il le reprend');
  // un seul objet dans la gueule : pas de jouet de Théo en plus
  run('va(toys[0].x, toys[0].y + 4);'); step(3);
  ok(run('!toys[0].carried') && run('b0.mode') === 'carried', 'la gueule pleine, il ne prend pas un jouet de Théo en plus');
  // sauvegarde avec le poisson dans la gueule : il est par terre, aux pieds de Tecky
  run('va(piquette.x - 400, piquette.y + 120); saveGame(); S = loadSave(); loadGame(S);'); advanceDialog();
  run('cars = []; dogs = []; P.inv = 99; b0 = babies[0];');
  ok(run('b0.mode') === 'ground' && run('b0.g.mode') === 'gone' && run('dist(b0.x, b0.y, P.x, P.y) < 2') && run('babies[1].mode') === 'held',
     'partie reprise : le poisson est par terre près de Tecky, sa mouette est partie, les autres tiennent toujours le leur');
  step(3);
  // il le rapporte à Suzanne
  run('va(piquette.x - 70, piquette.y + 50); pops = [];'); step(3);
  ok(run('b0.mode') === 'home' && run('babiesLeft()') === 2 && run('pops.some(p => p.text === txt("suzanne.arrive", { n: 1, reste: 2 }) && p.who === "suzanne")'),
     'rapporté à Suzanne : « ' + run('txt("suzanne.arrive", { n: 1, reste: 2 })') + ' »');
  ok(run('dist(b0.x, b0.y, piquette.x, piquette.y) < 90') && run('hudCounters().some(c => c[0] === "plage/poisson" && c[4] === 1)'), 'le poisson est posé près d\'elle, compteur 1 / 3');
  // les deux autres : une mouette aboyée en plein vol lâche aussi son poisson, qui tombe sur un sol libre
  run('var b1 = babies[1], g1 = b1.g; vise(g1, 100);'); step(2);
  ok(run('g1.mode') === 'hop', 'la deuxième s\'envole');
  step(10); run('P.x = g1.x - 200; P.y = g1.y; P.dir = "right"; pressed.bark = true;'); step(2);
  ok(run('b1.mode') === 'fall' && run('g1.mode') === 'away', 'aboyée en plein vol, elle lâche prise');
  step(90);
  ok(run('b1.mode') === 'ground' && run('!blockedFeet(b1.x, b1.y, 14)'), 'son poisson tombe sur un sol libre');
  run('va(b1.x - 20, b1.y);'); step(3); run('va(piquette.x - 70, piquette.y + 50);'); step(3);
  run('var b2 = babies[2]; vise(b2.g, 220); pressed.bark = true;'); step(90);
  run('va(b2.x - 20, b2.y);'); step(3); run('va(piquette.x - 70, piquette.y + 50); pops = [];'); step(3);
  ok(run('babiesLeft()') === 0 && run('pops.some(p => p.text === txt("suzanne.tous"))') && run('!piquette.worried'), 'les trois sont rapportés : Suzanne appelle Tecky');
  run('var sc0 = score, n0 = items.length; talkTo(piquette);');
  ok(run('dialog.lines[0].who') === 'suzanne' && run('dialog.lines[0].text') === run('txt("suzanne.merci.0")'), 'elle remercie : « ' + run('dialog.lines[0].text') + ' »');
  advanceDialog(); run('checkBadges();');
  ok(run('piq.state') === 'done' && run('score') === run('sc0 + 150') && run('items.length') === run('n0 + 1') && run('!!badges.mouettes && !badges.herissons'),
     'quête finie : des points, un os, le badge « ' + run('badgeName("mouettes")') + ' »');
  run('talkTo(piquette);');
  ok(run('dialog.lines[0].text') === run('txt("suzanne.apres")'), 'ensuite : « ' + run('dialog.lines[0].text') + ' »');
  advanceDialog();
  ok(run('questsHere().length') === 6 && run('questsHere().every(q => typeof q() === "boolean")'), 'la côte compte six quêtes');
  // au printemps, rien ne change
  run('episode = "printemps"; newGame("aventure", true);'); advanceDialog();
  ok(run('!gulls()') && run('piquette.look') === 'piquette' && run('babies.every(b => b.mode === "hidden" && !b.g)') && run('pqTxt("bonjour")') === run('txt("piquette.bonjour")'),
     'dans le monde : Maman Piquette et ses petits, comme avant');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
