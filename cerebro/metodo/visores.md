---
tipo: metodo
tags: [metodo, visualizacion]
---

# Visores de las redes

Cada red tiene un visor interactivo: un solo archivo HTML que se abre con doble clic en cualquier navegador, sin instalar nada y sin conexión a internet. Lo genera Python a partir de una plantilla y de las tablas de nodos y aristas.

- Red normada: [`red-normada/visor-red-normada.html`](../../red-normada/visor-red-normada.html)
- Red observada: [`red-observada/visor-red-observada.html`](../../red-observada/visor-red-observada.html)

## Cómo se dibuja

- **Solo en dos dimensiones.** En 3D los nodos se tapan, la perspectiva deforma tamaños y distancias, y la figura no se puede imprimir.
- **Las dos capas en una sola gráfica.** Los recursos van en línea continua azul y la información en línea punteada naranja. Así cada actor ocupa el mismo lugar en las dos capas y se comparan a simple vista. La forma de la línea basta para distinguir la capa sin depender del color.
- **El color del nodo dice en qué capas participa**: azul solo recursos, naranja solo información, aguamarina las dos, gris sin vínculos.
- **La forma del nodo dice su grupo**: círculo Estado, cuadrado sector privado, triángulo sociedad civil, rombo academia.
- Lo que no cumple los filtros se atenúa, o se oculta si se marca esa opción.
- Hay una **vista de tabla** equivalente, que es también la forma accesible de leer la gráfica.

## Qué se puede hacer

**En el visor de la red normada:**

- filtrar por capa, por tipo de flujo y por [observabilidad](red-normada.md);
- resaltar a los actores por grupo, sector o tamaño;
- hacer clic en un actor para ver sus datos y sus vínculos;
- ver la tabla de vínculos con la norma de cada uno.

**En el visor de la red observada:**

- cambiar de mes;
- mostrar u ocultar cada capa;
- filtrar por tipo de prestador y por departamento;
- colorear por la dependencia de la EPS principal;
- buscar una EPS, un prestador o un NIT.

## Cómo se regeneran

- Red normada: `python construir-red-normada.py`, en `red-normada/`.
- Red observada: el paso 12, `construir-visor-observada.py`, que también corre `correr-todo.py`.

Si se cambia la plantilla del visor, hay que volver a correr el programa para que el visor la use.

## Ver también

[Red normada](red-normada.md) · [Red observada](red-observada.md) · [Modelado de redes](../redes/modelado-de-redes.md)
