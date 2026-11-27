# -*- coding: utf-8 -*-
"""
Configuración común de los programas de la red observada: carpetas y meses de análisis.

Carpetas por defecto (relativas a esta carpeta):
  datos/anexos/   anexos de Lupa al Giro que baja descargar-anexos-giro.py
  datos/reps/     extractos del REPS que usa clasificar-prestadores.py
  salida/         todo lo que calculan los programas
  ../inventario-actores/   inventario de actores (actores.csv)
  ../red-normada/          red normada (aristas-normadas.csv y salida/nodos-red-normada.csv)
  ./              plantilla y visor de la red observada

Si alguna carpeta está en otro lugar, se puede crear aquí un archivo rutas-locales.json solo con
las que cambian. Por ejemplo:
  {"anexos": "D:/datos/lupa-al-giro"}
Las claves posibles son anexos, reps, salida, inventario, red_normada y visor. Las rutas relativas
se cuentan desde esta carpeta.

Meses: PRINCIPAL es el mes que se analiza y CONTROL, los meses con que se comprueba que el
resultado no depende del mes elegido. Para analizar un mes nuevo basta con cambiarlos aquí y volver
a correr correr-todo.py.

Compresión: GZIP es la forma en que los programas escriben los .csv.gz, sin la fecha en su
cabecera. Así, volver a correr los programas con los mismos datos da exactamente los mismos archivos.
"""
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))

PRINCIPAL = "2026-09"
CONTROL = ["2026-06", "2026-07", "2026-08"]

GZIP = {"method": "gzip", "mtime": 0}

_CARPETAS = {
    "anexos": os.path.join("datos", "anexos"),
    "reps": os.path.join("datos", "reps"),
    "salida": "salida",
    "inventario": os.path.join("..", "inventario-actores"),
    "red_normada": os.path.join("..", "red-normada"),
    "visor": ".",
}
_LOCALES = os.path.join(AQUI, "rutas-locales.json")
if os.path.exists(_LOCALES):
    with open(_LOCALES, encoding="utf-8") as _f:
        _cambios = json.load(_f)
    _desconocidas = set(_cambios) - set(_CARPETAS)
    if _desconocidas:
        raise SystemExit("ERROR: rutas-locales.json trae claves desconocidas: %s" % ", ".join(sorted(_desconocidas)))
    _CARPETAS.update(_cambios)


def _ruta(clave):
    return os.path.normpath(os.path.join(AQUI, _CARPETAS[clave]))


ANEXOS = _ruta("anexos")
REPS = _ruta("reps")
SALIDA = _ruta("salida")
INVENTARIO = os.path.join(_ruta("inventario"), "actores.csv")
ARISTAS_NORMADAS = os.path.join(_ruta("red_normada"), "aristas-normadas.csv")
NODOS_NORMADA = os.path.join(_ruta("red_normada"), "salida", "nodos-red-normada.csv")
PLANTILLA_VISOR = os.path.join(_ruta("visor"), "plantilla-visor-observada.html")
VISOR = os.path.join(_ruta("visor"), "visor-red-observada.html")

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre"]


def nombre_mes(corte):
    """'2026-09' -> 'septiembre de 2026'."""
    anio, mes = corte.split("-")
    return "%s de %s" % (MESES[int(mes) - 1], anio)


def mes_anterior(corte):
    """'2026-09' -> '2026-08'."""
    anio, mes = (int(x) for x in corte.split("-"))
    return "%04d-%02d" % ((anio, mes - 1) if mes > 1 else (anio - 1, 12))
