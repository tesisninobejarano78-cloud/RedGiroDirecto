---
tipo: datos
tags: [datos, prestadores]
aliases: [Registro Especial de Prestadores de Servicios de Salud]
---

# REPS

El Registro Especial de Prestadores y Sedes de Servicios de Salud es la lista oficial de quién está inscrito como prestador. Lo crea la [Resolución 3100 de 2019](../normas/resolucion-3100-de-2019.md): los prestadores se inscriben ante las entidades departamentales y distritales de salud, y el [Ministerio de Salud](../actores/ministerio-de-salud.md) consolida el registro. Lo publica en el portal de datos abiertos.

- Conjunto `c36g-9fc2` de datos.gov.co: <https://www.datos.gov.co/d/c36g-9fc2>
- Licencia: Creative Commons Atribución-CompartirIgual 4.0.

## Qué trae

Una fila por sede de prestador, con: código del prestador, nombre, tipo y número de identificación, naturaleza jurídica, si es Empresa Social del Estado (ESE), municipio y departamento, clase de prestador y fecha de corte. Tiene cuatro clases de prestador:

- Instituciones Prestadoras de Servicios de Salud (IPS);
- profesionales independientes;
- entidades con objeto social diferente a la prestación;
- transporte especial de pacientes.

## Para qué lo usa el proyecto

- En la [red observada](../metodo/red-observada.md), para darle a cada receptor del giro su clase, su naturaleza jurídica y su departamento. Con eso se agrupan los prestadores en las clases de la [red normada](../metodo/red-normada.md).
- En el [inventario de actores](../metodo/inventario-de-actores.md), como registro oficial de los prestadores.

## Cuidados

- **Datos personales.** El REPS incluye a los profesionales independientes con nombre, identificación, dirección, correo y teléfono. El proyecto solo pide las filas identificadas con NIT y las columnas sin datos de contacto. La copia del repositorio deja por fuera, además, 23 filas cuyo número no tiene forma de NIT de empresa ([datos personales y ética](../metodo/datos-personales-y-etica.md)).
- **Una fila por sede, no por NIT.** Un prestador con varias sedes aparece varias veces. El giro directo se identifica por NIT, así que hay que llevar el REPS a una fila por NIT antes de cruzarlo.
- **Registra habilitación, no actividad.** Un prestador inscrito puede no estar operando.
- **La clase depende del corte.** El extracto que usa el repositorio es del 20 de octubre de 2026, con corte del REPS del 12 de marzo de 2026. Otro corte puede clasificar distinto a algún prestador.

## En el repositorio

- `red-observada/datos/reps/` tiene el extracto usado, con su manifiesto.
- `red-observada/clasificar-prestadores.py` lo cruza con los receptores. Con `--reps-nuevo` baja un extracto nuevo y le aplica el mismo filtro.

## Ver también

[Prestadores](../actores/prestadores.md) · [Lupa al Giro](lupa-al-giro.md) · [Registros del inventario](registros-del-inventario.md)
