# ADA-09: Agentic Code Review

Ejecución completa del ciclo de desarrollo, verificación determinista, revisión de código agéntica independiente, toma de decisiones humanas, corrección acotada, re-review y consolidación de evidencia de Pull Request (`Coder Agent -> Verification Gate -> Reviewer Agent -> Human Review -> Fix -> Re-review -> PR Evidence`) sobre el sistema **Customer Search**.

## Resumen del ciclo ejecutado (`CR-02`)

- **Change Request (`CHANGE_REQUEST.md`)**: `CR-02` — Adición del filtro de límite de resultados (`limit: int | None = None` en `CustomerSearchService.search` y `--limit` en CLI) preservando `total_matches` previo al recorte, validación estricta de `limit >= 1` en `SearchQueryValidator`, e inclusión de la columna `PHONE` en la salida tabular del CLI (`FR-05` / `AC-05`).
- **Rama y Commits**:
  - Rama base: `main` (`24374dc`)
  - Rama de trabajo: `ada09/cr-02`
  - Commit candidato (Fase 1): `e2f8999` (`feat: implement CR-02`)
  - Commit de corrección (Fase 6): `5722e2a` (`fix: address ADA-09 review findings`)
- **Separación de roles e independencia de sesiones**:
  - **Coder Agent**: Sesión independiente (`02e1e837-b5f5-4752-b9d5-73aaa0622837`, permisos de escritura).
  - **Reviewer Agent**: Sesión independiente (`87d3351d-0769-4ec1-8378-9a83215d2f97`, permisos estrictamente `read-only` con `EnableWriteTools: false`).
- **Resultados de Revisión y Verificación**:
  - Revisión inicial (`results/review-report.md`): Detectó **2 `MUST FIX`** (`RF-01`, `RF-02`), **2 `SHOULD FIX`** (`RF-03`, `RF-04`) y **2 `OPTIONAL`** (`RF-05`, `RF-06`) que habían pasado desapercibidos pese a tener 48 tests en verde.
  - Decisiones humanas (`results/human-review-decisions.md`): `3 ACCEPTED` (`RF-01`, `RF-02`, `RF-04`), `1 MODIFIED` (`RF-03` elevado de `SHOULD FIX` a `MUST FIX`), `1 DEFERRED` (`RF-05`) y `1 REJECTED` (`RF-06`).
  - Re-review (`results/re-review-report.md`): `4 RESOLVED`, `0` regresiones nuevas y suite ampliada a **66 pruebas pasando en 0.12s** (`VERIFY_REPO: PASS`).
  - Estado final (`results/PR_EVIDENCE.md`): **`READY FOR HUMAN MERGE`**.

## Estructura de entrega (Sección 25)

```
ada-09-agentic-code-review/
├── AGENTS.md                          # Contrato operativo, separación de roles y reglas de review
├── REQUIREMENTS.md                    # Requisitos funcionales y no funcionales (fuente de verdad)
├── SPEC.md                            # Especificación técnica y criterios de aceptación
├── ARCHITECTURE.md                    # Diseño arquitectónico en capas y flujo de dependencias
├── TASKS.md                           # Desglose de tareas base
├── CHANGE_REQUEST.md                  # Solicitud de cambio acotada y aprobada (CR-02)
├── README.md                          # Documentación, comandos y Reflexión Individual (Sección 29)
├── AI_USAGE_LOG.md                    # Bitácora detallada de decisiones y supervisión de IA (Sección 28)
├── GEMINI.md                          # Adaptador de contexto que delega en AGENTS.md
├── requirements.txt                   # Dependencias de desarrollo/pruebas
├── docs/
│   ├── REPO_MAP.md                    # Mapa del repositorio y rutas protegidas
│   └── traceability.md                # Matriz de trazabilidad actualizada con CR-02 y findings
├── src/
│   └── customer_search/
│       ├── __init__.py
│       ├── cli.py                     # CLI con soporte para --limit y columna PHONE
│       ├── exceptions.py              # Excepciones de dominio (ValidationError, DataLoadError)
│       ├── models.py                  # Entidades inmutables Customer y SearchResult
│       ├── repository.py              # Repositorio en memoria y carga JSON
│       ├── service.py                 # Servicio de búsqueda con limit y preservación de total_matches
│       └── validator.py               # Validador de consultas y parámetro limit >= 1
├── tests/
│   ├── conftest.py
│   ├── test_cli.py                    # Pruebas de integración CLI (--limit, PHONE, errores)
│   ├── test_models.py                 # Pruebas de modelos de dominio
│   ├── test_performance.py            # Benchmark < 100 ms para 1,000 registros
│   ├── test_repository.py             # Pruebas de persistencia JSON y en memoria
│   ├── test_service.py                # Pruebas de servicio (limit, total_matches, validación)
│   └── test_validator.py              # Pruebas unitarias de validación (incluyendo limit y booleanos)
├── scripts/
│   ├── verify_repo.sh                 # Verification Gate determinista (Tests, Lint, Contract, Security)
│   └── check_repo_contract.py         # Verificador de contrato del repositorio y seguridad
└── results/
    ├── run-context.md                 # Registro de rama, commit base y sesiones de agentes
    ├── coder-report.md                # Reporte del Coder Agent (Fase 1 + Fase 6 Fix Cycle)
    ├── verification-report.md         # Reporte del Verification Gate determinista
    ├── pr.diff                        # Diff completo de la rama frente a main
    ├── commits.txt                    # Historial de commits de la rama ada09/cr-02
    ├── review-contract.md             # Contrato de revisión (requisitos, arquitectura, severidades)
    ├── review-report.md               # Reporte del Reviewer Agent independiente (Fase 4)
    ├── human-review-decisions.md      # Decisiones del Human Reviewer (Fase 5)
    ├── re-review-report.md            # Reporte de Re-review independiente (Fase 7)
    └── PR_EVIDENCE.md                 # Evidencia consolidada auditable y Human Gate Final (Fase 8)
```

## Instrucciones de ejecución y verificación

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar búsqueda desde CLI con columna PHONE y límite de resultados
python3 -m src.customer_search.cli "garcia" --limit 2

# 3. Ejecutar salida en formato JSON verificando total_matches vs customers recortados
python3 -m src.customer_search.cli "garcia" --limit 2 --json

# 4. Ejecutar el Verification Gate completo
./scripts/verify_repo.sh
```

---

## Reflexión individual (Sección 29)

### 1. ¿Qué encontró el reviewer-agent que el coder-agent no detectó?
El `reviewer-agent` independiente detectó dos defectos críticos (`MUST FIX`) que el `coder-agent` pasó por alto en su implementación inicial (`e2f8999`):
1. **Corrupción del conteo total (`RF-01`)**: En `src/customer_search/service.py`, el `coder-agent` aplicó el recorte `matched = matched[:limit]` *antes* de construir `SearchResult(..., total_matches=len(matched))`, provocando que `total_matches` reportara la longitud truncada (`2`) en lugar del total real de coincidencias antes del límite (`3`), violando `FR-05`, `AC-05` y el objetivo 2 de `CHANGE_REQUEST.md`.
2. **Violación de frontera arquitectónica y desacoplamiento (`RF-02`)**: El `coder-agent` colocó la validación `if args.limit is not None and args.limit < 1` únicamente dentro de `src/customer_search/cli.py`, omitiendo agregarla en `SearchQueryValidator.validate` (`validator.py`) e invocarla desde `CustomerSearchService.search` (`service.py`). Como consecuencia, cualquier llamada programática al servicio (`NFR-02` / `AC-08`) con `limit=0`, `limit=-1` o `limit=True` evitaba la validación y producía resultados silenciosamente erróneos (por ejemplo, `limit=-1` ejecutaba `matched[:-1]`, eliminando el último registro).

### 2. ¿Qué finding fue más difícil de clasificar y por qué?
El finding **`RF-03`** (ausencia de pruebas unitarias para `limit` en `test_validator.py`, falta de pruebas de `limit` inválido en `test_service.py` y omisión de la aserción `total_matches == 3` en `test_service.py` y `test_cli.py`). Inicialmente, el `reviewer-agent` lo clasificó como `SHOULD FIX` bajo la categoría de cobertura de pruebas, dado que ya existían pruebas básicas para `--limit` y el código parecía cubierto. Sin embargo, al analizarlo como revisor humano, resultó evidente que esas pruebas incompletas eran precisamente las que habían enmascarado los dos defectos `MUST FIX` (`RF-01` y `RF-02`), además de incumplir explícitamente la sección `Verification` de `CHANGE_REQUEST.md`. Por ello fue necesario reclasificarlo a `MUST FIX` durante el Human Review.

### 3. ¿Qué finding rechazaste o modificaste como humano y qué evidencia usaste?
- **Finding modificado (`RF-03`)**: Modifiqué su severidad de `SHOULD FIX` a `MUST FIX` utilizando como evidencia los puntos 1, 2 y 3 de la sección `Verification` en `CHANGE_REQUEST.md` y el requisito `NFR-03` (`AC-09`) de `SPEC.md`, exigiendo pruebas explícitas para `total_matches == 3` con `limit=2` y para valores inválidos de `limit` (`0`, `-1`, `True`, `False`, `"2"`) en `test_validator.py` y `test_service.py`.
- **Finding rechazado (`RF-06`)**: Rechacé (`REJECTED`) la sugerencia del reviewer de agregar el atributo `"limit"` al modelo `SearchResult` y al diccionario retornado por `SearchResult.to_dict()`. Utilicé como evidencia concreta el contrato del **Domain Model** en `SPEC.md` (líneas 39–44), que define estrictamente cuatro campos (`query`, `field`, `total_matches`, `customers`), junto con la prueba `test_search_result_serialization` en `tests/test_models.py` y la restricción de compatibilidad hacia atrás en `CHANGE_REQUEST.md`.

### 4. ¿Hubo algún test verde que produjera falsa confianza? Explica.
Sí. En el commit candidato `e2f8999`, la suite completa pasó con **48 pruebas en verde** (`48 passed in 0.09s`), incluyendo las nuevas pruebas `test_service_search_with_limit` y `test_cli_limit_flag`. Esas dos pruebas produjeron **falsa confianza** por dos razones:
1. Solo verificaban `assert len(res.customers) == 2` al buscar `"garcia"` con `limit=2`, omitiendo verificar `assert res.total_matches == 3`. Al validar únicamente el efecto secundario del recorte y no el invariante de negocio completo (`FR-05`), el test dio por bueno un resultado donde `total_matches` había sido sobrescrito erróneamente a `2`.
2. La validación de `limit=0` solo se probó a través del CLI (`test_cli_invalid_limit_zero`), lo que ocultó por completo que `CustomerSearchService.search` y `SearchQueryValidator.validate` carecían de validación cuando se invocaban directamente desde Python.

### 5. ¿Verificaste alguna API o dependencia que parecía plausible? ¿Qué encontraste?
Sí. Durante la construcción del `review-contract.md` y la revisión independiente se verificaron todas las llamadas entre módulos internos (`SearchQueryValidator.validate`, `InMemoryCustomerRepository.from_json_file`, `InMemoryCustomerRepository.get_all`, `Customer.to_dict`, `SearchResult.to_dict`) y librerías estándar (`argparse`, `json`, `dataclasses`, `pathlib`). Aunque el `coder-agent` no inventó librerías externas ni métodos inexistentes, sí se encontró una **discrepancia de firma de API interna**: `CHANGE_REQUEST.md` especificaba que `SearchQueryValidator.validate` debía validar el parámetro `limit`, pero en `src/customer_search/validator.py:14` la firma seguía siendo `validate(query: str, field: str = "all") -> str` sin el parámetro `limit: int | None = None`, mientras que `cli.py` simulaba esa validación por su cuenta.

### 6. ¿Qué arquitectura o regla del repositorio fue más útil para la revisión?
La tabla de responsabilidades y el diagrama de secuencia en **`ARCHITECTURE.md`** (`CLI -> CustomerSearchService -> SearchQueryValidator` y `CustomerRepository`), combinados con el requisito **`NFR-02` (`AC-08`)** en `REQUIREMENTS.md` y `SPEC.md`. Esa regla arquitectónica establece sin ambigüedad que toda validación de negocio debe vivir en `validator.py` y ser coordinada por `service.py` de forma desacoplada del CLI. Gracias a ese límite explícito, ubicar la validación de `args.limit < 1` en `cli.py` no fue una discusión subjetiva de estilo, sino una violación verificable de arquitectura (`RF-02` y `RF-04`).

### 7. ¿Qué problema pudo detectar un check determinista antes que el reviewer-agent?
El script determinista `./scripts/verify_repo.sh` (que ejecuta `pytest -q`, `python3 -m compileall -q src tests` y `python3 scripts/check_repo_contract.py`) verifica de forma instantánea y automática:
- Errores de sintaxis o compilación de bytecode en `src/` y `tests/`.
- Regresiones en las 44 pruebas existentes del sistema.
- Presencia obligatoria de los archivos contractuales (`AGENTS.md`, `REQUIREMENTS.md`, `SPEC.md`, `ARCHITECTURE.md`, `TASKS.md`, `CHANGE_REQUEST.md`) y sus secciones clave.
- Integridad del dataset protegido `data/customers.json` y ausencia de archivos sensibles o secretos (`.env`, `.pem`, `.key`, `id_rsa`, `credentials.json`).

### 8. ¿Qué parte del review sigue requiriendo criterio humano?
El criterio humano sigue siendo indispensable en tres decisiones que no pueden delegarse ni a checks deterministas ni al `reviewer-agent`:
1. **Arbitraje entre sugerencias del reviewer y contratos existentes**: Decidir rechazar `RF-06` porque agregar un campo `"limit"` a `SearchResult.to_dict()`, aunque suena útil en abstracto, rompe la compatibilidad hacia atrás definida en `SPEC.md`.
2. **Calibración de severidad según el riesgo real de negocio**: Elevar `RF-03` de `SHOULD FIX` a `MUST FIX` al reconocer que tests incompletos generan falsa confianza sobre invariantes críticos.
3. **Control de alcance y gestión de deuda técnica**: Decidir diferir `RF-05` para mantener el Pull Request acotado y autorizar formalmente cuándo la evidencia es suficiente para declarar `READY FOR HUMAN MERGE`.

### 9. ¿Qué technical debt aceptaste o diferiste y por qué?
Diferí el finding **`RF-05`** (`DEFERRED`), relacionado con el ancho fijo de las columnas (`12`, `28`, `30`, `16`, `8`) y la línea separadora de 98 guiones en `format_text_output` (`src/customer_search/cli.py`). Lo diferí porque la salida actual incluye correctamente los cinco atributos requeridos por `FR-05` y `AC-05` (`id`, `name`, `email`, `phone`, `is_active`) y todas las pruebas de aceptación pasan; introducir un motor de cálculo dinámico de ancho de columnas en este PR habría expandido innecesariamente el alcance de `CR-02` con cambios cosméticos no solicitados.

### 10. ¿Qué artefactos de este ADA reutilizarías en la Agentic Software Factory final?
Reutilizaría cinco artefactos fundamentales como parte del pipeline estándar de la **Agentic Software Factory**:
1. **`CHANGE_REQUEST.md` con Human Gate 0**: Para garantizar que ningún agente escriba código sin un alcance acotado, trazable a requisitos existentes y aprobado por un humano.
2. **`./scripts/verify_repo.sh` y `results/verification-report.md`**: Como Verification Gate determinista obligatorio antes de invocar cualquier agente revisor.
3. **`results/review-contract.md`**: Para obligar al `reviewer-agent` a reconstruir qué significa "correcto" (requisitos + límites arquitectónicos + matriz de severidad) antes de leer el diff.
4. **`results/review-report.md` y `results/re-review-report.md` generados por un subagente `read-only` en sesión separada**: Para asegurar independencia real de contexto y hallazgos sustentados en archivo/línea.
5. **`results/human-review-decisions.md` y `results/PR_EVIDENCE.md`**: Para mantener la trazabilidad auditable de extremo a extremo y preservar la responsabilidad final de merge en manos humanas.
