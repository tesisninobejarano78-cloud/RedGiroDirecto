---
tipo: referencia
tags: [referencia, particiones]
---

# Danon et al. (2005): información mutua normalizada

**Referencia**: Danon, L., Díaz-Guilera, A., Duch, J. y Arenas, A. (2005). Comparing community structure identification. *Journal of Statistical Mechanics: Theory and Experiment, 2005*(09), P09008.

Acceso: <https://doi.org/10.1088/1742-5468/2005/09/P09008>

## Qué propone

Compara métodos de detección de comunidades y propone medir la coincidencia entre dos particiones con la información mutua normalizada (NMI).

## Para qué la usa el proyecto

- La NMI se calcula sobre la matriz de confusión entre las dos particiones. Con ella se mide si las comunidades coinciden con el departamento del prestador y si se mantienen entre meses.
- `verificar-metodos.py` la compara con una implementación independiente.

## Ver también

[Métricas de redes](../redes/metricas-de-redes.md) · [Análisis de la red](../metodo/analisis-de-la-red.md) · [Índice de referencias](indice-de-referencias.md)
