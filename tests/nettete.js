// images nettes : l'atlas x4 en pages, lu aux mêmes places que l'atlas x2 ; sol peint à la demande, à l'échelle chargée
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = [];');
  // --- l'atlas : aucune image à cheval sur deux pages
  const PAGE = 2048;
  const frames = run('Object.keys(ATLAS).reduce((a, k) => a.concat(ATLAS[k].f.map(f => [k, f[1], f[3]])), [])');
  ok(frames.length > 1000 && frames.every(([k, y, h]) => Math.floor(y / PAGE) === Math.floor((y + h - 1) / PAGE)),
     frames.length + ' images dans l\\'atlas, aucune à cheval sur deux pages de ' + PAGE + ' px');
  const hd = run('HD_SRC');
  if (!hd) ok(true, 'jeu construit sans les images x4 (--sans-hd) : rien à charger');
  else {
    const pages = Math.max(...frames.map(([k, y, h]) => Math.floor((y + h - 1) / PAGE))) + 1;
    ok(hd.k === 2 && hd.page === PAGE && hd.atlas.length === pages && /tiles_x4\\.png\\?v=/.test(hd.tiles),
       'HD_SRC : ' + hd.atlas.length + ' pages d\\'atlas x4 et le tileset, avec leur version');
  }
  // --- sans navigateur à grand écran, rien n'est demandé : le jeu lit l'atlas x2
  ok(run('HD.k') === 1 && !run('HD.asked') && !run('wantHD()'), 'ici (ni adresse, ni fichiers), le jeu reste en x2');
  run('var calls = [], moves = []; ctx.drawImage = function () { calls.push([].slice.call(arguments)); }; ctx.translate = function (x, y) { moves.push([x, y]); };');
  const key = 'tecky/idle/down';
  const f = run('ATLAS["' + key + '"].f[0]'), o = run('ATLAS["' + key + '"].o');
  run('calls = []; drawSpr("' + key + '", 0, 300, 200);');
  let c = run('calls[0]');
  ok(run('calls[0][0] === atlas') && c.slice(1, 5).join() === f.slice(0, 4).join() && c[7] === f[2] && c[8] === f[3],
     'en x2, drawSpr lit le cadre tel quel dans l\\'atlas embarqué');
  // --- les images nettes : même cadre, deux fois plus de pixels, dans la bonne page
  run('var P0 = { page: 0 }, P1 = { page: 1 }, T4 = { tiles: 4 }; setHD(2, ' + PAGE + ', [P0, P1], T4);');
  ok(run('HD.k') === 2 && run('ground.size') === 0, 'images nettes posées : le sol est à repeindre');
  run('calls = []; drawSpr("' + key + '", 0, 300, 200);');
  c = run('calls[0]');
  const p = Math.floor(f[1] / PAGE);
  ok(run('calls[0][0] === [P0, P1][' + p + ']') && c[1] === f[0] * 2 && c[2] === (f[1] - p * PAGE) * 2 && c[3] === f[2] * 2 && c[4] === f[3] * 2,
     'en x4, drawSpr lit le même cadre deux fois plus grand, dans la page ' + p);
  ok(c[5] === f[4] - o[0] && c[6] === f[5] - o[1] && c[7] === f[2] && c[8] === f[3], 'et le pose au même endroit, à la même taille');
  const autre = frames.find(([k, y]) => Math.floor(y / PAGE) !== p);
  if (autre) {
    run('calls = []; drawSpr("' + autre[0] + '", ' + run('ATLAS["' + autre[0] + '"].f.findIndex(f => f[1] === ' + autre[1] + ')') + ', 0, 0);');
    const q = Math.floor(autre[1] / PAGE);
    ok(run('calls[0][0] === [P0, P1][' + q + ']') && run('calls[0][2]') === (autre[1] - q * PAGE) * 2,
       'une image de la page ' + q + ' (' + autre[0] + ') est lue dans cette page, à sa hauteur dans la page');
  }
  // la jauge des chiens : seulement une partie de la largeur
  const fb = run('ATLAS["hud/enemy_bar_fill"].f[0]');
  run('calls = []; blit(ctx, ATLAS["hud/enemy_bar_fill"].f[0], 10, 20, 9, ' + fb[3] + ', 9);');
  ok(run('calls[0][3]') === 18 && run('calls[0][7]') === 9, 'blit(…, part) : la jauge est coupée à la même proportion');
  // --- l'interface : en 1080p ses sprites x2 sont déjà à leur taille ; images nettes seulement si elle est agrandie
  run('scale = 2; guiTransform(); calls = []; drawSpr("' + key + '", 0, 300, 200);');
  ok(run('calls[0][0] === atlas'), 'interface à l\\'échelle 1 (canevas de 1920 px) : atlas x2, tel quel');
  run('scale = 4; guiTransform(); calls = []; drawSpr("' + key + '", 0, 300, 200);');
  ok(run('calls[0][0] === [P0, P1][' + p + ']'), 'interface agrandie (canevas 4K) : images nettes');
  run('scale = 2; drawWorld(); calls = []; drawSpr("' + key + '", 0, 300, 200);');
  ok(run('calls[0][0] === [P0, P1][' + p + ']'), 'le monde : toujours les images nettes');
  // --- un sprite immobile tombe sur un pixel du canevas
  run('scale = 2; moves = []; drawSpr("' + key + '", 0, 371.2, 205.7);');
  ok(run('moves[0][0]') === 371 && run('moves[0][1]') === 205.5, 'drawSpr pose l\\'origine sur la grille des pixels (371,2 -> 371 ; 205,7 -> 205,5 à l\\'échelle 2)');
  // --- le sol : blocs de 8 tuiles en x4, peints depuis le tileset net, à la demande
  run('resetGround(); calls = []; camX = 20 * 64; camY = 20 * 64; drawGround(camX, camY);');
  const blocs = run('[...ground.values()].map(k => [k.c.width, k.k, k.w])');
  ok(run('chunkTiles()') === 8 && blocs.length >= 2 && blocs.length <= 9 && blocs.every(([w, k, ww]) => k === 2 && w === (8 * 64 + 2 * 2) * 2 && ww === 8 * 64 + 4),
     blocs.length + ' blocs de 8 tuiles peints pour un écran, à l\\'échelle 2 (' + blocs[0][0] + ' px de canevas)');
  ok(run('calls.some(c => c[0] === T4 && c[3] === 128 && c[7] === 128)'), 'peints depuis le tileset x4, une tuile = 128 px');
  // (les blocs seulement : l'habillage de l'herbe et les ombres passent aussi par des canevas, en les peignant)
  ok(run('(() => { const blocs = new Set([...ground.values()].map(k => k.c)); const v = calls.filter(c => blocs.has(c[0])); return v.length > 0 && v.every(c => c[3] === c[7] * 2 && c[4] === c[8] * 2); })()'), 'et posés à l\\'écran deux fois plus petits que leur canevas');
  run('for (let y = -128; y < MAP.h * 64; y += 300) for (let x = -128; x < MAP.w * 64; x += 500) drawGround(x, y);');
  ok(run('ground.size') === run('GROUND_MAX'), 'toute la carte parcourue : ' + run('GROUND_MAX') + ' blocs gardés, pas un de plus');
  run('calls = []; drawGround(-64, -64); drawGround(-64, -64);');
  const n1 = run('calls.filter(c => c[0] === T4).length');
  run('calls = []; drawGround(-64, -64);');
  ok(n1 > 0 && run('calls.filter(c => c[0] === T4).length') === 0, 'un bloc déjà peint n\\'est pas repeint');
  run('calls = []; drawHole(500, 500);');
  ok(run('calls[0][0] === T4') && run('calls[0][3]') === 128 && run('calls[0][7]') === 64, 'le trou d\\'un trésor aussi vient du tileset net');
  // --- la carte de la pause se construit toujours, avec le tileset x2
  run('calls = []; mapImg = null; buildMapImg();');
  ok(run('!!mapImg') && run('calls.some(c => c[0] === tilesImg)') && !run('calls.some(c => c[0] === T4)'), 'la carte de la pause garde le tileset x2 (elle est au quart)');
  // --- l'écran titre le dit, à côté de la version
  run('var txt = []; var fill0 = ctx.fillText; ctx.fillText = function (s) { txt.push(String(s)); }; openTitleMenu(); drawTitle();');
  ok(run('txt.some(s => / · images x4$/.test(s))'), 'écran titre : « ' + run('txt.find(s => /images x4$/.test(s))') + ' »');
  run('txt = []; setHD(1, 0, null, null); drawTitle(); ctx.fillText = fill0; setHD(2, ' + PAGE + ', [P0, P1], T4);');
  ok(!run('txt.some(s => /images x/.test(s))') && run('txt.includes(VERSION)'), 'en x2, seulement la version');
  // --- retour en x2
  run('setHD(1, 0, null, null); calls = []; drawSpr("' + key + '", 0, 300, 200);');
  ok(run('calls[0][0] === atlas') && run('chunkTiles()') === 16, 'sans images nettes : atlas x2, blocs de 16 tuiles');
  // --- quand les demander : un grand écran, une vraie adresse, pas un téléphone
  run('this.location = { protocol: "https:" }; scale = 2;');
  ok(!!run('HD_SRC') === run('wantHD()'), 'grand écran servi en https : les images nettes sont demandées (si elles existent)');
  run('this.location = { protocol: "https:", search: "?x2" };');
  ok(!run('wantHD()'), '« ?x2 » dans l\\'adresse : non (pour comparer)');
  run('this.location = { protocol: "https:", search: "" }; scale = 1.4;');
  ok(!run('wantHD()'), 'fenêtre moyenne (échelle 1,4, canevas de 1344 px) : non, le x2 suffit');
  run('scale = 2; this.matchMedia = () => ({ matches: true });');
  ok(!run('wantHD()'), 'téléphone ou tablette (pointeur grossier) : non');
  run('this.matchMedia = () => ({ matches: false }); this.location = { protocol: "file:" };');
  ok(!run('wantHD()'), 'page ouverte depuis le disque : non');
}, 50);`);
