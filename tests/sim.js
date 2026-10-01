const vm = require('vm'), fs = require('fs');
const code = fs.readFileSync(__dirname + '/' + (process.argv[2] || 'game_full.js'), 'utf8');
const noop = () => {};
const ctxStub = new Proxy({}, { get: (t, k) => k === 'measureText' ? (s => ({ width: String(s).length * 18 })) : (k in t ? t[k] : noop), set: (t, k, v) => { t[k] = v; return true; } });
const canvas = () => ({ width: 0, height: 0, style: {}, getContext: () => ctxStub, addEventListener: noop, setPointerCapture: noop,
  getBoundingClientRect: () => ({ left: 0, top: 0 }) });
class Img { set src(v) { this._s = v; this.complete = true; this.naturalWidth = 10; } get src() { return this._s; } }
let rafs = [];
let nodes = 0;
const deep = () => new Proxy(function () {}, { get: (t, k) => k === 'value' ? 0 : deep(), apply: () => { nodes++; return deep(); }, set: () => true });
let now = 0;
class FakeAC { constructor() { this.sampleRate = 44100; this.state = 'running'; this.destination = deep(); }
  get currentTime() { return now; }
  createBuffer(c, l) { return { getChannelData: () => new Float32Array(l) }; }
  createOscillator() { nodes++; return deep(); } createGain() { return deep(); } createBiquadFilter() { return deep(); }
  createBufferSource() { nodes++; return deep(); } createPeriodicWave() { return {}; } resume() {} suspend() {} }
let intervals = [];
const g = {
  console, Math, Promise, setTimeout, JSON, String, Number, Array, Object, performance: { now: () => Date.now() },
  navigator: {}, screen: {}, innerWidth: 1600, innerHeight: 900, devicePixelRatio: 1, addEventListener: noop,
  matchMedia: () => ({ matches: false }), Image: Img, AudioContext: FakeAC, setInterval: (f) => { intervals.push(f); return 1; }, clearInterval: () => { intervals = []; }, requestAnimationFrame: f => rafs.push(f),
  document: { getElementById: canvas, createElement: canvas, fonts: { load: () => Promise.resolve() }, addEventListener: noop, hidden: false },
};
g.window = g;
vm.createContext(g);
vm.runInContext(code, g);
const run = s => vm.runInContext(s, g);
function step(n, setup) { for (let i = 0; i < n; i++) { if (setup) run(setup); now += 1/60; for (const f of intervals) f(); run('update(1/60); render();'); } }
function advanceDialog() { let k = 0; while (run('state') === 'dialog' && k++ < 60) { run('pressed.ok = true'); step(1); } }
const ok = (c, m) => { if (!c) { console.log('ÉCHEC :', m); process.exitCode = 1; } else console.log('ok :', m); };

setTimeout(() => {
  ok(run('state') === 'title', 'écran titre');
  step(30);
  run('audioOn(); pressed.ok = true'); step(1);
  ok(run('Music.on'), 'la musique démarre');
  ok(run('state') === 'dialog', 'dialogue d\'intro');
  advanceDialog();
  ok(run('state') === 'play', 'en jeu après l\'intro');
  run('var saveDogs = dogs; dogs = [];');
  const x0 = run('P.x');
  step(120, 'held.right = true');
  run('dogs = saveDogs;');
  run('held.right = false');
  ok(run('P.x') > x0 + 100, 'Tecky marche vers la droite (' + Math.round(run('P.x') - x0) + ' px)');
  // collisions : essayer de traverser l'étang (8..11, 1..4) par l'ouest
  run('P.x = 7.3*64; P.y = 2.6*64; P.mode="free"');
  step(90, 'held.right = true'); run('held.right = false');
  ok(!run('waterAt(P.x, P.y)'), 'l\'étang bloque Tecky (x = ' + Math.round(run('P.x')/64*10)/10 + ' tuiles)');
  // aboiement
  run('P.x = 5*64; P.y = 9*64; P.mode = "free"; P.cdBark = 0; P.dir = "right"; pressed.bark = true'); step(1);
  ok(run('P.mode') === 'bark', 'aboiement déclenché');
  step(40);
  // combat contre le roquet n°0
  run('var D = dogs[0]; D.mode = "idle"; P.x = D.x - 60; P.y = D.y; P.dir = "right"; P.mode = "free"; P.inv = 5;');
  const hp0 = run('D.hp');
  for (let i = 0; i < 12; i++) { run('if (dogs.includes(D) && D.mode !== "ko") { P.x = D.x - 60; P.y = D.y; P.dir = "right"; } pressed.bite = true'); step(40); }
  ok(run('D.mode') === 'ko' || !run('dogs.includes(D)'), 'le roquet est mis en fuite (PV ' + hp0 + ' -> ' + run('D.hp') + ')');
  step(200);
  ok(!run('dogs.includes(D)'), 'le roquet disparaît après sa fuite');
  ok(run('score') >= 30, 'score après la fuite : ' + run('score'));
  // se faire mordre par un bouledogue
  run('var B = dogs.find(d => d.kind === "bouledogue"); P.x = B.x + 70; P.y = B.y; P.inv = 0; P.hp = 10; P.mode="free";');
  step(300);
  ok(run('P.hp') < 10, 'le bouledogue mord Tecky (PV = ' + run('P.hp') + ')');
  // KO -> musique de défaite -> game over
  run('P.hp = 1; P.inv = 0; P.mode = "free"; P.x = B.x + 70; P.y = B.y;');
  { let k = 0; while (run('P.mode') !== 'ko' && k++ < 600) step(1); }
  ok(run('Music.on') && run('Music.cur') === 'lose', 'KO : la musique de défaite démarre');
  ok(run('LOSESONG.total') === run('WINSONG.total') && run('LOSESONG.bpm') === run('WINSONG.bpm'),
     'même durée que la fanfare (' + run('LOSESONG.total') + ' pas à ' + run('LOSESONG.bpm') + ' BPM)');
  { const n1 = nodes; step(60 * 2); ok(nodes - n1 > 20, 'elle joue des notes (' + (nodes - n1) + ' nœuds en 2 s)'); }
  step(60 * 8);
  ok(run('state') === 'over', 'game over quand la vie tombe à 0 (état : ' + run('state') + ')');
  ok(intervals.length === 0, 'la musique de défaite ne boucle pas (séquenceur arrêté)');
  run('pressed.ok = true'); step(1);
  advanceDialog();
  ok(run('state') === 'play' && run('P.hp') === 6, 'on peut rejouer, avec 3 os sur 5');
  ok(run('Music.on') && run('Music.cur') === 'main', 'le thème reprend');
  // ramasser une balle
  run('var it = items.find(i => i.n === "ball"); P.x = it.x; P.y = it.y + 30; P.mode="free"; var sc = score;');
  step(2);
  ok(run('score') === run('sc') + 20, 'balle ramassée : +20');
  // trésor (chiens écartés : un chien menaçant ferait mordre au lieu de gratter, voir threat.js)
  run('saveDogs = dogs; dogs = [];');
  run('var gd = digs[0]; P.x = gd.x; P.y = gd.y - 20; P.dir = "down"; P.mode = "free"; P.cdBite = 0; P.inv = 9; pressed.bite = true;');
  step(1);
  ok(run('P.mode') === 'dig', 'près du trésor, le bouton fait gratter');
  step(30);
  ok(run('treasures') === 0 && run('fxs.some(f => f.key === "fx/dirt")'), 'Tecky gratte, la terre vole');
  step(40);
  ok(run('treasures') === 1, 'trésor déterré après le grattage');
  advanceDialog();
  run('dogs = saveDogs;');
  // fin : les trois indices font sortir Alice de sa cachette (voir clues.js)
  run('clues = [true, true, true]; revealAlice(); P.x = alice.x - 100; P.y = alice.y + 10; P.mode = "free"; P.inv = 9;');
  step(2);
  ok(run('state') === 'dialog' && run('alice.found'), 'retrouvailles avec Alice');
  ok(run('Music.on') && run('Music.cur') === 'win', 'la fanfare de victoire démarre');
  { const n1 = nodes; step(60 * 3); ok(nodes - n1 > 100, 'la fanfare joue des notes (' + (nodes - n1) + ' nœuds en 3 s)'); }
  run('audioOn()');
  ok(run('Music.cur') === 'win', 'le thème principal ne repart pas pendant la fanfare');
  step(60 * 4);
  ok(run('Music.step') >= run('Music.song.total'), 'la fanfare arrive à son terme (' + run('Music.song.total') + ' pas)');
  advanceDialog();
  ok(run('state') === 'win', 'écran de victoire');
  step(60 * 3);
  ok(intervals.length === 0, 'le séquenceur s\'arrête à la fin de la fanfare (pas de bouclage)');
  const n0 = nodes; run('Music.start()'); step(120);
  ok(nodes > n0 + 20, 'le séquenceur joue des notes (' + (nodes - n0) + ' nœuds en 2 s)');
  step(120);
  // tactile : conversion de coordonnées
  run('offX = 0; offY = 0; scale = 2;');
  ok(JSON.stringify(run('toGui({clientX: 800, clientY: 450})')) === JSON.stringify([800, 450]), 'coordonnées tactiles -> GUI');
  console.log('images de l\'atlas :', Object.keys(run('ATLAS')).length, 'sprites');
}, 50);
setTimeout(() => {
  run('reset(); state = "play"; dialog = null;');
  ok(run('P.hp') === 6 && run('P.hpMax') === 6, 'départ : 3 os sur 3 (PV ' + run('P.hp') + '/' + run('P.hpMax') + ')');
  const give = n => { run('P.x = 5*64; P.y = 7*64; P.mode = "free"; items = [{ n: "' + n + '", x: P.x, y: P.y - 30, t: 0 }];'); step(2); };
  give('bone');
  ok(run('items.length') === 1, 'vie pleine : l\'os reste au sol');
  give('sausage');
  ok(run('P.hpMax') === 8 && run('P.hp') === 8, 'saucisse : 4 os, tous pleins (PV ' + run('P.hp') + '/' + run('P.hpMax') + ')');
  run('P.hp = 3');
  give('bone');
  ok(run('P.hp') === 5 && run('P.hpMax') === 8, 'os : rend un os perdu (PV ' + run('P.hp') + '/' + run('P.hpMax') + ')');
  run('P.hp = 7'); give('bone');
  ok(run('P.hp') === 8, 'os : pas au-delà du maximum courant (PV ' + run('P.hp') + ')');
  for (let i = 0; i < 6; i++) give('sausage');
  ok(run('P.hpMax') === 16, 'plafond à 8 os (PV max ' + run('P.hpMax') + ')');
  run('state = "play"; var cur0 = Music.cur; Music.cur = "main"'); const lm = run('Music.level()');
  run('Music.cur = "win"'); const lw = run('Music.level()'); run('Music.cur = cur0');
  ok(lm < lw, 'thème plus discret que la fanfare de fin (' + lm + ' < ' + lw + ')');
  run('drawHUD()');
  run('pressed = {}; drawDigits("01250", 0, 0, 1, undefined, true); drawDigits("+20", 0, 0, 0.75);');
  ok(true, 'rendu des chiffres (chasse fixe et proportionnelle)');
}, 400);
