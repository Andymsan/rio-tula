# Saneamiento y restauración del río Tula
## Dashboard interactivo — Guía de configuración

---

## 📁 Estructura del proyecto

```
rio-tula/
├── index.html          ← Abre esto en el navegador (con Live Server)
├── css/
│   └── styles.css      ← Estilos (tipografía, layout, tooltips)
├── js/
│   ├── config.js       ← 23 proyectos, metas, capas, videos
│   ├── sidebar.js      ← Lógica del panel izquierdo
│   └── map.js          ← Leaflet, capas GeoJSON, popups
├── data/               ← Archivos GeoJSON (ya convertidos a WGS84)
│   ├── colectores.geojson
│   ├── atotonilco.geojson
│   ├── cfe.geojson
│   ├── pemex.geojson
│   ├── estaciones.geojson
│   ├── centro.geojson
│   ├── industrias.geojson
│   └── monitoreo.geojson
└── videos/             ← Coloca aquí tus videos antes/después
    ├── antesx2.mp4     ← Ejemplo
    └── despuesx2.mp4   ← Ejemplo
```

---

## 🚀 Cómo abrir el proyecto

1. Abre la carpeta `rio-tula/` en **VSCode**
2. Instala la extensión **Live Server** (si no la tienes)
3. Click derecho en `index.html` → **"Open with Live Server"**
4. Se abre en `http://127.0.0.1:5500`

> ⚠️ **No** abras `index.html` con doble clic (file://) — los GeoJSON
> no cargarán por restricciones de seguridad del navegador.

---

## 🎬 Agregar videos a los tooltips

En `js/config.js`, cada proyecto tiene una propiedad `media: []`.
Para agregar videos antes/después:

```js
media: [
  { label: 'ANTES',   src: 'videos/proyecto_antes.mp4'  },
  { label: 'DESPUÉS', src: 'videos/proyecto_despues.mp4' },
],
```

Los videos se muestran en un carrusel dentro del tooltip al hacer
clic en el marcador en el mapa.

---

## 🗺️ Agregar nuevas capas GeoJSON

1. Coloca el archivo `.geojson` en la carpeta `data/`
   - Asegúrate de que esté en **WGS84 (EPSG:4326)**
2. En `js/map.js`, dentro de `loadAllLayers()`, agrega la carga:
   ```js
   loadPoint('mi_capa', makeLabel('Mi etiqueta', '#color')),
   ```
   O para líneas, sigue el patrón de `loadColectores()`.
3. En `js/config.js`, en el proyecto correspondiente, agrega la clave
   a su array `layers`:
   ```js
   layers: ['colTula', 'mi_capa'],
   ```

---

## 🎨 Cambiar el mapa base

En `js/map.js`, línea ~40, modifica la URL del tile:

```js
// CartoDB Voyager (actual — cálido, elegante)
'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'

// CartoDB Positron (más claro, casi blanco)
'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'

// OpenStreetMap (más detallado)
'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
```

---

## ✏️ Modificar proyectos

Todo el contenido está en `js/config.js`:
- Agregar/quitar proyectos dentro de cada `proyectos: []`
- Editar descripciones, indicadores (kv), años, estatus
- Agregar metas nuevas dentro de cada `metas: []`
- Los ejes son: `agua`, `inund`, `eco`

---

## 📐 Dimensiones del layout

| Elemento    | Ancho       | Alto     |
|-------------|-------------|----------|
| Panel       | 636 px      | 100vh    |
| Mapa        | flex: 1     | 100vh    |

Para ajustar el ancho del panel, edita en `css/styles.css`:
```css
:root { --panel-w: 636px; }
```
