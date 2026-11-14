// la côte a ses musiques et son ambiance : un morceau à elle par zone, les mouettes, les drisses du port, les rafales
// de la falaise, le ressac de la mer (et plus de grenouilles ni de clapotis de mare au bord de la mer)
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('EPISODES[1].chantier = false; audioOn(); episode = "ete"; newGame("balade", true);'); advanceDialog();
  run('cars = []; dogs = []; P.inv = 99;');
  const jusqua = (cond, max) => { let t = 0; while (!run(cond) && t < max) { step(1); t++; } return t; };
  const va = (x, y) => run(`P.x = ${x} * 64; P.y = ${y} * 64; P.mode = "free";`);
  // les morceaux
  const zs = JSON.parse(run('JSON.stringify(MAP.zones.map(z => [z.id, z.music || z.id]))'));
  ok(run('MAP.id') === 'cote' && zs.map(z => z.join(':')).join() === 'manege:manege,port:port,pecheurs:port,ville:ville,falaises:falaises,plage:plage,bocage:ferme,cote:cote',
     'les zones de la côte et leurs morceaux : ' + zs.map(z => z[0] + ' → ' + z[1]).join(', '));
  ok(['cote', 'port', 'ville', 'falaises', 'plage'].every(k => run(`!!SONGS.${k} && SONGS.${k}.loop !== null && SONGS.${k}.ev.some(e => e[1] === "harm")`))
     && run('SONGS.port.bar') === 12 && run('SONGS.ville.bar') === 12 && run('SONGS.falaises.echo && SONGS.falaises.inst.lead.echo') === 1
     && run('SONGS.plage.key') === 0 && run('SONGS.falaises.bpm') < run('SONGS.cote.bpm'),
     'cinq morceaux pour la côte : chant de marins et valse en ternaire, de l\'écho sur les falaises, la plage en do');
  jusqua('Music.track.id === "cote"', 60 * 4);
  ok(run('Music.track.id') === 'cote', 'au parking : l\'air de la Côte Fleurie');
  va(30, 52); jusqua('Music.track.id === "plage"', 60 * 8);
  ok(run('zone.id') === 'plage' && run('Music.track.id') === 'plage', 'sur la plage : le calypso');
  // le ressac : au bord de la mer, pas dans les terres ; il respire
  step(30);
  const sel = run('Ambience.salt'), eau = run('Ambience.wet');
  let lo = 1, hi = 0;
  for (let i = 0; i < 60 * 9; i++) { step(1); const v = run('Ambience.surfLevel'); lo = Math.min(lo, v); hi = Math.max(hi, v); }
  ok(sel > 0.2 && eau === 0 && run('!!Ambience.loops.surf') && run('!Ambience.loops.water') && hi > lo * 2 && hi <= run('AMB.surf') && lo > 0,
     'près de la mer : le ressac (part de mer ' + sel.toFixed(2) + '), qui enfle et retombe (' + lo.toFixed(4) + ' à ' + hi.toFixed(4) + '), sans clapotis de mare');
  ok(run('[0, 1.3, 4.4, 7, 30].every(t => surfSwell(t) > 0 && surfSwell(t) <= 1)'), 'la respiration du ressac reste entre 0 et 1');
  run('sun = 3; var joues = []; for (const n of ["frog", "gull"]) { const f = SOUNDS[n]; SOUNDS[n] = k => { joues.push(n); return f(k); }; }');
  ok(run('ambSound("frog")') === false && run('ambSound("gull")') === true && run('joues.join()') === 'gull', 'pas de grenouille au bord de la mer ; une mouette, si');
  run('sun = 0;');
  // les sons de chaque zone
  const sons = id => JSON.parse(run(`JSON.stringify((AMB_EVENTS[${JSON.stringify(id)}] || []).map(e => e[0]))`));
  ok(sons('plage').includes('gull') && sons('port').includes('rigging') && sons('port').includes('horn') && sons('falaises').includes('gust')
     && sons('pecheurs').includes('gull') && !sons('bocage').includes('cluck') && !sons('bocage').includes('rooster'),
     'mouettes sur la plage, drisses et corne au port, rafales sur la falaise ; ni poules ni coq dans la campagne normande');
  run('Ambience.played = 0; Ambience.timers = {};'); step(60 * 12);
  ok(run('Ambience.played') >= 1, 'des mouettes crient sur la plage (' + run('Ambience.played') + ' en 12 s)');
  va(60, 4); step(60);
  ok(run('zone.id') === 'bocage' && run('Ambience.surfLevel') === 0 && run('Ambience.salt') === 0, 'dans la campagne normande : plus de ressac');
  // le monde du printemps n'a pas de mer : rien ne change
  run('episode = "printemps"; newGame("balade", true);'); advanceDialog();
  run('P.x = 80 * 64; P.y = 43.5 * 64;'); step(30);
  ok(run('MAP.id') === 'monde' && run('Ambience.salt') === 0 && run('Ambience.wet') > 0.2 && run('Ambience.level') > 0, 'dans le monde, sur le pont : le clapotis, pas de ressac');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
