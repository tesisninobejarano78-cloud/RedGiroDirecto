---
tipo: referencia
tags: [referencia, correlaciones]
---

# Newman (2003): patrones de mezcla

**Referencia**: Newman, M. E. J. (2003). Mixing patterns in networks. *Physical Review E, 67*(2), 026126.

Acceso: <https://doi.org/10.1103/PhysRevE.67.026126>

## Qué propone

Estudia la tendencia de los nodos a unirse con nodos parecidos o distintos, en particular por grado.

## Para qué la usa el proyecto

- Da la versión dirigida de la asortatividad: correlaciona el grado de salida del nodo de origen con el grado de entrada del nodo de destino.
- En la red observada todas las aristas van de una EPS a un prestador, así que r correlaciona el número de prestadores de la EPS con el número de EPS del prestador. `verificar-metodos.py` comprueba que el cálculo coincide con el de NetworkX.

## Ver también

[Métricas de redes](../redes/metricas-de-redes.md) · [Análisis de la red](../metodo/analisis-de-la-red.md) · [Índice de referencias](indice-de-referencias.md)
