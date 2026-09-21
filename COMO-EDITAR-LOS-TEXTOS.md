# Cómo cambiar los textos de la página

> Guía corta. **No hace falta saber programar ni instalar nada.** Solo una cuenta de GitHub.

## Antes de empezar (una sola vez)

1. Andrea te invita al repositorio. Te llega un **correo de GitHub**: abre la invitación y acéptala.
2. Entra a **https://github.com/Andymsan/rio-tula** con tu cuenta.

## Cambiar un texto (5 pasos)

| # | Qué haces | Dónde |
|---|---|---|
| 1 | Abre el archivo **`TEXTOS.md`** | Lista de archivos del repositorio |
| 2 | Pulsa el **lápiz ✏️** (*Edit this file*) | Arriba a la derecha del archivo |
| 3 | Busca el texto con **Ctrl + F** y cámbialo | Solo lo que está **después de los dos puntos** |
| 4 | Pulsa el botón verde **Commit changes…** | Arriba a la derecha |
| 5 | Escribe en una línea qué cambiaste y confirma con **Commit changes** | Ventana que se abre |

**Espera 1 o 2 minutos** y abre https://andymsan.github.io/rio-tula/ (pulsa **Ctrl + F5** para ver lo nuevo).

## Reglas (para que no se rompa nada)

- ✅ Cambia **solo el texto** después de `campo:`.
- ✅ **Cada campo va en una sola línea**, aunque sea largo.
- ❌ No borres el nombre del campo (`titulo:`, `texto:`…) ni las líneas que empiezan con `##`.
- Para separar partes de un campo se usa la barra **|** (por ejemplo `cifra:` y `fotos:`). **Mantén la misma cantidad de partes.**

### Marcas dentro del texto

| Escribes | Se ve |
|---|---|
| `**así**` | **negrita** |
| `==así==` | texto **resaltado** de color |
| `*así*` | *cursiva* |
| `[texto](https://enlace)` | un enlace |

## ¿Y si me equivoco?

- **La página no se rompe.** Si algo está mal escrito, el sistema se **detiene** y **no cambia** la página.
- Para ver el mensaje de error: pestaña **Actions** → el último resultado con ❌ → *Generar index.html…*. Dice en español qué falta y en qué línea.
- Para **deshacer** un cambio: en `TEXTOS.md` → **History** → elige el cambio → **Revert**.
- Todo cambio queda guardado con **nombre, fecha y hora**.

## Cuidado especial

Dos textos hablan de la **inundación de 2021** y de personas que fallecieron:
`historia-7` e `inundaciones-0`. Antes de cambiarlos, lee **`GUIA-DE-TONO.md`**.
Reglas: decir solo lo que se sabe, no prometer de más, sin culpar a las personas y con palabras sencillas.

## Lo que se cambia con Andrea (no aquí)

Fotos, colores, mapas, nombres de lugares sobre el mapa y el orden de las secciones.
Las fotos: guardarlas en `img/fotos/` con el nombre que dice `img/fotos/LEEME.md`.

## ¿Prefieres que alguien revise antes de publicar?

En el paso 4, elige **"Create a new branch… and start a pull request"** en lugar de publicar directo.
Andrea revisa y aprueba, y hasta entonces la página no cambia.
