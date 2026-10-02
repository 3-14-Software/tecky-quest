// badges : médailles gardées d'une partie à l'autre, annonce « Nouveau badge ! », écran des badges
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  const ids = () => run('menu.items.map(i => i.id).join()');
  run('audioOn(); STORE.mem = {}; loadBadges(); toTitle();');
  const N = run('MAP.badges.length');
  ok(N === 13 && run('ATLAS["hud/badge"].f.length') === N + 1, N + ' badges (et l’image « verrouillé »)');
  ok(run('MAP.badges.every(id => BADGE_INFO[id])'), 'chacun a un nom et un objectif');
  ok(ids().endsWith('options,badges') && run('menu.items[menu.items.length - 1].sub').includes('0 sur ' + N), 'menu principal : « Badges », 0 sur ' + N);
  run('menu.sel = menu.items.findIndex(i => i.id === "aventure"); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999; P.x = 8 * 64; P.y = 5 * 64 + 32; P.mode = "free";');
  // la sieste
  { let k = 0; while (!run('napped') && k++ < 60 * 30) step(1); }
  step(40);
  ok(run('!!badges.sieste') && run('toasts.length') === 1 && run('toasts[0].id') === 'sieste', 'Tecky s’endort : badge « Roi de la sieste », annoncé');
  run('var used = []; var ds0 = drawSpr; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; render(); drawSpr = ds0;');
  ok(run('used.includes("hud/badge")'), 'annonce dessinée (médaille)');
  ok(run('STORE.get(BADGES_KEY).sieste') > 0, 'gardé dans le navigateur');
  step(60 * 5);
  ok(run('toasts.length') === 0, 'l’annonce s’efface');
  run('napped = true;'); step(40);
  ok(run('toasts.length') === 0, 'pas deux fois le même badge');
  // quêtes, petites bêtes, canards, os dorés, carte
  run('farm.state = "done"; post.state = "done"; rose.state = "done";'); step(40);
  ok(run('!!badges.poules && !!badges.facteur && !!badges.chat'), 'quêtes finies : berger, facteur, ami des chats');
  run('critters.forEach(c => c.scored = true); ducks.forEach(d => d.scored = true); treasures = MAP.dig.length; seenCells.fill(1);'); step(40);
  ok(['betes', 'canards', 'os_dores', 'explorateur'].every(id => run(`!!badges.${id}`)), 'petites bêtes, canards, os dorés, carte entière');
  ok(run('toasts.length') >= 3, 'les annonces attendent leur tour (' + run('toasts.length') + ')');
  // victoire en aventure, sans morsure, en moins de 10 minutes
  run('timePlayed = 300; bitten = false; clues = [true, true, true]; revealAlice(); P.x = alice.x; P.y = alice.y + 100;'); step(2);
  ok(run('!!badges.aventure && !!badges.intact && !!badges.rapide'), 'Alice retrouvée : retrouvailles, sans égratignure, truffe rapide');
  advanceDialog(); step(70); run('pressed.ok = true'); step(1);     // la scène de fin, passée
  run('used = []; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; overT = 2; render(); drawSpr = ds0;');
  ok(run('state') === 'win' && run('newBadges.length') >= 10 && run('used.filter(k => k === "hud/badge").length') >= 10, 'écran de victoire : les badges de la partie');
  // une morsure suffit pour perdre « Sans une égratignure » (nouvelle partie, badge pas encore gagné)
  run('delete badges.intact; newGame("aventure", true);'); advanceDialog();
  run('dogs = []; P.inv = 0; graceT = 0; hurtPlayer(1, P.x + 40, P.y);');
  ok(run('bitten') && run('saveGame() || loadSave().bitten'), 'une morsure : notée (et sauvegardée)');
  run('timePlayed = 300; clues = [true, true, true]; revealAlice(); P.inv = 999; P.x = alice.x; P.y = alice.y + 100;'); step(2); advanceDialog();
  ok(!run('badges.intact'), 'pas de badge « Sans une égratignure »');
  // copains : en balade, tous les chiens copains
  run('newGame("balade", true)'); advanceDialog();
  run('dogs.forEach(d => d.friend = true);'); step(40);
  ok(run('!!badges.copains'), 'balade : tous copains');
  // écran des badges
  run('toTitle();');
  ok(new RegExp('(' + (N - 2) + '|' + (N - 1) + ') sur ' + N).test(run('menu.items[menu.items.length - 1].sub')), 'menu : ' + run('menu.items[menu.items.length - 1].sub'));
  run('menu.sel = menu.items.length - 1; pressed.ok = true'); step(1);
  ok(run('state') === 'badges', 'écran des badges');
  run('used = []; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; render(); drawSpr = ds0;');
  ok(run('used.filter(k => k === "hud/badge").length') === N, 'les ' + N + ' médailles (une rangée de plus : cases compactes)');
  run('pressed.pause = true'); step(1);
  ok(run('state') === 'title' && run('menu.items[menu.sel].id') === 'badges', 'Échap : retour au menu, sur « Badges »');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
