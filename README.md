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

**Justificación:** permite visualizar externamente cómo fluye el razonamiento del sistema. También sirve para auditar la base de conocimiento y detectar síntomas o conclusiones huérfanas.

---

## Preguntas de Reflexión

**1. ¿Cuál es la diferencia principal entre un sistema experto y un programa de software tradicional?**

Un programa tradicional ejecuta lógica fija codificada por el programador. Un sistema experto separa el conocimiento (reglas) del motor que las procesa: las reglas pueden modificarse sin tocar el motor. Además, el sistema experto puede explicar por qué llegó a una conclusión, algo que un programa tradicional no hace.

---

**2. ¿Por qué se dice que los sistemas expertos tienen conocimiento separado de su motor de razonamiento? ¿Cuál es la ventaja?**

La base de conocimiento (reglas) y el motor de inferencia son módulos independientes. Se pueden agregar, quitar o modificar reglas sin alterar el motor. Esto permite que un experto del dominio (médico, técnico) actualice el conocimiento sin necesidad de saber programar.

---

**3. ¿Qué es la base de hechos y en qué se diferencia de la base de conocimiento?**

La base de hechos contiene el estado actual del caso: los síntomas observados en esta sesión específica. Es dinámica, cambia con cada consulta. La base de conocimiento contiene las reglas generales permanentes que no cambian entre casos.

---

**4. ¿Qué significa que un sistema experto pueda "explicar su razonamiento"? ¿Por qué es importante en medicina o derecho?**

Significa que puede mostrar qué reglas aplicó, qué hechos las activaron y por qué descartó otras opciones. En medicina o derecho esto es crítico: una decisión sin justificación no puede auditarse, cuestionarse ni defenderse legalmente. El médico o juez necesita saber el porqué, no solo el resultado.

---

**5. ¿Por qué fracasaron comercialmente los sistemas expertos en los años 90? Menciona al menos 3 razones.**

1. **Costo de mantenimiento:** actualizar la base de conocimiento requería entrevistar expertos humanos constantemente, proceso caro y lento.
2. **Fragilidad fuera del dominio:** funcionaban bien en su área específica pero fallaban ante casos ligeramente fuera de lo previsto; no generalizaban.
3. **Cuello de botella del conocimiento:** extraer el conocimiento tácito de un experto humano y convertirlo en reglas formales era extremadamente difícil.

---

**6. Dada la regla: SI (fiebre AND tos) OR perdida_olfato ENTONCES sospecha_covid, con hechos {fiebre=True, tos=False, perdida_olfato=True} — ¿Se activa la regla?**

Sí. La expresión evalúa:
- `(fiebre AND tos)` → `True AND False` → `False`
- `perdida_olfato` → `True`
- `False OR True` → **True**

La regla se activa porque `perdida_olfato` por sí sola satisface la condición OR.

---

**7. Tabla de verdad para (A AND NOT B) OR (NOT A AND B)**

Esta expresión es XOR (exclusivo): verdadera cuando A y B tienen valores distintos.

| A | B | NOT B | NOT A | A AND NOT B | NOT A AND B | Resultado |
|---|---|---|---|---|---|---|
| F | F | T | T | F | F | **F** |
| F | T | F | T | F | T | **T** |
| T | F | T | F | T | F | **T** |
| T | T | F | F | F | F | **F** |

---

**8. ¿Cuál es la diferencia entre encadenamiento hacia adelante y hacia atrás? Da un ejemplo real de cada uno.**

| | Hacia adelante | Hacia atrás |
|---|---|---|
| Punto de partida | Hechos conocidos | Meta/hipótesis |
| Dirección | Hechos → Conclusión | Conclusión → Hechos necesarios |
| Pregunta que responde | "¿Qué puedo concluir?" | "¿Qué necesito para probar X?" |

**Ejemplo hacia adelante:** un técnico observa que el PC no enciende, no tiene luces ni sonido → el sistema concluye falla en fuente de poder.

**Ejemplo hacia atrás:** un médico sospecha neumonía → el sistema le pregunta si el paciente tiene fiebre, tos con flema y dolor torácico para confirmar o descartar la hipótesis.

---

**9. Diseñá 3 reglas IF-THEN para asesorar sobre qué lenguaje aprender primero**

```
R01: SI objetivo = desarrollo_web AND preferencia = frontend
     ENTONCES aprender JavaScript
     [Confianza: 0.95]

R02: SI objetivo = analisis_datos AND gusto_por_matematicas = true
     ENTONCES aprender Python
     [Confianza: 0.93]

R03: SI objetivo = videojuegos AND plataforma = escritorio
     ENTONCES aprender C++
     [Confianza: 0.88]
```

---

**10. Red de inferencia de las 3 reglas anteriores**

```
[desarrollo_web] ──┐
[frontend]  ───────┴──► (R01) ──► [Aprender JavaScript]

[analisis_datos] ──┐
[gusto_matematicas]┴──► (R02) ──► [Aprender Python]

[videojuegos] ─────┐
[plataforma_pc] ───┴──► (R03) ──► [Aprender C++]
```

Cada par de nodos de síntoma converge en una regla (nodo intermedio) que apunta a un nodo de conclusión.

---

**11. ¿Qué problema surge si dos reglas tienen las mismas condiciones pero conclusiones diferentes? ¿Cómo lo resolverías?**

Es un conflicto de ambigüedad: ambas reglas se activan siempre juntas y el sistema no puede decidir cuál aplicar con criterio técnico válido. Con la estrategia actual (mayor confianza) siempre ganaría la misma, ignorando la otra permanentemente.

Soluciones:
- **Asignar confianzas distintas** basadas en evidencia estadística real.
- **Agregar condiciones diferenciadoras** a cada regla para que no sean idénticas.
- **Retornar ambas conclusiones** como diagnósticos posibles con sus probabilidades (cambio al modelo de múltiples diagnósticos, similar al desafío L2).