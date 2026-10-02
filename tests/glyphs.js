// icônes de touches et de boutons dans les textes d'aide : « [ok] pour valider » -> touche Entrée ou bouton A
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  run('audioOn(); touchMode = false; pad.on = false;');
  // chaque action a une image, au clavier comme à la manette
  for (const p of [false, true]) {
    ok(run(`pad.on = ${p}; Object.keys(GLYPH).every(n => glyphIcons(n).every(alt => alt.every(([s, i]) => i >= 0 && ATLAS[s].f[i])))`),
       (p ? 'manette' : 'clavier') + ' : chaque [action] a son image');
  }
  run('pad.on = false;');
  ok(run('JSON.stringify(richParts("[ok] pour valider"))') === JSON.stringify([[[['hud/key', run('MAP.keys.indexOf("Entrée")')]]], ' pour valider']),
     'au clavier : [ok] = la touche Entrée');
  ok(run('JSON.stringify(glyphIcons("walk").map(a => a.length))') === '[1,1]' && run('glyphIcons("updown")[0].length') === 2,
     '« a/b » : deux icônes au choix ; « a+b » : côte à côte');
  run('pad.on = true;');
  ok(run('JSON.stringify(glyphIcons("ok"))') === JSON.stringify([[['hud/pad', 0]]]), 'à la manette : [ok] = le bouton A');
  ok(run('glyphFrame("fs")[0]') === 'hud/key', 'sans bouton de manette (plein écran) : la touche');
  ok(run('JSON.stringify(richParts("[zzz] reste"))') === '["[zzz] reste"]', 'un mot inconnu entre crochets reste du texte');
  ok(run('richWidth("[ok]", 26)') > 0 && run('richWidth("[ok] pour", 26)') > run('richWidth("[ok]", 26)'), 'largeur d’un texte avec icônes');
  // la réplique s'écrit lettre à lettre sans jamais couper une [action]
  run('pad.on = false;');
  const intro = run('introLines()[3].text + introLines()[4].text');
  ok(intro.includes('[walk]') && intro.includes('[bite]'), 'l’aide de l’introduction passe par les icônes');
  let cut = false;
  for (let n = 0; n <= intro.length; n++) {
    const t = run(`typed(introLines()[3].text + introLines()[4].text, ${n})`);
    if (t.lastIndexOf('[') > t.lastIndexOf(']')) cut = true;
  }
  ok(!cut, 'frappe lettre à lettre : une [action] apparaît d’un bloc');
  // aucun écran n'affiche une [action] telle quelle, et les icônes sont bien dessinées
  run('var said = []; ctx.fillText = s => said.push(String(s)); var rich = 0, dr0 = drawRich;' +
      'drawRich = function () { rich++; return dr0.apply(this, arguments); };');
  const screens = {
    'écran titre': 'toTitle();',
    'pause': 'newGame("aventure", true); dialog = null; state = "pause"; openPauseMenu();',
    'options': 'openOptions("pause"); optSel = 0; fsRefusedAt = performance.now();',
    'badges': 'state = "badges";',
    'victoire': 'state = "win"; overT = 2.6;',
    'son coupé': 'state = "play"; muted = true;',
    'introduction': 'muted = false; newGame("aventure", false); dialog.i = 3; dialog.c = 9999; state = "dialog";',
    'introduction (bouton de morsure)': 'dialog.i = 4; dialog.c = 9999;',
  };
  for (const p of [false, true]) {
    for (const [name, setup] of Object.entries(screens)) {
      run(`pad.on = ${p}; touchMode = false; ${setup} said = []; rich = 0; render();`);
      ok(run('rich') > 0 && run('!said.some(s => /\\[[a-z]+\\]/.test(s))'),
         `${p ? 'manette' : 'clavier'}, ${name} : icônes dessinées, aucune [action] en toutes lettres`);
    }
  }
  run('drawRich = dr0;');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
