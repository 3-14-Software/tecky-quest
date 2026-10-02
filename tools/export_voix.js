// Export des répliques pour la synthèse vocale : node tools/export_voix.js (après python3 pack_web.py).
// Fait tourner le jeu sans affichage (comme les tests) et appelle chaque dialogue dans tous ses cas (comptes, appareil,
// mode, état des quêtes) en notant les répliques ; puis relève dans game.js les répliques écrites en dur, pour n'en
// oublier aucune ; de même pour les petites bulles (exclamations des personnages, de Tecky, cris des animaux : le 4e
// argument d'addWordPop dit qui parle). Une ligne par fichier audio à générer : voix/repliques.csv et
// voix/repliques.json (nom du fichier = voiceKey() du jeu, texte à dire = spokenText()). --check : dit seulement si ces
// fichiers sont à jour.
const fs = require('fs'), path = require('path'), { execSync } = require('child_process');
const ROOT = path.join(__dirname, '..'), OUT = path.join(ROOT, 'voix');
const GAME = path.join(ROOT, 'tests', 'game_full.js'), SRC = path.join(ROOT, 'web_src', 'game.js');
const CHECK = process.argv.includes('--check');
if (!fs.existsSync(GAME) || fs.statSync(GAME).mtimeMs < fs.statSync(path.join(ROOT, 'web', 'index.html')).mtimeMs)
  execSync('python3 tests/regen.py', { cwd: ROOT });
let base = fs.readFileSync(path.join(ROOT, 'tests', 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
base = base.replace("__dirname + '/' + (process.argv[2] || 'game_full.js')", JSON.stringify(GAME));

// personnages : nom affiché et voix conseillée (dans l'ordre de l'export)
const VOICES = {
  tecky: ['Tecky', 'petit teckel joyeux, courageux et un peu espiègle'],
  alice: ['Alice', 'petite fille de 5 ans, enjouée'],
  info: ['Narrateur', 'aides et panneaux : voix calme, claire et posée'],
  farmer: ['Gaston', 'le fermier : jovial, voix grave et chaleureuse'],
  postman: ['Marcel', 'le facteur : enjoué, un peu pressé'],
  neighbor: ['Mamie Rose', 'la voisine : douce vieille dame'],
  leon: ['Léon', 'le cariste du port : sympathique, voix forte'],
  iris: ['Iris', 'le vieux Jack Russell, ami et mentor de Tecky : voix posée et chaleureuse, un peu rocailleuse, celle d’un vieux sage'],
  piquette: ['Maman Piquette', 'la maman hérisson de la forêt : douce, tendre, un peu inquiète'],
  doberman: ['Le doberman', 'gros chien bourru, voix grave'],
  dog: ['Les chiens du coin', 'chiens grognons (« Grrr… »), ou contents en balade (« Copain ! »)'],
  cat: ['Les chats', 'Pompon et les chats du coin : miaulements, feulements'],
  squirrel: ['Les écureuils', 'petite voix aiguë et rapide'],
  duck: ['Les canards', 'coin-coin'],
  train: ['Titine', 'la petite locomotive du port : voix joyeuse et chantante'],
  hedgehog: ['Les bébés hérissons', 'toute petite voix aiguë (« Couic ! »)'],
  cow: ['Les vaches', 'meuglement grave et paisible (le veau : plus aigu)'],
  baker: ['Bernard', 'le boulanger du village : voix ronde et joviale'],
  vendor: ['Josette', 'la marchande de fruits : voix chantante, un peu gouailleuse, de marché'],
  florist: ['Lili', 'la fleuriste : jeune femme, voix douce et souriante'],
  kid: ['Lucas', 'un petit garçon d’environ 6 ans, tout content : voix aiguë et enthousiaste'],
};
// répliques dont le texte est calculé (pas une chaîne écrite en dur) : chacune doit être produite ci-dessous ; si ce
// nombre change, une réplique calculée a été ajoutée ou retirée dans game.js : adapter ce fichier
const DYNAMIC_SITES = 19;
const DYNAMIC_POPS = 10;          // de même pour les bulles (texte calculé : comptes, noms des jouets, mot passé à dropToy)
const NPC_VARS = { farmer: 'farmer', postman: 'postman', neighbor: 'neighbor', leon: 'leon', iris: 'iris', piquette: 'piquette' };
// répliques relevées dans le code (écrites en dur, dites en cours de route) : contexte selon la fonction qui les dit
const WHERE = { doBark: 'Premier aboiement sur le doberman', updatePompon: 'Tecky retrouve Pompon',
  updateTunnel: 'Premier terrier', updatePlayer: 'Devant la cachette d’Alice, avant les trois indices' };
// bulles relevées dans le code : contexte selon la fonction qui les affiche
const WHERE_POP = { doBark: 'Tecky aboie', updatePompon: 'Pompon', updateDog: 'Les chiens du coin',
  updateCritter: 'Écureuils et chats', scareDuck: 'Les canards s’envolent', updateTrain: 'Titine s’arrête devant Tecky',
  barkAtTrain: 'Tecky aboie vers Titine', updateVehicle: 'Une voiture bouscule Tecky', startSniff: 'Tecky flaire la piste',
  layTrail: 'Tecky flaire (pas de piste par ici)', updateItems: 'Tecky ramasse un objet', checkGoal: 'Un ballon entre dans le filet',
  cowMoo: 'Une vache meugle (Tecky est dans le pré)', scareCow: 'Tecky aboie vers une vache',
  edgeBump: 'Tecky pousse contre le bord de la carte' };
const TONE = { 2: 'joyeux', 3: 'inquiet' };               // expression du portrait (face) : le ton à donner
const AUDIO = /\.(mp3|ogg|wav)$/;

function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; var REC = [], CTX = "";' +
      'say = function (lines) { for (const l of lines) REC.push({ who: l.who, face: l.face || 0, text: l.text, ctx: CTX }); };' +
      'addWordPop = function (text, x, y, who) { if (who) REC.push({ who, face: 0, text, ctx: CTX, pop: true }); };');
  const ask = (ctx, code) => run(`CTX = ${JSON.stringify(ctx)}; ${code}`);
  // introduction (aventure, balade ; au clavier ou à la manette, ou au toucher), nouvelle partie, reprise
  for (const mode of ['aventure', 'balade']) for (const touch of [false, true])
    ask(`Introduction (${mode}${touch ? ', au toucher' : ''})`, `gameMode = "${mode}"; touchMode = ${touch}; say(introLines());`);
  ask('Recommencer', 'touchMode = false; newGame("aventure", true);');
  run('dogs = []; cars = [];');
  ask('Continuer', 'saveGame(); loadGame(STORE.get(SAVE_KEY), false);');
  ask('Reprendre après un KO', 'saveGame(); loadGame(STORE.get(SAVE_KEY), true);');
  run('dogs = []; cars = [];');
  // indices d'Alice, os dorés, panneaux
  ask('Indice trouvé', 'CLUE_FOUND.forEach(t => say([{ who: "tecky", text: t }]));');
  ask('Où chercher ensuite', 'CLUE_NEXT.forEach(t => say([{ who: "tecky", text: t }]));');
  ask('Os doré déterré', 'treasures = 0; digs.forEach(g => uncover(g));');
  ask('Panneau', 'MAP.signs.forEach(s => say([{ who: "info", text: s[2] }]));');
  // quêtes : première demande, rappels (chaque compte), remerciements, après coup
  ask('Gaston : demande', 'farm.state = "new"; talkFarmer();');
  for (let n = 5; n >= 1; n--)
    ask('Gaston : rappel', `farm.state = "asked"; questHens().forEach((h, i) => h.penned = i >= ${n}); talkFarmer();`);
  ask('Gaston : merci', 'questHens().forEach(h => h.penned = true); talkFarmer();');
  ask('Gaston : après la quête', 'farm.state = "done"; talkFarmer();');
  for (let got = 0; got <= 4; got++)
    ask('Marcel : demande', `post.state = "new"; letters.forEach((l, i) => l.got = i < ${got}); talkPostman();`);
  for (let n = 5; n >= 1; n--)
    ask('Marcel : rappel', `post.state = "asked"; letters.forEach((l, i) => l.got = i >= ${n}); talkPostman();`);
  ask('Marcel : merci', 'letters.forEach(l => l.got = true); talkPostman();');
  ask('Marcel : après la quête', 'post.state = "done"; talkPostman();');
  ask('Mamie Rose : demande', 'rose.state = "new"; pompon.mode = "lost"; talkNeighbor();');
  ask('Mamie Rose : rappel', 'rose.state = "asked"; pompon.mode = "lost"; talkNeighbor();');
  ask('Mamie Rose : rappel (Pompon suit Tecky)', 'pompon.mode = "follow"; talkNeighbor();');
  ask('Mamie Rose : merci', 'pompon.mode = "home"; talkNeighbor();');
  ask('Mamie Rose : après la quête', 'rose.state = "done"; talkNeighbor();');
  ask('Léon : demande', 'fete.state = "new"; talkLeon();');
  for (let n = 5; n >= 1; n--)
    ask('Léon : rappel', `fete.state = "asked"; balls.forEach((b, i) => b.inNet = i >= ${n}); talkLeon();`);
  ask('Léon : merci', 'balls.forEach(b => b.inNet = true); talkLeon();');
  ask('Léon : après la quête', 'fete.state = "done"; talkLeon();');
  ask('Iris : demande', 'jouets.state = "new"; talkIris();');
  for (let n = 3; n >= 1; n--)
    ask('Iris : rappel', `jouets.state = "asked"; toys.forEach((t, i) => t.home = i >= ${n}); talkIris();`);
  ask('Iris : merci', 'toys.forEach(t => t.home = true); talkIris();');
  for (const touch of [false, true])
    for (let i = 0; i < 5; i++) ask(`Iris : conseil après la quête${touch ? ' (au toucher)' : ''}`, `jouets.state = "done"; touchMode = ${touch}; iris.tip = ${i}; talkIris();`);
  run('touchMode = false;');
  // bulles calculées : saluts des personnages (selon l'état de leur quête), comptes, jouets d'Iris
  const greet = (who, ctx, setup) => ask(`${VOICES[who][0]} : ${ctx}`, setup + ` NPC_DO[${JSON.stringify(NPC_VARS[who])}].greet();`);
  greet('farmer', 'Tecky arrive', 'farm.state = "new";');
  for (let n = 5; n >= 0; n--) greet('farmer', 'Tecky arrive', `farm.state = "asked"; questHens().forEach((h, i) => h.penned = i >= ${n});`);
  greet('farmer', 'Tecky arrive', 'farm.state = "done";');
  greet('postman', 'Tecky arrive', 'post.state = "new";');
  for (let n = 5; n >= 0; n--) greet('postman', 'Tecky arrive', `post.state = "asked"; letters.forEach((l, i) => l.got = i >= ${n});`);
  greet('postman', 'Tecky arrive', 'post.state = "done";');
  greet('neighbor', 'Tecky arrive', 'rose.state = "new";');
  for (const m of ['lost', 'home']) greet('neighbor', 'Tecky arrive', `rose.state = "asked"; pompon.mode = "${m}";`);
  greet('neighbor', 'Tecky arrive', 'rose.state = "done";');
  greet('leon', 'Tecky arrive', 'fete.state = "new";');
  for (let n = 5; n >= 0; n--) greet('leon', 'Tecky arrive', `fete.state = "asked"; balls.forEach((b, i) => b.inNet = i >= ${n});`);
  greet('leon', 'Tecky arrive', 'fete.state = "done";');
  greet('iris', 'Tecky arrive', 'jouets.state = "new";');
  for (let n = 3; n >= 0; n--) greet('iris', 'Tecky arrive', `jouets.state = "asked"; toys.forEach((t, i) => t.home = i >= ${n});`);
  greet('iris', 'Tecky arrive', 'jouets.state = "done";');
  greet('piquette', 'Tecky arrive', 'piq.state = "new";');
  for (let n = 3; n >= 0; n--) greet('piquette', 'Tecky arrive', `piq.state = "asked"; babies.forEach((b, i) => b.mode = i >= ${n} ? "home" : "hidden");`);
  greet('piquette', 'Tecky arrive', 'piq.state = "done";');
  // les poules rentrent, Tecky ramasse les lettres, les ballons entrent dans le filet (avant ou après la demande)
  for (const st of ['new', 'asked']) {
    ask('Une poule rentre dans l’enclos', `farm.state = "${st}"; questHens().forEach(h => h.penned = false); var R = penRect();` +
        ' questHens().forEach(h => { h.x = (R[0] + R[2]) / 2; h.y = (R[1] + R[3]) / 2; keepHen(h); });');
    ask('Tecky ramasse une lettre', `post.state = "${st}"; letters.forEach(l => l.got = false); P.mode = "free";` +
        ' letters.forEach(l => { P.x = l.x; P.y = l.y + 20; updateLetters(0); });');
    ask('Un ballon entre dans le filet', `fete.state = "${st}"; balls.forEach(b => { b.inNet = false; b.x = MAP.goal[0]; b.y = MAP.goal[1] - 20; checkGoal(b); });`);
    ask('Tecky prend un jouet d’Iris', `jouets.state = "${st}"; toys.forEach(t => { t.home = t.carried = false; t.cd = 0; });` +
        ' toys.forEach(t => { P.x = t.x; P.y = t.y; updateToys(0); const c = carried(); if (c) c.carried = false; t.cd = 9; });');
    ask('Un petit hérisson rejoint sa maman', `piq.state = "${st}"; babies.forEach(b => b.mode = "hidden"); babies.forEach(b => { babyHome(b); piquetteCall(); });`);
    ask('Des petits hérissons rejoignent leur maman ensemble', `piq.state = "${st}"; babies.forEach(b => b.mode = "hidden"); babyHome(babies[0]); babyHome(babies[1]); piquetteCall();`);
    ask('Tecky rapporte un jouet à Iris', `jouets.state = "${st}"; toys.forEach(t => { t.home = t.carried = false; }); toys.forEach(t => giveToy(t));`);
  }
  ask('Tecky aboie avec un jouet dans la gueule', 'toys[0].home = false; toys[0].carried = true; dropToy("Oups !");');
  ask('Maman Piquette : demande', 'piq.state = "new"; talkPiquette();');
  for (let n = 3; n >= 1; n--)
    ask('Maman Piquette : rappel', `piq.state = "asked"; babies.forEach((b, i) => b.mode = i >= ${n} ? "home" : "hidden"); talkPiquette();`);
  ask('Maman Piquette : merci', 'babies.forEach(b => b.mode = "home"); talkPiquette();');
  ask('Maman Piquette : après la quête', 'piq.state = "done"; talkPiquette();');
  for (const k of ['baker', 'vendor', 'florist', 'kid'])
    for (let i = 0; i < 2; i++)
      ask(`${VOICES[k][0]} salue Tecky qui passe`, `var V = villagers.find(v => v.kind === "${k}"); V.near = false; V.cd = 0; V.i = ${i};` +
          ' P.x = V.x; P.y = V.y + 100; P.mode = "free"; updateVillager(V, 0);');
  ask('Retrouvailles avec Alice', 'finale();');
  const rec = JSON.parse(run('JSON.stringify(REC)'));

  // répliques écrites en dur dans game.js : toutes doivent être là (sinon, on les ajoute avec leur fonction comme contexte)
  const src = fs.readFileSync(SRC, 'utf8');
  const lit = /who: '(\w+)'(?:,\s*face: ([^,]+))?,\s*text: ("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')\s*}/g;
  let m, literal = 0;
  while ((m = lit.exec(src))) {
    literal++;
    const text = m[3][0] === '"' ? JSON.parse(m[3]) : m[3].slice(1, -1).replace(/\\'/g, "'");
    if (rec.some(r => r.who === m[1] && r.text === text)) continue;
    const before = src.slice(0, m.index), fn = [...before.matchAll(/(?:function (\w+)|const (\w+) = \(\) =>)/g)].pop();
    const name = fn ? fn[1] || fn[2] : '';
    rec.push({ who: m[1], face: +m[2] || 0, text, ctx: WHERE[name] || (name ? 'dans ' + name + '()' : '') });
  }
  const sites = (src.match(/who: '\w+'/g) || []).length - literal;
  // bulles écrites en dur : addWordPop('texte', x, y, 'qui') et npcShout(personnage, 'texte'), une alternative
  // (cond ? 'a' : 'b') comprise ; les autres (texte calculé) sont produites plus haut
  const lits = e => [...e.replace(/[!=]==\s*'(?:[^'\\]|\\.)*'/g, '').matchAll(/'((?:[^'\\]|\\.)*)'/g)]   // (sans les comparaisons)
    .map(x => x[1].replace(/\\'/g, "'"));
  const args = str => {        // arguments d'un appel, découpés aux virgules de premier niveau (hors des chaînes)
    const out = []; let depth = 0, cur = '', q = null;
    for (let i = 0; i < str.length; i++) {
      const ch = str[i];
      if (q) { cur += ch; if (ch === '\\') cur += str[++i]; else if (ch === q) q = null; continue; }
      if (ch === "'" || ch === '"' || ch === '`') { q = ch; cur += ch; continue; }
      if (ch === ',' && depth === 0) { out.push(cur.trim()); cur = ''; continue; }
      if ('([{'.includes(ch)) depth++;
      if (')]}'.includes(ch)) { if (depth === 0) break; depth--; }
      cur += ch;
    }
    return out.concat(cur.trim());
  };
  let pops = 0;
  for (const mm of src.matchAll(/(addWordPop|npcShout)\(/g)) {
    if (/function $/.test(src.slice(mm.index - 9, mm.index))) continue;
    const a = args(src.slice(mm.index + mm[0].length, mm.index + 400));
    const [textArg, whoList] = mm[1] === 'npcShout' ? [a[1], [NPC_VARS[a[0]]]] : [a[0], a[3] ? lits(a[3]).length ? lits(a[3]) : [] : []];
    if (!whoList.length || !whoList[0]) continue;                      // personne ne le dit (« ! » du chien de berger)
    if (/[+`]|^\w+$|\[/.test(textArg.replace(/'(?:[^'\\]|\\.)*'/g, "''"))) {          // calculé
      pops++;
      if (process.argv.includes('--sites')) console.log('bulle calculée, ligne', src.slice(0, mm.index).split('\n').length);
      continue;
    }
    const texts = lits(textArg);
    texts.forEach((text, i) => {
      const who = whoList[i] || whoList[0];
      if (rec.some(r => r.who === who && r.text === text)) return;
      const fn = [...src.slice(0, mm.index).matchAll(/function (\w+)/g)].pop();
      rec.push({ who, face: 0, text, ctx: WHERE_POP[fn && fn[1]] || (fn ? 'dans ' + fn[1] + '()' : ''), pop: true });
    });
  }
  const warn = [sites !== DYNAMIC_SITES
    ? `ATTENTION : ${sites} répliques calculées dans game.js (${DYNAMIC_SITES} attendues) : en produire les cas dans tools/export_voix.js` : '',
  pops !== DYNAMIC_POPS
    ? `ATTENTION : ${pops} bulles calculées dans game.js (${DYNAMIC_POPS} attendues) : en produire les cas dans tools/export_voix.js` : '']
    .filter(Boolean);

  // une ligne par texte à dire : les [action] en mots, au clavier et à la manette s'il y en a
  const rows = [];
  for (const r of rec) {
    const devices = /\[[a-z]+\]/.test(r.text) ? ['clavier', 'manette'] : [''];
    for (const dev of devices) {
      const spoken = run(`spokenText(${JSON.stringify(r.text)}, ${JSON.stringify(dev)})`);
      const file = run(`voiceKey(${JSON.stringify(r.who)}, ${JSON.stringify(spoken)})`);
      const same = rows.find(x => x.fichier === file);
      if (same) { if (r.ctx && !same.contexte.includes(r.ctx)) same.contexte += ' ; ' + r.ctx; continue; }
      rows.push({ fichier: file, personnage: (VOICES[r.who] || [r.who])[0], who: r.who, type: r.pop ? 'bulle' : 'dialogue',
        appareil: dev, ton: TONE[r.face] || '', texte: spoken, affiche: r.text, contexte: r.ctx });
    }
  }
  const order = Object.keys(VOICES);
  rows.sort((a, b) => order.indexOf(a.who) - order.indexOf(b.who) || (a.type === 'bulle') - (b.type === 'bulle'));
  const cell = v => /[;"\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  const csv = ['fichier;personnage;type;appareil;ton;texte à dire;contexte']
    .concat(rows.map(r => [r.fichier, r.personnage, r.type, r.appareil, r.ton, r.texte, r.contexte].map(cell).join(';'))).join('\n') + '\n';
  const json = JSON.stringify({
    voix: Object.fromEntries(order.map(w => [w, { nom: VOICES[w][0], voix: VOICES[w][1] }])),
    repliques: rows.map(({ who, ...r }) => Object.assign({ voix: who }, r)),
  }, null, 2) + '\n';

  const csvPath = path.join(OUT, 'repliques.csv'), jsonPath = path.join(OUT, 'repliques.json');
  const per = order.map(w => VOICES[w][0] + ' ' + rows.filter(r => r.who === w).length).join(', ');
  const nPop = rows.filter(r => r.type === 'bulle').length;
  if (CHECK) {
    const same = fs.existsSync(csvPath) && fs.readFileSync(csvPath, 'utf8') === csv;
    console.log(same ? `voix : ${rows.length} répliques et bulles, à jour` : 'voix : À METTRE À JOUR (node tools/export_voix.js)');
  } else {
    fs.mkdirSync(OUT, { recursive: true });
    fs.writeFileSync(csvPath, csv); fs.writeFileSync(jsonPath, json);
    console.log(`voix : ${rows.length} à enregistrer, dont ${nPop} bulles (${per}) -> voix/repliques.csv, voix/repliques.json`);
  }
  // fichiers audio déjà déposés dans voix/ : présents, manquants, en trop (répliques modifiées ou retirées)
  const have = fs.existsSync(OUT) ? fs.readdirSync(OUT).filter(f => AUDIO.test(f)) : [];
  const names = new Set(rows.map(r => r.fichier)), got = new Set(have.map(f => f.replace(AUDIO, '')));
  const extra = have.filter(f => !names.has(f.replace(AUDIO, '')));
  if (have.length) console.log(`voix : ${rows.filter(r => got.has(r.fichier)).length} / ${rows.length} enregistrées` +
    (extra.length ? ` ; en trop (à supprimer) : ${extra.join(', ')}` : ''));
  for (const w of warn) console.log('PB ' + w);
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
