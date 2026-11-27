# Inventario de actores del sistema de salud colombiano

Esta carpeta tiene una tabla con 252 actores del sistema de salud colombiano: entidades del Estado, aseguradoras, prestadores, industria farmacéutica y de dispositivos, gremios, universidades, organizaciones de la sociedad civil y órganos de control. De cada actor dice quién es, cuál es su identificador oficial, qué tan grande es, qué hace en el sistema y qué norma o registro oficial confirma que existe.

La tabla es la base con la que el proyecto construye la red de flujos de recursos e información entre la ADRES, las EPS y los prestadores de salud: de aquí salen los nodos de la red.

## Qué hay en la carpeta

| Archivo | Qué es |
|---|---|
| `actores.csv` | La tabla del inventario. Es el archivo principal: una fila por actor. |
| `actores-sistema-salud-colombiano.xlsx` | La misma tabla en Excel, con formato, más un diccionario de columnas, el conteo por subsector, la lista de fuentes y el contraste con el mapa COLEV 2022. Es una copia de la tabla al 15 de noviembre de 2026: si se cambia `actores.csv`, el Excel no se actualiza solo. |
| `inventario.py` | Define las columnas y los valores permitidos, y valida que la tabla esté bien escrita. |
| `auditoria.py` | Revisa que lo que dice la tabla sea coherente: dígitos de verificación, identificadores repetidos, que cada tamaño cuadre con su cifra y que toda cifra tenga fuente. |
| `verificar_nit.py` | Contrasta cada NIT contra varios registros oficiales y anota cuántos lo confirman. Necesita internet. |
| `resolver_nit.py` | Busca el NIT de una entidad por su nombre en registros oficiales. Necesita internet. |
| `fuentes/` | Las copias de los registros oficiales que usa el inventario y el resultado de la verificación de los NIT (ver más abajo). |

## Cómo se construyó

1. **Punto de partida.** El mapa de actores del sector salud de COLEV (Universidad de los Andes, 2022), que tiene 84 organizaciones. El inventario recoge 49 de ellas y agrega otras 203.
2. **Regla de entrada.** Un actor entra solo si una norma o un registro oficial confirma que existe y que tiene un papel en el sistema de salud. La columna `fuente_identificacion` dice cuál.
3. **Identificador.** Se usa el NIT que la entidad declara ante el Estado, tomado de un registro oficial (SECOP, DIAN, Supersociedades o REPS). El dígito de verificación se calcula con el algoritmo de la DIAN cuando el registro no lo publica. Cada NIT se contrasta contra varios registros independientes y la columna `identificador_fuentes` dice cuántos lo confirman. 186 actores tienen NIT.
4. **Actores sin NIT.** Los 66 restantes tienen un código propio del inventario (`ASC-###`), que no se reutiliza. Son clases que agrupan muchas organizaciones (por ejemplo, «Sindicatos del sector salud»), órganos y fondos sin personería jurídica, o entidades cuyo NIT no aparece en los registros oficiales consultados. Las notas de cada fila dicen cuál es el caso.
5. **Tamaño.** Cada actor tiene una categoría (Macro, Grande, Mediano o Pequeño) que sale de una cifra oficial, con umbrales fijos que están en el diccionario del Excel. La cifra puede ser el presupuesto, la población afiliada, los ingresos, el número de organizaciones o el de estudiantes, según el tipo de actor. Cuando no se encontró una cifra en las fuentes oficiales consultadas, el tamaño dice «Sin dato»; ninguna cifra se estimó. Hay 90 actores en ese caso.
6. **Dos niveles.** Algunas filas son subdivisiones de otra (los 32 departamentos de la fila «Entidades territoriales de salud departamentales», por ejemplo). La columna `parte_de` dice de qué fila son parte. Hay 166 filas de nivel base y 86 subdivisiones. Al contar actores o construir una red hay que usar un solo nivel; si se usan los dos, el mismo actor se cuenta dos veces.

## Columnas de `actores.csv`

| Columna | Qué guarda |
|---|---|
| `id` | Código del actor en el inventario (`ASC-###`). |
| `nombre`, `sigla` | Nombre oficial y nombre corto. |
| `identificador`, `tipo_identificador` | El NIT con su dígito de verificación, o el código `ASC-###` si no tiene NIT. |
| `identificador_alterno` | Otro código oficial: SIGEP, DIVIPOLA o CIIU. |
| `identificador_fuentes` | Qué registros oficiales confirman el NIT, o por qué no tiene uno. |
| `grupo`, `grupo_secundario` | Estado, Sector privado, Sociedad civil o Academia. El secundario recoge los casos mixtos, como una universidad pública. |
| `tamano`, `tamano_medida`, `tamano_fuente` | La categoría de tamaño, la cifra que la sustenta y de dónde salió. |
| `sector`, `subsector` | Ubicación en la clasificación del inventario (A a F, con sus subsectores). El Excel trae los nombres. |
| `funcion` | Qué hace el actor en el sistema, en una línea. |
| `naturaleza_juridica` | Pública, Privada, Mixta, Sin ánimo de lucro o Internacional. |
| `nivel_relacion` | 1, 2 o 3, con el mismo criterio de COLEV: funciones solo de salud, trabaja en salud entre otras cosas, o influye sin tener misión sanitaria. |
| `agregado` | «si» cuando la fila es una clase que agrupa varias organizaciones. |
| `flujo_recursos`, `flujo_informacion` | Si el actor participa en el flujo de dinero y en el de información: si, no o indirecto. |
| `fuente_identificacion` | La norma o el registro que confirma que el actor existe y es parte del sistema. |
| `parte_de` | El `id` de la fila de la que esta es una subdivisión. |
| `en_colev` | Si el actor estaba en el mapa COLEV 2022. |
| `estado_verificacion` | «verificado» en todas las filas: es la condición para entrar. |
| `notas` | Aclaraciones sobre el actor o sobre su identificador. |
| `fecha_registro` | Fecha en que la fila entró al inventario. |

El diccionario completo, con las reglas de cada columna y la escala de tamaño, está en la hoja «Diccionario» del Excel.

## Cómo usarlo

Se necesita Python 3.12 o más reciente. Los programas no usan librerías adicionales. Se corren desde esta carpeta:

```
python inventario.py              # valida la tabla
python auditoria.py               # revisa la coherencia de los datos
python verificar_nit.py --aplicar # vuelve a contrastar los NIT y actualiza la tabla (necesita internet)
python resolver_nit.py --esal "NOMBRE DE LA ENTIDAD"   # busca un NIT por nombre
```

Para agregar o corregir un actor: se edita `actores.csv` siguiendo el diccionario, con su fuente en `fuente_identificacion`. Después se corren `inventario.py` y `auditoria.py`, y si se agregó un NIT, `verificar_nit.py --aplicar`. La auditoría tiene que terminar sin errores.

## Fuentes

Todas son registros oficiales publicados en datos.gov.co, normas en las páginas oficiales del Estado o el mapa COLEV. Las copias que usan los programas están en `fuentes/`:

| Archivo | Fuente | Conjunto |
|---|---|---|
| `colev-2022-actores.csv`, `colev-2022-relaciones.csv` | COLEV, Universidad de los Andes, mapa de actores del sector salud 2020-2021 | DOI 10.57924/ADYMVD |
| `fuente-secop-entidades-nit.csv` | Agencia Nacional de Contratación Pública, catálogo de entidades del SECOP II | datos.gov.co, p6dx-8zbt, consulta del 20 de agosto de 2026 |
| `fuente-supersociedades-empresas-salud-2024.csv` | Superintendencia de Sociedades, 10.000 empresas más grandes, sector salud, corte 2024 | datos.gov.co, 6cat-2gcs |
| `fuente-invima-titulares.csv` | INVIMA, registros sanitarios vigentes por titular | datos.gov.co, ui32-p9f2, consulta del 23 de agosto de 2026 |
| `fuente-pgn-apropiacion-por-entidad.csv` | Ministerio de Hacienda, ejecución presupuestal del Presupuesto General de la Nación | datos.gov.co, xjxk-qhsc |
| `fuente-sigep-entidades-nacionales.csv` | Directorio de entidades públicas (SIGEP), entidades nacionales | datos.gov.co, kqut-4h4r |
| `fuente-bdua-afiliados-departamento.csv` | ADRES, Base de Datos Única de Afiliados, por departamento | datos.gov.co, tq4m-hmg2 y d7a5-cnra |
| `fuente-snies-matriculados-salud.csv` | Ministerio de Educación, estudiantes matriculados en programas del área de la salud, corte 2021 | datos.gov.co, 5wck-szir |
| `fuente-verificacion-nit.csv` | Resultado de `verificar_nit.py`: qué registros confirman cada NIT | Consulta del 15 de noviembre de 2026 |

Dos de estas copias están recortadas, porque los conjuntos originales incluyen datos de personas naturales:

- `fuente-secop-entidades-nit.csv` solo trae las filas cuyo identificador tiene forma de NIT de persona jurídica. Salen 16 de 12.311.
- `fuente-invima-titulares.csv` solo trae los titulares que son empresas nombradas en el inventario (158 filas). El conjunto completo del INVIMA incluye personas naturales como titulares y no dice qué tipo de titular es cada uno.

Las demás cifras de la tabla (presupuestos, afiliados, ingresos) vienen de los conjuntos citados en la columna `tamano_fuente` de cada fila. Los registros que confirman la existencia o el NIT de un actor y que no tienen copia aquí se citan en las columnas `fuente_identificacion` e `identificador_fuentes`. La lista completa de fuentes está en la hoja «Fuentes» del Excel.

## Licencia

Ningún archivo de esta carpeta tiene restricción comercial.

- **La tabla, el Excel, la verificación de NIT y las copias de datos.gov.co de `fuentes/`**: Creative Commons Atribución-CompartirIgual 4.0 (archivo `LICENSE-DATOS` en la raíz del repositorio). Es la licencia de los conjuntos de datos.gov.co de los que se derivan, comprobada en el portal el 26 y el 27 de noviembre de 2026, y obliga a compartir lo derivado en las mismas condiciones.
- **Las copias del mapa COLEV** (`fuentes/colev-2022-*.csv`): conservan su licencia CC0 1.0, sin condiciones.
- **Los programas**: licencia MIT (archivo `LICENSE` en la raíz del repositorio).

Quien use estos datos debe citar este repositorio y las fuentes originales. La licencia de cada fuente está en [`LICENCIAS.md`](../LICENCIAS.md).
