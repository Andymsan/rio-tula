# Río Tula

Sitio del Plan de Saneamiento y Restauración del Río Tula (2024–2030).

| Página | Qué es |
|---|---|
| `index.html` | **Portada corta (landing, ~8 pantallas):** portada con video y Participa → de dónde viene el agua (con mapa de ubicación) → fotos de diagnóstico → compromiso 92 → ya está en marcha → tira de fotos de obra → la solución (cuatro mensajes con foto) → participa → fuentes |
| `proyecto.html` | **Por proyecto:** los cuatro mensajes proyecto por proyecto, con mapa fijo, fotos y avance, y el resumen de cinco metas |
| `historia.html` | **Historia del río** (mapa por épocas) |
| `actores.html` | **Quiénes participan:** instituciones y comunidades (datos de `## actores` en TEXTOS.md; Ariel: revisar) |
| `mapa.html` | Visor interactivo (Leaflet). No se enlaza desde el sitio; se conserva por si se necesita. |

## Cómo verlo

- **`index.html`**: doble clic funciona.
- **`mapa.html`** (sin enlaces desde el sitio): necesita servidor local (los GeoJSON no cargan con doble clic). En VS Code → *Live Server*, o en la carpeta: `python -m http.server 8000` y abrir `http://localhost:8000`.

## Estructura

```
index.html, proyecto.html, historia.html, actores.html ← GENERADOS (no editar a mano): TEXTOS.md + tools/build_index.py
TEXTOS.md             ← TODOS LOS TEXTOS de la página (se editan aquí, en GitHub)
COMENTARIOS.md        ← comentarios de revisión sobre el sitio (se reemplaza en cada ronda)
DATOS.md              ← cifras de referencia, fuentes y datos pendientes de confirmar
.github/workflows/    ← reconstruye index.html solo cuando cambia TEXTOS.md
css/   temas.css      ← colores por tema (rosa / naranja / verde / azul) + flúor + "dato por confirmar"
       historia.css   ← mapa claro de la historia (municipios, obras, etiquetas, línea del tiempo)
       capitulos.css  ← nav, portada, compromiso 92, escenarios, tarjetas, carrusel, resumen, participa
js/    sitio.js       ← cámara del mapa, capas, pines, carruseles, lightbox, resumen, nav, índice
img/mapa/             ← renders de Blender ya convertidos a WebP (marcos, capas y burbujas)
img/fotos/            ← fotos de los proyectos (ver LEEME.md: una carpeta por sección)
img/ref/              ← fotos de referencia (parques inundables)
tools/ build_assets.py       ← renders de la carpeta de diseño → img/mapa/*.webp
       build_historia_map.py ← el mapa de la historia (municipios + capas); necesita la carpeta de diseño
       textos.py             ← lee TEXTOS.md y convierte las marcas (**negrita**, ==resaltado==)
       build_index.py        ← textos, datos, cámaras y pines → index.html
       fragmentos/           ← historia_mapa.html (mapa generado) + capas históricas ya proyectadas
data/                 ← GeoJSON del visor (mapa.html)
```

## Flujo de trabajo

| Quiero… | Hago… |
|---|---|
| **Cambiar un texto** | editar `TEXTOS.md` en GitHub. La página se reconstruye sola. |
| **Cambiar qué imagen/zoom/pines lleva un paso** | editar `tools/build_index.py` y correr `python tools/build_index.py` |
| **Cambiar el mapa de la historia** | `python tools/build_historia_map.py` (necesita la carpeta de diseño) y subir `historia_mapa.html` |
| **Poner una foto** | guardarla en `img/fotos/<id-de-sección>/` con el nombre `<orden>_<pie de foto>.<ext>` (ver `img/fotos/LEEME.md`), **o** subirla a la carpeta de Drive (se trae sola cada 15 min, ver abajo) |
| **Cambiar un render/capa** | reemplazar el PNG en la carpeta de diseño → `python tools/build_assets.py` |
| **Cambiar un color de tema** | `css/temas.css` (+ el filtro SVG de la capa en `tools/build_index.py`, variable `FILTROS`) |
| **Marcar un dato como pendiente** | envolverlo con `pend("…")` en `tools/build_index.py` (se ve amarillo) |

## Fotos desde Google Drive

Una carpeta de Drive recibe las fotos con el nombre `<sección>_<orden>_<pie de foto>.ext`
(por ejemplo `ecosistemas-3_1_Puma encontrado en una ADVC - 2026.jpg`). Cada 15 minutos,
`.github/workflows/sync-fotos.yml` corre `tools/sync_fotos_drive.py`, que trae las fotos
nuevas a `img/fotos/<sección>/` y reconstruye el sitio si hizo falta. Necesita dos secretos
del repositorio (Settings → Secrets and variables → Actions):
- `GDRIVE_SA_KEY`: el JSON de una cuenta de servicio de Google con acceso de lectura a esa carpeta.
- `GDRIVE_FOLDER_ID`: el id de la carpeta de Drive (la parte de la URL después de `/folders/`).

## Nombres de las fotos en Drive

`<sección>_<orden>_<pie de foto>` (el número de orden es opcional). Se puede dejar en cualquier subcarpeta de "Imágenes en carrusel".

| Dónde sale | Prefijo del nombre |
|---|---|
| Diagnóstico (fotos grandes) | `diagnostico_1_…` |
| Compromiso 92 | `promesa-1_…` |
| Calidad del agua | `calidad-1_…` a `calidad-4_…` |
| Inundaciones | `inundaciones-1_…` a `inundaciones-3_…` |
| Ecosistemas | `ecosistemas-1_…` a `ecosistemas-3_…` |
| Espacio público | `ecosistemas-4_…` |
| Participa | `participa_…` |

## Video de la portada

Un video en cualquier subcarpeta de Drive con nombre `portada_1_<descripción>` (mov o mp4) se convierte solo a un MP4 liviano
(1280 px, sin audio, máximo 20 s; y una versión de 640 px para celular) y se usa de fondo de la portada, con la imagen fija como respaldo. Si no hay uno con ese
prefijo, se usa el primer video `diagnostico_…`. No se reproduce con ahorro de datos, conexión lenta o "reducir movimiento".

## Otros

- `datos-proyectos.xlsx`: fuente de datos de proyectos 2025–2026.
- Capas geográficas que aún no se pueden agregar con precisión (industrias, estaciones de
  monitoreo, cárcamo de bombeo, vía del tren, topografía) están listadas en `DATOS.md`.


## Estructura de la página (nov 2026)

- **Participa** aparece en el menú de todas las páginas (abre un panel con los 4 enlaces), en la portada, en el cierre de cada página y, en celular, como barra inferior.
- **Glosario:** en `TEXTOS.md`, `[[término::definición]]` muestra la definición al tocar el término.
- **Estilo:** `css/sistema.css` se carga al final y concentra el sistema de diseño (5 estilos de texto, un acento, un color de acción) y el diseño propio de celular (texto plegado con "Leer más", barra Participa, tarjetas apiladas).
- **Fotos de la tira "Así se ve hoy" y de las tarjetas de "La solución":** salen solas de las carpetas de `img/fotos/` (la primera foto de cada una).
