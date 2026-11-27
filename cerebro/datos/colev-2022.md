---
tipo: datos
tags: [datos, actores, antecedente]
---

# Mapa de actores COLEV (2022)

Es el punto de partida del [inventario de actores](../metodo/inventario-de-actores.md): un mapa de las organizaciones relacionadas con el sector salud que participaron en la respuesta a la pandemia de COVID-19 en Colombia (2020-2021). Lo hizo el proyecto COLEV de la Facultad de Medicina de la Universidad de los Andes.

- Universidad de los Andes, DataHub. DOI: [10.57924/ADYMVD](https://doi.org/10.57924/ADYMVD)
- Licencia: CC0 (dominio público).

## Qué trae

- 84 organizaciones con atributos cualitativos y 107 relaciones entre ellas.
- Por actor: tipo de organización; si es público, privado o mixto; si es gubernamental; su nivel de relación con el sistema; etiquetas de función y una descripción de su misión.
- El mapa advierte que no da cuenta de la calidad ni de la densidad de las relaciones que dibuja.

## Qué tomó de él el inventario

- **El nivel de relación con el sistema**, para que los dos se puedan comparar:
  - nivel 1: funciones solo de salud;
  - nivel 2: trabaja en salud entre otras cosas;
  - nivel 3: influye en el sector sin tener misión sanitaria.
- **Un control de cobertura**: si un actor está en COLEV y no en el inventario, falta. El Excel del inventario trae la hoja «Contraste COLEV» con ese cruce, y la columna `en_colev` de `actores.csv` dice si cada actor estaba en el mapa.

## Lo que no tiene

- No trae identificador oficial (NIT) ni tamaño de los actores. Son las dos cosas que agrega el inventario.
- Es anterior al [Decreto 489 de 2024](../normas/decreto-489-de-2024.md), y algunas EPS que lista ya no operan.

## En el repositorio

`inventario-actores/fuentes/colev-2022-actores.csv` y `colev-2022-relaciones.csv` son la copia que usa el inventario ([README del inventario](../../inventario-actores/README.md)).

## Ver también

[Inventario de actores](../metodo/inventario-de-actores.md) · [Registros del inventario](registros-del-inventario.md)
