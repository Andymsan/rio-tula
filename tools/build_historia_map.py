# -*- coding: utf-8 -*-
"""
Genera tools/fragmentos/historia_mapa.html: el MAPA SVG de la Historia (obras,
etiquetas, ríos). Los TEXTOS de cada época viven en TEXTOS.md.
Este script sólo se corre en la computadora de Andrea (usa los datos de la carpeta de diseño);
el resultado (historia_mapa.html) se sube al repositorio.

    python tools/build_historia_map.py

Entradas
  · municipios.geojson  (carpeta de diseño, UTM 14N) — SOLO para ubicar etiquetas de lugares
    con precisión (su centroide). Ya NO se dibujan los polígonos/límites municipales.
  · capas históricas ya proyectadas al SVG (lago 1519, Tajo de Nochistongo, Gran Canal,
    túneles, presa Endhó, río Tula...) tomadas de tools/fragmentos/historia_capas.json
    (se extrajeron de la primera versión del mapa; no cambian).
Proyección: x = K*(E-E0), y = K*(N0-N)   (UTM 14N -> unidades SVG, viewBox 460x767)

Comentarios de Ariel aplicados (24-sep-2026):
  · Se quitan las divisiones municipales (siguen usándose sólo para ubicar etiquetas)
    y las capas "modernas" (humedales/cuerpos/red actuales) — el mapa histórico ya no las usa.
  · El Túnel Emisor Poniente (1962) aparece conectado hacia Cuautitlán (ruta aproximada:
    Vaso del Cristo → Barrientos → Cuautitlán; ver fuentes en REDISENO-2027.md).
  · Se agregan Lago de Xochimilco, y los puntos Iztapalapa/Azcapotzalco del dique de
    Nezahualcóyotl.
  · El "lago" se suaviza con Chaikin (2 pasadas) para que no se vea con esquinas de polígono.
  · El zoom por época se quitó (ver H_CAM en js/sitio.js: una sola cámara fija).
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

# ─── municipios: SOLO para ubicar etiquetas (ya no se dibujan sus límites) ─
mun = json.load(open(os.path.join(DISEÑO, "municipios.geojson"), encoding="utf-8"))
centros = {}
for f in mun["features"]:
    rp = shape(f["geometry"]).representative_point()
    centros[f["properties"]["NOMGEO"]] = P(rp.x, rp.y)

def C(nm, dx=0, dy=0):
    x, y = centros[nm]
    return (x + dx, y + dy)

# ─── suavizado de esquinas (Chaikin corner-cutting) ────────────────────────
def _chaikin(pts, closed, it=2):
    for _ in range(it):
        n = len(pts)
        if n < 3:
            return pts
        nxt = []
        rng = range(n) if closed else range(n - 1)
        for i in rng:
            p0, p1 = pts[i], pts[(i + 1) % n]
            nxt.append((0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]))
            nxt.append((0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1]))
        pts = ([pts[0]] + nxt + [pts[-1]]) if not closed else nxt
    return pts

def smooth_path(d, it=2):
    """Suaviza cada subtrazo (M...L...[Z]) de un path con Chaikin."""
    out = []
    for sub in re.findall(r'M[^M]*', d):
        closed = bool(re.search(r'Z\s*$', sub))
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', sub)]
        pts = [(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]
        pts = _chaikin(pts, closed, it)
        s = "M" + " L".join("%.2f,%.2f" % p for p in pts)
        if closed:
            s += " Z"
        out.append(s)
    return " ".join(out)

CAPAS["lake"] = smooth_path(CAPAS["lake"])

# ─── etiquetas: (texto, x, y, pasos donde se ve, tamaño) ──────────────────
lab = []
def L(txt, xy, steps, size="m", cls=""):
    lab.append('<text class="lbl %s %s" data-show="%s" x="%.1f" y="%.1f">%s</text>' %
               (size, cls, " ".join(map(str, steps)), xy[0], xy[1], txt))

def punto(xy, step):
    return '<circle class="hito" data-step="%d" cx="%.1f" cy="%.1f" r="2.6"/>' % (step, xy[0], xy[1])

zoc = LL(-99.1332, 19.4326)           # Zócalo, Ciudad de México (antes Tenochtitlan)
iztapalapa = LL(-99.0930, 19.3552)    # extremo sur del dique de Nezahualcóyotl
azcapotzalco = LL(-99.1868, 19.4837)  # extremo norte del dique
xochimilco = LL(-99.1029, 19.2647)    # Lago de Xochimilco

# ruta aproximada del Túnel Emisor Poniente (1962): Vaso del Cristo -> Barrientos -> Cuautitlán
tep_pts = [LL(-99.263, 19.480), LL(-99.211, 19.529), LL(-99.196, 19.677)]
tep_path = "M" + " L".join("%.1f,%.1f" % p for p in tep_pts)

# estados (siempre)
L("HIDALGO", (250, 62), range(0, 9), "st", "estado")
L("ESTADO DE MÉXICO", (215, 380), range(0, 9), "st", "estado")
L("CIUDAD DE MÉXICO", (zoc[0] - 4, zoc[1] + 26), [0, 3, 5], "st", "estado")
# cuenca / lagos
L("Cuenca de México", (60, 470), [0], "s", "cuenca")
L("Lago de Texcoco", (346, 612), [0, 1, 3], "m", "agua")
L("Lago de Zumpango", C("Zumpango", 1, -18), [0, 2, 3], "s", "agua")
L("Lago de Xochimilco", xochimilco, [0, 1, 3], "s", "agua")
L("Tenochtitlan", (zoc[0] + 6, zoc[1] - 6), [1], "m", "hist")
L("Ciudad de México", (zoc[0] + 8, zoc[1] - 8), [3, 5], "m", "ciudad")
L("Albarradón de Nezahualcóyotl", (zoc[0] + 22, zoc[1] + 66), [1], "s", "hist")
L("Iztapalapa", (iztapalapa[0] + 6, iztapalapa[1] + 2), [1], "s", "lm")
L("Azcapotzalco", (azcapotzalco[0] - 8, azcapotzalco[1] - 6), [1], "s", "lm")
# lugares clave
L("Huehuetoca", C("Huehuetoca", -6, 12), [2, 5], "m", "lm")
L("Zumpango", C("Zumpango", 10, 8), [2, 3], "m", "lm")
L("Tequixquiac", C("Tequixquiac", -22, 4), [2, 3], "s", "lm")
L("Cuautitlán", (tep_pts[2][0] + 6, tep_pts[2][1] + 4), [5], "s", "lm")
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
L("Túnel Emisor Poniente", (tep_pts[1][0] + 10, tep_pts[1][1] - 8), [5], "s", "emisor")
L("Emisor Central", (222, 410), [5], "m", "emisor")
L("Túnel Emisor Oriente", (325, 500), [5], "m", "teo")
L("río Tula", (188, 132), [4, 7, 8], "s", "rio")
L("río Rosas", (150, 158), [7], "s", "rio")
L("Tula de Allende", (120, 118), [7], "l", "lm key")

def capa(cls, step, d, extra=""):
    return '<path class="%s" data-step="%s"%s d="%s"/>' % (cls, step, extra, d)

L_ = CAPAS
svg = ['<svg class="hmap" id="hmap" viewBox="0 0 460 767" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Mapa del Valle de México y el río Tula">']
svg.append(capa("estados", 0, L_["estados"]))
svg.append(capa("cuenca", 0, L_["cuenca"]))
svg.append(capa("rivers", 0, L_["rivers"]))
svg.append(capa("waterbody", 0, L_["req"]))
svg.append(capa("waterbody", 0, L_["tax"]))
svg.append(capa("lake", 0, L_["lake"]))
svg.append(capa("endho", 4, L_["endho"]))
svg.append(capa("tulacity", 7, L_["tulacity"]))
svg.append(capa("dique", 1, L_["dique"], ' pathLength="1"'))
svg.append(punto(iztapalapa, 1))
svg.append(punto(azcapotzalco, 1))
svg.append(capa("line noch", 2, L_["noch"], ' pathLength="1"'))
svg.append(capa("line canal", 3, L_["canal"], ' pathLength="1"'))
svg.append(capa("line tep", 5, tep_path, ' pathLength="1"'))
svg.append(capa("line emisor", 5, L_["teo1"], ' pathLength="1"'))
svg.append(capa("line teo", 5, L_["teo2"], ' pathLength="1"'))
svg.append(capa("riotula", 0, L_["riotula"], ' pathLength="1"'))
svg.append('<g class="marker zump" data-step="2"><circle class="ping" cx="258.8" cy="308.4" r="4"/><circle class="dot" cx="258.8" cy="308.4" r="3.6"/></g>')
svg.append('<g class="marker enfasis" id="hsEnfasis"><circle class="ping" cx="0" cy="0" r="4"/><circle class="dot" cx="0" cy="0" r="3.6"/></g>')
svg.append('<g class="labels">' + "".join(lab) + "</g>")
svg.append("</svg>")

open(os.path.join(ROOT, "tools", "fragmentos", "historia_mapa.html"), "w", encoding="utf-8").write("".join(svg))
print("historia_mapa.html:", sum(len(x) for x in svg) // 1024, "KB;", len(lab), "etiquetas")
print("  zocalo %.0f,%.0f" % zoc, " iztapalapa %.0f,%.0f" % iztapalapa, " azcapotzalco %.0f,%.0f" % azcapotzalco)
for n in ("Tula de Allende", "Huehuetoca", "Zumpango", "Atotonilco de Tula"):
    print("  centro", n, "%.0f,%.0f" % centros[n])
print("  marcador de énfasis: Tula de Allende %.0f,%.0f  ·  PTAR Atotonilco 170.5,182.3" % centros["Tula de Allende"])
