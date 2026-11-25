# Mapa · página del insumo → sección del bloque `DATA`

Insumo: **un PowerPoint `.pptx`**, no un PDF. Nombre
`<DDMMAAAA>-_INFORME_COMIT__DE_PROYECTOS_V<n>.pptx`
(ej. `18112026-_INFORME_COMIT__DE_PROYECTOS_V2.pptx` = corte del
**18 de noviembre de 2026**).

⚠ **La fecha va en DDMMAAAA**, como la de Soporte. Confírmala siempre
contra la tarjeta «Actualizado: DD/MM/AAAA» del pie de la página 1: esa
manda sobre el nombre del archivo.

Destino: el bloque `const DATA = { … }` de `index.html`. **Es lo único que
se edita.** El resto del archivo —estilos, render, derivados— no se toca.

## Cómo leer el insumo

Las diapositivas son **capturas de pantalla pegadas**: no tienen texto
extraíble. No intentes `pptx` → texto, sale vacío.

**No conviertas con LibreOffice**: recorta las tablas y pierde filas.
Extrae las imágenes incrustadas, que vienen a resolución nativa, y léelas
como imágenes:

```python
from pptx import Presentation
p = Presentation(ruta)
for i, s in enumerate(p.slides, 1):
    for j, sh in enumerate(s.shapes, 1):
        if sh.shape_type == 13:          # PICTURE
            (carpeta / f"s{i:02d}_{j}.png").write_bytes(sh.image.blob)
```

⚠ **Una diapositiva puede traer varias imágenes, y hacen falta todas.**
Las tablas de Power BI tienen scroll: el export añade capturas sueltas con
las filas que no cabían. Si lees solo la primera imagen de la diapositiva,
**pierdes proyectos en silencio**. En el export del 18-nov: PARKING trae 3
imágenes, CONTROL DE ACCESO VEHICULAR 3, AEROPUERTOS 2, CONTROL DE ACCESO
PEATONAL 2.

## Las páginas

**Ubica cada sección por su título, nunca por su número de página.** El
número y la composición cambian entre exports. Si un título no aparece esta
semana, no transcribas esa sección, márcala en `DATA.cortes` con su fecha
anterior y dilo en la notificación.

Inventario del export del 18-nov-2026 (13 diapositivas):

| # | Título de la página | Alimenta |
|---|---|---|
| 1 | *(sin título; pie «Resumen Ejecutivo de Proyectos»)* | `resumen`, `clasificacion`, `procesos` |
| 2 | TRANSPORTE MASIVO | vacía → entra en `sinProyectos` |
| 3 | PARKING *(tabla, 3 imágenes)* | filas de `proyectos` con línea `parking` |
| 4 | PARKING *(ID+D, Diverplaza)* | **sin destino** · ver «Secciones nuevas» |
| 5 | PARKING *(ID+D, Bulevar y Alcaldía de Cuenca)* | `bulevar.tareas`, `cuenca` |
| 6 | PARKING *(MATRIZ DE ENTREGABLES – CONTRATO PLAZA CLARO)* | **sin destino** |
| 7 | AEROPUERTOS *(tabla, 2 imágenes)* | filas de `proyectos` con línea `aero` |
| 8 | CONTROL DE ACCESO PEATONAL *(tabla, 2 imágenes)* | filas de `proyectos` con línea `peat` |
| 9 | CONTROL DE ACCESO PEATONAL *(Diagrama de Gantt – Programación de proyectos)* | **sin destino** |
| 10 | CONTROL DE ACCESO VEHICULAR *(tabla, 3 imágenes)* | filas de `proyectos` con línea `vehi` |
| 11 | CONTROL DE ACCESO VEHICULAR *(matriz BL229/C20 y «Día 2»)* | **sin destino** |
| 12 | SOPORTE Y MANTENIMIENTOS | vacía → entra en `sinProyectos` |
| 13 | COMPRAS | filas de `proyectos` con línea `compras` |

⚠ La página 10 se titula **CONTROL DE ACCESO VEHICULAR** a secas, pero su
total incluye los peajes (15 = 5 vehicular + 10 peajes de la clasificación).
Corresponde a la línea `vehi`, «Control de acceso vehicular y peajes».

### Secciones del tablero que este export NO trae

`pereira`, `cmSabana`, `titan`, `jmc`, y de Bulevar las partes
`plazas`, `descartadas` y `cronograma`. **No las inventes ni las borres**:
déjalas con los valores publicados y márcalas en `DATA.cortes` con la
fecha del corte en que sí vinieron. Si no, la página afirmará que son del
corte nuevo.

### Secciones nuevas sin destino en el tablero

Las páginas 4, 6, 9 y 11 traen material que el `index.html` no sabe
pintar: pendientes ID+D de Diverplaza, la matriz de entregables del
contrato Plaza Claro, el Gantt de programación de los 13 proyectos y la
matriz BL229/C20 con el avance por día. **No las metas a la fuerza en una
sección que no les corresponde.** Avisa de que están y pregunta antes de
añadirles sitio en el tablero.

## Detalle por sección

**`corte` / `ant`** — ISO. `corte` sale de la tarjeta «Actualizado» de la
página 1 (y se contrasta con el nombre del archivo); `ant` es el `corte`
que estaba publicado antes de esta corrida. **Todo el texto de fecha de la
página se deriva de estos dos campos.**

**`cortes`** — solo para las secciones cuya página vino desfasada o no
vino; ver «Paso 2» del runbook. Vacío (`{}`) cuando todo está al corte.

**`resumen`** — `actual` y `anterior`, cada uno con `total`, `at`,
`riesgo`, `cli`, `inc`, de las cinco tarjetas de la página 1. `total` menos
la suma de los cuatro estados es el «sin estado de entrega»; puede ser > 0
(el 18-nov: 49 − 20 − 5 − 6 − 16 = 2). No lo fuerces a cero.
`anterior` **debe ser igual al `actual` publicado la semana pasada**: el
script lo comprueba.

**`clasificacion`** — del anillo «PROYECTOS POR CLASIFICACIÓN»:
`[nombre, valor del corte, valor del corte anterior]`. La suma de la
columna del corte tiene que dar `resumen.actual.total`.

**`procesos`** — del anillo «PROYECTOS POR PROCESOS», mismo formato.
⚠ **Los sectores pequeños del anillo salen sin etiqueta.** En el export del
18-nov, «Pend.Admin» no trae número: se deduce del total (49 − 19 − 17 −
10 − 2 = 1). Dedúcelo siempre por diferencia y **dilo en la notificación**;
nunca lo dejes fuera, porque entonces la suma no cuadra y el script falla.

**`proyectos`** — una fila por proyecto de las tablas de línea:
`[línea, CC, proyecto, estado, % cumplimiento, fecha fin, fecha proyectada, observaciones]`.

- `línea`: `parking` · `aero` · `peat` · `vehi` · `compras`
- `estado`, según la columna «Estado Entrega Automático»:
  `A TIEMPO` → `at` · `A TIEMPO PERO EN RIESGO` → `riesgo` ·
  `FUERA DE TIEMPO CAUSA CLIENTE` → `cli` ·
  `FUERA DE TIEMPO CAUSA INCOMELEC` → `inc` · `SIN FECHA` → `sin`
- fechas en ISO `AAAA-MM-DD`; en el insumo vienen como «18 de mayo de 2026»
- celda vacía → `null`, no cadena vacía
- `% cumplimiento` entero de 0 a 100

Las tarjetas laterales de cada página dan el total y el reparto por estado
de esa línea: **cuádralas contra las filas que transcribiste**. Si no
coinciden, te faltan filas de las capturas de scroll.

**`bulevar.tareas`** —
`[elemento, descripción, categoría, progreso, prioridad, inicio, vencimiento]`.
Progreso: `No iniciado` · `En curso` · `Completado` · `Bloqueado` ·
`Por detrás`. Las fechas de esta tabla van **en texto tal como vienen**
(«30 de mayo», «Hace 6 días», «Mañana»), no en ISO.

**`bulevar.plazas` / `descartadas` / `cronograma`** — no vienen en el
export del 18-nov. Ver «Secciones del tablero que este export NO trae».

**`cuenca`** —
`[descripción, categoría, progreso, prioridad, inicio, vencimiento]`, de la
lista ID+D filtrada por `CC-13113-ALCALDIA DE CUENCA` en la página 5.

**`pereira`** · **`cmSabana`** · **`titan`** · **`jmc`** — no vienen en el
export del 18-nov.

**`sinProyectos`** — los títulos cuyas páginas vinieron vacías (el 18-nov:
Transporte masivo y Soporte y mantenimientos).
