/* Éditeur de carte : les panneaux de la page (outils, calques, palette, inspecteur, problèmes, barre d'état) et le
   démarrage. Enregistrer (Ctrl+S) écrit carte.json ; Vérifier construit le jeu et relève les problèmes de placement ;
   Essayer ici (clic droit sur la carte) ouvre le jeu avec Tecky à cet endroit. */
(function () {
  const ED = window.ED, $ = id => document.getElementById(id);
  const P = ED.panneaux = {};
  let O, V;
  const h = (tag, attrs = {}, ...kids) => {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'on') for (const [ev, f] of Object.entries(v)) e.addEventListener(ev, f);
      else if (k === 'class') e.className = v;
      else if (v === false || v == null) continue;
      else if (k.startsWith('data-') || !(k in e)) e.setAttribute(k, v === true ? '' : v);
      else e[k] = v;                                   // (value, checked, selected, disabled, title…)
    }
    for (const k of kids.flat()) if (k != null) e.append(k instanceof Node ? k : document.createTextNode(String(k)));
    return e;
  };

  const TERRAINS = { grass: 'Herbe', dirt: 'Terre (chemin)', road: 'Route', paving: 'Pavés', concrete: 'Béton',
    sidewalk: 'Trottoir', water: 'Eau', field: 'Champ labouré', forest: 'Sous-bois' };
  const COULEURS = { grass: '#7CC36B', dirt: '#D9B47A', road: '#5B5E68', paving: '#D4CBB8', concrete: '#A9ACB2',
    sidewalk: '#CDD0D5', water: '#5DADE2', field: '#B07A45', forest: '#5A9A4E' };
  P.couleurTerrain = t => COULEURS[t] || '#FFFFFF';
  const OUTILS = [['select', 'Sélection', 'V'], ['pinceau', 'Pinceau', 'B'], ['rect', 'Rectangle', 'R'], ['remplir', 'Remplir', 'G'],
    ['pipette', 'Pipette', 'I'], ['details', 'Détails au sol', 'D'], ['poser', 'Poser', 'P']];
  // ce que l'outil « Poser » sait ajouter
  const POSABLES = ['decor', 'items', 'dig', 'enemies', 'signs', 'tunnels', 'hens', 'ducks', 'cows', 'critters', 'butterflies',
    'villagers', 'vehicles', 'crossings', 'calm', 'landmarks'];
  const AIDE = {
    select: 'Clic : choisir (Maj : ajouter ; Alt : l’objet suivant au même endroit). Glisser : déplacer, ou encadrer pour en choisir plusieurs. Flèches : petits pas (Maj : ×10). Suppr, Ctrl+D (dupliquer), Ctrl+A.',
    pinceau: 'Peint les coins de la grille (une tuile se dessine d’après ses quatre coins). [ et ] : taille du pinceau.',
    rect: 'Glisser : remplit un rectangle de coins.',
    remplir: 'Clic : remplit la surface du même terrain.',
    pipette: 'Clic : reprend le terrain d’un coin.',
    details: 'Clic ou glisser : pose le détail choisi sur la tuile. Alt (ou la gomme) : efface.',
    poser: 'Clic : ajoute l’élément choisi (à la fin de sa liste). Magnétisme : le pas de la barre d’outils.',
  };

  /* ------------------------------------------------------------------ vignettes */
  function vignette(key, frame = 0, taille = 44) {
    const c = h('canvas', { width: taille, height: taille, class: 'vig' });
    const m = ED.meta[key];
    if (!m) return c;
    const f = m.f[frame % m.f.length], g = c.getContext('2d'), s = Math.min(1, (taille - 4) / Math.max(f[2], f[3]));
    g.imageSmoothingQuality = 'high';
    g.drawImage(P.atlas, f[0], f[1], f[2], f[3], (taille - f[2] * s) / 2, (taille - f[3] * s) / 2, f[2] * s, f[3] * s);
    return c;
  }
  function vignetteTuile(idx, taille = 34) {
    const c = h('canvas', { width: taille, height: taille, class: 'vig' }), g = c.getContext('2d');
    g.fillStyle = '#7CC36B'; g.fillRect(0, 0, taille, taille);
    g.drawImage(P.tiles, (idx % 16) * 64, Math.floor(idx / 16) * 64, 64, 64, 0, 0, taille, taille);
    return c;
  }
  const tuilePleine = t => t === 'grass' ? 1 : (1 + ED.I.pairs.findIndex(([u, l]) => u === t && l === 'grass')) * ED.I.cols + 15;

  /* ------------------------------------------------------------------ barre d'outils */
  function construireBarre() {
    const b = $('outils');
    b.innerHTML = '';
    for (const [k, nom, t] of OUTILS) b.append(h('button', { class: 'outil', 'data-o': k, title: nom + ' (' + t + ')', on: { click: () => O.choisir(k) } }, nom));
    $('annuler').onclick = () => ED.annuler();
    $('retablir').onclick = () => ED.retablir();
    $('enregistrer').onclick = () => P.enregistrer();
    $('verifier').onclick = () => P.verifier();
    $('toutvoir').onclick = () => V.toutVoir();
    $('pas').onchange = e => { O.pas = +e.target.value; };
    $('grille').onchange = e => { V.grille = e.target.checked; V.demander(); };
    $('collisions').onchange = e => { V.collisions = e.target.checked; V.demander(); };
    $('acces').onchange = e => { V.setAtteint(e.target.checked ? P.atteint : null); };
  }
  P.majOutils = () => {
    for (const b of document.querySelectorAll('.outil')) b.classList.toggle('actif', b.dataset.o === O.outil);
    $('grille').checked = V.grille;
    $('aide').textContent = AIDE[O.outil];
    construirePalette();
    $('vue').dataset.outil = O.outil;
  };
  P.majEtat = () => {
    $('etat').textContent = ED.modifie ? '● Non enregistrée' : 'Enregistrée';
    $('etat').classList.toggle('modifie', ED.modifie);
    $('annuler').disabled = !ED.peutAnnuler();
    $('retablir').disabled = !ED.peutRetablir();
    document.title = (ED.modifie ? '● ' : '') + 'Carte — Tecky Quest';
  };

  /* ------------------------------------------------------------------ calques */
  const CLE = 'tecky-editeur-calques';
  function construireCalques() {
    let pref = {};
    try { pref = JSON.parse(localStorage.getItem(CLE) || '{}'); } catch (e) { /* (rien) */ }
    const ul = $('calques');
    ul.innerHTML = '';
    for (const [k, nom] of ED.CALQUES) {
      if (pref[k]) { V.calques[k] = pref[k].v !== false; V.verrous[k] = !!pref[k].l; }
      const n = ED.objs.filter(o => o.calque === k).length;
      const vu = h('input', { type: 'checkbox', checked: V.calques[k], title: 'Afficher', on: { change: e => { V.calques[k] = e.target.checked; sauver(); V.demander(); } } });
      const ver = h('button', { class: 'verrou' + (V.verrous[k] ? ' on' : ''), title: 'Verrouiller (on ne peut plus le choisir à la souris)',
        on: { click: e => { V.verrous[k] = !V.verrous[k]; e.target.classList.toggle('on', V.verrous[k]); sauver(); } } }, V.verrous[k] ? 'verrouillé' : 'libre');
      ul.append(h('li', {}, h('label', {}, vu, ' ', nom, n ? h('span', { class: 'n' }, ' ' + n) : null), ver));
    }
    function sauver() {
      const o = {};
      for (const [k] of ED.CALQUES) o[k] = { v: V.calques[k], l: V.verrous[k] };
      try { localStorage.setItem(CLE, JSON.stringify(o)); } catch (e) { /* (rien) */ }
      for (const b of ul.querySelectorAll('.verrou')) b.textContent = b.classList.contains('on') ? 'verrouillé' : 'libre';
    }
  }

  /* ------------------------------------------------------------------ palette */
  function construirePalette() {
    const p = $('palette');
    p.innerHTML = '';
    const out = O.outil;
    if (['pinceau', 'rect', 'remplir', 'pipette'].includes(out)) {
      p.append(h('h3', {}, 'Terrain'));
      const grid = h('div', { class: 'grille-pal' });
      for (const t of Object.keys(TERRAINS)) {
        grid.append(h('button', { class: 'pal' + (O.terrain === t ? ' actif' : ''), title: TERRAINS[t], on: { click: () => { O.terrain = t; if (out === 'pipette') O.choisir('pinceau'); else construirePalette(); } } },
          vignetteTuile(tuilePleine(t)), h('span', {}, TERRAINS[t])));
      }
      p.append(grid);
      if (out === 'pinceau') {
        p.append(h('h3', {}, 'Taille du pinceau'), h('div', { class: 'ligne' },
          h('input', { type: 'range', min: 1, max: 8, value: O.taille, on: { input: e => { O.taille = +e.target.value; $('taille').textContent = O.taille; } } }),
          h('span', { id: 'taille' }, O.taille)));
      }
      p.append(h('p', { class: 'note' }, 'Un chemin qui arrive sur la route s’arrête à son bord : sinon il mord sur la chaussée, sous le passage piéton.'));
    } else if (out === 'details') {
      p.append(h('h3', {}, 'Détail au sol'));
      const grid = h('div', { class: 'grille-pal' });
      const ov = ED.I.overlayRow * ED.I.cols;
      grid.append(h('button', { class: 'pal' + (O.detail === null ? ' actif' : ''), on: { click: () => { O.detail = null; construirePalette(); } } }, h('span', { class: 'gomme' }, '⌫'), h('span', {}, 'Gomme')));
      for (const n of ED.I.genres.details) {
        const i = ED.I.overlays.indexOf(n);
        grid.append(h('button', { class: 'pal' + (O.detail === n ? ' actif' : ''), title: n, on: { click: () => { O.detail = n; construirePalette(); } } }, vignetteTuile(ov + i), h('span', {}, n)));
      }
      p.append(grid, h('p', { class: 'note' }, 'Les massifs de « fleurs » sont aussi des perchoirs pour les papillons. Les traces de pattes viennent des os dorés.'));
    } else if (out === 'poser') {
      p.append(h('h3', {}, 'Poser'));
      const sel = h('select', { on: { change: e => { O.poser.type = e.target.value; O.poser.genre = genres(O.poser.type)[0] || null; construirePalette(); } } },
        POSABLES.map(t => h('option', { value: t, selected: O.poser.type === t }, ED.NOMS[t])));
      p.append(sel);
      const gs = genres(O.poser.type);
      if (gs.length) {
        const grid = h('div', { class: 'grille-pal' });
        for (const g of gs) {
          const [k, f] = ED.I.sprites[O.poser.type] ? ED.sprite(O.poser.type, g, 0) : ['vehicle/' + g, 0];
          grid.append(h('button', { class: 'pal' + (O.poser.genre === g ? ' actif' : ''), title: g, on: { click: () => { O.poser.genre = g; construirePalette(); } } }, vignette(k, f), h('span', {}, g)));
        }
        p.append(grid);
      }
      p.append(h('p', { class: 'note' }, 'Un nouvel élément va à la fin de sa liste : les sauvegardes retrouvent les autres par leur numéro.'));
    } else {
      p.append(h('h3', {}, 'Affichage'), h('p', { class: 'note' },
        'Molette : zoom. Bouton du milieu, ou Espace + glisser : déplacer la vue. F : toute la carte. H : grille. Clic droit : Essayer ici.'));
    }
  }
  const genres = t => t === 'vehicles' ? ED.I.genres.vehicles : (ED.I.genres[t] || []).filter(g => t !== 'items' || !ED.I.indices.includes(g) || !ED.c.items.some(it => it[0] === g));

  /* ------------------------------------------------------------------ inspecteur */
  const champ = (label, input, note) => h('div', { class: 'champ' }, h('label', {}, label), input, note ? h('div', { class: 'note' }, note) : null);
  const nombre = (v, onset, step = 0.05) => h('input', { type: 'number', step, value: ED.r4(v), on: { change: e => { const x = parseFloat(e.target.value); if (!isNaN(x)) onset(x); } } });
  const texte = (v, onset) => h('input', { type: 'text', value: v, on: { change: e => onset(e.target.value) } });
  const choix = (opts, v, onset) => h('select', { on: { change: e => onset(e.target.value) } }, opts.map(([k, t]) => h('option', { value: k, selected: String(k) === String(v) }, t)));
  const mod = fn => ED.modifier(fn);

  P.maj = () => {
    construireInspecteur();
    if (P._nCalques !== ED.objs.length) { P._nCalques = ED.objs.length; construireCalques(); }
  };
  function construireInspecteur() {
    const d = $('inspecteur');
    if (d.contains(document.activeElement) && document.activeElement.tagName !== 'BUTTON') return;   // (en pleine saisie)
    d.innerHTML = '';
    const objs = [...ED.sel].map(id => ED.byId.get(id)).filter(Boolean);
    if (!objs.length) {
      const c = ED.c;
      d.append(h('h2', {}, 'Carte'), h('p', { class: 'note' }, `${c.w} × ${c.h} tuiles · ${c.decor.length} décors · ${c.items.length} objets · ${c.enemies.length} chiens · ${c.dig.length} os dorés · ${c.signs.length} panneaux`),
        h('p', { class: 'note' }, AIDE[O.outil]));
      return;
    }
    if (objs.length > 1) {
      const par = {};
      for (const o of objs) par[ED.NOMS[o.type] || o.type] = (par[ED.NOMS[o.type] || o.type] || 0) + 1;
      d.append(h('h2', {}, objs.length + ' éléments'), h('ul', { class: 'compte' }, Object.entries(par).map(([k, n]) => h('li', {}, n + ' × ' + k))),
        h('div', { class: 'ligne' }, h('button', { on: { click: O.dupliquer } }, 'Dupliquer'), h('button', { class: 'danger', on: { click: O.supprimer } }, 'Supprimer')));
      return;
    }
    const o = objs[0], c = ED.c, I = ED.I;
    const titre = (ED.NOMS[o.type] || o.type) + (o.i !== undefined && O.LISTES[o.type] ? ' #' + o.i : '') + (o.type === 'tunnels' ? (o.bout ? ' (bout B)' : ' (bout A)') : '');
    d.append(h('h2', {}, titre));
    if (o.spr && ED.meta[o.spr]) d.append(vignette(o.spr, o.frame, 64));
    if (I.indexees.includes(o.type)) d.append(h('p', { class: 'note' }, 'La sauvegarde retient cet élément par son numéro : en ajouter à la fin, ne pas en retirer au milieu.'));
    if (I.tailles[o.type]) d.append(h('p', { class: 'note' }, `Il y en a exactement ${I.tailles[o.type]} : on peut seulement les déplacer.`));
    if (o.indice) d.append(h('p', { class: 'note' }, 'Indice d’Alice (un seul de chaque) : la flèche du HUD y mène.'));
    // genre
    const L = O.LISTES[o.type];
    if (o.genre && L && (I.genres[o.type] || o.type === 'vehicles') && !o.indice) {
      const gs = o.type === 'vehicles' ? I.genres.vehicles : I.genres[o.type].filter(g => !I.indices.includes(g));
      d.append(champ('Genre', choix(gs.map(g => [g, g]), o.genre, v => mod(c => { const e = L(c)[o.i]; if (o.type === 'vehicles') e[0] = v; else e[0] = v; }))));
    }
    // position
    if (o.forme === 'rect') {
      if (o.type === 'crossings') d.append(champ('x (première des deux tuiles)', nombre(o.rect[0], v => mod(c => { c.traffic.crossings[o.i] = Math.round(v); }), 1)));
      else if (o.type === 'penGate') d.append(champ('Ouverture : de x', nombre(c.penGate[0], v => mod(c => { c.penGate[0] = Math.round(v); }), 1)), champ('à x', nombre(c.penGate[1], v => mod(c => { c.penGate[1] = Math.round(v); }), 1)));
      else if (o.type === 'track') d.append(champ('Heurtoir ouest (x)', nombre(c.track[0], v => mod(c => { c.track[0] = v; }))), champ('Heurtoir est (x)', nombre(c.track[1], v => mod(c => { c.track[1] = v; }))), champ('y des rails', nombre(c.track[2], v => mod(c => { c.track[2] = v; }))));
      else {
        const r = o.rect;
        d.append(h('div', { class: 'quatre' }, ['x0', 'y0', 'x1', 'y1'].map((n, k) => champ(n, nombre(r[k], v => mod(() => { const q = r.slice(); q[k] = v; o.setRect(q); }), o.contrainte === 'xentier' && k % 2 === 0 ? 1 : 0.05)))));
      }
    } else if (o.set) {
      d.append(h('div', { class: 'deux' }, champ('x', nombre(o.x, v => mod(() => o.set(v, o.y)))), champ('y', nombre(o.y, v => mod(() => o.set(o.x, v))))));
    }
    // propres à chaque type
    if (o.type === 'signs') {
      const t = c.signs[o.i][2];
      const ta = h('textarea', { rows: 4, value: t, on: { change: e => mod(c => { c.signs[o.i][2] = e.target.value.trim() || 'Panneau.'; }) } });
      d.append(champ('Texte du panneau', ta, t.length > 110 ? `${t.length} caractères : vérifie qu’il tient en 3 lignes de dialogue.` : `${t.length} caractères. Après une modification : régénérer les voix.`));
    }
    if (o.type === 'hens') d.append(champ('', h('label', { class: 'case' }, h('input', { type: 'checkbox', checked: !!c.hens[o.i][3], on: { change: e => mod(c => { c.hens[o.i][3] = e.target.checked ? 1 : 0; }) } }), ' Poule de la quête du fermier (échappée de l’enclos)')));
    if (o.type === 'ducks') d.append(champ('Famille', nombre(c.ducks[o.i][3], v => mod(c => { c.ducks[o.i][3] = Math.max(0, Math.round(v)); }), 1), '0 : seul ; même numéro : la cane et ses canetons, qui la suivent en file.'));
    if (o.type === 'vehicles') d.append(champ('Voie', choix([[0, '0 : en haut, vers l’ouest'], [1, '1 : en bas, vers l’est']], c.traffic.vehicles[o.i][1], v => mod(c => { c.traffic.vehicles[o.i][1] = +v; }))));
    if (o.type === 'roadTunnels') d.append(champ('', h('label', { class: 'case' }, h('input', { type: 'checkbox', checked: c.roadTunnels[o.i][2], on: { change: e => mod(c => { c.roadTunnels[o.i][2] = e.target.checked; }) } }), ' En miroir (bord est)')));
    if (o.type === 'landmarks') d.append(champ('Étiquette', texte(c.landmarks[o.i].label, v => mod(c => { c.landmarks[o.i].label = v || 'Repère'; }))));
    if (o.zone !== undefined) inspecteurZone(d, o.zone, o);
    if (o.type === 'tunnels') d.append(h('p', { class: 'note' }, 'Un terrier relie ses deux bouts (raccourci sous un grillage) : les deux doivent être atteignables à pied.'));
    if (o.type === 'title') d.append(h('p', { class: 'note' }, 'Centre de la caméra de l’écran titre (le cadre pointillé).'));
    if (o.type === 'start') d.append(h('p', { class: 'note' }, 'Tout doit être atteignable à pied depuis ici (Vérifier). Le premier roquet doit rester assez loin.'));
    const boutons = h('div', { class: 'ligne' });
    if (L || o.type === 'zoneRect') {
      if (L && !o.indice) boutons.append(h('button', { on: { click: O.dupliquer } }, 'Dupliquer'));
      if (!o.indice) boutons.append(h('button', { class: 'danger', on: { click: O.supprimer } }, 'Supprimer'));
    }
    boutons.append(h('button', { on: { click: () => V.centrer(o.forme === 'rect' ? (o.rect[0] + o.rect[2]) / 2 : o.x, o.forme === 'rect' ? (o.rect[1] + o.rect[3]) / 2 : o.y) } }, 'Centrer'));
    d.append(boutons);
  }
  function inspecteurZone(d, i, o) {
    const c = ED.c, z = c.zones[i], I = ED.I;
    d.append(h('h3', { style: 'color:' + V.teinte(i) }, 'Zone « ' + z.id + ' »'),
      champ('Bandeau à l’arrivée', texte(z.name, v => mod(c => { c.zones[i].name = v || z.id; }))),
      champ('Étiquette de la carte', texte(z.label, v => mod(c => { c.zones[i].label = v || z.id; }))),
      champ('Musique et ambiance', choix(I.musiques.map(m => [m, m + (m === z.id ? ' (la sienne)' : '')]), z.music || z.id,
        v => mod(c => { if (v === c.zones[i].id) delete c.zones[i].music; else c.zones[i].music = v; }))),
      h('p', { class: 'note' }, 'Priorité : la première zone de la liste dont un rectangle contient le point. Un bord posé sur le bord de la carte n’a pas de limite. La dernière couvre toute la carte.'));
    const ul = h('ul', { class: 'rects' });
    z.rects.forEach((r, j) => ul.append(h('li', { class: o.type === 'zoneRect' && o.j === j ? 'actif' : '' },
      h('button', { class: 'lien', on: { click: () => { ED.sel = new Set(['zoneRect/' + i + '/' + j]); P.maj(); V.demander(); } } }, `[${r.map(v => ED.r4(v)).join(', ')}]`))));
    d.append(champ('Rectangles', ul));
    d.append(h('div', { class: 'ligne' },
      h('button', { on: { click: () => { mod(c => { const [x, y] = [V.versMonde(V.w / 2, V.h / 2)[0] / 64, V.versMonde(V.w / 2, V.h / 2)[1] / 64]; c.zones[i].rects.push([ED.r4(x - 3), ED.r4(y - 3), ED.r4(x + 3), ED.r4(y + 3)]); }); ED.sel = new Set(['zoneRect/' + i + '/' + (ED.c.zones[i].rects.length - 1)]); P.maj(); } } }, 'Ajouter un rectangle'),
      h('button', { disabled: i === 0, on: { click: () => deplacerZone(i, -1) } }, 'Avant'),
      h('button', { disabled: i >= c.zones.length - 2, on: { click: () => deplacerZone(i, 1) } }, 'Après')));
  }
  function deplacerZone(i, d) {
    mod(c => { const [z] = c.zones.splice(i, 1); c.zones.splice(i + d, 0, z); });
    ED.sel = new Set(['zones/' + (i + d)]); P.maj(); V.demander();
  }

  /* ------------------------------------------------------------------ barre d'état, messages */
  P.majSouris = (x, y) => {
    const c = ED.c;
    if (x < 0 || y < 0 || x > c.w || y > c.h) { $('souris').textContent = `(${x.toFixed(2)}, ${y.toFixed(2)}) hors de la carte`; return; }
    const z = c.zones[ED.zoneA(x, y)];
    $('souris').textContent = `x ${x.toFixed(2)}  y ${y.toFixed(2)} · tuile ${Math.floor(x)}, ${Math.floor(y)} · coin ${Math.round(x)}, ${Math.round(y)} : ${TERRAINS[O.terrainA(x, y)]} · zone ${z.id}${ED.calmeA(x, y) ? ' (calme)' : ''} · zoom ${Math.round(V.z * 100)} %`;
  };
  let msgT = null;
  P.message = (t, duree = 4500) => {
    const m = $('message');
    m.textContent = t; m.hidden = false;
    clearTimeout(msgT); msgT = setTimeout(() => { m.hidden = true; }, duree);
  };
  function occupe(t) { $('occupe').hidden = !t; $('occupe-texte').textContent = t || ''; }

  /* ------------------------------------------------------------------ enregistrer, vérifier, essayer */
  P.enregistrer = async () => {
    const r = await ED.enregistrer();
    if (r.ok) { P.message(r.change ? 'carte.json enregistré.' : 'Rien de nouveau : carte.json était déjà à jour.'); return true; }
    if (r.code === 409) {
      if (confirm(r.erreur + '\n\nRecharger la carte du disque maintenant ? (les modifications de cette page seront perdues)')) location.reload();
      return false;
    }
    afficherProblemes({ titre: 'Enregistrement refusé : ' + r.erreur, liste: (r.details || []).map(t => ({ texte: t })) });
    return false;
  };
  P.verifier = async () => {
    if (ED.modifie && !(await P.enregistrer())) return;
    occupe('Construction du jeu et vérification des placements…');
    try {
      const r = await fetch('verifier', { method: 'POST' }).then(r => r.json());
      if (r.jeu) { ED.I.jeu = r.jeu; ED.change(); }
      P.atteint = r.atteint;
      $('acces').disabled = !r.atteint;
      if ($('acces').checked) V.setAtteint(r.atteint);
      afficherProblemes({ verif: r });
    } catch (e) {
      afficherProblemes({ titre: 'Vérification impossible : ' + e.message, liste: [] });
    } finally { occupe(null); }
  };
  P.essayer = async (x, y, mode) => {
    const w = window.open('about:blank', '_blank');         // (tout de suite : après une attente, le navigateur le bloquerait)
    if (ED.modifie && !(await P.enregistrer())) { if (w) w.close(); return; }
    occupe('Construction du jeu…');
    try {
      const r = await fetch('essai', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ x, y, mode }) }).then(r => r.json());
      if (r.ok) { if (w) w.location = r.url; else window.open(r.url, '_blank'); }
      else { if (w) w.close(); afficherProblemes({ titre: 'La construction du jeu a échoué', sortie: r.sortie }); }
    } finally { occupe(null); }
  };
  async function voix() {
    occupe('Mise à jour de la liste des voix…');
    try {
      const r = await fetch('voix', { method: 'POST' }).then(r => r.json());
      P.message(r.ok ? 'Liste des voix mise à jour (voix/repliques.csv, .json).' : 'Échec : ' + r.sortie, 8000);
      if (r.ok) $('voix-pb') && $('voix-pb').remove();
    } finally { occupe(null); }
  }
  function afficherProblemes({ verif, titre, liste, sortie }) {
    const d = $('problemes');
    d.innerHTML = '';
    if (verif) {
      liste = verif.problemes;
      ED.problemes = liste.filter(p => p.x !== undefined);
      titre = !verif.construit ? 'La construction du jeu a échoué' : liste.length ? liste.length + ' problème' + (liste.length > 1 ? 's' : '') : 'Placements ok';
      if (!verif.construit) sortie = verif.construction;
    } else ED.problemes = (liste || []).filter(p => p.x !== undefined);
    d.append(h('h2', { class: liste && liste.length || sortie ? 'pb' : 'ok' }, titre));
    if (verif && verif.resume) d.append(h('p', { class: 'note' }, verif.resume));
    const ul = h('ul', { class: 'pbs' });
    for (const p of liste || []) {
      ul.append(h('li', {}, p.x !== undefined ? h('button', { class: 'lien', on: { click: () => { ED.probleme = p; V.centrer(p.x, p.y, Math.max(V.z, 0.6)); } } }, p.texte) : p.texte));
    }
    d.append(ul);
    if (verif && !verif.voixAJour) {
      d.append(h('div', { id: 'voix-pb', class: 'avert' }, h('p', {}, 'La liste des voix n’est plus à jour (texte d’un panneau modifié ?).'),
        h('button', { on: { click: voix } }, 'Mettre à jour les voix')));
    }
    if (sortie) d.append(h('pre', {}, sortie));
    ED.redessiner();
  }

  /* ------------------------------------------------------------------ démarrage */
  const image = src => new Promise((ok, ko) => { const i = new Image(); i.onload = () => ok(i); i.onerror = ko; i.src = src; });
  async function demarrer() {
    occupe('Chargement…');
    const [I, meta] = await Promise.all([fetch('infos.json').then(r => r.json()), fetch('atlas.json').then(r => r.json())]);
    ED.I = I; ED.meta = meta;
    const [atlas, tiles] = await Promise.all([image('atlas.png'), image('tiles.png')]);
    P.atlas = atlas; P.tiles = tiles;
    await ED.charger();
    O = ED.outils; V = ED.vue;
    const cv = $('carte');
    V.init(cv, { atlas, tiles });
    O.init(cv);
    construireBarre();
    ED.change();
    construireCalques();
    P.majOutils(); P.majEtat();
    V.toutVoir();
    occupe(null);
    addEventListener('beforeunload', e => { if (ED.modifie) { e.preventDefault(); e.returnValue = ''; } });
  }
  demarrer().catch(e => { occupe(null); document.body.prepend(h('pre', { class: 'fatal' }, 'Démarrage impossible : ' + e.stack)); });
})();
