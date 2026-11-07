# AI Usage Log

## Entrada 1: Auditoría inicial BEFORE
- Contexto: Evaluación del baseline funcional derivado de ADA-05.
- Propuesta del asistente: Asignar una calificación inicial de 3/5 a Automation & Guardrails argumentando que la presencia de pruebas con pytest contaba como automatización.
- Decisión tomada: Rechacé la sugerencia y reduje el puntaje a 1/5. Pytest verifica lógica de negocio de pruebas individuales, pero no valida la integridad del repositorio, contratos de documentación, variables de entorno ni revisiones de formato. El baseline carecía por completo de hooks, scripts unificados o pipelines de CI.
- Resultado: La auditoría BEFORE reflejó una puntuación realista de 47/100, identificando la ausencia de guardrails ejecutables como fricción principal.

## Entrada 2: Diseño y estructura de AGENTS.md
- Contexto: Redacción del contrato operativo en `AGENTS.md`.
- Propuesta del asistente: Incluir un resumen completo de los requisitos funcionales (`FR-01` a `FR-06`) dentro de `AGENTS.md` para evitar que el agente tuviera que abrir `REQUIREMENTS.md`.
- Decisión tomada: Rechacé duplicar requisitos en `AGENTS.md`. Duplicar especificaciones genera divergencias cuando los requisitos cambian. Diseñé `AGENTS.md` para actuar como índice operativo y directriz de ejecución, apuntando a `REQUIREMENTS.md` y `SPEC.md` como fuentes únicas de verdad.
- Resultado: `AGENTS.md` se mantuvo conciso (45 líneas) y enfocado en orden de lectura, comandos oficiales, reglas de cambio y condiciones de detención.

## Entrada 3: Conversión de reglas a software (Guardrails)
- Contexto: Protección de rutas sensibles y detección de archivos prohibidos.
- Propuesta del asistente: Agregar una advertencia textual en el prompt indicando al modelo que no modifique `data/customers.json` ni agregue archivos de configuración local.
- Decisión tomada: Convertí la regla en código verificable mediante `scripts/check_repo_contract.py`. El script inspecciona el sistema de archivos buscando extensiones prohibidas (`.env`, `.key`, `.pem`), comprueba que `data/customers.json` exista y sea un JSON válido, y valida que `SPEC.md` referencie identificadores de requisitos.
- Resultado: La restricción se volvió determinista y verificable por máquina, emitiendo un código de salida distinto de cero si se viola la regla.

## Entrada 4: Descubribilidad y conocimiento implícito
- Contexto: Análisis de conocimiento tribal detectado en la ejecución BEFORE.
- Propuesta del asistente: Crear múltiples archivos de documentación detallada explicando la arquitectura de cada módulo de Python.
- Decisión tomada: Rechacé crear documentación redundante. Sinteticé la navegación en un único archivo operativo: `docs/REPO_MAP.md`. El mapa especifica los puntos de entrada exactos, la ubicación de las pruebas correspondientes, una guía de cambio de cinco pasos y la lista de rutas protegidas.
- Resultado: El agente pasó de recorrer directorios mediante búsquedas ciegas a consultar directamente los archivos señalados en la guía de cambio.

## Entrada 5: Contrato compartido de verificación y CI
- Contexto: Configuración de la verificación en integración continua.
- Propuesta del asistente: Escribir comandos independientes dentro de `.github/workflows/verify.yml` para instalar dependencias y ejecutar pytest con parámetros específicos de CI.
- Decisión tomada: Unifiqué el contrato de verificación. El flujo de trabajo de GitHub Actions delega la validación completa al mismo script local: `./scripts/verify_repo.sh`.
- Resultado: Desarrolladores humanos, agentes de codificación y el pipeline de CI comparten exactamente el mismo criterio de aceptación y los mismos códigos de salida.

## Entrada 6: Comparación de ejecución AFTER
- Contexto: Ejecución de la tarea controlada `TASK_UNDER_TEST.md` en el repositorio mejorado.
- Observación del asistente: El agente consultó `AGENTS.md` y `docs/REPO_MAP.md`, procedió directamente a editar `src/customer_search/service.py` y `src/customer_search/cli.py`, añadió pruebas en los archivos indicados y validó todo con `./scripts/verify_repo.sh`.
- Evaluación: Cero comandos fallidos y cero suposiciones erróneas sobre nombres de fixtures. La ejecución completó los 44 tests, la verificación de sintaxis y el contrato del repositorio en un único intento.

## Entrada 7: Evaluación final y límites de autonomía
- Contexto: Identificación de operaciones que continúan exigiendo supervisión humana.
- Análisis: Aunque el repositorio provee guardrails ejecutables, ciertas decisiones no deben automatizarse sin revisión: modificaciones a la arquitectura de capas, cambios en los esquemas de datos de entrada o adición de dependencias de terceros.
- Decisión tomada: Se formalizaron stop conditions explícitas en `AGENTS.md` y `docs/REPO_MAP.md`, obligando al agente a detenerse y solicitar confirmación humana cuando detecte conflictos en requisitos o modificaciones en rutas protegidas.
