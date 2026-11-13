// la quête des ballons de Léon rejouée sur la côte (MAP.roles.leon) : Yvon, le pêcheur, a vu dériver les cinq bouées
// de ses casiers. Elles flottent ; Tecky les pousse à la nage, ou en aboyant, jusqu'au parc planté dans l'eau.
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('EPISODES[1].chantier = false; audioOn(); STORE.mem = {}; loadBadges(); episode = "ete"; newGame("balade", true);'); advanceDialog();
  run('cars = []; dogs = []; P.inv = 99; var T = MAP.ts; function va(x, y) { P.x = x; P.y = y; P.mode = "free"; for (const k in held) held[k] = false; syncSwim(true); }');
  ok(run('MAP.roles.leon') === 'yvon' && run('leon.kind') === 'leon' && run('leon.look') === 'yvon' && run('floats()') && run('balls.length') === 5
     && run('balls.every(b => swimAt(b.x, b.y) && !ballBlocked(b, b.x, b.y) && !b.inNet)') && run('npcList().length') === 5,
     'sur la côte, le rôle de Léon est tenu par Yvon ; ses cinq bouées flottent dans la zone de baignade');
  ok(['yvon/idle', 'yvon/talk', 'yvon/wave', 'yvon/cheer', 'yvon/worry', 'hud/portrait_yvon', 'mer/casier', 'decor/buoy_pen'].every(k => run(`!!ATLAS[${JSON.stringify(k)}]`))
     && run('ATLAS["mer/casier"].f.length') === 5 && run('WHO.yvon.name') === 'Yvon' && run('calmAt(leon.x, leon.y)') && run('sandAt(leon.x, leon.y)')
     && run('decor.some(d => d.n === "buoy_pen")') && run('!decor.some(d => d.n === "goal_net")') && run('swimAt(MAP.goal[0], MAP.goal[1] - 30)'),
     'ils ont leurs dessins : Yvon, son portrait, cinq bouées, le parc à bouées planté dans l\'eau ; il est sur le sable, en zone calme');
  run('va(leon.x - 60, leon.y + 30); talkTo(leon);');
  ok(run('state') === 'dialog' && run('dialog.lines[0].who') === 'yvon' && run('dialog.lines[0].text') === run('txt("yvon.demande.0")'),
     'Yvon demande : « ' + run('dialog.lines[1].text') + ' »');
  advanceDialog();
  ok(run('fete.state') === 'asked' && run('hudCounters().some(c => c[0] === "mer/casier" && c[4] === 0 && c[5] === 5)'), 'quête en cours : compteur 0 / 5, avec une bouée');
  // Tecky nage dans une bouée : elle glisse devant lui, sans sauter, et reste dans la zone de baignade
  run('var B = balls[2], bx0 = B.x; va(B.x - 70, B.y + 6); held.right = true;'); step(90);
  ok(run('P.swim') && run('B.x > bx0 + 40') && run('B.z') === 0 && run('swimAt(B.x, B.y)'), 'il nage dedans : elle glisse devant lui (' + Math.round(run('B.x - bx0')) + ' px), à plat sur l\'eau');
  // il aboie derrière elle
  run('for (const k in held) held[k] = false; B.vx = B.vy = 0;'); step(40);
  run('va(B.x - 120, B.y + 6); P.dir = "right"; bx0 = B.x; pressed.bark = true;'); step(40);
  ok(run('B.x > bx0 + 30'), 'il aboie derrière elle : elle file');
  // lancée vers le large ou vers la plage, elle ne quitte jamais l'eau où l'on nage
  run('for (const [vx, vy] of [[0, 900], [0, -900], [900, 0], [-900, 0]]) { B.vx = vx; B.vy = vy; for (let i = 0; i < 240; i++) updateBall(B, 1 / 60); }');
  ok(run('swimAt(B.x, B.y)') && run('!B.inNet'), 'lancée dans tous les sens, elle reste dans la zone de baignade');
  // poussée dans le parc, par son ouverture
  run('var g = MAP.goal; va(g[0], g[1] + 260); B.x = g[0]; B.y = g[1] + 90; B.vx = 0; B.vy = -260; pops = [];');
  let t = 0; while (run('!B.inNet') && t++ < 240) run('updateBall(B, 1 / 60);');
  ok(run('B.inNet') && run('pops.some(p => p.text === txt("bouees.but"))'), 'poussée entre les pieux, elle entre au parc : « ' + run('txt("bouees.but")') + ' »');
  run('B.vx = 600; B.vy = 500; for (let i = 0; i < 300; i++) updateBall(B, 1 / 60);');
  ok(run('B.inNet') && run('Math.abs(B.x - g[0]) < 70'), 'une bouée au parc y reste');
  // sauvegarde
  run('saveGame(); var S = loadSave(); loadGame(S);'); advanceDialog();
  ok(run('fete.state') === 'asked' && run('balls[2].inNet') && run('ballsLeft()') === 4, 'partie reprise : une bouée au parc, quatre à pousser');
  run('cars = []; dogs = []; for (const b of balls) if (!b.inNet) { b.x = MAP.goal[0]; b.y = MAP.goal[1] - 20; checkGoal(b); }');
  ok(run('ballsLeft()') === 0 && run('pops.some(p => p.text === txt("yvon.bravo"))'), 'les cinq sont au parc : Yvon appelle Tecky');
  run('va(leon.x - 60, leon.y + 30); var sc0 = score, n0 = items.length; talkTo(leon);');
  ok(run('dialog.lines[0].text') === run('txt("yvon.merci.0")'), 'il remercie : « ' + run('dialog.lines[0].text') + ' »');
  advanceDialog(); run('checkBadges();');
  ok(run('fete.state') === 'done' && run('score') === run('sc0 + LEON.reward') && run('items.length') === run('n0 + 1') && run('!!badges.bouees && !badges.ballons')
     && run('questsHere().length') === 5,
     'quête finie : des points, un os, le badge « ' + run('badgeName("bouees")') + ' » ; la côte a cinq quêtes');
  // au printemps, rien ne change
  run('episode = "printemps"; newGame("balade", true);'); advanceDialog();
  ok(run('!floats()') && run('leon.look') === 'leon' && run('decor.some(d => d.n === "goal_net")') && run('balls.every(b => !waterAt(b.x, b.y))'), 'dans le monde : Léon, ses ballons et son filet, comme avant');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
