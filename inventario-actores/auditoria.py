# -*- coding: utf-8 -*-
"""
Auditoría del inventario de actores. Se corre antes de publicar o entregar el inventario.

`inventario.py` valida que el archivo esté bien formado. Esto es otra cosa: mira
si lo que dice el archivo **es verdad y es coherente**.

Cada comprobación es independiente y declara su severidad:

  ERROR       rompe la validez del dato. No debe quedar ninguno.
  ADVERTENCIA no invalida, pero baja la calidad o esconde una decisión.
  NOTA        estado de cobertura; sirve para saber qué falta, no es un defecto.

Uso:
    python auditoria.py                # informe en consola
    python auditoria.py --md ruta.md   # además, informe en Markdown

Las comprobaciones que necesitan red están separadas: `verificar_nit.py` produce
`fuente-verificacion-nit.csv` y esta auditoría lo lee. Así el informe se puede
regenerar sin conexión.
"""
from __future__ import annotations

import collections
import csv
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventario as inv

DIR = os.path.dirname(os.path.abspath(__file__))

ERROR, ADVERTENCIA, NOTA = "ERROR", "ADVERTENCIA", "NOTA"


class Informe:
    def __init__(self):
        self.items = []

    def add(self, sev, prueba, mensaje):
        self.items.append((sev, prueba, mensaje))

    def por_severidad(self, sev):
        return [x for x in self.items if x[0] == sev]


def _norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").upper()
    return re.sub(r"[^A-Z0-9 ]", " ", re.sub(r"\s+", " ", s)).strip()


# Solo se descartan articulos, conjunciones y sufijos societarios. La palabra que
# dice QUE TIPO de organizacion es —superintendencia, asociacion, instituto— se
# conserva a proposito: es justo lo que distingue a un vigilante de su vigilado.
VACIAS = {"DE", "DEL", "LA", "EL", "LOS", "LAS", "Y", "SA", "SAS", "LTDA", "LIMITADA",
          "NACIONAL", "COLOMBIA", "COLOMBIANA", "COLOMBIANO", "GENERAL", "SALUD",
          "SISTEMA", "SERVICIOS"}


def _tokens(s):
    return {t for t in _norm(s).split() if t not in VACIAS and len(t) > 2}


# --------------------------------------------------------------------------- #
# 1. Estructura e integridad interna
# --------------------------------------------------------------------------- #
def estructura(filas, inf):
    for e in inv.validar(verbose=False):
        inf.add(ERROR, "esquema", e)

    # NIT que dos actores distintos comparten: uno de los dos no es suyo.
    por_nit = collections.defaultdict(list)
    for r in filas:
        if r["tipo_identificador"] == "NIT":
            por_nit[r["identificador"].split("-")[0]].append(r)
    for nit, v in por_nit.items():
        if len(v) > 1:
            inf.add(ERROR, "identificador compartido",
                    "%s lo llevan %s" % (nit, " y ".join("%s (%s)" % (x["id"], x["nombre"][:34]) for x in v)))

    # Digito de verificacion: detecta transcripciones erroneas.
    for r in filas:
        if r["tipo_identificador"] != "NIT" or "-" not in r["identificador"]:
            continue
        base, dv = r["identificador"].split("-")
        if dv != inv.digito_verificacion(base):
            inf.add(ERROR, "dígito de verificación",
                    "%s %s: el dígito no cuadra (esperado %s)" % (r["id"], r["identificador"],
                                                                  inv.digito_verificacion(base)))

    # parte_de: referencia, anidamiento, coherencia con la madre.
    idx = {r["id"]: r for r in filas}
    for r in filas:
        p = (r.get("parte_de") or "").strip()
        if not p:
            continue
        m = idx.get(p)
        if not m:
            inf.add(ERROR, "parte_de", "%s apunta a %s, que no existe" % (r["id"], p))
            continue
        if (m.get("parte_de") or "").strip():
            inf.add(ERROR, "parte_de", "%s cuelga de %s, que a su vez cuelga de otra fila" % (r["id"], p))
        if m["agregado"] != "si":
            inf.add(ADVERTENCIA, "parte_de", "%s cuelga de %s, que no es una clase agregada" % (r["id"], p))
        if m["subsector"] != r["subsector"]:
            inf.add(ADVERTENCIA, "parte_de", "%s (%s) cuelga de %s (%s): subsectores distintos"
                    % (r["id"], r["subsector"], p, m["subsector"]))

    # Nombres que podrian ser el mismo actor escrito dos veces.
    vistos = [(r, _tokens(r["nombre"])) for r in filas]
    for i, (ra, ta) in enumerate(vistos):
        for rb, tb in vistos[i + 1:]:
            # Con una sola palabra distintiva el parecido no significa nada:
            # «Universidad de Antioquia» y «Universidad Icesi» comparten «universidad».
            if len(ta) < 2 or len(tb) < 2:
                continue
            # Jaccard, no solapamiento sobre el menor: que un nombre este contenido
            # en otro mas largo no lo hace un duplicado.
            # Una clase agregada y una organizacion nunca son el mismo actor, por
            # parecidos que sean sus nombres: «Cajas de Compensacion Familiar» y el
            # gremio que las agrupa son cosas distintas.
            if ra["agregado"] != rb["agregado"]:
                continue
            if len(ta & tb) / len(ta | tb) > 0.8:
                inf.add(ADVERTENCIA, "posible duplicado",
                        "%s «%s» y %s «%s»" % (ra["id"], ra["nombre"][:38], rb["id"], rb["nombre"][:38]))


# --------------------------------------------------------------------------- #
# 2. Coherencia entre la categoría de tamaño y la cifra que la sustenta
# --------------------------------------------------------------------------- #
UMBRALES = {
    "cop": ([10, 1, 0.1], "billones de pesos"),
    "pob": ([10_000_000, 1_000_000, 100_000], "personas"),
    "org": ([10_000, 1_000, 100], "organizaciones"),
    "edu": ([5_000, 1_000, 200], "estudiantes matriculados"),
}
ESCALA = ["Macro", "Grande", "Mediano", "Pequeño"]


def _magnitud(texto):
    t = texto or ""
    # La metrica (7) se reconoce por su unidad, no por la posicion de la cifra:
    # en la clase agregada el primer numero es el de instituciones, no el de
    # estudiantes, y es este ultimo el que fija la categoria.
    m = re.search(r"([\d.]+) estudiantes matriculados", t)
    if m:
        return "edu", int(m.group(1).replace(".", ""))
    m = re.search(r"\$([\d.]*\d(?:,\d+)?) billones", t)
    if m:
        return "cop", float(m.group(1).replace(".", "").replace(",", "."))
    m = re.search(r"([\d.]+)\s+(?:afiliados|personas)", t)
    if m:
        return "pob", int(m.group(1).replace(".", ""))
    m = re.match(r"\s*([\d.]+)\s", t)
    if m:
        return "org", int(m.group(1).replace(".", ""))
    return None, None


def _categoria(tipo, v):
    cortes = UMBRALES[tipo][0]
    for i, c in enumerate(cortes):
        if v >= c:
            return ESCALA[i]
    return ESCALA[3]


def tamanos(filas, inf):
    sin_cifra = 0
    for r in filas:
        if r["tamano"] == "Sin dato":
            if r["tamano_medida"] != inv.SIN_CIFRA:
                inf.add(ADVERTENCIA, "tamaño",
                        "%s no tiene dato de tamaño pero su medida dice «%s»" % (r["id"], r["tamano_medida"][:52]))
            sin_cifra += 1
            continue
        tipo, v = _magnitud(r["tamano_medida"])
        if v is None:
            inf.add(ADVERTENCIA, "tamaño",
                    "%s tiene categoría %s pero de su medida no se puede extraer una cifra: «%s»"
                    % (r["id"], r["tamano"], r["tamano_medida"][:52]))
            continue
        esperado = _categoria(tipo, v)
        if esperado != r["tamano"]:
            inf.add(ERROR, "tamaño",
                    "%s %s: declara %s y la cifra (%s %s) da %s"
                    % (r["id"], r["nombre"][:30], r["tamano"], v, UMBRALES[tipo][1], esperado))
        if not (r["tamano_fuente"] or "").strip():
            inf.add(ERROR, "trazabilidad", "%s tiene cifra de tamaño sin fuente" % r["id"])
    inf.add(NOTA, "cobertura", "%d de %d filas sin dato de tamaño" % (sin_cifra, len(filas)))


# --------------------------------------------------------------------------- #
# 3. Trazabilidad y coherencia semántica
# --------------------------------------------------------------------------- #
def contenido(filas, inf):
    for r in filas:
        if not (r["fuente_identificacion"] or "").strip():
            inf.add(ERROR, "trazabilidad", "%s no dice de dónde salió que este actor existe" % r["id"])
        if len(r["funcion"]) < 40:
            inf.add(ADVERTENCIA, "contenido", "%s tiene una función demasiado escueta" % r["id"])
        if r["flujo_recursos"] == "no" and r["flujo_informacion"] == "no":
            inf.add(ADVERTENCIA, "pertinencia",
                    "%s no participa en ninguna de las dos capas: revisar si pertenece al inventario" % r["id"])
        if r["agregado"] == "si" and r["tipo_identificador"] == "NIT":
            inf.add(ADVERTENCIA, "agregación",
                    "%s es una clase agregada pero lleva NIT propio" % r["id"])
        if r["grupo"] == "Estado" and r["naturaleza_juridica"] == "Privada":
            inf.add(ADVERTENCIA, "clasificación", "%s es grupo Estado con naturaleza Privada" % r["id"])


# --------------------------------------------------------------------------- #
# 4. Confirmación cruzada de identificadores (lee el archivo de verificación)
# --------------------------------------------------------------------------- #
def identificadores(filas, inf):
    ruta = os.path.join(inv.FUENTES, "fuente-verificacion-nit.csv")
    if not os.path.exists(ruta):
        inf.add(ADVERTENCIA, "verificación cruzada",
                "no existe fuente-verificacion-nit.csv: correr antes `python verificar_nit.py`")
        return
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        v = {r["id"]: r for r in csv.DictReader(f)}
    con_nit = [r for r in filas if r["tipo_identificador"] == "NIT"]
    c = collections.Counter()
    for r in con_nit:
        x = v.get(r["id"])
        if not x:
            inf.add(ADVERTENCIA, "verificación cruzada",
                    "%s tiene NIT pero no está en el archivo de verificación: reejecutar verificar_nit.py" % r["id"])
            continue
        n = int(x["n_fuentes"])
        c[n] += 1
        if n == 0:
            inf.add(ADVERTENCIA, "verificación cruzada",
                    "%s %s: ningún registro confirma el par (NIT, nombre)" % (r["id"], r["nombre"][:40]))
        if x["discrepancias"]:
            # Que un registro publique el NIT con otro nombre puede ser un error o
            # puede ser un alias real (una razon social anterior, una sigla). Si la
            # fila ya explica el alias, esta documentado y deja de ser un defecto.
            alias = x["discrepancias"].split(":")[-1].strip().split()[0] if x["discrepancias"] else ""
            documentado = alias and alias.upper() in (r["notas"] or "").upper()
            inf.add(NOTA if documentado else ADVERTENCIA, "verificación cruzada",
                    "%s: %s publica ese NIT con otro nombre -> %s%s"
                    % (r["id"], "un registro", x["discrepancias"][:70],
                       " (alias documentado en la fila)" if documentado else ""))
    dos_o_mas = sum(n for k, n in c.items() if k >= 2)
    inf.add(NOTA, "verificación cruzada",
            "%d de %d identificadores confirmados por dos o más registros independientes"
            % (dos_o_mas, len(con_nit)))


# --------------------------------------------------------------------------- #
# 5. Cobertura contra fuentes externas
# --------------------------------------------------------------------------- #
# Integrantes del SGSSS segun el articulo 155 de la Ley 100 de 1993. Cada uno se
# busca por palabras clave en el inventario: es la comprobacion de que el mapa
# cubre lo que la norma dice que es el sistema.
LEY100_155 = [
    ("Ministerio de Salud", ["MINISTERIO", "SALUD"]),
    ("Ministerio de Trabajo", ["MINISTERIO", "TRABAJO"]),
    ("Consejo Nacional de Seguridad Social en Salud", ["CONSEJO", "SEGURIDAD"]),
    ("Superintendencia Nacional de Salud", ["SUPERINTENDENCIA", "SALUD"]),
    ("Entidades Promotoras de Salud", ["PROMOTORAS"]),
    ("Direcciones territoriales de salud", ["TERRITORIAL", "SALUD"]),
    ("Fondo de Solidaridad y Garantia (hoy ADRES)", ["ADMINISTRADORA", "RECURSOS"]),
    ("Instituciones Prestadoras de Servicios de Salud", ["PRESTADORAS"]),
    ("Aportantes, trabajadores y pensionados", ["APORTANTES"]),
    ("Beneficiarios y afiliados", ["AFILIADOS"]),
    ("Comites de Participacion Comunitaria", ["PARTICIPACION COMUNITARIA"]),
]


def cobertura(filas, inf):
    texto = " || ".join(_norm(r["nombre"]) for r in filas)
    faltan = []
    for etiqueta, claves in LEY100_155:
        if not all(_norm(k) in texto for k in claves):
            faltan.append(etiqueta)
    if faltan:
        for f in faltan:
            inf.add(ERROR, "cobertura Ley 100 art. 155",
                    "integrante del SGSSS que la norma nombra y el inventario no tiene: %s" % f)
    else:
        inf.add(NOTA, "cobertura Ley 100 art. 155",
                "los %d integrantes que nombra el artículo están representados" % len(LEY100_155))

    # Contraste con el unico mapa de actores previo del pais.
    ruta = os.path.join(inv.FUENTES, "colev-2022-actores.csv")
    if os.path.exists(ruta):
        n = sum(1 for r in filas if r["en_colev"] == "si")
        inf.add(NOTA, "contraste COLEV",
                "%d filas del inventario corresponden a actores de la base COLEV 2022" % n)

    # Subsectores con poca poblacion: no es un defecto, es una pista de donde seguir.
    c = collections.Counter(r["subsector"] for r in filas)
    flacos = [k for k, v in c.items() if v <= 3]
    if flacos:
        inf.add(NOTA, "cobertura",
                "subsectores con tres actores o menos: " + ", ".join(sorted(flacos)))

    # Equilibrio entre las dos capas de la red, que es el objeto del proyecto.
    rec = sum(1 for r in filas if r["flujo_recursos"] in ("si", "indirecto"))
    info = sum(1 for r in filas if r["flujo_informacion"] in ("si", "indirecto"))
    inf.add(NOTA, "capas de la red",
            "capa de recursos: %d actores · capa de información: %d actores" % (rec, info))


# --------------------------------------------------------------------------- #
def correr():
    filas = inv.leer()
    inf = Informe()
    estructura(filas, inf)
    tamanos(filas, inf)
    contenido(filas, inf)
    identificadores(filas, inf)
    cobertura(filas, inf)
    return filas, inf


def imprimir(filas, inf):
    base = [r for r in filas if not (r.get("parte_de") or "").strip()]
    print("=" * 78)
    print("AUDITORÍA DEL INVENTARIO DE ACTORES")
    print("=" * 78)
    print("Filas: %d   Nodos de nivel base: %d   Subdivisiones: %d"
          % (len(filas), len(base), len(filas) - len(base)))
    for sev in (ERROR, ADVERTENCIA, NOTA):
        items = inf.por_severidad(sev)
        print("\n%s (%d)" % (sev, len(items)))
        print("-" * 78)
        if not items:
            print("   ninguno")
        for _, prueba, msg in items:
            print("   [%s] %s" % (prueba, msg))
    print("\n" + "=" * 78)
    print("RESULTADO: %d errores, %d advertencias"
          % (len(inf.por_severidad(ERROR)), len(inf.por_severidad(ADVERTENCIA))))
    print("=" * 78)


def markdown(filas, inf, ruta):
    base = [r for r in filas if not (r.get("parte_de") or "").strip()]
    L = ["| Severidad | Prueba | Hallazgo |", "|---|---|---|"]
    for sev in (ERROR, ADVERTENCIA, NOTA):
        for _, prueba, msg in inf.por_severidad(sev):
            L.append("| %s | %s | %s |" % (sev, prueba, msg.replace("|", "/")))
    cab = ("# Auditoría del inventario de actores\n\n"
           "**%d filas · %d nodos de nivel base · %d subdivisiones.** "
           "%d errores y %d advertencias.\n\n"
           % (len(filas), len(base), len(filas) - len(base),
              len(inf.por_severidad(ERROR)), len(inf.por_severidad(ADVERTENCIA))))
    with open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write(cab + "\n".join(L) + "\n")
    print("\nInforme escrito: %s" % ruta)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    filas, inf = correr()
    imprimir(filas, inf)
    if "--md" in sys.argv:
        markdown(filas, inf, sys.argv[sys.argv.index("--md") + 1])
    sys.exit(1 if inf.por_severidad(ERROR) else 0)
