---
tipo: datos
tags: [datos, actores]
---

# Registros oficiales del inventario

El [inventario de actores](../metodo/inventario-de-actores.md) confirma cada actor, su identificador y su tamaño con registros oficiales publicados en datos.gov.co. Todos los conjuntos de abajo se publican con licencia Creative Commons Atribución-CompartirIgual 4.0. Por eso el repositorio publica sus derivados con la misma licencia.

El portal tiene una interfaz de consulta pública: `https://www.datos.gov.co/resource/<id>.json`.

| Conjunto | Publica | Enlace | Para qué se usa |
|---|---|---|---|
| Catálogo de entidades del SECOP II | Agencia Nacional de Contratación Pública | [`p6dx-8zbt`](https://www.datos.gov.co/d/p6dx-8zbt) | NIT de las entidades del Estado |
| SECOP II, contratos electrónicos | Agencia Nacional de Contratación Pública | [`jbjy-vk9h`](https://www.datos.gov.co/d/jbjy-vk9h) | NIT de proveedores privados que contratan con el Estado |
| SECOP II, proveedores registrados | Agencia Nacional de Contratación Pública | [`qmzu-gj57`](https://www.datos.gov.co/d/qmzu-gj57) | NIT de gremios y asociaciones |
| SECOP I y SECOP integrado | Agencia Nacional de Contratación Pública | [`f789-7hwg`](https://www.datos.gov.co/d/f789-7hwg), [`rpmr-utcd`](https://www.datos.gov.co/d/rpmr-utcd) | Contratación de las entidades sin NIT en el SECOP II |
| Entidades sin ánimo de lucro del Régimen Tributario Especial | DIAN | [`8tdc-u2ga`](https://www.datos.gov.co/d/8tdc-u2ga) | NIT de fundaciones, asociaciones y sociedades científicas |
| 10.000 empresas más grandes del país | Superintendencia de Sociedades | [`6cat-2gcs`](https://www.datos.gov.co/d/6cat-2gcs) | NIT e ingresos de empresas del sector salud |
| Entidades vigiladas por la Superintendencia Financiera | Superintendencia Financiera | [`sr9n-792w`](https://www.datos.gov.co/d/sr9n-792w) | NIT de aseguradoras, administradoras de riesgos laborales y fiduciarias |
| Población del Sistema del Subsidio Familiar | Superintendencia del Subsidio Familiar | [`gim6-e69u`](https://www.datos.gov.co/d/gim6-e69u) | Cajas de compensación y población cubierta por cada una |
| Códigos de departamentos de la DIVIPOLA | DANE | [`vcjz-niiq`](https://www.datos.gov.co/d/vcjz-niiq) | Universo de las entidades territoriales de orden departamental |
| Registros sanitarios vigentes | INVIMA | [`ui32-p9f2`](https://www.datos.gov.co/d/ui32-p9f2) | Quién fabrica, importa o distribuye |
| Ejecución presupuestal del Presupuesto General de la Nación | Ministerio de Hacienda | [`xjxk-qhsc`](https://www.datos.gov.co/d/xjxk-qhsc) | Tamaño de los actores del Estado |
| Directorio georreferenciado de entidades públicas (DIVIPOLA/SIGEP) | MinTIC | [`kqut-4h4r`](https://www.datos.gov.co/d/kqut-4h4r) | Universo de entidades del Estado |
| Base de Datos Única de Afiliados (BDUA), contributivo y subsidiado | ADRES | [`tq4m-hmg2`](https://www.datos.gov.co/d/tq4m-hmg2), [`d7a5-cnra`](https://www.datos.gov.co/d/d7a5-cnra) | Afiliados por EPS y departamento |
| Matriculados en programas de salud | Ministerio de Educación | [`5wck-szir`](https://www.datos.gov.co/d/5wck-szir) | Tamaño de las universidades (corte 2021) |
| Registro Especial de Prestadores | Ministerio de Salud | [`c36g-9fc2`](https://www.datos.gov.co/d/c36g-9fc2) | Registro oficial de prestadores ([REPS](reps.md)) |

Además, el inventario parte del [mapa COLEV 2022](colev-2022.md), que tiene licencia CC0.

## Cuidados

- **Datos personales.** El SECOP y el INVIMA incluyen personas naturales. Las copias del repositorio están recortadas:
  - la del SECOP solo trae las filas con forma de NIT de persona jurídica;
  - la del INVIMA, solo los titulares que son empresas nombradas en el inventario.

  Ver [datos personales y ética](../metodo/datos-personales-y-etica.md).
- **Fechas de consulta.** Varios conjuntos se actualizan con frecuencia. El README del inventario dice la fecha de cada copia.

## En el repositorio

Las copias están en `inventario-actores/fuentes/`, con su fuente y fecha en el [README del inventario](../../inventario-actores/README.md).

## Ver también

[Inventario de actores](../metodo/inventario-de-actores.md) · [REPS](reps.md)
