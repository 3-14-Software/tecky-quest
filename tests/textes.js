// textes en données : tout ce que le jeu écrit vient de textes/fr.json (txt), plus rien n'est écrit en dur dans game.js
const fs = require('fs'), path = require('path');
const base = fs.readFileSync(path.join(__dirname, 'sim.js'), 'utf8').split("setTimeout(() => {")[0];
const DOSSIER = __dirname;
function main() {
  const src = fs.readFileSync(path.join(DOSSIER, '..', 'web_src', 'game.js'), 'utf8');
  const T = JSON.parse(fs.readFileSync(path.join(DOSSIER, '..', 'textes', 'fr.json'), 'utf8'));
  const at = k => k.split('.').reduce((v, x) => v == null ? v : v[x], T);
  // 1. les clés citées dans le code existent : en entier, ou leur début quand la fin est calculée ('badges.' + id)
  const cites = [...src.matchAll(/\btxt(?:Dev|At)?\('([\w.]+)'/g)].map(m => m[1]);
  const manque = [...new Set(cites)].filter(k => k.endsWith('.') ? typeof at(k.slice(0, -1)) !== 'object' : at(k) === undefined);
  ok(cites.length > 200 && manque.length === 0,
     cites.length + ' clés citées dans game.js, toutes dans textes/fr.json (' + (manque.join(', ') || 'aucune manquante') + ')');
  // 2. chaque texte sert : sa clé est citée, ou elle prolonge une clé citée (pluriel, variante, début calculé)
  const feuilles = [];
  const voir = (v, k) => typeof v === 'string' ? feuilles.push(k) : Object.keys(v).forEach(x => voir(v[x], k ? k + '.' + x : x));
  voir(T, '');
  const sert = k => cites.some(c => c === k || k.startsWith(c.endsWith('.') ? c : c + '.'));
  const inutiles = feuilles.filter(k => !sert(k));
  ok(inutiles.length === 0, feuilles.length + ' textes, tous utilisés (' + (inutiles.join(', ') || 'aucun en trop') + ')');
  // 3. plus de texte écrit en dur : aucun littéral de game.js ne ressemble à une phrase
  const PERMIS = new Set(['use strict', 'file:', '(pointer: coarse)', '(display-mode: fullscreen)', '(display-mode: standalone)',
    'Entrée', 'Échap']);                      // (les deux derniers : des noms d'images de touches, MAP.keys)
  const lits = [];
  for (let i = 0; i < src.length; i++) {      // les littéraux, hors commentaires
    const c = src[i], d = src[i + 1];
    if (c === '/' && d === '/') { while (i < src.length && src[i] !== '\n') i++; continue; }
    if (c === '/' && d === '*') { i = src.indexOf('*/', i + 2) + 1; continue; }
    if (c === "'" || c === '"' || c === '`') {
      let j = i + 1;
      while (j < src.length && src[j] !== c) { if (src[j] === '\\') j++; j++; }
      lits.push(src.slice(i + 1, j)); i = j; continue;
    }
    if (c === '/' && /[=(,:\[!&|?{};\n]\s*$/.test(src.slice(Math.max(0, i - 20), i))) {       // une expression régulière
      let j = i + 1;
      while (j < src.length && src[j] !== '/' && src[j] !== '\n') { if (src[j] === '\\') j++; if (src[j] === '[') while (src[j] !== ']') { if (src[j] === '\\') j++; j++; } j++; }
      i = j;
    }
  }
  const phrase = s => /[a-zà-ÿ]{3,}/.test(s) && /[ À-ÿ’!?…]/.test(s) && !/^(#|rgba?\(|[a-z_0-9]+\/)/.test(s)
    && !/(px |Fredoka|sans-serif|source-|destination-)/.test(s) && !PERMIS.has(s);
  const dur = [...new Set(lits.filter(phrase))];
  ok(lits.length > 1500 && dur.length === 0,
     'aucun texte écrit en dur dans game.js (' + lits.length + ' littéraux ; ' + (dur.slice(0, 5).join(' | ') || 'rien') + ')');
  // 4. txt() : paramètres, pluriel de la langue, variante selon l'appareil, clé inconnue
  ok(run('txt("farmer.encore", { n: 1 })') === 'Encore 1 poule !' && run('txt("farmer.encore", { n: 3 })') === 'Encore 3 poules !'
     && run('txt("menu.indices", { n: 0 })') === '0 indice sur 3', 'pluriel : « 1 poule », « 3 poules », et 0 au singulier en français');
  ok(run('txt("lettres.trouvee", { n: 2, total: 5 })') === 'Une lettre ! (2/5)' && run('txt("farmer.rappel", { n: 1 })').startsWith("Plus qu'une !")
     && run('txt("farmer.rappel", { n: 4 })').startsWith('Il en reste 4 dehors !'), 'paramètres remplacés dans le texte');
  ok(run('touchMode = true, txtDev("badges.retour")') === 'Touche l’écran pour revenir'
     && run('touchMode = false, txtDev("badges.retour")') === '[back] pour revenir', 'txtDev : le texte du toucher, ou celui des touches (avec ses icônes)');
  ok(run('txt("rien.du.tout")') === 'rien.du.tout' && run('txtAt("rien.du.tout")') === undefined, 'une clé inconnue s\'affiche telle quelle');
  // 5. chaque pluriel a ses deux formes
  const pluriels = [];
  const chercher = (v, k) => {
    if (v && typeof v === 'object' && !Array.isArray(v) && ('one' in v || 'other' in v)) pluriels.push([k, v]);
    else if (v && typeof v === 'object') Object.keys(v).forEach(x => chercher(v[x], k + '.' + x));
  };
  chercher(T, '');
  ok(pluriels.length >= 9 && pluriels.every(([, v]) => typeof v.one === 'string' && typeof v.other === 'string'),
     pluriels.length + ' pluriels, chacun avec « one » et « other »');
  // 6. quelques textes composés
  run('recs = { [recKey("aventure", "normal")]: { score: 5000, time: 605, done: 80, wins: 3 } }; opts.diff = "normal";');
  ok(run('recordLine("aventure")') === 'Records en aventure : 5000 points · 10 min 05 s · 80 %', 'ligne des records : ' + run('recordLine("aventure")'));
  ok(run('WHO.neighbor.name') === 'Mamie Rose' && run('badgeName("sieste")') === 'Roi de la sieste'
     && run('spokenText("[bite] pour mordre (3 / 8)", "manette")') === 'Le bouton A pour mordre 3 sur 8',
     'noms des personnages, badges et touches dites à voix haute');
}
eval(base + 'setTimeout(' + main.toString() + ', 50);');
