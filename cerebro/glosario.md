---
tipo: glosario
tags: [glosario]
---

# Glosario

## Siglas y entidades

| Sigla | Qué es |
|---|---|
| ADRES | Administradora de los Recursos del Sistema General de Seguridad Social en Salud. Administra el dinero del sistema y ejecuta el giro directo. Ver [ADRES](actores/adres.md) |
| ARI | Índice de Rand ajustado: mide qué tanto coinciden dos particiones, corregido por azar. Ver [métricas](redes/metricas-de-redes.md) |
| BDUA | Base de Datos Única de Afiliados, de la ADRES |
| BRIM | Algoritmo para buscar comunidades en redes bipartitas ([Barber, 2007](referencias/barber-2007.md)) |
| CCF | Cajas de compensación familiar |
| CIIU | Código de actividad económica de una empresa. El inventario lo usa para el subsector de la cadena de suministro |
| COLEV | Proyecto de la Facultad de Medicina de la Universidad de los Andes que hizo el mapa de actores del sector salud. Ver [COLEV 2022](datos/colev-2022.md) |
| CR4 | Participación de las cuatro mayores en un total |
| DANE | Departamento Administrativo Nacional de Estadística |
| DIAN | Dirección de Impuestos y Aduanas Nacionales |
| DIVIPOLA | División Político-Administrativa: los códigos oficiales de departamentos y municipios, que publica el DANE |
| DNP | Departamento Nacional de Planeación |
| EPS | Entidades Promotoras de Salud: las aseguradoras. Ver [EPS](actores/eps.md) |
| ESE | Empresa Social del Estado: un prestador público |
| FONSAET | Fondo de Salvamento y Garantías para el Sector Salud ([Ley 1438 de 2011](normas/ley-1438-de-2011.md)) |
| Fosyga | Fondo de Solidaridad y Garantía, antecesor de la ADRES ([Ley 100 de 1993](normas/ley-100-de-1993.md)) |
| HHI | Índice de Herfindahl-Hirschman, una medida de concentración |
| ICONTEC | Instituto Colombiano de Normas Técnicas y Certificación, entidad acreditadora en salud |
| INVIMA | Instituto Nacional de Vigilancia de Medicamentos y Alimentos. Su registro de titulares dice quién fabrica, importa o distribuye |
| IPS | Instituciones Prestadoras de Servicios de Salud. Ver [prestadores](actores/prestadores.md) |
| LMA | Liquidación Mensual de Afiliados: el proceso con que la ADRES reconoce la UPC del subsidiado |
| MinSalud | Ministerio de Salud y Protección Social. Ver [Ministerio](actores/ministerio-de-salud.md) |
| NIT | Número de identificación tributaria. En el proyecto, el de una empresa tiene nueve dígitos y empieza en 8 o 9 |
| NMI | Información mutua normalizada: mide qué tanto coinciden dos particiones |
| PILA | Planilla Integrada de Liquidación de Aportes ([Decreto 1465 de 2005](normas/decreto-1465-de-2005.md)) |
| PISIS | Plataforma de Intercambio de Información del Ministerio de Salud, por la que las EPS reportan el giro directo ([Resolución 1587 de 2016](normas/resolucion-1587-de-2016.md)) |
| REPS | Registro Especial de Prestadores de Servicios de Salud. Ver [REPS](datos/reps.md) |
| SECOP | Sistema de compras públicas del Estado. El inventario usa su catálogo de entidades para los NIT |
| SGP | Sistema General de Participaciones: recursos de la Nación para los territorios |
| SGSSS | Sistema General de Seguridad Social en Salud. Ver [sistema de salud](sistema/sistema-de-salud.md) |
| SIGEP | Sistema de Información y Gestión del Empleo Público, de la Función Pública. El inventario usa su código de cada entidad del Estado |
| SISPRO | Sistema Integrado de Información de la Protección Social, del Ministerio de Salud. PISIS es una de sus plataformas |
| SOAT | Seguro Obligatorio de Accidentes de Tránsito. Sus aseguradoras transfieren una contribución a la ADRES |
| Supersalud | Superintendencia Nacional de Salud. Ver [Supersalud](actores/supersalud.md) |
| UGPP | Unidad de Gestión Pensional y Parafiscales |
| UPC | Unidad de Pago por Capitación. Ver [UPC](sistema/upc.md) |

## Términos del sistema

| Término | Qué quiere decir |
|---|---|
| Complemento | En el subsidiado, el dinero que la liquidación mensual no aplicó y que se gira después ([Lupa al Giro](datos/lupa-al-giro.md)) |
| Compensación | En el contributivo, el proceso en que la ADRES reconoce la UPC de cada EPS ([Decreto 780 de 2016](normas/decreto-780-de-2016.md)) |
| Contributivo y subsidiado | Los dos regímenes: el de quienes cotizan y el de la población pobre y vulnerable |
| Giro directo | El pago que la ADRES hace directamente a prestadores y proveedores por cuenta de la EPS. Ver [giro directo](sistema/giro-directo.md) |
| Patrimonio adecuado | Indicador financiero de las EPS. Si una EPS no lo cumple, queda obligada al giro directo ([informe de la Supersalud](datos/supersalud-patrimonio-adecuado.md)) |
| Presupuestos máximos | Recursos aparte de la UPC para servicios y tecnologías que la UPC no financia |

## Términos de redes

| Término | Qué quiere decir |
|---|---|
| Nodo y arista | Un actor y un flujo entre dos actores. Ver [modelado de redes](redes/modelado-de-redes.md) |
| Capa | Un tipo de flujo: recursos o información |
| Red bipartita | Red con dos tipos de nodo en la que las aristas solo unen nodos de tipos distintos. Ver [red bipartita](redes/red-bipartita-y-proyecciones.md) |
| Proyección | Red de un solo tipo de nodo que sale de una bipartita |
| Grado y fuerza | Número de vecinos de un nodo y suma de los pesos de sus aristas |
| Modularidad | Medida de qué tan bien se separa una red en grupos |
| Red normada | La red de flujos que establecen las normas. Ver [red normada](metodo/red-normada.md) |
| Red observada | La red del giro directo tal como ocurrió. Ver [red observada](metodo/red-observada.md) |
| Observabilidad | Si un vínculo de la red normada se puede ver con datos públicos |

## Ver también

[Inicio](README.md) · [Índice de normas](normas/indice-de-normas.md)
