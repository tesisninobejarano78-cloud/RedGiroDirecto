---
tipo: metodo
tags: [metodo, etica, datos-personales]
---

# Datos personales y ética

El proyecto trabaja solo con información pública, publicada por la entidad responsable y agregada por entidad. No usa microdatos, datos personales, datos clínicos ni información reservada. Quien siga el trabajo debe mantener estas reglas.

## El problema

Algunas fuentes públicas sí traen datos de personas, aunque estén publicadas abiertamente:

- **Los anexos del giro directo** ([Lupa al Giro](../datos/lupa-al-giro.md)): algunos receptores son personas naturales identificadas con su número de documento.
- **El [REPS](../datos/reps.md)**: incluye a los profesionales independientes con nombre, identificación, dirección, correo y teléfono.
- **El catálogo del SECOP y el registro de titulares del INVIMA** ([registros del inventario](../datos/registros-del-inventario.md)): incluyen personas naturales.

## Las reglas

1. **Una identificación cuenta como NIT de empresa solo si tiene nueve dígitos y empieza en 8 o 9.** Hay cédulas de ocho dígitos que empiezan en 8, y esta regla no las deja pasar.
2. **Las demás identificaciones se juntan en un nodo colectivo, `PN-AGREGADO`, al momento de leer el archivo.** Su número y su nombre no quedan en ninguna salida, y los programas no los imprimen.
3. **Las columnas personales se descartan al leer.** Del REPS se piden solo las filas identificadas con NIT y las columnas sin datos de contacto. La copia del repositorio deja por fuera, además, 23 filas que no cumplen la regla 1.
4. **Las copias de registros se recortan.** La del SECOP solo trae filas con forma de NIT de persona jurídica. La del INVIMA, solo los titulares que son empresas nombradas en el inventario.
5. **Los archivos originales no se redistribuyen.** Los anexos crudos de la ADRES no están en el repositorio. Se publica el programa que los baja de la fuente oficial y el manifiesto con la huella de cada archivo, para comprobar que son los mismos. Así cada persona reconstruye el insumo desde su origen. La carpeta donde el programa los guarda, `red-observada/datos/anexos/`, está excluida de git para que no se suban por error. Quien los baje los tiene en su computador con esos datos y no debe publicarlos.
6. **Cada corte nuevo se vuelve a revisar.** Si en un mes nuevo aparece una persona natural, la regla 2 la agrega. La revisión está dentro de los programas de lectura.

Con estas reglas, ningún archivo del repositorio, ni en sus versiones anteriores, trae el número, el nombre o los datos de contacto de una persona natural. Se comprobó sobre todas las tablas y todo el historial. Las personas naturales que aparecen en los anexos originales solo existen en el repositorio como el nodo `PN-AGREGADO`, sin número, nombre ni ubicación.

## Cómo hablar de los resultados

Los resultados nombran entidades (aseguradoras y prestadores) y las ordenan por su papel en el flujo de recursos. Una medida de concentración o de dependencia describe una posición en la red. No dice que una entidad hizo algo indebido. Por eso:

- ningún resultado se comparte suelto: va con la explicación de cómo se calculó y de sus límites;
- se evita el vocabulario que sugiera falta o infracción cuando el dato solo muestra una diferencia;
- una anomalía señala dónde mirar, no una irregularidad.

## Licencias de los datos

Los conjuntos de datos.gov.co que usa el proyecto se publican con Creative Commons Atribución-CompartirIgual 4.0. Se pueden usar y transformar citando la fuente y compartiendo lo derivado con la misma licencia. El mapa COLEV es CC0.

Los anexos de *Lupa al Giro* son distintos. Los términos de uso del sitio de la ADRES prohíben usar o transformar sus contenidos con fines comerciales sin su autorización previa, y piden mencionar que el contenido es de la ADRES ([Lupa al Giro](../datos/lupa-al-giro.md)).

Las licencias del repositorio están en tres archivos:
- [`LICENSE`](../../LICENSE): los programas, con MIT;
- [`LICENSE-DATOS-NO-COMERCIAL`](../../LICENSE-DATOS-NO-COMERCIAL): lo que se deriva de los anexos de la ADRES, con CC BY-NC-SA 4.0;
- [`LICENSE-DATOS`](../../LICENSE-DATOS): los demás datos y los textos, con CC BY-SA 4.0.

Qué archivo lleva cada licencia, y la licencia de cada fuente, están en [`LICENCIAS.md`](../../LICENCIAS.md).

## Ver también

[Criterios de inclusión](criterios-de-inclusion.md) · [Red observada](red-observada.md) · [Cómo seguir](../como-seguir.md)
