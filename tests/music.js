// musique : la variation du thème suit la zone, sans réagir aux passages éclair, en fondu enchaîné calé sur les phrases,
// le tempo glissant de l'une à l'autre
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999; P.mode = "free";'); step(5);
  const BAR = run('Music.song.bar'), PH = run('MUSIC_ZONE.phrase') * BAR, FD = run('MUSIC_ZONE.fade') * BAR;
  const settle = run('MUSIC_ZONE.settle');
  ok(BAR === 16 && run('Music.zone') === 'niche' && run('Music.layers.length') === 1, 'à la niche : son de base, une seule couche');
  ok(run('JSON.stringify(Object.keys(SONGS))') === '["base","village","ferme","foret","parc","industrie","berceuse"]',
     'une variation du thème par zone (niche et campagne : la base), et la berceuse de la fin');
  ok(run('Object.values(SONGS).every(S => S.total === SONGS.base.total && S.bar === SONGS.base.bar)'), 'même longueur, même grille de phrases');
  ok(run('SONGS.foret.bpm') < run('SONGS.base.bpm') && run('SONGS.village.bpm') > run('SONGS.base.bpm'), 'forêt plus lente, village plus entraînant');
  ok(run('SONGS.ferme.ev.some(e => e[1] === "lead" && e[5] < 0)') && !run('SONGS.parc.ev.some(e => e[1] === "drums")'), 'ferme : notes glissées ; parc : pas de batterie');
  ok(run('Music.bpm') === run('SONGS.base.bpm') && run('Music.layers[0].song') === run('Music.themes.base'), 'thème de base, à son tempo');
  // passage éclair au village : rien ne change
  run('P.x = 30 * 64; P.y = 5 * 64;'); step(Math.round(60 * settle * 0.7));
  run('P.x = MAP.start[0]; P.y = MAP.start[1] + 60;'); step(60 * 4);
  ok(run('Music.zone') === 'niche' && !run('Music.want') && run('Music.layers.length') === 1, 'un passage éclair au village : la musique ne change pas');
  // Tecky reste au village : changement demandé, puis fait au début d'une phrase
  run('P.x = 30 * 64; P.y = 5 * 64;');
  let t = 0; while (!run('Music.want') && t < 600) { step(1); t++; }
  ok(run('Music.want') === 'village' && Math.abs(t / 60 - settle) < 0.2, 'au bout de ' + (t / 60).toFixed(1) + ' s au village : changement demandé');
  ok(run('Music.zone') === 'niche' && run('Music.layers.length') === 1, 'il attend la fin de la phrase');
  t = 0; while (run('Music.layers.length') < 2 && t < 60 * 10) { step(1); t++; }
  ok(run('Music.zone') === 'village' && run('Music.fadeStep') % PH === PH - FD, 'fondu enchaîné pendant la dernière mesure d’une phrase (pas ' + run('Music.fadeStep') + ')');
  ok(t / 60 <= run('MUSIC_ZONE.phrase') * BAR * 15 / run('Music.song.bpm') + 0.2, 'au plus une phrase d’attente (' + (t / 60).toFixed(1) + ' s)');
  // pendant le fondu : la mélodie joue dans les deux timbres, les couches se croisent
  run('var vs = [], sps = [], v0 = Music.voice; Music.voice = function (e, tt, spb, tb) { if (e[1] === "lead") vs.push(tb); sps.push(spb); return v0.apply(this, arguments); };');
  ok(run('Music.layers.find(l => l.id === "niche").v1') === 0 && run('Music.layers.find(l => l.id === "village").v1') === 1, 'l’ancienne couche descend, la nouvelle monte');
  t = 0; while (run('Music.layers.length') > 1 && t < 60 * 4) { step(1); t++; }
  ok(run('new Set(vs).size') === 2, 'pendant le fondu : la mélodie dans les deux variations');
  ok(run('sps[0] > sps[sps.length - 1] && sps.every((v, i) => i === 0 || v <= sps[i - 1] + 1e-9)'), 'le tempo glisse : chaque pas un peu plus court');
  ok(Math.abs(t / 60 - run('Music.fadeDur')) < 0.3 && run('Music.fadeDur') < FD * 15 / 140, 'fondu d’une mesure, un peu plus courte : le tempo accélère (' + (t / 60).toFixed(2) + ' s)');
  ok(run('Music.bpm') === run('SONGS.village.bpm') && !run('Music.glide'), 'au village : ' + run('Music.bpm') + ' à la noire');
  ok(run('Music.layers.length') === 1 && run('Music.layers[0].id') === 'village' && run('Music.step') % PH < 4, 'la phrase suivante commence avec les nouveaux instruments');
  run('Music.voice = v0;');
  // une demande en attente s'annule si Tecky revient avant le début de la phrase
  run('P.x = 30 * 64; P.y = 20 * 64;');
  t = 0; while (!run('Music.want') && t < 600) { step(1); t++; }
  run('Music.step = 0;');                // la prochaine phrase est loin
  ok(run('Music.want') === 'industrie', 'zone industrielle : changement demandé');
  run('P.x = 30 * 64; P.y = 5 * 64;'); step(Math.round(60 * (settle + 0.3)));
  ok(!run('Music.want') && run('Music.zone') === 'village' && run('Music.layers.length') === 1, 'Tecky revient au village avant : rien ne change');
  // Continuer : la musique prend tout de suite le timbre de l'endroit
  run('P.x = 60 * 64; P.y = 40 * 64; saveGame(); toTitle(); loadGame(loadSave(), false);'); advanceDialog(); step(3);
  ok(run('Music.zone') === 'foret' && !run('Music.want'), 'Continuer en forêt : sa variation tout de suite');
  step(60);
  ok(run('Music.layers.length') === 1 && run('Music.layers[0].id') === 'foret', 'après un fondu rapide');
  // de la forêt au parc : le tempo remonte
  run('P.x = 22 * 64; P.y = 37 * 64;');
  t = 0; while (run('Music.bpm') !== run('SONGS.parc.bpm') && t < 60 * 14) { step(1); t++; }
  ok(run('Music.bpm') === run('SONGS.parc.bpm'), 'de la forêt au parc : ' + run('SONGS.foret.bpm') + ' puis ' + run('SONGS.parc.bpm') + ' à la noire');
  // la fanfare : son de base, pas de couches
  run('Music.stop(); Music.start("win"); var vw = []; Music.voice = function (e, tt, spb, tb) { if (e[1] === "lead") vw.push(tb); return v0.apply(this, arguments); };'); step(60);
  ok(run('vw.length') > 0 && run('vw.every(tb => tb === TIMBRE.niche)') && run('Music.layers.length') === 0, 'fanfare : son de base');
  run('Music.voice = v0; Music.stop(); Music.start("main");');
  ok(run('Music.layers.length') === 1 && run('Music.layers[0].id') === 'parc' && run('Music.bpm') === run('SONGS.parc.bpm'), 'le thème repart avec la variation de la zone, à son tempo');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
