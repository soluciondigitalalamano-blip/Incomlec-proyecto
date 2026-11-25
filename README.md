# Informe Semanal de Proyectos · INCOMELEC

Portal web estático con el Informe Semanal de Proyectos del Comité de
Proyectos de INCOMELEC.

## Estructura

| Ruta | Contenido |
|---|---|
| `index.html` | El informe completo (HTML, CSS y JS en un solo archivo) |
| `.automatizacion/` | Runbook, mapa del PDF, verificación y plantilla de correo |
| `.nojekyll` | Evita que GitHub Pages procese el sitio con Jekyll |

## Cómo actualizar

Se actualiza solo. Seis corridas por semana (jueves y viernes a las 12:52,
14:52 y 16:52, hora de Bogotá): la primera que encuentra el PDF del comité
en el correo publica, y las demás salen en silencio.

A mano, el procedimiento completo está en
[`.automatizacion/RUNBOOK.md`](.automatizacion/RUNBOOK.md). En resumen:

1. Editar **solo** el bloque `const DATA = { … }` de `index.html`.
2. `python3 .automatizacion/verificar.py` — si sale con código 1, no se publica.
3. Commit y push a `main`; Cloudflare Pages despliega en uno a cuatro minutos.

> **No escribas fechas ni totales a mano.** El encabezado, el pie, el
> filtro de periodo, los títulos de las tarjetas, las alertas y los
> insights se derivan de `DATA.corte`, `DATA.ant` y de los propios
> valores. Si encuentras una fecha literal en el código de presentación,
> conviértela en derivada en vez de editarla.

Si una página del PDF viene desfasada, no se transcribe: se rotula con su
propia fecha en `DATA.cortes` y la página muestra sola el aviso.

## Publicación

Cloudflare Pages, conectado a este repositorio: framework *Ninguno*, sin
comando de compilación, directorio de salida `/`.
