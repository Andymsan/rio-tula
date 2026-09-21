# -*- coding: utf-8 -*-
"""
Genera tools/fragmentos/historia_mapa.html: el MAPA SVG de la Historia (municipios con nombres,
obras, etiquetas). Los TEXTOS de cada época ya no están aquí: viven en TEXTOS.md.
Este script sólo se corre en la computadora de Andrea (usa los datos de la carpeta de diseño);
el resultado (historia_mapa.html) se sube al repositorio.

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

open(os.path.join(ROOT, "tools", "fragmentos", "historia_mapa.html"), "w", encoding="utf-8").write("".join(svg))
print("historia_mapa.html:", sum(len(x) for x in svg) // 1024, "KB;", len(muni_paths), "municipios;", len(lab), "etiquetas")
for n in ("Tula de Allende", "Huehuetoca", "Zumpango", "Atotonilco de Tula"):
    print("  centro", n, "%.0f,%.0f" % centros[n])
print("  zocalo %.0f,%.0f" % zoc)
