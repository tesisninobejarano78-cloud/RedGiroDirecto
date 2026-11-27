---
tipo: concepto
tags: [concepto, redes, bipartita]
---

# Red bipartita y proyecciones

La [red observada](../metodo/red-observada.md) es **bipartita**: tiene dos tipos de nodo, EPS y prestadores, y las relaciones solo unen una EPS con un prestador. Nunca dos EPS entre sí ni dos prestadores entre sí. Eso cambia cómo se miden muchas cosas.

## Por qué bipartita

El dinero del giro directo lo gira la [ADRES](../actores/adres.md), pero lo decide la [EPS](../actores/eps.md). Si la ADRES fuera un nodo, la red sería una estrella con la ADRES en el centro, central por construcción, y no mostraría nada nuevo. La red bipartita EPS → prestador, en cambio, muestra de qué EPS depende cada prestador.

## La matriz B

La red se puede escribir como una matriz **B**: una fila por EPS y una columna por prestador. Cada celda vale 1 si la EPS le giró a ese prestador en el mes y 0 si no. Con lo girado en lugar de 1, la matriz es ponderada.

## Las dos proyecciones

Una proyección convierte la red bipartita en una red de un solo tipo de nodo:

- **Proyección EPS–EPS**: C = B·Bᵀ. Dos EPS quedan unidas si comparten prestadores, y el peso es cuántos comparten.
- **Proyección prestador–prestador**: P = Bᵀ·B. Dos prestadores quedan unidos si reciben de las mismas EPS, y el peso es cuántas EPS comparten.

El número de prestadores compartidos depende del tamaño de las carteras. El **índice de Jaccard** lo normaliza: los prestadores compartidos sobre la unión de las dos carteras. Vale 0 si no comparten ninguno y 1 si tienen exactamente los mismos.

En la proyección de prestadores, un prestador que recibe de una sola EPS solo puede compartir esa. Por eso el programa usa un umbral de EPS compartidas y revisa qué tan sensibles son los resultados a ese umbral.

Sobre cada proyección se calculan grado, fuerza y comunidades con Louvain ([Blondel et al., 2008](../referencias/blondel-2008.md)); en la de EPS, sobre el Jaccard. Las comunidades se comparan con el departamento y entre meses ([métricas de redes](metricas-de-redes.md)).

## Qué cambia al medir en una red bipartita

- **Centralidad**: los valores se normalizan con el tamaño de cada lado ([Borgatti y Everett, 1997](../referencias/borgatti-everett-1997.md)).
- **Intermediación**: con dirección vale cero para todos, porque todas las flechas van de EPS a prestador. Por eso se calcula sin dirección.
- **Comunidades**: la modularidad estándar supone que cualquier par de nodos se puede unir, y en una bipartita no es así. Se usa la de [Barber (2007)](../referencias/barber-2007.md), cuyo término de azar solo une EPS con prestadores.
- **Correlaciones de grado**: con grados muy desiguales, algo de disortatividad sale por construcción, porque no puede haber dos aristas entre el mismo par.

## En el repositorio

`red-observada/proyecciones-y-comparacion.py` calcula las dos proyecciones. Sus salidas y figuras están en `red-observada/salida/proyecciones/`.

## Ver también

[Modelado de redes](modelado-de-redes.md) · [Análisis de la red](../metodo/analisis-de-la-red.md) · [Prestadores](../actores/prestadores.md)
