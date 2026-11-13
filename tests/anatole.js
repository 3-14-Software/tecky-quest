// la quête des poules rejouée sur la côte avec d'autres acteurs (MAP.roles) : Anatole, le gardien du phare, a perdu
// ses moutons sur le plateau des falaises ; Tecky les ramène dans l'enclos en aboyant derrière eux
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('EPISODES[1].chantier = false; audioOn(); episode = "ete"; newGame("balade", true);'); advanceDialog();
  run('cars = []; dogs = []; P.inv = 99;');
  ok(run('MAP.roles.farmer') === 'anatole' && run('farmer.kind') === 'farmer' && run('farmer.look') === 'anatole' && run('hens.length') === 6
     && run('hens.every(h => h.kind === "sheep")') && run('questHens().length') === 5 && run('ici("pen")') && run('npcList().length') === 3,
     'sur la côte, le rôle de Gaston est tenu par Anatole, celui des poules par ses moutons : cinq à ramener, un dans l\'enclos');
  ok(['anatole/idle', 'anatole/talk', 'anatole/wave', 'hud/portrait_anatole', 'sheep/idle/right', 'sheep/peck/right', 'sheep/walk/right', 'sheep/flap/right']
       .every(k => run(`!!ATLAS[${JSON.stringify(k)}]`)) && run('WHO.anatole.name') === 'Anatole' && run('calmAt(farmer.x, farmer.y)')
     && run('MAP.cast.includes("sheep")') && run('MAP.farmRoadY') > run('MAP.h * TS') && run('CARTES.monde.farmRoadY') < run('20 * TS'),
     'ils ont leurs dessins et leur ombre ; ici, pas de grande route à ne pas franchir (au printemps, si)');
  ok(run('decor.filter(d => d.n.startsWith("fence_wood")).length') > 15 && run('blockedFeet(MAP.pen[0], (MAP.pen[1] + MAP.pen[3]) / 2, 8)')
     && !run('blockedFeet((MAP.penGate[0] + MAP.penGate[1]) / 2, MAP.pen[3], 8)'), 'l\'enclos est clôturé, sa barrière du sud est ouverte');
  // la demande
  run('P.x = farmer.x - 60; P.y = farmer.y + 40; P.mode = "free"; talkTo(farmer);');
  ok(run('state') === 'dialog' && run('dialog.lines[0].who') === 'anatole' && run('dialog.lines[0].text') === run('txt("anatole.demande.0")'),
     'Anatole demande : « ' + run('dialog.lines[0].text') + ' »');
  advanceDialog();
  ok(run('farm.state') === 'asked' && run('hudCounters().some(c => c[0] === "sheep/idle/right" && c[4] === 0 && c[5] === 5)') && run('farmerMark()') === 1,
     'quête en cours : le compteur des moutons, à 0 / 5');
  run('talkTo(farmer);');
  ok(run('dialog.lines[0].text') === run('txt("anatole.rappel", { n: 5 })'), 'rappel : « ' + run('dialog.lines[0].text') + ' »');
  advanceDialog();
  // un aboiement fait détaler un mouton ; il reste où on l'a poussé
  run('var M = questHens()[0]; P.x = M.x; P.y = M.y + 150; P.dir = "up"; P.mode = "free"; var y0 = M.y; pressed.bark = true;'); step(90);
  ok(run('M.y') < run('y0 - 60') && run('Math.abs(M.hy - M.y) < 1') && !run('M.penned'), 'Tecky aboie derrière un mouton : il détale (' + Math.round(run('y0 - M.y')) + ' px) et reste où il s\'arrête');
  // poussé depuis sous la barrière, il entre dans l'enclos
  run('{ const [gx, gy] = gatePoint(); M.x = M.hx = gx; M.y = M.hy = gy + 70; M.mode = "idle"; M.timer = 9; P.x = gx; P.y = gy + 190; P.dir = "up"; P.cdBark = 0; pops = []; var sc0 = score; pressed.bark = true; }'); step(70);
  ok(run('M.penned') && run('score') === run('sc0 + FARM.perHen') && run('pops.some(p => p.text === txt("moutons.rentree"))')
     && run('hudCounters().some(c => c[0] === "sheep/idle/right" && c[4] === 1)'), 'poussé vers la barrière, il rentre : « ' + run('txt("moutons.rentree")') + ' », compteur à 1 / 5');
  step(200);
  ok(run('M.penned') && run('(() => { const R = penRect(); return M.x >= R[0] && M.x <= R[2] && M.y >= R[1] && M.y <= R[3]; })()'), 'une fois rentré, il ne ressort plus de l\'enclos');
  // les autres rentrent : Anatole appelle Tecky, puis le remercie
  run('pops = []; questHens().forEach(h => { if (!h.penned) { const R = penRect(); h.x = (R[0] + R[2]) / 2; h.y = (R[1] + R[3]) / 2; keepHen(h); } });');
  ok(run('hensLeft()') === 0 && run('pops.some(p => p.text === txt("moutons.toutes"))') && run('pops.some(p => p.text === txt("anatole.bravo") && p.who === "anatole")'),
     'tous rentrés : « ' + run('txt("moutons.toutes")') + ' », et Anatole : « ' + run('txt("anatole.bravo")') + ' »');
  run('var b0 = JSON.stringify(badges), n0 = items.length; sc0 = score; P.x = farmer.x - 60; P.y = farmer.y + 40; talkTo(farmer);');
  ok(run('dialog.lines[0].text') === run('txt("anatole.merci.0")'), 'il remercie : « ' + run('dialog.lines[0].text') + ' »');
  advanceDialog(); run('checkBadges();');
  ok(run('farm.state') === 'done' && run('score') === run('sc0 + FARM.reward') && run('items.length') === run('n0 + 1') && run('!badges.poules && !!badges.moutons') && run('JSON.stringify(badges)') !== run('b0')
     && run('questsHere().length') === 3, 'quête finie : des points, une saucisse ; le badge « Berger des falaises » (celui des poules reste à Gaston) ; trois quêtes comptent sur la côte');
  run('saveGame(); var S = loadSave();');
  ok(run('S.farm') === 'done' && run('S.hens.length') === 5 && run('S.hens.every(h => h[2] === 1)'), 'sauvegardé comme la quête des poules (farm, hens)');
  // au printemps, rien n'a changé
  run('episode = "printemps"; newGame("aventure", true);'); advanceDialog();
  ok(run('farmer.look') === 'farmer' && run('hens.every(h => h.kind !== "sheep")') && run('fmTxt("bonjour")') === run('txt("farmer.bonjour")')
     && run('flockTxt("rentree")') === 'Rentrée !' && run('flockKey()') === 'hen', 'au printemps : Gaston et ses poules');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
