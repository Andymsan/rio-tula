# -*- coding: utf-8 -*-
"""
Genera index.html (borrador v2027 del sitio del río Tula).

    python tools/build_index.py

El contenido (textos, datos, cámaras, pines) vive en este archivo para no
repetir marcado a mano.  La historia (SVG grande) se toma de
tools/fragmentos/historia.html.  Al terminar también escribe img/fotos/LEEME.md
con la lista de fotos que espera el sitio.

Convenciones
  · coordenadas de pines/cámaras: 0-1 sobre el marco 16:9 del render (x, y)
  · "pend(...)"  = dato por confirmar (se ve amarillo)
  · fotos: img/fotos/<clave>.jpg  (si no existe, se muestra un marcador)
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()

FOTOS = []          # (clave, pie) para el LEEME

# ─── helpers de marcado ────────────────────────────────────────────────────
def pend(t):
    return '<span class="pend" title="Dato por confirmar">%s</span>' % t

def fl(t):
    return '<mark class="fluor">%s</mark>' % t

def frame(name):
    return '<img class="frame" data-frame="%s" src="img/mapa/%s.webp" alt="" loading="lazy" decoding="async">' % (name, name)

def ov(id_, tint=""):
    return '<img class="ov %s" data-ov="%s" src="img/mapa/ov-%s.webp" alt="" loading="lazy" decoding="async">' % (tint, id_, id_)

def pin(id_, x, y, label, sub="", side=""):
    return ('<div class="pin %s" data-id="%s" style="--px:%s;--py:%s"><i></i><span class="lbl">%s<small>%s</small></span></div>'
            % (side, id_, x, y, label, sub))

def mlabel(id_, x, y, text):
    return '<div class="maplabel" data-id="%s" style="--px:%s;--py:%s"><span>%s</span></div>' % (id_, x, y, text)

def slide(foto=None, cap="", src=None, contain=False):
    a = ""
    if foto:
        a += ' data-foto="%s"' % foto
        FOTOS.append((foto, cap))
    if src:
        a += ' data-src="%s"' % src
    if contain:
        a += ' data-contain'
    return '<figure class="bu-slide"%s data-cap="%s"></figure>' % (a, cap)

def carousel(slides, etiqueta="Fotos del proyecto"):
    return ('<div class="burbuja" data-carousel aria-label="%s"><span class="bu-hint">Desliza →</span>'
            '<div class="bu-track">%s</div><div class="bu-dots"></div>'
            '<button class="bu-btn bu-prev" type="button" aria-label="Anterior">‹</button>'
            '<button class="bu-btn bu-next" type="button" aria-label="Siguiente">›</button></div>'
            % (etiqueta, "".join(slides)))

def card(tag, title, body, kf=None, facts=None, fuente=None):
    h = '<div class="card"><div class="tag">%s</div><h3>%s</h3>' % (tag, title)
    for p in (body if isinstance(body, list) else [body]):
        h += "<p>%s</p>" % p
    if kf:
        h += '<div class="kf"><b>%s</b><span>%s</span></div>' % kf
    if facts:
        h += '<ul class="facts">%s</ul>' % "".join("<li>%s</li>" % f for f in facts)
    if fuente:
        h += '<div class="fuente">%s</div>' % fuente
    return h + "</div>"

def step(cam, frame_, card_html, bub="", **kw):
    at = ' data-frame="%s" data-cam="%s"' % (frame_, cam)
    for k, v in kw.items():
        at += ' data-%s="%s"' % (k, v)
    return '<article class="step"%s>%s%s</article>' % (at, card_html, bub)

def cap(id_, tema, banner, canvas_inner, steps, extra_stage="", lead=False):
    h = ""
    if lead:
        h += '<div class="cap-lead" data-nav="dark"></div>'
    h += ('<section class="cap tema-%s" id="%s" data-tema="%s" data-nav="light">'
          '<div class="cap-stage"><div class="canvas">%s</div>%s<div class="banner">%s</div></div>'
          '<div class="cap-steps">%s</div></section>' % (tema, id_, tema, canvas_inner, extra_stage, banner, "".join(steps)))
    return h

# ═══════════════════════════════════════════════════════════════════════════
#  COORDENADAS (marco 16:9 de los renders)
# ═══════════════════════════════════════════════════════════════════════════
# marco "int" / "acc" / "base"  (cámara inclinada sobre Tula)
INT = dict(bojay=(0.585, 0.165), trescult=(0.575, 0.352), rosas=(0.455, 0.527),
           sanlorenzo=(0.537, 0.693), chamizal=(0.391, 0.934))
# marco "col" (vista amplia con colectores y PTAR Atotonilco)
COL = dict(atot=(0.615, 0.815), cfe=(0.881, 0.455), colec=(0.53, 0.52), endho=(0.55, 0.12))

def sitio_pins(pop=False):
    pops = dict(bojay="3 mil hab.", trescult="4 mil hab.", rosas="24 mil hab.", sanlorenzo="20 mil hab.", chamizal="10 mil hab.")
    names = dict(bojay="Bojay", trescult="Tres Culturas", rosas="Río Rosas", sanlorenzo="San Lorenzo", chamizal="Chamizal")
    sides = dict(bojay="l", trescult="r", rosas="l", sanlorenzo="r", chamizal="r")
    return "".join(pin(k, INT[k][0], INT[k][1], names[k], pops[k], sides[k]) for k in INT)

# ═══════════════════════════════════════════════════════════════════════════
#  EL PROYECTO (los tres círculos)
# ═══════════════════════════════════════════════════════════════════════════
VENN = '''<div class="venn" data-focus="all"><svg viewBox="0 0 400 400" role="img" aria-label="Calidad del agua, inundaciones y ecosistemas se cruzan en el río Tula">
<g class="c c-rosa"><a href="#calidad"><circle cx="150" cy="150" r="120" fill="#f0938c" fill-opacity=".66"/></a>
<text class="num" x="92" y="124">15</text><text class="lab" x="92" y="148">Calidad</text><text class="lab" x="92" y="165">del agua</text></g>
<g class="c c-naranja"><a href="#inundaciones"><circle cx="250" cy="150" r="120" fill="#f78b62" fill-opacity=".66"/></a>
<text class="num" x="308" y="124">6</text><text class="lab" x="308" y="148">Inundaciones</text></g>
<g class="c c-verde"><a href="#ecosistemas"><circle cx="200" cy="236" r="120" fill="#a6a12a" fill-opacity=".66"/></a>
<text class="num" x="200" y="306">9</text><text class="lab" x="200" y="326">Ecosistemas y</text><text class="lab" x="200" y="343">espacio público</text></g>
<g class="centro"><rect x="152" y="160" width="96" height="36" rx="18" fill="#fff"/><text x="200" y="184" style="font-size:15px">Río Tula</text></g>
</svg></div>'''

hub_steps = [
    step(".5,.5,1", "int", card("El proyecto", "Un río, tres frentes",
        ["El Plan de Saneamiento y Restauración del Río Tula actúa a la vez sobre el agua, el cauce y el territorio. Esto es lo que está pasando, todo junto: " + fl("37 proyectos") + " sobre un mismo río."],
        kf=("$1,478 MDP", "de inversión documentada en 2025 y 2026"),
        facts=["Conagua", "Semarnat", "Conafor", "Conanp", "Profepa", "Gobierno de Hidalgo"]),
        wash="0", tema="rosa"),
    step(".5,.5,1", "int", card("Frente 1 · 15 proyectos", "Calidad del agua",
        ["Plantas de tratamiento, colectores, control de la industria y monitoreo: " + fl("que el agua que llega al río sea cada vez más limpia") + "."]),
        wash=".8", venn="rosa", tema="rosa"),
    step(".5,.5,1", "int", card("Frente 2 · 6 proyectos", "Inundaciones",
        ["Taludes firmes, cauce desazolvado, estaciones que miden el río cada 5 minutos y más espacio para que el agua se extienda: " + fl("reducir el riesgo para Tula") + "."]),
        wash=".8", venn="naranja", tema="naranja"),
    step(".5,.5,1", "int", card("Frente 3 · 9 proyectos", "Ecosistemas y espacio público",
        ["Riberas, humedales, bosques y cinco espacios públicos ribereños: " + fl("devolverle el río a la gente") + " y la vida al río."]),
        wash=".8", venn="verde", tema="verde"),
    step(".5,.5,1", "int", card("Donde se cruzan", "En el centro está el río",
        ["Cada frente sostiene a los otros: un río más limpio se puede recorrer, un cauce ordenado se puede restaurar y un río con vida vuelve a ser de la gente.",
         "Además, " + fl("7 proyectos de gobernanza, estudios y participación") + " los articulan."],
        kf=("Baja", "y empecemos por la calidad del agua ↓")),
        wash=".8", venn="all", tema="rosa"),
]
hub = cap("proyecto", "rosa", "El proyecto",
          frame("int"), hub_steps, extra_stage='<div class="wash"></div>' + VENN, lead=True)

# ═══════════════════════════════════════════════════════════════════════════
#  CALIDAD DEL AGUA  (rosa)  — marco "col"
# ═══════════════════════════════════════════════════════════════════════════
calidad_canvas = (frame("col")
    + pin("atot", *COL["atot"], label="PTAR Atotonilco", sub="", side="")
    + pin("colec", *COL["colec"], label="Colectores del río Tula", sub="", side="l")
    + pin("cfe", *COL["cfe"], label="PTAR de la CFE", sub="", side="l")
    + pin("boya", *COL["endho"], label="Boya · presa Endhó", sub="", side=""))

calidad_steps = [
    step(".55,.5,1.05", "col", card("Frente 1 · Calidad del agua", "Tres fuentes de contaminación, tres respuestas",
        ["Tres fuentes principales contaminan hoy el río Tula, y el proyecto atiende las tres: " + fl("el agua residual del Valle de México que no alcanza a tratarse") + ", las descargas industriales y el drenaje de la ciudad de Tula."],
        kf=("15", "proyectos de calidad del agua")), pins=""),
    step(".615,.79,2.3", "col", card("1 · Atotonilco", "Tratar más agua en Atotonilco",
        ["Históricamente la PTAR Atotonilco trataba <strong>31 m³/s</strong> en promedio y dejaba pasar al río " + pend("XX m³/s") + " sin tratamiento. En 2026 el caudal tratado subió a <strong>38 m³/s</strong>, y " + fl("a partir de 2027 tratará todo el drenaje del río en estiaje") + "."],
        kf=("+7 m³/s", "de caudal tratado adicional"),
        facts=["Terminado en 2026", "Conagua · $112 MDP"]),
        carousel([slide("atotonilco-1", "PTAR Atotonilco"), slide("atotonilco-2", "Operación de la planta"), slide("atotonilco-3", "Caudal tratado")]),
        pins="atot"),
    step(".55,.47,1.25", "col", card("2 · Industria", "Vigilar lo que se descarga",
        ["Durante este sexenio Conagua y Profepa inspeccionarán al menos dos veces a las " + pend("XX") + " empresas que descargan al río o a sus afluentes. Hasta hoy suman <strong>92 inspecciones</strong>, y " + fl("29 industrias") + " están en capacitación y certificación en el Centro Regional de Prevención Ambiental, en la UTTT."],
        kf=("92", "inspecciones · 29 industrias en certificación"),
        facts=["Profepa", "Conagua", "UTTT"]),
        carousel([slide("industria-1", "Inspección a una industria"), slide("industria-2", "Centro Regional de Prevención Ambiental")]),
        pins=""),
    step(".64,.47,1.35", "col", card("3 · Drenaje de Tula", "Que el drenaje de la ciudad deje de caer al río",
        ["Todo el drenaje de la zona metropolitana de Tula se vertía al río sin tratamiento. El Gobierno de Hidalgo construye <strong>35.8 km de colectores</strong> para captar <strong>72 descargas</strong> y " + fl("llevarlas a tratar a la planta de la CFE") + ", que se está rehabilitando (600 l/s)."],
        kf=("35.8 km", "de colectores · etapa 1 con 89 % de avance"),
        facts=["Gobierno de Hidalgo · $570 MDP", "PTAR CFE en rehabilitación", "PTAR Pemex en planeación"]),
        carousel([slide("colectores-1", "Colector del río Tula · etapa 1"), slide("colectores-2", "Línea de conducción a la PTAR de la CFE"), slide("colectores-3", "Cárcamo de bombeo")]),
        pins="colec cfe"),
    step(".55,.46,1.05", "col", card("4 · Monitoreo", "Medir para saber si funciona",
        ["<strong>5 estaciones automáticas</strong> vigilan la calidad del agua en tiempo real: tres en tierra (CFE, Pemex y Atotonilco) y dos boyas en las presas Endhó y Requena. Además se muestrea a mano en " + fl("hasta 100 sitios") + ", en secas y en lluvias.",
         "Todo llega al Centro de Vigilancia y Cultura del Agua, en la PTAR Atotonilco (en construcción)."],
        kf=("5", "estaciones automáticas de calidad"),
        facts=["Conagua · GCA", "Muestreo manual: 92–100 sitios"]),
        carousel([slide("monitoreo-1", "Estación automática de calidad"), slide("monitoreo-2", "Muestreo manual")]),
        pins="boya atot"),
]
calidad = cap("calidad", "rosa", "Calidad del agua", calidad_canvas, calidad_steps)

# ═══════════════════════════════════════════════════════════════════════════
#  INUNDACIONES  (naranja) — marcos "int" y "col"
# ═══════════════════════════════════════════════════════════════════════════
inund_canvas = (frame("int") + frame("col")
    + ov("sanlorenzo", "tint-naranja") + ov("chamizal", "tint-naranja") + ov("trescult", "tint-naranja") + ov("rosas", "tint-naranja")
    + '<img class="ov tint-naranja-x2" data-ov="tramo" src="img/mapa/ov-rio.webp" alt="" loading="lazy" decoding="async" style="clip-path: inset(30% 30% 24% 40%)">'
    + pin("sanlorenzo", *INT["sanlorenzo"], label="San Lorenzo", side="r")
    + pin("chamizal", *INT["chamizal"], label="El Chamizal", side="r")
    + pin("trescult", *INT["trescult"], label="Tres Culturas", side="r")
    + pin("rosas", *INT["rosas"], label="Río Rosas", side="l"))

inund_steps = [
    step(".5,.55,1.05", "int", card("Frente 2 · Inundaciones", "Un río que sabe desbordarse",
        ["En septiembre de 2021 el desbordamiento de los ríos Tula y Rosas inundó la ciudad. Hoy el plan actúa sobre " + fl("el cauce, los taludes y la información") + " para reducir el riesgo."],
        kf=("6", "proyectos de gestión de inundaciones"))),
    step(".46,.81,1.9", "int", card("1 · Taludes", "Taludes firmes en la ciudad",
        ["Las zonas erosionadas del río son un riesgo para quienes viven cerca. Estabilizamos <strong>4.47 km</strong> de taludes con tapete articulado, gaviones y revegetación nativa en " + fl("San Lorenzo, El Chamizal, San Marcos y Ahuehuetes") + ", y seguiremos hasta cubrir todos los taludes críticos de las zonas urbanas."],
        kf=("4.47 km", "1 km terminado · 1.67 km en obra · 1.8 km en planeación"),
        facts=["Conagua · Hidroagrícola", "San Lorenzo 2025 · terminado"]),
        carousel([slide("taludes-1", "San Lorenzo · antes"), slide("taludes-2", "San Lorenzo · después"), slide("taludes-3", "El Chamizal · obra en proceso")]),
        ov="sanlorenzo chamizal", pins="sanlorenzo chamizal"),
    step(".5,.44,1.6", "int", card("2 · Desazolve", "Más espacio para el agua",
        ["Cuando el cauce está azolvado, el agua tiene menos por dónde correr. En 2025 " + fl("desazolvamos 3.9 km") + " del río en la zona urbana de Tula, retirando " + pend("XX ton") + " de sedimento, basura y escombro, para que pueda conducir " + pend("XX m³/s") + " sin riesgo."],
        kf=("3.9 km", "de río desazolvado · terminado en 2025"),
        facts=["Conagua · $31 MDP"]),
        carousel([slide("desazolve-1", "Desazolve del cauce"), slide("desazolve-2", "Antes y después")]),
        ov="tramo", pins="trescult rosas"),
    step(".55,.5,1.0", "col", card("3 · Monitoreo de caudal", "Ver el río cada 5 minutos",
        ["Instalamos " + fl("21 estaciones") + " que miden cuánta agua fluye en cada tramo del río <strong>cada 5 minutos</strong>. Esa información permite operar el sistema de drenaje y las presas de forma más eficiente y segura."],
        kf=("21", "estaciones automáticas de caudal"),
        facts=["Conagua · GASIR", "Terminado en 2025"]),
        carousel([slide("caudal-1", "Estación de monitoreo de caudal")])),
    step(".575,.35,2.2", "int", card("4 · Tres Culturas", "Devolverle espacio al río",
        ["Estudiamos " + fl("restaurar la llanura de inundación de Tres Culturas") + ": un parque que se puede inundar de forma segura. El BID modeló cómo cambia el riesgo en Tula y se contratará un panel de cinco asesores holandeses con experiencia en soluciones basadas en la naturaleza."],
        kf=("BID + 5", "modelo hidráulico y asesores holandeses"),
        facts=["Referencias de parques inundables →"]),
        carousel([slide(src="img/ref/buffalo-bayou-houston.jpg", cap="Referencia · Buffalo Bayou, Houston (65 ha, 2015)"),
                  slide(src="img/ref/rodney-cook-park-atlanta-1.jpg", cap="Referencia · Rodney Cook Sr. Park, Atlanta (6.5 ha, 2021)"),
                  slide(src="img/ref/parque-inundable-georgia.jpg", cap="Referencia · parque inundable, Georgia")], "Referencias"),
        ov="trescult", pins="trescult"),
]
inund = cap("inundaciones", "naranja", "Gestión de inundaciones", inund_canvas, inund_steps)

# ═══════════════════════════════════════════════════════════════════════════
#  ECOSISTEMAS Y ESPACIO PÚBLICO (verde) — marcos "int", "base", "acc"
# ═══════════════════════════════════════════════════════════════════════════
eco_canvas = (frame("int") + frame("base") + frame("acc")
    + ov("rio") + ov("bojay", "tint-verde") + ov("trescult", "tint-verde") + ov("rosas", "tint-verde") + ov("sanlorenzo", "tint-verde") + ov("chamizal", "tint-verde")
    + ov("conect", "tint-slate")
    + sitio_pins()
    + mlabel("endho", 0.63, 0.115, "Presa Endhó")
    + mlabel("anp", 0.34, 0.22, "Nueva Área Natural<br>Protegida")
    + mlabel("parque", 0.62, 0.465, "Parque Nacional y<br>Atlantes de Tula"))

eco_steps = [
    step(".5,.55,1.05", "int", card("Frente 3 · Ecosistemas y espacio público", "Regresarle la vida al río",
        ["Para que un río vuelva a estar vivo hay que recuperar sus ecosistemas —cuerpos de agua, humedales, riberas y bosques de la cuenca alta— y " + fl("abrir el río a la gente") + "."],
        kf=("9", "proyectos de restauración y espacio público")), labels="endho parque"),
    step(".5,.5,1.7", "int", card("1 · Riberas", "Árboles sanos en las orillas",
        ["Saneamos <strong>1,600 árboles</strong> en <strong>10 km</strong> de riberas —les quitamos heno motita y ramas muertas— y " + fl("plantamos 300 árboles") + " en 3.5 km de la zona urbana de Tula. Con Conafor trabajamos para limpiar, sanear o reforestar " + pend("XX km") + " de riberas hasta la presa Endhó."],
        kf=("1,600", "árboles ribereños saneados"),
        facts=["Conagua · Semarnat", "Terminado en 2025"]),
        carousel([slide("riberas-1", "Saneamiento forestal de riberas"), slide("riberas-2", "Revegetación de riberas")])),
    step(".585,.17,2.3", "int", card("2 · Humedales y Endhó", "Agua limpia a 2 km de Tula",
        ["En las Ciénegas de Endhó (Bojay) recuperamos <strong>50 ha de humedal</strong>, y se rehabilita el bordo de la laguna para separarla del río Tula: " + fl("un cuerpo de agua limpia") + " de " + pend("55 ha") + " a 2 km de la ciudad. En la presa Endhó se extraen <strong>110 mil m³</strong> de lirio."],
        kf=("50 ha", "de humedal recuperado en Bojay"),
        facts=["Conagua · Semarnat", "Bordo y vertedor · en licitación"]),
        carousel([slide(src="img/mapa/z-bojay-zoom.webp", cap="Propuesta · humedal y sendero de Bojay", contain=True),
                  slide(src="img/mapa/z-bojay-verde.webp", cap="Propuesta · Bojay en planta", contain=True),
                  slide("bojay-1", "Ciénegas de Endhó (Bojay)")]),
        ov="bojay", pins="bojay", labels="endho"),
    step(".36,.24,1.6", "base", card("3 · Bosques", "De 100 a 1,700 hectáreas protegidas",
        ["Al inicio del sexenio existían solo " + pend("100 ha") + " de Áreas Naturales Protegidas en la cuenca. Hoy la Conanp certificó " + fl("1,700 ha") + " como Áreas Destinadas Voluntariamente a la Conservación (9 áreas) y Conafor restauró <strong>663 ha</strong> de suelo forestal en 17 proyectos."],
        kf=("1,700 ha", "certificadas como ADVC · 9 áreas"),
        facts=["Conanp", "Conafor · 15 ejidos", "Terminado en 2025"]),
        carousel([slide("bosques-1", "Área Destinada Voluntariamente a la Conservación"), slide("bosques-2", "Restauración forestal con ejidos")]),
        ov="rio", labels="anp parque"),
    step(".5,.55,1.05", "int", card("4 · Espacio público", "Cinco lugares para volver al río",
        ["En la ciudad de Tula construimos " + fl("5 espacios públicos ribereños") + " aprovechando las obras de estabilización de taludes y restauración ecológica: <strong>Chamizal, San Lorenzo, Río Rosas, Tres Culturas y Bojay</strong>.",
         "En cada uno se hace, al mismo tiempo, saneamiento, revegetación con plantas nativas, prevención de inundaciones y equipamiento."],
        kf=("5", "sitios de espacio público ribereño")),
        carousel([slide(src="img/mapa/z-rosas.webp", cap="Propuesta · Río Rosas", contain=True),
                  slide(src="img/mapa/z-sanlorenzo.webp", cap="Propuesta · San Lorenzo", contain=True),
                  slide(src="img/mapa/z-bojay-zoom.webp", cap="Propuesta · Bojay", contain=True),
                  slide("espacio-publico-1", "Espacio público ribereño")]),
        ov="bojay trescult rosas sanlorenzo chamizal", pins="bojay trescult rosas sanlorenzo chamizal"),
    step(".5,.55,1.05", "acc", card("5 · Alcance", "Un río al alcance de la gente",
        [fl("52 % de la población del municipio") + " vive a menos de 15 minutos a pie de alguna de las intervenciones."],
        kf=("52 %", "de la población a 15 min a pie"),
        fuente="Isócronas de accesibilidad: OpenRouteService."),
        pins="bojay trescult rosas sanlorenzo chamizal", pop="1"),
    step(".5,.55,1.05", "int", card("6 · Conexión", "Todo conectado por una vía ciclable de 12 km",
        ["Sobre las antiguas vías del tren, los bordos rehabilitados y los caminos rurales, " + fl("una vía ciclable de 12 km") + " conecta todas las intervenciones: <strong>4 km</strong> de antiguas vías, <strong>6 km</strong> de bordos y <strong>2 km</strong> de caminos rurales."],
        kf=("12 km", "de vía ciclable")),
        ov="conect", labels="parque"),
]
eco = cap("ecosistemas", "verde", "Ecosistemas y espacio público", eco_canvas, eco_steps)

# ═══════════════════════════════════════════════════════════════════════════
#  PÁGINA
# ═══════════════════════════════════════════════════════════════════════════
INDICE = [
    ("01", "Historia", "Cómo llegó el río a esta condición", "#historia", "#f2c14e"),
    ("02", "Compromiso 92", "La promesa de limpiar los tres ríos más contaminados", "#promesa", "#f0938c"),
    ("03", "El proyecto", "Tres frentes, un mismo río", "#proyecto", "#f2c14e"),
    ("04", "Calidad del agua", "Atotonilco, industria, colectores y monitoreo", "#calidad", "#f0938c"),
    ("05", "Inundaciones", "Taludes, desazolve y más espacio para el agua", "#inundaciones", "#f78b62"),
    ("06", "Ecosistemas y espacio público", "Riberas, humedales, bosques y cinco sitios", "#ecosistemas", "#b3ae35"),
    ("07", "Cierre y mapa", "Los números y el visor interactivo", "#cierre", "#65748b"),
]
idx_items = "".join('<a class="idx-item" href="%s" style="--c:%s"><b>%s</b><span>%s</span></a>' % (h, c, n, t) for n, t, d, h, c in INDICE)
idx_list  = "".join('<li><a href="%s" style="--c:%s"><b>%s</b><span>%s<small>%s</small></span></a></li>' % (h, c, n, t, d) for n, t, d, h, c in INDICE)

FILTROS = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<filter id="f-rosa"    color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.941  0 0 0 0 0.576  0 0 0 0 0.549  0 0 0 1 0"/></filter>
<filter id="f-naranja" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.969  0 0 0 0 0.545  0 0 0 0 0.384  0 0 0 1 0"/></filter>
<filter id="f-naranja-x2" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.969  0 0 0 0 0.545  0 0 0 0 0.384  0 0 0 2.6 0"/></filter>
<filter id="f-verde"   color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.549  0 0 0 0 0.529  0 0 0 0 0.114  0 0 0 1 0"/></filter>
<filter id="f-slate"   color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.396  0 0 0 0 0.455  0 0 0 0 0.545  0 0 0 1 0"/></filter>
</defs></svg>'''

HERO = '''<header class="hero" id="top" data-nav="dark">
  <div class="hero-bg"></div><div class="hero-glow"></div>
  <p class="hs-eyebrow">Saneamiento · Restauración · 2024–2030</p>
  <h1 class="hs-main-title">Río <em>Tula</em></h1>
  <p class="hs-subtitle">Cómo llegó a estar así y cómo lo estamos recuperando: agua limpia, un cauce seguro y un río abierto a su gente.</p>
  <div class="hero-cta"><a class="btn btn-light" href="#historia">Comenzar el recorrido ↓</a><a class="btn btn-ghost" href="mapa.html">Ver mapa</a></div>
  <div class="idx-grid" aria-label="Índice">%s</div>
</header>''' % idx_items

PROMESA = '''<section class="s-promesa" id="promesa" data-nav="dark">
  <div class="pm-beat"><div class="pm-wrap pm-1">
    <div class="pm-92 rv">92</div>
    <div class="rv">
      <p class="pm-kicker">Compromiso presidencial</p>
      <h2 class="pm-h">Limpiar y sanear <em>los tres ríos más contaminados</em> del país</h2>
      <p class="pm-sub">Es el compromiso 92 de la Presidenta Claudia Sheinbaum Pardo: recuperar el Lerma-Santiago, el Tula y el Atoyac, tres ríos que atraviesan cuencas con millones de habitantes y cientos de industrias.</p>
    </div>
  </div></div>

  <div class="pm-beat"><div class="pm-wrap pm-2">
    <p class="pm-kicker rv">Los tres ríos</p>
    <h2 class="rv">Tres cuencas, una misma tarea</h2>
    <div class="rios rv">
      <article class="rio-card"><h3>Lerma-Santiago</h3><p class="edos">México, Querétaro, Guanajuato, Michoacán, Jalisco y Nayarit</p>
        <div class="m"><b>1,360</b><span>km de río</span><div class="bar"><i style="--w:100%"></i></div></div>
        <div class="m"><b>21.4</b><span>millones de habitantes</span><div class="bar"><i style="--w:100%"></i></div></div></article>
      <article class="rio-card hl"><h3>Tula</h3><p class="edos">Estado de México e Hidalgo</p>
        <div class="m"><b>191</b><span>km de río</span><div class="bar"><i style="--w:14%"></i></div></div>
        <div class="m"><b>0.8</b><span>millones de habitantes</span><div class="bar"><i style="--w:3.7%"></i></div></div></article>
      <article class="rio-card"><h3>Atoyac</h3><p class="edos">Tlaxcala y Puebla</p>
        <div class="m"><b>162</b><span>km de río</span><div class="bar"><i style="--w:11.9%"></i></div></div>
        <div class="m"><b>3.7</b><span>millones de habitantes</span><div class="bar"><i style="--w:17.3%"></i></div></div></article>
    </div>
    <p class="rio-nota rv">El Tula es el más corto de los tres, pero además recibe el drenaje del Valle de México.</p>
  </div></div>

  <div class="pm-beat"><div class="pm-wrap pm-3">
    <p class="pm-kicker rv">La escala del reto</p>
    <h2 class="rv">Una inversión histórica para tres ríos</h2>
    <div class="nums rv">
      <div class="n big"><b>+20 mil</b><span>millones de pesos de inversión durante el sexenio para los tres ríos</span></div>
      <div class="n"><b>3,202</b><span>puntos de descarga identificados en las tres cuencas</span></div>
      <div class="n"><b>479</b><span>tiraderos clandestinos</span></div>
      <div class="n"><b>460</b><span>industrias potencialmente contaminantes</span></div>
      <div class="n"><b>23</b><span>plantas de tratamiento construidas o rehabilitadas, con 282 km de colectores (sept. de 2026)</span></div>
    </div>
    <p class="pm-puente rv">Y en el Tula, el plan tiene nombre y ubicación.<span>↓</span></p>
    <p class="pm-fuentes rv">Fuentes: <a href="https://contralinea.com.mx/interno/semana/gobierno-invertira-mas-de-20-mil-mdp-para-sanear-los-rios-lerma-santiago-tula-y-atoyac/" target="_blank" rel="noopener">Contralínea (16 jul 2026)</a> ·
      <a href="https://www.gob.mx/profepa/prensa/avanza-saneamiento-y-recuperacion-de-los-rios-atoyac-lerma-santiago-y-tula-434666" target="_blank" rel="noopener">Profepa, gob.mx (1 sep 2026)</a> ·
      <a href="https://www.ambito.com/mexico/informacion-general/claudia-sheinbaum-ordena-limpiar-los-tres-rios-mas-contaminados-mexico-cuales-son-y-como-se-hara-este-historico-saneamiento-n6300195" target="_blank" rel="noopener">Ámbito</a>.</p>
  </div></div>
</section>'''

CIERRE = '''<section class="s-cierre" id="cierre" data-nav="dark">
  <h2 class="rv">Un río, tres frentes, 37 proyectos</h2>
  <p class="rv">Agua más limpia, un cauce más seguro y un río abierto a su gente. Explora cada intervención sobre el mapa: capas, avance y ubicación de todos los proyectos.</p>
  <div class="stats rv">
    <div><b>37</b><span>proyectos en el plan</span></div>
    <div><b>$1,478<sup>MDP</sup></b><span>de inversión documentada</span></div>
    <div><b>2,415<sup>ha</sup></b><span>restauradas y conservadas</span></div>
    <div><b>35.8<sup>km</sup></b><span>de colectores</span></div>
  </div>
  <a class="btn btn-light" href="mapa.html">Abrir el mapa interactivo →</a>
</section>
<footer>
  Secretaría de Medio Ambiente y Recursos Naturales · Plan de Saneamiento y Restauración del Río Tula 2024–2030<br>
  Datos: base de proyectos 2025–2026 (Conagua, Semarnat, Conafor, Conanp, Profepa y Gobierno de Hidalgo) · <a href="mapa.html">Ir al mapa interactivo</a>
</footer>'''

page = '''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Río Tula — Plan de Saneamiento y Restauración 2024–2030</title>
  <meta name="description" content="La historia del río Tula y el plan para sanearlo y restaurarlo: calidad del agua, inundaciones, ecosistemas y espacio público." />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Noto+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="css/temas.css" />
  <link rel="stylesheet" href="css/historia.css" />
  <link rel="stylesheet" href="css/capitulos.css" />
  <script>document.documentElement.classList.add('js')</script>
</head>
<body>
%(filtros)s
<div id="progress"></div>

<nav id="main-nav">
  <a class="nav-logo" href="#top">Río Tula <span>/ Plan 2024–2030</span></a>
  <div class="nav-right">
    <button class="nav-btn" id="idxBtn" type="button">☰ Índice</button>
    <a class="nav-cta" href="mapa.html">Ver mapa →</a>
  </div>
</nav>

<div class="idx-panel" id="idxPanel" role="dialog" aria-label="Índice">
  <button class="idx-close" id="idxClose" type="button" aria-label="Cerrar">×</button>
  <div class="idx-box"><h2>Índice</h2><ul class="idx-list">%(idx_list)s</ul></div>
</div>

<div class="borrador">Borrador · <span class="pend" style="cursor:default">amarillo</span> = dato por confirmar · las fotos son marcadores
  <button id="borradorClose" type="button" aria-label="Cerrar aviso">×</button></div>

%(hero)s

%(historia)s

%(promesa)s

%(hub)s

%(calidad)s

%(inund)s

%(eco)s

%(cierre)s

<script src="js/sitio.js"></script>
</body>
</html>
''' % dict(filtros=FILTROS, idx_list=idx_list, hero=HERO, historia=rd("tools/fragmentos/historia.html"),
           promesa=PROMESA, hub=hub, calidad=calidad, inund=inund, eco=eco, cierre=CIERRE)

open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page)

# ─── LEEME de fotos ────────────────────────────────────────────────────────
rows = "\n".join("| `%s.jpg` | %s |" % (k, c) for k, c in FOTOS)
leeme = """# Fotos del sitio

Para sustituir un marcador por una foto: **guarda la imagen aquí con el nombre exacto de la
tabla** (JPG, PNG o WebP; horizontal, ~1600 px de ancho). No hay que tocar código.

| Archivo | Pie de foto / qué va |
|---|---|
%s

- Si el archivo no existe, el sitio muestra un marcador con rayas y el nombre del archivo.
- Para agregar más fotos a un carrusel, pídeselo a Claude (hay que sumar una entrada).
- Archivo generado por `tools/build_index.py`.
""" % rows
os.makedirs(os.path.join(ROOT, "img", "fotos"), exist_ok=True)
open(os.path.join(ROOT, "img", "fotos", "LEEME.md"), "w", encoding="utf-8").write(leeme)
print("index.html escrito:", len(page) // 1024, "KB ·", len(FOTOS), "fotos esperadas")
