// sauvegarde automatique, « Continuer », reprise après un KO, records (meilleur score, meilleur temps) par mode
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  const ids = () => run('menu.items.map(i => i.id).join()');
  const save = () => JSON.parse(run('LS[SAVE_KEY] || "null"'));
  ok(run('state') === 'title' && ids() === 'aventure,balade,options,badges', 'écran titre sans sauvegarde : nouvelle aventure, nouvelle balade');
  // faux localStorage (chaînes JSON, comme le vrai)
  run('var LS = {}; this.localStorage = { getItem: k => k in LS ? LS[k] : null, setItem: (k, v) => { LS[k] = String(v); }, removeItem: k => { delete LS[k]; } };');
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  ok(run('state') === 'play' && run('gameMode') === 'aventure', 'nouvelle aventure');
  ok(save() && save().clues.join() === 'false,false,false', 'partie enregistrée dès la fin de l’intro');

  // progression réelle : la barrette (sauvegarde à la fin de la réplique), un trésor, un chien en fuite
  run('dogs.forEach(d => { d.x = d.hx; d.y = d.hy; d.mode = "idle"; }); P.inv = 999;');
  run('var it = items.find(i => i.n === "hairclip"); P.x = it.x; P.y = it.y + 30; P.mode = "free";'); step(2);
  advanceDialog();
  ok(save().clues[0] === true && !save().items.some(i => i[0] === 'hairclip'), 'indice trouvé : sauvegarde aussitôt (barrette retirée du sol)');
  run('var savedDogs = dogs; dogs = []; var gd = digs[1]; P.x = gd.x; P.y = gd.y - 20; P.dir = "down"; P.mode = "free"; P.cdBite = 0; pressed.bite = true;');
  step(80); advanceDialog(); step(40);
  ok(save().dug[1] === 1 && save().treasures === 1, 'trésor déterré : sauvegardé');
  run('dogs = savedDogs; hurtDog(dogs[3], 99, 0, 0, 0); var goneId = dogs[3].id;');
  step(200);
  // sauvegarde régulière, seulement hors de danger
  run('dogs.forEach(d => { if (d.mode !== "ko") { d.x = d.hx; d.y = d.hy; d.mode = "idle"; } }); P.x = MAP.start[0]; P.y = MAP.start[1]; P.mode = "free";');
  step(60 * 5);
  ok(Math.abs(save().x - run('P.x')) < 2 && !save().dogs.includes(run('goneId')) && save().dogs.length === 18,
     'sauvegarde toutes les ' + run('SAVE_EVERY') + ' s : position, chiens restants (' + save().dogs.length + ')');
  // (maison du chien déplacée près de la niche, sinon il rentre chez lui au lieu de rester sur Tecky)
  run('var D = dogs.find(d => d.kind === "bouledogue"), H = [D.hx, D.hy]; D.x = D.hx = P.x + 160; D.y = D.hy = P.y; D.mode = "chase";');
  run('var sx = JSON.parse(LS[SAVE_KEY]).x; P.x += 3;');
  step(60 * 5);
  ok(save().x === run('sx'), 'pas de sauvegarde automatique quand un chien menace Tecky');
  run('D.x = D.hx = H[0]; D.y = D.hy = H[1]; D.mode = "idle"; P.x = MAP.start[0]; P.y = MAP.start[1];'); step(60 * 5);

  // « rechargement » : mémoire vidée, seule reste la chaîne du localStorage
  run('score = 420; timePlayed = 125; P.hpMax = 8; P.hp = 3; P.x = 20 * 64; P.y = 9 * 64; P.dir = "left"; state = "pause"; saveOnLeave(); state = "play";');
  ok(save().x === 1280 && save().hp === 3 && save().time === 125, 'en quittant la page (pause), la partie est enregistrée');
  run('STORE.mem = {}; toTitle();');
  ok(ids() === 'continue,aventure,balade,options,badges' && run('menu.sel') === 0, 'écran titre : « Continuer » en premier');
  ok(/Aventure · 1 indice sur 3 · 2 min 05 s/.test(run('menu.items[0].sub')), 'résumé de la partie : ' + run('menu.items[0].sub'));
  run('pressed.ok = true'); step(1);
  ok(run('state') === 'dialog' && /Me revoilà/.test(run('dialog.lines[0].text')) && run('dialog.lines[1].text') === run('CLUE_NEXT[1]'),
     'Continuer : Tecky rappelle où chercher ensuite');
  advanceDialog();
  ok(run('clues.join()') === 'true,false,false' && run('digs[1].dug') && run('treasures') === 1 && run('score') === 420 &&
     run('Math.round(timePlayed)') >= 125 && run('fled') === 1, 'progression restaurée (indice, trésor, score, temps, chiens en fuite)');
  ok(run('P.x') === 1280 && run('P.y') === 576 && run('P.hp') === 3 && run('P.hpMax') === 8 && run('P.dir') === 'left', 'Tecky restauré (place, os)');
  ok(run('dogs.length') === 18 && !run('dogs.some(d => d.id === goneId)'), 'le chien mis en fuite ne revient pas');
  ok(!run('items.some(i => i.n === "hairclip")') && run('items.some(i => i.n === "shoe")'), 'objets au sol restaurés');
  ok(run('alice.hidden') && Math.abs(run('sun') - 1) < 1e-6, 'Alice toujours cachée, lumière d’après-midi (1 indice)');
  ok(run('arrowT') > 7, 'la flèche montre le prochain indice');

  // KO -> « Reprendre la partie » : vie pleine, progression gardée
  run('P.x = MAP.start[0]; P.y = MAP.start[1]; saveGame(); P.mode = "ko"; P.setAnim("ko"); P.timer = 3;'); step(1);
  ok(run('state') === 'over' && ids() === 'resume,restart,title', 'KO : reprendre, recommencer, menu principal');
  step(70); run('pressed.ok = true'); step(1);
  ok(run('state') === 'dialog' && /sieste/.test(run('dialog.lines[0].text')), 'reprise : « une petite sieste et ça repart »');
  advanceDialog();
  ok(run('P.hp') === 8 && run('clues[0]') && run('treasures') === 1, 'reprise : vie pleine (8 / 8), indice et trésor gardés');
  ok(run('Music.cur') === 'main', 'le thème reprend');
  // KO -> menu principal
  run('P.mode = "ko"; P.setAnim("ko"); P.timer = 3;'); step(1); step(70);
  run('menu.sel = 2; pressed.ok = true'); step(1);
  ok(run('state') === 'title' && ids() === 'continue,aventure,balade,options,badges', 'KO : retour au menu principal, la partie reste à continuer');

  // victoire : sauvegarde effacée, records du mode
  run('pressed.ok = true'); step(1); advanceDialog();
  const win = (sc, t) => {
    run('clues = [true, true, true]; revealAlice(); score = ' + sc + '; timePlayed = ' + t + '; P.x = alice.x - 100; P.y = alice.y + 10; P.mode = "free"; P.inv = 9;');
    step(2); advanceDialog(); step(70); run('pressed.ok = true'); step(1); step(70);   // la scène de fin, passée
  };
  win(900, 1500);
  ok(run('state') === 'win' && !('tecky-quest-save' in run('LS')), 'victoire : la sauvegarde est effacée');
  ok(run('JSON.stringify(JSON.parse(LS[RECORDS_KEY]).aventure)') === '{"score":900,"time":1500,"wins":1}' &&
     run('newRecord.score && newRecord.time'), 'premiers records en aventure (900 points, 25 min)');
  run('pressed.ok = true'); step(1);
  ok(run('state') === 'title' && ids() === 'aventure,balade,options,badges' && /900 points · 25 min 00 s/.test(run('recordLine("aventure")')),
     'retour au menu : records affichés (' + run('recordLine("aventure")') + ')');
  run('pressed.ok = true'); step(1); advanceDialog();
  win(1200, 1800);
  ok(run('newRecord.score') && !run('newRecord.time'), 'meilleur score battu, pas le meilleur temps');
  ok(run('JSON.stringify(JSON.parse(LS[RECORDS_KEY]).aventure)') === '{"score":1200,"time":1500,"wins":2}', 'records : 1200 points, 25 min gardées');
  run('pressed.ok = true'); step(1); run('menu.sel = 1; pressed.ok = true'); step(1); advanceDialog();
  ok(run('gameMode') === 'balade', 'nouvelle balade depuis le menu');
  win(300, 2000);
  ok(run('JSON.stringify(Object.keys(JSON.parse(LS[RECORDS_KEY])))') === '["aventure","balade"]' &&
     run('JSON.parse(LS[RECORDS_KEY]).aventure.score') === 1200, 'records séparés par mode');
  run('drawEnd(true)');
  // sauvegarde illisible : ignorée
  run('LS[SAVE_KEY] = "{oups"; STORE.mem = {}; toTitle();');
  ok(ids() === 'aventure,balade,options,badges', 'sauvegarde illisible : ignorée sans erreur');
  // stockage refusé (navigation privée) : repli en mémoire pour la session
  run('this.localStorage = { getItem() { throw new Error("refusé"); }, setItem() { throw new Error("refusé"); }, removeItem() { throw new Error("refusé"); } };');
  run('pressed.ok = true'); step(1); advanceDialog();
  run('toTitle();');
  ok(ids() === 'continue,aventure,balade,options,badges', 'stockage refusé : la partie reste continuable pendant la session');
  // la fenêtre perd le focus, l'onglet est caché : pause automatique (jamais pendant un dialogue)
  run('menu.sel = 0; pressed.ok = true'); step(1); advanceDialog();
  run('held.left = true; onLeave();');
  ok(run('state') === 'pause' && run('menu.items[0].id') === 'unpause' && !run('held.left'), 'fenêtre quittée : pause, touches relâchées');
  run('pressed.pause = true'); step(1);
  ok(run('state') === 'play', 'on reprend comme d’habitude');
  run('say([{ who: "tecky", text: "Ouaf !" }]); onLeave();');
  ok(run('state') === 'dialog', 'pendant un dialogue : rien ne change, il attend déjà');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
