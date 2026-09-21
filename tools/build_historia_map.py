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
L("Tula de Allende", C("Tula de Allende", -8, -14), [4, 6, 8], "l", "lm key")
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
    ("~700,000 años atrás", "Una cuenca sin salida",
     "Los volcanes del sur cerraron el Valle de México. La lluvia no tenía por dónde salir y formó grandes lagos. Como esa agua no corría hacia el mar, los lagos se volvieron salados."),
    ("1449", "El dique de Nezahualcóyotl",
     "Una inundación dejó a Tenochtitlan —hoy la <strong>Ciudad de México</strong>— bajo el agua. El tlatoani <strong>Nezahualcóyotl</strong> construyó un dique de más de 12 km. Separaba el agua salada del lago de Texcoco del agua dulce donde vivía la ciudad."),
    ("1607–1789", "El Tajo de Nochistongo",
     "Para proteger a la ciudad de las inundaciones, Enrico Martínez abrió en <strong>Huehuetoca</strong>, Estado de México, el primer desagüe artificial: un túnel que llevaba el agua desde la zona de <strong>Zumpango</strong> hacia el río Tula. Los derrumbes obligaron a rehacerlo como un corte abierto, que se terminó en <strong>1789</strong>, 182 años después. Desde entonces lleva agua de lluvia y aguas residuales hacia el Tula."),
    ("1900", "El Gran Canal del Desagüe",
     "El 17 de marzo de 1900 se inauguró el Gran Canal del Desagüe. Sale de la <strong>Ciudad de México</strong> y pasa por <strong>Ecatepec, Zumpango y Tequixquiac</strong>. Desde entonces, las aguas residuales de la ciudad salen del valle y llegan a la cuenca del Tula."),
    ("1951", "La presa Endhó",
     "Entre <strong>Tepetitlán y Tula de Allende</strong>, en Hidalgo, se construyó la presa Endhó para guardar agua de riego. Un valle seco se volvió zona de cultivo: el <strong>Valle del Mezquital</strong>. Con los años, la presa recibió cada vez más aguas residuales de la Ciudad de México."),
    ("1975 y 2019", "Los grandes túneles de drenaje",
     "En 1975 se inauguró el Emisor Central, y en 2019 el <strong>Túnel Emisor Oriente</strong>, de 62 km. Llevan el agua de la Ciudad de México hacia <strong>Atotonilco de Tula</strong>, en Hidalgo. Con ellos llegó más agua residual y de lluvia a la cuenca del Tula."),
    ("2018", "La planta de Atotonilco",
     "En <strong>Atotonilco de Tula</strong>, Hidalgo, empezó a funcionar la planta de tratamiento de aguas residuales (PTAR) de Atotonilco: la más grande del mundo construida en una sola etapa. Se hizo para reducir los riesgos para la salud de regar con agua sin tratar."),
    ("Septiembre de 2021", "La inundación de Tula",
     "En septiembre de 2021 se desbordaron los ríos Tula y Rosas, y el agua entró a la ciudad de <strong>Tula de Allende</strong>, Hidalgo. Más de 70 mil personas perdieron sus pertenencias. Fallecieron 17 personas, 14 de ellas en el hospital del IMSS, donde falló la energía eléctrica. Ninguna obra devuelve lo que se perdió. Por eso el plan busca reducir el riesgo para las familias de Tula."),
    ("2024–2030", "Comienza la restauración",
     "Recuperar el río Tula es hoy una prioridad nacional. Arranca el <strong>Plan de Saneamiento y Restauración del Río Tula 2024–2030</strong>, con 37 proyectos para mejorar la calidad del agua, reducir el riesgo de inundaciones y recuperar el río y sus orillas para quienes viven junto a él."),
]
ERA_BANNER = ["Hace ~700 mil años", "1449", "1607–1789", "1900", "1951", "1975 y 2019", "2018", "2021", "2024–2030"]

def capa(cls, step, d, extra=""):
    return '<path class="%s" data-step="%s"%s d="%s"/>' % (cls, step, extra, d)

L_ = CAPAS
svg = ['<svg class="hmap" id="hmap" viewBox="0 0 460 767" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Mapa del Valle de México y el río Tula">']
svg.append('<g class="muns">' + "".join(muni_paths) + "</g>")
svg.append(capa("humedales", 0, L_["humedales"]))
svg.append(capa("cuerpos", 0, L_["cuerpos"]))
svg.append(capa("tulanet", 0, L_["tulanet"]))
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
    <p class="s-body">Durante siglos, el río Tula recibió el agua que el Valle de México necesitaba sacar. Este recorrido cuenta cómo pasó y qué estamos haciendo hoy para cuidarlo.</p>
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
