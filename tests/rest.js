// Tecky au repos : assis quand on ne touche à rien, bâille ou se gratte, puis s'endort (« z ») ; un geste le réveille
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999; farm.state = "done"; P.x = 8 * 64; P.y = 5 * 64 + 32; P.mode = "free"; P.dir = "up";');
  ok(['sit', 'yawn', 'scratch', 'sleep', 'shake'].every(a => run(`FPS.${a} > 0`)), 'poses de repos connues (FPS)');
  ok(run('["sit/down", "sit/right", "yawn/down", "yawn/right", "scratch/right", "sleep/down", "sleep/right", "shake/down", "shake/right"].every(k => ATLAS["tecky/" + k])'),
     'toutes les vues dans l’atlas');
  step(60 * 3);
  ok(run('P.anim') === 'idle', 'au bout de 3 s : debout');
  step(60 * 4);
  ok(['sit', 'yawn', 'scratch'].includes(run('P.anim')) && run('P.dir') !== 'up', 'au bout de 7 s : assis, tourné vers nous (' + run('P.anim') + ', ' + run('P.dir') + ')');
  const seen = {};
  for (let i = 0; i < 60 * 15; i++) { step(1); seen[run('P.anim')] = 1; if (seen.yawn && seen.scratch) break; }
  ok(seen.yawn && seen.scratch, 'il bâille et se gratte de temps en temps');
  { let k = 0; while (run('P.anim') !== 'sleep' && k++ < 60 * 20) step(1); }
  ok(run('P.anim') === 'sleep' && run('napped'), 'puis il s’endort (au bout de ' + Math.round(run('P.restT')) + ' s)');
  step(60 * 2);
  ok(run('fxs.some(f => f.key === "fx/zzz")'), 'des « z » montent au-dessus de lui');
  run('var used = []; var ds0 = drawSpr; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; render(); drawSpr = ds0;');
  ok(run('used.some(k => /^tecky\\/sleep\\//.test(k))') && run('used.includes("fx/zzz")'), 'dessiné endormi, avec ses « z »');
  step(60 * 3);
  ok(run('fxs.filter(f => f.key === "fx/zzz").length') <= 4, 'les « z » s’effacent (' + run('fxs.filter(f => f.key === "fx/zzz").length') + ' à la fois)');
  // un geste le réveille
  run('held.right = true'); step(2); run('held.right = false');
  ok(run('P.anim') === 'walk' && run('P.restT') === 0, 'une flèche : réveillé, il marche');
  step(60 * 3);
  ok(run('P.anim') === 'idle', 'et le repos recommence à zéro');
  run('P.cdBark = 0; pressed.bark = true'); step(1);
  ok(run('P.restT') < 0.1, 'aboyer le réveille aussi');
  step(60);                                            // (fin de l'aboiement)
  // jamais assis quand un chien menace
  run('var D = new Actor("roquet", P.x + 150, P.y); Object.assign(D, { id: 99, T: DOGS.roquet, hp: 2, mode: "chase", timer: 0, hx: D.x, hy: D.y, vx: 0, vy: 0, kx: 0, ky: 0, cd: 9, barkCd: 9, chargeCd: 9, hitDone: false, fade: 0 }); dogs = [D];');
  run('P.restT = 10');
  step(5, 'D.mode = "chase"; D.x = P.x + 150; D.y = P.y; D.cd = 9;');
  ok(run('P.anim') === 'idle' && run('P.restT') === 0, 'un chien menace : il reste debout');
  run('dogs = []');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
