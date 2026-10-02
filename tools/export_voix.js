// Export des répliques pour la synthèse vocale : node tools/export_voix.js (après python3 pack_web.py).
// Fait tourner le jeu sans affichage (comme les tests) et appelle chaque dialogue dans tous ses cas (comptes, appareil,
// mode, état des quêtes) en notant les répliques ; puis relève dans game.js les répliques écrites en dur, pour n'en
// oublier aucune. Une ligne par fichier audio à générer : voix/repliques.csv et voix/repliques.json (nom du fichier
// = voiceKey() du jeu, texte à dire = spokenText()). --check : dit seulement si ces fichiers sont à jour.
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
  nestor: ['Nestor', 'le vieux chien du gardien : voix lente, grave et bonhomme'],
};
// répliques dont le texte est calculé (pas une chaîne écrite en dur) : chacune doit être produite ci-dessous ; si ce
// nombre change, une réplique calculée a été ajoutée ou retirée dans game.js : adapter ce fichier
const DYNAMIC_SITES = 17;
// répliques relevées dans le code (écrites en dur, dites en cours de route) : contexte selon la fonction qui les dit
const WHERE = { doBark: 'Premier aboiement sur le doberman', updatePompon: 'Tecky retrouve Pompon',
  updateTunnel: 'Premier terrier', updatePlayer: 'Devant la cachette d’Alice, avant les trois indices' };
const TONE = { 2: 'joyeux', 3: 'inquiet' };               // expression du portrait (face) : le ton à donner
const AUDIO = /\.(mp3|ogg|wav)$/;

function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; var REC = [], CTX = "";' +
      'say = function (lines) { for (const l of lines) REC.push({ who: l.who, face: l.face || 0, text: l.text, ctx: CTX }); };');
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
  ask('Nestor : demande', 'nest.state = "new"; talkNestor();');
  for (let n = 3; n >= 1; n--)
    ask('Nestor : rappel', `nest.state = "asked"; toys.forEach((t, i) => t.home = i >= ${n}); talkNestor();`);
  ask('Nestor : merci', 'toys.forEach(t => t.home = true); talkNestor();');
  ask('Nestor : après la quête', 'nest.state = "done"; talkNestor();');
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
  const warn = sites !== DYNAMIC_SITES
    ? `ATTENTION : ${sites} répliques calculées dans game.js (${DYNAMIC_SITES} attendues) : en produire les cas dans tools/export_voix.js` : '';

  // une ligne par texte à dire : les [action] en mots, au clavier et à la manette s'il y en a
  const rows = [];
  for (const r of rec) {
    const devices = /\[[a-z]+\]/.test(r.text) ? ['clavier', 'manette'] : [''];
    for (const dev of devices) {
      const spoken = run(`spokenText(${JSON.stringify(r.text)}, ${JSON.stringify(dev)})`);
      const file = run(`voiceKey(${JSON.stringify(r.who)}, ${JSON.stringify(spoken)})`);
      const same = rows.find(x => x.fichier === file);
      if (same) { if (r.ctx && !same.contexte.includes(r.ctx)) same.contexte += ' ; ' + r.ctx; continue; }
      rows.push({ fichier: file, personnage: (VOICES[r.who] || [r.who])[0], who: r.who, appareil: dev, ton: TONE[r.face] || '',
        texte: spoken, affiche: r.text, contexte: r.ctx });
    }
  }
  const order = Object.keys(VOICES);
  rows.sort((a, b) => order.indexOf(a.who) - order.indexOf(b.who));
  const cell = v => /[;"\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  const csv = ['fichier;personnage;appareil;ton;texte à dire;contexte']
    .concat(rows.map(r => [r.fichier, r.personnage, r.appareil, r.ton, r.texte, r.contexte].map(cell).join(';'))).join('\n') + '\n';
  const json = JSON.stringify({
    voix: Object.fromEntries(order.map(w => [w, { nom: VOICES[w][0], voix: VOICES[w][1] }])),
    repliques: rows.map(({ who, ...r }) => Object.assign({ voix: who }, r)),
  }, null, 2) + '\n';

  const csvPath = path.join(OUT, 'repliques.csv'), jsonPath = path.join(OUT, 'repliques.json');
  const per = order.map(w => VOICES[w][0] + ' ' + rows.filter(r => r.who === w).length).join(', ');
  if (CHECK) {
    const same = fs.existsSync(csvPath) && fs.readFileSync(csvPath, 'utf8') === csv;
    console.log(same ? `voix : ${rows.length} répliques, à jour` : 'voix : À METTRE À JOUR (node tools/export_voix.js)');
  } else {
    fs.mkdirSync(OUT, { recursive: true });
    fs.writeFileSync(csvPath, csv); fs.writeFileSync(jsonPath, json);
    console.log(`voix : ${rows.length} répliques à enregistrer (${per}) -> voix/repliques.csv, voix/repliques.json`);
  }
  // fichiers audio déjà déposés dans voix/ : présents, manquants, en trop (répliques modifiées ou retirées)
  const have = fs.existsSync(OUT) ? fs.readdirSync(OUT).filter(f => AUDIO.test(f)) : [];
  const names = new Set(rows.map(r => r.fichier)), got = new Set(have.map(f => f.replace(AUDIO, '')));
  const extra = have.filter(f => !names.has(f.replace(AUDIO, '')));
  if (have.length) console.log(`voix : ${rows.filter(r => got.has(r.fichier)).length} / ${rows.length} enregistrées` +
    (extra.length ? ` ; en trop (à supprimer) : ${extra.join(', ')}` : ''));
  if (warn) console.log('PB ' + warn);
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
