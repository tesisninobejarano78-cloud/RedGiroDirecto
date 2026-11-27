---
tipo: concepto
tags: [concepto, sistema, giro-directo]
---

# Giro directo

Es el mecanismo por el que la [ADRES](../actores/adres.md) les paga directamente a los prestadores y proveedores una parte de la [UPC](upc.md), **por cuenta de la EPS**. Sin giro directo, la EPS recibe la UPC y les paga a los prestadores según sus contratos. Con giro directo, el dinero va de la ADRES al prestador sin pasar por la cuenta de la EPS. Es el tramo del sistema que estudia la [red observada](../metodo/red-observada.md).

## Quién hace qué

- **La EPS no gira ni paga en el giro directo.** Programa a qué prestadores va el dinero y cuánto: la EPS decide, la ADRES ejecuta. Por eso, cuando la red observada dibuja una relación «EPS → prestador», la relación quiere decir «la ADRES le giró a este prestador por cuenta de esta EPS».
- **La [EPS](../actores/eps.md)** responde por la exactitud, la calidad y la oportunidad de la información que reporta para ordenar el giro ([Decreto 489 de 2024](../normas/decreto-489-de-2024.md), art. 2.6.4.3.1.3.4).
- **La ADRES** gira, lleva el registro y la trazabilidad, y fija las condiciones técnicas y operativas.
- **La [Supersalud](../actores/supersalud.md)** publica cada mes qué EPS no cumplen el patrimonio adecuado y le informa a la ADRES cuáles están intervenidas.
- **El [Ministerio de Salud](../actores/ministerio-de-salud.md)**, con la ADRES, garantiza que la información del giro sea pública.

## Cuándo aplica y cuánto

| Régimen | Cuándo | Mínimo | Norma |
|---|---|---|---|
| Contributivo | La EPS no cumple el patrimonio adecuado, está en vigilancia especial, intervención o liquidación, o se acoge voluntariamente | 80 % de la UPC desde abril de 2024; 90 % desde el 31 de julio de 2026 | [Decreto 489 de 2024](../normas/decreto-489-de-2024.md); [Decreto 930 de 2026](../normas/decreto-930-de-2026.md), art. 2 |
| Subsidiado | Hasta julio de 2026, según la modalidad de cada contrato | 100 % de la capitación y al menos el 50 % de lo facturado en las demás modalidades | [Resolución 1587 de 2016](../normas/resolucion-1587-de-2016.md), art. 5 |
| Subsidiado | Desde el mes siguiente al 31 de julio de 2026, todas las EPS | 90 % de la UPC de la Liquidación Mensual de Afiliados | Decreto 930 de 2026, art. 1 |
| Presupuestos máximos | Los dos regímenes | 80 %; 90 % desde el 31 de julio de 2026 | Decreto 489 de 2024; Decreto 930 de 2026, art. 3 |

La base legal vigente es el art. 150 de la [Ley 2294 de 2023](../normas/ley-2294-de-2023.md). El mecanismo ya estaba previsto en la [Ley 1753 de 2015](../normas/ley-1753-de-2015.md), art. 66, lit. d. Los considerandos del Decreto 489 y de la [Resolución 3110 de 2018](../normas/resolucion-3110-de-2018.md) citan como antecedente el art. 10 de la Ley 1608 de 2013, para las EPS bajo medida.

## A quién se le gira

- A los prestadores y proveedores que programe la EPS ([Decreto 489 de 2024](../normas/decreto-489-de-2024.md); [Ley 2294 de 2023](../normas/ley-2294-de-2023.md), art. 150). En el subsidiado, el prestador debe estar habilitado en el [REPS](../datos/reps.md), tener contrato con la EPS y haber registrado una cuenta bancaria ([Resolución 1587 de 2016](../normas/resolucion-1587-de-2016.md)).
- A los proveedores de servicios y tecnologías del plan de beneficios, aunque no estén en el REPS, si la EPS los certifica ([Resolución 4621 de 2016](../normas/resolucion-4621-de-2016.md)). Así entran a la red distribuidores, gestores farmacéuticos y otros proveedores.

## Límites

- El giro directo no exonera a la EPS de pagar el resto ni cambia los contratos entre la EPS y el prestador (Decreto 489, art. 2.6.4.3.1.3.4; Resolución 1587, art. 7).
- No le quita a la EPS el aseguramiento, que es indelegable ([Ley 1122 de 2007](../normas/ley-1122-de-2007.md), art. 14).
- **Por qué se adoptó**: el Decreto 489 y el Decreto 930 citan el Auto 2882 de 2023 de la Corte Constitucional. El Auto pidió fortalecer el giro directo ante fallas en el flujo de recursos y dijo que el giro «no ha tenido avances significativos».

## Dónde se ve

La ADRES publica cada mes lo girado, pareja por pareja, en [Lupa al Giro](../datos/lupa-al-giro.md). Con esos anexos se construye la red observada.

## Ver también

[Flujo de recursos](flujo-de-recursos.md) · [UPC](upc.md) · [Índice de normas](../normas/indice-de-normas.md)
