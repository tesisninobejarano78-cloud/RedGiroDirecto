# Licencias del repositorio

Cada parte del repositorio lleva la licencia que permiten sus fuentes. **Solo una parte tiene restricción comercial**: lo que se deriva de los anexos que publica la ADRES en *Lupa al Giro*. Todo lo demás se puede usar también con fines comerciales, citando la fuente.

## Qué licencia tiene cada parte

| Parte del repositorio | Licencia | ¿Permite uso comercial? |
|---|---|---|
| `red-observada/salida/` (todas las salidas y figuras), `red-observada/visor-red-observada.html` y `red-observada/red-observada.png` | CC BY-NC-SA 4.0 ([`LICENSE-DATOS-NO-COMERCIAL`](LICENSE-DATOS-NO-COMERCIAL)) | **No**, salvo autorización previa de la ADRES |
| `red-observada/datos/reps/`, la copia del REPS | CC BY-SA 4.0, la del REPS ([`LICENSE-DATOS`](LICENSE-DATOS)) | Sí |
| `inventario-actores/`: la tabla, el Excel, la verificación de NIT y las copias de datos.gov.co de `fuentes/` | CC BY-SA 4.0 ([`LICENSE-DATOS`](LICENSE-DATOS)) | Sí |
| `inventario-actores/fuentes/colev-2022-actores.csv` y `colev-2022-relaciones.csv`, las copias del mapa COLEV | CC0 1.0, la de COLEV | Sí, sin condiciones |
| `red-normada/`: los vínculos, las salidas, el visor y la imagen | CC BY-SA 4.0 ([`LICENSE-DATOS`](LICENSE-DATOS)) | Sí |
| `cerebro/`, los README, este archivo y `CITATION.cff` | CC BY-SA 4.0 ([`LICENSE-DATOS`](LICENSE-DATOS)) | Sí |
| Los programas (`.py`), las plantillas de los visores (`plantilla-visor.html` y `plantilla-visor-observada.html`) e `index.html` | MIT ([`LICENSE`](LICENSE)) | Sí |

## Qué pide cada licencia

- **CC BY-NC-SA 4.0** (Atribución-NoComercial-CompartirIgual 4.0 Internacional): se puede usar y transformar sin fines comerciales, citando la fuente y compartiendo lo derivado con la misma licencia.
- **CC BY-SA 4.0** (Atribución-CompartirIgual 4.0 Internacional): se puede usar y transformar para cualquier fin, citando la fuente y compartiendo lo derivado con la misma licencia.
- **CC0 1.0**: COLEV renunció a sus derechos, así que no hay condiciones. Aun así, conviene citarlo.
- **MIT**: se puede usar, copiar y modificar el código para cualquier fin, conservando el aviso de autoría.

## Por qué la red observada tiene restricción

La red observada se calcula con los anexos mensuales del giro directo que la ADRES publica en *Lupa al Giro*, dentro de su sitio web. La ADRES enlaza al pie de su sitio sus «Términos y Condiciones de Uso Portales Web de la Entidad» (2021). Esos términos:

- prohíben usar, transformar o explotar los contenidos del sitio con fines comerciales o promocionales sin autorización previa de la ADRES;
- piden mencionar que el contenido es de la ADRES.

Por eso todo lo que se deriva de los anexos va con una licencia no comercial y cita a la ADRES como fuente. Quien quiera usarlo con fines comerciales debe pedirle autorización a la ADRES.

La BDUA que usa el inventario también es de la ADRES, pero la ADRES la publica en datos.gov.co con CC BY-SA 4.0, sin restricción comercial. La restricción aplica solo a lo que viene de su sitio web.

## Datos de otras fuentes dentro de la red observada

Algunas salidas de la red observada y su visor traen datos puntuales de cada prestador que vienen de otras fuentes:

- del REPS: su clase, su naturaleza jurídica, si es ESE, su departamento, su municipio y su código de prestador;
- del inventario de actores: su código y su subsector, para los gestores farmacéuticos.

Son datos de hecho. Según las [preguntas frecuentes de Creative Commons](https://creativecommons.org/faq/), los hechos no están protegidos por derechos de autor. Quien usa solo los hechos de una base, sin copiar su estructura, no queda sujeto a las condiciones de la licencia de esa base. Por eso estos datos pueden ir en archivos con licencia no comercial sin incumplir la licencia del REPS.

Quien los necesite sin la restricción comercial los encuentra en `red-observada/datos/reps/`, la copia del REPS, y en el inventario de actores. Los dos tienen CC BY-SA 4.0.

## Licencia de cada fuente

Comprobada en el portal de cada fuente el 26 y el 27 de noviembre de 2026.

| Fuente | Quién la publica | Licencia | Dónde se usa |
|---|---|---|---|
| *Lupa al Giro*: anexos del giro directo y Boletín 72 | ADRES, en su sitio web | Términos de uso de la ADRES: sin uso comercial sin autorización | `red-observada/` |
| Registro Especial de Prestadores y Sedes, REPS (`c36g-9fc2`) | Ministerio de Salud y Protección Social, en datos.gov.co | CC BY-SA 4.0 | `red-observada/` |
| Población BDUA de los regímenes contributivo y subsidiado (`tq4m-hmg2`, `d7a5-cnra`) | ADRES, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| SECOP II, procesos de contratación (`p6dx-8zbt`) | Agencia Nacional de Contratación Pública, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| SECOP II, contratos electrónicos (`jbjy-vk9h`) | Agencia Nacional de Contratación Pública, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| SECOP II, proveedores registrados (`qmzu-gj57`) | Agencia Nacional de Contratación Pública, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| SECOP I y SECOP integrado (`f789-7hwg`, `rpmr-utcd`) | Agencia Nacional de Contratación Pública, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| Entidades sin ánimo de lucro del Régimen Tributario Especial (`8tdc-u2ga`) | Dirección de Impuestos y Aduanas Nacionales, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| 10.000 empresas más grandes del país (`6cat-2gcs`) | Superintendencia de Sociedades, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| Entidades vigiladas por la Superintendencia Financiera (`sr9n-792w`) | Superintendencia Financiera de Colombia, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| Población del Sistema del Subsidio Familiar (`gim6-e69u`) | Superintendencia del Subsidio Familiar, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| Códigos de departamentos de la DIVIPOLA (`vcjz-niiq`) | Departamento Administrativo Nacional de Estadística, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| Registros sanitarios vigentes y vencidos (`ui32-p9f2`) | INVIMA, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| Ejecución presupuestal del Presupuesto General de la Nación (`xjxk-qhsc`) | Ministerio de Hacienda y Crédito Público, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| Directorio de entidades públicas (`kqut-4h4r`) | Ministerio de Tecnologías de la Información y las Comunicaciones, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| Matrícula en educación superior (`5wck-szir`) | Ministerio de Educación Nacional, en datos.gov.co | CC BY-SA 4.0 | `inventario-actores/` |
| Mapa de actores del sector salud COLEV 2022 (DOI 10.57924/ADYMVD) | Universidad de los Andes, en su repositorio de datos | CC0 1.0 | `inventario-actores/` |
| Leyes, decretos y resoluciones | Secretaría del Senado, Función Pública y Ministerio de Salud | Se citan con su artículo; el repositorio no copia sus textos | `red-normada/`, `cerebro/` |

Cada README dice qué fuentes usa su carpeta y cómo citarlas.
