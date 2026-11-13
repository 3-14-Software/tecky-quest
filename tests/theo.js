// la quête des jouets d'Iris rejouée sur la côte (MAP.roles.iris) : Théo, le maître-nageur, a vu trois jouets de
// plage partir au large. Tecky nage les chercher et les rapporte un par un dans sa gueule.
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('EPISODES[1].chantier = false; audioOn(); STORE.mem = {}; loadBadges(); episode = "ete"; newGame("balade", true);'); advanceDialog();
  run('cars = []; dogs = []; P.inv = 99; var T = MAP.ts; function va(x, y) { P.x = x; P.y = y; P.mode = "free"; syncSwim(true); }');
  ok(run('MAP.roles.iris') === 'theo' && run('iris.kind') === 'iris' && run('iris.look') === 'theo' && run('!iris.woof') && run('seaToys()')
     && run('toys.length') === 3 && run('toys.every(t => swimAt(t.x, t.y) && !deepAt(t.x, t.y))') && run('npcList().length') === 6,
     'sur la côte, le rôle d\'Iris est tenu par Théo ; ses trois jouets flottent dans la zone de baignade');
  ok(['theo/idle', 'theo/talk', 'theo/wave', 'theo/cheer', 'theo/worry', 'hud/portrait_theo', 'plage/jouet', 'mer/jouet'].every(k => run(`!!ATLAS[${JSON.stringify(k)}]`))
     && run('ATLAS["plage/jouet"].f.length') === 3 && run('ATLAS["mer/jouet"].f.length') === 3 && run('MAP.beachToyBase.length') === 3
     && run('WHO.theo.name') === 'Théo' && run('calmAt(iris.x, iris.y)') && run('sandAt(iris.x, iris.y)'),
     'ils ont leurs dessins : Théo, son portrait, les jouets posés et à flot ; il est sur le sable, en zone calme');
  // la demande
  run('va(iris.x - 60, iris.y + 40); talkTo(iris);');
  ok(run('state') === 'dialog' && run('dialog.lines[0].who') === 'theo' && run('dialog.lines[0].text') === run('txt("theo.demande.0")'),
     'Théo demande : « ' + run('dialog.lines[2].text') + ' »');
  advanceDialog();
  ok(run('jouets.state') === 'asked' && run('hudCounters().some(c => c[0] === "plage/jouet" && c[4] === 0 && c[5] === 3)'), 'quête en cours : compteur 0 / 3, avec un jouet de plage');
  // un jouet à flot : dessiné sur l'eau, pris à la nage
  run('var keys = [], ds0 = drawSpr; drawSpr = function (k) { keys.push(k); return ds0.apply(this, arguments); }; drawToy(toys[0]); drawSpr = ds0;');
  ok(run('keys.join()') === 'mer/jouet', 'un jouet au large est dessiné à flot');
  run('va(toys[0].x, toys[0].y + 4);'); step(3);
  ok(run('P.swim') && run('toys[0].carried') && run('pops.some(p => p.text === txt("theo.jouet.0"))'), 'Tecky nage dessus et le prend dans sa gueule : « ' + run('txt("theo.jouet.0")') + ' »');
  // il aboie : il le lâche, le jouet flotte là
  run('pressed.bark = true;'); step(2);
  ok(run('!toys[0].carried') && run('waterAt(toys[0].x, toys[0].y)') && run('dist(toys[0].x, toys[0].y, P.x, P.y) < 40'), 's\'il aboie, il le lâche : le jouet flotte à côté de lui');
  step(60 * 2); run('va(toys[0].x, toys[0].y + 4);'); step(3);
  ok(run('toys[0].carried'), 'il le reprend');
  // sauvegarde avec un jouet dans la gueule : il est à l'eau, là où était Tecky
  run('saveGame(); var S = loadSave(); loadGame(S);'); advanceDialog();
  ok(run('jouets.state') === 'asked' && run('!toys[0].carried && !toys[0].home') && run('P.swim'), 'partie reprise : le jouet flotte près de Tecky, qui nage');
  step(60 * 2); run('cars = []; dogs = []; va(toys[0].x, toys[0].y + 4);'); step(3);
  // il le rapporte
  run('va(iris.x + 70, iris.y + 30);'); step(3);
  ok(run('toys[0].home') && run('!P.swim') && run('sandAt(toys[0].x, toys[0].y)') && run('pops.some(p => p.text === txt("theo.bravo_encore", { n: 2 }))'),
     'rapporté à Théo : le jouet est posé sur le sable à côté de lui, « ' + run('txt("theo.bravo_encore", { n: 2 })') + ' »');
  run('keys = []; drawSpr = function (k) { keys.push(k); return ds0.apply(this, arguments); }; drawToy(toys[0]); drawSpr = ds0;');
  ok(run('keys[0]') === 'plage/jouet', 'sur le sable, il a son dessin posé');
  for (const i of [1, 2]) { run(`va(toys[${i}].x, toys[${i}].y + 4);`); step(3); run('va(iris.x + 70, iris.y + 30);'); step(3); }
  ok(run('toysLeft()') === 0 && run('pops.some(p => p.text === txt("theo.tous"))'), 'les trois sont rapportés : Théo appelle Tecky');
  run('var sc0 = score, n0 = items.length; talkTo(iris);');
  ok(run('dialog.lines[0].text') === run('txt("theo.merci.0")'), 'il remercie : « ' + run('dialog.lines[0].text') + ' »');
  advanceDialog(); run('checkBadges();');
  ok(run('jouets.state') === 'done' && run('score') === run('sc0 + IRIS.reward') && run('items.length') === run('n0 + 1') && run('!!badges.nageur && !badges.iris'),
     'quête finie : des points, une saucisse, le badge « ' + run('badgeName("nageur")') + ' »');
  run('talkTo(iris);'); const c0 = run('dialog.lines[0].text'); advanceDialog(); run('talkTo(iris);'); const c1 = run('dialog.lines[0].text'); advanceDialog();
  ok(c0 === run('txt("theo.conseil.0")') && c1 === run('txt("theo.conseil.1")'), 'ensuite, un conseil de plage à chaque visite : « ' + c0 + ' »');
  // au printemps, rien ne change
  run('episode = "printemps"; newGame("balade", true);'); advanceDialog();
  ok(run('!seaToys()') && run('iris.look') === 'iris' && run('iris.woof') && run('toyKey()') === 'port/toy', 'dans le monde : Iris et ses jouets, comme avant');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
