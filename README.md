# Sistema Experto: Diagnóstico de PC

Motor de inferencia hacia adelante implementado en Python puro para diagnóstico de problemas técnicos en computadoras.

---

## Componentes del Sistema Experto

### 1. Base de Conocimiento
Contiene 7 reglas IF-THEN definidas como diccionarios Python. Cada regla tiene `id`, `descripcion`, `condiciones` (síntomas requeridos), `conclusion` y un factor de `confianza` entre 0 y 1. Es el repositorio del conocimiento del experto técnico.

### 2. Base de Hechos (Working Memory)
Un `set()` de Python que almacena los síntomas confirmados por el usuario durante la sesión. Se vacía al iniciar cada nuevo diagnóstico con `.clear()`.

### 3. Motor de Inferencia
Compuesto por tres funciones:
- `equiparar()`: compara los hechos actuales contra todas las reglas usando `issubset()`. Retorna el *conflict set* (reglas que aplican).
- `resolver_conflictos()`: selecciona la regla ganadora por mayor confianza; desempata por número de condiciones (más específica gana).
- `inferir()`: ejecuta el ciclo completo equiparar → resolver → mostrar resultado.

### 4. Interfaz de Explicación
Integrada dentro de `inferir()`. Muestra qué síntomas activaron la regla seleccionada y qué otras reglas fueron descartadas y por qué (menor confianza).

### 5. Interfaz de Usuario
Menú interactivo con 4 opciones. `PREGUNTAS` es un diccionario que mapea cada síntoma a una pregunta en lenguaje natural. El usuario responde `s/n`.

---

## Ajustes Realizados

| Ajuste | Justificación |
|---|---|
| Se agregó `import json` | Necesario para L4; el código original no lo incluía |
| `base_de_hechos.clear()` en `consultar()` | Sin esto, los hechos de una sesión anterior contaminaban la siguiente |
| Se refactorizó `consultar()` como función | El código original llamaba directamente a `consultar()` sin menú; imposible reutilizar |
| Se agregó `menu_principal()` | Permite navegar entre inferencia hacia adelante, L3 y L4 sin reiniciar |

---

## Desafíos Implementados

### L3 — Encadenamiento hacia Atrás (`backward_chain`)

**Qué hace:** dado un diagnóstico específico (meta), determina qué síntomas hay que confirmar para llegar a él, en lugar de partir de síntomas hacia una conclusión.

**Cómo funciona:**
1. Busca qué regla produce la conclusión buscada.
2. Por cada condición de esa regla: si ya está en hechos → confirmada; si no → pregunta al usuario.
3. Si todas las condiciones se confirman → meta probada.
4. Es recursiva: una condición podría ser conclusión de otra regla.
5. El parámetro `visitados` evita ciclos infinitos.

**Justificación:** permite al técnico partir de una hipótesis ("creo que es sobrecalentamiento") y que el sistema le diga exactamente qué verificar para confirmarla, en lugar de responder todas las preguntas.

---

### L4 — Exportar Red de Inferencia (`exportar_red`)

**Qué hace:** recorre la base de conocimiento y construye un grafo con nodos y aristas, exportado como JSON.

**Estructura:**
- **Nodos:** cada síntoma (`tipo: "sintoma"`) y cada conclusión (`tipo: "conclusion"`). Sin duplicados (controlado con un `set`).
- **Aristas:** cada regla como conexión entre sus condiciones y su conclusión, incluyendo `confianza`.

**Justificación:** permite visualizar externamente (con herramientas como Gephi o D3.js) cómo fluye el razonamiento del sistema. También sirve para auditar la base de conocimiento y detectar síntomas o conclusiones huérfanas.

---

