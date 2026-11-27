# -*- coding: utf-8 -*-
"""
Verificación cruzada de identificadores contra registros independientes.

Un NIT apoyado en una sola fuente puede tener errores de transcripción. Este
módulo contrasta cada NIT del inventario contra varios registros oficiales
distintos y deja constancia de cuántos lo confirman.

Qué se contrasta, y por qué son fuentes independientes entre sí:

  1. SECOP II — entidades compradoras (archivo local, ANCP)       -> entidades públicas
  2. Supersociedades — empresas del sector salud (archivo local y
     serie completa de las 10.000 empresas más grandes, en vivo)  -> sociedades comerciales
  3. REPS — prestadores habilitados (MinSalud, en vivo)           -> prestadores
  4. DIAN — ESAL del Régimen Tributario Especial (en vivo)        -> sin ánimo de lucro
  5. SECOP II — proveedores (ANCP, en vivo)                       -> quien contrata con el Estado

Un registro **confirma** un identificador solo si publica ese NIT **y** el nombre
que devuelve concuerda con el del inventario. Un NIT que aparece con otro nombre
no cuenta como confirmación: cuenta como alerta.

Además se comprueba el **dígito de verificación** con el algoritmo de la DIAN.
Cuando el registro publica el dígito, la comprobación detecta errores de
transcripción; cuando no lo publica, el dígito se calcula y se declara como
calculado, nunca como leído.

Uso:
    python verificar_nit.py            # escribe fuente-verificacion-nit.csv
    python verificar_nit.py --aplicar  # además, copia el resultado a actores.csv
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventario as inv

DIR = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(inv.FUENTES, "fuente-verificacion-nit.csv")

# Palabras que aparecen en casi toda razón social colombiana y que, por eso, no
# sirven para decidir si dos nombres son el mismo actor.
VACIAS = {"DE", "DEL", "LA", "EL", "LOS", "LAS", "Y", "SA", "SAS", "LTDA", "LIMITADA",
          "ESE", "EPS", "IPS", "S", "A", "NACIONAL", "COLOMBIA", "COLOMBIANO",
          "COLOMBIANA", "ASOCIACION", "FUNDACION", "SOCIEDAD", "EMPRESA", "ENTIDAD"}


def _norm(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").upper()
    return re.sub(r"[^A-Z0-9 ]", " ", re.sub(r"\s+", " ", s)).strip()


def _tokens(s):
    return {t for t in _norm(s).split() if t not in VACIAS and len(t) > 2}


def concuerda(nombre_inventario, sigla, nombre_registro):
    """¿El nombre que publica el registro corresponde al actor del inventario?"""
    reg = _tokens(nombre_registro)
    if not reg:
        return False
    for candidato in (nombre_inventario, sigla):
        t = _tokens(candidato)
        if t and len(t & reg) / min(len(t), len(reg)) >= 0.5:
            return True
    return False


def _soql(ds, **p):
    url = "https://www.datos.gov.co/resource/%s.json?" % ds + urllib.parse.urlencode(p)
    req = urllib.request.Request(url, headers={"User-Agent": "RedGiroDirecto/1.0 (proyecto academico)",
                                               "Accept": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=280))


def _nit9(v):
    n = re.sub(r"\D", "", v or "")
    return n[:9] if len(n) in (9, 10) else ""


def _local(archivo, col_nit, col_nombre):
    salida = {}
    ruta = os.path.join(inv.FUENTES, archivo)
    if not os.path.exists(ruta):
        return salida
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            n = _nit9(r.get(col_nit))
            if n:
                salida.setdefault(n, set()).add(r.get(col_nombre, ""))
    return salida


def _en_vivo_por_nit(ds, col_nit, col_nombre, nits, trozo=90):
    """Consulta un registro filtrando por la lista exacta de NIT del inventario.

    Buscar por identificador y no por nombre es lo que hace fuerte la
    comprobación: el registro tiene que devolver el nombre, y es ese nombre el
    que decide si confirma o no.
    """
    salida = {}
    formas = []
    for n in nits:
        formas += [n, n + inv.digito_verificacion(n)]
    for i in range(0, len(formas), trozo):
        lote = ",".join("'%s'" % x for x in formas[i:i + trozo])
        try:
            for x in _soql(ds, **{"$select": "%s,%s" % (col_nit, col_nombre),
                                  "$where": "%s in (%s)" % (col_nit, lote),
                                  "$group": "%s,%s" % (col_nit, col_nombre),
                                  "$limit": "2000"}):
                n = _nit9(x.get(col_nit))
                if n:
                    salida.setdefault(n, set()).add(x.get(col_nombre, ""))
        except Exception as e:                       # una fuente caída no invalida el resto
            print("   ! %s lote %d: %s" % (ds, i, repr(e)[:70]))
    return salida


def _supersociedades_en_vivo(nits, trozo=90):
    """Serie completa de las 10.000 empresas más grandes (Supersociedades), por NIT.

    El archivo local solo trae el corte 2024 del sector salud; la serie en vivo cubre
    los demás cortes. El campo NIT es numérico, así que la lista va sin comillas.
    """
    salida = {}
    for i in range(0, len(nits), trozo):
        lote = ",".join(nits[i:i + trozo])
        try:
            for x in _soql("6cat-2gcs", **{"$select": "nit,raz_n_social", "$where": "nit in (%s)" % lote,
                                           "$group": "nit,raz_n_social", "$limit": "5000"}):
                n = _nit9(x.get("nit", "").split(".")[0])
                if n:
                    salida.setdefault(n, set()).add(x.get("raz_n_social", ""))
        except Exception as e:                       # una fuente caída no invalida el resto
            print("   ! 6cat-2gcs lote %d: %s" % (i, repr(e)[:70]))
    return salida


def verificar(verbose=True):
    filas = inv.leer()
    con_nit = [r for r in filas if r["tipo_identificador"] == "NIT"]
    nits = sorted({_nit9(r["identificador"]) for r in con_nit if _nit9(r["identificador"])})

    registros = {
        "SECOP-entidades": _local("fuente-secop-entidades-nit.csv", "nit", "entidad"),
        "Supersociedades": _local("fuente-supersociedades-empresas-salud-2024.csv", "nit", "raz_n_social"),
    }
    if verbose:
        print("Registros locales cargados: " +
              ", ".join("%s=%d" % (k, len(v)) for k, v in registros.items()))
        print("Consultando registros en vivo para %d NIT..." % len(nits))

    for n, nombres in _supersociedades_en_vivo(nits).items():
        registros["Supersociedades"].setdefault(n, set()).update(nombres)
    registros["REPS"] = _en_vivo_por_nit("c36g-9fc2", "numeroidentificacion", "nombreprestador", nits)
    registros["DIAN-ESAL"] = _en_vivo_por_nit("8tdc-u2ga", "nit", "raz_n_social", nits)
    registros["SECOP-proveedores"] = _en_vivo_por_nit("jbjy-vk9h", "documento_proveedor",
                                                      "proveedor_adjudicado", nits)

    resultados, alertas = [], []
    for r in con_nit:
        n = _nit9(r["identificador"])
        confirman, discrepan = [], []
        for fuente, tabla in registros.items():
            if n not in tabla:
                continue
            if any(concuerda(r["nombre"], r["sigla"], nom) for nom in tabla[n]):
                confirman.append(fuente)
            else:
                discrepan.append("%s: %s" % (fuente, sorted(tabla[n])[0][:44]))

        # El origen del dígito lo fija el script de correcciones cuando normaliza el
        # identificador, porque solo él conoce el estado previo; aquí se arrastra.
        dv_origen = "publicado" if "DV publicado" in (r.get("identificador_fuentes") or "") else "calculado"

        resultados.append(dict(id=r["id"], nombre=r["nombre"], identificador=r["identificador"],
                               n_fuentes=len(confirman), fuentes=" · ".join(confirman),
                               dv_origen=dv_origen, discrepancias=" | ".join(discrepan)))
        if discrepan and not confirman:
            alertas.append((r, discrepan))

    with open(SALIDA, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "nombre", "identificador", "n_fuentes",
                                          "fuentes", "dv_origen", "discrepancias"], lineterminator="\n")
        w.writeheader()
        w.writerows(resultados)

    if verbose:
        import collections
        c = collections.Counter(x["n_fuentes"] for x in resultados)
        print("\nConfirmaciones independientes por identificador:")
        for k in sorted(c, reverse=True):
            print("   %d fuente(s): %3d actores" % (k, c[k]))
        sin = [x for x in resultados if x["n_fuentes"] == 0]
        print("\nSin ninguna confirmación: %d" % len(sin))
        for x in sin:
            print("   %s %-13s %s" % (x["id"], x["identificador"], x["nombre"][:52]))
        if alertas:
            print("\nALERTA — el registro publica ese NIT con otro nombre:")
            for r, d in alertas:
                print("   %s %-40s %s" % (r["id"], r["nombre"][:40], d[0][:70]))
        print("\nEscrito: %s" % os.path.basename(SALIDA))
    return resultados


def aplicar():
    """Copia el resultado de la verificación a la columna identificador_fuentes del inventario."""
    with open(SALIDA, encoding="utf-8-sig", newline="") as f:
        verif = {r["id"]: r for r in csv.DictReader(f)}
    filas = inv.leer()
    n = 0
    for r in filas:
        v = verif.get(r["id"])
        if r["tipo_identificador"] != "NIT" or not v or int(v["n_fuentes"]) == 0:
            continue
        origen = "DV publicado por el registro" if v["dv_origen"] == "publicado" else "DV calculado (algoritmo DIAN)"
        texto = "Confirmado por %s registro(s) independiente(s): %s · %s" % (v["n_fuentes"], v["fuentes"], origen)
        if r["identificador_fuentes"] != texto:
            r["identificador_fuentes"] = texto
            n += 1
    inv.escribir(filas)
    print("Filas actualizadas en actores.csv: %d" % n)


if __name__ == "__main__":
    verificar()
    if "--aplicar" in sys.argv:
        aplicar()
