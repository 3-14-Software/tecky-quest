// la fin : après les retrouvailles, Tecky et Alice rentrent à la niche (lucioles, berceuse, iris, « Fin »), puis la victoire
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); pressed.ok = true'); step(1); advanceDialog();
  const finale = () => {
    run('cars = []; clues = [true, true, true]; revealAlice(); P.x = alice.x - 100; P.y = alice.y + 10; P.mode = "free"; P.inv = 9;');
    step(2); advanceDialog();
  };
  finale();
  ok(run('state') === 'ending' && run('Music.cur') === 'end' && run('Music.on'), 'fin du dialogue : la scène de fin, avec la berceuse');
  ok(run('SONGS.berceuse.bpm') < run('SONGS.base.bpm') && run('SONGS.berceuse.ev.every(e => e[1] !== "drums")'),
     'berceuse : plus lente, sans batterie');
  run('onLeave();');
  ok(run('state') === 'ending', 'pas de pause automatique pendant la fin');
  step(70);
  ok(run('ending.home') && run('sun') === 4 && run('butterflies.length') === 0, 'au noir : tout le monde à la niche, la nuit');
  ok(run('dogs.every(d => d.x > camX + VW || d.y > camY + VH)'), 'aucun chien dans la scène');
  ok(run('alice.y') > run('ENDING.alice[1]') && run('alice.anim') === 'walk' && run('P.anim') === 'walk', 'ils remontent le chemin');
  ok(run('Math.abs(camX - clamp(ENDING.alice[0] - VW / 2, 0, MAP.w * TS - VW)) < 1'), 'la caméra regarde la niche');
  step(60 * 7);
  ok(run('alice.y') === run('ENDING.alice[1]') && run('alice.dir') === 'down', 'Alice arrive devant la niche');
  ok(run('P.anim') === 'sleep' && run('P.dir') === 'left' && run('fxs.some(f => f.key === "fx/zzz")'), 'Tecky s’endort à ses pieds (des « z »)');
  ok(run('ending.flies.length') === run('ENDING.flies'), 'des lucioles');
  step(Math.ceil(60 * (run('endingEnd()') - run('ending.t'))) + 2);
  ok(run('state') === 'win' && run('fade.a') > 0.5, 'puis l’écran de victoire, qui sort du noir');
  ok(run('P.anim') === 'sleep' && run('Music.cur') === 'end', 'Tecky dort toujours, la berceuse continue');
  // complétion : un pourcentage sur l'écran de victoire
  const pc = run('completion()');
  run('var said = []; ctx.fillText = s => said.push(String(s)); overT = 2; render(); delete ctx.fillText;');
  ok(pc >= 0 && pc < 100 && run(`said.includes("Aventure complétée") && said.includes("${pc}\u00a0%")`), 'écran de victoire : aventure complétée à ' + pc + ' %');
  run('treasures = MAP.dig.length; farm.state = post.state = rose.state = "done";' +
      'critters.forEach(c => c.scored = true); ducks.forEach(d => d.scored = true); seenCells.fill(1);');
  ok(run('completion()') === 100, 'tout trouvé, toutes les quêtes, toute la carte : 100 %');
  run('farm.state = "new";');
  ok(run('completion()') < 100 && run('completion()') > 90, 'une quête de moins : ' + run('completion()') + ' %');
  run('Music.step = Music.song.total - 1;'); step(30);
  ok(run('Music.on') && run('Music.step') < 20, 'la berceuse boucle');
  step(40); run('pressed.ok = true'); step(1);
  ok(run('state') === 'title' && run('Music.cur') === 'main', 'retour au menu : le thème');
  // un bouton passe la scène (pas tout de suite : l'appui qui ferme le dialogue ne doit pas la sauter)
  run('newGame("aventure", true);'); advanceDialog(); finale();
  run('pressed.ok = true'); step(1);
  ok(run('state') === 'ending', 'appui dès le début : la scène continue');
  step(60); run('pressed.bite = true'); step(1);
  ok(run('state') === 'win' && run('alice.x') === run('ENDING.alice[0]') && run('P.anim') === 'sleep', 'ensuite : directement la victoire, à la niche');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
