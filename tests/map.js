// carte agrandie : sol en blocs, rivière infranchissable sauf par le pont, garde-corps
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; P.inv = 99;');
  ok(run('MAP.w') === 96 && run('MAP.h') === 64, 'carte de 96 x 64 tuiles');
  ok(run('ground.size') >= 1 && run('ground.size') <= 4 && run('[...ground.values()].every(k => k.c.width === 1024 + 2 * CM && k.c.height === 1024 + 2 * CM)'),
     'sol pré-rendu à la demande : ' + run('ground.size') + ' blocs de 1024 px pour l\\'écran du début');
  run('for (let y = -128; y < MAP.h * 64; y += 300) for (let x = -128; x < MAP.w * 64; x += 500) drawGround(x, y);');
  ok(run('ground.size') === run('GROUND_MAX'), 'toute la carte parcourue : jamais plus de ' + run('GROUND_MAX') + ' blocs gardés');
  const walkDown = (x, n) => { run('P.x = ' + x + '; P.y = 40.4*64; P.mode = "free";'); step(n, 'held.down = true'); run('held.down = false'); return run('P.y') / 64; };
  ok(walkDown('80*64', 200) > 47, 'on traverse la rivière par le pont');
  ok(walkDown('76*64', 200) < 42.2, 'ailleurs, la rivière bloque');
  ok(walkDown('7*64', 200) < 42.2, 'au bout du chemin de la barque aussi');
  run('P.x = 80*64; P.y = 43.5*64; P.mode = "free";'); step(120, 'held.right = true'); run('held.right = false');
  ok(run('P.x') / 64 < 81.1, 'le garde-corps retient Tecky sur le pont (x = ' + (run('P.x') / 64).toFixed(2) + ')');
  ok(run('MAP.decor.some(d => d[0] === "bridge")') && run('FLAT.has("bridge")'), 'le pont est dessiné à plat, sous les personnages');
  // eau animée : des vaguelettes sur la rivière, jamais hors de l'eau, aucune au-dessus des champs
  run('var rip = [], gl = []; var drawSpr0 = drawSpr; drawSpr = function (k, f, x, y) { if (k === "fx/ripple") rip.push([x, y, f]); if (k === "fx/glint") gl.push([x, y, f]); return drawSpr0.apply(this, arguments); };');
  let pts = [];
  for (let t = 0; t < 4; t += 0.37) { run('rip = []; drawWater(30 * 64, 39 * 64, ' + t + ');'); pts = pts.concat(run('rip')); }
  ok(pts.length > 100 && pts.every(([x, y]) => run('deepWater(' + x + ', ' + y + ')')), pts.length + ' vaguelettes sur la rivière, toutes en eau profonde (loin des berges)');
  ok(pts.length / 11 < 40, 'peu nombreuses : ' + Math.round(pts.length / 11) + ' par image pour une rivière qui traverse l\\'écran');
  ok(new Set(pts.map(p => p[2])).size >= 6, 'à différentes étapes de leur animation');
  run('gl = []; for (let t = 0; t < 6; t += 0.29) drawWater(30 * 64, 39 * 64, t);');
  const gls = run('gl');
  ok(gls.length > 10 && gls.every(([x, y]) => run('deepWater(' + x + ', ' + y + ')')), gls.length + ' scintillements en plus des vaguelettes, en eau profonde');
  run('rip = []; drawWater(64 * 64, 2 * 64, 1.2); drawSpr = drawSpr0;');
  // fontaine animée : 8 images, le dessin change d'image avec le temps
  ok(run('ATLAS["decor/fountain"].f.length') === 8 && run('MAP.decorFps.fountain') === 10, 'la fontaine a 8 images à 10 par seconde');
  ok(run('rip.length') === 0, 'aucune vaguelette loin de l\\'eau');
  // --- la nature (nature.py) : variantes tirées de la position, ombres portées, herbe habillée
  const nat = run('decor.concat(EDGE_DECOR).filter(d => MAP.variants[d.n])');
  ok(nat.length > 150 && nat.every(d => run('!!ATLAS["' + d.key + '"] && !!ATLAS["' + d.shadow + '"]')) && nat.every(d => !d.flip),
     nat.length + ' arbres, sapins, buissons… : chacun a son modèle et son ombre, jamais en miroir');
  ok(new Set(nat.filter(d => d.n === 'tree').map(d => d.key)).size >= 4 && new Set(nat.filter(d => d.n === 'fir').map(d => d.key)).size === 3
     && new Set(nat.filter(d => d.n === 'bush').map(d => d.key)).size >= 4, 'plusieurs modèles d\\'arbres, de sapins et de buissons sur la carte');
  const avant = nat.map(d => d.key).join();
  run('reset();');
  ok(run('decor.concat(EDGE_DECOR).filter(d => MAP.variants[d.n]).map(d => d.key).join()') === avant, 'les mêmes d\\'une partie à l\\'autre (tirés de la position)');
  ok(run('decor.length === MAP.decor.length && decor.every((d, i) => d.n === MAP.decor[i][0])'), 'le décor garde son nom (obstacle, refuge, feuilles)');
  run('var semis = [], blit0 = blit; blit = function (g, f) { semis.push(f); blit0.apply(null, arguments); }; resetGround(); drawGround(18 * 64, 24 * 64); blit = blit0;');
  const cles = k => run('semis.filter(f => ATLAS["' + k + '"].f.includes(f)).length');
  ok(cles('sol/brins') > 30 && cles('sol/fleur') > 3, 'le pré : ' + cles('sol/brins') + ' touffes de brins et ' + cles('sol/fleur') + ' fleurs semées dans le sol d\\'un écran');
  ok(run('semis.some(f => Object.keys(ATLAS).some(k => k.startsWith("ombre/") && ATLAS[k].f.includes(f)))'), 'et les ombres des arbres y sont peintes');
  ok(run('grassAt(20, 27)') && !run('grassAt(80, 43)') && !run('grassAt(40, 19)'), 'herbe pleine dans le pré, pas dans la rivière ni sur la route');
  // --- l'eau habillée : nénuphars entre les hauts-fonds et le large, galets sur le sable, rien le long d'un quai
  run('var lys = [], gal = []; for (let ty = -2; ty < MAP.h + 2; ty++) for (let tx = -2; tx < MAP.w + 2; tx++) { const l = lilyAt(tx, ty); if (l) lys.push([tx, ty, l[0], l[1]]);'
    + ' if (shoreTile(tx, ty) && hash3(tx, ty, 90) < POND.pebbles) { const p = shorePoint(tx, ty, POND.sand, 91, 10); if (p) gal.push([tx, ty, p[0], p[1]]); } }');
  const lys = run('lys'), gal = run('gal');
  const dedans = (L, m) => L.every(([tx, ty, x, y]) => x >= tx * 64 + m && x <= tx * 64 + 64 - m && y >= ty * 64 + m && y <= ty * 64 + 64 - m);
  ok(lys.length > 25 && lys.every(([tx, ty, x, y]) => run('waterVal(' + x + ', ' + y + ')') > 0.67 && run('shoreTile(' + tx + ', ' + ty + ')')),
     lys.length + ' nénuphars, tous sur l\\'eau, au large des hauts-fonds, près d\\'une rive de terre');
  ok(gal.length > 40 && gal.every(([tx, ty, x, y]) => Math.abs(run('waterVal(' + x + ', ' + y + ')') - run('POND.sand')) < 0.02),
     gal.length + ' galets, tous sur le sable de la berge');
  ok(dedans(lys, 13) && dedans(gal, 10), 'chacun dans sa tuile : un bloc de sol ne coupe ni nénuphar ni galet');
  ok(run('shoreTile(45, 41) && !fullWater(45, 41) && fullWater(45, 43) && !shoreTile(45, 43) && !shoreTile(45, 39)'),
     'la rive : les tuiles où l\\'eau touche l\\'herbe, ni le large ni la terre');
  run('rip = []; var drawSpr1 = drawSpr; drawSpr = function (k, f, x, y) { if (k === "fx/ripple") rip.push([x, y]); return drawSpr1.apply(this, arguments); };'
    + ' for (let t = 0; t < 12; t += 0.31) for (const [tx, ty] of lys.slice(0, 12)) drawWater(tx * 64 - 480, ty * 64 - 270, t); drawSpr = drawSpr1;');
  ok(run('rip.length') > 200 && run('rip.every(([x, y]) => !lilyAt(Math.floor((x - 8) / 64), Math.floor(y / 64)))'), 'aucune vaguelette dans la tuile d\\'un nénuphar (' + run('rip.length') + ' vaguelettes autour d\\'eux)');
  run('semis = []; blit0 = blit; blit = function (g, f) { semis.push(f); blit0.apply(null, arguments); }; resetGround(); drawGround(' + (lys[0][2] - 480) + ', ' + (lys[0][3] - 270) + '); blit = blit0;');
  ok(cles('sol/nenuphar') >= 1 && cles('sol/galet') >= 1, 'peints dans le sol : ' + cles('sol/nenuphar') + ' nénuphars et ' + cles('sol/galet') + ' galets autour du premier');
  // --- les bâtiments (batiments.py) : de trois quarts, avec leur ombre, leurs fenêtres du soir, leurs perchoirs
  const bat = run('decor.filter(d => d.night)');
  ok(bat.length >= 12 && bat.every(d => run('!!ATLAS["' + d.key + '"] && !!ATLAS["' + d.shadow + '"] && !!ATLAS["' + d.night + '"]')),
     bat.length + ' bâtiments : chacun a son dessin, son ombre portée et ses fenêtres allumées');
  ok(new Set(bat.filter(d => d.n === 'house_red').map(d => d.key)).size === 2, 'les deux maisons rouges ne sont pas les mêmes (façade devant, pignon devant)');
  ok(bat.filter(d => /^house|bakery/.test(d.n)).every(d => run('(MAP.perches["' + d.look + '"] || []).length') === 2
     && run('MAP.perches["' + d.look + '"].every(([dx, dy]) => { const s = ATLAS["' + d.key + '"], f = s.f[0]; return dx > f[4] - s.o[0] && dx < f[4] - s.o[0] + f[2] && dy > f[5] - s.o[1] && dy < -40; })')),
     'chaque maison a deux perchoirs pour les chats, sur son toit');
  // le soir : les fenêtres s'allument ; devant un bâtiment, un personnage reste devant (elles passent par un canevas à part)
  run('var nuit = [], drawSpr2 = drawSpr; drawSpr = function (k) { if (k.startsWith("nuit/")) nuit.push([k, ctx === mainCtx]); return drawSpr2.apply(this, arguments); }; var mainCtx = ctx;');
  run('var B = decor.find(d => d.n === "bakery"); villagers = []; cars = []; P.x = B.x - 400; P.y = B.y - 300; camX = B.x - 480; camY = B.y - 400; sun = 2; drawWorld();');
  ok(run('nuit.length') === 0, 'en fin d\\'après-midi, aucune fenêtre allumée');
  run('nuit = []; sun = 3.2; drawWorld();');
  ok(run('nuit.length') >= 1 && run('nuit.some(n => n[0] === "nuit/boulangerie")') && run('ctx === mainCtx'), 'au coucher du soleil, lampadaires allumés : ' + run('nuit.length') + ' bâtiments aux fenêtres allumées à l\\'écran');
  run('var traits = 0, drawP = P.draw; P.draw = function () { traits++; return drawP.apply(this, arguments); }; nuit = []; drawWorld();');
  ok(run('traits') === 1, 'Tecky loin de la boulangerie : dessiné une fois');
  run('traits = 0; nuit = []; P.x = B.x; P.y = B.y + 20; drawWorld();');
  ok(run('nuit.some(n => n[0] === "nuit/boulangerie")') && run('traits') >= 2 && run('ctx === mainCtx'),
     'Tecky devant la boulangerie : redessiné en gomme sur les fenêtres des bâtiments derrière lui (il reste devant elles)');
  run('P.draw = drawP;');
  run('drawSpr = drawSpr2; sun = 0;');
}, 50);`);
