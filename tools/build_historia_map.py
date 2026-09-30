# -*- coding: utf-8 -*-
"""
Genera tools/fragmentos/historia_mapa.html (el mapa SVG de la Historia) y
img/mapa/hillshade.webp (relieve de fondo) a partir de capas GIS reales.
Sólo se corre en la computadora de Andrea (usa los datos de la carpeta de
diseño); los resultados (historia_mapa.html, hillshade.webp) se suben al
repositorio.

    python tools/build_historia_map.py

Entradas (carpeta de diseño, todas en UTM 14N salvo donde se indica)
  geojson/municipios.geojson        — sólo para ubicar etiquetas (centroide)
  geojson/edomex.geojson, hidalgo.geojson, cdmx.geojson   — límites estatales reales
  geojson/gran cuenca del valle de mexico.geojson         — límite de la cuenca
  geojson/delimitacion.geojson      — las 5 subcuencas del proyecto del río Tula
                                       (Cuautitlán, Presa Requena, Presa Endhó,
                                       Salado, Tula)
  geojson/lago de texcoco.geojson   — extensión histórica del lago
  geojson/cuerpos de agua.geojson   — Endhó, Requena, Taxhimay (con nombre)
  geojson/tula.geojson              — red de ríos/escurrimientos (tipo SIATL)
  geojson/red valle de mexico.geojson — Gran Canal, Emisor Poniente/Central,
                                         Túnel Emisor Oriente (trazo real)
  geojson/tajo de nochistongo.geojson — trazo real del Tajo
  geojson/distritos de riego.geojson — en lon/lat (CRS84); se reproyecta
  tif/srtm.tif                       — DEM (EPSG:4326) para el hillshade

Proyección: x = K*(E-E0), y = K*(N0-N)  (UTM 14N -> unidades SVG).
El encuadre (E0, N0, K) se calcula a partir del DEM, de forma que cubra
cómodamente las 5 subcuencas del proyecto (ver DELIM_BBOX abajo).
"""
import json, os, re
import numpy as np
from PIL import Image
from shapely.geometry import shape, box
from shapely.ops import transform as shp_transform
from pyproj import Transformer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISENO = r"E:\03_Trabajo\01_SEMARNAT\01_rio tula\2026\01_riotula\diseño\geojson"
TIF = r"E:\03_Trabajo\01_SEMARNAT\01_rio tula\2026\01_riotula\diseño\tif\srtm.tif"

# ─── proyección: encuadre calculado a partir del DEM reproyectado ──────────
E0, N0 = 428560.2, 2242443.8
K = 0.0065
W_SVG = round((513430.2 - E0) * K, 1)
H_SVG = round((N0 - 2145693.8) * K, 1)

def P(e, n):
    return (K * (e - E0), K * (N0 - n))

to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32614", always_xy=True).transform
def LL(lon, lat):
    return P(*to_utm(lon, lat))

def load(fn):
    return json.load(open(os.path.join(DISENO, fn), encoding="utf-8"))

# ─── hillshade: DEM (EPSG:4326) -> UTM14N -> relieve suave en PNG/WebP ─────
def build_hillshade():
    import rasterio
    from rasterio.warp import calculate_default_transform, reproject, Resampling
    with rasterio.open(TIF) as src:
        transform, width, height = calculate_default_transform(
            src.crs, "EPSG:32614", src.width, src.height, *src.bounds, resolution=90)
        dem = np.zeros((height, width), dtype=np.float32)
        reproject(
            source=rasterio.band(src, 1), destination=dem,
            src_transform=src.transform, src_crs=src.crs,
            dst_transform=transform, dst_crs="EPSG:32614",
            resampling=Resampling.bilinear, src_nodata=src.nodata, dst_nodata=np.nan,
        )
    valid = ~np.isnan(dem)
    dem_f = np.where(valid, dem, np.nanmedian(dem))
    # margen (reflejando el borde) para que el fondo nunca se corte en pantallas muy anchas/angostas
    pad = max(width, height) // 2
    dem_f = np.pad(dem_f, pad, mode="reflect")
    gy, gx = np.gradient(dem_f, 90.0)
    slope = np.pi / 2 - np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    az, alt = np.deg2rad(315), np.deg2rad(45)
    shade = np.clip(np.sin(alt) * np.sin(slope) + np.cos(alt) * np.cos(slope) * np.cos(az - aspect), 0, 1)
    lo, hi = 222, 255
    gray = (lo + shade * (hi - lo)).astype(np.uint8)
    rgb = np.stack([gray, gray, gray], axis=-1)  # gris neutro (igual que el mapa de referencia)
    img = Image.fromarray(rgb, "RGB")
    out_dir = os.path.join(ROOT, "img", "mapa")
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, "hillshade.webp"), "WEBP", quality=82, method=6)
    # bounds del raster reproyectado (con el margen agregado), en unidades SVG
    left, top = transform.c - pad * transform.a, transform.f - pad * transform.e
    right, bottom = left + transform.a * (width + 2 * pad), top + transform.e * (height + 2 * pad)
    x0, y0 = P(left, top)
    x1, y1 = P(right, bottom)
    print("hillshade.webp: %dx%d px -> svg x[%.1f,%.1f] y[%.1f,%.1f]" % (width, height, x0, x1, y0, y1))
    return x0, y0, x1 - x0, y1 - y0

HS_X, HS_Y, HS_W, HS_H = build_hillshade()

# ─── geojson -> path SVG ────────────────────────────────────────────────────
VIEW_BOX_PAD = 150000  # margen (m) generoso: que el borde del recorte no se vea ni con la cámara más abierta
CLIPBOX = box(E0 - VIEW_BOX_PAD, N0 - H_SVG / K - VIEW_BOX_PAD, E0 + W_SVG / K + VIEW_BOX_PAD, N0 + VIEW_BOX_PAD)

def _ring(coords, close):
    pts = [P(c[0], c[1]) for c in coords]
    s = "M" + " L".join("%.2f,%.2f" % p for p in pts)
    return s + " Z" if close else s

def path_d(geom):
    gt = geom.geom_type
    if gt == "Polygon":
        parts = [_ring(list(geom.exterior.coords), True)]
        parts += [_ring(list(r.coords), True) for r in geom.interiors]
        return " ".join(parts)
    if gt == "MultiPolygon":
        parts = []
        for poly in geom.geoms:
            parts.append(_ring(list(poly.exterior.coords), True))
            parts += [_ring(list(r.coords), True) for r in poly.interiors]
        return " ".join(parts)
    if gt == "LineString":
        return _ring(list(geom.coords), False)
    if gt == "MultiLineString":
        return " ".join(_ring(list(ls.coords), False) for ls in geom.geoms)
    if gt == "GeometryCollection":
        return " ".join(path_d(g) for g in geom.geoms if not g.is_empty)
    return ""

def feature_geoms(fc, simplify_m=0, clip=False):
    out = []
    for f in fc["features"]:
        g = f.get("geometry")
        if not g or not g.get("coordinates"):
            continue
        geom = shape(g)
        if clip:
            geom = geom.intersection(CLIPBOX)
            if geom.is_empty:
                continue
        if simplify_m:
            geom = geom.simplify(simplify_m, preserve_topology=True)
        out.append((geom, f.get("properties", {})))
    return out

def layer_path(fn, simplify_m=0, clip=False):
    geoms = feature_geoms(load(fn), simplify_m, clip)
    return " ".join(path_d(g) for g, _ in geoms)

# ─── municipios: para ubicar etiquetas, y el polígono real de Tula de Allende ─
mun = load("municipios.geojson")
centros = {}
tulacity_geom = None
for f in mun["features"]:
    nombre = f["properties"]["NOMGEO"]
    geom = shape(f["geometry"])
    centros[nombre] = P(geom.representative_point().x, geom.representative_point().y)
    if nombre == "Tula de Allende":
        tulacity_geom = geom.simplify(15, preserve_topology=True)
d_tulacity = path_d(tulacity_geom) if tulacity_geom else ""

def C(nm, dx=0, dy=0):
    x, y = centros[nm]
    return (x + dx, y + dy)

def mid_of(fn, name_field, name_value, prop_key="Name"):
    """Punto medio (a lo largo de la línea) de la feature con name_field==name_value."""
    for f in load(fn)["features"]:
        if f["properties"].get(prop_key) == name_value:
            g = shape(f["geometry"])
            m = g.interpolate(0.5, normalized=True)
            return P(m.x, m.y)
    raise KeyError(name_value)

def centroid_of(fn, prop_key, value):
    for f in load(fn)["features"]:
        if f["properties"].get(prop_key) == value:
            g = shape(f["geometry"])
            c = g.centroid
            return P(c.x, c.y)
    raise KeyError(value)

# ─── suavizado de esquinas (Chaikin corner-cutting), para el lago ──────────
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
    out = []
    for sub in re.findall(r'M[^M]*', d):
        closed = bool(re.search(r'Z\s*$', sub))
        nums = [float(x) for x in re.findall(r'-?\d+\.?\d*', sub)]
        pts = [(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]
        pts = _chaikin(pts, closed, it)
        s = "M" + " L".join("%.2f,%.2f" % p for p in pts)
        out.append(s + (" Z" if closed else ""))
    return " ".join(out)

def prepend_point(d, xy):
    nums = re.findall(r'-?\d+\.?\d*', d)
    resto = " L".join("%s,%s" % (nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2))
    return "M%.1f,%.1f L%s" % (xy[0], xy[1], resto)

# ─── distritos de riego: viene en lon/lat (CRS84) -> reproyectar. Solo los 3
# que tocan la cuenca del Tula (003 Tula, 100 Alfajayucan, 112 Ajacuba); cada
# uno con su color y su canal principal (dr<clave>_pr.geojson).
DISTRITOS_COLOR = {"003": "#d17b3f", "100": "#7a6bb0", "112": "#b8577a"}

def distritos_riego():
    fc = load("distritos de riego.geojson")
    to_utm14 = Transformer.from_crs("EPSG:4326", "EPSG:32614", always_xy=True).transform
    out = {}
    for f in fc["features"]:
        clave = f["properties"]["clvdr"]
        if clave not in DISTRITOS_COLOR:
            continue
        g = shp_transform(to_utm14, shape(f["geometry"]))
        g = g.intersection(CLIPBOX)
        if g.is_empty:
            continue
        g = g.simplify(30, preserve_topology=True)
        out[clave] = {"path": path_d(g), "centro": P(*g.centroid.coords[0])}
    return out

def canal_principal_path(clave):
    return layer_path("dr%s_pr.geojson" % clave, simplify_m=10, clip=True)

# ══════════════════════════════════════════════════════════════════════════
#  CAPAS
# ══════════════════════════════════════════════════════════════════════════
d_edomex = layer_path("edomex.geojson", simplify_m=40)
d_hidalgo = layer_path("hidalgo.geojson", simplify_m=40)
d_cdmx = layer_path("cdmx.geojson", simplify_m=25)
d_cuenca = layer_path("gran cuenca del valle de mexico.geojson", simplify_m=15)
d_delim = layer_path("delimitacion.geojson", simplify_m=15)
d_lake = layer_path("lago de texcoco.geojson", simplify_m=20, clip=True)
d_lake = smooth_path(d_lake, it=1)
d_rivers = layer_path("tula.geojson", simplify_m=10)
# el/los tramo(s) del río que cruzan Tula de Allende (para resaltar "río restaurado" en la época 8)
_riotula_buf = tulacity_geom.buffer(2500) if tulacity_geom else None
_riotula_parts = [path_d(g.simplify(10, preserve_topology=True))
                  for g, _ in feature_geoms(load("tula.geojson"))
                  if _riotula_buf is not None and g.intersects(_riotula_buf)]
d_riotula = " ".join(_riotula_parts)
d_presas = layer_path("presas.geojson", simplify_m=8, clip=True)
d_humedales = layer_path("humedales.geojson", simplify_m=8, clip=True)
DISTRITOS = distritos_riego()
for _clv in DISTRITOS:
    DISTRITOS[_clv]["canal"] = canal_principal_path(_clv)

# cuerpos de agua con nombre (Endhó, Requena, Taxhimay)
_cuerpos = feature_geoms(load("cuerpos de agua.geojson"))
_cuerpos_by_name = {p["nombre"]: g for g, p in _cuerpos}
d_endho = path_d(_cuerpos_by_name["Endho"])
d_requena = path_d(_cuerpos_by_name["Requena"])
d_taxhimay = path_d(_cuerpos_by_name["Taxhimay"])
endho_c = P(*_cuerpos_by_name["Endho"].centroid.coords[0])
requena_c = P(*_cuerpos_by_name["Requena"].centroid.coords[0])

# manzanas de la ciudad de Tula (para el acercamiento de la inundación de 2021)
_manzanas_buf = tulacity_geom.buffer(1800) if tulacity_geom else None
_manzanas_parts = [path_d(g.simplify(3, preserve_topology=True))
                   for g, _ in feature_geoms(load("manzanas.geojson"))
                   if _manzanas_buf is not None and g.intersects(_manzanas_buf)]
d_manzanas = " ".join(_manzanas_parts)

# planta de tratamiento de Atotonilco (polígono real)
_atot_geom = feature_geoms(load("atotonilco.geojson"))[0][0]
d_atotonilco = path_d(_atot_geom)
atot_c = P(*_atot_geom.centroid.coords[0])

# red valle de méxico: Gran Canal (+2), Emisor Poniente/Central, Túnel Emisor Oriente
_red = {p["Name"]: g for g, p in feature_geoms(load("red valle de mexico.geojson"))}
d_canal = path_d(_red["Gran Canal"]) + " " + path_d(_red["Gran Canal 2"])
d_tep = path_d(_red["Emisor Poniente"])
d_teo1 = path_d(_red["Emisor Central"])
d_teo2 = path_d(_red["Tunel Emisor Oriente"])
canal_mid = _red["Gran Canal"].interpolate(0.5, normalized=True)
canal_mid = P(canal_mid.x, canal_mid.y)
tep_mid = _red["Emisor Poniente"].interpolate(0.6, normalized=True)
tep_mid = P(tep_mid.x, tep_mid.y)
teo1_mid = _red["Emisor Central"].interpolate(0.5, normalized=True)
teo1_mid = P(teo1_mid.x, teo1_mid.y)
teo2_mid = _red["Tunel Emisor Oriente"].interpolate(0.5, normalized=True)
teo2_mid = P(teo2_mid.x, teo2_mid.y)

# tajo de nochistongo: trazo real, completo (la feature larga y detallada;
# trae un pequeño defecto de digitalización al inicio -dos puntos de más que
# regresan sobre sí mismos-, se quitan esos dos puntos).
_tajo_coords = [f["geometry"]["coordinates"] for f in load("tajo de nochistongo.geojson")["features"]
                if f.get("geometry") and f["geometry"].get("coordinates")][1]
_tajo_coords = [_tajo_coords[1]] + _tajo_coords[3:]
_tajo_geom = shape({"type": "LineString", "coordinates": _tajo_coords})
d_tajo = path_d(_tajo_geom)
tajo_mid = _tajo_geom.interpolate(0.5, normalized=True)
tajo_mid = P(tajo_mid.x, tajo_mid.y)

# conectar el tajo con Zumpango (marcador manual, ver ZUMPANGO_MARKER)
zumpango_c = C("Zumpango")
d_tajo = prepend_point(d_tajo, zumpango_c)

# ─── puntos de referencia (lon/lat) ─────────────────────────────────────────
zoc = LL(-99.1332, 19.4326)            # Zócalo, Ciudad de México (antes Tenochtitlan)
iztapalapa = LL(-99.0930, 19.3552)     # extremo sur del dique de Nezahualcóyotl
atzacoalco = LL(-99.1050, 19.4900)     # extremo norte del dique (hacia Ecatepec)
dique_bend = LL(-99.1180, 19.4450)     # quiebre del dique junto a la ciudad
d_dique = "M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f" % (
    iztapalapa[0], iztapalapa[1], dique_bend[0], dique_bend[1], atzacoalco[0], atzacoalco[1])

# ══════════════════════════════════════════════════════════════════════════
#  ETIQUETAS
# ══════════════════════════════════════════════════════════════════════════
lab = []
def L(txt, xy, steps, size="m", cls=""):
    lab.append('<text class="lbl %s %s" data-show="%s" x="%.1f" y="%.1f">%s</text>' %
               (size, cls, " ".join(map(str, steps)), xy[0], xy[1], txt))

def punto(xy, step):
    return '<circle class="hito" data-step="%d" cx="%.1f" cy="%.1f" r="2.6"/>' % (step, xy[0], xy[1])

def tenochtitlan(xy, step):
    x, y = xy
    return (
        '<g class="tenoch" data-step="%d">'
        '<circle class="tenoch-agua" cx="%.1f" cy="%.1f" r="5.2"/>'
        '<path class="tenoch-calz" d="M%.1f,%.1f l0,-5 M%.1f,%.1f l0,5 M%.1f,%.1f l-5,0 M%.1f,%.1f l5,0"/>'
        '<circle class="tenoch-isla" cx="%.1f" cy="%.1f" r="3"/>'
        '</g>'
    ) % (step, x, y, x, y, x, y, x, y, x, y, x, y)

# estados (siempre, salvo en los pasos donde estorban)
L("HIDALGO", (W_SVG * 0.62, H_SVG * 0.12), [i for i in range(9) if i not in (5, 6, 7)], "s", "estado")
L("ESTADO DE MÉXICO", (W_SVG * 0.4, H_SVG * 0.72), [i for i in range(9) if i not in (4, 5, 6, 7)], "s", "estado")
L("CIUDAD DE MÉXICO", (zoc[0] - 4, zoc[1] + 26), [i for i in range(9) if i not in (4, 5, 6, 7)], "s", "estado")
# cuenca / lagos
L("Cuenca del Valle de México", (W_SVG * 0.1, H_SVG * 0.66), [0, 1, 2, 3], "s", "cuenca")
L("Cuenca del río Tula", (endho_c[0] - 40, endho_c[1] - 18), [i for i in range(9) if i not in (0, 1, 2, 3)], "s", "delim")
L("Lago de Texcoco", (zoc[0] - 30, zoc[1] + 16), [0, 1], "m", "agua")
L("Lago de Zumpango", C("Zumpango", -6, -22), [0, 2], "s", "agua")
L("Tenochtitlan", (zoc[0] + 6, zoc[1] - 6), [1], "m", "hist")
L("Ciudad de México", (zoc[0] + 8, zoc[1] - 8), [3], "m", "ciudad")
L("Albarradón de Nezahualcóyotl", (zoc[0] + 22, zoc[1] + 66), [1], "s", "hist")
# lugares clave
L("Huehuetoca", C("Huehuetoca", -6, 12), [2], "m", "lm")
L("Zumpango", C("Zumpango", 10, 14), [2, 3], "s", "lm")
L("Tequixquiac", C("Tequixquiac", -22, 4), [2, 3], "s", "lm")
L("Tula de Allende", C("Tula de Allende", -8, -14), [8], "l", "lm key")
L("Atotonilco de Tula", C("Atotonilco de Tula", 34, 6), [8], "m", "lm key")
L("Tezontepec de Aldama", C("Tezontepec de Aldama", 14, 12), [8], "s", "lm")
L("Tlaxcoapan", C("Tlaxcoapan", 12, 6), [8], "s", "lm")
L("Tepetitlán", C("Tepetitlán", -18, -8), [4], "s", "lm")
L("Ecatepec", C("Ecatepec de Morelos", 30, -14), [3], "s", "lm")
L("Valle del Mezquital", (endho_c[0] - 32, endho_c[1] + 46), [4], "m", "hist")
for _clv, _d in DISTRITOS.items():
    lab.append('<text class="lbl s distritodr" data-show="4" x="%.1f" y="%.1f" style="fill:%s">DR %s</text>'
               % (_d["centro"][0], _d["centro"][1], DISTRITOS_COLOR[_clv], _clv))
# elementos (posiciones tomadas de la geometría real)
L("Presa Endhó", (endho_c[0] + 8, endho_c[1] - 6), [4, 8], "m", "agua")
L("Presa Requena", (requena_c[0] - 8, requena_c[1] + 18), [8], "s", "agua")
L("PTAR Atotonilco", (atot_c[0] + 10, atot_c[1] - 2), [6, 8], "m", "ptar")
L("Gran Canal del Desagüe", (canal_mid[0] + 8, canal_mid[1]), [3], "m", "canal")
L("Tajo de Nochistongo", (tajo_mid[0] - 34, tajo_mid[1] - 20), [2], "s", "tajo")
L("Túnel Emisor Poniente", (tep_mid[0] - 46, tep_mid[1] - 14), [5], "s", "tep")
L("Emisor Central", (teo1_mid[0] - 10, teo1_mid[1] - 26), [5], "s", "teo")
L("Túnel Emisor Oriente", (teo2_mid[0] + 10, teo2_mid[1] + 18), [5], "s", "teo")
L("río Tula", (requena_c[0] - 55, requena_c[1] - 45), [i for i in range(9) if i not in (0, 1)], "s", "rio")
L("Tula de Allende", C("Tula de Allende", -8, -14), [7], "l", "lm key")

# ══════════════════════════════════════════════════════════════════════════
#  ENSAMBLE DEL SVG
# ══════════════════════════════════════════════════════════════════════════
def capa(cls, step, d, extra=""):
    return '<path class="%s" data-step="%s"%s d="%s"/>' % (cls, step, extra, d)

svg = ['<svg class="hmap" id="hmap" viewBox="0 0 %.1f %.1f" preserveAspectRatio="xMidYMid meet" '
       'role="img" aria-label="Mapa del Valle de México y el río Tula">' % (W_SVG, H_SVG)]
svg.append('<image class="hillshade" href="img/mapa/hillshade.webp" x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
           'preserveAspectRatio="none"/>' % (HS_X, HS_Y, HS_W, HS_H))
svg.append(capa("delim", 0, d_delim))
svg.append(capa("cuenca", 0, d_cuenca))
svg.append(capa("estados", 0, d_edomex + " " + d_hidalgo + " " + d_cdmx))
svg.append(capa("humedal", 0, d_humedales))
svg.append(capa("waterbody", 0, d_presas))
svg.append(capa("waterbody", 0, d_taxhimay))
svg.append(capa("rivers", 0, d_rivers))
svg.append(capa("lake", 0, d_lake))
svg.append(capa("endho", 4, d_endho))
svg.append(capa("waterbody", 4, d_requena))
svg.append(capa("endho", 6, d_atotonilco))
for _clv, _d in DISTRITOS.items():
    svg.append(capa("distritos", 4, _d["path"], ' style="fill:%s33;stroke:%s"' % (DISTRITOS_COLOR[_clv], DISTRITOS_COLOR[_clv])))
    svg.append(capa("line canaldr", 4, _d["canal"], ' pathLength="1" style="stroke:%s"' % DISTRITOS_COLOR[_clv]))
svg.append(capa("riotula", 0, d_riotula, ' pathLength="1"'))
svg.append(capa("tulacity", 8, d_tulacity))  # ciudad restaurada; en 2021 (paso 7) solo resalta el punto que pulsa
svg.append(capa("manzanas", 7, d_manzanas))  # manzanas de la ciudad; solo visibles en el acercamiento de la inundación

svg.append(capa("dique", 1, d_dique, ' pathLength="1"'))
svg.append(punto(iztapalapa, 1))
svg.append(punto(atzacoalco, 1))
svg.append(capa("line noch", 2, d_tajo, ' pathLength="1"'))
svg.append(capa("line canal", 3, d_canal, ' pathLength="1"'))
svg.append(capa("line tep", 5, d_tep, ' pathLength="1"'))
svg.append(capa("line emisor", 5, d_teo1, ' pathLength="1"'))
svg.append(capa("line teo", 5, d_teo2, ' pathLength="1"'))
svg.append(tenochtitlan(zoc, 1))
svg.append('<g class="marker zump" data-step="2"><circle class="ping" cx="%.1f" cy="%.1f" r="4"/>'
           '<circle class="dot" cx="%.1f" cy="%.1f" r="3.6"/></g>' % (zumpango_c[0], zumpango_c[1], zumpango_c[0], zumpango_c[1]))
svg.append('<g class="marker enfasis" id="hsEnfasis"><circle class="ping" cx="0" cy="0" r="4"/><circle class="dot" cx="0" cy="0" r="3.6"/></g>')
svg.append('<g class="labels">' + "".join(lab) + "</g>")
svg.append("</svg>")

open(os.path.join(ROOT, "tools", "fragmentos", "historia_mapa.html"), "w", encoding="utf-8").write("".join(svg))
print("historia_mapa.html: %d KB; %d etiquetas" % (sum(len(x) for x in svg) // 1024, len(lab)))
print("viewBox: 0 0 %.1f %.1f" % (W_SVG, H_SVG))
print("zocalo %.0f,%.0f  endho %.0f,%.0f  requena %.0f,%.0f" % (zoc[0], zoc[1], endho_c[0], endho_c[1], requena_c[0], requena_c[1]))
print("tula de allende:", C("Tula de Allende"))
print("iztapalapa %.0f,%.0f  atzacoalco %.0f,%.0f  zumpango %.0f,%.0f" % (iztapalapa[0], iztapalapa[1], atzacoalco[0], atzacoalco[1], zumpango_c[0], zumpango_c[1]))
print("tajo_mid %.0f,%.0f  canal_mid %.0f,%.0f" % (tajo_mid[0], tajo_mid[1], canal_mid[0], canal_mid[1]))
print("tep_mid %.0f,%.0f  teo1_mid %.0f,%.0f  teo2_mid %.0f,%.0f" % (tep_mid[0], tep_mid[1], teo1_mid[0], teo1_mid[1], teo2_mid[0], teo2_mid[1]))
print("atot_c %.0f,%.0f  manzanas: %d features, %d KB" % (atot_c[0], atot_c[1], len(_manzanas_parts), len(d_manzanas)//1024))
