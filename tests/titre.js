// l'écran titre dessiné (un paysage par saison, le menu à droite) et l'été plus marqué sur le monde : palette,
// lumière et ombres de la saison, décors d'été posés (la liste « extras » de la surcharge).
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  const step = n => { for (let i = 0; i < n; i++) run('pollPad(); update(1 / 60);'); };
  run('audioOn(); STORE.mem = {}; loadBadges(); toTitle();');
  // ---- sans les images (la page seule, les tests) : l'écran titre d'avant
  ok(run('typeof TITRE') === 'object' && run('Object.keys(TITRE.fonds).join()') === 'printemps,ete'
     && ['nuage', 'alice_printemps', 'alice_ete', 'tecky', 'papillon', 'mouette'].every(n => run(`TITRE.meta.${n}.f.length`) > 0),
     'la page connaît les images du titre : un paysage par saison, la planche de ce qui bouge');
  ok(!run('titleArt.ok') && !run('artOn()') && run('titleCX()') === run('GW / 2') && run('menuBox(0).x + menu.w / 2') === run('GW / 2'),
     'sans ces images : le monde sous son voile, le menu au milieu');
  run('var monde = 0, dw0 = drawWorld; drawWorld = function () { monde++; return dw0.apply(this, arguments); }; render();');
  ok(run('monde') === 1, 'le monde est à l’image');
  // ---- les images arrivées : le paysage de la saison, le menu à droite, le monde plus dessiné
  run('titleArt.ok = true; titleArt.sheet = {}; titleArt.fonds = { printemps: { n: "printemps" }, ete: { n: "ete" } };');
  run('var posees = [], di0 = ctx.drawImage; monde = 0; render();');
  ok(run('artOn()') && run('monde') === 0 && run('titleArt.shown') === 'printemps' && run('titleArt.t') === 1,
     'images chargées : le paysage du printemps, sans dessiner le monde');
  ok(run('titleCX()') === run('ART.cx') && run('menuBox(0).x + menu.w / 2') === run('ART.cx') && run('menuBox(0).x + menu.w') < run('GW'),
     'le logo et le menu passent à droite');
  run('var b = menuBox(1); menu.sel = 0;');
  ok(run('menuHit(b.x + 20, b.y + 20)') === 1 && run('menuHit(GW / 2 - 300, b.y + 20)') === -1, 'au toucher, les entrées sont là où on les voit');
  // ---- changer d'épisode : le paysage de l'été, en fondu
  run('STORE.set(RECORDS_KEY, { aventure: { wins: 1 } }); openTitleMenu();');
  ok(run('openEpisodes().length') === 2, 'le printemps gagné : deux épisodes');
  run('pressed.right = true;'); step(1); run('pressed.right = false; render();');
  ok(run('episode') === 'ete' && run('titleArt.shown') === 'ete' && run('titleArt.from') === 'printemps' && run('titleArt.t') < 1,
     'flèche droite : le paysage de l’été remplace celui du printemps, en fondu');
  step(60);
  ok(run('titleArt.t') === 1, 'le fondu est fini');
  ok(run('episodeTap(ART.cx - 200, EP_PICK.y - 10)') && run('episode') === 'printemps', 'au toucher, le choix de l’épisode est à droite lui aussi');
  // ---- Options et Badges, ouverts depuis le titre, restent sur le paysage ; une partie ne le montre plus
  run('menu.sel = menu.items.findIndex(it => it.id === "badges"); pressed.ok = true;'); step(1);
  run('monde = 0; render();');
  ok(run('state') === 'badges' && run('artOn()') && run('monde') === 0 && run('titleCX()') === run('GW / 2'), 'l’écran des badges se pose sur le paysage');
  run('toTitle(); newGame("aventure", true); monde = 0; render();');
  ok(!run('artOn()') && run('monde') === 1, 'en jeu : le monde');
  // ---- l'été sur le monde : la lumière, les ombres, les décors posés
  ok(!run('SUMMER()') && run('SHADOW.alpha') === run('SHADOW.alphaPr') && run('(sun = 0, shadowLen())') === 1
     && run('SUN.tints[0].join()') === '255,255,255', 'au printemps : la lumière et les ombres de toujours');
  ok(!run('decor.some(d => ["clothesline", "paddling_pool", "deckchair"].includes(d.n))'), 'pas de linge ni de pataugeoire au printemps');
  run('toTitle(); episode = "ete"; delete EPISODES[1].voyage; newGame("balade", true);');
  ok(run('SUMMER()') && run('MAP.id') === 'region' && run('SHADOW.alpha') > run('SHADOW.alphaPr') && run('(sun = 0, shadowLen())') < 1
     && run('SUN.tints[0][2]') < 255, 'en été : des ombres plus courtes et plus franches, une teinte dorée en plein jour');
  ok(['clothesline', 'paddling_pool', 'deckchair', 'hay'].every(n => run(`decor.some(d => d.n === "${n}")`))
     && run('decor.filter(d => d.n === "deckchair").length') === 3, 'le monde en été a son linge qui sèche, sa pataugeoire, ses transats');
  ok(run('["clothesline", "paddling_pool", "deckchair"].every(n => { const d = decor.find(d => d.n === n); return blockedFeet(d.x, d.y - 8, 8); })'),
     'ce sont des obstacles');
  ok(['corde_a_linge', 'pataugeoire', 'transat'].every(n => run(`!!ATLAS["decor/${n}"] && !!MAP.sols["${n}"]`)), 'chacun a son dessin et sa ligne de contact (son ombre portée)');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
