'use strict';
/* =====================================================================
   TECKY QUEST — moteur Canvas 2D
   Monde : pixels "x2" (tuile = 64 px). Caméra : 960 x 540 px de monde.
   Interface (GUI) : 1920 x 1080, sprites HUD x2.
   ===================================================================== */

const VW = 960, VH = 540;               // caméra, en px de monde
const GW = 1920, GH = 1080;             // repère de l'interface
const TS = MAP.ts;

const cv = document.getElementById('game');
const ctx = cv.getContext('2d');
let dpr = 1, scale = 1, offX = 0, offY = 0;

function resize() {
  dpr = Math.min(window.devicePixelRatio || 1, 2);
  cv.width = Math.round(innerWidth * dpr);
  cv.height = Math.round(innerHeight * dpr);
  scale = Math.min(cv.width / VW, cv.height / VH);
  offX = Math.round((cv.width - VW * scale) / 2);
  offY = Math.round((cv.height - VH * scale) / 2);
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';
}
addEventListener('resize', resize);
resize();

/* ------------------------------------------------------------------ images */
const atlas = new Image();
const tilesImg = new Image();
atlas.src = ATLAS_SRC;
tilesImg.src = TILES_SRC;

/* ------------------------------------------------------------------ utilitaires */
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const dist = (ax, ay, bx, by) => Math.hypot(ax - bx, ay - by);
const lerp = (a, b, t) => a + (b - a) * t;
const DIRV = { down: [0, 1], up: [0, -1], left: [-1, 0], right: [1, 0] };

function dirFrom(dx, dy, fallback) {
  if (Math.abs(dx) < 1e-3 && Math.abs(dy) < 1e-3) return fallback;
  if (Math.abs(dx) >= Math.abs(dy)) return dx > 0 ? 'right' : 'left';
  return dy > 0 ? 'down' : 'up';
}

/* Dessin d'une image de l'atlas, origine en (x, y). */
function drawSpr(key, i, x, y, opt) {
  const s = ATLAS[key];
  if (!s) return;
  const n = s.f.length;
  const f = s.f[((i % n) + n) % n];
  const o = opt || {};
  ctx.save();
  if (o.alpha !== undefined) ctx.globalAlpha = o.alpha;
  ctx.translate(x, y);
  if (o.angle) ctx.rotate(o.angle);
  if (o.flip) ctx.scale(-1, 1);
  if (o.sc) ctx.scale(o.sc, o.sc);
  if (o.sy) ctx.scale(1, o.sy);       // écrasement vertical autour des pieds (berger accroupi)
  ctx.drawImage(atlas, f[0], f[1], f[2], f[3], f[4] - s.o[0], f[5] - s.o[1], f[2], f[3]);
  ctx.restore();
}

/* 9-slice : bords de b px */
/* 9-slice : le panneau est d'abord assemblé à taille réelle (1:1, sans mise à l'échelle) dans un
   canvas hors écran, puis posé en un seul drawImage -> aucune jointure visible, même sur fond translucide. */
const NINE_CACHE = new Map();
function drawNine(key, x, y, w, h, b) {
  w = Math.round(w); h = Math.round(h);
  const ck = key + '|' + w + '|' + h + '|' + b;
  let oc = NINE_CACHE.get(ck);
  if (!oc) {
    const s = ATLAS[key], [sx, sy, sw, sh] = s.f[0];
    oc = document.createElement('canvas'); oc.width = w; oc.height = h;
    const c = oc.getContext('2d');
    const xs = [[0, b, 0, b], [b, sw - b, b, w - b], [sw - b, sw, w - b, w]];
    const ys = [[0, b, 0, b], [b, sh - b, b, h - b], [sh - b, sh, h - b, h]];
    for (const [a0, a1, d0, d1] of xs)
      for (const [c0, c1, e0, e1] of ys)
        c.drawImage(atlas, sx + a0, sy + c0, a1 - a0, c1 - c0, d0, e0, d1 - d0, e1 - e0);
    NINE_CACHE.set(ck, oc);
  }
  ctx.drawImage(oc, x, y);
}

/* Texte en chiffres-sprites (0123456789+-x/:%) */
const DIGITS = '0123456789+-x/:%';
let DIGIT_CELL = 0;                       // largeur d'une case pour les chiffres à chasse fixe
function digitCell() {
  if (!DIGIT_CELL) for (let i = 0; i < 10; i++) DIGIT_CELL = Math.max(DIGIT_CELL, ATLAS['hud/digits'].f[i][2]);
  return DIGIT_CELL + 2;
}
/* mono = true : chiffres à chasse fixe (score) ; sinon espacement proportionnel (« +20 », « 1/3 ») */
function drawDigits(text, x, y, sc, alpha, mono) {
  sc = sc || 1;
  let cx = x;
  const cell = digitCell();
  for (const ch of text) {
    const i = DIGITS.indexOf(ch);
    if (i < 0) continue;
    const f = ATLAS['hud/digits'].f[i];
    const adv = mono ? cell : f[2] + 3;
    const ox = mono ? (cell - f[2]) / 2 : 0;
    ctx.save();
    if (alpha !== undefined) ctx.globalAlpha = alpha;
    ctx.drawImage(atlas, f[0], f[1], f[2], f[3], cx + ox * sc, y + f[5] * sc, f[2] * sc, f[3] * sc);
    ctx.restore();
    cx += adv * sc;
  }
}

/* ------------------------------------------------------------------ son (synthétisé) */
let AC = null, muted = false;
const SFX_VOL = 1.4;   // bruitages un peu plus forts, pour bien ressortir sur la musique
function audioOn() {
  if (!AC) {
    try { AC = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { AC = null; }
  }
  if (AC && AC.state === 'suspended') AC.resume();
  if (AC && !Music.on && !(alice && alice.found) && (state === 'title' || state === 'play' || state === 'dialog' || state === 'pause')) Music.start();
}
function tone(freq, dur, type, vol, slide, delay) {
  if (!AC || muted) return;
  const t0 = AC.currentTime + (delay || 0);
  const o = AC.createOscillator(), g = AC.createGain();
  o.type = type || 'square';
  o.frequency.setValueAtTime(freq, t0);
  if (slide) o.frequency.exponentialRampToValueAtTime(Math.max(40, freq + slide), t0 + dur);
  g.gain.setValueAtTime((vol || 0.08) * SFX_VOL, t0);
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
  o.connect(g); g.connect(AC.destination);
  o.start(t0); o.stop(t0 + dur + 0.02);
}
function noise(dur, vol, freq, delay) {
  if (!AC || muted) return;
  const t0 = AC.currentTime + (delay || 0);
  const len = Math.floor(AC.sampleRate * dur);
  const buf = AC.createBuffer(1, len, AC.sampleRate);
  const d = buf.getChannelData(0);
  for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / len);
  const src = AC.createBufferSource(), f = AC.createBiquadFilter(), g = AC.createGain();
  src.buffer = buf; f.type = 'bandpass'; f.frequency.value = freq || 1000; f.Q.value = 1.2;
  g.gain.value = (vol || 0.1) * SFX_VOL;
  src.connect(f); f.connect(g); g.connect(AC.destination);
  src.start(t0);
}
const SFX = {
  bark(p) { const k = p || 1; tone(520 * k, 0.09, 'sawtooth', 0.16, -260 * k); noise(0.08, 0.14, 1400 * k); tone(470 * k, 0.11, 'sawtooth', 0.14, -240 * k, 0.12); noise(0.09, 0.12, 1200 * k, 0.12); },
  bite() { noise(0.05, 0.18, 2600); tone(180, 0.06, 'square', 0.06, -80); },
  pick() { tone(880, 0.07, 'triangle', 0.08); tone(1320, 0.1, 'triangle', 0.08, 0, 0.07); },
  treasure() { [660, 880, 990, 1320].forEach((f, i) => tone(f, 0.12, 'triangle', 0.08, 0, i * 0.08)); },
  heal() { tone(520, 0.08, 'sine', 0.1, 200); tone(780, 0.12, 'sine', 0.1, 200, 0.08); },
  hurt() { tone(240, 0.18, 'square', 0.08, -150); noise(0.1, 0.08, 500); },
  hit() { noise(0.06, 0.12, 900); tone(140, 0.08, 'square', 0.05, -60); },
  flee() { tone(700, 0.25, 'sine', 0.06, 500); },
  scratch() { noise(0.07, 0.09, 700 + Math.random() * 500); },
  blip() { tone(1200, 0.02, 'square', 0.02); },
  honk(p) { const k = p || 1; tone(415 * k, 0.13, 'square', 0.06); tone(330 * k, 0.13, 'square', 0.05);
    tone(415 * k, 0.2, 'square', 0.06, 0, 0.18); tone(330 * k, 0.2, 'square', 0.05, 0, 0.18); },
  yip(p) { const k = p || 1; tone(820 * k, 0.07, 'square', 0.045, 420 * k); tone(980 * k, 0.09, 'square', 0.045, 380 * k, 0.11); },
  cluck() { tone(950, 0.05, 'square', 0.05, 250); tone(1150, 0.05, 'square', 0.05, 200, 0.08); tone(1400, 0.12, 'square', 0.05, -600, 0.17); },
  win() { [523, 659, 784, 1046, 784, 1046].forEach((f, i) => tone(f, 0.18, 'triangle', 0.09, 0, i * 0.14)); },
};

/* ------------------------------------------------------------------ musique chiptune */
/* « Promenade de Tecky » : événements générés par music.py (même partition que le WAV GameMaker) */
const Music = {
  on: false, gain: null, timer: null, step: 0, next: 0, waves: {}, noiseBuf: null, byStep: null,
  VOL: { lead: 0.16, arp: 0.045, bass: 0.2, kick: 0.5, snare: 0.2, hat: 0.07 },
  init() {
    const mk = S => { const b = Array.from({ length: S.total }, () => []); for (const e of S.ev) b[e[0]].push(e); return { byStep: b, total: S.total, bpm: S.bpm }; };
    this.songs = { main: mk(SONG), win: mk(WINSONG), lose: mk(LOSESONG) };
    this.byStep = true;
    const len = AC.sampleRate;
    this.noiseBuf = AC.createBuffer(1, len, AC.sampleRate);
    const d = this.noiseBuf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
  },
  wave(duty) {
    if (!this.waves[duty]) {
      const N = 48, re = new Float32Array(N), im = new Float32Array(N);
      for (let n = 1; n < N; n++) re[n] = 2 / (n * Math.PI) * Math.sin(n * Math.PI * duty);
      this.waves[duty] = AC.createPeriodicWave(re, im);
    }
    return this.waves[duty];
  },
  // thème discret (derrière les bruitages), fanfare de fin à plein volume
  level() { return muted ? 0 : state === 'pause' ? 0.12 : this.cur === 'main' ? 0.35 : 0.55; },
  /* name : 'main' (boucle), 'win' (fanfare de victoire) ou 'lose' (musique de défaite), ces deux-là jouées une seule fois */
  start(name) {
    name = name || 'main';
    if (!AC) return;
    if (this.on && this.cur !== 'main' && name === 'main') this.stop();   // rejouer pendant la fanfare ou la défaite
    if (this.on) return;
    if (!this.byStep) this.init();
    this.cur = name; this.song = this.songs[name];
    this.on = true;
    this.gain = AC.createGain();
    this.gain.gain.value = this.level();
    this.gain.connect(AC.destination);
    this.step = 0;
    this.next = AC.currentTime + 0.08;
    this.timer = setInterval(() => this.tick(), 25);
  },
  stop() {
    if (!this.on) return;
    this.on = false;
    clearInterval(this.timer);
    const g = this.gain;
    g.gain.setTargetAtTime(0, AC.currentTime, 0.08);
    setTimeout(() => g.disconnect(), 800);
  },
  refresh() { if (this.on) this.gain.gain.setTargetAtTime(this.level(), AC.currentTime, 0.05); },
  tick() {
    const spb = 60 / this.song.bpm / 4;
    if (this.next < AC.currentTime - 0.2) this.next = AC.currentTime + 0.05;   // retour d'onglet
    while (this.next < AC.currentTime + 0.15) {
      for (const e of this.song.byStep[this.step]) this.play(e, this.next, spb);
      this.next += spb;
      this.step++;
      if (this.step >= this.song.total) {
        if (this.cur === 'main') this.step = 0;
        else { clearInterval(this.timer); const g0 = this.gain; setTimeout(() => { if (this.gain === g0) this.stop(); }, 2500); return; }   // fanfare, défaite : une seule fois
      }
    }
  },
  play(e, t, spb) {
    const [, ch, note, len, vol] = e;
    const out = this.gain;
    if (ch === 'drums') {
      const g = AC.createGain();
      g.connect(out);
      if (note === 'kick') {
        const o = AC.createOscillator();
        o.frequency.setValueAtTime(190, t);
        o.frequency.exponentialRampToValueAtTime(45, t + 0.12);
        g.gain.setValueAtTime(this.VOL.kick * vol, t);
        g.gain.exponentialRampToValueAtTime(0.001, t + 0.14);
        o.connect(g); o.start(t); o.stop(t + 0.16);
      } else {
        const src = AC.createBufferSource(), f = AC.createBiquadFilter();
        src.buffer = this.noiseBuf;
        const snare = note === 'snare';
        f.type = snare ? 'bandpass' : 'highpass';
        f.frequency.value = snare ? 1800 : 7000;
        const d = snare ? 0.12 : 0.035;
        g.gain.setValueAtTime(this.VOL[note] * vol, t);
        g.gain.exponentialRampToValueAtTime(0.001, t + d);
        src.connect(f); f.connect(g);
        src.start(t, Math.random() * 0.5, d + 0.02);
      }
      return;
    }
    const o = AC.createOscillator(), g = AC.createGain();
    if (ch === 'bass') o.type = 'triangle';
    else o.setPeriodicWave(this.wave(ch === 'lead' ? 0.25 : 0.125));
    o.frequency.value = 440 * Math.pow(2, (note - 69) / 12);
    const dur = len * spb, v = this.VOL[ch] * vol;
    const sus = ch === 'arp' ? 0.4 : ch === 'bass' ? 0.8 : 0.65;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(v, t + 0.004);
    g.gain.linearRampToValueAtTime(v * sus, t + 0.05);
    g.gain.setValueAtTime(v * sus, t + Math.max(0.05, dur - 0.03));
    g.gain.linearRampToValueAtTime(0.0001, t + dur);
    o.connect(g); g.connect(out);
    o.start(t); o.stop(t + dur + 0.02);
  },
};
document.addEventListener('visibilitychange', () => {
  if (!AC) return;
  if (document.hidden) AC.suspend(); else AC.resume();
});

/* ------------------------------------------------------------------ plein écran */
const INSTALLED = !!(window.matchMedia && (matchMedia('(display-mode: fullscreen)').matches ||
  matchMedia('(display-mode: standalone)').matches)) || navigator.standalone === true;
function fsElement() { return document.fullscreenElement || document.webkitFullscreenElement || null; }
function canFullscreen() {
  const el = document.documentElement;
  return !INSTALLED && !!(el.requestFullscreen || el.webkitRequestFullscreen) &&
    (document.fullscreenEnabled !== false || document.webkitFullscreenEnabled);
}
function goFullscreen() {
  // doit être appelé directement dans un geste de l'utilisateur (toucher, clic, touche)
  if (!canFullscreen() || fsElement()) return;
  const el = document.documentElement;
  try {
    const p = el.requestFullscreen ? el.requestFullscreen({ navigationUI: 'hide' }) : el.webkitRequestFullscreen();
    Promise.resolve(p).then(() => {
      if (screen.orientation && screen.orientation.lock) screen.orientation.lock('landscape').catch(() => {});
    }).catch(() => {});
  } catch (e) { /* refusé : on reste en fenêtre */ }
}
function toggleFullscreen() {
  if (fsElement()) { (document.exitFullscreen || document.webkitExitFullscreen).call(document); }
  else goFullscreen();
}
const FS_BTN = { x: GW - 150, y: 310, w: 126, h: 70 };

/* ------------------------------------------------------------------ entrées */
const held = {};
let pressed = {};
const MOVE_CODES = {
  ArrowUp: 'up', KeyW: 'up', ArrowDown: 'down', KeyS: 'down',
  ArrowLeft: 'left', KeyA: 'left', ArrowRight: 'right', KeyD: 'right',
};
function actionOfKey(e) {
  const k = (e.key || '').toLowerCase();
  if (k === 'x' || k === 'j') return 'bark';
  if (k === 'c' || k === 'k') return 'bite';
  if (k === 'e') return 'act';
  if (k === 'enter' || k === ' ') return 'ok';
  if (k === 'escape' || k === 'p') return 'pause';
  if (k === 'm') return 'mute';
  if (k === 'f') return 'fullscreen';
  return null;
}
addEventListener('keydown', e => {
  audioOn();
  touchMode = false; pad.on = false;
  const m = MOVE_CODES[e.code];
  if (m) { held[m] = true; if (!e.repeat) pressed[m] = true; e.preventDefault(); }
  const a = actionOfKey(e);
  if (a === 'fullscreen') { if (!e.repeat) toggleFullscreen(); e.preventDefault(); return; }
  if (a) {
    if (!e.repeat) pressed[a] = true;
    held[a] = true;
    e.preventDefault();
  }
});
addEventListener('keyup', e => {
  const m = MOVE_CODES[e.code];
  if (m) held[m] = false;
  const a = actionOfKey(e);
  if (a) held[a] = false;
});
addEventListener('blur', () => { for (const k in held) held[k] = false; });

/* manette (API Gamepad, disposition « standard ») : stick gauche ou croix pour marcher et choisir dans les menus,
   A = mordre / gratter / lire et valider, X ou B = aboyer, Y = lire, Start = pause, Select = son.
   Les boutons sont lus à chaque image (pollPad) : un appui = une impulsion dans `pressed`, comme une touche. */
const PAD_MAP = { 0: ['bite', 'ok'], 1: ['bark'], 2: ['bark'], 3: ['act'], 8: ['mute'], 9: ['pause'],
                  12: ['up'], 13: ['down'], 14: ['left'], 15: ['right'] };
const PAD_DEAD = 0.25;
const pad = { on: false, vx: 0, vy: 0, prev: {}, sy: 0 };
function pollPad() {
  const list = (navigator.getGamepads && navigator.getGamepads()) || [];
  const down = {};
  let vx = 0, vy = 0, used = false;
  for (const gp of list) {
    if (!gp || gp.connected === false) continue;
    const ax = gp.axes[0] || 0, ay = gp.axes[1] || 0;
    if (Math.hypot(ax, ay) > PAD_DEAD) { vx = ax; vy = ay; }
    gp.buttons.forEach((b, i) => { if (b && (b.pressed || b.value > 0.5)) down[i] = true; });
  }
  const cx = (down[15] ? 1 : 0) - (down[14] ? 1 : 0), cy = (down[13] ? 1 : 0) - (down[12] ? 1 : 0);
  if (cx || cy) { vx = cx; vy = cy; }
  for (const i in PAD_MAP) if (down[i] && !pad.prev[i]) { for (const a of PAD_MAP[i]) pressed[a] = true; used = true; }
  // dans les menus, le stick donne une impulsion par mouvement franc (la croix passe par PAD_MAP)
  const sy = Math.abs(vy) > 0.6 ? Math.sign(vy) : 0;
  if (sy && sy !== pad.sy && !cy) pressed[sy < 0 ? 'up' : 'down'] = true;
  pad.sy = sy; pad.prev = down; pad.vx = vx; pad.vy = vy;
  if (used) audioOn();
  if (used || Math.hypot(vx, vy) > 0.5) { pad.on = true; touchMode = false; }
}

/* tactile : joystick à gauche, boutons à droite (repère GUI) */
let touchMode = !!(window.matchMedia && matchMedia('(pointer: coarse)').matches);
const stick = { id: null, ox: 0, oy: 0, x: 0, y: 0, vx: 0, vy: 0 };
const BTN = { bark: { x: 1560, y: 900, r: 105 }, bite: { x: 1780, y: 790, r: 105 } };
function toGui(ev) {
  const r = cv.getBoundingClientRect();
  const px = (ev.clientX - r.left) * dpr, py = (ev.clientY - r.top) * dpr;
  const gs = scale * VW / GW;
  return [(px - offX) / gs, (py - offY) / gs];
}
cv.addEventListener('pointerdown', e => {
  audioOn();
  if (e.pointerType !== 'mouse') touchMode = true;
  pad.on = false;
  const [gx, gy] = toGui(e);
  // au premier toucher de l'écran titre, on passe en plein écran (Android)
  if (touchMode && state === 'title') goFullscreen();
  if (touchMode && canFullscreen() && !fsElement() && (state === 'play' || state === 'pause') &&
      gx > FS_BTN.x && gx < FS_BTN.x + FS_BTN.w && gy > FS_BTN.y && gy < FS_BTN.y + FS_BTN.h) { goFullscreen(); return; }
  if (menu && (state === 'title' || state === 'over')) {     // menus : toucher (ou cliquer) une entrée la choisit
    const i = menuHit(gx, gy);
    if (i >= 0) { menu.sel = i; pressed.ok = true; }
    return;
  }
  if (state !== 'play' || !touchMode) { pressed.ok = true; return; }
  if (gx > GW - 160 && gy > 210 && gy < 310) { pressed.pause = true; return; }
  for (const k of ['bark', 'bite']) {
    const b = BTN[k];
    if (dist(gx, gy, b.x, b.y) < b.r * 1.15) { pressed[k] = true; return; }
  }
  if (gx < GW * 0.55 && stick.id === null) {
    stick.id = e.pointerId; stick.ox = gx; stick.oy = gy; stick.x = gx; stick.y = gy;
    stick.vx = stick.vy = 0;
    cv.setPointerCapture(e.pointerId);
  } else {
    pressed.act = true;
  }
});
cv.addEventListener('pointermove', e => {
  if (e.pointerId !== stick.id) return;
  const [gx, gy] = toGui(e);
  const dx = gx - stick.ox, dy = gy - stick.oy, l = Math.hypot(dx, dy), R = 120;
  const k = l > R ? R / l : 1;
  stick.x = stick.ox + dx * k; stick.y = stick.oy + dy * k;
  stick.vx = (dx * k) / R; stick.vy = (dy * k) / R;
});
const endStick = e => { if (e.pointerId === stick.id) { stick.id = null; stick.vx = stick.vy = 0; } };
cv.addEventListener('pointerup', endStick);
cv.addEventListener('pointercancel', endStick);

/* ------------------------------------------------------------------ sol (pré-rendu) */
/* Le sol est pré-rendu en blocs de CHUNK tuiles (1024 px) : une seule image de toute la carte dépasserait
   la taille de canevas permise sur certains téléphones. Chaque bloc déborde de CM px sur ses voisins
   (mêmes pixels) pour qu'aucune jointure n'apparaisse à l'échelle d'affichage. */
const CHUNK = 16, CM = 2;
let groundChunks = [];
function buildGround() {
  groundChunks = [];
  for (let cy = 0; cy < MAP.h; cy += CHUNK) for (let cx = 0; cx < MAP.w; cx += CHUNK) {
    const w = Math.min(CHUNK, MAP.w - cx), h = Math.min(CHUNK, MAP.h - cy);
    const c = document.createElement('canvas');
    c.width = w * TS + 2 * CM; c.height = h * TS + 2 * CM;
    const g = c.getContext('2d');
    const blit = (idx, tx, ty) => g.drawImage(tilesImg, (idx % 16) * TS, Math.floor(idx / 16) * TS, TS, TS,
      (tx - cx) * TS + CM, (ty - cy) * TS + CM, TS, TS);
    for (let ty = Math.max(0, cy - 1); ty < Math.min(MAP.h, cy + h + 1); ty++)
      for (let tx = Math.max(0, cx - 1); tx < Math.min(MAP.w, cx + w + 1); tx++) {
        const i = ty * MAP.w + tx;
        blit(MAP.ground[i], tx, ty);
        if (MAP.over[i]) blit(MAP.over[i], tx, ty);
      }
    groundChunks.push({ c, x: cx * TS - CM, y: cy * TS - CM, w: c.width, h: c.height });
  }
}
function drawGround(vx, vy) {
  for (const k of groundChunks) {
    const x0 = Math.max(k.x, vx), y0 = Math.max(k.y, vy);
    const x1 = Math.min(k.x + k.w, vx + VW), y1 = Math.min(k.y + k.h, vy + VH);
    if (x1 > x0 && y1 > y0) ctx.drawImage(k.c, x0 - k.x, y0 - k.y, x1 - x0, y1 - y0, x0, y0, x1 - x0, y1 - y0);
  }
}
/* Eau animée : la texture de l'eau est unie dans la version web ; quelques vaguelettes (fx/ripple) y naissent,
   s'étirent en dérivant un peu, puis s'effacent, à un endroit qui change à chaque cycle (une par tuile, un cycle sur
   deux, chaque tuile avec son décalage). En plus, des scintillements (fx/glint, mini-étoiles) avec leur propre
   cadence et leur propre place, en bref éclat au milieu de leur cycle. Uniquement en eau profonde : tout le contour,
   plus une marge pour le liseré clair du bord, doit être dans l'eau. */
const RIPPLE = { cycle: 2.4, show: 0.5, drift: 8, glintCycle: 2.8, glintShow: 0.4 };
const deepWater = (x, y) => [[-30, 0], [30, 0], [0, -18], [0, 22], [-22, -12], [22, -12], [-22, 16], [22, 16]]
  .every(([dx, dy]) => waterAt(x + dx, y + dy));
let waterTiles = null;
function hash3(a, b, c) {
  let h = Math.imul(a, 374761393) ^ Math.imul(b, 668265263) ^ Math.imul(c, 1274126177);
  h = Math.imul(h ^ (h >>> 13), 1103515245);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}
function drawWater(vx, vy, time) {
  if (!waterTiles) {                       // tuiles ayant au moins un coin d'eau
    waterTiles = new Uint8Array(MAP.w * MAP.h);
    const W1 = MAP.w + 1, c = (a, b) => MAP.water[b * W1 + a];
    for (let j = 0; j < MAP.h; j++) for (let i = 0; i < MAP.w; i++)
      waterTiles[j * MAP.w + i] = c(i, j) | c(i + 1, j) | c(i, j + 1) | c(i + 1, j + 1);
  }
  const n = ATLAS['fx/ripple'].f.length, ng = ATLAS['fx/glint'].f.length;
  for (let ty = Math.max(0, Math.floor(vy / TS)); ty <= Math.min(MAP.h - 1, Math.floor((vy + VH) / TS)); ty++)
    for (let tx = Math.max(0, Math.floor(vx / TS)); tx <= Math.min(MAP.w - 1, Math.floor((vx + VW) / TS)); tx++) {
      if (!waterTiles[ty * MAP.w + tx]) continue;
      // vaguelette : un cycle sur deux en moyenne
      let c = time / RIPPLE.cycle + hash3(tx, ty, 7), cyc = Math.floor(c), u = c - cyc;
      if (hash3(tx, cyc, ty) < RIPPLE.show) {
        const x = tx * TS + 8 + hash3(tx, ty, cyc * 31) * (TS - 16) + u * RIPPLE.drift;
        const y = ty * TS + 8 + hash3(ty, tx, cyc * 17) * (TS - 16);
        if (deepWater(x, y)) drawSpr('fx/ripple', Math.floor(u * n), x, y);
      }
      // scintillement, en plus : sa propre cadence et sa propre place, bref éclat au milieu du cycle
      c = time / RIPPLE.glintCycle + hash3(ty, tx, 11); cyc = Math.floor(c); u = c - cyc;
      if (u > 0.3 && u < 0.7 && hash3(cyc, tx, ty) < RIPPLE.glintShow) {
        const x = tx * TS + 8 + hash3(tx, ty, cyc * 47 + 5) * (TS - 16);
        const y = ty * TS + 8 + hash3(ty, tx, cyc * 53 + 9) * (TS - 16);
        if (deepWater(x, y)) drawSpr('fx/glint', Math.floor((u - 0.3) / 0.4 * ng), x, y);
      }
    }
}

function drawHole(x, y) {
  const idx = MAP.hole;
  ctx.drawImage(tilesImg, (idx % 16) * TS, Math.floor(idx / 16) * TS, TS, TS, x - TS / 2, y - TS / 2 - 6, TS, TS);
}

/* ------------------------------------------------------------------ collisions */
const FOOT = {
  tree: [-18, -16, 18, 0], bush: [-28, -18, 28, 0], hay: [-26, -22, 26, 0], rock: [-22, -18, 22, 0],
  fence_wood_h: [0, -14, 64, 0], fence_wood_v: [-8, -64, 8, 0], signpost: [-7, -8, 7, 0],
  cone: [-12, -10, 12, 0], road_sign: [-7, -8, 7, 0], lamppost: [-10, -10, 10, 0],
  house_red: [-76, -84, 76, -2], house_blue: [-76, -84, 76, -2], doghouse: [-28, -26, 28, 0],
  bench: [-40, -20, 40, 0], mailbox: [-7, -6, 7, 0], hedge: [0, -36, 64, 0], flower_pot: [-14, -18, 14, 0],
  warehouse: [-116, -104, 116, -4], container: [-92, -54, 92, 0], pallet: [-26, -16, 26, 0],
  barrel_blue: [-18, -16, 18, 0], barrel_red: [-18, -16, 18, 0], crate: [-24, -22, 24, 0],
  fence_metal_h: [0, -12, 64, 0], fence_metal_v: [-6, -64, 6, 0],
  // ferme et rivière (roseaux, barque et pont : pas de collision)
  barn: [-96, -84, 96, -2], chicken_coop: [-36, -14, 36, 0],
  tractor: [-52, -20, 52, 0], scarecrow: [-7, -8, 7, 0],
  // forêt et parc (champignons, fougère et bac à sable : pas de collision)
  fir: [-18, -16, 18, 0], stump: [-20, -16, 20, 0], log: [-54, -22, 56, 0], slide: [-56, -14, 58, 0],
  swing: [-58, -12, 58, 0], fountain: [-52, -40, 52, 0], playhouse: [-44, -50, 44, -2],
};
const FLAT = new Set(['bridge', 'sandbox']);   // posés à plat : dessinés sous les personnages
// pont : garde-corps de chaque côté (son tablier n'est pas de l'eau, voir BRIDGES dans pack_web.py)
const RAILS = { bridge: [[-80, -320, -62, 0], [62, -320, 80, 0]] };
let solids = [];
function waterAt(x, y) {
  const fx = x / TS, fy = y / TS;
  const i = Math.floor(fx), j = Math.floor(fy);
  if (i < 0 || j < 0 || i >= MAP.w || j >= MAP.h) return false;
  const W1 = MAP.w + 1, c = (a, b) => MAP.water[b * W1 + a];
  const u = fx - i, v = fy - j;
  const val = c(i, j) * (1 - u) * (1 - v) + c(i + 1, j) * u * (1 - v) + c(i, j + 1) * (1 - u) * v + c(i + 1, j + 1) * u * v;
  return val > 0.42;
}
function blockedPoint(x, y) {
  if (x < 12 || y < 40 || x > MAP.w * TS - 12 || y > MAP.h * TS - 4) return true;
  if (waterAt(x, y)) return true;
  for (const s of solids) if (x > s[0] && x < s[2] && y > s[1] && y < s[3]) return true;
  return false;
}
/* Pieds = rectangle [x-hw, y-12] -> [x+hw, y]. Obstacles : vrai test de chevauchement
   (un poteau plus fin que les pattes ne peut plus se glisser entre deux points testés).
   Eau : échantillonnage du bord, suffisant car ses contours sont arrondis. */
function blockedFeet(x, y, hw) {
  const x0 = x - hw, x1 = x + hw, y0 = y - 12, y1 = y;
  if (x0 < 12 || y0 < 28 || x1 > MAP.w * TS - 12 || y1 > MAP.h * TS - 4) return true;
  for (const s of solids) if (x1 > s[0] && x0 < s[2] && y1 > s[1] && y0 < s[3]) return true;
  for (const [px, py] of [[x0, y1], [x1, y1], [x0, y0], [x1, y0], [x, y0], [x, y1], [x0, y - 6], [x1, y - 6]])
    if (waterAt(px, py)) return true;
  return false;
}
function moveActor(a, dx, dy, hw, noSlide) {
  hw = hw || 16;
  if (dx && !blockedFeet(a.x + dx, a.y, hw)) a.x += dx;
  else if (dx && !noSlide) {
    // glisser le long d'un coin
    for (const s of [6, -6]) if (!blockedFeet(a.x + dx, a.y + s, hw)) { a.y += s * 0.5; break; }
  }
  if (dy && !blockedFeet(a.x, a.y + dy, hw)) a.y += dy;
  else if (dy && !noSlide) {
    for (const s of [6, -6]) if (!blockedFeet(a.x + s, a.y + dy, hw)) { a.x += s * 0.5; break; }
  }
}

/* Déplacement d'un chien avec contournement : s'il est bloqué, il longe l'obstacle
   par le côté le plus dégagé et garde ce côté le temps de passer (pas d'aller-retour). */
// ligne droite praticable entre deux points (pour la charge du berger)
function clearPath(x0, y0, x1, y1) {
  const n = Math.ceil(dist(x0, y0, x1, y1) / 24);
  for (let i = 1; i < n; i++) if (blockedFeet(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n, 14)) return false;
  return true;
}
function steer(d, vx, vy, s, dt) {
  const ox = d.x, oy = d.y;
  if (d.detT > 0) {
    d.detT -= dt;
    const mx = d.detX + vx * 0.35, my = d.detY + vy * 0.35, ml = Math.hypot(mx, my) || 1;
    moveActor(d, mx / ml * s, my / ml * s, 14, true);
  } else {
    moveActor(d, vx * s, vy * s, 14, true);
  }
  const moved = Math.hypot(d.x - ox, d.y - oy);
  if (moved < s * 0.4 && s > 0) {
    const sides = [[-vy, vx], [vy, -vx]];
    // distance (en pas de 18 px) à parcourir le long de chaque côté avant de pouvoir repartir droit devant
    const reach = ([px, py]) => {
      // on simule le détour avec les mêmes règles de déplacement que le chien (axes séparés)
      const m = Math.hypot(px + vx * 0.35, py + vy * 0.35) || 1;
      const f = { x: d.x, y: d.y };
      for (let k = 1; k <= 40; k++) {
        const bx = f.x, by = f.y;
        moveActor(f, (px + vx * 0.35) / m * 18, (py + vy * 0.35) / m * 18, 14, true);
        if (Math.hypot(f.x - bx, f.y - by) < 6) return Infinity;
        if (!blockedFeet(f.x + vx * 24, f.y + vy * 24, 14)) return k;
      }
      return Infinity;
    };
    let pick = d.detSide !== undefined ? d.detSide : 0;
    const f0 = reach(sides[0]), f1 = reach(sides[1]);
    if (d.detSide === undefined || (pick === 0 ? f0 : f1) === Infinity) pick = f1 < f0 ? 1 : 0;
    d.detSide = pick;
    d.detX = sides[pick][0]; d.detY = sides[pick][1];
    d.detT = 0.45;
  } else if (d.detT <= 0 && d.detSide !== undefined) {
    // fin du détour : si la route directe est encore barrée plus loin (long grillage, mur),
    // on continue à longer l'obstacle au lieu de revenir se cogner contre son bord.
    let clear = true;
    for (let k = 1; k <= 6 && clear; k++)
      if (blockedFeet(d.x + vx * 24 * k, d.y + vy * 24 * k, 14)) clear = false;
    d.detTot = (d.detTot || 0) + dt;
    if (!clear && d.detTot < 4) d.detT = 0.2;
    else if (moved >= s * 0.9) { d.detSide = undefined; d.detTot = 0; }   // voie libre : on oublie le côté
  }
  return moved;
}

/* ------------------------------------------------------------------ acteurs */
const FPS = { idle: 6, walk: 12, bark: 10, bite: 14, hurt: 10, ko: 6, happy: 8, dig: 14 };
const LOOP = { idle: true, walk: true, happy: true, dig: true, flap: true };

class Actor {
  constructor(kind, x, y) {
    this.kind = kind; this.x = x; this.y = y;
    this.dir = 'down'; this.anim = 'idle'; this.t = 0; this.alpha = 1;
  }
  setAnim(a) { if (this.anim !== a) { this.anim = a; this.t = 0; } }
  key() {
    if (this.anim === 'ko') return `${this.kind}/ko/right`;
    const d = this.dir === 'left' ? 'right' : this.dir;
    return `${this.kind}/${this.anim}/${d}`;
  }
  frames() { return ATLAS[this.key()].f.length; }
  frame() {
    const n = this.frames(), i = Math.floor(this.t * (this.fps || FPS)[this.anim]);
    return LOOP[this.anim] ? i % n : Math.min(i, n - 1);
  }
  done() { return this.t * (this.fps || FPS)[this.anim] >= this.frames(); }
  draw(alpha) {
    drawSpr(this.key(), this.frame(), this.x + (this.shake || 0), this.y - (this.hop || 0), { flip: this.dir === 'left',
      alpha: alpha === undefined ? this.alpha : alpha, sy: this.mode === 'crouch' ? 0.84 : undefined });
  }
}

/* ------------------------------------------------------------------ état du jeu */
const DOGS = {
  roquet:     { hp: 2, spd: 170, aggro: 330, range: 74, dmg: 1, cd: 1.1, windup: 0.22, score: 30, pitch: 1.35 },
  bouledogue: { hp: 4, spd: 100, aggro: 290, range: 84, dmg: 2, cd: 1.5, windup: 0.3, score: 60, pitch: 0.8 },
  molosse:    { hp: 7, spd: 150, aggro: 400, range: 90, dmg: 2, cd: 1.2, windup: 0.25, score: 150, pitch: 0.65, barks: true,
                barkImmune: true },   // le doberman ne craint pas les aboiements : il faut le mordre
  // chien de berger : s'accroupit (« ! ») puis charge en ligne droite ; on peut l'esquiver, il souffle ensuite
  berger:     { hp: 3, spd: 175, aggro: 360, range: 78, dmg: 1, cd: 1.0, windup: 0.22, score: 80, pitch: 1.1, charge: true },
};
const CHARGE = { min: 130, max: 300, crouch: 0.5, speed: 560, time: 0.55, tired: 1.1, cd: 3.2 };
/* Mode balade (choisi à l'écran titre) : personne ne se fait mal. Les chiens ne mordent pas, n'aboient pas et ne
   chargent pas : ils viennent près de Tecky et attendent en sautillant qu'il joue avec eux (patience). Près d'un chien,
   le bouton de morsure devient « Jouer » : les deux sautillent en semant des cœurs, et le chien devient un copain
   (points, compté dans fled) ; il ne le poursuit plus, mais lui fait la fête quand il passe. L'aboiement ne repousse
   plus personne : il appelle les chiens qu'il touche (sautillement, cœur), qui accourent pour jouer. */
const PLAY = { time: 2.2, calm: 9, hop: 14, heartEvery: 0.55, reach: 120, patience: 8, tecky: 0.9, waitHop: 1.1, friendR: 170 };
let gameMode = 'aventure';                  // 'aventure' | 'balade'
const balade = () => gameMode === 'balade';
/* Vie : 2 PV par os. Tecky démarre avec 3 os ; chaque saucisse ajoute un os
   (déjà plein) jusqu'à MAX_BONES ; un os ramassé rend un os perdu, sans dépasser le maximum. */
const START_BONES = 3, MAX_BONES = 8;
const ITEM = {
  bone: { heal: 2 }, sausage: { grow: true },
  medal: { pts: 100 }, squeaky: { pts: 50 }, ball: { pts: 20 },
  hairclip: { clue: 0 }, shoe: { clue: 1 }, plush: { clue: 2 },
};
/* Indices : Alice joue à cache-cache et a semé trois affaires. Chacune oriente vers la suivante (la flèche
   au bord de l'écran aussi) ; Alice ne sort de sa cachette, la cabane du parc, qu'une fois les trois trouvées. */
const CLUES = ['hairclip', 'shoe', 'plush'];
const CLUE_FOUND = [
  "La barrette d'Alice ! Elle est passée par la ferme.",
  "Une chaussure d'Alice ! Elle a traversé la rivière par le pont.",
  "Le doudou d'Alice ! Elle ne doit plus être bien loin.",
];
const CLUE_NEXT = [                  // où chercher ensuite : le prochain indice, puis Alice
  "Je vais chercher du côté de la ferme, tout à l'est, en suivant la grande route.",
  "Ses traces partent vers le pont, au sud de la ferme… Elle est allée dans la forêt !",
  "Elle a continué à travers la forêt, vers l'ouest. Ça sent le parc, par là !",
  "Et maintenant, je sens son odeur ! Elle se cache au parc, du côté de la cabane.",
];
let clues = [false, false, false];
function nextClue() { const i = clues.indexOf(false); return i < 0 ? 3 : i; }
/* La flèche n'est pas permanente : elle s'affiche quelques secondes quand Tecky apprend où chercher (intro, indice),
   et revient brièvement s'il tourne en rond trop longtemps sans trouver la suite. */
const ARROW = { show: 8, nudgeAfter: 45, nudge: 5 };
let arrowT = 0, stuckT = 0;
function showArrow(t) { arrowT = Math.max(arrowT, t || ARROW.show); stuckT = 0; }
function arrowTarget() {
  const k = nextClue();
  if (k === 3) return alice;
  return items.find(it => it.n === CLUES[k]) || alice;
}

let state = 'loading';          // loading | title | play | dialog | pause | over | win
let P, alice, dogs, hens, cars, butterflies, items, fxs, pops, rings, digs, decor, camX = 0, camY = 0, shake = 0;
let dusts = [], leaves = [], leafTrees = null, clouds = [], sun = 0, saveT = 0;
// fled : chiens mis en fuite (aventure) ou devenus copains (balade)
let score = 0, timePlayed = 0, fled = 0, treasures = 0, dialog = null, dialogReturn = 'play', aliceSniffed = false;
let hintText = null, digHint = null, playHint = null, overT = 0, titleT = 0;

function reset() {
  solids = [];
  decor = MAP.decor.map(([n, x, y]) => {
    for (const f of [FOOT[n], ...(RAILS[n] || [])]) if (f) solids.push([x + f[0], y + f[1], x + f[2], y + f[3]]);
    return { key: 'decor/' + n, x, y, n };
  });
  P = new Actor('tecky', MAP.start[0], MAP.start[1]);
  // 5 emplacements d'os (2 PV par os) ; Tecky démarre avec 3 os pleins
  Object.assign(P, { hp: START_BONES * 2, hpMax: START_BONES * 2, boneFx: 0, inv: 0, bumpT: 0, cdBark: 0, cdBite: 0, mode: 'free', kx: 0, ky: 0, hitDone: false });
  alice = new Actor('alice', MAP.alice[0], MAP.alice[1]);
  alice.fps = Object.assign({}, FPS, { walk: 10 });
  alice.found = false;
  alice.hidden = true;               // dans la cabane jusqu'aux trois indices
  dogs = MAP.enemies.map(([n, x, y], id) => {
    const d = new Actor(n, x, y);
    Object.assign(d, { id, T: DOGS[n], hp: DOGS[n].hp, mode: 'idle', timer: Math.random() * 2, hx: x, hy: y,
      vx: 0, vy: 0, kx: 0, ky: 0, cd: 0, barkCd: 2, chargeCd: 1.5, hitDone: false, fade: 0 });
    d.t = Math.random();
    return d;
  });
  hens = MAP.hens.map(newHen);
  cars = MAP.traffic.vehicles.map(newVehicle);
  butterflies = MAP.butterflies.map(newButterfly);
  items = MAP.items.map(([n, x, y]) => ({ n, x, y, t: Math.random() * 3 }));
  digs = MAP.dig.map(([x, y]) => ({ x, y, dug: false, t: Math.random() * 2 }));
  fxs = []; pops = []; rings = []; dusts = []; leaves = []; leafTrees = null;
  score = 0; timePlayed = 0; fled = 0; treasures = 0; shake = 0; barkImmuneSeen = false; pendingSay = null;
  clues = [false, false, false]; aliceSniffed = false; arrowT = 0; stuckT = 0; sun = 0; saveT = 0;
  camX = clamp(P.x - VW / 2, 0, MAP.w * TS - VW);
  camY = clamp(P.y - VH / 2, 0, MAP.h * TS - VH);
}

/* ------------------------------------------------------------------ dialogues */
const WHO = {
  tecky: { name: 'Tecky', portrait: 'hud/portrait_tecky' },
  alice: { name: 'Alice', portrait: 'hud/portrait_alice' },
  info:  { name: '', portrait: null },
};
function say(lines, onEnd) {
  dialog = { lines, i: 0, c: 0, onEnd };
  dialogReturn = state === 'dialog' ? dialogReturn : state;
  state = 'dialog';
}
function updateDialog(dt) {
  const L = dialog.lines[dialog.i];
  const before = Math.floor(dialog.c);
  dialog.c = Math.min(L.text.length, dialog.c + dt * 48);
  if (Math.floor(dialog.c) !== before && Math.floor(dialog.c) % 3 === 0) SFX.blip();
  if (pressed.ok || pressed.act || pressed.bark || pressed.bite) {
    if (dialog.c < L.text.length) dialog.c = L.text.length;
    else if (++dialog.i >= dialog.lines.length) {
      const cb = dialog.onEnd;
      dialog = null;
      state = dialogReturn === 'dialog' ? 'play' : dialogReturn;
      if (cb) cb();
    } else dialog.c = 0;
  }
}
function introLines() {
  return [
    { who: 'tecky', face: 0, text: "Ouaf ! Alice est partie jouer… et elle n'est pas rentrée !" },
    { who: 'tecky', face: 2, text: "Elle a dû semer des affaires en chemin. En les retrouvant, je saurai où elle se cache !" },
    { who: 'tecky', face: 0, text: balade()
        ? "La flèche au bord de l'écran me guide. Et les chiens du coin ont l'air d'avoir envie de jouer !"
        : "La flèche au bord de l'écran me guide. Gare aux chiens du coin, ils ne sont pas commodes." },
    { who: 'info', text: touchMode
        ? "Glisse le doigt à gauche pour marcher. Boutons à droite pour aboyer et mordre. Près d'un panneau, le bouton de morsure devient « lire »."
        : pad.on
        ? "Stick ou croix pour marcher, X pour aboyer, A pour mordre ou lire un panneau. Start pour la pause, Select pour le son."
        : "Flèches ou ZQSD pour marcher, X pour aboyer, C pour mordre ou lire un panneau. P pour la pause, M pour le son, F pour le plein écran." },
    { who: 'info', text: touchMode
        ? "Les os rendent un os perdu, les saucisses ajoutent un os en plus. Près des traces de pattes, le bouton de morsure devient « gratter » : un trésor est peut-être enterré !"
        : "Les os rendent un os perdu, les saucisses ajoutent un os en plus. Près des traces de pattes, " + (pad.on ? 'A' : 'C') +
          " sert à gratter le sol : un trésor est peut-être enterré !" },
  ].concat(balade() ? [
    { who: 'info', text: touchMode
        ? "En balade, près d'un chien, le bouton de morsure devient « jouer » : vous deviendrez copains ! Aboyer appelle les chiens."
        : "En balade, près d'un chien, " + (pad.on ? 'A' : 'C') + " sert à jouer avec lui : vous deviendrez copains ! X appelle les chiens." },
  ] : []);
}

/* ------------------------------------------------------------------ combat */
function addFx(key, x, y, opt) { fxs.push(Object.assign({ key, x, y, t: 0, fps: 14 }, opt || {})); }
function addPop(text, x, y) { pops.push({ text, x, y, t: 0 }); }
function addWordPop(text, x, y) { pops.push({ text, x, y, t: 0, word: true }); }
let barkImmuneSeen = false, pendingSay = null;

/* Aboiement : touche dans un cône devant celui qui aboie (cos de l'angle > cos), jusqu'à range (pattes à pattes).
   Une onde (arc ondulé au sol) s'étend jusqu'à cette portée puis s'efface, pour la montrer. */
const BARK = { range: 300, cos: 0.62 };          // Tecky
const DOG_BARK = { range: 320, cos: 0.6 };       // doberman
const RING_GROW = 0.22, RING_FADE = 0.2;
function addBarkRing(x, y, dir, B, color) {
  const [vx, vy] = DIRV[dir];
  rings.push({ x, y, ang: Math.atan2(vy, vx), half: Math.acos(B.cos), range: B.range, color, t: 0 });
}
function drawRings() {
  for (const r of rings) {
    const k = Math.min(1, r.t / RING_GROW);
    const rad = r.range * (1 - Math.pow(1 - k, 3));          // part vite puis ralentit en arrivant à la portée
    const a = r.t < RING_GROW ? 1 : Math.max(0, 1 - (r.t - RING_GROW) / RING_FADE);
    if (rad < 24 || a <= 0) continue;
    const len = rad * r.half * 2;
    const n = Math.max(24, Math.round(len / 3)), waves = Math.max(3, Math.round(len / 26));
    ctx.beginPath();
    for (let i = 0; i <= n; i++) {
      const u = i / n, th = r.ang - r.half + u * 2 * r.half;
      const rr = rad + Math.sin((u * waves + r.t * 4) * Math.PI * 2) * 4;   // ligne ondulée qui défile
      const px = r.x + Math.cos(th) * rr, py = r.y + Math.sin(th) * rr;
      if (i) ctx.lineTo(px, py); else ctx.moveTo(px, py);
    }
    ctx.save();
    ctx.globalAlpha = a * 0.9; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.strokeStyle = '#3A1E12'; ctx.lineWidth = 7; ctx.stroke();
    ctx.strokeStyle = r.color; ctx.lineWidth = 3.5; ctx.stroke();
    ctx.restore();
  }
}

function hurtDog(d, dmg, kx, ky, stun) {
  if (d.mode === 'ko') return;
  d.hp -= dmg; d.hop = 0;
  d.kx = kx; d.ky = ky;
  addFx('fx/hit', d.x, d.y - 40, { fps: 16 });
  SFX.hit();
  if (d.hp <= 0) {
    d.mode = 'ko'; d.setAnim('ko'); d.timer = 0;
    fled++;
    score += d.T.score;
    addPop('+' + d.T.score, d.x - 20, d.y - 120);
    SFX.flee();
    if (Math.random() < 0.5) items.push({ n: Math.random() < 0.75 ? 'bone' : 'sausage', x: d.x, y: d.y - 20, t: 0 });
  } else {
    d.mode = 'hurt'; d.setAnim('hurt'); d.timer = stun;
  }
}

function doBark() {
  const [vx, vy] = DIRV[P.dir];
  const mouth = { right: [40, -44], left: [-40, -44], up: [0, -86], down: [0, -26] }[P.dir];
  const ang = { right: 0, down: Math.PI / 2, left: Math.PI, up: -Math.PI / 2 }[P.dir];
  addFx('fx/bark', P.x + mouth[0], P.y + mouth[1], { angle: ang, fps: 12 });
  addBarkRing(P.x, P.y, P.dir, BARK, '#FFF7E6');
  SFX.bark(1);
  for (const d of dogs) {
    if (d.mode === 'ko') continue;
    const dx = d.x - P.x, dy = d.y - P.y, l = Math.hypot(dx, dy);
    if (l > BARK.range || l < 1) continue;
    const cos = (dx * vx + dy * vy) / l;
    if (cos <= BARK.cos) continue;
    if (balade()) { callDog(d); continue; }
    if (d.T.barkImmune) {
      // aucun effet : il se fâche et répond
      if (!pops.some(p => p.word && p.dog === d)) { addWordPop('Même pas peur !', d.x, d.y - 130); pops[pops.length - 1].dog = d; }
      d.mode = 'chase';
      d.barkCd = Math.min(d.barkCd, 0.4);
      if (!barkImmuneSeen) {
        barkImmuneSeen = true;
        pendingSay = { t: 0.7, lines: [{ who: 'tecky', face: 0,
          text: "Grr… Ce doberman n'a pas peur de mes aboiements. Il va falloir le mordre !" }] };
      }
      continue;
    }
    hurtDog(d, 1, dx / l * 380, dy / l * 380, 1.1);
  }
  for (const h of hens) {
    const dx = h.x - P.x, dy = h.y - P.y, l = Math.hypot(dx, dy);
    if (l > 1 && l < BARK.range && (dx * vx + dy * vy) / l > BARK.cos) scareHen(h, P.x, P.y, HEN.fleeT);
  }
  for (const b of butterflies) {
    const dx = b.x - P.x, dy = b.y - P.y, l = Math.hypot(dx, dy);
    if (l > 1 && l < BARK.range && (dx * vx + dy * vy) / l > BARK.cos) scareButterfly(b, P.x, P.y);
  }
}

/* ------------------------------------------------------------------ circulation */
/* Voitures, camionnette et bus roulent à droite sur la grande route (voie du haut vers l'ouest, du bas vers l'est)
   et réapparaissent de l'autre côté de la carte. Un véhicule klaxonne quand Tecky est devant lui, et s'il le touche,
   le projette sur le bas-côté, sans dégâts (« Ouf ! »). Aux passages piétons, ils s'arrêtent toujours pour Tecky.
   Les chiens sont aussi écartés de la route. */
const VEHICLE = { car: { len: 116, spd: 215, pitch: 1.15 }, van: { len: 146, spd: 185, pitch: 1 },
                  bus: { len: 240, spd: 140, pitch: 0.75 } };
const TRAFFIC = { gap: 60, accel: 260, brake: 900, honk: 300, knock: 950, look: 230 };
function newVehicle([name, lane, x]) {
  return { name, lane, x, T: VEHICLE[name.split('_')[0]], dir: lane === 0 ? -1 : 1, y: MAP.traffic.lanes[lane],
    v: VEHICLE[name.split('_')[0]].spd, t: Math.random(), honkT: 0 };
}
// passage piéton où se trouve (ou entre) Tecky, sinon null
function crossingAt(x, y) {
  const [r0, r1] = MAP.traffic.road;
  if (y < r0 - 24 || y > r1 + 34) return null;
  return MAP.traffic.crossings.find(([x0, x1]) => x > x0 - 18 && x < x1 + 18) || null;
}
// dans la bande de la voie, devant la carrosserie (pieds de 12 px de haut)
const inLane = (v, y) => y > v.y - 58 && y < v.y + 6;
function updateVehicle(v, dt) {
  const W = MAP.w * TS, half = v.T.len / 2;
  // sortie de carte : il réapparaît de l'autre côté dès que la place est libre
  if (v.dir > 0 ? v.x - half > W + 40 : v.x + half < -40) {
    const nx = v.dir > 0 ? -half - 40 : W + half + 40;
    if (!cars.some(o => o !== v && o.lane === v.lane && Math.abs(o.x - nx) < half + o.T.len / 2 + TRAFFIC.gap)) {
      v.x = nx; v.v = v.T.spd;
    }
    return;
  }
  const front = v.x + v.dir * half;
  let target = v.T.spd;
  for (const o of cars) if (o !== v && o.lane === v.lane) {          // garder ses distances
    const gap = (o.x - v.x) * v.dir - half - o.T.len / 2;
    if (gap > -20 && gap < TRAFFIC.look) target = Math.min(target, Math.max(0, (gap - TRAFFIC.gap) * 2.2));
  }
  const cw = P.mode !== 'ko' ? crossingAt(P.x, P.y) : null;
  if (cw) {                                                           // Tecky sur le passage : on s'arrête avant
    const stop = (v.dir > 0 ? cw[0] - 14 : cw[1] + 14);
    const gap = (stop - front) * v.dir;
    if (gap > -6 && gap < TRAFFIC.look) target = Math.min(target, Math.max(0, gap * 2.2));
  }
  v.v = target < v.v ? Math.max(target, v.v - TRAFFIC.brake * dt) : Math.min(target, v.v + TRAFFIC.accel * dt);
  v.x += v.dir * v.v * dt;
  v.t += dt * v.v / 90;                                                // enjoliveurs
  v.honkT -= dt;
  if (P.mode === 'ko' || state !== 'play') return;
  const ahead = (P.x - v.x) * v.dir;
  if (!cw && inLane(v, P.y) && ahead > 0 && ahead < half + TRAFFIC.honk && v.v > 40 && v.honkT <= 0) {
    SFX.honk(v.T.pitch); v.honkT = 2.5;
  }
  const mid = (MAP.traffic.road[0] + MAP.traffic.road[1]) / 2;
  if (!cw && inLane(v, P.y) && Math.abs(P.x - v.x) < half + 10 && v.v > 30 && P.bumpT <= 0) {
    // projeté sur le bas-côté le plus proche, sans dégâts
    P.kx = v.dir * 220; P.ky = (P.y < mid ? -1 : 1) * TRAFFIC.knock;
    P.mode = 'hurt'; P.setAnim('hurt'); P.timer = 0.25; P.bumpT = 1;
    shake = 0.15;
    for (let k = 0; k < 4; k++) addDust(P.x + (Math.random() - 0.5) * 30, P.y - 2, (Math.random() - 0.5) * 90, -10 - Math.random() * 20, 6 + Math.random() * 3);
    addWordPop('Ouf !', P.x, P.y - 130);
  }
  for (const d of dogs) if (d.mode !== 'ko' && inLane(v, d.y) && Math.abs(d.x - v.x) < half + 6 && v.v > 30) {
    d.kx = v.dir * 160; d.ky = (d.y < mid ? -1 : 1) * 760;
    if (d.mode !== 'hurt') { d.mode = 'hurt'; d.setAnim('hurt'); d.timer = 0.5; }
  }
}

/* ------------------------------------------------------------------ papillons */
// Ils volettent en zigzag autour de leur coin (surtout au parc ; petite ombre au sol), se posent parfois sur un pot
// de fleurs ou un massif proche (MAP.flowers) en ouvrant et fermant lentement les ailes, et s'envolent, plus haut et
// plus vite, si Tecky s'approche ou aboie vers eux. Ils volent au-dessus de tout : pas de collision.
const BFLY = { roam: 190, spd: 55, alt: 36, flee: 240, fleeT: 1.3, scare: 80, perch: 0.35, sc: 0.8 };
function newButterfly([color, x, y]) {
  return { color, x, y, hx: x, hy: y, tx: x, ty: y, alt: BFLY.alt, t: Math.random() * 9, flap: Math.random() * 4,
    mode: 'fly', timer: 0, heading: -Math.PI / 2, perch: null };
}
function pickTarget(b) {          // parfois une fleur libre à portée, sinon un point au hasard autour de sa place
  const free = MAP.flowers.filter(f => dist(f[0], f[1], b.hx, b.hy) < BFLY.roam * 1.3 && !butterflies.some(o => o !== b && o.perch === f));
  if (free.length && Math.random() < BFLY.perch) {
    b.perch = free[Math.floor(Math.random() * free.length)]; b.tx = b.perch[0]; b.ty = b.perch[1];
  } else {
    const a = Math.random() * Math.PI * 2, r = Math.random() * BFLY.roam;
    b.perch = null; b.tx = b.hx + Math.cos(a) * r; b.ty = b.hy + Math.sin(a) * r * 0.7;
  }
}
function scareButterfly(b, fromX, fromY) {
  if (b.mode === 'flee') return;
  const dx = b.x - fromX, dy = b.y - fromY, l = Math.max(1, Math.hypot(dx, dy));
  b.mode = 'flee'; b.timer = BFLY.fleeT; b.vx = dx / l; b.vy = dy / l; b.perch = null;
}
function updateButterfly(b, dt) {
  b.t += dt;
  if (P.mode !== 'ko' && dist(b.x, b.y, P.x, P.y) < BFLY.scare) scareButterfly(b, P.x, P.y);
  const ease = (want, k) => { b.alt += (want - b.alt) * Math.min(1, dt * k); };
  if (b.mode === 'rest') {                                    // posé : ouvre et ferme lentement les ailes
    b.flap += dt * 3;
    ease(b.perch[2], 6);
    if ((b.timer -= dt) <= 0) { b.mode = 'fly'; pickTarget(b); }
    return;
  }
  let vx, vy, spd;
  if (b.mode === 'flee') {
    b.flap += dt * 22;
    vx = b.vx; vy = b.vy; spd = BFLY.flee * Math.max(0.3, b.timer / BFLY.fleeT);
    ease(BFLY.alt * 2, 3);
    if ((b.timer -= dt) <= 0) { b.mode = 'fly'; pickTarget(b); }   // puis il revient vers sa place
  } else {
    b.flap += dt * 14;
    const dx = b.tx - b.x, dy = b.ty - b.y, l = Math.hypot(dx, dy);
    if (l < 8) {
      if (b.perch) { b.mode = 'rest'; b.timer = 2 + Math.random() * 2.5; } else pickTarget(b);
      return;
    }
    const w = Math.sin(b.t * 5.3) * 0.7;                       // zigzag
    vx = dx / l - dy / l * w; vy = dy / l + dx / l * w;
    const n = Math.hypot(vx, vy); vx /= n; vy /= n;
    spd = BFLY.spd * (l < 40 ? 0.6 : 1);
    ease(b.perch && l < 70 ? b.perch[2] : BFLY.alt + Math.sin(b.t * 2.6) * 10, 3);
  }
  b.x += vx * spd * dt; b.y += vy * spd * dt;
  b.heading = Math.atan2(vy, vx);
}

/* ------------------------------------------------------------------ poules */
// Elles picorent et se promènent autour de leur place ; un aboiement de Tecky (même cône, même portée que pour les
// chiens) les fait fuir de quelques pas en battant des ailes. Elles ne bloquent pas : si Tecky leur fonce dessus,
// elles s'écartent aussi.
const HEN = { roam: 64, spd: 34, flee: 260, fleeT: 0.85, bump: 40, bumpT: 0.45 };
const HEN_FPS = { idle: 4, peck: 10, walk: 10, flap: 14 };      // comme hens.py
let lastCluck = -1;
function newHen([kind, x, y]) {
  const h = new Actor(kind, x, y);
  return Object.assign(h, { fps: HEN_FPS, hx: x, hy: y, mode: 'idle', timer: Math.random() * 2,
    dir: Math.random() < 0.5 ? 'left' : 'right' });
}
function scareHen(h, fromX, fromY, t) {
  if (h.mode === 'flee' && h.timer >= t) return;
  if (h.mode !== 'flee' && timePlayed - lastCluck > 0.15) { lastCluck = timePlayed; SFX.cluck(); }
  const dx = h.x - fromX, dy = h.y - fromY, l = Math.max(1, Math.hypot(dx, dy));
  h.mode = 'flee'; h.timer = t; h.fleeT = t; h.vx = dx / l; h.vy = dy / l;
  h.dir = h.vx < 0 ? 'left' : 'right';
  h.setAnim('flap');
}
function updateHen(h, dt) {
  h.t += dt;
  h.timer -= dt;
  if (P.mode !== 'ko' && dist(h.x, h.y, P.x, P.y) < HEN.bump) scareHen(h, P.x, P.y, HEN.bumpT);
  switch (h.mode) {
    case 'flee': {
      const k = Math.max(0.25, h.timer / h.fleeT);              // ralentit en fin de fuite
      moveActor(h, h.vx * HEN.flee * k * dt, h.vy * HEN.flee * k * dt, 8);
      if (h.timer <= 0) { h.mode = 'idle'; h.timer = 0.6 + Math.random(); h.setAnim('idle'); }
      return;
    }
    case 'peck':
      if (h.done()) { h.mode = 'idle'; h.timer = 0.3 + Math.random() * 1.2; h.setAnim('idle'); }
      return;
    case 'walk': {
      const dx = h.tx - h.x, dy = h.ty - h.y, l = Math.hypot(dx, dy), ox = h.x, oy = h.y;
      if (l > 4) moveActor(h, dx / l * HEN.spd * dt, dy / l * HEN.spd * dt, 8);
      if (l <= 4 || h.timer <= 0 || (ox === h.x && oy === h.y)) { h.mode = 'idle'; h.timer = 0.4 + Math.random(); h.setAnim('idle'); }
      return;
    }
    default:   // au repos : picorer (le plus souvent) ou faire quelques pas autour de sa place
      if (h.timer > 0) return;
      if (Math.random() < 0.6) { h.mode = 'peck'; h.setAnim('peck'); return; }
      const a = Math.random() * Math.PI * 2, r = Math.random() * HEN.roam;
      h.tx = h.hx + Math.cos(a) * r; h.ty = h.hy + Math.sin(a) * r * 0.6;
      h.dir = h.tx < h.x ? 'left' : 'right';
      h.mode = 'walk'; h.timer = 2.5; h.setAnim('walk');
  }
}

function doBite() {
  const [vx, vy] = DIRV[P.dir];
  const hx = P.x + vx * 58, hy = P.y - 22 + vy * 46;
  addFx('fx/bite', hx, hy, { fps: 18 });
  SFX.bite();
  if (balade()) return;                // en balade, une morsure dans le vide ne blesse personne
  let hit = false;
  for (const d of dogs) {
    if (d.mode === 'ko') continue;
    if (dist(hx, hy, d.x, d.y - 26) < 66) {
      const l = Math.max(1, dist(P.x, P.y, d.x, d.y));
      hurtDog(d, 2, (d.x - P.x) / l * 300, (d.y - P.y) / l * 300, 0.35);
      hit = true;
    }
  }
}

/* ------------------------------------------------------------------ gratter, lire */
// menace immédiate : un chien lancé contre Tecky et tout proche. Mordre passe alors avant gratter ou lire.
const THREAT_R = 240;
const ENGAGED = new Set(['chase', 'attack', 'bark', 'hurt', 'crouch', 'charge', 'tired']);
function threatened() {
  if (balade()) return false;          // en balade, les chiens ne menacent personne
  return dogs.some(d => ENGAGED.has(d.mode) && dist(P.x, P.y, d.x, d.y) < THREAT_R);
}
function nearDig() {
  for (const g of digs) if (!g.dug && dist(P.x, P.y, g.x, g.y + 6) < 86) return g;
  return null;
}
// panneau à portée : [x, y, texte]
function nearSign() {
  for (const s of MAP.signs) if (dist(P.x, P.y, s[0], s[1] + 30) < 95) return s;
  return null;
}
// ce que fait C (le bouton de morsure) : mordre si un chien menace, sinon gratter un trésor
// ou lire un panneau à portée, sinon mordre
// en balade : un chien à portée de jeu (les copains passent après les trésors et les panneaux)
function playTarget(friends) {
  let best = null, bd = PLAY.reach;
  for (const d of dogs) {
    if (d.mode === 'ko' || d.mode === 'play' || !!d.friend !== friends) continue;
    const l = dist(P.x, P.y, d.x, d.y);
    if (l < bd) { best = d; bd = l; }
  }
  return best;
}
const playDog = () => playTarget(false) || playTarget(true);
function biteAction() {
  if (threatened()) return 'bite';
  if (balade() && playTarget(false)) return 'play';
  if (nearDig()) return 'dig';
  if (nearSign()) return 'read';
  if (balade() && playTarget(true)) return 'play';
  return 'bite';
}
const ACTION_FRAME = { bite: 2, dig: 4, read: 6, play: 8 };   // images de hud/action
// Tecky et le chien sautillent ensemble ; à la fin, le chien devient un copain (voir updateDog, mode 'play')
function startPlay(d) {
  P.mode = 'play'; P.timer = PLAY.tecky; P.setAnim('idle'); P.cdBite = 0.5; P.cdBiteMax = 0.5;
  P.dir = dirFrom(d.x - P.x, d.y - P.y, P.dir);
  d.mode = 'play'; d.timer = PLAY.time; d.heartT = 0; d.hop = 0; d.wait = 0;
  d.dir = dirFrom(P.x - d.x, P.y - d.y, d.dir);
  d.setAnim('idle');
  SFX.yip(d.T.pitch);
}
// aboiement en balade : le chien répond (petit bond, cœur) et accourt pour jouer
function callDog(d) {
  if (d.mode === 'play') return;
  d.hopT = 0.4; d.calm = 0; d.wait = 0;
  addFx('fx/heart', d.x, d.y - 96, { fps: 10 });
  if (d.mode !== 'wait') { d.mode = 'chase'; d.setAnim('walk'); }
}
function startDig(g) {
  P.mode = 'dig'; P.setAnim('dig'); P.timer = 1.0; P.digSpot = g; P.digTick = 0;
  P.dir = dirFrom(g.x - P.x, g.y - P.y, P.dir);
}
function updateDig(dt) {
  const g = P.digSpot;
  P.digTick -= dt;
  if (P.digTick <= 0) {
    P.digTick = 0.16;
    const [vx, vy] = DIRV[P.dir];
    // la terre part derrière Tecky
    addFx('fx/dirt', g.x - vx * 10 + (Math.random() - 0.5) * 16, g.y + 4 - vy * 6, { fps: 16 });
    SFX.scratch();
  }
  P.timer -= dt;
  if (P.timer <= 0) { P.mode = 'free'; uncover(g); }
}
function uncover(g) {
  g.dug = true; treasures++; score += 100;
  items.push({ n: 'medal', x: g.x, y: g.y - 30, t: 0, pop: 0.001 });
  addFx('fx/pickup', g.x, g.y - 20, { fps: 12 });
  addPop('+100', g.x - 30, g.y - 90);
  SFX.treasure();
  shake = 0.15;
  say([{ who: 'tecky', face: 2, text: "Wouf ! Un trésor enterré ! (" + treasures + " / " + MAP.dig.length + ")" }], saveGame);
}

function hurtPlayer(dmg, fromX, fromY) {
  if (P.inv > 0 || P.mode === 'ko' || state !== 'play' || balade()) return;
  P.hp = Math.max(0, P.hp - dmg);
  const l = Math.max(1, dist(P.x, P.y, fromX, fromY));
  P.kx = (P.x - fromX) / l * 420; P.ky = (P.y - fromY) / l * 420;
  P.inv = 1.2; shake = 0.25;
  addFx('fx/hit', P.x, P.y - 44, { fps: 16 });
  SFX.hurt();
  if (P.hp <= 0) {
    P.mode = 'ko'; P.setAnim('ko'); P.timer = 0;
    Music.stop();
    Music.start('lose');
  } else {
    P.mode = 'hurt'; P.setAnim('hurt'); P.timer = 0.25;
  }
}

/* ------------------------------------------------------------------ petits effets */
/* Poussière : petits nuages clairs sous les pattes de Tecky quand il marche (et quand une voiture le bouscule,
   ou quand le berger charge). Au sol, sous les personnages. */
const DUST = { every: 0.12, life: 0.45, max: 40 };
function addDust(x, y, vx, vy, r) { if (dusts.length < DUST.max) dusts.push({ x, y, vx, vy, r, t: 0 }); }
function updateDust(dt) {
  const damp = Math.pow(0.02, dt);
  for (let i = dusts.length - 1; i >= 0; i--) {
    const d = dusts[i];
    if ((d.t += dt) > DUST.life) { dusts.splice(i, 1); continue; }
    d.x += d.vx * dt; d.y += d.vy * dt; d.vx *= damp; d.vy *= damp;
  }
}
function drawDust() {
  ctx.save();
  ctx.fillStyle = '#F1E7D0';
  for (const d of dusts) {
    const u = d.t / DUST.life;
    ctx.globalAlpha = 0.55 * (1 - u);
    ctx.beginPath(); ctx.ellipse(d.x, d.y - u * 6, d.r * (1 + u * 1.3), d.r * (0.8 + u), 0, 0, Math.PI * 2); ctx.fill();
  }
  ctx.restore();
}

/* Feuilles : les arbres et les sapins à l'écran en lâchent de temps en temps (fx/leaf, une image par couleur).
   Elles tournoient en descendant avec une petite ombre au sol, se posent, puis s'effacent. */
const LEAF = { rate: 0.08, max: 50, fall: 34, sway: 14, rest: 2.2, fade: 0.8 };
function updateLeaves(dt) {
  if (!leafTrees) leafTrees = decor.filter(d => d.n === 'tree' || d.n === 'fir');
  for (const tr of leafTrees) {
    if (leaves.length >= LEAF.max) break;
    if (tr.x < camX - 60 || tr.x > camX + VW + 60 || tr.y < camY - 20 || tr.y > camY + VH + 160) continue;
    if (Math.random() < LEAF.rate * dt) {
      const fir = tr.n === 'fir';                     // aiguilles vertes pour les sapins, toutes les couleurs ailleurs
      leaves.push({ x: tr.x + (Math.random() - 0.5) * (fir ? 56 : 80), y: tr.y + 2 + Math.random() * 36,
        h: (fir ? 70 : 80) + Math.random() * 50, t: 0, ph: Math.random() * 6.28, landed: 0,
        c: fir ? Math.floor(Math.random() * 2) : Math.floor(Math.random() * 4) });
    }
  }
  for (let i = leaves.length - 1; i >= 0; i--) {
    const l = leaves[i];
    l.t += dt;
    if (l.h > 0) { l.h = Math.max(0, l.h - LEAF.fall * dt); if (!l.h) l.landed = l.t; }
    else if (l.t - l.landed > LEAF.rest + LEAF.fade) leaves.splice(i, 1);
  }
}
const leafX = l => l.x + Math.sin((l.h ? l.t : l.landed) * 1.8 + l.ph) * LEAF.sway;
function drawLeavesOnGround() {                       // feuilles posées, ombres des feuilles qui tombent
  for (const l of leaves) {
    if (l.h > 0) {
      ctx.save(); ctx.globalAlpha = 0.16; ctx.fillStyle = '#000';
      ctx.beginPath(); ctx.ellipse(leafX(l), l.y, 5, 2, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
    } else {
      const a = 1 - Math.max(0, l.t - l.landed - LEAF.rest) / LEAF.fade;
      drawSpr('fx/leaf', l.c, leafX(l), l.y, { angle: l.ph, alpha: a });
    }
  }
}
function drawFallingLeaves() {
  for (const l of leaves) if (l.h > 0)
    drawSpr('fx/leaf', l.c, leafX(l), l.y - l.h, { angle: Math.sin(l.t * 2.4 + l.ph) * 0.9,
      sy: 0.3 + 0.7 * Math.abs(Math.cos(l.t * 3.1 + l.ph)) });
}

/* Ombres de nuages : de grandes taches douces (amas de disques flous pré-rendus) qui glissent lentement sur la
   carte, et sur tout ce qui s'y trouve. */
const CLOUD = { n: 14, vx: 14, vy: 4, alpha: 0.1, w: 560, h: 320 };
let cloudImgs = [];
function buildClouds() {
  cloudImgs = [0, 1, 2].map(k => {
    const c = document.createElement('canvas');
    c.width = CLOUD.w; c.height = CLOUD.h;
    const g = c.getContext('2d');
    for (let i = 0; i < 9; i++) {
      const r = 70 + hash3(k, i, 1) * 60;
      const x = 120 + hash3(k, i, 2) * (CLOUD.w - 240), y = 110 + hash3(k, i, 3) * (CLOUD.h - 220);
      const gr = g.createRadialGradient(x, y, r * 0.45, x, y, r);
      gr.addColorStop(0, 'rgba(24, 30, 56, 1)'); gr.addColorStop(1, 'rgba(24, 30, 56, 0)');
      g.fillStyle = gr; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
    }
    return c;
  });
  const W = MAP.w * TS + CLOUD.w, H = MAP.h * TS + CLOUD.h;
  clouds = Array.from({ length: CLOUD.n }, (_, i) => ({ img: i % 3, x: hash3(i, 5, 9) * W - CLOUD.w, y: hash3(i, 7, 3) * H - CLOUD.h }));
}
function updateClouds(dt) {
  const W = MAP.w * TS, H = MAP.h * TS;
  for (const c of clouds) {
    c.x += CLOUD.vx * dt; c.y += CLOUD.vy * dt;
    if (c.x > W) c.x -= W + CLOUD.w;                  // ressort de l'autre côté
    if (c.y > H) c.y -= H + CLOUD.h;
  }
}
function drawClouds(cx, cy) {
  ctx.save();
  ctx.globalAlpha = CLOUD.alpha;
  for (const c of clouds)
    if (c.x < cx + VW && c.x + CLOUD.w > cx && c.y < cy + VH && c.y + CLOUD.h > cy) ctx.drawImage(cloudImgs[c.img], c.x, c.y);
  ctx.restore();
}

/* Coucher de soleil : la lumière suit la progression, un cran par indice (0 : plein jour, 3 : soleil couchant), et se
   réchauffe encore aux retrouvailles avec Alice (4). Teinte multipliée sur le monde (pas sur l'interface), halo doré
   venant de l'ouest, vignette au crépuscule ; les lampadaires s'allument à partir du deuxième indice. */
const SUN = { speed: 0.25, tints: [[255, 255, 255], [255, 241, 220], [255, 222, 182], [238, 180, 150], [255, 200, 160]],
  glow: [0, 0.08, 0.16, 0.22, 0.3], vignette: [0, 0, 0.06, 0.2, 0.1] };
const sunGoal = () => alice.found ? 4 : clues.filter(Boolean).length;
function updateSun(dt) { sun += clamp(sunGoal() - sun, -SUN.speed * dt, SUN.speed * dt); }
const sunAt = (arr, k) => { const i = Math.min(arr.length - 2, Math.floor(k)), f = k - i; return arr[i] + (arr[i + 1] - arr[i]) * f; };
function drawLight(cx, cy) {
  if (sun < 0.01) return;
  const k = clamp(sun, 0, 4);
  const tint = [0, 1, 2].map(j => Math.round(sunAt(SUN.tints.map(t => t[j]), k)));
  ctx.save();
  ctx.globalCompositeOperation = 'multiply';
  ctx.fillStyle = `rgb(${tint[0]}, ${tint[1]}, ${tint[2]})`;
  ctx.fillRect(cx, cy, VW, VH);
  const vig = sunAt(SUN.vignette, k);
  if (vig > 0) {
    const g = ctx.createRadialGradient(cx + VW / 2, cy + VH / 2, VH * 0.45, cx + VW / 2, cy + VH / 2, VW * 0.62);
    g.addColorStop(0, 'rgba(90, 50, 110, 0)'); g.addColorStop(1, `rgba(90, 50, 110, ${vig})`);
    ctx.fillStyle = g; ctx.fillRect(cx, cy, VW, VH);
  }
  ctx.globalCompositeOperation = 'screen';
  const glow = sunAt(SUN.glow, k);
  const g = ctx.createLinearGradient(cx, cy, cx + VW, cy + VH * 0.5);
  g.addColorStop(0, `rgba(255, 190, 110, ${glow})`); g.addColorStop(1, 'rgba(255, 190, 110, 0)');
  ctx.fillStyle = g; ctx.fillRect(cx, cy, VW, VH);
  // lampadaires allumés en fin de journée : halo autour de la lanterne et flaque de lumière au sol
  const lamp = clamp(k - 1.5, 0, 1);
  if (lamp > 0) for (const d of decor) {
    if (d.n !== 'lamppost' || d.x < cx - 120 || d.x > cx + VW + 120 || d.y < cy - 40 || d.y > cy + VH + 160) continue;
    for (const [x, y, r, a] of [[d.x, d.y - 93, 64, 0.55], [d.x, d.y - 4, 70, 0.3]]) {
      const h = ctx.createRadialGradient(x, y, 4, x, y, r);
      h.addColorStop(0, `rgba(255, 214, 130, ${a * lamp})`); h.addColorStop(1, 'rgba(255, 214, 130, 0)');
      ctx.fillStyle = h; ctx.fillRect(x - r, y - r, r * 2, r * 2);
    }
  }
  // retrouvailles : une lumière chaude autour d'Alice et de Tecky
  const hug = clamp(k - 3, 0, 1);
  if (hug > 0) {
    const x = (alice.x + P.x) / 2, y = (alice.y + P.y) / 2 - 50;
    const h = ctx.createRadialGradient(x, y, 20, x, y, 260);
    h.addColorStop(0, `rgba(255, 210, 150, ${0.45 * hug})`); h.addColorStop(1, 'rgba(255, 210, 150, 0)');
    ctx.fillStyle = h; ctx.fillRect(x - 260, y - 260, 520, 520);
  }
  ctx.restore();
}

/* ------------------------------------------------------------------ sauvegarde, records */
/* La partie est enregistrée dans le navigateur (localStorage, en mémoire si le stockage est refusé) : toutes les
   SAVE_EVERY secondes de jeu quand aucun chien ne menace Tecky, à chaque indice et chaque trésor, et quand on quitte
   la page. L'écran titre propose alors « Continuer » ; après un KO, « Reprendre la partie » repart de cette
   sauvegarde, vie pleine. La victoire efface la sauvegarde et met à jour les records de son mode (meilleur score,
   meilleur temps). */
const SAVE_KEY = 'tecky-quest-save', RECORDS_KEY = 'tecky-quest-records', SAVE_EVERY = 4;
const STORE = {
  mem: {},
  get(k) {
    try { const v = localStorage.getItem(k); if (v !== null) return JSON.parse(v); } catch (e) { /* stockage refusé */ }
    return this.mem[k] || null;
  },
  set(k, v) { this.mem[k] = v; try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* idem */ } },
  del(k) { delete this.mem[k]; try { localStorage.removeItem(k); } catch (e) { /* idem */ } },
};
function loadSave() { const s = STORE.get(SAVE_KEY); return s && s.v === 1 ? s : null; }
const r1 = v => Math.round(v * 10) / 10;
function saveGame() {
  if (!P || P.mode === 'ko' || P.hp <= 0 || alice.found) return;
  STORE.set(SAVE_KEY, {
    v: 1, mode: gameMode, at: Date.now(), x: r1(P.x), y: r1(P.y), dir: P.dir, hp: P.hp, hpMax: P.hpMax,
    score, time: r1(timePlayed), fled, treasures, clues: clues.slice(), sniffed: aliceSniffed, immune: barkImmuneSeen,
    dug: digs.map(g => g.dug ? 1 : 0),
    items: items.map(it => [it.n, r1(it.x), r1(it.y)]),
    dogs: dogs.filter(d => d.mode !== 'ko').map(d => d.id),
    friends: dogs.filter(d => d.friend).map(d => d.id),        // balade : chiens devenus copains
  });
}
// pas de sauvegarde automatique en plein combat : on reprendrait au milieu des crocs
const safeToSave = () => P.mode !== 'ko' && (balade() || !dogs.some(d => ENGAGED.has(d.mode) && dist(P.x, P.y, d.x, d.y) < 600));
function saveOnLeave() { if (P && (state === 'play' || state === 'dialog' || state === 'pause')) saveGame(); }
addEventListener('pagehide', saveOnLeave);
document.addEventListener('visibilitychange', () => { if (document.hidden) saveOnLeave(); });

/* rested : reprise après un KO (Tecky a fait une sieste : vie pleine) */
function loadGame(s, rested) {
  reset();
  gameMode = s.mode === 'balade' ? 'balade' : 'aventure';
  Object.assign(P, { x: s.x, y: s.y, dir: s.dir || 'down', hpMax: s.hpMax, hp: rested ? s.hpMax : Math.max(1, s.hp) });
  score = s.score; timePlayed = s.time; fled = s.fled; treasures = s.treasures;
  clues = [0, 1, 2].map(i => !!s.clues[i]); aliceSniffed = !!s.sniffed; barkImmuneSeen = !!s.immune;
  digs.forEach((g, i) => { g.dug = !!s.dug[i]; });
  items = s.items.map(([n, x, y]) => ({ n, x, y, t: Math.random() * 3 }));
  dogs = dogs.filter(d => s.dogs.includes(d.id));
  for (const d of dogs) d.friend = (s.friends || []).includes(d.id);
  if (nextClue() === 3) revealAlice();
  sun = sunGoal();
  camX = clamp(P.x - VW / 2, 0, MAP.w * TS - VW);
  camY = clamp(P.y - 40 - VH / 2, 0, MAP.h * TS - VH);
  state = 'play';
  Music.start();
  say([{ who: 'tecky', face: rested ? 0 : 2, text: rested ? "Ouf, une petite sieste et ça repart !" : "Me revoilà ! Je reprends mes recherches." },
       { who: 'tecky', face: 0, text: CLUE_NEXT[nextClue()] }], () => showArrow());
}
function newGame(mode, again) {
  const cx = camX, cy = camY;
  reset();
  gameMode = mode;
  if (!again) { camX = cx; camY = cy; }          // depuis l'écran titre, la caméra glisse du village jusqu'à la niche
  state = 'play';
  Music.start();
  say(again ? [{ who: 'tecky', face: 0, text: "C'est reparti ! Je vais retrouver les affaires d'Alice, et Alice avec." }] : introLines(),
    () => { showArrow(); saveGame(); });
}

let recs = {}, newRecord = { score: false, time: false };
function recordRun() {
  const all = STORE.get(RECORDS_KEY) || {}, r = all[gameMode] || {}, t = Math.floor(timePlayed);
  newRecord = { score: !(r.score >= score), time: !(r.time <= t) };
  if (newRecord.score) r.score = score;
  if (newRecord.time) r.time = t;
  r.wins = (r.wins || 0) + 1;
  all[gameMode] = r;
  STORE.set(RECORDS_KEY, all);
  recs = all;
}
const fmtTime = t => Math.floor(t / 60) + ' min ' + String(Math.floor(t % 60)).padStart(2, '0') + ' s';
const MODE_NAME = { aventure: 'Aventure', balade: 'Balade' };
function recordLine(mode) {
  const r = recs[mode];
  if (!r || !r.wins) return '';
  return 'Records en ' + mode + ' : ' + r.score + ' points · ' + fmtTime(r.time);
}

/* ------------------------------------------------------------------ menus (écran titre, KO) */
/* Une liste d'entrées : flèches, croix ou stick pour choisir, Entrée / A pour valider ; au toucher ou à la souris,
   l'entrée touchée est choisie et validée. */
let menu = null;              // { items: [{ id, label, sub, mode }], sel, y0, w, h, gap }
function openTitleMenu() {
  recs = STORE.get(RECORDS_KEY) || {};
  const s = loadSave(), items = [];
  if (s) {
    const n = s.clues.filter(Boolean).length;
    items.push({ id: 'continue', label: 'Continuer', mode: s.mode,
      sub: MODE_NAME[s.mode] + ' · ' + (n ? n + (n > 1 ? ' indices' : ' indice') + ' sur 3' : 'aucun indice') + ' · ' + fmtTime(s.time) });
  }
  items.push({ id: 'aventure', label: 'Nouvelle aventure', sub: 'Gare aux chiens du coin !', mode: 'aventure' });
  items.push({ id: 'balade', label: 'Nouvelle balade', sub: 'Les chiens veulent seulement jouer', mode: 'balade' });
  menu = { items, sel: 0, y0: 520, w: 760, h: 104, gap: 20 };
}
function openOverMenu() {
  const items = [];
  if (loadSave()) items.push({ id: 'resume', label: 'Reprendre la partie', sub: 'Après une petite sieste, avec les indices trouvés' });
  items.push({ id: 'restart', label: 'Recommencer', sub: 'Depuis la niche, sans les indices' });
  items.push({ id: 'title', label: 'Menu principal', sub: 'Pour changer de mode' });
  menu = { items, sel: 0, y0: 600, w: 760, h: 96, gap: 18 };
}
function menuBox(i) {
  return { x: GW / 2 - menu.w / 2, y: menu.y0 + i * (menu.h + menu.gap), w: menu.w, h: menu.h };
}
function menuHit(gx, gy) {
  for (let i = 0; i < menu.items.length; i++) {
    const b = menuBox(i);
    if (gx > b.x && gx < b.x + b.w && gy > b.y && gy < b.y + b.h) return i;
  }
  return -1;
}
function menuInput() {
  const n = menu.items.length;
  if (pressed.up) { menu.sel = (menu.sel + n - 1) % n; SFX.blip(); }
  if (pressed.down) { menu.sel = (menu.sel + 1) % n; SFX.blip(); }
  return pressed.ok || pressed.bark || pressed.bite || pressed.act ? menu.items[menu.sel].id : null;
}
function chooseMenu(id) {
  const s = loadSave();
  menu = null;
  if (id === 'continue' && s) loadGame(s, false);
  else if (id === 'resume' && s) loadGame(s, true);
  else if (id === 'restart') newGame(gameMode, true);
  else if (id === 'aventure' || id === 'balade') newGame(id, false);
  else toTitle();
}
function toTitle() {
  reset();
  gameMode = 'aventure';
  camX = clamp(MAP.title[0] - VW / 2, 0, MAP.w * TS - VW);   // caméra de l'écran titre : la place du village
  camY = clamp(MAP.title[1] - VH / 2, 0, MAP.h * TS - VH);
  state = 'title'; titleT = 0;
  openTitleMenu();
  Music.start();
}

/* ------------------------------------------------------------------ mise à jour */
function inputVector() {
  let x = (held.right ? 1 : 0) - (held.left ? 1 : 0);
  let y = (held.down ? 1 : 0) - (held.up ? 1 : 0);
  if (stick.id !== null && Math.hypot(stick.vx, stick.vy) > 0.15) { x = stick.vx; y = stick.vy; }
  const pl = Math.hypot(pad.vx, pad.vy);
  if (pl > PAD_DEAD) {                    // stick de manette : zone morte retirée, la vitesse suit l'inclinaison
    const k = Math.min(1, (pl - PAD_DEAD) / (0.9 - PAD_DEAD));
    x = pad.vx / pl * k; y = pad.vy / pl * k;
  }
  const l = Math.hypot(x, y);
  if (l > 1) { x /= l; y /= l; }
  return [x, y];
}

function updatePlayer(dt) {
  P.t += dt;
  hintText = null;
  digHint = null;
  playHint = null;
  P.inv = Math.max(0, P.inv - dt);
  P.bumpT = Math.max(0, P.bumpT - dt);           // une voiture ne bouscule Tecky qu'une fois à la fois
  P.cdBark = Math.max(0, P.cdBark - dt);
  P.cdBite = Math.max(0, P.cdBite - dt);
  P.boneFx = Math.max(0, P.boneFx - dt * 1.5);
  // recul
  if (Math.abs(P.kx) + Math.abs(P.ky) > 5) {
    moveActor(P, P.kx * dt, P.ky * dt);
    const damp = Math.pow(0.004, dt);
    P.kx *= damp; P.ky *= damp;
  }
  if (P.mode === 'ko') {
    P.timer += dt;
    if (P.timer > 2.2) { state = 'over'; overT = 0; openOverMenu(); }
    return;
  }
  if (P.mode === 'hurt') {
    P.timer -= dt;
    if (P.timer <= 0) P.mode = 'free';
    return;
  }
  if (P.mode === 'bark') { if (P.done()) P.mode = 'free'; return; }
  if (P.mode === 'play') {             // balade : il sautille avec son copain
    P.timer -= dt;
    P.hop = Math.abs(Math.sin(P.timer * 10)) * 10;
    if (P.timer <= 0) { P.mode = 'free'; P.hop = 0; }
    return;
  }
  if (P.mode === 'dig') {
    // un chien arrive pendant qu'on gratte : C interrompt le grattage pour mordre
    if (!(pressed.bite && threatened())) { updateDig(dt); return; }
    P.mode = 'free';
  }
  if (P.mode === 'bite') {
    if (!P.hitDone && P.t > 0.12) { P.hitDone = true; doBite(); }
    if (P.done()) P.mode = 'free';
    return;
  }
  const [ix, iy] = inputVector();
  const spd = 250;
  if (ix || iy) {
    const ox = P.x, oy = P.y;
    moveActor(P, ix * spd * dt, iy * spd * dt);
    P.dir = dirFrom(ix, iy, P.dir);
    P.setAnim('walk');
    // petits nuages de poussière derrière les pattes
    if ((P.dustT = (P.dustT || 0) - dt) <= 0 && Math.hypot(P.x - ox, P.y - oy) > spd * dt * 0.5) {
      P.dustT = DUST.every;
      addDust(P.x - ix * 16 + (Math.random() - 0.5) * 10, P.y - 2, -ix * 30, -iy * 30 - 6, 5 + Math.random() * 3);
    }
  } else P.setAnim('idle');

  if (pressed.bark && P.cdBark <= 0) {
    P.mode = 'bark'; P.setAnim('bark'); P.cdBark = 1.0; P.cdBarkMax = 1.0; doBark();
  } else if (pressed.bite) {
    const a = biteAction();
    if (a === 'read') say([{ who: 'info', text: nearSign()[2] }]);
    else if (P.cdBite <= 0) {
      if (a === 'play') startPlay(playDog());
      else if (a === 'dig') startDig(nearDig());
      else { P.mode = 'bite'; P.setAnim('bite'); P.cdBite = 0.5; P.cdBiteMax = 0.5; P.hitDone = false; }
    }
  }

  // panneau (C ou E pour lire) et trésor à portée : bulles "lire" / "gratter"
  const sign = nearSign(), act = biteAction();
  if (sign && pressed.act) say([{ who: 'info', text: sign[2] }]);
  if (act === 'read') hintText = { x: sign[0], y: sign[1] - 110 };
  if (act === 'dig') digHint = nearDig();
  if (act === 'play') playHint = playDog();
  // Alice
  if (!alice.found && !alice.hidden && dist(P.x, P.y, alice.x, alice.y) < 120) finale();
  // devant la cachette trop tôt : Tecky la sent mais il lui manque des indices
  if (alice.hidden && !aliceSniffed && dist(P.x, P.y, alice.x, alice.y) < 170) {
    aliceSniffed = true;
    say([{ who: 'tecky', face: 0, text: "Hmm… ça sent Alice par ici, mais je ne la vois nulle part. Il me manque des indices !" }],
      () => showArrow());
  }
}

function updateDog(d, dt) {
  d.t += dt;
  const T = d.T;
  if (Math.abs(d.kx) + Math.abs(d.ky) > 5) {
    moveActor(d, d.kx * dt, d.ky * dt, 14);
    const damp = Math.pow(0.003, dt);
    d.kx *= damp; d.ky *= damp;
  }
  d.cd = Math.max(0, d.cd - dt);
  d.barkCd = Math.max(0, d.barkCd - dt);
  d.chargeCd = Math.max(0, d.chargeCd - dt);
  d.calm = Math.max(0, (d.calm || 0) - dt);
  if (d.hopT > 0) {                    // petit bond (appelé par un aboiement, ou impatient de jouer)
    d.hopT -= dt;
    d.hop = d.hopT > 0 ? Math.sin((1 - d.hopT / 0.4) * Math.PI) * 16 : 0;
  }
  const dx = P.x - d.x, dy = P.y - d.y, l = Math.hypot(dx, dy);
  const alive = P.mode !== 'ko';

  switch (d.mode) {
    case 'crouch':                     // berger : il se ramasse et tremble avant de charger
      d.timer -= dt;
      d.shake = Math.sin(d.t * 70) * 2;
      if (d.timer <= 0) { d.shake = 0; d.mode = 'charge'; d.timer = CHARGE.time; d.hitDone = false; d.setAnim('walk');
        addFx('fx/dirt', d.x - d.cx * 20, d.y, { fps: 16 }); }
      return;
    case 'charge': {
      d.timer -= dt;
      const ox = d.x, oy = d.y, st = CHARGE.speed * dt;
      moveActor(d, d.cx * st, d.cy * st, 14, true);
      if ((d.dustT = (d.dustT || 0) - dt) <= 0) { d.dustT = 0.05; addDust(d.x - d.cx * 22, d.y - 2, -d.cx * 40, -d.cy * 40 - 8, 6); }
      if (!d.hitDone && dist(d.x, d.y, P.x, P.y) < 52) { d.hitDone = true; hurtPlayer(T.dmg, d.x, d.y); }
      if (d.timer <= 0 || Math.hypot(d.x - ox, d.y - oy) < st * 0.3) {   // fin de course ou obstacle
        d.mode = 'tired'; d.timer = CHARGE.tired; d.chargeCd = CHARGE.cd; d.setAnim('idle');
      }
      return;
    }
    case 'tired':                      // essoufflé après la charge : le moment de le mordre
      d.timer -= dt;
      if (d.timer <= 0) d.mode = 'chase';
      return;
    case 'play': {                     // balade : il joue avec Tecky en semant des cœurs, puis devient son copain
      d.timer -= dt;
      d.dir = dirFrom(dx, dy, d.dir);
      d.hop = Math.abs(Math.sin(d.timer * 9)) * PLAY.hop;
      if ((d.heartT -= dt) <= 0) { d.heartT = PLAY.heartEvery; addFx('fx/heart', d.x + (Math.random() - 0.5) * 30, d.y - 96, { fps: 10 }); }
      if (d.timer <= 0) {
        d.hop = 0; d.mode = 'return'; d.calm = PLAY.calm; d.setAnim('walk');
        if (!d.friend) {
          d.friend = true; fled++; score += T.score;
          addPop('+' + T.score, d.x - 20, d.y - 120);
          addWordPop('Copain !', d.x, d.y - 150);
          SFX.treasure();
        }
      }
      return;
    }
    case 'wait': {                     // balade : il attend que Tecky joue avec lui, en sautillant
      d.dir = dirFrom(dx, dy, d.dir);
      d.setAnim('idle');
      d.wait += dt;
      if ((d.timer -= dt) <= 0) { d.timer = PLAY.waitHop; d.hopT = 0.4; }
      if (d.wait > PLAY.patience || !alive) { d.mode = 'return'; d.calm = PLAY.calm; d.wait = 0; }
      else if (l > T.range * 1.8) d.mode = 'chase';
      return;
    }
    case 'ko':
      d.timer += dt;
      if (d.timer > 1.6) d.fade += dt * 1.6;
      return;
    case 'hurt':
      d.timer -= dt;
      if (d.done()) d.setAnim('idle');
      if (d.timer <= 0) { d.mode = 'chase'; }
      return;
    case 'attack': {
      if (!d.hitDone && d.t > T.windup) {
        d.hitDone = true;
        const [vx, vy] = DIRV[d.dir];
        const hx = d.x + vx * 50, hy = d.y + vy * 30;
        if (dist(hx, hy, P.x, P.y) < 70) hurtPlayer(T.dmg, d.x, d.y);
      }
      if (d.done()) { d.mode = 'chase'; d.cd = T.cd; }
      return;
    }
    case 'bark':
      if (!d.hitDone && d.t > 0.2) {
        d.hitDone = true;
        const [vx, vy] = DIRV[d.dir];
        const mouth = { right: [44, -54], left: [-44, -54], up: [0, -100], down: [0, -30] }[d.dir];
        const ang = { right: 0, down: Math.PI / 2, left: Math.PI, up: -Math.PI / 2 }[d.dir];
        addFx('fx/bark', d.x + mouth[0], d.y + mouth[1], { angle: ang, fps: 12 });
        addBarkRing(d.x, d.y, d.dir, DOG_BARK, '#D7332B');
        SFX.bark(T.pitch);
        if (l < DOG_BARK.range && (dx * vx + dy * vy) / Math.max(1, l) > DOG_BARK.cos) hurtPlayer(1, d.x, d.y);
      }
      if (d.done()) { d.mode = 'chase'; d.barkCd = 3.2; }
      return;
  }

  const homeD = dist(d.x, d.y, d.hx, d.hy);
  const keen = !d.calm && !(balade() && d.friend);     // un copain ne poursuit plus Tecky (sauf s'il l'appelle)
  if (alive && l < T.aggro && homeD < 700 && keen && d.mode !== 'chase') { d.mode = 'chase'; d.wait = 0; }

  if (d.mode === 'chase') {
    if (balade() && (d.wait = (d.wait || 0) + dt) > PLAY.patience) { d.mode = 'return'; d.calm = PLAY.calm; d.wait = 0; }
    else if (!alive || l > T.aggro * 1.5 || homeD > 750) { d.mode = 'return'; }
    else if (balade() && l < T.range) {
      d.dir = dirFrom(dx, dy, d.dir);
      d.mode = 'wait'; d.timer = 0.3; d.setAnim('idle'); SFX.yip(T.pitch);
      return;
    } else if (l < T.range && d.cd <= 0) {
      d.dir = dirFrom(dx, dy, d.dir);
      d.mode = 'attack'; d.setAnim('bite'); d.hitDone = false;
      return;
    } else if (T.charge && !balade() && d.chargeCd <= 0 && l > CHARGE.min && l < CHARGE.max && clearPath(d.x, d.y, P.x, P.y)) {
      d.dir = dirFrom(dx, dy, d.dir);
      d.mode = 'crouch'; d.timer = CHARGE.crouch; d.cx = dx / l; d.cy = dy / l; d.setAnim('idle');
      addWordPop('!', d.x, d.y - 120);
      return;
    } else if (T.barks && !balade() && l > 150 && l < 300 && d.barkCd <= 0) {
      d.dir = dirFrom(dx, dy, d.dir);
      d.mode = 'bark'; d.setAnim('bark'); d.hitDone = false;
      return;
    } else if (l > T.range * 0.7) {
      steer(d, dx / l, dy / l, T.spd * dt, dt);
      d.dir = d.detT > 0 ? dirFrom(d.detX + dx / l * 0.35, d.detY + dy / l * 0.35, d.dir) : dirFrom(dx, dy, d.dir);
      d.setAnim('walk');
    } else {
      d.dir = dirFrom(dx, dy, d.dir);
      d.setAnim('idle');
    }
    return;
  }
  if (d.mode === 'return') {
    const hx = d.hx - d.x, hy = d.hy - d.y;
    if (homeD < 20) { d.mode = 'idle'; d.timer = 1; d.setAnim('idle'); return; }
    steer(d, hx / homeD, hy / homeD, T.spd * 0.7 * dt, dt);
    d.dir = d.detT > 0 ? dirFrom(d.detX, d.detY, d.dir) : dirFrom(hx, hy, d.dir);
    d.setAnim('walk');
    if (alive && l < T.aggro * 0.8 && keen) { d.mode = 'chase'; d.wait = 0; }
    return;
  }
  // balade : un copain fait la fête à Tecky quand il passe près de chez lui
  if (balade() && d.friend && alive && l < PLAY.friendR) {
    d.dir = dirFrom(dx, dy, d.dir);
    d.setAnim('idle');
    if ((d.heartT = (d.heartT || 0) - dt) <= 0) { d.heartT = 2; d.hopT = 0.4; addFx('fx/heart', d.x, d.y - 96, { fps: 10 }); }
    return;
  }
  // flânerie
  d.timer -= dt;
  if (d.mode === 'idle') {
    d.setAnim('idle');
    if (d.timer <= 0) {
      const a = Math.random() * Math.PI * 2;
      d.vx = Math.cos(a); d.vy = Math.sin(a);
      if (homeD > 150) { d.vx = (d.hx - d.x) / homeD; d.vy = (d.hy - d.y) / homeD; }
      d.mode = 'wander'; d.timer = 0.8 + Math.random() * 1.2;
    }
  } else if (d.mode === 'wander') {
    const s = T.spd * 0.35 * dt;
    const ox = d.x, oy = d.y;
    moveActor(d, d.vx * s, d.vy * s, 14);
    d.dir = dirFrom(d.vx, d.vy, d.dir);
    d.setAnim('walk');
    if (d.timer <= 0 || (ox === d.x && oy === d.y)) { d.mode = 'idle'; d.timer = 1 + Math.random() * 2; }
  }
}

function separateDogs() {
  for (let i = 0; i < dogs.length; i++)
    for (let j = i + 1; j < dogs.length; j++) {
      const a = dogs[i], b = dogs[j];
      if (a.mode === 'ko' || b.mode === 'ko') continue;
      const dx = b.x - a.x, dy = b.y - a.y, l = Math.hypot(dx, dy);
      if (l > 0 && l < 50) {
        const push = (50 - l) / 2;
        moveActor(a, -dx / l * push, -dy / l * push, 14);
        moveActor(b, dx / l * push, dy / l * push, 14);
      }
    }
}

function updateItems(dt) {
  for (const it of items) it.t += dt;
  for (let i = items.length - 1; i >= 0; i--) {
    const it = items[i];
    if (it.t < 0.5 && it.pop !== undefined) continue;
    if (dist(P.x, P.y - 10, it.x, it.y + 22) < 52 && P.mode !== 'ko') {
      const e = ITEM[it.n];
      if (e.grow) {
        // saucisse : un os de plus, déjà plein
        if (P.hpMax < MAX_BONES * 2) {
          P.hpMax += 2;
          P.boneFx = 1;
          addWordPop('Un os de plus !', P.x, P.y - 140);
          SFX.treasure();
        } else SFX.heal();
        P.hp = Math.min(P.hpMax, P.hp + 2);
        addFx('fx/heal', P.x, P.y - 60, { fps: 10 });
      } else if (e.clue !== undefined) {
        clues[e.clue] = true;
        addFx('fx/pickup', it.x, it.y, { fps: 14 });
        SFX.treasure();
        const k = nextClue();
        if (k === 3) revealAlice();
        say([{ who: 'tecky', face: 2, text: CLUE_FOUND[e.clue] }, { who: 'tecky', face: 0, text: CLUE_NEXT[k] }],
          () => { showArrow(); saveGame(); });
      } else if (e.heal) {
        if (P.hp >= P.hpMax) continue;   // vie pleine : on laisse l'os pour plus tard
        P.hp = Math.min(P.hpMax, P.hp + e.heal);
        addFx('fx/heal', P.x, P.y - 60, { fps: 10 });
        SFX.heal();
      } else {
        score += e.pts;
        addPop('+' + e.pts, it.x - 24, it.y - 60);
        addFx('fx/pickup', it.x, it.y, { fps: 14 });
        if (it.pop === undefined) SFX.pick();
      }
      items.splice(i, 1);
    }
  }
}

function updateFx(dt) {
  for (let i = rings.length - 1; i >= 0; i--) if ((rings[i].t += dt) > RING_GROW + RING_FADE) rings.splice(i, 1);
  for (let i = fxs.length - 1; i >= 0; i--) {
    const f = fxs[i];
    f.t += dt;
    if (f.t * f.fps >= ATLAS[f.key].f.length) fxs.splice(i, 1);
  }
  for (let i = pops.length - 1; i >= 0; i--) {
    pops[i].t += dt;
    if (pops[i].t > 1.1) pops.splice(i, 1);
  }
  for (const g of digs) g.t += dt;
  updateDust(dt);
}

function revealAlice() {
  alice.hidden = false;
  if (dist(P.x, P.y, alice.x, alice.y) > 40) solids.push([alice.x - 16, alice.y - 12, alice.x + 16, alice.y]);
}

function finale() {
  alice.found = true;
  recordRun();
  STORE.del(SAVE_KEY);                 // partie terminée : plus rien à continuer
  P.mode = 'free'; P.setAnim('idle');
  P.dir = dirFrom(alice.x - P.x, alice.y - P.y, P.dir);
  alice.dir = dirFrom(P.x - alice.x, P.y - alice.y, 'down');
  alice.setAnim('happy');
  Music.stop();
  Music.start('win');
  say([
    { who: 'alice', face: 2, text: "Tecky ! Tu m'as trouvée ! Tu as vu ma super cachette dans la cabane ?" },
    { who: 'tecky', face: 2, text: "Ouaf ! Ouaf ouaf !" },
    { who: 'alice', face: 0, text: "Et tu as ramassé ma barrette, ma chaussure et mon doudou ! Merci mon Tecky." },
    { who: 'alice', face: 0, text: "Viens, on rentre à la maison. Tu as bien mérité une grosse saucisse !" },
  ], () => { state = 'win'; overT = 0; });
}

function updateCamera(dt) {
  const tx = clamp(P.x - VW / 2, 0, MAP.w * TS - VW);
  const ty = clamp(P.y - 40 - VH / 2, 0, MAP.h * TS - VH);
  const k = 1 - Math.pow(0.0005, dt);
  camX = lerp(camX, tx, k); camY = lerp(camY, ty, k);
  shake = Math.max(0, shake - dt);
}

function update(dt) {
  if (pressed.mute) { muted = !muted; Music.refresh(); }
  updateClouds(dt);
  if (state !== 'title') updateSun(dt);
  switch (state) {
    case 'title': {
      titleT += dt;
      alice.t += dt; P.t += dt;
      for (const v of cars) updateVehicle(v, dt);
      for (const b of butterflies) updateButterfly(b, dt);
      updateLeaves(dt);
      const id = menuInput();
      if (id) chooseMenu(id);
      break;
    }
    case 'dialog':
      updateDialog(dt);
      alice.t += dt; P.t += dt;
      for (const d of dogs) if (d.mode !== 'ko') d.t += dt;
      for (const h of hens) h.t += dt;
      updateFx(dt);
      updateCamera(dt);
      break;
    case 'pause':
      if (pressed.pause || pressed.ok) { state = 'play'; Music.refresh(); }
      break;
    case 'play':
      if (pressed.pause) { state = 'pause'; Music.refresh(); break; }
      timePlayed += dt;
      if (pendingSay && (pendingSay.t -= dt) <= 0) { const l = pendingSay.lines; pendingSay = null; say(l); break; }
      arrowT = Math.max(0, arrowT - dt);
      if (!alice.found && (stuckT += dt) > ARROW.nudgeAfter) showArrow(ARROW.nudge);
      updatePlayer(dt);
      if ((saveT += dt) >= SAVE_EVERY && safeToSave()) { saveT = 0; saveGame(); }
      for (const d of dogs) updateDog(d, dt);
      for (const h of hens) updateHen(h, dt);
      for (const v of cars) updateVehicle(v, dt);
      for (const b of butterflies) updateButterfly(b, dt);
      separateDogs();
      dogs = dogs.filter(d => d.fade < 1);
      alice.t += dt;
      if (!alice.found && !alice.hidden) {
        alice.dir = dist(P.x, P.y, alice.x, alice.y) < 500 ? dirFrom(P.x - alice.x, P.y - alice.y, 'down') : 'down';
      }
      updateItems(dt);
      updateFx(dt);
      updateLeaves(dt);
      updateCamera(dt);
      break;
    case 'over':
    case 'win':
      overT += dt;
      alice.t += dt; P.t += dt;
      updateFx(dt);
      if (overT > 1) {
        if (state === 'over') { const id = menuInput(); if (id) chooseMenu(id); }
        else if (pressed.ok || pressed.bark || pressed.bite || pressed.act) toTitle();
      }
      break;
  }
  pressed = {};
}

/* ------------------------------------------------------------------ rendu du monde */
function drawWorld() {
  const sx = shake > 0 ? (Math.random() - 0.5) * 10 * shake / 0.25 : 0;
  const sy = shake > 0 ? (Math.random() - 0.5) * 10 * shake / 0.25 : 0;
  const cx = clamp(Math.round((camX + sx) * scale) / scale, 0, MAP.w * TS - VW);
  const cy = clamp(Math.round((camY + sy) * scale) / scale, 0, MAP.h * TS - VH);
  ctx.setTransform(scale, 0, 0, scale, offX - cx * scale, offY - cy * scale);
  drawGround(cx, cy);
  drawWater(cx, cy, performance.now() / 1000);

  const vis = (x, y, m) => x > cx - m && x < cx + VW + m && y > cy - m && y < cy + VH + m + 140;
  // trous et scintillements des trésors
  for (const g of digs) {
    if (g.dug) drawHole(g.x, g.y);
    else if (g.t % 2.4 < 0.7) drawSpr('fx/pickup', Math.floor((g.t % 2.4) * 7), g.x, g.y - 24, { sc: 0.55, alpha: 0.9 });
  }
  for (const d of decor) if (FLAT.has(d.n) && vis(d.x, d.y, 400)) drawSpr(d.key, 0, d.x, d.y);   // pont, bac à sable
  drawLeavesOnGround();
  drawDust();
  drawRings();   // ondes d'aboiement, au sol sous les personnages
  for (const b of butterflies) if (vis(b.x, b.y, 60)) {             // ombres des papillons, plus pâles en altitude
    ctx.save();
    ctx.globalAlpha = 0.2 * (1 - Math.min(0.7, b.alt / 110));
    ctx.fillStyle = '#000';
    ctx.beginPath(); ctx.ellipse(b.x, b.y, Math.max(4, 9 - b.alt * 0.05), 3, 0, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }

  const list = [];
  const now = performance.now() / 1000;            // décors animés (fontaine) : MAP.decorFps
  for (const d of decor) if (!FLAT.has(d.n) && vis(d.x, d.y, 280))
    list.push({ y: d.y, draw: () => drawSpr(d.key, Math.floor(now * (MAP.decorFps[d.n] || 0)), d.x, d.y) });
  for (const it of items) if (vis(it.x, it.y, 80)) {
    const i = Math.floor(it.t * 8);
    let dy = 0;
    if (it.pop !== undefined && it.t < 0.5) dy = -Math.sin(it.t / 0.5 * Math.PI) * 60;
    list.push({ y: it.y + 24, draw: () => drawSpr('item/' + it.n, i, it.x, it.y + dy) });
  }
  for (const d of dogs) if (vis(d.x, d.y, 120)) list.push({ y: d.y, draw: () => d.draw(Math.max(0, 1 - d.fade)) });
  for (const h of hens) if (vis(h.x, h.y, 60)) list.push({ y: h.y, draw: () => h.draw() });
  for (const v of cars) if (vis(v.x, v.y, 280)) list.push({ y: v.y, draw: () =>
    drawSpr('vehicle/' + v.name, Math.floor(v.t * 4), v.x, v.y, { flip: v.dir < 0 }) });
  if (!alice.hidden && vis(alice.x, alice.y, 120)) list.push({ y: alice.y, draw: () => alice.draw() });
  const blink = P.inv > 0 && P.mode !== 'ko' && Math.floor(P.inv * 12) % 2 === 0;
  list.push({ y: P.y, draw: () => P.draw(blink ? 0.35 : 1) });
  list.sort((a, b) => a.y - b.y);
  for (const o of list) o.draw();

  // papillons : au-dessus de tout, tournés dans le sens du vol
  for (const b of butterflies) if (vis(b.x, b.y, 80))
    drawSpr('butterfly/' + b.color, Math.floor(b.flap) % 4, b.x, b.y - b.alt, { angle: b.heading + Math.PI / 2, sc: BFLY.sc });
  drawFallingLeaves();
  for (const f of fxs) drawSpr(f.key, Math.floor(f.t * f.fps), f.x, f.y, { angle: f.angle });
  drawClouds(cx, cy);
  drawLight(cx, cy);

  // barres de vie ennemies
  for (const d of dogs) {
    if (d.mode === 'ko' || d.hp >= d.T.hp) continue;
    const top = d.kind === 'molosse' ? 118 : d.kind === 'roquet' ? 100 : 96;
    drawSpr('hud/enemy_bar_bg', 0, d.x - 30, d.y - top - 2);
    const fb = ATLAS['hud/enemy_bar_fill'].f[0];
    const w = fb[2] * d.hp / d.T.hp;
    ctx.drawImage(atlas, fb[0], fb[1], w, fb[3], d.x - 24, d.y - top + 4, w, fb[3]);
  }
  // points gagnés
  for (const p of pops) {
    const a = Math.min(1, 2.2 - p.t * 2);
    if (p.word) {
      ctx.save();
      ctx.globalAlpha = Math.max(0, a);
      ctx.font = '700 26px Fredoka, "Trebuchet MS", sans-serif';
      ctx.textAlign = 'center'; ctx.lineJoin = 'round'; ctx.lineWidth = 6; ctx.strokeStyle = '#3A1E12';
      const y = p.y - p.t * 40;
      ctx.strokeText(p.text, p.x, y); ctx.fillStyle = '#F2C14E'; ctx.fillText(p.text, p.x, y);
      ctx.restore();
    } else drawDigits(p.text, p.x, p.y - p.t * 60, 0.75, a);
  }
  // bulles "gratter" / "lire" : ce que fait C à cet endroit (touche C devant le mot au clavier)
  const bob = Math.sin(performance.now() / 200) * 4;
  if (digHint && state === 'play' && P.mode !== 'dig') {
    // juste au-dessus des traces de pattes, dessinées sur la tuile du sol qui contient le trésor
    const mx = Math.floor(digHint.x / TS) * TS + TS / 2, my = Math.floor(digHint.y / TS) * TS;
    actionBubble('Gratter', mx, my - 36 + bob);
  }
  if (hintText && state === 'play') actionBubble('Lire', hintText.x, hintText.y + bob);
  if (playHint && state === 'play' && P.mode !== 'play') actionBubble('Jouer', playHint.x, playHint.y - 125 + bob);
}
function actionBubble(label, bx, by) {
  ctx.font = '600 22px Fredoka, "Trebuchet MS", sans-serif';
  ctx.textAlign = 'center'; ctx.lineWidth = 5; ctx.strokeStyle = '#3A1E12'; ctx.lineJoin = 'round';
  // même écart touche-mot que pour « Gratter », l'ensemble restant centré
  const shift = (ctx.measureText('Gratter').width - ctx.measureText(label).width) / 2;
  if (!touchMode) drawSpr(pad.on ? 'hud/pad' : 'hud/key', pad.on ? 0 : 1, bx - 40 - 34 + shift, by - 4, { sc: 0.9 });
  const tx = touchMode ? bx : bx + 26;
  ctx.strokeText(label, tx, by + 26); ctx.fillStyle = '#FFF7E6'; ctx.fillText(label, tx, by + 26);
}

/* ------------------------------------------------------------------ interface */
function guiTransform() {
  const gs = scale * VW / GW;
  ctx.setTransform(gs, 0, 0, gs, offX, offY);
}
function text(str, x, y, size, color, align, weight) {
  ctx.font = `${weight || 600} ${size}px Fredoka, "Trebuchet MS", sans-serif`;
  ctx.textAlign = align || 'left';
  ctx.textBaseline = 'alphabetic';
  ctx.fillStyle = color;
  ctx.fillText(str, x, y);
}
function outlined(str, x, y, size, fill, align) {
  ctx.font = `700 ${size}px Fredoka, "Trebuchet MS", sans-serif`;
  ctx.textAlign = align || 'center';
  ctx.lineJoin = 'round';
  ctx.lineWidth = size * 0.16;
  ctx.strokeStyle = '#3A1E12';
  ctx.strokeText(str, x, y);
  ctx.fillStyle = fill;
  ctx.fillText(str, x, y);
}
function wrap(str, maxW) {
  const words = str.split(' '), lines = [];
  let cur = '';
  for (const w of words) {
    const t = cur ? cur + ' ' + w : w;
    if (ctx.measureText(t).width > maxW && cur) { lines.push(cur); cur = w; } else cur = t;
  }
  if (cur) lines.push(cur);
  return lines;
}

/* paragraphe : passe à la ligne dans maxW ; retourne le y de la ligne suivante */
function para(str, x, y, size, color, align, weight, maxW, lineH) {
  ctx.font = `${weight || 600} ${size}px Fredoka, "Trebuchet MS", sans-serif`;
  const lines = wrap(str, maxW);
  lines.forEach((ln, i) => text(ln, x, y + i * lineH, size, color, align, weight));
  return y + lines.length * lineH;
}

function drawHUD() {
  guiTransform();
  // vie : le panneau s'allonge avec le nombre d'os
  const bones = P.hpMax / 2;
  drawNine('hud/panel_dark', 24, 24, 150 + bones * 64 + 24, 132, 32);
  const face = P.mode === 'ko' ? 3 : P.mode === 'bark' ? 2 : (P.mode === 'hurt' ? 1 : 0);
  drawSpr('hud/portrait_tecky', face, 36, 42);
  for (let i = 0; i < bones; i++) {
    const f = P.hp >= (i + 1) * 2 ? 0 : P.hp === i * 2 + 1 ? 1 : 2;
    const pulse = i === bones - 1 && P.boneFx > 0 ? 1 + Math.sin(P.boneFx * Math.PI) * 0.5 : 1;
    ctx.save();
    ctx.translate(150 + i * 64 + 32, 58 + 32); ctx.scale(pulse, pulse);
    drawSpr('hud/bone', f, -32, -32);
    ctx.restore();
  }
  // score
  drawNine('hud/panel_dark', GW - 24 - 330, 24, 330, 104, 32);
  drawSpr('item/medal', 0, GW - 24 - 330 + 50, 76);
  const dz = ATLAS['hud/digits'].f[0];                 // chiffre « 0 » : [x, y, w, h, décalage x, décalage y]
  drawDigits(String(score).padStart(5, '0'), GW - 24 - 330 + 96, 24 + 104 / 2 - dz[5] - dz[3] / 2, 1, undefined, true);
  // trésors trouvés
  drawNine('hud/panel_dark', GW - 24 - 210, 138, 210, 70, 32);
  ctx.save();
  ctx.translate(GW - 24 - 210 + 40, 173);
  ctx.scale(0.7, 0.7);
  ctx.drawImage(tilesImg, (MAP.hole % 16) * TS, Math.floor(MAP.hole / 16) * TS, TS, TS, -32, -38, 64, 64);
  ctx.restore();
  drawDigits(treasures + '/' + MAP.dig.length, GW - 24 - 210 + 82, 146, 0.8);

  // indices d'Alice : trois cases sous la vie, l'objet apparaît quand il est retrouvé
  drawNine('hud/panel_dark', 24, 166, 24 + CLUES.length * 76, 88, 32);
  CLUES.forEach((n, i) => drawSpr('item/' + n, 0, 24 + 12 + 38 + i * 76, 166 + 44 + 4, { alpha: clues[i] ? 1 : 0.22 }));

  // flèche (quelques secondes) vers le prochain indice, puis vers Alice ; seule la pointe tourne, l'icône reste droite
  if (!alice.found && state === 'play' && arrowT > 0) {
    const tg = arrowTarget();
    const ax = (tg.x - camX) * GW / VW, ay = (tg.y - 50 - camY) * GH / VH;
    if (ax < 0 || ax > GW || ay < 0 || ay > GH) {
      const ang = Math.atan2(ay - GH / 2, ax - GW / 2), a = Math.min(1, arrowT);
      const px = clamp(ax, 80, GW - 80), py = clamp(ay, 300, GH - 80);
      drawSpr('hud/arrow', Math.floor(performance.now() / 150), px, py, { angle: ang, alpha: a });
      // centre de la pastille : 6 px derrière le centre de rotation ; icône 0..2 = indices, 3 = Alice
      drawSpr('hud/arrow_icon', tg === alice ? 3 : nextClue(), px - Math.cos(ang) * 6, py - Math.sin(ang) * 6, { alpha: a });
    }
  }

  // boutons d'action
  if (touchMode) {
    const biteFr = ACTION_FRAME[biteAction()];
    for (const [k, fr] of [['bark', 0], ['bite', biteFr]]) {
      const b = BTN[k];
      const cd = k === 'bark' ? P.cdBark / (P.cdBarkMax || 1) : P.cdBite / (P.cdBiteMax || 1);
      ctx.save();
      ctx.translate(b.x, b.y); ctx.scale(2.2, 2.2);
      drawSpr('hud/action', fr, -40, -40, { alpha: 0.92 });
      if (cd > 0) drawSpr('hud/cooldown', Math.floor((1 - cd) * 8), -40, -40);
      ctx.restore();
    }
    // joystick
    if (stick.id !== null) {
      ctx.save();
      ctx.globalAlpha = 0.35; ctx.fillStyle = '#FFF7E6';
      ctx.beginPath(); ctx.arc(stick.ox, stick.oy, 120, 0, Math.PI * 2); ctx.fill();
      ctx.globalAlpha = 0.8; ctx.fillStyle = '#D7332B';
      ctx.beginPath(); ctx.arc(stick.x, stick.y, 52, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
    } else if (state === 'play') {
      ctx.save(); ctx.globalAlpha = 0.18; ctx.fillStyle = '#FFF7E6';
      ctx.beginPath(); ctx.arc(250, 830, 120, 0, Math.PI * 2); ctx.fill(); ctx.restore();
    }
    // pause
    drawNine('hud/panel_dark', GW - 150, 224, 126, 70, 32);
    text('II', GW - 87, 272, 40, '#FFF7E6', 'center', 700);
    if (canFullscreen() && !fsElement()) drawFsButton();
  } else {
    [['bark', 0, 0], ['bite', ACTION_FRAME[biteAction()], 1]].forEach(([k, fr, key], i) => {
      const x = GW - 230 + i * 110, y = GH - 190;
      drawSpr('hud/action', fr, x, y);
      const cd = k === 'bark' ? P.cdBark / (P.cdBarkMax || 1) : P.cdBite / (P.cdBiteMax || 1);
      if (cd > 0) drawSpr('hud/cooldown', Math.floor((1 - cd) * 8), x, y);
      if (pad.on) drawSpr('hud/pad', key ? 0 : 2, x, y + 86);      // A mord, X aboie
      else drawSpr('hud/key', key, x, y + 86);
    });
  }
  if (muted) text(pad.on ? 'son coupé (Select)' : 'son coupé (M)', 40, GH - 30, 28, '#FFF7E6', 'left', 500);
}

function drawFsButton() {
  const b = FS_BTN;
  drawNine('hud/panel_dark', b.x, b.y, b.w, b.h, 32);
  ctx.save();
  ctx.strokeStyle = '#FFF7E6'; ctx.lineWidth = 6; ctx.lineCap = 'round';
  const cx = b.x + b.w / 2, cy = b.y + b.h / 2, w = 26, h = 18, k = 10;
  for (const [sx, sy] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
    ctx.beginPath();
    ctx.moveTo(cx + sx * w, cy + sy * (h - k)); ctx.lineTo(cx + sx * w, cy + sy * h); ctx.lineTo(cx + sx * (w - k), cy + sy * h);
    ctx.stroke();
  }
  ctx.restore();
}

function drawDialog() {
  guiTransform();
  const L = dialog.lines[dialog.i], who = WHO[L.who];
  const bx = 250, by = GH - 262, bw = GW - 500, bh = 226;
  drawNine('hud/panel', bx, by, bw, bh, 32);
  let tx = bx + 60;
  if (who.portrait) {
    drawSpr(who.portrait, L.face || 0, bx + 36, by + 64);
    tx = bx + 170;
    drawSpr('hud/name_tag', 0, bx + 150, by - 18);
    text(who.name, bx + 150 + 64, by + 12, 26, '#FFFFFF', 'center', 600);
  }
  ctx.font = '500 38px Fredoka, "Trebuchet MS", sans-serif';
  const lines = wrap(L.text.slice(0, Math.floor(dialog.c)), bx + bw - 70 - tx);
  lines.slice(0, 3).forEach((ln, i) => text(ln, tx, by + 84 + i * 50, 38, '#3A1E12', 'left', 500));
  if (dialog.c >= L.text.length) drawSpr('hud/next', Math.floor(performance.now() / 120), bx + bw - 70, by + bh - 62);
}

function veil(a) {
  guiTransform();
  ctx.fillStyle = `rgba(27, 18, 12, ${a})`;
  ctx.fillRect(0, 0, GW, GH);
}

function drawTitle() {
  veil(0.35);
  const bob = Math.sin(titleT * 2) * 8;
  drawSpr('hud/title_logo', 0, GW / 2, 250 + bob, { sc: 1.75 });
  outlined('Aide Tecky le teckel à retrouver Alice', GW / 2, 472, 38, '#FFF7E6');
  drawMenu(titleT);
  const r = recordLine(menu.items[menu.sel].mode);
  const last = menuBox(menu.items.length - 1);
  if (r) outlined(r, GW / 2, last.y + last.h + 58, 30, '#F2C14E');
  if (!touchMode) text(pad.on ? 'Croix pour choisir, A pour valider' : '↑ ↓ pour choisir, Entrée pour valider',
    GW / 2, GH - 28, 26, '#E9DCC8', 'center', 500);
}
/* entrées du menu : l'entrée choisie est claire, encadrée de deux os qui la montrent */
function drawMenu(t) {
  menu.items.forEach((it, i) => {
    const b = menuBox(i), sel = i === menu.sel;
    drawNine(sel ? 'hud/panel' : 'hud/panel_dark', b.x, b.y, b.w, b.h, 32);
    const ink = sel ? '#3A1E12' : '#FFF7E6';
    text(it.label, GW / 2, b.y + b.h * 0.48, 40, ink, 'center', 700);
    if (it.sub) text(it.sub, GW / 2, b.y + b.h * 0.48 + 34, 26, sel ? '#6B5A4E' : '#E9DCC8', 'center', 500);
    if (sel) {
      const k = Math.sin(t * 6) * 6;
      drawSpr('hud/bone', 0, b.x - 76 - k, b.y + b.h / 2 - 32);
      drawSpr('hud/bone', 0, b.x + b.w + 12 + k, b.y + b.h / 2 - 32);
    }
  });
}

function drawEnd(win) {
  veil(Math.min(win ? 0.65 : 0.72, overT));
  if (overT < 0.4) return;
  if (!win) {
    // KO : le menu (reprendre, recommencer, menu principal) sur le voile
    outlined('Tecky est épuisé…', GW / 2, 190, 72, '#E24B4B');
    drawSpr('hud/portrait_tecky', 3, GW / 2 - 48, 230);
    const ny = para('Il reste des os et des saucisses sur le chemin pour reprendre des forces.', GW / 2, 440, 32, '#FFF7E6', 'center', 500, 900, 42);
    text('Score : ' + score, GW / 2, ny + 22, 36, '#F2C14E', 'center', 600);
    if (overT > 1 && menu) drawMenu(overT);
    return;
  }
  const pw = 900, ph = 600, px = (GW - pw) / 2, py = (GH - ph) / 2;
  drawNine('hud/panel', px, py, pw, ph, 32);
  outlined('Tecky a retrouvé Alice !', GW / 2, py + 100, 64, '#F2C14E');
  drawSpr('hud/portrait_tecky', 2, GW / 2 - 130, py + 140);
  drawSpr('hud/portrait_alice', 2, GW / 2 + 34, py + 140);
  const rows = [['Score', String(score)], ['Temps', fmtTime(timePlayed)],
    ['Trésors déterrés', treasures + ' / ' + MAP.dig.length], [balade() ? 'Copains de jeu' : 'Chiens mis en fuite', String(fled)]];
  rows.forEach(([k, v], i) => {
    text(k, px + 180, py + 320 + i * 46, 34, '#6B5A4E', 'left', 500);
    text(v, px + pw - 180, py + 320 + i * 46, 34, '#3A1E12', 'right', 600);
    // meilleur score, meilleur temps : une étiquette dorée à côté de la valeur
    if ((i === 0 && newRecord.score) || (i === 1 && newRecord.time)) {
      ctx.save(); ctx.translate(px + pw - 98, py + 308 + i * 46); ctx.rotate(-0.08);
      outlined('Record !', 0, 0, 26, '#F2C14E'); ctx.restore();
    }
  });
  const r = recordLine(gameMode);
  if (r) text(r, GW / 2, py + ph - 96, 26, '#6B5A4E', 'center', 500);
  if (overT > 1 && Math.floor(overT * 1.6) % 2 === 0)
    text(touchMode ? 'Touche l’écran pour revenir au menu' : pad.on ? 'A pour revenir au menu' : 'Entrée pour revenir au menu',
      GW / 2, py + ph - 40, 34, '#D7332B', 'center', 600);
}

function render() {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = '#16100C';
  ctx.fillRect(0, 0, cv.width, cv.height);
  if (state === 'loading') {
    guiTransform();
    text('Chargement…', GW / 2, GH / 2, 48, '#FFF7E6', 'center', 600);
    return;
  }
  ctx.save();
  ctx.beginPath(); ctx.rect(offX, offY, VW * scale, VH * scale); ctx.clip();
  drawWorld();
  if (state === 'title') drawTitle();
  else {
    drawHUD();
    if (state === 'dialog' && dialog) drawDialog();
    if (state === 'pause') {
      veil(0.5);
      outlined('Pause', GW / 2, GH / 2, 96, '#FFF7E6');
      para(touchMode ? 'Touche l’écran pour reprendre' : pad.on ? 'Start ou A pour reprendre' : 'P ou Entrée pour reprendre, F pour le plein écran',
        GW / 2, GH / 2 + 80, 36, '#FFF7E6', 'center', 500, GW - 240, 46);
      text('Mode ' + gameMode + ' · partie enregistrée automatiquement', GW / 2, GH / 2 + 160, 28, '#E9DCC8', 'center', 500);
      if (touchMode && canFullscreen() && !fsElement()) drawFsButton();
    }
    if (state === 'over') drawEnd(false);
    if (state === 'win') drawEnd(true);
  }
  ctx.restore();
}

/* ------------------------------------------------------------------ boucle */
let last = 0;
function frame(ts) {
  const dt = Math.min(0.05, (ts - last) / 1000 || 0);
  last = ts;
  if (state !== 'loading') { pollPad(); update(dt); }
  render();
  requestAnimationFrame(frame);
}

function whenLoaded(img) {
  return img.complete && img.naturalWidth ? Promise.resolve() : new Promise((res, rej) => { img.onload = res; img.onerror = rej; });
}
function start() {
  const fontReady = document.fonts && document.fonts.load
    ? Promise.race([document.fonts.load('600 40px Fredoka'), new Promise(r => setTimeout(r, 2500))]).catch(() => {})
    : Promise.resolve();
  Promise.all([whenLoaded(atlas), whenLoaded(tilesImg), fontReady]).then(() => {
    buildGround();
    buildClouds();
    toTitle();
  });
  requestAnimationFrame(frame);
}
start();
