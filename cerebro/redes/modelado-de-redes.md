---
tipo: concepto
tags: [concepto, redes]
---

# Modelado de redes

Representar el sistema de salud como una red, o grafo, permite estudiar su estructura en lugar de mirar a cada actor por separado. Los actores son **nodos** y los flujos entre ellos son **aristas** (o vínculos). Es lo que permite tratar el dinero y la información como dos capas de una misma red. La revisión general del campo es la de [Newman (2003)](../referencias/newman-2003-estructura-y-funcion.md).

## Las piezas

- **Nodo**: un actor. En la [red normada](../metodo/red-normada.md), cada nodo es una clase de actor (por ejemplo, «EPS»). En la [red observada](../metodo/red-observada.md), cada nodo es una entidad: una EPS o un prestador con su NIT.
- **Arista dirigida**: el flujo tiene sentido, de quien envía a quien recibe.
- **Arista ponderada**: el flujo tiene un peso. En la red observada, el peso es lo girado en el mes.
- **Capa**: un tipo de flujo. Aquí hay dos: la de [recursos](../sistema/flujo-de-recursos.md) y la de [información](../sistema/sistema-unico-de-informacion.md).

## Red multicapa

Cuando hay varias capas de aristas sobre los mismos actores, la red es multicapa ([Kivelä et al., 2014](../referencias/kivela-2014.md)). Sirve para estudiar cómo se acoplan las capas: por ejemplo, si una decisión que viaja por la capa de información cambia quién recibe dinero en la capa de recursos.

En este proyecto las dos capas no tienen exactamente los mismos nodos. La de recursos de la red observada tiene EPS y prestadores; la de información tiene además a la [ADRES](../actores/adres.md), la [Supersalud](../actores/supersalud.md) y el [Ministerio de Salud](../actores/ministerio-de-salud.md). Las capas se unen por los actores que comparten, sobre todo las EPS.

## Red de derecho y red de hecho

El proyecto construye dos redes y las compara:

| | Red normada | Red observada |
|---|---|---|
| Qué es | Lo que las normas establecen | Lo que pasó con el giro directo |
| Nodos | Clases de actor | Entidades (EPS y prestadores) |
| Fuente | [Normas](../normas/indice-de-normas.md) | [Lupa al Giro](../datos/lupa-al-giro.md) |
| Capas | Recursos e información | Sobre todo recursos (giro directo) |

Como una tiene clases y la otra entidades, no se comparan sus métricas directamente. Se agrupan los prestadores en las mismas clases y se compara qué vínculos aparecen ([análisis de la red](../metodo/analisis-de-la-red.md); [Tantardini et al., 2019](../referencias/tantardini-2019.md)).

## Ver también

[Red bipartita y proyecciones](red-bipartita-y-proyecciones.md) · [Métricas de redes](metricas-de-redes.md) · [Visores](../metodo/visores.md)
