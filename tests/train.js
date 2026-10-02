// Titine, le petit train du port : aller-retour sur la voie du quai, arrêt devant Tecky, sifflet quand il aboie
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; critters = []; P.inv = 999; P.x = 10 * 64; P.y = 5 * 64;');
  ok(run('!!train') && run('zoneAt(train.x, trainY()).id') === 'industrie', 'Titine roule au port');
  const x0 = run('train.x'); step(60 * 2);
  ok(run('train.x') > x0 + 60 && run('train.dir') === 1, 'elle avance (' + Math.round(run('train.x') - x0) + ' px en 2 s)');
  // au bout de la voie : une pause, puis elle repart dans l'autre sens, sans jamais passer les heurtoirs
  let lo = 1e9, hi = -1e9, waited = false, back = false;
  for (let i = 0; i < 60 * 40; i++) {
    step(1); lo = Math.min(lo, run('trainWest()')); hi = Math.max(hi, run('trainEast()'));
    if (run('train.mode') === 'wait') waited = true;
    if (waited && run('train.dir') === -1 && run('train.v') > 0) { back = true; break; }
  }
  ok(waited && back, 'au bout de la voie, une pause, puis elle repart en arrière');
  ok(hi <= run('MAP.track[1]') - 16 && lo >= run('MAP.track[0]') + 16, 'jamais dans les heurtoirs');
  // Tecky sur la voie, devant elle : elle s'arrête avant lui, sonne, et repart quand il s'en va
  run('train.x = (trainMin() + trainMax()) / 2; train.dir = 1; train.v = TRAIN.spd; train.mode = "run";' +
      'P.x = trainEast() + 150; P.y = trainY(); P.mode = "free"; pops = [];');
  let overlap = false, rang = false;
  for (let i = 0; i < 60 * 6; i++) {
    step(1); if (run('trainHit(P.x - 16, P.y - 12, P.x + 16, P.y)')) overlap = true;
    if (run('pops.some(p => p.text === "Tut-tut !")')) rang = true;
  }
  ok(run('train.v') === 0 && run('trainEast()') < run('P.x') - 16 && !overlap, 'elle s’arrête devant Tecky, sans le toucher');
  ok(rang, '« Tut-tut ! »');
  run('P.x = 10 * 64; P.y = 5 * 64;'); step(60 * 2);
  ok(run('train.v') > 0, 'la voie libre, elle repart');
  // c'est un obstacle : Tecky ne passe pas à travers
  run('train.v = 0; train.mode = "wait"; train.waitT = 99; P.x = train.x; P.y = trainY() + 120; P.dir = "up"; P.mode = "free";');
  step(60, 'held.up = true'); run('held.up = false');
  ok(!run('trainHit(P.x - 16, P.y - 12, P.x + 16, P.y)') && run('P.y') > run('trainY()'), 'on ne traverse pas le train');
  // un ballon de Léon sur les rails : écarté doucement
  run('train.mode = "run"; train.dir = 1; train.v = TRAIN.spd; var B = balls[0]; B.inNet = false; B.x = trainEast() + 40; B.y = trainY(); B.vx = B.vy = 0; P.x = 10 * 64; P.y = 5 * 64;');
  step(60 * 2);
  ok(run('B.y') < run('trainY() - TRAIN.top') || run('B.x') > run('trainEast()') + 20, 'un ballon sur les rails est écarté');
  // un aboiement vers elle : « Tchou-tchou ! », vapeur, des points la première fois seulement
  run('balls.forEach(b => { b.x = 10 * 64; b.y = 20 * 64; }); P.x = train.x; P.y = trainY() + 200; P.dir = "up"; P.mode = "free"; P.cdBark = 0; pops = []; fxs = []; var sc0 = score;');
  run('pressed.bark = true'); step(1);
  ok(run('pops.some(p => p.text === "Tchou-tchou !")') && run('fxs.some(f => f.key === "fx/steam")'), 'elle siffle, dans un nuage de vapeur');
  ok(run('train.scored') && run('score') === run('sc0 + TRAIN.score'), '+' + run('TRAIN.score') + ' points la première fois');
  step(120); run('P.cdBark = 0; pressed.bark = true; var sc1 = score;'); step(1);
  ok(run('score') === run('sc1'), 'ensuite, plus de points');
  step(40);
  ok(run('!!badges.train'), 'badge « Tchou-tchou ! »');
  run('saveGame();');
  ok(run('STORE.get(SAVE_KEY).train') === 1, 'sauvegardé');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
