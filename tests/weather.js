// météo : averses (gouttes, flaques, plouf, arc-en-ciel, Tecky s'ébroue), neige (flocons, sol blanc), réglage
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  run('dogs = []; cars = []; P.inv = 999; P.x = 8 * 64; P.y = 5 * 64 + 32; P.mode = "free"; var used = [], ds0 = drawSpr;');
  const spy = () => run('used = []; drawSpr = function (k) { used.push(k); return ds0.apply(this, arguments); }; render(); drawSpr = ds0;');
  ok(run('opts.weather') === 'auto' && run('weather.k') === 0 && run('weather.timer') > 30, 'auto : beau temps au départ, une averse plus tard');
  ok(run('["fx/puddle", "fx/splash", "fx/drop", "fx/snowflake", "tecky/shake/down"].every(k => ATLAS[k])'), 'sprites de la météo');
  // pluie
  run('opts.weather = "pluie";'); step(60 * 8);
  ok(run('weather.kind') === 'rain' && run('weather.k') === 1, 'Pluie : l’averse arrive');
  ok(run('weatherTint()[0]') < 230, 'le temps se couvre (teinte ' + run('JSON.stringify(weatherTint().map(Math.round))') + ')');
  ok(run('fxs.some(f => f.key === "fx/splash")'), 'des gouttes éclaboussent le sol');
  ok(run('Ambience.rainLevel') > 0.03, 'on entend la pluie');
  step(60 * 20);
  ok(run('weather.wet') > 0.6, 'les flaques se remplissent (' + run('weather.wet').toFixed(2) + ')');
  run('buildPuddles(); var pd = puddles.find(p => Math.abs(p.x - 12 * 64) < 900 && Math.abs(p.y - 8 * 64) < 500) || puddles[0]; P.x = pd.x - 40; P.y = pd.y; camX = P.x - VW / 2; camY = P.y - VH / 2;');
  ok(run('puddles.length') > 40 && run('puddles.every(p => !waterAt(p.x, p.y) && !blockedFeet(p.x, p.y, 30))'), run('puddles.length') + ' flaques possibles, jamais dans l’eau ni sous un décor');
  spy();
  ok(run('used.includes("fx/puddle")'), 'flaques dessinées');
  run('fxs = []; P.plopT = 0;');
  let plop = false;
  for (let i = 0; i < 20; i++) { step(1, 'held.right = true'); if (run('fxs.some(f => f.key === "fx/splash" && Math.abs(f.x - pd.x) < 50 && Math.abs(f.y - pd.y) < 10)')) plop = true; }
  run('held.right = false');
  ok(plop, 'Tecky marche dans la flaque : plouf');
  // fin de l'averse : arc-en-ciel, Tecky s'ébroue
  run('opts.weather = "soleil"; P.mode = "free";');
  let shook = false;
  for (let i = 0; i < 60 * 8; i++) { step(1); if (run('P.anim') === 'shake') shook = true; }
  ok(run('weather.k') === 0 && run('weather.bow') > 0, 'le soleil revient : arc-en-ciel');
  ok(shook && run('P.mode') === 'free', 'Tecky s’ébroue, puis repart');
  step(60 * 40);
  ok(run('weather.wet') < 0.8 && run('weather.bow') === 0, 'les flaques sèchent, l’arc-en-ciel s’efface');
  // neige
  run('opts.weather = "neige";'); step(60 * 8);
  ok(run('weather.kind') === 'snow' && run('weather.k') === 1 && run('Ambience.rainLevel') === 0, 'Neige : il neige, sans bruit de pluie');
  spy();
  ok(run('Math.round(flakes.length * snowNow())') > 100 && run('flakes.every(f => f.x > -40 && f.x < VW + 40)'), 'des flocons (' + run('Math.round(flakes.length * snowNow())') + ')');
  step(60 * 40);
  ok(run('weather.cover') > 0.3, 'le sol blanchit (' + run('weather.cover').toFixed(2) + ')');
  // auto : averse au bout d'un moment, neige en décembre
  run('opts.weather = "auto"; resetWeather(); weather.timer = 1;'); step(60 * 3);
  ok(run('weather.on') && run('weather.kind') === (new Date().getMonth() === 11 ? 'snow' : 'rain'), 'auto : une averse arrive');
  run('december = () => true; resetWeather(); weather.timer = 1;'); step(60 * 3);
  ok(run('weather.kind') === 'snow', 'auto en décembre : de la neige');
  run('december = () => false; resetWeather(); weather.timer = 1;'); step(60 * 3);
  ok(run('weather.kind') === 'rain', 'le reste de l’année : de la pluie');
  ok(run('weather.timer') > 30, 'l’averse dure un moment (' + Math.round(run('weather.timer')) + ' s)');
  // lampadaires allumés (coucher de soleil, nuit) : plus d'arc-en-ciel
  run('var arcs = 0; ctx.arc = () => arcs++; sun = 0; weather.bow = 0.8; drawRainbow();');
  ok(run('arcs') > 0, 'en plein jour : l’arc-en-ciel est dessiné');
  run('arcs = 0; sun = SUN.lamp + 0.25; drawRainbow();');
  ok(run('arcs') > 0, 'les lampadaires s’allument : il pâlit…');
  run('arcs = 0; sun = SUN.lamp + 0.6; drawRainbow();');
  ok(run('arcs') === 0, '… et disparaît');
  run('opts.weather = "pluie"; resetWeather(); clues = [true, true, true]; sun = 3;'); step(60 * 10);
  ok(run('weather.k') === 1 && run('lampsOn()'), 'une averse la nuit');
  run('opts.weather = "soleil";'); step(60 * 8);
  ok(run('weather.k') === 0 && run('weather.bow') === 0, 'elle finit : pas d’arc-en-ciel la nuit');
  run('delete ctx.arc; opts.weather = "auto";');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
