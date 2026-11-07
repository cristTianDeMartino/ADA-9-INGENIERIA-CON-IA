# Tasks

## T-01 Project setup
- Goal: Inicializar la estructura de directorios del proyecto Python (`src/customer_search/`, `tests/`, `data/`, `docs/`, `results/`), configuración de entorno virtual y archivo `.gitignore`.
- Files: `src/customer_search/__init__.py`, `tests/__init__.py`, `tests/conftest.py`, `.gitignore`
- Acceptance: La estructura del proyecto existe, el entorno Python está listo y `pytest` se ejecuta sin errores de importación.
- Verification: `pytest -v` se ejecuta en la terminal retornando código 0 (sin tests o recolectando el entorno).

## T-02 Domain model
- Goal: Implementar el modelo de dominio `Customer` y el contenedor de resultados `SearchResult` según `SPEC.md`.
- Files: `src/customer_search/models.py`, `tests/test_models.py`
- Acceptance: `Customer` contiene los atributos requeridos (`id`, `name`, `email`, `phone`, `is_active`) con validación de tipos e inmutabilidad o igualdad por valor, y `SearchResult` agrupa los clientes encontrados junto al conteo y término buscado.
- Verification: `pytest tests/test_models.py -v` pasa al 100%.

## T-03 Search logic
- Goal: Implementar el protocolo de repositorio `CustomerRepository`, la implementación en memoria con carga opcional desde JSON, y el servicio de búsqueda `CustomerSearchService` con soporte para coincidencia parcial, case-insensitive y búsqueda unificada.
- Files: `src/customer_search/repository.py`, `src/customer_search/service.py`, `data/customers.json`, `tests/test_repository.py`, `tests/test_service.py`
- Acceptance: Las búsquedas por nombre, por email o combinadas (`field="all"`) retornan los resultados esperados ordenados alfabéticamente y sin duplicados, cumpliendo `FR-01`, `FR-02`, `FR-03`.
- Verification: `pytest tests/test_repository.py tests/test_service.py -v` pasa al 100%.

## T-04 Validation and errors
- Goal: Implementar la jerarquía de excepciones y el validador de entradas `SearchQueryValidator` que aplica las reglas de validación `VR-01`, `VR-02` y `VR-03`.
- Files: `src/customer_search/exceptions.py`, `src/customer_search/validator.py`, `tests/test_validator.py`
- Acceptance: Consultas vacías, con solo espacios, menores a 2 caracteres o con campos inválidos levantan `ValidationError` con mensajes explicativos precisos, cumpliendo `FR-04` y `FR-06`.
- Verification: `pytest tests/test_validator.py -v` pasa al 100%.

## T-05 Tests
- Goal: Implementar la interfaz CLI interactiva (`src/customer_search/cli.py`) y consolidar la suite completa de pruebas automatizadas incluyendo pruebas de integración del CLI, pruebas de rendimiento (< 100 ms) y escenarios de casos límite.
- Files: `src/customer_search/cli.py`, `tests/test_cli.py`, `tests/test_performance.py`
- Acceptance: La CLI procesa argumentos, soporta `--json` y `--field`, maneja errores con mensajes a `stderr` y códigos de salida apropiados (0 y 1) sin tracebacks; todos los criterios de aceptación `AC-01` a `AC-09` quedan cubiertos por tests automatizados.
- Verification: `pytest -v` pasa todos los tests con 100% de éxito.

## T-06 Documentation
- Goal: Elaborar la matriz de trazabilidad (`docs/traceability.md`), el registro de uso de IA (`AI_USAGE_LOG.md`), el reporte del agente (`results/agent-report.md`) y el `README.md` con instrucciones y respuestas de reflexión.
- Files: `docs/traceability.md`, `AI_USAGE_LOG.md`, `results/agent-report.md`, `README.md`
- Acceptance: Todos los entregables de documentación especificados en las secciones 12, 14, 16, 17 y 18 de ADA-05 están completos, coherentes y verificables.
- Verification: Inspección de enlaces cruzados y verificación de consistencia entre requisitos, especificación, tareas, pruebas y registros.
