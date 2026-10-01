// Même contrôle que pack_web.py : rien dans l'eau ni dans un obstacle, et tout (objets, indices, trésors,
// panneaux, Alice) atteignable à pied depuis la niche. Voir web_src/check_placement.js.
process.argv[2] = __dirname + '/../web/index.html';
require('../web_src/check_placement.js');
