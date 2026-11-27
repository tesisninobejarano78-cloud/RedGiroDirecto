# -*- coding: utf-8 -*-
"""
Descarga de los anexos mensuales del giro directo que publica la ADRES en Lupa al Giro.

La red observada se construye con estos anexos. El programa los guarda en datos/anexos/ sin
modificarlos y anota en un manifiesto de dónde salió cada archivo, cuándo se bajó y su huella
SHA-256, para poder comprobar después que se trabaja con el mismo archivo.

Qué hace:
  1. Lee las páginas de los módulos contributivo y subsidiado de Lupa al Giro y saca la lista
     completa de documentos de los datos que trae la página (la tabla visible muestra 20 a la
     vez; los datos los traen todos).
  2. Guarda un catálogo con lo publicado hoy en las tres series que usa el proyecto.
  3. Descarga los cortes desde --desde en adelante.
  4. Si la página ya no lista un anexo que el manifiesto registra y que falta en este computador,
     lo baja de la dirección que guarda el manifiesto.

Series:
  contributivo    giro directo del régimen contributivo (zip mensual)
  subsidiado-ips  «Giro LMA por IPS»: giro directo del subsidiado, por prestador
  subsidiado-eps  «Giro LMA por EPS»: giro del subsidiado, por EPS

Reglas:
  - Nunca sobrescribe un archivo. Si ya está guardado, no lo vuelve a bajar.
  - Si falta un archivo que el manifiesto ya registra (por ejemplo, en una copia nueva del
    repositorio), lo baja y compara su huella. Si coincide, lo guarda donde dice el manifiesto.
    Si no coincide, la ADRES cambió el archivo: se guarda aparte, con la fecha de descarga en el
    nombre, y el manifiesto lo registra como «reprocesado».
  - Con --verificar vuelve a bajar los archivos ya guardados para ver si la ADRES los cambió.
  - El manifiesto (salida/manifiesto-descargas.csv) solo se amplía, nunca se reescribe.

Ejecutar:  python descargar-anexos-giro.py [--desde AAAA-MM] [--verificar]
"""

import argparse
import csv
import datetime
import hashlib
import io
import json
import os
import re
import sys
import time
import zipfile
from urllib.error import HTTPError, URLError
from urllib.parse import unquote
from urllib.request import Request, urlopen

import configuracion as cfg

DESTINO = cfg.ANEXOS
SALIDA = cfg.SALIDA
MANIFIESTO = os.path.join(SALIDA, "manifiesto-descargas.csv")

BASE = "https://www.adres.gov.co"
MODULOS = {
    "contributivo": "/lupa-al-giro/regimen-contributivo",
    "subsidiado": "/lupa-al-giro/regimen-subsidiado",
}
UA = {"User-Agent": "RedGiroDirecto/1.0 (proyecto academico; descarga de anexos publicos)"}
DESDE = "2024-01"
PAUSA = 1.0  # segundos entre descargas, para no cargar el servidor de la entidad

CAMPOS_MANIFIESTO = ["serie", "corte", "nombre_publicado", "archivo_publicado", "url",
                     "ruta_local", "fecha_descarga", "bytes", "sha256", "estado"]


def bajar(url, timeout=300):
    return urlopen(Request(url, headers=UA), timeout=timeout).read()


def datos_embebidos(html):
    """Concatena los fragmentos de datos que la página trae embebidos (Next.js)."""
    partes = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html, re.S)
    return "".join(json.loads('"' + p + '"') for p in partes)


def listas_de_documentos(texto):
    """Devuelve [(encabezado, [documentos])] por cada lista de documentos de la página."""
    dec = json.JSONDecoder()
    listas = []
    for m in re.finditer(r'"documents":', texto):
        docs, fin = dec.raw_decode(texto, m.end())
        h = re.search(r'"heading":"([^"]*)"', texto[fin:fin + 400])
        listas.append((h.group(1) if h else "", docs))
    return listas


def catalogo():
    """Las tres series del proyecto, tal como las publica hoy la ADRES."""
    series = {}
    for modulo, ruta in MODULOS.items():
        html = bajar(BASE + ruta, timeout=120).decode("utf-8", "replace")
        for encabezado, docs in listas_de_documentos(datos_embebidos(html)):
            archivos = [d["file"]["filename"] for d in docs if d.get("file")]
            if modulo == "contributivo" and any("contributivo" in a.lower() for a in archivos):
                serie = "contributivo"
            elif modulo == "subsidiado" and encabezado == "Giro LMA por IPS":
                serie = "subsidiado-ips"
            elif modulo == "subsidiado" and encabezado == "Giro LMA por EPS":
                serie = "subsidiado-eps"
            else:
                continue
            if serie in series:
                sys.exit("ERROR: la serie %s aparece dos veces en la página" % serie)
            series[serie] = [{
                "serie": serie,
                "corte": d.get("date") or "",
                "nombre_publicado": d.get("name") or d["file"].get("alt") or "",
                "archivo_publicado": d["file"]["filename"],
                "url": BASE + d["file"]["url"],
            } for d in docs if d.get("file")]
    faltan = {"contributivo", "subsidiado-ips", "subsidiado-eps"} - set(series)
    if faltan:
        sys.exit("ERROR: la página ya no publica la(s) serie(s) %s como antes; hay que revisarla"
                 % ", ".join(sorted(faltan)))
    return series


def anotar(fila):
    nuevo = not os.path.exists(MANIFIESTO)
    with io.open(MANIFIESTO, "a", encoding="utf-8-sig" if nuevo else "utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS_MANIFIESTO, lineterminator="\n")
        if nuevo:
            w.writeheader()
        w.writerow(fila)


def manifiesto():
    """Filas ya registradas en el manifiesto."""
    if not os.path.exists(MANIFIESTO):
        return []
    with io.open(MANIFIESTO, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def relativa(ruta):
    return os.path.relpath(ruta, DESTINO).replace(os.sep, "/")


def huellas_guardadas(carpeta, nombre):
    """Huellas de todas las versiones guardadas de un archivo: la original y las reprocesadas."""
    raiz, ext = os.path.splitext(nombre)
    huellas = set()
    for a in os.listdir(carpeta):
        if a == nombre or (a.startswith(raiz + "__descarga-") and a.endswith(ext)):
            with open(os.path.join(carpeta, a), "rb") as fh:
                huellas.add(hashlib.sha256(fh.read()).hexdigest())
    return huellas


def guardar_sin_sobrescribir(ruta, contenido):
    if os.path.exists(ruta):
        raise FileExistsError(ruta)
    tmp = ruta + ".parcial"
    with open(tmp, "wb") as fh:
        fh.write(contenido)
    os.replace(tmp, ruta)


def ultimos_registrados(registrados):
    """El último archivo registrado de cada (serie, corte), como lo usa la lectura."""
    ultimo = {}
    for r in registrados:
        if r["estado"] in ("nuevo", "reprocesado"):
            clave = (r["serie"], r["corte"])
            if clave not in ultimo or r["fecha_descarga"] >= ultimo[clave]["fecha_descarga"]:
                ultimo[clave] = r
    return ultimo


def traer(serie, d, registrados, hoy, resumen, verificar):
    """Baja un documento y lo anota en el manifiesto según lo que ya se tenía de él."""
    carpeta = os.path.join(DESTINO, serie)
    os.makedirs(carpeta, exist_ok=True)
    nombre = unquote(d["archivo_publicado"])
    ruta = os.path.join(carpeta, nombre)
    if os.path.exists(ruta) and not verificar:
        resumen["omitido"] += 1
        return
    contenido = bajar(d["url"])
    if not zipfile.is_zipfile(io.BytesIO(contenido)):
        sys.exit("ERROR: %s no es un zip ni un xlsx válido" % d["url"])
    huella = hashlib.sha256(contenido).hexdigest()
    fila = dict(d, ruta_local=relativa(ruta), fecha_descarga=hoy, bytes=len(contenido), sha256=huella)
    previas = [r for r in registrados
               if r["serie"] == serie and r["archivo_publicado"] == d["archivo_publicado"]]
    igual = next((r for r in previas if r["sha256"] == huella), None)
    if not os.path.exists(ruta) and igual:
        destino = os.path.join(DESTINO, *igual["ruta_local"].split("/"))
        if not os.path.exists(destino):
            guardar_sin_sobrescribir(destino, contenido)
        resumen["recuperado"] += 1
        print("  %-15s %s  %-44s %9d  recuperado (igual al manifiesto)"
              % (serie, d["corte"], nombre, len(contenido)))
        time.sleep(PAUSA)
        return
    if not os.path.exists(ruta) and not previas:
        guardar_sin_sobrescribir(ruta, contenido)
        fila["estado"] = "nuevo"
    elif os.path.exists(ruta) and huella in huellas_guardadas(carpeta, nombre):
        fila["estado"] = "sin-cambios"
    else:
        raiz, ext = os.path.splitext(nombre)
        ruta_v = os.path.join(carpeta, "%s__descarga-%s%s" % (raiz, hoy, ext))
        n = 2
        while os.path.exists(ruta_v):
            ruta_v = os.path.join(carpeta, "%s__descarga-%s-%d%s" % (raiz, hoy, n, ext))
            n += 1
        guardar_sin_sobrescribir(ruta_v, contenido)
        fila["ruta_local"] = relativa(ruta_v)
        fila["estado"] = "reprocesado"
        print("  AVISO: la ADRES cambió %s desde la última descarga registrada; los resultados "
              "pueden diferir de los publicados" % nombre)
    anotar(fila)
    resumen[fila["estado"]] += 1
    print("  %-15s %s  %-44s %9d  %s" % (serie, d["corte"], nombre, len(contenido), fila["estado"]))
    time.sleep(PAUSA)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", default=DESDE, help="primer corte a descargar (AAAA-MM)")
    ap.add_argument("--verificar", action="store_true",
                    help="volver a bajar los cortes ya guardados para detectar reprocesos")
    args = ap.parse_args()

    os.makedirs(SALIDA, exist_ok=True)
    hoy = datetime.date.today().isoformat()
    series = catalogo()

    # 1. Catálogo de lo publicado hoy, en todas las fechas.
    ruta_cat = os.path.join(SALIDA, "catalogo-lupa-al-giro-%s.csv" % hoy)
    with io.open(ruta_cat, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["serie", "corte", "nombre_publicado",
                                           "archivo_publicado", "url"], lineterminator="\n")
        w.writeheader()
        for serie in sorted(series):
            for d in sorted(series[serie], key=lambda d: d["corte"]):
                w.writerow(d)
    for serie in sorted(series):
        cortes = sorted(d["corte"] for d in series[serie])
        print("%-15s %3d documentos publicados (%s a %s)" % (serie, len(cortes), cortes[0], cortes[-1]))

    # 2. Descarga de la ventana.
    resumen = {"nuevo": 0, "recuperado": 0, "sin-cambios": 0, "reprocesado": 0, "omitido": 0}
    registrados = manifiesto()
    for serie in sorted(series):
        for d in sorted(series[serie], key=lambda d: d["corte"]):
            if not re.fullmatch(r"\d{4}-\d{2}", d["corte"]) or d["corte"] < args.desde:
                continue
            traer(serie, d, registrados, hoy, resumen, args.verificar)

    # 3. Anexos del manifiesto que la página ya no lista y que faltan en este computador: se bajan
    #    de la dirección que guarda el manifiesto, para que la lectura tenga todos sus cortes.
    publicados = {(s, d["archivo_publicado"]) for s in series for d in series[s]}
    for (serie, corte), r in sorted(ultimos_registrados(registrados).items()):
        if (serie, r["archivo_publicado"]) in publicados or corte < args.desde:
            continue
        if os.path.exists(os.path.join(DESTINO, *r["ruta_local"].split("/"))):
            continue
        print("  AVISO: la página ya no lista %s (%s, %s); se baja de la dirección del manifiesto"
              % (r["archivo_publicado"], serie, corte))
        d = {k: r[k] for k in ("serie", "corte", "nombre_publicado", "archivo_publicado", "url")}
        try:
            traer(serie, d, registrados, hoy, resumen, False)
        except (HTTPError, URLError) as e:
            print("  AVISO: no se pudo bajar %s (%s); sin ese archivo, la lectura no puede seguir"
                  % (r["archivo_publicado"], e))

    print("\nCatálogo:", os.path.basename(ruta_cat))
    print("Resumen:", ", ".join("%s %d" % kv for kv in resumen.items()))


if __name__ == "__main__":
    main()
