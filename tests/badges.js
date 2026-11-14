// badges : médailles gardées d'une partie à l'autre, annonce « Nouveau badge ! », écran des badges
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  const ids = () => run('menu.items.map(i => i.id).join()');
  // (ce test éprouve le premier épisode seul : l'été est remis en chantier, sinon une victoire au printemps l'ouvre
  // et l'écran titre le propose)
  run('EPISODES[1].chantier = true;');
  run('audioOn(); STORE.mem = {}; loadBadges(); toTitle();');
  // (les badges de l'été ne sont ni montrés ni comptés tant que l'épisode n'est pas ouvert)
  const N = run('shownBadges().length'), T = run('MAP.badges.length');
  ok(N === 16 && T === 32 && run('ATLAS["hud/badge"].f.length') === T + 1 && run('badgePages().join()') === 'printemps',
     N + ' badges montrés sur ' + T + ' (et l’image « verrouillé ») : une seule page');
  ok(run('MAP.badges.every(id => txtAt("badges." + id + ".nom") && txtAt("badges." + id + ".but"))'), 'chacun a un nom et un objectif');
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
  // l'aboiement du doberman et la charge du chien de berger font mal, mais ce ne sont pas des morsures
  run('var D = dogs.find(d => d.kind === "molosse"); P.x = 30 * 64; P.y = 33 * 64; D.x = P.x + 120; D.y = P.y; dogs = [D];');
  run('Object.assign(D, { mode: "bark", dir: "left", t: 0.3, hitDone: false }); P.inv = 0; P.mode = "free"; graceT = 0; var hp0 = P.hp;'); step(1);
  ok(run('P.hp') < run('hp0') && !run('bitten'), 'l’aboiement du doberman fait mal, mais n’est pas une morsure');
  run('dogs = []; P.inv = 0; P.mode = "free"; graceT = 0; hurtPlayer(1, P.x + 40, P.y, false);');
  ok(!run('bitten'), 'une charge non plus');
  run('dogs = []; P.inv = 0; P.mode = "free"; graceT = 0; hurtPlayer(1, P.x + 40, P.y);');
  ok(run('bitten') && run('saveGame() || loadSave().bitten'), 'une morsure : notée (et sauvegardée)');
  run('timePlayed = 300; clues = [true, true, true]; revealAlice(); P.inv = 999; P.x = alice.x; P.y = alice.y + 100;'); step(2); advanceDialog();
  ok(!run('badges.intact'), 'pas de badge « Sans une égratignure »');
  // copains : en balade, tous les chiens copains
  run('newGame("balade", true)'); advanceDialog();
  run('dogs.forEach(d => d.friend = true);'); step(40);
  ok(run('!!badges.copains'), 'balade : tous copains');
  // écran des badges
  run('toTitle();');
  ok(new RegExp('(' + [1, 2, 3, 4, 5].map(k => N - k).join('|') + ') sur ' + N).test(run('menu.items[menu.items.length - 1].sub')), 'menu : ' + run('menu.items[menu.items.length - 1].sub'));
  run('menu.sel = menu.items.length - 1; pressed.ok = true'); step(1);
  ok(run('state') === 'badges', 'écran des badges');
  run('used = []; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; render(); drawSpr = ds0;');
  ok(run('used.filter(k => k === "hud/badge").length') === N, 'les ' + N + ' médailles (une rangée de plus : cases compactes)');
  run('pressed.right = true'); step(1);
  ok(run('state') === 'badges' && run('badgePage') === 0, 'une seule page : la flèche ne fait rien');
  run('pressed.pause = true'); step(1);
  ok(run('state') === 'title' && run('menu.items[menu.sel].id') === 'badges', 'Échap : retour au menu, sur « Badges »');
  // l'été ouvert : ses badges ont leur page
  run('EPISODES[1].chantier = false; toTitle();');
  ok(run('epOpen(EPISODES[1])') && run('badgePages().join()') === 'printemps,ete' && run('shownBadges().length') === T
     && run('menu.items[menu.items.length - 1].sub').includes(' sur ' + T), 'l’été ouvert : deux pages, ' + T + ' badges comptés');
  run('menu.sel = menu.items.length - 1; pressed.ok = true'); step(1);
  run('pressed.right = true'); step(1);
  run('used = []; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; render(); drawSpr = ds0;');
  ok(run('badgePage') === 1 && run('used.filter(k => k === "hud/badge").length') === 16, 'flèche droite : la page de l’été, seize médailles comme au printemps');
  ok(run('badgeIds("ete").length') === 16 && run('new Set(badgeIds("ete")).size') === 16 && run('badgeIds("ete").every(id => badgeEp(id) === "ete")')
     && run('MAP.badges.filter(id => badgeEp(id) === "ete").length') === 16, 'la page de l’été range tous ses badges, une fois chacun');
  // les pendants d'été : sur la côte seulement
  run('toTitle(); episode = "ete"; delete EPISODES[1].voyage; newGame("aventure", true);'); advanceDialog();
  run('var avant = Object.keys(badges).length; critters.forEach(c => c.scored = true); seenCells.fill(1); P.swum = true; beachNap = true; checkBadges();');
  ok(run('MAP.id') === 'monde' && !run('badges.bain || badges.sieste_ete || badges.explorateur_ete || badges.crabes || badges.goelands'), 'dans le monde, aucun badge de la côte');
  run('useMap("cote"); resetWorld(); dogs = []; cars = []; P.x = MAP.start[0] * 64; P.y = MAP.start[1] * 64; P.inv = 999; P.swum = false; beachNap = false; treasures = 0; seenCells.fill(0); checkBadges();');
  ok(!run('badges.bain || badges.sieste_ete || badges.explorateur_ete || badges.crabes || badges.goelands || badges.os_dores_ete || badges.copains_ete'), 'sur la côte, rien n’est donné d’avance');
  run('P.swum = true; beachNap = true; treasures = MAP.dig.length; seenCells.fill(1); crabs.forEach(c => c.scored = true); seagulls.forEach(g => g.scored = true); checkBadges();');
  ok(['bain', 'sieste_ete', 'os_dores_ete', 'explorateur_ete', 'crabes', 'goelands'].every(id => run(`!!badges.${id}`)) && !run('badges.copains_ete'),
     'baignade, sieste sur le sable, os dorés, carte, crabes, goélands');
  // un pincement n'est pas une morsure, mais c'est un coup
  run('P.inv = 0; P.mode = "free"; graceT = 0; bitten = false; scratched = false; var cz = MAP.calm; MAP.calm = []; hurtPlayer(1, P.x + 40, P.y, false); MAP.calm = cz;');
  ok(!run('bitten') && run('scratched') && run('saveGame() || loadSave().scratched'), 'un pincement : pas une morsure, mais un coup (sauvegardé)');
  run('delete badges.aventure; delete badges.intact; delete badges.rapide; timePlayed = 300; winBadges();');
  ok(run('!!badges.aventure_ete && !!badges.rapide_ete && !badges.intact_ete') && !run('badges.aventure || badges.intact || badges.rapide'),
     'victoire sur la côte : les retrouvailles et la vitesse de l’été, pas « ' + run('badgeName("intact_ete")') + ' », ni les badges du printemps');
  run('scratched = false; winBadges();');
  ok(run('!!badges.intact_ete'), 'sans un coup : « ' + run('badgeName("intact_ete")') + ' »');
  run('toTitle(); menu.sel = menu.items.length - 1; pressed.ok = true'); step(1); run('badgePage = 1;');
  run('badgesTap(GW / 2 - 200, BADGE_PICK.y - 14)');
  ok(run('badgePage') === 0 && run('state') === 'badges', 'au toucher, la flèche de gauche revient à la première page');
  run('badgesTap(GW / 2, 700)');
  ok(run('state') === 'title', 'toucher ailleurs : retour au menu');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
