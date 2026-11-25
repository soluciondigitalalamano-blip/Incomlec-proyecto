# Mapa · página del PDF → sección del bloque `DATA`

Insumo: `<AAMMDD> INFORME COMITE DE PROYECTOS<...>.pdf`, exportado de
Power BI. La fecha del nombre es la del corte, **en AAMMDD**
(`261014` = 14 oct 2026), no en DDMMAAAA como el de Soporte.

Destino: el bloque `const DATA = { … }` de `index.html` (hoy, líneas ~536
a ~675). **Es lo único que se edita.** El resto del archivo —estilos,
render, derivados— no se toca nunca.

> ⚠ **TÍTULOS POR CONFIRMAR.** Esta tabla se construyó a partir de los
> nombres que el propio dashboard cita en sus comentarios de
> transcripción, porque el PDF de origen no estaba disponible al montar el
> repositorio. **En la primera corrida real, abre el PDF, compara los
> títulos de sus páginas con la columna izquierda y corrige aquí lo que no
> coincida**, antes de transcribir. Dilo en la notificación.

> El PDF no trae texto fiable: la extracción con `pdftotext` sale
> desordenada y mezcla columnas. Renderiza cada página a imagen
> (`pdftoppm -png -r 110 -f N -l N informe.pdf pagN`) y **léela como
> imagen**. Nunca transcribas desde el texto plano.

> **El número de página NO es estable.** Los exports de Power BI cambian de
> composición entre semanas. **Localiza cada sección por su título, nunca
> por su número de página.** Si un título no aparece en el export de esta
> semana, deja publicados los valores anteriores de esa sección y dilo en
> la notificación.

| Título en el PDF | Alimenta |
|---|---|
| RESUMEN EJECUTIVO DE PROYECTOS | `resumen`, `clasificacion`, `procesos`, `sinProyectos` |
| PARKING | filas de `proyectos` con línea `parking` |
| AEROPUERTOS | filas de `proyectos` con línea `aero` |
| CONTROL DE ACCESO PEATONAL | filas de `proyectos` con línea `peat` |
| CONTROL DE ACCESO VEHICULAR Y PEAJES | filas de `proyectos` con línea `vehi` |
| COMPRAS | filas de `proyectos` con línea `compras` |
| SEGUIMIENTO DE CLIENTES PARKING | entra a `bulevar`, `cuenca`, `pereira`, `cmSabana` (ver abajo) |
| ID+D · BULEVAR NIZA | `bulevar.tareas`, `bulevar.plazas`, `bulevar.descartadas`, `bulevar.cronograma` |
| ID+D – PROYECTOS PENDIENTES (CC-13113) | `cuenca` |
| SOCIEDAD DE MEJORAS DE PEREIRA | `pereira` |
| CENTRO MÉDICO LA SABANA | `cmSabana` |
| RE: TITAN · VIABILIDAD SPARK2 | `titan.grupos` |
| AEROPUERTO JMC – MEDELLÍN (ampliación EMIGRA / IMIGRA) | `jmc.hitos`, `jmc.nota` |

## Detalle por sección

**`corte` / `ant`** — ISO. `corte` sale de los seis dígitos del nombre del
archivo; `ant` es el `corte` que estaba publicado antes de esta corrida.
**Todo el texto de fecha de la página se deriva de estos dos campos.**

**`cortes`** — solo para las secciones cuya página vino desfasada; ver
«Paso 2» del runbook. Vacío (`{}`) cuando todo está al corte.

**`resumen`** — `actual` y `anterior`, cada uno con `total`, `at`,
`riesgo`, `cli`, `inc`. `total` menos la suma de los cuatro estados es el
«sin estado de entrega»; puede ser > 0, no lo fuerces a cero.
`anterior` **debe ser igual al `actual` publicado la semana pasada**: el
script lo comprueba.

**`clasificacion`** — `[nombre, valor del corte, valor del corte anterior]`.
La suma de la columna del corte tiene que dar `resumen.actual.total`, y la
del anterior, `resumen.anterior.total`.

**`procesos`** — igual que `clasificacion`: `[nombre, corte, anterior]`, y
las mismas dos sumas.

**`sinProyectos`** — las clasificaciones que esta semana quedaron sin
proyectos registrados (hoy: Transporte masivo y Soporte y mantenimientos).

**`proyectos`** — una fila por proyecto de las tablas de línea:
`[línea, CC, proyecto, estado, % cumplimiento, fecha fin, fecha proyectada, observaciones]`.

- `línea`: `parking` · `aero` · `peat` · `vehi` · `compras`
- `estado`: `at` (a tiempo) · `riesgo` (a tiempo pero en riesgo) ·
  `cli` (fuera de tiempo, causa cliente) · `inc` (fuera de tiempo, causa
  Incomelec) · `sin` (sin fecha)
- fechas en ISO `AAAA-MM-DD`, o `null` cuando la tabla no la trae
- `% cumplimiento` entero de 0 a 100

Las filas de las tablas **pueden ser menos que `resumen.actual.total`**: el
resumen ejecutivo cuenta proyectos que no están desglosados en las tablas
de línea. La página lo dice así («proyectos en las tablas»). El script
avisa de la diferencia pero no la trata como error.

**`bulevar.tareas`** —
`[elemento, descripción, categoría, progreso, prioridad, inicio, vencimiento]`.
Progreso: `No iniciado` · `En curso` · `Completado`. Prioridad: `Alto` ·
`Crítico`. Las fechas de esta tabla van **en texto tal como vienen**
(«30 de mayo»), no en ISO.

**`bulevar.plazas`** — `sot1` + `sot2` = `total`; `totSot1` + `totSot2` =
`totales`; más `dif`, `inicial`, `servidumbre` y `notas`.

**`bulevar.descartadas`** — `cols` (los encabezados, con `Total` al final),
`filas` por sótano y `total` general. Cada fila tiene que cerrar en su
propia columna `Total`, y `total` tiene que ser la suma de las filas.

**`bulevar.cronograma`** — `[WBS, tarea, inicio ISO, fin ISO, progreso, nivel]`.
`nivel` 0/1/2 es la sangría del WBS. **De aquí salen solos** el rango del
Gantt, la línea del corte, los meses del eje, el insight de Bulevar y las
tarjetas de «fase en curso», «inicio de instalación» y «entrega
funcional»: no hay fechas de Bulevar escritas en ningún otro lado.

**`cuenca`** —
`[descripción, categoría, progreso, prioridad, inicio, vencimiento]`.
Alimenta además el título de la tarjeta y la alerta de la semana: el
número de pendientes, las categorías y los críticos se cuentan de aquí.

**`pereira`** — `[tema, novedad]`. El número de novedades del título y de
la alerta se cuenta de aquí.

**`cmSabana`** — `[conclusión, es crítica]`. `true` la pinta en rojo.

**`titan.grupos`** — `[tipo, desde, hasta, modelo, tarjeta]`. El total de
equipos del título, las tarjetas por tipo y el pie de la tabla se calculan
de aquí: no escribas «34 equipos» ni «UDOO 18 · URVE 16» a mano.

**`jmc`** — `hitos`: `[nombre, fecha ISO o null, es acción prioritaria]`;
`nota`: el párrafo de contexto.
