// les finitions de l'été : la tenue d'Alice (marinière, tongs, une tong perdue), la chaise haute de Théo, les
// deux-roues et les véhicules garés, le sable habillé, les cultures d'été, les vagues, le manège qui tourne en
// musique, le chenal du bassin et son pont.
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('EPISODES[1].chantier = false; audioOn(); STORE.mem = {}; loadBadges(); episode = "ete"; newGame("aventure", true);');
  // ---- Alice : au départ ses deux tongs ; cachée, il lui en manque une ; à la fin, Tecky la lui a rapportée
  ok(run('aliceKind(false)') === 'alice_ete' && run('WHO.alice.portrait') === 'hud/portrait_alice_ete' && run('aliceKind(true)') === 'alice_ete1',
     'en été, Alice a sa marinière et ses tongs (dessins et portrait de la saison)');
  ok(['idle', 'walk', 'happy'].every(a => ['down', 'up', 'right'].every(v => run(`ATLAS["alice_ete/${a}/${v}"].f.length === ATLAS["alice/${a}/${v}"].f.length && ATLAS["alice_ete1/${a}/${v}"].f.length === ATLAS["alice/${a}/${v}"].f.length`)))
     && run('ATLAS["hud/portrait_alice_ete"].f.length') === 3 && run('CAST.has("alice_ete") && CAST.has("alice_ete1")'),
     'ses dessins d’été : les mêmes animations, avec ses deux tongs ou un pied nu, leur ombre portée, trois visages');
  run('tripDone();');
  ok(run('alice.kind') === 'alice_ete1' && run('alice.hidden'), 'cachée, elle a perdu une tong (l’indice de la plage)');
  run('cars = []; dogs = []; crabs = []; seagulls = []; critters = []; var T = MAP.ts; function va(x, y) { P.x = x; P.y = y; P.mode = "free"; P.inv = 0; P.kx = P.ky = 0; graceT = 0; syncSwim(true); }');
  // ---- la chaise haute de Théo
  const chaise = run('decor.find(d => d.n === "lifeguard_chair")');
  ok(chaise && run('var CH = decor.find(d => d.n === "lifeguard_chair"); dist(CH.x, CH.y, iris.x, iris.y) < 4 * T && sandAt(CH.x, CH.y) && !!ATLAS[CH.key]')
     && run('blockedFeet(CH.x, CH.y - 8, 10)'), 'la chaise haute du maître-nageur est sur le sable, près de Théo, et c’est un obstacle');
  // ---- les véhicules garés et les deux-roues
  ok(run('decor.filter(d => d.n === "parked_car").length') >= 4 && run('decor.filter(d => d.n === "parked_scooter").length') >= 2 && run('decor.some(d => d.n === "parked_moto")')
     && run('decor.filter(d => d.n.startsWith("parked_")).every(d => !!ATLAS[d.key] && blockedFeet(d.x, d.y - 8, 8))')
     && run('new Set(decor.filter(d => d.n === "parked_car").map(d => d.key)).size') >= 2,
     'des voitures, des scooters et des motos garés : des obstacles, de plusieurs couleurs');
  ok(run('MAP.traffic.vehicles.some(v => v[0].startsWith("scooter_")) && MAP.traffic.vehicles.some(v => v[0].startsWith("moto_"))')
     && run('MAP.traffic.vehicles.every(v => !!ATLAS["vehicle/" + v[0]] && !!VEHICLE[v[0].split("_")[0]])')
     && run('VEHICLE.scooter.horn') === 'meep' && run('typeof SFX.meep') === 'function' && run('VEHICLE.scooter.len < VEHICLE.car.len'),
     'sur la route de la côte : un scooter (son petit klaxon) et une moto, plus courts qu’une voiture');
  // ---- le sable habillé, les vagues
  ok(run('ATLAS["sol/sable"].f.length') === 10 && run('SAND.pick.every(i => i < 10)') && run('sandTile(Math.floor(CH.x / T), Math.floor(CH.y / T))') && run('!sandTile(30, 8)'),
     'ce que la mer laisse sur le sable : dix dessins, semés dans le sable plein');
  ok(run('shoreLine().length') > 200 && run('shoreDots.every(d => Math.abs(cornerVal(MAP.sea, d[0], d[1]) - 0.5) < 0.2 && Math.abs(Math.hypot(d[2], d[3]) - 1) < 0.01)')
     && run('shoreDots.every(d => cornerVal(MAP.sea, d[0] + d[2] * 20, d[1] + d[3] * 20) < cornerVal(MAP.sea, d[0] - d[2] * 20, d[1] - d[3] * 20))'),
     'les vagues : ' + run('shoreDots.length') + ' points le long du bord de mer, leur normale tournée vers le sable');
  let err = null;
  try { run('va(22 * T, 47.5 * T); camX = P.x - VW / 2; camY = P.y - VH / 2;'); step(30); run('render()'); } catch (e) { err = e; }
  ok(!err, 'la plage se dessine (sable, vagues)' + (err ? ' : ' + err.message : ''));
  // ---- le manège tourne, en musique
  ok(run('["manege_socle", "manege_mat", "manege_chapiteau", "manege_cheval_0", "manege_cheval_1", "manege_cheval_2", "manege_cheval_3"].every(n => !!ATLAS["decor/" + n])')
     && run('!!SONGS.manege') && run('SONGS.manege.loop') === 0, 'le manège a ses morceaux, ses quatre chevaux et sa valse');
  run('var MG = decor.find(d => d.n === "carousel"); va(MG.x, MG.y + 90);');
  ok(run('zoneAt(P.x, P.y).id') === 'manege' && run('zoneAt(MG.x + 12 * T, MG.y).id') === 'ville', 'autour du manège, sa zone (dans la ville)');
  for (let i = 0; i < 60 * 6; i++) step(1);
  ok(run('Music.zone') === 'manege' || run('Music.want') === 'manege', 'Tecky s’y attarde : la valse du manège');
  run('var seen = []; var d0 = drawSpr; drawSpr = function (k, i, x, y, o) { if (k.startsWith("decor/manege_")) seen.push([k, x, y, o && o.flip]); return d0.apply(this, arguments); };');
  run('seen = []; drawCarousel(MG, 0); var A = seen.slice(); seen = []; drawCarousel(MG, CAROUSEL.turn / 8); var B = seen.slice(); drawSpr = d0;');
  ok(run('A.length') === 7 && run('A[0][0]') === 'decor/manege_socle' && run('A[6][0]') === 'decor/manege_chapiteau' && run('A.findIndex(a => a[0] === "decor/manege_mat")') === 3
     && run('A.filter(a => a[0].includes("cheval")).some((a, i) => { const b = B.find(q => q[0] === a[0]); return Math.abs(a[1] - b[1]) > 20; })')
     && run('A.slice(1, 3).every(a => a[3]) && A.slice(4, 6).every(a => !a[3])'),
     'il tourne : plateau, deux chevaux au fond (tournés de l’autre côté), le mât, deux devant, le chapiteau');
  // ---- le chenal du bassin : la mer entre dans le bassin, un pont de bois le franchit
  ok(run('seaAt(35 * T, 31.5 * T) || !waterAt(35 * T, 31.5 * T)') && run('waterAt(38.5 * T, 31.5 * T)') && run('waterAt(28 * T, 30 * T)')
     && run('decor.some(d => d.n === "bridge")'), 'le bassin s’ouvre sur la rivière par un chenal, franchi par un pont');
  run('va(35 * T, 28.6 * T); P.dir = "down";');
  step(60 * 8, 'held.down = true'); run('held.down = false');
  ok(run('P.y') > 34.5 * run('T') && run('Math.abs(P.x - 35 * T) < T'), 'Tecky traverse le chenal par le pont (y = ' + (run('P.y') / run('T')).toFixed(1) + ')');
  run('va(37.5 * T, 28.9 * T); P.dir = "down";');
  step(60 * 3, 'held.down = true'); run('held.down = false');
  ok(run('P.y') < 30.2 * run('T'), 'à côté du pont, l’eau du chenal l’arrête');
  // ---- les cultures d'été, et le printemps inchangé
  ok(run('ATLAS["sol/culture_ete"].f.length === ATLAS["sol/culture"].f.length'), 'le champ a ses cultures d’été (blé, tournesols, maïs, tomates)');
  run('episode = "printemps"; newGame("aventure", true);');
  ok(run('alice.kind') === 'alice1' && run('WHO.alice.portrait') === 'hud/portrait_alice' && run('shoreLine().length') === 0
     && run('!decor.some(d => d.n === "lifeguard_chair" || d.n.startsWith("parked_"))'),
     'au printemps : Alice a sa tenue et sa chaussure perdue, pas de vagues, rien de la côte');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
