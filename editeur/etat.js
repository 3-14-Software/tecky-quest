/* Éditeur de carte : l'état (la carte, l'historique, l'enregistrement) et les « objets » de la carte, c'est-à-dire tout
   ce qui se sélectionne, se déplace ou se redimensionne : décors, objets, chiens, personnages, bêtes, panneaux,
   terriers, rectangles des zones… Positions en tuiles, comme dans carte.json. */
(function () {
  const ED = window.ED;
  ED.c = null;          // la carte (carte.json)
  ED.I = null;          // /infos.json (editeur.py)
  ED.meta = null;       // /atlas.json
  ED.etag = null;       // version de carte.json sur le disque (enregistrement refusé si elle a changé)
  ED.modifie = false;
  ED.sel = new Set();   // ids des objets sélectionnés
  ED.objs = [];         // les objets de la carte (rebâtis à chaque modification)
  ED.byId = new Map();
  ED.sol = null;        // { ground, over, ring, composites }

  /* ------------------------------------------------------------------ historique */
  const hist = [], futur = [];
  let avant = null, sauve = null;          // sauve : la carte telle qu'enregistrée (modifiée = différente)
  ED.debut = () => { if (avant === null) avant = JSON.stringify(ED.c); };
  ED.fin = () => {
    if (avant === null) return;
    const now = JSON.stringify(ED.c);
    if (now !== avant) {
      hist.push(avant);
      if (hist.length > 300) hist.shift();
      futur.length = 0;
      ED.modifie = now !== sauve;
    }
    avant = null;
    ED.majEtat();
  };
  // une modification d'un coup : fn(c) change la carte
  ED.modifier = fn => { ED.debut(); fn(ED.c); ED.fin(); ED.change(); };
  function remet(json) { ED.c = JSON.parse(json); ED.modifie = json !== sauve; ED.change(); ED.majEtat(); }
  ED.annuler = () => { ED.fin(); if (hist.length) { futur.push(JSON.stringify(ED.c)); remet(hist.pop()); } };
  ED.retablir = () => { ED.fin(); if (futur.length) { hist.push(JSON.stringify(ED.c)); remet(futur.pop()); } };
  ED.peutAnnuler = () => hist.length > 0;
  ED.peutRetablir = () => futur.length > 0;

  // après chaque modification : le sol, les objets, la sélection (ids disparus retirés), l'affichage
  ED.change = () => {
    ED.sol = ED.solDe(ED.c);
    ED.objs = objets(ED.c);
    ED.byId = new Map(ED.objs.map(o => [o.id, o]));
    for (const id of [...ED.sel]) if (!ED.byId.has(id)) ED.sel.delete(id);
    ED.zonesMod = true;
    if (ED.vue) ED.vue.majSol();
    if (ED.panneaux) ED.panneaux.maj();
    ED.redessiner();
  };
  ED.solDe = c => ED.calculerSol(c, ED.I);
  ED.redessiner = () => { if (ED.vue) ED.vue.demander(); };
  ED.majEtat = () => { if (ED.panneaux) ED.panneaux.majEtat(); };

  /* ------------------------------------------------------------------ chargement, enregistrement */
  ED.charger = async () => {
    const r = await fetch('carte.json', { cache: 'no-store' });
    ED.etag = r.headers.get('ETag');
    ED.c = await r.json();
    sauve = JSON.stringify(ED.c);
    hist.length = futur.length = 0;
    ED.modifie = false;
    ED.sel.clear();
  };
  ED.enregistrer = async () => {
    ED.fin();
    const corps = JSON.stringify(ED.c);
    const r = await fetch('carte.json', { method: 'PUT', headers: { 'If-Match': ED.etag || '', 'Content-Type': 'application/json' },
      body: corps });
    const j = await r.json().catch(() => ({}));
    if (r.ok) {
      ED.etag = r.headers.get('ETag');
      sauve = corps;
      ED.modifie = JSON.stringify(ED.c) !== sauve;
      ED.majEtat();
      return { ok: true, change: j.change };
    }
    return { ok: false, code: r.status, erreur: j.erreur || ('erreur ' + r.status), details: j.details || [] };
  };

  /* ------------------------------------------------------------------ objets */
  const r4 = v => Math.round(v * 1e4) / 1e4;
  ED.r4 = r4;
  // les calques (l'ordre de la liste des calques)
  ED.CALQUES = [
    ['terrain', 'Terrain'], ['details', 'Détails au sol'], ['decors', 'Décors'], ['objets', 'Objets'],
    ['tresors', 'Os dorés (trésors)'], ['chiens', 'Chiens'], ['personnages', 'Personnages'], ['quetes', 'Quêtes'],
    ['animaux', 'Animaux'], ['panneaux', 'Panneaux'], ['terriers', 'Terriers'], ['route', 'Route'],
    ['calme', 'Zones calmes'], ['zones', 'Zones (musique, bandeau)'], ['reperes', 'Repères (départ, Alice, titre, fin)'],
  ];
  // noms des types (inspecteur, palette)
  ED.NOMS = {
    decor: 'Décor', items: 'Objet', dig: 'Os doré (trésor)', enemies: 'Chien', signs: 'Panneau', tunnels: 'Terrier',
    hens: 'Poule', ducks: 'Canard', cows: 'Vache', critters: 'Petite bête', butterflies: 'Papillon', villagers: 'Villageois',
    start: 'Départ de Tecky', alice: 'Alice (cachée dans la cabane)', title: 'Caméra de l’écran titre',
    endingAlice: 'Fin : Alice devant la niche', endingTecky: 'Fin : Tecky à ses pieds',
    farmer: 'Gaston, le fermier', postman: 'Marcel, le facteur', neighbor: 'Mamie Rose, la voisine', pompon: 'Pompon, son chat',
    leon: 'Léon, le cariste', iris: 'Iris, le vieux chien', piquette: 'Maman Piquette', goal: 'Filet de Léon',
    letters: 'Lettre du facteur', balls: 'Ballon de Léon', toys: 'Jouet d’Iris', babies: 'Petit hérisson',
    roadTunnels: 'Tunnel de la route', vehicles: 'Véhicule', crossings: 'Passage piéton', calm: 'Zone calme',
    zones: 'Zone', zoneRect: 'Rectangle de zone', landmarks: 'Étiquette de la carte', pen: 'Enclos des poules',
    penGate: 'Barrière de l’enclos', ballBox: 'Terrain des ballons', track: 'Voie de Titine',
  };
  const PERSONNAGES = ['farmer', 'postman', 'neighbor', 'leon', 'iris', 'piquette'];
  const TOY_NAMES = ['canard', 'anneau', 'corde'];

  // clé d'atlas d'un élément (carte.SPRITES)
  ED.sprite = (type, genre, i) => {
    const s = ED.I.sprites[type];
    if (Array.isArray(s)) return [s[0], i || 0];
    return [s.replace('{}', genre), 0];
  };

  function objets(c) {
    const out = [], I = ED.I;
    const flat = new Set((I.jeu && I.jeu.flat) || ['bridge', 'sandbox', 'burrow', 'rail', 'dog_bed', 'fallen_apples']);
    // un élément de liste [genre, x, y, …] ou [x, y, …]
    const liste = (type, calque, opts = {}) => (c[type] || []).forEach((e, i) => {
      const nomme = typeof e[0] === 'string', o = nomme ? 1 : 0;
      const [key, frame] = ED.sprite(type, nomme ? e[0] : null, i);
      out.push(Object.assign({
        id: type + '/' + i, type, i, calque, x: e[o], y: e[o + 1], genre: nomme ? e[0] : null, spr: key, frame,
        set: (x, y) => { const v = ED.c[type][i]; v[o] = r4(x); v[o + 1] = r4(y); },
      }, typeof opts === 'function' ? opts(e, i) : opts));
    });
    const point = (type, calque, get, opts = {}) => {
      const p = get(c);
      const [key, frame] = 'spr' in opts ? [opts.spr, 0] : ED.sprite(type, null, 0);
      out.push(Object.assign({ id: type, type, calque, x: p[0], y: p[1], spr: key, frame,
        set: (x, y) => { const v = get(ED.c); v[0] = r4(x); v[1] = r4(y); } }, opts));
    };
    liste('decor', 'decors', e => ({ flat: flat.has(e[0]), contrainte: e[0] === 'bridge' ? 'entier' : null }));
    liste('items', 'objets', e => ({ indice: I.indices.includes(e[0]) }));
    liste('dig', 'tresors', { contrainte: 'centre', alpha: 0.9 });
    liste('enemies', 'chiens', { num: true });
    liste('signs', 'panneaux');
    (c.tunnels || []).forEach((t, i) => ['a', 'b'].forEach((b, k) => out.push({
      id: 'tunnels/' + i + '/' + b, type: 'tunnels', i, bout: k, calque: 'terriers', x: t[2 * k], y: t[2 * k + 1],
      spr: 'decor/burrow', frame: 0, flat: true, autre: [t[2 - 2 * k], t[3 - 2 * k]],
      set: (x, y) => { const v = ED.c.tunnels[i]; v[2 * k] = r4(x); v[2 * k + 1] = r4(y); } })));
    liste('hens', 'animaux');
    liste('ducks', 'animaux');
    liste('cows', 'animaux');
    liste('critters', 'animaux');
    liste('butterflies', 'animaux');
    liste('villagers', 'personnages');
    for (const k of PERSONNAGES) point(k, 'personnages', c => c[k]);
    point('pompon', 'quetes', c => c.pompon);
    liste('letters', 'quetes', { num: true });
    liste('balls', 'quetes', { num: true });
    liste('toys', 'quetes', (e, i) => ({ num: true, genre: TOY_NAMES[i] }));
    liste('babies', 'quetes', { num: true });
    point('goal', 'quetes', c => c.goal);
    point('start', 'reperes', c => c.start);
    point('alice', 'reperes', c => c.alice);
    point('endingAlice', 'reperes', c => c.ending.alice, { spr: 'alice/idle/down', alpha: 0.55, fin: true });
    point('endingTecky', 'reperes', c => c.ending.tecky, { spr: 'tecky/idle/down', alpha: 0.55, fin: true });
    point('title', 'reperes', c => c.title, { spr: null, camera: true });
    (c.roadTunnels || []).forEach((t, i) => out.push({ id: 'roadTunnels/' + i, type: 'roadTunnels', i, calque: 'route',
      x: t[0], y: t[1], spr: 'decor/tunnel', frame: 0, flip: t[2],
      set: (x, y) => { const v = ED.c.roadTunnels[i]; v[0] = r4(x); v[1] = r4(y); } }));
    const road = c.traffic.y, lanes = [road + 0.95, road + 2.95];
    c.traffic.vehicles.forEach((v, i) => out.push({ id: 'vehicles/' + i, type: 'vehicles', i, calque: 'route', genre: v[0],
      x: v[2], y: lanes[v[1]], spr: 'vehicle/' + v[0], frame: 0, flip: v[1] === 0,
      set: (x, y) => { const e = ED.c.traffic.vehicles[i]; e[2] = r4(x); e[1] = Math.abs(y - lanes[0]) < Math.abs(y - lanes[1]) ? 0 : 1; } }));
    c.traffic.crossings.forEach((x, i) => out.push({ id: 'crossings/' + i, type: 'crossings', i, calque: 'route', forme: 'rect',
      rect: [x, road, x + 2, road + 3], fixe: 'h', set: (nx) => { ED.c.traffic.crossings[i] = Math.round(nx); } }));
    // rectangles
    const rect = (id, type, calque, get, opts = {}) => {
      const r = get(c);
      out.push(Object.assign({ id, type, calque, forme: 'rect', rect: r.slice(),
        setRect: q => { const v = get(ED.c); for (let k = 0; k < 4; k++) v[k] = r4(q[k]); } }, opts));
    };
    c.calm.forEach((r, i) => rect('calm/' + i, 'calm', 'calme', c => c.calm[i], { i }));
    c.zones.forEach((z, i) => {
      z.rects.forEach((r, j) => rect('zoneRect/' + i + '/' + j, 'zoneRect', 'zones', c => c.zones[i].rects[j], { i, j, zone: i, cache: true }));
      out.push({ id: 'zones/' + i, type: 'zones', i, calque: 'zones', x: z.at[0], y: z.at[1], texte: z.label, zone: i,
        set: (x, y) => { const v = ED.c.zones[i].at; v[0] = r4(x); v[1] = r4(y); } });
    });
    c.landmarks.forEach((l, i) => out.push({ id: 'landmarks/' + i, type: 'landmarks', i, calque: 'zones', x: l.at[0], y: l.at[1],
      texte: l.label, set: (x, y) => { const v = ED.c.landmarks[i].at; v[0] = r4(x); v[1] = r4(y); } }));
    rect('pen', 'pen', 'quetes', c => c.pen, { contrainte: 'xentier' });
    rect('ballBox', 'ballBox', 'quetes', c => c.ballBox);
    const [g0, g1] = c.penGate;
    out.push({ id: 'penGate', type: 'penGate', calque: 'quetes', forme: 'rect', rect: [g0, c.pen[3] - 0.15, g1, c.pen[3] + 0.15],
      fixe: 'h', set: null, setRect: q => { ED.c.penGate = [Math.round(q[0]), Math.max(Math.round(q[0]) + 1, Math.round(q[2]))]; } });
    const [t0, t1, ty] = c.track;
    out.push({ id: 'track', type: 'track', calque: 'quetes', forme: 'rect', rect: [t0, ty - 0.35, t1, ty + 0.15],
      setRect: q => { ED.c.track = [r4(q[0]), r4(q[2]), r4(q[3] - 0.15)]; } });
    return out;
  }

  /* ------------------------------------------------------------------ décors déduits (dessinés, pas modifiables) */
  // comme pack_web.derived_decor : clôtures de l'enclos, rails et heurtoirs (poteaux, terriers, filet : leurs objets)
  ED.deduits = c => {
    const out = [], [x0, x1, y] = c.track;
    out.push(['buffer_stop', x0, y + 0.1], ['buffer_stop', x1, y + 0.1]);
    for (let x = Math.floor(x0); x < Math.ceil(x1); x++) out.push(['rail', x, y]);
    const [px0, py0, px1, py1] = c.pen;
    for (let x = px0; x < px1; x++) {
      out.push(['fence_wood_h', x, py0]);
      if (!(c.penGate[0] <= x && x < c.penGate[1])) out.push(['fence_wood_h', x, py1]);
    }
    const ys = [];
    for (let k = 1; py0 + k < py1; k++) ys.push(py0 + k);
    for (const y of ys.concat([py1])) out.push(['fence_wood_v', px0, y], ['fence_wood_v', px1, y]);
    return out;
  };

  /* ------------------------------------------------------------------ zones */
  // comme zoneAt de game.js : la première zone dont un rectangle contient le point (bords de carte sans limite)
  ED.zoneA = (x, y) => {
    const c = ED.c;
    for (let i = 0; i < c.zones.length; i++) {
      for (const [x0, y0, x1, y1] of c.zones[i].rects) {
        if ((x0 <= 0 || x >= x0) && (y0 <= 0 || y >= y0) && (x1 >= c.w || x < x1) && (y1 >= c.h || y < y1)) return i;
      }
    }
    return c.zones.length - 1;
  };
  ED.calmeA = (x, y) => ED.c.calm.some(([x0, y0, x1, y1]) => x >= x0 && x <= x1 && y >= y0 && y <= y1);
})();
