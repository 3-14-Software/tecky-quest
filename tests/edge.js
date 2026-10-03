// bord de la carte : la lisière dans une marge que la caméra montre, les tunnels de la grande route, et Tecky qui le
// dit quand il pousse contre le bord (plus de mur invisible muet)
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 99;');
  const W = run('MAP.w * TS'), H = run('MAP.h * TS');
  // la caméra déborde d'EDGE.cam au-delà de la carte, pas plus
  run('P.x = 30; P.y = 12 * 64;'); step(150);
  ok(Math.abs(run('camX') + run('EDGE.cam')) < 2, 'au bord ouest, la caméra montre la marge (camX = ' + run('camX').toFixed(1) + ')');
  run(`P.x = ${W} - 30; P.y = ${H} - 6;`); step(150);
  ok(Math.abs(run('camX') - (W - run('VW') + run('EDGE.cam'))) < 2 && Math.abs(run('camY') - (H - run('VH') + run('EDGE.cam'))) < 2,
     'au coin sud-est aussi, sans aller plus loin');
  // le sol continue dans la marge, la rivière aussi
  ok(run('[[-1, 5], [-2, -2], [MAP.w + 1, MAP.h + 1], [40, -1], [40, MAP.h + 1], [MAP.w, 30]].every(([x, y]) => groundTile(x, y))')
     && run('groundTile(-3, 5)') === null, 'du sol tout autour de la carte, sur ' + run('MAP.edge.r') + ' tuiles');
  ok(run(`waterAt(-40, 43.5 * 64) && waterAt(${W} + 40, 43.5 * 64) && !waterAt(-40, 12 * 64)`), 'la rivière continue au-delà des bords');
  // la lisière : dans la marge, jamais là où l'on marche ; un tunnel à chaque bout de la grande route
  ok(run('EDGE_DECOR.length') > 300, run('EDGE_DECOR.length') + ' fourrés, arbres et sapins de lisière');
  ok(run('EDGE_DECOR.filter(d => d.n !== "tunnel").every(d => offMap(d.x, d.y - 12, d.x, d.y))'), 'tous au-delà du bord des pieds');
  run('var tun = EDGE_DECOR.filter(d => d.n === "tunnel"), T = ATLAS["decor/tunnel"], tf = T.f[0];');
  ok(run('tun.length === 2 && tun.every(d => d.y > MAP.traffic.road[1] && d.y - 7 * 64 < MAP.traffic.road[0])') && run(`tun.some(d => !d.flip && d.x === 0) && tun.some(d => d.flip && d.x === ${W})`),
     'deux tunnels, un à chaque bout de la grande route');
  ok(run('tf[4] - T.o[0] <= -EDGE.cam - 6 && tun[0].y + tf[5] - T.o[1] <= MAP.traffic.road[0] - 60 && tun[0].y + tf[5] - T.o[1] + tf[3] >= MAP.traffic.road[1]'),
     'la butte couvre la route sur toute la marge visible : les voitures y disparaissent');
  // Tecky pousse contre le bord ouest, dans le pré : il le dit au bout d'un moment, une fois
  run('pops = []; P.edgeAt = -99; P.x = 200; P.y = 12 * 64; P.mode = "free";');
  step(60, 'held.left = true');
  // (à un pas près : 250 px/s, soit 4,2 px par image)
  ok(run('P.x - 16 - BOUND.side') < 4.5 && !run('pops.some(p => p.who === "tecky")'), 'il s’arrête au bord (x = ' + run('P.x').toFixed(1) + '), sans rien dire tout de suite');
  step(40, 'held.left = true');
  ok(run('pops.some(p => p.text === "Alice n’a pas pu aller si loin !" && p.who === "tecky")'), 'puis : « Alice n’a pas pu aller si loin ! »');
  run('var at0 = P.edgeAt;'); step(60 * 3, 'held.left = true');
  ok(run('P.edgeAt === at0'), 'pas à chaque instant (au plus une fois toutes les ' + run('EDGE.again') + ' s)');
  step(60 * run('EDGE.again'), 'held.left = true');
  ok(run('P.edgeAt > at0'), 'mais il le redit s’il insiste');
  run('held.left = false'); step(2);
  ok(run('P.edgeT') === 0, 'il lâche : le compte repart de zéro');
  // en haut de la carte, aux champs de la ferme : pareil
  run('pops = []; P.edgeAt = -99; P.x = 62 * 64; P.y = 3 * 64;');
  step(100, 'held.up = true'); run('held.up = false');
  ok(run('P.y - 12 - BOUND.top') < 4.5 && run('pops.some(p => p.text === "Alice n’a pas pu aller si loin !")'), 'au bord nord aussi');
  // au bout de la grande route : il s'arrête devant la bouche du tunnel, sans y fourrer la tête, et l'explique
  for (const [x, key, side] of [[300, 'left', 'ouest'], [W - 300, 'right', 'est']]) {
    run(`cars = []; pops = []; P.edgeAt = -99; P.x = ${x}; P.y = 19.3 * 64; P.mode = "free";`);
    step(120, `held.${key} = true`); run(`held.${key} = false`);
    const px = run('P.x');
    ok(key === 'left' ? px - 16 >= 39 && px - 16 < 44 : px + 16 <= W - 39 && px + 16 > W - 44,
       `bout ${side} de la route : Tecky s’arrête devant le tunnel (x = ${px.toFixed(1)})`);
    ok(run('pops.some(p => p.text === "Le tunnel, c’est pour les voitures !")'), '« Le tunnel, c’est pour les voitures ! »');
  }
  // au joystick, on ne pousse jamais tout droit : Tecky glisse le long de la butte ou du bord, et le dit quand même
  for (const [sx, sy, side] of [[1, 0.3, 'est'], [-1, -0.3, 'ouest'], [1, 0.15, 'est']]) {
    run(`cars = []; pops = []; P.edgeAt = -99; P.x = ${sx > 0 ? 'MAP.w * TS - 200' : '200'}; P.y = (MAP.traffic.road[0] + MAP.traffic.road[1]) / 2; P.mode = "free";`);
    let said = false;
    for (let i = 0; i < 60 * 3; i++) { run(`cars = []; stick.id = 1; stick.vx = ${sx}; stick.vy = ${sy};`); step(1); if (run('pops.some(p => p.text === "Le tunnel, c’est pour les voitures !")')) said = true; }
    run('stick.id = null; stick.vx = stick.vy = 0;');
    ok(said, `au joystick, un peu en biais (${sy}), tunnel ${side} : il le dit aussi`);
  }
  // les voitures, elles, passent : elles entrent dans un tunnel et ressortent de l'autre
  run('cars = MAP.traffic.vehicles.map(newVehicle); var c0 = cars[0]; c0.x = 30; P.x = 40 * 64; P.y = 12 * 64;');
  let back = false;
  for (let i = 0; i < 60 * 3 && !back; i++) { step(1); if (run('c0.x') > W / 2) back = true; }
  ok(back, 'une voiture qui entre dans le tunnel ouest ressort par celui de l’est');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
