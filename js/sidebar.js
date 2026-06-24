const UI = (() => {

  let curEje = null;
  const switchOn = {};

  const ICONS = {
    agua:  '<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M12 2C7 9 4 13 4 17a8 8 0 0016 0c0-4-3-8-8-15z"/></svg>',
    inund: '<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M3 11c2-2 4-2 6 0s4 2 6 0 4-2 6 0v2c-2-2-4-2-6 0s-4 2-6 0-4-2-6 0zm0 5c2-2 4-2 6 0s4 2 6 0 4-2 6 0v2c-2-2-4-2-6 0s-4 2-6 0-4-2-6 0z"/></svg>',
    eco:   '<svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M17 8C8 10 5 20 5 20c3-3 6-5 9-5-1 2-3 4-6 6 9-2 12-8 12-14-1 0-2 1-3 1z"/></svg>',
  };

  function init() { renderHome(); }

  /* ── HOME / LANDING ── */
  function renderHome() {
    curEje = null;
    ['agua','inund','eco'].forEach(e =>
      document.getElementById('tab-' + e).className = 'etab'
    );
    hideBadge(); hideDboLegend();

    const wrap = document.getElementById('plist');
    wrap.innerHTML = '';

    const intro = document.createElement('div');
    intro.className = 'home-intro';
    intro.innerHTML =
      '<p class="home-text">Plan de accion 2024–2030 para el saneamiento y la restauracion integral del rio Tula, uno de los rios mas contaminados de Mexico.</p>' +
      '<p class="home-hint">Selecciona un eje para explorar las acciones en el mapa.</p>';
    wrap.appendChild(intro);

    ['agua','inund','eco'].forEach(eje => {
      const cfg = CONFIG[eje];
      const projCount = cfg.metas.reduce((s, m) => s + m.proyectos.length, 0);
      const card = document.createElement('div');
      card.className = 'theme-card tc-' + cfg.tabClass;
      card.innerHTML =
        '<div class="tc-icon">' + ICONS[eje] + '</div>' +
        '<div class="tc-body">' +
          '<div class="tc-title">' + cfg.label + '</div>' +
          '<div class="tc-desc">' + cfg.desc + '</div>' +
          '<div class="tc-counts">' + cfg.metas.length + ' metas &nbsp;&middot;&nbsp; ' + projCount + ' proyectos</div>' +
        '</div>' +
        '<div class="tc-chevron">&#8250;</div>';
      card.onclick = () => selEje(eje);
      wrap.appendChild(card);
    });
  }

  /* ── SELECCIONAR EJE ── */
  function selEje(eje) {
    curEje = eje;
    ['agua','inund','eco'].forEach(e =>
      document.getElementById('tab-' + e).className =
        'etab' + (e === eje ? ' ' + CONFIG[e].tabClass : '')
    );
    renderList();
    hideBadge(); hideDboLegend();
  }

  /* ── VOLVER AL HOME ── */
  function goHome() {
    Object.keys(switchOn).forEach(k => {
      if (!switchOn[k]) return;
      const parts = k.split('_m');
      const ejeKey = parts[0], mi = parseInt(parts[1]);
      const m = CONFIG[ejeKey] && CONFIG[ejeKey].metas[mi];
      if (m && typeof MAP !== 'undefined') {
        const keys = new Set();
        m.proyectos.forEach(p => (p.layerDefs||[]).forEach(ld => keys.add(ld.key)));
        keys.forEach(key => MAP.setLayer(key, false));
      }
      switchOn[k] = false;
    });
    if (typeof MAP !== 'undefined') MAP.resetView();
    renderHome();
  }

  /* ── TOGGLE META ── */
  function toggleMeta(metaId, isOn, ejeKey, metaIdx) {
    switchOn[metaId] = isOn;
    const cfg = CONFIG[ejeKey];
    const m   = cfg.metas[metaIdx];

    const det = document.getElementById('pin-' + metaId);
    if (det) {
      if (isOn) {
        det.innerHTML = buildMetaDetail(m, cfg);
        det.classList.add('open');
      } else {
        det.classList.remove('open');
        setTimeout(() => { det.innerHTML = ''; }, 300);
      }
    }

    if (typeof MAP !== 'undefined') {
      const keys = new Set();
      m.proyectos.forEach(p => (p.layerDefs||[]).forEach(ld => keys.add(ld.key)));
      keys.forEach(k => MAP.setLayer(k, isOn));
      if (isOn && keys.size > 0) setTimeout(() => MAP.fitToLayers([...keys]), 150);
    }

    if (isOn) {
      showBadge(m.meta, cfg.accent);
      if (m.proyectos.some(p => p.hasMon)) showDboLegend(); else hideDboLegend();
    } else {
      if (!Object.values(switchOn).some(v => v)) { hideBadge(); hideDboLegend(); }
    }

    renderList();
  }

  /* ── FILTRO MONITOREO ── */
  function filterMon(btn) {
    document.querySelectorAll('.mpill').forEach(b => b.classList.remove('mact'));
    btn.classList.add('mact');
    if (typeof MAP !== 'undefined') MAP.buildMon(btn.dataset.t);
  }

  /* ── RENDER LISTA ── */
  function renderList() {
    const cfg  = CONFIG[curEje];
    const wrap = document.getElementById('plist');
    wrap.innerHTML = '';

    const hdr = document.createElement('div');
    hdr.className = 'eje-header';
    hdr.style.setProperty('--acc', cfg.accent);
    hdr.innerHTML =
      '<button class="back-btn" onclick="UI.goHome()">&#8249; Inicio</button>' +
      '<p class="eje-desc-bar">' + cfg.desc + '</p>';
    wrap.appendChild(hdr);

    cfg.metas.forEach((m, mi) => {
      const metaId = curEje + '_m' + mi;
      const isOn   = !!switchOn[metaId];
      const accLt  = cfg.tabClass==='ta' ? '#f5e8ed' : cfg.tabClass==='ti' ? '#fdf3ec' : '#eaf3ef';

      const row = document.createElement('div');
      row.className = 'meta-row' + (isOn ? ' active' : '');
      row.style.setProperty('--acc', cfg.accent);
      row.style.setProperty('--acc-lt', accLt);
      row.innerHTML =
        '<label class="switch" onclick="event.stopPropagation()">' +
          '<input type="checkbox"' + (isOn ? ' checked' : '') +
          ' onchange="UI.toggleMeta(\'' + metaId + '\',this.checked,\'' + curEje + '\',' + mi + ')">' +
          '<span class="switch-slider"></span>' +
        '</label>' +
        '<div class="meta-row-body">' +
          '<div class="meta-row-title">' + m.meta + '</div>' +
          (m.desc ? '<div class="meta-row-desc">' + m.desc + '</div>' : '') +
        '</div>';
      wrap.appendChild(row);

      const det = document.createElement('div');
      det.className = 'pinline' + (isOn ? ' open' : '');
      det.id = 'pin-' + metaId;
      det.style.setProperty('--acc', cfg.accent);
      det.style.setProperty('--acc-lt', accLt);
      if (isOn) det.innerHTML = buildMetaDetail(m, cfg);
      wrap.appendChild(det);
    });
  }

  /* ── DETALLE DE META ── */
  function buildMetaDetail(m, cfg) {
    const hasMon = m.proyectos.some(p => p.hasMon);
    const STATUS = {'En ejecucion':'b-ej','Por iniciar':'b-pi','Terminado':'b-te','Planeacion':'b-pl'};

    const proyItems = m.proyectos.map(p => {
      const pills = (p.layerDefs||[]).map(ld =>
        '<span class="p-layer-pill">' + symHTML(ld.sym, ld.color) + ' ' + ld.label + '</span>'
      ).join('');
      return '<li class="meta-proy-item">' +
        '<div class="meta-proy-top">' +
          '<span class="meta-proy-name">' + p.titulo + '</span>' +
          '<span class="badge ' + (STATUS[p.estatus]||'b-pi') + '">' + p.estatus + '</span>' +
        '</div>' +
        '<div class="meta-proy-year">' + p.anio + '</div>' +
        (pills ? '<div class="meta-proy-pills">' + pills + '</div>' : '') +
      '</li>';
    }).join('');

    const monHTML = hasMon
      ? '<div class="mon-btns">' +
          '<button class="mpill mact" data-t="all" onclick="UI.filterMon(this)">Todas</button>' +
          '<button class="mpill" data-t="Estiaje" onclick="UI.filterMon(this)">Estiaje</button>' +
          '<button class="mpill" data-t="Lluvias" onclick="UI.filterMon(this)">Lluvias</button>' +
        '</div>'
      : '';

    return '<div class="pinline-inner"><ul class="meta-proy-list">' + proyItems + '</ul>' + monHTML + '</div>';
  }

  /* ── SIMBOLO ── */
  function symHTML(sym, color) {
    const s = 'style="background:' + color + '"';
    if (sym === 'line') return '<span class="layer-sym-line" ' + s + '></span>';
    if (sym === 'dot')  return '<span class="layer-sym-dot"  ' + s + '></span>';
    if (sym === 'dia')  return '<span class="layer-sym-dia"  ' + s + '></span>';
    if (sym === 'sq')   return '<span class="layer-sym-sq"   ' + s + '></span>';
    if (sym === 'star') return '<span class="layer-sym-star" style="color:' + color + '">&#9733;</span>';
    return '<span class="layer-sym-dot" ' + s + '></span>';
  }

  /* ── BADGE / LEYENDA ── */
  function showBadge(text, color) {
    const el = document.getElementById('map-badge');
    document.getElementById('map-badge-txt').textContent = text;
    el.style.borderLeftColor = color;
    el.classList.remove('hidden');
  }
  function hideBadge()     { document.getElementById('map-badge').classList.add('hidden'); }
  function showDboLegend() { document.getElementById('dbo-legend').classList.remove('hidden'); }
  function hideDboLegend() { document.getElementById('dbo-legend').classList.add('hidden'); }

  return { init, selEje, goHome, toggleMeta, filterMon };

})();

document.addEventListener('DOMContentLoaded', UI.init);
