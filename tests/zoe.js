// la quête des lettres rejouée sur la côte avec d'autres acteurs (MAP.roles) : Zoé, une petite fille, bâtit un château
// de sable ; ses cinq coquillages sont enfouis dans la plage. Tecky gratte, le coquillage sort, il le ramasse.
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('EPISODES[1].chantier = false; audioOn(); STORE.mem = {}; loadBadges(); episode = "ete"; newGame("balade", true);'); advanceDialog();
  run('cars = []; dogs = []; P.inv = 99;');
  ok(run('MAP.roles.postman') === 'zoe' && run('postman.kind') === 'postman' && run('postman.look') === 'zoe' && run('shells()') && run('letters.length') === 5
     && run('letters.every(l => l.shell && !l.dug && !l.got && sandAt(l.x, l.y))') && run('npcList().length') === 3,
     'sur la côte, le rôle de Marcel est tenu par Zoé, celui des lettres par cinq coquillages enfouis dans le sable');
  ok(['zoe/idle', 'zoe/talk', 'zoe/wave', 'zoe/cheer', 'hud/portrait_zoe', 'item/shell', 'sable/butte', 'fx/sand', 'decor/chateau_de_sable', 'decor/chateau_de_sable_fini']
       .every(k => run(`!!ATLAS[${JSON.stringify(k)}]`)) && run('ATLAS["item/shell"].f.length') === 5 && run('MAP.shellBase.length') === 5
     && run('WHO.zoe.name') === 'Zoé' && run('calmAt(postman.x, postman.y)') && run('decor.some(d => d.n === "sandcastle" && d.key === "decor/chateau_de_sable")'),
     'ils ont leurs dessins : Zoé, son portrait, cinq coquillages, la butte de sable, le château ; elle est en zone calme');
  // un coquillage enfoui ne se ramasse pas en passant : il faut gratter
  run('var L = letters[0]; P.x = L.x; P.y = L.y + 20; P.mode = "free";'); step(20);
  ok(run('!L.got && !L.dug') && run('biteAction()') === 'dig' && run('nearDig() === L'), 'en passant dessus, rien : il est sous le sable ; C propose de gratter');
  run('var fx0 = []; var af0 = addFx; addFx = function (k) { fx0.push(k); return af0.apply(this, arguments); }; pressed.bite = true;'); step(1);
  ok(run('P.mode') === 'dig', 'Tecky gratte');
  run('P.x = L.x + 70; P.y = L.y + 6;');               // (à portée de grattage, hors de portée de ramassage)
  let t = 0; while (run('!L.dug') && t++ < 200) step(1);
  ok(run('L.dug && !L.got && L.wait > 0') && run('fx0.includes("fx/sand") && !fx0.includes("fx/dirt")'), 'le coquillage saute du sable (une gerbe de sable, pas de terre)');
  step(60);
  ok(run('!L.got && L.up === 0'), 'il retombe et attend');
  run('P.x = L.x; P.y = L.y + 20;'); step(3);
  ok(run('L.got') && run('pops.some(p => p.text === txt("coquillages.premiere"))'), 'Tecky le ramasse : « ' + run('txt("coquillages.premiere")') + ' »');
  // la demande
  run('P.x = postman.x - 60; P.y = postman.y + 40; talkTo(postman);');
  ok(run('state') === 'dialog' && run('dialog.lines[0].who') === 'zoe' && run('dialog.lines[1].text') === run('txt("zoe.deja", { n: 1 })'),
     'Zoé demande : « ' + run('dialog.lines[1].text') + ' »');
  advanceDialog();
  ok(run('post.state') === 'asked' && run('hudCounters().some(c => c[0] === "item/shell" && c[4] === 1 && c[5] === 5)'), 'quête en cours : compteur 1 / 5, avec un coquillage');
  // sauvegarde : un coquillage sorti du sable mais pas ramassé le reste
  run('uncoverShell(letters[1]); saveGame(); var S = loadSave(); loadGame(S);'); advanceDialog();
  ok(run('letters[0].got && letters[1].dug && !letters[1].got && !letters[2].dug') && run('post.state') === 'asked', 'partie reprise : ramassé, sorti, enfoui — chacun à sa place');
  // les quatre autres
  run('cars = []; dogs = []; for (const l of letters) if (!l.got) { l.dug = true; l.wait = 0; }');
  for (let i = 1; i < 5; i++) { run(`P.x = letters[${i}].x; P.y = letters[${i}].y + 20; P.mode = "free";`); step(3); }
  ok(run('lettersLeft()') === 0 && run('postman.waveT') > 0, 'les cinq sont ramassés : Zoé appelle Tecky');
  run('var sc0 = score, n0 = items.length; P.x = postman.x - 60; P.y = postman.y + 40; talkTo(postman);');
  ok(run('dialog.lines[0].text') === run('txt("zoe.merci.0")'), 'elle remercie : « ' + run('dialog.lines[0].text') + ' »');
  advanceDialog(); run('checkBadges();');
  ok(run('post.state') === 'done' && run('score') === run('sc0 + POST.reward') && run('items.length') === run('n0 + 1')
     && run('!!badges.coquillages && !badges.facteur') && run('decor.some(d => d.n === "sandcastle" && d.key === "decor/chateau_de_sable_fini")')
     && run('questsHere().length') === 3,
     'quête finie : des points, un os, le badge « Chercheur de coquillages », et le château est paré de coquillages');
  run('saveGame(); var S2 = loadSave(); loadGame(S2);'); advanceDialog();
  ok(run('post.state') === 'done' && run('decor.some(d => d.key === "decor/chateau_de_sable_fini")'), 'partie reprise : le château garde sa parure');
  run('render();');
  // au printemps, rien ne change : les lettres de Marcel se ramassent en passant
  run('episode = "printemps"; newGame("balade", true);'); advanceDialog();
  ok(run('!shells()') && run('postman.look') === 'postman' && run('letters.every(l => l.dug && !l.shell)') && run('MAP.sand.length') === 0, 'dans le monde : Marcel et ses lettres, comme avant');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
