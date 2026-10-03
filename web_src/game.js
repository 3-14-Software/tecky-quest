'use strict';
/* =====================================================================
   TECKY QUEST — moteur Canvas 2D
   Monde : pixels "x2" (tuile = 64 px). Caméra : 960 x 540 px de monde.
   Interface (GUI) : 1920 x 1080, sprites HUD x2.
   ===================================================================== */

const VW = 960, VH = 540;               // caméra, en px de monde
const GW = 1920, GH = 1080;             // repère de l'interface
const TS = MAP.ts;

/* Réglages du joueur (écran d'options, plus bas) : lus ici, avant le premier resize(). */
const OPTIONS_KEY = 'tecky-quest-options';
const OPT_DEF = { music: 7, sfx: 8, diff: 'normal', text: 'normal', image: 'fluide', vib: 'oui', weather: 'auto' };
const opts = (() => {
  let o = null;
  try { o = JSON.parse(localStorage.getItem(OPTIONS_KEY)); } catch (e) { /* stockage refusé */ }
  return Object.assign({}, OPT_DEF, o || {});
})();

const cv = document.getElementById('game');
const ctx = cv.getContext('2d');
let dpr = 1, scale = 1, offX = 0, offY = 0;

/* Au plus MAX_PIXELS pixels dans le canvas : au-delà (plein écran sur un écran 1440p ou 4K), le navigateur l'agrandit
   lui-même à l'affichage, gratuitement. Le monde est dessiné en px x2 (960 x 540 de caméra) : un canvas plus grand
   n'ajoute presque rien à l'image, mais multiplie le travail (Firefox dessine souvent le canvas avec le processeur :
   60 ms par image en 4K, contre 15 ms en 1920 x 1080). Option « Image : nette » : pas de plafond.
   dpr = rapport réel canvas / CSS (sert aussi aux pointeurs). */
const MAX_PIXELS = 1920 * 1080;
function resize() {
  dpr = Math.min(window.devicePixelRatio || 1, 2);
  const px = innerWidth * innerHeight * dpr * dpr;
  if (opts.image !== 'nette' && px > MAX_PIXELS) dpr *= Math.sqrt(MAX_PIXELS / px);
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
const sfxGain = () => SFX_VOL * opts.sfx / OPT_DEF.sfx;     // réglage « Bruitages » (8 = normal)
function audioOn() {
  if (!AC) {
    try { AC = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { AC = null; }
  }
  if (AC && AC.state === 'suspended') AC.resume();
  if (AC && !Music.on && !(alice && alice.found) && ['title', 'play', 'dialog', 'pause', 'options'].includes(state)) Music.start();
}
function tone(freq, dur, type, vol, slide, delay) {
  if (!AC || muted) return;
  const t0 = AC.currentTime + (delay || 0);
  const o = AC.createOscillator(), g = AC.createGain();
  o.type = type || 'square';
  o.frequency.setValueAtTime(freq, t0);
  if (slide) o.frequency.exponentialRampToValueAtTime(Math.max(40, freq + slide), t0 + dur);
  g.gain.setValueAtTime((vol || 0.08) * sfxGain(), t0);
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
  g.gain.value = (vol || 0.1) * sfxGain();
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
  sniff() { for (let i = 0; i < 3; i++) noise(0.06, 0.07, 1900 + i * 150, i * 0.13); },
  yip(p) { const k = p || 1; tone(820 * k, 0.07, 'square', 0.045, 420 * k); tone(980 * k, 0.09, 'square', 0.045, 380 * k, 0.11); },
  quack(p) { const k = p || 1; tone(640 * k, 0.08, 'square', 0.035, -260 * k); tone(560 * k, 0.1, 'square', 0.035, -280 * k, 0.11); },
  flap() { for (let i = 0; i < 4; i++) noise(0.05, 0.05, 700 + i * 60, i * 0.08); },
  yawn() { tone(420, 0.55, 'triangle', 0.035, -200); tone(630, 0.4, 'sine', 0.015, -260, 0.05); },
  snore() { noise(0.5, 0.025, 260); },
  badge() { [784, 988, 1175, 1568].forEach((f, i) => tone(f, 0.14, 'triangle', 0.07, 0, i * 0.09)); },
  plop() { tone(380 + Math.random() * 120, 0.08, 'sine', 0.05, -200); noise(0.06, 0.04, 1600); },
  shake() { for (let i = 0; i < 11; i++) noise(0.05, 0.05, 1200 + (i % 5) * 200, i * 0.065); },
  hey(p) { const k = p || 1; tone(560 * k, 0.08, 'triangle', 0.08, 160 * k); tone(760 * k, 0.13, 'triangle', 0.08, -120 * k, 0.09); },
  cluck() { tone(950, 0.05, 'square', 0.05, 250); tone(1150, 0.05, 'square', 0.05, 200, 0.08); tone(1400, 0.12, 'square', 0.05, -600, 0.17); },
  win() { [523, 659, 784, 1046, 784, 1046].forEach((f, i) => tone(f, 0.18, 'triangle', 0.09, 0, i * 0.14)); },
  boing() { tone(260 + Math.random() * 60, 0.13, 'sine', 0.07, 280); tone(520, 0.08, 'sine', 0.03, -200, 0.06); },
  goal() { [523, 659, 784, 1046].forEach((f, i) => tone(f, 0.11, 'square', 0.04, 0, i * 0.07)); noise(0.3, 0.03, 3200, 0.12); },
  whistle() { tone(880, 0.22, 'triangle', 0.07, -30); tone(988, 0.22, 'triangle', 0.05, -30); noise(0.3, 0.03, 2600);
    tone(880, 0.32, 'triangle', 0.07, -60, 0.3); tone(988, 0.32, 'triangle', 0.05, -60, 0.3); noise(0.4, 0.03, 2600, 0.3); },
  bell() { tone(1320, 0.12, 'sine', 0.06); tone(1320, 0.14, 'sine', 0.06, 0, 0.18); },
  moo(p) { const k = p || 1; tone(130 * k, 0.75, 'sawtooth', 0.04, 45 * k); tone(260 * k, 0.6, 'triangle', 0.035, -70 * k, 0.2);
    tone(1700, 0.08, 'sine', 0.02, 0, 0.05); },     // « mmmeuh », et un tintement de clochette
};

/* ------------------------------------------------------------------ musique chiptune */
/* « Promenade de Tecky » : événements générés par music.py (SONGS : une variation du thème par zone, même mélodie,
   mêmes accords, même grille de phrases ; « base » = le WAV GameMaker, pour la niche et la campagne).
   Chaque zone joue sa variation avec ses instruments (TIMBRE) dans une couche (layers : gain propre). setZone()
   demande un changement ; il se fait en fondu enchaîné pendant la dernière mesure d'une phrase (MUSIC_ZONE), le tempo
   glissant d'une variation à l'autre (glide) : la phrase suivante commence avec la nouvelle variation, à son tempo. */
const MUSIC_ZONE = {
  settle: 2,        // s : Tecky doit rester ce temps dans une zone pour que la musique change (pas de passage éclair)
  phrase: 4,        // mesures par phrase
  fade: 1,          // mesures de fondu, juste avant le début d'une phrase
  cut: 0.6,         // s : fondu rapide quand la scène change d'un coup (nouvelle partie, Continuer)
};
const Music = {
  on: false, gain: null, timer: null, step: 0, next: 0, waves: {}, noiseBuf: null, byStep: null,
  zone: 'niche', want: null, layers: [], fadeStep: -1, bpm: 140, glide: null, fadeDur: 0,
  VOL: { lead: 0.16, arp: 0.045, bass: 0.2, kick: 0.5, snare: 0.2, hat: 0.07 },
  init() {
    const mk = S => { const b = Array.from({ length: S.total }, () => []); for (const e of S.ev) b[e[0]].push(e); return { byStep: b, total: S.total, bpm: S.bpm, bar: S.bar }; };
    this.themes = {};
    for (const k in SONGS) this.themes[k] = mk(SONGS[k]);
    this.songs = { main: this.themes.base, win: mk(WINSONG), lose: mk(LOSESONG), end: this.themes.berceuse };
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
  level() {                            // réglage « Musique » : 7 = normal
    const quiet = state === 'pause' || (state === 'options' && optReturn === 'pause');
    return muted ? 0 : (quiet ? 0.12 : this.cur === 'main' || this.cur === 'end' ? 0.35 : 0.55) * opts.music / OPT_DEF.music;
  },
  /* name : 'main' (boucle), 'win' (fanfare de victoire) ou 'lose' (musique de défaite), ces deux-là jouées une seule fois,
     'end' (berceuse de la fin, en boucle) */
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
    this.layers = this.cur === 'main' ? [this.layer(this.zone, 1)] : [];
    this.want = null; this.glide = null;
    this.bpm = (this.layers[0] ? this.layers[0].song : this.song).bpm;
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
  /* Changement de timbre : demandé (want), il attend la dernière mesure d'une phrase ; now = tout de suite, en fondu
     rapide. Redemander la zone en cours annule une demande en attente. */
  setZone(id, now) {
    if (!this.on || this.cur !== 'main') { this.zone = id; this.want = null; return; }
    if (now) { if (id !== this.zone || this.layers.length > 1) this.fadeTo(id, AC.currentTime, MUSIC_ZONE.cut); this.want = null; return; }
    this.want = id === this.zone ? null : id;
  },
  layer(id, v) {                       // la variation et les instruments de la zone id
    const g = AC.createGain();
    g.gain.value = v;
    g.connect(this.gain);
    return { id, g, song: this.themes[id] || this.themes.base, t0: 0, t1: 0, v0: v, v1: v };
  },
  ramp(l, to, t, d) {                  // fondu linéaire de la couche l vers to, de t à t + d, depuis sa valeur à t
    const k = l.t1 > l.t0 ? Math.min(1, Math.max(0, (t - l.t0) / (l.t1 - l.t0))) : 1, v = l.v0 + (l.v1 - l.v0) * k;
    const p = l.g.gain;
    p.cancelScheduledValues(t); p.setValueAtTime(v, t); p.linearRampToValueAtTime(to, t + d);
    Object.assign(l, { t0: t, t1: t + d, v0: v, v1: to });
  },
  /* Fondu vers la zone id à partir du temps t : en d secondes (fondu rapide, nouveau tempo tout de suite) ou, sans d,
     pendant MUSIC_ZONE.fade mesures où le tempo glisse de l'ancien au nouveau (d = durée de ces pas). */
  fadeTo(id, t, d) {
    let n = this.layers.find(l => l.id === id);
    if (!n) { n = this.layer(id, 0); this.layers.push(n); }
    const to = n.song.bpm;
    if (d === undefined) {
      const steps = MUSIC_ZONE.fade * this.song.bar;
      this.glide = { from: this.bpm, to, n: steps, i: 0 };
      d = 0;
      for (let i = 0; i < steps; i++) d += this.stepLen(i);
    } else { this.glide = null; this.bpm = to; }
    for (const l of this.layers) this.ramp(l, l === n ? 1 : 0, t, d);
    this.zone = id; this.want = null; this.fadeStep = this.step; this.fadeDur = d;
  },
  stepLen(i) {                         // durée d'un pas (double-croche), selon le tempo qui glisse pendant un fondu
    const gl = this.glide;
    if (!gl) return 15 / this.bpm;
    return 15 / (gl.from + (gl.to - gl.from) * ((i === undefined ? gl.i : i) + 0.5) / gl.n);
  },
  tick() {
    if (this.next < AC.currentTime - 0.2) this.next = AC.currentTime + 0.05;   // retour d'onglet
    while (this.next < AC.currentTime + 0.15) {
      const bar = this.song.bar;
      if (this.want && (this.step + MUSIC_ZONE.fade * bar) % (MUSIC_ZONE.phrase * bar) === 0) this.fadeTo(this.want, this.next);
      for (const l of this.layers.filter(l => l.v1 === 0 && l.t1 < this.next)) {   // couches éteintes : plus de notes
        this.layers.splice(this.layers.indexOf(l), 1);
        setTimeout(() => l.g.disconnect(), 1000);
      }
      const spb = this.stepLen();
      if (this.cur === 'main') for (const l of this.layers) for (const e of l.song.byStep[this.step]) this.play(e, this.next, spb, l);
      else for (const e of this.song.byStep[this.step]) this.play(e, this.next, spb, null);
      this.next += spb;
      this.step++;
      if (this.glide && ++this.glide.i >= this.glide.n) { this.bpm = this.glide.to; this.glide = null; }
      if (this.step >= this.song.total) {
        if (this.cur === 'main' || this.cur === 'end') this.step = 0;
        else { clearInterval(this.timer); const g0 = this.gain; setTimeout(() => { if (this.gain === g0) this.stop(); }, 2500); return; }   // fanfare, défaite : une seule fois
      }
    }
  },
  play(e, t, spb, l) {                 // l : couche de la zone (thème), null pour la fanfare et la défaite
    const out = l ? l.g : this.gain;
    if (e[1] === 'drums') this.drum(e, t, out);
    else this.voice(e, t, spb, (l && TIMBRE[l.id]) || TIMBRE[this.cur] || TIMBRE.niche, out);
  },
  drum(e, t, out) {
    const [, , note, , vol] = e;
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
  },
  voice(e, t, spb, tb, out) {          // tb : instruments de la zone (TIMBRE) ; la basse garde son triangle
    const [, ch, note, len, vol] = e;
    const o = AC.createOscillator(), g = AC.createGain();
    if (ch === 'bass') o.type = 'triangle';
    else { const w = ch === 'lead' ? tb.lead : tb.arp; if (typeof w === 'number') o.setPeriodicWave(this.wave(w)); else o.type = w; }
    const f = 440 * Math.pow(2, (note - 69) / 12);
    if (e[5]) {                        // note glissée (ferme) : part de e[5] demi-tons et rejoint la sienne
      o.frequency.setValueAtTime(f * Math.pow(2, e[5] / 12), t);
      o.frequency.exponentialRampToValueAtTime(f, t + 0.07);
    } else o.frequency.value = f;
    const dur = len * spb, v = this.VOL[ch] * vol * (ch === 'bass' ? 1 : tb.lv);
    const sus = (ch === 'arp' ? 0.4 : ch === 'bass' ? 0.8 : 0.65) * (ch === 'bass' ? 1 : tb.sus);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(v, t + 0.004);
    g.gain.linearRampToValueAtTime(v * sus, t + 0.05);
    g.gain.setValueAtTime(v * sus, t + Math.max(0.05, dur - 0.03));
    g.gain.linearRampToValueAtTime(0.0001, t + dur);
    o.connect(g); g.connect(out);
    o.start(t); o.stop(t + dur + 0.02);
  },
};
/* Timbre de la mélodie (lead) et des arpèges (arp) selon la zone : rapport cyclique d'une onde carrée, ou forme d'onde
   ('triangle', 'sine') ; sus : tenue des notes ; lv : volume (les ondes douces sonnent moins fort). La partition est
   la variation du thème de la zone (SONGS, music.py). */
const TIMBRE = {
  niche: { lead: 0.25, arp: 0.125, sus: 1, lv: 1 },
  village: { lead: 0.25, arp: 0.125, sus: 1, lv: 1 },
  campagne: { lead: 0.25, arp: 0.125, sus: 1, lv: 1 },
  ferme: { lead: 0.5, arp: 0.25, sus: 0.45, lv: 0.85 },          // notes sèches et rondes, façon banjo
  industrie: { lead: 0.125, arp: 0.0625, sus: 0.8, lv: 0.95 },    // son fin, un peu métallique
  foret: { lead: 'triangle', arp: 'triangle', sus: 1.15, lv: 1.7 },   // flûte
  parc: { lead: 'sine', arp: 0.25, sus: 0.7, lv: 1.8 },              // boîte à musique
  end: { lead: 'sine', arp: 'triangle', sus: 1, lv: 1.8 },            // berceuse de la fin (Music.start('end'))
};

/* ------------------------------------------------------------------ ambiance sonore des zones */
/* Petits sons selon la zone où se trouve Tecky (voir ZONES) : oiseaux (surtout en forêt et au parc), caquètements et coq
   à la ferme, sonnette de vélo au village, cliquetis à la zone industrielle ; et un clapotis continu dont le volume suit
   la quantité d'eau autour de Tecky (rivière, étang, mare). Seulement en jeu (coupé en pause et pendant les dialogues). */
const AMB = { vol: 0.55, water: 0.09, waterR: [140, 300], rain: 0.07 };
const AMB_EVENTS = {   // zone : [son, intervalle min (s), max]
  foret: [['bird', 1.4, 3.8]], parc: [['bird', 3, 7]], campagne: [['bird', 4, 9]], niche: [['bird', 4, 9]],
  village: [['bell', 18, 32], ['bird', 7, 13]], industrie: [['clank', 5, 11]],
  ferme: [['cluck', 3.5, 8], ['rooster', 28, 50], ['bird', 8, 14]], verger: [['bird', 3, 7], ['cluck', 9, 18]],
};
function ambSound(name) {
  const v = AMB.vol;
  if (name === 'bird') {               // gazouillis : quelques notes aiguës qui glissent
    const base = 2600 + Math.random() * 1600, n = 2 + Math.floor(Math.random() * 4), up = Math.random() < 0.5;
    let t = 0;
    for (let i = 0; i < n; i++) {
      tone(base * (1 + (up ? i : -i) * 0.06), 0.06 + Math.random() * 0.04, 'sine', 0.022 * v,
        (Math.random() < 0.5 ? 1 : -1) * (400 + Math.random() * 900), t);
      t += 0.09 + Math.random() * 0.05;
    }
  } else if (name === 'bell') {        // sonnette de vélo
    tone(2350, 0.35, 'sine', 0.02 * v); tone(2350, 0.4, 'sine', 0.02 * v, 0, 0.16); tone(4700, 0.2, 'sine', 0.006 * v);
  } else if (name === 'clank') {
    noise(0.05, 0.05 * v, 3200); tone(1500 + Math.random() * 600, 0.3, 'triangle', 0.012 * v, -300);
  } else if (name === 'cluck') {       // poules qui caquètent doucement, s'il y en a près de Tecky
    if (!hens.some(h => dist(h.x, h.y, P.x, P.y) < 600)) return;
    tone(800, 0.05, 'square', 0.012 * v, 200); tone(950, 0.06, 'square', 0.012 * v, 150, 0.09);
  } else if (name === 'rooster') {     // cocorico
    let t = 0;
    for (const [f, d, sl] of [[620, 0.11, 260], [700, 0.11, 300], [800, 0.13, 380], [1150, 0.42, -420]]) {
      tone(f, d, 'square', 0.014 * v, sl, t); t += d + 0.02;
    }
  }
}
const Ambience = {
  timers: {}, gain: null, phase: 0, played: 0,
  update(dt) {
    if (!AC) return;
    const z = zone ? zone.id : 'niche';
    for (const [name, a, b] of AMB_EVENTS[z] || []) {
      const k = z + '/' + name;
      if (this.timers[k] === undefined) this.timers[k] = a + Math.random() * (b - a);
      if ((this.timers[k] -= dt) <= 0) {
        this.timers[k] = a + Math.random() * (b - a);
        if (!muted && !(name === 'bird' && weather.k > 0.3)) { ambSound(name); this.played++; }     // sous la pluie, les oiseaux se taisent
      }
    }
    // clapotis : part d'eau sur deux cercles autour de Tecky, avec une lente respiration
    let n = 0, w = 0;
    for (const r of AMB.waterR) for (let i = 0; i < 8; i++) {
      const a = i * Math.PI / 4;
      n++; if (waterAt(P.x + Math.cos(a) * r, P.y + Math.sin(a) * r)) w++;
    }
    this.phase += dt;
    const lap = 0.75 + 0.25 * Math.sin(this.phase * 1.7) * Math.sin(this.phase * 0.63);
    this.level = muted ? 0 : (w / n) * AMB.water * lap * opts.sfx / OPT_DEF.sfx;
    if (!this.gain && this.level > 0.001) this.startWater();
    if (this.gain && Math.abs(this.level - (this.set || 0)) > 0.0005) { this.set = this.level; this.gain.gain.setTargetAtTime(this.level, AC.currentTime, 0.3); }
    // pluie : un souffle aigu, selon l'averse
    this.rainLevel = muted || weather.kind !== 'rain' ? 0 : weather.k * AMB.rain * opts.sfx / OPT_DEF.sfx;
    if (!this.rainGain && this.rainLevel > 0.001) this.startRain();
    if (this.rainGain && Math.abs(this.rainLevel - (this.rainSet || 0)) > 0.0005) { this.rainSet = this.rainLevel; this.rainGain.gain.setTargetAtTime(this.rainLevel, AC.currentTime, 0.4); }
  },
  startRain() {                        // bruit blanc en boucle, filtré autour des aigus : le crépitement de la pluie
    const len = AC.sampleRate * 2, buf = AC.createBuffer(1, len, AC.sampleRate), d = buf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
    const src = AC.createBufferSource(), f = AC.createBiquadFilter(), g = AC.createGain();
    src.buffer = buf; src.loop = true; f.type = 'bandpass'; f.frequency.value = 2600; f.Q.value = 0.5; g.gain.value = 0;
    src.connect(f); f.connect(g); g.connect(AC.destination); src.start();
    this.rainGain = g;
  },
  startWater() {                       // bruit grave et doux, en boucle, à travers un filtre passe-bas
    const len = AC.sampleRate * 2, buf = AC.createBuffer(1, len, AC.sampleRate), d = buf.getChannelData(0);
    let b = 0;
    for (let i = 0; i < len; i++) { b = (b + (Math.random() * 2 - 1) * 0.08) * 0.985; d[i] = b * 3; }
    const src = AC.createBufferSource(), f = AC.createBiquadFilter(), g = AC.createGain();
    src.buffer = buf; src.loop = true; f.type = 'lowpass'; f.frequency.value = 700; g.gain.value = 0;
    src.connect(f); f.connect(g); g.connect(AC.destination); src.start();
    this.gain = g;
  },
  quiet() {
    this.level = 0; this.rainLevel = 0;
    if (this.gain && this.set !== 0) { this.set = 0; this.gain.gain.setTargetAtTime(0, AC.currentTime, 0.2); }
    if (this.rainGain && this.rainSet !== 0) { this.rainSet = 0; this.rainGain.gain.setTargetAtTime(0, AC.currentTime, 0.2); }
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
  return !!el && !INSTALLED && !!(el.requestFullscreen || el.webkitRequestFullscreen) &&
    (document.fullscreenEnabled !== false || document.webkitFullscreenEnabled);
}
/* Il faut un geste de l'utilisateur (toucher, clic, touche) : appeler goFullscreen() directement dans l'événement.
   Un bouton de manette en vaut un pour Chromium, pas pour Firefox : le refus est noté (fsRefusedAt) et la ligne
   « Plein écran » des options dit alors comment faire. En sortir est toujours permis. */
let fsRefusedAt = -1e9;
const FS_REFUSED_NOTE = 5000;          // ms
function goFullscreen() {
  if (!canFullscreen() || fsElement()) return;
  const el = document.documentElement, refused = () => { fsRefusedAt = performance.now(); };
  try {
    const p = el.requestFullscreen ? el.requestFullscreen({ navigationUI: 'hide' }) : el.webkitRequestFullscreen();
    Promise.resolve(p).then(() => {
      fsRefusedAt = -1e9;
      if (screen.orientation && screen.orientation.lock) screen.orientation.lock('landscape').catch(() => {});
    }).catch(refused);
  } catch (e) { refused(); }   // on reste en fenêtre
}
function toggleFullscreen() {
  if (fsElement()) { (document.exitFullscreen || document.webkitExitFullscreen).call(document); }
  else goFullscreen();
}
// boutons tactiles en haut, à gauche du score (la colonne de droite reste aux compteurs des quêtes)
const PAUSE_BTN = { x: GW - 24 - 330 - 20 - 126, y: 41, w: 126, h: 70 };
const FS_BTN = { x: PAUSE_BTN.x - 20 - 126, y: 41, w: 126, h: 70 };

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
  if (k === 'r') return 'sniff';
  if (k === 'enter' || k === ' ') return 'ok';
  if (k === 'escape' || k === 'p') return 'pause';
  if (k === 'm') return 'mute';
  if (k === 'f') return 'fullscreen';
  return null;
}
addEventListener('keydown', e => {
  audioOn();
  touchMode = false; pad.on = false;
  const m = MOVE_CODES[e.code], a = actionOfKey(e);
  if (a === 'fullscreen') { if (!e.repeat) toggleFullscreen(); e.preventDefault(); return; }
  if (state === 'options' && (a === 'ok' || a === 'bite' || a === 'act' || m === 'left' || m === 'right') && optRows()[optSel].id === 'fs') {
    if (!e.repeat) toggleFullscreen();   // dans l'événement : le navigateur l'accepte
    e.preventDefault(); return;
  }
  if (m) { held[m] = true; if (!e.repeat) pressed[m] = true; e.preventDefault(); }
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
/* Pause automatique : une partie ne continue jamais sans personne devant (fenêtre qui perd le focus, onglet caché,
   manette débranchée). Seulement en cours de jeu : un dialogue attend déjà le joueur. */
function autoPause() {
  if (state !== 'play') return;
  state = 'pause'; openPauseMenu(); Music.refresh();
}
function onLeave() { for (const k in held) held[k] = false; autoPause(); }
addEventListener('blur', onLeave);

/* manette (API Gamepad, disposition « standard ») : stick gauche ou croix pour marcher et choisir dans les menus,
   A = mordre (ou parler, lire, gratter…) et valider, X ou B = aboyer, Y = flairer, Start = pause, Select = son.
   Les boutons sont lus à chaque image (pollPad) : un appui = une impulsion dans `pressed`, comme une touche. */
const PAD_MAP = { 0: ['bite', 'ok'], 1: ['bark'], 2: ['bark'], 3: ['sniff'], 8: ['mute'], 9: ['pause'],
                  12: ['up'], 13: ['down'], 14: ['left'], 15: ['right'] };
const PAD_DEAD = 0.25;
const pad = { on: false, vx: 0, vy: 0, prev: {}, sx: 0, sy: 0, n: 0 };
function pollPad() {
  const list = (navigator.getGamepads && navigator.getGamepads()) || [];
  const down = {};
  let vx = 0, vy = 0, used = false, n = 0;
  for (const gp of list) {
    if (!gp || gp.connected === false) continue;
    n++;
    const ax = gp.axes[0] || 0, ay = gp.axes[1] || 0;
    if (Math.hypot(ax, ay) > PAD_DEAD) { vx = ax; vy = ay; }
    gp.buttons.forEach((b, i) => { if (b && (b.pressed || b.value > 0.5)) down[i] = true; });
  }
  const cx = (down[15] ? 1 : 0) - (down[14] ? 1 : 0), cy = (down[13] ? 1 : 0) - (down[12] ? 1 : 0);
  if (cx || cy) { vx = cx; vy = cy; }
  for (const i in PAD_MAP) if (down[i] && !pad.prev[i]) { for (const a of PAD_MAP[i]) pressed[a] = true; used = true; }
  // dans les menus, le stick donne une impulsion par mouvement franc, sur son axe principal : haut / bas (menus en
  // colonne), gauche / droite (menu de la pause, en ligne ; réglages des options). La croix passe par PAD_MAP.
  const horiz = Math.abs(vx) > Math.abs(vy);
  const sx = horiz && Math.abs(vx) > 0.6 ? Math.sign(vx) : 0, sy = !horiz && Math.abs(vy) > 0.6 ? Math.sign(vy) : 0;
  if (sy && sy !== pad.sy && !cy) pressed[sy < 0 ? 'up' : 'down'] = true;
  if (sx && sx !== pad.sx && !cx) pressed[sx < 0 ? 'left' : 'right'] = true;
  if (n < pad.n && pad.on) autoPause();             // la manette dont on jouait est débranchée
  pad.n = n; pad.sx = sx; pad.sy = sy; pad.prev = down; pad.vx = vx; pad.vy = vy;
  if (used) audioOn();
  if (used || Math.hypot(vx, vy) > 0.5) { pad.on = true; touchMode = false; }
}

/* tactile : joystick à gauche, boutons à droite (repère GUI) */
let touchMode = !!(window.matchMedia && matchMedia('(pointer: coarse)').matches);
const stick = { id: null, ox: 0, oy: 0, x: 0, y: 0, vx: 0, vy: 0 };
const BTN = { bark: { x: 1560, y: 900, r: 105 }, bite: { x: 1780, y: 790, r: 105 }, sniff: { x: 1800, y: 575, r: 78 } };
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
  if (state === 'options') { optionsTap(gx, gy); return; }
  if (state === 'badges') { closeBadges(); return; }
  if (menu && (state === 'title' || state === 'over' || state === 'pause')) {   // menus : toucher une entrée la choisit
    const i = menuHit(gx, gy);
    if (i >= 0) { menu.sel = i; pressed.ok = true; }
    else if (state === 'pause') pressed.pause = true;                    // ailleurs : on reprend
    return;
  }
  if (state !== 'play' || !touchMode) { pressed.ok = true; return; }
  const pb = PAUSE_BTN;
  if (gx > pb.x - 10 && gx < pb.x + pb.w + 10 && gy > pb.y - 10 && gy < pb.y + pb.h + 10) { pressed.pause = true; return; }
  for (const k of ['bark', 'bite', 'sniff']) {
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
   (mêmes pixels) pour qu'aucune jointure n'apparaisse à l'échelle d'affichage. Autour de la carte, la marge de la
   lisière (MAP.edge.ring : MAP.edge.r tuiles qui prolongent le bord) a ses propres blocs, en bandes. */
const CHUNK = 16, CM = 2;
let groundChunks = [], ringTiles = null;
function groundTile(tx, ty) {              // [tuile, détail] du sol, dans la carte ou dans la marge (null au-delà)
  if (tx >= 0 && ty >= 0 && tx < MAP.w && ty < MAP.h) { const i = ty * MAP.w + tx; return [MAP.ground[i], MAP.over[i]]; }
  const idx = ringTiles.get(tx + ',' + ty);
  return idx === undefined ? null : [idx, 0];
}
function buildChunk(cx, cy, w, h) {
  const c = document.createElement('canvas');
  c.width = w * TS + 2 * CM; c.height = h * TS + 2 * CM;
  const g = c.getContext('2d');
  const blit = (idx, tx, ty) => g.drawImage(tilesImg, (idx % 16) * TS, Math.floor(idx / 16) * TS, TS, TS,
    (tx - cx) * TS + CM, (ty - cy) * TS + CM, TS, TS);
  for (let ty = cy - 1; ty < cy + h + 1; ty++) for (let tx = cx - 1; tx < cx + w + 1; tx++) {
    const t = groundTile(tx, ty);
    if (!t) continue;
    blit(t[0], tx, ty);
    if (t[1]) blit(t[1], tx, ty);
  }
  groundChunks.push({ c, x: cx * TS - CM, y: cy * TS - CM, w: c.width, h: c.height });
}
function buildGround() {
  groundChunks = [];
  ringTiles = new Map(MAP.edge.ring.map(([tx, ty, idx]) => [tx + ',' + ty, idx]));
  for (let cy = 0; cy < MAP.h; cy += CHUNK) for (let cx = 0; cx < MAP.w; cx += CHUNK)
    buildChunk(cx, cy, Math.min(CHUNK, MAP.w - cx), Math.min(CHUNK, MAP.h - cy));
  const R = MAP.edge.r;                    // la marge : bandes nord et sud (coins compris), puis ouest et est
  for (let cx = -R; cx < MAP.w + R; cx += CHUNK) {
    const w = Math.min(CHUNK, MAP.w + R - cx);
    buildChunk(cx, -R, w, R); buildChunk(cx, MAP.h, w, R);
  }
  for (let cy = 0; cy < MAP.h; cy += CHUNK) {
    const h = Math.min(CHUNK, MAP.h - cy);
    buildChunk(-R, cy, R, h); buildChunk(MAP.w, cy, R, h);
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
   plus une marge pour le liseré clair du bord, doit être dans l'eau. Marge de la lisière comprise (l'eau y continue). */
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
  const R = MAP.edge.r, WR = MAP.w + 2 * R;
  if (!waterTiles) {                       // tuiles ayant au moins un coin d'eau (marge comprise)
    waterTiles = new Uint8Array(WR * (MAP.h + 2 * R));
    const W1 = MAP.w + 1, c = (a, b) => MAP.water[clamp(b, 0, MAP.h) * W1 + clamp(a, 0, MAP.w)];
    for (let j = -R; j < MAP.h + R; j++) for (let i = -R; i < MAP.w + R; i++)
      waterTiles[(j + R) * WR + i + R] = c(i, j) | c(i + 1, j) | c(i, j + 1) | c(i + 1, j + 1);
  }
  const n = ATLAS['fx/ripple'].f.length, ng = ATLAS['fx/glint'].f.length;
  for (let ty = Math.max(-R, Math.floor(vy / TS)); ty <= Math.min(MAP.h + R - 1, Math.floor((vy + VH) / TS)); ty++)
    for (let tx = Math.max(-R, Math.floor(vx / TS)); tx <= Math.min(MAP.w + R - 1, Math.floor((vx + VW) / TS)); tx++) {
      if (!waterTiles[(ty + R) * WR + tx + R]) continue;
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
  tree: [-18, -16, 18, 0], apple_tree: [-18, -16, 18, 0], apple_tree_young: [-14, -12, 14, 0], apple_crate: [-24, -18, 24, 0],
  bicycle: [-34, -10, 34, 0], bush: [-28, -18, 28, 0], hay: [-26, -22, 26, 0], rock: [-22, -18, 22, 0],
  fence_wood_h: [0, -14, 64, 0], fence_wood_v: [-8, -64, 8, 0], signpost: [-7, -8, 7, 0],
  cone: [-12, -10, 12, 0], road_sign: [-7, -8, 7, 0], lamppost: [-10, -10, 10, 0],
  house_red: [-76, -84, 76, -2], house_blue: [-76, -84, 76, -2], house_timber: [-70, -84, 70, -2], house_tall: [-76, -84, 76, -2],
  bakery: [-90, -84, 90, -2], stall_fruit: [-52, -24, 52, 0], stall_veg: [-52, -24, 52, 0], stall_flower: [-52, -24, 52, 0],
  cafe_table: [-22, -10, 22, 0], doghouse: [-28, -26, 28, 0],
  bench: [-40, -20, 40, 0], mailbox: [-7, -6, 7, 0], hedge: [0, -36, 64, 0], flower_pot: [-14, -18, 14, 0],
  warehouse: [-116, -104, 116, -4], container: [-92, -54, 92, 0], pallet: [-26, -16, 26, 0],
  barrel_blue: [-18, -16, 18, 0], barrel_red: [-18, -16, 18, 0], crate: [-24, -22, 24, 0],
  fence_metal_h: [0, -12, 64, 0], fence_metal_v: [-6, -64, 6, 0],
  // le port (rails, péniche, portique : pas de collision ; les pieds du portique sont dans RAILS)
  container_blue: [-92, -54, 92, 0], container_green: [-92, -54, 92, 0], container_stack: [-92, -54, 92, 0],
  truck: [-104, -26, 104, 0], forklift: [-48, -18, 48, 0], guard_hut: [-50, -40, 50, -2], bollard: [-10, -10, 10, 0],
  buffer_stop: [-16, -12, 16, 0],
  // ferme et rivière (roseaux, barque et pont : pas de collision)
  barn: [-96, -84, 96, -2], chicken_coop: [-36, -14, 36, 0],
  tractor: [-52, -20, 52, 0], scarecrow: [-7, -8, 7, 0],
  // forêt et parc (champignons, fougère et bac à sable : pas de collision)
  fir: [-18, -16, 18, 0], stump: [-20, -16, 20, 0], log: [-54, -22, 56, 0], slide: [-56, -14, 58, 0],
  swing: [-58, -12, 58, 0], fountain: [-52, -40, 52, 0], playhouse: [-44, -50, 44, -2],
  // lisière : la butte du tunnel, jusqu'à la bouche (Tecky s'arrête devant au lieu d'y fourrer la tête)
  tunnel: [-200, -420, 40, 0],
};
const FLAT = new Set(['bridge', 'sandbox', 'burrow', 'rail', 'dog_bed', 'fallen_apples']);   // posés à plat : dessinés sous les personnages
// collisions en plusieurs morceaux : garde-corps du pont (son tablier n'est pas de l'eau, voir BRIDGES dans
// pack_web.py), pieds du portique du port
const RAILS = { bridge: [[-80, -320, -62, 0], [62, -320, 80, 0]], crane: [[-204, -16, -156, 0], [156, -16, 204, 0]],
  goal_net: [[-90, -58, -72, 0], [72, -58, 90, 0], [-80, -64, 80, -52]] };   // filet de Léon : côtés et fond
let solids = [];
// limites des pieds (rectangle [x0, y0] -> [x1, y1]) au bord de la carte ; au-delà, la lisière (voir « bord de la carte »)
const BOUND = { side: 12, top: 28, bottom: 4 };
const offMap = (x0, y0, x1, y1) =>
  x0 < BOUND.side || y0 < BOUND.top || x1 > MAP.w * TS - BOUND.side || y1 > MAP.h * TS - BOUND.bottom;
function waterAt(x, y) {           // (au-delà du bord, l'eau continue tout droit, comme le sol de la lisière)
  const fx = x / TS, fy = y / TS;
  const i = Math.floor(fx), j = Math.floor(fy);
  const W1 = MAP.w + 1, c = (a, b) => MAP.water[clamp(b, 0, MAP.h) * W1 + clamp(a, 0, MAP.w)];
  const u = fx - i, v = fy - j;
  const val = c(i, j) * (1 - u) * (1 - v) + c(i + 1, j) * u * (1 - v) + c(i, j + 1) * (1 - u) * v + c(i + 1, j + 1) * u * v;
  return val > 0.42;
}
function blockedPoint(x, y) {
  if (offMap(x, y - 12, x, y)) return true;
  if (waterAt(x, y)) return true;
  for (const s of solids) if (x > s[0] && x < s[2] && y > s[1] && y < s[3]) return true;
  return false;
}
/* Pieds = rectangle [x-hw, y-12] -> [x+hw, y]. Obstacles : vrai test de chevauchement
   (un poteau plus fin que les pattes ne peut plus se glisser entre deux points testés).
   Eau : échantillonnage du bord, suffisant car ses contours sont arrondis. */
function blockedFeet(x, y, hw) {
  const x0 = x - hw, x1 = x + hw, y0 = y - 12, y1 = y;
  if (offMap(x0, y0, x1, y1)) return true;
  for (const s of solids) if (x1 > s[0] && x0 < s[2] && y1 > s[1] && y0 < s[3]) return true;
  if (train && trainHit(x0, y0, x1, y1)) return true;      // Titine, le petit train du port (obstacle qui bouge)
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

/* ------------------------------------------------------------------ bord de la carte */
/* La carte est bordée d'une lisière (MAP.edge.decor, lisiere.py : fourrés, arbres, sapins le long de la forêt) et, aux
   deux bouts de la grande route, de l'entrée d'un tunnel où les voitures disparaissent. Elle est dessinée dans une
   marge que la caméra peut montrer au-delà des bords (EDGE.cam), sur un sol qui prolonge celui du bord (buildGround).
   Ce n'est pas un obstacle : c'est le bord de la carte (BOUND) qui arrête Tecky, juste devant. S'il pousse contre le
   bord sans avancer pendant EDGE.push s, il le dit (pas plus d'une fois toutes les EDGE.again s de jeu). */
const EDGE = { cam: 64, push: 0.6, again: 8, near: 8 };
const EDGE_DECOR = MAP.edge.decor.map(([n, x, y, flip]) => ({ key: 'decor/' + n, n, x, y, flip }));
const EDGE_SOLIDS = EDGE_DECOR.filter(d => FOOT[d.n]).map(({ n, x, y, flip }) => {   // (ajoutés à solids par reset)
  const [a, b, c, e] = FOOT[n];
  return flip ? [x - c, y + b, x - a, y + e] : [x + a, y + b, x + c, y + e];
});
const camClampX = x => clamp(x, -EDGE.cam, MAP.w * TS - VW + EDGE.cam);
const camClampY = y => clamp(y, -EDGE.cam, MAP.h * TS - VH + EDGE.cam);
function edgeBump(dt, ix, iy, ox, oy) {
  // un pas de plus vers l'extérieur sortirait de la carte, ou entrerait dans la butte d'un tunnel
  const hw = 16, x = P.x + Math.sign(ix) * EDGE.near, y = P.y + Math.sign(iy) * EDGE.near;
  const x0 = x - hw, x1 = x + hw, y0 = y - 12, y1 = y;
  const out = offMap(x0, y0, x1, y1) || EDGE_SOLIDS.some(s => x1 > s[0] && x0 < s[2] && y1 > s[1] && y0 < s[3]);
  P.edgeT = out && Math.hypot(P.x - ox, P.y - oy) < 1 ? P.edgeT + dt : 0;
  if (P.edgeT < EDGE.push || timePlayed - P.edgeAt < EDGE.again) return;
  P.edgeT = 0; P.edgeAt = timePlayed;
  const [r0, r1] = MAP.traffic.road, tunnel = ix !== 0 && P.y > r0 && P.y < r1 + 24;   // au bout de la grande route
  addWordPop(tunnel ? 'Le tunnel, c’est pour les voitures !' : 'Alice n’a pas pu aller si loin !', P.x, P.y - 120, 'tecky');
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
// poses de repos de Tecky (tecky.REST_ANIMS) : assis, bâille, se gratte, dort, s'ébroue
for (const [a, [fps, loop]] of Object.entries(MAP.rest)) { FPS[a] = fps; if (loop) LOOP[a] = true; }

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
      alpha: alpha === undefined ? this.alpha : alpha, sy: this.mode === 'crouch' ? 0.84 : this.sy });
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
/* Difficulté « facile » (option, pour les nouvelles parties ; gardée dans la sauvegarde) : 5 os au départ, morsures
   moitié moins fortes (un demi-os), et un chien sur trois en moins (toujours les mêmes : d.id % 3 === 2). */
let gameDiff = 'normal';
const facile = () => gameDiff === 'facile';
const ITEM = {
  bone: { heal: 2 }, sausage: { grow: true },
  medal: { pts: 100 }, squeaky: { pts: 50 }, ball: { pts: 20 },
  hairclip: { clue: 0 }, shoe: { clue: 1 }, plush: { clue: 2 },
  goldbone: { pts: 100, gold: true },     // trésor enterré (os doré), à collectionner
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
const ARROW = { show: 12, nudgeAfter: 45, nudge: 8, sc: 1.3 };   // s ; sc : taille de la flèche et de son icône
let arrowT = 0, stuckT = 0;
function showArrow(t) { arrowT = Math.max(arrowT, t || ARROW.show); stuckT = 0; }
function arrowTarget() {
  const k = nextClue();
  if (k === 3) return alice;
  return items.find(it => it.n === CLUES[k]) || alice;
}

let state = 'loading';          // loading | title | play | dialog | pause | options | badges | over | ending | win
let P, alice, dogs, hens, cars, butterflies, items, fxs, pops, rings, digs, decor, camX = 0, camY = 0, shake = 0;
let dusts = [], leaves = [], leafTrees = null, clouds = [], sun = 0, saveT = 0;
// fled : chiens mis en fuite (aventure) ou devenus copains (balade)
let score = 0, timePlayed = 0, fled = 0, treasures = 0, dialog = null, dialogReturn = 'play', aliceSniffed = false;
let hintText = null, digHint = null, playHint = null, tunnelHint = null, talkHint = null, overT = 0, titleT = 0;

function reset() {
  solids = [];
  decor = MAP.decor.map(([n, x, y]) => {
    for (const f of [FOOT[n], ...(RAILS[n] || [])]) if (f) solids.push([x + f[0], y + f[1], x + f[2], y + f[3]]);
    return { key: 'decor/' + n, x, y, n };
  });
  solids.push(...EDGE_SOLIDS);                       // les buttes des tunnels, au bord de la carte
  P = new Actor('tecky', MAP.start[0], MAP.start[1]);
  // 5 emplacements d'os (2 PV par os) ; Tecky démarre avec 3 os pleins
  const bones = facile() ? 5 : START_BONES;
  Object.assign(P, { hp: bones * 2, hpMax: bones * 2, boneFx: 0, inv: 0, bumpT: 0, cdBark: 0, cdBite: 0, cdSniff: 0,
    mode: 'free', kx: 0, ky: 0, hitDone: false, edgeT: 0, edgeAt: -99 });
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
  if (facile()) dogs = dogs.filter(d => d.id % 3 !== 2);
  hens = MAP.hens.map(newHen);
  cows = MAP.cows.map(newCow);
  farmer = newFarmer(); farm = { state: 'new' };
  postman = newNpc('postman', MAP.postman, 1.05); post = { state: 'new' };
  letters = MAP.letters.map(([x, y]) => ({ x, y, t: Math.random() * 2, got: false }));
  neighbor = newNpc('neighbor', MAP.neighbor, 1.35); rose = { state: 'new' }; pompon = newPompon();
  leon = newNpc('leon', MAP.leon, 0.95); fete = { state: 'new' }; balls = MAP.balls.map(newBall);
  iris = Object.assign(newNpc('iris', MAP.iris, 0.8), { markY: IRIS.markY, woof: true, tip: 0 }); jouets = { state: 'new' };
  toys = MAP.toys.map(newToy);
  villagers = MAP.villagers.map(newVillager);
  train = newTrain();
  piquette = Object.assign(newNpc('piquette', MAP.piquette, 1.3), { markY: BABY.markY }); piq = { state: 'new' };
  babies = MAP.babies.map(newBaby); babySeq = 0;
  critters = MAP.critters.map(newCritter);
  ducks = MAP.ducks.map(newDuck); linkDucks();
  bitten = false; newBadges = []; toasts = []; napped = false;
  resetWeather(); puddles = null; graceT = 0;
  walkGrid = null; distField = null; trail = []; tunnelSeen = false; crumbs = []; followN = 0;
  seenCells = new Uint8Array(cellsW() * cellsH()); zone = null; zoneT = 0; banner = null; tuneT = 0;
  cars = MAP.traffic.vehicles.map(newVehicle);
  butterflies = MAP.butterflies.map(newButterfly);
  items = MAP.items.map(([n, x, y]) => ({ n, x, y, t: Math.random() * 3 }));
  digs = MAP.dig.map(([x, y]) => ({ x, y, dug: false, t: Math.random() * 2 }));
  fxs = []; pops = []; rings = []; dusts = []; leaves = []; leafTrees = null;
  score = 0; timePlayed = 0; fled = 0; treasures = 0; shake = 0; barkImmuneSeen = false; pendingSay = null;
  clues = [false, false, false]; aliceSniffed = false; arrowT = 0; stuckT = 0; sun = 0; hug = 0; saveT = 0;
  camX = camClampX(P.x - VW / 2);
  camY = camClampY(P.y - VH / 2);
}

/* ------------------------------------------------------------------ dialogues */
const WHO = {
  tecky: { name: 'Tecky', portrait: 'hud/portrait_tecky' },
  alice: { name: 'Alice', portrait: 'hud/portrait_alice' },
  farmer: { name: 'Gaston', portrait: 'hud/portrait_farmer' },
  postman: { name: 'Marcel', portrait: 'hud/portrait_postman' },
  neighbor: { name: 'Mamie Rose', portrait: 'hud/portrait_neighbor' },
  leon: { name: 'Léon', portrait: 'hud/portrait_leon' },
  iris: { name: 'Iris', portrait: 'hud/portrait_iris' },
  piquette: { name: 'Maman Piquette', portrait: 'hud/portrait_piquette' },
  info:  { name: '', portrait: null },
};
// une réplique demandée pendant un dialogue passe à la suite (ex. : le fermier parle, et Tecky ramasse la barrette)
function say(lines, onEnd) {
  if (state === 'dialog' && dialog) { (dialog.queue = dialog.queue || []).push([lines, onEnd]); return; }
  dialog = { lines, i: 0, c: 0, onEnd };
  dialogReturn = state;
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
      const cb = dialog.onEnd, queue = dialog.queue || [];
      dialog = null;
      graceT = GRACE;                  // un petit répit en sortant d'un dialogue
      state = dialogReturn === 'dialog' ? 'play' : dialogReturn;
      if (cb) cb();
      for (const [l, e] of queue) say(l, e);
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
        ? "Glisse le doigt à gauche pour marcher. Les boutons à droite servent à aboyer, à mordre et à flairer la piste d'Alice."
        : "[walk] pour marcher, [bark] pour aboyer, [sniff] pour flairer la piste d'Alice. [pause] pour la pause, [mute] pour le son." },
    // le bouton de morsure fait tout ce qui se fait de près (biteAction) : la bulle au-dessus de la cible le dit
    { who: 'info', text: (balade() ? 'En balade, personne ne se fait mal : ' + (touchMode ? 'le bouton de morsure' : '[bite]') +
        " sert à jouer avec un chien, à parler, à lire un panneau, à gratter le sol ou à passer dans un terrier, selon ce qui est tout près. Un petit mot s'affiche pour le dire."
      : (touchMode ? 'Le bouton de morsure' : '[bite]') +
        " sert à mordre, mais aussi à parler, à lire un panneau, à gratter le sol ou à passer dans un terrier, selon ce qui est tout près. Un petit mot s'affiche pour le dire.") },
    { who: 'info', text: "Les os rendent un os perdu, les saucisses ajoutent un os en plus. Et des traces de pattes au sol cachent peut-être un trésor : il n'y a plus qu'à gratter !" },
  ].concat(balade() ? [
    { who: 'info', text: "En balade, joue avec les chiens du coin : vous deviendrez copains ! " +
        (touchMode ? 'Aboyer les appelle.' : '[bark] les appelle.') },
  ] : []);
}

/* ------------------------------------------------------------------ combat */
function addFx(key, x, y, opt) { fxs.push(Object.assign({ key, x, y, t: 0, fps: 14 }, opt || {})); }
function addPop(text, x, y) { pops.push({ text, x, y, t: 0 }); }
// who : qui le dit (voix des bulles : un personnage, 'tecky', 'info' = narrateur, ou un animal, 'train')
function addWordPop(text, x, y, who) { pops.push({ text, x, y, t: 0, word: true, who }); }
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
  dropToy('Oups !');                   // on n'aboie pas la gueule pleine
  const [vx, vy] = DIRV[P.dir];
  barkAtTrain(vx, vy);
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
      if (!pops.some(p => p.word && p.dog === d)) { addWordPop('Même pas peur !', d.x, d.y - 130, 'doberman'); pops[pops.length - 1].dog = d; }
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
  for (const c of cows) {
    const dx = c.x - P.x, dy = c.y - P.y, l = Math.hypot(dx, dy);
    if (l > 1 && l < BARK.range + 40 && (dx * vx + dy * vy) / l > BARK.cos) scareCow(c);
  }
  for (const b of butterflies) {
    const dx = b.x - P.x, dy = b.y - P.y, l = Math.hypot(dx, dy);
    if (l > 1 && l < BARK.range && (dx * vx + dy * vy) / l > BARK.cos) scareButterfly(b, P.x, P.y);
  }
  for (const c of critters) {
    const dx = c.x - P.x, dy = c.y - P.y, l = Math.hypot(dx, dy);
    if (l > 1 && l < BARK.range && (dx * vx + dy * vy) / l > BARK.cos) scareCritter(c);
  }
  for (const b of babies) {            // les bébés hérissons se roulent en boule
    const dx = b.x - P.x, dy = b.y - P.y, l = Math.hypot(dx, dy);
    if (b.mode !== 'home' && l > 1 && l < BARK.range && (dx * vx + dy * vy) / l > BARK.cos) b.ballT = BABY.ball;
  }
  for (const b of balls) {             // les ballons de Léon roulent, plus fort de près
    const dx = b.x - P.x, dy = b.y - P.y, l = Math.hypot(dx, dy);
    if (l > 1 && l < BARK.range && (dx * vx + dy * vy) / l > BARK.cos) kickBall(b, P.x, P.y, BALL.bark * (1 - 0.5 * l / BARK.range));
  }
  for (const d of ducks) {
    const dx = d.x - P.x, dy = d.y - P.y, l = Math.hypot(dx, dy);
    if (l > 1 && l < BARK.range && (dx * vx + dy * vy) / l > BARK.cos) scareDuck(d);
  }
  {                                    // Pompon n'aime pas qu'on lui aboie dessus
    const dx = pompon.x - P.x, dy = pompon.y - P.y, l = Math.hypot(dx, dy);
    if (l > 1 && l < BARK.range && (dx * vx + dy * vy) / l > BARK.cos) { pompon.hissT = 0.8; addWordPop('Pfff !', pompon.x, pompon.y - 70, 'cat'); }
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
    addWordPop('Ouf !', P.x, P.y - 130, 'tecky');
    rumble('bump');
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
function newHen([kind, x, y, quest]) {
  const h = new Actor(kind, x, y);
  return Object.assign(h, { fps: HEN_FPS, hx: x, hy: y, mode: 'idle', timer: Math.random() * 2,
    dir: Math.random() < 0.5 ? 'left' : 'right', quest: !!quest, penned: false });
}
function scareHen(h, fromX, fromY, t) {
  if (h.mode === 'flee' && h.timer >= t) return;
  if (h.mode !== 'flee' && timePlayed - lastCluck > 0.15) { lastCluck = timePlayed; SFX.cluck(); }
  const dx = h.x - fromX, dy = h.y - fromY, l = Math.max(1, Math.hypot(dx, dy));
  h.mode = 'flee'; h.timer = t; h.fleeT = t; h.vx = dx / l; h.vy = dy / l;
  if (h.quest && !h.penned) funnelHen(h);
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
      keepHen(h);
      if (h.timer <= 0) {
        h.mode = 'idle'; h.timer = 0.6 + Math.random(); h.setAnim('idle');
        if (h.quest && !h.penned) { h.hx = h.x; h.hy = h.y; }    // poule de la quête : elle reste où on l'a poussée
      }
      return;
    }
    case 'peck':
      if (h.done()) { h.mode = 'idle'; h.timer = 0.3 + Math.random() * 1.2; h.setAnim('idle'); }
      return;
    case 'walk': {
      const dx = h.tx - h.x, dy = h.ty - h.y, l = Math.hypot(dx, dy), ox = h.x, oy = h.y;
      if (l > 4) { moveActor(h, dx / l * HEN.spd * dt, dy / l * HEN.spd * dt, 8); keepHen(h); }
      if (l <= 4 || h.timer <= 0 || (ox === h.x && oy === h.y)) { h.mode = 'idle'; h.timer = 0.4 + Math.random(); h.setAnim('idle'); }
      return;
    }
    default:   // au repos : picorer (le plus souvent) ou faire quelques pas autour de sa place
      if (h.timer > 0) return;
      if (Math.random() < 0.6) { h.mode = 'peck'; h.setAnim('peck'); return; }
      const a = Math.random() * Math.PI * 2, r = Math.random() * HEN.roam;
      h.tx = h.hx + Math.cos(a) * r; h.ty = h.hy + Math.sin(a) * r * 0.6;
      if (h.penned) { const R = penRect(); h.tx = clamp(h.tx, R[0], R[2]); h.ty = clamp(h.ty, R[1], R[3]); }
      h.dir = h.tx < h.x ? 'left' : 'right';
      h.mode = 'walk'; h.timer = 2.5; h.setAnim('walk');
  }
}

/* ------------------------------------------------------------------ les vaches de la campagne */
/* Trois vaches (MAP.cows : [espèce, x, y] ; cows.py : la pie noire, la pie rouge et son veau) paissent dans le grand pré
   de la campagne : elles broutent, font quelques pas autour de leur place (COW.roam ; le veau reste près de sa mère),
   lèvent la tête vers Tecky quand il approche (COW.look) et meuglent de temps en temps quand il est dans les parages
   (« Meuh ! »). Un aboiement les fait meugler et s'éloigner au petit trot (le veau suit sa mère). Ce sont des obstacles :
   une boîte de `solids` (box) déplacée avec elles, vidée le temps de leur propre pas (cowStep) ; elles ne marchent
   jamais sur Tecky. Rien n'est sauvegardé. */
const COW = { roam: 150, spd: 38, trot: 130, trotT: 1.5, look: 200, moo: [9, 20], hear: 520, half: 44, calfHalf: 30, depth: 16 };
let cows = [];
function newCow([kind, x, y], i) {
  const c = { kind, i, x, y, hx: x, hy: y, anim: 'graze', mode: 'graze', t: Math.random() * 3, timer: 2 + Math.random() * 4,
    dir: Math.random() < 0.5 ? 'left' : 'right', mooT: rnd(COW.moo), vx: 0, vy: 0, box: [0, 0, 0, 0] };
  cowBox(c); solids.push(c.box);
  return c;
}
const cowMother = c => c.kind === 'calf' ? cows.find(o => o.kind === 'cow_brown') : null;
function cowBox(c) {
  const w = c.kind === 'calf' ? COW.calfHalf : COW.half;
  c.box[0] = c.x - w; c.box[1] = c.y - COW.depth; c.box[2] = c.x + w; c.box[3] = c.y;
}
function cowAnim(c, a) { if (c.anim !== a) { c.anim = a; c.t = 0; } }
// un pas : jamais dans un obstacle (sa propre boîte est retirée le temps du pas), ni sur Tecky
function cowStep(c, dx, dy) {
  const ox = c.x, oy = c.y;
  c.box.fill(0);
  moveActor(c, dx, dy, c.kind === 'calf' ? COW.calfHalf : COW.half);
  const b = c.box; cowBox(c);
  if (P.x + 12 > b[0] && P.x - 12 < b[2] && P.y > b[1] && P.y - 12 < b[3]) { c.x = ox; c.y = oy; cowBox(c); }
  return c.x !== ox || c.y !== oy;
}
function cowMoo(c) {
  addWordPop('Meuh !', c.x, c.y - (c.kind === 'calf' ? 80 : 110), 'cow');
  SFX.moo(c.kind === 'calf' ? 1.6 : 1);
  if (c.mode !== 'trot') { c.mode = 'moo'; c.timer = 0.9; cowAnim(c, 'moo'); c.dir = P.x < c.x ? 'left' : 'right'; }
}
function scareCow(c) {               // un aboiement : elle meugle et s'éloigne au petit trot (le veau suit sa mère)
  if (c.mode === 'trot') return;
  const dx = c.x - P.x, dy = c.y - P.y, l = Math.max(1, Math.hypot(dx, dy));
  c.vx = dx / l; c.vy = dy / l * 0.6; c.mode = 'trot'; c.timer = COW.trotT; c.dir = c.vx < 0 ? 'left' : 'right'; cowAnim(c, 'walk');
  addWordPop('Meuuuh !', c.x, c.y - (c.kind === 'calf' ? 80 : 110), 'cow');
  SFX.moo(c.kind === 'calf' ? 1.6 : 0.9);
  for (const o of cows) if (cowMother(o) === c) scareCow(o);
}
function updateCow(c, dt) {
  c.t += dt; c.timer -= dt;
  const dP = dist(c.x, c.y, P.x, P.y);
  if ((c.mooT -= dt) <= 0) { c.mooT = rnd(COW.moo); if (dP < COW.hear && (c.mode === 'graze' || c.mode === 'idle')) cowMoo(c); }
  switch (c.mode) {
    case 'moo':
      if (c.timer <= 0) { c.mode = 'idle'; c.timer = 1 + Math.random() * 2; cowAnim(c, 'idle'); }
      return;
    case 'trot': {
      const k = Math.max(0.3, c.timer / COW.trotT);
      const moved = cowStep(c, c.vx * COW.trot * k * dt, c.vy * COW.trot * k * dt);
      if (c.timer <= 0 || !moved) { c.mode = 'idle'; c.timer = 1.5 + Math.random() * 2; cowAnim(c, 'idle'); c.hx = c.x; c.hy = c.y; }
      return;
    }
    case 'walk': {
      const dx = c.tx - c.x, dy = c.ty - c.y, l = Math.hypot(dx, dy);
      const moved = l > 4 && cowStep(c, dx / l * COW.spd * dt, dy / l * COW.spd * dt);
      if (l <= 4 || c.timer <= 0 || !moved) { c.mode = 'graze'; c.timer = 3 + Math.random() * 5; cowAnim(c, 'graze'); }
      return;
    }
    default: {                         // broute, ou se repose ; lève la tête vers Tecky quand il approche
      if (dP < COW.look && P.mode !== 'ko') {
        cowAnim(c, 'idle'); c.dir = P.x < c.x ? 'left' : 'right'; c.timer = Math.max(c.timer, 1.2); return;
      }
      if (c.timer > 0) return;
      if (Math.random() < 0.45) {
        c.mode = c.mode === 'graze' ? 'idle' : 'graze'; cowAnim(c, c.mode); c.timer = 2 + Math.random() * 4; return;
      }
      // quelques pas autour de sa place (le veau, à côté de sa mère)
      const m = cowMother(c), a = Math.random() * Math.PI * 2, r = Math.random() * (m ? 50 : COW.roam);
      const hx = m ? m.x + (m.dir === 'left' ? 80 : -80) : c.hx, hy = m ? m.y + 12 : c.hy;
      c.tx = hx + Math.cos(a) * r; c.ty = hy + Math.sin(a) * r * 0.5;
      c.dir = c.tx < c.x ? 'left' : 'right'; c.mode = 'walk'; c.timer = 5; cowAnim(c, 'walk');
    }
  }
}
function drawCow(c) {
  const fps = MAP.cowFps[c.kind][c.anim] * (c.mode === 'trot' ? 2.2 : 1);
  drawSpr(c.kind + '/' + c.anim, Math.floor(c.t * fps), c.x, c.y, { flip: c.dir === 'left' });
}

function doBite() {
  dropToy('Oups !');
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
  if (hit) rumble('bite');
}

/* ------------------------------------------------------------------ petites bêtes */
/* Écureuils (forêt, parc) et chats (village, zone industrielle) flânent près de leur coin. Si Tecky approche ou aboie vers
   eux, ils filent vers le refuge le plus proche qui ne soit pas du côté de Tecky : un arbre ou un sapin pour l'écureuil
   (il grimpe au tronc et disparaît dans le feuillage), un toit de maison ou un conteneur pour le chat (il saute dessus
   et feule quand Tecky s'approche). Ils redescendent quand Tecky s'est éloigné. La première fois que Tecky fait
   grimper chacun d'eux : des points. Pas de collision : ce sont de petites bêtes agiles. */
const CRITTER = { scare: 170, run: 330, walk: 38, roam: 100, climb: 0.55, jump: 0.45, back: 340, wait: 4, pts: 40, hiss: 230 };
// refuges : décor -> [décalage x, hauteur (px au-dessus du pied du décor)] du perchoir
const REFUGES = {
  squirrel: { tree: [[0, -58]], fir: [[0, -46]] },
  cat: { house_red: [[-44, -116], [44, -116]], house_blue: [[-44, -116], [44, -116]], house_timber: [[-34, -120], [34, -120]],
    house_tall: [[-36, -170], [36, -170]], bakery: [[-52, -110], [52, -110]], container: [[-40, -66], [40, -66]],
         container_blue: [[-40, -66], [40, -66]], container_green: [[-40, -66], [40, -66]],
         container_stack: [[-40, -118], [40, -118]] },
};
let critters = [];
const species = k => k === 'squirrel' ? 'squirrel' : 'cat';
function newCritter([kind, x, y]) {
  return { kind, x, y, hx: x, hy: y, h: 0, mode: 'roam', anim: 'idle', t: Math.random() * 3, timer: 1 + Math.random() * 2,
    dir: Math.random() < 0.5 ? 'left' : 'right', scored: false, tx: x, ty: y };
}
function critAnim(c, a) { if (c.anim !== a) { c.anim = a; c.t = 0; } }
function scareCritter(c) {
  if (c.mode !== 'roam') return;
  // refuge le plus proche, en évitant ceux qui sont du côté de Tecky
  let best = null, bs = Infinity;
  for (const d of decor) {
    const offs = (REFUGES[species(c.kind)] || {})[d.n];
    if (!offs) continue;
    for (const [ox, oy] of offs) {
      const bx = d.x + ox, l = dist(c.x, c.y, bx, d.y + 6);
      if (l > 900) continue;
      const sc = l + (dist(P.x, P.y, bx, d.y) < l ? 700 : 0);
      if (sc < bs) { bs = sc; best = { x: bx, y: d.y + 6, h: -oy, deco: d }; }
    }
  }
  c.mode = 'flee'; c.ref = best;
  if (!best) { const l = Math.max(1, dist(c.x, c.y, P.x, P.y)); c.ref = { x: c.x + (c.x - P.x) / l * 300, y: c.y + (c.y - P.y) / l * 300, h: 0 }; }
  critAnim(c, 'run');
}
function updateCritter(c, dt) {
  c.t += dt;
  const dP = dist(c.x, c.y, P.x, P.y), alive = P.mode !== 'ko';
  switch (c.mode) {
    case 'roam':
      if (alive && dP < CRITTER.scare && state === 'play') { scareCritter(c); return; }
      if ((c.timer -= dt) <= 0) {
        if (c.anim === 'idle') {
          const a = Math.random() * Math.PI * 2, r = Math.random() * CRITTER.roam;
          c.tx = c.hx + Math.cos(a) * r; c.ty = c.hy + Math.sin(a) * r * 0.6;
          critAnim(c, species(c.kind) === 'cat' ? 'walk' : 'run'); c.timer = 3;
        } else { critAnim(c, 'idle'); c.timer = 1.5 + Math.random() * 3; }
      }
      if (c.anim !== 'idle') {
        const dx = c.tx - c.x, dy = c.ty - c.y, l = Math.hypot(dx, dy);
        const sp = species(c.kind) === 'cat' ? CRITTER.walk : CRITTER.walk * 2.2;
        if (l < 4) { critAnim(c, 'idle'); c.timer = 1.5 + Math.random() * 3; }
        else { c.x += dx / l * Math.min(l, sp * dt); c.y += dy / l * Math.min(l, sp * dt); c.dir = dx < 0 ? 'left' : 'right'; }
      }
      return;
    case 'flee': {
      const dx = c.ref.x - c.x, dy = c.ref.y - c.y, l = Math.hypot(dx, dy);
      if (l < 6) {
        if (!c.ref.h) { c.mode = 'roam'; c.hx = c.x; c.hy = c.y; critAnim(c, 'idle'); c.timer = 2; return; }
        c.mode = 'up'; c.timer = 0; c.y0 = c.y;
        critAnim(c, species(c.kind) === 'cat' ? 'jump' : 'climb');
        if (!c.scored) {
          c.scored = true; score += CRITTER.pts;
          addPop('+' + CRITTER.pts, c.x - 20, c.y - 60);
        }
        addWordPop(c.kind === 'squirrel' ? 'Tchic tchic !' : 'Pfff !', c.x, c.y - 90, c.kind === 'squirrel' ? 'squirrel' : 'cat');
        return;
      }
      c.x += dx / l * Math.min(l, CRITTER.run * dt); c.y += dy / l * Math.min(l, CRITTER.run * dt);
      c.dir = dx < 0 ? 'left' : 'right';
      return;
    }
    case 'up': {                       // l'écureuil grimpe au tronc, le chat saute sur le toit
      c.timer += dt;
      const T = species(c.kind) === 'cat' ? CRITTER.jump : CRITTER.climb, u = Math.min(1, c.timer / T);
      c.h = c.ref.h * (species(c.kind) === 'cat' ? u : u * u) + (species(c.kind) === 'cat' ? Math.sin(u * Math.PI) * 40 : 0);
      if (u >= 1) {
        c.h = c.ref.h; c.mode = 'perched'; c.timer = 0; c.chatT = 1 + Math.random();
        critAnim(c, 'idle');
        if (c.kind === 'squirrel') for (let k = 0; k < 2; k++) leaves.push({ x: c.x + (Math.random() - 0.5) * 50, y: c.ref.y + 10 + Math.random() * 20,
          h: c.ref.h + 20, t: 0, ph: Math.random() * 6.28, landed: 0, c: Math.floor(Math.random() * 2) });
      }
      return;
    }
    case 'perched':
      // le chat regarde Tecky et feule s'il est tout près ; l'écureuil, caché, rouspète de temps en temps
      if (species(c.kind) === 'cat') {
        c.dir = P.x < c.x ? 'left' : 'right';
        critAnim(c, alive && dP < CRITTER.hiss ? 'hiss' : 'idle');
      } else if (alive && dP < 260 && (c.chatT -= dt) <= 0) {
        c.chatT = 2.5 + Math.random() * 2;
        addWordPop('Tchic !', c.x, c.y - c.h - 40, 'squirrel');
      }
      c.timer = dP > CRITTER.back ? c.timer + dt : 0;
      if (c.timer > CRITTER.wait) { c.mode = 'down'; c.timer = 0; critAnim(c, species(c.kind) === 'cat' ? 'jump' : 'climb'); }
      return;
    case 'down': {
      c.timer += dt;
      const T = species(c.kind) === 'cat' ? CRITTER.jump : CRITTER.climb, u = Math.min(1, c.timer / T);
      c.h = c.ref.h * (1 - u) + (species(c.kind) === 'cat' ? Math.sin(u * Math.PI) * 30 : 0);
      if (u >= 1) {                    // de retour au sol : il rentre tranquillement vers son coin
        c.h = 0; c.mode = 'roam'; c.tx = c.hx; c.ty = c.hy;
        critAnim(c, species(c.kind) === 'cat' ? 'walk' : 'run'); c.timer = 6;
      }
      return;
    }
  }
}
function critterVisible(c) { return !(c.kind === 'squirrel' && c.mode === 'perched'); }    // caché dans le feuillage
function drawCritter(c) {
  const fps = (MAP.critterFps[c.kind] || {})[c.anim] || 8;
  const loop = c.anim !== 'jump';
  const n = (ATLAS[c.kind + '/' + c.anim] || { f: [0] }).f.length;
  const i = Math.floor(c.t * fps);
  drawSpr(c.kind + '/' + c.anim, loop ? i : Math.min(i, n - 1), c.x, c.y - c.h, { flip: c.dir === 'left' });
}

/* ------------------------------------------------------------------ canards */
/* Canards sur l'étang, les mares et la rivière (MAP.ducks : [espèce, x, y, famille]). Ils nagent tranquillement près de
   leur place sans quitter l'eau profonde (duckWater), cancanent et plongent. Si Tecky approche ou aboie vers eux, les
   adultes s'envolent (avec leur ombre au sol) vers un autre coin d'eau, loin de Tecky et pas de son côté
   (pickLanding), et s'y posent. Une cane suivie de
   canetons (même famille) ne s'envole pas : elle s'éloigne vite à la nage, ses petits en file derrière elle. Points la
   première fois que chacun s'enfuit (scored, sauvegardé). */
const DUCK = { scare: 190, swim: 24, roam: 110, flee: 100, gap: 30, flyH: 90, fly: 230, rise: 0.7, away: 1.2,
  land: [300, 900], safe: 420, calm: 2.5, quack: [5, 14], dive: [10, 24], pts: 30 };
let ducks = [];
const DUCK_EDGE = { big: [[-28, 0], [28, 0], [0, -14], [0, 12], [-20, -10], [20, -10], [-20, 9], [20, 9]],
  small: [[-16, 0], [16, 0], [0, -9], [0, 8]] };
const duckWater = (d, x, y) => DUCK_EDGE[d.kind === 'duckling' ? 'small' : 'big'].every(([dx, dy]) => waterAt(x + dx, y + dy));
const rnd = ([a, b]) => a + Math.random() * (b - a);
const onScreen = (x, y) => x > camX - 60 && x < camX + VW + 60 && y > camY - 60 && y < camY + VH + 60;
function newDuck([kind, x, y, fam], id) {
  return { id, kind, fam, x, y, hx: x, hy: y, tx: x, ty: y, h: 0, mode: 'swim', anim: 'swim', t: Math.random() * 2,
    timer: Math.random() * 2, flip: Math.random() < 0.5, quackT: rnd(DUCK.quack), diveT: rnd(DUCK.dive), scored: false,
    lead: null, hasKids: false, vx: 0, vy: 0, calmT: 0 };
}
function linkDucks() {               // les canetons d'une famille se suivent en file derrière leur mère
  for (const m of ducks) if (m.kind === 'duck_f' && m.fam) {
    let prev = m;
    for (const k of ducks) if (k.kind === 'duckling' && k.fam === m.fam) { k.lead = prev; prev = k; m.hasKids = true; }
  }
}
const duckMom = d => d.lead ? ducks.find(m => m.hasKids && m.fam === d.fam) : d;
function duckAnim(d, a) { if (d.anim !== a) { d.anim = a; d.t = 0; } }
function duckFrame(d) {               // [image, fini ?] : les animations sans boucle (cancan, plongeon) se jouent une fois
  const fps = (MAP.duckFps[d.kind] || {})[d.anim] || 8, n = (ATLAS[d.kind + '/' + d.anim] || { f: [0] }).f.length;
  const i = Math.floor(d.t * fps);
  return MAP.duckLoop[d.kind][d.anim] ? [i, false] : [Math.min(i, n - 1), i >= n];
}
function scareDuck(d) {
  d = duckMom(d);
  if (!d || d.mode !== 'swim') return;
  if (d.hasKids) {
    d.mode = 'flee'; d.calmT = 0; duckAnim(d, 'swim');
    for (const k of ducks) if (k.lead && k.fam === d.fam) k.mode = 'flee';
  } else {
    const l = Math.max(1, dist(d.x, d.y, P.x, P.y)), p = pickLanding(d);
    d.mode = 'fly'; d.vx = (d.x - P.x) / l; d.vy = (d.y - P.y) / l;
    d.timer = p ? 0 : DUCK.away;                      // sans coin d'eau sûr : il s'éloigne un peu, puis revient
    [d.tx, d.ty] = p || [d.hx, d.hy];
    duckAnim(d, 'fly');
    if (onScreen(d.x, d.y)) SFX.flap();
  }
  if (!d.scored) { d.scored = true; score += DUCK.pts; addPop('+' + DUCK.pts, d.x - 20, d.y - 60); }
  addWordPop('Coin coin !', d.x, d.y - 80, 'duck');
  if (onScreen(d.x, d.y)) SFX.quack(d.kind === 'duck' ? 0.95 : 1.1);
}
function swimTo(d, tx, ty, sp, dt) {  // avance vers (tx, ty) sans quitter l'eau ; faux si la rive barre le chemin
  const dx = tx - d.x, dy = ty - d.y, l = Math.hypot(dx, dy);
  if (l < 1) return true;
  const st = Math.min(l, sp * dt), nx = d.x + dx / l * st, ny = d.y + dy / l * st;
  if (!duckWater(d, nx, ny)) return false;
  d.x = nx; d.y = ny;
  if (Math.abs(dx) > 1) d.flip = dx < 0;
  return true;
}
function pickLanding(d) {             // où se poser : de l'eau à bonne distance, loin de Tecky et pas de son côté
  const ok = [], away = [];
  for (let y = d.y - DUCK.land[1]; y <= d.y + DUCK.land[1]; y += 32) for (let x = d.x - DUCK.land[1]; x <= d.x + DUCK.land[1]; x += 32) {
    const l = dist(x, y, d.x, d.y);
    if (l < DUCK.land[0] || l > DUCK.land[1] || dist(x, y, P.x, P.y) < DUCK.safe || !duckWater(d, x, y)) continue;
    ok.push([x, y]);
    if ((x - d.x) * (d.x - P.x) + (y - d.y) * (d.y - P.y) > 0) away.push([x, y]);
  }
  const c = away.length ? away : ok;
  return c.length ? c[Math.floor(Math.random() * c.length)] : null;
}
function pickWater(d, cx, cy, r0, r1, far) {   // un point d'eau autour de (cx, cy), loin de Tecky si far
  for (let k = 0; k < 40; k++) {
    const a = Math.random() * Math.PI * 2, r = r0 + Math.random() * (r1 - r0);
    const x = cx + Math.cos(a) * r, y = cy + Math.sin(a) * r * 0.7;
    if (duckWater(d, x, y) && (!far || dist(x, y, P.x, P.y) > far)) return [x, y];
  }
  return null;
}
function duckChatter(d, dt, pitch) {  // cancans et plongeons de temps en temps
  if ((d.quackT -= dt) <= 0) {
    d.quackT = rnd(DUCK.quack) * (d.lead ? 0.6 : 1); duckAnim(d, 'quack');
    if (state === 'play' && onScreen(d.x, d.y)) SFX.quack(pitch);
  } else if (!d.lead && !d.hasKids && (d.diveT -= dt) <= 0) { d.diveT = rnd(DUCK.dive); duckAnim(d, 'dive'); }
}
function updateDuck(d, dt) {
  d.t += dt;
  if (d.anim !== 'swim' && d.anim !== 'fly' && duckFrame(d)[1]) duckAnim(d, 'swim');
  const dP = dist(d.x, d.y, P.x, P.y), alive = P.mode !== 'ko' && state === 'play';
  if (d.lead) {                       // caneton : suit celui qui le précède, à DUCK.gap
    const L = d.lead, dx = L.x - d.x, dy = L.y - d.y, l = Math.hypot(dx, dy);
    if (alive && dP < DUCK.scare * 0.8) scareDuck(d);
    if (l > DUCK.gap) swimTo(d, L.x - dx / l * DUCK.gap, L.y - dy / l * DUCK.gap, d.mode === 'flee' ? DUCK.flee * 1.15 : DUCK.swim * 1.8, dt);
    duckChatter(d, dt, 1.6);
    return;
  }
  switch (d.mode) {
    case 'swim':
      if (alive && dP < DUCK.scare) { scareDuck(d); return; }
      duckChatter(d, dt, d.kind === 'duck' ? 0.95 : 1.1);
      if (d.anim === 'dive') return;                    // la tête sous l'eau : il ne bouge pas
      if ((d.timer -= dt) <= 0 || dist(d.x, d.y, d.tx, d.ty) < 4) {
        const p = pickWater(d, d.hx, d.hy, 0, DUCK.roam);
        if (p) { d.tx = p[0]; d.ty = p[1]; }
        d.timer = 4 + Math.random() * 5;
      }
      if (!swimTo(d, d.tx, d.ty, DUCK.swim, dt)) d.timer = 0;
      return;
    case 'flee': {                    // la cane et ses petits s'éloignent à la nage
      let moved = false;
      const a0 = Math.atan2(d.y - P.y, d.x - P.x);
      for (const da of [0, 0.5, -0.5, 1, -1, 1.5, -1.5])
        if (swimTo(d, d.x + Math.cos(a0 + da) * 40, d.y + Math.sin(a0 + da) * 40, DUCK.flee, dt)) { moved = true; break; }
      d.calmT = dP > DUCK.scare + 120 || !moved ? d.calmT + dt : 0;
      if (d.calmT > DUCK.calm) {
        d.mode = 'swim'; d.hx = d.tx = d.x; d.hy = d.ty = d.y; d.timer = 2;
        for (const k of ducks) if (k.lead && k.fam === d.fam) k.mode = 'swim';
      }
      return;
    }
    case 'fly': {                     // s'envole, file vers son nouveau coin d'eau et s'y pose
      let dx = d.tx - d.x, dy = d.ty - d.y, l = Math.hypot(dx, dy);
      if (d.timer > 0) { d.timer -= dt; dx = d.vx; dy = d.vy; l = Infinity; }        // d'abord s'éloigner de Tecky
      const st = Math.min(l, DUCK.fly * dt), n = Math.hypot(dx, dy) || 1;
      d.x = clamp(d.x + dx / n * st, 40, MAP.w * TS - 40); d.y = clamp(d.y + dy / n * st, 160, MAP.h * TS - 40);
      if (Math.abs(dx) > 1) d.flip = dx < 0;
      d.h = Math.min(d.h + DUCK.flyH / DUCK.rise * dt, DUCK.flyH * Math.min(1, l / 180));   // monte, puis descend en arrivant
      if (l - st < 1) {
        d.h = 0; d.mode = 'swim'; d.hx = d.tx = d.x; d.hy = d.ty = d.y; d.timer = 2; duckAnim(d, 'swim');
        addFx(ATLAS['fx/splash'] ? 'fx/splash' : 'fx/ripple', d.x, d.y, { fps: 12 });
      }
      return;
    }
  }
}
function drawDuck(d) {
  drawSpr(d.kind + '/' + d.anim, duckFrame(d)[0], d.x, d.y - d.h, { flip: d.flip });
}

/* ------------------------------------------------------------------ quête des poules */
/* Le fermier Gaston a perdu ses poules : cinq (quest) se promènent hors de l'enclos (MAP.pen, barrière MAP.penGate au
   sud). Tecky les y ramène en aboyant derrière elles. Après chaque fuite, une poule reste où elle est arrivée : on la
   pousse petit à petit. Près de la barrière, sa fuite est guidée vers l'ouverture (funnelHen). Une fois dans l'enclos,
   elle y reste (keepHen). Le fermier ne parle que si Tecky vient le voir (C, « Parler », voir « personnages ») : il
   lui demande son aide, puis le remercie une fois toutes les poules rentrées (saucisse et points). Tout cela marche
   aussi en balade. */
const FARM = { reward: 200, perHen: 20, funnel: 190, roadY: MAP.farmRoadY };   // roadY : la grande route, en dessous
let farm = { state: 'new' };          // new (pas encore parlé) | asked | done
let farmer = null;
// intérieur de l'enclos (pieds des poules) : [x0, y0, x1, y1]
const penRect = () => [MAP.pen[0] + 14, MAP.pen[1] + 12, MAP.pen[2] - 14, MAP.pen[3] - 18];
const gatePoint = () => [(MAP.penGate[0] + MAP.penGate[1]) / 2, MAP.pen[3]];
const questHens = () => hens.filter(h => h.quest);
const hensLeft = () => questHens().filter(h => !h.penned).length;
function funnelHen(h) {
  const [gx, gy] = gatePoint();
  if (h.y < gy - 6 || dist(h.x, h.y, gx, gy) > FARM.funnel || h.vy > 0.2) return;
  // sous la barrière et poussée vers le haut : on l'aide à viser l'ouverture
  const tx = gx - h.x, ty = gy - 60 - h.y, tl = Math.hypot(tx, ty) || 1;
  const vx = h.vx * 0.35 + tx / tl * 0.65, vy = h.vy * 0.35 + ty / tl * 0.65, l = Math.hypot(vx, vy) || 1;
  h.vx = vx / l; h.vy = vy / l;
}
function keepHen(h) {
  if (!h.quest) return;
  if (h.penned) { const R = penRect(); h.x = clamp(h.x, R[0], R[2]); h.y = clamp(h.y, R[1], R[3]); return; }
  h.y = Math.min(h.y, FARM.roadY);                     // jamais sur la grande route
  const R = penRect();
  if (h.x > R[0] && h.x < R[2] && h.y > R[1] && h.y < R[3]) {
    h.penned = true; h.hx = h.x; h.hy = h.y;
    score += FARM.perHen;
    addPop('+' + FARM.perHen, h.x - 20, h.y - 70);
    addWordPop(hensLeft() ? 'Rentrée !' : 'Toutes rentrées !', h.x, h.y - 100, 'info');
    SFX.cluck();
    if (!hensLeft()) { farmer.waveT = 2.5; npcShout(farmer, farm.state === 'asked' ? 'Bravo ! Viens me voir !' : 'Oh ! Mes poules !'); }
  }
}
function newNpc(kind, [x, y], pitch) {
  solids.push([x - 16, y - 12, x + 16, y]);
  return { kind, x, y, t: 0, anim: 'idle', near: false, waveT: 0, cheerT: 0, pitch };
}
const newFarmer = () => newNpc('farmer', MAP.farmer, 0.8);
const farmThanks = () => [
  { who: 'farmer', face: 2, text: "Toutes mes poules sont rentrées ! Tu es un vrai chien de berger, Tecky." },
  { who: 'farmer', face: 0, text: "Tiens, voilà une bonne saucisse pour toi. Et bonne chance pour retrouver Alice !" },
];
function finishFarm() {
  farm.state = 'done';
  score += FARM.reward;
  addPop('+' + FARM.reward, P.x - 30, P.y - 140);
  items.push({ n: 'sausage', x: P.x + 40, y: P.y - 30, t: 0, pop: 0.001 });
  farmer.waveT = 3;
  saveGame();
}
function farmerMark() {          // « ! » : une demande, ou des remerciements à faire ; « ? » : quête en cours
  if (farm.state === 'done') return -1;
  return farm.state === 'asked' && hensLeft() ? 1 : 0;
}
function farmerGreet() {
  if (farm.state === 'new') npcShout(farmer, 'Hé, petit chien ! Par ici !');
  else if (farm.state === 'asked') {
    const n = hensLeft();
    npcShout(farmer, !n ? 'Bravo ! Viens me voir !' : 'Encore ' + n + (n > 1 ? ' poules !' : ' poule !'));
  } else { npcShout(farmer, 'Bonjour, Tecky !'); farmer.waveT = 1.5; }
}
function talkFarmer() {
  if (farm.state === 'done') {
    farmer.waveT = 2;
    say([{ who: 'farmer', face: 2, text: "Merci encore pour mes poules, Tecky ! Bonne chance pour retrouver Alice." }]);
    return;
  }
  if (!hensLeft()) { say(farmThanks(), finishFarm); return; }
  if (farm.state === 'asked') {
    const n = hensLeft();
    say([{ who: 'farmer', face: 0, text: n > 1
      ? `Il en reste ${n} dehors ! Aboie derrière elles pour les pousser vers la barrière ouverte, au sud de l'enclos.`
      : "Plus qu'une ! Aboie derrière elle pour la pousser vers la barrière ouverte, au sud de l'enclos." }]);
    return;
  }
  farm.state = 'asked';
  say([
    { who: 'farmer', face: 0, text: "Bonjour, petit teckel ! Une petite fille est passée par ici tout à l'heure… Mais pardon, mes poules se sont sauvées !" },
    { who: 'farmer', face: 0, text: "Tu voudrais bien les ramener dans l'enclos ? Aboie derrière elles pour les pousser vers la barrière ouverte, au sud." },
    { who: 'tecky', face: 2, text: "Ouaf ! Je m'en occupe !" },
  ], saveGame);
}
function updateNpcAnim(n, dt) {       // parle, se réjouit, salue, s'inquiète ou attend
  n.t += dt;
  n.waveT = Math.max(0, n.waveT - dt); n.cheerT = Math.max(0, n.cheerT - dt);
  const talking = state === 'dialog' && dialog && dialog.lines[dialog.i].who === n.kind;
  const a = talking ? 'talk' : n.cheerT > 0 && ATLAS[n.kind + '/cheer'] ? 'cheer' : n.waveT > 0 ? 'wave' :
    n.worried && ATLAS[n.kind + '/worry'] ? 'worry' : 'idle';
  if (a !== n.anim) { n.anim = a; n.t = 0; }
}
function updateFarmer(dt) {           // tous les personnages
  for (const n of npcList()) updateNpcAnim(n, dt);
  neighbor.worried = rose.state !== 'done' && pompon.mode !== 'home';
  leon.worried = ballsLeft() > 0;
  piquette.worried = babiesLeft() > 0;
}
function drawNpc(n) {
  const k = n.kind + '/' + n.anim;
  if (ATLAS[k]) drawSpr(k, Math.floor(n.t * ((MAP.npcFps[n.kind] || {})[n.anim] || 6)), n.x, n.y);
}

/* ------------------------------------------------------------------ personnages */
/* Les personnages ne parlent que si Tecky vient les voir et appuie sur C (« Parler », E aussi), comme dans un RPG.
   Au-dessus de leur tête, une bulle (hud/talk) : « ! » ils ont quelque chose à demander ou à donner, « ? » leur
   demande est en cours ; tout près, elle laisse la place à la bulle « Parler ». Quand Tecky arrive près d'eux, ils le
   saluent d'une petite exclamation (bulle de mots, sans bloquer le jeu). NPC_DO : par personnage, bulle (0 « ! »,
   1 « ? », -1 aucune), salut et conversation. */
const NPC = { talk: 150, markY: 150 };
const npcList = () => [farmer, postman, neighbor, leon, iris, piquette];
const NPC_DO = {
  farmer: { mark: farmerMark, greet: farmerGreet, talk: talkFarmer },
  postman: { mark: postmanMark, greet: postmanGreet, talk: talkPostman },
  neighbor: { mark: neighborMark, greet: neighborGreet, talk: talkNeighbor },
  leon: { mark: leonMark, greet: leonGreet, talk: talkLeon },
  iris: { mark: irisMark, greet: irisGreet, talk: talkIris },
  piquette: { mark: piquetteMark, greet: piquetteGreet, talk: talkPiquette },
};
const markY = n => n.markY || NPC.markY;            // hauteur de la bulle (Iris, assis, est plus petit)
function nearNpc() {
  let best = null, bd = NPC.talk;
  for (const n of npcList()) { const d = dist(P.x, P.y, n.x, n.y); if (d < bd) { best = n; bd = d; } }
  return best;
}
// une seule bulle à la fois par personnage : la nouvelle remplace celle qui est encore affichée
function npcShout(n, text) {
  pops = pops.filter(o => !(o.word && o.who === n.kind));
  addWordPop(text, n.x, n.y - markY(n) + 10, n.kind);
  if (n.woof) SFX.yip(n.pitch); else SFX.hey(n.pitch);
}
function talkTo(n) { P.dir = dirFrom(n.x - P.x, n.y - P.y, P.dir); P.setAnim('idle'); NPC_DO[n.kind].talk(); }
/* Petit salut quand Tecky arrive près d'un personnage. S'il lui ramène quelque chose (un jouet dans la gueule, Pompon
   ou des petits hérissons qui le suivent), le salut se tait : c'est l'arrivée qui fait parler le personnage. */
function updateNpcs() {
  const near = nearNpc();
  for (const n of npcList()) { if (n === near && !n.near) NPC_DO[n.kind].greet(); n.near = n === near; }
}

/* ------------------------------------------------------------------ le facteur */
/* Marcel, le facteur du village, a perdu ses lettres dans un coup de vent (MAP.letters : cinq lettres autour du
   village). Tecky les ramasse en passant dessus, même avant d'avoir parlé à Marcel ; quand il les a toutes, Marcel
   l'appelle et, quand Tecky vient lui parler, le remercie (un os et des points). Sauvegardé (post, letters). */
const POST = { reward: 150, pick: 54 };
let post = { state: 'new' }, postman = null, letters = [];
const lettersLeft = () => letters.filter(l => !l.got).length;
function updateLetters(dt) {
  for (const l of letters) {
    l.t += dt;
    if (l.got || dist(P.x, P.y, l.x, l.y + 20) > POST.pick || P.mode === 'ko') continue;
    l.got = true;
    const n = letters.length - lettersLeft();
    addWordPop(post.state === 'new' ? 'Une lettre ?' : 'Une lettre ! (' + n + '/' + letters.length + ')', l.x, l.y - 70, 'tecky');
    SFX.pick();
    if (!lettersLeft()) { postman.waveT = 2.5; if (post.state === 'asked') npcShout(postman, 'Mes lettres ! Viens vite !'); }
  }
}
function postmanMark() { return post.state === 'done' ? -1 : post.state === 'asked' && lettersLeft() ? 1 : 0; }
function postmanGreet() {
  if (post.state === 'new') npcShout(postman, 'Oh là là, mes lettres !');
  else if (post.state === 'asked') {
    const n = lettersLeft();
    npcShout(postman, !n ? 'Mes lettres ! Merci !' : 'Encore ' + n + (n > 1 ? ' lettres !' : ' lettre !'));
  } else { npcShout(postman, 'Bonne journée, Tecky !'); postman.waveT = 1.5; }
}
const postThanks = () => [
  { who: 'postman', face: 2, text: "Toutes mes lettres ! Merci, Tecky : tout le monde va enfin recevoir son courrier." },
  { who: 'postman', face: 0, text: "Tiens, un bel os pour la peine. Et si je croise ta petite Alice, je lui dis que tu la cherches !" },
];
function finishPost() {
  post.state = 'done'; score += POST.reward;
  addPop('+' + POST.reward, P.x - 30, P.y - 140);
  items.push({ n: 'bone', x: P.x + 40, y: P.y - 30, t: 0, pop: 0.001 });
  postman.cheerT = 3;
  saveGame();
}
function talkPostman() {
  if (post.state === 'done') {
    postman.waveT = 2;
    say([{ who: 'postman', face: 2, text: "Grâce à toi, la tournée est finie à l'heure ! Bonne chance pour retrouver Alice." }]);
    return;
  }
  if (!lettersLeft()) { post.state = 'asked'; say(postThanks(), finishPost); return; }
  if (post.state === 'asked') {
    const n = lettersLeft();
    say([{ who: 'postman', face: 0, text: (n > 1 ? `Il m'en manque encore ${n}.` : "Plus qu'une !") +
      " Le vent les a emportées un peu partout : dans le village, dans la campagne, et même vers les entrepôts." }]);
    return;
  }
  post.state = 'asked';
  const got = letters.length - lettersLeft();
  say([
    { who: 'postman', face: 3, text: "Bonjour, petit chien ! Un coup de vent a fait s'envoler mes lettres, juste au début de ma tournée…" },
    { who: 'postman', face: 0, text: got ? `Tu en as déjà trouvé ${got} ? Bravo ! Il y en a cinq en tout, autour du village. Rapporte-les-moi, s'il te plaît !`
      : "Il y en a cinq, dans le village et autour. Si tu les trouves, rapporte-les-moi, s'il te plaît !" },
    { who: 'tecky', face: 2, text: "Ouaf ! Je vais les chercher !" },
  ], saveGame);
}

/* ------------------------------------------------------------------ la voisine et son chat */
/* Mamie Rose (devant sa maison, au village) a perdu son chat Pompon (cat_white, collier rose), caché près des entrepôts
   (MAP.pompon). Une fois que Tecky lui a parlé, Pompon le suit quand il le retrouve (sur ses traces, comme les copains
   en balade, terriers compris) ; trop loin, il s'assoit et attend. Arrivé près de Mamie Rose, il reste avec elle, et
   elle remercie Tecky quand il vient lui parler (une saucisse et des points). Un aboiement le fait feuler. Sauvegardé
   (rose, cat). */
const CAT = { find: 130, gap: 70, walk: 150, run: 330, lost: 700, home: 280, meow: [2.5, 5] };
let rose = { state: 'new' }, neighbor = null, pompon = null;
function newPompon() {
  const [x, y] = MAP.pompon;
  return { kind: 'cat_white', x, y, mode: 'lost', anim: 'idle', t: 0, dir: 'left', meowT: 1, hissT: 0 };
}
function catAnim(c, a) { if (c.anim !== a) { c.anim = a; c.t = 0; } }
function catMove(c, tx, ty, dt) {      // va vers (tx, ty), d'autant plus vite que c'est loin (il court pour rattraper Tecky)
  const dx = tx - c.x, dy = ty - c.y, l = Math.hypot(dx, dy);
  if (l < 10) { catAnim(c, 'idle'); return; }
  const sp = clamp(l * 3, CAT.walk * 0.6, CAT.run), st = Math.min(l, sp * dt);
  c.x += dx / l * st; c.y += dy / l * st; c.dir = dx < 0 ? 'left' : 'right';
  catAnim(c, sp > 220 ? 'run' : 'walk');
}
function updatePompon(dt) {
  const c = pompon, dP = dist(c.x, c.y, P.x, P.y);
  c.t += dt;
  if (c.hissT > 0) { c.hissT -= dt; catAnim(c, 'hiss'); return; }
  switch (c.mode) {
    case 'lost':
    case 'wait':
      catAnim(c, 'idle');
      if (dP < 300) c.dir = P.x < c.x ? 'left' : 'right';
      if (dP < CAT.find && rose.state === 'asked') {
        if (c.mode === 'lost') say([{ who: 'tecky', face: 2, text: "Te voilà, Pompon ! Viens, on rentre chez Mamie Rose." }]);
        c.mode = 'follow'; addWordPop('Miaou !', c.x, c.y - 70, 'cat');
      } else if (dP < 260 && (c.meowT -= dt) <= 0) { c.meowT = rnd(CAT.meow); addWordPop(c.mode === 'lost' ? 'Miaou ?' : 'Miaou !', c.x, c.y - 70, 'cat'); }
      return;
    case 'follow': {
      const [tx, ty] = crumbAt(CAT.gap);
      catMove(c, tx, ty, dt);
      if (dist(c.x, c.y, neighbor.x, neighbor.y) < CAT.home) {
        c.mode = 'home'; neighbor.cheerT = 3;
        npcShout(neighbor, 'Pompon ! Viens me voir, Tecky !');
        saveGame();
      } else if (dP > CAT.lost) { c.mode = 'wait'; addWordPop('Miaou !', c.x, c.y - 70, 'cat'); }
      return;
    }
    case 'home':                       // près de Mamie Rose, à côté de ses chaussons
      catMove(c, neighbor.x + 56, neighbor.y + 18, dt);
      if (c.anim === 'idle') c.dir = 'left';
      return;
  }
}
function drawPompon() {
  const c = pompon, fps = (MAP.critterFps.cat_white || {})[c.anim] || 8;
  drawSpr('cat_white/' + c.anim, Math.floor(c.t * fps), c.x, c.y, { flip: c.dir === 'left' });
}
function neighborMark() { return rose.state === 'done' ? -1 : rose.state === 'asked' && pompon.mode !== 'home' ? 1 : 0; }
function neighborGreet() {
  if (rose.state === 'new') npcShout(neighbor, 'Pompon ? Pompon, où es-tu ?');
  else if (rose.state === 'asked') { if (pompon.mode !== 'follow') npcShout(neighbor, pompon.mode === 'home' ? 'Mon Pompon est là !' : 'Tu as vu Pompon ?'); }
  else { npcShout(neighbor, 'Bonjour, Tecky !'); neighbor.waveT = 1.5; }
}
const nbThanks = () => [
  { who: 'neighbor', face: 2, text: "Pompon ! Te voilà enfin, mon chaton ! J'étais si inquiète…" },
  { who: 'neighbor', face: 0, text: "Merci, Tecky ! Tiens, une bonne saucisse : tu l'as bien méritée." },
];
function finishNeighbor() {
  rose.state = 'done'; score += POST.reward;
  addPop('+' + POST.reward, P.x - 30, P.y - 140);
  items.push({ n: 'sausage', x: P.x + 40, y: P.y - 30, t: 0, pop: 0.001 });
  neighbor.cheerT = 3;
  saveGame();
}
function talkNeighbor() {
  if (rose.state === 'done') {
    neighbor.waveT = 2;
    say([{ who: 'neighbor', face: 2, text: "Pompon ne quitte plus le jardin, grâce à toi. Bonne chance pour retrouver ta petite Alice !" }]);
    return;
  }
  if (pompon.mode === 'home') { say(nbThanks(), finishNeighbor); return; }
  if (rose.state === 'asked') {
    say([{ who: 'neighbor', face: 3, text: pompon.mode === 'follow' || pompon.mode === 'wait'
      ? "Tu l'as trouvé ! Ramène-le-moi : il te suivra si tu ne vas pas trop vite."
      : "Pompon adore se cacher près des entrepôts, de l'autre côté de la grande route. Attention aux voitures !" }]);
    return;
  }
  rose.state = 'asked';
  say([
    { who: 'neighbor', face: 3, text: "Bonjour, mon petit. Tu n'aurais pas vu mon chat, Pompon ? Il est tout blanc, avec un collier rose et un grelot." },
    { who: 'neighbor', face: 0, text: "Il s'est sauvé ce matin… Il adore se cacher près des entrepôts, de l'autre côté de la grande route." },
    { who: 'tecky', face: 2, text: "Ouaf ! Je te le ramène !" },
  ], saveGame);
}

/* ------------------------------------------------------------------ Léon et ses ballons */
/* Léon, le cariste du port, devait livrer cinq gros ballons pour la fête du parc ; le carton s'est ouvert et ils ont
   roulé partout dans la zone industrielle (MAP.balls). Tecky les pousse en fonçant dedans (dans le sens où il va) ou en
   aboyant derrière (cône de l'aboiement) : ils roulent, rebondissent sur les obstacles, et près de l'ouverture du filet
   (MAP.goal, décor goal_net), leur course est guidée vers lui (funnelBall). Un ballon dans le filet y reste. Comme les
   autres personnages, Léon ne parle que si Tecky vient le voir : il demande, rappelle, remercie (un os et des points).
   Tout marche aussi avant de lui avoir parlé, et en balade. Sauvegardé (fete, balls). */
const BALL = { r: 26, touch: 44, kick: 330, bark: 470, fric: 1.6, bounce: 0.55, hop: 150, g: 1200, cd: 0.2, funnel: 240,
  box: MAP.ballBox };            // box : la zone industrielle, en tuiles (jamais hors du grillage du dépôt ; carte.json)
const GOAL_IN = [50, -46, -8];                 // intérieur du filet (pied du ballon) : |dx| < 50, -46 < dy < -8
const LEON = { reward: 150, perBall: 20 };
let fete = { state: 'new' }, leon = null, balls = [];
const ballsLeft = () => balls.filter(b => !b.inNet).length;
function newBall([x, y], i) { return { i, x, y, vx: 0, vy: 0, z: 0, vz: 0, rot: 0, cd: 0, inNet: false }; }
// pousse le ballon loin de (fx, fy) ; ahead : direction où va Tecky, qui oriente un peu le tir (on dribble)
function kickBall(b, fx, fy, speed, ahead) {
  if (b.inNet) return;
  let dx = b.x - fx, dy = b.y - fy, l = Math.hypot(dx, dy) || 1;
  dx /= l; dy /= l;
  if (ahead) {
    const [ax, ay] = DIRV[ahead];
    if (dx * ax + dy * ay > 0) { dx = dx * 0.5 + ax * 0.5; dy = dy * 0.5 + ay * 0.5; l = Math.hypot(dx, dy) || 1; dx /= l; dy /= l; }
  }
  b.vx = dx * speed; b.vy = dy * speed; b.vz = BALL.hop; b.cd = BALL.cd;
  funnelBall(b);
  if (!muted) SFX.boing();
}
// devant l'ouverture du filet, un ballon qui monte vers lui est guidé vers le milieu (comme les poules et la barrière) :
// au tir, puis à chaque image tant qu'il roule
function funnelBall(b) {
  const [gx, gy] = MAP.goal, sp = Math.hypot(b.vx, b.vy);
  if (!sp || b.vy > -sp * 0.2 || b.y < gy - 20 || dist(b.x, b.y, gx, gy) > BALL.funnel) return;
  const tx = gx - b.x, ty = gy - 30 - b.y, tl = Math.hypot(tx, ty) || 1;
  const vx = b.vx / sp * 0.35 + tx / tl * 0.65, vy = b.vy / sp * 0.35 + ty / tl * 0.65, l = Math.hypot(vx, vy) || 1;
  b.vx = vx / l * sp; b.vy = vy / l * sp;
}
function ballBlocked(b, x, y) {
  const B = BALL.box, [gx, gy] = MAP.goal;
  if (x < B[0] * TS || x > B[2] * TS || y < B[1] * TS || y > B[3] * TS) return true;
  if (b.inNet && (Math.abs(x - gx) > GOAL_IN[0] + 8 || y < gy + GOAL_IN[1] || y > gy + GOAL_IN[2])) return true;
  return blockedFeet(x, y, 12);
}
function moveBall(b, dx, dy) {           // un obstacle le renvoie (moins vite)
  if (!ballBlocked(b, b.x + dx, b.y)) b.x += dx; else b.vx = -b.vx * BALL.bounce;
  if (!ballBlocked(b, b.x, b.y + dy)) b.y += dy; else b.vy = -b.vy * BALL.bounce;
}
function checkGoal(b) {
  const [gx, gy] = MAP.goal, dx = b.x - gx, dy = b.y - gy;
  if (Math.abs(dx) >= GOAL_IN[0] || dy <= GOAL_IN[1] || dy >= GOAL_IN[2]) return;
  b.inNet = true; b.vx *= 0.4; b.vy *= 0.4;
  score += LEON.perBall;
  addPop('+' + LEON.perBall, b.x - 20, b.y - 80);
  addWordPop(ballsLeft() ? 'But !' : 'Tous dans le filet !', b.x, b.y - 110, 'info');
  if (!muted) SFX.goal();
  if (!ballsLeft()) { leon.cheerT = 3; npcShout(leon, fete.state === 'asked' ? 'Bravo, champion ! Viens me voir !' : 'Mes ballons !'); }
}
function updateBall(b, dt) {
  b.cd = Math.max(0, b.cd - dt);
  if (b.z > 0 || b.vz > 0) {                     // petits rebonds
    b.vz -= BALL.g * dt; b.z += b.vz * dt;
    if (b.z <= 0) { b.z = 0; b.vz = b.vz < -160 ? -b.vz * 0.4 : 0; }
  }
  if (!b.inNet && b.cd <= 0 && P.mode !== 'ko' && P.alpha !== 0 && dist(b.x, b.y, P.x, P.y) < BALL.touch)
    kickBall(b, P.x, P.y, BALL.kick, P.anim === 'walk' ? P.dir : null);
  const k = Math.exp(-BALL.fric * dt);
  b.vx *= k; b.vy *= k;
  const sp = Math.hypot(b.vx, b.vy);
  if (sp < 8) { b.vx = b.vy = 0; return; }
  if (!b.inNet) funnelBall(b);                 // tant qu'il roule vers l'ouverture, il est guidé
  moveBall(b, b.vx * dt, b.vy * dt);
  b.rot += (b.vx >= 0 ? 1 : -1) * sp * dt / BALL.r;
  if (!b.inNet) checkGoal(b);
}
function drawBall(b) {
  ctx.save();
  ctx.globalAlpha = 0.22 * Math.max(0.4, 1 - b.z / 120); ctx.fillStyle = '#000';
  ctx.beginPath(); ctx.ellipse(b.x, b.y - 2, 22, 7, 0, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
  drawSpr('port/balloon', b.i, b.x, b.y - BALL.r - b.z, { angle: b.rot });
}
function leonMark() { return fete.state === 'done' ? -1 : fete.state === 'asked' && ballsLeft() ? 1 : 0; }
function leonGreet() {
  if (fete.state === 'new') npcShout(leon, 'Oh non, mes ballons !');
  else if (fete.state === 'asked') {
    const n = ballsLeft();
    npcShout(leon, !n ? 'Bravo, champion ! Viens me voir !' : 'Encore ' + n + (n > 1 ? ' ballons !' : ' ballon !'));
  } else { npcShout(leon, 'Salut, champion !'); leon.waveT = 1.5; }
}
const leonThanks = () => [
  { who: 'leon', face: 2, text: "Cinq buts ! Tous mes ballons sont dans le filet. Bravo, champion !" },
  { who: 'leon', face: 0, text: "Tiens, un bon os pour toi. Et si tu croises une petite fille, dis-lui qu'il y aura des ballons à la fête du parc !" },
];
function finishLeon() {
  fete.state = 'done'; score += LEON.reward;
  addPop('+' + LEON.reward, P.x - 30, P.y - 140);
  items.push({ n: 'bone', x: P.x + 40, y: P.y - 30, t: 0, pop: 0.001 });
  leon.cheerT = 3;
  saveGame();
}
function talkLeon() {
  if (fete.state === 'done') {
    leon.waveT = 2;
    say([{ who: 'leon', face: 2, text: "Merci encore, champion ! Mes ballons seront prêts pour la fête du parc." }]);
    return;
  }
  if (!ballsLeft()) { fete.state = 'asked'; say(leonThanks(), finishLeon); return; }
  if (fete.state === 'asked') {
    const n = ballsLeft();
    say([{ who: 'leon', face: 0, text: (n > 1 ? `Il en reste ${n} !` : "Plus qu'un !") +
      " Pousse-les dans le grand filet, à côté de moi : fonce dedans, ou aboie derrière eux." }]);
    return;
  }
  fete.state = 'asked';
  say([
    { who: 'leon', face: 3, text: "Salut, petit chien ! Je devais livrer ces gros ballons pour la fête du parc… mais le carton s'est ouvert, et ils ont roulé partout !" },
    { who: 'leon', face: 0, text: "Tu veux bien les pousser dans le grand filet, à côté de moi ? Fonce dedans, ou aboie derrière eux : comme au foot !" },
    { who: 'tecky', face: 2, text: "Ouaf ! Je vais marquer des buts !" },
  ], saveGame);
}

/* ------------------------------------------------------------------ Iris et ses jouets */
/* Iris, le vieux Jack Russell, ami et mentor de Tecky (un personnage, pas un chien de `dogs`), vit au verger, sur son
   panier. Pour entraîner Tecky, il a caché ses trois jouets (MAP.toys : canard, anneau, corde ; port.py) dans les prés de
   la ferme. Tecky en prend un dans la gueule en passant dessus (un seul à la fois : `carried`), le lâche devant lui s'il
   aboie ou mord, ou s'il est KO, et le donne à Iris en arrivant près de lui (IRIS.give) : le jouet reste à côté d'Iris,
   qui remue la queue. Comme les autres personnages, Iris ne parle que si Tecky vient le voir : il demande, rappelle,
   remercie (une saucisse et des points), puis donne un conseil de vieux chien à chaque visite (IRIS_TIPS, iris.tip).
   Tout marche aussi avant de lui avoir parlé. Sauvegardé (jouets, toys ; un jouet porté l'est par terre, aux pieds de
   Tecky). */
const IRIS_TIPS = [
  () => "Un conseil de vieux chien : quand tu ne sais plus où aller, fais confiance à ta truffe. " +
    (touchMode ? 'Touche le bouton à truffe' : 'Appuie sur [sniff]') + ", et suis la piste !",
  () => "Un chien te cherche des ennuis ? Un bon aboiement " + (touchMode ? '' : '[bark] ') + "et il recule. " +
    "Sauf le doberman : celui-là, il faut le mordre " + (touchMode ? '!' : '[bite] !'),
  () => "Les trous sous les grillages, ce sont des terriers : un vrai raccourci de teckel ! Approche-toi, et " +
    (touchMode ? 'touche « Passer ».' : 'appuie sur [bite].'),
  () => "Pour traverser la grande route, prends les passages piétons : les voitures s'y arrêtent toujours.",
  () => "Tu es fatigué ? Les os te redonnent des forces, et une saucisse, encore plus. Ouvre l'œil, il y en a partout !",
];
const IRIS = { reward: 150, perToy: 20, pick: 54, give: 110, markY: 90, home: [[-46, 10], [46, 12], [-22, 28]],
  regrab: 1.2 };     // regrab : un jouet lâché ne se reprend pas tout de suite (Tecky est juste à côté)
const TOY_NAMES = ['Le canard d’Iris !', 'L’anneau d’Iris !', 'La corde d’Iris !'];
const MOUTH = { right: [38, -40], left: [-38, -40], up: [0, -78], down: [0, -22] };   // gueule de Tecky (jouet porté)
let jouets = { state: 'new' }, iris = null, toys = [];
const toysLeft = () => toys.filter(t => !t.home).length;
const carried = () => toys.find(t => t.carried);
function newToy([x, y], i) { return { i, x, y, home: false, carried: false, t: Math.random() * 2, cd: 0 }; }
function dropToy(word) {
  const t = carried();
  if (!t) return;
  t.carried = false; t.cd = IRIS.regrab;
  t.x = P.x + MOUTH[P.dir][0] * 0.8; t.y = P.y + (P.dir === 'up' ? -28 : P.dir === 'down' ? 26 : 6);
  if (blockedFeet(t.x, t.y, 8)) { t.x = P.x; t.y = P.y; }     // jamais dans l'eau ni dans un obstacle
  if (word) addWordPop(word, P.x, P.y - 120, 'tecky');
}
function giveToy(t) {
  const [hx, hy] = IRIS.home[toys.filter(o => o.home).length];
  t.carried = false; t.home = true; t.x = iris.x + hx; t.y = iris.y + hy;
  score += IRIS.perToy;
  addPop('+' + IRIS.perToy, iris.x - 20, iris.y - 120);
  iris.cheerT = 2.2;
  const left = toysLeft();
  npcShout(iris, left ? (jouets.state === 'asked' ? 'Bravo ! Encore ' + left + ' !' : 'Tiens, mon jouet !')
    : jouets.state === 'asked' ? 'Tous mes jouets ! Viens me voir !' : 'Mes jouets ! Bravo !');
}
function updateToys(dt) {
  for (const t of toys) { t.t += dt; t.cd = Math.max(0, t.cd - dt); }
  const c = carried();
  if (c) {
    if (P.mode === 'ko') dropToy();
    else if (dist(P.x, P.y, iris.x, iris.y) < IRIS.give) giveToy(c);
    return;
  }
  if (P.mode === 'ko' || P.alpha === 0) return;
  for (const t of toys) {
    if (t.home || t.cd > 0 || dist(P.x, P.y, t.x, t.y) > IRIS.pick) continue;
    t.carried = true;
    addWordPop(jouets.state === 'new' ? 'Un jouet ?' : TOY_NAMES[t.i], P.x, P.y - 120, 'tecky');
    SFX.pick();
    break;
  }
}
function drawToy(t) {
  if (t.carried) {
    if (P.alpha === 0) return;
    const [mx, my] = MOUTH[P.dir];
    drawSpr('port/toy', t.i, P.x + mx, P.y + my, { sc: 0.7, flip: P.dir === 'right' });
    return;
  }
  ctx.save(); ctx.globalAlpha = 0.18; ctx.fillStyle = '#000';
  ctx.beginPath(); ctx.ellipse(t.x, t.y, 15, 5, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  const bob = t.home ? 0 : Math.sin(t.t * 3) * 2;
  drawSpr('port/toy', t.i, t.x, t.y - 16 + bob, { sc: 0.85 });
}
function irisMark() { return jouets.state === 'done' ? -1 : jouets.state === 'asked' && toysLeft() ? 1 : 0; }
function irisGreet() {
  if (carried()) return;                 // il lui rapporte un jouet : giveToy() parle
  if (jouets.state === 'new') npcShout(iris, 'Salut, mon petit Tecky !');
  else if (jouets.state === 'asked') {
    const n = toysLeft();
    npcShout(iris, !n ? 'Tous mes jouets ! Viens me voir !' : 'Encore ' + n + (n > 1 ? ' jouets !' : ' jouet !'));
  } else { npcShout(iris, 'Bonne chasse, Tecky !'); iris.waveT = 1.5; }
}
const irisThanks = () => [
  { who: 'iris', face: 2, text: "Mes trois jouets ! Bravo, Tecky : quelle truffe ! Je n'aurais pas fait mieux à ton âge." },
  { who: 'iris', face: 0, text: "Tiens, une bonne saucisse pour la route. Reviens me voir quand tu veux : j'ai toujours un conseil pour toi." },
];
function finishIris() {
  jouets.state = 'done'; score += IRIS.reward;
  addPop('+' + IRIS.reward, P.x - 30, P.y - 140);
  items.push({ n: 'sausage', x: P.x + 40, y: P.y - 30, t: 0, pop: 0.001 });
  iris.cheerT = 3;
  saveGame();
}
function talkIris() {
  if (jouets.state === 'done') {            // un conseil de vieux chien à chaque visite, à tour de rôle
    iris.waveT = 2;
    say([{ who: 'iris', face: 0, text: IRIS_TIPS[iris.tip++ % IRIS_TIPS.length]() }]);
    return;
  }
  if (!toysLeft()) { jouets.state = 'asked'; say(irisThanks(), finishIris); return; }
  if (jouets.state === 'asked') {
    const n = toysLeft();
    say([{ who: 'iris', face: 0, text: (n > 1 ? `Encore ${n} à trouver, mon petit.` : "Plus qu'un !") +
      " Ils sont dans les prés de la ferme. Et n'oublie pas : si tu aboies, tu les lâches !" }]);
    return;
  }
  jouets.state = 'asked';
  say([
    { who: 'iris', face: 2, text: "Tiens, mon petit Tecky ! Ça me fait plaisir de te voir. Alors, tu cherches ta petite Alice ?" },
    { who: 'tecky', face: 0, text: "Ouaf ! Iris ! Elle joue à cache-cache, et je ne la trouve pas…" },
    { who: 'iris', face: 0, text: "Un bon chien ne perd jamais une piste. Pour t'entraîner, j'ai caché mes trois jouets dans les prés de la ferme : mon canard, mon anneau et ma corde." },
    { who: 'iris', face: 0, text: "Rapporte-les-moi un par un, dans ta gueule. Attention : si tu aboies, tu les lâches !" },
    { who: 'tecky', face: 2, text: "Ouaf ! « Va chercher », c'est mon jeu préféré !" },
  ], saveGame);
}

/* ------------------------------------------------------------------ les villageois */
/* Des habitants du village, sans quête (MAP.villagers : [qui, x, y] ; villageois.py) : Bernard le boulanger à la porte de
   sa boutique, Josette la marchande de fruits et Lili la fleuriste à côté de leurs étals, Lucas et son ballon près de la
   fontaine. Quand Tecky arrive près d'eux (VILLAGER.near), ils le saluent d'une bulle (une phrase après l'autre,
   VILLAGER_LINES ; pas plus d'une fois toutes les VILLAGER.again s) et de la main (Lucas sautille). On ne leur parle
   pas : ni « ! » ni « Parler » (ils ne sont pas dans npcList). Obstacles, comme les personnages. Rien n'est sauvegardé. */
const VILLAGER = { near: 170, again: 10, wave: 1.8, markY: 150, kidMarkY: 112 };
const VILLAGER_LINES = {
  baker: ['Bonjour, Tecky !', 'Ça sent bon le pain chaud !'],
  vendor: ['Des belles pommes !', 'Tout frais, tout beau !'],
  florist: ['Coucou, Tecky !', 'Une jolie fleur ?'],
  kid: ['Un toutou !', 'Regarde mon ballon !'],
};
const VILLAGER_PITCH = { baker: 0.85, vendor: 1.15, florist: 1.35, kid: 1.7 };
let villagers = [];
function newVillager([kind, x, y]) {
  solids.push([x - 16, y - 12, x + 16, y]);
  return { kind, x, y, t: Math.random() * 2, anim: 'idle', near: false, cd: 0, i: 0, waveT: 0 };
}
function updateVillager(v, dt) {
  v.t += dt; v.cd = Math.max(0, v.cd - dt);
  const near = P.mode !== 'ko' && dist(P.x, P.y, v.x, v.y) < VILLAGER.near;
  if (near && !v.near && v.cd <= 0) {
    const lines = VILLAGER_LINES[v.kind];
    addWordPop(lines[v.i++ % lines.length], v.x, v.y - (v.kind === 'kid' ? VILLAGER.kidMarkY : VILLAGER.markY) + 10, v.kind);
    SFX.hey(VILLAGER_PITCH[v.kind]);
    v.waveT = VILLAGER.wave; v.cd = VILLAGER.again;
  }
  v.near = near;
  v.waveT = Math.max(0, v.waveT - dt);
  const a = v.waveT > 0 ? (v.kind === 'kid' ? 'hop' : 'wave') : 'idle';
  if (a !== v.anim) { v.anim = a; v.t = 0; }
}
function drawVillager(v) {
  drawSpr(v.kind + '/' + v.anim, Math.floor(v.t * MAP.villagerFps[v.kind][v.anim]), v.x, v.y);
}

/* ------------------------------------------------------------------ Maman Piquette et ses petits */
/* Maman Piquette, la maman hérisson de la clairière de la forêt (MAP.piquette, zone calme), a perdu ses trois petits :
   ils jouaient à cache-cache sous les fougères (MAP.babies, herissons.py). Une fois qu'elle a demandé de l'aide, un
   petit que Tecky trouve (BABY.find) le suit sur ses traces, en file indienne derrière les autres (dans l'ordre où ils
   ont été trouvés, après Pompon s'il suit aussi : crumbAt), attend s'il va trop vite (BABY.lost) et reste près de sa
   maman en arrivant (babyHome, BABY.home). Un aboiement le fait se rouler en boule un instant. Caché, il pousse un
   petit « Couic ? » quand Tecky passe près. Elle remercie : un os et des points. Sauvegardé (piq, babies). */
const BABY = { find: 110, gap: 60, lost: 650, home: 170, walk: 110, run: 300, ball: 1.4, squeak: [2.5, 5], markY: 100, call: 0.7,
  slots: [[-46, 16], [46, 18], [-14, 34]] };
let piq = { state: 'new' }, piquette = null, babies = [], babySeq = 0;
const babiesLeft = () => babies.filter(b => b.mode !== 'home').length;
function newBaby([x, y], i) {
  return { i, x, y, mode: 'hidden', anim: 'idle', t: Math.random() * 2, dir: 'left', ballT: 0, squeakT: 1, seq: 0, slot: 0 };
}
function babyAnim(b, a) { if (b.anim !== a) { b.anim = a; b.t = 0; } }
function babyMove(b, tx, ty, dt) {     // comme Pompon : d'autant plus vite que c'est loin
  const dx = tx - b.x, dy = ty - b.y, l = Math.hypot(dx, dy);
  if (l < 8) { babyAnim(b, 'idle'); return; }
  const sp = clamp(l * 3, BABY.walk * 0.6, BABY.run), st = Math.min(l, sp * dt);
  b.x += dx / l * st; b.y += dy / l * st; b.dir = dx < 0 ? 'left' : 'right';
  babyAnim(b, 'walk');
}
// un petit arrive chez sa maman ; ceux qui arrivent ensemble n'ont droit qu'à un cri (BABY.call s après le dernier)
function babyHome(b) {
  b.mode = 'home'; b.slot = babies.filter(o => o.mode === 'home' && o !== b).length;
  piquette.cheerT = 2.5; piquette.got = (piquette.got || 0) + 1; piquette.callT = BABY.call;
  saveGame();
}
function piquetteCall() {
  const left = babiesLeft(), k = piquette.got;
  piquette.got = 0; piquette.callT = 0;
  npcShout(piquette, left ? (k > 1 ? 'Mes petits ! Encore ' : 'Mon petit ! Encore ') + left + ' !'
    : piq.state === 'asked' ? 'Tous mes petits ! Viens me voir !' : 'Mes petits !');
}
function updateBaby(b, dt) {
  const dP = dist(b.x, b.y, P.x, P.y);
  b.t += dt;
  if (b.ballT > 0) { b.ballT -= dt; babyAnim(b, 'ball'); return; }
  switch (b.mode) {
    case 'hidden':
    case 'wait':
      babyAnim(b, 'idle');
      if (dP < 300) b.dir = P.x < b.x ? 'left' : 'right';
      if (dP < BABY.find && piq.state === 'asked' && P.alpha !== 0) {
        b.mode = 'follow'; b.seq = ++babySeq; addWordPop('Couic !', b.x, b.y - 50, 'hedgehog');
      } else if (dP < 240 && (b.squeakT -= dt) <= 0) {
        b.squeakT = rnd(BABY.squeak); addWordPop(b.mode === 'hidden' ? 'Couic ?' : 'Couic !', b.x, b.y - 50, 'hedgehog');
      }
      return;
    case 'follow': {          // en file indienne, derrière Pompon et les petits trouvés avant lui
      const rank = babies.filter(o => o.mode === 'follow' && o.seq < b.seq).length;
      const [tx, ty] = crumbAt(BABY.gap * (rank + 1) + (pompon.mode === 'follow' ? CAT.gap : 0));
      babyMove(b, tx, ty, dt);
      if (dist(b.x, b.y, piquette.x, piquette.y) < BABY.home) babyHome(b);
      else if (dP > BABY.lost) { b.mode = 'wait'; addWordPop('Couic !', b.x, b.y - 50, 'hedgehog'); }
      return;
    }
    case 'home': {            // blotti contre sa maman, tourné vers elle
      const [sx, sy] = BABY.slots[b.slot];
      babyMove(b, piquette.x + sx, piquette.y + sy, dt);
      if (b.anim === 'idle') b.dir = sx < 0 ? 'right' : 'left';
      return;
    }
  }
}
function drawBaby(b) {
  drawSpr('hedgehog/' + b.anim, Math.floor(b.t * (MAP.babyFps[b.anim] || 6)), b.x, b.y, { flip: b.dir === 'left' });
}
function piquetteMark() { return piq.state === 'done' ? -1 : piq.state === 'asked' && babiesLeft() ? 1 : 0; }
function piquetteGreet() {
  if (babies.some(b => b.mode === 'follow')) return;      // ses petits arrivent : piquetteCall() parle
  if (piq.state === 'new') npcShout(piquette, 'Mes petits ! Où êtes-vous ?');
  else if (piq.state === 'asked') {
    const n = babiesLeft();
    npcShout(piquette, !n ? 'Tous mes petits ! Viens me voir !' : 'Encore ' + n + (n > 1 ? ' petits !' : ' petit !'));
  } else { npcShout(piquette, 'Bonjour, Tecky !'); piquette.waveT = 1.5; }
}
const piquetteThanks = () => [
  { who: 'piquette', face: 2, text: "Mes trois petits ! Merci, gentil teckel. Ils ont bien joué, mais maintenant, c'est l'heure de la sieste !" },
  { who: 'piquette', face: 0, text: "Tiens, un bon os que j'ai trouvé sous les feuilles. Et bonne chance pour retrouver ta petite fille !" },
];
function finishPiquette() {
  piq.state = 'done'; score += 150;
  addPop('+150', P.x - 30, P.y - 140);
  items.push({ n: 'bone', x: P.x + 40, y: P.y - 30, t: 0, pop: 0.001 });
  piquette.cheerT = 3;
  saveGame();
}
function talkPiquette() {
  if (piq.state === 'done') {
    piquette.waveT = 2;
    say([{ who: 'piquette', face: 2, text: "Mes petits dorment à poings fermés. Merci encore, Tecky !" }]);
    return;
  }
  if (!babiesLeft()) { piq.state = 'asked'; say(piquetteThanks(), finishPiquette); return; }
  if (piq.state === 'asked') {
    const n = babiesLeft();
    say([{ who: 'piquette', face: 3, text: (n > 1 ? `Il m'en manque encore ${n}.` : "Plus qu'un !") +
      " Ils se cachent sous les fougères : approche-toi doucement, ils te suivront. Mais n'aboie pas, ça leur fait peur !" }]);
    return;
  }
  piq.state = 'asked';
  say([
    { who: 'piquette', face: 3, text: "Oh, bonjour, petit chien ! Je suis Maman Piquette. Mes trois petits jouaient à cache-cache dans la forêt…" },
    { who: 'piquette', face: 0, text: "Ils se sont cachés sous les fougères, et ils n'osent plus sortir. Tu veux bien me les ramener ? Ils te suivront !" },
    { who: 'tecky', face: 2, text: "Ouaf ! Moi aussi, je cherche quelqu'un qui joue à cache-cache !" },
  ], saveGame);
}

/* ------------------------------------------------------------------ Titine, le petit train du port */
/* Une locomotive à vapeur (vehicle/loco) et trois wagons font l'aller-retour sur la voie du quai (MAP.track : x des
   heurtoirs ouest et est, y des rails), avec une pause à chaque bout. La locomotive est à l'est : elle tire vers l'est,
   pousse vers l'ouest. Le train s'arrête devant Tecky, un chien, Pompon ou un chat, et sonne (« Tut-tut ! ») pour
   Tecky ; il écarte doucement un ballon de Léon posé sur les rails. C'est un obstacle (trainHit, dans blockedFeet),
   mais il n'avance que la voie libre : il ne pousse jamais personne. Un aboiement vers lui le fait siffler
   (« Tchou-tchou ! », vapeur) : des points la première fois (train.scored, sauvegardé), badge « train ». */
const TRAIN = { spd: 80, acc: 60, brake: 160, look: 70, pause: 3, score: 50, puff: 0.7, whistleCd: 1.6,
  cars: ['wagon_orange', 'wagon_green', 'wagon_blue'], loco: 128, wagon: 96, top: 30, bottom: 12, ground: 10 };
let train = null;
// x : centre de la locomotive ; les wagons sont à l'ouest, attelés bout à bout
function newTrain() {
  const [x0, x1] = MAP.track, len = TRAIN.loco + TRAIN.cars.length * TRAIN.wagon;
  return { x: (x0 + x1) / 2 + len / 2 - TRAIN.loco / 2, dir: 1, v: 0, mode: 'run', t: 0, dist: 0, rang: false,
    puffT: 0, whistleT: 0, scored: false };
}
const trainWest = () => train.x - TRAIN.loco / 2 - TRAIN.cars.length * TRAIN.wagon;
const trainEast = () => train.x + TRAIN.loco / 2;
const trainY = () => MAP.track[2];
function trainHit(x0, y0, x1, y1) {
  const ty = trainY();
  return x1 > trainWest() && x0 < trainEast() && y1 > ty - TRAIN.top && y0 < ty + TRAIN.bottom;
}
// limites de la locomotive : les heurtoirs (avec leur épaisseur)
const trainMin = () => MAP.track[0] + 24 + TRAIN.cars.length * TRAIN.wagon + TRAIN.loco / 2;
const trainMax = () => MAP.track[1] - 24 - TRAIN.loco / 2;
// qui est sur la voie devant le train (de lead à lead + dir * look) ?
function trainBlocker() {
  const ty = trainY(), lead = train.dir > 0 ? trainEast() : trainWest();
  const a = Math.min(lead, lead + train.dir * TRAIN.look), b = Math.max(lead, lead + train.dir * TRAIN.look);
  const onTrack = (x, y, hw) => x + hw > a && x - hw < b && y > ty - TRAIN.top && y - 12 < ty + TRAIN.bottom;
  for (const bl of balls) if (!bl.inNet && onTrack(bl.x, bl.y, 14)) { kickBall(bl, bl.x, ty + 60, 260); return bl; }
  if (P.alpha !== 0 && onTrack(P.x, P.y, 16)) return P;
  for (const d of dogs) if (onTrack(d.x, d.y, 16)) return d;
  if (onTrack(pompon.x, pompon.y, 12)) return pompon;
  for (const c of critters) if (c.h === 0 && onTrack(c.x, c.y, 12)) return c;
  return null;
}
function trainPuff(n) {
  for (let i = 0; i < n; i++)
    addFx('fx/steam', train.x + 32 + (Math.random() - 0.5) * 8, trainY() + TRAIN.ground - 74 - i * 7,   // sur la cheminée
      { fps: 10, vx: -train.dir * 12 + (Math.random() - 0.5) * 20, vy: -22 - Math.random() * 12 });
}
function updateTrain(dt) {
  const T = train;
  T.t += dt; T.whistleT = Math.max(0, T.whistleT - dt);
  if (T.mode === 'wait') {                          // pause au bout de la voie, puis on repart dans l'autre sens
    if ((T.waitT -= dt) <= 0) { T.mode = 'run'; T.dir = -T.dir; }
    return;
  }
  const who = trainBlocker();
  if (who === P && !T.rang) { T.rang = true; addWordPop('Tut-tut !', P.x, P.y - 120, 'train'); if (!muted) SFX.bell(); }
  if (!who) T.rang = false;
  const target = who ? 0 : TRAIN.spd;
  T.v = T.v < target ? Math.min(target, T.v + TRAIN.acc * dt) : Math.max(target, T.v - TRAIN.brake * dt);
  if (T.v <= 0) return;
  const lim = T.dir > 0 ? trainMax() : trainMin();
  const dx = T.dir * Math.min(T.v * dt, Math.abs(lim - T.x));
  T.x += dx; T.dist += Math.abs(dx);
  if ((T.puffT -= dt) <= 0) { T.puffT = TRAIN.puff; trainPuff(1); }
  if (T.x === lim) { T.mode = 'wait'; T.waitT = TRAIN.pause; T.v = 0; }
}
function barkAtTrain(vx, vy) {
  if (train.whistleT > 0) return;
  const ty = trainY() - 40;
  const near = [trainWest(), train.x, trainEast()].some(x => {
    const dx = x - P.x, dy = ty - P.y, l = Math.hypot(dx, dy);
    return l < BARK.range + 60 && (dx * vx + dy * vy) / Math.max(1, l) > BARK.cos * 0.8;
  });
  if (!near) return;
  train.whistleT = TRAIN.whistleCd;
  addWordPop('Tchou-tchou !', train.x, trainY() - 140, 'train');
  trainPuff(4);
  if (!muted) SFX.whistle();
  if (!train.scored) { train.scored = true; score += TRAIN.score; addPop('+' + TRAIN.score, train.x - 20, trainY() - 110); }
}
function drawTrain() {
  const f = Math.floor(train.dist / 10), y = trainY() + TRAIN.ground;
  drawSpr('vehicle/loco', f, train.x, y);
  TRAIN.cars.forEach((n, k) => drawSpr('vehicle/' + n, f, train.x - TRAIN.loco / 2 - TRAIN.wagon / 2 - k * TRAIN.wagon, y));
}

/* ------------------------------------------------------------------ terriers */
/* Sous certains grillages, un terrier (MAP.tunnels : deux extrémités). Près d'une extrémité, C fait « Passer » :
   Tecky gratte, disparaît sous la clôture et ressort de l'autre côté. Les chiens, eux, doivent faire le tour. */
const TUNNEL = { reach: 66, dig: 0.55, under: 0.3, out: 0.3 };
let tunnelSeen = false;
function nearTunnel() {
  for (const [ax, ay, bx, by] of MAP.tunnels) {
    if (dist(P.x, P.y, ax, ay) < TUNNEL.reach) return { fx: ax, fy: ay, tx: bx, ty: by };
    if (dist(P.x, P.y, bx, by) < TUNNEL.reach) return { fx: bx, fy: by, tx: ax, ty: ay };
  }
  return null;
}
function startTunnel(t) {
  P.mode = 'tunnel'; P.timer = 0; P.tun = t; P.setAnim('dig'); P.digTick = 0;
  P.x = t.fx; P.y = t.fy;
  P.dir = dirFrom(t.tx - t.fx, t.ty - t.fy, P.dir);
}
function updateTunnel(dt) {
  const t = P.tun, T = TUNNEL;
  P.timer += dt;
  if (P.timer < T.dig) {                               // il gratte
    if ((P.digTick -= dt) <= 0) { P.digTick = 0.16; addFx('fx/dirt', t.fx + (Math.random() - 0.5) * 16, t.fy + 4, { fps: 16 }); SFX.scratch(); }
    P.sy = 1 - P.timer / T.dig * 0.6;
  } else if (P.timer < T.dig + T.under) {              // sous le grillage
    P.alpha = 0; P.sy = 0.3;
    if (!t.moved) { t.moved = true; P.x = t.tx; P.y = t.ty; P.setAnim('idle'); afterTunnel(); }   // (terriers verticaux : même x aux deux bouts)
  } else if (P.timer < T.dig + T.under + T.out) {      // il ressort de l'autre côté
    P.alpha = 1; P.sy = 0.3 + (P.timer - T.dig - T.under) / T.out * 0.7;
  } else {
    P.alpha = 1; P.sy = undefined; P.mode = 'free'; P.inv = Math.max(P.inv, 0.5);
    addFx('fx/dirt', P.x, P.y + 4, { fps: 16 });
    if (!tunnelSeen) {
      tunnelSeen = true;
      say([{ who: 'tecky', face: 2, text: "Un teckel, ça creuse des terriers : hop, sous le grillage ! Les autres chiens, eux, doivent faire le tour." }]);
    }
  }
}

/* ------------------------------------------------------------------ flair */
/* R (Y à la manette, bouton à truffe au toucher) : Tecky flaire, et une piste de petits pieds nus (fx/footprint) apparaît
   au sol vers le prochain indice, puis vers Alice. Elle suit un vrai chemin à pied (distances calculées sur une grille
   de 16 px, comme check_placement.js) et s'efface au bout de quelques secondes. Les trésors proches scintillent aussi. */
const SNIFF = { time: 0.75, cd: 2.5, len: 1150, step: 36, delay: 0.05, life: 5, fade: 1, treasure: 560 };
const GRID = 16;
let walkGrid = null, distField = null, trail = [];
function buildWalkGrid() {
  const W = Math.floor(MAP.w * TS / GRID), H = Math.floor(MAP.h * TS / GRID), g = new Uint8Array(W * H);
  for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
    const x = i * GRID + GRID / 2, y = j * GRID + GRID / 2;
    g[j * W + i] = (x < 24 || y < 40 || x > MAP.w * TS - 24 || y > MAP.h * TS - 4 ||
      waterAt(x - 12, y) || waterAt(x + 12, y) || waterAt(x, y - 12) || waterAt(x, y)) ? 0 : 1;
  }
  for (const s of solids) {                            // pieds de 24 x 12 : même test que blockedFeet
    for (let j = Math.max(0, Math.floor(s[1] / GRID)); j <= Math.min(H - 1, Math.floor((s[3] + 12) / GRID)); j++)
      for (let i = Math.max(0, Math.floor((s[0] - 12) / GRID)); i <= Math.min(W - 1, Math.floor((s[2] + 12) / GRID)); i++) {
        const x = i * GRID + GRID / 2, y = j * GRID + GRID / 2;
        if (x + 12 > s[0] && x - 12 < s[2] && y > s[1] && y - 12 < s[3]) g[j * W + i] = 0;
      }
  }
  walkGrid = { W, H, g };
}
function nearestOpen(x, y) {
  const { W, H, g } = walkGrid;
  const ci = clamp(Math.floor(x / GRID), 0, W - 1), cj = clamp(Math.floor(y / GRID), 0, H - 1);
  for (let r = 0; r < 12; r++)
    for (let j = cj - r; j <= cj + r; j++) for (let i = ci - r; i <= ci + r; i++)
      if (i >= 0 && j >= 0 && i < W && j < H && g[j * W + i] && Math.max(Math.abs(i - ci), Math.abs(j - cj)) === r) return j * W + i;
  return -1;
}
function fieldTo(x, y) {                               // distances (en cases) jusqu'au point visé, par parcours en largeur
  if (!walkGrid) buildWalkGrid();
  const key = Math.round(x) + ',' + Math.round(y);
  if (distField && distField.key === key) return distField.d;
  const { W, H, g } = walkGrid, d = new Int32Array(W * H).fill(-1), q = new Int32Array(W * H);
  const start = nearestOpen(x, y);
  if (start >= 0) {
    let qa = 0, qb = 0;
    d[start] = 0; q[qb++] = start;
    while (qa < qb) {
      const c = q[qa++], i = c % W, j = (c - i) / W;
      for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const ni = i + di, nj = j + dj, n = nj * W + ni;
        if (ni < 0 || nj < 0 || ni >= W || nj >= H || d[n] >= 0 || !g[n]) continue;
        d[n] = d[c] + 1; q[qb++] = n;
      }
    }
  }
  distField = { key, d };
  return d;
}
// suite de points du chemin à pied de Tecky vers (x, y), limitée à len pixels
function scentPath(x, y, len) {
  const d = fieldTo(x, y), { W, H } = walkGrid;
  let c = nearestOpen(P.x, P.y);
  if (c < 0 || d[c] < 0) return null;
  const pts = [[P.x, P.y]];
  let total = 0;
  while (d[c] > 0 && total < len) {
    const i = c % W, j = (c - i) / W;
    let best = c;
    for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]) {
      const ni = i + di, nj = j + dj, n = nj * W + ni;
      if (ni < 0 || nj < 0 || ni >= W || nj >= H || d[n] < 0) continue;
      if (di && dj && (d[j * W + ni] < 0 || d[nj * W + i] < 0)) continue;     // pas de coin coupé
      if (d[n] < d[best]) best = n;
    }
    if (best === c) break;
    c = best;
    const bi = c % W, bj = (c - bi) / W, p = [bi * GRID + GRID / 2, bj * GRID + GRID / 2], q = pts[pts.length - 1];
    total += Math.hypot(p[0] - q[0], p[1] - q[1]);
    pts.push(p);
  }
  return pts;
}
function startSniff() {
  P.mode = 'sniff'; P.timer = SNIFF.time; P.cdSniff = SNIFF.cd; P.cdSniffMax = SNIFF.cd; P.setAnim('idle');
  addWordPop('Snif snif…', P.x, P.y - 130, 'tecky');
  SFX.sniff();
}
function layTrail() {
  const tg = arrowTarget();
  trail = [];
  const pts = scentPath(tg.x, tg.y, SNIFF.len);
  if (pts && pts.length > 1) {
    // empreintes tous les SNIFF.step px le long du chemin, pied gauche et pied droit en alternance
    let acc = SNIFF.step * 0.8, k = 0;
    for (let n = 1; n < pts.length; n++) {
      const [x0, y0] = pts[n - 1], [x1, y1] = pts[n], seg = Math.hypot(x1 - x0, y1 - y0);
      let u = 0;
      while (acc + (seg - u) >= SNIFF.step) {
        u += SNIFF.step - acc; acc = 0;
        const ang = Math.atan2(y1 - y0, x1 - x0), side = k % 2 ? 1 : -1;
        trail.push({ x: x0 + (x1 - x0) * u / seg - Math.sin(ang) * 7 * side, y: y0 + (y1 - y0) * u / seg + Math.cos(ang) * 7 * side,
          ang, foot: k % 2, t: -k * SNIFF.delay });
        k++;
      }
      acc += seg - u;
    }
  } else addWordPop('Hmm…', P.x, P.y - 160, 'tecky');
  for (const g of digs) if (!g.dug && dist(P.x, P.y, g.x, g.y) < SNIFF.treasure) addFx('fx/pickup', g.x, g.y - 24, { fps: 9 });
}
function updateTrail(dt) {
  for (let i = trail.length - 1; i >= 0; i--) if ((trail[i].t += dt) > SNIFF.life + SNIFF.fade) trail.splice(i, 1);
}
function drawTrail() {
  for (const f of trail) {
    if (f.t < 0) continue;
    const a = Math.min(1, f.t / 0.15) * (f.t > SNIFF.life ? 1 - (f.t - SNIFF.life) / SNIFF.fade : 1);
    drawSpr('fx/footprint', f.foot, f.x, f.y, { angle: f.ang + Math.PI / 2, alpha: a * 0.9 });
  }
}

/* ------------------------------------------------------------------ gratter, lire */
// menace immédiate : un chien lancé contre Tecky et tout proche. Mordre passe alors avant gratter ou lire.
const THREAT_R = 240;
const ENGAGED = new Set(['chase', 'attack', 'bark', 'hurt', 'crouch', 'charge', 'tired']);
/* Zones calmes (MAP.calm : le village, la cour de la ferme), comme les villes d'un RPG : aucun chien hostile n'y vit,
   un chien qui poursuit Tecky s'arrête quand il y entre (« Grrr… ») et rentre chez lui, et aucune morsure n'y porte.
   En plus, un petit répit (GRACE s) après chaque dialogue. */
const GRACE = 1.5;
let graceT = 0;
const calmAt = (x, y) => MAP.calm.some(([x0, y0, x1, y1]) => x >= x0 && x <= x1 && y >= y0 && y <= y1);
function threatened() {
  if (balade()) return false;          // en balade, les chiens ne menacent personne
  if (calmAt(P.x, P.y)) return false;  // (zone calme)
  return dogs.some(d => ENGAGED.has(d.mode) && dist(P.x, P.y, d.x, d.y) < THREAT_R);
}
// portées des actions (check_placement.js s'en sert aussi : deux actions différentes ne se recouvrent jamais)
const REACH = { sign: 95, dig: 86, item: 52 };
function nearDig() {
  for (const g of digs) if (!g.dug && dist(P.x, P.y, g.x, g.y + 6) < REACH.dig) return g;
  return null;
}
// panneau à portée : [x, y, texte]
function nearSign() {
  for (const s of MAP.signs) if (dist(P.x, P.y, s[0], s[1] + 30) < REACH.sign) return s;
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
  if (nearNpc()) return 'talk';
  if (nearDig()) return 'dig';
  if (nearTunnel()) return 'tunnel';
  if (nearSign()) return 'read';
  if (balade() && playTarget(true)) return 'play';
  return 'bite';
}
const ACTION_FRAME = { bite: 2, dig: 4, read: 6, talk: 12, play: 8, tunnel: 4, sniff: 10 };   // images de hud/action
// Tecky et le chien sautillent ensemble ; à la fin, le chien devient un copain (voir updateDog, mode 'play')
function startPlay(d) {
  P.mode = 'play'; P.timer = PLAY.tecky; P.setAnim('idle'); P.cdBite = 0.5; P.cdBiteMax = 0.5;
  P.dir = dirFrom(d.x - P.x, d.y - P.y, P.dir);
  d.mode = 'play'; d.timer = PLAY.time; d.heartT = 0; d.hop = 0; d.wait = 0;
  d.dir = dirFrom(P.x - d.x, P.y - d.y, d.dir);
  d.setAnim('idle');
  SFX.yip(d.T.pitch);
}
/* Copains qui suivent (balade) : après une partie de jeu, le chien suit Tecky FOLLOW.time secondes, en file indienne
   derrière lui (chacun marche sur ses traces, à FOLLOW.gap px du précédent), puis rentre chez lui. Ils passent aussi
   par les terriers avec lui. */
const FOLLOW = { time: 30, gap: 58, spd: 330, crumb: 6, max: 500 };
let crumbs = [], followN = 0;         // traces de Tecky, de la plus récente à la plus ancienne
function recordCrumb() {
  const c = crumbs[0];
  if (!c || Math.hypot(P.x - c[0], P.y - c[1]) >= FOLLOW.crumb) {
    crumbs.unshift([P.x, P.y]);
    if (crumbs.length > FOLLOW.max) crumbs.pop();
  }
}
function crumbAt(d) {                  // point des traces de Tecky, d px derrière lui
  let acc = 0, prev = [P.x, P.y];
  for (const c of crumbs) {
    const l = Math.hypot(c[0] - prev[0], c[1] - prev[1]);
    if (acc + l >= d) { const u = (d - acc) / (l || 1); return [prev[0] + (c[0] - prev[0]) * u, prev[1] + (c[1] - prev[1]) * u]; }
    acc += l; prev = c;
  }
  return prev;
}
function startFollow(d) { d.mode = 'follow'; d.followT = FOLLOW.time; d.followN = ++followN; d.setAnim('walk'); }
function afterTunnel() {               // les copains qui suivent passent sous le grillage avec Tecky
  crumbs = [];
  for (const d of dogs) if (d.mode === 'follow') { d.x = P.x; d.y = P.y; }
  if (pompon.mode === 'follow') { pompon.x = P.x; pompon.y = P.y; }
  for (const b of babies) if (b.mode === 'follow') { b.x = P.x; b.y = P.y; }
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
// trésor : un os doré jaillit du trou (treasures = nombre d'os dorés trouvés)
function uncover(g) {
  g.dug = true; treasures++; score += 100;
  items.push({ n: 'goldbone', x: g.x, y: g.y - 30, t: 0, pop: 0.001 });
  addFx('fx/pickup', g.x, g.y - 20, { fps: 12 });
  addPop('+100', g.x - 30, g.y - 90);
  SFX.treasure();
  shake = 0.15;
  rumble('treasure');
  say([{ who: 'tecky', face: 2, text: "Wouf ! Un os doré était enterré ! (" + treasures + " / " + MAP.dig.length + ")" }], saveGame);
}

function hurtPlayer(dmg, fromX, fromY) {
  if (P.inv > 0 || P.mode === 'ko' || state !== 'play' || balade() || graceT > 0 || calmAt(P.x, P.y)) return;
  if (facile()) dmg = Math.max(1, Math.floor(dmg / 2));
  P.hp = Math.max(0, P.hp - dmg);
  bitten = true;                      // (badge « Sans une égratignure »)
  const l = Math.max(1, dist(P.x, P.y, fromX, fromY));
  P.kx = (P.x - fromX) / l * 420; P.ky = (P.y - fromY) / l * 420;
  P.inv = 1.2; shake = 0.25;
  addFx('fx/hit', P.x, P.y - 44, { fps: 16 });
  SFX.hurt();
  rumble(P.hp <= 0 ? 'ko' : 'hurt');
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
  if (!leafTrees) leafTrees = decor.concat(EDGE_DECOR).filter(d => d.n === 'tree' || d.n === 'apple_tree' || d.n === 'apple_tree_young' || d.n === 'fir');
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

/* Du jour à la nuit : la lumière suit la progression, un cran par indice. 0 : plein jour ; 1 : fin d'après-midi ;
   2 : coucher de soleil orangé ; 3 (troisième indice, puis les retrouvailles) : le soleil se couche encore, un peu plus
   rouge, et les lampadaires s'allument (passé SUN.lamp : plus d'arc-en-ciel) ; 4 : la nuit bleutée, qui ne tombe que
   pendant la scène de fin, quand Tecky et Alice rentrent à la niche (et reste sur l'écran de victoire).
   Teinte multipliée sur le monde (pas sur l'interface), halo doré venant de l'ouest au coucher, vignette le soir.
   hug : la lumière chaude autour d'Alice et de Tecky, qui monte une fois qu'il l'a trouvée. */
const SUN = { speed: 0.25, lamp: 2.5,
  tints: [[255, 255, 255], [255, 241, 220], [255, 214, 170], [250, 198, 160], [132, 142, 196]],
  glow: [0, 0.08, 0.2, 0.24, 0], vignette: [0, 0, 0.08, 0.14, 0.3] };
let hug = 0;
const sunGoal = () => !alice.found ? clues.filter(Boolean).length : (ending && ending.home) || state === 'win' ? 4 : 3;
const lampsOn = () => sun > SUN.lamp;
function updateSun(dt) {
  sun += clamp(sunGoal() - sun, -SUN.speed * dt, SUN.speed * dt);
  hug += clamp((alice.found ? 1 : 0) - hug, -SUN.speed * dt, SUN.speed * dt);
}
const sunAt = (arr, k) => { const i = Math.min(arr.length - 2, Math.floor(k)), f = k - i; return arr[i] + (arr[i + 1] - arr[i]) * f; };
/* Pour rester rapide (Firefox dessine souvent le canvas avec le processeur : les dégradés recalculés à chaque image sur
   tout l'écran coûtaient plus de 150 ms par image en 4K), la teinte est un simple remplissage, et la vignette et le
   halo doré sont pré-rendus en petit (LIGHT, recalculés seulement quand le soleil bouge) puis posés agrandis sans
   lissage : ce sont des dégradés très doux, aucune marche n'est visible. Halos des lampadaires et des retrouvailles :
   une même tache de lumière pré-rendue (glowImg). */
const LIGHT = { w: 480, h: 270, step: 0.01, glowK: 0.75 };
let lightImg = null, lightK = -1, glowImg = null;
function buildLight(k) {
  if (!lightImg) { lightImg = document.createElement('canvas'); lightImg.width = LIGHT.w; lightImg.height = LIGHT.h; }
  const o = lightImg.getContext('2d'), W = LIGHT.w, H = LIGHT.h;
  o.clearRect(0, 0, W, H);
  const vig = sunAt(SUN.vignette, k);
  if (vig > 0) {
    const g = o.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, W * 0.62);
    g.addColorStop(0, 'rgba(40, 40, 100, 0)'); g.addColorStop(1, `rgba(40, 40, 100, ${vig})`);
    o.fillStyle = g; o.fillRect(0, 0, W, H);
  }
  // halo doré venant de l'ouest (posé par-dessus, un peu moins fort que l'ancien mode « screen »)
  const glow = sunAt(SUN.glow, k) * LIGHT.glowK;
  const g = o.createLinearGradient(0, 0, W, H * 0.5);
  g.addColorStop(0, `rgba(255, 190, 110, ${glow})`); g.addColorStop(1, 'rgba(255, 190, 110, 0)');
  o.fillStyle = g; o.fillRect(0, 0, W, H);
  lightK = k;
}
function glowSpot(x, y, r, a) {                       // tache de lumière chaude, pré-rendue une fois
  if (!glowImg) {
    glowImg = document.createElement('canvas'); glowImg.width = glowImg.height = 128;
    const o = glowImg.getContext('2d'), g = o.createRadialGradient(64, 64, 4, 64, 64, 64);
    g.addColorStop(0, 'rgba(255, 212, 140, 1)'); g.addColorStop(1, 'rgba(255, 212, 140, 0)');
    o.fillStyle = g; o.fillRect(0, 0, 128, 128);
  }
  ctx.globalAlpha = a; ctx.drawImage(glowImg, x - r, y - r, r * 2, r * 2); ctx.globalAlpha = 1;
}
function drawLight(cx, cy) {
  if (sun < 0.01 && weather.k < 0.01) return;
  const k = clamp(sun, 0, 4), wt = weatherTint();          // (la météo assombrit dans le même remplissage)
  const tint = [0, 1, 2].map(j => Math.round(sunAt(SUN.tints.map(t => t[j]), k) * wt[j] / 255));
  ctx.save();
  ctx.globalCompositeOperation = 'multiply';
  ctx.fillStyle = `rgb(${tint[0]}, ${tint[1]}, ${tint[2]})`;
  ctx.fillRect(cx, cy, VW, VH);
  ctx.globalCompositeOperation = 'source-over';
  if (sun < 0.01) { ctx.restore(); return; }
  if (Math.abs(k - lightK) >= LIGHT.step || (k !== lightK && (k === Math.round(k)))) buildLight(k);
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(lightImg, cx, cy, VW, VH);
  ctx.imageSmoothingEnabled = true;
  // lampadaires allumés en fin de journée : halo autour de la lanterne et flaque de lumière au sol, plus forts la nuit
  const lamp = clamp((k - SUN.lamp) * 2, 0, 1), night = clamp(k - 3, 0, 1);
  if (lamp > 0) for (const d of decor) {
    if (d.n !== 'lamppost' || d.x < cx - 160 || d.x > cx + VW + 160 || d.y < cy - 40 || d.y > cy + VH + 200) continue;
    glowSpot(d.x, d.y - 93, 64 + 16 * night, (0.55 + 0.3 * night) * lamp);
    glowSpot(d.x, d.y - 4, 70 + 40 * night, (0.3 + 0.3 * night) * lamp);
  }
  // retrouvailles : une lumière chaude autour d'Alice et de Tecky
  if (hug > 0) glowSpot((alice.x + P.x) / 2, (alice.y + P.y) / 2 - 50, 260, 0.45 * hug);
  if (ending && ending.home) drawFireflies();
  ctx.restore();
}

/* ------------------------------------------------------------------ météo */
/* Option « Météo » : auto (une averse de temps en temps, de la neige au lieu de la pluie en décembre), soleil, pluie ou
   neige en continu. weather.k = force de l'averse (0..1, monte et descend en WEATHER.ramp s). Pluie : gouttes (traits),
   éclaboussures (fx/splash), temps plus gris (teinte dans drawLight), flaques (fx/puddle, places fixes tirées une fois :
   elles se remplissent avec weather.wet et sèchent ensuite), plouf quand Tecky marche dedans, crépitement (Ambience).
   Après l'averse : un arc-en-ciel, et Tecky s'ébroue (pose « shake », gouttes fx/drop). Neige : flocons (fx/snowflake),
   sol qui blanchit (weather.cover), teinte froide. Rien n'est sauvegardé : c'est le temps qu'il fait. */
const WEATHER = { first: [50, 110], every: [110, 230], rain: [35, 65], snow: [90, 160], ramp: 6, bow: 16, drops: 150, flakes: 130,
  wetUp: 0.05, wetDown: 0.01, coverUp: 0.012, coverDown: 0.002, splashes: 10, puddle: 30 };
let weather = { kind: 'rain', k: 0, on: false, timer: 60, wet: 0, cover: 0, bow: 0, wasRain: false, splashT: 0 };
let drops = [], flakes = [], puddles = null, shakePending = false;
function december() { return new Date().getMonth() === 11; }
function weatherKind() { return opts.weather === 'neige' || (opts.weather === 'auto' && december()) ? 'snow' : 'rain'; }
function resetWeather() {
  weather = { kind: weatherKind(), k: 0, on: false, timer: rnd(WEATHER.first), wet: 0, cover: 0, bow: 0, wasRain: false, splashT: 0 };
  drops = Array.from({ length: WEATHER.drops }, () => ({ x: Math.random() * (VW + 200), y: Math.random() * VH, l: 18 + Math.random() * 16, v: 0.8 + Math.random() * 0.4 }));
  flakes = Array.from({ length: WEATHER.flakes }, () => ({ x: Math.random() * VW, y: Math.random() * VH, f: Math.floor(Math.random() * 3),
    v: 30 + Math.random() * 45, ph: Math.random() * 6.28 }));
  shakePending = false;
}
function buildPuddles() {             // places des flaques : quelques coins de sol praticable, tirés une fois pour toutes
  puddles = [];
  for (let ty = 1; ty < MAP.h - 1; ty++) for (let tx = 1; tx < MAP.w - 1; tx++) {
    if (hash3(tx, ty, 77) > 0.03) continue;
    const x = tx * TS + 16 + hash3(ty, tx, 5) * 32, y = ty * TS + 16 + hash3(tx, ty, 9) * 32;
    if (!blockedFeet(x, y, 30) && !waterAt(x, y) && !blockedFeet(x - 24, y, 12) && !blockedFeet(x + 24, y, 12))
      puddles.push({ x, y, f: Math.floor(hash3(tx, ty, 3) * 3), s: 0.8 + hash3(ty, tx, 2) * 0.5 });
  }
}
function updateWeather(dt) {
  const w = weather;
  if (opts.weather === 'soleil') w.on = false;
  else if (opts.weather !== 'auto') w.on = true;
  else if ((w.timer -= dt) <= 0) {     // auto : une averse de temps en temps
    w.on = !w.on;
    if (w.on) w.kind = weatherKind();
    w.timer = w.on ? rnd(w.kind === 'snow' ? WEATHER.snow : WEATHER.rain) : rnd(WEATHER.every);
  }
  if (w.k === 0) w.kind = weatherKind();                  // (on change de pluie à neige seulement par temps sec)
  w.k = clamp(w.k + (w.on ? 1 : -1) * dt / WEATHER.ramp, 0, 1);
  const rain = w.kind === 'rain' ? w.k : 0, snow = w.kind === 'snow' ? w.k : 0;
  w.wet = clamp(w.wet + (rain > 0.3 ? WEATHER.wetUp * rain : -WEATHER.wetDown) * dt, 0, 1);
  w.cover = clamp(w.cover + (snow > 0.3 ? WEATHER.coverUp * snow : -WEATHER.coverDown) * dt, 0, 1);
  // fin de l'averse : un arc-en-ciel, et Tecky s'ébroue
  if (rain > 0.6) w.wasRain = true;
  if (w.wasRain && w.k < 0.05) { w.wasRain = false; if (!lampsOn()) w.bow = 1; if (state === 'play') shakePending = true; }
  w.bow = Math.max(0, w.bow - dt / WEATHER.bow);
  // gouttes et flocons (en coordonnées de l'écran du monde : ils tombent devant la caméra)
  if (rain > 0) {
    for (const d of drops) { d.y += 980 * d.v * dt; d.x -= 170 * d.v * dt; if (d.y > VH + 40) { d.y -= VH + 80; d.x = Math.random() * (VW + 200); } }
    if (state === 'play' && (w.splashT -= dt * WEATHER.splashes * rain) <= 0) {
      w.splashT = 1;
      addFx('fx/splash', camX + Math.random() * VW, camY + Math.random() * VH, { fps: 16 });
    }
  }
  if (snow > 0) for (const f of flakes) {
    f.y += f.v * dt; f.x += (Math.sin(f.y / 40 + f.ph) * 18 - 12) * dt;
    if (f.y > VH + 20) { f.y -= VH + 40; f.x = Math.random() * VW; }
    if (f.x < -20) f.x += VW + 40;
  }
}
const rainNow = () => weather.kind === 'rain' ? weather.k : 0;
const snowNow = () => weather.kind === 'snow' ? weather.k : 0;
function weatherTint() {              // teinte multipliée : gris-bleu sous la pluie, froide sous la neige (255 = rien)
  const r = rainNow(), n = snowNow();
  return [255 - 50 * r - 22 * n, 255 - 40 * r - 14 * n, 255 - 22 * r];
}
function drawGroundWeather(cx, cy) {   // sous les personnages : neige au sol, flaques
  const w = weather;
  if (w.cover > 0.01) { ctx.fillStyle = `rgba(246, 250, 255, ${0.45 * w.cover})`; ctx.fillRect(cx, cy, VW, VH); }
  if (w.wet < 0.02) return;
  if (!puddles) buildPuddles();
  for (const p of puddles) {
    if (p.x < cx - 80 || p.x > cx + VW + 80 || p.y < cy - 60 || p.y > cy + VH + 60) continue;
    drawSpr('fx/puddle', p.f, p.x, p.y, { alpha: Math.min(1, w.wet * 1.4), sc: p.s * (0.6 + 0.4 * w.wet) });
  }
}
function drawSkyWeather(cx, cy) {     // par-dessus le monde : gouttes, flocons
  const r = rainNow(), n = snowNow();
  if (r > 0.01) {
    ctx.save();
    ctx.strokeStyle = 'rgba(210, 225, 255, 0.55)'; ctx.lineWidth = 2; ctx.lineCap = 'round';
    ctx.beginPath();
    const count = Math.round(drops.length * r);
    for (let i = 0; i < count; i++) {
      const d = drops[i], x = cx + d.x - 100, y = cy + d.y;
      ctx.moveTo(x, y); ctx.lineTo(x - d.l * 0.17, y + d.l);
    }
    ctx.stroke();
    ctx.restore();
  }
  if (n > 0.01) {                      // flocons : directement depuis l'atlas (beaucoup d'images, sans save/restore)
    const S = ATLAS['fx/snowflake'], count = Math.round(flakes.length * n);
    for (let i = 0; i < count; i++) {
      const fl = flakes[i], f = S.f[fl.f];
      ctx.drawImage(atlas, f[0], f[1], f[2], f[3], cx + fl.x + f[4] - S.o[0], cy + fl.y + f[5] - S.o[1], f[2], f[3]);
    }
  }
}
function drawRainbow() {              // après l'averse : un grand arc-en-ciel, doux, qui s'efface (et vite, si les lampadaires s'allument)
  const b = weather.bow, day = 1 - clamp((sun - SUN.lamp) * 2, 0, 1);
  if (b < 0.01 || day <= 0) return;
  guiTransform();
  ctx.save();
  ctx.globalAlpha = 0.24 * Math.min(1, b * 3) * Math.min(1, (1 - b) * 8) * day;
  ctx.lineWidth = 22;
  ['#E5484D', '#F2994A', '#F2C94C', '#6FCF97', '#56CCF2', '#5B6CF2', '#9B51E0'].forEach((c, i) => {
    ctx.strokeStyle = c;
    ctx.beginPath(); ctx.arc(GW * 0.62, GH + 260, 1060 - i * 22, Math.PI * 1.08, Math.PI * 1.92); ctx.stroke();
  });
  ctx.restore();
}
function startShake() {               // Tecky s'ébroue (deux secousses) : des gouttes partent tout autour, deux fois
  if (P.dir === 'up') P.dir = 'down';
  P.mode = 'shake'; P.setAnim('shake'); P.drops2 = false;
  shakeDrops(0);
  if (!muted) SFX.shake();
}
function shakeDrops(turn) {
  for (let k = 0; k < 12; k++) {
    const a = (k + turn) / 12 * Math.PI * 2;
    addFx('fx/drop', P.x + Math.cos(a) * 14, P.y - 36, { fps: 0, frame: 0, life: 0.45, vx: Math.cos(a) * 170, vy: Math.sin(a) * 110 - 40 });
  }
}
function puddleSplash(dt) {           // Tecky marche dans une flaque : plouf
  if (weather.wet < 0.3 || !puddles || (P.plopT = (P.plopT || 0) - dt) > 0) return;
  for (const p of puddles) if (Math.abs(p.x - P.x) < WEATHER.puddle && Math.abs(p.y - P.y) < WEATHER.puddle * 0.6) {
    P.plopT = 0.3;
    addFx('fx/splash', P.x, P.y, { fps: 18 });
    if (!muted) SFX.plop();
    return;
  }
}

/* ------------------------------------------------------------------ zones */
/* La carte est découpée en zones (MAP.zones, carte.json : la première dont un rectangle contient le point ; coordonnées
   en tuiles). Elles donnent le bandeau qui s'affiche en arrivant (nom de la zone), les étiquettes de la carte de la
   pause, l'ambiance sonore et le timbre des instruments de la musique (TIMBRE ; music : la variation d'une autre zone,
   comme le verger qui a celle de la ferme). La rivière n'est pas une zone : celles du nord et du sud vont jusqu'à son
   milieu, sinon la musique changerait en la longeant ou en passant le pont. Un bord de rectangle posé sur le bord de la
   carte n'a pas de limite (la caméra et la lisière vont au-delà) ; la dernière zone couvre toute la carte. */
// name : bandeau à l'arrivée ; label : étiquette de la carte, posée en at (tuiles)
const ZONES = MAP.zones.map(z => {
  const lim = z.rects.map(([x0, y0, x1, y1]) => [x0 <= 0 ? -Infinity : x0, y0 <= 0 ? -Infinity : y0,
    x1 >= MAP.w ? Infinity : x1, y1 >= MAP.h ? Infinity : y1]);
  return { ...z, has: (x, y) => lim.some(([x0, y0, x1, y1]) => x >= x0 && x < x1 && y >= y0 && y < y1) };
});
const zoneAt = (x, y) => ZONES.find(z => z.has(x / TS, y / TS)) || ZONES[ZONES.length - 1];
const LANDMARKS = MAP.landmarks;      // autres étiquettes de la carte de la pause (la rivière)
const BANNER = { settle: 0.8, life: 3 };
let zone = null, zoneT = 0, banner = null, tuneT = 0;
function updateZone(dt) {
  const z = zoneAt(P.x, P.y);
  if (!zone) { zone = z; Music.setZone(z.music || z.id, true); }   // nouvelle partie, Continuer : la musique suit tout de suite
  if (z !== zone) {                    // nouvelle zone : on attend un peu (pas de bandeau en longeant une frontière)
    if ((zoneT += dt) > BANNER.settle) { zone = z; zoneT = 0; banner = { text: z.name, t: 0 }; }
  } else zoneT = 0;
  // musique : seulement si Tecky reste MUSIC_ZONE.settle s dans la zone (un passage éclair ne la change pas)
  if ((z.music || z.id) !== (Music.want || Music.zone)) {
    if ((tuneT += dt) > MUSIC_ZONE.settle) { Music.setZone(z.music || z.id); tuneT = 0; }
  } else tuneT = 0;
  if (banner && (banner.t += dt) > BANNER.life) banner = null;
}
function drawBanner() {
  if (!banner || state !== 'play') return;
  const t = banner.t, a = Math.min(1, t / 0.4, (BANNER.life - t) / 0.6);
  ctx.save();
  ctx.globalAlpha = Math.max(0, a);
  outlined(banner.text, GW / 2, 150 - (1 - Math.min(1, t / 0.4)) * 20, 52, '#FFF7E6');
  ctx.restore();
}

/* ------------------------------------------------------------------ carte (pause) */
/* La pause montre la carte : sol et décors en réduction (pré-rendus une fois), brouillard sur ce qui n'a pas encore été vu
   (cases de MAPV.cell tuiles, marquées quand elles passent à l'écran, sauvegardées), noms des zones déjà vues, Tecky,
   indices trouvés, os dorés déterrés, Alice une fois sortie de sa cachette, et l'enclos pendant la quête des poules. */
const MAPV = { cell: 4, w: 1080, top: 150, mark: 0.7 };   // mark : taille des « ! » / « ? » des personnages
let seenCells = null, mapImg = null;
const cellsW = () => Math.ceil(MAP.w / MAPV.cell), cellsH = () => Math.ceil(MAP.h / MAPV.cell);
function markSeen() {
  const c = MAPV.cell * TS, W = cellsW();
  for (let j = Math.max(0, Math.floor(camY / c)); j <= Math.min(cellsH() - 1, Math.floor((camY + VH) / c)); j++)
    for (let i = Math.max(0, Math.floor(camX / c)); i <= Math.min(W - 1, Math.floor((camX + VW) / c)); i++) seenCells[j * W + i] = 1;
}
function buildMapImg() {
  const k = 0.25, c = document.createElement('canvas');
  c.width = Math.round(MAP.w * TS * k); c.height = Math.round(MAP.h * TS * k);
  const g = c.getContext('2d');
  g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
  for (const ch of groundChunks) g.drawImage(ch.c, ch.x * k, ch.y * k, ch.w * k, ch.h * k);
  const sorted = decor.slice().sort((a, b) => (FLAT.has(b.n) - FLAT.has(a.n)) || a.y - b.y);
  for (const d of sorted) {
    const s = ATLAS[d.key];
    if (!s) continue;
    const f = s.f[0];
    g.drawImage(atlas, f[0], f[1], f[2], f[3], (d.x + f[4] - s.o[0]) * k, (d.y + f[5] - s.o[1]) * k, f[2] * k, f[3] * k);
  }
  mapImg = c;
}
function drawPauseMap() {
  if (!mapImg) buildMapImg();
  const w = MAPV.w, h = Math.round(w * MAP.h / MAP.w), x0 = (GW - w) / 2, y0 = MAPV.top, k = w / (MAP.w * TS);
  const mx = x => x0 + x * k, my = y => y0 + y * k;
  drawNine('hud/panel', x0 - 22, y0 - 22, w + 44, h + 44, 32);
  ctx.drawImage(mapImg, x0, y0, w, h);
  // brouillard : une image d'une case par pixel, agrandie avec lissage (bords doux)
  const W = cellsW(), H = cellsH(), fog = document.createElement('canvas');
  fog.width = W; fog.height = H;
  const fg = fog.getContext('2d'), im = fg.createImageData ? fg.createImageData(W, H) : null;
  if (im) {
    for (let i = 0; i < W * H; i++) { im.data[i * 4] = 233; im.data[i * 4 + 1] = 220; im.data[i * 4 + 2] = 192; im.data[i * 4 + 3] = seenCells[i] ? 0 : 236; }
    fg.putImageData(im, 0, 0);
    ctx.save(); ctx.imageSmoothingEnabled = true; ctx.drawImage(fog, x0, y0, w, h); ctx.restore();
  }
  const seenAt = (tx, ty) => seenCells[Math.min(H - 1, Math.floor(ty / MAPV.cell)) * W + Math.min(W - 1, Math.floor(tx / MAPV.cell))];
  for (const z of ZONES.concat(LANDMARKS)) if (seenAt(z.at[0], z.at[1])) outlined(z.label, mx(z.at[0] * TS), my(z.at[1] * TS) + 12, 30, '#FFF7E6');
  // repères
  for (const g of digs) if (g.dug) drawSpr('item/goldbone', 0, mx(g.x), my(g.y) - 4, { sc: 0.55 });
  CLUES.forEach((n, i) => {
    const it = MAP.items.find(e => e[0] === n);
    if (clues[i] && it) drawSpr('hud/arrow_icon', i, mx(it[1]), my(it[2]), { sc: 1.1 });
  });
  if (!alice.hidden) drawSpr('hud/arrow_icon', 3, mx(alice.x), my(alice.y) - 10, { sc: 1.2 });
  if (farm.state === 'asked') drawSpr('hen/idle/right', 0, mx((MAP.pen[0] + MAP.pen[2]) / 2), my(MAP.pen[3]) + 6, { sc: 0.7 });
  if (fete.state === 'asked') drawSpr('port/balloon', 0, mx(MAP.goal[0]), my(MAP.goal[1]) - 10, { sc: 0.55 });
  // personnages déjà vus qui ont quelque chose à dire : leur « ! » (demande, remerciements) ou « ? » (quête en cours)
  const bob = Math.sin(performance.now() / 260) * 3;
  for (const n of npcList()) {
    const m = NPC_DO[n.kind].mark(), f = m >= 0 && ATLAS['hud/talk'] && ATLAS['hud/talk'].f[m];
    if (!f || !seenAt(n.x / TS, n.y / TS)) continue;
    drawSpr('hud/talk', m, mx(n.x) - f[2] * MAPV.mark / 2, my(n.y) - f[3] * MAPV.mark - 4 + bob, { sc: MAPV.mark });
  }
  const pulse = 1 + Math.sin(performance.now() / 180) * 0.08;
  ctx.save(); ctx.translate(mx(P.x), my(P.y) - 18); ctx.scale(0.62 * pulse, 0.62 * pulse);
  drawSpr('hud/portrait_tecky', 0, -48, -48);
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
// v : version de la sauvegarde ; v2 = la carte agrandie (96 x 64) : une partie de l'ancienne carte ne se reprend pas
const SAVE_V = 2;
function loadSave() { const s = !essai && STORE.get(SAVE_KEY); return s && s.v === SAVE_V ? s : null; }
const r1 = v => Math.round(v * 10) / 10;
function saveGame() {
  if (essai || !P || P.mode === 'ko' || P.hp <= 0 || alice.found) return;
  STORE.set(SAVE_KEY, {
    v: SAVE_V, mode: gameMode, diff: gameDiff, at: Date.now(), x: r1(P.x), y: r1(P.y), dir: P.dir, hp: P.hp, hpMax: P.hpMax,
    score, time: r1(timePlayed), fled, treasures, clues: clues.slice(), sniffed: aliceSniffed, immune: barkImmuneSeen,
    dug: digs.map(g => g.dug ? 1 : 0),
    items: items.map(it => [it.n, r1(it.x), r1(it.y)]),
    dogs: dogs.filter(d => d.mode !== 'ko').map(d => d.id),
    friends: dogs.filter(d => d.friend).map(d => d.id),        // balade : chiens devenus copains
    farm: farm.state, hens: questHens().map(h => [r1(h.hx), r1(h.hy), h.penned ? 1 : 0]),
    seen: Array.from(seenCells).join(''),
    critters: critters.map(c => c.scored ? 1 : 0).join(''),
    ducks: ducks.map(d => d.scored ? 1 : 0).join(''),
    post: post.state, letters: letters.map(l => l.got ? 1 : 0).join(''),
    rose: rose.state, cat: [r1(pompon.x), r1(pompon.y), pompon.mode], bitten,
    fete: fete.state, balls: balls.map(b => [r1(b.x), r1(b.y), b.inNet ? 1 : 0]),
    jouets: jouets.state, toys: toys.map(t => t.carried ? [r1(P.x), r1(P.y), 0] : [r1(t.x), r1(t.y), t.home ? 1 : 0]),
    train: train.scored ? 1 : 0,
    piq: piq.state, babies: babies.map(b => [r1(b.x), r1(b.y), b.mode === 'follow' ? 'wait' : b.mode, b.slot]),
  });
}
// pas de sauvegarde automatique en plein combat : on reprendrait au milieu des crocs
const safeToSave = () => P.mode !== 'ko' && (balade() || !dogs.some(d => ENGAGED.has(d.mode) && dist(P.x, P.y, d.x, d.y) < 600));
function saveOnLeave() { if (P && (state === 'play' || state === 'dialog' || state === 'pause' || (state === 'options' && optReturn === 'pause'))) saveGame(); }
addEventListener('pagehide', saveOnLeave);
document.addEventListener('visibilitychange', () => { if (document.hidden) { saveOnLeave(); onLeave(); } });

/* rested : reprise après un KO (Tecky a fait une sieste : vie pleine) */
function loadGame(s, rested) {
  transition();
  gameDiff = s.diff === 'facile' ? 'facile' : 'normal';
  reset();
  gameMode = s.mode === 'balade' ? 'balade' : 'aventure';
  Object.assign(P, { x: s.x, y: s.y, dir: s.dir || 'down', hpMax: s.hpMax, hp: rested ? s.hpMax : Math.max(1, s.hp) });
  score = s.score; timePlayed = s.time; fled = s.fled; treasures = s.treasures;
  clues = [0, 1, 2].map(i => !!s.clues[i]); aliceSniffed = !!s.sniffed; barkImmuneSeen = !!s.immune;
  digs.forEach((g, i) => { g.dug = !!s.dug[i]; });
  items = s.items.map(([n, x, y]) => ({ n, x, y, t: Math.random() * 3 }));
  dogs = dogs.filter(d => s.dogs.includes(d.id));
  for (const d of dogs) d.friend = (s.friends || []).includes(d.id);
  farm.state = s.farm || 'new';
  if (s.seen) for (let i = 0; i < seenCells.length; i++) seenCells[i] = s.seen[i] === '1' ? 1 : 0;
  critters.forEach((c, i) => { c.scored = (s.critters || '')[i] === '1'; });
  ducks.forEach((d, i) => { d.scored = (s.ducks || '')[i] === '1'; });
  post.state = s.post || 'new';
  letters.forEach((l, i) => { l.got = (s.letters || '')[i] === '1'; });
  rose.state = s.rose || 'new';
  fete.state = s.fete || 'new';
  (s.balls || []).forEach((q, i) => { const b = balls[i]; if (b && q) { b.x = q[0]; b.y = q[1]; b.inNet = !!q[2]; } });
  jouets.state = s.jouets || 'new';
  train.scored = !!s.train;
  piq.state = s.piq || 'new';
  (s.babies || []).forEach((q, i) => { const b = babies[i]; if (b && q) { b.x = q[0]; b.y = q[1]; b.mode = q[2]; b.slot = q[3] || 0; } });
  (s.toys || []).forEach((q, i) => { const t = toys[i]; if (t && q) { t.x = q[0]; t.y = q[1]; t.home = !!q[2]; } });
  bitten = !!s.bitten || rested;
  if (s.cat) { pompon.x = s.cat[0]; pompon.y = s.cat[1]; pompon.mode = s.cat[2] === 'follow' ? 'wait' : s.cat[2]; }
  questHens().forEach((h, i) => { const q = (s.hens || [])[i]; if (q) { h.x = h.hx = q[0]; h.y = h.hy = q[1]; h.penned = !!q[2]; } });
  if (nextClue() === 3) revealAlice();
  sun = sunGoal();
  camX = camClampX(P.x - VW / 2);
  camY = camClampY(P.y - 40 - VH / 2);
  state = 'play';
  Music.start();
  say([{ who: 'tecky', face: rested ? 0 : 2, text: rested ? "Ouf, une petite sieste et ça repart !" : "Me revoilà ! Je reprends mes recherches." },
       { who: 'tecky', face: 0, text: CLUE_NEXT[nextClue()] }], () => showArrow());
}
function newGame(mode, again) {
  transition();
  const cx = camX, cy = camY;
  gameDiff = opts.diff;
  reset();
  gameMode = mode;
  if (!again) { camX = cx; camY = cy; }          // depuis l'écran titre, la caméra glisse du village jusqu'à la niche
  state = 'play';
  Music.start();
  say(again ? [{ who: 'tecky', face: 0, text: "C'est reparti ! Je vais retrouver les affaires d'Alice, et Alice avec." }] : introLines(),
    () => { showArrow(); saveGame(); });
}

let recs = {}, newRecord = { score: false, time: false, done: false }, winDone = 0;
const recKey = (mode, diff) => mode + (diff === 'facile' ? '-facile' : '');     // records à part en facile
function recordRun() {
  const all = STORE.get(RECORDS_KEY) || {}, k = recKey(gameMode, gameDiff), r = all[k] || {}, t = Math.floor(timePlayed);
  winDone = completion();               // (calculée une fois : la scène de fin renvoie des chiens chez eux)
  newRecord = { score: !(r.score >= score), time: !(r.time <= t), done: !(r.done >= winDone) };
  if (newRecord.score) r.score = score;
  if (newRecord.time) r.time = t;
  if (newRecord.done) r.done = winDone;
  r.wins = (r.wins || 0) + 1;
  all[k] = r;
  STORE.set(RECORDS_KEY, all);
  recs = all;
}
const fmtTime = t => Math.floor(t / 60) + ' min ' + String(Math.floor(t % 60)).padStart(2, '0') + ' s';
const MODE_NAME = { aventure: 'Aventure', balade: 'Balade' };
function recordLine(mode) {
  const r = recs[recKey(mode, opts.diff)];
  if (!r || !r.wins) return '';
  return 'Records en ' + mode + (opts.diff === 'facile' ? ' facile' : '') + ' : ' + r.score + ' points · ' + fmtTime(r.time) +
    (r.done >= 0 ? ' · ' + r.done + '\u00a0%' : '');
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
      sub: MODE_NAME[s.mode] + (s.diff === 'facile' ? ' facile' : '') + ' · ' + (n ? n + (n > 1 ? ' indices' : ' indice') + ' sur 3' : 'aucun indice') + ' · ' + fmtTime(s.time) });
  }
  items.push({ id: 'aventure', label: 'Nouvelle aventure', sub: 'Gare aux chiens du coin !', mode: 'aventure' });
  items.push({ id: 'balade', label: 'Nouvelle balade', sub: 'Les chiens veulent seulement jouer', mode: 'balade' });
  items.push({ id: 'options', label: 'Options', sub: 'Son, difficulté, texte, météo…' });
  items.push({ id: 'badges', label: 'Badges', sub: badgeCount() + ' sur ' + MAP.badges.length + ' gagnés' });
  menu = items.length > 4 ? { items, sel: 0, y0: 500, w: 760, h: 80, gap: 12 } : { items, sel: 0, y0: 506, w: 760, h: 88, gap: 14 };
}
function openOverMenu() {
  const items = [];
  if (loadSave()) items.push({ id: 'resume', label: 'Reprendre la partie', sub: 'Après une petite sieste, avec les indices trouvés' });
  items.push({ id: 'restart', label: 'Recommencer', sub: 'Depuis la niche, sans les indices' });
  items.push({ id: 'title', label: 'Menu principal', sub: 'Pour changer de mode' });
  menu = { items, sel: 0, y0: 600, w: 760, h: 96, gap: 18 };
}
function openPauseMenu() {             // sous la carte de la pause, en ligne
  menu = { items: [{ id: 'unpause', label: 'Reprendre' }, { id: 'options', label: 'Options' }, { id: 'quit', label: 'Menu principal' }],
    sel: 0, y0: 912, w: 380, h: 78, gap: 30, row: true };
}
function menuBox(i) {
  if (menu.row) {
    const n = menu.items.length, tw = n * menu.w + (n - 1) * menu.gap;
    return { x: GW / 2 - tw / 2 + i * (menu.w + menu.gap), y: menu.y0, w: menu.w, h: menu.h };
  }
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
  if (pressed.up || (menu.row && pressed.left)) { menu.sel = (menu.sel + n - 1) % n; SFX.blip(); }
  if (pressed.down || (menu.row && pressed.right)) { menu.sel = (menu.sel + 1) % n; SFX.blip(); }
  return pressed.ok || pressed.bark || pressed.bite || pressed.act ? menu.items[menu.sel].id : null;
}
function chooseMenu(id) {
  const s = loadSave();
  menu = null;
  if (id === 'continue' && s) loadGame(s, false);
  else if (id === 'resume' && s) loadGame(s, true);
  else if (id === 'restart') newGame(gameMode, true);
  else if (id === 'aventure' || id === 'balade') newGame(id, false);
  else if (id === 'options') openOptions(state);
  else if (id === 'badges') openBadges();
  else if (id === 'unpause') { state = 'play'; Music.refresh(); }
  else if (id === 'quit') { saveGame(); toTitle(); }
  else toTitle();
}
/* Essai depuis l'éditeur de carte : editeur.py sert web/essai.html, le jeu précédé de const ESSAI = [x, y, mode]
   (en tuiles). La partie commence là, sans écran titre ni intro, et rien n'est sauvegardé. */
const essai = typeof ESSAI !== 'undefined' ? ESSAI : null;
function startEssai() {
  gameDiff = opts.diff;
  reset();
  gameMode = essai[2] === 'balade' ? 'balade' : 'aventure';
  Object.assign(P, { x: essai[0] * TS, y: essai[1] * TS });
  camX = camClampX(P.x - VW / 2); camY = camClampY(P.y - VH / 2);
  state = 'play';
  Music.start();
}
// l'écran titre joue toujours le thème d'origine (« base »), quelle que soit la zone de la partie quittée
const TITLE_MUSIC = 'niche';
function toTitle() {
  transition();
  reset();
  gameMode = 'aventure';
  camX = camClampX(MAP.title[0] - VW / 2);   // caméra de l'écran titre : la place du village
  camY = camClampY(MAP.title[1] - VH / 2);
  state = 'title'; titleT = 0;
  openTitleMenu();
  if (Music.on && Music.cur !== 'main') Music.stop();     // la berceuse de la fin, la musique de défaite
  Music.setZone(TITLE_MUSIC, true);                       // (arrêtée : retient seulement la zone)
  Music.start();
}

/* ------------------------------------------------------------------ vibrations */
/* Option « Vibrations » : la manette (vibrationActuator, si c'est elle qui sert) ou le téléphone (navigator.vibrate, au
   toucher) vibrent quand Tecky est mordu ou heurté, plus fort au KO, et d'un petit coup quand sa morsure porte ou qu'un
   os doré sort de terre. RUMBLE : [force du gros moteur, du petit, durée en ms]. */
const RUMBLE = { hurt: [0.7, 0.4, 180], ko: [1, 0.8, 450], bump: [0.5, 0.6, 220], bite: [0.25, 0.35, 70], treasure: [0.2, 0.5, 120] };
function rumble(kind) {
  if (opts.vib === 'non') return;
  const [strong, weak, ms] = RUMBLE[kind];
  try {
    if (pad.on) {
      for (const gp of (navigator.getGamepads && navigator.getGamepads()) || []) {
        const a = gp && gp.vibrationActuator;
        if (!a || !a.playEffect) continue;
        const p = a.playEffect('dual-rumble', { duration: ms, strongMagnitude: strong, weakMagnitude: weak });
        if (p && p.catch) p.catch(() => {});
      }
    } else if (touchMode && navigator.vibrate) navigator.vibrate(Math.round(ms * (0.4 + strong * 0.6)));
  } catch (e) { /* vibrations refusées par le navigateur */ }
}

/* ------------------------------------------------------------------ badges */
/* Douze badges (MAP.badges, même ordre que hud.BADGES : image i de hud/badge, la dernière = verrouillé), gardés dans le
   navigateur d'une partie à l'autre (BADGES_KEY). checkBadges() regarde la partie toutes les demi-secondes ; la
   victoire débloque aussi « aventure », « intact » (sans morsure, bitten) et « rapide ». À chaque nouveau badge, une
   annonce en haut de l'écran (toasts). Écran « Badges » depuis le menu principal ; nouveaux badges rappelés à la fin. */
const BADGES_KEY = 'tecky-quest-badges';
const BADGE_INFO = {
  aventure: ['Retrouvailles', 'Retrouver Alice en mode aventure.'],
  copains: ['Copain de tous', 'En balade, devenir copain avec tous les chiens.'],
  os_dores: ['Chercheur d’or', 'Déterrer tous les os dorés.'],
  intact: ['Sans une égratignure', 'Retrouver Alice en aventure sans se faire mordre.'],
  rapide: ['Truffe rapide', 'Retrouver Alice en moins de 10 minutes.'],
  poules: ['Chien de berger', 'Ramener toutes les poules de Gaston.'],
  facteur: ['Facteur en herbe', 'Rapporter ses cinq lettres à Marcel.'],
  chat: ['Ami des chats', 'Ramener Pompon à Mamie Rose.'],
  betes: ['Curieux', 'Surprendre tous les écureuils et les chats.'],
  canards: ['Coin-coin', 'Faire s’envoler tous les canards.'],
  explorateur: ['Explorateur', 'Découvrir toute la carte.'],
  sieste: ['Roi de la sieste', 'Laisser Tecky s’endormir.'],
  ballons: ['Champion du ballon', 'Pousser tous les ballons de Léon dans le filet.'],
  iris: ['Va chercher !', 'Rapporter ses trois jouets à Iris.'],
  train: ['Tchou-tchou !', 'Faire siffler Titine, le petit train du port.'],
  herissons: ['Nounou des hérissons', 'Ramener ses trois petits à Maman Piquette.'],
};
const TOAST = { life: 3.6 };
let badges = {}, toasts = [], newBadges = [], badgeT = 0, bitten = false;
function loadBadges() { badges = STORE.get(BADGES_KEY) || {}; }
const badgeCount = () => MAP.badges.filter(id => badges[id]).length;
function unlockBadge(id) {
  if (badges[id]) return;
  badges[id] = Date.now();
  STORE.set(BADGES_KEY, badges);
  newBadges.push(id); toasts.push({ id, t: 0 });
  SFX.badge();
}
function checkBadges() {
  if (balade() && dogs.length && dogs.every(d => d.friend)) unlockBadge('copains');
  if (treasures >= MAP.dig.length) unlockBadge('os_dores');
  if (farm.state === 'done') unlockBadge('poules');
  if (post.state === 'done') unlockBadge('facteur');
  if (rose.state === 'done') unlockBadge('chat');
  if (fete.state === 'done') unlockBadge('ballons');
  if (jouets.state === 'done') unlockBadge('iris');
  if (train.scored) unlockBadge('train');
  if (piq.state === 'done') unlockBadge('herissons');
  if (critters.every(c => c.scored)) unlockBadge('betes');
  if (ducks.filter(d => !d.lead).every(d => d.scored)) unlockBadge('canards');
  if (seenCells.reduce((a, v) => a + v, 0) >= seenCells.length * 0.95) unlockBadge('explorateur');
  if (napped) unlockBadge('sieste');
}
/* Complétion de la partie (écran de victoire), en % : moyenne de catégories qui comptent toutes autant — os dorés, quêtes,
   petites bêtes, canards, carte explorée (95 % suffisent, comme pour le badge), et les copains en balade. Une nouvelle
   quête : l'ajouter à QUESTS_DONE. */
const QUESTS_DONE = [() => farm.state === 'done', () => post.state === 'done', () => rose.state === 'done',
  () => fete.state === 'done', () => jouets.state === 'done', () => piq.state === 'done'];
function completion() {
  const part = (n, of) => of ? Math.min(1, n / of) : 1, count = (a, f) => a.filter(f).length;
  const adults = ducks.filter(d => !d.lead);          // comme le badge : sans les canetons
  const parts = [part(treasures, MAP.dig.length), part(count(QUESTS_DONE, q => q()), QUESTS_DONE.length),
    part(count(critters, c => c.scored), critters.length), part(count(adults, d => d.scored), adults.length),
    part(seenCells.reduce((a, v) => a + v, 0), seenCells.length * 0.95)];
  if (balade()) parts.push(part(count(dogs, d => d.friend), dogs.length));
  return Math.floor(100 * parts.reduce((a, v) => a + v, 0) / parts.length);
}
function winBadges() {
  if (!balade()) { unlockBadge('aventure'); if (!bitten) unlockBadge('intact'); }
  if (timePlayed < 600) unlockBadge('rapide');
  checkBadges();
}
function updateToasts(dt) {
  if (toasts.length && (toasts[0].t += dt) > TOAST.life) toasts.shift();
}
function drawToast() {                // « Nouveau badge ! » en haut de l'écran
  const T = toasts[0];
  if (!T) return;
  guiTransform();
  const a = clamp(Math.min(T.t / 0.3, (TOAST.life - T.t) / 0.5), 0, 1), w = 640, h = 120, x = GW / 2 - w / 2;
  const y = 196 - (1 - Math.min(1, T.t / 0.3)) * 30;
  ctx.save(); ctx.globalAlpha = a;
  drawNine('hud/panel', x, y, w, h, 32);
  drawSpr('hud/badge', MAP.badges.indexOf(T.id), x + 18, y + 12, { sc: 1 });
  text('Nouveau badge !', x + 130, y + 48, 28, '#D7332B', 'left', 600);
  text(BADGE_INFO[T.id][0], x + 130, y + 90, 36, '#3A1E12', 'left', 700);
  ctx.restore();
}
// écran des badges : 4 x 3 cartes ; ceux qu'il reste à gagner sont en gris, avec leur objectif
function openBadges() { menu = null; state = 'badges'; }
function closeBadges() { state = 'title'; openTitleMenu(); menu.sel = menu.items.findIndex(it => it.id === 'badges'); }
function badgesInput() { if (pressed.pause || pressed.bark || pressed.ok || pressed.bite || pressed.act) closeBadges(); }
function drawBadges() {
  guiTransform();
  veil(0.6);
  outlined('Badges : ' + badgeCount() + ' / ' + MAP.badges.length, GW / 2, 118, 64, '#FFF7E6');
  // trois rangées de quatre au plus : grandes cases ; au-delà (jusqu'à 16 badges), cases plus compactes
  const big = MAP.badges.length <= 12, sc = big ? 1 : 0.76;
  const cw = 420, ch = big ? 236 : 196, gx = 26, gy = big ? 22 : 14, x0 = GW / 2 - (4 * cw + 3 * gx) / 2, y0 = 168;
  MAP.badges.forEach((id, i) => {
    const x = x0 + (i % 4) * (cw + gx), y = y0 + Math.floor(i / 4) * (ch + gy), got = !!badges[id];
    drawNine(got ? 'hud/panel' : 'hud/panel_dark', x, y, cw, ch, 32);
    drawSpr('hud/badge', got ? i : MAP.badges.length, x + cw / 2 - 48 * sc, y + (big ? 14 : 8), { sc });
    text(got ? BADGE_INFO[id][0] : '?', x + cw / 2, y + (big ? 144 : 112), 30, got ? '#3A1E12' : '#FFF7E6', 'center', 700);
    para(BADGE_INFO[id][1], x + cw / 2, y + (big ? 180 : 146), 22, got ? '#6B5A4E' : '#E9DCC8', 'center', 500, cw - 50, 28);
  });
  text(touchMode ? 'Touche l’écran pour revenir' : '[back] pour revenir', GW / 2, GH - 30, 26, '#E9DCC8', 'center', 500);
}

/* ------------------------------------------------------------------ écran d'options */
/* Réglages gardés dans le navigateur (OPTIONS_KEY, lus au démarrage) : volumes de la musique et des bruitages (0 à 10),
   difficulté (« facile », pour les nouvelles parties), taille du texte des dialogues, image (« fluide » : canvas
   plafonné à MAX_PIXELS ; « nette » : pleine résolution, pour les machines rapides), vibrations, météo, plein écran. Ouvert depuis le menu
   principal ou le menu de la pause. Flèches ↑ ↓ pour choisir une ligne, ← → pour la régler (Entrée / A aussi),
   Échap / B pour revenir ; au toucher, la moitié gauche d'une ligne baisse, la moitié droite monte. */
const OPTV = { y0: 196, w: 1120, h: 76, gap: 10, hTight: 68, gapTight: 8 };
let optSel = 0, optReturn = 'title';
function optRows() {
  const rows = [
    { id: 'music', label: 'Musique', level: true },
    { id: 'sfx', label: 'Bruitages', level: true },
    { id: 'diff', label: 'Difficulté', values: [['normal', 'Normale'], ['facile', 'Facile']],
      note: opts.diff === 'facile' ? '5 os au départ, morsures moins fortes, moins de chiens' : 'Pour les nouvelles parties' },
    { id: 'text', label: 'Texte des dialogues', values: [['normal', 'Normal'], ['grand', 'Grand']] },
    { id: 'image', label: 'Image', values: [['fluide', 'Fluide'], ['nette', 'Nette']],
      note: opts.image === 'nette' ? 'Pleine résolution : pour les ordinateurs rapides' : 'Plus légère sur les grands écrans' },
    { id: 'vib', label: 'Vibrations', values: [['oui', 'Oui'], ['non', 'Non']], note: 'Manette et téléphone' },
    { id: 'weather', label: 'Météo', values: [['auto', 'Auto'], ['soleil', 'Soleil'], ['pluie', 'Pluie'], ['neige', 'Neige']],
      note: opts.weather === 'auto' ? 'Une averse de temps en temps, de la neige en décembre' : '' },
  ];
  if (canFullscreen()) rows.push({ id: 'fs', label: 'Plein écran', value: fsElement() ? 'Oui' : 'Non',
    note: performance.now() - fsRefusedAt < FS_REFUSED_NOTE ? 'Ce navigateur le refuse à la manette : [fs] au clavier, ou un clic ici' : '' });
  // remise à zéro : seulement depuis l'écran titre (en jeu, la partie se resauvegarderait aussitôt) ; elle demande
  // confirmation, « Non » d'abord (resetAsk)
  if (optReturn === 'title') rows.push(resetAsk ? { id: 'reset', label: 'Tout effacer ?', ask: true, note: 'Partie en cours, records et badges' }
    : { id: 'reset', label: 'Réinitialiser la progression', value: '', note: 'Efface la partie en cours, les records et les badges' });
  rows.push({ id: 'back', label: 'Retour' });
  return rows;
}
let resetAsk = null, resetDoneAt = -1e9;        // { yes } pendant la confirmation ; heure de la dernière remise à zéro
const RESET_NOTE = 2600;                        // ms d'affichage de « Progression effacée »
function resetProgress() {
  STORE.del(SAVE_KEY); STORE.del(RECORDS_KEY); STORE.del(BADGES_KEY);
  badges = {}; recs = {}; newRecord = { score: false, time: false, done: false }; newBadges = [];
  resetAsk = null; resetDoneAt = performance.now();
  SFX.hurt();
}
function resetChoose(r) {                       // valider la ligne de remise à zéro
  if (!resetAsk) { resetAsk = { yes: false }; SFX.blip(); }
  else if (resetAsk.yes) resetProgress();
  else { resetAsk = null; SFX.blip(); }
}
function openOptions(from) { optReturn = from === 'pause' ? 'pause' : 'title'; optSel = 0; menu = null; state = 'options'; resetAsk = null; Music.refresh(); }
function closeOptions() {
  state = optReturn; resetAsk = null;
  if (state === 'title') { openTitleMenu(); menu.sel = menu.items.findIndex(it => it.id === 'options'); }
  else { openPauseMenu(); menu.sel = 1; }
  Music.refresh();
}
function changeOpt(r, dir) {
  if (r.id === 'reset') { if (resetAsk) { resetAsk.yes = dir > 0; SFX.blip(); } return; }
  if (r.level) opts[r.id] = clamp(opts[r.id] + dir, 0, 10);
  else if (r.values) {
    const v = r.values.map(x => x[0]), i = Math.max(0, v.indexOf(opts[r.id]));
    opts[r.id] = v[(i + (dir < 0 ? v.length - 1 : 1)) % v.length];
  } else return;
  STORE.set(OPTIONS_KEY, opts);
  if (r.id === 'image') resize();
  if (r.id === 'weather') weather.timer = Math.min(weather.timer, 2);
  Music.refresh();
  SFX.blip();
}
function optionsInput() {
  const rows = optRows(), n = rows.length;
  optSel = Math.min(optSel, n - 1);
  if (pressed.up) { optSel = (optSel + n - 1) % n; SFX.blip(); resetAsk = null; }
  if (pressed.down) { optSel = (optSel + 1) % n; SFX.blip(); resetAsk = null; }
  const r = rows[optSel];
  if (r.id === 'fs') {                 // (au clavier, déjà fait dans l'événement : ici, la manette)
    if (pressed.left || pressed.right || pressed.ok || pressed.bite || pressed.act) toggleFullscreen();
  } else {
    if (pressed.left) changeOpt(r, -1);
    if (pressed.right) changeOpt(r, 1);
  }
  if ((pressed.ok || pressed.bite || pressed.act) && r.id !== 'fs') {
    if (r.id === 'back') { closeOptions(); return; }
    if (r.id === 'reset') { resetChoose(r); return; }
    changeOpt(r, r.level && opts[r.id] >= 10 ? -10 : 1);     // Entrée / A : on monte, puis on repart de 0
  }
  if (pressed.pause || pressed.bark) closeOptions();
}
function optBox(i, n) {                // plus serré quand il y a beaucoup de lignes (remise à zéro, plein écran)
  const h = n > 9 ? OPTV.hTight : OPTV.h, gap = n > 9 ? OPTV.gapTight : OPTV.gap;
  return { x: GW / 2 - OPTV.w / 2, y: OPTV.y0 + i * (h + gap), w: OPTV.w, h };
}
// au toucher, pendant la confirmation : « Non » et « Oui » sont deux cases à droite de la ligne
const resetPills = b => [{ yes: false, x: b.x + b.w - 330, w: 130 }, { yes: true, x: b.x + b.w - 180, w: 130 }];
function optionsTap(gx, gy) {         // toucher / clic : appelé directement par l'événement (plein écran permis)
  const rows = optRows();
  for (let i = 0; i < rows.length; i++) {
    const b = optBox(i, rows.length), r = rows[i];
    if (gx < b.x || gx > b.x + b.w || gy < b.y || gy > b.y + b.h) continue;
    if (i !== optSel) resetAsk = null;
    optSel = i;
    if (r.id === 'reset') {
      const p = resetAsk && resetPills(b).find(q => gx >= q.x && gx <= q.x + q.w);
      if (!resetAsk) resetChoose(r);
      else if (p && p.yes) resetProgress();
      else { resetAsk = null; SFX.blip(); }
      return;
    }
    if (r.id === 'back') closeOptions();
    else if (r.id === 'fs') toggleFullscreen();
    else changeOpt(r, r.level && gx < b.x + b.w * 0.6 ? -1 : 1);
    return;
  }
}
function arrowHead(x, y, dir, size, color) {   // petit triangle ◀ ▶ (la police n'a pas ces signes)
  ctx.fillStyle = color;
  ctx.beginPath(); ctx.moveTo(x + dir * size, y); ctx.lineTo(x - dir * size * 0.6, y - size); ctx.lineTo(x - dir * size * 0.6, y + size);
  ctx.closePath(); ctx.fill();
}
function drawOptions() {
  guiTransform();
  veil(0.55);
  outlined('Options', GW / 2, 128, 68, '#FFF7E6');
  if (performance.now() - resetDoneAt < RESET_NOTE) outlined('Progression effacée', GW / 2, 178, 32, '#F2C14E');
  const rows = optRows();
  rows.forEach((r, i) => {
    const b = optBox(i, rows.length), sel = i === optSel, ink = sel ? '#3A1E12' : '#FFF7E6', soft = sel ? '#6B5A4E' : '#E9DCC8';
    drawNine(sel ? 'hud/panel' : 'hud/panel_dark', b.x, b.y, b.w, b.h, 32);
    const cy = b.y + b.h / 2, vx = b.x + b.w - 44;
    if (r.id === 'back') { text(r.label, GW / 2, cy + 13, 36, ink, 'center', 700); return; }
    text(r.label, b.x + 44, r.note ? cy - 2 : cy + 12, 34, ink, 'left', 600);
    if (r.note) text(r.note, b.x + 44, cy + 26, 21, soft, 'left', 500);
    if (r.ask) {                                       // confirmation : « Non » / « Oui », le choix en couleur
      resetPills(b).forEach(q => {
        const on = resetAsk.yes === q.yes;
        ctx.fillStyle = on ? (q.yes ? '#D7332B' : '#4E9A47') : (sel ? '#E3D3B8' : 'rgba(255, 247, 230, 0.22)');
        ctx.fillRect(q.x, cy - 24, q.w, 48);
        text(q.yes ? 'Oui' : 'Non', q.x + q.w / 2, cy + 12, 32, on ? '#FFF7E6' : ink, 'center', 700);
      });
      return;
    }
    if (r.level) {                                     // dix crans
      for (let k = 0; k < 10; k++) {
        ctx.fillStyle = k < opts[r.id] ? (sel ? '#E07A2E' : '#F2C14E') : (sel ? '#E3D3B8' : 'rgba(255, 247, 230, 0.22)');
        ctx.fillRect(vx - 330 + k * 34, cy - 15, 26, 30);
      }
      text(String(opts[r.id]), vx - 352, cy + 12, 32, ink, 'right', 600);
    } else {
      const label = r.values ? (r.values.find(v => v[0] === opts[r.id]) || r.values[0])[1] : r.value;
      ctx.font = '600 34px Fredoka, "Trebuchet MS", sans-serif';
      const w = ctx.measureText(label).width;
      text(label, vx - 34, cy + 12, 34, ink, 'right', 600);
      if (r.values) { arrowHead(vx - 8, cy, 1, 11, ink); arrowHead(vx - 58 - w, cy, -1, 11, ink); }
    }
  });
  text(touchMode ? 'Touche une ligne pour la régler (à gauche : moins, à droite : plus)' : pad.on ? '[arrows] : choisir et régler · [back] : retour' :
    '[updown] : choisir · [leftright] : régler · [back] : retour', GW / 2, GH - 34, 26, '#E9DCC8', 'center', 500);
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

/* Tecky au repos : quand on ne touche à rien, il s'assoit (REST.sit s), bâille ou se gratte de temps en temps, puis
   s'endort (REST.sleep s) avec des « z » qui montent (fx/zzz). Le moindre geste le réveille. Jamais quand un chien le
   menace. Vues : assis, bâille et dort de face ou de profil (de dos, il se tourne vers nous) ; il se gratte de profil. */
const REST = { sit: 6, sleep: 24, every: [3, 6.5], z: 0.95, snore: 2.6 };
let napped = false;                   // il a fait la sieste (badge)
// Tecky endormi : des « z » qui montent, et un ronflement de temps en temps (quiet : sans le son)
function snooze(dt, quiet) {
  if ((P.zT -= dt) <= 0) {
    P.zT = REST.z;
    const side = P.dir === 'left' ? -1 : 1;
    addFx('fx/zzz', P.x + side * (P.dir === 'down' ? 18 : 30), P.y - 52, { fps: 0, frame: 0, life: 2, vx: side * 12, vy: -34, grow: [0.55, 1.1] });
  }
  if ((P.snoreT -= dt) <= 0) { P.snoreT = REST.snore; if (!muted && !quiet) SFX.snore(); }
}
function restPose(dt) {
  if (threatened()) { P.restT = 0; P.setAnim('idle'); return; }
  P.restT = (P.restT || 0) + dt;
  if (P.restT < REST.sit) { P.setAnim('idle'); return; }
  if (P.dir === 'up') P.dir = 'down';
  if (P.restT >= REST.sleep) {
    if (P.anim !== 'sleep') { P.setAnim('sleep'); P.zT = 0.4; P.snoreT = 1; napped = true; }
    snooze(dt, false);
    return;
  }
  // assis ; de temps en temps, un bâillement ou une grattouille derrière l'oreille (à tour de rôle)
  const busy = (P.anim === 'yawn' && !P.done()) || (P.anim === 'scratch' && P.t < 1.3);
  if (!busy && P.anim !== 'sit') { P.setAnim('sit'); P.restEv = rnd(REST.every); }
  if (P.anim === 'sit' && (P.restEv -= dt) <= 0) {
    P.lastRest = P.lastRest === 'yawn' ? 'scratch' : P.lastRest === 'scratch' ? 'yawn' : Math.random() < 0.5 ? 'yawn' : 'scratch';
    if (P.lastRest === 'yawn') { P.setAnim('yawn'); if (!muted) SFX.yawn(); }
    else { if (P.dir === 'down') P.dir = Math.random() < 0.5 ? 'left' : 'right'; P.setAnim('scratch'); }
  }
}
function updatePlayer(dt) {
  P.t += dt;
  hintText = null;
  digHint = null;
  playHint = null;
  tunnelHint = null;
  talkHint = null;
  P.inv = Math.max(0, P.inv - dt);
  P.bumpT = Math.max(0, P.bumpT - dt);           // une voiture ne bouscule Tecky qu'une fois à la fois
  P.cdBark = Math.max(0, P.cdBark - dt);
  P.cdBite = Math.max(0, P.cdBite - dt);
  P.cdSniff = Math.max(0, P.cdSniff - dt);
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
  if (P.mode === 'shake') {
    if (!P.drops2 && P.t * FPS.shake >= P.frames() / 2) { P.drops2 = true; shakeDrops(0.5); }   // 2e secousse
    if (P.done()) P.mode = 'free';
    return;
  }
  if (shakePending && P.mode === 'free') { shakePending = false; startShake(); return; }
  if (P.mode === 'tunnel') { updateTunnel(dt); return; }
  if (P.mode === 'sniff') {
    P.timer -= dt;
    P.hop = Math.abs(Math.sin(P.timer * 14)) * 3;       // petits coups de truffe
    if (P.timer <= 0) { P.mode = 'free'; P.hop = 0; layTrail(); }
    return;
  }
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
  recordCrumb();
  const [ix, iy] = inputVector();
  const spd = 250;
  if (pressed.sniff || pressed.bark || pressed.bite || pressed.act) P.restT = 0;
  if (ix || iy) {
    P.restT = 0;
    const ox = P.x, oy = P.y;
    moveActor(P, ix * spd * dt, iy * spd * dt);
    edgeBump(dt, ix, iy, ox, oy);
    P.dir = dirFrom(ix, iy, P.dir);
    P.setAnim('walk');
    puddleSplash(dt);
    // petits nuages de poussière derrière les pattes
    if ((P.dustT = (P.dustT || 0) - dt) <= 0 && Math.hypot(P.x - ox, P.y - oy) > spd * dt * 0.5) {
      P.dustT = DUST.every;
      addDust(P.x - ix * 16 + (Math.random() - 0.5) * 10, P.y - 2, -ix * 30, -iy * 30 - 6, 5 + Math.random() * 3);
    }
  } else { P.edgeT = 0; restPose(dt); }

  if (pressed.sniff && P.cdSniff <= 0 && !alice.found) startSniff();
  else if (pressed.bark && P.cdBark <= 0) {
    P.mode = 'bark'; P.setAnim('bark'); P.cdBark = 1.0; P.cdBarkMax = 1.0; doBark();
  } else if (pressed.bite) {
    const a = biteAction();
    if (a === 'read') say([{ who: 'info', text: nearSign()[2] }]);
    else if (a === 'talk') talkTo(nearNpc());
    else if (P.cdBite <= 0) {
      if (a === 'play') startPlay(playDog());
      else if (a === 'tunnel') startTunnel(nearTunnel());
      else if (a === 'dig') startDig(nearDig());
      else { P.mode = 'bite'; P.setAnim('bite'); P.cdBite = 0.5; P.cdBiteMax = 0.5; P.hitDone = false; }
    }
  }

  // panneau (C ou E pour lire) et trésor à portée : bulles "lire" / "gratter"
  const sign = nearSign(), act = biteAction();
  if (pressed.act && act === 'talk') talkTo(nearNpc());
  else if (sign && pressed.act) say([{ who: 'info', text: sign[2] }]);
  if (act === 'read') hintText = { x: sign[0], y: sign[1] - 110 };
  if (act === 'dig') digHint = nearDig();
  if (act === 'play') playHint = playDog();
  if (act === 'tunnel') { const t = nearTunnel(); tunnelHint = { x: t.fx, y: t.fy }; }
  if (act === 'talk') { const n = nearNpc(); talkHint = { x: n.x, y: n.y - markY(n) }; }
  updateNpcs();
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
  const calmP = !balade() && calmAt(P.x, P.y);         // Tecky en zone calme : on ne le poursuit pas
  const alive = P.mode !== 'ko' && !calmP;

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
        d.hop = 0; d.calm = PLAY.calm;
        startFollow(d);                // il suit Tecky un moment
        if (!d.friend) {
          d.friend = true; fled++; score += T.score;
          addPop('+' + T.score, d.x - 20, d.y - 120);
          addWordPop('Copain !', d.x, d.y - 150, 'dog');
          SFX.treasure();
        }
      }
      return;
    }
    case 'follow': {                   // balade : un copain suit Tecky en file indienne
      d.followT -= dt;
      if (d.followT <= 0 || !balade()) {
        d.mode = 'return'; d.calm = PLAY.calm; d.hopT = 0.4;
        addFx('fx/heart', d.x, d.y - 96, { fps: 10 });
        return;
      }
      const rank = dogs.filter(o => o.mode === 'follow' && o.followN < d.followN).length;
      const [tx, ty] = crumbAt((rank + 1) * FOLLOW.gap);
      const fx = tx - d.x, fy = ty - d.y, fl = Math.hypot(fx, fy);
      if (fl > 6) {
        const st = Math.min(fl, Math.min(FOLLOW.spd, fl * 5) * dt);
        d.x += fx / fl * st; d.y += fy / fl * st;
        d.dir = dirFrom(fx, fy, d.dir); d.setAnim('walk');
      } else { d.dir = dirFrom(dx, dy, d.dir); d.setAnim('idle'); }
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
      // (heurté par une voiture loin de Tecky : il rentre chez lui, il ne traverse pas la carte pour le poursuivre)
      if (d.timer <= 0) d.mode = dist(d.x, d.y, P.x, P.y) < T.aggro * 1.5 ? 'chase' : 'return';
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
    else if (!alive || l > T.aggro * 1.5 || homeD > 750) {
      if (calmP && l < T.aggro * 1.5) addWordPop('Grrr…', d.x, d.y - 100, 'dog');     // il n'ose pas le suivre plus loin
      d.mode = 'return';
    }
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
    if (dist(P.x, P.y - 10, it.x, it.y + 22) < REACH.item && P.mode !== 'ko') {
      const e = ITEM[it.n];
      if (e.grow) {
        // saucisse : un os de plus, déjà plein
        if (P.hpMax < MAX_BONES * 2) {
          P.hpMax += 2;
          P.boneFx = 1;
          addWordPop('Un os de plus !', P.x, P.y - 140, 'tecky');
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
        if (e.gold) { SFX.treasure(); addWordPop('Os doré !', P.x, P.y - 150, 'tecky'); }
        else if (it.pop === undefined) SFX.pick();
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
    if (f.life ? f.t >= f.life : f.t * f.fps >= ATLAS[f.key].f.length) fxs.splice(i, 1);
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
  winBadges();
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
  ], startEnding);
}

/* ------------------------------------------------------------------ la fin */
/* Après les retrouvailles : fondu au noir, Tecky et Alice remontent le chemin de la niche au coucher du soleil ; la nuit
   tombe (sunGoal() passe à 4) et les lucioles s'allument avec elle ;
   Alice saute de joie, Tecky s'assoit, bâille et s'endort à ses pieds. Un iris se referme sur eux, « Fin », puis l'écran
   de victoire. La berceuse (variation lente du thème) joue jusqu'au retour au menu. Après `skip` s, un bouton passe
   directement à la victoire. Positions en pixels du monde (MAP.ending : Alice devant la niche, Tecky à ses pieds) ;
   `from` : ils partent de ce nombre de pixels sous le bas de l'écran. */
const ENDING = { fade: 1, from: 60, alice: MAP.ending.alice, tecky: MAP.ending.tecky, spd: 105, happy: 1.6, sit: 1.4, yawn: 1.4,
  iris: 9, irisDur: 1.6, irisR: 170, hold: 1.2, close: 0.5, fin: 2.4, skip: 1, flies: 12 };
let ending = null;
function startEnding() {
  state = 'ending'; ending = { t: 0, home: false, flies: [] };
  Music.stop(); Music.start('end');
}
// au noir : tout le monde au bas du chemin de la niche, la caméra fixée sur la niche ; la pluie s'arrête, le soleil se
// couche (la nuit tombe ensuite, à la vitesse de SUN.speed)
function endingHome() {
  const E = ENDING;
  ending.home = true;
  // (cadrage fixe, dans la carte : la lisière n'y entre pas) ; ils arrivent d'un peu plus bas que l'écran (from)
  camX = clamp(E.alice[0] - VW / 2, 0, MAP.w * TS - VW); camY = clamp(E.alice[1] - 40 - VH / 2, 0, MAP.h * TS - VH);
  const y0 = camY + VH + E.from;
  alice.x = E.alice[0]; alice.y = y0; alice.dir = 'up'; alice.setAnim('walk');
  P.x = E.tecky[0]; P.y = y0 + 30; P.dir = 'up'; P.mode = 'free'; P.setAnim('walk');
  fxs = []; pops = []; rings = []; dusts = []; leaves = []; butterflies = []; drops = []; flakes = [];
  dogs = dogs.filter(d => d.x < camX - 150 || d.x > camX + VW + 150 || d.y < camY - 100 || d.y > camY + VH + 200);   // pas de chiens
  weather.k = 0; weather.on = false; sun = 3; hug = 1;     // (au noir : sans transition, si le joueur a fait vite)
  ending.flies = Array.from({ length: E.flies }, () => ({ x: camX + 40 + Math.random() * (VW - 80),
    y: camY + 40 + Math.random() * (VH - 80), p: Math.random() * 7 }));
}
// pose finale : Alice debout devant la niche, Tecky endormi à ses pieds
function endingPose() {
  const E = ENDING;
  alice.x = E.alice[0]; alice.y = E.alice[1]; alice.dir = 'down'; alice.setAnim('idle');
  P.x = E.tecky[0]; P.y = E.tecky[1]; P.dir = 'left';
  if (P.anim !== 'sleep') { P.setAnim('sleep'); P.zT = 0.4; P.snoreT = 1; }
}
function endingDone() {
  if (!ending.home) endingHome();
  endingPose();
  ending = null; state = 'win'; overT = 0; sun = 4;      // (scène passée : directement la nuit)
  fadeFrom(0.8);
}
const endingEnd = () => ENDING.iris + ENDING.irisDur + ENDING.hold + ENDING.close + ENDING.fin;
function updateEnding(dt) {
  const E = ENDING, e = ending;
  e.t += dt; alice.t += dt; P.t += dt;
  updateFx(dt);
  if (e.t > E.skip && (pressed.ok || pressed.bite || pressed.bark || pressed.act || pressed.pause)) { endingDone(); return; }
  if (e.t >= endingEnd()) { endingDone(); return; }
  if (!e.home) { if (e.t >= E.fade) endingHome(); return; }
  // Alice remonte le chemin, puis saute de joie devant la niche
  if (alice.anim === 'walk') {
    alice.y = Math.max(E.alice[1], alice.y - E.spd * dt);
    if (alice.y === E.alice[1]) { alice.dir = 'down'; alice.setAnim('happy'); e.happyT = 0; }
  } else if (alice.anim === 'happy' && (e.happyT += dt) > E.happy) alice.setAnim('idle');
  // Tecky la suit, s'assoit à côté d'elle, bâille et s'endort
  if (P.anim === 'walk') {
    P.y = Math.max(E.tecky[1], P.y - E.spd * dt);
    if (P.y === E.tecky[1]) { P.dir = 'left'; P.setAnim('sit'); e.restT = 0; }
  } else if (P.anim === 'sit' || P.anim === 'yawn') {
    e.restT += dt;
    if (P.anim === 'sit' && e.restT > E.sit) { P.setAnim('yawn'); if (!muted) SFX.yawn(); }
    else if (P.anim === 'yawn' && e.restT > E.sit + E.yawn) { P.setAnim('sleep'); P.zT = 0.4; P.snoreT = 1; }
  } else if (P.anim === 'sleep') snooze(dt, false);
}
// lucioles : de petites lumières qui flottent et clignotent (dessinées avec la lumière, par-dessus la nuit)
function drawFireflies() {
  const t = ending.t;
  for (const f of ending.flies) {
    const x = f.x + Math.sin(t * 0.7 + f.p) * 46, y = f.y + Math.sin(t * 1.1 + f.p * 1.3) * 28;
    const a = clamp(0.45 + 0.45 * Math.sin(t * 2.2 + f.p * 3), 0, 1) * clamp(sun - 3, 0, 1);   // avec la nuit
    glowSpot(x, y, 26, 0.5 * a);
    ctx.fillStyle = `rgba(255, 246, 170, ${a})`; ctx.fillRect(x - 2, y - 2, 4, 4);
  }
}
// repère GUI : fondu au noir et retour, puis l'iris qui se referme sur Tecky et Alice, et « Fin »
function drawEnding() {
  const E = ENDING, t = ending.t;
  guiTransform();
  const a = t < E.fade ? t / E.fade : !ending.home ? 1 : clamp(1 - (t - E.fade) / E.fade, 0, 1);
  if (a > 0) { ctx.fillStyle = `rgba(0, 0, 0, ${a})`; ctx.fillRect(0, 0, GW, GH); }
  const ti = t - E.iris;
  if (ti <= 0) return;
  const k = GW / VW, cx = ((alice.x + P.x) / 2 - camX) * k, cy = ((alice.y + P.y) / 2 - 45 - camY) * k;
  const far = Math.hypot(GW, GH);
  const r = ti < E.irisDur ? lerp(far, E.irisR, 1 - Math.pow(1 - ti / E.irisDur, 3))
    : ti < E.irisDur + E.hold ? E.irisR : E.irisR * Math.max(0, 1 - (ti - E.irisDur - E.hold) / E.close);
  ctx.fillStyle = '#000';
  ctx.beginPath(); ctx.rect(0, 0, GW, GH);
  if (r > 0.5) { ctx.moveTo(cx + r, cy); ctx.arc(cx, cy, r, 0, Math.PI * 2); }
  ctx.fill('evenodd');
  const tf = ti - E.irisDur - E.hold - E.close;
  if (tf > 0) { ctx.globalAlpha = Math.min(1, tf / 0.6); outlined('Fin', GW / 2, GH / 2 + 45, 130, '#FFF7E6'); ctx.globalAlpha = 1; }
}

/* Fondus de l'écran entier, au-dessus de tout. fadeFrom(d) : part du noir et s'éclaircit en d secondes. transition() :
   change d'écran en passant par le noir (titre <-> jeu, Continuer, Recommencer) ; le jeu change d'écran tout de suite,
   une image de l'écran qu'on quitte (snap) s'assombrit pendant la première moitié, puis le nouveau se découvre. */
const FADE = { swap: 0.7 };
let fade = { a: 0, d: 1, snap: null, t: 0 };
function fadeFrom(d) { fade = { a: 1, d, snap: null, t: 0 }; }
function transition() {
  let snap = null;
  try {
    snap = document.createElement('canvas'); snap.width = cv.width; snap.height = cv.height;
    snap.getContext('2d').drawImage(cv, 0, 0);
  } catch (e) { snap = null; }
  fade = snap ? { a: 0, d: FADE.swap, snap, t: 0 } : { a: 1, d: FADE.swap / 2, snap: null, t: 0 };
}
function updateFade(dt) {
  if (!fade.snap) { fade.a = Math.max(0, fade.a - dt / fade.d); return; }
  fade.t += dt; fade.a = Math.min(1, fade.t / (fade.d / 2));
  if (fade.a >= 1) fadeFrom(fade.d / 2);                     // au noir : on découvre le nouvel écran
}
function drawFade() {
  if (fade.snap) { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.drawImage(fade.snap, 0, 0); }
  if (fade.a <= 0) return;
  guiTransform();
  ctx.fillStyle = `rgba(0, 0, 0, ${fade.a})`; ctx.fillRect(0, 0, GW, GH);
}

function updateCamera(dt) {
  const tx = camClampX(P.x - VW / 2);
  const ty = camClampY(P.y - 40 - VH / 2);
  const k = 1 - Math.pow(0.0005, dt);
  camX = lerp(camX, tx, k); camY = lerp(camY, ty, k);
  shake = Math.max(0, shake - dt);
  markSeen();
}

function update(dt) {
  updateFade(dt);
  if (pressed.mute) { muted = !muted; Music.refresh(); }
  updateToasts(dt);
  if (state === 'title' || state === 'play' || state === 'dialog') updateWeather(dt);
  if (state !== 'play' && AC) Ambience.quiet();
  updateClouds(dt);
  if (state !== 'title') updateSun(dt);
  switch (state) {
    case 'title': {
      titleT += dt;
      alice.t += dt; P.t += dt;
      for (const v of cars) updateVehicle(v, dt);
      for (const b of butterflies) updateButterfly(b, dt);
      for (const c of critters) updateCritter(c, dt);
      for (const d of ducks) updateDuck(d, dt);
      updateFarmer(dt);
      updateLeaves(dt);
      const id = menuInput();
      if (id) chooseMenu(id);
      break;
    }
    case 'dialog':
      updateDialog(dt);
      updateFarmer(dt);
      alice.t += dt; P.t += dt;
      for (const d of dogs) if (d.mode !== 'ko') d.t += dt;
      for (const h of hens) h.t += dt;
      for (const c of cows) c.t += dt;
      for (const v of villagers) v.t += dt;
      updateFx(dt);
      updateCamera(dt);
      break;
    case 'pause': {
      if (pressed.pause) { menu = null; state = 'play'; Music.refresh(); break; }
      const id = menu && menuInput();
      if (id) chooseMenu(id);
      break;
    }
    case 'options':
      optionsInput();
      break;
    case 'badges':
      badgesInput();
      break;
    case 'play':
      if (pressed.pause) { state = 'pause'; openPauseMenu(); Music.refresh(); break; }
      timePlayed += dt;
      if (pendingSay && (pendingSay.t -= dt) <= 0) { const ps = pendingSay; pendingSay = null; say(ps.lines, ps.onEnd); break; }
      arrowT = Math.max(0, arrowT - dt);
      graceT = Math.max(0, graceT - dt);
      if (!alice.found && (stuckT += dt) > ARROW.nudgeAfter) showArrow(ARROW.nudge);
      updatePlayer(dt);
      if ((saveT += dt) >= SAVE_EVERY && safeToSave()) { saveT = 0; saveGame(); }
      for (const d of dogs) updateDog(d, dt);
      for (const h of hens) updateHen(h, dt);
      for (const c of cows) updateCow(c, dt);
      for (const v of villagers) updateVillager(v, dt);
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
      updateFarmer(dt);
      updateLetters(dt);
      updatePompon(dt);
      for (const b of balls) updateBall(b, dt);
      updateToys(dt);
      updateTrain(dt);
      for (const b of babies) updateBaby(b, dt);
      if (piquette.callT > 0 && (piquette.callT -= dt) <= 0) piquetteCall();
      for (const c of critters) updateCritter(c, dt);
      for (const d of ducks) updateDuck(d, dt);
      updateTrail(dt);
      if ((badgeT += dt) > 0.5) { badgeT = 0; checkBadges(); }
      updateZone(dt);
      Ambience.update(dt);
      updateCamera(dt);
      break;
    case 'ending':
      updateEnding(dt);
      break;
    case 'over':
    case 'win':
      overT += dt;
      alice.t += dt; P.t += dt;
      if (state === 'win' && P.anim === 'sleep') snooze(dt, true);    // Tecky dort derrière le tableau des scores
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
  const cx = camClampX(Math.round((camX + sx) * scale) / scale);
  const cy = camClampY(Math.round((camY + sy) * scale) / scale);
  ctx.setTransform(scale, 0, 0, scale, offX - cx * scale, offY - cy * scale);
  drawGround(cx, cy);
  drawWater(cx, cy, performance.now() / 1000);
  drawGroundWeather(cx, cy);

  const vis = (x, y, m) => x > cx - m && x < cx + VW + m && y > cy - m && y < cy + VH + m + 140;
  // trous et scintillements des trésors
  for (const g of digs) {
    if (g.dug) drawHole(g.x, g.y);
    else if (g.t % 2.4 < 0.7) drawSpr('fx/pickup', Math.floor((g.t % 2.4) * 7), g.x, g.y - 24, { sc: 0.55, alpha: 0.9 });
  }
  for (const d of decor) if (FLAT.has(d.n) && vis(d.x, d.y, 400)) drawSpr(d.key, 0, d.x, d.y);   // pont, bac à sable
  drawLeavesOnGround();
  drawTrail();
  drawDust();
  drawRings();   // ondes d'aboiement, au sol sous les personnages
  for (const d of ducks) if (d.h > 0 && vis(d.x, d.y, 60)) {           // ombres des canards en vol
    ctx.save();
    ctx.globalAlpha = 0.2 * (1 - Math.min(0.6, d.h / 200));
    ctx.fillStyle = '#000';
    ctx.beginPath(); ctx.ellipse(d.x, d.y, 18, 5, 0, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }
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
  for (const d of EDGE_DECOR) if (vis(d.x, d.y, d.n === 'tunnel' ? 460 : 280))     // la lisière, au bord de la carte
    list.push({ y: d.y, draw: () => drawSpr(d.key, 0, d.x, d.y, d.flip ? { flip: true } : undefined) });
  for (const it of items) if (vis(it.x, it.y, 80)) {
    const i = Math.floor(it.t * 8);
    let dy = 0;
    if (it.pop !== undefined && it.t < 0.5) dy = -Math.sin(it.t / 0.5 * Math.PI) * 60;
    list.push({ y: it.y + 24, draw: () => drawSpr('item/' + it.n, i, it.x, it.y + dy) });
  }
  for (const d of dogs) if (vis(d.x, d.y, 120)) list.push({ y: d.y, draw: () => d.draw(Math.max(0, 1 - d.fade)) });
  for (const h of hens) if (vis(h.x, h.y, 60)) list.push({ y: h.y, draw: () => h.draw() });
  for (const c of cows) if (vis(c.x, c.y, 140)) list.push({ y: c.y, draw: () => drawCow(c) });
  for (const v of villagers) if (vis(v.x, v.y, 140)) list.push({ y: v.y, draw: () => drawVillager(v) });
  for (const v of cars) if (vis(v.x, v.y, 280)) list.push({ y: v.y, draw: () =>
    drawSpr('vehicle/' + v.name, Math.floor(v.t * 4), v.x, v.y, { flip: v.dir < 0 }) });
  if (!alice.hidden && vis(alice.x, alice.y, 120)) list.push({ y: alice.y, draw: () => alice.draw() });
  for (const n of npcList()) if (vis(n.x, n.y, 140)) list.push({ y: n.y, draw: () => drawNpc(n) });
  for (const l of letters) if (!l.got && vis(l.x, l.y, 60)) list.push({ y: l.y + 20, draw: () => drawSpr('item/letter', Math.floor(l.t * 6), l.x, l.y) });
  if (vis(pompon.x, pompon.y, 60)) list.push({ y: pompon.y, draw: drawPompon });
  for (const b of babies) if (vis(b.x, b.y, 60)) list.push({ y: b.y, draw: () => drawBaby(b) });
  for (const b of balls) if (vis(b.x, b.y, 80)) list.push({ y: b.y, draw: () => drawBall(b) });
  if (trainEast() > cx - 100 && trainWest() < cx + VW + 100 && vis(train.x, trainY(), 200))
    list.push({ y: trainY() + TRAIN.ground, draw: drawTrain });
  for (const t of toys) {   // un jouet porté : devant Tecky (derrière lui s'il nous tourne le dos)
    const y = t.carried ? P.y + (P.dir === 'up' ? -0.5 : 0.5) : t.y;
    if (vis(t.carried ? P.x : t.x, y, 80)) list.push({ y, draw: () => drawToy(t) });
  }
  for (const d of ducks) if (d.h === 0 && vis(d.x, d.y, 60)) list.push({ y: d.y, draw: () => drawDuck(d) });
  for (const c of critters) if (critterVisible(c) && vis(c.x, c.y - c.h, 60))
    list.push({ y: c.h > 0 && c.ref ? c.ref.y + 2 : c.y, draw: () => drawCritter(c) });
  const blink = P.inv > 0 && P.mode !== 'ko' && Math.floor(P.inv * 12) % 2 === 0;
  list.push({ y: P.y, draw: () => P.draw(blink ? 0.35 : 1) });
  list.sort((a, b) => a.y - b.y);
  for (const o of list) o.draw();

  // papillons : au-dessus de tout, tournés dans le sens du vol
  for (const b of butterflies) if (vis(b.x, b.y, 80))
    drawSpr('butterfly/' + b.color, Math.floor(b.flap) % 4, b.x, b.y - b.alt, { angle: b.heading + Math.PI / 2, sc: BFLY.sc });
  for (const d of ducks) if (d.h > 0 && vis(d.x, d.y - d.h, 80)) drawDuck(d);   // canards en vol, au-dessus de tout
  drawFallingLeaves();
  for (const f of fxs) drawSpr(f.key, f.frame !== undefined ? f.frame : Math.floor(f.t * f.fps), f.x + (f.vx || 0) * f.t,
    f.y + (f.vy || 0) * f.t, { angle: f.angle, sc: f.grow ? f.grow[0] + (f.grow[1] - f.grow[0]) * f.t / f.life : undefined,
      alpha: f.life ? clamp(Math.min(f.t / 0.25, (f.life - f.t) / 0.5), 0, 1) : undefined });
  drawClouds(cx, cy);
  drawLight(cx, cy);
  drawSkyWeather(cx, cy);

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
      const y = p.y - p.t * 40, hw = ctx.measureText(p.text).width / 2 + 8, x = clamp(p.x, cx + hw, cx + VW - hw);
      ctx.strokeText(p.text, x, y); ctx.fillStyle = '#F2C14E'; ctx.fillText(p.text, x, y);
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
  if (tunnelHint && state === 'play' && P.mode !== 'tunnel') actionBubble('Passer', tunnelHint.x, tunnelHint.y - 100 + bob);
  if (talkHint && state === 'play') actionBubble('Parler', talkHint.x, talkHint.y + bob);
  // « ! » / « ? » au-dessus des personnages (sauf celui à qui Tecky peut parler : bulle « Parler »)
  for (const n of npcList()) {
    const m = NPC_DO[n.kind].mark(), k = ATLAS['hud/talk'];
    if (m < 0 || !k || (talkHint && n.near) || !vis(n.x, n.y, 140)) continue;
    const [, , w, h] = k.f[m];
    drawSpr('hud/talk', m, n.x - w / 2, n.y - markY(n) - h + 26 + bob * 1.5);
  }
}
function actionBubble(label, bx, by) {
  ctx.font = '600 22px Fredoka, "Trebuchet MS", sans-serif';
  ctx.textAlign = 'center'; ctx.lineWidth = 5; ctx.strokeStyle = '#3A1E12'; ctx.lineJoin = 'round';
  // même écart touche-mot que pour « Gratter », l'ensemble restant centré
  const shift = (ctx.measureText('Gratter').width - ctx.measureText(label).width) / 2;
  if (!touchMode) drawSpr(...glyphFrame('bite'), bx - 40 - 34 + shift, by - 4, { sc: 0.9 });
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
  if (String(str).includes('[')) drawRich(str, x, y, size); else ctx.fillText(str, x, y);
}

/* Icônes de touches et de boutons dans les textes : « [ok] pour valider ». Le mot entre crochets est une action de
   GLYPH, montrée avec l'appareil du moment : la touche au clavier, le bouton à la manette (sans bouton : la touche).
   « a/b » : deux icônes au choix, séparées par une barre ; « a+b » : côte à côte. Noms : MAP.keys, MAP.pads. */
const GLYPH = {
  bite: ['C', 'A'], bark: ['X', 'X'], sniff: ['R', 'Y'], ok: ['Entrée', 'A'], back: ['Échap', 'B'],
  pause: ['P', 'Start'], mute: ['M', 'Select'], fs: ['F', null], walk: ['arrows/zqsd', 'stick/croix'],
  updown: ['up+down', 'croix'], leftright: ['left+right', 'croix'], arrows: ['arrows', 'croix'],
};
// les mêmes, à dire (synthèse vocale des répliques) : [clavier, manette]
const GLYPH_SPOKEN = {
  bite: ['la touche C', 'le bouton A'], bark: ['la touche X', 'le bouton X'], sniff: ['la touche R', 'le bouton Y'],
  ok: ['la touche Entrée', 'le bouton A'], back: ['la touche Échap', 'le bouton B'], pause: ['la touche P', 'le bouton Start'],
  mute: ['la touche M', 'le bouton Select'], fs: ['la touche F', 'la touche F'], walk: ['les flèches ou Z, Q, S, D', 'le stick ou la croix'],
  updown: ['les flèches haut et bas', 'la croix'], leftright: ['les flèches gauche et droite', 'la croix'], arrows: ['les flèches', 'la croix'],
};
/* Voix des répliques (tools/export_voix.js, voix/) : le texte à dire (spokenText : les [action] en mots, selon
   l'appareil, « (3 / 8) » -> « 3 sur 8 »), et le nom de son fichier (voiceKey : personnage + empreinte du texte à dire,
   si bien qu'une réplique modifiée change de nom et se repère tout de suite). device : 'clavier' ou 'manette'. */
function spokenText(text, device) {
  const k = device === 'manette' ? 1 : 0;
  return text.replace(/\[([a-z]+)\]/g, (m, n, at) => {
    const w = GLYPH_SPOKEN[n] ? GLYPH_SPOKEN[n][k] : m;
    return at === 0 || /[.!?]\s+$/.test(text.slice(0, at)) ? w[0].toUpperCase() + w.slice(1) : w;
  }).replace(/\((\d+) ?\/ ?(\d+)\)/g, '$1 sur $2');
}
function voiceKey(who, spoken) {
  let h = 0x811c9dc5;                                    // FNV-1a 32 bits
  for (let i = 0; i < spoken.length; i++) { h ^= spoken.charCodeAt(i); h = Math.imul(h, 0x01000193) >>> 0; }
  return who + '-' + h.toString(16).padStart(8, '0');
}
const ICON = { h: 1.25, gap: 0.12, bar: 0.12 };   // en taille de texte : hauteur, écart entre deux icônes, autour de « / »
// [[[sprite, image], …] par choix, …]
function glyphIcons(name) {
  const g = GLYPH[name];
  if (!g) return null;
  const usePad = pad.on && g[1], spr = usePad ? 'hud/pad' : 'hud/key', names = usePad ? MAP.pads : MAP.keys;
  return (usePad ? g[1] : g[0]).split('/').map(alt => alt.split('+').map(k => [spr, names.indexOf(k)]));
}
const glyphFrame = name => glyphIcons(name)[0][0];
// morceaux d'un texte : chaînes, et icônes à la place des [action] connues
function richParts(str) {
  const out = [], re = /\[([a-z]+)\]/g;
  let last = 0, m;
  while ((m = re.exec(str))) {
    const ic = glyphIcons(m[1]);
    if (!ic) continue;
    if (m.index > last) out.push(str.slice(last, m.index));
    out.push(ic); last = re.lastIndex;
  }
  if (last < str.length) out.push(str.slice(last));
  return out;
}
const iconScale = size => size * ICON.h / ATLAS['hud/key'].f[1][3];
// largeur d'un morceau ; draw : le dessine aussi, à partir de x (ctx.textAlign à gauche)
function richPart(p, x, y, size, draw) {
  if (typeof p === 'string') { if (draw) ctx.fillText(p, x, y); return ctx.measureText(p).width; }
  const sc = iconScale(size), mid = y - size * 0.34;
  let cx = x;
  p.forEach((alt, j) => {
    if (j) { cx += size * ICON.bar; if (draw) ctx.fillText('/', cx, y); cx += ctx.measureText('/').width + size * ICON.bar; }
    alt.forEach(([s, i], k) => {
      const f = ATLAS[s].f[i];
      if (k) cx += size * ICON.gap;
      if (draw) ctx.drawImage(atlas, f[0], f[1], f[2], f[3], cx, mid - f[3] * sc / 2, f[2] * sc, f[3] * sc);
      cx += f[2] * sc;
    });
  });
  return cx - x;
}
function richWidth(str, size) { return richParts(str).reduce((w, p) => w + richPart(p, 0, 0, size, false), 0); }
// ctx.font et ctx.fillStyle déjà réglés ; ctx.textAlign respecté
function drawRich(str, x, y, size) {
  const parts = richParts(str), al = ctx.textAlign;
  const w = parts.reduce((v, p) => v + richPart(p, 0, 0, size, false), 0);
  let cx = al === 'center' ? x - w / 2 : al === 'right' ? x - w : x;
  ctx.textAlign = 'left';
  for (const p of parts) cx += richPart(p, cx, y, size, true);
  ctx.textAlign = al;
}
// taille de la police courante (pour mesurer les icônes en passant à la ligne)
function fontSize() { const m = /(\d+(?:\.\d+)?)px/.exec(ctx.font || ''); return m ? +m[1] : 26; }
// texte d'une réplique tapé jusqu'au caractère n, sans couper une [action] en deux
function typed(str, n) {
  const cut = str.slice(0, n), o = cut.lastIndexOf('[');
  if (o < 0 || cut.indexOf(']', o) >= 0) return cut;
  const e = str.indexOf(']', o);
  return e < 0 ? cut : str.slice(0, e + 1);
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
  const words = str.split(' '), lines = [], size = str.includes('[') && fontSize();
  let cur = '';
  for (const w of words) {
    const t = cur ? cur + ' ' + w : w;
    if ((size ? richWidth(t, size) : ctx.measureText(t).width) > maxW && cur) { lines.push(cur); cur = w; } else cur = t;
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

/* Compteurs du HUD, empilés à droite sous le score : os dorés (dès le premier trouvé : c'est une quête aussi), puis les
   quêtes en cours, dans l'ordre : poules rentrées, lettres retrouvées, Pompon retrouvé.
   [sprite, décalage x, décalage y, échelle, nombre, total] */
// les compteurs, en colonne à droite sous le score ; ils passent sur une colonne de plus (à gauche) plutôt que de
// descendre jusqu'aux boutons d'action (au toucher : le bouton du flair ; sinon, les aides de touches du bas)
const COUNTER = { w: 210, h: 70, step: 82, top: 138, gap: 12 };
function counterBox(i) {
  const bottom = touchMode ? BTN.sniff.y - BTN.sniff.r - 14 : GH - 200;
  const per = Math.max(1, Math.floor((bottom - COUNTER.top - COUNTER.h) / COUNTER.step) + 1);
  return { x: GW - 24 - COUNTER.w - Math.floor(i / per) * (COUNTER.w + COUNTER.gap), y: COUNTER.top + (i % per) * COUNTER.step,
    w: COUNTER.w, h: COUNTER.h };
}
function hudCounters() {
  const c = [];
  if (treasures > 0) c.push(['item/goldbone', 42, 28, 0.8, treasures, MAP.dig.length]);
  if (farm.state === 'asked') c.push(['hen/idle/right', 46, 58, 0.9, questHens().length - hensLeft(), questHens().length]);
  if (post.state === 'asked') c.push(['item/letter', 50, 36, 0.8, letters.length - lettersLeft(), letters.length]);
  if (rose.state === 'asked') c.push(['cat_white/idle', 46, 58, 0.9, pompon.mode === 'lost' ? 0 : 1, 1]);
  if (fete.state === 'asked') c.push(['port/balloon', 42, 35, 0.8, balls.length - ballsLeft(), balls.length]);
  if (jouets.state === 'asked') c.push(['port/toy', 42, 35, 0.8, toys.length - toysLeft(), toys.length]);
  if (piq.state === 'asked') c.push(['hedgehog/idle', 44, 58, 1.1, babies.length - babiesLeft(), babies.length]);
  return c;
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
  // compteurs, à droite sous le score (hudCounters)
  const counters = hudCounters();
  counters.forEach(([k, ox, oy, sc, a, b], i) => {
    const { x, y, w, h } = counterBox(i);
    drawNine('hud/panel_dark', x, y, w, h, 32);
    drawSpr(k, 0, x + ox, y + oy, { sc });
    drawDigits(a + '/' + b, x + 86, y + 8, 0.8);
  });

  // indices d'Alice : trois cases sous la vie, l'objet apparaît quand il est retrouvé
  drawNine('hud/panel_dark', 24, 166, 24 + CLUES.length * 76, 88, 32);
  CLUES.forEach((n, i) => drawSpr('item/' + n, 0, 24 + 12 + 38 + i * 76, 166 + 44 + 4, { alpha: clues[i] ? 1 : 0.22 }));

  // flèche (quelques secondes) vers le prochain indice, puis vers Alice ; seule la pointe tourne, l'icône reste droite
  if (!alice.found && state === 'play' && arrowT > 0) {
    const tg = arrowTarget();
    const ax = (tg.x - camX) * GW / VW, ay = (tg.y - 50 - camY) * GH / VH;
    if (ax < 0 || ax > GW || ay < 0 || ay > GH) {
      const ang = Math.atan2(ay - GH / 2, ax - GW / 2), a = Math.min(1, arrowT), sc = ARROW.sc, m = 80 * sc;
      const px = clamp(ax, m, GW - m), py = clamp(ay, 300, GH - m);
      drawSpr('hud/arrow', Math.floor(performance.now() / 150), px, py, { angle: ang, alpha: a, sc });
      // centre de la pastille : 6 px derrière le centre de rotation ; icône 0..2 = indices, 3 = Alice
      drawSpr('hud/arrow_icon', tg === alice ? 3 : nextClue(), px - Math.cos(ang) * 6 * sc, py - Math.sin(ang) * 6 * sc, { alpha: a, sc });
    }
  }

  // boutons d'action
  const cdOf = k => k === 'bark' ? P.cdBark / (P.cdBarkMax || 1) : k === 'sniff' ? P.cdSniff / (P.cdSniffMax || 1) : P.cdBite / (P.cdBiteMax || 1);
  if (touchMode) {
    const biteFr = ACTION_FRAME[biteAction()];
    for (const [k, fr] of [['bark', 0], ['bite', biteFr], ['sniff', 10]]) {
      const b = BTN[k];
      const cd = cdOf(k);
      ctx.save();
      ctx.translate(b.x, b.y); ctx.scale(b.r / 48, b.r / 48);
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
    drawNine('hud/panel_dark', PAUSE_BTN.x, PAUSE_BTN.y, PAUSE_BTN.w, PAUSE_BTN.h, 32);
    text('II', PAUSE_BTN.x + PAUSE_BTN.w / 2, PAUSE_BTN.y + 48, 40, '#FFF7E6', 'center', 700);
    if (canFullscreen() && !fsElement()) drawFsButton();
  } else {
    // touches : R flaire, X aboie, C mord (ou gratte, lit…) ; manette : Y, X, A (GLYPH)
    [['sniff', 10], ['bark', 0], ['bite', ACTION_FRAME[biteAction()]]].forEach(([k, fr], i) => {
      const x = GW - 340 + i * 110, y = GH - 190;
      drawSpr('hud/action', fr, x, y);
      const cd = cdOf(k);
      if (cd > 0) drawSpr('hud/cooldown', Math.floor((1 - cd) * 8), x, y);
      drawSpr(...glyphFrame(k), x, y + 86);
    });
  }
  if (muted) text('son coupé · [mute] pour le remettre', 40, GH - 30, 28, '#FFF7E6', 'left', 500);
  drawBanner();
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
  // option « Texte : grand » : plus gros, une ligne de plus, panneau plus haut
  const big = opts.text === 'grand', fs = big ? 46 : 38, lh = big ? 56 : 50, maxL = big ? 4 : 3;
  const bh = big ? 296 : 226, bx = 250, by = GH - 36 - bh, bw = GW - 500;
  drawNine('hud/panel', bx, by, bw, bh, 32);
  let tx = bx + 60;
  if (who.portrait) {
    drawSpr(who.portrait, L.face || 0, bx + 36, by + 64);
    tx = bx + 170;
    ctx.font = '600 26px Fredoka, "Trebuchet MS", sans-serif';
    const nw = Math.max(128, Math.ceil(ctx.measureText(who.name).width) + 40);       // l'étiquette s'élargit avec le nom
    drawNine('hud/name_tag', bx + 150, by - 18, nw, 40, 16);
    text(who.name, bx + 150 + nw / 2, by + 12, 26, '#FFFFFF', 'center', 600);
  }
  ctx.font = `500 ${fs}px Fredoka, "Trebuchet MS", sans-serif`;
  const lines = wrap(typed(L.text, Math.floor(dialog.c)), bx + bw - 70 - tx);
  lines.slice(0, maxL).forEach((ln, i) => text(ln, tx, by + 84 + (fs - 38) * 0.6 + i * lh, fs, '#3A1E12', 'left', 500));
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
  if (r) outlined(r, GW / 2, last.y + last.h + 46, 30, '#F2C14E');
  if (!touchMode) text('[updown] pour choisir, [ok] pour valider',
    GW / 2, GH - 28, 26, '#E9DCC8', 'center', 500);
  text(VERSION, GW - 28, GH - 28, 20, 'rgba(233, 220, 200, 0.75)', 'right', 500);   // date de construction (pack_web)
}
/* entrées du menu : l'entrée choisie est claire, encadrée de deux os qui la montrent */
function drawMenu(t) {
  menu.items.forEach((it, i) => {
    const b = menuBox(i), sel = i === menu.sel;
    drawNine(sel ? 'hud/panel' : 'hud/panel_dark', b.x, b.y, b.w, b.h, 32);
    const ink = sel ? '#3A1E12' : '#FFF7E6';
    const small = b.h < 90;                                        // menu principal à cinq entrées : un peu plus petit
    text(it.label, b.x + b.w / 2, it.sub ? b.y + b.h * (small ? 0.46 : 0.48) : b.y + b.h / 2 + 14, small ? 36 : 40, ink, 'center', 700);
    if (it.sub) text(it.sub, GW / 2, b.y + b.h * (small ? 0.46 : 0.48) + (small ? 29 : 34), small ? 23 : 26, sel ? '#6B5A4E' : '#E9DCC8', 'center', 500);
    if (sel && !menu.row) {
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
  const pw = 900, ph = 650, px = (GW - pw) / 2, py = (GH - ph) / 2;
  drawNine('hud/panel', px, py, pw, ph, 32);
  outlined('Tecky a retrouvé Alice !', GW / 2, py + 100, 64, '#F2C14E');
  drawSpr('hud/portrait_tecky', 2, GW / 2 - 130, py + 140);
  drawSpr('hud/portrait_alice', 2, GW / 2 + 34, py + 140);
  // badges gagnés pendant cette partie, en petit sous les portraits
  newBadges.forEach((id, i) => drawSpr('hud/badge', MAP.badges.indexOf(id), GW / 2 - newBadges.length * 30 + i * 60 + 4, py + 242, { sc: 0.55 }));
  const rows = [['Score', String(score)], ['Temps', fmtTime(timePlayed)],
    ['Os dorés', treasures + ' / ' + MAP.dig.length], [balade() ? 'Copains de jeu' : 'Chiens mis en fuite', String(fled)],
    [balade() ? 'Balade complétée' : 'Aventure complétée', winDone + '\u00a0%']];
  rows.forEach(([k, v], i) => {
    text(k, px + 180, py + 320 + i * 46, 34, '#6B5A4E', 'left', 500);
    text(v, px + pw - 180, py + 320 + i * 46, 34, '#3A1E12', 'right', 600);
    // meilleur score, meilleur temps, meilleure complétion : une étiquette dorée à côté de la valeur
    if ((i === 0 && newRecord.score) || (i === 1 && newRecord.time) || (i === 4 && newRecord.done)) {
      ctx.save(); ctx.translate(px + pw - 98, py + 308 + i * 46); ctx.rotate(-0.08);
      outlined('Record !', 0, 0, 26, '#F2C14E'); ctx.restore();
    }
  });
  const r = recordLine(gameMode);
  if (r) text(r, GW / 2, py + ph - 96, 26, '#6B5A4E', 'center', 500);
  if (overT > 1 && Math.floor(overT * 1.6) % 2 === 0)
    text(touchMode ? 'Touche l’écran pour revenir au menu' : '[ok] pour revenir au menu',
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
  drawRainbow();
  if (state === 'title') drawTitle();
  else if (state === 'options' && optReturn === 'title') { veil(0.35); drawOptions(); }
  else if (state === 'badges') { veil(0.35); drawBadges(); }
  else if (state === 'ending') drawEnding();
  else {
    drawHUD();
    if (state === 'dialog' && dialog) drawDialog();
    if (state === 'pause') {
      veil(0.6);
      outlined('Pause', GW / 2, 104, 68, '#FFF7E6');
      drawPauseMap();
      if (menu) drawMenu(titleT);
      text((touchMode ? 'Touche un bouton, ou ailleurs pour reprendre' :
        '[leftright] et [ok] pour choisir, [pause] pour reprendre' + (pad.on ? '' : ', [fs] pour le plein écran')) + ' · mode ' + gameMode +
        (facile() ? ' facile' : '') + ' · partie enregistrée', GW / 2, GH - 34, 26, '#E9DCC8', 'center', 500);
      if (touchMode && canFullscreen() && !fsElement()) drawFsButton();
    }
    if (state === 'options') drawOptions();
    if (state === 'over') drawEnd(false);
    if (state === 'win') drawEnd(true);
    if (state === 'play' || state === 'dialog' || state === 'win') drawToast();
  }
  drawFade();
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
    loadBadges();
    if (essai) startEssai(); else toTitle();
  });
  requestAnimationFrame(frame);
}
start();
