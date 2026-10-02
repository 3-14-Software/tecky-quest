// quête des poules : le fermier demande de l'aide (seulement si Tecky vient lui parler, C), Tecky ramène les cinq
// poules dans l'enclos en aboyant
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999;');   // pas de voitures : Tecky aboie parfois au bord de la route
  ok(run('questHens().length') === 5 && run('hens.length') === 9, '5 poules de la quête (et 4 autres au sud de la route)');
  ok(run('questHens().every(h => !h.penned)') && run('farm.state') === 'new', 'au départ, elles sont toutes hors de l’enclos');
  // le fermier : il ne parle que si Tecky vient le voir et appuie sur C
  run('P.x = farmer.x; P.y = farmer.y + 250; P.mode = "free"; pops = [];'); step(2);
  ok(run('state') === 'play' && !run('pops.length'), 'loin du fermier : rien');
  ok(run('farmerMark()') === 0, 'au-dessus de sa tête : « ! »');
  run('P.y = farmer.y + 110;'); step(2);
  ok(run('pops.some(p => /Hé, petit chien/.test(p.text))'), 'Tecky arrive : petite exclamation (« Hé, petit chien ! »)');
  ok(run('farm.state') === 'new' && !(run('state') === 'dialog' && run('dialog.lines[0].who') === 'farmer'), 'mais il ne donne pas la quête tout seul');
  ok(!run('clues[0]') && !run('items.some(i => i.n === "hairclip" && dist(i.x, i.y, farmer.x, farmer.y) < 400)'),
     'la barrette n’est pas à côté de lui (on ne la ramasse pas en lui parlant)');
  step(1); run('updateCamera(10)');                                    // (caméra recentrée sur Tecky)
  ok(run('biteAction()') === 'talk' && run('talkHint !== null'), 'près de lui : C fait « Parler »');
  ok(run('ACTION_FRAME.talk') !== run('ACTION_FRAME.read') && run('ATLAS["hud/action"].f.length') > run('ACTION_FRAME.talk') + 1,
     'bouton « Parler » : sa bulle de dialogue, pas la pancarte de « Lire »');
  run('var used = []; var ds0 = drawSpr; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; render(); drawSpr = ds0;');
  ok(run('used.includes("hud/talk")') === false, 'tout près, la bulle « Parler » remplace le « ! »');
  run('P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('state') === 'dialog' && run('dialog.lines[0].who') === 'farmer' && /poules/.test(run('dialog.lines[0].text')),
     'C : il demande de l’aide');
  ok(run('farmer.anim') === 'talk', 'il parle (animation)');
  advanceDialog();
  ok(run('farm.state') === 'asked' && run('farmerMark()') === 1, 'quête acceptée, bulle « ? »');
  run('used = []; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; drawHUD(); drawSpr = ds0;');
  ok(run('used.includes("hen/idle/right")'), 'compteur de poules dans le HUD');
  run('P.y = farmer.y + 400'); step(2);
  run('used = []; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; render(); drawSpr = ds0;');
  ok(run('used.includes("hud/talk")'), 'de loin, on voit sa bulle');
  run('P.y = farmer.y + 110; pops = [];'); step(2);
  ok(run('state') === 'play' && run('pops.some(p => /Encore 5 poules/.test(p.text))'), 'en repassant : « Encore 5 poules ! », sans dialogue');
  run('pressed.act = true'); step(1);
  ok(run('state') === 'dialog' && /Il en reste 5/.test(run('dialog.lines[0].text')), 'E parle aussi : « Il en reste 5 dehors ! »');
  advanceDialog();
  // la file des dialogues : une réplique demandée pendant un dialogue passe ensuite
  run('say([{ who: "farmer", text: "A" }]); say([{ who: "tecky", text: "B" }]);');
  ok(run('(dialog.queue || []).length') === 1, 'say() pendant un dialogue : la réplique attend son tour');
  advanceDialog();

  // pousser une poule : elle reste où elle arrive
  const [gx, gy] = run('gatePoint()');
  const bark = (hx, hy, px, py, dir) => {
    run(`var H = questHens().find(h => !h.penned); H.x = H.hx = ${hx}; H.y = H.hy = ${hy}; H.mode = "idle"; H.timer = 9;` +
        `P.x = ${px}; P.y = ${py}; P.dir = "${dir}"; P.mode = "free"; P.cdBark = 0; pressed.bark = true;`);
    step(80);
  };
  bark(gx - 400, gy + 120, gx - 550, gy + 120, 'right');
  ok(run('H.mode') !== 'flee' && run('H.x') > gx - 340 && Math.abs(run('H.hx') - run('H.x')) < 1 && !run('H.penned'),
     'une poule poussée reste là où elle arrive (' + Math.round(run('H.x') - (gx - 400)) + ' px)');
  step(60 * 6);
  ok(run('dist(H.x, H.y, H.hx, H.hy)') < 90, 'puis picore autour de sa nouvelle place');
  // jamais sur la grande route
  bark(gx - 300, 11 * 64, gx - 300, 9.4 * 64, 'down');
  ok(run('H.y') <= run('FARM.roadY') + 0.01, 'poussée vers la route, elle s’arrête au bord');
  // droit dans la barrière, puis de biais : la barrière l'aspire
  const n0 = run('hensLeft()'), sc0 = run('score');
  bark(gx, gy + 70, gx, gy + 180, 'up');
  ok(run('hensLeft()') === n0 - 1 && run('score') === sc0 + run('FARM.perHen'), 'aboyée par la barrière ouverte : rentrée (+' + run('FARM.perHen') + ')');
  ok(run('pops.some(p => p.text === "Rentrée !")'), 'bulle « Rentrée ! »');
  bark(gx + 70, gy + 70, gx + 70, gy + 180, 'up');
  ok(run('hensLeft()') === n0 - 2, 'de biais, la barrière la guide vers l’ouverture');
  // une poule rentrée reste dans l'enclos, même si Tecky aboie dedans
  run('var I = questHens().find(h => h.penned); P.x = I.x - 100; P.y = I.y; P.dir = "right"; P.mode = "free"; P.cdBark = 0; pressed.bark = true;');
  step(60 * 3);
  const R = run('penRect()');
  ok(run('questHens().filter(h => h.penned).every(h => h.x >= penRect()[0] && h.x <= penRect()[2] && h.y >= penRect()[1] && h.y <= penRect()[3])'),
     'les poules rentrées restent dans l’enclos');
  // les deux poules du sud ne comptent pas
  ok(run('hens.filter(h => !h.quest).every(h => !h.penned)'), 'les poules du sud ne font pas partie de la quête');
  // sauvegarde : état de la quête et poules rentrées
  run('saveGame(); var S = loadSave();');
  ok(run('S.farm') === 'asked' && run('S.hens.filter(h => h[2]).length') === 2, 'la sauvegarde garde la quête et les poules rentrées');
  run('loadGame(S, false)'); advanceDialog();
  ok(run('farm.state') === 'asked' && run('questHens().filter(h => h.penned).length') === 2, 'Continuer : quête restaurée');
  run('dogs = []; cars = []; P.inv = 999;');
  // les dernières : le fermier remercie, saucisse et points
  for (let k = 0; k < 6 && run('hensLeft()') > 0; k++) bark(gx, gy + 70, gx, gy + 180, 'up');
  ok(run('hensLeft()') === 0, 'toutes les poules sont rentrées');
  ok(run('pops.some(p => /Viens me voir/.test(p.text))') && run('farmerMark()') === 0 && run('state') === 'play',
     'le fermier appelle Tecky (« Bravo ! Viens me voir ! », bulle « ! »), sans dialogue');
  const sc1 = run('score');
  run('P.x = farmer.x; P.y = farmer.y + 400; P.mode = "free";'); step(2);
  run('P.y = farmer.y + 110;'); step(2); if (run('state') === 'dialog') advanceDialog();
  run('P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('state') === 'dialog' && run('dialog.lines[0].who') === 'farmer' && /Toutes mes poules/.test(run('dialog.lines[0].text')),
     'C : le fermier remercie Tecky');
  const hp0 = run('P.hpMax');
  advanceDialog(); step(40);
  ok(run('farm.state') === 'done' && run('score') >= sc1 + run('FARM.reward'), 'quête terminée : +' + run('FARM.reward') + ' points');
  ok(run('P.hpMax') === hp0 + 2, 'et une saucisse : un os de plus (' + hp0 / 2 + ' -> ' + run('P.hpMax') / 2 + ')');
  ok(run('farmer.anim') === 'wave' || run('farmer.waveT') > 0, 'le fermier salue');
  run('P.y = farmer.y + 400'); step(2); run('P.x = farmer.x; P.y = farmer.y + 110; pops = [];'); step(2);
  ok(run('state') === 'play' && run('pops.some(p => p.text === "Bonjour, Tecky !")') && run('farmerMark()') === -1,
     'ensuite : « Bonjour, Tecky ! », plus de bulle');
  run('P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('state') === 'dialog' && /Merci encore/.test(run('dialog.lines[0].text')), 'C : « Merci encore pour mes poules »');
  advanceDialog();

  // autre ordre : toutes rentrées avant de parler au fermier -> il remercie directement
  run('newGame("balade", true)'); advanceDialog();
  run('dogs = []; questHens().forEach(h => { h.x = h.hx = gatePoint()[0]; h.y = h.hy = gatePoint()[1] - 60; keepHen(h); }); P.x = farmer.x - 60; P.y = farmer.y + 100; P.mode = "free";');
  step(2); if (run('state') === 'dialog') advanceDialog();
  run('P.cdBite = 0; pressed.bite = true'); step(1);
  ok(run('state') === 'dialog' && /Toutes mes poules/.test(run('dialog.lines[0].text')), 'poules rentrées avant d’avoir parlé : C, et il remercie tout de suite');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
