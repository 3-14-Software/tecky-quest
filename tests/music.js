// musique : un morceau par zone ; en changeant de zone, le morceau en cours s'éteint (fondu vers le silence), puis
// celui de la nouvelle zone commence après un court silence ; un passage éclair ne change rien
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999; P.mode = "free";'); step(5);
  const Z = JSON.parse(run('JSON.stringify(MUSIC_ZONE)')), settle = Z.settle;
  const ici = (x, y) => run(`P.x = ${x} * 64; P.y = ${y} * 64;`);
  const jusqua = (cond, max) => { let t = 0; while (!run(cond) && t < max) { step(1); t++; } return t; };
  ok(run('Music.zone') === 'niche' && run('Music.track.id') === 'niche' && !run('Music.swap'), 'à la niche : le thème');
  ok(run('JSON.stringify(Object.keys(SONGS))') === '["niche","village","campagne","ferme","foret","parc","industrie","berceuse","win","lose"]',
     'un morceau par zone, la berceuse de la fin, la fanfare et la défaite');
  ok(run('MAP.zones.every(z => SONGS[z.music || z.id])'), 'chaque zone de la carte a son morceau');
  ok(run('Object.values(SONGS).every(S => S.ev.every(e => e[0] < S.total && (e[1] === "drums" ? DRUMS[e[2]] : S.inst[e[1]])))'),
     'chaque note a son instrument');
  ok(run('Object.values(SONGS).every(S => S.total % S.bar === 0 && (S.loop === null || (S.loop < S.total && S.entries.length && ' +
         'S.entries.every(e => e >= S.loop && e < S.total && e % S.bar === 0))))'), 'reprises : au début d’une partie, après les mesures d’entrée');
  ok(run('SONGS.win.loop') === null && run('SONGS.lose.loop') === null && run('SONGS.niche.loop') > 0, 'fanfare et défaite : une seule fois ; le thème a deux mesures d’entrée');
  ok(run('SONGS.foret.bpm') < run('SONGS.niche.bpm') && run('SONGS.village.bpm') > run('SONGS.niche.bpm'), 'forêt plus lente, village plus entraînant');
  ok(run('SONGS.ferme.ev.some(e => e[1] === "lead" && e[5] < 0)') && !run('SONGS.parc.ev.some(e => e[1] === "drums")'), 'ferme : notes glissées ; parc : pas de batterie');
  ok(run('SONGS.parc.bar') === 12 && run('SONGS.campagne.bar') === 12 && run('SONGS.niche.bar') === 16, 'parc : une valse ; campagne : ternaire');
  ok(run('["niche", "village", "campagne", "ferme", "industrie"].every(k => SONGS[k].ev.some(e => e[1] === "harm"))'), 'une deuxième voix');
  ok(run('SONGS.foret.echo && SONGS.foret.inst.lead.echo') === 1 && !run('SONGS.village.echo'), 'forêt : de l’écho');
  // passage éclair au village : rien ne change
  ici(46, 5); step(Math.round(60 * settle * 0.7));
  run('P.x = MAP.start[0]; P.y = MAP.start[1] + 60;'); step(60 * 4);
  ok(run('Music.zone') === 'niche' && !run('Music.want') && !run('Music.swap'), 'un passage éclair au village : la musique ne change pas');
  // Tecky reste au village : le thème s'éteint, puis le morceau du village commence
  ici(46, 5);
  let t = jusqua('Music.want', 600);
  ok(run('Music.want') === 'village' && Math.abs(t / 60 - settle) < 0.2, 'au bout de ' + (t / 60).toFixed(1) + ' s au village : changement demandé');
  ok(run('Music.zone') === 'niche' && run('Music.track.id') === 'niche' && run('Music.track.v1') === 0, 'le thème s’éteint (fondu vers le silence)');
  const st0 = run('Music.step');
  step(30);
  ok(run('Music.track.id') === 'niche' && run('Music.step') > st0, 'pendant le fondu, il joue encore');
  t = 30 + jusqua('Music.zone === "village"', 600);
  ok(Math.abs(t / 60 - Z.out) < 0.25, 'fondu de ' + (t / 60).toFixed(2) + ' s');
  ok(run('Music.track.id') === 'village' && run('Music.step') === 0 && run('Music.track.v1') === 1 && !run('Music.want') && !run('Music.swap'),
     'puis le morceau du village, depuis son début, à plein volume');
  const silence = run('Music.next') - now;
  ok(silence > Z.gap - 0.05 && silence < Z.gap + 0.2, 'après un silence (' + silence.toFixed(2) + ' s)');
  ok(run('Music.pos.niche') > st0, 'le thème retient où il a été quitté');
  run('var vs = [], v0 = Music.voice; Music.voice = function (e, tt, spb, I) { if (e[1] === "lead") vs.push([I, spb]); return v0.apply(this, arguments); };');
  step(120);
  ok(run('vs.length') > 3 && run('vs.every(v => v[0] === SONGS.village.inst.lead && v[1] === SONGS.village.spb)'), 'avec ses instruments, à son tempo');
  run('Music.voice = v0;');
  // Tecky repart avant la fin du fondu : le morceau remonte tout de suite
  ici(46, 26);
  jusqua('Music.want', 600);
  ok(run('Music.want') === 'industrie' && run('Music.track.v1') === 0, 'zone industrielle : le morceau du village s’éteint');
  step(20); ici(46, 5); step(2);
  ok(!run('Music.want') && !run('Music.swap') && run('Music.track.v1') === 1 && run('Music.zone') === 'village', 'Tecky revient pendant le fondu : il remonte');
  step(60 * 3);
  ok(run('Music.track.id') === 'village' && run('Music.zone') === 'village', 'et continue');
  // Continuer : fondu rapide, puis le morceau de l'endroit
  ici(76, 56); run('saveGame(); toTitle(); loadGame(loadSave(), false);'); advanceDialog(); step(3);
  ok(run('Music.want') === 'foret', 'Continuer en forêt : son morceau demandé tout de suite');
  t = jusqua('Music.zone === "foret"', 120);
  ok(t / 60 < Z.cut + 0.2 && run('Music.track.id') === 'foret' && run('Music.step') === 0, 'après un fondu rapide (' + (t / 60).toFixed(2) + ' s), depuis son début');
  // le verger (au sud de la route) : le morceau de la ferme, avec son bandeau à lui
  ici(70, 33); run('saveGame(); toTitle(); loadGame(loadSave(), false);'); advanceDialog(); step(60);
  ok(run('zoneAt(P.x, P.y).id') === 'verger' && run('Music.zone') === 'ferme' && run('Music.track.id') === 'ferme', 'Continuer au verger : le morceau de la ferme');
  // de la ferme au parc, puis retour : le morceau reprend au début de la partie la plus proche
  step(60 * 9);
  const quitte = run('Music.step');
  ici(30, 53);
  jusqua('Music.zone === "parc"', 60 * 6);
  ok(run('Music.track.id') === 'parc' && run('Music.song.spb') === run('SONGS.parc.spb') && run('Music.pos.ferme') >= quitte, 'au parc : sa valse, à son tempo');
  step(60); ici(70, 33);
  jusqua('Music.zone === "ferme"', 60 * 6);
  const repris = run('Music.step');
  ok(repris > 0 && run('SONGS.ferme.entries').includes(repris) && Math.abs(repris - run('Music.pos.ferme')) <= 4 * 16,
     'retour au verger : la ferme reprend au début de la partie la plus proche (pas ' + repris + ', quittée au pas ' + run('Music.pos.ferme') + ')');
  run('Music.pos.ferme = 20; Music.open("ferme", 0);');
  ok(run('Music.step') === 0, 'une partie à peine entamée est rejouée');
  run('Music.pos.ferme = SONGS.ferme.total - 20; Music.open("ferme", 0);');
  ok(run('Music.step') === run('SONGS.ferme.entries[0]'), 'quittée à la fin : elle reprend au début de la boucle');
  // la fanfare : son morceau, joué une fois
  step(60);
  run('Music.stop(); Music.start("win");'); step(60);
  ok(run('Music.track.id') === 'win' && run('Music.song.loop') === null && run('Music.cur') === 'win', 'fanfare');
  run('Music.stop(); Music.start("main");');
  ok(run('Music.cur') === 'main' && run('Music.track.id') === 'ferme', 'puis le morceau de la zone repart');
  // menu principal : l'écran titre reprend son thème, depuis le début
  run('toTitle();'); step(90);
  ok(run('state') === 'title' && run('Music.zone') === run('TITLE_MUSIC') && run('Music.track.id') === run('TITLE_MUSIC') &&
     run('Music.step') < run('SONGS.niche.loop'), 'retour au menu : le thème de l’écran titre, depuis ses mesures d’entrée');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
