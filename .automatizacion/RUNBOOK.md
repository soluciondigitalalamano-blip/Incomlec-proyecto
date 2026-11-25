# Runbook · Informe Semanal de Proyectos · INCOMELEC

Operación real. Seis corridas por semana: **jueves y viernes a las 12:52,
14:52 y 16:52** (hora de Bogotá). La primera que encuentre el insumo
publica; las demás salen en silencio. **La última (viernes 16:52) lleva
excepción**: si a esa hora no llegó nada en toda la semana, avisa.

El reloj de la máquina está en UTC. Saca la hora local con
`TZ=America/Bogota date '+%Y-%m-%dT%H:%M'` y nunca escribas en el informe
una hora que quede en el futuro.

---

## Paso 0 · Salidas tempranas

Busca en Gmail un correo **del dominio `incomelec.com`**, con **«informe
proyectos» en el asunto** y un **adjunto de PowerPoint**.

Consulta sugerida: `from:incomelec.com subject:(informe proyectos) has:attachment newer_than:10d`

⚠ **El insumo es un `.pptx`, no un PDF.** El adjunto se llama
`<DDMMAAAA>-_INFORME_COMIT__DE_PROYECTOS_V<n>.pptx`, por ejemplo
`18112026-_INFORME_COMIT__DE_PROYECTOS_V2.pptx` = corte del **18 de
noviembre de 2026**. La fecha va en **DDMMAAAA**, igual que en Soporte.

Los separadores, los acentos y el sufijo de versión varían; no descartes un
adjunto por eso. Lo que importa son los ocho dígitos iniciales — y aun así,
**la fecha que manda es la de la tarjeta «Actualizado: DD/MM/AAAA» del pie
de la página 1**, no la del nombre. Si no coinciden, no publiques y avisa.

### Qué es «ya está publicado»

Hay **dos** cortes que mirar, y no son el mismo:

| Dónde | Qué significa |
|---|---|
| `DATA.corte` en `index.html` del repo | lo que está **transcrito y commiteado** |
| `corte.txt` **del sitio desplegado** | lo que el cliente **ve de verdad** |

Pueden separarse: si el push sale pero Cloudflare no despliega, el repo va
por delante del sitio. **El que manda para decidir si hay trabajo pendiente
es el desplegado.** Léelo con WebFetch:
`https://incomlec-proyecto.pages.dev/corte.txt?v=<algo distinto cada vez>`

### Las salidas

- **No llegó el correo** → termina en silencio. No avises.
  **Excepción**: en la última franja de la semana (viernes 16:52), si no
  llegó nada en ninguna franja, avisa que no hubo insumo.
- **Llegó y su corte ya está en el `corte.txt` desplegado** → termina en
  silencio: ya se publicó y ya se avisó.
- **Llegó, el repo ya tiene ese corte transcrito pero el desplegado es
  anterior** → **no vuelvas a transcribir**. La transcripción de otra
  franja se quedó a medias: el push salió y el despliegue no. Salta
  directo al **Paso 5** (esperar y verificar el despliegue) y sigue desde
  ahí con el correo y la Bitácora. Si el despliegue sigue sin llegar,
  avisa: probablemente la conexión Git del proyecto en Cloudflare se cayó.
- **Su corte es anterior al desplegado** → no publiques y avisa. Nunca
  retrocedas el corte.

## Paso 1 · Descargar y extraer las imágenes

Baja el adjunto a una carpeta nueva y vacía.

Las diapositivas son capturas pegadas: no tienen texto extraíble, y
convertirlas con LibreOffice **recorta las tablas y pierde filas**. Extrae
las imágenes incrustadas, que vienen a resolución nativa, y léelas como
imágenes. El procedimiento exacto está en `MAPA_PDF_A_DATA.md`.

⚠ **Una diapositiva puede traer varias imágenes, y hacen falta todas**: las
tablas de Power BI tienen scroll y el export añade capturas con las filas
que no cabían. Leer solo la primera imagen hace perder proyectos en
silencio. Cuadra siempre las filas que transcribas contra las tarjetas
laterales de total y de reparto por estado de esa misma página.

## Paso 2 · Validar que el PDF viene completo  ⚠️ OBLIGATORIO

Lee en **cada página** su tarjeta de fecha (el «Actualizado: DD/MM/AAAA»
del pie, el segmentador de periodo, o el rótulo de corte que traiga) y
compárala con el corte.

Esto no es teórico: en Soporte, el 18-nov-2026 una página vino congelada en
la fecha de la semana anterior, con cifras idénticas, mientras el resto del
PDF sí traía el corte nuevo.

Lo mismo vale para una página que **no venga**: el export del 18-nov-2026
no trajo Pereira, Centro Médico La Sabana, Titán ni JMC, que sí están en
el tablero. Una sección que falta se trata igual que una desfasada.

Si alguna página no corresponde al corte, o no aparece:

- **no transcribas esa sección**: deja publicados los valores anteriores;
- **rotúlala con su propia fecha** en `DATA.cortes` (ver abajo). No la
  dejes etiquetada con el corte nuevo;
- sigue con las demás páginas;
- nombra en la notificación final qué páginas venían viejas.

Nunca publiques como dato nuevo una cifra repetida de la semana anterior.

### `DATA.cortes` · el campo para las secciones desfasadas

```js
cortes:{},                            // todo al corte: lo normal
cortes:{cuenca:'2026-09-30'},         // esa seccion viene del 30 sep
```

Claves válidas: `resumen` · `proyectos` · `bulevar` · `cuenca` · `pereira`
· `cmsabana` · `titan` · `jmc`.

Cuando una clave tiene fecha distinta del corte, la página muestra sola un
aviso arriba del resumen y un sello «⚠ datos al …» en el subtítulo de esa
sección. **Cuando la página vuelva a venir al día, borra la clave.** Si la
dejas puesta por descuido, el informe seguirá afirmando una fecha vieja.

## La plantilla está parametrizada · no la des-parametrices

Encabezado, pie, título del documento, filtro de periodo, títulos de las
tarjetas, alertas e insights se derivan de `DATA.corte`, `DATA.ant` y de
los propios valores, con las constantes `CORTE_TXT`, `CORTE_DM`, `ANT_TXT`,
`ANT_DM`, `TOT`, `pctTot()`, `vsAnt()`, `mov()`, `proporcion()`, `topClas`
y `topProc`.

**No escribas una fecha ni un total a mano en ninguna parte.** Si al
revisar encuentras una fecha o una cifra literal en el código de
presentación, conviértela en derivada en vez de editarla.

Los textos que antes eran fijos («Parking concentra 16 de los 45»,
«Más de la mitad del portafolio…», «El portafolio creció de 41 a 45»,
«Titán: 34 equipos») ahora salen de los datos y cambian solos. Las alertas
y los insights se descartan solos cuando su condición no se cumple.

**Después de cada edición, `node --check`** sobre el bloque de script:

```
awk '/^<script>$/{on=1;next} /^<\/script>$/{on=0} on' index.html > /tmp/_chk.js && node --check /tmp/_chk.js
```

## Paso 3 · Transcribir

Sigue `MAPA_PDF_A_DATA.md`, que dice qué página alimenta cada sección. No
inventes correspondencias que no estén ahí.

**Ubica cada sección por el título de la página, nunca por su número.** Los
exports de Power BI cambian de composición entre semanas. Si un título no
aparece esta semana, deja publicados los valores anteriores de esa sección
y dilo en la notificación.

Edita **solo** el bloque `const DATA = { … }` de `index.html`, incluidos
`corte`, `ant` y `cortes`. Nada más de ese archivo.

## Paso 4 · Verificar  ⚠️ OBLIGATORIO, antes del commit

No improvises comprobaciones. Ejecuta el script del repositorio, **con los
cambios todavía sin commitear** para que pueda compararlos con lo publicado:

```
python3 .automatizacion/verificar.py
```

- **Código 0** → se puede publicar.
- **Código 1** → hay un FALLA. **No publiques**, no envíes el correo, no
  toques la Bitácora: avisa con la salida del script.
- **AVISO** no detiene la publicación, pero exige volver al PDF y
  confirmar ese punto a ojo antes de seguir.

Pega la salida completa del script en la notificación final. Es la prueba
de que la transcripción se revisó.

## Paso 5 · Publicar

Commit y push a `main`. Cloudflare Pages despliega solo.

El despliegue tarda **entre uno y cuatro minutos** desde el push. Espera y
vuelve a consultar con un parámetro distinto en la URL (`?v=<algo>`) para
no leer la copia en caché; **no des por fallido el despliegue antes de
cinco minutos**.

⚠ **Cómo NO comprobarlo.** Los rótulos de fecha los pinta el JavaScript
al abrir la página, así que no están en el HTML servido: buscar
«14 oct 2026» en el fuente no encuentra nada nunca. Y el bloque `DATA`
tampoco sirve, porque las herramientas de lectura web descartan los
`<script>`. Además, **desde el entorno del agente `curl` no llega a
`pages.dev`** (el proxy responde 403): solo funciona WebFetch.

Por eso el corte se publica también en texto plano, en `corte.txt`, que
escribe `verificar.py` a partir de `DATA.corte` (no se edita a mano).
Comprueba con **WebFetch**:

```
https://incomlec-proyecto.pages.dev/corte.txt?v=<algo distinto cada vez>
```

Tiene que devolver el corte nuevo en ISO. **Si todavía devuelve el corte
anterior, o da 404, no envíes el correo**: avisa que el despliegue no
llegó.

## Paso 6 · Correo

Solo si el Paso 5 terminó bien. Sale por **Resend**, nunca por Gmail: el
conector de Gmail reescribe las direcciones y borra las imágenes externas.

Con `mcp__Resend__send-email`:

- `from`: `LIDATO <operaciones@lidato.site>`
- `to`: `["soluciondigitalalamano@gmail.com"]`
- `subject`: `Actualización informe de proyectos`
- `html`: el contenido de `correo-aviso.html`, **tal cual, sin reemplazar nada**
- `text`: el contenido de `correo-aviso.txt`, también tal cual. Es
  obligatorio junto al html; no lo omitas.
- `attachments`: **ninguno**. La plantilla trae el logo y el icono como
  imágenes remotas (`src` a raw.githubusercontent.com), no como adjuntos
  `cid:`. No le agregues adjuntos ni conviertas las imágenes a `cid:`.

La plantilla no lleva fecha ni marcadores: no hay `{{FECHA_CORTE}}` que
sustituir. No le agregues la fecha del corte al cuerpo ni al asunto.

No toques el enlace del botón ni lo envuelvas en nada: Resend lo entrega
intacto y el cliente entra con un solo clic.

Después de enviar, con el `id` que devuelve llama a `mcp__Resend__get-email`
y comprueba en el HTML enviado que aparezca
`href="https://incomlec-proyecto.pages.dev/"` sin `google.com/url`. Reporta
el resultado en una línea.

Si Resend falla, avisa el error y **no reintentes por Gmail**.

## Paso 7 · Bitácora en Notion

Solo si el correo salió. Base `LIDATO QUEST · Bitácora`
(`collection://4204c6f8-c23f-8158-bae8-000bdfbb3f41`).

Fila madre: **INF-23 · Informe Semanal de Proyectos** (semanal, viernes
2:00 p. m., empezó en noviembre). Fila del ciclo: `Registro` exactamente
`INCOMELEC · Informe Semanal de Proyectos · <YYYY-MM>`. Si no existe la
fila del ciclo, **no la crees** y no inventes el `Total`: avisa que falta.

### El contador va por entrega, no por día de trabajo  ⚠️

El `Total` del ciclo son los **viernes del mes**: el compromiso es semanal
con fecha el viernes. Se cuenta la entrega, no el día en que el agente la
publicó.

La pregunta no es «¿ya marqué hoy?» sino **«¿ya está contada la entrega que
cubre este informe?»**:

1. Calcula la **entrega que cubre el corte**: el viernes de la semana a la
   que pertenece `DATA.corte`. Un corte del miércoles 18-nov cubre la
   entrega del viernes 20-nov.
2. Mira el campo `Fecha` de la fila: guarda la **última entrega contada**,
   no la última vez que corrió el agente.
3. Si `Fecha` es igual o posterior a esa entrega, **ya está contada: no
   toques nada**.
4. Si es anterior o está vacía, marca: `Hecho` = el valor leído **más 1**,
   `date:Fecha:start` = la **fecha de la entrega** (el viernes), no la de
   hoy, y `date:Fecha:is_datetime` = 0.

Comparar contra «hoy» o contra «la semana en curso» es incorrecto y hace
doble conteo: publicar el lunes 24 un informe con corte del 18 cubre la
entrega del viernes 20, no la del 27.

- Si el nuevo `Hecho` iguala a `Total`: `Estado` = `Entregado a tiempo`.
  Si queda por debajo: `Estado` = `Parcial`. Si lo superaría: no escribas
  nada y avisa.
- **Nunca crees filas nuevas.** No cambies ninguna otra propiedad.
- Si `Fecha` está vacía pero el campo `Detalle` dice que ya hay entregas
  contadas, **no marques**: avisa, porque la fila no tiene todavía la
  referencia que necesita el candado y marcar podría duplicar.

Al terminar, relee la fila y di en una línea qué pasó: `contador 3 → 4,
entrega del 27 nov` o `la entrega del 20 nov ya estaba contada, no se tocó`.

Si Notion falla, el correo ya salió y eso no se deshace: avisa que falta
marcar la entrega y no reintentes en bucle.

## Si algo falla

Transcripción, verificación o push fallidos: avisa el error con detalle,
**no envíes el correo** y **no escribas en la Bitácora**.
