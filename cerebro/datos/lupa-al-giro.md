---
tipo: datos
tags: [datos, adres, giro-directo]
---

# Lupa al Giro (ADRES)

Es el sitio donde la [ADRES](../actores/adres.md) publica cada mes lo que giró y a quién. De sus anexos sale la [red observada](../metodo/red-observada.md). El acceso es libre, sin registro ni solicitud. La publicación cumple el deber de publicidad del [giro directo](../sistema/giro-directo.md):

- [Ley 2294 de 2023](../normas/ley-2294-de-2023.md), art. 150, parágrafo 2;
- [Decreto 489 de 2024](../normas/decreto-489-de-2024.md), art. 2.6.4.3.1.3.7, parágrafo;
- [Resolución 1587 de 2016](../normas/resolucion-1587-de-2016.md), art. 8.

**Cómo llegar.** Desde la página de inicio de la ADRES, <https://www.adres.gov.co>, *Lupa al Giro* está en el menú, en las secciones «EPS» e «IPS y proveedores». Tiene un módulo para el régimen contributivo y otro para el subsidiado. Este cerebro solo enlaza a la página de inicio porque así lo piden los términos de uso de la ADRES (ver «Condiciones de uso», abajo).

## Las tres series de anexos

| Serie | Qué trae |
|---|---|
| Contributivo: giro directo | Un archivo comprimido por mes. Trae la hoja de giros a prestadores, los valores reconocidos por EPS y las licencias |
| Subsidiado: giro por prestador | La hoja del proceso mensual y la del complemento: el dinero que la liquidación no aplicó y se gira después |
| Subsidiado: giro por EPS | La certificación del giro a cada EPS: UPC, descuentos, giro directo, giro neto y observaciones |

La hoja de giros a prestadores tiene la misma estructura en los dos regímenes:

| Columna | Qué es | Papel en la red |
|---|---|---|
| `NIT`, `Razón Social` | El receptor del giro | Nodo de destino |
| `Código EPS`, `Nombre EPS` | La EPS por cuya cuenta se gira | Nodo de origen |
| `Valor Ordenado $` | Lo que la EPS ordenó girar | Peso ordenado |
| `Valor Giro IPS $` | Lo que la ADRES giró | Peso girado |
| `Observación` | Anotación del proceso | Atributo |
| `Fecha Proceso Giro Directo`, `Fecha Giro` | Fechas del ciclo (solo en el contributivo) | Atributo |

## Cosas que conviene saber antes de usarlos

- **El formato cambia a lo largo de la serie.** Cambian los nombres de los archivos, el encabezado aparece en filas distintas y en la certificación aparecen y desaparecen columnas de descuento. En el subsidiado no hay «valor ordenado» hasta junio de 2024. El programa de lectura revisa cada hoja y se detiene si encuentra un formato que no conoce.
- **Códigos de EPS mal publicados.** En algunos meses el anexo trae mal el código de una EPS. Solo se corrige cuando el nombre de la misma fila corresponde sin duda a otro código, y cada corrección queda registrada en `correcciones-codigo-eps.csv`.
- **Una EPS, varios códigos.** Una EPS puede tener un código por régimen. Los programas los unen en una entidad (`eps-entidades.csv`).
- **Datos de personas.** Algunos receptores son personas naturales identificadas con su número de documento. Por eso los anexos crudos **no se redistribuyen** ([datos personales y ética](../metodo/datos-personales-y-etica.md)).
- **Condiciones de uso.** La ADRES enlaza al pie de su sitio los «Términos y Condiciones de Uso Portales Web de la Entidad» (2021). Prohíben usar o transformar sus contenidos con fines comerciales sin su autorización previa y piden mencionar que el contenido es de la ADRES. Por eso lo que el repositorio deriva de los anexos se publica con una licencia no comercial ([datos personales y ética](../metodo/datos-personales-y-etica.md)). Los términos piden también que los enlaces al sitio lleven solo a su página de inicio. Las direcciones exactas de cada anexo están únicamente en el programa de descarga y en el manifiesto, que las necesitan para bajar los archivos y comprobar que son los mismos.
- **La ADRES puede reprocesar un mes.** El programa de descarga guarda la huella de cada archivo en un manifiesto y avisa si un archivo cambió.

## Los boletines

Además de los anexos, la ADRES publica cada mes un boletín en PDF con las cifras agregadas del giro. La red observada usa el **Boletín 72** (junio de 2026) como control: los programas reproducen sus cifras a partir de los anexos.

- Boletín 72 (junio de 2026): está enlazado desde *Lupa al Giro*, con el nombre de archivo `Boletin_lupa_al_giro_UPC_Junio_2026.pdf`.

## En el repositorio

- `red-observada/descargar-anexos-giro.py` baja los anexos de enero de 2024 en adelante.
- `red-observada/salida/manifiesto-descargas.csv` guarda la dirección, la fecha, el tamaño y la huella SHA-256 de cada archivo.
- `red-observada/ingerir-anexos-giro.py` los lee sin modificarlos.

Ver el [README de la red observada](../../red-observada/README.md).

## Ver también

[Red observada](../metodo/red-observada.md) · [REPS](reps.md) · [Giro directo](../sistema/giro-directo.md)
