# Río Tula

Sitio del Plan de Saneamiento y Restauración del Río Tula (2024–2030).

| Página | Qué es |
|---|---|
| `index.html` | **Sitio de scroll (borrador, todo en claro):** portada con índice → historia (mapa con municipios) → compromiso 92 → el proyecto → calidad del agua → inundaciones → ecosistemas y espacio público → resumen (mapa con las 5 metas) → participa |
| `mapa.html` | Visor interactivo (Leaflet). No se enlaza desde el sitio; se conserva por si se necesita. |

## Cómo verlo

- **`index.html`**: doble clic funciona.
- **`mapa.html`** (sin enlaces desde el sitio): necesita servidor local (los GeoJSON no cargan con doble clic). En VS Code → *Live Server*, o en la carpeta: `python -m http.server 8000` y abrir `http://localhost:8000`.

## Estructura

```
index.html            ← GENERADO (no editar a mano): TEXTOS.md + tools/build_index.py
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

## Otros

- `datos-proyectos.xlsx`: fuente de datos de proyectos 2025–2026.
- Capas geográficas que aún no se pueden agregar con precisión (industrias, estaciones de
  monitoreo, cárcamo de bombeo, vía del tren, topografía) están listadas en `DATOS.md`.
