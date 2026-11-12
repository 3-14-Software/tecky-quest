// les saisons : chaque épisode a la sienne ; ses images (tileset, sprites aux couleurs de la saison) se chargent à
// côté de la page et remplacent celles du printemps ; sans elles, le monde garde les couleurs d'avant
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
async function main() {
  const attendre = () => new Promise(r => setTimeout(r, 5));            // (laisse arriver les images demandées)
  // ce que blit() lit pour un sprite : [image, x, y] de la source
  run('var lu = k => { let a; blit({ drawImage: (...q) => { a = q; } }, ATLAS[k].f[0], 0, 0, 10, 10); return a; };');
  ok(run('Object.keys(SAISONS).join()') === 'ete' && run('Object.keys(SAISONS.ete.meta).length') >= 10
     && run('Object.values(SAISONS.ete.meta).every(v => v.f.every(f => f[1] >= SEASON_Y))'),
     'la page connaît les images de l\'été : ' + run('Object.keys(SAISONS.ete.meta).length') + ' sprites, un tileset');
  ok(run('season') === null && run('groundTiles() === tilesImg') && run('lu("decor/chene")[0] === atlas'), 'au printemps : les images de la page');

  // l'été : ses images arrivent, ATLAS change pour ses sprites, le sol se repeint
  run('EPISODES[1].chantier = false; recs = { aventure: { wins: 1 } }; STORE.set(RECORDS_KEY, recs); toTitle(); var y0 = ATLAS["decor/chene"].f[0][1];');
  step(2);
  ok(run('ground.size') > 0 && run('season') === null, 'écran titre du printemps : le sol est peint');
  run('stepEpisode(1);'); step(1);
  ok(run('episode') === 'ete' && run('seasonAsked') === 'ete' && run('season') === null, 'choisir l\'été : ses images sont demandées, le printemps reste en attendant');
  await attendre();
  ok(run('season && season.nom') === 'ete' && run('ATLAS["decor/chene"].f[0][1] >= SEASON_Y') && run('ATLAS["tecky/idle/down"].f[0][1] < SEASON_Y')
     && run('ground.size') === 0 && run('mapImg') === null,
     'images arrivées : les arbres se lisent dans l\'image de l\'été (pas Tecky), le sol est à repeindre');
  ok(run('lu("decor/chene")[0] === season.img') && run('lu("decor/chene")[2]') === run('ATLAS["decor/chene"].f[0][1] - SEASON_Y')
     && run('lu("tecky/idle/down")[0] === atlas') && run('groundTiles() === season.tiles') && run('season.img.src').startsWith('saison_ete_atlas.png'),
     'blit() : un sprite de saison dans son image, les autres dans l\'atlas ; le sol avec les tuiles de l\'été');
  step(3);
  run('audioOn(); menu.sel = menu.items.findIndex(it => it.id === "balade"); pressed.ok = true;'); step(1); advanceDialog();
  step(30);
  run('state = "pause"; openPauseMenu(); render(); state = "play"; menu = null;');
  ok(run('state') === 'play' && run('season.nom') === 'ete' && run('ground.size') > 0 && run('mapImg !== null'), 'une partie d\'été se joue et se dessine (sol, ombres, carte de la pause)');

  // images nettes : la saison sans les siennes est retirée, redemandée, et revient avec ses pages
  if (!run('!!SAISONS.ete.hd')) console.log('ok : pas d\'images x4 (jeu construit avec --sans-hd)');
  else {
  run('var P4 = [new Image(), new Image()], T4 = new Image(); setHD(2, 2048, P4, T4);');
  ok(run('season') === null && run('ATLAS["decor/chene"].f[0][1]') === run('y0') && run('lu("decor/chene")[0] === P4[0]'),
     'images nettes posées : l\'été, qui n\'a pas encore les siennes, s\'efface (jamais un sprite x2 parmi les x4)');
  // (HD.on, que le dessin de l'interface éteint à chaque image, ne doit pas compter : seulement HD.k)
  run('HD.on = false;'); step(1); await attendre(); run('HD.on = true;');
  ok(run('season && season.nom') === 'ete' && run('season.pages.length') === run('SAISONS.ete.hd.atlas.length')
     && run('lu("decor/chene")[0] === season.pages[0]') && run('lu("decor/chene")[1]') === run('ATLAS["decor/chene"].f[0][0] * 2')
     && run('groundTiles() === season.tilesHD') && run('lu("tecky/idle/down")[0] === P4[Math.floor(ATLAS["tecky/idle/down"].f[0][1] / 2048)]'),
     'il revient avec ses images nettes : blit() lit sa page x4, le sol son tileset x4');
  }

  // retour au printemps : tout de suite, ATLAS comme avant
  run('toTitle(); stepEpisode(-1);'); step(1);
  ok(run('episode') === 'printemps' && run('season') === null && run('ATLAS["decor/chene"].f[0][1]') === run('y0')
     && run('Object.keys(springFrames).length') === 0 && run('groundTiles() === (HD.k > 1 ? HD.tiles : tilesImg)'), 'retour au printemps : sans attendre, ATLAS comme avant');
  run('stepEpisode(1);'); step(1); await attendre();
  ok(run('season && season.nom') === 'ete', 'l\'été de nouveau : ses images, déjà chargées');

  // fichiers absents : le monde garde ses couleurs, rien ne casse, et on peut réessayer
  run('stepEpisode(-1);'); step(1);
  run('for (const k in seasons) delete seasons[k]; var Bonne = Image; Image = class { set src(v) { setTimeout(() => this.onerror && this.onerror(new Error("absent")), 0); } };');
  run('stepEpisode(1);'); step(1); await attendre(); step(5);
  ok(run('episode') === 'ete' && run('season') === null && run('state') === 'title' && run('seasons.ete.p2') === null,
     'images de l\'été introuvables : la partie continue aux couleurs du printemps');
  run('Image = Bonne; seasonAsked = null;'); step(1); await attendre();
  ok(run('season && season.nom') === 'ete', 'fichiers revenus : la saison se pose à la demande suivante');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
