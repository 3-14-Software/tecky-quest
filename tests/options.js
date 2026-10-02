// écran d'options : volumes, difficulté (facile), taille du texte, image, vibrations ; menu de la pause
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  const ids = () => run('menu.items.map(i => i.id).join()');
  const rowIds = () => run('optRows().map(r => r.id).join()');
  const go = id => run(`optSel = optRows().findIndex(r => r.id === "${id}")`);
  run('audioOn(); STORE.mem = {};');
  ok(run('state') === 'title' && /options/.test(ids()), 'menu principal : entrée « Options »');
  run('menu.sel = menu.items.findIndex(i => i.id === "options"); pressed.ok = true'); step(1);
  ok(run('state') === 'options' && /^music,sfx,diff,text,image,vib,weather,(fs,)?back$/.test(rowIds()), 'écran d’options : ' + rowIds());
  // volumes
  const lv0 = run('Music.level()');
  run('pressed.right = true'); step(1);
  ok(run('opts.music') === 8 && run('Music.level()') > lv0, 'Musique : ' + run('opts.music') + ', thème plus fort');
  ok(run('STORE.get(OPTIONS_KEY).music') === 8, 'réglage gardé dans le navigateur');
  go('sfx'); for (let i = 0; i < 12; i++) { run('pressed.left = true'); step(1); }
  ok(run('opts.sfx') === 0 && run('sfxGain()') === 0, 'Bruitages à 0 : muets');
  run('pressed.ok = true'); step(1);
  ok(run('opts.sfx') === 1, 'Entrée : un cran de plus');
  run('opts.sfx = 8;');
  // au toucher : moitié gauche = moins, moitié droite = plus
  run('var b = optBox(0); optionsTap(b.x + 40, b.y + 20);');
  ok(run('opts.music') === 7 && run('optSel') === 0, 'toucher à gauche d’une ligne : moins');
  run('optionsTap(b.x + b.w - 40, b.y + 20);');
  ok(run('opts.music') === 8, 'à droite : plus');
  // difficulté, texte, image
  go('diff'); run('pressed.right = true'); step(1);
  ok(run('opts.diff') === 'facile' && /5 os/.test(run('optRows()[optSel].note')), 'Difficulté : facile (' + run('optRows()[optSel].note') + ')');
  go('text'); run('pressed.right = true'); step(1);
  ok(run('opts.text') === 'grand', 'Texte : grand');
  run('innerWidth = 3840; innerHeight = 2160; devicePixelRatio = 1; resize();');
  ok(run('cv.width * cv.height') <= run('MAX_PIXELS') + 4000, 'Image fluide : canvas plafonné (' + run('cv.width') + ' x ' + run('cv.height') + ')');
  go('image'); run('pressed.right = true'); step(1);
  ok(run('opts.image') === 'nette' && run('cv.width') === 3840, 'Image nette : pleine résolution (' + run('cv.width') + ' px)');
  run('pressed.left = true'); step(1);
  ok(run('cv.width') < 3840, 'retour à fluide');
  run('innerWidth = 1600; innerHeight = 900; resize();');
  run('pressed.pause = true'); step(1);
  ok(run('state') === 'title' && run('menu.items[menu.sel].id') === 'options', 'Échap : retour au menu principal, sur « Options »');

  // nouvelle partie en facile
  run('menu.sel = menu.items.findIndex(i => i.id === "aventure"); pressed.ok = true'); step(1); advanceDialog();
  const nAll = run('MAP.enemies.length'), nF = run('MAP.enemies.filter((e, i) => i % 3 !== 2).length');
  ok(run('gameDiff') === 'facile' && run('P.hpMax') === 10 && run('P.hp') === 10, 'facile : 5 os au départ');
  ok(run('dogs.length') === nF && nF < nAll, 'un chien sur trois en moins (' + nF + ' sur ' + nAll + ')');
  run('P.inv = 0; var hp0 = P.hp; graceT = 0; hurtPlayer(2, P.x + 50, P.y);');
  ok(run('P.hp') === run('hp0') - 1, 'une grosse morsure n’enlève qu’un demi-os');
  run('saveGame(); opts.diff = "normal";');
  ok(run('loadSave().diff') === 'facile', 'la sauvegarde garde la difficulté');
  run('loadGame(loadSave(), false)'); advanceDialog();
  ok(run('gameDiff') === 'facile' && run('dogs.length') === nF, 'Continuer : toujours en facile, même si l’option a changé');
  run('timePlayed = 600; score = 500; recordRun();');
  ok(run('JSON.stringify(Object.keys(STORE.get(RECORDS_KEY)))') === '["aventure-facile"]', 'records à part en facile');
  // texte grand dans les dialogues
  run('opts.text = "grand"; say([{ who: "tecky", text: "Ouaf !" }]); var f0 = null; drawDialog(); f0 = ctx.font;');
  ok(/46px/.test(run('f0')), 'texte grand : police de 46 px');
  run('opts.text = "normal"; drawDialog(); f0 = ctx.font;');
  ok(/38px/.test(run('f0')), 'texte normal : 38 px');
  advanceDialog();

  // vibrations : téléphone au toucher, manette quand elle sert, rien si l'option est coupée
  run('var vib = []; navigator.vibrate = ms => { vib.push(ms); return true; }; touchMode = true; pad.on = false; P.inv = 0; P.mode = "free"; graceT = 0; hurtPlayer(2, P.x + 50, P.y);');
  ok(run('vib.length') === 1 && run('vib[0]') > 50, 'mordu : le téléphone vibre (' + run('vib[0]') + ' ms)');
  run('opts.vib = "non"; P.inv = 0; P.mode = "free"; graceT = 0; hurtPlayer(2, P.x + 50, P.y);');
  ok(run('vib.length') === 1, 'option « Vibrations : non » : rien');
  run('var eff = []; var GP2 = { axes: [0, 0], buttons: [], vibrationActuator: { playEffect: (t, o) => { eff.push([t, o.duration, o.strongMagnitude]); return Promise.resolve(); } } };');
  run('navigator.getGamepads = () => [null, GP2]; touchMode = false; pad.on = true; opts.vib = "oui"; P.inv = 0; P.mode = "free"; graceT = 0; hurtPlayer(2, P.x + 50, P.y);');
  ok(run('eff.length') === 1 && run('eff[0][0]') === 'dual-rumble' && run('vib.length') === 1, 'à la manette : elle vibre, pas le téléphone');
  run('uncover(digs.find(g => !g.dug));'); advanceDialog();
  ok(run('eff.length') === 2 && run('eff[1][2]') < run('eff[0][2]'), 'os doré déterré : un petit coup');
  run('P.hp = 6; P.inv = 0; P.mode = "free"; navigator.getGamepads = () => []; pad.on = false; P.x = 30 * 64; P.y = 20 * 64;');
  ok(run('optRows().some(r => r.id === "vib")'), 'ligne « Vibrations » dans les options');

  // menu de la pause : reprendre, options, menu principal
  run('pressed.pause = true'); step(1);
  ok(run('state') === 'pause' && ids() === 'unpause,options,quit', 'pause : Reprendre, Options, Menu principal');
  run('pressed.right = true'); step(1); run('pressed.ok = true'); step(1);
  ok(run('state') === 'options' && run('optReturn') === 'pause', 'Options depuis la pause');
  ok(run('Music.level()') < 0.2, 'musique toujours discrète');
  run('pressed.bark = true'); step(1);
  ok(run('state') === 'pause' && run('menu.sel') === 1, 'B : retour à la pause');
  run('pressed.pause = true'); step(1);
  ok(run('state') === 'play', 'P : reprise');
  run('pressed.pause = true'); step(1); run('menu.sel = 2; pressed.ok = true'); step(1);
  ok(run('state') === 'title' && ids().startsWith('continue'), 'Menu principal : la partie est gardée (« Continuer »)');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
