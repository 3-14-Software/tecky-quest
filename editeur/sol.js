/* Éditeur de carte : le sol, calculé comme pack_web.build_map() (même résultat, vérifié par tests/editeur_sol.js).
   Chaque tuile se dessine d'après ses quatre coins (NO, NE, SO, SE) : tiles.resolve() choisit le terrain du dessus et
   celui du dessous, ou une tuile composée (trois terrains, ou deux sans paire dans le tileset). Les variantes (herbe,
   terre, route…) dépendent de la position (hash3), jamais de l'ordre de la carte. I : /infos.json (editeur.py). */
(function (root) {
  const ED = root.ED = root.ED || {};

  // même calcul que hash3 de game.js et de pack_web.py
  function hash3(a, b, c) {
    let h = Math.imul(a, 374761393) ^ Math.imul(b, 668265263) ^ Math.imul(c, 1274126177);
    h = Math.imul(h ^ (h >>> 13), 1103515245);
    return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
  }

  function prep(I) {
    if (I._prio) return;
    I._prio = Object.fromEntries(I.priority.map((t, i) => [t, i]));
    I._pairs = new Map(I.pairs.map(([u, l], i) => [u + '/' + l, i]));
    I._ter = I.legende;
  }
  const kindsOf = (cs, I) => [...new Set(cs)].sort((a, b) => I._prio[a] - I._prio[b]);
  // tiles.resolve : (dessus, dessous, bits)
  function resolve(cs, I) {
    const kinds = kindsOf(cs, I);
    if (kinds.length === 1) return [kinds[0], kinds[0], 15];
    const up = kinds[kinds.length - 1], others = cs.filter(c => c !== up);
    const count = c => others.filter(o => o === c).length;
    let lo = null;
    for (const c of new Set(others)) {
      if (lo === null || count(c) > count(lo) || (count(c) === count(lo) && I._prio[c] < I._prio[lo])) lo = c;
    }
    if (!I._pairs.has(up + '/' + lo)) lo = 'grass';
    let bits = 0;
    cs.forEach((c, i) => { if (c === up) bits |= 1 << i; });
    return [up, lo, bits];
  }
  // tiles.needs_composite
  function needsComposite(cs, I) {
    const k = kindsOf(cs, I);
    return k.length >= 3 || (k.length === 2 && !I._pairs.has(k[1] + '/' + k[0]));
  }
  const tileIndex = (up, bits, lo, I) => (1 + I._pairs.get(up + '/' + lo)) * I.cols + bits;

  // grille des coins [y][x] -> terrain
  function grille(c) {
    const L = c.legende;
    return c.terrain.map(s => Array.from(s, ch => L[ch]));
  }

  /* carte -> { ground, over, ring, composites } comme MAP (ground : index du tileset ; une tuile composée a l'index
     compositeBase + son rang dans composites, dans l'ordre où le balayage la rencontre, carte puis lisière) */
  function sol(c, I) {
    prep(I);
    const W = c.w, H = c.h, g = grille(c), comp = [], compIdx = new Map();
    const pick = (cs, tx, ty) => {
      const [up, lo, bits] = resolve(cs, I);
      if (needsComposite(cs, I)) {
        const k = cs.join(',');
        if (!compIdx.has(k)) { compIdx.set(k, comp.length); comp.push(cs); }
        return I.compositeBase + compIdx.get(k);
      }
      if (up === 'grass') return I.grassVariants[Math.floor(hash3(tx, ty, 1) * I.grassVariants.length)];
      let idx = tileIndex(up, bits, bits === 15 ? 'grass' : lo, I);
      const v = I.fullVariants[up];
      if (bits === 15 && v && hash3(tx, ty, 2) < 0.35) idx = v[Math.floor(hash3(tx, ty, 3) * v.length)];
      return idx;
    };
    const ground = new Array(W * H);
    for (let ty = 0; ty < H; ty++) for (let tx = 0; tx < W; tx++)
      ground[ty * W + tx] = pick([g[ty][tx], g[ty][tx + 1], g[ty + 1][tx], g[ty + 1][tx + 1]], tx, ty);
    const road = c.traffic.y, full = tileIndex('road', 15, 'grass', I), mark = tx => (tx % 2 === 0 ? 5 : full);
    for (let tx = 0; tx < W; tx++) ground[(road + 1) * W + tx] = mark(tx);
    // lisière : I.lisiere tuiles autour de la carte, coins ramenés sur le bord
    const R = I.lisiere, ring = [];
    const at = (x, y) => g[Math.min(Math.max(y, 0), H)][Math.min(Math.max(x, 0), W)];
    for (let ty = -R; ty < H + R; ty++) for (let tx = -R; tx < W + R; tx++) {
      if (tx >= 0 && tx < W && ty >= 0 && ty < H) continue;
      const idx = pick([at(tx, ty), at(tx + 1, ty), at(tx, ty + 1), at(tx + 1, ty + 1)], tx, ty);
      ring.push([tx, ty, ty === road + 1 ? mark(tx) : idx]);
    }
    for (const tx of c.traffic.crossings) for (const ty of [road, road + 1, road + 2]) ground[ty * W + tx] = ground[ty * W + tx + 1] = 7;
    const over = new Array(W * H).fill(0), ov = I.overlayRow * I.cols;
    const OV = Object.fromEntries(I.overlays.map((n, i) => [n, i]));
    for (const [n, tx, ty] of c.details) if (n in OV) over[ty * W + tx] = ov + OV[n];
    for (const [x, y] of c.dig) over[Math.floor(y) * W + Math.floor(x)] = ov + OV['traces de pattes'];
    return { ground, over, ring, composites: comp };
  }

  ED.hash3 = hash3;
  ED.resolve = resolve;
  ED.needsComposite = needsComposite;
  ED.grille = grille;
  ED.calculerSol = sol;
  if (typeof module !== 'undefined') module.exports = ED;
})(typeof window !== 'undefined' ? window : globalThis);
