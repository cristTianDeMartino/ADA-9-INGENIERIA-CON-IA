# Customer Search Feature

## Goal
Proveer una capacidad de búsqueda de clientes rápida, robusta y completamente verificable para aplicaciones locales, permitiendo a los usuarios consultar clientes por nombre, correo electrónico o de forma combinada con coincidencia parcial, insensibilidad a mayúsculas y validaciones estrictas.

## Requirements Covered
- FR-01
- FR-02
- FR-03
- FR-04
- FR-05
- FR-06
- NFR-01
- NFR-02
- NFR-03

## Scope
- Búsqueda en memoria de registros de clientes a partir de un repositorio de datos (soporte de carga desde archivo JSON o estructuras en memoria).
- Filtrado por campo específico (`name` o `email`) y búsqueda unificada en ambos campos (`all`).
- Coincidencia parcial de subcadenas (`substring match`) e insensibilidad a mayúsculas/minúsculas.
- Normalización automática de la consulta (recorte de espacios en blanco `strip`).
- Validación rigurosa de entradas y rechazo controlado con mensajes claros.
- Interfaz CLI amigable con salida formateada en texto legible y soporte para formato JSON mediante flag `--json`.
- Suite completa de pruebas unitarias y de integración automatizadas.

## Out of Scope
- Operaciones de modificación de datos (creación, edición o eliminación de clientes / CRUD completo).
- Integración con motores de bases de datos relacionales o NoSQL externas.
- Autenticación, autorización o control de acceso basado en roles.
- Paginación remota basada en cursores o servidores web HTTP complejos.

## Domain Model
- **`Customer`**:
  - `id: str`: Identificador único no vacío del cliente.
  - `name: str`: Nombre completo del cliente.
  - `email: str`: Dirección de correo electrónico del cliente.
  - `phone: str`: Número telefónico de contacto.
  - `is_active: bool`: Indicador de estado activo o inactivo del cliente (por defecto `True`).
- **`SearchResult`**:
  - `query: str`: Término de búsqueda consultado tras normalización.
  - `field: str`: Campo sobre el cual se aplicó el filtro (`"all"`, `"name"`, `"email"`).
  - `total_matches: int`: Cantidad total de clientes coincidentes.
  - `customers: list[Customer]`: Lista ordenada de entidades de clientes encontrados.

## Search Rules
- **SR-01 (Normalización)**: Antes de evaluar la coincidencia, el término de búsqueda debe ser recortado en sus extremos (`query.strip()`).
- **SR-02 (Case-Insensitive Match)**: La comparación se realiza convirtiendo tanto el valor del campo como el término de búsqueda a minúsculas (`value.lower()` contiene `query.lower()`).
- **SR-03 (Substring / Coincidencia Parcial)**: Un cliente coincide si el término normalizado es una subcadena del campo consultado.
- **SR-04 (Búsqueda Unificada)**: Cuando el campo objetivo es `"all"`, un cliente coincide si el término está presente en su atributo `name` O en su atributo `email`. No se generan duplicados en el resultado.
- **SR-05 (Ordenamiento)**: Los resultados se ordenan alfabéticamente por el campo `name` de manera ascendente. En caso de igualdad de nombre, se ordenan por `id`.

## Validation Rules
- **VR-01 (Consulta no vacía)**: El término de búsqueda no puede ser una cadena vacía ni contener únicamente espacios en blanco.
- **VR-02 (Longitud mínima)**: El término normalizado debe tener una longitud mínima de 2 caracteres (`len(query.strip()) >= 2`).
- **VR-03 (Campos permitidos)**: Si se especifica un campo de búsqueda, este debe pertenecer estrictamente al conjunto admitido: `{"all", "name", "email"}`. Cualquier otro valor es rechazado.

## Error Handling
- **`ValidationError`**: Lanzada cuando la consulta viola `VR-01`, `VR-02` o `VR-03`.
  - Mensaje esperado para consulta vacía o menor a 2 caracteres: `"Search query must contain at least 2 non-whitespace characters."`
  - Mensaje esperado para campo no válido: `"Invalid search field '{field}'. Allowed fields are: all, name, email."`
  - En la CLI, se captura y presenta en `stderr` con código de salida `1`, sin mostrar trazas de error (tracebacks).
- **`DataLoadError`**: Lanzada cuando la fuente de datos JSON no existe, no tiene formato válido o contiene registros corruptos.
  - En la CLI, se captura y presenta con código de salida `1`.
- **Sin resultados (`Zero Matches`)**: No se considera un error. Retorna `total_matches = 0` y lista vacía `customers = []`. En la CLI se informa de forma amigable con código de salida `0`.

## Acceptance Criteria
- **AC-01 (Mapeado a FR-01)**: Al buscar con `--field name "garcia"`, retorna todos los clientes cuyo nombre contenga "garcia" ignorando mayúsculas/minúsculas.
- **AC-02 (Mapeado a FR-02)**: Al buscar con `--field email "acme.com"`, retorna todos los clientes cuyo email contenga "acme.com" ignorando mayúsculas/minúsculas.
- **AC-03 (Mapeado a FR-03)**: Al buscar con `--field all` (o por defecto sin flag de campo) `"ana"`, retorna clientes cuyo nombre contenga "ana" o cuyo email contenga "ana", sin duplicados.
- **AC-04 (Mapeado a FR-04)**: Al consultar con cadenas vacías, espacios (`"   "`) o un único carácter (`"a"`), el sistema rechaza la solicitud levantando `ValidationError` y en CLI termina con código de salida `1` y mensaje descriptivo.
- **AC-05 (Mapeado a FR-05)**: La salida del sistema detalla el conteo total de coincidencias y los datos de cada cliente (`id`, `name`, `email`, `phone`, `is_active`). Si no hay resultados, muestra `"No customers found matching '{query}'."` con código de salida `0`.
- **AC-06 (Mapeado a FR-06)**: Las condiciones anómalas (errores de validación o datos inexistentes) son capturadas limpiamente, emitiendo mensajes de error a `stderr` sin tracebacks no controlados.
- **AC-07 (Mapeado a NFR-01)**: La ejecución de una búsqueda sobre un conjunto de 1,000 registros sintéticos toma menos de 100 ms.
- **AC-08 (Mapeado a NFR-02)**: La clase `CustomerSearchService` puede instanciarse e invocarse de forma independiente en código Python sin depender de `sys.argv` ni del CLI.
- **AC-09 (Mapeado a NFR-03)**: La totalidad de la suite de pruebas unitarias y de integración se ejecuta satisfactoriamente con `pytest -v` reportando 0 fallos.

## Test Scenarios
- **TS-01**: Búsqueda parcial por nombre en mayúsculas, minúsculas y mixto.
- **TS-02**: Búsqueda parcial por email en mayúsculas, minúsculas y dominios.
- **TS-03**: Búsqueda unificada (`field="all"`) donde un cliente coincide solo por nombre, otro solo por email y otro por ambos, verificando deduplicación.
- **TS-04**: Validación de término vacío (`""`) y espacios en blanco (`"  "`).
- **TS-05**: Validación de término con longitud menor a 2 caracteres (`"x"`).
- **TS-06**: Validación de campo de búsqueda no soportado (`field="phone"` o `"address"`).
- **TS-07**: Consulta sin coincidencias en el repositorio existente.
- **TS-08**: Formateo de salida CLI en modo texto tabular y en modo JSON (`--json`).
- **TS-09**: Prueba de rendimiento de búsqueda sobre 1,000 registros sintéticos verificando tiempo < 100 ms.

## Constraints
- Se restringe la solución a Python estándar (3.11+) y `pytest` para testing, operando en entorno local sin conectividad a servicios de nube o pagos.

## Open Questions
- N/A — No existen preguntas abiertas pendientes; las resoluciones de `REQUIREMENTS.md` quedaron incorporadas en las reglas de validación y criterios de aceptación.
