// Usage : node web_src/check_placement.js web/index.html
// Vérifie que rien n'est posé dans l'eau ou dans un obstacle, et que chaque trésor est atteignable.
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
    const reachable = (x, y, R) => { for (let a = 0; a < 16; a++) for (const d of [30, 50, 70]) if (d < R) {
        const px = x + Math.cos(a * Math.PI / 8) * d, py = y + Math.sin(a * Math.PI / 8) * d; if (standable(px, py)) return true; } return false; };
    for (const it of items) if (waterAt(it.x, it.y + 22) || !reachable(it.x, it.y + 22, 52)) out.push('objet ' + it.n + ' ' + tile(it.x, it.y));
    for (const d of digs) if (waterAt(d.x, d.y) || !reachable(d.x, d.y + 6, 86)) out.push('trésor ' + tile(d.x, d.y));
    for (const d of dogs) if (!standable(d.x, d.y)) out.push('chien ' + d.kind + ' ' + tile(d.x, d.y));
    if (!standable(P.x, P.y)) out.push('départ de Tecky');
    for (const [x, y] of MAP.signs) if (!reachable(x, y + 30, 95)) out.push('panneau ' + tile(x, y));
    if (!reachable(alice.x, alice.y, 120)) out.push('Alice');
    return out;
  })())`));
  if (bad.length) { console.log('PROBLÈMES :\n  ' + bad.join('\n  ')); process.exitCode = 1; }
  else console.log('placements ok :', r('items.length'), 'objets,', r('digs.length'), 'trésors,', r('dogs.length'), 'chiens, départ, panneaux et Alice');
}, 20);
