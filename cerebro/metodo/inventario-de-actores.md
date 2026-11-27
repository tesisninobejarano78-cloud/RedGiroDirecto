---
tipo: metodo
tags: [metodo, inventario, actores]
---

# Inventario de actores

Es la tabla de los actores del sistema de salud colombiano de la que salen los nodos de las redes: quién es cada uno, su identificador oficial, su tamaño, su función y la norma o el registro que confirma que existe. Tiene 252 actores. Los datos, los programas y el diccionario de columnas están en [`inventario-actores/`](../../inventario-actores/README.md).

## Antes de construirlo

Se buscó si ya existía una base así. Existía un antecedente académico, el [mapa COLEV 2022](../datos/colev-2022.md), con 84 organizaciones pero sin identificador ni tamaño. En el portal de datos abiertos hay registros por clase de actor (prestadores, afiliados, entidades del Estado), pero no un inventario de todo el sistema. El inventario parte de COLEV, recoge 49 de sus organizaciones y agrega las demás con [registros oficiales](../datos/registros-del-inventario.md).

## Las reglas

1. **Frontera.** Entra todo actor que la ley nombra como parte del sistema, más todo actor que condicione de forma identificable el flujo de recursos o de información: industria, operadores logísticos, gremios, academia, sociedad civil, órganos de control, poder legislativo y judicial.
2. **Regla de entrada.** Un actor entra solo si una norma o un registro oficial confirma que existe y que tiene un papel en el sistema. La columna `fuente_identificacion` dice cuál.
3. **Clase o fila propia.** Una fila por clase cuando la clase es numerosa y su función es homogénea (EPS, IPS, cajas de compensación, droguerías). Una organización tiene fila propia si cumple al menos una de tres condiciones:
   - una norma le delega una función pública (por ejemplo, el ICONTEC como acreditador);
   - agrupa a toda una clase (un gremio, una federación);
   - aparece con nombre en una fuente oficial del flujo, como los receptores del giro directo que nombra el Boletín 72 de [Lupa al Giro](../datos/lupa-al-giro.md).
4. **Dos niveles.** Algunas filas son subdivisiones de otra: por ejemplo, los 32 departamentos dentro de «entidades territoriales de salud departamentales». La columna `parte_de` lo dice. Para contar actores o construir una red se usa un solo nivel. Si se mezclan, el mismo actor se cuenta dos veces.
5. **Cuatro grupos**: Estado, Sector privado, Sociedad civil y Academia. Cuando un actor es mixto, `grupo` guarda el principal y `grupo_secundario` el otro. Cuando hay duda, manda la base social del actor (quién lo compone y a quién responde), no su forma jurídica. Una universidad pública, por ejemplo, va en Academia con Estado como grupo secundario, porque esa es la función que cumple en el sistema de salud.
6. **Identificador.** Es el NIT que la entidad declara ante el Estado, tomado de un registro oficial y contrastado contra varios registros independientes. El dígito de verificación se calcula con el algoritmo de la DIAN cuando el registro no lo publica. Si no hay NIT (clases, órganos sin personería jurídica, entidades sin NIT en los registros), el actor recibe un código propio `ASC-###`. Ese código no se reutiliza.
7. **Tamaño.** Una categoría (Macro, Grande, Mediano, Pequeño) que sale de una cifra oficial con umbrales fijos. La cifra puede ser el presupuesto, la población afiliada, los ingresos, el número de organizaciones o el de estudiantes, según el tipo de actor. Sin cifra oficial, el tamaño dice «Sin dato»: ninguna cifra se estima. Los umbrales están en la hoja «Diccionario» del Excel.
8. **Nivel de relación con el sistema** (1, 2 o 3), con el mismo criterio de COLEV, para poder compararlos.

## La clasificación por sectores

| Sector | Qué agrupa |
|---|---|
| A | Núcleo del sistema: rectoría, financiamiento, aseguramiento, prestación, vigilancia, salud pública, información, gobierno territorial, regímenes especiales |
| B | Cadena de suministro y soporte: medicamentos, distribución y dispensación, servicios financieros y tecnológicos, dispositivos médicos |
| C | Representación de intereses: gremios y talento humano |
| D | Conocimiento: universidades, centros de investigación, ciencia |
| E | Sociedad civil y participación: pacientes, veedurías, ONG |
| F | Contrapesos institucionales: poder legislativo, poder judicial, órganos de control |

En la cadena de suministro (sector B), las empresas entran por reglas escritas. Una es un umbral de ingresos en el registro de la Superintendencia de Sociedades. La otra, estar entre los mayores titulares de registros sanitarios ante el INVIMA. El código de actividad económica (CIIU) fija el subsector, salvo en dispositivos médicos, donde lo fija el segmento de producto del INVIMA. La titularidad de registros queda anotada en la fila como evidencia de lo que hace la empresa.

## Cómo se comprueba

- `inventario.py` valida que cada columna tenga valores permitidos.
- `auditoria.py` revisa la coherencia: dígitos de verificación, identificadores repetidos, que cada tamaño cuadre con su cifra y que toda cifra tenga fuente.
- `verificar_nit.py` vuelve a contrastar cada NIT contra los registros oficiales (necesita internet).

## Cómo lo usan las redes

- La [red normada](red-normada.md) toma los actores de nivel base: cada clase es un nodo.
- La [red observada](red-observada.md) usa el inventario para clasificar a los receptores del giro que no están en el [REPS](../datos/reps.md), como los gestores farmacéuticos.
- El inventario y la red son objetos distintos: muchos actores del inventario no tienen vínculos en la red, y eso es esperable.

## Ver también

[Otros actores de la red](../actores/otros-actores-de-la-red.md) · [Registros del inventario](../datos/registros-del-inventario.md) · [Cómo seguir](../como-seguir.md)
