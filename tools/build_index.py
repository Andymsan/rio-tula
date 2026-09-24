# -*- coding: utf-8 -*-
"""
Genera index.html (sitio de scroll del río Tula).

    python tools/build_index.py

QUÉ ES CADA COSA
  · TEXTOS.md            → todos los TEXTOS (se editan ahí, en GitHub, sin programar)
  · este archivo         → la ESTRUCTURA: qué imagen, zoom, pines y capas lleva cada paso
  · tools/fragmentos/historia_mapa.html → el mapa SVG de la historia (lo genera build_historia_map.py)
  · tools/textos.py      → lee TEXTOS.md y convierte las marcas (**negrita**, ==resaltado==…)

Al terminar también escribe img/fotos/LEEME.md (lista de fotos que espera el sitio).
Si falta algo en TEXTOS.md se detiene con un mensaje claro y NO cambia index.html.

Convenciones
  · coordenadas de pines/cámaras: 0-1 sobre el marco 16:9 del render (x, y)
  · fotos: img/fotos/<clave>.jpg  (si no existe, se muestra un marcador)
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textos import Textos, TextosError, fmt, attr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()

def _mensaje_amable(tipo, valor, tb):
    """Si el error es de los textos, lo dice en español y sin traceback."""
    if issubclass(tipo, TextosError):
        sys.stderr.write("\nERROR EN LOS TEXTOS: %s\n(index.html NO se modificó.)\n\n" % valor)
    else:
        sys.__excepthook__(tipo, valor, tb)
sys.excepthook = _mensaje_amable

try:
    T = Textos(os.path.join(ROOT, "TEXTOS.md"))
except FileNotFoundError:
    sys.exit("ERROR: no encuentro TEXTOS.md")

FOTOS = []          # (clave, pie) para el LEEME

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

def carousel(id_, slides, etiqueta="Fotos del proyecto"):
    """slides = [("clave-de-foto", None) | (None, "ruta/imagen.webp", contain?)] — los pies de foto vienen de TEXTOS.md (campo fotos:)."""
    caps = T.lista(id_, "fotos", esperado=len(slides))
    out = []
    for i, s in enumerate(slides):
        foto, src, contain = (s + (None, None))[:3] if len(s) < 3 else s
        cap = attr(caps[i])
        a = ""
        if foto:
            a += ' data-foto="%s"' % foto
            FOTOS.append((foto, caps[i]))
        if src:
            a += ' data-src="%s"' % src
        if contain:
            a += ' data-contain'
        out.append('<figure class="bu-slide"%s data-cap="%s"></figure>' % (a, cap))
    return ('<div class="burbuja" data-carousel aria-label="%s"><span class="bu-hint">Desliza →</span>'
            '<div class="bu-track">%s</div><div class="bu-dots"></div>'
            '<button class="bu-btn bu-prev" type="button" aria-label="Anterior">‹</button>'
            '<button class="bu-btn bu-next" type="button" aria-label="Siguiente">›</button></div>'
            % (etiqueta, "".join(out)))

def card(id_):
    """Tarjeta de texto de un paso; todo sale de TEXTOS.md."""
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
#  COORDENADAS (marco 16:9 de los renders)
# ═══════════════════════════════════════════════════════════════════════════
# marco "int" / "acc" / "base"  (cámara inclinada sobre Tula)
INT = dict(bojay=(0.585, 0.165), trescult=(0.575, 0.352), rosas=(0.455, 0.527),
           sanlorenzo=(0.537, 0.693), chamizal=(0.391, 0.934))
# marco "col" (vista amplia con colectores y PTAR Atotonilco)
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
    V = (260.0, 250.0)                                  # esquina compartida = el río
    cen = dict(rosa=(V[0], V[1] - R),                   # arriba
               naranja=(V[0] + W, V[1] + R / 2),        # abajo-derecha
               verde=(V[0] - W, V[1] + R / 2))          # abajo-izquierda

    def poly(c):
        x, y = c
        pts = [(x, y - R), (x + W, y - R / 2), (x + W, y + R / 2), (x, y + R), (x - W, y + R / 2), (x - W, y - R / 2)]
        return " ".join("%.1f,%.1f" % p for p in pts)

    ico = dict(
        rosa='<path class="ico" d="M0 -30 C10 -15 16 -8 16 0 A16 16 0 0 1 -16 0 C-16 -8 -10 -15 0 -30 Z"/>',       # gota
        naranja='<path class="ico" d="M-20 -6 q5 -7 10 0 t10 0 t10 0 t10 0 M-20 6 q5 -7 10 0 t10 0 t10 0 t10 0"/>',  # olas
        verde='<path class="ico" d="M-16 12 C-18 -12 2 -26 18 -22 C22 -4 10 14 -16 12 Z M-16 12 L4 -8"/>',         # hoja
    )
    def tile(k):
        partes = T.lista("hexagonos", k)          # línea 1 | (línea 2) — sin número de proyectos (pidió Ariel)
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

# Simplificado a pedido de Ariel: una sola figura (sin resaltar cada hexágono por
# separado ni mostrar el número de proyectos en ellos) con 2 pasos de texto.
hub_steps = [
    step(".5,.5,1", "int", card("proyecto-0"), wash=".93", hex="all", tema="rosa"),
    step(".5,.5,1", "int", card("proyecto-4"), wash=".93", hex="all", tema="rosa"),
]
hub = cap("proyecto", "rosa", T.t("proyecto", "banner"), frame("int"), hub_steps, extra_stage='<div class="wash"></div>' + HEXES)

# ═══════════════════════════════════════════════════════════════════════════
#  CALIDAD DEL AGUA  (rosa) — marco "col"
# ═══════════════════════════════════════════════════════════════════════════
calidad_canvas = (frame("col")
    + pin("atot", *COL["atot"], label="PTAR Atotonilco", sub="", side="")
    + pin("colec", *COL["colec"], label="Colectores del río Tula", sub="", side="r")
    + pin("cfe", *COL["cfe"], label="PTAR de la CFE", sub="", side="l")
    + pin("boya", *COL["endho"], label="Boya · presa Endhó", sub="", side=""))

calidad_steps = [
    step(".55,.5,1.05", "col", card("calidad-0"), pins=""),
    step(".615,.79,2.3", "col", card("calidad-1"),
         carousel("calidad-1", [("atotonilco-1",), ("atotonilco-2",), ("atotonilco-3",)]), pins="atot"),
    # Orden invertido a pedido de Ariel: primero Drenaje de Tula, luego Industria.
    step(".64,.47,1.35", "col", card("calidad-3"),
         carousel("calidad-3", [("colectores-1",), ("colectores-2",), ("colectores-3",)]), pins="colec cfe"),
    step(".55,.47,1.25", "col", card("calidad-2"),
         carousel("calidad-2", [("industria-1",), ("industria-2",)]), pins=""),
    step(".55,.46,1.05", "col", card("calidad-4"),
         carousel("calidad-4", [("monitoreo-1",), ("monitoreo-2",)]), pins="boya atot"),
]
calidad = cap("calidad", "rosa", T.t("calidad", "banner"), calidad_canvas, calidad_steps)

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
    step(".5,.55,1.05", "int", card("inundaciones-0")),
    step(".46,.81,1.9", "int", card("inundaciones-1"),
         carousel("inundaciones-1", [("taludes-1",), ("taludes-2",), ("taludes-3",)]), ov="sanlorenzo chamizal", pins="sanlorenzo chamizal"),
    step(".5,.44,1.6", "int", card("inundaciones-2"),
         carousel("inundaciones-2", [("desazolve-1",), ("desazolve-2",)]), ov="tramo", pins="trescult rosas"),
    step(".55,.5,1.0", "col", card("inundaciones-3"),
         carousel("inundaciones-3", [("caudal-1",)])),
    step(".575,.35,2.2", "int", card("inundaciones-4"),
         carousel("inundaciones-4", [(None, "img/ref/buffalo-bayou-houston.jpg"),
                                     (None, "img/ref/rodney-cook-park-atlanta-1.jpg"),
                                     (None, "img/ref/parque-inundable-georgia.jpg")], "Referencias"),
         ov="trescult", pins="trescult"),
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
    step(".5,.5,1.7", "int", card("ecosistemas-1"),
         carousel("ecosistemas-1", [("riberas-1",), ("riberas-2",)])),
    step(".585,.17,2.3", "int", card("ecosistemas-2"),
         carousel("ecosistemas-2", [(None, "img/mapa/z-bojay-zoom.webp", True),
                                    (None, "img/mapa/z-bojay-verde.webp", True),
                                    ("bojay-1",)]), ov="bojay", pins="bojay", labels="endho"),
    step(".36,.24,1.6", "base", card("ecosistemas-3"),
         carousel("ecosistemas-3", [("bosques-1",), ("bosques-2",)]), ov="rio", labels="anp parque"),
    step(".5,.55,1.05", "int", card("ecosistemas-4"),
         carousel("ecosistemas-4", [(None, "img/mapa/z-rosas.webp", True),
                                    (None, "img/mapa/z-sanlorenzo.webp", True),
                                    (None, "img/mapa/z-bojay-zoom.webp", True),
                                    ("espacio-publico-1",)]),
         ov="bojay trescult rosas sanlorenzo chamizal", pins="bojay trescult rosas sanlorenzo chamizal"),
    step(".5,.55,1.05", "acc", card("ecosistemas-5"),
         pins="bojay trescult rosas sanlorenzo chamizal", pop="1"),
    step(".5,.55,1.05", "int", card("ecosistemas-6"), ov="conect", labels="parque"),
]
eco = cap("ecosistemas", "verde", T.t("ecosistemas", "banner"), eco_canvas, eco_steps)

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
INDICE = [   # (número en TEXTOS.md, ancla, color) — 4/5/6 son subíndices de "3 El proyecto"
    ("1", "#historia", "#1f6fd6"), ("2", "#promesa", "#f0938c"), ("3", "#proyecto", "#1f6fd6"),
    ("4", "#calidad", "#f0938c"), ("5", "#inundaciones", "#f78b62"), ("6", "#ecosistemas", "#8c871d"),
]
idx_items = idx_list = ""
for i, (n, h, c) in enumerate(INDICE, 1):
    k = "indice-" + n
    if i <= 3:
        num, sub = str(i), ""
    else:
        num, sub = "3.%d" % (i - 3), " idx-sub"
    idx_items += '<a class="idx-item%s" href="%s" style="--c:%s"><b>%s</b><span>%s</span></a>' % (sub, h, c, num, T.t(k, "titulo"))
    idx_list += '<li class="%s"><a href="%s" style="--c:%s"><b>%s</b><span>%s<small>%s</small></span></a></li>' % (sub.strip(), h, c, num, T.t(k, "titulo"), T.t(k, "descripcion"))

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
    foto = carousel("promesa-1", [("presidenta-toma-protesta",)], "Foto")
    return ('<section class="s-promesa" id="promesa" data-nav="light">'
            '<div class="pm-beat"><div class="pm-wrap pm-1"><div class="rv">'
            '<p class="pm-kicker">%s</p><h2 class="pm-h">%s<span>%s</span></h2><p class="pm-sub">%s</p>'
            '<div class="tula-facts"><div><b>%s</b><span>%s</span></div><div><b>%s</b><span>%s</span></div><div><b>%s</b><span>%s</span></div></div>'
            '</div>%s</div></div>'
            '<div class="pm-beat"><div class="pm-wrap pm-2"><p class="pm-kicker rv">%s</p><h2 class="rv">%s</h2>'
            '<div class="nums rv"><div class="n" style="--nc:#1f6fd6"><b>%s</b><span>%s</span></div>'
            '<div class="n" style="--nc:#ec6f66"><b>%s</b><span>%s</span></div></div>'
            '<p class="pm-puente rv">%s<span>↓</span></p><p class="pm-fuentes rv">%s</p></div></div></section>'
            % (T.t("promesa-1", "etiqueta"), T.t("promesa-1", "titulo"), T.t("promesa-1", "titulo2"), T.t("promesa-1", "texto"),
               a[0], a[1], b[0], b[1], c[0], c[1], foto,
               T.t("promesa-2", "etiqueta"), T.t("promesa-2", "titulo"),
               t1[0], t1[1], t2[0], t2[1], T.t("promesa-2", "puente"), T.t("promesa-2", "fuentes")))

def pie():
    return '<footer>%s<br>%s</footer>' % (T.t("sitio", "pie1"), T.t("sitio", "pie2"))

PLANTILLA = '''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>%(titulo)s</title>
  <meta name="description" content="%(descripcion)s" />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Noto+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="css/temas.css?v=5" />
  <link rel="stylesheet" href="css/historia.css?v=5" />
  <link rel="stylesheet" href="css/capitulos.css?v=5" />
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

%(hero)s

%(historia)s

%(promesa)s

%(hub)s

%(calidad)s

%(inund)s

%(eco)s

%(pie)s

<script src="js/sitio.js?v=5"></script>
</body>
</html>
'''

def construir():
    return PLANTILLA % dict(
        titulo=attr(T.raw("sitio", "titulo")), descripcion=attr(T.raw("sitio", "descripcion")),
        logo=T.t("sitio", "logo"), logo_sub=T.t("sitio", "logo_sub"), boton_indice=T.t("sitio", "boton_indice"),
        titulo_indice=T.t("sitio", "titulo_indice"), aviso=T.t("sitio", "aviso"),
        filtros=FILTROS, idx_list=idx_list, hero=hero(), historia=historia_section(), promesa=promesa(),
        hub=hub, calidad=calidad, inund=inund, eco=eco, pie=pie())

try:
    page = construir()
except TextosError as e:
    sys.exit("\nERROR EN LOS TEXTOS: %s\n(index.html NO se modificó.)\n" % e)

open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page)

# ─── LEEME de fotos ────────────────────────────────────────────────────────
rows = "\n".join("| `%s.jpg` | %s |" % (k, c) for k, c in FOTOS)
leeme = """# Fotos del sitio

Para sustituir un marcador por una foto: **guarda la imagen aquí con el nombre exacto de la
tabla** (JPG o PNG; horizontal, ~1600 px de ancho). No hay que tocar código.

| Archivo | Pie de foto / qué va |
|---|---|
%s

- Si el archivo no existe, el sitio muestra un marcador con rayas y el nombre del archivo.
- Los pies de foto se cambian en `TEXTOS.md` (campo `fotos:`).
- Para agregar más fotos a un carrusel, pídeselo a Andrea (hay que sumar una entrada).
- Archivo generado por `tools/build_index.py`.
""" % rows
os.makedirs(os.path.join(ROOT, "img", "fotos"), exist_ok=True)
open(os.path.join(ROOT, "img", "fotos", "LEEME.md"), "w", encoding="utf-8").write(leeme)
print("index.html escrito:", len(page) // 1024, "KB ·", len(FOTOS), "fotos esperadas")
