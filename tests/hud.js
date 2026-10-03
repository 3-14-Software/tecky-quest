// compteurs du HUD : quand beaucoup de quêtes sont en cours, ils passent sur une deuxième colonne plutôt que de
// descendre sous les boutons d'action (au toucher) ou les aides de touches (clavier, manette)
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('treasures = 1; farm.state = post.state = rose.state = fete.state = jouets.state = piq.state = "asked";');
  ok(run('hudCounters().length') === 7, 'sept compteurs (os dorés et six quêtes)');
  const panels = () => run('var nine = [], d0 = drawNine; drawNine = function (k, x, y, w, h) { if (w === COUNTER.w && h === COUNTER.h) nine.push([x, y, w, h]); return d0.apply(this, arguments); }; drawHUD(); drawNine = d0; nine');
  // au toucher
  run('touchMode = true;');
  const t = panels(), S = run('BTN.sniff'), B = run('BTN.bite');
  const hits = (p, c) => p[0] < c.x + c.r && p[0] + p[2] > c.x - c.r && p[1] < c.y + c.r && p[1] + p[3] > c.y - c.r;
  ok(t.length === 7 && t.every(p => !hits(p, S) && !hits(p, B)), 'au toucher : aucun compteur sous les boutons');
  ok(new Set(t.map(p => p[0])).size === 2 && t.every(p => p[0] + p[2] <= 1920 - 24), 'sur deux colonnes, dans l’écran');
  ok(t.every((p, i) => t.every((q, j) => i === j || p[0] + p[2] <= q[0] || q[0] + q[2] <= p[0] || p[1] + p[3] <= q[1] || q[1] + q[3] <= p[1])),
     'sans se chevaucher');
  // au clavier : une seule colonne, au-dessus des aides de touches
  run('touchMode = false;');
  const k = panels();
  ok(new Set(k.map(p => p[0])).size === 1 && Math.max(...k.map(p => p[1] + p[3])) < run('GH - 190'), 'au clavier : une colonne, au-dessus des aides de touches');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
