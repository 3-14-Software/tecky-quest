// la quête de Pompon rejouée sur la côte avec d'autres acteurs (MAP.roles) : Madame Hortense, devant le casino, a
// perdu Praline, son caniche, dans les jardins ; même mécanique, autres dessins, autres textes, autre compteur
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('EPISODES[1].chantier = false; audioOn(); episode = "ete"; newGame("balade", true);'); advanceDialog();
  run('cars = []; dogs = []; P.inv = 99;');
  ok(run('MAP.id') === 'cote' && run('MAP.roles.neighbor') === 'hortense' && run('MAP.roles.pompon') === 'poodle' && run('JSON.stringify(CARTES.monde.roles)') === '{}'
     && run('neighbor.kind') === 'neighbor' && run('neighbor.look') === 'hortense' && run('pompon.kind') === 'poodle' && run('npcList().includes(neighbor)'),
     'sur la côte, le rôle de Mamie Rose est tenu par Madame Hortense, celui de Pompon par Praline, son caniche');
  ok(['hortense/idle', 'hortense/talk', 'hortense/worry', 'poodle/idle', 'poodle/walk', 'poodle/run', 'poodle/hiss', 'icone/poodle', 'hud/portrait_hortense']
       .every(k => run(`!!ATLAS[${JSON.stringify(k)}]`)) && run('WHO.hortense.name') === 'Madame Hortense' && run('calmAt(neighbor.x, neighbor.y)'),
     'ils ont leurs dessins, leur portrait, leur icône de compteur ; elle est en zone calme');
  // la demande
  run('P.x = neighbor.x - 60; P.y = neighbor.y + 40; P.mode = "free";'); step(2);
  ok(run('biteAction()') === 'talk' && run('neighborMark()') === 0, 'près d\'elle : « Parler », et sa bulle « ! »');
  run('talkTo(neighbor);');
  ok(run('state') === 'dialog' && run('dialog.lines[0].who') === 'hortense' && run('dialog.lines[0].text') === run('txt("hortense.demande.0")') && run('dialog.lines.length') === 3,
     'elle demande : « ' + run('dialog.lines[0].text') + ' »');
  step(3);
  ok(run('neighbor.anim') === 'talk', 'elle parle (son animation)');
  advanceDialog();
  ok(run('rose.state') === 'asked' && run('hudCounters().some(c => c[0] === "icone/poodle" && c[4] === 0)') && run('neighbor.worried'), 'quête en cours : le compteur du caniche, à 0 / 1 ; elle s\'inquiète');
  // Tecky retrouve Praline dans les jardins
  run('P.x = pompon.x - 70; P.y = pompon.y + 20; pops = [];'); step(3);
  ok(run('state') === 'dialog' && run('dialog.lines[0].text') === run('txt("tecky.praline")') && run('pops.some(p => p.text === txt("caniche.miaou") && p.who === "poodle")'),
     'il la trouve : « ' + run('dialog.lines[0].text') + ' », et elle jappe (« ' + run('txt("caniche.miaou")') + ' »)');
  advanceDialog();
  ok(run('pompon.mode') === 'follow' && run('hudCounters().some(c => c[0] === "icone/poodle" && c[4] === 1)'), 'elle le suit ; compteur à 1 / 1');
  step(40, 'held.left = true;'); run('held.left = false;');
  ok(run('dist(pompon.x, pompon.y, P.x, P.y)') < 200 && ['walk', 'run', 'idle'].includes(run('pompon.anim')), 'elle marche sur ses traces');
  // retour auprès de Madame Hortense
  run('P.x = neighbor.x - 90; P.y = neighbor.y + 70; crumbs = []; pompon.x = P.x - 50; pompon.y = P.y; pops = [];'); step(40);
  ok(run('pompon.mode') === 'home' && run('pops.some(p => p.text === txt("hortense.viens") && p.who === "hortense")') && run('neighbor.cheerT') > 0,
     'arrivée près d\'elle, Praline reste : « ' + run('txt("hortense.viens")') + ' »');
  run('var sc0 = score, n0 = items.length, b0 = JSON.stringify(badges); talkTo(neighbor);');
  ok(run('state') === 'dialog' && run('dialog.lines[0].text') === run('txt("hortense.merci.0")'), 'elle remercie : « ' + run('dialog.lines[0].text') + ' »');
  advanceDialog(); run('checkBadges();');
  ok(run('rose.state') === 'done' && run('score') === run('sc0 + POST.reward') && run('items.length') === run('n0 + 1') && run('items[items.length - 1].n') === 'sausage'
     && run('!badges.chat && !!badges.caniche') && run('JSON.stringify(badges)') !== run('b0'), 'quête finie : des points, une saucisse, le badge « Ami des caniches » (« Ami des chats » reste celui de Pompon)');
  ok(run('questsHere().length') === 6 && run('questsHere().filter(q => q()).length') === 1 && run('QUESTS_DONE.length') === 6, 'pour la complétion, seules comptent les quêtes de cette carte (six, dont celle-ci, finie)');
  run('saveGame(); var S = loadSave();');
  ok(run('S.rose') === 'done' && run('S.cat[2]') === 'home', 'sauvegardé comme la quête de Pompon (rose, cat)');
  // au printemps, rien n'a changé
  run('episode = "printemps"; newGame("aventure", true);'); advanceDialog();
  ok(run('neighbor.look') === 'neighbor' && run('pompon.kind') === 'cat_white' && run('questsHere().length') === 6 && run('nbTxt("bonjour")') === run('txt("neighbor.bonjour")')
     && run('petTxt("miaou")') === 'Miaou !', 'au printemps : Mamie Rose et Pompon, les six quêtes');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
