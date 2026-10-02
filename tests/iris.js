// quête d'Iris (le verger) : le vieux Jack Russell, ami et mentor de Tecky, a caché ses trois jouets dans les prés de
// la ferme ; Tecky les lui rapporte un par un, dans sa gueule ; ensuite, Iris donne des conseils
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999;');
  ok(run('toys.length') === 3 && run('toysLeft()') === 3 && run('jouets.state') === 'new', 'trois jouets, aucun rapporté');
  ok(run('calmAt(iris.x, iris.y)') && run('zoneAt(iris.x, iris.y).id') === 'verger' && run('!dogs.includes(iris)'),
     'Iris vit au verger, en zone calme (c’est un personnage, pas un chien des rues)');
  ok(run('MAP.decor.some(d => d[0] === "dog_bed" && dist(d[1], d[2], iris.x, iris.y) < 20)'), 'sur son panier');
  ok(run('MAP.decor.filter(d => d[0].startsWith("apple_tree") && zoneAt(d[1], d[2]).id === "verger").length') >= 8, 'au milieu des pommiers');
  ok(run('toys.every(t => zoneAt(t.x, t.y).id === "verger")'), 'ses jouets sont cachés dans les prés de la ferme');
  // il ne parle que si Tecky vient le voir ; sa bulle est plus basse (il est assis)
  run('P.x = iris.x; P.y = iris.y + 110; P.mode = "free"; pops = [];'); step(2);
  ok(run('pops.some(p => /Salut/.test(p.text))') && run('irisMark()') === 0 && run('markY(iris)') < run('NPC.markY'),
     'Tecky arrive : « Salut, mon petit Tecky ! », bulle « ! » à sa hauteur');
  step(1); run('updateCamera(10)');
  run('P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('state') === 'dialog' && run('dialog.lines[0].who') === 'iris' && run('dialog.lines.some(l => /trois jouets/.test(l.text))'), 'il propose l’entraînement');
  ok(run('!!ATLAS[WHO.iris.portrait]') && run('!!ATLAS["iris/wave"]') && run('WHO.iris.name') === 'Iris', 'son nom, son portrait, ses animations');
  advanceDialog();
  ok(run('jouets.state') === 'asked' && run('irisMark()') === 1, 'quête acceptée, bulle « ? »');
  run('var used = [], ds0 = drawSpr; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; drawHUD(); drawSpr = ds0;');
  ok(run('used.includes("port/toy")'), 'compteur de jouets dans le HUD');
  // Tecky passe sur un jouet : il le prend dans sa gueule
  run('var T0 = toys[0]; P.x = T0.x; P.y = T0.y + 10; P.mode = "free"; pops = [];'); step(2);
  ok(run('T0.carried') && run('carried() === T0') && run('pops.some(p => p.text === TOY_NAMES[0])'), 'il prend le canard dans sa gueule');
  run('updateCamera(10); used = []; drawSpr = function (k, f, x, y) { used.push([k, f, x, y]); return ds0.apply(this, arguments); }; render(); drawSpr = ds0;');
  ok(run('used.some(u => u[0] === "port/toy" && u[1] === 0 && Math.abs(u[2] - P.x - MOUTH[P.dir][0]) < 1)'), 'le jouet est dessiné dans sa gueule');
  // un seul à la fois
  run('var T1 = toys[1]; P.x = T1.x; P.y = T1.y + 10;'); step(2);
  ok(run('!T1.carried') && run('T0.carried'), 'un seul jouet à la fois');
  // il aboie : il le lâche (« Oups ! »), et peut le reprendre
  run('P.x = iris.x + 400; P.y = iris.y + 150; P.dir = "down"; P.cdBark = 0; pressed.bark = true; pops = [];'); step(1);   // (loin des autres jouets)
  ok(run('!T0.carried') && run('pops.some(p => p.text === "Oups !")') && run('dist(T0.x, T0.y, P.x, P.y)') < 80, 'il aboie : il lâche le canard devant lui');
  ok(run('!waterAt(T0.x, T0.y)'), 'par terre, jamais dans l’eau');
  step(30);
  ok(!run('T0.carried'), 'il ne le reprend pas aussitôt');
  run('P.x = T0.x; P.y = T0.y + 8; P.mode = "free";'); step(60);
  ok(run('T0.carried'), 'mais ensuite, en repassant dessus');
  // il le donne à Iris en arrivant près de lui : une seule bulle (pas de salut en plus)
  run('P.x = iris.x + 60; P.y = iris.y + 70; P.mode = "free"; pops = []; var sc0 = score;'); step(2);
  ok(run('T0.home') && !run('carried()') && run('score') === run('sc0 + IRIS.perToy') && run('iris.cheerT') > 0, 'Iris reçoit son canard (il remue la queue)');
  ok(run('pops.some(p => /Encore 2/.test(p.text))') && run('pops.filter(p => p.who === "iris").length') === 1, '« Bravo ! Encore 2 ! », et rien d’autre');
  // KO : il lâche le jouet
  run('P.x = T1.x; P.y = T1.y + 10;'); step(2);
  ok(run('T1.carried'), 'deuxième jouet');
  run('P.mode = "ko";'); step(1);
  ok(run('!T1.carried') && !run('T1.home'), 'KO : il lâche le jouet');
  run('P.mode = "free"; P.hp = P.hpMax;');
  // sauvegarde : un jouet porté est enregistré par terre, aux pieds de Tecky
  run('P.x = T1.x; P.y = T1.y + 10;'); step(2);
  run('saveGame(); var sv = STORE.get(SAVE_KEY);');
  ok(run('sv.jouets') === 'asked' && run('sv.toys[0][2]') === 1 && run('sv.toys[1][2]') === 0 && Math.abs(run('sv.toys[1][0] - P.x')) < 1,
     'sauvegardés (le canard rentré, l’anneau porté : par terre, aux pieds de Tecky)');
  run('toTitle(); loadGame(STORE.get(SAVE_KEY), false);'); advanceDialog();
  ok(run('jouets.state') === 'asked' && run('toys[0].home') && !run('carried()') && run('toysLeft()') === 2, 'Continuer : tout est à sa place');
  // les deux derniers : Iris appelle, puis remercie (saucisse, points), badge
  run('dogs = []; cars = []; P.inv = 999;');
  for (const k of [1, 2]) {
    run(`P.x = toys[${k}].x; P.y = toys[${k}].y + 10; P.mode = "free";`); step(2);
    run('P.x = iris.x + 60; P.y = iris.y + 70; pops = [];'); step(2);
  }
  ok(run('toysLeft()') === 0 && run('pops.some(p => /Viens me voir/.test(p.text))'), 'tous rapportés : « Tous mes jouets ! Viens me voir ! »');
  ok(run('toys.every(t => dist(t.x, t.y, iris.x, iris.y) < 80)'), 'ses jouets sont à côté de lui');
  run('P.x = iris.x; P.y = iris.y + 110; P.mode = "free"; var sc1 = score, n0 = items.length;'); step(2);
  run('P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('state') === 'dialog' && /Mes trois jouets/.test(run('dialog.lines[0].text')), 'Iris félicite Tecky');
  advanceDialog();
  ok(run('jouets.state') === 'done' && run('score') === run('sc1 + IRIS.reward') && run('items[items.length - 1].n') === 'sausage', 'une saucisse et des points');
  step(40);
  ok(run('!!badges.iris') && run('QUESTS_DONE[4]()'), 'badge « Va chercher ! », compté dans la complétion');
  // ensuite : un conseil de vieux chien à chaque visite, à tour de rôle (sans icônes au toucher)
  const tips = [];
  for (let i = 0; i < run('IRIS_TIPS.length') + 1; i++) {
    run('P.cdBite = 0; pressed.bite = true'); step(1);
    tips.push(run('state') === 'dialog' ? run('dialog.lines[0].text') : '');
    advanceDialog(); step(2);
  }
  ok(new Set(tips).size === run('IRIS_TIPS.length') && tips[0] === tips[tips.length - 1], 'des conseils, chacun son tour (' + (new Set(tips)).size + ')');
  ok(/\[sniff\]/.test(tips[0]) && !run('touchMode = true, IRIS_TIPS.some(f => /\\[/.test(f()))'), 'avec les icônes des touches (pas au toucher)');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
