---
tipo: actor
tags: [actor, estado]
aliases: [Administradora de los Recursos del Sistema General de Seguridad Social en Salud]
---

# ADRES

La Administradora de los Recursos del Sistema General de Seguridad Social en Salud administra el dinero del sistema: lo recibe de sus fuentes, reconoce la [UPC](../sistema/upc.md) a las EPS y ejecuta el [giro directo](../sistema/giro-directo.md) a prestadores y proveedores. Es el centro de la capa de recursos de la red normada. También publica los datos con que se construye la red observada ([Lupa al Giro](../datos/lupa-al-giro.md)).

## Qué es

- La creó el art. 66 de la [Ley 1753 de 2015](../normas/ley-1753-de-2015.md). Es una entidad de naturaleza especial del orden nacional, asimilada a una empresa industrial y comercial del Estado y adscrita al [Ministerio de Salud](ministerio-de-salud.md).
- Reemplazó al Fondo de Solidaridad y Garantía (Fosyga) de la [Ley 100 de 1993](../normas/ley-100-de-1993.md).
- Maneja los recursos con unidad de caja, salvo los de las entidades territoriales.
- **Límite legal**: «En ningún caso la Entidad asumirá las funciones asignadas a las Entidades Promotoras de Salud». La ADRES paga, pero no asegura.

## Qué hace en el giro directo

- **Ejecuta, no decide.** Gira a cada prestador lo que la [EPS](eps.md) programa. Los porcentajes mínimos los fijan el Ministerio de Salud, el Ministerio de Hacienda y el DNP ([Ley 2294 de 2023](../normas/ley-2294-de-2023.md), art. 150).
- Fija las condiciones técnicas y operativas del giro, lleva su registro y su trazabilidad ([Decreto 489 de 2024](../normas/decreto-489-de-2024.md)).
- En el subsidiado no verifica los valores a girar, salvo que el total cuadre con lo que le corresponde a la EPS ([Decreto 930 de 2026](../normas/decreto-930-de-2026.md)).
- Puede detener el giro de presupuestos máximos cuando la [Supersalud](supersalud.md) le comunica la intervención de una EPS para liquidarla.

## Sus vínculos en la red normada

Estos son sus vínculos en la [red normada](../metodo/red-normada.md), con el código de cada uno.

| Capa | Sentido | Vínculos |
|---|---|---|
| Recursos | Le llegan | R01 cotizaciones de los aportantes · R12 Ministerio de Hacienda · R13 y R14 entidades territoriales · R15 Coljuegos · R16 SOAT · R17 cajas de compensación · R18 UGPP · R28 Ministerio de Salud · R29 operadores de juegos |
| Recursos | Salen | R03 UPC a las EPS · R04 y R05 giro directo a las IPS · R07 a R11 y R25 a R27 giro directo a proveedores, gestores farmacéuticos y cajas · R19 FONSAET |
| Información | Le llega | I01 ordenación del giro y I02 afiliación, de las EPS · I03 lista de incumplimiento, de la Supersalud · I10 reglas del giro, del Ministerio · I21 planilla de aportes, de los operadores de la PILA |
| Información | Sale | I04 trazabilidad y publicidad del giro, al Ministerio · I24 resultados del recaudo y la compensación, a las EPS |

## En la red observada

No es un nodo: es quien ejecuta todos los pagos. Cada relación de la red observada es un giro de la ADRES a un prestador por cuenta de una EPS ([red observada](../metodo/red-observada.md)).

## Ver también

[Giro directo](../sistema/giro-directo.md) · [Flujo de recursos](../sistema/flujo-de-recursos.md) · [Otros actores de la red](otros-actores-de-la-red.md)
