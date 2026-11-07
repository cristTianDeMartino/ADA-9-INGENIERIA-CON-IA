# ADA-08: Agent-Ready Repository

Auditoría de preparación para agentes, mejoras operativas y evaluación comparativa BEFORE / AFTER sobre el sistema Customer Search.

## Resumen de resultados

- Baseline (BEFORE): 47 / 100 puntos.
- Repositorio optimizado (AFTER): 96 / 100 puntos.
- Delta total: +49 puntos.
- Suite de pruebas: 44 pruebas unitarias e integración en 0.04s.
- Verificación automatizada: script unificado `./scripts/verify_repo.sh` compartido entre humanos, agentes y CI.

## Estructura del repositorio

```
ada-08-agentreadyrepo/
├── AGENTS.md                          # Contrato operativo y fuentes de verdad
├── README.md                          # Documentación del proyecto y reflexiones
├── REQUIREMENTS.md                    # Especificación de requisitos funcionales y no funcionales
├── SPEC.md                            # Especificación técnica y criterios de aceptación
├── ARCHITECTURE.md                    # Diseño arquitectónico y capas
├── TASKS.md                           # Desglose de tareas del sistema
├── TASK_UNDER_TEST.md                 # Tarea controlada de prueba (CR-01: active_only)
├── GEMINI.md                          # Adaptador para el agente sin duplicar requisitos
├── requirements.txt                   # Dependencias mínimas versionadas
├── REPOSITORY_READINESS_AUDIT.md      # Auditoría detallada BEFORE / AFTER y registro de mejoras
├── AI_USAGE_LOG.md                    # Bitácora de decisiones y supervisión de IA
├── .github/
│   └── workflows/
│       └── verify.yml                 # Pipeline de CI que invoca verify_repo.sh
├── docs/
│   ├── REPO_MAP.md                    # Mapa de navegación, puntos de entrada y rutas protegidas
│   └── traceability.md                # Matriz de trazabilidad
├── scripts/
│   ├── verify_repo.sh                 # Contrato ejecutable único (tests, sintaxis, contrato)
│   └── check_repo_contract.py         # Guardrail determinista de integridad del repo
├── src/
│   └── customer_search/
│       ├── __init__.py
│       ├── cli.py                     # Interfaz CLI con soporte para --active-only
│       ├── exceptions.py              # Excepciones de dominio y validación
│       ├── models.py                  # Entidades Customer y SearchResult
│       ├── repository.py              # Repositorio en memoria y carga JSON
│       ├── service.py                 # Servicio de búsqueda con parámetro active_only
│       └── validator.py               # Validador de consultas
├── tests/                             # Suite automatizada (44 pruebas)
└── results/
    ├── before-agent-run.md            # Registro de ejecución BEFORE
    ├── implicit-knowledge.md          # Registro de conocimiento tribal detectado
    ├── after-agent-run.md             # Registro de ejecución AFTER
    └── readiness-improvement-report.md# Comparativa técnica BEFORE vs AFTER
```

## Instrucciones de ejecución y verificación

### 1. Instalación de dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecución del sistema (CLI)
```bash
# Búsqueda unificada predeterminada
python3 -m src.customer_search.cli "garcia"

# Búsqueda filtrando únicamente clientes activos
python3 -m src.customer_search.cli "garcia" --active-only

# Salida en formato JSON
python3 -m src.customer_search.cli "garcia" --active-only --json
```

### 3. Ejecución del contrato de verificación
```bash
./scripts/verify_repo.sh
```
El script valida en una sola llamada:
1. Suite completa de pruebas con `pytest`.
2. Compilación y sintaxis de Python con `compileall`.
3. Integridad del contrato del repositorio, presencia de archivos requeridos y ausencia de secretos con `check_repo_contract.py`.

## Reflexión individual (Sección 26)

### 1. ¿Cuál fue el principal obstáculo para el agente en la ejecución BEFORE?
El obstáculo principal fue la falta de un mapa directo de navegación y de comandos estándar de verificación. El agente tuvo que inspeccionar manualmente múltiples archivos para ubicar los puntos de entrada del código y asumió incorrectamente que existía un fixture en pytest, lo que provocó una falla inicial en la prueba de integración.

### 2. ¿Qué información tuvo que inferir el agente que un desarrollador experimentado ya conocía?
Tuvo que inferir que el entorno local contenía pytest preinstalado, que `data/customers.json` funcionaba como fixture de prueba intocable para las búsquedas predeterminadas del CLI, y que el comando de prueba no requería flags adicionales ni un linter previo.

### 3. ¿Qué mejora produjo el mayor impacto y por qué?
El script unificado `./scripts/verify_repo.sh`. Al empaquetar la ejecución de pruebas, la compilación de sintaxis y la validación de contratos en una sola llamada con códigos de salida deterministas, eliminó la incertidumbre sobre cuándo un cambio cumple los criterios de aceptación.

### 4. ¿Qué información pertenece en AGENTS.md y qué información NO debería vivir ahí?
En `AGENTS.md` deben vivir el orden de lectura, las referencias a las fuentes de verdad, los comandos estándar reproducibles, las reglas de modificación, las condiciones de parada y la definición de terminado. No deben vivir en `AGENTS.md` las especificaciones funcionales completas, la lógica de negocio detallada ni duplicados de los requisitos de `REQUIREMENTS.md`, pues duplicar información genera desincronización cuando el software evoluciona.

### 5. ¿Qué regla convertiste en software/hook/script en lugar de dejarla como instrucción?
La verificación de integridad de archivos y rutas protegidas se convirtió en `scripts/check_repo_contract.py`. En lugar de pedirle al modelo por texto que no agregue secretos o que mantenga intacto `data/customers.json`, el script inspecciona el árbol de archivos en busca de patrones sensibles, comprueba que el dataset conserve formato JSON válido y valida que `SPEC.md` incluya los identificadores de requisitos.

### 6. ¿Qué diferencia observaste entre 'más contexto' y 'mejor contexto'?
Más contexto satura la ventana de atención con explicaciones históricas o asignaciones pedagógicas que no orientan la acción. Mejor contexto estructura la información mínima necesaria en el punto donde se requiere, mediante un mapa de repositorio directo (`docs/REPO_MAP.md`), comandos oficiales verificables y límites de modificación claros.

### 7. ¿Qué riesgo aparece cuando CLAUDE.md/GEMINI.md/copilot instructions duplican información del proyecto?
Aparece el riesgo de desincronización y contradicción entre fuentes. Si los requisitos se editan en el archivo principal pero se omiten en el archivo específico del asistente, los agentes ejecutan supuestos obsoletos. Por eso estos archivos deben funcionar como adaptadores que delegan en `AGENTS.md`.

### 8. ¿Qué checks comparten ahora el agente, el desarrollador humano y CI?
Comparten exactamente el mismo contrato ejecutable: `./scripts/verify_repo.sh`. Los tres ejecutan la suite de pytest, la comprobación de sintaxis con `python3 -m compileall` y la validación determinista del contrato del repositorio con `scripts/check_repo_contract.py`.

### 9. ¿Qué parte del proceso sigue requiriendo decisión humana?
La aprobación de cambios arquitectónicos, la adición de nuevas dependencias externas, la redefinición de contratos en `REQUIREMENTS.md` y la autorización para modificar archivos sensibles o rutas protegidas.

### 10. ¿Qué evidencia demuestra que el AFTER es realmente mejor?
La evidencia cuantitativa muestra que el puntaje de readiness subió de 47/100 a 96/100 (+49 puntos). La evidencia operativa muestra cero comandos fallidos en AFTER frente a una falla en BEFORE, cero suposiciones erróneas sobre fixtures y la verificación exitosa de 44 pruebas y contratos en una sola corrida de 0.04 segundos.

### 11. ¿Qué mejora realizada para el agente también beneficia a un desarrollador que entra por primera vez al proyecto?
El mapa de repositorio (`docs/REPO_MAP.md`) y el script único de verificación (`./scripts/verify_repo.sh`). Un nuevo colaborador puede ubicar inmediatamente los puntos de entrada y ejecutar la validación completa del proyecto sin depender de explicaciones verbales ni adivinar dependencias.

### 12. ¿Qué variable no controlada podría afectar tu comparación BEFORE/AFTER?
La variabilidad estocástica en la generación del modelo de lenguaje y la presencia de dependencias preinstaladas en el entorno global del sistema operativo (como pytest en Homebrew), que permitieron la ejecución de pruebas en BEFORE a pesar de no existir un archivo de requerimientos versionado.

### 13. ¿Qué elementos de este ADA conservarás como base para tu proyecto final?
Conservaré la tríada operativa: un `AGENTS.md` conciso con fuentes de verdad y reglas de cambio, un `docs/REPO_MAP.md` con entry points y rutas protegidas, y un script ejecutable `./scripts/verify_repo.sh` integrado en CI para validar código, sintaxis y contratos en un solo paso.
