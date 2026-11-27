---
tipo: metodo
tags: [metodo, red-observada, criterios]
---

# Criterios de inclusión

Qué entra a la [red observada](red-observada.md) y qué no, en cada nivel donde hay que decidirlo: el flujo, la fila del anexo, el nodo, el período y la naturaleza del dato.

## Qué flujo entra

- **Entra** el [giro directo](../sistema/giro-directo.md) de la [UPC](../sistema/upc.md) en los dos regímenes: el contributivo, por el proceso de compensación, y el subsidiado, por la Liquidación Mensual de Afiliados, con su hoja de complemento.
- **No entran** los demás módulos de [Lupa al Giro](../datos/lupa-al-giro.md) que no son giro directo de la UPC: recobros, presupuestos máximos, reclamaciones, residentes médicos, mecanismos de la pandemia y población migrante.

## Qué fila entra

Una fila del anexo es una operación de giro. La relación de la red es la pareja EPS–prestador dentro del mes, y su peso es la suma de sus operaciones.

- **Entra** toda fila cuya identificación del receptor sea válida y que tenga la EPS identificada. Los encabezados, títulos y totales no cumplen esa condición y quedan fuera sin filtros especiales.
- **Entran también las filas con giro en cero y las que tienen lo ordenado distinto de lo girado.** No son errores: dicen algo del proceso. Su campo de observación explica, por ejemplo, que la cuenta no existe o está bloqueada.
- **No entran** las filas sin identificación del receptor o sin código de EPS: son filas de totales y notas.
- **Códigos de EPS mal publicados.** Se corrigen solo si se cumplen dos condiciones:
  - el código no existe en la tabla de EPS del mismo mes, o pertenece a otra EPS;
  - el nombre de la EPS en la misma fila corresponde a un solo código.

  Cada corrección queda registrada y se valida contra la certificación del mes.

## Qué nodo entra

- **Todo receptor que aparezca en un anexo**, esté o no en el inventario. Si recibe recursos del sistema, es un nodo, sin importar cómo se clasifique a sí mismo.
- **Toda EPS con código en el anexo**, incluidas las intervenidas y en liquidación. Como una EPS puede tener varios códigos (uno por régimen, entre otros), los códigos se unen en entidades por su nombre.
- Los actores del [inventario](inventario-de-actores.md) que no reciben giro directo no entran a esta red.

## Qué período entra

Un mes como fotografía principal y unos pocos meses de control. No hay series de tiempo: se mapea la estructura, no su evolución.

## Qué datos entran

Solo información pública, publicada por la entidad responsable y agregada por entidad. No entran microdatos, datos personales, datos clínicos ni información reservada. Las reglas concretas están en [datos personales y ética](datos-personales-y-etica.md).

## Ver también

[Red observada](red-observada.md) · [Lupa al Giro](../datos/lupa-al-giro.md) · [Resolución 4621 de 2016](../normas/resolucion-4621-de-2016.md)
