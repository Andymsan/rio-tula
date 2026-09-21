/* ============================================================================
   sitio.js — Río Tula v2027 (borrador)
   1) nav + progreso + índice   2) reveals   3) historia (scrollytelling)
   4) escenarios: mapa fijo con cámara, capas, pines y textitos por paso
   5) carruseles de fotos con marcadores de posición
   ============================================================================ */
(function () {
  'use strict';
  const $  = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const html = document.documentElement;
  const mobile = window.matchMedia('(max-width: 900px)');

  /* ── 1. Nav, progreso, índice ─────────────────────────────────────── */
  const nav = $('#main-nav'), bar = $('#progress');
  function onScroll() {
    const max = html.scrollHeight - html.clientHeight;
    bar.style.width = (max > 0 ? (window.scrollY / max) * 100 : 0) + '%';
    nav.classList.toggle('scrolled', window.scrollY > 60);
  }
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // nav claro/oscuro según la sección que está bajo la barra
  let navObs;
  function buildNavObs() {
    if (navObs) navObs.disconnect();
    navObs = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return;
      nav.classList.toggle('light', e.target.dataset.nav === 'light');
      if (!e.target.classList.contains('cap')) delete html.dataset.tema;
    }), { rootMargin: '-30px 0px -' + Math.max(0, innerHeight - 31) + 'px 0px', threshold: 0 });
    $$('[data-nav]').forEach(el => navObs.observe(el));
  }

  const idx = $('#idxPanel');
  const setIdx = open => { idx.classList.toggle('open', open); document.body.style.overflow = open ? 'hidden' : ''; };
  $('#idxBtn').addEventListener('click', () => setIdx(true));
  $('#idxClose').addEventListener('click', () => setIdx(false));
  idx.addEventListener('click', e => { if (e.target === idx || e.target.closest('a')) setIdx(false); });
  addEventListener('keydown', e => { if (e.key === 'Escape') setIdx(false); });
  const bd = $('#borradorClose');
  if (bd) bd.addEventListener('click', () => bd.closest('.borrador').remove());

  /* ── 2. Reveals ───────────────────────────────────────────────────── */
  const rvObs = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('visible', 'in'); rvObs.unobserve(e.target); }
  }), { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  $$('.reveal, .rv').forEach(el => rvObs.observe(el));

  /* ── 4. Escenarios (mapa fijo + cámara) ───────────────────────────── */
  const TEMAS = ['tema-rosa', 'tema-naranja', 'tema-verde'];
  const stages = new Map();          // cap -> estado
  const allSteps = [];

  $$('.cap').forEach(cap => {
    const st = { cap, stage: $('.cap-stage', cap), canvas: $('.canvas', cap), steps: $$('.step', cap), cur: null, hist: cap.classList.contains('hist') };
    stages.set(cap, st);
    st.steps.forEach(s => allSteps.push(s));
  });

  function applyCam(st, step) {
    let [x, y, z] = (step.dataset.cam || '0.5,0.5,1').split(',').map(Number);
    if (mobile.matches) z = Math.max(1, z * 0.8);   // en móvil se ve un pedazo más chico del mapa: menos zoom
    const W = st.stage.clientWidth, H = st.stage.clientHeight;
    const Wc = Math.max(W, H * 16 / 9), Hc = Wc * 9 / 16;
    // punto de la pantalla donde queremos ver el objetivo (deja libre la tarjeta de texto)
    const hasBub = !!$('.burbuja', step);
    const ax = mobile.matches ? 0.5 : 0.6;
    const ay = mobile.matches ? 0.5 : (hasBub ? 0.42 : 0.5);
    let tx = (ax - 0.5) * W - z * (x - 0.5) * Wc;
    let ty = (ay - 0.5) * H - z * (y - 0.5) * Hc;
    const mx = Math.max(0, (z * Wc - W) / 2), my = Math.max(0, (z * Hc - H) / 2);
    tx = Math.min(mx, Math.max(-mx, tx));
    ty = Math.min(my, Math.max(-my, ty));
    st.canvas.style.setProperty('--tx', tx.toFixed(1) + 'px');
    st.canvas.style.setProperty('--ty', ty.toFixed(1) + 'px');
    st.canvas.style.setProperty('--z', z);
  }

  const list = v => (v || '').split(/\s+/).filter(Boolean);

  function activate(st, step, init) {
    if (st.cur === step && !init) return;
    st.cur = step;
    if (st.hist) return activateHist(st, step, init);
    const d = step.dataset;
    st.steps.forEach(s => s.classList.toggle('active', s === step));
    $$('.frame', st.canvas).forEach(f => f.classList.toggle('on', f.dataset.frame === d.frame));
    const ovs = list(d.ov);      $$('.ov', st.canvas).forEach(o => o.classList.toggle('on', ovs.includes(o.dataset.ov)));
    const pins = list(d.pins);   $$('.pin', st.canvas).forEach(p => p.classList.toggle('on', pins.includes(p.dataset.id)));
    const lbls = list(d.labels); $$('.maplabel', st.canvas).forEach(p => p.classList.toggle('on', lbls.includes(p.dataset.id)));
    st.stage.classList.toggle('show-pop', d.pop === '1');
    st.stage.style.setProperty('--wash', d.wash || 0);
    const v = $('.hexes', st.stage);
    if (v) { v.classList.toggle('on', !!d.hex); if (d.hex) v.dataset.focus = d.hex; }
    applyCam(st, step);
    const t = d.tema || st.cap.dataset.tema;
    if (t) {
      st.cap.classList.remove(...TEMAS); st.cap.classList.add('tema-' + t);
      if (!init) html.dataset.tema = t;
    }
    $$('[data-carousel]', step).forEach(initCarousel);
  }

  let stepObs;
  function buildStepObs() {
    if (stepObs) stepObs.disconnect();
    let rm = '-49% 0px -49% 0px';
    if (mobile.matches) {
      const stageH = Math.round(innerHeight * 0.44);
      rm = '-' + (stageH + 30) + 'px 0px -' + Math.max(0, innerHeight - stageH - 130) + 'px 0px';
    }
    stepObs = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) activate(stages.get(e.target.closest('.cap')), e.target);
    }), { rootMargin: rm, threshold: 0 });
    allSteps.forEach(s => stepObs.observe(s));
  }


  /* ── Historia: mapa SVG que se acerca a cada época ─────────────────── */
  const H_POS   = [0, 14, 28, 42, 56, 68, 78, 88, 100];
  // cámara por época: [centro x, centro y, alto visible] en unidades del SVG (460×767)
  const H_CAM   = [[230, 385, 860], [300, 590, 330], [218, 255, 270], [275, 400, 470], [135, 100, 250], [260, 340, 430], [172, 182, 190], [112, 118, 200], [140, 120, 290]];
  let hView = null, hRaf = 0;

  function hDraw(st, v) {
    const svg = $('#hmap'), W = st.stage.clientWidth, H = st.stage.clientHeight;
    const scale = mobile.matches ? 1.1 : 1;
    const h = v.h * scale, w = h * (W / H), ax = mobile.matches ? 0.5 : 0.6;
    svg.setAttribute('viewBox', (v.cx - w * ax).toFixed(2) + ' ' + (v.cy - h / 2).toFixed(2) + ' ' + w.toFixed(2) + ' ' + h.toFixed(2));
    svg.style.setProperty('--fs', (12 * h / H).toFixed(3));
  }
  function hGo(st, to, instant) {
    cancelAnimationFrame(hRaf);
    if (instant || !hView) { hView = { cx: to[0], cy: to[1], h: to[2] }; hDraw(st, hView); return; }
    const from = Object.assign({}, hView), t0 = performance.now(), dur = 1400;
    const ease = t => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
    const tick = now => {
      const t = Math.min(1, (now - t0) / dur), e = ease(t);
      hView = { cx: from.cx + (to[0] - from.cx) * e, cy: from.cy + (to[1] - from.cy) * e, h: from.h + (to[2] - from.h) * e };
      hDraw(st, hView);
      if (t < 1) hRaf = requestAnimationFrame(tick);
    };
    hRaf = requestAnimationFrame(tick);
  }
  function activateHist(st, step, init) {
    const i = Number(step.dataset.step), svg = $('#hmap');
    st.steps.forEach(s => s.classList.toggle('active', s === step));
    $$('[data-step]', svg).forEach(el => el.classList.toggle('on', Number(el.dataset.step) <= i));
    $$('.lbl', svg).forEach(el => el.classList.toggle('on', (el.dataset.show || '').split(' ').includes(String(i))));
    const q = sel => $(sel, svg);
    q('.lake').classList.toggle('drained', i >= 3);
    q('.riotula').classList.toggle('restored', i >= 8);
    const city = q('.tulacity'); city.classList.toggle('flood', i === 7); city.classList.toggle('restored', i >= 8);
    $('#hsDot').style.left = H_POS[i] + '%'; $('#hsFill').style.width = H_POS[i] + '%';
    const here = $('#hsHere'); here.style.left = H_POS[i] + '%'; here.textContent = step.dataset.here || '';
    $('#hsBanner').textContent = step.dataset.banner || '';
    hGo(st, H_CAM[i], init);
    if (!init) html.dataset.tema = 'azul';
  }

  /* ── 5. Carruseles ────────────────────────────────────────────────── */
  const CAM_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg>';
  const EXTS = ['jpg', 'png'];

  function loadSlide(fig) {
    const name = fig.dataset.foto, src = fig.dataset.src, cap = fig.dataset.cap || '';
    const img = new Image();
    img.alt = cap; img.decoding = 'async'; img.draggable = false;
    let i = 0;
    const placeholder = () => {
      const ph = document.createElement('div'); ph.className = 'ph';
      ph.innerHTML = CAM_SVG + '<b>Foto por agregar</b><small>' + (src || 'img/fotos/' + name + '.jpg') + '</small>' + (cap ? '<small><em>' + cap + '</em></small>' : '');
      fig.prepend(ph);
    };
    const next = () => {
      if (src) { if (i++ === 0) { img.src = src; return; } return placeholder(); }
      if (i >= EXTS.length) return placeholder();
      img.src = 'img/fotos/' + name + '.' + EXTS[i++];
    };
    img.onload = () => {
      fig.prepend(img);
      if (fig.hasAttribute('data-contain')) fig.classList.add('contain');
      if (cap) { const fc = document.createElement('figcaption'); fc.textContent = cap; fig.append(fc); }
    };
    img.onerror = next;
    next();
  }

  function initCarousel(root) {
    if (root.dataset.ready) return;
    root.dataset.ready = '1';
    const track = $('.bu-track', root), slides = $$('.bu-slide', track);
    slides.forEach(loadSlide);
    const dots = $('.bu-dots', root);
    slides.forEach(() => dots.append(document.createElement('i')));
    const setDot = () => {
      const n = Math.round(track.scrollLeft / Math.max(1, track.clientWidth));
      $$('i', dots).forEach((d, k) => d.classList.toggle('on', k === n));
    };
    track.addEventListener('scroll', setDot, { passive: true });
    setDot();
    const go = dir => track.scrollBy({ left: dir * track.clientWidth, behavior: 'smooth' });
    $('.bu-prev', root).addEventListener('click', () => go(-1));
    $('.bu-next', root).addEventListener('click', () => go(1));
    // arrastrar con el mouse
    let down = false, sx = 0, sl = 0;
    track.addEventListener('pointerdown', e => { if (e.pointerType !== 'mouse') return; down = true; sx = e.clientX; sl = track.scrollLeft; track.classList.add('drag'); });
    addEventListener('pointermove', e => { if (down) track.scrollLeft = sl - (e.clientX - sx); });
    addEventListener('pointerup', () => { if (!down) return; down = false; track.classList.remove('drag'); });
    if (slides.length < 2) { $('.bu-prev', root).hidden = true; $('.bu-next', root).hidden = true; dots.hidden = true; }
  }

  /* ── Arranque ─────────────────────────────────────────────────────── */
  function boot() {
    buildNavObs(); buildStepObs();
    stages.forEach(st => { if (st.steps[0]) activate(st, st.steps[0], true); });
  }
  let rz;
  addEventListener('resize', () => {
    clearTimeout(rz);
    rz = setTimeout(() => { buildNavObs(); buildStepObs(); stages.forEach(st => { if (!st.cur) return; if (st.hist) { if (hView) hDraw(st, hView); } else applyCam(st, st.cur); }); }, 160);
  });
  boot();

  /* Ayuda para pruebas: ?goto=calidad:2  (paso 2 del capítulo)  ó  ?goto=#promesa&off=900 */
  (function () {
    const q = new URLSearchParams(location.search), g = q.get('goto');
    if (!g) return;
    html.style.scrollBehavior = 'auto';
    setTimeout(() => {
      if (g[0] === '#') { const e = $(g); if (e) scrollTo(0, e.getBoundingClientRect().top + scrollY + Number(q.get('off') || 0)); return; }
      const [id, i] = g.split(':'), st = $$('#' + id + ' .step')[Number(i) || 0];
      if (!st) return;
      const r = st.getBoundingClientRect();
      scrollTo(0, mobile.matches ? scrollY + r.top - innerHeight * 0.44 - 20 : scrollY + r.top + r.height / 2 - innerHeight / 2 + 2);
    }, 400);
  })();
})();
