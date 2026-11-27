---
tipo: referencia
tags: [referencia, comunidades]
---

# Barber (2007): modularidad bipartita

**Referencia**: Barber, M. J. (2007). Modularity and community detection in bipartite networks. *Physical Review E, 76*(6), 066102.

Acceso: <https://doi.org/10.1103/PhysRevE.76.066102>

## Qué propone

Define una modularidad apropiada para redes bipartitas, cuyo término de azar solo une nodos de lados distintos, y un algoritmo para hallar las comunidades (BRIM). El algoritmo se apoya en que las comunidades de un lado inducen las del otro.

## Para qué la usa el proyecto

- Es la medida con que se buscan las comunidades de la red observada.
- BRIM asigna por turnos cada lado a la comunidad que más aporta, dado el otro lado. `redes_metodos.py` lo implementa con varios arranques y un paso de fusión de comunidades.
- `verificar-metodos.py` comprueba que el cálculo coincide con la definición y que da 1 − 1/c en c bloques completos.

## Ver también

[Métricas de redes](../redes/metricas-de-redes.md) · [Red bipartita y proyecciones](../redes/red-bipartita-y-proyecciones.md) · [Análisis de la red](../metodo/analisis-de-la-red.md) · [Índice de referencias](indice-de-referencias.md)
