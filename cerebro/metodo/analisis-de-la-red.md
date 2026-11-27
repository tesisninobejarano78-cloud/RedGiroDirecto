---
tipo: metodo
tags: [metodo, red-observada, metricas]
---

# Análisis de la red

Qué se mide sobre la [red observada](red-observada.md), con qué método y con qué referencia, y cómo se compara con la [red normada](red-normada.md). El análisis es **descriptivo**: mide la estructura de la red y no estima causas. Esta página explica el método. Las cifras que produce están en las salidas del repositorio (`red-observada/salida/`).

## Qué se mide

| Bloque | Qué se mide | Referencia | Programa |
|---|---|---|---|
| Centralidad | Grado, fuerza, intermediación y cercanía de cada nodo, normalizadas para redes bipartitas; distancia media y diámetro | [Borgatti y Everett (1997)](../referencias/borgatti-everett-1997.md), [Brandes (2001)](../referencias/brandes-2001.md) | `teoria-redes-observada.py`, `metricas-red-observada.py` |
| Concentración | Distribución del grado; heterogeneidad; índice de Gini y curva de Lorenz del dinero; participación de las cuatro mayores (CR4) e índice de Herfindahl-Hirschman (HHI) | [Clauset et al. (2009)](../referencias/clauset-2009.md), para no ajustar leyes de potencias | `teoria-redes-observada.py` |
| Fuerza y grado | Cómo crece lo que recibe un prestador con su número de EPS: s(k) ~ k^β, con intervalo bootstrap | [Barrat et al. (2004)](../referencias/barrat-2004.md) | `teoria-redes-observada.py` |
| Dependencia | Qué parte de lo que recibe un prestador viene de su EPS principal; aristas puente | — | `metricas-red-observada.py` |
| Correlaciones de grado | Asortatividad y grado medio de los vecinos | [Newman (2002)](../referencias/newman-2002.md), [Newman (2003)](../referencias/newman-2003-mezcla.md), [Pastor-Satorras et al. (2001)](../referencias/pastor-satorras-2001.md) | `teoria-redes-observada.py` |
| Comunidades | Modularidad bipartita de Barber, optimizada con BRIM; Louvain como comparación | [Barber (2007)](../referencias/barber-2007.md), [Blondel et al. (2008)](../referencias/blondel-2008.md), [Newman y Girvan (2004)](../referencias/newman-girvan-2004.md) | `teoria-redes-observada.py` |
| Comparar particiones | Si las comunidades coinciden con el departamento del prestador, y si se mantienen entre meses (NMI y ARI, con prueba de permutaciones) | [Danon et al. (2005)](../referencias/danon-2005.md), [Vinh et al. (2010)](../referencias/vinh-2010.md), [Phipson y Smyth (2010)](../referencias/phipson-smyth-2010.md) | `teoria-redes-observada.py` |
| Proyecciones | EPS–EPS y prestador–prestador, con el índice de Jaccard | [Red bipartita y proyecciones](../redes/red-bipartita-y-proyecciones.md) | `proyecciones-y-comparacion.py` |
| Casos para mirar de cerca | Prestadores lejos de la curva fuerza–grado (z modificado mayor que 3,5) y relaciones ordenadas y no giradas | [NIST, z modificado](../referencias/nist-z-modificado.md) | `contraste-y-acoplamiento.py` |

Las definiciones de cada métrica están en [métricas de redes](../redes/metricas-de-redes.md).

## Cómo se compara con la norma

1. **Sobre los mismos nodos.** La red observada tiene entidades y la normada tiene clases. Por eso los prestadores se agrupan en las clases de la red normada (IPS, cajas de compensación, gestores farmacéuticos, droguerías, importadores, industria y proveedores sin REPS). Se compara qué vínculos normados aparecen, con cuánto dinero, y se resume con el índice de Jaccard. No se comparan métricas de una red con las de la otra ([Tantardini et al., 2019](../referencias/tantardini-2019.md)).
2. **Densidad sobre las mismas clases.** Para cada EPS, a cuántas de las clases que la norma habilita llega el giro.
3. **Las reglas de la [Ley 1122 de 2007](../normas/ley-1122-de-2007.md), EPS por EPS.**
   - La del art. 16 es solo una referencia: el giro directo no es todo el gasto contratado.
   - El parágrafo del art. 15 pide IPS públicas en la red del contributivo.
   - El límite del 30 % con IPS propias no se puede medir, porque la propiedad de las IPS no es pública en forma estructurada.

## Las dos capas juntas

Las dos capas comparten las EPS: forman una red multicapa ([Kivelä et al., 2014](../referencias/kivela-2014.md)). Se mide qué parte de la red de recursos depende, en el mes, de EPS cuyo giro quedó condicionado por la capa de información: comunicaciones de la Supersalud que dirigen o detienen giro, y retenciones del giro. Con 25 EPS, las asociaciones EPS por EPS son descriptivas.

## Lo que no se hace, y por qué

- **No se ajusta una ley de potencias al grado.** Un prestador recibe de 25 EPS como máximo, y del lado de las EPS solo hay 25 valores (Clauset et al., 2009).
- **No se calculan intermediación ni cercanía dirigidas, ni con el dinero como distancia.** Con dirección dan cero por construcción, y el dinero no es una distancia.
- **No se calculan centralidades de la capa de información.** Es una estrella alrededor de la ADRES, central por construcción.

## Cómo leer los resultados

- Una métrica de concentración o de dependencia **describe una posición en la red**. No es una imputación de conducta a una entidad.
- Una anomalía señala dónde mirar; no es una irregularidad.
- Las comunidades salen de métodos que buscan la mejor partición sin garantía de encontrarla. Por eso se fijan las semillas y se comparan varias particiones. La modularidad tiene además un límite de resolución: las EPS pequeñas pueden quedar fundidas con otras ([Fortunato y Barthélemy, 2007](../referencias/fortunato-barthelemy-2007.md)).

## Código y pruebas

- `redes_metodos.py` implementa lo que NetworkX no trae: modularidad de Barber y BRIM, NMI y ARI, valor p de permutación, Gini, Lorenz y heterogeneidad.
- `verificar-metodos.py` prueba esos métodos contra casos de respuesta conocida. Si una prueba falla, `correr-todo.py` se detiene antes del análisis.

Las librerías son [NetworkX](../referencias/hagberg-2008-networkx.md), [NumPy](../referencias/harris-2020-numpy.md), [SciPy](../referencias/virtanen-2020-scipy.md) y pandas.

## Ver también

[Métricas de redes](../redes/metricas-de-redes.md) · [Índice de referencias](../referencias/indice-de-referencias.md) · [Visores](visores.md)
