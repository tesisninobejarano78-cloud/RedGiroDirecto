# -*- coding: utf-8 -*-
"""
Clasificación de los prestadores de la red observada con el REPS.

Los anexos de Lupa al Giro identifican a cada receptor por su NIT y su razón social, sin decir qué
clase de prestador es. Este programa le pone a cada NIT la clase, la naturaleza jurídica, la
condición de ESE y el departamento que registra el REPS (Registro Especial de Prestadores y Sedes
del Ministerio de Salud, conjunto c36g-9fc2 de datos.gov.co), y marca los receptores que no
aparecen en el REPS. Sirve para leer las métricas de la red por tipo de prestador y para agrupar a
los prestadores en el visor.

Datos personales: la consulta trae solo filas con tipo de identificación NI y solo columnas sin
datos de contacto (no pide nombres, direcciones, correos ni teléfonos). Además se descartan las
identificaciones que no tienen la forma de un NIT de empresa (nueve dígitos que empiezan en 8 o 9),
que pueden ser de personas naturales; es la misma regla que usa la lectura de los anexos.

Pasos:
  1. Con --descargar, baja un extracto nuevo del REPS a datos/reps/ y lo anota en su manifiesto.
     Nunca sobrescribe: cada descarga es un archivo nuevo. Sin --descargar usa el extracto más
     reciente que ya esté guardado, para que los resultados no cambien de una corrida a otra.
  2. Resume el extracto por NIT: un prestador puede tener varios códigos y muchas sedes.
  3. Cruza con salida/prestadores.csv (los NIT de los anexos) y, para los que no están en el REPS,
     con el inventario de actores (subsector B2, distribución y dispensación de medicamentos).

Salida: salida/prestadores-clasificados.csv

Ejecutar:  python clasificar-prestadores.py [--descargar]
"""

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import urllib.parse
import urllib.request

import pandas as pd

import configuracion as cfg

SALIDA = cfg.SALIDA
CRUDO = cfg.REPS
INVENTARIO = cfg.INVENTARIO

REPS = "https://www.datos.gov.co/resource/c36g-9fc2.json"
COLUMNAS = ["numeroidentificacion", "codigoprestador", "naturalezajuridica", "ese",
            "claseprestador", "departamentoprestadordesc", "municipioprestadordesc",
            "fecha_corte_reps"]
CLASE_IPS = "Instituciones Prestadoras de Servicios de Salud - IPS"


def soql(**params):
    url = REPS + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "RedGiroDirecto/1.0 (proyecto academico)"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r), url


def descargar():
    """Baja el extracto del día (filas NI, columnas sin datos de contacto) y lo registra.
    Descarta las identificaciones que no son NIT de empresa (posibles personas naturales)."""
    os.makedirs(CRUDO, exist_ok=True)
    hoy = dt.date.today().isoformat()
    destino = os.path.join(CRUDO, "reps-prestadores-nit-%s.csv" % hoy)
    if os.path.exists(destino):
        print("Ya existe %s: no se vuelve a descargar" % os.path.basename(destino))
        return destino
    filas, urls, offset = [], [], 0
    while True:
        lote, url = soql(**{"$select": ",".join(COLUMNAS) + ",count(*) as sedes",
                            "$where": "tipoid='NI'",
                            "$group": ",".join(COLUMNAS),
                            "$order": "numeroidentificacion,codigoprestador",
                            "$limit": "20000", "$offset": str(offset)})
        filas += lote
        urls.append(url)
        if len(lote) < 20000:
            break
        offset += 20000
    filas = [f for f in filas if re.fullmatch(r"[89]\d{8}", str(f.get("numeroidentificacion", "")).strip())]
    with io.open(destino, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS + ["sedes"], lineterminator="\n")
        w.writeheader()
        for f in filas:
            w.writerow({k: f.get(k, "") for k in COLUMNAS + ["sedes"]})
    huella = hashlib.sha256(open(destino, "rb").read()).hexdigest()
    manifiesto = os.path.join(CRUDO, "manifiesto.csv")
    nuevo = not os.path.exists(manifiesto)
    with io.open(manifiesto, "a", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        if nuevo:
            w.writerow(["archivo", "fecha_descarga", "filas", "sha256", "consulta"])
        w.writerow([os.path.basename(destino), hoy, len(filas), huella, " | ".join(urls)])
    print("Descargado %s: %d filas (NIT x código de prestador x municipio)" % (
        os.path.basename(destino), len(filas)))
    return destino


def ultimo_extracto():
    archivos = sorted(f for f in os.listdir(CRUDO) if f.startswith("reps-prestadores-nit-")) \
        if os.path.isdir(CRUDO) else []
    if not archivos:
        raise SystemExit("ERROR: no hay extracto del REPS en %s; correr con --descargar" % CRUDO)
    return os.path.join(CRUDO, archivos[-1])


def resumir(ruta):
    """Una fila por NIT. Si un NIT tiene varios códigos, manda el que más sedes tiene."""
    r = pd.read_csv(ruta, dtype=str)
    r["sedes"] = r.sedes.astype(int)
    r = r[r.numeroidentificacion.str.fullmatch(r"\d+")]
    por_cod = (r.groupby(["numeroidentificacion", "codigoprestador", "naturalezajuridica", "ese",
                          "claseprestador", "departamentoprestadordesc", "municipioprestadordesc"],
                         as_index=False).sedes.sum()
               .sort_values(["numeroidentificacion", "sedes", "codigoprestador"],
                            ascending=[True, False, True]))
    g = por_cod.groupby("numeroidentificacion")
    out = g.first().reset_index()[["numeroidentificacion", "naturalezajuridica", "ese", "claseprestador",
                                   "departamentoprestadordesc", "municipioprestadordesc"]]
    out["codigos_reps"] = g.codigoprestador.nunique().values
    out["sedes_reps"] = g.sedes.sum().values
    out["departamentos_reps"] = g.departamentoprestadordesc.nunique().values
    out["ese"] = g.ese.agg(lambda s: "SI" if (s == "SI").any() else "NO").values
    out["clases_reps"] = g.claseprestador.nunique().values
    out["fecha_corte_reps"] = r.fecha_corte_reps.iloc[0]
    return out.rename(columns={"numeroidentificacion": "nit", "naturalezajuridica": "naturaleza_juridica",
                               "claseprestador": "clase_prestador",
                               "departamentoprestadordesc": "departamento",
                               "municipioprestadordesc": "municipio"})


def tipo(f):
    if f.en_reps:
        if f.ese == "SI":
            return "ESE (empresa social del Estado)"
        if f.clase_prestador != CLASE_IPS:
            return "Otra clase del REPS"
        return {"Pública": "IPS pública no ESE", "Privada": "IPS privada",
                "Mixta": "IPS mixta"}.get(f.naturaleza_juridica, "IPS sin naturaleza")
    if f.subsector_inventario == "B2":
        return "Gestor o dispensador farmacéutico"
    return "Sin inscripción en el REPS"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--descargar", action="store_true", help="bajar un extracto nuevo del REPS")
    if ap.parse_args().descargar:
        descargar()
    ruta = ultimo_extracto()
    print("Extracto del REPS:", os.path.basename(ruta))
    reps = resumir(ruta)
    pre = pd.read_csv(os.path.join(SALIDA, "prestadores.csv"), dtype=str)
    inv = pd.read_csv(INVENTARIO, dtype=str)
    inv = inv[inv.tipo_identificador.fillna("").str.contains("NIT")].copy()
    inv["nit"] = inv.identificador.str.split("-").str[0].str.strip()
    inv = (inv.sort_values("id").drop_duplicates("nit")
           [["nit", "id", "subsector"]].rename(columns={"id": "id_inventario",
                                                        "subsector": "subsector_inventario"}))
    out = pre.merge(reps, on="nit", how="left").merge(inv, on="nit", how="left")
    out["en_reps"] = out.clase_prestador.notna()
    out["tipo_prestador"] = out.apply(tipo, axis=1)
    out["fuente_tipo"] = out.en_reps.map({True: "REPS", False: ""})
    out.loc[~out.en_reps & out.subsector_inventario.eq("B2"), "fuente_tipo"] = "inventario de actores"
    out = out[["nit", "razon_social", "tipo_prestador", "fuente_tipo", "en_reps", "clase_prestador",
               "naturaleza_juridica", "ese", "departamento", "municipio", "departamentos_reps",
               "codigos_reps", "clases_reps", "sedes_reps", "id_inventario", "subsector_inventario",
               "cortes_contributivo", "cortes_subsidiado", "primer_corte", "ultimo_corte",
               "fecha_corte_reps"]]
    out.to_csv(os.path.join(SALIDA, "prestadores-clasificados.csv"), index=False, encoding="utf-8-sig",
               lineterminator="\n")

    print("\nPrestadores de los anexos: %d · en el REPS: %d (%.1f %%) · con varios departamentos: %d" % (
        len(out), out.en_reps.sum(), 100 * out.en_reps.mean(), (out.departamentos_reps > 1).sum()))
    print("\nPor tipo:")
    print(out.tipo_prestador.value_counts().to_string())
    desde = min(cfg.CONTROL + [cfg.PRINCIPAL])
    recientes = out[out.ultimo_corte >= desde]
    print("\nCon giro desde %s (%d), por tipo:" % (desde, len(recientes)))
    print(recientes.tipo_prestador.value_counts().to_string())


if __name__ == "__main__":
    main()
