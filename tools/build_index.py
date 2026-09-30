# -*- coding: utf-8 -*-
"""
Genera index.html a partir de TEXTOS.md (contenido) y este archivo (estructura:
imagen, cámara, capas y pines de cada paso).

    python tools/build_index.py

Fotos: se colocan en img/fotos/<id-de-sección>/<orden>_<pie de foto>.jpg
(ver img/fotos/LEEME.md, generado automáticamente). Si no hay fotos para una
sección, se muestra un marcador con la ruta esperada.

Si TEXTOS.md tiene un error, el script se detiene con un mensaje y NO toca
index.html.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textos import Textos, TextosError, fmt, attr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS_DIR = os.path.join(ROOT, "img", "fotos")

def rd(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()

def _mensaje_amable(tipo, valor, tb):
    if issubclass(tipo, TextosError):
        sys.stderr.write("\nERROR EN LOS TEXTOS: %s\n(index.html no se modificó.)\n\n" % valor)
    else:
        sys.__excepthook__(tipo, valor, tb)
sys.excepthook = _mensaje_amable

try:
    T = Textos(os.path.join(ROOT, "TEXTOS.md"))
except FileNotFoundError:
    sys.exit("ERROR: no se encuentra TEXTOS.md")

SECCIONES_FOTOS = []   # (id, carpeta esperada) para el LEEME

# ─── helpers de marcado ────────────────────────────────────────────────────
def frame(name):
    return '<img class="frame" data-frame="%s" src="img/mapa/%s.webp" alt="" loading="lazy" decoding="async">' % (name, name)

def ov(id_, tint=""):
    return '<img class="ov %s" data-ov="%s" src="img/mapa/ov-%s.webp" alt="" loading="lazy" decoding="async">' % (tint, id_, id_)

def pin(id_, x, y, label, sub="", side=""):
    return ('<div class="pin %s" data-id="%s" style="--px:%s;--py:%s"><i></i><span class="lbl">%s<small>%s</small></span></div>'
            % (side, id_, x, y, label, sub))

def mlabel(id_, x, y, text):
    return '<div class="maplabel" data-id="%s" style="--px:%s;--py:%s"><span>%s</span></div>' % (id_, x, y, text)

# ─── fotos: una carpeta por sección, nombre = "<orden>_<pie de foto>.ext" ──
def fotos_de(id_):
    d = os.path.join(FOTOS_DIR, id_)
    SECCIONES_FOTOS.append(id_)
    if not os.path.isdir(d):
        return []
    out = []
    for fn in os.listdir(d):
        m = re.match(r'^(\d+)_(.+)\.(jpe?g|png|webp)$', fn, re.I)
        if m:
            out.append((int(m.group(1)), "img/fotos/%s/%s" % (id_, fn), m.group(2)))
    out.sort(key=lambda r: r[0])
    return [(src, cap) for _, src, cap in out]

def slide(src, cap, contain=False):
    a = ' data-src="%s" data-cap="%s"' % (src, attr(cap))
    if contain:
        a += " data-contain"
    return "<figure class=\"bu-slide\"%s></figure>" % a

def carousel(id_=None, extra=None, etiqueta="Fotos del proyecto"):
    """Arma un carrusel. `id_` toma las fotos de img/fotos/<id_>/ (si hay).
    `extra` agrega imágenes fijas del propio sitio: [(src, pie, contain?), ...]."""
    slides = [slide(src, cap) for src, cap in (fotos_de(id_) if id_ else [])]
    for e in (extra or []):
        src, cap = e[0], e[1]
        contain = e[2] if len(e) > 2 else False
        slides.append(slide(src, cap, contain))
    if not slides:
        slides = ['<figure class="bu-slide bu-pend" data-pend="img/fotos/%s/1_&lt;pie de foto&gt;.jpg"></figure>' % id_]
    return ('<div class="burbuja" data-carousel aria-label="%s"><span class="bu-hint">Desliza →</span>'
            '<div class="bu-track">%s</div><div class="bu-dots"></div>'
            '<button class="bu-btn bu-prev" type="button" aria-label="Anterior">‹</button>'
            '<button class="bu-btn bu-next" type="button" aria-label="Siguiente">›</button>'
            '<button class="bu-zoom" type="button" aria-label="Ver en grande">🔍</button></div>'
            % (etiqueta, "".join(slides)))

def card(id_):
    h = '<div class="card"><div class="tag">%s</div><h3>%s</h3>' % (T.t(id_, "etiqueta"), T.t(id_, "titulo"))
    for campo in ("texto", "texto2", "texto3"):
        v = T.t(id_, campo, requerido=(campo == "texto"))
        if v:
            h += "<p>%s</p>" % v
    cifra = T.raw(id_, "cifra", requerido=False)
    if cifra:
        partes = [x.strip() for x in cifra.split("|", 1)]
        if len(partes) != 2:
            raise TextosError('En "## %s", el campo "cifra:" debe ser "número | explicación".' % id_)
        h += '<div class="kf"><b>%s</b><span>%s</span></div>' % (fmt(partes[0]), fmt(partes[1]))
    chips = T.lista(id_, "chips", requerido=False)
    if chips:
        h += '<ul class="facts">%s</ul>' % "".join("<li>%s</li>" % fmt(c) for c in chips)
    fuente = T.t(id_, "fuente", requerido=False)
    if fuente:
        h += '<div class="fuente">%s</div>' % fuente
    return h + "</div>"

def step(cam, frame_, card_html, bub="", **kw):
    at = ' data-frame="%s" data-cam="%s"' % (frame_, cam)
    for k, v in kw.items():
        at += ' data-%s="%s"' % (k, v)
    return '<article class="step"%s>%s%s</article>' % (at, card_html, bub)

def cap(id_, tema, banner, canvas_inner, steps, extra_stage=""):
    return ('<section class="cap tema-%s" id="%s" data-tema="%s" data-nav="light">'
            '<div class="cap-stage"><div class="canvas">%s</div>%s<div class="banner">%s</div></div>'
            '<div class="cap-steps">%s</div></section>' % (tema, id_, tema, canvas_inner, extra_stage, banner, "".join(steps)))

# ═══════════════════════════════════════════════════════════════════════════
#  COORDENADAS (marco 16:9 de los renders; comparten cámara: int / base / acc)
# ═══════════════════════════════════════════════════════════════════════════
INT = dict(bojay=(0.585, 0.165), trescult=(0.575, 0.352), rosas=(0.455, 0.527),
           sanlorenzo=(0.537, 0.693), chamizal=(0.391, 0.934))
# marco "col" (vista amplia con colectores y PTAR Atotonilco) — cámara distinta
COL = dict(atot=(0.615, 0.815), cfe=(0.881, 0.455), colec=(0.53, 0.52), endho=(0.55, 0.12))

def sitio_pins():
    pops = dict(bojay="3 mil hab.", trescult="4 mil hab.", rosas="24 mil hab.", sanlorenzo="20 mil hab.", chamizal="10 mil hab.")
    names = dict(bojay="Bojay", trescult="Tres Culturas", rosas="Río Rosas", sanlorenzo="San Lorenzo", chamizal="Chamizal")
    sides = dict(bojay="l", trescult="r", rosas="l", sanlorenzo="r", chamizal="r")
    return "".join(pin(k, INT[k][0], INT[k][1], names[k], pops[k], sides[k]) for k in INT)

# ═══════════════════════════════════════════════════════════════════════════
#  EL PROYECTO (tres hexágonos que se tocan en una esquina: el río)
# ═══════════════════════════════════════════════════════════════════════════
def hexes_svg():
    R = 112.0
    W = R * 0.8660254
    V = (260.0, 250.0)
    cen = dict(rosa=(V[0], V[1] - R), naranja=(V[0] + W, V[1] + R / 2), verde=(V[0] - W, V[1] + R / 2))

    def poly(c):
        x, y = c
        pts = [(x, y - R), (x + W, y - R / 2), (x + W, y + R / 2), (x, y + R), (x - W, y + R / 2), (x - W, y - R / 2)]
        return " ".join("%.1f,%.1f" % p for p in pts)

    ico = dict(
        rosa='<path class="ico" d="M0 -30 C10 -15 16 -8 16 0 A16 16 0 0 1 -16 0 C-16 -8 -10 -15 0 -30 Z"/>',
        naranja='<path class="ico" d="M-20 -6 q5 -7 10 0 t10 0 t10 0 t10 0 M-20 6 q5 -7 10 0 t10 0 t10 0 t10 0"/>',
        verde='<path class="ico" d="M-16 12 C-18 -12 2 -26 18 -22 C22 -4 10 14 -16 12 Z M-16 12 L4 -8"/>',
    )
    def tile(k):
        partes = T.lista("hexagonos", k)
        x, y = cen[k]
        t = '<g class="h h-%s"><polygon points="%s"/>' % (k, poly(cen[k]))
        t += '<g transform="translate(%.1f,%.1f)">%s</g>' % (x, y - 44, ico[k])
        for j, linea in enumerate(partes[:2]):
            t += '<text class="lab" x="%.1f" y="%.1f">%s</text>' % (x, y + 14 + 17 * j, fmt(linea))
        return t + "</g>"

    centro = T.lista("hexagonos", "centro", esperado=2)
    svg = '<svg viewBox="0 12 520 428" role="img" aria-label="Calidad del agua, inundaciones y ecosistemas se tocan en un mismo punto: el río Tula">'
    svg += tile("rosa") + tile("naranja") + tile("verde")
    svg += ('<g class="nodo"><circle class="anillo" cx="%.1f" cy="%.1f" r="34"/><circle class="disco" cx="%.1f" cy="%.1f" r="34"/>'
            '<text x="%.1f" y="%.1f">%s</text><text x="%.1f" y="%.1f">%s</text></g>'
            % (V[0], V[1], V[0], V[1], V[0], V[1] - 2, fmt(centro[0]), V[0], V[1] + 15, fmt(centro[1])))
    return svg + "</svg>"

HEXES = '<div class="hexes" data-focus="all">%s</div>' % hexes_svg()

hub_steps = [
    step(".5,.5,1", "int", card("proyecto-0"), wash=".93", hex="all", tema="rosa"),
]
hub = cap("proyecto", "rosa", T.t("proyecto", "banner"), frame("int"), hub_steps, extra_stage='<div class="wash"></div>' + HEXES)

# ═══════════════════════════════════════════════════════════════════════════
#  CALIDAD DEL AGUA  (rosa) — marco "col"
# ═══════════════════════════════════════════════════════════════════════════
calidad_canvas = (frame("col")
    + pin("atot", *COL["atot"], label="Centro de Vigilancia del Agua", sub="", side="")
    + pin("colec", *COL["colec"], label="Colectores del río Tula", sub="", side="r")
    + pin("cfe", *COL["cfe"], label="PTAR de la CFE", sub="", side="l")
    + pin("boya", *COL["endho"], label="Boya · presa Endhó", sub="", side=""))

calidad_steps = [
    step(".55,.5,1.05", "col", card("calidad-0"), pins=""),
    step(".615,.79,2.3", "col", card("calidad-1"), carousel("calidad-1"), pins="atot"),
    step(".64,.47,1.35", "col", card("calidad-3"), carousel("calidad-3"), pins="colec cfe"),
    step(".55,.47,1.25", "col", card("calidad-2"), carousel("calidad-2"), pins=""),
    step(".55,.46,1.05", "col", card("calidad-4"), carousel("calidad-4"), pins="boya atot"),
]
calidad = cap("calidad", "rosa", T.t("calidad", "banner"), calidad_canvas, calidad_steps)

# ═══════════════════════════════════════════════════════════════════════════
#  INUNDACIONES  (naranja) — marcos "int" y "col"
# ═══════════════════════════════════════════════════════════════════════════
inund_canvas = (frame("int") + frame("col")
    + ov("sanlorenzo", "tint-naranja") + ov("chamizal", "tint-naranja") + ov("trescult", "tint-naranja") + ov("rosas", "tint-naranja")
    + '<img class="ov tint-naranja-x2" data-ov="tramo" src="img/mapa/ov-rio.webp" alt="" loading="lazy" decoding="async" style="clip-path: inset(30% 30% 24% 40%)">'
    + ov("rio")
    + pin("sanlorenzo", *INT["sanlorenzo"], label="San Lorenzo", side="r")
    + pin("chamizal", *INT["chamizal"], label="El Chamizal", side="r")
    + pin("trescult", *INT["trescult"], label="Tres Culturas", side="r")
    + pin("rosas", *INT["rosas"], label="Río Rosas", side="l"))

inund_steps = [
    step(".5,.55,1.05", "int", card("inundaciones-0")),
    step(".46,.81,1.9", "int", card("inundaciones-1"), carousel("inundaciones-1"), ov="sanlorenzo chamizal", pins="sanlorenzo chamizal"),
    step(".5,.44,1.6", "int", card("inundaciones-2"), carousel("inundaciones-2"), ov="tramo", pins="trescult rosas"),
    step(".55,.5,1.0", "col", card("inundaciones-3"), carousel("inundaciones-3")),
    # la capa del río va después de la de la llanura, para que quede encima
    step(".575,.35,2.2", "int", card("inundaciones-4"),
         carousel("inundaciones-4", [
             ("img/ref/buffalo-bayou-houston.jpg", "Referencia · Buffalo Bayou, Houston (65 ha, 2015)"),
             ("img/ref/rodney-cook-park-atlanta-1.jpg", "Referencia · Rodney Cook Sr. Park, Atlanta (6.5 ha, 2021)"),
             ("img/ref/parque-inundable-georgia.jpg", "Referencia · parque inundable, Georgia"),
         ], "Referencias"),
         ov="trescult rio", pins="trescult"),
]
inund = cap("inundaciones", "naranja", T.t("inundaciones", "banner"), inund_canvas, inund_steps)

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
    step(".5,.55,1.05", "int", card("ecosistemas-0"), labels="endho parque"),
    step(".5,.5,1.7", "int", card("ecosistemas-1"), carousel("ecosistemas-1")),
    step(".585,.17,2.3", "int", card("ecosistemas-2"),
         carousel("ecosistemas-2"), ov="bojay", pins="bojay", labels="endho"),
    step(".36,.24,1.6", "base", card("ecosistemas-3"), carousel("ecosistemas-3"), ov="rio", labels="anp parque"),
    # Cámara desplazada hacia arriba para que Bojay (cerca del borde superior
    # de la imagen) no se corte; incluye las isócronas (marco "acc").
    step(".5,.4,1.0", "acc", card("ecosistemas-4"),
         carousel("ecosistemas-4"),
         ov="bojay trescult rosas sanlorenzo chamizal", pins="bojay trescult rosas sanlorenzo chamizal"),
]
eco = cap("ecosistemas", "verde", T.t("ecosistemas", "banner"), eco_canvas, eco_steps)

# ═══════════════════════════════════════════════════════════════════════════
#  RESUMEN (mapa con las 5 metas; se resalta la que está en foco)
# ═══════════════════════════════════════════════════════════════════════════
# (cámara, marco, capas [+ "tint-x" para recolorear], pines, etiquetas, título, detalle, descripción)
METAS = [
    (".55,.5,1.05", "col", "", "atot colec cfe", "", "Tratar todo el drenaje del río Tula",
     "Optimización de Atotonilco + colectores del río Tula",
     "La optimización de la PTAR Atotonilco va a permitir que todo el drenaje del Valle de México sea "
     "tratado durante secas. El proyecto de colectores va a captar la mayor parte de las descargas de "
     "drenaje al río Tula."),
    (".55,.47,1.25", "col", "", "", "", "Controlar la contaminación industrial",
     "Industrias inspeccionadas + estaciones de monitoreo automático",
     "La Profepa y Conagua trabajan para inspeccionar y regularizar a todas las industrias que descargan "
     "al río Tula. Adicionalmente, estamos construyendo 5 estaciones de monitoreo automático de la "
     "calidad del agua para identificar descargas industriales oportunamente."),
    (".5,.55,1.05", "int", "sanlorenzo chamizal trescult rosas tint-naranja", "sanlorenzo chamizal trescult rosas", "",
     "Prevenir inundaciones en la ciudad de Tula",
     "Desazolve + estabilización de taludes + estaciones automáticas + llanura de inundación en Tres Culturas",
     "La Conagua implementa obras para asegurar que el río Tula no se desborde: desazolve, estabilización "
     "de taludes, monitoreo automático y la recuperación de una llanura aluvial."),
    (".36,.24,1.3", "base", "rio", "", "anp parque", "Restaurar los ecosistemas que le dan vida al río",
     "Saneamiento forestal + revegetación + ADVC + proyectos de restauración",
     "El sector ambiental federal trabaja para proteger y restaurar las riberas del río Tula, cuerpos de "
     "agua como la laguna de Bojay de 55 ha y más de 3,800 ha de suelo forestal."),
    (".5,.55,1.05", "int", "bojay trescult rosas sanlorenzo chamizal tint-verde", "bojay trescult rosas sanlorenzo chamizal", "",
     "Construir espacio público ribereño para toda la población de Tula", "Los 5 proyectos de espacio público",
     "Para que la población de Tula pueda reconectar con el río, estamos construyendo 5 proyectos de "
     "espacio público ribereño que incluyen revegetación nativa, equipamiento público y agua limpia."),
]

def resumen_canvas():
    ovs, tint_por_ov = set(), {}
    for _, _, ovlist, _, _, _, _, _ in METAS:
        parts = ovlist.split()
        tint = next((p for p in parts if p.startswith("tint-")), "")
        for name in parts:
            if not name.startswith("tint-"):
                ovs.add(name)
                tint_por_ov.setdefault(name, tint)
    html = frame("int") + frame("col") + frame("base") + frame("acc")
    for name in sorted(ovs):
        html += ov(name, tint_por_ov.get(name, ""))
    html += sitio_pins()
    html += pin("atot", *COL["atot"], label="Centro de Vigilancia del Agua", side="")
    html += pin("colec", *COL["colec"], label="Colectores del río Tula", side="r")
    html += pin("cfe", *COL["cfe"], label="PTAR de la CFE", side="l")
    html += mlabel("anp", 0.34, 0.22, "Nueva Área Natural<br>Protegida")
    html += mlabel("parque", 0.62, 0.465, "Parque Nacional y<br>Atlantes de Tula")
    return html

def resumen_meta(i, cam, frame_, ovlist, pins, labels, titulo, detalle, desc):
    ov_sin_tint = " ".join(x for x in ovlist.split() if not x.startswith("tint-"))
    return ('<li class="meta" tabindex="0" role="button" aria-expanded="false" '
            'data-cam="%s" data-frame="%s" data-ov="%s" data-pins="%s" data-labels="%s">'
            '<b>%d</b><div><strong>%s</strong><span>%s</span><p class="meta-desc">%s</p></div></li>'
            % (cam, frame_, ov_sin_tint, pins, labels, i + 1, fmt(titulo), fmt(detalle), fmt(desc)))

def resumen():
    metas_html = "".join(resumen_meta(i, *m) for i, m in enumerate(METAS))
    return ('<section class="s-resumen tema-azul" id="resumen" data-nav="light">'
            '<div class="section-inner"><span class="s-tag">%s</span><h2 class="s-title">%s</h2>'
            '<p class="s-subtitle">%s</p><p class="s-body">%s</p></div>'
            '<div class="resumen-wrap"><div class="resumen-stage" id="resumenStage"><div class="canvas">%s</div><div class="wash"></div></div>'
            '<ul class="resumen-metas" id="resumenMetas">%s</ul></div></section>'
            % (T.t("resumen", "etiqueta"), T.t("resumen", "titulo"), T.t("resumen", "subtitulo"), T.t("resumen", "texto"),
               resumen_canvas(), metas_html))

# ═══════════════════════════════════════════════════════════════════════════
#  PARTICIPA
# ═══════════════════════════════════════════════════════════════════════════
def participa():
    enlaces = T.lista("participa", "enlaces")
    li = ""
    for e in enlaces:
        texto, url = [x.strip() for x in e.split("->", 1)]
        li += '<a class="link-btn" href="%s" target="_blank" rel="noopener">%s</a>' % (attr(url), fmt(texto))
    return ('<section class="s-participa" id="participa" data-nav="light">'
            '<div class="participa-wrap">%s<div class="participa-texto">'
            '<span class="s-tag">%s</span><h2 class="s-title">%s</h2><p class="s-body">%s</p>'
            '<div class="participa-links">%s</div></div></div></section>'
            % (carousel("participa"), T.t("participa", "etiqueta"), T.t("participa", "titulo"), T.t("participa", "texto"), li))

# ═══════════════════════════════════════════════════════════════════════════
#  HISTORIA (mapa SVG + textos por época)
# ═══════════════════════════════════════════════════════════════════════════
def historia_section():
    ticks = [("0", "700 mil a.C."), ("14", "1449"), ("28", "1789"), ("42", "1900"), ("56", "1950"), ("75", "2000"), ("100", "hoy")]
    ticks_html = "".join('<span class="hs-tick" style="left:%s%%">%s</span>' % t for t in ticks)
    steps = ""
    for i in range(9):
        k = "historia-%d" % i
        fuente = T.t(k, "fuente", requerido=False)
        fuente_html = ('<div class="fuente">%s</div>' % fuente) if fuente else ""
        steps += ('<article class="step hs-step" data-step="%d" data-banner="%s" data-here="%s"><div class="card">'
                  '<div class="tag">%s</div><h3>%s</h3><p>%s</p>%s</div></article>'
                  % (i, attr(T.raw(k, "banner")), attr(T.raw(k, "linea")), T.t(k, "epoca"), T.t(k, "titulo"), T.t(k, "texto"), fuente_html))
    return ('<section class="s-historia" id="historia" data-nav="light">'
            '<div class="hs-intro-plain reveal"><span class="s-tag">%s</span><h2 class="s-title">%s</h2><p class="s-body">%s</p></div>'
            '<div class="cap hist tema-azul" data-nav="light"><div class="cap-stage">%s'
            '<div class="banner" id="hsBanner">%s</div>'
            '<div class="hs-timeline"><div class="hs-timeline-here" id="hsHere">%s</div>'
            '<div class="hs-timeline-track"><div class="hs-timeline-fill" id="hsFill"></div><div class="hs-timeline-dot" id="hsDot"></div>%s</div></div>'
            '</div><div class="cap-steps" id="hsSteps">%s</div></div></section>'
            % (T.t("historia-intro", "etiqueta"), T.t("historia-intro", "titulo"), T.t("historia-intro", "texto"),
               rd("tools/fragmentos/historia_mapa.html"), T.t("historia-0", "banner"), T.t("historia-0", "linea"), ticks_html, steps))

# ═══════════════════════════════════════════════════════════════════════════
#  PÁGINA
# ═══════════════════════════════════════════════════════════════════════════
# índice: 1 Historia · 2 El proyecto (2.1-2.4 subíndices) · 3 Participa.
# El compromiso presidencial queda como contenido (entre Historia y El proyecto)
# pero no aparece como punto del índice.
INDICE = [
    ("1", "#historia", "#1f6fd6", ""),
    ("2", "#proyecto", "#1f6fd6", ""),
    ("2.1", "#calidad", "#f0938c", "sub"),
    ("2.2", "#inundaciones", "#f78b62", "sub"),
    ("2.3", "#ecosistemas", "#8c871d", "sub"),
    ("2.4", "#resumen", "#1f6fd6", "sub"),
    ("3", "#participa", "#3fae7a", ""),
]
idx_items = idx_list = ""
for num, h, c, sub in INDICE:
    k = "indice-" + num
    cls = " idx-sub" if sub else ""
    idx_items += '<a class="idx-item%s" href="%s" style="--c:%s"><b>%s</b><span>%s</span></a>' % (cls, h, c, num, T.t(k, "titulo"))
    idx_list += '<li class="%s"><a href="%s" style="--c:%s"><b>%s</b><span>%s<small>%s</small></span></a></li>' % (sub, h, c, num, T.t(k, "titulo"), T.t(k, "descripcion"))

FILTROS = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<filter id="f-rosa"    color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.941  0 0 0 0 0.576  0 0 0 0 0.549  0 0 0 1 0"/></filter>
<filter id="f-naranja" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.969  0 0 0 0 0.545  0 0 0 0 0.384  0 0 0 1 0"/></filter>
<filter id="f-naranja-x2" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.969  0 0 0 0 0.545  0 0 0 0 0.384  0 0 0 2.6 0"/></filter>
<filter id="f-verde"   color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.549  0 0 0 0 0.529  0 0 0 0 0.114  0 0 0 1 0"/></filter>
<filter id="f-slate"   color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.396  0 0 0 0 0.455  0 0 0 0 0.545  0 0 0 1 0"/></filter>
</defs></svg>'''

def hero():
    return ('<header class="hero" id="top" data-nav="light">'
            '<div class="hero-bg"></div><div class="hero-glow"></div>'
            '<p class="hs-eyebrow">%s</p><h1 class="hs-main-title">%s</h1><p class="hs-subtitle">%s</p>'
            '<div class="hero-cta"><a class="btn btn-dark" href="#historia">%s</a></div>'
            '<div class="idx-grid" aria-label="Índice">%s</div></header>'
            % (T.t("portada", "eyebrow"), T.t("portada", "titulo"), T.t("portada", "subtitulo"), T.t("portada", "boton"), idx_items))

def kfpair(id_, campo):
    partes = [x.strip() for x in T.raw(id_, campo).split("|", 1)]
    if len(partes) != 2:
        raise TextosError('En "## %s", el campo "%s:" debe ser "cifra | explicación".' % (id_, campo))
    return fmt(partes[0]), fmt(partes[1])

def promesa():
    a, b, c = (kfpair("promesa-1", "cifra%d" % i) for i in (1, 2, 3))
    t1, t2 = kfpair("promesa-2", "tarjeta1"), kfpair("promesa-2", "tarjeta2")
    foto = carousel("promesa-1", etiqueta="Foto")
    return ('<section class="s-promesa" id="promesa" data-nav="light" '
            'style="background-image:url(img/mapa/historia-final.webp)">'
            '<div class="pm-scrim"></div><div class="pm-fade"></div>'
            '<div class="pm-grid">'
            '<div class="pm-text rv">'
            '<p class="pm-kicker">%s</p>'
            '<div class="pm-92-row"><div class="pm-92">92</div><div><h2 class="pm-h">%s</h2><p class="pm-h-sub">%s</p></div></div>'
            '<p class="pm-sub">%s</p>'
            '<div class="tula-facts"><div><b>%s</b><span>%s</span></div><div><b>%s</b><span>%s</span></div><div><b>%s</b><span>%s</span></div></div>'
            '<div class="pm-divider"></div>'
            '<p class="pm-kicker">%s</p><h3 class="pm-h2">%s</h3>'
            '<div class="nums"><div class="n"><b>%s</b><span>%s</span></div><div class="n"><b>%s</b><span>%s</span></div></div>'
            '<p class="pm-puente">%s<span>↓</span></p><p class="pm-fuentes">%s</p>'
            '</div>'
            '<div class="pm-photo">%s</div>'
            '</div></section>'
            % (T.t("promesa-1", "etiqueta"), T.t("promesa-1", "titulo"), T.t("promesa-1", "titulo2"), T.t("promesa-1", "texto"),
               a[0], a[1], b[0], b[1], c[0], c[1],
               T.t("promesa-2", "etiqueta"), T.t("promesa-2", "titulo"),
               t1[0], t1[1], t2[0], t2[1], T.t("promesa-2", "puente"), T.t("promesa-2", "fuentes"), foto))

def pie():
    return '<footer>%s<br>%s</footer>' % (T.t("sitio", "pie1"), T.t("sitio", "pie2"))

PLANTILLA = '''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>%(titulo)s</title>
  <meta name="description" content="%(descripcion)s" />
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="css/temas.css?v=7" />
  <link rel="stylesheet" href="css/historia.css?v=7" />
  <link rel="stylesheet" href="css/capitulos.css?v=7" />
  <script>document.documentElement.classList.add('js')</script>
</head>
<body>
%(filtros)s
<div id="progress"></div>

<nav id="main-nav">
  <a class="nav-logo" href="#top">%(logo)s <span>%(logo_sub)s</span></a>
  <div class="nav-right">
    <button class="nav-btn" id="idxBtn" type="button">%(boton_indice)s</button>
  </div>
</nav>

<div class="idx-panel" id="idxPanel" role="dialog" aria-label="%(titulo_indice)s">
  <button class="idx-close" id="idxClose" type="button" aria-label="Cerrar">×</button>
  <div class="idx-box"><h2>%(titulo_indice)s</h2><ul class="idx-list">%(idx_list)s</ul></div>
</div>

<div class="borrador">%(aviso)s <button id="borradorClose" type="button" aria-label="Cerrar aviso">×</button></div>

<div class="lightbox" id="lightbox"><button class="lightbox-close" type="button" aria-label="Cerrar">×</button><button class="lightbox-nav lightbox-prev" type="button" aria-label="Anterior">‹</button><img id="lightboxImg" alt=""><button class="lightbox-nav lightbox-next" type="button" aria-label="Siguiente">›</button><div class="lightbox-cap" id="lightboxCap"></div></div>

%(hero)s

%(historia)s

%(promesa)s

%(hub)s

%(calidad)s

%(inund)s

%(eco)s

%(resumen)s

%(participa)s

%(pie)s

<script src="js/sitio.js?v=7"></script>
</body>
</html>
'''

def construir():
    return PLANTILLA % dict(
        titulo=attr(T.raw("sitio", "titulo")), descripcion=attr(T.raw("sitio", "descripcion")),
        logo=T.t("sitio", "logo"), logo_sub=T.t("sitio", "logo_sub"), boton_indice=T.t("sitio", "boton_indice"),
        titulo_indice=T.t("sitio", "titulo_indice"), aviso=T.t("sitio", "aviso"),
        filtros=FILTROS, idx_list=idx_list, hero=hero(), historia=historia_section(), promesa=promesa(),
        hub=hub, calidad=calidad, inund=inund, eco=eco, resumen=resumen(), participa=participa(), pie=pie())

try:
    page = construir()
except TextosError as e:
    sys.exit("\nERROR EN LOS TEXTOS: %s\n(index.html no se modificó.)\n" % e)

open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page)

# ─── LEEME de fotos ────────────────────────────────────────────────────────
rows = "\n".join("| `img/fotos/%s/1_<pie de foto>.jpg` |" % s for s in SECCIONES_FOTOS)
leeme = """# Fotos

Una carpeta por sección. Dentro, un archivo por foto: `<orden>_<pie de foto>.jpg`
(el pie de foto es el nombre del archivo; se muestra tal cual en el sitio).

Ejemplo: `img/fotos/inundaciones-1/1_Obra de estabilización con gaviones en El Chamizal - agosto 2026.jpg`

Formatos admitidos: jpg, jpeg, png, webp. Si una carpeta no existe o está vacía,
se muestra un marcador con la ruta esperada.

## Carpetas esperadas

%s

Este archivo se genera automáticamente; no editar a mano.
""" % rows
os.makedirs(FOTOS_DIR, exist_ok=True)
open(os.path.join(FOTOS_DIR, "LEEME.md"), "w", encoding="utf-8").write(leeme)
print("index.html:", len(page) // 1024, "KB ·", len(SECCIONES_FOTOS), "secciones con carrusel")
