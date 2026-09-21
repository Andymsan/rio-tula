# Río Tula 

Sitio del Plan de Saneamiento y Restauración del Río Tula (2024–2030).

| Página | Qué es |
|---|---|
| `index.html` | **Sitio de scroll (borrador v2027, todo en claro):** portada con índice → historia (mapa con municipios) → compromiso 92 → el proyecto (hexágonos) → calidad del agua → inundaciones → ecosistemas y espacio público |
| `mapa.html` | Visor interactivo (Leaflet). **Ya no se enlaza desde el sitio**: el scroll lo va a reemplazar. Se conserva en el repo por si se necesita. |
| `index-v1.html` | Versión anterior del scroll (respaldo) |

## Cómo verlo

- **`index.html`**: doble clic funciona.
- **`mapa.html`** (sin enlaces desde el sitio): necesita servidor local (los GeoJSON no cargan con doble clic). En VS Code → *Live Server*, o en la carpeta: `python -m http.server 8000` y abrir `http://localhost:8000`.

## Estructura

```
index.html            ← GENERADO por tools/build_index.py (no editar a mano)
css/   temas.css      ← colores por tema (rosa / naranja / verde) + flúor + "dato por confirmar"
       historia.css   ← mapa claro de la historia (municipios, obras, etiquetas, línea del tiempo)
       capitulos.css  ← nav, portada, compromiso 92, mapa-escenario, tarjetas, carrusel, hexágonos, pie
js/    sitio.js       ← cámara del mapa, capas, pines, carruseles, nav, índice
img/mapa/             ← renders de Blender ya convertidos a WebP (marcos, capas y burbujas)
img/fotos/            ← fotos de los proyectos (ver LEEME.md: se sustituyen por nombre de archivo)
img/ref/              ← fotos de referencia (parques inundables) y video de la animación
tools/ build_assets.py       ← renders de la carpeta de diseño → img/mapa/*.webp
       build_historia_map.py ← mapa de la historia (municipios + capas + textos por época)
       build_index.py        ← textos, datos, cámaras y pines → index.html
       fragmentos/           ← historia generada + capas históricas ya proyectadas
data/                 ← GeoJSON del visor (mapa.html)
```

## Flujo de trabajo

| Quiero… | Hago… |
|---|---|
| **Cambiar un texto o dato** | editar `tools/build_index.py` → `python tools/build_index.py` (la Historia: `tools/build_historia_map.py` y luego `build_index.py`) |
| **Poner una foto** | guardarla en `img/fotos/` con el nombre de `img/fotos/LEEME.md` (no hay que tocar código) |
| **Cambiar un render/capa** | reemplazar el PNG en la carpeta de diseño → `python tools/build_assets.py` |
| **Cambiar un color de tema** | `css/temas.css` (+ el filtro SVG de la capa en `tools/build_index.py`, variable `FILTROS`) |
| **Marcar un dato como pendiente** | envolverlo con `pend("…")` en `tools/build_index.py` (se ve amarillo). Por ahora **no se muestra ninguno**: los pendientes se quitaron del texto (ver `datos-tula.md`) |

## Documentos de trabajo

| Archivo | Para qué |
|---|---|
| `REDISENO-2027.md` | Decisiones, storyboard y estado del rediseño |
| `FLUJO-DE-TRABAJO.md` | Fases, checklist por escena y formatos de archivo |
| `datos-tula.md` | Cruce del Excel con el storyboard + **datos pendientes** |
| `datos-proyectos.xlsx` | Fuente de datos de proyectos 2025–2026 |
