---
tipo: actor
tags: [actor, prestadores]
aliases: [IPS, Instituciones Prestadoras de Servicios de Salud]
---

# Prestadores (IPS)

Las Instituciones Prestadoras de Servicios de Salud (IPS) atienden a los afiliados. Son el destino final del [giro directo](../sistema/giro-directo.md): reciben dinero de la [ADRES](adres.md) por cuenta de cada [EPS](eps.md) con la que tienen contrato, más lo que la EPS les pague por fuera del giro.

## Qué son

- **Definición** ([Ley 100 de 1993](../normas/ley-100-de-1993.md), art. 185): prestan los servicios en su nivel de atención, con autonomía administrativa, técnica y financiera. Deben dar información oportuna, suficiente y veraz a los usuarios.
- **Quién cuenta como prestador**: el que está inscrito y habilitado según la [Resolución 3100 de 2019](../normas/resolucion-3100-de-2019.md). La inscripción se hace ante las entidades departamentales y distritales de salud, y el Ministerio la consolida en el [REPS](../datos/reps.md).
- **Empresas Sociales del Estado (ESE)**: los prestadores públicos. La [Ley 1122 de 2007](../normas/ley-1122-de-2007.md), art. 16, obliga a las EPS del subsidiado a contratar con ellas una parte mínima del gasto.
- **Acreditación**: voluntaria, la otorga el ICONTEC ([Resolución 2082 de 2014](../normas/resolucion-2082-de-2014.md); [Resolución 488 de 2026](../normas/resolucion-488-de-2026.md)).

## Otros receptores del giro directo

No todo el que recibe giro directo es una IPS. La [Resolución 4621 de 2016](../normas/resolucion-4621-de-2016.md) permite girar a proveedores de servicios y tecnologías que la EPS certifica, aunque no estén en el REPS. Por eso la red tiene también droguerías y gestores farmacéuticos, importadores y distribuidores, industria y proveedores sin inscripción ([otros actores de la red](otros-actores-de-la-red.md)).

## Sus vínculos en la red normada

En la [red normada](../metodo/red-normada.md) las IPS son un solo nodo.

| Capa | Sentido | Vínculos |
|---|---|---|
| Recursos | Les llega | R04 giro directo de la UPC y R05 de presupuestos máximos, de la ADRES · R06 pago contractual y residual, de las EPS · R20 rescate de ESE, del FONSAET |
| Información | Sale | I06 reporte al sistema único, al Ministerio · I07 información a los usuarios · I13 e I14 inscripción y habilitación, ante las entidades territoriales |
| Información | Les llega | I09 vigilancia, de la Supersalud · I12 evaluación del goce efectivo, del Ministerio · I17 acreditación, del ICONTEC |

## En la red observada

Cada prestador es un nodo, identificado por su NIT. Con el REPS se le asigna una clase (ESE, IPS pública, privada o mixta) y un departamento. Los receptores que no están en el REPS se cruzan con el [inventario de actores](../metodo/inventario-de-actores.md). Las identificaciones que no tienen forma de NIT de empresa se juntan en un solo nodo, sin número ni nombre ([datos personales y ética](../metodo/datos-personales-y-etica.md)).

## Ver también

[REPS](../datos/reps.md) · [Giro directo](../sistema/giro-directo.md) · [Red bipartita y proyecciones](../redes/red-bipartita-y-proyecciones.md)
