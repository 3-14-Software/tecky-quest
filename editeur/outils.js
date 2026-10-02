/* Éditeur de carte : les outils (souris, clavier). Sélection et déplacement (magnétisme : O.pas tuile), pinceau,
   rectangle et remplissage de terrain sur la grille des coins, pipette, détails au sol (une tuile), poser un élément.
   Molette : zoom ; bouton du milieu, ou Espace + glisser : défilement ; clic droit : menu (Essayer ici…). */
(function () {
  const ED = window.ED, TS = 64;
  const O = ED.outils = { outil: 'select', terrain: 'dirt', taille: 1, detail: 'flaque', pas: 0.05,
    poser: { type: 'decor', genre: 'tree' } };
  let cv, V, drag = null, souris = null, espace = false, precedent = 'pinceau';

  // listes de la carte (pour ajouter, dupliquer, supprimer)
  const LISTES = {
    decor: c => c.decor, items: c => c.items, dig: c => c.dig, enemies: c => c.enemies, signs: c => c.signs,
    tunnels: c => c.tunnels, hens: c => c.hens, ducks: c => c.ducks, cows: c => c.cows, critters: c => c.critters,
    butterflies: c => c.butterflies, villagers: c => c.villagers, roadTunnels: c => c.roadTunnels,
    vehicles: c => c.traffic.vehicles, crossings: c => c.traffic.crossings, calm: c => c.calm, landmarks: c => c.landmarks,
  };
  O.LISTES = LISTES;
  const INV = () => Object.fromEntries(Object.entries(ED.c.legende).map(([k, v]) => [v, k]));

  O.init = canvas => {
    cv = canvas; V = ED.vue;
    cv.addEventListener('mousedown', bas);
    addEventListener('mousemove', bouge);
    addEventListener('mouseup', haut);
    cv.addEventListener('wheel', e => { e.preventDefault(); const [sx, sy] = pos(e); V.zoomer(Math.exp(-e.deltaY * 0.0015), sx, sy); }, { passive: false });
    cv.addEventListener('contextmenu', e => { e.preventDefault(); menu(e); });
    cv.addEventListener('mouseleave', () => { souris = null; V.demander(); });
    addEventListener('keydown', clavier);
    addEventListener('keyup', e => { if (e.code === 'Space') { espace = false; cv.style.cursor = ''; } });
  };
  O.choisir = outil => {
    if (outil === 'pipette' && O.outil !== 'pipette') precedent = ['pinceau', 'rect', 'remplir'].includes(O.outil) ? O.outil : 'pinceau';
    O.outil = outil;
    drag = null;
    ED.panneaux.majOutils();
    V.demander();
  };

  /* ------------------------------------------------------------------ coordonnées */
  function pos(e) { const r = cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; }
  const tuiles = (sx, sy) => { const [wx, wy] = V.versMonde(sx, sy); return [wx / TS, wy / TS]; };
  const coin = (x, y) => [Math.min(ED.c.w, Math.max(0, Math.round(x))), Math.min(ED.c.h, Math.max(0, Math.round(y)))];
  const snap = v => Math.round(v / O.pas) * O.pas;
  function coinsPinceau(x, y) {                  // les coins du pinceau (carré de O.taille coins) autour de (x, y)
    const k = O.taille - 1, x0 = Math.round(x - k / 2), y0 = Math.round(y - k / 2), out = [];
    for (let j = y0; j <= y0 + k; j++) for (let i = x0; i <= x0 + k; i++)
      if (i >= 0 && j >= 0 && i <= ED.c.w && j <= ED.c.h) out.push([i, j]);
    return out;
  }

  /* ------------------------------------------------------------------ terrain */
  function peindre(coins, terrain) {
    const ch = INV()[terrain], t = ED.c.terrain;
    const rows = new Map();
    for (const [x, y] of coins) {
      if (!rows.has(y)) rows.set(y, Array.from(t[y]));
      rows.get(y)[x] = ch;
    }
    for (const [y, r] of rows) t[y] = r.join('');
  }
  O.terrainA = (x, y) => { const [i, j] = coin(x, y); return ED.c.legende[ED.c.terrain[j][i]]; };
  function remplir(x, y, terrain) {
    const [i0, j0] = coin(x, y), t = ED.c.terrain, from = t[j0][i0], to = INV()[terrain];
    if (from === to) return;
    const W = ED.c.w + 1, H = ED.c.h + 1, seen = new Uint8Array(W * H), out = [], q = [[i0, j0]];
    seen[j0 * W + i0] = 1;
    while (q.length) {
      const [i, j] = q.pop();
      out.push([i, j]);
      for (const [a, b] of [[i + 1, j], [i - 1, j], [i, j + 1], [i, j - 1]]) {
        if (a < 0 || b < 0 || a >= W || b >= H || seen[b * W + a] || t[b][a] !== from) continue;
        seen[b * W + a] = 1; q.push([a, b]);
      }
    }
    peindre(out, terrain);
  }
  function poserDetail(tx, ty, nom) {
    const d = ED.c.details;
    for (let k = d.length - 1; k >= 0; k--) if (d[k][1] === tx && d[k][2] === ty) d.splice(k, 1);
    if (nom) d.push([nom, tx, ty]);
  }

  /* ------------------------------------------------------------------ objets sous la souris */
  const zoneActive = o => [...ED.sel].some(id => { const s = ED.byId.get(id); return s && s.zone === o.zone; });
  function sous(sx, sy) {
    const [wx, wy] = V.versMonde(sx, sy), m = 6 / V.z, res = [];
    for (const o of ED.objs) {
      if (!V.actif(o.calque)) continue;
      const [x0, y0, x1, y1] = V.bornes(o);
      if (!(wx >= x0 - m && wx <= x1 + m && wy >= y0 - m && wy <= y1 + m)) continue;
      if (o.forme === 'rect') {
        if (o.cache && !zoneActive(o)) continue;
        const petit = (x1 - x0) * V.z < 80 || (y1 - y0) * V.z < 80 || ['crossings', 'track', 'penGate'].includes(o.type);
        const bord = wx < x0 + m || wx > x1 - m || wy < y0 + m || wy > y1 - m;
        if (!petit && !bord) continue;
        res.push([o, petit ? (x1 - x0) * (y1 - y0) : 1e12]);
      } else res.push([o, (x1 - x0) * (y1 - y0)]);
    }
    res.sort((a, b) => a[1] - b[1]);
    return res.map(r => r[0]);
  }
  function poigneeSous(sx, sy) {
    for (const id of ED.sel) {
      const o = ED.byId.get(id);
      if (!o || o.forme !== 'rect' || o.type === 'crossings') continue;
      for (const [hx, hy, bords] of V.poignees(o)) if (Math.abs(hx - sx) < 8 && Math.abs(hy - sy) < 8) return [o, bords];
    }
    return null;
  }
  const dansSelRect = (sx, sy) => {
    const [wx, wy] = V.versMonde(sx, sy);
    return [...ED.sel].map(id => ED.byId.get(id)).find(o => o && o.forme === 'rect' && V.actif(o.calque) && (() => {
      const [x0, y0, x1, y1] = V.bornes(o); return wx >= x0 && wx <= x1 && wy >= y0 && wy <= y1; })());
  };

  /* ------------------------------------------------------------------ déplacer */
  function contraindre(o, x, y) {
    if (o.contrainte === 'centre') return [Math.floor(x) + 0.5, Math.floor(y) + 0.5];
    if (o.contrainte === 'entier') return [Math.round(x), Math.round(y)];
    return [x, y];
  }
  function debutDeplacer(w) {
    const orig = new Map();
    for (const id of ED.sel) { const o = ED.byId.get(id); if (o) orig.set(id, o.forme === 'rect' ? o.rect.slice() : [o.x, o.y]); }
    drag = { mode: 'move', start: w, orig, moved: false };
    ED.debut();
  }
  function deplacer(dx, dy) {
    for (const [id, p] of drag.orig) {
      const o = ED.byId.get(id);
      if (!o) continue;
      if (o.type === 'crossings') o.set(p[0] + Math.round(dx));
      else if (o.forme === 'rect') {
        const q = [p[0] + dx, p[1] + dy, p[2] + dx, p[3] + dy];
        if (o.contrainte === 'xentier') { const r = Math.round(dx); q[0] = p[0] + r; q[2] = p[2] + r; }
        o.setRect(q);
      } else o.set(...contraindre(o, p[0] + dx, p[1] + dy));
    }
    ED.change();
  }
  function redimensionner(o, bords, orig, x, y) {
    const q = orig.slice(), min = 0.25;
    if (bords.includes('g')) q[0] = Math.min(x, q[2] - min);
    if (bords.includes('d')) q[2] = Math.max(x, q[0] + min);
    if (bords.includes('h')) q[1] = Math.min(y, q[3] - min);
    if (bords.includes('b')) q[3] = Math.max(y, q[1] + min);
    if (o.contrainte === 'xentier') { q[0] = Math.round(q[0]); q[2] = Math.max(q[0] + 1, Math.round(q[2])); }
    o.setRect(q);
    ED.change();
  }

  /* ------------------------------------------------------------------ souris */
  function bas(e) {
    cv.focus();
    fermerMenu();
    const [sx, sy] = pos(e), [x, y] = tuiles(sx, sy);
    if (e.button === 1 || (e.button === 0 && espace)) { drag = { mode: 'pan', last: [sx, sy] }; e.preventDefault(); return; }
    if (e.button !== 0) return;
    const out = O.outil;
    if (out === 'select') {
      const h = poigneeSous(sx, sy);
      if (h) { drag = { mode: 'resize', o: h[0], bords: h[1], orig: h[0].rect.slice() }; ED.debut(); return; }
      const cands = sous(sx, sy);
      let o = cands[0];
      if (e.altKey && cands.length > 1) {            // Alt : l'objet suivant à cet endroit
        const k = cands.findIndex(c => ED.sel.has(c.id));
        o = cands[(k + 1) % cands.length];
        ED.sel.clear();
      }
      if (!o) {
        const r = dansSelRect(sx, sy);
        if (r) { debutDeplacer([x, y]); return; }
        if (!e.shiftKey) ED.sel.clear();
        drag = { mode: 'band', a: [sx, sy], b: [sx, sy] };
        ED.panneaux.maj(); V.demander();
        return;
      }
      if (e.shiftKey) { ED.sel.has(o.id) ? ED.sel.delete(o.id) : ED.sel.add(o.id); ED.panneaux.maj(); V.demander(); return; }
      if (!ED.sel.has(o.id)) { ED.sel.clear(); ED.sel.add(o.id); }
      ED.panneaux.maj(); V.demander();
      debutDeplacer([x, y]);
      return;
    }
    if (!V.actif(out === 'details' ? 'details' : 'terrain') && out !== 'poser') { ED.panneaux.message('Le calque est masqué ou verrouillé.'); return; }
    if (out === 'pinceau') { ED.debut(); drag = { mode: 'paint', last: [x, y] }; peindre(coinsPinceau(x, y), O.terrain); ED.change(); return; }
    if (out === 'rect') { drag = { mode: 'rectT', a: coin(x, y), b: coin(x, y) }; return; }
    if (out === 'remplir') { ED.modifier(() => remplir(x, y, O.terrain)); return; }
    if (out === 'pipette') { O.terrain = O.terrainA(x, y); O.choisir(precedent); return; }
    if (out === 'details') {
      const tx = Math.floor(x), ty = Math.floor(y);
      if (tx < 0 || ty < 0 || tx >= ED.c.w || ty >= ED.c.h) return;
      ED.debut(); drag = { mode: 'detail', efface: e.altKey || O.detail === null };
      poserDetail(tx, ty, drag.efface ? null : O.detail); ED.change();
      return;
    }
    if (out === 'poser') O.ajouter(O.poser.type, O.poser.genre, snap(x), snap(y));
  }
  function bouge(e) {
    if (!cv) return;
    const [sx, sy] = pos(e), [x, y] = tuiles(sx, sy);
    const dedans = e.target === cv || drag;
    souris = dedans ? [x, y, sx, sy] : null;
    if (dedans) ED.panneaux.majSouris(x, y);
    if (!drag) { if (dedans && O.outil !== 'select') V.demander(); return; }
    if (drag.mode === 'pan') {
      V.ox -= (sx - drag.last[0]) / V.z; V.oy -= (sy - drag.last[1]) / V.z; drag.last = [sx, sy]; V.demander(); return;
    }
    if (drag.mode === 'move') {
      let dx = x - drag.start[0], dy = y - drag.start[1];
      if (!drag.moved && Math.hypot(dx, dy) * TS * V.z < 4) return;
      drag.moved = true;
      if (!e.altKey) { dx = snap(dx); dy = snap(dy); }
      deplacer(dx, dy);
      return;
    }
    if (drag.mode === 'resize') { redimensionner(drag.o, drag.bords, drag.orig, e.altKey ? x : snap(x), e.altKey ? y : snap(y)); return; }
    if (drag.mode === 'band') { drag.b = [sx, sy]; V.demander(); return; }
    if (drag.mode === 'paint') {
      const [lx, ly] = drag.last, n = Math.ceil(Math.hypot(x - lx, y - ly) * 2) || 1, pts = [];
      for (let k = 1; k <= n; k++) pts.push(...coinsPinceau(lx + (x - lx) * k / n, ly + (y - ly) * k / n));
      drag.last = [x, y];
      peindre(pts, O.terrain); ED.change();
      return;
    }
    if (drag.mode === 'rectT') { drag.b = coin(x, y); V.demander(); return; }
    if (drag.mode === 'detail') {
      const tx = Math.floor(x), ty = Math.floor(y);
      if (tx >= 0 && ty >= 0 && tx < ED.c.w && ty < ED.c.h) { poserDetail(tx, ty, drag.efface ? null : O.detail); ED.change(); }
    }
  }
  function haut() {
    if (!drag) return;
    const d = drag;
    drag = null;
    if (d.mode === 'band') {
      const [ax, ay] = V.versMonde(...d.a), [bx, by] = V.versMonde(...d.b);
      const x0 = Math.min(ax, bx) / TS, x1 = Math.max(ax, bx) / TS, y0 = Math.min(ay, by) / TS, y1 = Math.max(ay, by) / TS;
      if (x1 - x0 > 0.05 || y1 - y0 > 0.05) {
        for (const o of ED.objs) if (o.forme !== 'rect' && V.actif(o.calque) && o.x >= x0 && o.x <= x1 && o.y >= y0 && o.y <= y1) ED.sel.add(o.id);
      }
      ED.panneaux.maj(); V.demander();
      return;
    }
    if (d.mode === 'rectT') {
      const [i0, j0] = d.a, [i1, j1] = d.b, pts = [];
      for (let j = Math.min(j0, j1); j <= Math.max(j0, j1); j++) for (let i = Math.min(i0, i1); i <= Math.max(i0, i1); i++) pts.push([i, j]);
      ED.modifier(() => peindre(pts, O.terrain));
      return;
    }
    if (d.mode !== 'pan') ED.fin();
    ED.panneaux.maj(); V.demander();
  }

  /* ------------------------------------------------------------------ ajouter, dupliquer, supprimer */
  const msg = t => ED.panneaux.message(t);
  O.ajouter = (type, genre, x, y) => {
    const c = ED.c, road = c.traffic.y;
    if (type === 'items' && ED.I.indices.includes(genre) && c.items.some(it => it[0] === genre)) {
      msg('Un seul indice « ' + genre + ' » : déplace celui qui existe.'); return;
    }
    let id = null;
    ED.modifier(c => {
      const L = LISTES[type] && LISTES[type](c), n = L ? L.length : 0;
      if (type === 'dig') L.push([Math.floor(x) + 0.5, Math.floor(y) + 0.5]);
      else if (type === 'signs') L.push([x, y, 'Nouveau panneau.']);
      else if (type === 'tunnels') L.push([x, y, x, ED.r4(y + 1.25)]);
      else if (type === 'hens' || type === 'ducks') L.push([genre, x, y, 0]);
      else if (type === 'vehicles') L.push([genre, Math.abs(y - road - 0.95) < Math.abs(y - road - 2.95) ? 0 : 1, x]);
      else if (type === 'crossings') L.push(Math.round(x));
      else if (type === 'calm') L.push([ED.r4(x - 2), ED.r4(y - 2), ED.r4(x + 2), ED.r4(y + 2)]);
      else if (type === 'landmarks') L.push({ label: 'Repère', at: [x, y] });
      else L.push([genre, x, y]);
      id = type + '/' + n + (type === 'tunnels' ? '/a' : '');
    });
    ED.sel.clear(); if (id) ED.sel.add(id);
    ED.panneaux.maj(); V.demander();
  };
  const FIXES = ['letters', 'balls', 'toys', 'babies'];
  O.supprimer = () => {
    const objs = [...ED.sel].map(id => ED.byId.get(id)).filter(Boolean);
    if (!objs.length) return;
    const refus = objs.find(o => !(LISTES[o.type] || o.type === 'zoneRect') || (o.type === 'items' && ED.I.indices.includes(o.genre)));
    if (refus) {
      msg(FIXES.includes(refus.type) ? `${ED.NOMS[refus.type]} : il en faut exactement ${ED.I.tailles[refus.type]}, on peut seulement les déplacer.`
        : refus.indice ? 'Un indice d’Alice ne se supprime pas : déplace-le.' : `« ${ED.NOMS[refus.type] || refus.type} » ne se supprime pas : déplace-le.`);
      return;
    }
    // listes indexées par la sauvegarde : retirer au milieu décale les numéros des suivants
    const milieu = objs.filter(o => ED.I.indexees.includes(o.type) && o.i < LISTES[o.type](ED.c).length - objs.filter(p => p.type === o.type).length);
    if (milieu.length && !confirm('Supprimer au milieu de la liste « ' + ED.NOMS[milieu[0].type] + ' » décale les numéros des suivants : '
      + 'une partie sauvegardée en cours les retrouverait mélangés (sinon, augmenter SAVE_V dans game.js). Supprimer quand même ?')) return;
    for (const o of objs.filter(o => o.type === 'zoneRect')) {
      if (ED.c.zones[o.i].rects.length - objs.filter(p => p.type === 'zoneRect' && p.i === o.i).length < 1) { msg('Une zone garde au moins un rectangle.'); return; }
    }
    ED.modifier(c => {
      const par = new Map();
      for (const o of objs) {
        const k = o.type === 'zoneRect' ? 'zoneRect/' + o.i : o.type;
        if (!par.has(k)) par.set(k, new Set());
        par.get(k).add(o.type === 'zoneRect' ? o.j : o.i);
      }
      for (const [k, idx] of par) {
        const L = k.startsWith('zoneRect/') ? c.zones[+k.split('/')[1]].rects : LISTES[k](c);
        for (const i of [...idx].sort((a, b) => b - a)) L.splice(i, 1);
      }
    });
    ED.sel.clear(); ED.panneaux.maj();
  };
  O.dupliquer = () => {
    const objs = [...ED.sel].map(id => ED.byId.get(id)).filter(o => o && LISTES[o.type]);
    if (!objs.length) { msg('Rien à dupliquer (personnages, repères et listes fixes ne se dupliquent pas).'); return; }
    if (objs.some(o => o.indice)) { msg('Un indice d’Alice ne se duplique pas.'); return; }
    const neufs = [], vus = new Set();
    ED.modifier(c => {
      for (const o of objs) {
        const L = LISTES[o.type](c), k = o.type + o.i;
        if (vus.has(k)) continue;
        vus.add(k);
        const e = JSON.parse(JSON.stringify(L[o.i]));
        if (o.type === 'dig') { e[0] += 1; e[1] += 1; }
        else if (o.type === 'signs') { e[0] += 0.5; e[1] += 0.5; }
        else if (o.type === 'tunnels') { e[0] += 1; e[2] += 1; }
        else if (o.type === 'vehicles') e[2] += 3;
        else if (o.type === 'crossings') { L.push(e + 3); neufs.push(o.type + '/' + (L.length - 1)); continue; }
        else if (o.type === 'calm') e.forEach((v, k) => { e[k] = v + 1; });
        else if (o.type === 'landmarks') { e.at[0] += 1; e.at[1] += 1; }
        else { e[1] = ED.r4(e[1] + 0.5); e[2] = ED.r4(e[2] + 0.5); }
        L.push(e);
        neufs.push(o.type + '/' + (L.length - 1) + (o.type === 'tunnels' ? '/a' : ''));
      }
    });
    ED.sel = new Set(neufs); ED.panneaux.maj(); V.demander();
  };
  function pousser(dx, dy) {
    if (!ED.sel.size) return;
    debutDeplacer([0, 0]);
    deplacer(dx, dy);
    drag = null;
    ED.fin(); ED.panneaux.maj();
  }

  /* ------------------------------------------------------------------ clavier */
  const TOUCHES = { v: 'select', b: 'pinceau', r: 'rect', g: 'remplir', i: 'pipette', d: 'details', p: 'poser' };
  function clavier(e) {
    const t = e.target;           // (dans un champ de saisie, les touches sont pour lui ; pas pour une case à cocher)
    if (t && (t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || (t.tagName === 'INPUT' && !['checkbox', 'range', 'button'].includes(t.type)))) {
      if (e.key === 'Escape') t.blur();
      return;
    }
    const k = e.key.toLowerCase(), ctrl = e.ctrlKey || e.metaKey;
    if (ctrl && k === 's') { e.preventDefault(); ED.panneaux.enregistrer(); return; }
    if (ctrl && k === 'z') { e.preventDefault(); e.shiftKey ? ED.retablir() : ED.annuler(); return; }
    if (ctrl && k === 'y') { e.preventDefault(); ED.retablir(); return; }
    if (ctrl && k === 'd') { e.preventDefault(); O.dupliquer(); return; }
    if (ctrl && k === 'a') { e.preventDefault(); for (const o of ED.objs) if (o.forme !== 'rect' && V.actif(o.calque)) ED.sel.add(o.id); ED.panneaux.maj(); V.demander(); return; }
    if (ctrl) return;
    if (e.code === 'Space') { espace = true; cv.style.cursor = 'grab'; e.preventDefault(); return; }
    if (k === 'delete' || k === 'backspace') { e.preventDefault(); O.supprimer(); return; }
    if (k === 'escape') { fermerMenu(); drag = null; ED.sel.clear(); ED.panneaux.maj(); V.demander(); return; }
    if (k.startsWith('arrow')) {
      e.preventDefault();
      const s = O.pas * (e.shiftKey ? 10 : 1);
      pousser(k === 'arrowleft' ? -s : k === 'arrowright' ? s : 0, k === 'arrowup' ? -s : k === 'arrowdown' ? s : 0);
      return;
    }
    if (k === '[' || k === ']') { O.taille = Math.max(1, Math.min(8, O.taille + (k === ']' ? 1 : -1))); ED.panneaux.majOutils(); V.demander(); return; }
    if (k === 'f') { V.toutVoir(); return; }
    if (k === 'h') { V.grille = !V.grille; ED.panneaux.majOutils(); V.demander(); return; }
    if (TOUCHES[k]) O.choisir(TOUCHES[k]);
  }

  /* ------------------------------------------------------------------ menu du clic droit */
  const menuEl = () => document.getElementById('menu');
  function fermerMenu() { const m = menuEl(); if (m) m.hidden = true; }
  function menu(e) {
    const [sx, sy] = pos(e), [x, y] = tuiles(sx, sy), o = sous(sx, sy)[0];
    const items = [
      ['Essayer ici (aventure)', () => ED.panneaux.essayer(x, y, 'aventure')],
      ['Essayer ici (balade)', () => ED.panneaux.essayer(x, y, 'balade')],
      ['Centrer ici', () => V.centrer(x, y)],
    ];
    if (o) {
      if (!ED.sel.has(o.id)) { ED.sel.clear(); ED.sel.add(o.id); ED.panneaux.maj(); V.demander(); }
      items.push(null, ['Dupliquer (Ctrl+D)', O.dupliquer], ['Supprimer (Suppr)', O.supprimer]);
    }
    const m = menuEl();
    m.innerHTML = '';
    for (const it of items) {
      if (!it) { m.appendChild(document.createElement('hr')); continue; }
      const b = document.createElement('button');
      b.textContent = it[0];
      b.onclick = () => { fermerMenu(); it[1](); };
      m.appendChild(b);
    }
    m.hidden = false;
    m.style.left = Math.min(e.clientX, innerWidth - 220) + 'px'; m.style.top = Math.min(e.clientY, innerHeight - 160) + 'px';
  }
  addEventListener('mousedown', e => { if (menuEl() && !menuEl().contains(e.target)) fermerMenu(); });

  /* ------------------------------------------------------------------ aperçu (dessiné par la vue, à l'écran) */
  O.apercu = (ctx, E) => {
    if (drag && drag.mode === 'band') {
      const [a, b] = drag.a, [c, d] = drag.b;
      ctx.fillStyle = 'rgba(255,216,77,0.12)'; ctx.fillRect(a, b, c - a, d - b);
      ctx.strokeStyle = '#FFD84D'; ctx.lineWidth = 1; ctx.strokeRect(a, b, c - a, d - b);
    }
    if (!souris) return;
    const [x, y] = souris, out = O.outil;
    const couleur = ED.panneaux.couleurTerrain(O.terrain);
    const carre = (i, j) => { const [a, b] = E(i, j); const s = Math.max(4, Math.min(12, 10 * V.z)); ctx.fillRect(a - s / 2, b - s / 2, s, s); ctx.strokeRect(a - s / 2, b - s / 2, s, s); };
    ctx.strokeStyle = '#000'; ctx.lineWidth = 1;
    if (out === 'pinceau') { ctx.fillStyle = couleur; for (const [i, j] of coinsPinceau(x, y)) carre(i, j); }
    else if (out === 'remplir' || out === 'pipette') { ctx.fillStyle = out === 'pipette' ? '#FFF' : couleur; carre(...coin(x, y)); }
    else if (out === 'rect') {
      const [i0, j0] = drag && drag.mode === 'rectT' ? drag.a : coin(x, y), [i1, j1] = drag && drag.mode === 'rectT' ? drag.b : coin(x, y);
      const [a, b] = E(Math.min(i0, i1), Math.min(j0, j1)), [c, d] = E(Math.max(i0, i1), Math.max(j0, j1));
      ctx.fillStyle = couleur + '66'; ctx.fillRect(a - 4, b - 4, c - a + 8, d - b + 8);
      ctx.strokeStyle = '#FFF'; ctx.strokeRect(a - 4, b - 4, c - a + 8, d - b + 8);
    } else if (out === 'details') {
      const tx = Math.floor(x), ty = Math.floor(y), [a, b] = E(tx, ty), [c, d] = E(tx + 1, ty + 1);
      ctx.strokeStyle = O.detail === null ? '#FF6B6B' : '#FFF'; ctx.lineWidth = 2; ctx.strokeRect(a, b, c - a, d - b);
    } else if (out === 'poser') {
      const p = O.poser, sx = snap(x), sy = snap(y);
      const [k, f] = ED.I.sprites[p.type] ? ED.sprite(p.type, p.genre, 0) : [null, 0];
      if (k) {
        const [a, b] = E(sx, sy);
        ctx.save(); ctx.setTransform(devicePixelRatio * V.z, 0, 0, devicePixelRatio * V.z, a * devicePixelRatio, b * devicePixelRatio);
        V.spr(k, f, 0, 0, false, 0.6); ctx.restore();
      } else { ctx.fillStyle = '#FFD84D'; carre(sx, sy); }
    }
  };
})();
