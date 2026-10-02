/* Éditeur de carte : la vue (zoom, défilement) et le dessin de la carte avec les vraies tuiles et les sprites du jeu.
   Monde en pixels du jeu (une tuile = 64 px) ; vue : écran = (monde - o) * z. Vue éloignée (z < LOIN) : le sol vient
   d'une image de la carte en petit (16 px par tuile), tenue à jour tuile par tuile ; vue proche : tuiles dessinées. */
(function () {
  const ED = window.ED;
  const TS = 64, P = 16, LOIN = 0.4;
  const V = ED.vue = { z: 0.2, ox: 0, oy: 0, w: 0, h: 0, grille: false, collisions: false, atteint: null,
    calques: {}, verrous: {} };
  let cv, ctx, dpr = 1, atlas, tileset, pending = false;
  const tuiles = new Map();                  // tuiles composées chargées : 'NO,NE,SO,SE' -> Image
  let petit, pctx, petitOv, povx, prev = null, R = 2, zonesImg = null, atteintImg = null;

  V.init = (canvas, imgs) => {
    cv = canvas; ctx = cv.getContext('2d');
    atlas = imgs.atlas; tileset = imgs.tiles;
    R = ED.I.lisiere;
    for (const [k] of ED.CALQUES) V.calques[k] = k !== 'zones';      // (les zones teintent toute la carte : à la demande)
    new ResizeObserver(V.resize).observe(cv.parentElement);
    V.resize();
  };
  V.resize = () => {
    const r = cv.parentElement.getBoundingClientRect();
    dpr = window.devicePixelRatio || 1;
    V.w = r.width; V.h = r.height;
    cv.width = Math.round(r.width * dpr); cv.height = Math.round(r.height * dpr);
    cv.style.width = r.width + 'px'; cv.style.height = r.height + 'px';
    V.demander();
  };
  V.demander = () => { if (!pending) { pending = true; requestAnimationFrame(dessiner); } };
  V.versMonde = (sx, sy) => [V.ox + sx / V.z, V.oy + sy / V.z];
  V.versEcran = (wx, wy) => [(wx - V.ox) * V.z, (wy - V.oy) * V.z];
  V.zoomer = (f, sx, sy) => {
    const [wx, wy] = V.versMonde(sx, sy);
    V.z = Math.min(3, Math.max(0.05, V.z * f));
    V.ox = wx - sx / V.z; V.oy = wy - sy / V.z;
    V.demander();
  };
  V.centrer = (x, y, z) => {                // x, y en tuiles
    if (z) V.z = z;
    V.ox = x * TS - V.w / 2 / V.z; V.oy = y * TS - V.h / 2 / V.z;
    V.demander();
  };
  V.toutVoir = () => {
    const c = ED.c, m = R * TS;
    V.z = Math.min(V.w / (c.w * TS + 2 * m), V.h / (c.h * TS + 2 * m));
    V.ox = -m - (V.w / V.z - c.w * TS - 2 * m) / 2; V.oy = -m - (V.h / V.z - c.h * TS - 2 * m) / 2;
    V.demander();
  };
  V.visible = calque => V.calques[calque] !== false;
  V.actif = calque => V.visible(calque) && !V.verrous[calque];

  /* ------------------------------------------------------------------ le sol */
  const base = () => ED.I.compositeBase;
  function tuileImg(idx) {
    if (idx < base()) return null;
    const key = ED.sol.composites[idx - base()].join(',');
    let im = tuiles.get(key);
    if (!im) {
      im = new Image();
      im.onload = () => { im.ok = true; clearTimeout(V.attente); V.attente = setTimeout(() => V.majSol(true), 60); };   // (une fois pour toutes celles qui arrivent)
      im.src = 'tuile?c=' + encodeURIComponent(key);
      tuiles.set(key, im);
    }
    return im;
  }
  // dessine la tuile idx (index du tileset, ou tuile composée) dans g, en (dx, dy), de côté s
  function tuile(g, idx, dx, dy, s) {
    if (idx >= base()) {
      const im = tuileImg(idx);
      if (im && im.ok) g.drawImage(im, 0, 0, TS, TS, dx, dy, s, s);
      else { g.fillStyle = '#7CC36B'; g.fillRect(dx, dy, s, s); }
    } else if (idx > 0) g.drawImage(tileset, (idx % 16) * TS, Math.floor(idx / 16) * TS, TS, TS, dx, dy, s, s);
  }
  // l'index de la tuile (tx, ty), lisière comprise (-1 : rien)
  let ringIdx = null;
  function idxA(tx, ty) {
    const c = ED.c;
    if (tx >= 0 && ty >= 0 && tx < c.w && ty < c.h) return ED.sol.ground[ty * c.w + tx];
    if (tx < -R || ty < -R || tx >= c.w + R || ty >= c.h + R) return -1;
    return ringIdx[(ty + R) * (c.w + 2 * R) + tx + R];
  }
  // après une modification : l'image en petit, seulement les tuiles qui ont changé (force : tout)
  V.majSol = force => {
    const c = ED.c, s = ED.sol, W = c.w + 2 * R, H = c.h + 2 * R;
    ringIdx = new Int32Array(W * H).fill(-1);
    for (const [tx, ty, idx] of s.ring) ringIdx[(ty + R) * W + tx + R] = idx;
    if (!petit || petit.width !== W * P) {
      petit = document.createElement('canvas'); petit.width = W * P; petit.height = H * P;
      petitOv = document.createElement('canvas'); petitOv.width = W * P; petitOv.height = H * P;
      pctx = petit.getContext('2d'); povx = petitOv.getContext('2d');
      prev = null; force = true;
    }
    // (les tuiles composées changent de rang d'une carte à l'autre : on compare leurs coins)
    const cle = (idx) => idx >= base() ? 'c' + s.composites[idx - base()].join(',') : idx;
    const now = [];
    for (let ty = -R; ty < c.h + R; ty++) for (let tx = -R; tx < c.w + R; tx++) {
      const k = (ty + R) * W + tx + R, idx = idxA(tx, ty), inside = tx >= 0 && ty >= 0 && tx < c.w && ty < c.h;
      const ov = inside ? s.over[ty * c.w + tx] : 0;
      now[k] = cle(idx) + '|' + ov;
      if (!force && prev && prev[k] === now[k]) continue;
      pctx.clearRect((tx + R) * P, (ty + R) * P, P, P);
      if (idx >= 0) tuile(pctx, idx, (tx + R) * P, (ty + R) * P, P);
      povx.clearRect((tx + R) * P, (ty + R) * P, P, P);
      if (ov) tuile(povx, ov, (tx + R) * P, (ty + R) * P, P);
    }
    prev = now;
    V.demander();
  };

  /* ------------------------------------------------------------------ sprites */
  function spr(key, frame, X, Y, flip, alpha) {
    const m = ED.meta[key];
    if (!m) { ctx.fillStyle = '#E24B4B'; ctx.beginPath(); ctx.arc(X, Y - 12, 12, 0, 7); ctx.fill(); return; }
    const f = m.f[(frame || 0) % m.f.length];
    if (alpha != null) ctx.globalAlpha = alpha;
    if (flip) {
      ctx.save(); ctx.translate(X, Y); ctx.scale(-1, 1);
      ctx.drawImage(atlas, f[0], f[1], f[2], f[3], f[4] - m.o[0], f[5] - m.o[1], f[2], f[3]);
      ctx.restore();
    } else ctx.drawImage(atlas, f[0], f[1], f[2], f[3], X - m.o[0] + f[4], Y - m.o[1] + f[5], f[2], f[3]);
    ctx.globalAlpha = 1;
  }
  V.spr = spr;
  // boîte d'un objet, en px du monde [x0, y0, x1, y1]
  V.bornes = o => {
    const X = o.x * TS, Y = o.y * TS;
    if (o.forme === 'rect') return [o.rect[0] * TS, o.rect[1] * TS, o.rect[2] * TS, o.rect[3] * TS];
    if (o.texte !== undefined) { const w = (o.texte.length * 9 + 20) / V.z, h = 16 / V.z; return [X - w / 2, Y - h, X + w / 2, Y + h]; }
    if (o.camera) { const k = 14 / V.z; return [X - k, Y - k, X + k, Y + k]; }
    const m = ED.meta[o.spr];
    if (!m) return [X - 16, Y - 24, X + 16, Y];
    const f = m.f[(o.frame || 0) % m.f.length];
    const x0 = o.flip ? X + m.o[0] - f[4] - f[2] : X - m.o[0] + f[4], y0 = Y - m.o[1] + f[5];
    return [x0, y0, x0 + f[2], y0 + f[3]];
  };

  /* ------------------------------------------------------------------ zones (pré-rendues : 2 cases par tuile) */
  const TEINTES = ['#4FA3E0', '#E0884F', '#9B59D0', '#E04F7A', '#4FC08D', '#D9C24A', '#5A6FD8', '#8D6E63', '#26A69A', '#EF6C00'];
  V.teinte = i => TEINTES[i % TEINTES.length];
  function majZones() {
    const c = ED.c, W = c.w * 2, H = c.h * 2;
    zonesImg = zonesImg || document.createElement('canvas');
    zonesImg.width = W; zonesImg.height = H;
    const g = zonesImg.getContext('2d'), im = g.createImageData(W, H);
    const rgb = TEINTES.map(h => [1, 3, 5].map(k => parseInt(h.slice(k, k + 2), 16)));
    for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
      const z = ED.zoneA((i + 0.5) / 2, (j + 0.5) / 2), [r, gg, b] = rgb[z % rgb.length], k = (j * W + i) * 4;
      im.data[k] = r; im.data[k + 1] = gg; im.data[k + 2] = b; im.data[k + 3] = 70;
    }
    g.putImageData(im, 0, 0);
    ED.zonesMod = false;
  }
  V.setAtteint = a => {
    if (!a) { atteintImg = null; V.demander(); return; }
    atteintImg = document.createElement('canvas'); atteintImg.width = a.w; atteintImg.height = a.h;
    const g = atteintImg.getContext('2d'), im = g.createImageData(a.w, a.h);
    for (let k = 0; k < a.w * a.h; k++) {
      const v = a.data[k];
      if (v === '1') { im.data[4 * k] = 255; im.data[4 * k + 1] = 40; im.data[4 * k + 2] = 40; im.data[4 * k + 3] = 150; }   // praticable, pas atteint
      else if (v === '0') { im.data[4 * k] = 20; im.data[4 * k + 1] = 10; im.data[4 * k + 2] = 40; im.data[4 * k + 3] = 110; }   // obstacle, eau
    }
    g.putImageData(im, 0, 0);
    V.atteintG = a.g;
    V.demander();
  };

  /* ------------------------------------------------------------------ dessin */
  function dessiner() {
    pending = false;
    if (!ED.c || !petit) return;
    const c = ED.c, z = V.z, W = c.w * TS, H = c.h * TS;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = '#1B1D22'; ctx.fillRect(0, 0, cv.width, cv.height);
    ctx.setTransform(dpr * z, 0, 0, dpr * z, -V.ox * z * dpr, -V.oy * z * dpr);
    ctx.imageSmoothingEnabled = true;
    // sol
    const [vx0, vy0] = V.versMonde(0, 0), [vx1, vy1] = V.versMonde(V.w, V.h);
    if (V.visible('terrain')) {
      if (z < LOIN) ctx.drawImage(petit, -R * TS, -R * TS, petit.width / P * TS, petit.height / P * TS);
      else {
        for (let ty = Math.max(-R, Math.floor(vy0 / TS)); ty <= Math.min(c.h + R - 1, Math.floor(vy1 / TS)); ty++)
          for (let tx = Math.max(-R, Math.floor(vx0 / TS)); tx <= Math.min(c.w + R - 1, Math.floor(vx1 / TS)); tx++) {
            const idx = idxA(tx, ty);
            if (idx >= 0) tuile(ctx, idx, tx * TS, ty * TS, TS + 0.5);
          }
      }
    } else { ctx.fillStyle = '#2A2D33'; ctx.fillRect(0, 0, W, H); }
    if (V.visible('details')) {
      if (z < LOIN) ctx.drawImage(petitOv, -R * TS, -R * TS, petitOv.width / P * TS, petitOv.height / P * TS);
      else {
        for (let ty = Math.max(0, Math.floor(vy0 / TS)); ty <= Math.min(c.h - 1, Math.floor(vy1 / TS)); ty++)
          for (let tx = Math.max(0, Math.floor(vx0 / TS)); tx <= Math.min(c.w - 1, Math.floor(vx1 / TS)); tx++) {
            const ov = ED.sol.over[ty * c.w + tx];
            if (ov) tuile(ctx, ov, tx * TS, ty * TS, TS);
          }
      }
    }
    // au-delà du bord : la lisière (assombrie)
    ctx.fillStyle = 'rgba(10,12,16,0.45)';
    ctx.fillRect(-R * TS, -R * TS, W + 2 * R * TS, R * TS); ctx.fillRect(-R * TS, H, W + 2 * R * TS, R * TS);
    ctx.fillRect(-R * TS, 0, R * TS, H); ctx.fillRect(W, 0, R * TS, H);
    ctx.imageSmoothingEnabled = false;
    if (V.visible('zones')) { if (ED.zonesMod || !zonesImg) majZones(); ctx.drawImage(zonesImg, 0, 0, W, H); }
    if (V.visible('calme')) {
      ctx.fillStyle = 'rgba(90,220,130,0.16)';
      for (const [x0, y0, x1, y1] of c.calm) ctx.fillRect(x0 * TS, y0 * TS, (x1 - x0) * TS, (y1 - y0) * TS);
    }
    if (atteintImg) ctx.drawImage(atteintImg, 0, 0, atteintImg.width * V.atteintG, atteintImg.height * V.atteintG);
    ctx.imageSmoothingEnabled = true;
    // les sprites : décors plats d'abord, puis tout le reste trié par y (comme le jeu)
    const vis = o => V.visible(o.calque);
    const marge = 400;
    const dedans = (x, y) => x * TS > vx0 - marge && x * TS < vx1 + marge && y * TS > vy0 - 100 && y * TS < vy1 + marge;
    const plats = [], debout = [];
    for (const o of ED.objs) {
      if (!o.spr || !vis(o) || !dedans(o.x, o.y)) continue;
      (o.flat ? plats : debout).push(o);
    }
    if (V.visible('quetes')) for (const [n, x, y] of ED.deduits(c)) {
      if (!dedans(x, y)) continue;
      const o = { spr: 'decor/' + n, x, y, frame: 0, deduit: true };
      ((ED.I.jeu && ED.I.jeu.flat || []).includes(n) ? plats : debout).push(o);
    }
    debout.sort((a, b) => a.y - b.y);
    for (const o of plats.concat(debout)) spr(o.spr, o.frame, o.x * TS, o.y * TS, o.flip, o.alpha);
    if (V.collisions && ED.I.jeu) dessinerCollisions(c);
    // en coordonnées d'écran : traits fins, étiquettes, poignées
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const E = (x, y) => V.versEcran(x * TS, y * TS);
    // bord de la carte
    { const [a, b] = E(0, 0), [d, e] = E(c.w, c.h); ctx.strokeStyle = 'rgba(255,255,255,0.5)'; ctx.lineWidth = 1; ctx.strokeRect(a, b, d - a, e - b); }
    if (V.grille && z >= 0.3) {
      ctx.strokeStyle = 'rgba(0,0,0,0.18)'; ctx.beginPath();
      for (let x = Math.max(0, Math.floor(vx0 / TS)); x <= Math.min(c.w, vx1 / TS); x++) { const [a] = E(x, 0); ctx.moveTo(a, E(0, 0)[1]); ctx.lineTo(a, E(0, c.h)[1]); }
      for (let y = Math.max(0, Math.floor(vy0 / TS)); y <= Math.min(c.h, vy1 / TS); y++) { const [, b] = E(0, y); ctx.moveTo(E(0, 0)[0], b); ctx.lineTo(E(c.w, 0)[0], b); }
      ctx.stroke();
    }
    // rectangles (zones calmes, enclos, terrain des ballons, voie, passages piétons) et zone choisie
    const zoneSel = [...ED.sel].map(id => ED.byId.get(id)).find(o => o && o.zone !== undefined);
    for (const o of ED.objs) {
      if (o.forme !== 'rect' || !vis(o)) continue;
      if (o.cache && !(zoneSel && zoneSel.zone === o.zone)) continue;
      const [a, b] = E(o.rect[0], o.rect[1]), [d, e] = E(o.rect[2], o.rect[3]);
      ctx.setLineDash(o.type === 'calm' ? [6, 4] : []);
      ctx.strokeStyle = o.type === 'calm' ? 'rgba(90,220,130,0.9)' : o.type === 'zoneRect' ? V.teinte(o.zone) : 'rgba(255,214,90,0.85)';
      ctx.lineWidth = o.type === 'zoneRect' ? 2.5 : 1.5;
      ctx.strokeRect(a, b, d - a, e - b);
      ctx.setLineDash([]);
    }
    // terriers : les deux bouts reliés
    if (V.visible('terriers')) {
      ctx.strokeStyle = 'rgba(255,240,200,0.8)'; ctx.setLineDash([4, 4]); ctx.lineWidth = 1.5;
      for (const t of c.tunnels) { const [a, b] = E(t[0], t[1]), [d, e] = E(t[2], t[3]); ctx.beginPath(); ctx.moveTo(a, b); ctx.lineTo(d, e); ctx.stroke(); }
      ctx.setLineDash([]);
    }
    // caméra de l'écran titre
    if (V.visible('reperes')) {
      const vw = (ED.I.jeu ? ED.I.jeu.vue[0] : 960) / TS, vh = (ED.I.jeu ? ED.I.jeu.vue[1] : 540) / TS;
      const [a, b] = E(c.title[0] - vw / 2, c.title[1] - vh / 2), [d, e] = E(c.title[0] + vw / 2, c.title[1] + vh / 2);
      ctx.strokeStyle = 'rgba(255,255,255,0.75)'; ctx.setLineDash([10, 6]); ctx.lineWidth = 1.5; ctx.strokeRect(a, b, d - a, e - b); ctx.setLineDash([]);
      const [px, py] = E(c.title[0], c.title[1]);
      ctx.beginPath(); ctx.moveTo(px - 10, py); ctx.lineTo(px + 10, py); ctx.moveTo(px, py - 10); ctx.lineTo(px, py + 10); ctx.stroke();
      etiquette('écran titre', px, b + 12, 'rgba(255,255,255,0.85)');
    }
    // étiquettes : zones, rivière ; numéros (chiens, lettres…) ; texte des panneaux de près
    for (const o of ED.objs) {
      if (!vis(o)) continue;
      if (o.texte !== undefined) { const [a, b] = E(o.x, o.y); etiquette(o.texte, a, b, o.zone !== undefined ? V.teinte(o.zone) : '#FFF7E6', true); }
      else if (o.num && z >= 0.25) { const [a, b] = E(o.x, o.y); etiquette('#' + o.i, a, b + 10, '#FFE08A'); }
      else if (o.fin && z >= 0.2) { const [a, b] = E(o.x, o.y); etiquette('fin', a, b + 10, '#FFE08A'); }
      else if (o.type === 'hens' && c.hens[o.i][3] && z >= 0.25) { const [a, b] = E(o.x, o.y); etiquette('quête', a, b + 10, '#FFE08A'); }
    }
    // problèmes de la dernière vérification
    for (const p of ED.problemes || []) {
      if (p.x === undefined) continue;
      const [a, b] = E(p.x, p.y);
      ctx.strokeStyle = p === ED.probleme ? '#FFFFFF' : '#FF4D4D'; ctx.lineWidth = p === ED.probleme ? 3 : 2;
      ctx.beginPath(); ctx.arc(a, b, p === ED.probleme ? 22 : 14, 0, 7); ctx.stroke();
    }
    // sélection
    for (const id of ED.sel) {
      const o = ED.byId.get(id);
      if (!o) continue;
      const [x0, y0, x1, y1] = V.bornes(o), [a, b] = V.versEcran(x0, y0), [d, e] = V.versEcran(x1, y1);
      ctx.strokeStyle = '#FFD84D'; ctx.lineWidth = 2;
      ctx.strokeRect(a - 2, b - 2, d - a + 4, e - b + 4);
      if (o.forme === 'rect') for (const [hx, hy] of V.poignees(o)) { ctx.fillStyle = '#FFD84D'; ctx.fillRect(hx - 5, hy - 5, 10, 10); ctx.strokeStyle = '#000'; ctx.lineWidth = 1; ctx.strokeRect(hx - 5, hy - 5, 10, 10); }
      else {
        const [px, py] = E(o.x, o.y);
        ctx.strokeStyle = '#000'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(px - 6, py); ctx.lineTo(px + 6, py); ctx.moveTo(px, py - 6); ctx.lineTo(px, py + 6); ctx.stroke();
        ctx.strokeStyle = '#FFD84D'; ctx.lineWidth = 1.5; ctx.stroke();
      }
    }
    if (ED.outils && ED.outils.apercu) ED.outils.apercu(ctx, E);
  }
  // poignées d'un rectangle sélectionné, à l'écran : [x, y, bords touchés (g, h, d, b)]
  V.poignees = o => {
    const [x0, y0, x1, y1] = o.rect, out = [];
    const xs = [[x0, 'g'], [(x0 + x1) / 2, ''], [x1, 'd']], ys = [[y0, 'h'], [(y0 + y1) / 2, ''], [y1, 'b']];
    for (const [x, kx] of xs) for (const [y, ky] of ys) {
      if (!kx && !ky) continue;
      if (o.fixe === 'h' && !kx) continue;            // (barrière, passages : seulement en largeur)
      if (o.fixe === 'h' && ky) continue;
      const [a, b] = V.versEcran(x * TS, y * TS);
      out.push([a, b, kx + ky]);
    }
    return out;
  };
  function etiquette(t, x, y, couleur, gras) {
    ctx.font = (gras ? '600 ' : '') + '13px system-ui, sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.lineWidth = 3.5; ctx.strokeStyle = 'rgba(0,0,0,0.75)'; ctx.strokeText(t, x, y);
    ctx.fillStyle = couleur; ctx.fillText(t, x, y);
  }
  function dessinerCollisions(c) {
    const J = ED.I.jeu;
    ctx.fillStyle = 'rgba(255,40,40,0.35)';
    const boite = (n, X, Y, flip) => {
      const f = J.foot[n];
      if (f) flip ? ctx.fillRect(X - f[2], Y + f[1], f[2] - f[0], f[3] - f[1]) : ctx.fillRect(X + f[0], Y + f[1], f[2] - f[0], f[3] - f[1]);
      for (const r of J.rails[n] || []) ctx.fillRect(X + r[0], Y + r[1], r[2] - r[0], r[3] - r[1]);
    };
    for (const [n, x, y] of c.decor) boite(n, x * TS, y * TS);
    for (const [n, x, y] of ED.deduits(c)) boite(n, x * TS, y * TS);
    for (const [x, y] of c.signs) boite('signpost', x * TS, y * TS);
    boite('goal_net', c.goal[0] * TS, c.goal[1] * TS);
    for (const [x, y, f] of c.roadTunnels) boite('tunnel', x * TS, y * TS, f);
  }
})();
