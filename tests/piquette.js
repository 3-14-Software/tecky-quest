// quête de Maman Piquette (la forêt) : ses trois petits se cachent sous les fougères ; trouvés, ils suivent Tecky en
// file indienne jusqu'à leur maman
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999;');
  ok(run('babies.length') === 3 && run('babiesLeft()') === 3 && run('babies.every(b => b.mode === "hidden")'), 'trois petits, cachés');
  ok(run('calmAt(piquette.x, piquette.y)') && run('zoneAt(piquette.x, piquette.y).id') === 'foret', 'Maman Piquette vit dans la forêt, en zone calme');
  ok(run('MAP.decor.filter(d => d[0] === "fir").every(d => !calmAt(d[1], d[2]) || dist(d[1], d[2], piquette.x, piquette.y) > 300)'),
     'une clairière sans sapins autour d’elle');
  // avant la demande : un petit caché ne suit pas Tecky, il pousse juste un « Couic ? »
  run('var B0 = babies[0]; P.x = B0.x - 60; P.y = B0.y + 20; P.mode = "free"; pops = [];');
  let squeak = false;
  for (let i = 0; i < 60 * 6; i++) { step(1); if (run('pops.some(p => p.text === "Couic ?")')) squeak = true; }
  ok(run('B0.mode') === 'hidden' && squeak, 'avant la demande : il reste caché (« Couic ? »)');
  // Maman Piquette : elle ne parle que si Tecky vient la voir
  run('P.x = piquette.x; P.y = piquette.y + 110; pops = [];'); step(2);
  ok(run('pops.some(p => /Où êtes-vous/.test(p.text))') && run('piquetteMark()') === 0, '« Mes petits ! Où êtes-vous ? », bulle « ! »');
  step(1); run('updateCamera(10)'); run('P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('state') === 'dialog' && run('dialog.lines[0].who') === 'piquette' && run('!!ATLAS[WHO.piquette.portrait]'), 'elle demande de l’aide (son portrait)');
  advanceDialog();
  ok(run('piq.state') === 'asked' && run('piquetteMark()') === 1, 'quête acceptée, bulle « ? »');
  run('var used = [], ds0 = drawSpr; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; drawHUD(); drawSpr = ds0;');
  ok(run('used.includes("hedgehog/idle")'), 'compteur de petits dans le HUD');
  // Tecky trouve deux petits : ils le suivent, l'un derrière l'autre
  run('P.x = babies[0].x - 60; P.y = babies[0].y + 10; pops = [];'); step(2);
  ok(run('babies[0].mode') === 'follow' && run('pops.some(p => p.text === "Couic !")'), 'trouvé : il suit Tecky (« Couic ! »)');
  run('P.x = babies[1].x - 60; P.y = babies[1].y + 10; babies[0].x = P.x - 50; babies[0].y = P.y;'); step(2);
  ok(run('babies[1].mode') === 'follow', 'un deuxième');
  step(60 * 2, 'held.left = true'); step(60, 'held.down = true'); run('held.left = false; held.down = false;'); step(60);
  const d0 = run('dist(babies[0].x, babies[0].y, P.x, P.y)'), d1 = run('dist(babies[1].x, babies[1].y, P.x, P.y)');
  ok(d0 < 110 && d1 < 170 && d1 > d0, 'en file indienne derrière Tecky (' + Math.round(d0) + ' px, puis ' + Math.round(d1) + ' px)');
  // un aboiement : ils se roulent en boule, puis continuent
  run('P.cdBark = 0; P.dir = P.x < babies[0].x ? "right" : "left"; pressed.bark = true;'); step(2);
  ok(run('babies[0].anim') === 'ball', 'un aboiement : roulés en boule');
  step(60 * 2);
  ok(run('babies[0].mode') === 'follow' && run('babies[0].anim') !== 'ball', 'puis ils repartent');
  // trop loin : il attend
  run('P.x = 10 * 64; P.y = 5 * 64;'); step(10);
  ok(run('babies[0].mode') === 'wait', 'Tecky trop loin : il attend');
  run('P.x = babies[0].x + 40; P.y = babies[0].y;'); step(2);
  ok(run('babies[0].mode') === 'follow', 'Tecky revient : il le suit de nouveau');
  // sauvegarde : un petit qui suivait attend à sa place
  run('saveGame(); var sv = STORE.get(SAVE_KEY);');
  ok(run('sv.piq') === 'asked' && run('sv.babies[0][2]') === 'wait' && run('sv.babies[2][2]') === 'hidden', 'sauvegardés (qui suit attend ; les autres cachés)');
  run('toTitle(); loadGame(STORE.get(SAVE_KEY), false);'); advanceDialog();
  ok(run('piq.state') === 'asked' && run('babies[0].mode') === 'wait' && run('babies[2].mode') === 'hidden', 'Continuer : tout est à sa place');
  // tous chez leur maman : elle appelle, puis remercie (os, points), badge
  run('dogs = []; cars = []; P.inv = 999; pops = [];');
  run('babies.forEach(b => { b.x = piquette.x + 120; b.y = piquette.y + 60; b.mode = "follow"; b.seq = ++babySeq; });');
  step(2);
  ok(run('babiesLeft()') === 0 && run('pops.some(p => /Viens me voir/.test(p.text))'), 'tous rentrés : « Tous mes petits ! Viens me voir ! »');
  step(60 * 2);
  ok(run('babies.every(b => dist(b.x, b.y, piquette.x, piquette.y) < 80)'), 'blottis contre leur maman');
  run('P.x = piquette.x; P.y = piquette.y + 110; P.mode = "free"; var sc0 = score;'); step(2);
  run('P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('state') === 'dialog' && /Mes trois petits/.test(run('dialog.lines[0].text')), 'Maman Piquette remercie Tecky');
  advanceDialog();
  ok(run('piq.state') === 'done' && run('score') === run('sc0 + 150') && run('items[items.length - 1].n') === 'bone', 'un os et des points');
  step(40);
  ok(run('!!badges.herissons') && run('QUESTS_DONE[5]()'), 'badge « Nounou des hérissons », compté dans la complétion');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
