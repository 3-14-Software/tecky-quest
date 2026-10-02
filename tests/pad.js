// manette (API Gamepad simulée) : menus, marche au stick et à la croix, actions, pause, appui = une seule impulsion
const base = require('fs').readFileSync(__dirname + '/sim.js', 'utf8').split("setTimeout(() => {")[0];
function main() {
  // une manette « standard » : 17 boutons, 4 axes
  run('var GP = { connected: true, axes: [0, 0, 0, 0], buttons: Array.from({ length: 17 }, () => ({ pressed: false, value: 0 })) };' +
      'navigator.getGamepads = () => [null, GP];');
  // comme frame() : lecture de la manette puis mise à jour
  const pstep = n => { for (let i = 0; i < n; i++) run('pollPad(); update(1/60); render();'); };
  const btn = (i, on) => run(`GP.buttons[${i}].pressed = ${on}; GP.buttons[${i}].value = ${on ? 1 : 0};`);
  const tap = i => { btn(i, true); pstep(1); btn(i, false); pstep(1); };
  const axes = (x, y) => run(`GP.axes[0] = ${x}; GP.axes[1] = ${y};`);

  ok(run('state') === 'title' && !run('pad.on'), 'écran titre, manette pas encore utilisée');
  tap(13);
  ok(run('menu.sel') === 1 && run('pad.on'), 'croix bas : entrée suivante du menu, indices de manette affichés');
  tap(12); tap(12);
  ok(run('menu.sel') === 3, 'croix haut : le menu boucle (' + run('menu.sel') + ')');
  axes(0, 0.95); pstep(20);
  ok(run('menu.sel') === 0, 'stick incliné et tenu : une seule impulsion');
  axes(0, 0); pstep(1);
  axes(0, 0.95); pstep(2); axes(0, 0); pstep(1);
  ok(run('menu.sel') === 1, 'nouvelle inclinaison : entrée suivante');
  tap(0);
  ok(run('state') === 'dialog' && run('gameMode') === 'balade', 'A valide : nouvelle balade');
  ok(/\[walk\] pour marcher/.test(run('dialog.lines[3].text')) && /^En balade, personne ne se fait mal : \[bite\] sert à jouer/.test(run('dialog.lines[4].text')) &&
     run('glyphFrame("walk")[0]') === 'hud/pad' && run('MAP.pads[glyphFrame("bite")[1]]') === 'A',
     'l’intro explique les commandes de la manette (stick, A…)');
  for (let k = 0; k < 40 && run('state') === 'dialog'; k++) { tap(0); run('if (dialog) dialog.c = 999'); }
  ok(run('state') === 'play', 'A fait défiler les répliques');
  // (8, 5) : ligne droite dégagée sur 300 px de chaque côté
  run('dogs = []; P.x = 8 * 64; P.y = 5 * 64 + 32; P.mode = "free"; var x0 = P.x;');
  axes(0.95, 0); pstep(60); axes(0, 0); pstep(1);
  const full = run('P.x - x0');
  ok(full > 200 && run('P.dir') === 'right', 'stick à droite : Tecky marche (' + Math.round(full) + ' px en 1 s)');
  run('P.x = 8 * 64 + 200; x0 = P.x'); axes(-0.45, 0); pstep(60); axes(0, 0); pstep(1);
  const slow = run('x0 - P.x');
  ok(slow > 20 && slow < full * 0.6, 'stick à moitié : il marche plus lentement (' + Math.round(slow) + ' px)');
  run('x0 = P.y'); btn(13, true); pstep(30); btn(13, false); pstep(1);
  ok(run('P.y') > run('x0') + 80, 'croix bas : Tecky descend');
  axes(0.1, -0.12); run('x0 = P.x'); pstep(30);
  ok(run('P.x') === run('x0'), 'zone morte : un stick à peine décentré ne fait pas bouger Tecky');
  axes(0, 0);
  // actions
  run('P.cdBark = 0'); tap(2);
  ok(run('P.mode') === 'bark', 'X aboie');
  pstep(40); run('P.cdBark = 0'); tap(1);
  ok(run('P.mode') === 'bark', 'B aboie aussi');
  pstep(40); run('P.cdBite = 0; var nb = 0, db0 = doBite; doBite = function () { nb++; return db0(); };');
  btn(0, true); pstep(60); btn(0, false); pstep(1);
  run('doBite = db0');
  ok(run('nb') === 1, 'A tenu une seconde : une seule morsure (' + run('nb') + ')');
  tap(9);
  ok(run('state') === 'pause', 'Start : pause');
  // menu de la pause, en ligne : le stick à gauche / à droite change d'entrée, comme la croix
  run('menu.sel = 0;'); axes(0.95, 0.1); pstep(20);
  ok(run('menu.sel') === 1, 'pause : stick à droite (tenu) : entrée suivante, une seule fois');
  axes(0, 0); pstep(1); axes(-0.9, 0.2); pstep(2); axes(0, 0); pstep(1);
  ok(run('menu.sel') === 0, 'stick à gauche : entrée précédente');
  axes(0.7, 0.75); pstep(2); axes(0, 0); pstep(1);
  ok(run('menu.sel') === 1, 'en diagonale : un seul pas (l’axe principal), pas deux');
  run('menu.sel = 0;');
  tap(9);
  ok(run('state') === 'play', 'Start : reprise');
  tap(9); tap(0);
  ok(run('state') === 'play', 'A reprend aussi');
  tap(8);
  ok(run('muted'), 'Select coupe le son');
  tap(8);
  // indices à l'écran : boutons de manette au lieu des touches
  run('var used = []; var ds0 = drawSpr; drawSpr = function (k, f) { used.push(k + ":" + f); return ds0.apply(this, arguments); }; drawHUD(); drawSpr = ds0;');
  ok(run('used.includes("hud/pad:2") && used.includes("hud/pad:0") && !used.some(u => u.startsWith("hud/key"))'),
     'HUD : X (aboyer) et A (mordre) au lieu de X et C');
  run('pad.on = false; used = []; drawSpr = function (k, f) { used.push(k + ":" + f); return ds0.apply(this, arguments); }; drawHUD(); drawSpr = ds0;');
  ok(run('used.includes("hud/key:0") && used.includes("hud/key:1")'), 'au clavier : touches X et C');
  // manette débranchée en cours de jeu
  run('pad.on = true;');
  ok(run('state') === 'play', 'en jeu, à la manette');
  run('navigator.getGamepads = () => [null, null];'); pstep(5);
  ok(run('pad.vx === 0 && pad.vy === 0'), 'manette débranchée : plus de mouvement fantôme');
  ok(run('state') === 'pause', 'et la partie se met en pause');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
