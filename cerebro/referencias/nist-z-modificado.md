---
tipo: referencia
tags: [referencia, inferencia]
---

# NIST: detección de atípicos con el z modificado

**Referencia**: NIST/SEMATECH (s. f.). 1.3.5.17. Detection of Outliers. En *e-Handbook of Statistical Methods*. National Institute of Standards and Technology.

Acceso: <https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm>

## Qué propone

El manual de métodos estadísticos del NIST explica cómo detectar observaciones atípicas.

## Para qué la usa el proyecto

- El z modificado de Iglewicz y Hoaglin es M = 0,6745 (x − mediana) / MAD, donde MAD es la desviación absoluta mediana. Se marcan como posibles atípicos los valores con |M| > 3,5.
- Es robusto porque usa la mediana: los mismos atípicos no lo inflan, como sí inflarían la desviación estándar. Con él se marcan los prestadores lejos de la curva fuerza–grado.

## Ver también

[Métricas de redes](../redes/metricas-de-redes.md) · [Análisis de la red](../metodo/analisis-de-la-red.md) · [Índice de referencias](indice-de-referencias.md)
