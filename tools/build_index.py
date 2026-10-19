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
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textos import Textos, TextosError, fmt, attr
import sankey, donut

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
    _datos_insp = os.path.join(ROOT, "data", "inspecciones.json")
    _insp = json.load(open(_datos_insp, encoding="utf-8"))["total"] if os.path.exists(_datos_insp) else 92
    T = Textos(os.path.join(ROOT, "TEXTOS.md"), {"inspecciones": _insp})
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
    return ('<div class="burbuja" data-carousel aria-label="%s">'
            '<div class="bu-track">%s</div><div class="bu-dots"></div>'
            '<button class="bu-btn bu-prev" type="button" aria-label="Anterior">‹</button>'
            '<button class="bu-btn bu-next" type="button" aria-label="Siguiente">›</button></div>'
            % (etiqueta, "".join(slides)))

ESTADOS = {"terminado": "Terminado", "obra": "En obra", "licitacion": "En licitación", "curso": "En marcha", "planeacion": "En planeación"}

def card(id_):
    h = '<div class="card"><div class="tag">%s</div>' % T.t(id_, "etiqueta")
    est = T.raw(id_, "estado", requerido=False)
    if est:
        partes = [x.strip() for x in est.split("|", 1)]
        if len(partes) != 2 or partes[0] not in ESTADOS:
            raise TextosError('En "## %s", "estado:" debe ser "tipo | texto" con tipo = %s.' % (id_, ", ".join(ESTADOS)))
        h += '<div class="estado e-%s"><i></i><b>%s</b><span>· %s</span></div>' % (partes[0], ESTADOS[partes[0]], fmt(partes[1]))
    h += '<h3>%s</h3>' % T.t(id_, "titulo")
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
    av = T.raw(id_, "avance", requerido=False)
    if av:
        n = [x.strip() for x in av.split("|")]
        if len(n) != 4:
            raise TextosError('En "## %s", "avance:" debe ser "terminado | en obra | en planeación | unidad".' % id_)
        h += ('<div class="avance"><div class="av-bar"><i class="a1" style="flex:%s"></i><i class="a2" style="flex:%s"></i><i class="a3" style="flex:%s"></i></div>'
              '<div class="av-leg"><span class="a1">%s %s terminado</span><span class="a2">%s %s en obra</span><span class="a3">%s %s en planeación</span></div></div>'
              % (n[0], n[1], n[2], n[0], n[3], n[1], n[3], n[2], n[3]))
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

def banner_html(texto, num=None):
    """'Un río más limpio | Calidad del agua' -> lema grande + frente chico (con el número del lema)."""
    if "|" not in texto:
        return '<div class="banner">%s</div>' % texto
    a, b = [x.strip() for x in texto.split("|", 1)]
    n = '<b class="bn">%s</b>' % num if num else ""
    return '<div class="banner dos">%s<span class="bt"><strong>%s</strong><small>%s</small></span></div>' % (n, a, b)

def cap(id_, tema, banner, canvas_inner, steps, extra_stage="", num=None):
    return ('<section class="cap tema-%s" id="%s" data-tema="%s" data-nav="light">'
            '<div class="cap-stage"><div class="canvas">%s</div>%s%s</div>'
            '<div class="cap-steps">%s</div></section>' % (tema, id_, tema, canvas_inner, extra_stage, banner_html(banner, num), "".join(steps)))

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
        for j, linea in enumerate(partes[:3]):
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
    + pin("atot", *COL["atot"], label="PTAR Atotonilco", sub="", side="")
    + pin("cvig", *COL["atot"], label="Centro de Vigilancia del Agua", sub="", side="")
    + pin("colec", *COL["colec"], label="Colectores del río Tula", sub="", side="r")
    + pin("cfe", *COL["cfe"], label="PTAR de la CFE", sub="", side="l")
    + pin("boya", *COL["endho"], label="Boya · presa Endhó", sub="", side=""))

calidad_steps = [
    step(".55,.5,1.05", "col", card("calidad-0"), pins=""),
    step(".615,.79,2.3", "col", card("calidad-1"), carousel("calidad-1"), pins="atot"),
    step(".64,.47,1.35", "col", card("calidad-3"), carousel("calidad-3"), pins="colec cfe"),
    step(".55,.47,1.25", "col", card("calidad-2"), carousel("calidad-2"), pins=""),
    step(".55,.46,1.05", "col", card("calidad-4"), carousel("calidad-4"), pins="boya cvig"),
]
calidad = cap("calidad", "rosa", T.raw("calidad", "banner"), calidad_canvas, calidad_steps, num=1)

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
]
inund = cap("inundaciones", "naranja", T.raw("inundaciones", "banner"), inund_canvas, inund_steps, num=2)

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

]
eco = cap("ecosistemas", "verde", T.raw("ecosistemas", "banner"), eco_canvas, eco_steps, num=3)

# Espacio público: capítulo propio ("Un río para todas y todos"). Cámara desplazada
# hacia arriba para que Bojay (cerca del borde superior de la imagen) no se corte;
# incluye las isócronas (marco "acc").
ep_steps = [
    step(".5,.4,1.0", "acc", card("ecosistemas-4"),
         carousel("ecosistemas-4"),
         ov="bojay trescult rosas sanlorenzo chamizal", pins="bojay trescult rosas sanlorenzo chamizal"),
]
espacio = cap("espacio-publico", "verde", T.raw("espacio-publico", "banner"), eco_canvas, ep_steps, num=4)

# ═══════════════════════════════════════════════════════════════════════════
#  RESUMEN (mapa con las 5 metas; se resalta la que está en foco)
# ═══════════════════════════════════════════════════════════════════════════
# (cámara, marco, capas [+ "tint-x" para recolorear], pines, etiquetas, título, detalle, descripción)
# (cámara, marco, capas [+ "tint-x" para recolorear], pines, etiquetas); título y texto: ## resumen-N en TEXTOS.md
METAS = [
    (".55,.5,1.05", "col", "", "atot colec cfe", ""),
    (".55,.47,1.25", "col", "", "", ""),
    (".5,.55,1.05", "int", "sanlorenzo chamizal trescult rosas tint-naranja", "sanlorenzo chamizal trescult rosas", ""),
    (".36,.24,1.3", "base", "rio", "", "anp parque"),
    (".5,.55,1.05", "int", "bojay trescult rosas sanlorenzo chamizal tint-verde", "bojay trescult rosas sanlorenzo chamizal", ""),
]

def resumen_canvas():
    ovs, tint_por_ov = set(), {}
    for _, _, ovlist, _, _ in METAS:
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
    html += pin("atot", *COL["atot"], label="PTAR Atotonilco", side="")
    html += pin("colec", *COL["colec"], label="Colectores del río Tula", side="r")
    html += pin("cfe", *COL["cfe"], label="PTAR de la CFE", side="l")
    html += mlabel("anp", 0.34, 0.22, "Nueva Área Natural<br>Protegida")
    html += mlabel("parque", 0.62, 0.465, "Parque Nacional y<br>Atlantes de Tula")
    return html

META_ICONOS = [
    '<path d="M12 3C16 9 19 12 19 15.5A7 7 0 0 1 5 15.5C5 12 8 9 12 3Z"/>',
    '<circle cx="11" cy="11" r="6"/><path d="M16 16l5 5"/>',
    '<path d="M3 9q3-4 6 0t6 0t6 0M3 15q3-4 6 0t6 0t6 0"/>',
    '<path d="M12 21v-6M12 15c-4 0-6-3-5-6 0-2 2-4 5-4s5 2 5 4c1 3-1 6-5 6z"/>',
    '<path d="M12 21s-6-5.2-6-10a6 6 0 0 1 12 0c0 4.8-6 10-6 10z"/><circle cx="12" cy="11" r="2.2"/>',
]
META_COLOR = ["rosa", "rosa", "naranja", "verde", "verde"]

def resumen_meta(i, cam, frame_, ovlist, pins, labels):
    k = "resumen-%d" % (i + 1)
    titulo, desc = T.t(k, "titulo"), T.t(k, "texto")
    kp = [x.strip() for x in T.raw(k, "cifra").split("|", 1)]
    ov_sin_tint = " ".join(x for x in ovlist.split() if not x.startswith("tint-"))
    return ('<li class="meta" tabindex="0" role="button" aria-expanded="false" style="--c:var(--%s-fill);--cd:var(--%s-dark)" '
            'data-cam="%s" data-frame="%s" data-ov="%s" data-pins="%s" data-labels="%s" data-n="%d" data-t="%s" data-d="%s" data-kv="%s" data-ks="%s">'
            '<span class="meta-top"><span class="meta-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">%s</svg></span>'
            '<em>%d</em></span><span class="meta-kpi"><b class="cnt">%s</b><small>%s</small></span><strong>%s</strong><i class="meta-bar"></i></li>'
            % (META_COLOR[i], META_COLOR[i], cam, frame_, ov_sin_tint, pins, labels, i + 1, attr(titulo), attr(T.raw(k, "texto")), attr(kp[0]), attr(kp[1]),
               META_ICONOS[i], i + 1, fmt(kp[0]), fmt(kp[1]), T.t(k, "corto")))

def resumen():
    metas_html = "".join(resumen_meta(i, *m) for i, m in enumerate(METAS))
    return ('<section class="s-resumen tema-azul" id="resumen" data-nav="light" data-fit><div class="fit-in">'
            '<div class="section-inner"><span class="s-tag">%s</span><h2 class="s-title">%s</h2>'
            '<p class="s-subtitle">%s</p>%s</div>'
            '<div class="resumen-wrap"><div class="resumen-stage" id="resumenStage"><div class="canvas">%s</div><div class="wash"></div></div>'
            '<div class="rc" id="rc"><i class="rc-bar"><b></b></i><div class="rc-top"><span class="rc-n"></span><span class="rc-of">%s</span></div>'
            '<div class="rc-kpi"><b id="rcK"></b><small id="rcS"></small></div><h3 id="rcT"></h3><p id="rcP"></p>'
            '<div class="rc-nav"><button type="button" class="rc-prev" aria-label="Meta anterior">‹</button><span class="rc-dots">%s</span><button type="button" class="rc-next" aria-label="Meta siguiente">›</button></div></div>'
            '<ul class="resumen-metas" id="resumenMetas" hidden>%s</ul></div></div></section>'
            % (T.t("resumen", "etiqueta"), T.t("resumen", "titulo"), T.t("resumen", "subtitulo"),
               ('<p class="s-body">%s</p>' % T.t("resumen", "texto")) if T.raw("resumen", "texto", requerido=False) not in (None, '""') else "",
               resumen_canvas(), "de 5 metas", "".join('<button type="button" aria-label="Meta %d"></button>' % (n + 1) for n in range(len(METAS))),
               metas_html))

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
# índice: 1 De dónde viene el agua · 2 Historia (subpágina) · 3 El proyecto (3.1-3.5) · 4 Participa.
# El compromiso presidencial queda como contenido pero no aparece como punto del índice.
INDICE = [
    ("origen", "#origen", "#1f6fd6", ""),
    ("historia", "historia.html", "#1f6fd6", ""),
    ("proyecto", "#proyecto", "#1f6fd6", ""),
    ("limpio", "#calidad", "#f0938c", "sub"),
    ("seguro", "#inundaciones", "#f78b62", "sub"),
    ("vivo", "#ecosistemas", "#8c871d", "sub"),
    ("todos", "#espacio-publico", "#8c871d", "sub"),
    ("resumen", "#resumen", "#1f6fd6", "sub"),
    ("participa", "#participa", "#3fae7a", ""),
]

def indice(desde_historia=False):
    """(tarjetas del hero, lista del panel). En la subpágina los enlaces a la portada llevan index.html."""
    items = lista = ""
    n = sub_n = 0
    for k, h, c, sub in INDICE:
        if sub:
            sub_n += 1; num = "%d.%d" % (n, sub_n)
        else:
            n += 1; sub_n = 0; num = str(n)
        if desde_historia and h.startswith("#"):
            h = "index.html" + h
        key = "indice-" + k
        cls = " idx-sub" if sub else ""
        items += '<a class="idx-item%s" href="%s" style="--c:%s"><b>%s</b><span>%s</span></a>' % (cls, h, c, num, T.t(key, "titulo"))
        lista += '<li class="%s"><a href="%s" style="--c:%s"><b>%s</b><span>%s<small>%s</small></span></a></li>' % (sub, h, c, num, T.t(key, "titulo"), T.t(key, "descripcion"))
    return items, lista

idx_items, idx_list = indice()
_, idx_list_hist = indice(True)

FILTROS = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<filter id="f-rosa"    color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.753  0 0 0 0 0.478  0 0 0 0 0.447  0 0 0 1 0"/></filter>
<filter id="f-naranja" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.788  0 0 0 0 0.400  0 0 0 0 0.122  0 0 0 1 0"/></filter>
<filter id="f-naranja-x2" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.788  0 0 0 0 0.400  0 0 0 0 0.122  0 0 0 2.6 0"/></filter>
<filter id="f-verde"   color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.435  0 0 0 0 0.420  0 0 0 0 0.100  0 0 0 1 0"/></filter>
<filter id="f-slate"   color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0 0 0 0 0.396  0 0 0 0 0.455  0 0 0 0 0.545  0 0 0 1 0"/></filter>
</defs></svg>'''

def video_portada():
    """Video de fondo de la portada: img/video/portada_*.mp4 si existe; si no, el primero de diagnostico_*."""
    d = os.path.join(ROOT, "img", "video")
    if not os.path.isdir(d):
        return ""
    vids = sorted(f for f in os.listdir(d) if f.lower().endswith(".mp4") and not f.endswith("_m.mp4") and f.startswith(("portada_", "diagnostico_")))
    vids.sort(key=lambda f: 0 if f.startswith("portada_") else 1)
    if not vids:
        return ""
    v = vids[0]; poster = v[:-4] + ".jpg"
    tiene_poster = os.path.exists(os.path.join(d, poster))
    movil = v[:-4] + "_m.mp4"
    dm = (' data-src-m="img/video/%s"' % movil.replace(" ", "%20")) if os.path.exists(os.path.join(d, movil)) else ""
    return ('<video class="hero-video" muted loop playsinline preload="none" aria-hidden="true" data-src="img/video/%s"%s%s></video>'
            % (v.replace(" ", "%20"), dm, (' poster="img/video/%s"' % poster.replace(" ", "%20")) if tiene_poster else ""))

def hero():
    return ('<header class="hero" id="top" data-nav="light">'
            '<div class="hero-bg"></div><div class="hero-glow"></div>%s'
            '<p class="hs-eyebrow">%s</p><h1 class="hs-main-title">%s</h1><p class="hs-subtitle">%s</p>'
            '<div class="hero-cta"><a class="btn btn-dark" href="#origen">%s</a><a class="btn btn-claro" href="historia.html">%s</a></div>'
            '</header>'
            % (video_portada(), T.t("portada", "eyebrow"), T.t("portada", "titulo"), T.t("portada", "subtitulo"), T.t("portada", "boton"), T.t("portada", "boton2")))

def kfpair(id_, campo):
    partes = [x.strip() for x in T.raw(id_, campo).split("|", 1)]
    if len(partes) != 2:
        raise TextosError('En "## %s", el campo "%s:" debe ser "cifra | explicación".' % (id_, campo))
    return fmt(partes[0]), fmt(partes[1])

def promesa():
    t1, t2 = kfpair("promesa-2", "tarjeta1"), kfpair("promesa-2", "tarjeta2")
    foto = carousel("promesa-1", etiqueta="Foto")
    return ('<section class="s-promesa" id="promesa" data-nav="light" data-fit '
            'style="background-image:url(img/mapa/historia-final.webp)">'
            '<div class="pm-scrim"></div><div class="pm-fade"></div>'
            '<div class="pm-grid fit-in"><div class="pm-text rv">'
            '<p class="pm-kicker">%s</p>'
            '<div class="pm-92-row"><div class="pm-92 cnt">92</div><div><h2 class="pm-h">%s</h2><p class="pm-h-sub">%s</p></div></div>'
            '<p class="pm-kicker pm-k2">%s</p>'
            '<div class="nums"><div class="n rv" style="--i:0"><b class="cnt">%s</b><span>%s</span></div><div class="n rv" style="--i:1"><b class="cnt">%s</b><span>%s</span></div></div>'
            '<p class="pm-puente">%s<span>↓</span></p><p class="pm-fuentes">%s</p>'
            '</div><div class="pm-photo">%s</div></div></section>'
            % (T.t("promesa-1", "etiqueta"), T.t("promesa-1", "titulo"), T.t("promesa-1", "titulo2"), T.t("promesa-2", "etiqueta"),
               t1[0], t1[1], t2[0], t2[1], T.t("promesa-2", "puente"), T.t("promesa-2", "fuentes"), foto))

AV_ICONOS = [
    '<path d="M12 3C16 9 19 12 19 15.5A7 7 0 0 1 5 15.5C5 12 8 9 12 3Z"/>',
    '<circle cx="11" cy="11" r="6"/><path d="M16 16l5 5"/>',
    '<path d="M3 8h11a4 4 0 0 1 4 4v8"/><path d="M3 13h6a4 4 0 0 1 4 4v3"/>',
    '<path d="M3 9q3-4 6 0t6 0t6 0M3 15q3-4 6 0t6 0t6 0"/>',
    '<circle cx="12" cy="12" r="2"/><path d="M7.5 7.5a6 6 0 0 0 0 9M16.5 7.5a6 6 0 0 1 0 9M4.5 4.5a10 10 0 0 0 0 15M19.5 4.5a10 10 0 0 1 0 15"/>',
    '<path d="M12 21v-6M12 15c-4 0-6-3-5-6 0-2 2-4 5-4s5 2 5 4c1 3-1 6-5 6z"/>',
    '<path d="M5 19C5 9 10 5 20 4c0 10-4 15-14 15zM5 19l8-8"/>',
]

def origen():
    fig, ley = donut.unica()
    ag = [x.strip() for x in T.raw("origen", "va_agri").split("|")]
    rio = [x.strip() for x in T.raw("origen", "va_rio").split("|")]
    if len(ag) != 4 or len(rio) != 4:
        raise TextosError('En "## origen", "va_agri:" y "va_rio:" deben ser "cifra | título | detalle | porcentaje".')
    ico_ag = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21v-9"/><path d="M12 12c0-4-3-6-7-6 0 4 3 6 7 6z"/><path d="M12 14c0-3 2.5-5 6-5 0 3-2.5 5-6 5z"/></svg>'
    ico_rio = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9q3-4 6 0t6 0t6 0M3 15q3-4 6 0t6 0t6 0"/></svg>'
    def seg(cls, v, ico):
        return ('<div class="va-seg %s" style="--w:%s%%"><span class="va-ico">%s</span><span class="va-t"><b>%s</b> %s</span></div>' % (cls, v[3], ico, v[3] + " %", fmt(v[1])))
    def card(cls, v, ico):
        return ('<div class="va-card %s"><span class="va-ico">%s</span><div><b class="cnt">%s</b><strong>%s</strong><span>%s</span></div></div>'
                % (cls, ico, fmt(v[0]), fmt(v[1]), fmt(v[2])))
    sol = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
    nube = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M7 15a4 4 0 0 1 .5-7.9A5.5 5.5 0 0 1 18 9a3.5 3.5 0 0 1-.5 7H7z"/><path d="M9 19l-1 2M13 19l-1 2M17 19l-1 2"/></svg>'
    return ('<section class="s-origen" id="origen" data-nav="light" data-fit><div class="fit-in">'
            '<div class="or-top rv"><span class="s-tag">%s</span><h2 class="s-title">%s</h2></div>'
            '<div class="or-tabs" role="tablist"><button class="or-tab on" type="button" data-tab="vi"><i>1</i>%s</button>'
            '<button class="or-tab" type="button" data-tab="va"><i>2</i>%s</button></div>'
            '<div class="or-pane on" data-pane="vi"><div class="vi-grid">'
            '<div class="or-map">%s</div>'
            '<div class="vi-panel"><p class="vi-t">%s</p>'
            '<div class="vi-sw" role="group"><button type="button" class="on" data-m="s">%s%s</button><button type="button" data-m="l">%s%s</button></div>'
            '<div class="vi-dn">%s</div>%s<p class="vi-pista">%s</p></div></div></div>'
            '<div class="or-pane" data-pane="va"><p class="or-baj">%s</p>'
            '<div class="va-bar">%s%s</div><div class="va-cards">%s%s</div><p class="or-nota">%s</p></div>'
            '<div class="or-pie"><p class="or-cierre">%s</p><a class="or-btn" href="historia.html"><span class="l">%s</span><span class="s">%s</span></a></div>'
            '</div></section>'
            % (T.t("origen", "etiqueta"), T.t("origen", "titulo"), T.t("origen", "tab1"), T.t("origen", "tab2"),
               rd("tools/fragmentos/origen_mapa.html"), T.t("origen", "viene_titulo"),
               sol, T.t("origen", "secas"), nube, T.t("origen", "lluvias"), fig, ley, T.t("origen", "viene_pista"),
               T.t("origen", "va_titulo"), seg("ag", ag, ico_ag), seg("rio", rio, ico_rio),
               card("ag", ag, ico_ag), card("rio", rio, ico_rio), T.t("origen", "va_nota"),
               T.t("origen", "cierre"), T.t("origen", "boton"), T.t("origen", "boton_corto")))

def avance():
    hechos = ""
    for i in range(1, 8):
        n, txt = kfpair("avance", "hecho%d" % i)
        hechos += ('<div class="av-h rv" style="--i:%d"><span class="av-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
                   'stroke-linecap="round" stroke-linejoin="round">%s</svg></span><b class="cnt">%s</b><span class="av-t">%s</span></div>' % (i - 1, AV_ICONOS[i - 1], n, txt))
    return ('<section class="s-avance" id="avance" data-nav="light" data-fit><div class="av-in fit-in av-split">'
            '<div class="av-left rv"><span class="s-tag"><i class="av-live"></i>%s</span><h2 class="s-title">%s</h2>'
            '<a class="or-btn" href="#proyecto">%s</a></div>'
            '<div class="av-grid">%s</div></div></section>'
            % (T.t("avance", "etiqueta"), T.t("avance", "titulo"), T.t("avance", "siguiente"), hechos))

def diagnostico():
    return ('<section class="s-diag" id="diagnostico" data-nav="light">'
            '<div class="diag-head"><span class="s-tag">%s</span><h2>%s</h2></div>%s<div class="diag-prog"><i></i></div></section>'
            % (T.t("diagnostico", "etiqueta"), T.t("diagnostico", "titulo"), carousel("diagnostico", etiqueta="Fotos de diagnóstico")))

LEMAS = {"limpio": ("img/calidad.jpg", "#f0938c"), "seguro": ("img/inundaciones.jpg", "#f78b62"),
         "vivo": ("img/restauracion.jpg", "#cdd36a"), "todos": ("img/plan.jpg", "#d9b45c")}

RAIL_COLORES = {"limpio": "#c07a72", "seguro": "#c9661f", "vivo": "#6f6b19", "todos": "#9a7421"}

def rail():
    """Guía fija a la izquierda: los cuatro lemas como puntos numerados sobre una línea (aparecen juntos, se abren y resaltan el actual)."""
    its = "".join('<a class="lr-i" href="#lema-%s" data-k="%s" data-t="%s" aria-label="%s" style="--c:%s;--t:%d%%"><i class="lr-dot">%d</i></a>'
                  % (k, k, attr(T.raw("lema-" + k, "titulo")), attr(T.raw("lema-" + k, "titulo")), RAIL_COLORES[k], n * 25, n + 1)
                  for n, k in enumerate(LEMAS))
    return '<nav class="lr" id="lemaRail" aria-label="Los cuatro lemas del proyecto"><span class="lr-line"><b id="lrFill"></b></span>%s</nav>' % its

def lema(k):
    """Ancla invisible al inicio de cada frente (la usan la guía lateral y sus enlaces)."""
    return '<section class="s-lema" id="lema-%s" aria-hidden="true"></section>' % k

def fuentes():
    items = "".join("<li>%s</li>" % fmt(x) for x in T.lista("fuentes", "items"))
    return ('<section class="s-fuentes" id="fuentes" data-nav="light"><div class="fu-in"><h2>%s</h2><ul>%s</ul><p class="fu-nota">%s</p></div></section>'
            % (T.t("fuentes", "titulo"), items, T.t("fuentes", "nota")))

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
  <link rel="stylesheet" href="css/temas.css?v=19" />
  <link rel="stylesheet" href="css/historia.css?v=19" />
  <link rel="stylesheet" href="css/capitulos.css?v=19" />
  <script>(function(){var h=document.documentElement;h.classList.add('js');try{var s=localStorage;if(s.getItem('rt-noche')==='1')h.dataset.theme='dark';if(s.getItem('rt-cvd')==='1')h.dataset.cvd='1'}catch(e){}})()</script>
</head>
<body>
%(filtros)s
<div id="progress"></div>

<nav id="main-nav">
  <a class="nav-logo" href="%(logo_href)s">%(logo)s <span>%(logo_sub)s</span></a>
  <div class="nav-right">
    <a class="nav-btn nav-link" href="%(nav_href)s">%(nav_texto)s</a>
    <div class="a11y">
      <button class="nav-btn a11y-btn" id="a11yBtn" type="button" aria-haspopup="true" aria-expanded="false" aria-controls="a11yMenu" aria-label="%(acc_titulo)s" title="%(acc_titulo)s">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 3v18" /><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg>
      </button>
      <div class="a11y-menu" id="a11yMenu" role="group" aria-label="%(acc_titulo)s">
        <p class="a11y-t">%(acc_titulo)s</p>
        <label class="a11y-sw"><input type="checkbox" id="swNoche"><span class="sw"></span><span>%(acc_noche)s</span></label>
        <label class="a11y-sw"><input type="checkbox" id="swCvd"><span class="sw"></span><span>%(acc_cvd)s</span></label>
      </div>
    </div>
    <button class="nav-btn" id="idxBtn" type="button">%(boton_indice)s</button>
  </div>
</nav>

<div class="idx-panel" id="idxPanel" role="dialog" aria-label="%(titulo_indice)s">
  <button class="idx-close" id="idxClose" type="button" aria-label="Cerrar">×</button>
  <div class="idx-box"><h2>%(titulo_indice)s</h2><ul class="idx-list">%(idx_list)s</ul></div>
</div>

<div class="lightbox" id="lightbox"><button class="lightbox-close" type="button" aria-label="Cerrar">×</button><button class="lightbox-nav lightbox-prev" type="button" aria-label="Anterior">‹</button><img id="lightboxImg" alt=""><button class="lightbox-nav lightbox-next" type="button" aria-label="Siguiente">›</button><div class="lightbox-cap" id="lightboxCap"></div></div>

%(contenido)s

<script src="js/sitio.js?v=19"></script>
</body>
</html>
'''

def comun(**extra):
    d = dict(
        titulo=attr(T.raw("sitio", "titulo")), descripcion=attr(T.raw("sitio", "descripcion")),
        logo=T.t("sitio", "logo"), logo_sub=T.t("sitio", "logo_sub"), boton_indice=T.t("sitio", "boton_indice"),
        titulo_indice=T.t("sitio", "titulo_indice"), filtros=FILTROS,

        acc_titulo=T.t("sitio", "boton_acc"), acc_noche=T.t("sitio", "modo_noche"), acc_cvd=T.t("sitio", "modo_daltonismo"))
    d.update(extra)
    return d

def construir():
    contenido = "\n\n".join([
        rail(), hero(), origen(), diagnostico(), promesa(), avance(), hub,
        lema("limpio"), calidad, lema("seguro"), inund, lema("vivo"), eco, lema("todos"), espacio,
        resumen(), participa(), fuentes(), pie()])
    return PLANTILLA % comun(logo_href="#top", idx_list=idx_list, contenido=contenido,
                             nav_href="historia.html", nav_texto=T.t("sitio", "boton_historia"))

def construir_historia():
    fin = ('<section class="hs-fin" data-nav="light"><a class="btn btn-dark" href="index.html#promesa">%s</a>'
           '<a class="hs-volver" href="index.html">%s</a></section>' % (T.t("historia-intro", "boton"), T.t("historia-intro", "volver")))
    return PLANTILLA % comun(titulo=attr("Historia del río Tula — " + T.raw("sitio", "titulo")), logo_href="index.html",
                             nav_href="index.html", nav_texto=T.t("sitio", "boton_proyecto"),
                             idx_list=idx_list_hist, contenido=historia_section() + fin + pie())

try:
    page = construir()
    page_historia = construir_historia()
except TextosError as e:
    sys.exit("\nERROR EN LOS TEXTOS: %s\n(index.html no se modificó.)\n" % e)

open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page)
open(os.path.join(ROOT, "historia.html"), "w", encoding="utf-8").write(page_historia)

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
