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


  /* ── Historia: mapa SVG (relieve real + capas GIS; cámara fija salvo las dos
     primeras épocas, viewBox 551.7×628.9) ──────────────────────────── */
  const H_POS   = [0, 14, 28, 42, 56, 68, 78, 88, 100];
  const H_FULL  = [276, 314, 660];
  const H_ALL   = [500, 442, 960];   // época 1: la cuenca del Valle de México completa
  const H_TENOCH = [330, 560, 480];  // época 2: un poco más cerca de Tenochtitlan
  const H_CAM   = [H_ALL, H_TENOCH, H_FULL, H_FULL, H_FULL, H_FULL, H_FULL, H_FULL, H_FULL];
  // marcador de énfasis (círculo que pulsa): a dónde se mueve en cada época; sin entrada = oculto
  const H_ENF   = { 1: [373, 609], 2: [319, 308], 4: [214, 107], 6: [264, 228], 7: [211, 165], 8: [211, 165] };
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
    q('.distritos').classList.toggle('on', i >= 4);
    q('.dique').classList.toggle('on', i === 1);
    q('.manzanas').classList.toggle('on', i === 7);
    $$('.hito', svg).forEach(h => h.classList.toggle('on', i === 1));
    const enf = q('#hsEnfasis'), pos = H_ENF[i];
    enf.classList.toggle('on', !!pos);
    if (pos) $$('circle', enf).forEach(c => { c.setAttribute('cx', pos[0]); c.setAttribute('cy', pos[1]); });
    $('#hsDot').style.left = H_POS[i] + '%'; $('#hsFill').style.width = H_POS[i] + '%';
    const here = $('#hsHere'); here.style.left = H_POS[i] + '%'; here.textContent = step.dataset.here || '';
    $('#hsBanner').textContent = step.dataset.banner || '';
    hGo(st, H_CAM[i], init);
    if (!init) html.dataset.tema = 'azul';
  }

  /* ── 5. Carruseles ────────────────────────────────────────────────── */
  const CAM_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg>';

  function loadSlide(fig) {
    const src = fig.dataset.src, cap = fig.dataset.cap || '', pend = fig.dataset.pend;
    const placeholder = (ruta) => {
      const ph = document.createElement('div'); ph.className = 'ph';
      ph.innerHTML = CAM_SVG + '<b>Foto por agregar</b>';
      const small = document.createElement('small'); small.textContent = ruta;
      ph.append(small);
      fig.prepend(ph);
    };
    if (pend) { placeholder(pend); return; }
    if (!src) return;
    const img = new Image();
    img.alt = cap; img.decoding = 'async'; img.draggable = false;
    img.onload = () => {
      fig.prepend(img);
      if (fig.hasAttribute('data-contain')) fig.classList.add('contain');
      if (cap) { const fc = document.createElement('figcaption'); fc.textContent = cap; fig.append(fc); }
    };
    img.onerror = () => placeholder(src);
    img.src = src;
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
    const go = dir => {
      const w = Math.max(1, track.clientWidth), n = Math.round(track.scrollLeft / w) + dir;
      track.scrollTo({ left: ((n + slides.length) % slides.length) * w, behavior: 'smooth' });
    };
    $('.bu-prev', root).addEventListener('click', () => go(-1));
    $('.bu-next', root).addEventListener('click', () => go(1));
    // arrastrar con el mouse
    let down = false, sx = 0, sl = 0;
    track.addEventListener('pointerdown', e => { if (e.pointerType !== 'mouse') return; down = true; sx = e.clientX; sl = track.scrollLeft; track.classList.add('drag'); });
    addEventListener('pointermove', e => { if (down) track.scrollLeft = sl - (e.clientX - sx); });
    addEventListener('pointerup', () => { if (!down) return; down = false; track.classList.remove('drag'); });
    // clic en la foto (sin arrastrar) = ampliar
    let px = 0, py = 0;
    track.addEventListener('pointerdown', e => { px = e.clientX; py = e.clientY; });
    track.addEventListener('click', e => {
      if (Math.abs(e.clientX - px) > 6 || Math.abs(e.clientY - py) > 6) return;
      const fig = e.target.closest('.bu-slide');
      if (!fig || !$('img', fig)) return;
      document.dispatchEvent(new CustomEvent('ampliar', { detail: { track, index: slides.indexOf(fig) } }));
    });
    if (slides.length < 2) {
      $('.bu-prev', root).hidden = true; $('.bu-next', root).hidden = true; dots.hidden = true;
      const hint = $('.bu-hint', root); if (hint) hint.hidden = true;
    }
  }

  /* ── Resumen: mapa con hover-highlight de las 5 metas ─────────────── */
  function initResumen() {
    const root = $('#resumenStage'); if (!root) return;
    const canvas = $('.canvas', root), metas = $$('#resumenMetas .meta');
    function applyMetaCam(cam) {
      let [x, y, z] = (cam || '0.5,0.5,1').split(',').map(Number);
      if (mobile.matches) z = Math.max(1, z * 0.8);
      const W = root.clientWidth, H = root.clientHeight;
      const Wc = Math.max(W, H * 16 / 9), Hc = Wc * 9 / 16;
      let tx = -z * (x - 0.5) * Wc, ty = -z * (y - 0.5) * Hc;
      const mx = Math.max(0, (z * Wc - W) / 2), my = Math.max(0, (z * Hc - H) / 2);
      tx = Math.min(mx, Math.max(-mx, tx));
      ty = Math.min(my, Math.max(-my, ty));
      canvas.style.setProperty('--tx', tx.toFixed(1) + 'px');
      canvas.style.setProperty('--ty', ty.toFixed(1) + 'px');
      canvas.style.setProperty('--z', z);
    }
    function show(li) {
      metas.forEach(m => {
        const on = m === li;
        m.classList.toggle('active', on);
        m.setAttribute('aria-expanded', String(on));
      });
      const d = li.dataset;
      $$('.frame', canvas).forEach(f => f.classList.toggle('on', f.dataset.frame === d.frame));
      const ovs = list(d.ov);      $$('.ov', canvas).forEach(o => o.classList.toggle('on', ovs.includes(o.dataset.ov)));
      const pins = list(d.pins);   $$('.pin', canvas).forEach(p => p.classList.toggle('on', pins.includes(p.dataset.id)));
      const lbls = list(d.labels); $$('.maplabel', canvas).forEach(p => p.classList.toggle('on', lbls.includes(p.dataset.id)));
      applyMetaCam(d.cam);
    }
    metas.forEach(li => {
      li.addEventListener('click', () => show(li));
      li.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); show(li); }
      });
    });
    if (metas[0]) show(metas[0]);
    addEventListener('resize', () => {
      const on = metas.find(m => m.classList.contains('active'));
      if (on) applyMetaCam(on.dataset.cam);
    });
  }

  /* ── Lightbox: ampliar fotos (clic en la foto); sigue
     funcionando como carrusel adentro, con las mismas fotos ──────────── */
  function initLightbox() {
    const box = $('#lightbox'); if (!box) return;
    const img = $('#lightboxImg', box), cap = $('#lightboxCap', box);
    const prevBtn = $('.lightbox-prev', box), nextBtn = $('.lightbox-next', box);
    let fotos = [], i = 0;
    function render() {
      const f = fotos[i];
      img.src = f.src; img.alt = f.cap || ''; cap.textContent = f.cap || '';
      const varias = fotos.length > 1;
      prevBtn.hidden = nextBtn.hidden = !varias;
    }
    function open(track, startIndex) {
      fotos = $$('.bu-slide', track).map(s => { const im = $('img', s); return im ? { src: im.src, cap: im.alt } : null; }).filter(Boolean);
      if (!fotos.length) return;
      i = Math.max(0, Math.min(startIndex, fotos.length - 1));
      render();
      box.classList.add('on');
    }
    function close() { box.classList.remove('on'); img.src = ''; }
    function step(dir) { if (fotos.length < 2) return; i = (i + dir + fotos.length) % fotos.length; render(); }
    $('.lightbox-close', box).addEventListener('click', close);
    prevBtn.addEventListener('click', () => step(-1));
    nextBtn.addEventListener('click', () => step(1));
    box.addEventListener('click', e => { if (e.target === box) close(); });
    addEventListener('keydown', e => {
      if (!box.classList.contains('on')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') step(-1);
      if (e.key === 'ArrowRight') step(1);
    });
    document.addEventListener('ampliar', e => open(e.detail.track, e.detail.index));
  }

  /* ── Introducción: pestañas (mapa / caudales), resalte por paso, tooltip del Sankey y letra constante del mapa ── */
  function initOrigen() {
    const svg = $('#omap'); if (!svg) return;
    const vb = svg.viewBox.baseVal;
    const fit = () => { const k = Math.min(svg.clientWidth / vb.width, svg.clientHeight / vb.height) || 1; svg.style.setProperty('--fs', (11.5 / k).toFixed(3)); };
    fit(); addEventListener('resize', fit);
    $$('.or-tab').forEach(b => b.addEventListener('click', () => {
      $$('.or-tab').forEach(x => x.classList.toggle('on', x === b));
      $$('.or-pane').forEach(p => p.classList.toggle('on', p.dataset.pane === b.dataset.tab));
      fit(); fitSections();
    }));
    const ks = [['tec', 'teo', 'salto', 'canal'], ['portal', 'ptar', 'dr'], ['rios', 'presa', 'tula', 'endho']];
    const offMapa = () => { svg.classList.remove('hl'); $$('[data-k].is, #orPasos li.is').forEach(el => el.classList.remove('is')); };
    $$('#orPasos li').forEach((li, i) => {
      const on = () => { offMapa(); svg.classList.add('hl'); li.classList.add('is'); $$('[data-k]', svg).forEach(el => el.classList.toggle('is', (ks[i] || []).includes(el.dataset.k))); };
      li.addEventListener('mouseenter', on); li.addEventListener('mouseleave', offMapa);
      li.addEventListener('click', () => (li.classList.contains('is') ? offMapa() : on()));
    });
    const tip = document.createElement('div'); tip.className = 'sk-tip'; document.body.append(tip);
    const off = () => { tip.classList.remove('on'); $$('.sankey.dim').forEach(x => x.classList.remove('dim')); $$('.sk-l.hv').forEach(p => p.classList.remove('hv')); };
    $$('.dn').forEach(f => {
      const v = $('.dn-v', f), u = $('.dn-u', f), v0 = v.textContent, u0 = u.textContent;
      $$('.dn-seg', f).forEach(sg => {
        sg.addEventListener('mouseenter', e => {
          sg.classList.add('on'); f.classList.add('hv'); v.textContent = sg.dataset.p + ' %'; u.textContent = sg.dataset.v + ' m³/s';
          tip.innerHTML = '<b>' + sg.dataset.n + '</b>'; tip.classList.add('on');
        });
        sg.addEventListener('mousemove', e => { tip.style.left = Math.min(e.clientX + 14, innerWidth - 260) + 'px'; tip.style.top = (e.clientY + 14) + 'px'; });
        sg.addEventListener('mouseleave', () => { sg.classList.remove('on'); f.classList.remove('hv'); v.textContent = v0; u.textContent = u0; tip.classList.remove('on'); });
      });
    });
    $$('.dn-ley li[data-i]').forEach(li => {
      const set = on => $$('.dn-seg[data-i="' + li.dataset.i + '"]').forEach(sg => { sg.classList.toggle('on', on); sg.closest('.dn').classList.toggle('hv', on); li.classList.toggle('on', on); });
      li.addEventListener('mouseenter', () => set(true)); li.addEventListener('mouseleave', () => set(false));
    });
    $$('.sankey').forEach(sk => {
    $$('.sk-l', sk).forEach(p => {
      const show = e => {
        const [a, q, d] = p.dataset.tip.split('|');
        tip.innerHTML = '<b>' + a + '</b><br>' + q + (d ? ' · ' + d : '');
        tip.style.left = Math.min(e.clientX + 14, innerWidth - 230) + 'px'; tip.style.top = (e.clientY + 14) + 'px';
        tip.classList.add('on'); sk.classList.add('dim'); $$('.sk-l.hv', sk).forEach(x => x.classList.remove('hv')); p.classList.add('hv');
      };
      p.addEventListener('mousemove', show); p.addEventListener('click', show); p.addEventListener('mouseleave', off);
    });
    });
    addEventListener('scroll', off, { passive: true });
  }

  /* ── Guía lateral de los cuatro lemas: aparece junta, se abre y resalta el lema actual ── */
  function initRail() {
    const rail = $('#lemaRail'); if (!rail) return;
    const ks = ['limpio', 'seguro', 'vivo', 'todos'], lemas = ks.map(k => $('#lema-' + k)), fin = $('#resumen');
    const items = $$('.lr-i', rail), fill = $('#lrFill');
    let tick = false, timer = 0;
    function upd() {
      tick = false;
      const vh = innerHeight, first = lemas[0].getBoundingClientRect().top, end = fin ? fin.getBoundingClientRect().top : Infinity;
      const vis = first < vh * 0.55 && end > vh * 0.45;
      if (vis && !rail.classList.contains('show')) { rail.classList.add('show'); clearTimeout(timer); timer = setTimeout(() => rail.classList.add('spread'), 520); }
      if (!vis) { clearTimeout(timer); rail.classList.remove('show', 'spread'); }
      const ban = $$('.cap-stage .banner.dos').map(b => b.getBoundingClientRect()).find(r => r.top > 40 && r.top < vh * 0.45);
      rail.style.top = (ban ? ban.bottom + 14 : 176) + 'px';
      rail.classList.toggle('con', !!ban);
      let act = -1;
      lemas.forEach((l, i) => { if (l.getBoundingClientRect().top <= vh * 0.5) act = i; });
      items.forEach((it, i) => { it.classList.toggle('on', i === act); it.classList.toggle('past', i < act); });
      if (act >= 0) { rail.style.setProperty('--lc', getComputedStyle(items[act]).getPropertyValue('--c').trim()); fill.style.height = Math.max(0, 5 + act * 0.2325 * rail.clientHeight) + 'px'; }
      else fill.style.height = '0';
    }
    addEventListener('scroll', () => { if (!tick) { tick = true; requestAnimationFrame(upd); } }, { passive: true });
    addEventListener('resize', upd);
    upd();
  }

  /* ── Números que cuentan hacia arriba al entrar en pantalla ── */
  function initContadores() {
    const els = $$('.cnt'); if (!els.length || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const obs = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return;
      obs.unobserve(e.target);
      const el = e.target, m = el.textContent.match(/^(\D*?)(\d[\d,]*\.?\d*)(.*)$/);
      if (!m) return;
      const dec = (m[2].split('.')[1] || '').length, coma = m[2].includes(','), fin = parseFloat(m[2].replace(/,/g, '')), t0 = performance.now(), dur = 1300;
      const fmt = v => { let s = v.toFixed(dec); if (coma) { const [a, b] = s.split('.'); s = a.replace(/\B(?=(\d{3})+(?!\d))/g, ',') + (b ? '.' + b : ''); } return s; };
      const tick = now => { const k = Math.min(1, (now - t0) / dur), v = fin * (1 - Math.pow(1 - k, 3)); el.textContent = m[1] + fmt(v) + m[3]; if (k < 1) requestAnimationFrame(tick); };
      requestAnimationFrame(tick);
    }), { threshold: 0.6 });
    els.forEach(el => obs.observe(el));
  }

  /* ── Ajuste a la pantalla: cada sección y cada tarjeta caben en el 100 % de la vista ── */
  function fitSections() {
    $$('[data-fit]').forEach(sec => {
      const inner = $('.fit-in', sec); if (!inner) return;
      inner.style.zoom = '';
      if (mobile.matches) return;
      const cs = getComputedStyle(sec), pad = parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom);
      const h = inner.getBoundingClientRect().height, avail = innerHeight - pad;
      if (h > avail) inner.style.zoom = Math.max(0.5, avail / h).toFixed(3);
    });
  }
  function fitCards() {
    $$('.cap .step .card').forEach(c => {
      c.style.zoom = '';
      if (mobile.matches) return;
      const top = c.closest('.cap').classList.contains('hist') ? 140 : 176, avail = innerHeight - top - 28, h = c.offsetHeight;
      if (h > avail) c.style.zoom = Math.max(0.55, avail / h).toFixed(3);
    });
  }
  function fitAll() { fitSections(); fitCards(); }
  addEventListener('resize', () => { clearTimeout(fitAll.t); fitAll.t = setTimeout(fitAll, 120); });
  addEventListener('load', fitAll);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitAll);

  /* ── Accesibilidad: modo noche y modo daltonismo (se recuerdan en este navegador) ── */
  function initA11y() {
    const root = $('.a11y'); if (!root) return;
    const btn = $('#a11yBtn'), noche = $('#swNoche'), cvd = $('#swCvd');
    const guardar = (k, v) => { try { localStorage.setItem(k, v ? '1' : '0'); } catch (e) {} };
    const toggle = open => { root.classList.toggle('open', open); btn.setAttribute('aria-expanded', String(open)); };
    btn.addEventListener('click', e => { e.stopPropagation(); toggle(!root.classList.contains('open')); });
    document.addEventListener('click', e => { if (!root.contains(e.target)) toggle(false); });
    addEventListener('keydown', e => { if (e.key === 'Escape') toggle(false); });

    const CVD_DR = { '#d17b3f': '#e69f00', '#7a6bb0': '#0072b2', '#b8577a': '#cc79a7' };
    const FILTROS = { 'f-rosa': [0, 0.447, 0.698, 1], 'f-naranja': [0.835, 0.369, 0, 1], 'f-naranja-x2': [0.835, 0.369, 0, 2.6], 'f-verde': [0, 0.62, 0.451, 1] };
    const lerp = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * t));
    const rgb = c => '#' + c.map(v => v.toString(16).padStart(2, '0')).join('');
    const cvdDbo = d => { const az = [86, 180, 233], am = [240, 228, 66], rj = [213, 94, 0]; return rgb(d <= 50 ? az : d <= 100 ? lerp(az, am, (d - 50) / 50) : lerp(am, rj, Math.min(1, (d - 100) / 50))); };
    function aplicarCvd(on) {
      document.documentElement.toggleAttribute('data-cvd', on);
      Object.entries(FILTROS).forEach(([id, v]) => {
        const m = document.querySelector('#' + id + ' feColorMatrix'); if (!m) return;
        if (!m.dataset.orig) m.dataset.orig = m.getAttribute('values');
        m.setAttribute('values', on ? '0 0 0 0 ' + v[0] + '  0 0 0 0 ' + v[1] + '  0 0 0 0 ' + v[2] + '  0 0 0 ' + v[3] + ' 0' : m.dataset.orig);
      });
      $$('.sankey.mode-cal .sk-l').forEach(p => {
        if (!p.dataset.fill) p.dataset.fill = p.getAttribute('fill');
        p.setAttribute('fill', on && p.dataset.dbo ? cvdDbo(Number(p.dataset.dbo)) : p.dataset.fill);
      });
      $$('.sk-grad').forEach(g => {
        if (!g.dataset.bg) g.dataset.bg = g.getAttribute('style');
        g.setAttribute('style', on ? 'background:linear-gradient(90deg,#56b4e9,#f0e442 62%,#d55e00)' : g.dataset.bg);
      });
      $$('[style]').forEach(el => {
        const st = el.getAttribute('style') || '';
        if (on) { if (/#(d17b3f|7a6bb0|b8577a)/i.test(st)) { if (!el.dataset.st) el.dataset.st = st; el.setAttribute('style', st.replace(/#(d17b3f|7a6bb0|b8577a)/gi, m => CVD_DR[m.toLowerCase()])); } }
        else if (el.dataset.st) { el.setAttribute('style', el.dataset.st); delete el.dataset.st; }
      });
    }
    noche.checked = document.documentElement.dataset.theme === 'dark';
    cvd.checked = document.documentElement.hasAttribute('data-cvd');
    noche.addEventListener('change', () => { if (noche.checked) document.documentElement.dataset.theme = 'dark'; else delete document.documentElement.dataset.theme; guardar('rt-noche', noche.checked); });
    cvd.addEventListener('change', () => { aplicarCvd(cvd.checked); guardar('rt-cvd', cvd.checked); });
    if (cvd.checked) aplicarCvd(true);
  }

  /* ── Arranque ─────────────────────────────────────────────────────── */
  function boot() {
    buildNavObs(); buildStepObs();
    stages.forEach(st => { if (st.steps[0]) activate(st, st.steps[0], true); });
    // carruseles fuera del scroll por pasos (p. ej. el de "Compromiso 92")
    $$('[data-carousel]').forEach(initCarousel);
    initResumen();
    initOrigen();
    initRail();
    initA11y();
    initContadores();
    fitAll();
    initLightbox();
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
