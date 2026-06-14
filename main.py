# ================================================================
# SISTEMA EXPERTO: Diagnóstico de PC
# Implementación con motor de inferencia hacia adelante
# Extensiones: L3 (Encadenamiento hacia atrás) + L4 (Exportar red)
# ================================================================

import json

# ──────────────────────────────────────────────────────────────
# COMPONENTE 1: BASE DE CONOCIMIENTO
# Cada regla: id, condiciones (síntomas requeridos),
# conclusión y factor de confianza 0-1.
# ──────────────────────────────────────────────────────────────

base_de_conocimiento = [
    {
        "id": "R01",
        "descripcion": "Fuente de poder dañada",
        "condiciones": ["no_enciende", "sin_luces", "sin_sonido"],
        "conclusion": "Revisar o reemplazar la fuente de poder",
        "confianza": 0.92
    },
    {
        "id": "R02",
        "descripcion": "Falla de RAM",
        "condiciones": ["enciende", "pitidos_arranque", "sin_video"],
        "conclusion": "Probar con módulos de RAM de a uno",
        "confianza": 0.88
    },
    {
        "id": "R03",
        "descripcion": "Falla de tarjeta de video",
        "condiciones": ["enciende", "pantalla_negra", "sin_pitidos"],
        "conclusion": "Revisar tarjeta de video y conexiones del monitor",
        "confianza": 0.80
    },
    {
        "id": "R04",
        "descripcion": "Problemas de almacenamiento",
        "condiciones": ["enciende", "inicia_lento", "disco_al_100"],
        "conclusion": "Verificar salud del disco duro con herramienta SMART",
        "confianza": 0.85
    },
    {
        "id": "R05",
        "descripcion": "Infección por malware",
        "condiciones": ["enciende", "inicia_lento", "ventilador_siempre_activo"],
        "conclusion": "Escanear con antivirus y revisar procesos en segundo plano",
        "confianza": 0.72
    },
    {
        "id": "R06",
        "descripcion": "Driver o RAM dañada",
        "condiciones": ["enciende", "pantalla_azul_frecuente"],
        "conclusion": "Actualizar drivers y testear memoria RAM con MemTest86",
        "confianza": 0.87
    },
    {
        "id": "R07",
        "descripcion": "Sobrecalentamiento",
        "condiciones": ["enciende", "se_apaga_solo", "calor_excesivo"],
        "conclusion": "Limpiar ventiladores y reaplicar pasta térmica",
        "confianza": 0.90
    },
]


# ──────────────────────────────────────────────────────────────
# COMPONENTE 2: BASE DE HECHOS (Working Memory)
# Set de síntomas confirmados por el usuario.
# ──────────────────────────────────────────────────────────────

base_de_hechos = set()


# ──────────────────────────────────────────────────────────────
# COMPONENTE 3: MOTOR DE INFERENCIA
# ──────────────────────────────────────────────────────────────

def equiparar(base_conocimiento, hechos):
    """
    Pattern matching: retorna todas las reglas cuyas condiciones
    están completamente satisfechas por los hechos actuales.
    Resultado = conflict set.
    """
    conflict_set = []
    for regla in base_conocimiento:
        if set(regla['condiciones']).issubset(hechos):
            conflict_set.append(regla)
    return conflict_set


def resolver_conflictos(conflict_set):
    """
    Estrategia: mayor confianza. Desempate: más condiciones (más específica).
    Retorna una sola regla ganadora.
    """
    if not conflict_set:
        return None
    return max(
        conflict_set,
        key=lambda r: (r['confianza'], len(r['condiciones']))
    )


def inferir(base_conocimiento, hechos):
    """
    Ciclo principal: equiparar → resolver → ejecutar → explicar.
    """
    print()
    print('━' * 55)
    print('  MOTOR DE INFERENCIA INICIADO')
    print('━' * 55)
    print(f'  Hechos ingresados: {hechos}')
    print()

    conflict_set = equiparar(base_conocimiento, hechos)

    if not conflict_set:
        print('  ⚠ No se encontraron reglas aplicables.')
        print('  Considera agregar más síntomas o revisar la base de conocimiento.')
        return

    print(f'  Reglas que aplican (conflict set): {[r["id"] for r in conflict_set]}')
    print()

    regla = resolver_conflictos(conflict_set)

    print('  DIAGNÓSTICO')
    print('  ' + '─' * 51)
    print(f'  Regla aplicada: {regla["id"]} — {regla["descripcion"]}')
    print(f'  Recomendación:  {regla["conclusion"]}')
    print(f'  Confianza:      {regla["confianza"] * 100:.0f}%')
    print()

    # COMPONENTE 4: INTERFAZ DE EXPLICACIÓN
    print('  TRAZABILIDAD DEL RAZONAMIENTO')
    print('  ' + '─' * 51)
    print(f'  Síntomas que activaron la regla: {regla["condiciones"]}')
    if len(conflict_set) > 1:
        descartadas = [r['id'] for r in conflict_set if r['id'] != regla['id']]
        print(f'  Reglas descartadas por menor confianza: {descartadas}')
    print('━' * 55)


# ──────────────────────────────────────────────────────────────
# EXTENSIÓN L3: ENCADENAMIENTO HACIA ATRÁS
#
# Dado un diagnóstico (meta/conclusión), el sistema determina
# qué síntomas se necesitan confirmar para llegar a él.
#
# Lógica:
#   1. Busca en la base qué regla(s) producen esa conclusión.
#   2. Por cada condición de esa regla:
#      - Si ya está en hechos → confirmada.
#      - Si no está → pregunta al usuario.
#   3. Al final reporta si la meta es alcanzable con los hechos.
#
# Es recursiva porque una condición podría ser conclusión de
# otra regla (encadenamiento en cadena). visited evita loops.
# ──────────────────────────────────────────────────────────────

def backward_chain(meta, base_conocimiento, hechos, visitados=None):
    """
    Encadenamiento hacia atrás.

    Parámetros:
        meta            : string con la conclusión que se quiere probar
        base_conocimiento: lista de reglas
        hechos          : set de síntomas actuales (se modifica en lugar)
        visitados       : set interno para evitar recursión infinita

    Retorna:
        True  → la meta puede probarse con los hechos actuales/confirmados
        False → no hay regla que lleve a esa meta o el usuario negó síntomas
    """
    if visitados is None:
        visitados = set()

    # Evitar ciclos: si ya intentamos probar esta meta, salir
    if meta in visitados:
        return False
    visitados.add(meta)

    # Si la meta ya está en hechos directamente, está confirmada
    if meta in hechos:
        return True

    # Buscar reglas que concluyan en la meta
    reglas_aplicables = [
        r for r in base_conocimiento if r['conclusion'] == meta
    ]

    if not reglas_aplicables:
        # La meta no es conclusión de ninguna regla → preguntar directamente
        resp = input(f'\n  [Backward] ¿Confirmas el síntoma "{meta}"? [s/n]: ').strip().lower()
        if resp == 's':
            hechos.add(meta)
            return True
        return False

    # Intentar cada regla que produce la meta
    for regla in reglas_aplicables:
        print(f'\n  [Backward] Intentando regla {regla["id"]}: {regla["descripcion"]}')
        todas_confirmadas = True

        for condicion in regla['condiciones']:
            # Intentar probar cada condición (recursivo)
            if not backward_chain(condicion, base_conocimiento, hechos, visitados):
                todas_confirmadas = False
                break  # Esta regla no funciona, probar la siguiente

        if todas_confirmadas:
            print(f'\n  ✔ Meta alcanzada: "{meta}"')
            print(f'    Vía regla {regla["id"]} — {regla["descripcion"]}')
            return True

    return False


def iniciar_backward_chain(base_conocimiento, hechos):
    """
    Interfaz de usuario para el encadenamiento hacia atrás.
    Muestra las conclusiones disponibles y deja elegir una meta.
    """
    print()
    print('=' * 55)
    print('  ENCADENAMIENTO HACIA ATRÁS')
    print('  ¿Qué diagnóstico querés verificar?')
    print('=' * 55)

    # Listar todas las conclusiones disponibles
    conclusiones = [(r['id'], r['descripcion'], r['conclusion']) for r in base_conocimiento]
    for i, (rid, desc, conc) in enumerate(conclusiones):
        print(f'  {i+1}. [{rid}] {desc}')
        print(f'      → {conc}')

    print()
    try:
        opcion = int(input('  Elegí un número: ').strip()) - 1
        if opcion < 0 or opcion >= len(conclusiones):
            print('  Opción inválida.')
            return
    except ValueError:
        print('  Entrada inválida.')
        return

    meta = conclusiones[opcion][2]  # la conclusión (string)
    print(f'\n  Intentando probar: "{meta}"')
    print('  ' + '─' * 51)

    resultado = backward_chain(meta, base_conocimiento, hechos)

    print()
    print('━' * 55)
    if resultado:
        print(f'  ✔ CONFIRMADO: El diagnóstico es alcanzable.')
        print(f'  Hechos confirmados durante el proceso: {hechos}')
    else:
        print(f'  ✘ NO CONFIRMADO: No se pudo probar el diagnóstico.')
    print('━' * 55)


# ──────────────────────────────────────────────────────────────
# EXTENSIÓN L4: EXPORTAR RED DE INFERENCIA
#
# Recorre la base de conocimiento y construye un grafo:
#   - Nodos: cada síntoma (hecho) y cada conclusión
#   - Aristas: cada regla conecta sus condiciones → conclusión
#
# Útil para visualizar cómo fluye el razonamiento del sistema.
# Se exporta como JSON estándar.
# ──────────────────────────────────────────────────────────────

def exportar_red(base_conocimiento):
    """
    Genera y retorna un dict representando el grafo de inferencia.

    Estructura del grafo:
        {
          "nodos": [
              {"id": "no_enciende", "tipo": "sintoma"},
              {"id": "Revisar fuente...", "tipo": "conclusion"},
              ...
          ],
          "aristas": [
              {
                "regla": "R01",
                "descripcion": "Fuente de poder dañada",
                "condiciones": [...],
                "conclusion": "...",
                "confianza": 0.92
              },
              ...
          ]
        }
    """
    nodos_set = set()   # Para evitar nodos duplicados
    nodos = []
    aristas = []

    for regla in base_conocimiento:
        # Agregar cada condición como nodo tipo "sintoma"
        for condicion in regla['condiciones']:
            if condicion not in nodos_set:
                nodos_set.add(condicion)
                nodos.append({"id": condicion, "tipo": "sintoma"})

        # Agregar la conclusión como nodo tipo "conclusion"
        if regla['conclusion'] not in nodos_set:
            nodos_set.add(regla['conclusion'])
            nodos.append({"id": regla['conclusion'], "tipo": "conclusion"})

        # Agregar la arista: condiciones → conclusion via esta regla
        aristas.append({
            "regla": regla['id'],
            "descripcion": regla['descripcion'],
            "condiciones": regla['condiciones'],
            "conclusion": regla['conclusion'],
            "confianza": regla['confianza']
        })

    red = {"nodos": nodos, "aristas": aristas}
    return red


def mostrar_red(base_conocimiento):
    """
    Llama a exportar_red() e imprime el resultado como JSON formateado.
    """
    print()
    print('=' * 55)
    print('  RED DE INFERENCIA (JSON)')
    print('=' * 55)
    red = exportar_red(base_conocimiento)
    print(json.dumps(red, ensure_ascii=False, indent=2))
    print('=' * 55)


# ──────────────────────────────────────────────────────────────
# COMPONENTE 5: INTERFAZ DE USUARIO
# ──────────────────────────────────────────────────────────────

PREGUNTAS = {
    "no_enciende":               "¿El equipo NO enciende (sin luces, sin sonido)?",
    "sin_luces":                 "¿No hay ninguna luz LED encendida?",
    "sin_sonido":                "¿No se escucha ningún sonido al encender?",
    "enciende":                  "¿El equipo SÍ enciende (hay luces y/o sonido)?",
    "pitidos_arranque":          "¿Se escuchan pitidos (beeps) al encender?",
    "sin_video":                 "¿La pantalla no muestra absolutamente nada?",
    "pantalla_negra":            "¿La pantalla queda en negro (sin pitidos)?",
    "sin_pitidos":               "¿No se escuchan pitidos?",
    "inicia_lento":              "¿El equipo tarda más de 3 minutos en iniciar?",
    "disco_al_100":              "¿El administrador de tareas muestra disco al 100%?",
    "ventilador_siempre_activo": "¿El ventilador está siempre a máxima velocidad?",
    "pantalla_azul_frecuente":   "¿Aparece pantalla azul (BSOD) con frecuencia?",
    "se_apaga_solo":             "¿El equipo se apaga solo sin advertencia?",
    "calor_excesivo":            "¿El chasis está muy caliente al tacto?"
}


def menu_principal():
    """
    Menú de entrada que permite elegir entre los modos disponibles.
    """
    print()
    print('=' * 55)
    print('  SISTEMA EXPERTO: Diagnóstico de Computador')
    print('=' * 55)
    print('  1. Diagnóstico por síntomas (inferencia hacia adelante)')
    print('  2. Verificar diagnóstico específico (hacia atrás) [L3]')
    print('  3. Ver red de inferencia en JSON [L4]')
    print('  4. Salir')
    print('=' * 55)
    return input('  Opción: ').strip()


def consultar():
    """
    Flujo de inferencia hacia adelante: pregunta síntomas y diagnostica.
    """
    print()
    print('  Responde s (sí) o n (no) a cada pregunta')
    print()
    base_de_hechos.clear()  # Limpiar hechos anteriores

    for sintoma, pregunta in PREGUNTAS.items():
        resp = input(f'  {pregunta} [s/n]: ').strip().lower()
        if resp == 's':
            base_de_hechos.add(sintoma)

    inferir(base_de_conocimiento, base_de_hechos)


# ──────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ──────────────────────────────────────────────────────────────

def main():
    while True:
        opcion = menu_principal()

        if opcion == '1':
            consultar()
        elif opcion == '2':
            iniciar_backward_chain(base_de_conocimiento, base_de_hechos)
        elif opcion == '3':
            mostrar_red(base_de_conocimiento)
        elif opcion == '4':
            print('\n  Saliendo...\n')
            break
        else:
            print('\n  Opción inválida.')


main()