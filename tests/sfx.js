// bruitages : chaque son appelé par le jeu existe et se joue ; un son placé dans le monde sort de son côté et se tait
// au loin ; les petits airs suivent le ton du morceau ; chaque personnage a son babil ; le soir, grillons et chouette
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999; P.mode = "free";'); step(5);
  const src = require('fs').readFileSync(__dirname + '/game_full.js', 'utf8');
  const noms = JSON.parse(run('JSON.stringify(Object.keys(SOUNDS))'));
  const appels = [...new Set([...src.matchAll(/\bSFX\.([A-Za-z]\w*)/g)].map(m => m[1]))];
  const inconnus = appels.filter(n => !noms.includes(n));
  ok(appels.length > 40 && !inconnus.length, appels.length + ' bruitages appelés par le jeu, tous dans SOUNDS' + (inconnus.length ? ' (inconnus : ' + inconnus + ')' : ''));
  const muets = noms.filter(n => !appels.includes(n) && !run('Object.values(AMB_EVENTS).flat().concat(AMB_NIGHT).some(e => e[0] === "' + n + '")') &&
    !['tweet', 'trill', 'titu'].includes(n));
  ok(!muets.length, 'aucune recette oubliée' + (muets.length ? ' (jamais jouées : ' + muets + ')' : ''));
  ok(run('Object.values(AMB_EVENTS).flat().concat(AMB_NIGHT).every(e => e[0] === "bird" || e[0] === "cluck" || SOUNDS[e[0]])'), 'chaque son d’ambiance a sa recette');
  ok(run('Object.keys(TUNED).every(n => SOUNDS[n])') && run('Object.keys(VOICE).every(w => WHO[w])'), 'airs accordés et voix : des noms connus');
  // chacun se joue
  const faibles = noms.filter(n => { const n0 = nodes; run('SFX.' + n + '(1)'); return nodes - n0 < 4; });
  ok(!faibles.length, 'les ' + noms.length + ' bruitages se jouent' + (faibles.length ? ' (rien pour : ' + faibles + ')' : ''));
  ok(run('sfxOut') === null && run('sfxTune') === 1, 'après un bruitage : sortie et hauteur remises');
  let n0 = nodes; run('muted = true; SFX.bark(1); SFX.pick(1); muted = false;');
  ok(nodes === n0, 'son coupé : rien');
  // placement : côté de l'écran, silence au loin
  run('var pans = [], sp0 = AC.createStereoPanner; AC.createStereoPanner = () => ({ pan: { set value(v) { pans.push(v); } }, connect() {} });');
  run('SFX.quack(1, { x: camX + 40, y: camY + VH / 2 }); SFX.quack(1, { x: camX + VW - 40, y: camY + VH / 2 }); SFX.quack(1, { x: camX + VW / 2, y: camY + VH / 2 });');
  const pans = JSON.parse(run('JSON.stringify(pans)'));
  ok(pans.length === 3 && pans[0] < -0.5 && pans[1] > 0.5 && pans[2] === 0, 'un canard à gauche sort à gauche, à droite à droite (' + pans.map(v => v.toFixed(2)) + ')');
  n0 = nodes; run('SFX.quack(1, { x: camX + VW / 2 + SOUND.far + 50, y: camY + VH / 2 });');
  ok(nodes === n0 && run('pans.length') === 3, 'trop loin : on ne l’entend pas');
  run('AC.createStereoPanner = sp0;');
  // hauteur : un peu différente à chaque fois, sauf les petits airs, dans le ton du morceau
  run('var tunes = [], played = {}; for (const n in SOUNDS) { const f = SOUNDS[n]; SOUNDS[n] = k => { tunes.push(sfxTune); played[n] = (played[n] || 0) + 1; return f(k); }; }');
  run('tunes = []; for (let i = 0; i < 20; i++) SFX.quack(1);');
  ok(run('new Set(tunes).size') > 10 && run('tunes.every(v => Math.abs(v - 1) <= SOUND.vary + 1e-9)'), 'vingt « coin coin » : vingt hauteurs, à ± ' + run('SOUND.vary * 100') + ' %');
  ok(run('Object.values(SONGS).every(S => S.key >= 0 && S.key < 12)') && run('SONGS.niche.key') === 0 && run('SONGS.village.key') === 7 &&
     run('SONGS.foret.key') === 0 && run('SONGS.industrie.key') === 7, 'chaque morceau donne son ton (la mineur : do ; mi mineur : sol)');
  run('tunes = []; SFX.pick(1);');
  ok(run('Music.track.id') === 'niche' && run('tunes[0]') === 1, 'à la niche (do) : l’air d’un objet ramassé tel qu’il est écrit');
  run('P.x = 46 * 64; P.y = 5 * 64;'); let t = 0; while (run('Music.track.id') !== 'village' && t++ < 600) step(1);
  run('tunes = []; SFX.pick(1); SFX.treasure(1);');
  ok(run('Music.track.id') === 'village' && Math.abs(run('tunes[0]') - Math.pow(2, -5 / 12)) < 1e-9 && run('tunes[1]') === run('tunes[0]'),
     'au village (sol) : le même air une quarte plus bas');
  // babil des dialogues
  const babil = (who, texte) => {
    run('played = {}; say([{ who: "' + who + '", text: "' + texte + '" }]);'); step(40);
    const p = JSON.parse(run('JSON.stringify(played)'));
    advanceDialog();
    return p;
  };
  let p = babil('farmer', 'Bonjour Tecky ! Mes poules se sont sauvées, tu sais.');
  ok(p.talk > 4 && !p.wuf && !p.blip, 'Gaston parle : son babil (' + p.talk + ' syllabes)');
  p = babil('tecky', 'Ouaf ! Je les ramène tout de suite, promis !');
  ok(p.wuf > 4 && !p.talk && !p.blip, 'Tecky parle : de petits « wouf » (' + p.wuf + ')');
  p = babil('info', 'Les poules sont rentrées dans leur enclos.');
  ok(p.blip > 4 && !p.talk && !p.wuf, 'une information : des « tic »');
  p = babil('alice', '. . . . . . . . . . . . . . . . . . . . . .');
  ok(!p.talk, 'rien sur les espaces ni la ponctuation');
  // menus
  run('played = {}; pressed.pause = true;'); step(2);
  ok(run('state') === 'pause' && run('played.pause') === 1, 'pause : son de la pause');
  run('played = {}; pressed.right = true;'); step(1); run('pressed.ok = true;'); step(2);
  ok(run('state') === 'options' && run('played.blip') >= 1 && run('played.ok') === 1, 'menu : « tic » en se déplaçant, validation');
  run('played = {}; closeOptions();'); step(1);
  ok(run('state') === 'pause' && run('played.back') === 1 && !run('played.pause'), 'retour des options : son du retour');
  run('menu.sel = 0; pressed.ok = true;'); step(2);
  ok(run('state') === 'play', 'reprise');
  // fontaine du village
  run('var F = decor.find(d => d.n === "fountain"); P.x = F.x; P.y = F.y + 90;'); step(5);
  const near = run('Ambience.fountLevel');
  run('P.x = F.x + 900;'); step(5);
  ok(near > run('AMB.fountain') * 0.8 && run('Ambience.fountLevel') === 0 && run('!!Ambience.loops.fountain'), 'près de la fontaine : son glouglou (' + near.toFixed(3) + '), plus rien à 900 px');
  // ambiance : oiseaux le jour ; le soir, grillons et chouette
  run('P.x = 76 * 64; P.y = 56 * 64; played = {};'); step(60 * 30);
  const jour = JSON.parse(run('JSON.stringify(played)')), oiseaux = q => (q.tweet || 0) + (q.trill || 0) + (q.titu || 0);
  ok(oiseaux(jour) > 4 && !jour.cricket && !jour.owl, 'forêt, de jour : des oiseaux (' + oiseaux(jour) + ' en 30 s), ni grillon ni chouette');
  run('clues = [true, true, true]; sun = 3; played = {};'); step(60 * 45);
  const soir = JSON.parse(run('JSON.stringify(played)'));
  ok(run('lampsOn()') && !oiseaux(soir) && !soir.cuckoo && soir.cricket > 4 && soir.owl >= 1,
     'le soir : les oiseaux se taisent, grillons (' + soir.cricket + ') et chouette (' + soir.owl + ')');
  ok(!soir.frog, 'pas de grenouille loin de l’eau');
  run('P.x = 80 * 64; P.y = 46.6 * 64; played = {};'); step(60 * 40);
  ok(run('Ambience.wet') >= run('AMB.frog') && run('played.frog') >= 1, 'au bord de la rivière, le soir : des grenouilles (' + run('played.frog') + ')');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
