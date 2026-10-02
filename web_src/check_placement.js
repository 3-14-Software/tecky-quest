// Usage : node web_src/check_placement.js web/index.html
// Vérifie que rien n'est posé dans l'eau ou dans un obstacle, que tout (objets, indices, trésors, panneaux,
// Alice) est atteignable à pied depuis la niche de Tecky, que deux actions différentes ne se recouvrent pas (règle
// d'espacement) et que les personnages vivent en zone calme, sans chien.
const vm = require('vm'), fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const code = html.slice(html.indexOf('<script>') + 8, html.lastIndexOf('</script>'));
const noop = () => {};
const ctxStub = new Proxy({}, { get: (t, k) => k === 'measureText' ? (() => ({ width: 10 })) :
  k === 'createRadialGradient' || k === 'createLinearGradient' ? (() => ({ addColorStop: noop })) : noop });
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
    for (const c of critters) if (!standable(c.x, c.y) || !reachable(c.x, c.y, 120)) out.push(c.kind + ' ' + tile(c.x, c.y));
    for (const d of ducks) if (!duckWater(d, d.x, d.y)) out.push(d.kind + ' hors de l’eau ' + tile(d.x, d.y));
    if (!standable(P.x, P.y)) out.push('départ de Tecky');
    for (const [x, y] of MAP.signs) if (!reachable(x, y + 30, 95)) out.push('panneau ' + tile(x, y));
    if (!reachable(alice.x, alice.y, 120)) out.push('Alice');
    if (!reachable(farmer.x, farmer.y, 150)) out.push('fermier');
    if (!reachable(postman.x, postman.y, 150)) out.push('facteur');
    if (!reachable(neighbor.x, neighbor.y, 150)) out.push('voisine');
    if (!reachable(leon.x, leon.y, 150)) out.push('Léon');
    // ballons de Léon : posés sur un sol praticable, atteignables, hors du filet ; l'ouverture du filet est atteignable
    for (const b of balls) if (!standable(b.x, b.y) || !reachable(b.x, b.y, 80) || ballBlocked(b, b.x, b.y)) out.push('ballon ' + tile(b.x, b.y));
    for (const b of balls) { checkGoal(b); if (b.inNet) out.push('ballon déjà dans le filet ' + tile(b.x, b.y)); }
    if (!reachable(MAP.goal[0], MAP.goal[1] + 60, 60)) out.push('ouverture du filet');
    for (const l of letters) if (waterAt(l.x, l.y + 20) || !reachable(l.x, l.y + 20, 52)) out.push('lettre ' + tile(l.x, l.y));
    if (!standable(pompon.x, pompon.y) || !reachable(pompon.x, pompon.y, 120)) out.push('Pompon ' + tile(pompon.x, pompon.y));
    // terriers : les deux bouts praticables et atteignables à pied (le terrier est un raccourci, pas un passage obligé)
    for (const [ax, ay, bx, by] of MAP.tunnels)
      for (const [x, y] of [[ax, ay], [bx, by]]) if (!standable(x, y) || !reachable(x, y, 40)) out.push('terrier ' + tile(x, y));
    // quête des poules : la barrière de l'enclos est atteignable, et les poules de la quête démarrent dehors
    { const [gx, gy] = gatePoint(); if (!reachable(gx, gy + 40, 60)) out.push('barrière de l’enclos'); }
    for (const h of hens) if (h.quest && h.x > penRect()[0] && h.x < penRect()[2] && h.y > penRect()[1] && h.y < penRect()[3]) out.push('poule déjà dans l’enclos ' + tile(h.x, h.y));
    // règle d'espacement : deux actions différentes ne se recouvrent jamais (avec une marge), sinon le joueur en déclenche
    // une en voulant l'autre (ramasser un indice en parlant à quelqu'un, déterrer un os en passant sous un grillage…)
    const MARGIN = 60, A = [];        // [genre, nom, x, y, portée]
    for (const n of npcList()) A.push(['personnage', n.kind, n.x, n.y, NPC.talk]);
    for (const s of MAP.signs) A.push(['panneau', 'panneau', s[0], s[1] + 30, REACH.sign]);
    for (const g of digs) A.push(['os doré', 'trésor', g.x, g.y + 6, REACH.dig]);
    MAP.tunnels.forEach(([ax, ay, bx, by]) => { A.push(['terrier', 'terrier', ax, ay, TUNNEL.reach]); A.push(['terrier', 'terrier', bx, by, TUNNEL.reach]); });
    for (const it of items) if (CLUES.includes(it.n)) A.push(['indice', it.n, it.x, it.y + 32, REACH.item]);
    for (const l of letters) A.push(['lettre', 'lettre', l.x, l.y + 20, POST.pick]);
    A.push(['chat', 'Pompon', pompon.x, pompon.y, CAT.find]);
    for (let i = 0; i < A.length; i++) for (let j = i + 1; j < A.length; j++) {
      const a = A[i], b = A[j];
      if (a[0] === b[0] && a[0] !== 'personnage') continue;
      if (dist(a[2], a[3], b[2], b[3]) < a[4] + b[4] + MARGIN)
        out.push('trop proches : ' + a[0] + ' ' + tile(a[2], a[3]) + ' et ' + b[0] + ' ' + tile(b[2], b[3]) + ' (deux actions au même endroit)');
    }
    // rien à ramasser à portée de parole d'un personnage
    for (const n of npcList()) for (const it of items)
      if (dist(n.x, n.y, it.x, it.y + 32) < NPC.talk + REACH.item) out.push('objet ' + it.n + ' ' + tile(it.x, it.y) + ' à portée de parole de ' + n.kind);
    // les personnages vivent en zone calme, et aucun chien n'y habite
    for (const n of npcList()) if (!calmAt(n.x, n.y)) out.push('personnage hors zone calme : ' + n.kind + ' ' + tile(n.x, n.y));
    for (const d of dogs) if (calmAt(d.hx, d.hy)) out.push('chien en zone calme : ' + d.kind + ' ' + tile(d.hx, d.hy));
    return out;
  })())`));
  if (bad.length) { console.log('PROBLÈMES :\n  ' + bad.join('\n  ')); process.exitCode = 1; }
  else console.log('placements ok :', r('items.length'), 'objets,', r('digs.length'), 'trésors,', r('dogs.length'), 'chiens,', r('hens.length'), 'poules,', r('ducks.length'), 'canards,', r('letters.length'), 'lettres, départ, panneaux, terriers, personnages, Pompon et Alice');
}, 20);
