# -*- coding: utf-8 -*-
"""
Diagrama de Sankey de caudales (m³/s) del río Tula, coloreado por calidad (DBO, mg/L).
Datos: hoja "Sankey Tula calidad" (TEC & TEO, El Salto, Portal de Salida, Atotonilco,
DR-003, río Tula) + afluentes de la lámina de caudales (Requena, Tlautla, Cd. Tula,
río Rosas, Pemex). Donde no hay DBO el flujo va en gris ("sin dato").
"""

W, H, NW, K = 1180, 500, 14, 8.2     # ancho, alto, ancho de nodo, px por m³/s
COLX = [175, 365, 570, 790, 965]

# id: (nombre, columna, y superior)
NODOS = {
    "salto":   ("El Salto", 0, 40),
    "tec":     ("TEC y TEO", 0, 70),
    "portal":  ("Portal de Salida", 1, 60),
    "ptar":    ("PTAR Atotonilco", 2, 190),
    "dr3":     ("Agricultura · distrito de riego 003", 3, 262),
    "perd":    ("Pérdidas en la planta", 3, 218),
    "rio":     ("Río Tula", 3, 30),
    "requena": ("Presa Requena", 3, 104),
    "tlautla": ("Río Tlautla", 3, 128),
    "cdtula":  ("Cd. de Tula", 3, 152),
    "rosas":   ("Río Rosas", 3, 176),
    "pemex":   ("Pemex", 3, 200),
    "final":   ("Río Tula, hacia Endhó", 4, 30),
}

# origen, destino, caudal (m³/s, estiaje 2021-2024, "Aprovechamientos y caudales.xlsx"), DBO (None = sin dato)
# Portal = TEC y TEO 33.0 + El Salto 1.17 = 34.17.  Planta: recibe 32.07 y entrega 26.29 a riego, 4.78 al río y pierde 1.0.
FLUJOS = [
    ("tec", "portal", 33.0, 150), ("salto", "portal", 1.1718, 50),
    ("portal", "ptar", 32.0718, 150), ("portal", "rio", 2.1, 100),
    ("ptar", "dr3", 26.28996, 50), ("ptar", "rio", 4.78184, 100), ("ptar", "perd", 1.0, None),
    ("rio", "final", 6.88184, 50), ("requena", "final", 0.0748, 20),
    ("tlautla", "final", 0.3292, None), ("cdtula", "final", 0.172, None),
    ("rosas", "final", 0.32537, None), ("pemex", "final", 0.3, None),
]

def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))

def color(dbo):
    if dbo is None:
        return "#b4bcc0"
    verde, ambar, rojo = (106, 168, 79), (233, 196, 106), (200, 85, 61)
    if dbo <= 50:
        c = verde
    elif dbo <= 100:
        c = _lerp(verde, ambar, (dbo - 50) / 50)
    else:
        c = _lerp(ambar, rojo, min(1, (dbo - 100) / 50))
    return "#%02x%02x%02x" % c

def _fmt(v):
    return ("%.2f" % v) if v < 1 else ("%.1f" % v)

def svg(modo=""):
    val = {k: 0.0 for k in NODOS}
    for o, d, q, _ in FLUJOS:
        val[o] = max(val[o], sum(f[2] for f in FLUJOS if f[0] == o))
        val[d] = max(val[d], sum(f[2] for f in FLUJOS if f[1] == d))
    alto = {k: max(val[k] * K, 3) for k in NODOS}
    cy = {k: NODOS[k][2] + alto[k] / 2 for k in NODOS}
    x = {k: COLX[NODOS[k][1]] for k in NODOS}

    # posiciones dentro de cada nodo (salidas ordenadas por el destino, entradas por el origen)
    sal = {k: NODOS[k][2] for k in NODOS}
    ent = {k: NODOS[k][2] for k in NODOS}
    orden_sal = sorted(range(len(FLUJOS)), key=lambda i: (FLUJOS[i][0], cy[FLUJOS[i][1]]))
    orden_ent = sorted(range(len(FLUJOS)), key=lambda i: (FLUJOS[i][1], cy[FLUJOS[i][0]]))
    ys, yt = {}, {}
    for i in orden_sal:
        o, d, q, _ = FLUJOS[i]
        ys[i] = sal[o]; sal[o] += max(q * K, 1.6)
    for i in orden_ent:
        o, d, q, _ = FLUJOS[i]
        yt[i] = ent[d]; ent[d] += max(q * K, 1.6)

    azul = modo == "mode-va"
    out = ['<svg class="sankey %s" viewBox="0 0 %d %d" role="img" '
           'aria-label="Caudales del río Tula, coloreados por calidad del agua">' % (modo, W, H)]
    for i, (o, d, q, dbo) in enumerate(FLUJOS):
        t = max(q * K, 1.6)
        x0, x1 = x[o] + NW, x[d]
        xm = (x0 + x1) / 2
        p = ("M%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f L%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f Z"
             % (x0, ys[i], xm, ys[i], xm, yt[i], x1, yt[i], x1, yt[i] + t, xm, yt[i] + t, xm, ys[i] + t, x0, ys[i] + t))
        tip = "%s → %s|%s m³/s|%s" % (NODOS[o][0], NODOS[d][0], _fmt(q), "" if azul else (("DBO %d mg/L" % dbo) if dbo else "Sin dato de DBO"))
        out.append('<path class="sk-l" d="%s" fill="%s" data-tip="%s" data-o="%s" data-d="%s" data-dbo="%s"/>' % (p, "#3f93ab" if azul else color(dbo), tip, o, d, dbo if dbo else ""))
    for k, (nombre, col, y0) in NODOS.items():
        out.append('<rect class="sk-n" x="%d" y="%.1f" width="%d" height="%.1f"/>' % (x[k], y0, NW, alto[k]))
        v = _fmt(val[k]) + " m³/s"
        grande = k in ("tec", "portal", "ptar", "dr3", "rio", "final")
        if NODOS[k][1] == 0:
            out.append('<text class="sk-t%s" x="%d" y="%.1f" text-anchor="end"><tspan>%s</tspan><tspan class="v" x="%d" dy="15">%s</tspan></text>'
                       % (" b" if grande else "", x[k] - 8, cy[k] - (2 if grande else 0), nombre, x[k] - 8, v))
        elif k in ("requena", "tlautla", "cdtula", "rosas", "pemex", "perd"):
            out.append('<text class="sk-t s" x="%d" y="%.1f" dominant-baseline="middle">%s · %s</text>' % (x[k] + NW + 6, cy[k], nombre, v))
        elif k == "dr3":
            out.append('<text class="sk-t b" x="%d" y="%.1f"><tspan>%s</tspan><tspan class="v" x="%d" dy="15">%s · va a riego</tspan></text>'
                       % (x[k] + NW + 8, cy[k] - 4, nombre, x[k] + NW + 8, v))
        elif k == "final":
            out.append('<text class="sk-t b" x="%d" y="%.1f"><tspan>%s</tspan><tspan class="v" x="%d" dy="15">%s</tspan></text>'
                       % (x[k] + NW + 8, cy[k] - 4, nombre, x[k] + NW + 8, v))
        else:
            out.append('<text class="sk-t b" x="%d" y="%.1f"><tspan>%s</tspan><tspan class="v" x="%d" dy="15">%s</tspan></text>'
                       % (x[k], NODOS[k][2] - 26, nombre, x[k], v))
    out.append("</svg>")
    return "".join(out)

def leyenda():
    paradas = ", ".join("%s %d%%" % (color(v), p) for v, p in ((20, 0), (50, 23), (100, 62), (150, 100)))
    return ('<div class="sk-ley"><span class="sk-esc"><span class="sk-grad" style="background:linear-gradient(90deg,%s)"></span>'
            '<span class="sk-ticks"><b>20</b><b>50</b><b>100</b><b>150 mg/L</b></span></span>'
            '<span class="sk-nd"><i style="background:%s"></i>sin dato</span></div>' % (paradas, color(None)))
