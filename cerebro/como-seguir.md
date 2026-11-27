---
tipo: guia
tags: [guia]
---

# Cómo seguir el trabajo

Qué hacer para actualizar o ampliar el proyecto, y cómo mantener este cerebro al día cuando se hace. Cada cambio en los datos o en el código va acompañado de su cambio en la página correspondiente.

## Analizar un mes nuevo

1. En `red-observada/configuracion.py`, cambiar `PRINCIPAL` (el mes que se analiza) y `CONTROL` (los meses de comparación).
2. Correr `python correr-todo.py` en `red-observada/`. El primer paso baja de [Lupa al Giro](datos/lupa-al-giro.md) los anexos que falten.
3. Revisar lo que avisan los programas:
   - si la ADRES cambió un archivo ya bajado;
   - si la ADRES dejó de listar un anexo que el manifiesto registra;
   - si apareció un formato de hoja nuevo;
   - si hubo códigos de EPS corregidos.
4. Revisar que no haya datos personales en las salidas, y no subir nunca los anexos originales, que quedan en `red-observada/datos/anexos/` ([datos personales y ética](metodo/datos-personales-y-etica.md)).
5. Si cambió la norma del giro directo, actualizar la [red normada](metodo/red-normada.md) antes de comparar.

## Agregar una norma

1. Leer la norma en su fuente oficial: la Secretaría del Senado para las leyes, el Gestor Normativo de la Función Pública para los decretos y el Ministerio de Salud para las resoluciones. Usar el texto vigente.
2. Si establece un flujo nuevo, agregar el vínculo a `red-normada/aristas-normadas.csv` con su norma y artículo, y volver a correr `construir-red-normada.py`.
3. Crear la página de la norma en `normas/`, con la misma estructura de las demás:
   - qué dice, en lo que importa para la red;
   - qué vínculos sostiene;
   - cómo se relaciona con otras normas;
   - dónde leerla.
4. Agregarla al [índice de normas](normas/indice-de-normas.md) y enlazarla desde las páginas de actores y conceptos que toca.
5. Volver a correr la red observada desde la comparación con la norma: `python correr-todo.py --desde 9`.

## Agregar un actor

1. Agregar la fila a `inventario-actores/actores.csv` siguiendo el diccionario, con su fuente en `fuente_identificacion`.
2. Correr `inventario.py` y `auditoria.py`; si tiene NIT, también `verificar_nit.py --aplicar`. La auditoría tiene que terminar sin errores.
3. Si el actor entra a la red normada, darle una posición en `posiciones-normada.csv` y volver a construir la red.
4. Agregarlo a [otros actores de la red](actores/otros-actores-de-la-red.md), o crear su página si su papel lo amerita.

El orden importa: la red normada usa el inventario, y la red observada usa las dos. Si cambia el inventario, hay que reconstruir la red normada y luego la observada.

## Reglas para escribir en el cerebro

- **Una página por cosa**: una norma, un actor, un concepto, una fuente, una referencia. Antes de crear una página, revisar si ya existe una donde quepa.
- **Toda afirmación con su fuente**: la norma con su artículo, el conjunto de datos con su enlace o la referencia académica. Las cifras de los análisis no van en el cerebro: están en las salidas de los programas.
- **Enlaces normales de Markdown**, relativos (por ejemplo, `[ADRES](actores/adres.md)`), para que funcionen en Obsidian y en GitHub. En Obsidian, la opción «Usar Wikilinks» debe estar apagada; ya viene así en la configuración de esta bóveda.
- **Ninguna página suelta**: toda página nueva se enlaza desde al menos otra.
- **Sin datos personales** ni nombres de personas, salvo los autores de las referencias.
- **Textos con tildes** y en lenguaje claro.
- **Metadatos mínimos** al inicio de cada página: `tipo` y `tags`.

## Ver también

[Inicio](README.md) · [El proyecto](proyecto.md) · [Glosario](glosario.md)
