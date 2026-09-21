# Rediseño del sitio — Río Tula (v2027)

> Documento de trabajo. Recopila los insumos entregados por Andrea para la nueva
> versión del sitio. El **layout lo define Andrea**; aquí sólo se almacena el
> contenido, la identidad gráfica y las decisiones técnicas mientras se
> reconfigura el código.
>
> Insumos originales:
> - `Layout nuevo sitio.pdf` (características + storyboard)
> - `Acciones 2027 - RC.pptx` (ilustraciones Blender + estilo de animación)
> - Copias en `img/hero/_src/` y capturas en el scratchpad de la sesión.

---

## 1. Características generales (del PDF)

- **Interacción principal: scroll down.** Cada "escena" combina:
  - Mapa (base nuevo con inclinación, resalta zonas pobladas)
  - "Textitos": un título + micro‑texto de 1–2 frases a la vez, con una palabra/
    frase resaltada tipo **flúor**.
  - Carrusel de imágenes cuando haga falta (formato "burbuja" / recuadro).
  - Banners de título a todo lo ancho cuando cambia de sección o hay un mensaje clave.
- **Mapa base:** el mismo render nuevo (Blender) con inclinación isométrica.
- **Paleta por tema:** cambia según la sección — **rosa**, **naranja**, **verde** —
  y afecta: títulos, elementos del mapa y resaltados de texto (flúor).
  - Referencia de swatches en el PDF: *Calidad del agua* = rosa/salmón,
    *Inundaciones* = naranja.
- **Móvil:** debe funcionar bien; mapa arriba y carrusel abajo (o al revés),
  apilados.
- **Landing con índice antes del scroll:** confirmado por Andrea. Portada con
  índice para saltar a cada sección.
- **Tarea explícita:** proponer layout para computadora y para celular
  (lo hace Andrea).

### Resaltado "flúor"
En el PDF el ejemplo resalta *"operar el sistema de drenaje y presas de forma
eficiente segura"* con fondo naranja sólido y texto blanco. Es un `<mark>` con el
color del tema.

---

## 2. Identidad gráfica nueva (ilustraciones Blender)

Guardadas en `img/hero/`:

| Archivo | Qué es | Uso |
|---|---|---|
| `tula-base.jpg` | Render base opaco: terreno blanco, edificios gris claro, polígonos verdes de ANP ya integrados. Vista oblicua (inclinada) de Tula de Allende y la cuenca. | Capa de fondo del mapa‑escena. |
| `tula-glow.png` | Overlay **RGBA transparente**: río + traza urbana brillando en turquesa sobre negro (alpha 0–148). | Se superpone al base; **se recolorea por tema** (rosa/naranja/verde) con `filter`/`mix-blend-mode` o versiones tintadas. |
| `tula-rio.jpg` | Frame ya compuesto (base + verde + río turquesa + presa Endhó resaltada). | Escena donde el protagonista es el río. |
| `img/hero/_src/*.png` | PNG originales sin comprimir de Blender. | Re‑exportar / re‑tintar en el futuro. |

**Estilo de animación (de la pptx):** el render de Blender es **una sola imagen
fija**; en las slides las "animaciones" se logran superponiendo, sobre ese fondo,
elementos vectoriales que aparecen/crecen:
- Banner de título arriba‑izquierda (`Saneamiento`, `Gestión de inundaciones`,
  `Restauración`, `Proyectos de espacio público`, `Interconectividad`).
- Etiqueta "Parque Nacional y Atlantes de Tula" sobre el cerro.
- Pines con foto circular + etiqueta ("Bojay 3k habitantes", "San Lorenzo 20k",
  "Río Rosas 24k", "Tres Culturas 4k", "Chamizal 10k", "San Lorenzo"…).
- Trazos que se dibujan: río, vías del tren, ciclovía, polígono de la nueva ANP.
- Tarjeta de "mensaje clave" abajo‑derecha (ej. *"Tratar más del 95% del drenaje
  doméstico que se vierte al río"*, *"52% de la población del municipio a 15 min a
  pie de alguna intervención"*).
- Isócronas de accesibilidad "15 min a pie" (fuente: OpenRouteService).

→ En web esto se traduce a: **imagen de fondo fija (o con leve parallax/zoom) +
capas SVG/DOM absolutas que se activan por paso de scroll** (mismo patrón que el
scrollytelling actual, pero con el render Blender como base en vez del SVG
esquemático).

### Decisiones de Andrea (10-sep-2026)
- **El río del render ya NO lleva glow** — va como línea fina y discreta.
- El **glow/color de tema se aplica a las capas de intervención** (rutas, pines,
  polígonos, isócronas), no al río. El **filtro CSS de recoloreo se activa a
  medida que aparece cada proyecto** con el scroll.
- Andrea diseña en **InDesign**, formato **1920×1080**.
- Andrea pasa las **capas de intervención poco a poco** (una escena a la vez).
- Video de referencia de la animación del mapa base:
  `img/ref/animacion-referencia/animacion-mapa-base.mp4` (+ frames sueltos).
  Fuente original: `E:\03_Trabajo\01_SEMARNAT\01_rio tula\2026\01_riotula\diseño\a.mp4`.

### Fotos de referencia (`img/ref/`)
Parques inundables usados como inspiración / posible contenido de carrusel:
- `buffalo-bayou-houston.jpg`, `buffalo-bayou-aerea.jpg`, `buffalo-bayou-plano.jpg`
  — Buffalo Bayou, Houston TX, 2015, 65 ha.
- `rodney-cook-park-atlanta-1.jpg`, `-2.jpg`, `parque-inundable-georgia.jpg`
  — Rodney Cook Sr. Park, Atlanta, 2021, 6.5 ha.
- `img/ref/iconos_pptx/` — recortes de pines/íconos de la pptx.

---

## 3. Storyboard / contenido (del PDF)

Estructura: **Sección → Subsección → Texto → (Mapa) → (Carrusel)**.

### 1. Introducción — "Conexión con el drenaje del Valle de México"
> Desde la época colonial, iniciaron las obras hidráulicas que envían el drenaje
> del Valle de México hacia el río Tula.
> - En 1636, el Tajo de Nochistongo
> - En 1900, ___
> - xxx

Subsecciones que siguen (sólo títulos en el PDF, contenido pendiente):
- Construcción de la PTAR Atotonilco
- Inundación en Tula
- Proyecto de restauración del río Tula

### 0. Intro del proyecto — "MEJORAR LA CALIDAD DEL AGUA"
> Existen tres fuentes principales de contaminación del río Tula que estamos
> atendiendo en este proyecto.

#### 1. Atotonilco — "Optimización de la PTAR Atotonilco" (tag: Saneamiento)
> Históricamente la PTAR Atotonilco trataba **31 m³/s** en promedio, dejando fluir
> por el río XX m³/s sin tratamiento. En 2026 incrementamos el caudal tratado a
> **38 m³/s** y a partir de 2027 la PTAR Atotonilco va a tratar todo el drenaje
> del río en estiaje.

#### 2. Contaminación industrial — "Control de la contaminación industrial"
> Durante este sexenio, la Conagua y la Profepa van a inspeccionar a las XX
> empresas que descargan al río Tula o sus tributarios al menos dos veces para
> asegurar su cumplimiento. A la fecha hemos inspeccionado a XX industrias y se
> está capacitando y certificando a XX.

#### 3. Colectores — "Drenaje de la ciudad de Tula"
> Todo el drenaje de la zona metropolitana de Tula se vierte al río sin
> tratamiento. El gobierno del estado de Hidalgo está construyendo XX km de
> colectores para captar XX descargas y tratarlas en la planta de tratamiento de
> la central termoeléctrica de CFE.

#### 4. Monitoreo
> Para conocer la calidad de XX km de río a detalle, estamos realizando 3
> campañas de monitoreo manual por año en más de **95 sitios**. Adicionalmente,
> estamos instalando **5 estaciones de monitoreo automático** para conocer la
> calidad del río en tiempo real.

### 2. RESTAURACIÓN DE ECOSISTEMAS
> Para regresarle la vida a un río, es necesario recuperar ecosistemas como
> cuerpos de agua, humedales, riberas y zonas boscosas en la cuenca alta.

#### 1. Restauración de riberas
> A la fecha hemos saneado **1,600 árboles ribereños** para quitarles heno motita
> y ramas muertas. Adicionalmente, hemos plantado **300 árboles de 3 m** en la
> zona urbana de Tula. Junto con Conafor, estamos trabajando en limpiar, sanear o
> reforestar los XX km de riberas del río desde su nacimiento hasta la presa Endhó.

#### 2. Restauración y conservación forestal
> A inicios del sexenio existían solo **100 ha** de Áreas Naturales Protegidas en
> la cuenca del río Tula. A la fecha la Conanp ha certificado **1,700 ha** de
> Áreas Destinadas Voluntariamente a la Conservación. Adicionalmente, la Conafor
> está en proceso de restaurar XX ha de suelo forestal.
>
> La Conagua trabaja en controlar la población de lirio y mosquito en la presa
> Endhó, el cuerpo de agua más grande de la cuenca. Por otro lado, se está
> rehabilitando el bordo de la laguna de Bojay para separar la laguna (alimentada
> por manantiales) del río Tula y contar con un cuerpo de agua limpia de **55 ha**
> a 2 km de la ciudad de Tula.

### ESPACIO PÚBLICO
> En la ciudad de Tula estamos construyendo **5 sitios de espacio público
> ribereño**, aprovechando las intervenciones de estabilización de taludes y
> restauración ecológica.

Carrusel / lista de sitios:
1. Chamizal — Parque ribereño (10k habitantes)
2. San Lorenzo — Parque ribereño (20k habitantes)
3. Río Rosas (24k habitantes)
4. Tres Culturas (4k habitantes)
5. Bojay (3k habitantes)

- **Intervenciones integrales:** en cada sitio se hace de forma simultánea
  saneamiento, revegetación con plantas nativas, prevención de inundaciones y
  equipamiento de espacio público.
- **Interconexión:** aprovechando las antiguas vías del tren y los taludes que se
  están trabajando. → *"Todas las intervenciones interconectadas por vía ciclable
  de 12 km"*. Antiguas vías del tren: 4 km. Bordos rehabilitados: 6 km. Caminos
  rurales rehabilitados: 2 km.
- **Nueva ANP** ("Nueva Área Nacional Protegida") con hitos: Antigua estación del
  tren, Antigua planta Tolteca, Petrograbados Toltecas, Manantial, Nuevos sitios
  arqueológicos.
- Dato clave: *"52% de la población del municipio a 15 min a pie de alguna
  intervención"* (accesibilidad, fuente OpenRouteService). Estación Tula del Tren
  México–Querétaro como referencia.

### INUNDACIONES

#### 1. Estabilización de taludes
> Las zonas del río altamente erosionadas representan un riesgo para la población
> que vive cerca. Estamos estabilizando XX km de taludes y seguiremos haciendo
> obras para estabilizar todos los taludes críticos de las zonas urbanas.

#### 2. Desazolve
> Cuando el río está azolvado, hay menos espacio para que el agua pueda fluir,
> incrementando riesgos de inundación. En 2025 desazolvamos **3.9 km** de río
> removiendo XX ton de sedimentos, basura y escombros. Con estas obras buscamos
> asegurar que el río pueda descargar XX m³/s sin riesgos.

#### 3. Monitoreo automático
> Instalamos **21 estaciones** para conocer cuánta agua fluye en cada segmento
> del río cada 5 minutos. Esta información va a permitir operar el sistema de
> drenaje y las presas de forma eficiente y segura.

> **Pendiente de Andrea / la fuente:** todos los "XX" son datos por confirmar.
> Cruzar con el Excel *"Datos de proyectos - Atoyac, Lerma-Santiago, Tula.xlsx"*
> ya usado en la versión anterior.

---

## 4. Temas de color

| Tema | Uso previsto | Rol |
|---|---|---|
| **Rosa / salmón** | Calidad del agua / Saneamiento | títulos, glow del mapa, `<mark>` flúor |
| **Naranja** | Inundaciones / gestión de riesgo | idem |
| **Verde** | Restauración de ecosistemas / espacio público | idem |

Valores propuestos (ajustables por Andrea) en `css/temas.css`:
`--tema-rosa #e8637a`, `--tema-naranja #e8791f`, `--tema-verde #3f8f5f`.

---

## 5. Estado del código (se irá actualizando)

- [x] Insumos almacenados: `img/hero/`, `img/ref/`, `datos-proyectos.xlsx`, este documento.
- [x] `css/temas.css` con las 3 paletas + utilidades (`.tema-rosa/naranja/verde`,
      `<mark class="fluor">`, banner de sección, "textito", burbuja de carrusel).
- [x] Cruce de datos del Excel con el storyboard → `datos-tula.md`.
- [x] Historia del río resuelta (versión verificada, se ignora el PDF).
- [x] Flujo de trabajo definido → `FLUJO-DE-TRABAJO.md`.
- [x] Video de referencia de la animación guardado.
- [x] **Borrador v2027 armado por Claude (21-sep-2026)** por falta de tiempo para el layout:
      portada con índice → historia → **compromiso 92** → el proyecto (3 círculos) →
      calidad del agua → inundaciones → ecosistemas y espacio público → cierre.
      Usa las capas de `diseño/espacio publico/` (marcos, capas y burbujas → `img/mapa/`).
- [x] Carrusel de fotos con marcadores (se sustituyen por nombre de archivo, ver `img/fotos/LEEME.md`).
- [x] Cámara con zoom por paso, pines con líder punteado, tema de color por capítulo.
- [ ] **Andrea revisa el borrador** (textos, orden, qué falta).
- [ ] Sustituir marcadores por fotos reales y por las capas finales de Andrea.
- [ ] Animaciones "tipo pptx" por escena (rutas que se dibujan, isócronas) cuando lleguen las capas.
- [ ] Cerrar los datos amarillos (ver `datos-tula.md`).
- [ ] Revisar `mapa.html` (el mapa Leaflet detallado sigue como vista aparte).

## 6. Datos

- **Fuente:** `datos-proyectos.xlsx` (hoja *Tula*).
- **Cruce y pendientes:** `datos-tula.md`.
- Cifras clave: **37 proyectos** · $1,478 MDP · 2,415 ha · 4 ejes
  (Calidad 15 · Inundaciones 6 · Restauración/espacio público 9 · Otros 7).
  (Chamizal Etapa 2 se engloba en Chamizal; se agrega Ahuehuetes.)
