# -*- coding: utf-8 -*-
"""
Convierte los renders de Blender/Photoshop de la carpeta de diseño en imágenes
web (WebP) dentro de img/mapa/.  Uso:

    python tools/build_assets.py                # usa la ruta por defecto
    python tools/build_assets.py --src "D:\ruta\espacio publico"

Requiere:  pip install pillow numpy
Regla: todos los marcos del mapa comparten la MISMA cámara (16:9), así que
las coordenadas de pines del sitio (0-1) sirven para todos.
"""
import argparse, os
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

DEF_SRC = r"E:\03_Trabajo\01_SEMARNAT\01_rio tula\2026\01_riotula\diseño\espacio publico"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "img", "mapa")

# Marcos opacos (fondo del mapa) -> ancho 3200 px
FRAMES = {
    "base.webp": "mapa base.png",           # ANP nueva + parque nacional, sin río
    "int.webp":  "mapa int.png",            # río + todas las intervenciones
    "acc.webp":  "mapa intervenciones.png", # + isócronas de 15 min a pie
    "col.webp":  "col.png",                 # vista amplia: colectores + PTAR Atotonilco
}
# Capas con transparencia (mismo encuadre que los marcos)
OVERLAYS = {
    "ov-rio.webp":        "rio.png",
    "ov-bojay.webp":      "bojay.png",
    "ov-rosas.webp":      "rosas.png",
    "ov-sanlorenzo.webp": "san lorenzo i.png",
    "ov-trescult.webp":   "tres culturas i.png",
    "ov-chamizal.webp":   "chamizal u.png",
    "ov-conect.webp":     "conectividad.png",
}
# Burbujas circulares de zoom (cuadradas con transparencia) -> 900 px
BUBBLES = {
    "z-bojay-zoom.webp":  "BOJAY ZOOM.png",
    "z-bojay-verde.webp": "BOJAY VERDE.png",
    "z-rosas.webp":       "RIO ROSAS.png",
    "z-sanlorenzo.webp":  "SAN LORENZO.png",
}

def save(im, name, w, alpha):
    im = im.convert("RGBA" if alpha else "RGB")
    h = round(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    p = os.path.join(OUT, name)
    if alpha:
        im.save(p, "WEBP", quality=88, alpha_quality=100, method=6)
    else:
        im.save(p, "WEBP", quality=80, method=6)
    print(f"{name:22} {im.size}  {os.path.getsize(p)//1024:5} KB")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=DEF_SRC)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    for out, src in FRAMES.items():
        save(Image.open(os.path.join(a.src, src)), out, 3200, False)
    for out, src in OVERLAYS.items():
        save(Image.open(os.path.join(a.src, src)), out, 3200, True)
    for out, src in BUBBLES.items():
        save(Image.open(os.path.join(a.src, src)), out, 900, True)

if __name__ == "__main__":
    main()
