---
tipo: metodo
tags: [metodo, red-observada, giro-directo]
---

# Red observada

Es la red «de hecho»: el [giro directo](../sistema/giro-directo.md) tal como ocurrió, construido con los anexos mensuales que publica la [ADRES](../actores/adres.md) en [Lupa al Giro](../datos/lupa-al-giro.md). Dice qué EPS ordenó pagos a qué prestadores y cuánto dinero pasó por cada relación. Se compara con la [red normada](red-normada.md). Los programas y las salidas están en [`red-observada/`](../../red-observada/README.md).

## Cómo se lee

- Es una **red bipartita**: hay dos tipos de nodo, EPS y prestadores, y las relaciones solo van de una EPS a un prestador ([red bipartita y proyecciones](../redes/red-bipartita-y-proyecciones.md)).
- Una relación existe si en el mes la ADRES le giró dinero a ese prestador por cuenta de esa EPS. **La EPS no paga**: la flecha dice por cuenta de quién se giró.
- El peso de la relación es lo girado en el mes. Se suman el proceso mensual y el complemento, y los dos regímenes.
- La ADRES no es un nodo de esta red: ejecuta todos los pagos. En el visor aparece en la capa de información.
- Cada prestador se identifica por su NIT. Las identificaciones que no tienen forma de NIT de empresa se juntan en un solo nodo, `PN-AGREGADO` ([datos personales y ética](datos-personales-y-etica.md)).

## Cómo se construye

1. **Descarga.** Se bajan los anexos de las tres series, de enero de 2024 en adelante. Un manifiesto guarda la huella de cada archivo.
2. **Lectura.** Cada fila de un anexo es una operación de giro, no una relación. La relación es la pareja EPS–prestador dentro del mes; su peso es la suma de sus operaciones, y el número de operaciones queda como dato. Qué filas entran se explica en los [criterios de inclusión](criterios-de-inclusion.md).
3. **Comprobaciones.** La suma de las relaciones se compara con la certificación del giro del subsidiado, EPS por EPS y mes por mes. También se reproducen las cifras del Boletín 72 de la ADRES.
4. **Clasificación.** Cada NIT se cruza con el [REPS](../datos/reps.md) para saber si es Empresa Social del Estado (ESE), IPS pública, privada o mixta, y en qué departamento está. Los que no están en el REPS se cruzan con el [inventario de actores](inventario-de-actores.md).
5. **Análisis.** Todo es descriptivo: se mide la estructura de la red, no se estiman causas ([análisis de la red](analisis-de-la-red.md)).
6. **Comparación con la norma.** Los prestadores se agrupan en las mismas clases de actor que usa la red normada. Así las dos redes se comparan sobre los mismos nodos.

## El mes que se analiza

Se toma un mes como fotografía principal y otros como control, para ver si los resultados dependen del mes elegido. En el repositorio el mes principal es septiembre de 2026, y junio, julio y agosto de 2026 son de control. Se cambian en `configuracion.py`. No es un análisis de cómo cambia la red en el tiempo, sino de su estructura.

## Cómo se corre

Se necesitan Python 3.12 o más reciente y las librerías de [`requirements.txt`](../../requirements.txt): pandas, numpy, scipy, networkx, matplotlib y openpyxl, en las versiones con que se probó. Desde la carpeta `red-observada/`:

```
python correr-todo.py
```

Corre los doce pasos en orden, desde la descarga hasta el visor. Las opciones (`--sin-descarga`, `--reps-nuevo`, `--desde N`) están en el README de la carpeta.

## Límites

- El giro directo no es todo lo que recibe un prestador: también cobra a la EPS por fuera del giro y a otros pagadores.
- Solo se mide el giro directo de la UPC. Los presupuestos máximos y otros recursos no están en esta red.
- La clase de cada prestador depende de cómo está inscrito en el REPS en la fecha del extracto.

## Ver también

[Lupa al Giro](../datos/lupa-al-giro.md) · [Visores](visores.md) · [Prestadores](../actores/prestadores.md)
