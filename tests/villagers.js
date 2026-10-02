// les villageois (sans quête) : le boulanger, la marchande de fruits, la fleuriste et le petit garçon au ballon saluent
// Tecky quand il passe (une phrase après l'autre), font signe de la main ; on ne leur parle pas
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999; P.x = 10 * 64; P.y = 5 * 64;');
  ok(run('JSON.stringify(villagers.map(v => v.kind))') === '["baker","vendor","florist","kid"]', 'le boulanger, la marchande, la fleuriste, le petit garçon');
  ok(run('villagers.every(v => zoneAt(v.x, v.y).id === "village" && calmAt(v.x, v.y))'), 'tous au village, en zone calme');
  ok(run('villagers.every(v => !!ATLAS[v.kind + "/idle"] && !!ATLAS[v.kind + (v.kind === "kid" ? "/hop" : "/wave")])'), 'leurs animations');
  // Tecky passe devant le boulanger : une bulle, il fait signe de la main
  run('var B = villagers[0]; P.x = B.x - 100; P.y = B.y + 60; P.mode = "free"; pops = [];'); step(2);
  ok(run('pops.some(p => p.text === "Bonjour, Tecky !" && p.who === "baker")') && run('B.anim') === 'wave', '« Bonjour, Tecky ! », et il salue');
  ok(run('biteAction()') !== 'talk' && !run('npcList().includes(B)'), 'on ne lui parle pas (pas de quête)');
  ok(run('blockedFeet(B.x, B.y, 16)'), 'on ne lui passe pas à travers');
  step(60 * 3);
  ok(run('B.anim') === 'idle', 'puis il reprend sa pose');
  // Tecky repart et revient : pas tout de suite une autre bulle, puis la phrase suivante
  run('P.x = B.x - 600; pops = [];'); step(10); run('P.x = B.x - 100;'); step(2);
  ok(!run('pops.some(p => p.who === "baker")'), 'revenu trop vite : il ne répète pas');
  run('P.x = B.x - 600;'); step(60 * Math.ceil(run('VILLAGER.again'))); run('P.x = B.x - 100; pops = [];'); step(2);
  ok(run('pops.some(p => p.text === "Ça sent bon le pain chaud !")'), 'plus tard : « Ça sent bon le pain chaud ! »');
  // le petit garçon sautille de joie
  run('var K = villagers[3]; P.x = K.x + 120; P.y = K.y; pops = [];'); step(2);
  ok(run('K.anim') === 'hop' && run('pops.some(p => p.text === "Un toutou !" && p.who === "kid")'), 'le petit garçon : « Un toutou ! », il sautille');
  run('render()');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
