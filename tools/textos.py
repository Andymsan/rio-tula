# -*- coding: utf-8 -*-
"""
Lee TEXTOS.md (los textos del sitio) y los convierte a HTML.

Formato de TEXTOS.md
  ## nombre-de-la-seccion   (comentario opcional)
  campo: valor en UNA sola línea

Marcas dentro de un texto
  **negrita**      →  <strong>
  ==resaltado==    →  <mark class="fluor"> (color del tema)
  *cursiva*        →  <em>
  [texto](https://enlace)  →  enlace

Si algo falta o está mal escrito, se detiene con un mensaje en español que dice qué y dónde.
"""
import html
import re


class TextosError(Exception):
    pass


def fmt(t):
    """Convierte las marcas de TEXTOS.md a HTML (escapando lo demás)."""
    t = html.escape(t, quote=False)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'==(.+?)==', r'<mark class="fluor">\1</mark>', t)
    t = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', t)
    return t


def attr(t):
    """Texto plano seguro para usar dentro de un atributo HTML."""
    return html.escape(re.sub(r'[*=]{1,2}', '', t), quote=True)


class Textos:
    def __init__(self, ruta):
        self.ruta = ruta
        self.s = {}
        actual = None
        with open(ruta, encoding="utf-8") as f:
            for n, linea in enumerate(f.read().splitlines(), 1):
                m = re.match(r'^##\s+([a-z0-9-]+)', linea)
                if m:
                    actual = m.group(1)
                    if actual in self.s:
                        raise TextosError('TEXTOS.md, línea %d: la sección "%s" está repetida.' % (n, actual))
                    self.s[actual] = {"_linea": n}
                    continue
                if actual is None:
                    continue
                m = re.match(r'^([a-z0-9_]+):\s?(.*)$', linea)
                if m:
                    k, v = m.group(1), m.group(2).strip()
                    if k in self.s[actual]:
                        raise TextosError('TEXTOS.md, línea %d: el campo "%s" está repetido en "%s".' % (n, k, actual))
                    self.s[actual][k] = v

    # ── acceso ──
    def sec(self, id_):
        if id_ not in self.s:
            raise TextosError('Falta la sección "## %s" en TEXTOS.md.' % id_)
        return self.s[id_]

    def raw(self, id_, campo, requerido=True):
        d = self.sec(id_)
        v = d.get(campo)
        if v is None or v == "":
            if requerido:
                raise TextosError('En la sección "## %s" (TEXTOS.md, línea %d) falta el campo "%s:".' % (id_, d["_linea"], campo))
            return None
        return v

    def t(self, id_, campo, requerido=True):
        v = self.raw(id_, campo, requerido)
        return fmt(v) if v is not None else None

    def lista(self, id_, campo, esperado=None, requerido=True):
        """Campo con varios valores separados por | ."""
        v = self.raw(id_, campo, requerido)
        if v is None:
            return []
        items = [x.strip() for x in v.split("|") if x.strip()]
        if esperado is not None and len(items) != esperado:
            d = self.sec(id_)
            raise TextosError('En "## %s" (línea %d), el campo "%s:" debe tener %d elementos separados por | y tiene %d.'
                              % (id_, d["_linea"], campo, esperado, len(items)))
        return items
