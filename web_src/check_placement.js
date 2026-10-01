// Usage : node web_src/check_placement.js web/index.html
// Vérifie que rien n'est posé dans l'eau ou dans un obstacle, et que tout (objets, indices, trésors, panneaux,
// Alice) est atteignable à pied depuis la niche de Tecky.
const vm = require('vm'), fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const code = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));
const noop = () => {};
const ctxStub = new Proxy({}, { get: (t, k) => k === 'measureText' ? (() => ({ width: 10 })) : noop });
const canvas = () => ({ width: 0, height: 0, style: {}, getContext: () => ctxStub, addEventListener: noop, getBoundingClientRect: () => ({ left: 0, top: 0 }) });
class Img { set src(v) { this.complete = true; this.naturalWidth = 1; } }
const g = { console, Math, Promise, setTimeout, JSON, String, Number, Array, Object, navigator: {}, screen: {},
  performance: { now: () => 0 }, innerWidth: 1600, innerHeight: 900, devicePixelRatio: 1, addEventListener: noop,
  matchMedia: () => ({ matches: false }), Image: Img, requestAnimationFrame: noop, setInterval: noop, clearInterval: noop,
  document: { getElementById: canvas, createElement: canvas, fonts: { load: () => Promise.resolve() }, addEventListener: noop } };
g.window = g; vm.createContext(g); vm.runInContext(code, g);
setTimeout(() => {
  const r = s => vm.runInContext(s, g);
  const bad = JSON.parse(r(`JSON.stringify((() => {
    const out = [];
    const tile = (x, y) => '(' + (x / 64).toFixed(1) + ', ' + (y / 64).toFixed(1) + ')';
    // un point du sol est "praticable" si Tecky peut s'y tenir
    const standable = (x, y) => !blockedFeet(x, y, 16);
    // parcours en largeur depuis la niche, sur une grille de 16 px : ce que Tecky peut atteindre en marchant
    const G = 16, GW_ = Math.floor(MAP.w * TS / G), GH_ = Math.floor(MAP.h * TS / G);
    const seen = new Uint8Array(GW_ * GH_), ok = new Uint8Array(GW_ * GH_);
    for (let j = 0; j < GH_; j++) for (let i = 0; i < GW_; i++) ok[j * GW_ + i] = standable(i * G + G / 2, j * G + G / 2) ? 1 : 0;
    const q = [Math.floor(P.y / G) * GW_ + Math.floor(P.x / G)];
    seen[q[0]] = 1;
    while (q.length) {
      const c = q.pop(), i = c % GW_, j = (c - i) / GW_;
      for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const ni = i + di, nj = j + dj, n = nj * GW_ + ni;
        if (ni < 0 || nj < 0 || ni >= GW_ || nj >= GH_ || seen[n] || !ok[n]) continue;
        seen[n] = 1; q.push(n);
      }
    }
    const reachable = (x, y, R) => {
      for (let j = Math.max(0, Math.floor((y - R) / G)); j <= Math.min(GH_ - 1, Math.floor((y + R) / G)); j++)
        for (let i = Math.max(0, Math.floor((x - R) / G)); i <= Math.min(GW_ - 1, Math.floor((x + R) / G)); i++)
          if (seen[j * GW_ + i] && dist(i * G + G / 2, j * G + G / 2, x, y) < R - 8) return true;
      return false;
    };
    for (const it of items) if (waterAt(it.x, it.y + 22) || !reachable(it.x, it.y + 22, 52)) out.push('objet ' + it.n + ' ' + tile(it.x, it.y));
    for (const d of digs) if (waterAt(d.x, d.y) || !reachable(d.x, d.y + 6, 86)) out.push('trésor ' + tile(d.x, d.y));
    for (const d of dogs) if (!standable(d.x, d.y)) out.push('chien ' + d.kind + ' ' + tile(d.x, d.y));
    for (const h of hens) if (!standable(h.x, h.y)) out.push('poule ' + tile(h.x, h.y));
    if (!standable(P.x, P.y)) out.push('départ de Tecky');
    for (const [x, y] of MAP.signs) if (!reachable(x, y + 30, 95)) out.push('panneau ' + tile(x, y));
    if (!reachable(alice.x, alice.y, 120)) out.push('Alice');
    return out;
  })())`));
  if (bad.length) { console.log('PROBLÈMES :\n  ' + bad.join('\n  ')); process.exitCode = 1; }
  else console.log('placements ok :', r('items.length'), 'objets,', r('digs.length'), 'trésors,', r('dogs.length'), 'chiens,', r('hens.length'), 'poules, départ, panneaux et Alice');
}, 20);
