# -*- coding: utf-8 -*-
"""
Resolvedor de NIT contra registros oficiales. Fuente primaria en los tres casos:
el identificador lo declara la propia organización ante el Estado.

  1. ENTIDADES ESTATALES  -> `fuente-secop-entidades-nit.csv` (local, 12.311 registros)
     Catálogo de entidades compradoras del SECOP II, publicado por la Agencia
     Nacional de Contratación Pública en datos.gov.co (dataset p6dx-8zbt).
     Descargado el 2026-08-20.

  2. SIN ÁNIMO DE LUCRO   -> DIAN, "Entidades sin ánimo de lucro del Régimen
     Tributario Especial" (datos.gov.co, dataset 8tdc-u2ga, 340.038 registros).
     Consulta en vivo. Cubre gremios, fundaciones, asociaciones científicas,
     organizaciones de pacientes y universidades privadas.

  3. EMPRESAS            -> SECOP II, contratos electrónicos (dataset jbjy-vk9h),
     campo `documento_proveedor`. Consulta en vivo; lenta. Último recurso.

ADVERTENCIA: estos registros tienen errores de digitación
(NIT con un dígito de más, nombres truncados). El resultado NO se copia sin
mirar el nombre devuelto. Un NIT mal emparejado es un dato inventado.

Uso:
    python resolver_nit.py "ADRES" "SUPERINTENDENCIA NACIONAL DE SALUD"
    python resolver_nit.py --esal "ASOCIACION COLOMBIANA DE HOSPITALES"
    python resolver_nit.py --empresa "AUDIFARMA"
"""
from __future__ import annotations

import csv
import json
import os
import sys
import unicodedata
import urllib.parse
import urllib.request

DIR = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0 Safari/537.36"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").upper()


def _get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def _soda(dataset: str, campos: str, campo_nombre: str, patron: str, limite: int = 40):
    where = "upper(%s) like '%%%s%%'" % (campo_nombre, norm(patron).replace("'", "''"))
    url = "https://www.datos.gov.co/resource/%s.json?%s" % (
        dataset, urllib.parse.urlencode({"$select": campos, "$where": where, "$limit": limite}))
    return _get(url)


# --------------------------------------------------------------------------- #
def estatal(patron: str):
    """Entidades públicas. Catálogo local del SECOP II."""
    fuentes = os.path.join(DIR, "fuentes")
    ruta = os.path.join(fuentes if os.path.isdir(fuentes) else DIR, "fuente-secop-entidades-nit.csv")
    if not os.path.exists(ruta):
        return []
    términos = norm(patron).split()
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return [(r["nit"], r["entidad"], "SECOP II · entidades estatales")
                for r in csv.DictReader(f)
                if all(t in norm(r["entidad"]) for t in términos)]


def esal(patron: str):
    """Entidades sin ánimo de lucro. Registro de la DIAN."""
    filas = _soda("8tdc-u2ga", "nit,raz_n_social,a_o", "raz_n_social", patron)
    vistos, salida = set(), []
    for r in sorted(filas, key=lambda x: -int(x.get("a_o", 0) or 0)):
        k = (r["nit"], r["raz_n_social"])
        if k in vistos:
            continue
        vistos.add(k)
        salida.append((r["nit"], r["raz_n_social"], "DIAN · ESAL rég. tributario especial (%s)" % r.get("a_o")))
    return salida


def empresa(patron: str):
    """Sociedades comerciales. Proveedores del SECOP II. Consulta lenta."""
    filas = _soda("jbjy-vk9h", "documento_proveedor,proveedor_adjudicado", "proveedor_adjudicado", patron, 200)
    vistos, salida = set(), []
    for r in filas:
        k = (r.get("documento_proveedor", ""), r.get("proveedor_adjudicado", ""))
        if k in vistos or not k[0]:
            continue
        vistos.add(k)
        salida.append((k[0], k[1], "SECOP II · proveedores"))
    return salida


BUSCADORES = {"--estatal": estatal, "--esal": esal, "--empresa": empresa}

if __name__ == "__main__":
    args = sys.argv[1:]
    modos = [a for a in args if a.startswith("--")] or ["--estatal"]
    patrones = [a for a in args if not a.startswith("--")]
    for patron in patrones:
        print("== %s" % patron)
        for modo in modos:
            try:
                res = BUSCADORES[modo](patron)
            except Exception as e:
                print("   ! %s: %s" % (modo, e))
                continue
            for nit, nom, fuente in res[:10]:
                print("   %-13s %-42s %s" % (nit, fuente, nom[:72]))
            if not res:
                print("   (sin resultados en %s)" % modo)
