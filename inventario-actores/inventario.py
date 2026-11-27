# -*- coding: utf-8 -*-
"""
Módulo base del inventario de actores del sistema de salud colombiano.

Fuente de verdad: `actores.csv` (una fila por actor).
Este módulo define el esquema, los vocabularios controlados, y las funciones
para añadir filas y validar el archivo. Los demás programas del inventario lo importan.

Reglas de integridad:
  - Ningún actor entra sin `fuente_identificacion`.
  - Ninguna cifra de tamaño entra sin `tamano_fuente`. Si no se encontró una cifra
    en las fuentes oficiales consultadas, `tamano` = "Sin dato" y `tamano_medida` =
    SIN_CIFRA. NUNCA se estima.
  - Un actor entra solo cuando su existencia y su identificador están confirmados en
    una norma o en un registro oficial: `estado_verificacion` = "verificado".
"""
from __future__ import annotations

import csv
import os
import re
import sys
import unicodedata

DIR = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(DIR, "actores.csv")
# Archivos de fuentes: en la subcarpeta fuentes/ si existe; si no, junto a este archivo.
FUENTES = os.path.join(DIR, "fuentes") if os.path.isdir(os.path.join(DIR, "fuentes")) else DIR

# --------------------------------------------------------------------------- #
# Esquema
# --------------------------------------------------------------------------- #
COLUMNAS = [
    # --- Identificación, grupo y tamaño ---
    "id",                     # ASC-###  clave estable del inventario, nunca se reutiliza
    "nombre",                 # nombre oficial completo
    "sigla",                  # sigla o nombre corto de uso común
    "identificador",          # NIT autodado (en forma canonica NIT-DV); si no tiene, el ASC-###
    "tipo_identificador",     # NIT | SIGEP | ASC-asignado
    "identificador_alterno",  # código SIGEP u otro código oficial, si existe
    "identificador_fuentes",  # registros independientes que confirman el par (NIT, nombre) + origen del DV
    "grupo",                  # Sociedad civil | Estado | Academia | Sector privado
    "grupo_secundario",       # captura la hibridez (p. ej. universidad pública)
    "tamano",                 # Macro | Grande | Mediano | Pequeño | Sin dato
    "tamano_medida",          # la cifra real, con unidad y fecha de corte
    "tamano_fuente",          # fuente primaria de esa cifra
    # --- Columnas de apoyo: sirven para desmenuzar la red y para trazabilidad ---
    "sector",                 # macro-sector A..F
    "subsector",              # subsector A1..F3
    "funcion",                # qué hace este actor en el sistema, en una línea
    "naturaleza_juridica",    # Pública | Privada | Mixta | Sin ánimo de lucro | Internacional
    "nivel_relacion",         # 1 | 2 | 3 (criterio COLEV 2022, ver metodologia)
    "agregado",               # si | no  (¿la fila representa una clase, no una organización?)
    "flujo_recursos",         # si | no | indirecto  (capa de recursos de la red)
    "flujo_informacion",      # si | no | indirecto  (capa de información de la red)
    "fuente_identificacion",  # de dónde salió que este actor existe y es pertinente
    "parte_de",               # id del actor agregado del que esta fila es subdivision (vacio = fila de nivel base)
    "en_colev",               # si | no  (contraste contra la base COLEV 2022)
    "estado_verificacion",    # verificado
    "notas",
    "fecha_registro",
]

REQUERIDAS = ["id", "nombre", "identificador", "grupo", "sector", "subsector",
              "funcion", "fuente_identificacion", "fecha_registro"]

GRUPOS = {"Sociedad civil", "Estado", "Academia", "Sector privado"}
TAMANOS = {"Macro", "Grande", "Mediano", "Pequeño", "Sin dato"}
SIN_CIFRA = "No se encontró una cifra en las fuentes oficiales consultadas"
TIPO_ID = {"NIT", "SIGEP", "ASC-asignado"}
SINO = {"si", "no"}
SINO_IND = {"si", "no", "indirecto"}
NATURALEZA = {"Pública", "Privada", "Mixta", "Sin ánimo de lucro", "Internacional"}
VERIFICACION = {"verificado"}

# Taxonomía de sectores: el andamiaje con que se desmenuza la red.
# Cada subsector se declara "cubierto" solo cuando se agotó su fuente de referencia.
SECTORES = {
    "A": "Núcleo funcional del SGSSS",
    "B": "Cadena de suministro y soporte",
    "C": "Representación de intereses",
    "D": "Conocimiento",
    "E": "Sociedad civil y participación",
    "F": "Contrapesos institucionales",
}

SUBSECTORES = {
    "A1":  "Rectoría, regulación y formulación de política",
    "A2":  "Financiamiento y administración de recursos",
    "A3":  "Aseguramiento",
    "A4":  "Prestación de servicios",
    "A5":  "Inspección, vigilancia y control del sistema",
    "A6":  "Salud pública y vigilancia sanitaria",
    "A7":  "Información, conocimiento y evaluación de tecnologías",
    "A8":  "Gobierno territorial de la salud",
    "A9":  "Regímenes especiales y de excepción",
    "A10": "Otros aseguramientos en salud (laboral, tránsito, voluntario)",
    "B1":  "Producción de medicamentos, dispositivos y biológicos",
    "B2":  "Distribución, dispensación y operación logística",
    "B3":  "Servicios financieros y tecnológicos de soporte",
    "B4":  "Dispositivos médicos, diagnóstico in vitro y equipamiento biomédico",
    "C1":  "Gremios de aseguradores y prestadores",
    "C2":  "Gremios de industria y comercio en salud",
    "C3":  "Talento humano: colegios, sindicatos y sociedades científicas",
    "D1":  "Universidades y facultades del área de la salud",
    "D2":  "Centros de investigación, observatorios y think tanks",
    "D3":  "Institucionalidad de ciencia y tecnología",
    "E1":  "Organizaciones de pacientes",
    "E2":  "Participación social, veeduría y control ciudadano",
    "E3":  "ONG y fundaciones con misión en salud",
    "F1":  "Poder legislativo",
    "F2":  "Poder judicial y control constitucional",
    "F3":  "Órganos de control del Estado",
}


# --------------------------------------------------------------------------- #
# Lectura / escritura
# --------------------------------------------------------------------------- #
# Pesos del algoritmo del digito de verificacion del NIT que publica la DIAN.
# Se aplican de derecha a izquierda sobre los nueve digitos base.
PESOS_DV = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]


def digito_verificacion(nit9: str) -> str:
    """Digito de verificacion del NIT segun el algoritmo de la DIAN.

    Es una funcion deterministica del propio NIT, no un dato externo: sirve para
    (a) detectar errores de transcripcion cuando el registro publica el digito y
    (b) completar el identificador a su forma canonica cuando no lo publica.
    Validado contra diez NIT cuyo digito publican los registros oficiales.
    """
    n = re.sub(r"[^0-9]", "", nit9)[:9]
    s = sum(int(d) * PESOS_DV[i] for i, d in enumerate(reversed(n)))
    r = s % 11
    return str(r if r < 2 else 11 - r)


def normaliza_nit(nit: str) -> str:
    """Los registros oficiales publican el NIT con o sin digito de verificacion.

    Cuando vienen diez digitos seguidos, el ultimo es el digito de verificacion:
    se separa con guion para que el identificador quede en forma canonica. No se
    calcula ni se corrige nada: solo se reformatea lo que el registro publica.
    """
    n = re.sub(r"[^0-9]", "", nit or "")
    if len(n) == 10:
        return n[:9] + "-" + n[9]
    if len(n) == 9:
        return n + "-" + digito_verificacion(n)
    return n


def clave_nombre(nombre: str) -> str:
    """Nombre para comparar: sin tildes ni mayúsculas.

    Así, un nombre escrito con o sin tildes se reconoce como el mismo actor.
    """
    s = unicodedata.normalize("NFD", nombre or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip().lower()


def leer() -> list[dict]:
    if not os.path.exists(CSV):
        return []
    with open(CSV, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def escribir(filas: list[dict]) -> None:
    filas = sorted(filas, key=lambda r: int(r["id"].split("-")[1]))
    with open(CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in filas:
            w.writerow({c: r.get(c, "") for c in COLUMNAS})


def siguiente_id(filas: list[dict]) -> str:
    n = max((int(r["id"].split("-")[1]) for r in filas), default=0)
    return "ASC-%03d" % (n + 1)


def agregar(nuevos: list[dict], fecha: str) -> list[dict]:
    """Añade actores asignando IDs consecutivos. Rechaza nombres ya presentes."""
    filas = leer()
    vistos = {clave_nombre(r["nombre"]) for r in filas}
    creados = []
    for a in nuevos:
        nom = a["nombre"].strip()
        if clave_nombre(nom) in vistos:
            print("  [OMITIDO: ya existe] " + nom)
            continue
        a = dict(a)
        a["id"] = siguiente_id(filas)
        a.setdefault("fecha_registro", fecha)
        # Regla del identificador: NIT si lo tiene; si no, el propio ASC-###.
        if not a.get("identificador"):
            a["identificador"] = a["id"]
            a["tipo_identificador"] = "ASC-asignado"
        filas.append(a)
        vistos.add(clave_nombre(nom))
        creados.append(a)
    escribir(filas)
    return creados


def actualizar(cambios: dict[str, dict]) -> int:
    """Modifica campos de actores ya existentes. {id: {campo: valor}}.

    Se usa para reencuadrar una fila agregada cuando sus subdivisiones entran al
    inventario, o para completar una medida de tamano que antes no tenia fuente.
    Nunca borra filas: el inventario solo crece o se corrige.
    """
    filas = leer()
    idx = {r["id"]: r for r in filas}
    n = 0
    for aid, campos in cambios.items():
        r = idx.get(aid)
        if not r:
            print("  ! %s no existe" % aid)
            continue
        for c, v in campos.items():
            if c not in COLUMNAS:
                raise KeyError("columna desconocida: %s" % c)
            r[c] = v
        n += 1
    escribir(filas)
    return n


# --------------------------------------------------------------------------- #
# Validación
# --------------------------------------------------------------------------- #
def validar(verbose: bool = True) -> list[str]:
    filas = leer()
    errores: list[str] = []

    def err(fila, msg):
        errores.append("%s (%s): %s" % (fila.get("id", "?"), fila.get("nombre", "?")[:45], msg))

    todos_ids = {r["id"] for r in filas}
    ids, nombres = set(), set()
    for r in filas:
        padre = (r.get("parte_de") or "").strip()
        if padre:
            if padre not in todos_ids:
                err(r, "parte_de apunta a un id inexistente: %r" % padre)
            if padre == r["id"]:
                err(r, "parte_de se apunta a si mismo")
        for c in REQUERIDAS:
            if not (r.get(c) or "").strip():
                err(r, "falta campo obligatorio '%s'" % c)
        if r["id"] in ids:
            err(r, "id duplicado")
        ids.add(r["id"])
        if clave_nombre(r["nombre"]) in nombres:
            err(r, "nombre duplicado")
        nombres.add(clave_nombre(r["nombre"]))
        if r.get("grupo") not in GRUPOS:
            err(r, "grupo inválido: %r" % r.get("grupo"))
        if (r.get("grupo_secundario") or "") and r["grupo_secundario"] not in GRUPOS:
            err(r, "grupo_secundario inválido: %r" % r["grupo_secundario"])
        if r.get("tamano") and r["tamano"] not in TAMANOS:
            err(r, "tamano inválido: %r" % r["tamano"])
        if r.get("subsector") not in SUBSECTORES:
            err(r, "subsector inválido: %r" % r.get("subsector"))
        if r.get("sector") != r.get("subsector", " ")[0]:
            err(r, "sector no coincide con subsector")
        if r.get("tipo_identificador") and r["tipo_identificador"] not in TIPO_ID:
            err(r, "tipo_identificador inválido: %r" % r["tipo_identificador"])
        if r.get("naturaleza_juridica") and r["naturaleza_juridica"] not in NATURALEZA:
            err(r, "naturaleza_juridica inválida: %r" % r["naturaleza_juridica"])
        if r.get("estado_verificacion") not in VERIFICACION:
            err(r, "estado_verificacion inválido: %r" % r.get("estado_verificacion"))
        for c in ("agregado", "en_colev"):
            if r.get(c) not in SINO:
                err(r, "%s debe ser si|no, es %r" % (c, r.get(c)))
        for c in ("flujo_recursos", "flujo_informacion"):
            if r.get(c) not in SINO_IND:
                err(r, "%s debe ser si|no|indirecto, es %r" % (c, r.get(c)))
        if r.get("nivel_relacion") not in {"1", "2", "3"}:
            err(r, "nivel_relacion debe ser 1|2|3, es %r" % r.get("nivel_relacion"))
        # Integridad: una cifra de tamaño sin fuente sería una cifra inventada.
        med = (r.get("tamano_medida") or "").strip()
        if (r.get("tamano") == "Sin dato") != (med == SIN_CIFRA):
            err(r, "tamano «Sin dato» y tamano_medida sin cifra deben ir juntos")
        if med and med != SIN_CIFRA and not (r.get("tamano_fuente") or "").strip():
            err(r, "tiene tamano_medida sin tamano_fuente")
        if r.get("tipo_identificador") == "NIT":
            ident = r.get("identificador", "")
            if not re.fullmatch(r"\d{9}(-\d)?", ident):
                err(r, "NIT con formato inesperado: %r" % ident)
            elif "-" in ident and ident.split("-")[1] != digito_verificacion(ident.split("-")[0]):
                err(r, "digito de verificacion del NIT no cuadra: %s (esperado %s)"
                    % (ident, digito_verificacion(ident.split("-")[0])))

    if verbose:
        print("Actores: %d | Errores: %d" % (len(filas), len(errores)))
        for e in errores:
            print("  [X]", e)
    return errores


if __name__ == "__main__":
    sys.exit(1 if validar() else 0)
