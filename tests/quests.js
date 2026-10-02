// petites quêtes du village : les lettres du facteur Marcel, le chat de Mamie Rose (Pompon)
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999; farm.state = "done"; var used = [], ds0 = drawSpr;');
  const spy = what => run(`used = []; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; ${what}; drawSpr = ds0;`);
  const talk = () => { run('P.cdBite = 0; pressed.bite = true'); step(1); };
  const near = n => { run(`P.x = ${n}.x; P.y = ${n}.y + 400; P.mode = "free";`); step(2); run(`P.x = ${n}.x; P.y = ${n}.y + 110; pops = [];`); step(2); };

  // ---- le facteur
  ok(run('letters.length') === 5 && run('ATLAS["item/letter"] && ATLAS["postman/idle"] && ATLAS["neighbor/worry"] && ATLAS["hud/portrait_postman"]'),
     '5 lettres, le facteur, la voisine et leurs portraits');
  near('postman');
  ok(run('pops.some(p => /mes lettres/.test(p.text))') && run('postmanMark()') === 0 && run('state') === 'play', 'le facteur : « Oh là là, mes lettres ! », bulle « ! »');
  ok(run('biteAction()') === 'talk', 'C : « Parler »');
  talk();
  ok(run('state') === 'dialog' && run('dialog.lines[0].who') === 'postman' && /lettres/.test(run('dialog.lines[0].text')), 'Marcel raconte le coup de vent');
  advanceDialog();
  ok(run('post.state') === 'asked' && run('postmanMark()') === 1, 'quête acceptée, bulle « ? »');
  spy('drawHUD()');
  ok(run('used.includes("item/letter")'), 'compteur de lettres dans le HUD');
  ok(run('JSON.stringify(hudCounters().map(c => c[0]))') === '["item/letter"]', 'à droite, seul (pas encore d’os doré, poules finies)');
  for (let i = 0; i < 5; i++) { run(`P.x = letters[${i}].x; P.y = letters[${i}].y + 20; pops = [];`); step(2); }
  ok(run('lettersLeft()') === 0 && run('pops.some(p => /Une lettre ! \\(5\\/5\\)/.test(p.text))'), 'en passant dessus, Tecky ramasse les cinq lettres');
  ok(run('pops.some(p => /Viens vite/.test(p.text))') && run('postmanMark()') === 0, 'Marcel l’appelle (« ! »)');
  near('postman'); const s0 = run('score'), it0 = run('items.length');
  talk();
  ok(run('state') === 'dialog' && /Toutes mes lettres/.test(run('dialog.lines[0].text')), 'C : il remercie Tecky');
  advanceDialog(); step(5);
  ok(run('post.state') === 'done' && run('score') >= s0 + run('POST.reward') && run('items.some(i => i.n === "bone")'), 'un os et des points');
  ok(run('postmanMark()') === -1, 'plus de bulle ensuite');

  // ---- la voisine et Pompon
  near('neighbor');
  ok(run('pops.some(p => /Pompon/.test(p.text))') && run('neighbor.anim') === 'worry', 'Mamie Rose s’inquiète : « Pompon ? Pompon, où es-tu ? »');
  // avant de lui avoir parlé : Pompon miaule mais ne suit pas
  run('P.x = pompon.x + 90; P.y = pompon.y; pops = [];');
  let meow = 0;
  for (let i = 0; i < 60 * 6; i++) { step(1); if (run('pops.some(p => p.text === "Miaou ?")')) meow++; }
  ok(run('pompon.mode') === 'lost' && meow > 0, 'Pompon miaule (« Miaou ? »), mais ne suit pas encore');
  near('neighbor'); if (run('state') === 'dialog') advanceDialog();
  talk();
  ok(run('state') === 'dialog' && run('dialog.lines[0].who') === 'neighbor' && /Pompon/.test(run('dialog.lines[0].text')), 'C : elle demande de l’aide');
  advanceDialog();
  ok(run('rose.state') === 'asked' && run('neighborMark()') === 1, 'quête acceptée');
  const cat = () => JSON.stringify(run('JSON.stringify(hudCounters().filter(c => c[0] === "cat_white/idle").map(c => c[4] + "/" + c[5]))'));
  ok(cat() === JSON.stringify('["0/1"]'), 'compteur du chat : 0/1');
  run('P.x = pompon.x + 100; P.y = pompon.y;'); step(2);
  ok(run('state') === 'dialog' && /Te voilà, Pompon/.test(run('dialog.lines[0].text')), 'Tecky retrouve Pompon');
  advanceDialog();
  ok(run('pompon.mode') === 'follow', 'Pompon le suit');
  ok(cat() === JSON.stringify('["1/1"]'), 'retrouvé : 1/1');
  // Tecky rentre au village, à pied (en ligne droite) : Pompon suit derrière lui
  run('var tx = neighbor.x + 60, ty = neighbor.y + 130, sx = P.x, sy = P.y;');
  let far = 0;
  for (let i = 0; i <= 300; i++) {
    run(`P.x = sx + (tx - sx) * ${i / 300}; P.y = sy + (ty - sy) * ${i / 300};`); step(1);
    if (i > 40 && run('dist(pompon.x, pompon.y, P.x, P.y)') > 260) far++;
  }
  ok(far === 0, 'il reste derrière Tecky tout le long');
  step(60 * 2);
  ok(run('pompon.mode') === 'home' && run('neighbor.anim') === 'cheer', 'arrivé chez Mamie Rose : elle se réjouit');
  ok(run('neighborMark()') === 0, 'bulle « ! » : elle veut remercier Tecky');
  near('neighbor'); if (run('state') === 'dialog') advanceDialog();
  const s1 = run('score');
  talk();
  ok(run('state') === 'dialog' && /Pompon ! Te voilà enfin/.test(run('dialog.lines[0].text')), 'C : elle remercie Tecky');
  advanceDialog(); step(5);
  ok(run('rose.state') === 'done' && run('score') >= s1 + run('POST.reward') && run('items.some(i => i.n === "sausage")'), 'une saucisse et des points');
  ok(cat() === JSON.stringify('[]'), 'quête finie : plus de compteur');
  step(60 * 3);
  ok(run('dist(pompon.x, pompon.y, neighbor.x, neighbor.y)') < 120, 'Pompon reste avec elle');
  spy('render()');
  ok(run('used.some(k => /^cat_white\\//.test(k))') && run('used.some(k => /^neighbor\\//.test(k))'), 'Pompon et Mamie Rose dessinés');

  // ---- trop loin : il attend ; aboiement : il feule ; sauvegarde
  run('newGame("aventure", true)'); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999; rose.state = "asked"; pompon.mode = "follow"; pompon.x = P.x + 60; pompon.y = P.y; crumbs = [];');
  run('P.x += 1200;'); step(3);
  ok(run('pompon.mode') === 'wait', 'Tecky trop loin : Pompon s’assoit et attend');
  run('P.x = pompon.x + 100; P.y = pompon.y;'); step(2);
  ok(run('pompon.mode') === 'follow' && run('state') === 'play', 'Tecky revient : il le suit de nouveau (sans dialogue)');
  run('P.x = pompon.x - 200; P.y = pompon.y; P.dir = "right"; P.cdBark = 0; P.mode = "free"; pressed.bark = true;'); step(2);
  ok(run('pompon.anim') === 'hiss', 'un aboiement : il feule');
  run('letters[1].got = letters[3].got = true; post.state = "asked"; saveGame(); var SV = loadSave();');
  ok(run('SV.post') === 'asked' && run('SV.letters') === '01010' && run('SV.rose') === 'asked' && run('SV.cat[2]') === 'follow', 'la sauvegarde garde les deux quêtes');
  run('loadGame(SV, false)'); advanceDialog();
  ok(run('post.state') === 'asked' && run('lettersLeft()') === 3 && run('rose.state') === 'asked' && run('pompon.mode') === 'wait', 'Continuer : quêtes restaurées (Pompon attend Tecky)');
  // lettres trouvées avant d'avoir parlé au facteur
  run('newGame("aventure", true)'); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999; P.x = letters[0].x; P.y = letters[0].y + 20; pops = [];'); step(2);
  ok(run('letters[0].got') && run('pops.some(p => p.text === "Une lettre ?")'), 'une lettre ramassée avant de connaître le facteur : « Une lettre ? »');
  near('postman'); if (run('state') === 'dialog') advanceDialog();
  talk();
  ok(run('dialog.lines[1].text').includes('déjà trouvé 1'), 'Marcel : « Tu en as déjà trouvé 1 ? »');
  advanceDialog();
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
