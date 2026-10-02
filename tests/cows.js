// les vaches de la campagne : elles broutent et se promènent autour de leur place, regardent Tecky, meuglent ; un
// aboiement les fait trotter plus loin (le veau suit sa mère) ; ce sont des obstacles, qui ne marchent jamais sur Tecky
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999; P.x = 10 * 64; P.y = 5 * 64; opts.weather = "soleil"; resetWeather();');
  ok(run('cows.length') === 3 && run('JSON.stringify(cows.map(c => c.kind))') === '["cow_bw","cow_brown","calf"]', 'la pie noire, la pie rouge et son veau');
  ok(run('cows.every(c => zoneAt(c.x, c.y).id === "campagne")'), 'dans le pré de la campagne');
  ok(run('cows.every(c => ["idle", "graze", "walk", "moo"].every(a => !!ATLAS[c.kind + "/" + a]))'), 'leurs animations');
  // loin de Tecky : elles broutent et se promènent, sans s'éloigner de leur place (le veau, de sa mère)
  let walked = false, grazed = false;
  for (let i = 0; i < 60 * 40; i++) {
    step(1);
    if (run('cows.some(c => c.anim === "walk")')) walked = true;
    if (run('cows.some(c => c.anim === "graze")')) grazed = true;
  }
  ok(walked && grazed, 'elles broutent et font quelques pas');
  ok(run('cows.filter(c => c.kind !== "calf").every(c => dist(c.x, c.y, c.hx, c.hy) < COW.roam + 60)'), 'sans quitter leur coin de pré');
  ok(run('dist(cows[2].x, cows[2].y, cows[1].x, cows[1].y)') < 220, 'le veau reste près de sa mère (' + Math.round(run('dist(cows[2].x, cows[2].y, cows[1].x, cows[1].y)')) + ' px)');
  // Tecky approche : elle lève la tête vers lui
  run('var C = cows[0]; C.mode = "graze"; C.anim = "graze"; C.timer = 5; P.x = C.x + 150; P.y = C.y; P.mode = "free";'); step(2);
  ok(run('C.anim') === 'idle' && run('C.dir') === 'right', 'Tecky approche : elle lève la tête et le regarde');
  // de temps en temps, quand il est dans les parages : « Meuh ! »
  run('var mooed = 0, m0 = SFX.moo; SFX.moo = function () { mooed++; return m0.apply(this, arguments); }; C.mooT = 0.01; pops = [];'); step(2);
  ok(run('pops.some(p => p.text === "Meuh !" && p.who === "cow")') && run('mooed') > 0 && run('C.anim') === 'moo', '« Meuh ! » (et son meuglement)');
  // c'est un obstacle : Tecky ne lui passe pas à travers
  run('C.mode = "graze"; C.timer = 99; C.mooT = 99; P.x = C.x - 140; P.y = C.y; P.dir = "right";');
  step(60 * 2, 'held.right = true'); run('held.right = false');
  ok(run('P.x') < run('C.box[0]') && run('C.box[2] - C.box[0]') > 60, 'on ne traverse pas une vache (Tecky s’arrête à ' + Math.round(run('C.box[0] - P.x')) + ' px)');
  // et elle ne lui marche jamais dessus
  run('P.x = C.x + 110; P.y = C.y; C.mode = "walk"; C.tx = P.x + 200; C.ty = C.y; C.timer = 4; C.anim = "walk";');
  let overlap = false;
  for (let i = 0; i < 60 * 3; i++) { step(1); if (run('P.x + 12 > C.box[0] && P.x - 12 < C.box[2] && P.y > C.box[1] && P.y - 12 < C.box[3]')) overlap = true; }
  ok(!overlap, 'elle ne marche jamais sur Tecky');
  // un aboiement vers la vache brune : elle meugle et s'éloigne au trot, et son veau la suit
  run('var B = cows[1], V = cows[2]; B.mode = V.mode = "graze"; P.x = B.x - 220; P.y = B.y; P.dir = "right"; P.mode = "free"; P.cdBark = 0; pops = []; var b0 = dist(B.x, B.y, P.x, P.y);');
  run('pressed.bark = true'); step(1);
  ok(run('B.mode') === 'trot' && run('V.mode') === 'trot' && run('pops.some(p => p.text === "Meuuuh !")'), 'un aboiement : « Meuuuh ! », elle trotte, son veau aussi');
  step(60 * 2);
  ok(run('dist(B.x, B.y, P.x, P.y)') > run('b0') + 60, 'elle s’est éloignée (' + Math.round(run('dist(B.x, B.y, P.x, P.y) - b0')) + ' px)');
  step(60 * 3);
  ok(run('B.mode') !== 'trot' && run('B.box[0]') === run('B.x - COW.half'), 'puis elle se calme, et sa boîte l’a suivie');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
