#!/usr/bin/env python3
"""
Verificacion del informe semanal de Proyectos · INCOMELEC

Comprueba el bloque DATA de «index.html» contra si mismo y contra la
version publicada anteriormente. NO es opcional: el Paso 4 del runbook
consiste en ejecutar esto y pegar su salida en la notificacion.

    python3 .automatizacion/verificar.py

Sale con codigo 0 si todo pasa y 1 si algo falla. Si falla, NO se publica.
"""
import json, subprocess, sys, pathlib, datetime, re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
HTML = RAIZ / 'index.html'
ESTADOS = {'at', 'riesgo', 'cli', 'inc', 'sin'}
LINEAS = {'parking', 'aero', 'peat', 'vehi', 'compras'}
SECCIONES = {'resumen','proyectos','bulevar','cuenca','pereira','cmsabana','titan','jmc',
              'bulevarplan','diverplaza','plazaclaro','programacion','bl229'}
ISO = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def extraer(texto):
    """Evalua el bloque const DATA = {...} y lo devuelve como diccionario."""
    i = texto.index('const DATA={')
    j = texto.index('\n};', i) + 3
    js = texto[i:j] + '\nconsole.log(JSON.stringify(DATA));'
    tmp = pathlib.Path('/tmp/_data_verif_proy.js'); tmp.write_text(js)
    r = subprocess.run(['node', str(tmp)], capture_output=True, text=True)
    if r.returncode:
        sys.exit('No se pudo evaluar el bloque DATA:\n' + r.stderr)
    return json.loads(r.stdout)


def anterior():
    """El bloque DATA tal como estaba en el ultimo commit, o None."""
    r = subprocess.run(['git', '-C', str(RAIZ), 'show', 'HEAD:index.html'],
                       capture_output=True, text=True)
    if r.returncode:
        return None
    try:
        return extraer(r.stdout)
    except ValueError:
        return None


fallos, avisos = [], []
def chk(cond, ok, mal):
    print(('  OK    ' if cond else '  FALLA ') + (ok if cond else mal))
    if not cond: fallos.append(mal)
def avisa(t):
    print('  AVISO ' + t); avisos.append(t)
def d(s):
    return datetime.date.fromisoformat(s)


def sintaxis():
    """node --check sobre el bloque <script> del informe."""
    txt = HTML.read_text()
    i = txt.index('\n<script>\n'); j = txt.index('\n</script>\n', i)
    tmp = pathlib.Path('/tmp/_chk_proy.js'); tmp.write_text(txt[i + 10:j])
    r = subprocess.run(['node', '--check', str(tmp)], capture_output=True, text=True)
    chk(r.returncode == 0, 'el script del informe compila (node --check)',
        'node --check fallo:\n' + r.stderr.strip())


D = extraer(HTML.read_text())
P = anterior()
R, A, B = D['resumen'], D['resumen']['actual'], D['resumen']['anterior']
PR = D['proyectos']

print('\n── Sintaxis ──')
sintaxis()

print('\n── Fechas del corte ──')
chk(bool(ISO.match(D.get('corte',''))) and bool(ISO.match(D.get('ant',''))),
    f"corte {D.get('corte')} · anterior {D.get('ant')}",
    f"corte o ant no son ISO AAAA-MM-DD: {D.get('corte')} / {D.get('ant')}")
if ISO.match(D.get('corte','')) and ISO.match(D.get('ant','')):
    chk(d(D['corte']) > d(D['ant']), 'el corte es posterior al anterior',
        f"el corte {D['corte']} NO es posterior al anterior {D['ant']}")
    hoy = datetime.date.today()
    chk(d(D['corte']) <= hoy, f"el corte no esta en el futuro (hoy {hoy})",
        f"el corte {D['corte']} esta en el FUTURO (hoy {hoy}) · casi seguro es la fecha del nombre mal leida (va en DDMMAAAA)")
cortes = D.get('cortes', {})
desc = set(cortes) - SECCIONES
chk(not desc, f"claves de DATA.cortes validas ({len(cortes)} seccion(es) desfasada(s))",
    f"DATA.cortes tiene claves desconocidas: {', '.join(sorted(desc))}")
for k, v in sorted(cortes.items()):
    if k not in SECCIONES:
        continue                      # ya conto como FALLA arriba
    chk(bool(ISO.match(str(v))) and d(v) < d(D['corte']),
        f"cortes.{k} = {v}: anterior al corte, correcto",
        f"cortes.{k} = {v}: debe ser ISO y ANTERIOR al corte {D['corte']}; si la pagina vino al dia, borra la clave")

print('\n── Coherencia interna ──')
for nom, o in (('actual', A), ('anterior', B)):
    suma = o['at'] + o['riesgo'] + o['cli'] + o['inc']
    chk(suma <= o['total'],
        f"resumen.{nom}: {suma} con estado de {o['total']} ({o['total']-suma} sin estado)",
        f"resumen.{nom}: los estados suman {suma} y el total es {o['total']}")
    chk(all(o[k] >= 0 for k in ('total','at','riesgo','cli','inc')),
        f"resumen.{nom}: sin negativos", f"resumen.{nom} tiene valores negativos")

for nom, serie in (('clasificacion', D['clasificacion']), ('procesos', D['procesos'])):
    for idx, lbl, esp in ((1, 'corte', A['total']), (2, 'anterior', B['total'])):
        tot = sum(f[idx] for f in serie)
        chk(tot == esp, f"{nom} ({lbl}): suma {tot} = resumen {esp}",
            f"{nom} ({lbl}): suma {tot} ≠ resumen.{'actual' if idx==1 else 'anterior'}.total {esp}")

malos = [p[1] for p in PR if p[3] not in ESTADOS]
chk(not malos, f"los {len(PR)} proyectos usan estados validos",
    f"estado desconocido en: {', '.join(malos)}")
malos = [p[1] for p in PR if p[0] not in LINEAS]
chk(not malos, "todos los proyectos tienen una linea valida",
    f"linea desconocida en: {', '.join(malos)}")
malos = [p[1] for p in PR if not isinstance(p[4], (int, float)) or not 0 <= p[4] <= 100]
chk(not malos, "todos los % de cumplimiento estan entre 0 y 100",
    f"% de cumplimiento fuera de rango en: {', '.join(malos)}")
malos = [f"{p[1]} ({c})" for p in PR for c in (p[5], p[6]) if c is not None and not ISO.match(str(c))]
chk(not malos, "todas las fechas de los proyectos son ISO o null",
    f"fechas que no son ISO AAAA-MM-DD: {', '.join(malos)}")
sinfecha = [p[1] for p in PR if p[3] == 'sin' and p[5]]
chk(not sinfecha, "los proyectos marcados «sin fecha» no traen fecha fin",
    f"marcados «sin fecha» pero con fecha fin: {', '.join(sinfecha)}")
ccs = [p[1].strip() for p in PR]
dup = sorted({c for c in ccs if ccs.count(c) > 1})
if dup: avisa(f"centros de costo repetidos: {', '.join(dup)} · confirma que son proyectos distintos")
else:   print('  OK    no hay centros de costo repetidos')
if len(PR) != A['total']:
    avisa(f"las tablas traen {len(PR)} filas y el resumen dice {A['total']} proyectos "
          f"({A['total']-len(PR)} sin desglosar) · normal, pero confirmalo contra el PDF")
else:
    print(f"  OK    las tablas traen las {len(PR)} filas del resumen")

porlinea = {}
for p_ in PR:
    porlinea[p_[0]] = porlinea.get(p_[0], 0) + 1
print('  INFO  filas por linea: ' + ' · '.join(f"{k} {v}" for k, v in sorted(porlinea.items())) +
      f" · total {len(PR)}")
print('        Cuadralo a mano contra la tarjeta TOTAL de cada pagina del insumo:')
print('        si falta una fila, es una captura de scroll que no se leyo.')

tablas = {}
for p_ in PR:
    tablas[p_[3]] = tablas.get(p_[3], 0) + 1
difs = [f"{k}: resumen {A.get(k)} vs tablas {tablas.get(k, 0)}"
        for k in ('at', 'riesgo', 'cli', 'inc') if A.get(k) != tablas.get(k, 0)]
if difs:
    avisa('el resumen ejecutivo no coincide con la suma de las tablas · ' + ' · '.join(difs) +
          ' · si se publica asi, rellena DATA.discrepancia para que la pagina lo diga')
    if not D.get('discrepancia'):
        chk(False, '', 'hay descuadre entre el resumen y las tablas y DATA.discrepancia esta vacio: '
                       'la pagina mostraria dos cifras contradictorias sin explicarlo')
    else:
        print('  OK    DATA.discrepancia explica el descuadre en la pagina')
else:
    print(f"  OK    el resumen coincide con las tablas en los cuatro estados")

# --- secciones nuevas, solo si vienen ---
if D.get('plazaClaro'):
    C = D['plazaClaro']
    malos = [r[0] for r in C['categorias'] if sum(r[2:]) != r[1]]
    chk(not malos, f"plazaClaro: las {len(C['categorias'])} categorias cierran en su total",
        f"plazaClaro: el desglose no suma el total en {', '.join(malos)}")
if D.get('programacion'):
    G = D['programacion']
    malos = [f[0] for f in G['filas'] if f[1] and f[2] and d(f[1]) > d(f[2])]
    chk(not malos, f"programacion: {len(G['filas'])} filas con fin >= inicio",
        f"programacion: fin anterior al inicio en {', '.join(malos)}")
    fuera = [f[0] for f in G['filas'] if f[1] and (d(f[1]) < d(G['desde']) or d(f[2]) > d(G['hasta']))]
    if fuera: avisa(f"programacion: filas fuera del periodo general declarado: {', '.join(fuera)}")
    sinf = [f[0] for f in G['filas'] if not (f[1] and f[2])]
    if sinf: avisa(f"programacion: sin fechas visibles en el export: {', '.join(sinf)}")
if D.get('bl229'):
    Bl = D['bl229']
    t = sum(f[2] for f in Bl['filas'])
    if t != Bl.get('totalDeclarado'):
        avisa(f"bl229: las filas suman {t} barreras y la hoja declara {Bl.get('totalDeclarado')} · la pagina muestra las dos")
    else:
        print(f"  OK    bl229: las filas suman las {t} barreras declaradas")
if D.get('diverplaza'):
    print(f"  OK    diverplaza: {len(D['diverplaza'])} pendientes")

B_ = D['bulevar']; pz = B_['plazas']
chk(pz['sot1'] + pz['sot2'] == pz['total'],
    f"plazas: {pz['sot1']}+{pz['sot2']} = {pz['total']}",
    f"plazas: {pz['sot1']}+{pz['sot2']} ≠ {pz['total']}")
chk(pz['totSot1'] + pz['totSot2'] == pz['totales'],
    f"plazas totales: {pz['totSot1']}+{pz['totSot2']} = {pz['totales']}",
    f"plazas totales: {pz['totSot1']}+{pz['totSot2']} ≠ {pz['totales']}")
de = B_['descartadas']
malos = [f[0] for f in de['filas'] if sum(f[1:-1]) != f[-1]]
chk(not malos, "descartadas: cada sotano cierra en su total",
    f"descartadas: no cierra el total de {', '.join(malos)}")
cols = [sum(f[i] for f in de['filas']) for i in range(1, len(de['total']))]
chk(cols == de['total'][1:], "descartadas: la fila de total es la suma de los sotanos",
    f"descartadas: total {de['total'][1:]} ≠ suma por columna {cols}")

cr = B_['cronograma']
malos = [r[0] for r in cr if not (ISO.match(r[2]) and ISO.match(r[3])) or d(r[2]) > d(r[3])]
chk(not malos, f"cronograma: las {len(cr)} tareas tienen fechas ISO y fin ≥ inicio",
    f"cronograma: fechas invalidas o fin < inicio en WBS {', '.join(malos)}")
malos = [r[0] for r in cr if not 0 <= r[4] <= 100]
chk(not malos, "cronograma: avances entre 0 y 100",
    f"cronograma: avance fuera de rango en WBS {', '.join(malos)}")
wbs = [r[0] for r in cr]
chk(len(wbs) == len(set(wbs)), "cronograma: WBS sin repetir",
    f"cronograma: WBS repetido: {', '.join(sorted({w for w in wbs if wbs.count(w)>1}))}")
chk(any(r[5] == 0 for r in cr), "cronograma: hay tareas de nivel 0 (de ellas sale el Gantt)",
    "cronograma: ninguna tarea de nivel 0 · el Gantt y el insight de Bulevar quedarian vacios")

malos = [g[0] for g in D['titan']['grupos'] if g[1] > g[2]]
chk(not malos, f"titan: {sum(g[2]-g[1]+1 for g in D['titan']['grupos'])} equipos, rangos correctos",
    f"titan: rango invertido en {', '.join(malos)}")
malos = [h[0] for h in D['jmc']['hitos'] if h[1] is not None and not ISO.match(str(h[1]))]
chk(not malos, "jmc: fechas de los hitos ISO o null",
    f"jmc: fechas invalidas en {', '.join(malos)}")

print('\n── Contra la version publicada ──')
if not P:
    avisa('no se pudo leer la version anterior; sin comparacion')
else:
    sucio = subprocess.run(['git', '-C', str(RAIZ), 'diff', '--quiet', '--', 'index.html']).returncode != 0
    if D['corte'] != P.get('corte'):
        print(f"  OK    el corte avanzo: {P.get('corte')} → {D['corte']}")
    elif sucio:
        chk(False, '', f"hay cambios sin publicar pero el corte sigue en {D['corte']}")
    else:
        avisa(f"el corte {D['corte']} ya esta publicado; esta comparacion es contra si misma. "
              "Ejecuta este script ANTES del commit.")

    # El «anterior» de esta semana tiene que ser el «actual» que se publico.
    # Es el equivalente de los meses ya cerrados: si se movio, es una mala lectura.
    if D['corte'] != P.get('corte'):
        chk(D['ant'] == P.get('corte'),
            f"ant {D['ant']} = corte publicado {P.get('corte')}",
            f"ant {D['ant']} ≠ corte publicado {P.get('corte')} · la comparacion de la pagina seria falsa")
        dif = [f"{k} {P['resumen']['actual'][k]}→{B[k]}" for k in ('total','at','riesgo','cli','inc')
               if P['resumen']['actual'].get(k) != B.get(k)]
        chk(not dif, "resumen.anterior coincide con el actual publicado",
            f"resumen.anterior cambio respecto al actual publicado: {', '.join(dif)} · casi seguro es una lectura equivocada")
        for nom in ('clasificacion', 'procesos'):
            viejo = {f[0]: f[1] for f in P[nom]}
            dif = [f"{f[0]} {viejo[f[0]]}→{f[2]}" for f in D[nom] if f[0] in viejo and viejo[f[0]] != f[2]]
            if dif: avisa(f"{nom}: la columna «anterior» no coincide con lo publicado: {', '.join(dif)} · confirmalo contra el PDF")
            else:   print(f"  OK    {nom}: la columna «anterior» coincide con lo publicado")

        if A == P['resumen']['actual']:
            avisa('el resumen ejecutivo es identico al de la semana pasada pero el corte avanzo · revisa el Paso 2, la pagina pudo venir congelada')
        if D['proyectos'] == P.get('proyectos'):
            avisa('las tablas de proyectos son identicas a las de la semana pasada · revisa el Paso 2')

    # Un proyecto no deberia retroceder en avance ni desaparecer sin aviso.
    viejo = {p[1].strip(): p for p in P.get('proyectos', [])}
    nuevo = {p[1].strip(): p for p in PR}
    ido = sorted(set(viejo) - set(nuevo))
    if ido: avisa(f"proyectos que ya no estan en las tablas: {', '.join(ido)} · confirma que salieron de verdad")
    retro = [f"{cc} {viejo[cc][4]}%→{nuevo[cc][4]}%" for cc in nuevo if cc in viejo and nuevo[cc][4] < viejo[cc][4]]
    if retro: avisa(f"proyectos cuyo % de cumplimiento BAJO: {', '.join(retro)} · confirmalo contra el PDF")
    else:     print('  OK    ningun proyecto retrocedio en % de cumplimiento')

    # Las secciones marcadas como desfasadas no deben haber cambiado.
    LLAVE = {'cuenca':'cuenca','pereira':'pereira','cmsabana':'cmSabana','titan':'titan','jmc':'jmc'}
    # `bulevar` son las tareas; `bulevarplan`, las plazas y el cronograma.
    # Pueden venir de cortes distintos, asi que se comparan por separado.
    SUB = {'bulevar': ('tareas',), 'bulevarplan': ('plazas', 'descartadas', 'cronograma')}
    for sec, f in sorted(cortes.items()):
        if sec in SUB:
            viejo_b, nuevo_b = P.get('bulevar', {}), D.get('bulevar', {})
            movidas = [x for x in SUB[sec] if x in viejo_b and viejo_b.get(x) != nuevo_b.get(x)]
            if movidas:
                chk(False, '', f"cortes.{sec} dice que eso vino desfasado ({f}) pero cambio: {', '.join(movidas)}")
            else:
                print(f"  OK    cortes.{sec}: {', '.join(SUB[sec])} conserva(n) los valores publicados")
            continue
        k = LLAVE.get(sec)
        if k and k in P and D.get(k) != P.get(k):
            chk(False, '', f"cortes.{sec} dice que esa pagina vino desfasada ({f}) pero sus datos CAMBIARON · no se transcribe una seccion desfasada")
        elif k:
            print(f"  OK    cortes.{sec}: la seccion conserva los valores publicados")

# corte.txt: el unico sitio donde el corte viaja en texto plano servible.
# Lo escribe el script, no la mano, para que no pueda discrepar de DATA.corte.
CORTE_TXT_FILE = RAIZ / 'corte.txt'
if not fallos and ISO.match(D.get('corte', '')):
    previo = CORTE_TXT_FILE.read_text().strip() if CORTE_TXT_FILE.exists() else None
    CORTE_TXT_FILE.write_text(D['corte'] + '\n')
    print('\n── corte.txt ──')
    print(f"  OK    corte.txt escrito con {D['corte']}" +
          (f" (antes {previo})" if previo and previo != D['corte'] else ''))
    print('        Acuerdate de incluirlo en el commit: es lo que se consulta')
    print('        para dar el despliegue por bueno en el Paso 5.')

print('\n── Resultado ──')
if fallos:
    print(f"  {len(fallos)} FALLO(S). No publiques."); sys.exit(1)
print("  Sin fallos." + (f" {len(avisos)} aviso(s) para confirmar a ojo." if avisos else " Listo para publicar."))
