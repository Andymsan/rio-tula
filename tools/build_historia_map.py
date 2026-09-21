# -*- coding: utf-8 -*-
"""
Genera tools/fragmentos/historia.html (sección "Historia": mapa claro con nombres de
municipios + textos por época).

    python tools/build_historia_map.py

Entradas
  · municipios.geojson  (carpeta de diseño, UTM 14N, 58 municipios con NOMGEO)
  · capas históricas ya proyectadas al SVG (lago 1519, Tajo de Nochistongo, Gran Canal,
    túneles, presa Endhó, río Tula...) tomadas de tools/fragmentos/historia_capas.json
    (se extrajeron de la primera versión del mapa; no cambian).
Proyección: x = K*(E-E0), y = K*(N0-N)   (UTM 14N -> unidades SVG, viewBox 460x767)
"""
import json, os, re
from shapely.geometry import shape
from pyproj import Transformer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISEÑO = r"E:\03_Trabajo\01_SEMARNAT\01_rio tula\2026\01_riotula\diseño\geojson"
K, E0, N0 = 0.006566, 443196.0, 2234750.0

def P(e, n):
    return (K * (e - E0), K * (N0 - n))

to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32614", always_xy=True).transform
def LL(lon, lat):
    return P(*to_utm(lon, lat))

# ─── capas históricas ya proyectadas ───────────────────────────────────────
CAPAS = json.load(open(os.path.join(ROOT, "tools", "fragmentos", "historia_capas.json"), encoding="utf-8"))

# ─── municipios ────────────────────────────────────────────────────────────
mun = json.load(open(os.path.join(DISEÑO, "municipios.geojson"), encoding="utf-8"))
def ring_d(coords):
    return "M" + " L".join("%.1f,%.1f" % P(x, y) for x, y in coords) + " Z"

muni_paths, centros = [], {}
for f in mun["features"]:
    nm = f["properties"]["NOMGEO"]; ent = f["properties"]["CVE_ENT"]
    g = shape(f["geometry"]).simplify(110)
    polys = g.geoms if g.geom_type == "MultiPolygon" else [g]
    d = " ".join(ring_d(list(p.exterior.coords)) for p in polys if not p.is_empty)
    rp = shape(f["geometry"]).representative_point()
    centros[nm] = P(rp.x, rp.y)
    muni_paths.append('<path class="mun e%s" data-n="%s" d="%s"/>' % (ent, nm, d))

# ─── etiquetas: (texto, x, y, pasos donde se ve, tamaño) ──────────────────
def C(nm, dx=0, dy=0):
    x, y = centros[nm]; return (x + dx, y + dy)

zoc = LL(-99.1332, 19.4326)      # Zócalo, Ciudad de México
lab = []
def L(txt, xy, steps, size="m", cls=""):
    lab.append('<text class="lbl %s %s" data-show="%s" x="%.1f" y="%.1f">%s</text>' %
               (size, cls, " ".join(map(str, steps)), xy[0], xy[1], txt))

# estados (siempre)
L("HIDALGO", (250, 62), range(0, 9), "st", "estado")
L("ESTADO DE MÉXICO", (215, 380), range(0, 9), "st", "estado")
L("CIUDAD DE MÉXICO", (zoc[0] - 4, zoc[1] + 26), [0, 3, 5], "st", "estado")
# cuenca / lagos
L("Cuenca de México", (60, 470), [0], "s", "cuenca")
L("Lago de Texcoco", (346, 612), [0, 1, 3], "m", "agua")
L("Lago de Zumpango", (264, 296), [0, 2, 3], "s", "agua")
L("Tenochtitlan", (zoc[0] + 6, zoc[1] - 6), [1], "m", "hist")
L("Ciudad de México", (zoc[0] + 8, zoc[1] - 8), [3, 5], "m", "ciudad")
L("Texcoco", C("Texcoco", 6, 0), [1], "s", "lm")
L("Albarradón de Nezahualcóyotl", (zoc[0] + 22, zoc[1] + 66), [1], "s", "hist")
# municipios clave
L("Huehuetoca", C("Huehuetoca", -6, 12), [2, 5], "m", "lm")
L("Zumpango", C("Zumpango", 10, 8), [2, 3], "m", "lm")
L("Tequixquiac", C("Tequixquiac", -22, 4), [2, 3], "s", "lm")
L("Tula de Allende", C("Tula de Allende", -8, -14), [4, 6, 7, 8], "l", "lm key")
L("Atotonilco de Tula", C("Atotonilco de Tula", 14, 0), [5, 6, 8], "m", "lm key")
L("Tepeji del Río", C("Tepeji del Río de Ocampo", 0, 6), [5, 6], "s", "lm")
L("Tezontepec de Aldama", C("Tezontepec de Aldama", 14, -2), [4, 8], "s", "lm")
L("Tlaxcoapan", C("Tlaxcoapan", 12, 6), [4, 8], "s", "lm")
L("Tepetitlán", C("Tepetitlán", -18, -8), [4], "s", "lm")
L("Ecatepec", C("Ecatepec de Morelos", 30, -14), [3, 5], "s", "lm")
L("Valle del Mezquital", (70, 152), [4], "m", "hist")
# elementos
L("Presa Endhó", (141, 58), [4, 7, 8], "m", "agua")
L("Presa Requena", (176, 196), [6, 8], "s", "agua")
L("PTAR Atotonilco", (176, 179), [6, 8], "m", "ptar")
L("Gran Canal del Desagüe", (262, 470), [3], "m", "canal")
L("Tajo de Nochistongo", (200, 336), [2], "m", "tajo")
L("Emisor Central", (222, 410), [5], "m", "emisor")
L("Túnel Emisor Oriente", (325, 500), [5], "m", "teo")
L("río Tula", (188, 132), [4, 7, 8], "s", "rio")
L("Tula de Allende", (120, 118), [7], "l", "lm key")

# ─── textos de cada época (pasos) ─────────────────────────────────────────
PASOS = [
    ("~700,000 años atrás", "Una cuenca cerrada, lagos de sal",
     "La actividad volcánica de la Sierra de Chichinautzin cerró por el sur la cuenca de México y la convirtió en un sistema endorreico, sin salida al mar. Toda el agua de lluvia empezó a escurrir hacia el centro del valle, donde formó los grandes lagos que, al no tener drenaje natural, se volvieron salados por evaporación."),
    ("1449", "El dique de Nezahualcóyotl",
     "Tras una inundación que devastó Tenochtitlan —hoy la <strong>Ciudad de México</strong>—, el tlatoani de Texcoco, <strong>Nezahualcóyotl</strong>, construyó un albarradón de más de 12 km de piedra, madera y tierra para separar las aguas saladas del lago de Texcoco de las aguas dulces donde se asentaba la ciudad."),
    ("1607–1789", "El Tajo de Nochistongo",
     "Enrico Martínez abrió el primer desagüe artificial de la cuenca: un túnel en <strong>Huehuetoca</strong>, Estado de México, para desviar el agua desde <strong>Zumpango</strong> hacia el río Tula. Los colapsos sucesivos obligaron a rehacerlo como un corte abierto, terminado hasta <strong>1789 —182 años después de iniciado—</strong>, y que desde entonces conduce agua de lluvia y aguas negras hacia el Tula."),
    ("1900", "El Gran Canal del Desagüe",
     "El 17 de marzo de 1900, Porfirio Díaz inauguró el Gran Canal del Desagüe, que sale de la <strong>Ciudad de México</strong> y cruza <strong>Ecatepec, Zumpango y Tequixquiac</strong>. Con él se terminó de drenar lo que quedaba de los antiguos lagos, y toda el agua residual de la ciudad quedó encauzada, de forma permanente, hacia la cuenca del Tula."),
    ("1951", "La presa Endhó",
     "Entre <strong>Tepetitlán y Tula de Allende</strong>, en Hidalgo, se construyó la presa Endhó para almacenar agua de riego y convertir un valle semidesértico en zona agrícola: el <strong>Valle del Mezquital</strong>. Con los años empezaría a recibir, cada vez en mayor volumen, las aguas negras de la Ciudad de México."),
    ("1975 y 2019", "Los grandes túneles de drenaje",
     "El Emisor Central (1975) y, después, el <strong>Túnel Emisor Oriente</strong> —62 km de longitud y hasta 150 m³/s de capacidad, inaugurado en 2019— llevan el agua de la Ciudad de México hasta <strong>Atotonilco de Tula</strong> y multiplicaron el volumen de aguas negras y pluviales que se descarga hacia la cuenca del Tula."),
    ("2018", "La planta de Atotonilco",
     "En <strong>Atotonilco de Tula</strong>, Hidalgo, entra en operación la <strong>PTAR Atotonilco</strong>: la planta de tratamiento de aguas residuales más grande del mundo construida en una sola etapa, y la tercera con mayor capacidad de tratamiento a nivel mundial, pensada para reducir los riesgos sanitarios del riego con aguas sin tratar."),
    ("Septiembre de 2021", "Las inundaciones de Tula",
     "El desbordamiento de los ríos Tula y Rosas inunda la ciudad de <strong>Tula de Allende</strong>, Hidalgo. <strong>Más de 70,000 personas pierden su patrimonio y 17 mueren</strong> —14 de ellas en el Hospital del IMSS, cuando la energía eléctrica falló durante la emergencia."),
    ("2024–2030", "Comienza la restauración",
     "Recuperar el río Tula se vuelve prioridad nacional. Arranca el <strong>Plan de Saneamiento y Restauración del Río Tula 2024–2030</strong>: 37 proyectos para sanear el agua, prevenir inundaciones y restaurar los ecosistemas y el espacio público de un río que durante siglos absorbió el peso de una megaciudad."),
]
ERA_BANNER = ["Hace ~700 mil años", "1449", "1607–1789", "1900", "1951", "1975 y 2019", "2018", "2021", "2024–2030"]

def capa(cls, step, d, extra=""):
    return '<path class="%s" data-step="%s"%s d="%s"/>' % (cls, step, extra, d)

L_ = CAPAS
svg = ['<svg class="hmap" id="hmap" viewBox="0 0 460 767" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Mapa del Valle de México y el río Tula">']
svg.append('<g class="muns">' + "".join(muni_paths) + "</g>")
svg.append(capa("estados", 0, L_["estados"]))
svg.append(capa("cuenca", 0, L_["cuenca"]))
svg.append(capa("rivers", 0, L_["rivers"]))
svg.append(capa("waterbody", 0, L_["req"]))
svg.append(capa("waterbody", 0, L_["tax"]))
svg.append(capa("lake", 0, L_["lake"]))
svg.append(capa("endho", 4, L_["endho"]))
svg.append(capa("tulacity", 7, L_["tulacity"]))
svg.append(capa("dique", 1, L_["dique"], ' pathLength="1"'))
svg.append(capa("line noch", 2, L_["noch"], ' pathLength="1"'))
svg.append(capa("line canal", 3, L_["canal"], ' pathLength="1"'))
svg.append(capa("line emisor", 5, L_["teo1"], ' pathLength="1"'))
svg.append(capa("line teo", 5, L_["teo2"], ' pathLength="1"'))
svg.append(capa("riotula", 0, L_["riotula"], ' pathLength="1"'))
svg.append('<g class="marker zump" data-step="2"><circle class="ping" cx="258.8" cy="308.4" r="4"/><circle class="dot" cx="258.8" cy="308.4" r="3.6"/></g>')
svg.append('<g class="marker ptar" data-step="6"><circle class="ping" cx="170.5" cy="182.3" r="4"/><circle class="dot" cx="170.5" cy="182.3" r="3.8"/></g>')
svg.append('<g class="marker zoc" data-step="1"><circle class="ping" cx="%.1f" cy="%.1f" r="4"/><circle class="dot" cx="%.1f" cy="%.1f" r="3.6"/></g>' % (zoc[0], zoc[1], zoc[0], zoc[1]))
svg.append('<g class="labels">' + "".join(lab) + "</g>")
svg.append("</svg>")

ticks = [("0", "700 mil a.C."), ("14", "1449"), ("28", "1789"), ("42", "1900"), ("56", "1950"), ("75", "2000"), ("100", "hoy")]
ticks_html = "".join('<span class="hs-tick" style="left:%s%%">%s</span>' % t for t in ticks)

steps_html = ""
for i, (era, title, body) in enumerate(PASOS):
    steps_html += ('<article class="step hs-step" data-step="%d"><div class="card"><div class="tag">%s</div><h3>%s</h3><p>%s</p></div></article>'
                   % (i, era, title, body))

frag = '''<section class="s-historia" id="historia" data-nav="light">
  <div class="hs-intro-plain reveal">
    <span class="s-tag">01 · El río y su historia</span>
    <h2 class="s-title">700 mil años de una cuenca en transformación</h2>
    <p class="s-body">Antes de ser un colector de aguas negras, el Tula fue el desfogue de una de las cuencas más alteradas del planeta. Esta es la ruta —de los lagos prehispánicos a la restauración de hoy— que explica por qué.</p>
  </div>
  <div class="cap hist tema-azul" data-nav="light">
    <div class="cap-stage">
      %s
      <div class="banner" id="hsBanner">%s</div>
      <div class="hs-timeline">
        <div class="hs-timeline-here" id="hsHere">700 mil a.C.</div>
        <div class="hs-timeline-track"><div class="hs-timeline-fill" id="hsFill"></div><div class="hs-timeline-dot" id="hsDot"></div>%s</div>
      </div>
    </div>
    <div class="cap-steps" id="hsSteps">%s</div>
  </div>
</section>''' % ("".join(svg), ERA_BANNER[0], ticks_html, steps_html)

open(os.path.join(ROOT, "tools", "fragmentos", "historia.html"), "w", encoding="utf-8").write(frag)
print("historia.html:", len(frag) // 1024, "KB;", len(muni_paths), "municipios;", len(lab), "etiquetas")
for n in ("Tula de Allende", "Huehuetoca", "Zumpango", "Atotonilco de Tula"):
    print("  centro", n, "%.0f,%.0f" % centros[n])
print("  zocalo %.0f,%.0f" % zoc)
