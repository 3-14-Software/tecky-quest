// carte agrandie : sol en blocs, rivière infranchissable sauf par le pont, garde-corps
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; P.inv = 99;');
  ok(run('MAP.w') === 96 && run('MAP.h') === 64, 'carte de 96 x 64 tuiles');
  ok(run('ground.size') >= 1 && run('ground.size') <= 12 && run('[...ground.values()].every(k => k.c.width === 1024 + 2 * CM && k.c.height === 1024 + 2 * CM)'),
     'sol pré-rendu à la demande : ' + run('ground.size') + ' blocs de 1024 px pour l\\'écran du début');
  // blocs d'avance : une image qui n'a rien peint prépare un bloc dont la caméra s'approche, un seul, et pas plus loin
  run('var vx = 18 * 64, vy = 24 * 64; sun = 0; resetGround(); drawGround(vx, vy); var b0 = ground.size; prepareGround(vx, vy); var b1 = ground.size;'
    + ' drawGround(vx, vy); prepareGround(vx, vy); var b2 = ground.size; for (let i = 0; i < 8; i++) { drawGround(vx, vy); prepareGround(vx, vy); } var b3 = ground.size;');
  ok(run('b1 === b0') && run('b2 === b0 + 1') && run('b3 === b0 + 2') && run('ground.has("0,1") && ground.has("0,2") && !ground.has("3,1") && !ground.has("1,0")'),
     'blocs d\\'avance : rien dans l\\'image qui a peint l\\'écran (' + run('b0') + ' blocs), puis un par image, seulement ceux dont la caméra est à moins de ' + run('GROUND_AHEAD') + ' px');
  run('sun = 2; drawGround(vx, vy); prepareGround(vx, vy);');
  ok(run('[...ground.values()].filter(c => c.len === shadowLen()).length') === 1, 'pendant que le soleil descend, l\\'avance ne repeint pas les ombres : un bloc de l\\'écran par image, comme avant');
  run('sun = 0; resetGround();');
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
  ok(nat.length > 150 && nat.every(d => run('!!ATLAS["' + d.key + '"] && (MAP.sols["' + d.look + '"] || []).length > 0') !== ['barge', 'dog_bed'].includes(d.n)) && nat.every(d => !d.flip),
     nat.length + ' arbres, sapins, buissons, mobilier… : chacun a son modèle et son ombre (sauf la péniche, sur l\\'eau, et le panier, à plat), jamais en miroir');
  ok(new Set(nat.filter(d => d.n === 'tree').map(d => d.key)).size >= 4 && new Set(nat.filter(d => d.n === 'fir').map(d => d.key)).size === 3
     && new Set(nat.filter(d => d.n === 'bush').map(d => d.key)).size >= 4, 'plusieurs modèles d\\'arbres, de sapins et de buissons sur la carte');
  const avant = nat.map(d => d.key).join();
  run('reset();');
  ok(run('decor.concat(EDGE_DECOR).filter(d => MAP.variants[d.n]).map(d => d.key).join()') === avant, 'les mêmes d\\'une partie à l\\'autre (tirés de la position)');
  ok(run('decor.length === MAP.decor.length && decor.every((d, i) => d.n === MAP.decor[i][0])'), 'le décor garde son nom (obstacle, refuge, feuilles)');
  run('var semis = [], couches = [], blit0 = blit, cols0 = blitCols; blit = function (g, f) { semis.push(f); blit0.apply(null, arguments); };'
    + ' blitCols = function (g, f) { couches.push(f); cols0.apply(null, arguments); }; resetGround(); drawGround(18 * 64, 24 * 64); blit = blit0;');
  const cles = k => run('semis.filter(f => ATLAS["' + k + '"].f.includes(f)).length');
  ok(cles('sol/brins') > 30 && cles('sol/fleur') > 3, 'le pré : ' + cles('sol/brins') + ' touffes de brins et ' + cles('sol/fleur') + ' fleurs semées dans le sol d\\'un écran');
  ok(run('couches.length') > 20 && run('couches.every(f => Object.keys(MAP.sols).some(n => ATLAS["decor/" + n].f.includes(f)))'),
     'et les ombres des décors y sont peintes à partir de leur silhouette (' + run('couches.length') + ' bandes couchées)');
  // --- le sous-bois et le champ : habillés comme l'herbe, peints une fois dans le sol
  run('semis = []; blit = function (g, f) { semis.push(f); blit0.apply(null, arguments); }; var poses = [], put0 = chunkPut;'
    + ' chunkPut = function (g, x0, y0, k) { const p = put0(g, x0, y0, k); return function (key, i, x, y) { poses.push([key, i, x, y]); return p(key, i, x, y); }; };'
    + ' resetGround(); drawGround(70 * 64, 50 * 64);');
  ok(cles('sol/sousbois') > 40 && run('Object.values(MAP.wild).reduce((a, v) => a + v[1], 0)') === run('ATLAS["sol/sousbois"].f.length')
     && run('poses.filter(p => p[0] === "sol/sousbois").every(p => groundTile(Math.floor(p[2] / 64), Math.floor(p[3] / 64))[0] === MAP.wood)'),
     'le sous-bois : ' + cles('sol/sousbois') + ' fougères, mousses, brindilles… dans le sol d\\'un écran, toutes dans du sous-bois plein');
  ok(run('new Set(poses.filter(p => p[0] === "sol/sousbois").map(p => p[1])).size') >= 9, 'de toutes les sortes (fougères, mousse, champignons, pommes de pin, brindilles, feuilles)');
  run('semis = []; poses = []; resetGround(); drawGround(66 * 64, 22 * 64);');
  const plants = run('poses.filter(p => p[0] === "sol/culture")');
  ok(plants.length > 150 && run('ATLAS["sol/culture"].f.length') === 2 * run('MAP.crops') && new Set(plants.map(p => p[1] >> 1)).size >= 3,
     'le champ : ' + plants.length + ' plants en rangs, ' + new Set(plants.map(p => p[1] >> 1)).size + ' cultures à l\\'écran');
  ok(plants.every(p => run('fieldBits(' + Math.floor(p[2] / 64) + ', ' + Math.floor(p[3] / 64) + ')') > 0)
     && plants.every(p => run('MAP.furrows').some(f => Math.abs(((p[3] % 64) + 64) % 64 - f - run('FIELD.dy')) <= 2)),
     'tous dans le champ, sur les crêtes des buttes dessinées par la tuile (' + run('MAP.furrows.join(", ")') + ' px)');
  const rangs = {};
  plants.forEach(p => { (rangs[Math.round(p[3] / 8)] = rangs[Math.round(p[3] / 8)] || new Set()).add(p[1] >> 1); });
  ok(Object.values(rangs).every(s => s.size === 1), 'une seule culture par rang, d\\'un bout à l\\'autre');
  run('chunkPut = put0; blit = blit0;');
  // les ombres s'allongent quand le soleil baisse ; les blocs de sol sont alors repeints un par image
  ok(run('sun = 0, shadowLen()') === 1 && run('sun = 2, shadowLen()') > 1.4 && run('sun = 3, shadowLen()') > run('sun = 2, shadowLen()'),
     'ombres : longueur 1 en plein jour, ' + run('sun = 2, shadowLen()') + ' au coucher du soleil, ' + run('sun = 3, shadowLen()') + ' ensuite');
  run('sun = 0; resetGround(); drawGround(18 * 64, 24 * 64); var blocs = ground.size; sun = 2; couches = []; drawGround(18 * 64, 24 * 64);');
  const repeints = n => run('[...ground.values()].filter(c => c.len === shadowLen()).length') === n;
  ok(repeints(1) && run('couches.length') > 0, 'le soleil baisse : un seul bloc de sol repeint dans l\\'image');
  for (let i = 0; i < 8; i++) run('drawGround(18 * 64, 24 * 64)');
  ok(run('[...ground.values()].every(c => c.len === shadowLen())') && run('ground.size === blocs'), 'puis les autres, un par image (' + run('blocs') + ' blocs à l\\'écran)');
  run('sun = 0; resetGround(); blitCols = cols0;');
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
  ok(run('["lampadaire", "banc", "foin", "fence_wood_h", "truck", "fountain"].every(n => MAP.sols[n] && MAP.sols[n].length)')
     && run('["bridge", "sandbox", "boat", "peniche", "panier", "rail", "goal_net"].every(n => !MAP.sols[n])') && run('Object.keys(ATLAS).every(k => !k.startsWith("ombre/"))'),
     'bancs, lampadaires, foin, clôtures, camion, fontaine : une ombre portée aussi ; rien pour ce qui est à plat ou sur l\\'eau');
  // --- les bâtiments (batiments.py) : de trois quarts, avec leur ombre, leurs fenêtres du soir, leurs perchoirs
  const bat = run('decor.filter(d => d.night)');
  ok(bat.length >= 12 && bat.every(d => run('!!ATLAS["' + d.key + '"] && MAP.sols["' + d.look + '"].length > 2 && !!ATLAS["' + d.night + '"]')),
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
  ok(run('traits') === 2, 'Tecky loin de la boulangerie : dessiné une fois (plus la passe des ombres portées)');
  run('traits = 0; nuit = []; P.x = B.x; P.y = B.y + 20; drawWorld();');
  ok(run('nuit.some(n => n[0] === "nuit/boulangerie")') && run('traits') >= 3 && run('ctx === mainCtx'),
     'Tecky devant la boulangerie : redessiné en gomme sur les fenêtres des bâtiments derrière lui (il reste devant elles)');
  run('P.draw = drawP;');
  run('drawSpr = drawSpr2; sun = 0;');
  // --- ombres portées des personnages, des bêtes et des véhicules : leur silhouette couchée, sous tous les sprites
  run('var portees = [], ordre = [], cast0 = castShadow, spr0 = drawSpr; castShadow = function (g, s, f, x, y, o) { portees.push([Object.keys(ATLAS).find(k => ATLAS[k] === s), o.alpha, o.lift || 0, g === mainCtx]); ordre.push("ombre"); return cast0.apply(this, arguments); };'
    + ' drawSpr = function (k) { if (!shadowCtx && k.startsWith("tecky/")) ordre.push("tecky"); return spr0.apply(this, arguments); };');
  run('sun = 0; P.x = 20 * 64; P.y = 27 * 64; P.alpha = 1; P.hop = 0; P.inv = 0; camX = P.x - 480; camY = P.y - 270; cars = [newVehicle(["car_red", 0, P.x + 200])]; drawWorld();');
  ok(run('portees.some(p => p[0].startsWith("tecky/") && p[3])') && run('portees.some(p => p[0] === "vehicle/car_red")')
     && run('ordre.indexOf("tecky") > ordre.lastIndexOf("ombre")') && run('ctx === mainCtx'),
     'Tecky et une voiture ont leur ombre portée, dessinée avant les sprites (' + run('portees.length') + ' ombres à l\\'écran)');
  ok(run('portees.every(p => MAP.cast.includes(p[0].split("/")[0]))') && run('!MAP.cast.includes("decor") && !MAP.cast.includes("duck") && !MAP.cast.includes("fx")'),
     'seulement les personnages, les bêtes, les véhicules et les objets posés au sol (pas les décors, les canards ni les effets)');
  // un gros ballon de Léon a son ovale dessous, pas d'ombre couchée en plus (un jouet d'Iris, de la même famille, si)
  run('portees = []; balls[0].x = P.x + 80; balls[0].y = P.y + 40; balls[0].rot = 0; balls[0].z = 0; toys[0].x = P.x - 80; toys[0].y = P.y + 40; toys[0].carried = false; drawWorld();');
  ok(run('!portees.some(p => p[0] === "port/balloon")') && run('portees.some(p => p[0] === "port/toy")'),
     'un ballon de Léon, même sans avoir roulé, n\\'a que l\\'ombre qui est dessous ; un jouet d\\'Iris a son ombre portée');
  // bords naturels froissés : variantes tirées de la position, mêmes coins (tileLook) ; la voirie reste droite
  run('var vus = new Set(), memes = true, eau = MAP.shore; for (let tx = 0; tx < 40; tx++) { const v = tileLook(eau + 12, tx, 41); vus.add(v >> 4); memes = memes && (v & 15) === 12 && v === tileLook(eau + 12, tx, 41); }');
  ok(run('vus.size') === 3 && run('memes') && run('tileLook(MAP.shore + 15, 3, 3) === MAP.shore + 15') && run('tileLook(1, 3, 3) === 1')
     && run('Object.keys(MAP.tileAlt).length') === 5 && run('!MAP.tileAlt[tileLookRoute >> 4]'.replace('tileLookRoute', '(2 * 16 + 3)')),
     'rives et chemins : trois froissements du même bord, tirés de la position ; ni l\\'eau pleine, ni l\\'herbe, ni la route n\\'en ont');
  // ce qui vole : une ombre de la teinte des ombres portées, du côté opposé au soleil
  run('var ell = [], e0 = ctx.ellipse; ctx.ellipse = function (x, y) { ell.push([x, y]); }; flyShadow(100, 200, 80, 9, 3, 1); flyShadow(100, 200, 0, 9, 3, 1); ctx.ellipse = e0;');
  ok(run('ell[0][0] > 100 + 30 && ell[0][1] > 200 + 15 && ell[1][0] === 100 && ell[1][1] === 200'),
     'un papillon haut de 80 px a son ombre à droite et plus bas, comme les ombres portées ; posé, elle est sous lui');
  // objets à ramasser, lettres, jouets : posés au sol, réduits (POSED.sc), avec leur ombre portée (drawPosed)
  run('var poses = [], drawSpr2 = drawSpr; drawSpr = function (k, i, x, y, o) { poses.push([k, x, y, o || {}]); };'
    + ' drawPosed("item/bone", 0, 500, 700, MAP.itemBase.bone, 0.1, 0); drawPosed("item/medal", 0, 500, 700, MAP.itemBase.medal, 5, 30); drawSpr = drawSpr2;');
  ok(run('MAP.cast.includes("item") && MAP.cast.includes("port")') && run('Object.keys(MAP.itemBase).length') === 10 && run('MAP.toyBase.length') === 3
     && run('Object.values(MAP.itemBase).concat(MAP.toyBase).every(b => b > 4 && b < 32)'),
     'objets, lettre et jouets : chacun sait où est le bas de son dessin (' + run('JSON.stringify(MAP.itemBase)') + ')');
  ok(run('poses[0][0] === "item/bone" && poses[0][3].sc === POSED.sc && Math.abs(poses[0][2] + poses[0][3].lift - 700) < 0.01')
     && run('poses[1][0] === "fx/glint"') && run('poses[2][0] === "item/medal" && Math.abs(poses[2][2] + poses[2][3].lift - 700) < 0.01 && poses[2][3].lift > 30'),
     'un objet est posé au sol (son ombre part de là, même pendant un bond) et scintille de temps en temps');
  ok(run('ATLAS["item/bone"].f.length') === 1 && run('ATLAS["item/squeaky"].f.length') === 6 && run('ATLAS["item/letter"].f.length') === 4,
     'plus de rebond dans le dessin : une image par objet, sauf le canard pouic-pouic (6) et la lettre qui frémit (4)');
  run('portees = []; P.hop = 20; drawWorld(); P.hop = 0;');
  ok(run('portees.find(p => p[0].startsWith("tecky/"))[2]') === 20, 'un saut : l\\'ombre reste au sol (la hauteur du saut lui est passée)');
  run('portees = []; P.alpha = 0; drawWorld(); P.alpha = 1;');
  ok(run('portees.find(p => p[0].startsWith("tecky/"))[1]') === 0, 'Tecky sous un grillage (invisible) : son ombre aussi');
  // les ombres fusionnent : celle de Tecky est gommée là où le sol porte déjà celle d'un arbre, puis posée d'un bloc
  run('var vus = [], di0 = mainCtx.drawImage; mainCtx.drawImage = function (img) { vus.push(img === shadowLayer ? "couche" : [...ground.values()].some(k => k.m === img) ? mainCtx.globalCompositeOperation : ""); };');
  run('portees = []; P.x = 13.5 * 64; P.y = 5 * 64; camX = P.x - 480; camY = P.y - 270; drawWorld(); mainCtx.drawImage = di0;');
  ok(run('[...ground.values()].some(k => k.m && k.m.width === Math.ceil(k.c.width * SHADOW.mask))') && run('SHADOW.mask') === 0.5,
     'chaque bloc de sol garde le masque de ses ombres, à demi-taille');
  ok(run('vus.includes("destination-out")') && run('vus.indexOf("destination-out") < vus.indexOf("couche")')
     && run('vus.filter(v => v === "couche").length') === run('shadowRects.length') && run('shadowRects.length') === run('portees.length'),
     'ombres fusionnées : la silhouette de Tecky est gommée par le masque du sol avant d\\'être posée (' + run('shadowRects.length') + ' emprise(s))');
  run('castShadow = cast0; drawSpr = spr0; cars = [];');
}, 50);`);
