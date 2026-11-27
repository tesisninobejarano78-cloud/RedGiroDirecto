---
tipo: metodo
tags: [metodo, red-normada]
---

# Red normada

Es la red «de derecho»: los flujos de dinero y de información que las normas vigentes establecen entre los actores del sistema. Quién debe enviarle dinero a quién y quién debe enviarle información a quién. Tiene 25 actores y 49 vínculos, 26 de recursos y 23 de información, y cada vínculo tiene su norma con el artículo. Los archivos, el programa y el visor están en [`red-normada/`](../../red-normada/README.md).

## Cómo se construye

1. **Actores.** Salen del [inventario de actores](inventario-de-actores.md), en su nivel base: cada clase es un nodo. «EPS» es un solo nodo, no veinticinco. La red habla de papeles, no de entidades una por una.
2. **Vínculos.** Un vínculo entra solo si una norma lo establece y esa norma se leyó en su fuente oficial. Cuando una norma cambió, se usa el texto vigente. Las normas están en el [índice de normas](../normas/indice-de-normas.md).
3. **Dos capas.** Cada vínculo es de recursos (dinero) o de información (reportes, reglas, vigilancia, planillas). Ver [modelado de redes](../redes/modelado-de-redes.md).
4. **Sentido.** El vínculo va de quien envía a quien recibe.
5. **Lo que queda por fuera.** Si ninguna norma conecta a dos actores, no hay vínculo, aunque el actor sea importante en la práctica. Los contratos entre EPS y prestadores entran como un solo vínculo general (pago contractual), porque la norma no dice con quién contrata cada EPS. Los actores del inventario sin vínculos aparecen en el visor en una cuadrícula aparte.

## Los códigos de los vínculos

Cada vínculo tiene un código: R para recursos, I para información. Los números no son consecutivos porque un código retirado no se reutiliza. Las páginas de normas y de actores usan estos códigos.

## Observabilidad

Cada vínculo dice si se puede ver con datos públicos:

- **observable**: un dato abierto lo registra pareja por pareja, como el [giro directo](../sistema/giro-directo.md) en [Lupa al Giro](../datos/lupa-al-giro.md);
- **parcial**: solo hay cifras agregadas;
- **no observable**: no hay dato público.

Esto marca hasta dónde se puede comparar la norma con lo que ocurre: la [red observada](red-observada.md) solo puede mirar los vínculos observables.

## Archivos principales

| Archivo | Qué es |
|---|---|
| `aristas-normadas.csv` | Los 49 vínculos con su norma. Es la entrada principal |
| `posiciones-normada.csv` | Dónde se dibuja cada actor en el visor |
| `construir-red-normada.py` | Une los vínculos con el inventario, comprueba que todo cuadre y genera las salidas y el visor |
| `visor-red-normada.html` | El [visor](visores.md) interactivo |

## Cómo agregar o corregir un vínculo

Se edita `aristas-normadas.csv` con su norma y artículo, y se vuelve a correr `python construir-red-normada.py`. Si el vínculo trae un actor nuevo, ese actor tiene que estar en el inventario y necesita una posición. El programa se detiene con un mensaje si algo no cuadra. Ver [cómo seguir](../como-seguir.md).

## Ver también

[Índice de normas](../normas/indice-de-normas.md) · [Otros actores de la red](../actores/otros-actores-de-la-red.md) · [Análisis de la red](analisis-de-la-red.md)
