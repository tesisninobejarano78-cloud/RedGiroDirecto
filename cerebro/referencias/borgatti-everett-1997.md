---
tipo: referencia
tags: [referencia, centralidad]
---

# Borgatti y Everett (1997): redes de dos modos

**Referencia**: Borgatti, S. P. y Everett, M. G. (1997). Network analysis of 2-mode data. *Social Networks, 19*(3), 243–269.

Acceso: <https://doi.org/10.1016/S0378-8733(96)00301-2>

## Qué propone

Explica cuándo y cómo cambia el análisis de redes cuando los datos tienen dos clases de nodo, incluida la centralidad.

## Para qué la usa el proyecto

- Las centralidades de grado, cercanía e intermediación se normalizan por el máximo posible en un grafo bipartito con esos dos lados, no por el de un grafo cualquiera.
- NetworkX aplica esta normalización en `bipartite.closeness_centrality` y `bipartite.betweenness_centrality`.

## Ver también

[Métricas de redes](../redes/metricas-de-redes.md) · [Red bipartita y proyecciones](../redes/red-bipartita-y-proyecciones.md) · [Análisis de la red](../metodo/analisis-de-la-red.md) · [Índice de referencias](indice-de-referencias.md)
