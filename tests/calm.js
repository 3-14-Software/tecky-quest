// zones calmes (village, cour de la ferme) : aucun chien hostile n'y vit ni n'y poursuit Tecky ; répit après un dialogue
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('cars = []; P.inv = 0; graceT = 0;');
  ok(run('MAP.calm.length') === 5 && run('npcList().every(n => calmAt(n.x, n.y))'),
     'zones calmes : le village, la cour de la ferme, les coins de Léon et de Nestor, la clairière de Maman Piquette');
  ok(run('dogs.every(d => !calmAt(d.hx, d.hy))'), 'aucun chien n’y habite');
  ok(run('!calmAt(MAP.start[0], MAP.start[1])') && run('!calmAt(46 * 64, 19.5 * 64)'), 'la niche et la grande route n’en sont pas');
  // un roquet poursuit Tecky jusqu'au village : il s'arrête à l'entrée et rentre chez lui
  run('var R = dogs.find(d => d.kind === "roquet"); dogs = [R]; R.x = R.hx = 35 * 64; R.y = R.hy = 22.4 * 64; R.mode = "idle"; R.cd = 9;');
  run('P.x = 35 * 64; P.y = 20.2 * 64; P.mode = "free"; P.inv = 999;'); step(20);
  ok(run('R.mode') === 'chase', 'sur la route : le roquet le poursuit');
  run('pops = [];'); for (let i = 0; i < 30; i++) { run('P.y = Math.max(16.6 * 64, P.y - 12);'); step(1); }
  ok(run('calmAt(P.x, P.y)') && run('R.mode') === 'return', 'Tecky entre au village : le roquet rentre chez lui');
  ok(run('pops.some(p => p.text === "Grrr…")'), 'en grognant (« Grrr… »)');
  step(60 * 3);
  ok(run('!calmAt(R.x, R.y)') && run('dist(R.x, R.y, R.hx, R.hy)') < 120, 'il ne met pas une patte au village');
  // aucune morsure n'y porte, et C n'y mord jamais
  run('P.inv = 0; graceT = 0; var hp0 = P.hp; hurtPlayer(2, P.x + 40, P.y);');
  ok(run('P.hp') === run('hp0'), 'pas de morsure en zone calme');
  run('R.mode = "chase"; R.x = P.x + 100; R.y = P.y;');
  ok(!run('threatened()'), 'personne ne menace Tecky au village : C sert à parler, lire…');
  // en parlant au facteur, avec tous les chiens de la carte : personne ne vient
  run('newGame("aventure", true)'); advanceDialog();
  run('cars = []; P.x = postman.x; P.y = postman.y + 90; P.mode = "free"; P.inv = 0; graceT = 0; var hp1 = P.hp;');
  ok(run('calmAt(P.x, P.y)') && run('dist(P.x, P.y, postman.x, postman.y)') < run('NPC.talk'), 'sur le trottoir, assez près pour lui parler : en zone calme');
  let eng = false;
  for (let i = 0; i < 60 * 15; i++) { step(1); if (run('dogs.some(d => ENGAGED.has(d.mode))')) eng = true; if (run('state') === 'dialog') advanceDialog(); }
  ok(!eng && run('P.hp') === run('hp1'), '15 s près du facteur : aucun chien ne s’en prend à Tecky');
  // répit : juste après un dialogue, une morsure ne porte pas ; ensuite si
  run('dogs = []; cars = []; P.x = 10 * 64; P.y = 20 * 64; say([{ who: "tecky", text: "Ouaf !" }]);'); advanceDialog();
  run('P.inv = 0; var hp2 = P.hp; hurtPlayer(1, P.x + 40, P.y);');
  ok(run('P.hp') === run('hp2') && run('graceT') > 1, 'en sortant d’un dialogue : un petit répit');
  step(60 * 2); run('P.inv = 0; P.mode = "free"; hurtPlayer(1, P.x + 40, P.y);');
  ok(run('P.hp') === run('hp2') - 1, 'puis les morsures portent de nouveau');
  // en balade, les copains peuvent suivre Tecky au village
  run('newGame("balade", true)'); advanceDialog();
  run('cars = []; var C = dogs.find(d => d.kind === "roquet"); dogs = [C]; P.x = 37 * 64; P.y = 9 * 64; P.mode = "free"; C.x = C.hx = P.x; C.y = C.hy = P.y + 300; C.mode = "chase"; C.calm = 0;');
  step(60);
  ok(run('dist(C.x, C.y, P.x, P.y)') < 150, 'en balade : un chien vient jouer avec Tecky au village');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
