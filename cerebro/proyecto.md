---
tipo: proyecto
tags: [proyecto]
---

# El proyecto

## La pregunta

> ¿Cuál es la estructura de la red de flujos de recursos e información entre la ADRES, las EPS y las IPS bajo el esquema de giro directo en Colombia, y qué nodos y conexiones presentan mayor centralidad, concentración o potencial de restricción?

La pregunta no tiene período: interroga la **estructura** del sistema tal como opera, no su evolución. Los meses de datos que se usan son el instrumento para verla, no el objeto de estudio.

## El objeto: una sola red con dos flujos

El objeto es el flujo de dinero y de información entre los agentes del sistema de salud. No son dos temas separados: son los dos tipos de flujo que viajan por la misma red de actores. La [Ley 1751 de 2015](normas/ley-1751-de-2015.md), art. 4, define el sistema de salud incluyendo el financiamiento y la información como partes del mismo sistema ([sistema de salud](sistema/sistema-de-salud.md)).

La pregunta se descompone en tres partes:

1. **Estructura**: construir la red dirigida y ponderada, con sus dos capas. Ver [modelado de redes](redes/modelado-de-redes.md).
2. **Centralidad y concentración**: medirlas con métricas de teoría de redes ([métricas de redes](redes/metricas-de-redes.md)).
3. **Potencial de restricción**: encontrar los nodos y las relaciones cuya falla o demora interrumpiría el flujo. Se contrasta lo que dicen las normas con lo que pasa ([red normada](metodo/red-normada.md) y [red observada](metodo/red-observada.md)).

## Qué cubre

- **Actores**: la [ADRES](actores/adres.md), las [EPS](actores/eps.md) y los [prestadores](actores/prestadores.md) como nodos centrales. La [Supersalud](actores/supersalud.md) y el [Ministerio de Salud](actores/ministerio-de-salud.md) aparecen como nodos de la capa de información. La red normada incluye además a los demás actores que las normas conectan ([otros actores de la red](actores/otros-actores-de-la-red.md)).
- **Recursos**: el [giro directo](sistema/giro-directo.md) de la UPC, en los dos regímenes, contributivo y subsidiado.
- **Información**: los reportes, listas, reglas y vigilancia que las normas establecen entre los mismos actores.
- **Cobertura**: nacional. Los datos de la ADRES son nacionales, por entidad.
- **Método**: cuantitativo y descriptivo, con análisis de redes ([análisis de la red](metodo/analisis-de-la-red.md)).

## Qué no cubre

- **La evolución en el tiempo** (antes y después de una norma, tendencias, series de tiempo). Solo puede aparecer como contexto.
- **El contenido clínico** y la calidad de la atención: el proyecto mira los flujos entre agentes, no el acto médico.
- **La veracidad de los datos frente a la realidad** como tema en sí mismo.
- **Otros recursos** distintos del giro directo de la UPC en la red observada, como los presupuestos máximos o los recobros ([criterios de inclusión](metodo/criterios-de-inclusion.md)).
- **Información privada o sensible**: microdatos, datos personales, clínicos o protegidos por la ley. El proyecto usa solo datos administrativos públicos, agregados por entidad ([datos personales y ética](metodo/datos-personales-y-etica.md)).

## Los productos

| Producto | Qué es | Dónde está |
|---|---|---|
| Inventario de actores | 252 actores del sistema, con identificador, tamaño, función y fuente | [`inventario-actores/`](../inventario-actores/README.md) · [método](metodo/inventario-de-actores.md) |
| Red normada | Los flujos que establecen las normas, con su norma y artículo | [`red-normada/`](../red-normada/README.md) · [método](metodo/red-normada.md) |
| Red observada | El giro directo tal como ocurrió, con los anexos de la ADRES | [`red-observada/`](../red-observada/README.md) · [método](metodo/red-observada.md) |
| Visores | Un visor interactivo de cada red | [Visores](metodo/visores.md) |

## Ver también

[Inicio](README.md) · [Glosario](glosario.md) · [Cómo seguir](como-seguir.md)
