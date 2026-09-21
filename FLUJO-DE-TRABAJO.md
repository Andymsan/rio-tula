# Flujo de trabajo — Rediseño Río Tula (v2027)

> Guía para no perder nada. Andrea diseña en **InDesign**, formato **1920×1080**.
> Claude integra al sitio, reconfigura el código y mantiene los pendientes.

---

## 1. Reparto de tareas

| Andrea | Claude |
|---|---|
| Define el **layout** (desktop + móvil) | Traduce el layout a HTML/CSS |
| Diseña cada escena en InDesign | Integra cada escena al scroll |
| Exporta **capas** (PNG/JPG/RGBA) | Apila capas, aplica temas de color |
| Pasa **textos** aparte (no dentro de la imagen) | Maqueta textos como texto real |
| Confirma los **datos pendientes** | Rellena datos y actualiza `datos-tula.md` |
| Renderiza en Blender | Encadena frames con el scroll |

---

## 2. Orden recomendado (por fases)

### Fase 0 — Base *(hecho)*
- [x] Insumos guardados (`img/hero/`, `img/ref/`, `datos-proyectos.xlsx`)
- [x] Storyboard y datos cruzados (`REDISENO-2027.md`, `datos-tula.md`)
- [x] Sistema de temas (`css/temas.css`)
- [x] Video de referencia de la animación (`img/ref/animacion-referencia/`)

### Fase 1 — Esqueleto *(siguiente — necesito de Andrea)*
- [ ] **Layout general** en 1 lámina: cómo se arma una escena en desktop y en móvil
  (dónde va el mapa, el textito, el carrusel, el banner)
- [ ] **Landing con índice**: qué secciones lista y en qué orden
- [ ] Tipografías y tamaños base
- [ ] Confirmar 3 colores de tema (rosa / naranja / verde) — valores hex

→ Con esto Claude arma el **cascarón** del sitio (landing + 1 escena de ejemplo vacía).

### Fase 2 — Escenas, una por una
Para **cada escena** Andrea entrega un paquete (ver sección 3). Claude la integra,
manda preview, Andrea ajusta. Recién entonces se pasa a la siguiente.

Orden de escenas (del storyboard):
1. [ ] Introducción — Conexión con el drenaje del Valle de México
2. [ ] Mejorar la calidad del agua — intro
3. [ ] Atotonilco (PTAR)
4. [ ] Contaminación industrial
5. [ ] Colectores (drenaje de la ciudad)
6. [ ] Monitoreo de calidad
7. [ ] Restauración de ecosistemas — intro
8. [ ] Restauración de riberas
9. [ ] Restauración y conservación forestal
10. [ ] Espacio público (5 sitios + carrusel)
11. [ ] Interconectividad / Nueva ANP
12. [ ] Inundaciones — taludes
13. [ ] Desazolve
14. [ ] Monitoreo automático (21 estaciones)

### Fase 3 — Cierre
- [ ] Rellenar datos pendientes conforme Andrea los confirme
- [ ] Revisar `mapa.html` (vista Leaflet detallada)
- [ ] Pruebas en móvil
- [ ] Publicar en GitHub Pages

---

## 3. Qué entrega Andrea por escena (checklist copiable)

Para la escena **"____"**:

- [ ] **Fondo del mapa**: 1 o varios frames Blender (JPG/PNG, 1920×1080)
  - si hay movimiento: 1 frame por posición de cámara, numerados
- [ ] **Capas de intervención** de esta escena: PNG con **fondo transparente**
  (río, rutas, polígonos, pines, isócronas…)
  - el **río va sin glow**; las intervenciones sí llevan color de tema
- [ ] **Textito**: título + 1–2 frases + qué palabra va en flúor
- [ ] **Carrusel** (si aplica): imágenes + pie de foto de cada una
- [ ] **Banner**: texto del banner de sección o mensaje clave
- [ ] **Tema de color**: rosa / naranja / verde
- [ ] **Datos**: valores nuevos o "sigue pendiente"

> Regla de oro: **el texto se pasa como texto**, nunca incrustado en la imagen
> (para que sea seleccionable, responsivo y accesible).

---

## 4. Formato de archivos

| Tipo | Formato | Nota |
|---|---|---|
| Fondo de mapa (Blender) | JPG (o PNG si necesita transparencia) | 1920×1080, ≤ 2560 px ancho |
| Capa que va encima del mapa | **PNG RGBA** (fondo transparente) | misma cámara/encuadre que el fondo |
| Secuencia de animación | PNG numerados (`escena3_01.png`, `_02`…) o MP4/WebM | |
| Fotos de carrusel | JPG | horizontal si se puede |
| Textos | pegados en el chat o un `.txt`/`.docx` | no dentro de la imagen |
| Diseño InDesign | export PNG/PDF por lámina | como **referencia visual**, no se usa el archivo `.indd` |

Cómo mandarlos: a **Descargas** y arrastrar al chat con `@`. Si son muchos, un
`.zip` o la ruta de una carpeta.

---

## 5. ¿Poco a poco o todo junto?

**Poco a poco** — pero con el esqueleto definido primero.

| | Poco a poco ✅ | Todo junto ❌ |
|---|---|---|
| Errores | se ven de a uno, fáciles de arreglar | se acumulan, difícil rastrear |
| Feedback | rápido, por escena | hasta el final |
| Tu carga | 1 paquete a la vez | armar todo antes de ver nada |
| Riesgo | bajo | rehacer mucho si algo no cuadra |

**Excepción:** el **layout general** (Fase 1) sí conviene tenerlo completo antes
de empezar, porque es el molde de todo lo demás.

---

## 6. Estado vivo (21-sep-2026, ronda 2)

- **Borrador v2027, ronda 2 lista** (`index.html`): inicio en claro, historia con mapa de municipios,
  compromiso 92 sólo del Tula, hexágonos, sin cierre ni mapa interactivo, sin datos amarillos.
- **Andrea ahora:** mandar la **imagen nueva** y "más cosas" (los renders que uso son previos) + fotos.
- **Pendiente de datos:** 7 datos que ya no se muestran (ver `datos-tula.md`).
- **Cómo se edita:** textos/datos en `tools/build_index.py` y `tools/build_historia_map.py`; fotos por nombre en `img/fotos/`.
