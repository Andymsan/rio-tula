# -*- coding: utf-8 -*-
"""
Reduce el peso de las fotos de img/fotos/ para que el sitio cargue rápido:
lado mayor <= 1800 px y calidad 82 (JPEG) / optimizado (PNG, WebP).
Se usa solo con fotos grandes (> 700 KB o > 1800 px). Conserva nombre y extensión.

    python tools/optimizar_fotos.py            # todas las carpetas
    python tools/optimizar_fotos.py archivo    # una foto
"""
import os, sys
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS = os.path.join(ROOT, "img", "fotos")
MAX_LADO, MAX_BYTES = 1800, 700 * 1024
EXTS = (".jpg", ".jpeg", ".png", ".webp")


def optimizar(ruta):
    """Devuelve (bytes_antes, bytes_despues). No toca fotos que ya están livianas."""
    antes = os.path.getsize(ruta)
    with Image.open(ruta) as im:
        im = ImageOps.exif_transpose(im)
        grande = max(im.size) > MAX_LADO
        if antes <= MAX_BYTES and not grande:
            return antes, antes
        if grande:
            im.thumbnail((MAX_LADO, MAX_LADO), Image.LANCZOS)
        ext = os.path.splitext(ruta)[1].lower()
        tmp = ruta + ".tmp"
        if ext in (".jpg", ".jpeg"):
            im.convert("RGB").save(tmp, "JPEG", quality=82, optimize=True, progressive=True)
        elif ext == ".png":
            im.save(tmp, "PNG", optimize=True)
        else:
            im.save(tmp, "WEBP", quality=82, method=6)
    despues = os.path.getsize(tmp)
    if despues < antes:
        os.replace(tmp, ruta)
        return antes, despues
    os.remove(tmp)
    return antes, antes


def main():
    rutas = [sys.argv[1]] if len(sys.argv) > 1 else [
        os.path.join(d, f) for d, _, fs in os.walk(FOTOS) for f in fs if f.lower().endswith(EXTS)]
    total_a = total_d = 0
    for r in rutas:
        a, d = optimizar(r)
        total_a += a; total_d += d
        if d < a:
            print("%6.1f MB -> %5.2f MB  %s" % (a / 1e6, d / 1e6, os.path.relpath(r, ROOT)))
    print("Total: %.1f MB -> %.1f MB" % (total_a / 1e6, total_d / 1e6))


if __name__ == "__main__":
    main()
