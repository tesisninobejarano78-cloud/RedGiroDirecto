---
tipo: inicio
tags: [inicio]
---

# Cerebro del proyecto RedGiroDirecto

Esta carpeta es una bóveda de Obsidian con el conocimiento sobre el que se construyó el proyecto:

- las normas que establecen los flujos de dinero y de información del sistema de salud colombiano;
- los actores y lo que hace cada uno;
- los conceptos del sistema y de la teoría de redes;
- el método con que se armaron el inventario y las dos redes;
- las fuentes de datos y las referencias académicas.

Sirve para entender el proyecto y para seguir trabajando sobre él. Los datos, los programas y los resultados están en las otras carpetas del repositorio. Cada página del cerebro dice qué archivo del repositorio usa.

## Qué estudia el proyecto

La estructura de la red de flujos de recursos e información entre la ADRES, las EPS y los prestadores de salud bajo el giro directo en Colombia, y qué nodos y conexiones concentran o pueden restringir esos flujos. Ver [el proyecto](proyecto.md).

## Cómo abrirlo

- **En Obsidian**: «Abrir carpeta como bóveda» y elegir esta carpeta, `cerebro/`. No necesita complementos. La vista de grafo muestra cómo se conectan las páginas, con un color por carpeta.
- **Sin Obsidian**: son archivos Markdown con enlaces normales, así que se leen en GitHub o en cualquier editor.

Los enlaces a las otras carpetas del repositorio (por ejemplo, al README de la red normada) funcionan en GitHub y en el explorador de archivos. Dentro de Obsidian no se abren, porque la bóveda es solo esta carpeta.

## Por dónde empezar

1. [El proyecto](proyecto.md): la pregunta, qué cubre y qué no.
2. [Sistema de salud](sistema/sistema-de-salud.md) y [giro directo](sistema/giro-directo.md): lo mínimo para entender el sistema.
3. [Modelado de redes](redes/modelado-de-redes.md): por qué una red y cuáles son las dos redes.
4. [Red normada](metodo/red-normada.md) y [red observada](metodo/red-observada.md): cómo se construyó cada una.
5. [Cómo seguir](como-seguir.md): qué hacer para actualizar o ampliar el trabajo.

Si aparece una sigla desconocida, está en el [glosario](glosario.md).

## Cómo está organizado

| Carpeta | Qué tiene |
|---|---|
| [`sistema/`](sistema/sistema-de-salud.md) | Conceptos del sistema de salud: el sistema, el flujo de recursos, la UPC, el giro directo y el sistema único de información |
| [`actores/`](actores/otros-actores-de-la-red.md) | Una página por actor principal (ADRES, EPS, prestadores, Supersalud, Ministerio de Salud) y una con los demás actores de la red |
| [`normas/`](normas/indice-de-normas.md) | Una página por norma: qué fija, qué vínculos de la red sostiene y dónde leerla |
| [`redes/`](redes/metricas-de-redes.md) | Conceptos de teoría de redes: la red multicapa, la red bipartita y sus proyecciones, y las métricas |
| [`metodo/`](metodo/analisis-de-la-red.md) | Cómo se hicieron el inventario, las dos redes, el análisis y los visores, y las reglas de datos personales |
| [`datos/`](datos/lupa-al-giro.md) | Las fuentes de datos públicas: qué traen, dónde están y qué cuidados piden |
| [`referencias/`](referencias/indice-de-referencias.md) | Las referencias académicas del método |

## Relación con el resto del repositorio

| Carpeta del repositorio | Páginas del cerebro que la explican |
|---|---|
| [`inventario-actores/`](../inventario-actores/README.md) | [Inventario de actores](metodo/inventario-de-actores.md) · [Registros del inventario](datos/registros-del-inventario.md) · [COLEV 2022](datos/colev-2022.md) |
| [`red-normada/`](../red-normada/README.md) | [Red normada](metodo/red-normada.md) · [Índice de normas](normas/indice-de-normas.md) · [Otros actores de la red](actores/otros-actores-de-la-red.md) |
| [`red-observada/`](../red-observada/README.md) | [Red observada](metodo/red-observada.md) · [Criterios de inclusión](metodo/criterios-de-inclusion.md) · [Análisis de la red](metodo/analisis-de-la-red.md) · [Lupa al Giro](datos/lupa-al-giro.md) |

## Licencia

Los textos de esta carpeta se publican con la licencia Creative Commons Atribución-CompartirIgual 4.0 ([`LICENSE-DATOS`](../LICENSE-DATOS)), igual que la mayor parte de los datos del repositorio. Los datos de la red observada tienen una licencia no comercial, por los términos de uso de la ADRES. Qué archivo lleva cada licencia está en [`LICENCIAS.md`](../LICENCIAS.md). La autoría y la forma de citar están en el [README del repositorio](../README.md).
