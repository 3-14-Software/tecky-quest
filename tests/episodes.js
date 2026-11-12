// les épisodes : le printemps d'abord ; le gagner ouvre le suivant, que l'écran titre propose alors ; chaque épisode a
// ses cartes, sa sauvegarde le nomme, ses records sont à part ; un épisode en chantier n'est jamais proposé
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
function main() {
  // la partie en cours est gagnée, la scène de fin passée : l'écran de victoire
  const gagner = () => {
    run('cars = []; clues = [true, true, true]; revealAlice(); P.x = alice.x - 100; P.y = alice.y + 10; P.mode = "free"; P.inv = 9;');
    step(2); advanceDialog(); run('endingDone();'); step(80);
  };
  const auTitre = () => { run('pressed.ok = true'); step(1); };
  const choisir = id => { run(`menu.sel = menu.items.findIndex(it => it.id === "${id}"); pressed.ok = true;`); step(1); advanceDialog(); };
  const fleche = k => { run(`pressed.${k} = true`); step(1); run(`pressed.${k} = false`); };

  // 1. les données, et un jeu qui n'a qu'un épisode ouvert : l'écran titre d'avant
  ok(run('EPISODES.map(e => e.id).join()') === 'printemps,ete' && run('EPISODES[0].cartes.join()') === 'monde'
     && run('EPISODES[1].cartes.join()') === 'monde,pre' && run('EPISODES[1].chantier') === true,
     'deux épisodes : le printemps (le monde), l\'été (le monde et la deuxième carte), encore en chantier');
  ok(run('state') === 'title' && run('episode') === 'printemps' && run('openEpisodes().length') === 1
     && run('menu.items.map(it => it.id).join()') === 'aventure,balade,options,badges',
     'au départ : le printemps seul, et le menu de toujours');
  fleche('right');
  ok(run('episode') === 'printemps', 'un seul épisode ouvert : gauche / droite ne changent rien');
  run('audioOn();'); choisir('aventure');
  ok(run('state') === 'play' && run('STORE.get(SAVE_KEY).ep') === 'printemps' && run('MAP.id') === 'monde',
     'nouvelle aventure : la sauvegarde nomme son épisode');
  ok(run('MAP.passages.length') === 1 && run('(P.x = MAP.w * TS - 200, passageHere())') === null,
     'au printemps, le tunnel de l\'est est fermé : la deuxième carte n\'est pas de l\'épisode');

  // 2. l'été en chantier : gagner le printemps n'ouvre rien
  gagner();
  ok(run('state') === 'win' && run('opened') === null && run('recs.aventure.wins') === 1 && run('openEpisodes().length') === 1,
     'printemps gagné, l\'été en chantier : rien ne s\'ouvre');
  auTitre();
  ok(run('state') === 'title' && run('episode') === 'printemps', 'retour au titre : toujours le printemps');

  // 3. l'été prêt : un joueur qui avait déjà gagné le printemps le trouve ouvert ; choix sur l'écran titre
  run('EPISODES[1].chantier = false; toTitle();');
  ok(run('openEpisodes().map(e => e.id).join()') === 'printemps,ete' && run('episode') === 'printemps',
     'l\'été sorti du chantier : ouvert pour qui a déjà gagné le printemps');
  fleche('right');
  ok(run('episode') === 'ete' && run('episodeLabel()') === 'L’été · Tecky à la mer', 'droite : « ' + run('episodeLabel()') + ' »');
  fleche('right');
  ok(run('episode') === 'printemps' && run('episodeLabel()') === 'Le printemps · Tecky cherche Alice', 'encore : on revient au printemps');
  fleche('left');
  ok(run('episode') === 'ete', 'gauche : l\'été');
  ok(run('episodeTap(GW / 2 - 200, 460)') === true && run('episode') === 'printemps'
     && run('episodeTap(GW / 2 + 200, 460)') === true && run('episode') === 'ete'
     && run('episodeTap(GW / 2, 700)') === false && run('episode') === 'ete',
     'au toucher : la moitié gauche ou droite de la ligne ; ailleurs, rien');
  ok(run('recordLine("aventure")') === '' && run('(episode = "printemps", recordLine("aventure"))') !== '' && run('(episode = "ete", true)'),
     'les records affichés sont ceux de l\'épisode choisi');

  // 4. une partie de l'été
  choisir('aventure');
  ok(run('state') === 'play' && run('episode') === 'ete' && run('MAP.id') === 'monde' && run('STORE.get(SAVE_KEY).ep') === 'ete'
     && run('P.hpMax') === run('START_BONES * 2') && run('score') === 0,
     'nouvelle aventure en été : une partie neuve, à la niche');
  ok(run('(P.x = MAP.w * TS - 200, passageHere() || [])[1]') === 'pre', 'en été, le tunnel de l\'est mène à la deuxième carte');
  run('P.x = MAP.start[0]; P.y = MAP.start[1]; score = 77; saveGame(); toTitle();');
  ok(run('episode') === 'ete' && run('menu.items[0].id') === 'continue' && run('menu.items[0].sub').startsWith('L’été · '),
     'menu principal : « Continuer » dit de quel épisode (' + run('menu.items[0].sub') + ')');
  fleche('left'); choisir('continue');
  ok(run('episode') === 'ete' && run('score') === 77, 'Continuer reprend l\'épisode de la sauvegarde, pas celui qui était choisi');
  run('newGame("balade", true);'); advanceDialog(); gagner();
  ok(run('state') === 'win' && run('recs["ete:balade"].wins') === 1 && run('recs.aventure.wins') === 1 && !run('recs.balade')
     && run('opened') === null, 'été gagné en balade : ses records à part (« ete:balade »), ceux du printemps intacts');
  auTitre();

  // 5. progression effacée : le printemps seul ; le gagner (même en balade) ouvre l'été, annoncé et proposé
  run('resetProgress(); toTitle();');
  ok(run('episode') === 'printemps' && run('openEpisodes().length') === 1 && !run('loadSave()'), 'progression effacée : le printemps seul');
  choisir('balade'); gagner();
  ok(run('state') === 'win' && run('opened') === 'ete' && run('txt("victoire.episode", { nom: txt("episodes." + opened + ".nom") })') === 'Nouvel épisode : L’été !',
     'printemps gagné en balade : « Nouvel épisode : L’été ! »');
  auTitre();
  ok(run('state') === 'title' && run('episode') === 'ete' && run('opened') === null && run('openEpisodes().length') === 2,
     'retour au titre : l\'été est ouvert, et c\'est lui qui est proposé');

  // 6. une sauvegarde sur une carte qui n'est plus de son épisode : la partie reprend à la niche
  choisir('aventure');
  run('items.splice(0, 1); score = 55; var nItems = items.length; travel("pre", 0); saveGame();');
  run('var S = STORE.get(SAVE_KEY); S.ep = "printemps"; STORE.set(SAVE_KEY, S); toTitle(); loadGame(loadSave(), false);'); advanceDialog();
  ok(run('episode') === 'printemps' && run('MAP.id') === 'monde' && run('Math.abs(P.x - MAP.start[0]) < 1 && Math.abs(P.y - MAP.start[1]) < 1')
     && run('score') === 55 && run('items.length') === run('nItems') && run('Object.keys(elsewhere).length') === 0,
     'elle reprend à la niche, score gardé, le monde comme Tecky l\'avait laissé');
  run('saveGame(); S = STORE.get(SAVE_KEY); S.ep = "zzz"; STORE.set(SAVE_KEY, S); toTitle(); loadGame(loadSave(), false);'); advanceDialog();
  ok(run('episode') === 'printemps' && run('state') === 'play', 'un épisode inconnu dans la sauvegarde : le premier');

  // au chargement de la page : l'épisode de la partie à continuer ; sans partie, le dernier ouvert
  ok(run('epOfSave({ ep: "ete" })') === 'ete' && run('epOfSave({})') === 'printemps' && run('lastOpen()') === 'ete',
     'au chargement : l\'épisode de la sauvegarde (le premier pour une sauvegarde d\'avant), sinon le dernier ouvert');

  // 7. un épisode retourné en chantier n'est plus proposé
  run('episode = "ete"; EPISODES[1].chantier = true; toTitle();');
  ok(run('episode') === 'printemps' && run('openEpisodes().length') === 1, 'été remis en chantier : le titre revient au printemps');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
