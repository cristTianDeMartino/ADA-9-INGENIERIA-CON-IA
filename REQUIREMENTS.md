# Requirements — Customer Search

## User Story
As a user,
I want to search customers by name or email,
so that I can quickly find the customer record I need.

## Functional Requirements
FR-01: El sistema debe permitir la búsqueda de clientes por nombre admitiendo coincidencias parciales (substring) e insensibilidad a mayúsculas y minúsculas (case-insensitive).
FR-02: El sistema debe permitir la búsqueda de clientes por correo electrónico admitiendo coincidencias parciales e insensibilidad a mayúsculas y minúsculas.
FR-03: El sistema debe permitir una búsqueda general/unificada por término que evalúe simultáneamente los campos de nombre y correo electrónico sin duplicar registros en el resultado.
FR-04: El sistema debe validar el término de búsqueda ingresado, exigiendo una longitud mínima de 2 caracteres significativos (ignorando espacios en blanco al inicio o al final) y rechazando consultas vacías.
FR-05: El sistema debe presentar los resultados indicando el total de coincidencias y los datos de cada cliente encontrado (identificador, nombre completo, correo electrónico, teléfono y estado activo). Si no hay coincidencias, debe retornar una lista vacía con un mensaje informativo claro.
FR-06: El sistema debe manejar entradas inválidas o errores de consulta mediante mensajes descriptivos y códigos de finalización de error controlados, sin provocar caídas inesperadas de la aplicación ni mostrar tracebacks no gestionados al usuario.

## Non-Functional Requirements
NFR-01: Rendimiento: La operación de búsqueda en la colección de clientes debe completarse en menos de 100 ms para volúmenes típicos de prueba (hasta 1,000 registros en memoria/archivo local).
NFR-02: Mantenibilidad y Desacoplamiento: El motor de búsqueda y la lógica de negocio deben estar completamente desacoplados de la interfaz de usuario (CLI), permitiendo reutilizar el servicio de búsqueda programáticamente o a través de otros adaptadores.
NFR-03: Calidad y Verificabilidad: Todo el comportamiento funcional y reglas de validación deben estar cubiertos por pruebas automatizadas ejecutables mediante `pytest` con un 100% de éxito.

## Open Questions
Q-01: ¿Cómo debe comportarse la búsqueda si el usuario ingresa espacios en blanco al inicio o al final del término?
- Resolución: El sistema aplicará un recorte automático (`strip`) al término antes de validarlo y procesarlo.
Q-02: ¿Qué criterio de orden se aplicará a los resultados coincidentes?
- Resolución: Los resultados se ordenarán de forma predeterminada alfabéticamente por el nombre del cliente, priorizando coincidencias exactas o de prefijo cuando sea relevante.

## Constraints / Assumptions
C-01: La solución se desarrollará en Python 3.11+ utilizando únicamente librerías estándar para la lógica y CLI (`argparse`, `json`, `dataclasses`, `typing`), y `pytest` exclusivamente para pruebas automatizadas.
A-01: Cada registro de cliente cuenta con los atributos: `id` (cadena única), `name` (cadena), `email` (cadena), `phone` (cadena) y `is_active` (booleano).
