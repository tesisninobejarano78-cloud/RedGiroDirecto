---
tipo: concepto
tags: [concepto, redes, metricas]
---

# Métricas de redes

Qué mide cada métrica que usa el [análisis de la red](../metodo/analisis-de-la-red.md) y cómo se lee en la red bipartita EPS → prestador ([red bipartita y proyecciones](red-bipartita-y-proyecciones.md)).

## Grado y fuerza

- El **grado** *k* de un nodo es su número de vecinos. El de una EPS es a cuántos prestadores se les gira por su cuenta; el de un prestador, de cuántas EPS recibe.
- La **fuerza** *s* es la suma de los pesos de sus aristas: lo girado o lo recibido en el mes.
- **Fuerza contra grado**: se ajusta la curva *s(k)* ~ *k*^β ([Barrat et al., 2004](../referencias/barrat-2004.md)). Si β es mayor que 1, los nodos con más vínculos también reciben más por vínculo. Los nodos muy lejos de la curva son casos para mirar de cerca. Se detectan con el z modificado ([NIST](../referencias/nist-z-modificado.md)), que no se deja inflar por los mismos atípicos.

## Distribución y concentración

- **Distribución del grado** *P(k)*: la fracción de nodos con grado *k*. Se dibuja acumulada, a menudo en escala logarítmica.
- **Heterogeneidad** ⟨k²⟩/⟨k⟩: mayor cuanto más desigual es la red.
- **Gini y curva de Lorenz**: qué tan desigual es el reparto del dinero. Gini 0 es reparto igual; cerca de 1, todo en pocos.
- **CR4 y HHI**: la participación de las cuatro mayores y el índice de Herfindahl-Hirschman, medidas usuales de concentración.
- **Cuidado**: no se ajusta una ley de potencias. Una recta en escala log-log no basta para llamar a una red «libre de escala» ([Clauset et al., 2009](../referencias/clauset-2009.md)). Aquí, además, el grado de un prestador tiene un techo: el número de EPS.

## Dependencia

Qué parte de lo que recibe un prestador por giro directo viene de su EPS principal. Un prestador que depende de una sola EPS queda expuesto si esa EPS deja de ordenarle giro. Una **arista puente** es una relación que, si se quita, parte la red; casi siempre porque el prestador queda aislado.

## Correlaciones de grado

- **Asortatividad** *r*: la correlación entre los grados de los dos extremos de cada arista ([Newman, 2002](../referencias/newman-2002.md); versión dirigida en [Newman, 2003](../referencias/newman-2003-mezcla.md)). Si *r* > 0, los nodos con muchos vínculos se unen con otros que también tienen muchos; si *r* < 0, con los que tienen pocos.
- **Grado medio de los vecinos** *k_nn(k)*: el grado promedio de los vecinos de los nodos de grado *k* ([Pastor-Satorras et al., 2001](../referencias/pastor-satorras-2001.md)). Muestra la forma de la correlación, no solo su signo.

## Intermediación y cercanía

- **Intermediación**: la fracción de caminos más cortos entre pares de nodos que pasan por un nodo dado. **Cercanía**: el inverso de la distancia media de un nodo a todos los demás. Las dos son definiciones de Freeman; el cálculo sigue a [Brandes (2001)](../referencias/brandes-2001.md) y la normalización para bipartitas a [Borgatti y Everett (1997)](../referencias/borgatti-everett-1997.md).
- En esta red miden una posición en la estructura, no un camino que recorra el dinero. Se calculan sin dirección.

## Comunidades

- **Modularidad** *Q*: la fracción de aristas dentro de los grupos menos la que se esperaría al azar conservando los grados ([Newman y Girvan, 2004](../referencias/newman-girvan-2004.md)).
- **Barber y BRIM**: en una red bipartita se usa la modularidad de [Barber (2007)](../referencias/barber-2007.md), optimizada con el algoritmo BRIM. **Louvain** ([Blondel et al., 2008](../referencias/blondel-2008.md)) se usa como comparación y en las proyecciones.
- **Límite de resolución**: la modularidad puede fundir grupos pequeños dentro de otros más grandes ([Fortunato y Barthélemy, 2007](../referencias/fortunato-barthelemy-2007.md)).

## Comparar particiones

Para saber si una partición en comunidades coincide con otra (el departamento del prestador, o la del mes anterior):

- **NMI**, información mutua normalizada ([Danon et al., 2005](../referencias/danon-2005.md)): 1 si las particiones son iguales, cerca de 0 si no se parecen;
- **ARI**, índice de Rand ajustado ([Vinh et al., 2010](../referencias/vinh-2010.md)): corrige el parecido que se daría por azar;
- **prueba de permutaciones**: se barajan las etiquetas muchas veces y se ve qué tan raro es el valor observado. El valor p se calcula como recomiendan [Phipson y Smyth (2010)](../referencias/phipson-smyth-2010.md), sin que pueda dar cero.

## Ver también

[Modelado de redes](modelado-de-redes.md) · [Índice de referencias](../referencias/indice-de-referencias.md)
