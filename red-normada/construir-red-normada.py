# -*- coding: utf-8 -*-
"""
Red normada de flujos de recursos e información.

Une los actores del inventario con los vínculos que establecen las normas y genera el visor
interactivo: una sola gráfica en 2D con las dos capas, recursos en línea continua e información en
línea punteada.

Entradas
  ../inventario-actores/actores.csv   inventario de actores; se usa el nivel base (filas sin
                                      `parte_de`) para no contar dos veces
  ../inventario-actores/inventario.py nombres de los sectores y subsectores
  aristas-normadas.csv                vínculos, cada uno con su norma y su observabilidad
  posiciones-normada.csv              posición de los actores de la red, de izquierda a derecha en el
                                      sentido del dinero
  plantilla-visor.html                visor sin dependencias externas

Salidas
  salida/nodos-red-normada.csv · salida/aristas-red-normada.csv
  visor-red-normada.html              el visor con los datos incrustados

Se detiene sin escribir si un vínculo apunta a un actor que no está en el nivel base del inventario,
si un campo controlado trae un valor no permitido, si a un vínculo le falta su norma, si un
identificador se repite o si un actor de la red no tiene posición. No estima nada: cada vínculo
viene de su norma.

Ejecutar:  python construir-red-normada.py
"""
import collections
import csv
import json
import os
import sys

import networkx as nx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DIR, "..", "inventario-actores"))
import inventario as inv  # noqa: E402

SALIDA = os.path.join(DIR, "salida")
VISOR = os.path.join(DIR, "visor-red-normada.html")

CAPAS = ("recursos", "informacion")
OBSERVABILIDAD = ("observable", "parcial", "no observable")
CAMPOS = ("id", "origen", "destino", "capa", "tipo", "descripcion", "norma", "observabilidad", "nota")
NIVELES = {"1": "1 · funciones exclusivamente de salud",
           "2": "2 · trabaja en salud, no exclusivamente",
           "3": "3 · sin misión sanitaria, con influencia"}
Y_INVENTARIO = 760          # donde empieza la cuadrícula de actores sin vínculo normado
COLUMNAS_INVENTARIO = 24


def fallar(mensaje):
    raise SystemExit("ERROR: " + mensaje)


def leer_csv(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# ------------------------------------------------------------ 1. inventario
base = {r["id"]: r for r in inv.leer() if not r["parte_de"].strip()}
sectores, subsectores = inv.SECTORES, inv.SUBSECTORES

# ----------------------------------------------------------- 2. vínculos
aristas = leer_csv(os.path.join(DIR, "aristas-normadas.csv"))
if not aristas or tuple(aristas[0].keys()) != CAMPOS:
    fallar("aristas-normadas.csv debe tener exactamente las columnas: %s" % ", ".join(CAMPOS))
vistos = set()
for a in aristas:
    if a["id"] in vistos:
        fallar("identificador de vínculo repetido: %s" % a["id"])
    vistos.add(a["id"])
    for extremo in ("origen", "destino"):
        if a[extremo] not in base:
            fallar("%s: el %s %s no está en el nivel base del inventario" % (a["id"], extremo, a[extremo]))
    if a["capa"] not in CAPAS or a["observabilidad"] not in OBSERVABILIDAD:
        fallar("%s: capa u observabilidad fuera del vocabulario" % a["id"])
    for campo in ("tipo", "descripcion", "norma"):
        if not a[campo].strip():
            fallar("%s: falta el campo %s" % (a["id"], campo))

# ---------------------------------------------------------- 3. posiciones
posiciones = {r["id"]: (float(r["x"]), float(r["y"]))
              for r in leer_csv(os.path.join(DIR, "posiciones-normada.csv"))}
en_red = {a["origen"] for a in aristas} | {a["destino"] for a in aristas}
sin_posicion = sorted(en_red - set(posiciones))
if sin_posicion:
    fallar("actores de la red sin posición: %s" % ", ".join(sin_posicion))
sobrantes = sorted(set(posiciones) - en_red)
if sobrantes:
    fallar("posiciones de actores que no tienen vínculos: %s" % ", ".join(sobrantes))

# --------------------------------------------------------------- 4. grafo
G = nx.MultiDiGraph()
for i, r in base.items():
    G.add_node(i, **r)
for a in aristas:
    G.add_edge(a["origen"], a["destino"], key=a["id"], **a)


def grados(capa):
    """Vínculos que entran y salen de cada actor en una capa."""
    H = nx.MultiDiGraph()
    H.add_nodes_from(G.nodes)
    H.add_edges_from((u, v, k) for u, v, k, d in G.edges(keys=True, data=True) if d["capa"] == capa)
    return dict(H.in_degree()), dict(H.out_degree())


entra, sale = {}, {}
for capa in CAPAS:
    entra[capa], sale[capa] = grados(capa)


def rol(capa, i):
    e, s = entra[capa][i], sale[capa][i]
    if e == 0 and s == 0:
        return "sin vínculos"
    return "solo emite" if e == 0 else "solo recibe" if s == 0 else "emite y recibe"


def participacion(i):
    r = entra["recursos"][i] + sale["recursos"][i] > 0
    f = entra["informacion"][i] + sale["informacion"][i] > 0
    return "ambas" if r and f else "recursos" if r else "informacion" if f else "ninguna"


# --------------------- 5. cuadrícula para los actores sin vínculo normado
# Una franja por sector, con su nombre encima, para que la cuadrícula se pueda leer.
def orden_inventario(i):
    sub = base[i]["subsector"]
    return (int(sub[1:]) if sub[1:].isdigit() else 99, base[i]["nombre"])


etiquetas_inventario = []
y = Y_INVENTARIO
for sector in sorted({base[i]["sector"] for i in base}):
    del_sector = sorted((i for i in base if i not in en_red and base[i]["sector"] == sector), key=orden_inventario)
    if not del_sector:
        continue
    etiquetas_inventario.append({"texto": "%s · %s (%d)" % (sector, sectores.get(sector, ""), len(del_sector)),
                                 "x": 60, "y": y})
    y += 26
    for k, i in enumerate(del_sector):
        posiciones[i] = (60 + (k % COLUMNAS_INVENTARIO) * 40, y + (k // COLUMNAS_INVENTARIO) * 36)
    y += ((len(del_sector) - 1) // COLUMNAS_INVENTARIO + 1) * 36 + 18

# ------------------------------------------------------------ 6. exportar
os.makedirs(SALIDA, exist_ok=True)
nodos = []
for i in sorted(base):
    r = base[i]
    nodos.append({
        "id": i,
        "nombre": r["nombre"],
        "sigla": r["sigla"] or r["nombre"],
        "grupo": r["grupo"],
        "sector": r["sector"],
        "subsector": r["subsector"],
        "naturaleza": r["naturaleza_juridica"],
        "nivel": r["nivel_relacion"],
        "en_colev": "Sí" if r["en_colev"] == "si" else "No",
        "tamano": r["tamano"],
        "tamano_medida": r["tamano_medida"],
        "funcion": r["funcion"],
        "en_red": i in en_red,
        "x": posiciones[i][0],
        "y": posiciones[i][1],
        "participacion": participacion(i),
        "grado_doc": G.degree(i),
        "rol_recursos": rol("recursos", i),
        "rol_informacion": rol("informacion", i),
    })

campos_nodo = ["id", "nombre", "sigla", "grupo", "sector", "subsector", "naturaleza", "nivel", "en_colev",
               "tamano", "en_red", "participacion", "grado_doc", "rol_recursos", "rol_informacion", "x", "y"]
with open(os.path.join(SALIDA, "nodos-red-normada.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=campos_nodo, extrasaction="ignore", lineterminator="\n")
    w.writeheader()
    w.writerows(nodos)
with open(os.path.join(SALIDA, "aristas-red-normada.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(CAMPOS), lineterminator="\n")
    w.writeheader()
    w.writerows(aristas)

tipos = []
for a in aristas:
    if not any(t["tipo"] == a["tipo"] for t in tipos):
        tipos.append({"tipo": a["tipo"], "capa": a["capa"]})

datos = {
    "meta": {
        "titulo": "Red normada de flujos de recursos e información",
        "version": "versión 2 · 15 de noviembre de 2026",
        "fuente": "Inventario de actores (nivel base) y vínculos que establecen las normas, cada uno con su norma de respaldo.",
        "y_inventario": Y_INVENTARIO,
        "etiquetas_inventario": etiquetas_inventario,
    },
    "catalogos": {"sectores": sectores, "subsectores": subsectores, "niveles": NIVELES, "tipos": tipos},
    "nodos": nodos,
    "aristas": [{k: a[k] for k in CAMPOS} for a in aristas],
}
carga = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
with open(os.path.join(DIR, "plantilla-visor.html"), encoding="utf-8") as f:
    plantilla = f.read()
if "/*__DATOS__*/null" not in plantilla:
    fallar("la plantilla del visor no tiene el marcador de datos")
with open(VISOR, "w", encoding="utf-8", newline="\n") as f:
    f.write(plantilla.replace("/*__DATOS__*/null", carga))

# ------------------------------------------------------------- 7. resumen
print("Red normada: %d actores con vínculos de %d del nivel base; %d vínculos (%s)"
      % (len(en_red), len(base), len(aristas),
         ", ".join("%s %d" % (c, sum(a["capa"] == c for a in aristas)) for c in CAPAS)))
print("Observabilidad:", dict(collections.Counter(a["observabilidad"] for a in aristas)))
print("Participación de los actores de la red:",
      dict(collections.Counter(participacion(i) for i in en_red)))
for capa in CAPAS:
    print("\nRoles en la capa de %s:" % capa)
    por_rol = collections.defaultdict(list)
    for i in sorted(en_red):
        por_rol[rol(capa, i)].append(base[i]["sigla"] or base[i]["nombre"])
    for r_, quienes in sorted(por_rol.items()):
        print("  %-15s %2d  %s" % (r_, len(quienes), ", ".join(quienes)))
print("\nVínculos por actor (todas las capas), los cinco mayores:",
      ", ".join("%s %d" % (base[i]["sigla"], d) for i, d in
                sorted(((i, G.degree(i)) for i in en_red), key=lambda t: -t[1])[:5]))
print("Visor:", os.path.basename(VISOR))
