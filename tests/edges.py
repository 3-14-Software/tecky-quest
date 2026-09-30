# Détecte les sprites dont des pixels opaques touchent le bord du cadre (signe de découpe)
import sys; import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import numpy as np
import pack_web
TILEABLE = ('decor/fence', 'decor/hedge', 'hud/panel', 'hud/cooldown')   # conçus pour toucher le bord
res = {}
for key, ims, o, trim in pack_web.collect():
    if key.startswith(TILEABLE):
        continue
    for i, im in enumerate(ims):
        a = np.array(im.getchannel('A'))
        sides = []
        for name, edge in (('haut', a[0]), ('bas', a[-1]), ('gauche', a[:, 0]), ('droite', a[:, -1])):
            if (edge > 40).sum() > 0:
                sides.append(name)
        if sides:
            res.setdefault(key, set()).update(sides)
for k, v in sorted(res.items()):
    print(f'{k:32s} {", ".join(sorted(v))}')
print(len(res), 'sprites touchent un bord')
