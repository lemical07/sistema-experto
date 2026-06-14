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

