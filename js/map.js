/**
 * map.js — v5
 */
const MAP = (() => {

  const CENTER   = [20.04, -99.30];
  const ZOOM     = 11;
  const DATA_DIR = 'data/';

  let map;
  let monLayer = null;
  let _initBounds = null;
  const _cache = {};

  /* ── INIT ────────────────────────────────── */
  function initMap() {
    if (typeof L === 'undefined') {
      document.getElementById('map').innerHTML =
        '<div style="height:100%;display:flex;align-items:center;justify-content:center;color:#888;font-size:15px;padding:2rem;text-align:center">Corre con <b>python riotula.py</b> y abre http://localhost:5500</div>';
      return;
    }
    map = L.map('map', { zoomControl: true }).setView(CENTER, ZOOM);
    setTimeout(() => map.invalidateSize(), 300);
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
      { attribution: '© ESRI', maxZoom: 16 }).addTo(map);
    preloadLayers();
  }

  /* ── MAPA BASE — siempre visible ─────────── */
  async function loadAllBaseLayers() {
    const CUERPO = { color:'#1a4d5c', weight:1, opacity:.8, fillColor:'#1a4d5c', fillOpacity:1 };
    const capas = [
      { f:'delimitacion2030',   e:{ color:'#7a1a2e', weight:1.5, opacity:.9,  fillOpacity:0 }},
      { f:'rio_tula',           e:{ color:'#1a4d5c', weight:1.5, opacity:.85, fillOpacity:0 }},
      { f:'cuerpos_de_agua',    e: CUERPO },
      { f:'humedales',          e:{ color:'#1a4d5c', weight:1,   opacity:.7,  fillColor:'#2a7080', fillOpacity:1 }},
      { f:'tren_mx_qro',        e:{ color:'#888',    weight:1.5, opacity:.55, fillOpacity:0, dashArray:'6 4' }},
      { f:'dn',                 e: CUERPO },
    ];

    for (const capa of capas) {
      try {
        const r  = await fetch('data/mapa%20base/' + capa.f + '.geojson');
        if (!r.ok) { console.warn('No se cargo mapa base:', capa.f); continue; }
        const fc  = await r.json();
        const tipo = fc.features?.[0]?.geometry?.type || '';
        let lyr;
        if (tipo.includes('Point')) {
          lyr = L.geoJSON(fc, {
            pointToLayer: (f, ll) => L.circleMarker(ll, {
              radius:5, color:capa.e.color, fillColor:capa.e.fillColor||capa.e.color,
              fillOpacity:capa.e.fillOpacity??1, weight:capa.e.weight||1, opacity:capa.e.opacity||1
            })
          }).addTo(map);
        } else {
          lyr = L.geoJSON(fc, { style: capa.e }).addTo(map);
        }
        if (capa.f === 'delimitacion2030') {
          _initBounds = lyr.getBounds();
          map.setView(_initBounds.getCenter(), 9);
        }
      } catch(e) { console.warn('Error capa base:', capa.f, e.message); }
    }
  }

  /* ── PRE-CARGAR CAPAS DE PROYECTOS ──────── */
  async function preloadLayers() {
    await loadAllBaseLayers();

    await Promise.all([
      /* CALIDAD DEL AGUA */
      loadColectores(),
      loadPoint('atotonilco', makeLabel('PTAR Atotonilco','#9b2247'),
        {titulo:'PTAR Atotonilco', kv:[], desc:'Planta de Tratamiento de Aguas Residuales de Atotonilco.', media:[]}),
      loadPoint('cfe', makeLabel('PTAR CFE','#285c4d'),
        {titulo:'PTAR CFE Tula', kv:[], desc:'Planta de Tratamiento de Aguas Residuales de la CFE en Tula.', media:[]}),
      loadPoint('pemex', makeLabel('Pemex','#7f3d1e'),
        {titulo:'Refineria Miguel Hidalgo', kv:[{l:'Estaciones',v:'5'}], desc:'Monitoreo y control de la descarga de la refineria para reducir riesgos de contaminacion en el rio Tula.', media:[]}),
      loadPoint('estaciones', makeIcon('dot','#2f5d6d',11),
        {titulo:'Estacion automatica', kv:[], desc:'Estacion automatica para el monitoreo permanente de calidad y cantidad del agua.', media:[]}),
      loadPoint('centro_de_vigilancia', makeIcon('star','#9b2247',16),
        {titulo:'Centro de vigilancia', kv:[], desc:'Centro de visualizacion y vigilancia para el monitoreo permanente de la calidad y cantidad del agua.', media:[]}, 'centro'),
      loadDiamonds(),

      /* PREVENCION DE INUNDACIONES */
      loadGeoLayer('estabilizacion_de_taludes',
        {color:'#c45e1a', weight:3, fillColor:'#ed7d31', fillOpacity:.5},
        {titulo:'Estabilizacion de taludes', desc:'Obras de estabilizacion de taludes, revegetacion y rehabilitacion de bordos en tramos criticos del rio Tula.'}),
      loadGeoLayer('azolve',
        {color:'#c45e1a', weight:2.5, fillColor:'#ff9e5d', fillOpacity:.6},
        {titulo:'Desazolve / Trampa de azolve', desc:'Retiro de sedimentos y construccion de infraestructura para reducir riesgos de inundacion.'}),
      loadGeoLayer('zona_inundable',
        {color:'#c45e1a', weight:1.5, fillColor:'#ff8f44', fillOpacity:.3},
        {titulo:'Zona inundable Tres Culturas', desc:'Recuperacion y habilitacion de zona inundable como area de amortiguamiento hidraulico.'}),
      loadGeoLayer('estaciones_hidrometricas_monitoreo',
        {color:'#c45e1a', weight:2, fillColor:'#ed7d31', fillOpacity:.8},
        {titulo:'Estacion hidrometrica', desc:'Estacion automatica para monitoreo en tiempo real de caudales y niveles.'}),
      loadGeoLayer('estaciones_hidroclimatologicas_monitoreo',
        {color:'#c45e1a', weight:2, fillColor:'#ed7d31', fillOpacity:.8},
        {titulo:'Estacion hidroclimatologica', desc:'Estacion automatica de monitoreo hidroclimatologico.'}),

      /* RESTAURACION ECOLOGICA */
      loadGeoLayer('revegetacion_de_margenes',
        {color:'#285c4d', weight:2, fillColor:'#4a9e7a', fillOpacity:.6},
        {titulo:'Revegetacion de margenes', desc:'Plantacion de 300 arboles y 3,400 herbaceas en margenes del rio Tula.'}),
      loadGeoLayer('saneamiento_forestal',
        {color:'#285c4d', weight:2, fillColor:'#5a8048', fillOpacity:.5},
        {titulo:'Saneamiento de arboles', desc:'Saneamiento fitosanitario de mas de 1,600 arboles riberenos.'}),
      loadGeoLayer('zona_federal',
        {color:'#285c4d', weight:2, fillColor:'#285c4d', fillOpacity:.2, dashArray:'5 4'},
        {titulo:'Liberacion de zona federal', desc:'Recuperacion y liberacion de zonas federales invadidas para restaurar la conectividad ecologica.'}),
      loadGeoLayer('conservacion_forestal',
        {color:'#619787', weight:1.5, fillColor:'#85b2a5', fillOpacity:.35},
        {titulo:'Conservacion forestal', desc:'Conservacion de mas de 1,700 hectareas mediante ADVC y acciones de proteccion forestal.'}),
      loadGeoLayer('restauracion_forestal',
        {color:'#285c4d', weight:1.5, fillColor:'#4a9e7a', fillOpacity:.4},
        {titulo:'Restauracion forestal', desc:'Restauracion ecologica de mas de 600 hectareas en zonas prioritarias.'}),
      loadGeoLayer('nueva_anp',
        {color:'#1a4d30', weight:2, fillColor:'#285c4d', fillOpacity:.25},
        {titulo:'Nueva ANP en Tula', desc:'Nueva Area Natural Protegida de 100 hectareas.'}),
      loadGeoLayer('bojay',
        {color:'#285c4d', weight:2, fillColor:'#4a9e7a', fillOpacity:.5},
        {titulo:'Restauracion cuerpo de agua Bojay', desc:'Restauracion de 60 hectareas del cuerpo de agua y zona riberena de Bojay.'}),
      loadGeoLayer('endho',
        {color:'#1a4d5c', weight:2, fillColor:'#2a7080', fillOpacity:.4},
        {titulo:'Presa Endho', desc:'Estrategia integral de saneamiento y restauracion ecologica de la presa Endho.'}),
    ]);

    await loadMon('all');
    console.log('Todas las capas listas');
  }

  /* ── CAPA GENERICA ───────────────────────── */
  async function loadGeoLayer(nombre, estilo, info) {
    const key = nombre;
    try {
      const r = await fetch(DATA_DIR + nombre + '.geojson');
      if (!r.ok) { console.warn('No se cargo:', nombre); return; }
      const fc = await r.json();
      _cache[nombre] = fc;
      LAYERS[key] = L.geoJSON(fc, {
        style: estilo,
        pointToLayer: (f, ll) => L.circleMarker(ll, {
          radius:6, color:estilo.color, fillColor:estilo.fillColor||estilo.color,
          fillOpacity:estilo.fillOpacity??0.9, weight:estilo.weight||1.5, opacity:estilo.opacity??1
        }),
        onEachFeature: (f, l) => {
          const titulo = f.properties?.nombre || f.properties?.Name || info.titulo;
          bindHoverTooltip(l, {titulo, color:estilo.color, kv:[], desc:info.desc, media:info.media||[]});
        },
      });
    } catch(e) { console.warn('Error:', nombre, e.message); }
  }

  /* ── ZOOM A CAPAS ────────────────────────── */
  function fitToLayers(keys) {
    const lats = [], lngs = [];

    keys.forEach(k => {
      // Usar coordenadas del cache GeoJSON directamente (mas confiable que getBounds)
      const fc = _cache[k] || _cache[k.replace(/_/g, ' ')];
      if (!fc || !fc.features) return;

      fc.features.forEach(f => {
        const g = f.geometry;
        if (!g) return;
        collectCoords(g.coordinates, g.type, lats, lngs);
      });
    });

    if (!lats.length) { console.warn('fitToLayers: sin coordenadas para', [...keys]); return; }

    const minLat = Math.min(...lats), maxLat = Math.max(...lats);
    const minLng = Math.min(...lngs), maxLng = Math.max(...lngs);

    // Verificar que sean WGS84 valido (UTM tendria valores > 1000)
    if (Math.abs(minLat) > 90 || Math.abs(maxLat) > 90 || Math.abs(minLng) > 180 || Math.abs(maxLng) > 180) {
      console.warn('CRS incorrecto — exporta en 4326 desde QGIS:', [...keys]);
      if (_initBounds) map.flyTo(_initBounds.getCenter(), 9, {duration:1});
      return;
    }

    map.fitBounds([[minLat, minLng],[maxLat, maxLng]], {padding:[40,40], maxZoom:14});
  }

  function collectCoords(coords, type, lats, lngs) {
    if (!coords) return;
    if (type === 'Point') {
      lngs.push(coords[0]); lats.push(coords[1]);
    } else if (type === 'MultiPoint' || type === 'LineString') {
      coords.forEach(c => { lngs.push(c[0]); lats.push(c[1]); });
    } else if (type === 'MultiLineString' || type === 'Polygon') {
      coords.forEach(ring => ring.forEach(c => { lngs.push(c[0]); lats.push(c[1]); }));
    } else if (type === 'MultiPolygon') {
      coords.forEach(poly => poly.forEach(ring => ring.forEach(c => { lngs.push(c[0]); lats.push(c[1]); })));
    }
  }

  /* ── ENCENDER / APAGAR CAPA ──────────────── */
  function setLayer(key, isOn) {
    const lyr = LAYERS[key];
    if (!lyr) { console.warn('Capa no encontrada:', key); return; }
    if (isOn) lyr.addTo(map);
    else { try { map.removeLayer(lyr); } catch(e) {} }
  }

  /* ── MONITOREO ───────────────────────────── */
  async function buildMon(temp) {
    const fc = await fetchGeo('monitoreo_manual');
    if (!fc) return;
    const wasOn = monLayer && map.hasLayer(monLayer);
    if (monLayer) { try { map.removeLayer(monLayer); } catch(e) {} }
    const feats = temp === 'all' ? fc.features : fc.features.filter(f => f.properties.temporada === temp);
    monLayer = L.geoJSON({type:'FeatureCollection', features:feats}, {
      pointToLayer: (f, ll) => L.marker(ll, {icon: makeIcon('sq', dboColor(f.properties.DBO), 9)()}),
      onEachFeature: (f, l) => {
        const p = f.properties;
        bindHoverTooltip(l, {
          titulo: p.sitio || 'Sitio de monitoreo', color:'#9b2247',
          kv:[{l:'Temporada',v:p.temporada||'-'},{l:'DBO',v:fmt(p.DBO)+' mg/L'},{l:'DQO',v:fmt(p.DQO)+' mg/L'},{l:'OD',v:fmt(p.OD)+' mg/L'},{l:'pH',v:fmt(p.pH)}],
          desc: p.cuerpo ? 'Cuerpo de agua: '+p.cuerpo+'. Municipio: '+(p.municipio||'-')+'.' : '',
          media:[],
        });
      },
    });
    LAYERS.monitoreo = monLayer;
    if (wasOn) monLayer.addTo(map);
  }

  /* ── COLECTORES ──────────────────────────── */
  async function loadColectores() {
    const fc = await fetchGeo('colectores');
    if (!fc) return;
    const defs = {
      Tula:   {key:'colTula',   color:'#1a7a3f', label:'Colector rio Tula'},
      Salado: {key:'colSalado', color:'#c0392b', label:'Colector rio Salado'},
      CFE:    {key:'colCFE',    color:'#285c4d', label:'Colector CFE'},
    };
    Object.entries(defs).forEach(([tipo, d]) => {
      const feats = fc.features.filter(f => f.properties.tipo === tipo);
      LAYERS[d.key] = L.geoJSON({type:'FeatureCollection', features:feats}, {
        style:{color:d.color, weight:4, opacity:.9, lineJoin:'round', lineCap:'round'},
        onEachFeature:(f,l) => bindHoverTooltip(l, {
          titulo:d.label, color:d.color,
          kv:[{l:'Longitud total',v:'38',u:'km'},{l:'Descargas captadas',v:'148'}],
          desc:'Construccion de colectores para captar descargas de aguas residuales y conducirlas a la PTAR de la CFE en Tula.',
          media:[],
        }),
      });
    });
  }

  async function loadPoint(name, iconFn, info, layerKey) {
    const fc = await fetchGeo(name);
    if (!fc) return;
    const lkey = layerKey || name;
    LAYERS[lkey] = L.geoJSON(fc, {
      pointToLayer: (f, ll) => L.marker(ll, {icon: iconFn(f)}),
      onEachFeature: (f, l) => bindHoverTooltip(l, {titulo:info.titulo, color:'#9b2247', kv:info.kv, desc:info.desc, media:info.media||[]}),
    });
  }

  async function loadDiamonds() {
    const fc = await fetchGeo('industrias');
    if (!fc) return;
    LAYERS.industrias = L.geoJSON(fc, {
      pointToLayer: (f, ll) => L.marker(ll, {icon: makeIcon('dia','#9b2247',10)()}),
      onEachFeature: (f, l) => {
        const p = f.properties;
        bindHoverTooltip(l, {
          titulo:p.nombre||'Industria', color:'#9b2247',
          kv:[{l:'Municipio',v:p.municipio||'-'},{l:'Descarga rio',v:p.descarga?'Si':'No'}],
          desc:'Industria sujeta a inspeccion y vigilancia ambiental en la cuenca del rio Tula.',
          media:[],
        });
      },
    });
  }

  async function loadMon(temp) { await buildMon(temp); }

  /* ── TOOLTIP ─────────────────────────────── */
  let _carCur = 0, _carItems = [];

  function buildTooltipHTML(data) {
    const color   = data.color || '#9b2247';
    const colorDk = shadeColor(color, -30);
    const kvHTML  = data.kv && data.kv.length
      ? '<ul class="tt-ul">' + data.kv.map(k => '<li><strong>'+k.l+':</strong> '+k.v+(k.u?' '+k.u:'')).join('') + '</ul>' : '';
    const descHTML = data.desc ? '<p class="tt-p">'+data.desc+'</p>' : '';
    return '<div class="tt-box" style="border-top-color:'+color+'"><h3 class="tt-h3" style="color:'+colorDk+'">'+data.titulo+'</h3>'+kvHTML+descHTML+'</div>';
  }

  function bindHoverTooltip(layer, data) {
    layer.bindTooltip(buildTooltipHTML(data), {
      sticky: true,
      opacity: 1,
      className: 'rich-tooltip',
      direction: 'top'
    });
  }

  function openTooltip(layer, data) {
    const html = buildTooltipHTML(data) + buildCarousel(data.media||[]);
    const latlng = layer.getLatLng ? layer.getLatLng() : layer.getBounds().getCenter();
    L.popup({maxWidth:340}).setLatLng(latlng).setContent(html).openOn(map);
    setTimeout(initCarousel, 120);
  }

  function buildCarousel(media) {
    if (!media||!media.length) return '';
    return '<div class="carousel">'+
      media.map((m,i)=>'<div class="carousel-item'+(i===0?' active':'')+'"><div class="c-label">'+m.label+'</div><video muted loop playsinline preload="auto"><source src="'+m.src+'" type="video/mp4"></video></div>').join('')+
      '<button class="c-btn c-prev" onclick="MAP.carousel(-1)">&#8249;</button>'+
      '<button class="c-btn c-next" onclick="MAP.carousel(1)">&#8250;</button>'+
    '</div>';
  }

  function initCarousel() {
    _carCur=0; _carItems=Array.from(document.querySelectorAll('.carousel-item'));
    _carItems.forEach((it,i)=>{ it.classList.toggle('active',i===0); const v=it.querySelector('video'); if(v){i===0?v.play().catch(()=>{}):v.pause();} });
  }

  function carousel(dir) {
    if(!_carItems.length) return;
    const v0=_carItems[_carCur].querySelector('video'); if(v0) v0.pause();
    _carItems[_carCur].classList.remove('active');
    _carCur=(_carCur+dir+_carItems.length)%_carItems.length;
    _carItems[_carCur].classList.add('active');
    const v1=_carItems[_carCur].querySelector('video'); if(v1) v1.play().catch(()=>{});
  }

  async function fetchGeo(name) {
    if (_cache[name]) return _cache[name];
    try {
      const r = await fetch(DATA_DIR+name+'.geojson');
      if (!r.ok) throw new Error(r.status);
      _cache[name] = await r.json(); return _cache[name];
    } catch(e) { console.warn('No se cargo '+name+'.geojson:', e.message); return null; }
  }

  function makeIcon(shape, color, size) {
    return function() {
      size=size||10; const s2=size+4, a=Math.ceil(s2/2); let h='';
      if(shape==='dia')  h='<div style="width:'+size+'px;height:'+size+'px;transform:rotate(45deg);background:'+color+';border-radius:2px;border:1.5px solid rgba(255,255,255,.8)"></div>';
      else if(shape==='sq')   h='<div style="width:'+size+'px;height:'+size+'px;background:'+color+';border-radius:2px;border:1.5px solid rgba(255,255,255,.8)"></div>';
      else if(shape==='star') h='<span style="font-size:'+(size+3)+'px;color:'+color+';line-height:1;filter:drop-shadow(0 1px 2px rgba(0,0,0,.3))">&#9733;</span>';
      else h='<div style="width:'+size+'px;height:'+size+'px;border-radius:50%;background:'+color+';border:1.5px solid rgba(255,255,255,.8)"></div>';
      return L.divIcon({html:h, className:'', iconSize:[s2,s2], iconAnchor:[a,a], tooltipAnchor:[a+4,0]});
    };
  }

  function makeLabel(text, color) {
    return function() {
      return L.divIcon({html:'<div style="font-size:11px;font-weight:700;color:'+color+';background:#fff;border:1.5px solid '+color+';border-radius:4px;padding:2px 9px;white-space:nowrap;box-shadow:0 2px 6px rgba(0,0,0,.15)">'+text+'</div>', className:'', iconAnchor:[0,10]});
    };
  }

  function dboColor(v) { if(v==null)return'#bbb'; return v<30?'#27ae60':v<100?'#f1c40f':v<300?'#e67e22':'#e74c3c'; }
  function fmt(v) { if(v==null)return'-'; return typeof v==='number'?v.toLocaleString('es-MX',{maximumFractionDigits:1}):String(v); }
  function shadeColor(hex, pct) {
    const n=parseInt(hex.slice(1),16);
    const r=Math.min(255,Math.max(0,(n>>16)+pct)), g=Math.min(255,Math.max(0,((n>>8)&0xff)+pct)), b=Math.min(255,Math.max(0,(n&0xff)+pct));
    return '#'+[r,g,b].map(x=>x.toString(16).padStart(2,'0')).join('');
  }

  /* ── RESET VIEW ─────────────────────────── */
  function resetView() {
    if (_initBounds && _initBounds.isValid()) {
      map.flyTo(_initBounds.getCenter(), 9, { duration: 1 });
    } else {
      map.flyTo(CENTER, ZOOM, { duration: 1 });
    }
  }

  document.addEventListener('DOMContentLoaded', initMap);
  return { setLayer, buildMon, carousel, fitToLayers, resetView };

})();
