// éditeur de carte : le sol calculé dans la page (editeur/sol.js) est exactement celui du jeu (pack_web.build_map)
const fs = require('fs'), { execFileSync } = require('child_process');
const ED = require('../editeur/sol.js');
const root = __dirname + '/..';
const ok = (c, m) => { if (!c) { console.log('ÉCHEC :', m); process.exitCode = 1; } else console.log('ok :', m); };
const html = fs.readFileSync(root + '/web/index.html', 'utf8');
const MAP = JSON.parse(html.match(/const MAP = (.*);\n/)[1]);
const I = JSON.parse(execFileSync('python3', ['editeur.py', '--infos'], { cwd: root, encoding: 'utf8' }));
const c = JSON.parse(fs.readFileSync(root + '/carte.json', 'utf8'));
const s = ED.calculerSol(c, I);
const diff = (a, b) => a.reduce((n, v, i) => n + (v !== b[i] ? 1 : 0), 0) + Math.abs(a.length - b.length);
ok(diff(s.ground, MAP.ground) === 0, 'sol : les ' + MAP.ground.length + ' tuiles de la carte (' + diff(s.ground, MAP.ground) + ' différences)');
ok(diff(s.over, MAP.over) === 0, 'détails au sol et traces de pattes (' + diff(s.over, MAP.over) + ' différences)');
ok(JSON.stringify(s.ring) === JSON.stringify(MAP.edge.ring), 'sol de la lisière (' + s.ring.length + ' tuiles)');
ok(s.composites.length > 0 && s.ground.some(i => i >= I.compositeBase), s.composites.length + ' tuiles composées, mêmes index');
// un coin de plus : seules ses quatre tuiles changent (les variantes ne dépendent que de la position)
const c2 = JSON.parse(JSON.stringify(c)), y = 30, x = 2, row = c2.terrain[y];
c2.terrain[y] = row.slice(0, x) + (row[x] === 't' ? '.' : 't') + row.slice(x + 1);
const s2 = ED.calculerSol(c2, I), changed = s.ground.map((v, i) => v !== s2.ground[i] ? i : -1).filter(i => i >= 0);
ok(changed.length > 0 && changed.every(i => Math.abs(i % c.w - x + 0.5) <= 1 && Math.abs(Math.floor(i / c.w) - y + 0.5) <= 1),
   'changer un coin ne touche que ses tuiles voisines (' + changed.length + ')');
