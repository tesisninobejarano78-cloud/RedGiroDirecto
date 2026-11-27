---
tipo: referencia
tags: [referencia, inferencia]
---

# Phipson y Smyth (2010): valores p de permutación

**Referencia**: Phipson, B. y Smyth, G. K. (2010). Permutation p-values should never be zero: calculating exact p-values when permutations are randomly drawn. *Statistical Applications in Genetics and Molecular Biology, 9*(1), artículo 39.

Acceso: <https://doi.org/10.2202/1544-6115.1585>

## Qué propone

Los valores p de permutación se suelen subestimar. Cuando las permutaciones se sortean, el valor p exacto es (b + 1) / (m + 1).

## Para qué la usa el proyecto

- En la fórmula, b es el número de permutaciones con un valor igual o más extremo que el observado y m el número de permutaciones. Con m permutaciones, el menor valor posible es 1 / (m + 1): nunca cero.
- Es la fórmula de las pruebas de permutaciones de `redes_metodos.py`.

## Ver también

[Métricas de redes](../redes/metricas-de-redes.md) · [Análisis de la red](../metodo/analisis-de-la-red.md) · [Índice de referencias](indice-de-referencias.md)
