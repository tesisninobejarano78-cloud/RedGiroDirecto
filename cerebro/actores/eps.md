---
tipo: actor
tags: [actor, aseguradores]
aliases: [Entidades Promotoras de Salud]
---

# EPS

Las Entidades Promotoras de Salud afilian a la población y responden por su aseguramiento. Reciben la [UPC](../sistema/upc.md) por cada afiliado y contratan a los [prestadores](prestadores.md). Con el [giro directo](../sistema/giro-directo.md) dejaron de ejecutar buena parte del pago: lo ejecuta la [ADRES](adres.md) por su cuenta, pero la EPS sigue decidiendo a quién y cuánto.

## Qué son

- **Definición** ([Ley 100 de 1993](../normas/ley-100-de-1993.md), art. 177): responden por la afiliación, el registro y el recaudo de las cotizaciones, y deben organizar y garantizar el plan de beneficios.
- **Aseguramiento** ([Ley 1122 de 2007](../normas/ley-1122-de-2007.md), art. 14): administrar el riesgo financiero, gestionar el riesgo en salud, articular los servicios para que el acceso sea efectivo, garantizar la calidad y representar al afiliado ante el prestador. Son funciones indelegables.
- **Autorización**: la [Supersalud](supersalud.md) autoriza su funcionamiento (Ley 100, art. 180).

## Reglas sobre con quién contratan

- Prestan los servicios directamente o los contratan con prestadores (Ley 100, art. 179).
- No pueden contratar con sus propias IPS más del 30 % del gasto en salud (Ley 1122, art. 15).
- Las del contributivo deben incluir IPS públicas en sus redes (Ley 1122, art. 15, parágrafo).
- Las del subsidiado deben contratar como mínimo el 60 % del gasto con Empresas Sociales del Estado del municipio del afiliado, si allí hay capacidad (Ley 1122, art. 16).

## Qué hacen en el giro directo

- **Programan el giro.** Nada se gira sin que la EPS lo reporte. En el subsidiado reporta cada mes, por la plataforma PISIS, cuánto va a cada prestador ([Resolución 1587 de 2016](../normas/resolucion-1587-de-2016.md)). En el contributivo el reporte es semanal ([Resolución 3110 de 2018](../normas/resolucion-3110-de-2018.md)).
- **Responden por la información**: por su exactitud, su calidad y su oportunidad ([Decreto 489 de 2024](../normas/decreto-489-de-2024.md)). Los errores del reporte son su responsabilidad ([Decreto 930 de 2026](../normas/decreto-930-de-2026.md)).
- **Siguen debiendo el resto.** El giro directo no las exonera de pagar lo que no cubre ni cambia sus contratos.
- **Certifican a sus proveedores** sin REPS para que puedan recibir giro directo ([Resolución 4621 de 2016](../normas/resolucion-4621-de-2016.md)).

## Sus vínculos en la red normada

En la [red normada](../metodo/red-normada.md) las EPS son un solo nodo, porque la norma habla del papel y no de cada entidad.

| Capa | Sentido | Vínculos |
|---|---|---|
| Recursos | Les llega | R03 UPC, de la ADRES |
| Recursos | Sale | R06 pago contractual y residual a las IPS |
| Información | Sale | I01 ordenación del giro e I02 afiliación y novedades, a la ADRES · I05 reporte al sistema único, al Ministerio |
| Información | Les llega | I08 vigilancia, de la Supersalud · I11 evaluación del goce efectivo, del Ministerio · I18 acreditación, del ICONTEC · I22 planilla de aportes, de los operadores de la PILA · I24 resultados del recaudo y la compensación, de la ADRES |

## En la red observada

Cada EPS es un nodo. Una EPS puede tener un código distinto en cada régimen. Los programas los unen en una sola entidad (`eps-entidades.csv`, en la [red observada](../metodo/red-observada.md)).

## Ver también

[Giro directo](../sistema/giro-directo.md) · [Supersalud y el patrimonio adecuado](../datos/supersalud-patrimonio-adecuado.md) · [Prestadores](prestadores.md)
