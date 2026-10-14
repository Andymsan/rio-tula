# -*- coding: utf-8 -*-
"""
Dos gráficas de pastel (dona) interactivas: de dónde llega el agua al río Tula en secas y en lluvias.
Secas: caudales del diagrama (hoja "Sankey Tula calidad"): túneles 33.0, El Salto 1.2, Requena 0.1, Tlautla 0.3,
       otros (Cd. de Tula 0.2 + río Rosas 0.3 + Pemex 0.3) 0.8.
Lluvias: flujos máximos de la inundación de 2021 (lámina "Flujo máximo de tributarios", Conagua).
"""
import math

# nombre, color, secas (m³/s), lluvias 2021 (m³/s)
CATS = [
    ("Valle de México (túneles Central y Oriente)", "#3b3f46", 33.0, 209.0),
    ("Río El Salto", "#8a979d", 1.2, 91.0),
    ("Presa Requena", "#5fa8b8", 0.1, 100.0),
    ("Río Tlautla", "#025d6e", 0.3, 80.0),
    ("Otros afluentes y escurrimiento", "#cfc6b4", 0.8, 130.0),
]
R, SW = 78, 38
CIRC = 2 * math.pi * R

def _num(v, dec=None):
    if dec is None:
        dec = 1 if v < 100 else 0
    return ("%.*f" % (dec, v))

def donut(idx, titulo, nota):
    total = sum(c[idx] for c in CATS)
    segs, acc = [], 0.0
    for i, (nombre, color, *vals) in enumerate(CATS):
        v = vals[idx - 2]
        frac = v / total
        largo = max(frac * CIRC - 1.6, 0.4)
        segs.append('<circle class="dn-seg" r="%d" cx="0" cy="0" fill="none" stroke="%s" stroke-width="%d" '
                    'stroke-dasharray="%.2f %.2f" stroke-dashoffset="%.2f" data-n="%s" data-v="%s" data-p="%d" data-i="%d"/>'
                    % (R, color, SW, largo, CIRC - largo, -acc * CIRC, nombre, _num(v, 1 if idx == 2 else 0), round(frac * 100), i))
        acc += frac
    return ('<figure class="dn"><svg viewBox="-110 -110 220 220" role="img" aria-label="%s"><g transform="rotate(-90)">%s</g>'
            '<g class="dn-c"><text class="dn-v" y="2">%s</text><text class="dn-u" y="22">m³/s</text></g></svg>'
            '<figcaption><b>%s</b><span>%s</span></figcaption></figure>'
            % (titulo, "".join(segs), _num(total), titulo, nota)), total

def leyenda():
    filas = "".join('<li data-i="%d"><i style="background:%s"></i><span>%s</span><b>%s</b><b>%s</b></li>'
                    % (n, c[1], c[0], _num(c[2], 1), _num(c[3], 0)) for n, c in enumerate(CATS))
    return '<ul class="dn-ley"><li class="dn-h"><i></i><span></span><b>Secas</b><b>Lluvias</b></li>%s</ul>' % filas

def pastel(tit_secas, nota_secas, tit_lluvias, nota_lluvias):
    a, _ = donut(2, tit_secas, nota_secas)
    b, _ = donut(3, tit_lluvias, nota_lluvias)
    return '<div class="dn-wrap">%s%s%s</div>' % (a, leyenda(), b)
