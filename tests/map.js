// carte agrandie : sol en blocs, rivière infranchissable sauf par le pont, garde-corps
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
eval(base + `setTimeout(() => {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; P.inv = 99;');
  ok(run('MAP.w') === 80 && run('MAP.h') === 48, 'carte de 80 x 48 tuiles');
  ok(run('groundChunks.length') === 15 && run('groundChunks.every(k => k.w <= 1024 + 2 * CM && k.h <= 1024 + 2 * CM)'),
     'sol pré-rendu en 15 blocs de 1024 px au plus');
  const walkDown = (x, n) => { run('P.x = ' + x + '; P.y = 24.4*64; P.mode = "free";'); step(n, 'held.down = true'); run('held.down = false'); return run('P.y') / 64; };
  ok(walkDown('64*64', 200) > 31, 'on traverse la rivière par le pont');
  ok(walkDown('60*64', 200) < 26.2, 'ailleurs, la rivière bloque');
  ok(walkDown('7*64', 200) < 26.2, 'au bout du chemin de la barque aussi');
  run('P.x = 64*64; P.y = 27.5*64; P.mode = "free";'); step(120, 'held.right = true'); run('held.right = false');
  ok(run('P.x') / 64 < 65.1, 'le garde-corps retient Tecky sur le pont (x = ' + (run('P.x') / 64).toFixed(2) + ')');
  ok(run('MAP.decor.some(d => d[0] === "bridge")') && run('FLAT.has("bridge")'), 'le pont est dessiné à plat, sous les personnages');
  // eau animée : des vaguelettes sur la rivière, jamais hors de l'eau, aucune au-dessus des champs
  run('var rip = [], gl = []; var drawSpr0 = drawSpr; drawSpr = function (k, f, x, y) { if (k === "fx/ripple") rip.push([x, y, f]); if (k === "fx/glint") gl.push([x, y, f]); return drawSpr0.apply(this, arguments); };');
  let pts = [];
  for (let t = 0; t < 4; t += 0.37) { run('rip = []; drawWater(30 * 64, 23 * 64, ' + t + ');'); pts = pts.concat(run('rip')); }
  ok(pts.length > 100 && pts.every(([x, y]) => run('deepWater(' + x + ', ' + y + ')')), pts.length + ' vaguelettes sur la rivière, toutes en eau profonde (loin des berges)');
  ok(pts.length / 11 < 40, 'peu nombreuses : ' + Math.round(pts.length / 11) + ' par image pour une rivière qui traverse l\\'écran');
  ok(new Set(pts.map(p => p[2])).size >= 6, 'à différentes étapes de leur animation');
  run('gl = []; for (let t = 0; t < 6; t += 0.29) drawWater(30 * 64, 23 * 64, t);');
  const gls = run('gl');
  ok(gls.length > 10 && gls.every(([x, y]) => run('deepWater(' + x + ', ' + y + ')')), gls.length + ' scintillements en plus des vaguelettes, en eau profonde');
  run('rip = []; drawWater(64 * 64, 2 * 64, 1.2); drawSpr = drawSpr0;');
  // fontaine animée : 8 images, le dessin change d'image avec le temps
  ok(run('ATLAS["decor/fountain"].f.length') === 8 && run('MAP.decorFps.fountain') === 10, 'la fontaine a 8 images à 10 par seconde');
  ok(run('rip.length') === 0, 'aucune vaguelette loin de l\\'eau');
}, 50);`);
