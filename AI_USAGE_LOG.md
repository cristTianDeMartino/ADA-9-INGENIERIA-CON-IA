# AI Usage Log — ADA-09 Agentic Code Review

## Entrada 1: Definición y refinamiento del Change Request (`CR-02`)
- **Fase**: Preparación del Change Request y Human Gate 0 (`CHANGE_REQUEST.md`).
- **Contexto**: Selección de un cambio acotado pero técnicamente significativo sobre el repositorio Agent-Ready proveniente de ADA-08 (`Customer Search`).
- **Propuesta del asistente**: Crear un nuevo requisito funcional (`FR-07`) en `REQUIREMENTS.md` para agregar paginación completa con `offset`, `limit` y cursores de página.
- **Decisión humana**: **Rechazada / Refinada**. La sección 6 y 7 de ADA-09 prohíben redefinir requisitos o introducir features fuera del alcance de `SPEC.md` (que declara explícitamente la paginación compleja como *Out of Scope*). En su lugar, definí `CR-02` referenciando exclusivamente requisitos existentes (`FR-04`, `FR-05`, `FR-06`, `NFR-02`, `NFR-03` y `AC-04`, `AC-05`, `AC-06`, `AC-08`, `AC-09`) para: (1) agregar el parámetro opcional `limit: int | None = None` (`--limit` en CLI) preservando `total_matches` previo al recorte, (2) validar `limit >= 1` en `SearchQueryValidator`, y (3) completar la visualización de la columna `PHONE` en la tabla de texto del CLI (`AC-05`).
- **Resultado**: `CHANGE_REQUEST.md` quedó acotado, verificable y autorizado bajo **Human Gate 0** antes de iniciar el `coder-agent`.

## Entrada 2: Plan del Coder-Agent y decisión humana sobre el plan
- **Fase**: Fase 1 — Coder Agent (Sesión independiente `02e1e837-b5f5-4752-b9d5-73aaa0622837`).
- **Contexto**: Elaboración del plan de implementación para `CR-02` en la rama `ada09/cr-02` (commit base `24374dc`).
- **Propuesta del coder-agent**: Propuso un plan de 5 pasos tocando `src/customer_search/service.py`, `src/customer_search/cli.py`, `tests/test_service.py` y `tests/test_cli.py`, manteniendo intactos `data/customers.json`, `REQUIREMENTS.md` y `SPEC.md`.
- **Decisión humana**: **Aprobada para ejecución inicial del candidato**, manteniendo la separación estricta de roles (el `coder-agent` implementa y ejecuta `./scripts/verify_repo.sh`, pero no puede aprobar su propio cambio).
- **Resultado**: El `coder-agent` implementó el candidato inicial (`e2f8999 feat: implement CR-02`) y generó `results/coder-report.md`.

## Entrada 3: Implementación inicial y falsa confianza en pruebas verdes
- **Fase**: Fase 1 y Fase 2 — Implementación del candidato y Verification Gate (`results/verification-report.md`).
- **Contexto**: Evaluación del commit candidato `e2f8999` mediante `./scripts/verify_repo.sh`.
- **Observación técnica**: En la primera implementación, el `coder-agent` colocó la validación `if args.limit is not None and args.limit < 1` directamente dentro de `src/customer_search/cli.py` y aplicó `matched = matched[:limit]` en `src/customer_search/service.py` antes de calcular `total_matches=len(matched)`. A pesar de estos dos defectos, `./scripts/verify_repo.sh` reportó `48 passed in 0.09s` (`VERIFY_REPO: PASS`).
- **Análisis humano**: Las pruebas añadidas por el `coder-agent` (`test_service_search_with_limit` y `test_cli_limit_flag`) solo verificaban `len(customers) == 2` sin comprobar `total_matches == 3`, produciendo **falsa confianza**. Esto demostró empíricamente por qué un Verification Gate en verde no sustituye a un `reviewer-agent` independiente.

## Entrada 4: Reviewer-Agent independiente — Findings y evidencia concreta
- **Fase**: Fase 3 y Fase 4 — Review Contract (`results/review-contract.md`) y Reviewer Agent independiente (Sesión read-only `87d3351d-0769-4ec1-8378-9a83215d2f97`).
- **Contexto**: Inspección del candidato `e2f8999` en un contexto limpio con permisos de solo lectura (`EnableWriteTools: false`).
- **Hallazgos del reviewer-agent**:
  - `RF-01 (MUST FIX)`: Evidencia en `src/customer_search/service.py:74-82`. El corte `matched = matched[:limit]` ocurría antes de `total_matches=len(matched)`, alterando el conteo real de coincidencias exigido por `FR-05` / `AC-05`.
  - `RF-02 (MUST FIX)`: Evidencia en `src/customer_search/validator.py:13-44` y `src/customer_search/cli.py:95-96`. La validación de `limit` se implementó en `cli.py` en lugar de `SearchQueryValidator.validate`, violando la arquitectura en capas (`CLI -> Service -> Validator`) y `NFR-02` / `AC-08` (llamadas programáticas con `limit=-1`, `limit=0` o `limit=True` no lanzaban `ValidationError`).
  - `RF-03 (SHOULD FIX)`: Ausencia de pruebas en `tests/test_validator.py` y omisión de aserciones sobre `total_matches` en `tests/test_service.py` y `tests/test_cli.py`.
  - `RF-04 (SHOULD FIX)`: Duplicación y acoplamiento de validación en `cli.py`.
  - `RF-05 (OPTIONAL)`: Diferencia cosmética en longitud del separador `"-" * 98` frente a filas de 106 caracteres en `cli.py`.
  - `RF-06 (OPTIONAL)`: Sugerencia de agregar `"limit"` al diccionario retornado por `SearchResult.to_dict()`.
- **Resultado**: Reporte documentado en `results/review-report.md` con recomendación `READY AFTER MUST FIX`.

## Entrada 5: Human Review — Decisiones (`ACCEPTED`, `MODIFIED`, `DEFERRED`, `REJECTED`)
- **Fase**: Fase 5 — Human Review (`results/human-review-decisions.md`).
- **Contexto**: Toma de decisiones humanas sobre cada uno de los 6 findings del `reviewer-agent`.
- **Decisiones tomadas y justificación**:
  - `RF-01` -> **ACCEPTED (`MUST FIX`)**: Defecto funcional real que corrompe `total_matches` cuando `limit` trunca la lista.
  - `RF-02` -> **ACCEPTED (`MUST FIX`)**: Violación real de frontera arquitectónica (`ARCHITECTURE.md`) y de desacoplamiento del servicio (`NFR-02`), incluyendo el caso borde de Python donde `isinstance(True, int)` es `True`.
  - `RF-03` -> **MODIFIED (`SHOULD FIX` -> `MUST FIX`)**: Elevé la severidad a `MUST FIX` porque sin pruebas de regresión en `test_validator.py`, `test_service.py` y `test_cli.py` que verifiquen `total_matches` y rechacen `limit` inválidos (incluyendo booleanos y negativos), la suite de pruebas seguiría dando falsa confianza e incumpliría la sección `Verification` de `CHANGE_REQUEST.md`.
  - `RF-04` -> **ACCEPTED (`SHOULD FIX`)**: Eliminar la validación duplicada en `cli.py` una vez centralizada en `validator.py`.
  - `RF-05` -> **DEFERRED (`OPTIONAL`)**: Diferido como deuda técnica menor porque la tabla incluye todos los campos de `AC-05` y rediseñar el cálculo dinámico de columnas excede el alcance de `CR-02`.
  - `RF-06` -> **REJECTED (`OPTIONAL`)**: Rechazado con evidencia en `SPEC.md` (líneas 39-44) y `tests/test_models.py`: modificar las llaves de `SearchResult.to_dict()` rompería la compatibilidad hacia atrás del contrato JSON.

## Entrada 6: Fix Cycle — Corrección acotada de findings aceptados y modificados
- **Fase**: Fase 6 — Fix Cycle (`results/coder-report.md` y commit `5722e2a`).
- **Contexto**: Regreso al `coder-agent` (`02e1e837-b5f5-4752-b9d5-73aaa0622837`) con instrucciones restringidas únicamente a `RF-01`, `RF-02`, `RF-03` y `RF-04`.
- **Cambios aplicados**:
  1. `src/customer_search/validator.py`: `SearchQueryValidator.validate` ahora recibe `limit: int | None = None` y valida `if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1: raise ValidationError(...)`.
  2. `src/customer_search/service.py`: `CustomerSearchService.search` delega la validación de `limit` a `self._validator.validate(query, field=field, limit=limit)` y guarda `total_matches = len(matched)` antes de recortar `matched = matched[:limit]`.
  3. `src/customer_search/cli.py`: Se eliminó la validación manual redundante en `main()`.
  4. `tests/`: Se añadieron 18 casos de prueba parametrizados y de regresión en `test_validator.py`, `test_service.py` y `test_cli.py`, subiendo la suite de 48 a **66 pruebas pasando en 0.12s** (`VERIFY_REPO: PASS`).

## Entrada 7: Re-review independiente y consolidación de PR Evidence
- **Fase**: Fase 7 y Fase 8 — Re-review (`results/re-review-report.md`) y PR Evidence (`results/PR_EVIDENCE.md`).
- **Contexto**: Segunda inspección por el `reviewer-agent` independiente (`87d3351d-0769-4ec1-8378-9a83215d2f97`) sobre el commit `5722e2a`.
- **Resultado**: El `reviewer-agent` verificó con evidencia de archivo y línea que `RF-01`, `RF-02`, `RF-03` y `RF-04` están **RESOLVED**, que `RF-05` (`DEFERRED`) y `RF-06` (`REJECTED`) fueron respetados sin expandir el alcance, y que no se introdujeron nuevas regresiones `MUST FIX`. Con base en esta evidencia completa, aprobé el **Human Gate Final** como `READY FOR HUMAN MERGE` en `results/PR_EVIDENCE.md`.
