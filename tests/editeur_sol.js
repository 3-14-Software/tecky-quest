// éditeur de carte : le sol calculé dans la page (editeur/sol.js) est exactement celui du jeu (pack_web.build_map)
const fs = require('fs'), { execFileSync } = require('child_process');
const ED = require('../editeur/sol.js');
const root = __dirname + '/..';
const ok = (c, m) => { if (!c) { console.log('ÉCHEC :', m); process.exitCode = 1; } else console.log('ok :', m); };
const html = fs.readFileSync(root + '/web/index.html', 'utf8');
const MAP = Object.assign(JSON.parse(html.match(/const JEU = (.*);\n/)[1]), JSON.parse(html.match(/const CARTES = (.*);\n/)[1]).monde);
const I = JSON.parse(execFileSync('python3', ['editeur.py', '--infos'], { cwd: root, encoding: 'utf8' }));
const c = JSON.parse(fs.readFileSync(root + '/carte.json', 'utf8'));
const s = ED.calculerSol(c, I);
const diff = (a, b) => a.reduce((n, v, i) => n + (v !== b[i] ? 1 : 0), 0) + Math.abs(a.length - b.length);
ok(diff(s.ground, MAP.ground) === 0, 'sol : les ' + MAP.ground.length + ' tuiles de la carte (' + diff(s.ground, MAP.ground) + ' différences)');
ok(diff(s.over, MAP.over) === 0, 'détails au sol (' + diff(s.over, MAP.over) + ' différences)');
ok(JSON.stringify(s.ring) === JSON.stringify(MAP.edge.ring), 'sol de la lisière (' + s.ring.length + ' tuiles)');
ok(s.composites.length > 0 && s.ground.some(i => i >= I.compositeBase), s.composites.length + ' tuiles composées, mêmes index');
// une carte annexe (cartes/cote.json) : même sol que le jeu, elle aussi, avec sa route et sa lisière
{
  const cote = JSON.parse(fs.readFileSync(root + '/cartes/cote.json', 'utf8')), jeu = JSON.parse(html.match(/const CARTES = (.*);\n/)[1]).cote;
  const sp = ED.calculerSol(cote, I);
  // (les tuiles composées sont numérotées à la suite pour toutes les cartes du jeu : on compare leurs places, pas leur numéro)
  const sansNumero = a => a.map(v => v >= I.compositeBase ? -1 : v);
  ok(diff(sansNumero(sp.ground), sansNumero(jeu.ground)) === 0 && diff(sp.over, jeu.over) === 0
     && JSON.stringify(sp.ring.map(([x, y, v]) => [x, y, v >= I.compositeBase ? -1 : v])) === JSON.stringify(jeu.edge.ring.map(([x, y, v]) => [x, y, v >= I.compositeBase ? -1 : v])),
     'carte annexe « cote » : sol, détails et lisière comme dans le jeu (' + jeu.ground.length + ' tuiles)');
}
// décors redessinés : l'éditeur montre, pour chaque décor de la carte, le modèle que le jeu tire de sa position
const jeu = (n, x, y) => { const v = MAP.variants[n]; return 'decor/' + (v ? v[0][v[1][Math.floor(ED.hash3(Math.round(x), Math.round(y), 7) * v[1].length)]] : n); };
const ecarts = c.decor.filter(([n, x, y], i) => ED.cle('decor/' + n, x, y, I) !== jeu(n, MAP.decor[i][1], MAP.decor[i][2]));
ok(c.decor.every(([n], i) => MAP.decor[i][0] === n) && ecarts.length === 0,
   'décors : pour les ' + c.decor.length + ' de la carte, le même modèle que dans le jeu (' + ecarts.length + ' écarts)');
const ATLAS = JSON.parse(html.match(/const ATLAS = (.*);\n/)[1]);
const sans = [...new Set(c.decor.map(([n, x, y]) => ED.cle('decor/' + n, x, y, I)).concat(Object.keys(I.variants).map(n => ED.cle('decor/' + n, undefined, undefined, I))))].filter(k => !ATLAS[k]);
ok(sans.length === 0 && ED.cle('item/bone', 1, 2, I) === 'item/bone', 'chacun a son dessin dans l\'atlas, palette comprise (' + (sans.join(', ') || 'aucun manquant') + ')');
// un coin de plus : seules ses quatre tuiles changent (les variantes ne dépendent que de la position)
const c2 = JSON.parse(JSON.stringify(c)), y = 30, x = 2, row = c2.terrain[y];
c2.terrain[y] = row.slice(0, x) + (row[x] === 't' ? '.' : 't') + row.slice(x + 1);
const s2 = ED.calculerSol(c2, I), changed = s.ground.map((v, i) => v !== s2.ground[i] ? i : -1).filter(i => i >= 0);
ok(changed.length > 0 && changed.every(i => Math.abs(i % c.w - x + 0.5) <= 1 && Math.abs(Math.floor(i / c.w) - y + 0.5) <= 1),
   'changer un coin ne touche que ses tuiles voisines (' + changed.length + ')');
