# -*- coding: utf-8 -*-
"""
Cuenta las inspecciones industriales de la hoja de Google (compartida "cualquier persona con el enlace
puede ver") y guarda el resultado en data/inspecciones.json. El sitio lo lee al reconstruirse
(token {inspecciones} en TEXTOS.md). Solo se guardan totales: no se publican nombres de empresas.

    python tools/sync_inspecciones.py

Sale con código 0 y escribe "cambio=1" / "cambio=0" en $GITHUB_OUTPUT.
"""
import csv, datetime, io, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(ROOT, "data", "inspecciones.json")
HOJA = os.environ.get("INSPECCIONES_SHEET_ID", "1aaqsHs3xAtrVIQmVXabr_3ztkAK2HrWH87sQvr9Du2w")
URL = "https://docs.google.com/spreadsheets/d/%s/export?format=csv" % HOJA


def contar():
    req = urllib.request.Request(URL, headers={"User-Agent": "rio-tula-sync"})
    with urllib.request.urlopen(req, timeout=60) as r:
        texto = r.read().decode("utf-8")
    filas = list(csv.DictReader(io.StringIO(texto)))
    if not filas or "Año de inspección" not in filas[0]:
        raise SystemExit("La hoja no tiene la columna 'Año de inspección': ¿cambió el formato?")
    inspeccionadas = [f for f in filas if (f.get("Año de inspección") or "").strip()]
    por_anio = {}
    for f in inspeccionadas:
        a = f["Año de inspección"].strip()
        por_anio[a] = por_anio.get(a, 0) + 1
    return {"total": len(inspeccionadas), "por_anio": dict(sorted(por_anio.items()))}


def main():
    nuevo = contar()
    anterior = {}
    if os.path.exists(SALIDA):
        anterior = json.load(open(SALIDA, encoding="utf-8"))
    cambio = (anterior.get("total"), anterior.get("por_anio")) != (nuevo["total"], nuevo["por_anio"])
    if cambio:
        nuevo["actualizado"] = datetime.date.today().isoformat()
        os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
        json.dump(nuevo, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("Inspecciones: %s -> %s" % (anterior.get("total"), nuevo["total"]))
    else:
        print("Sin cambios (%s inspecciones)." % nuevo["total"])
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write("cambio=%s\n" % ("1" if cambio else "0"))


if __name__ == "__main__":
    main()
