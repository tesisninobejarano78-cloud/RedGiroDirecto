---
tipo: actor
tags: [actor, indice]
---

# Otros actores de la red normada

La [red normada](../metodo/red-normada.md) tiene 25 actores. Cinco tienen página propia: la [ADRES](adres.md), las [EPS](eps.md), los [prestadores (IPS)](prestadores.md), la [Supersalud](supersalud.md) y el [Ministerio de Salud](ministerio-de-salud.md). Esta página reúne a los otros veinte. Cada uno sale del [inventario de actores](../metodo/inventario-de-actores.md): el código es su `id` en [`actores.csv`](../../inventario-actores/actores.csv), donde está la norma o el registro que confirma que existe.

Varias filas son clases que agrupan muchas organizaciones (por ejemplo, todas las aseguradoras del SOAT). La red normada habla de papeles, no de entidades una por una.

## Fuentes de dinero hacia la ADRES

| Código | Actor | Qué hace en la red | Vínculos |
|---|---|---|---|
| ASC-251 | Aportantes y cotizantes | Empleadores, independientes y pensionados que cotizan; su dinero llega a cuentas de la ADRES y su planilla va al operador de la PILA | R01, I20 |
| ASC-003 | Ministerio de Hacienda y Crédito Público | Aportes de la Nación al sistema | R12 |
| ASC-008 | Unidad de Gestión Pensional y Parafiscales (UGPP) | Fiscaliza los aportes a la seguridad social y gira a la ADRES los recursos de su gestión | R18 |
| ASC-044 | Coljuegos | Administra los juegos de suerte y azar novedosos y localizados, y gira a la ADRES la parte que financia el subsidiado | R15 |
| ASC-045 | Operadores de juegos de suerte y azar y loterías territoriales | Explotan loterías, chance y rifas; giran a la ADRES la parte del subsidiado y a los territorios el resto | R29, R23, R24 |
| ASC-047 | Cajas de compensación familiar | Aportan recursos al sistema y, como prestadoras, reciben giro directo | R17, R11 |
| ASC-062 | Aseguradoras del SOAT | Transfieren a la ADRES una contribución del 50 % de la prima | R16 |

## Los territorios

| Código | Actor | Qué hace en la red | Vínculos |
|---|---|---|---|
| ASC-027 | Entidades territoriales de salud departamentales | Reciben rentas de juegos, giran recursos propios a la ADRES, inscriben prestadores y alimentan el REPS | R13, R23, I13, I15 |
| ASC-028 | Entidades territoriales de salud distritales y municipales | Igual que las departamentales, en su municipio o distrito | R14, R24, I14, I16 |

## Receptores del giro directo que no son IPS

Pueden recibir giro directo por la [Resolución 4621 de 2016](../normas/resolucion-4621-de-2016.md) y el art. 150 de la [Ley 2294 de 2023](../normas/ley-2294-de-2023.md).

| Código | Actor | Qué hace en la red | Vínculos |
|---|---|---|---|
| ASC-071 | Droguerías, gestores farmacéuticos y canal de dispensación | Entregan el medicamento al paciente | R07 |
| ASC-067 | Audifarma S.A. | Gestor farmacéutico y dispensador de medicamentos para EPS | R08 |
| ASC-068 | Disfarma G.C. S.A.S. | Distribuidor y dispensador de medicamentos para el canal institucional | R09 |
| ASC-069 | Helpharma S.A.S. | Operador farmacéutico de medicamentos de alto costo | R10 |
| ASC-070 | Importadores y distribuidores mayoristas | Importan o distribuyen al por mayor medicamentos y tecnologías | R25 |
| ASC-065 | Industria farmacéutica y de dispositivos médicos | Fabrica en el país medicamentos, dispositivos y biológicos | R26 |
| ASC-253 | Proveedores sin inscripción en el REPS | Proveen servicios y tecnologías del plan de beneficios sin ser prestadores inscritos | R27 |

Los tres gestores farmacéuticos tienen fila propia en el inventario. Sus fuentes son el Boletín 72 de [Lupa al Giro](../datos/lupa-al-giro.md) y el listado de empresas de la Superintendencia de Sociedades.

## Fondos, información y acreditación

| Código | Actor | Qué hace en la red | Vínculos |
|---|---|---|---|
| ASC-164 | Fondo de Salvamento y Garantías para el Sector Salud (FONSAET) | Paga obligaciones de Empresas Sociales del Estado intervenidas o liquidadas; lo administra la ADRES ([Ley 1438 de 2011](../normas/ley-1438-de-2011.md)) | R19, R20 |
| ASC-212 | Operadores de información de la PILA | Reciben y validan la planilla de aportes, y distribuyen su información a la ADRES, las EPS y el Ministerio. Por ellos pasa el dato, no el dinero ([Decreto 1465 de 2005](../normas/decreto-1465-de-2005.md)) | I20, I21, I22, I23 |
| ASC-177 | Instituto Colombiano de Normas Técnicas y Certificación (ICONTEC) | Entidad acreditadora en salud de IPS y EPS ([Resolución 488 de 2026](../normas/resolucion-488-de-2026.md)) | I17, I18 |
| ASC-252 | Afiliados y beneficiarios | Reciben de los prestadores información sobre los servicios ([Ley 100 de 1993](../normas/ley-100-de-1993.md), art. 185) | I07 |

## Ver también

[Índice de normas](../normas/indice-de-normas.md) · [Flujo de recursos](../sistema/flujo-de-recursos.md) · [Inventario de actores](../metodo/inventario-de-actores.md)
