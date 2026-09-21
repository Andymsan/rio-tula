# Río Tula — sitio de scroll + mapa interactivo

Sitio del Plan de Saneamiento y Restauración del Río Tula (2024–2030).

| Página | Qué es |
|---|---|
| `index.html` | **Sitio de scroll (borrador v2027):** historia → compromiso 92 → el proyecto → calidad del agua → inundaciones → ecosistemas y espacio público → cierre |
| `mapa.html` | Visor interactivo (Leaflet) con todas las capas y proyectos |
| `index-v1.html` | Versión anterior del scroll (respaldo) |

## Cómo verlo

- **`index.html`**: doble clic funciona.
- **`mapa.html`**: necesita servidor local (los GeoJSON no cargan con doble clic). En VS Code → *Live Server*, o en la carpeta: `python -m http.server 8000` y abrir `http://localhost:8000`.

## Estructura

```
index.html            ← GENERADO por tools/build_index.py (no editar a mano)
css/   temas.css      ← colores por tema (rosa / naranja / verde) + flúor + "dato por confirmar"
       historia.css   ← scroll oscuro de la historia
       capitulos.css  ← nav, portada, compromiso 92, mapa-escenario, tarjetas, carrusel, círculos, cierre
js/    sitio.js       ← cámara del mapa, capas, pines, carruseles, nav, índice
img/mapa/             ← renders de Blender ya convertidos a WebP (marcos, capas y burbujas)
img/fotos/            ← fotos de los proyectos (ver LEEME.md: se sustituyen por nombre de archivo)
img/ref/              ← fotos de referencia (parques inundables) y video de la animación
tools/ build_assets.py  ← renders de la carpeta de diseño → img/mapa/*.webp
       build_index.py   ← textos, datos, cámaras y pines → index.html
       fragmentos/      ← historia (SVG grande) reutilizada
data/                 ← GeoJSON del visor (mapa.html)
```

## Flujo de trabajo

| Quiero… | Hago… |
|---|---|
| **Cambiar un texto o dato** | editar `tools/build_index.py` → `python tools/build_index.py` |
| **Poner una foto** | guardarla en `img/fotos/` con el nombre de `img/fotos/LEEME.md` (no hay que tocar código) |
| **Cambiar un render/capa** | reemplazar el PNG en la carpeta de diseño → `python tools/build_assets.py` |
| **Cambiar un color de tema** | `css/temas.css` (+ el filtro SVG de la capa en `tools/build_index.py`, variable `FILTROS`) |
| **Marcar un dato como pendiente** | envolverlo con `pend("…")` en `tools/build_index.py` (se ve amarillo) |

## Documentos de trabajo

| Archivo | Para qué |
|---|---|
| `REDISENO-2027.md` | Decisiones, storyboard y estado del rediseño |
| `FLUJO-DE-TRABAJO.md` | Fases, checklist por escena y formatos de archivo |
| `datos-tula.md` | Cruce del Excel con el storyboard + **datos pendientes** |
| `datos-proyectos.xlsx` | Fuente de datos de proyectos 2025–2026 |
