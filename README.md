# RedGiroDirecto

Repositorio del proyecto de grado de Juanita Bejarano y Federico Niño (Ingeniería Industrial, Universidad de los Andes). El proyecto estudia la estructura de la red de flujos de recursos e información entre la ADRES, las EPS y los prestadores de salud bajo el giro directo en Colombia.

El repositorio reúne los datos, los programas y los resultados del proyecto para que otras personas puedan revisarlos, repetirlos y seguir trabajando sobre ellos.

## Contenido

| Carpeta | Qué tiene |
|---|---|
| [`inventario-actores/`](inventario-actores/) | Inventario de 252 actores del sistema de salud colombiano, con su identificador oficial, su tamaño, su función y la fuente que confirma cada uno. Incluye los programas que lo validan y las copias de los registros oficiales que usa. |
| [`red-normada/`](red-normada/) | La red de flujos de recursos e información que establecen las normas: 25 actores y 49 vínculos, cada uno con su norma y artículo. Incluye el programa que la construye y un visor interactivo que se abre en el navegador. |
| [`red-observada/`](red-observada/) | La red del giro directo tal como ocurrió, construida con los anexos mensuales que publica la ADRES en *Lupa al Giro*: en septiembre de 2026, 25 EPS, 3.810 prestadores y $7,58 billones. Incluye los programas que bajan y leen los anexos, el análisis de la red, la comparación con la red normada, las figuras y un visor interactivo. Todo se vuelve a calcular con un solo comando. |
| [`cerebro/`](cerebro/) | Una bóveda de Obsidian con el conocimiento en que se apoya el proyecto: las normas que sostienen cada vínculo, los actores, los conceptos del sistema de salud y de la teoría de redes, el método, las fuentes de datos y las referencias. Se lee también en GitHub o en cualquier editor. |

Cada carpeta tiene su propio README con lo que contiene, cómo se construyó y cómo se usa.

## Ver las redes

Cada red tiene un visor interactivo: [`red-normada/visor-red-normada.html`](red-normada/visor-red-normada.html) y [`red-observada/visor-red-observada.html`](red-observada/visor-red-observada.html). Hay dos formas de abrirlos:

- **En la web**, sin descargar nada, en la página del proyecto en GitHub Pages: <https://tesisninobejarano78-cloud.github.io/RedGiroDirecto/>. Su portada es [`index.html`](index.html).
- **En el computador**: se descarga el archivo y se abre con doble clic. No necesita internet.

GitHub muestra los archivos `.html` como código, así que desde la lista de archivos del repositorio no se ven como visores.

## Requisitos

Python 3.12 o más reciente; todo se probó con Python 3.14. El inventario no necesita librerías adicionales; la red normada necesita networkx, y la red observada, además, pandas, numpy, scipy, matplotlib y openpyxl. El archivo [`requirements.txt`](requirements.txt) trae las versiones con que se probó. Con ellas, los resultados salen iguales a los publicados:

```
pip install -r requirements.txt
```

Los visores solo necesitan un navegador.

## Orden de las carpetas

La red normada usa el inventario de actores, y la red observada usa las dos: el inventario para clasificar a algunos receptores y la red normada para la comparación. Si se cambia el inventario, conviene volver a construir la red normada y luego la observada.

## Cómo seguir el trabajo

La guía completa está en [`cerebro/como-seguir.md`](cerebro/como-seguir.md). En resumen:

- **Analizar otro mes**: cambiar `PRINCIPAL` y `CONTROL` en `red-observada/configuracion.py` y correr `python correr-todo.py` en esa carpeta. El primer paso baja de la ADRES los anexos que falten.
- **Agregar o corregir un vínculo normado**: editar `red-normada/aristas-normadas.csv` con su norma y artículo, y correr `python construir-red-normada.py`.
- **Agregar o corregir un actor**: editar `inventario-actores/actores.csv` siguiendo su diccionario, y correr `inventario.py` y `auditoria.py`.

Después de cualquier cambio hay que respetar el orden de las carpetas de la sección anterior. El [cerebro](cerebro/README.md) explica las normas, los actores y el método en que se apoya cada producto.

## Cómo citar

Los datos para citar el repositorio están en [`CITATION.cff`](CITATION.cff). Su dirección es <https://github.com/tesisninobejarano78-cloud/RedGiroDirecto>. Quien use los datos debe citar también las fuentes originales que indica cada carpeta.

## Licencias

**Solo una parte tiene restricción comercial**: lo que se deriva de los anexos de la ADRES, es decir:
- `red-observada/salida/`;
- el visor de la red observada (`red-observada/visor-red-observada.html`);
- su imagen (`red-observada/red-observada.png`).

Va con la licencia Creative Commons Atribución-NoComercial-CompartirIgual 4.0 (archivo [`LICENSE-DATOS-NO-COMERCIAL`](LICENSE-DATOS-NO-COMERCIAL)), porque los términos de uso de la ADRES prohíben el uso comercial de sus contenidos sin autorización previa.

**Todo lo demás se puede usar también con fines comerciales**, citando la fuente:
- los datos y los textos, con Creative Commons Atribución-CompartirIgual 4.0 (archivo [`LICENSE-DATOS`](LICENSE-DATOS)); las copias del mapa COLEV conservan su licencia CC0 1.0;
- los programas, las plantillas de los visores e `index.html`, con la licencia MIT (archivo [`LICENSE`](LICENSE)).

El detalle está en [`LICENCIAS.md`](LICENCIAS.md):
- qué licencia tiene cada parte y qué pide cada una;
- por qué los datos del REPS pueden ir en la red observada;
- la licencia de cada fuente, comprobada en su portal.
