# -*- coding: utf-8 -*-
"""
Lectura de los anexos del giro directo.

Lee los anexos guardados en datos/anexos/ (los que registra el manifiesto de
descargar-anexos-giro.py), sin modificarlos, en dos pasadas:

  1. Las tablas por EPS de cada corte: la certificación del giro a EPS del subsidiado y las hojas
     de valores reconocidos y licencias del contributivo.
  2. Las relaciones (hojas «Giro a IPS - Proceso» y «Giro a Prestadores-Complemento»), corrigiendo
     con las tablas de la pasada 1 los códigos de EPS que el anexo publica mal.

Antes de leer cada archivo comprueba que su huella SHA-256 sea la del manifiesto.

Salidas en salida/:
  esquema-anexos.csv               una fila por hoja leída: encabezado, columnas y cómo se
                                   interpretó cada una
  controles-por-hoja.csv           los controles de lectura, en cada corte y hoja
  correcciones-codigo-eps.csv      cada código de EPS reasignado, con su regla
  relaciones-giro-directo.csv.gz   la tabla de relaciones: una fila por corte, régimen, proceso,
                                   EPS y prestador, con la suma de lo ordenado y lo girado y el
                                   número de operaciones
  operaciones-con-diferencia.csv   las operaciones con giro en cero u ordenado distinto de
                                   girado, con su observación
  observaciones-por-corte.csv      operaciones y montos según la causa que cita el campo
                                   Observación (quién ordenó un complemento, por qué no se giró lo
                                   ordenado) y cuántas llegaron por correo
  observaciones-por-eps.csv        lo mismo, abierto por código de EPS
  prestadores.csv                  un registro por prestador receptor
  codigos-eps.csv                  un registro por código de EPS, con los nombres vistos
  eps-por-corte.csv                los valores por EPS de las tablas de la pasada 1
  cotejo-certificacion.csv         giro directo por EPS según la certificación del subsidiado
                                   frente a la suma de las relaciones
  resumen-ingesta.txt              lo anterior, en texto

Reglas:
  - Una fila es una operación, no una relación: la relación es la pareja EPS-prestador dentro del
    corte, su peso es la suma y el número de operaciones queda como atributo.
  - Las filas con giro en cero u ordenado distinto de girado se conservan.
  - Los encabezados, títulos, subtotales y notas quedan fuera porque no tienen identificación
    válida; se cuentan en los controles.
  - Una identificación que no tiene la forma de un NIT de empresa (nueve dígitos que empiezan en
    8 o 9) se trata como posible persona natural: se agrega en un nodo colectivo (PN-AGREGADO) y su
    identificación no se publica.
  - Un código de EPS se reasigna solo si no existe en la tabla de EPS del corte o pertenece a otra
    EPS, y el nombre publicado en la misma fila corresponde a un único código de esa tabla. Lo
    demás se conserva como viene.
  - Una columna o una hoja desconocida detiene el programa: un cambio de formato no debe pasar en
    silencio.

Ejecutar:  python ingerir-anexos-giro.py
"""

import collections
import csv
import datetime
import gzip
import hashlib
import io
import os
import re
import sys
import unicodedata
import zipfile

import openpyxl

import configuracion as cfg

SALIDA = cfg.SALIDA
MANIFIESTO = os.path.join(SALIDA, "manifiesto-descargas.csv")

REGIMEN = {"contributivo": "contributivo", "subsidiado-ips": "subsidiado", "subsidiado-eps": "subsidiado"}
NODO_PERSONA_NATURAL = "PN-AGREGADO"
MESES = {m: i for i, m in enumerate(
    ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
     "septiembre", "octubre", "noviembre", "diciembre"], 1)}

# Tipo de hoja según su nombre (normalizado, por prefijo: la ADRES a veces lo trunca).
TIPOS_HOJA = [
    ("giro a ips - proceso", "proceso"),
    ("giro a prestadores-comple", "complemento"),
    ("valores reconocidos proceso", "reconocimiento-eps"),
    ("licencias", "licencias-eps"),
    ("certificacion giro a eps", "certificacion-eps"),
]
ARISTAS = ("proceso", "complemento")

# Encabezado normalizado -> campo. Una columna que no esté aquí detiene la ingesta.
CAMPOS_ARISTA = {
    "nit": "nit", "razon social": "razon_social", "codigo eps": "codigo_eps",
    "nombre eps": "nombre_eps", "valor ordenado": "valor_ordenado",
    "valor giro ips": "valor_girado", "valor giro a ips": "valor_girado",
    "observacion": "observacion", "observaciones": "observacion",
    "fecha proceso giro directo": "fecha_proceso", "fecha proceso": "fecha_proceso",
    "fecha giro": "fecha_giro", "fecha de giro": "fecha_giro",
}
CAMPOS_EPS = {
    "codigo eps": "codigo_eps", "eps": "nombre_eps", "nombre eps": "nombre_eps",
    "entidad": "nombre_eps", "observacion": "observacion",
    # certificación del subsidiado
    "upc apropiada": "upc_apropiada", "upc restituida": "upc_restituida", "upc neta": "upc_neta",
    "valor a girar fuentes de financiacion nivel central": "valor_a_girar",
    "descuento de auditorias rs": "descuento_auditorias",
    "descuento de cuenta de alto costo": "descuento_alto_costo",
    "descuento cuenta de alto costo": "descuento_alto_costo",
    "descuento de tasa compensada": "descuento_tasa_compensada",
    "descuento reintegro de recursos - dop": "descuento_reintegro_dop",
    "hemofilia": "descuento_hemofilia", "descuento de hemofilia": "descuento_hemofilia",
    "descuento hemofilia": "descuento_hemofilia",
    "recobros": "descuento_recobros",
    "giro directo a ips y/o proveedores - proceso": "giro_directo_proceso",
    "giro directo a ips y/o proveedores - complemento": "giro_directo_complemento",
    "fecha de giro complemento": "fecha_giro_complemento",
    "giro neto a eps": "giro_neto_eps",
    # reconocimiento del contributivo
    "upc de afiliados activos": "upc_afiliados_activos",
    "provision de incapacidades": "provision_incapacidades",
    "per capita promocion y prevencion": "percapita_promocion_prevencion",
    "valor total reconocido": "valor_total_reconocido",
    # licencias del contributivo
    "valor maternidad": "licencias_maternidad", "valor paternidad": "licencias_paternidad",
    "valor tutelas": "licencias_tutelas", "total": "licencias_total",
}
CAMPOS_NUMERICOS_EPS = [c for c in dict.fromkeys(CAMPOS_EPS.values())
                        if c not in ("codigo_eps", "nombre_eps", "observacion", "fecha_giro_complemento")]

# Palabras que no distinguen a una EPS de otra al comparar nombres.
VACIAS_EPS = {"EPS", "EPSS", "EPSI", "EOC", "E", "P", "S", "SA", "SAS", "LTDA",
              "MOVILIDAD", "LA", "EL", "EN", "LIQUIDACION", "ESP"}


def norm(s):
    """Minúsculas, sin tildes, sin $ ( ) * y con espacios simples."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[$()*]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def canon_eps(nombre):
    """Nombre de EPS reducido a lo que la distingue: «EPS COOSALUD» y «Coosalud movilidad» -> COOSALUD."""
    s = unicodedata.normalize("NFKD", str(nombre or "")).encode("ascii", "ignore").decode().upper()
    s = s.replace(".", "")
    return "".join(t for t in re.split(r"[^A-Z0-9]+", s) if t and t not in VACIAS_EPS)


def compatibles(a, b):
    if not a or not b:
        return False
    corto, largo = sorted((a, b), key=len)
    return corto == largo or (len(corto) >= 5 and largo.startswith(corto))


def corregir_codigo(cod, nombre, tabla):
    """Código de EPS que corresponde a la fila y la regla aplicada ("" si se conserva).

    tabla: {código: {nombres canónicos}} de la tabla por EPS del mismo régimen y corte.
    """
    if not tabla:
        return cod, ""
    cn = canon_eps(nombre)
    propios = tabla.get(cod)
    if propios is not None and (not cn or any(compatibles(cn, n) for n in propios)):
        return cod, ""
    candidatos = sorted(c for c, ns in tabla.items() if any(compatibles(cn, n) for n in ns))
    if len(candidatos) == 1 and candidatos[0] != cod:
        regla = "código inexistente en el corte" if propios is None else "código de otra EPS"
        return candidatos[0], regla
    if propios is None:
        return cod, "sin corrección: " + ("nombre ambiguo" if candidatos else "sin correspondencia")
    return cod, ""  # código válido con otro nombre (p. ej. cambio de razón social): se conserva


def categoria_observacion(texto):
    """Causa que cita el campo Observación de una operación.

    Los giros del complemento dicen «con cargo a los $X no aplicados en el proceso de la
    LMA, atendiendo comunicación de …»: se clasifican por quién emitió la comunicación.
    Las demás observaciones explican por qué no se giró lo ordenado.
    """
    t = norm(texto)
    if not t:
        return "(vacía)"
    if "con cargo a" in t:
        if "pisis" in t:
            return "cargue en PISIS"
        if "agente interventor" in t:
            return "comunicación del agente interventor"
        if re.search(r"\bsns\b|superintendencia|supersalud", t):
            return "comunicación de la Supersalud"
        if re.search(r"comunicaci\w* de la eps", t):
            return "comunicación de la EPS"
        if "comunicaci" in t:
            return "comunicación sin emisor identificado"
        return "otra"
    if "embargo" in t:
        return "embargo"
    if "giro realizado" in t:
        return "giro tras un rechazo"
    if re.search(r"rechaz|cuenta|reversad|no habilitada|no autorizada", t):
        return "falla bancaria"
    if "auditoria" in t:
        return "descuento de auditoría"
    if re.search(r"\bsns\b|superintendencia|supersalud", t):
        return "comunicación de la Supersalud"
    if "resolucion" in t:
        return "resolución sin emisor identificado"
    return "otra"


def tipo_de_hoja(nombre):
    n = norm(nombre)
    for prefijo, tipo in TIPOS_HOJA:
        if n.startswith(prefijo):
            return tipo
    sys.exit("ERROR: hoja no reconocida %r; el formato del anexo cambió" % nombre)


def leer_manifiesto():
    """Último archivo descargado por (serie, corte): si la ADRES reprocesó un corte, el más reciente."""
    with io.open(MANIFIESTO, encoding="utf-8-sig", newline="") as fh:
        filas = list(csv.DictReader(fh))
    ultimo = {}
    for f in filas:
        if f["estado"] in ("nuevo", "reprocesado"):
            clave = (f["serie"], f["corte"])
            if clave not in ultimo or f["fecha_descarga"] >= ultimo[clave]["fecha_descarga"]:
                ultimo[clave] = f
    return [ultimo[k] for k in sorted(ultimo)]


def abrir(ruta, sha256):
    with open(ruta, "rb") as fh:
        contenido = fh.read()
    if hashlib.sha256(contenido).hexdigest() != sha256:
        sys.exit("ERROR: %s no coincide con la huella del manifiesto" % ruta)
    if ruta.lower().endswith(".zip"):
        z = zipfile.ZipFile(io.BytesIO(contenido))
        libros = [n for n in z.namelist() if n.lower().endswith(".xlsx")]
        if len(libros) != 1 or len(z.namelist()) != 1:
            sys.exit("ERROR: %s trae %s; se esperaba un solo libro" % (ruta, z.namelist()))
        contenido = z.read(libros[0])
    return openpyxl.load_workbook(io.BytesIO(contenido), read_only=True, data_only=True)


def nit_normalizado(v):
    """Devuelve la identificación como texto de dígitos, o None si la celda no es una identificación."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, float):
        if v != int(v):
            return None
        v = int(v)
    s = re.sub(r"[\s.]", "", str(v).strip())
    if re.fullmatch(r"\d+-\d", s):  # NIT con dígito de verificación
        s = s.split("-")[0]
    return s if re.fullmatch(r"\d{5,11}", s) else None


def numero(v, contexto):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    s = str(v).strip()
    if re.fullmatch(r"-?\d+(\.\d+)?", s):
        return float(s)
    sys.exit("ERROR: valor no numérico %r en %s" % (v, contexto))


def mes_del_titulo(filas_titulo):
    """Mes y año que declara el título de la hoja (p. ej. «OCTUBRE DE 2026»)."""
    texto = " ".join(norm(c) for r in filas_titulo for c in r if isinstance(c, str))
    m = re.search(r"\b(%s)\b(?: de)? (\d{4})" % "|".join(MESES), texto)
    return "%s-%02d" % (m.group(2), MESES[m.group(1)]) if m else ""


def fecha_de_giro_del_titulo(filas_titulo):
    for r in filas_titulo:
        for c in r:
            if isinstance(c, str):
                m = re.search(r"fecha de giro:\s*(\d{2})/(\d{2})/(\d{4})", norm(c))
                if m:
                    return "%s-%s-%s" % (m.group(3), m.group(2), m.group(1))
    return ""


def como_fecha(v):
    if isinstance(v, datetime.datetime):
        return v.date().isoformat()
    if isinstance(v, datetime.date):
        return v.isoformat()
    return "" if v is None else str(v).strip()


def ubicar_encabezado(filas, tipo):
    """Fila del encabezado y mapa columna -> nombre. La certificación del subsidiado
    trae un encabezado de dos filas (grupo arriba, columna abajo)."""
    clave = "nit" if tipo in ARISTAS else "codigo eps"
    for i, r in enumerate(filas[:60]):
        if any(c is not None and norm(c) == clave for c in r):
            principal = list(r)
            sub = list(filas[i + 1]) if tipo == "certificacion-eps" and i + 1 < len(filas) else []
            nombres = {}
            for j, c in enumerate(principal):
                s = sub[j] if j < len(sub) and sub[j] is not None else c
                if s is not None and str(s).strip():
                    nombres[j] = str(s).strip()
            return i, (1 if sub else 0), nombres
    sys.exit("ERROR: no se encontró el encabezado de una hoja de tipo %s" % tipo)


def mapear(nombres, tipo, contexto):
    tabla = CAMPOS_ARISTA if tipo in ARISTAS else CAMPOS_EPS
    mapa, notas, vistos = {}, [], collections.Counter()
    for j in sorted(nombres):
        n = norm(nombres[j])
        if n in ("liquidacion del proceso", "giros y descuentos aplicados en el proceso"):
            continue  # rótulos de grupo del encabezado de dos filas
        if n not in tabla:
            sys.exit("ERROR: columna desconocida %r en %s" % (nombres[j], contexto))
        campo = tabla[n]
        vistos[campo] += 1
        if vistos[campo] == 2 and campo == "valor_girado" and "valor_ordenado" not in mapa.values():
            # Complemento de junio de 2024: «Valor Giro a IPS ($)» aparece dos veces. En el
            # resto de la serie el orden es ordenado, girado: la primera se toma como ordenado.
            primera = [k for k, v in mapa.items() if v == "valor_girado"][0]
            mapa[primera] = "valor_ordenado"
            notas.append("encabezado «%s» repetido: la primera se lee como valor ordenado" % nombres[j])
        elif vistos[campo] > 1:
            sys.exit("ERROR: columna repetida %r en %s" % (nombres[j], contexto))
        mapa[j] = campo
    return mapa, notas


class Hoja:
    """Una hoja ya ubicada: su tipo, su registro de esquema y acceso a sus celdas por campo."""

    def __init__(self, wb, nombre, serie, corte, archivo):
        self.tipo = tipo_de_hoja(nombre)
        contexto = "%s %s «%s»" % (serie, corte, nombre)
        self.contexto = contexto
        filas = [tuple(r) for r in wb[nombre].iter_rows(values_only=True)]
        i_enc, extra, nombres = ubicar_encabezado(filas, self.tipo)
        mapa, notas = mapear(nombres, self.tipo, contexto)
        titulo = filas[:i_enc]
        mes_titulo = mes_del_titulo(titulo)
        if mes_titulo and mes_titulo != corte:
            notas.append("el título dice %s y el catálogo %s" % (mes_titulo, corte))
        self.campos = set(mapa.values())
        if self.tipo in ARISTAS and "valor_ordenado" not in self.campos:
            notas.append("sin columna de valor ordenado")
        self.esquema = {
            "serie": serie, "corte": corte, "archivo": archivo, "hoja": nombre,
            "tipo": self.tipo, "fila_encabezado": i_enc + 1,
            "columnas_originales": " | ".join(nombres[j] for j in sorted(nombres)),
            "campos": " | ".join(mapa[j] for j in sorted(mapa)),
            "mes_del_titulo": mes_titulo,
            "fecha_giro_del_titulo": fecha_de_giro_del_titulo(titulo),
            "notas": "; ".join(notas)}
        self.cuerpo = filas[i_enc + 1 + extra:]
        self.col = {v: k for k, v in mapa.items()}

    def celda(self, r, campo):
        k = self.col.get(campo)
        return r[k] if k is not None and k < len(r) else None


def hojas(archivos, tipos):
    """Recorre las hojas de los tipos pedidos, archivo por archivo."""
    for a in archivos:
        ruta = os.path.join(cfg.ANEXOS, *a["ruta_local"].split("/"))
        wb = abrir(ruta, a["sha256"])
        for nombre in wb.sheetnames:
            if tipo_de_hoja(nombre) in tipos:
                yield a, Hoja(wb, nombre, a["serie"], a["corte"], os.path.basename(ruta))
        wb.close()


def main():
    os.makedirs(SALIDA, exist_ok=True)
    archivos = leer_manifiesto()
    faltan = [a["ruta_local"] for a in archivos
              if not os.path.exists(os.path.join(cfg.ANEXOS, *a["ruta_local"].split("/")))]
    if faltan:
        sys.exit("ERROR: faltan %d de los %d anexos del manifiesto en %s (por ejemplo, %s).\n"
                 "Para bajarlos, corra correr-todo.py sin --sin-descarga. Si ya están en otra carpeta, "
                 "indíquela en rutas-locales.json (ver configuracion.py)."
                 % (len(faltan), len(archivos), cfg.ANEXOS, faltan[0]))
    esquema = []

    # ------------------------------------------------- pasada 1: tablas por EPS
    eps_filas = []
    tabla_eps = collections.defaultdict(lambda: collections.defaultdict(set))
    for a, h in hojas(archivos, ("reconocimiento-eps", "licencias-eps", "certificacion-eps")):
        esquema.append(h.esquema)
        regimen = REGIMEN[a["serie"]]
        for r in h.cuerpo:
            cod = h.celda(r, "codigo_eps")
            if cod is None or not str(cod).strip() or norm(cod).startswith("total"):
                continue
            if not re.fullmatch(r"[A-Z0-9]{4,8}", str(cod).strip().upper()):
                continue  # notas al pie
            fila = {"serie": a["serie"], "corte": a["corte"], "regimen": regimen, "tabla": h.tipo,
                    "codigo_eps": str(cod).strip().upper(),
                    "nombre_eps": str(h.celda(r, "nombre_eps") or "").strip(),
                    "observacion": str(h.celda(r, "observacion") or "").strip(),
                    "fecha_giro_complemento": como_fecha(h.celda(r, "fecha_giro_complemento"))}
            for campo in CAMPOS_NUMERICOS_EPS:
                v = numero(h.celda(r, campo), h.contexto) if campo in h.campos else None
                fila[campo] = "" if v is None else "%.2f" % v
            eps_filas.append(fila)
            tabla_eps[(regimen, a["corte"])][fila["codigo_eps"]].add(canon_eps(fila["nombre_eps"]))

    # ------------------------------------------------- pasada 2: aristas
    controles, diferencias = [], []
    correcciones = collections.Counter()
    relaciones = {}       # (corte, regimen, proceso, codigo_eps, nit) -> acumulados
    nombres_ips = collections.defaultdict(collections.Counter)
    cortes_ips = collections.defaultdict(set)
    nombres_eps = collections.defaultdict(collections.Counter)
    cortes_eps = collections.defaultdict(set)
    firmas = {}           # (serie, proceso, corte) -> operaciones con fecha propia
    # operaciones, girado, no girado, por correo, operaciones con algo sin girar
    causas = collections.defaultdict(lambda: [0, 0.0, 0.0, 0, 0])
    causas_eps = collections.defaultdict(lambda: [0, 0.0, 0.0, 0, 0])  # lo mismo, por código de EPS
    personas_naturales = 0

    for a, h in hojas(archivos, ARISTAS):
        esquema.append(h.esquema)
        serie, corte, regimen, tipo = a["serie"], a["corte"], REGIMEN[a["serie"]], h.tipo
        tabla = tabla_eps.get((regimen, corte), {})
        datos, descartadas = [], collections.Counter()
        for r in h.cuerpo:
            if not any(c is not None and str(c).strip() for c in r):
                continue
            nit = nit_normalizado(h.celda(r, "nit"))
            cod = h.celda(r, "codigo_eps")
            if nit is None or cod is None or not str(cod).strip():
                descartadas[norm(r[0])[:40] if r and r[0] is not None else "(subtotal sin identificación)"] += 1
                continue
            datos.append(r)

        c = collections.Counter()
        parejas = collections.Counter()
        exactas = collections.Counter()
        obs = collections.Counter()
        firmas_hoja = set()
        tot_ord = tot_gir = dif_total = 0.0
        tiene_ord = "valor_ordenado" in h.campos
        for r in datos:
            nit = nit_normalizado(h.celda(r, "nit"))
            cod_pub = str(h.celda(r, "codigo_eps")).strip().upper()
            nom_eps = str(h.celda(r, "nombre_eps") or "").strip()
            razon = str(h.celda(r, "razon_social") or "").strip()
            ctx = "%s fila de %s" % (h.contexto, nit)
            gir = numero(h.celda(r, "valor_girado"), ctx)
            ordn = numero(h.celda(r, "valor_ordenado"), ctx) if tiene_ord else None
            o = str(h.celda(r, "observacion") or "").strip()
            cod, regla = corregir_codigo(cod_pub, nom_eps, tabla)
            if regla:
                correcciones[(serie, corte, tipo, cod_pub, nom_eps, cod, regla)] += 1
                c["codigo_corregido" if cod != cod_pub else "codigo_sin_correspondencia"] += 1
            if not nit.startswith(("8", "9")) or len(nit) != 9:
                c["id_no_8_9" if not nit.startswith(("8", "9")) else "id_longitud_distinta_de_9"] += 1
                personas_naturales += 1
                nit, razon = NODO_PERSONA_NATURAL, "Personas naturales (agregado)"
            exactas[tuple("" if v is None else str(v) for v in r)] += 1
            parejas[(cod, nit)] += 1
            obs[o[:80] if o else "(vacía)"] += 1
            if gir is None:
                c["sin_valor_girado"] += 1
                gir = 0.0
            if gir == 0:
                c["girado_cero"] += 1
            if gir < 0:
                c["girado_negativo"] += 1
            con_dif = ordn is not None and abs(ordn - gir) > 0.5
            if con_dif:
                c["ordenado_distinto_de_girado"] += 1
                dif_total += ordn - gir
            if gir == 0 or con_dif:
                diferencias.append({
                    "serie": serie, "corte": corte, "proceso": tipo, "codigo_eps": cod,
                    "nit": nit, "razon_social": razon,
                    "valor_ordenado": "" if ordn is None else "%.0f" % ordn,
                    "valor_girado": "%.0f" % gir, "observacion": o})
            categoria = categoria_observacion(o)
            for causa in (causas[(serie, corte, tipo, categoria)],
                          causas_eps[(serie, corte, tipo, cod, categoria)]):
                causa[0] += 1
                causa[1] += gir
                causa[2] += (ordn - gir) if ordn is not None else 0.0
                causa[3] += 1 if "correo electr" in norm(o) else 0
                causa[4] += 1 if (gir == 0 or con_dif) else 0
            fecha_giro = como_fecha(h.celda(r, "fecha_giro"))
            if fecha_giro:  # solo las hojas que traen la fecha de cada operación
                firmas_hoja.add((nit, cod, round(gir), fecha_giro, como_fecha(h.celda(r, "fecha_proceso"))))
            tot_gir += gir
            tot_ord += ordn or 0.0
            k = (corte, regimen, tipo, cod, nit)
            acc = relaciones.setdefault(k, [0.0, 0.0, 0, 0, 0, tiene_ord])
            acc[0] += ordn or 0.0
            acc[1] += gir
            acc[2] += 1
            acc[3] += 1 if gir == 0 else 0
            acc[4] += 1 if con_dif else 0
            nombres_ips[nit][razon] += 1
            cortes_ips[nit].add((regimen, corte))
            nombres_eps[(regimen, cod)][nom_eps] += 1
            cortes_eps[(regimen, cod)].add(corte)
        if firmas_hoja:
            firmas[(serie, tipo, corte)] = firmas_hoja

        controles.append({
            "serie": serie, "corte": corte, "regimen": regimen, "proceso": tipo,
            "filas_datos": len(datos),
            "filas_descartadas": sum(descartadas.values()),
            "descartadas_detalle": "; ".join("%s: %d" % kv for kv in descartadas.most_common(4)),
            "parejas": len(parejas),
            "parejas_repetidas": sum(1 for n in parejas.values() if n > 1),
            "receptores": len({n for _, n in parejas}),
            "eps": len({e for e, _ in parejas}),
            "valor_ordenado": "%.0f" % tot_ord if tiene_ord else "",
            "valor_girado": "%.0f" % tot_gir,
            "girado_cero": c["girado_cero"], "girado_negativo": c["girado_negativo"],
            "sin_valor_girado": c["sin_valor_girado"],
            "ordenado_distinto_de_girado": c["ordenado_distinto_de_girado"] if tiene_ord else "",
            "suma_diferencias": "%.0f" % dif_total if tiene_ord else "",
            "filas_duplicadas_exactas": sum(n - 1 for n in exactas.values() if n > 1),
            "codigo_corregido": c["codigo_corregido"],
            "codigo_sin_correspondencia": c["codigo_sin_correspondencia"],
            "id_no_8_9": c["id_no_8_9"],
            "id_longitud_distinta_de_9": c["id_longitud_distinta_de_9"],
            "observaciones_principales": " || ".join("%s (%d)" % kv for kv in obs.most_common(4)),
        })

    # Doble conteo entre archivos: la misma operación (prestador, EPS, valor, fechas)
    # publicada en dos cortes consecutivos. Solo donde cada fila trae su fecha de giro.
    repetidas = []
    claves = sorted(firmas)
    for k1, k2 in zip(claves, claves[1:]):
        if k1[:2] == k2[:2]:
            n = len(firmas[k1] & firmas[k2])
            repetidas.append((k2[0], k2[1], k1[2], k2[2], n))

    # ---------------------------------------------------------------- escritura
    def escribir(nombre, filas, campos=None, comprimido=False):
        ruta = os.path.join(SALIDA, nombre)
        campos = campos or list(filas[0].keys())
        abre = (lambda: io.TextIOWrapper(gzip.GzipFile(ruta, "wb", mtime=cfg.GZIP["mtime"]),
                                         encoding="utf-8", newline="")) if comprimido else \
               (lambda: io.open(ruta, "w", encoding="utf-8-sig", newline=""))
        with abre() as fh:
            w = csv.DictWriter(fh, fieldnames=campos, lineterminator="\n")
            w.writeheader()
            w.writerows(filas)

    esquema.sort(key=lambda e: (e["serie"], e["corte"], e["hoja"]))
    escribir("esquema-anexos.csv", esquema)
    escribir("controles-por-hoja.csv", controles)
    escribir("operaciones-con-diferencia.csv", diferencias,
             ["serie", "corte", "proceso", "codigo_eps", "nit", "razon_social",
              "valor_ordenado", "valor_girado", "observacion"])
    escribir("observaciones-por-corte.csv",
             [{"serie": k[0], "corte": k[1], "proceso": k[2], "causa": k[3], "operaciones": v[0],
               "valor_girado": "%.0f" % v[1], "valor_no_girado": "%.0f" % v[2],
               "operaciones_por_correo": v[3], "operaciones_no_giradas": v[4]}
              for k, v in sorted(causas.items())])
    escribir("observaciones-por-eps.csv",
             [{"serie": k[0], "corte": k[1], "proceso": k[2], "codigo_eps": k[3], "causa": k[4],
               "operaciones": v[0], "valor_girado": "%.0f" % v[1], "valor_no_girado": "%.0f" % v[2],
               "operaciones_por_correo": v[3], "operaciones_no_giradas": v[4]}
              for k, v in sorted(causas_eps.items())])
    escribir("eps-por-corte.csv", eps_filas,
             ["serie", "corte", "regimen", "tabla", "codigo_eps", "nombre_eps"]
             + CAMPOS_NUMERICOS_EPS + ["fecha_giro_complemento", "observacion"])

    filas_corr = []
    for (serie, corte, tipo, cod_pub, nom, cod, regla), n in sorted(correcciones.items()):
        filas_corr.append({"serie": serie, "corte": corte, "proceso": tipo,
                           "codigo_publicado": cod_pub, "nombre_publicado": nom,
                           "codigo_asignado": cod, "regla": regla, "operaciones": n})
    escribir("correcciones-codigo-eps.csv", filas_corr,
             ["serie", "corte", "proceso", "codigo_publicado", "nombre_publicado",
              "codigo_asignado", "regla", "operaciones"])

    rel = [{"corte": k[0], "regimen": k[1], "proceso": k[2], "codigo_eps": k[3], "nit": k[4],
            "valor_ordenado": "%.0f" % v[0] if v[5] else "", "valor_girado": "%.0f" % v[1],
            "operaciones": v[2], "operaciones_girado_cero": v[3], "operaciones_con_diferencia": v[4]}
           for k, v in sorted(relaciones.items())]
    escribir("relaciones-giro-directo.csv.gz", rel, comprimido=True)

    prestadores = []
    for nit in sorted(nombres_ips):
        cortes = sorted(cortes_ips[nit])
        prestadores.append({
            "nit": nit, "razon_social": nombres_ips[nit].most_common(1)[0][0],
            "nombres_distintos": len(nombres_ips[nit]),
            "cortes_contributivo": sum(1 for r, _ in cortes if r == "contributivo"),
            "cortes_subsidiado": sum(1 for r, _ in cortes if r == "subsidiado"),
            "primer_corte": min(c for _, c in cortes), "ultimo_corte": max(c for _, c in cortes)})
    escribir("prestadores.csv", prestadores)

    codigos = []
    for (regimen, cod) in sorted(nombres_eps):
        vistos = [n for n, _ in nombres_eps[(regimen, cod)].most_common() if n]
        cortes = sorted(cortes_eps[(regimen, cod)])
        codigos.append({"regimen": regimen, "codigo_eps": cod,
                        "nombre_mas_frecuente": vistos[0] if vistos else "",
                        "nombres_vistos": " | ".join(vistos[:6]),
                        "primer_corte": cortes[0], "ultimo_corte": cortes[-1], "cortes": len(cortes)})
    # Los códigos que solo aparecen en las tablas por EPS también son parte del catálogo.
    en_aristas = {(c["regimen"], c["codigo_eps"]) for c in codigos}
    extra = collections.defaultdict(lambda: [collections.Counter(), set()])
    for f in eps_filas:
        if (f["regimen"], f["codigo_eps"]) not in en_aristas:
            extra[(f["regimen"], f["codigo_eps"])][0][f["nombre_eps"]] += 1
            extra[(f["regimen"], f["codigo_eps"])][1].add(f["corte"])
    for (regimen, cod), (noms, cortes) in sorted(extra.items()):
        cortes = sorted(cortes)
        codigos.append({"regimen": regimen, "codigo_eps": cod,
                        "nombre_mas_frecuente": noms.most_common(1)[0][0],
                        "nombres_vistos": " | ".join(n for n, _ in noms.most_common(6)),
                        "primer_corte": cortes[0], "ultimo_corte": cortes[-1], "cortes": len(cortes)})
    codigos.sort(key=lambda c: (c["regimen"], c["codigo_eps"]))
    escribir("codigos-eps.csv", codigos)

    # Cotejo interno: giro directo por EPS en la certificación del subsidiado frente a la
    # suma de las aristas del mismo corte (ya con los códigos corregidos).
    suma = collections.defaultdict(lambda: [0.0, 0.0, False])
    for k, v in relaciones.items():
        if k[1] == "subsidiado":
            s = suma[(k[0], k[2], k[3])]
            s[0] += v[0]
            s[1] += v[1]
            s[2] = s[2] or bool(v[5])
    cotejo = []
    vistos_cert = set()
    for f in eps_filas:
        if f["tabla"] != "certificacion-eps":
            continue
        for proceso, campo in (("proceso", "giro_directo_proceso"),
                               ("complemento", "giro_directo_complemento")):
            cert = float(f[campo]) if f[campo] else 0.0
            ordn, gir, tiene_ord = suma.get((f["corte"], proceso, f["codigo_eps"]), (0.0, 0.0, False))
            vistos_cert.add((f["corte"], proceso, f["codigo_eps"]))
            if cert == 0 and gir == 0:
                continue
            cotejo.append((f["corte"], f["codigo_eps"], proceso, cert, ordn if tiene_ord else None, gir))
    for (corte, proceso, cod), (ordn, gir, tiene_ord) in suma.items():
        if (corte, proceso, cod) not in vistos_cert and gir:
            cotejo.append((corte, cod, proceso, 0.0, ordn if tiene_ord else None, gir))
    filas_cot = []
    for corte, cod, proceso, cert, ordn, gir in sorted(cotejo):
        if ordn is not None and abs(cert - ordn) <= 1:
            clase = "igual a lo ordenado"
        elif abs(cert - gir) <= 1:
            clase = "igual a lo girado"
        elif min(abs(cert - gir), abs(cert - (ordn if ordn is not None else gir))) < 1000:
            clase = "diferencia menor de $1.000"
        else:
            clase = "no cuadra"
        filas_cot.append({"corte": corte, "codigo_eps": cod, "proceso": proceso,
                          "certificacion": "%.0f" % cert,
                          "suma_ordenado": "" if ordn is None else "%.0f" % ordn,
                          "suma_girado": "%.0f" % gir, "clase": clase})
    escribir("cotejo-certificacion.csv", filas_cot)

    # ---------------------------------------------------------------- resumen
    lineas = []
    p = lineas.append
    fechas = sorted({a["fecha_descarga"] for a in archivos})
    p("Lectura de los anexos del giro directo descargados %s" % (
        "el %s" % fechas[0] if len(fechas) == 1 else "entre el %s y el %s" % (fechas[0], fechas[-1])))
    p("Archivos leídos: %d  ·  hojas: %d" % (len(archivos), len(esquema)))
    for serie in ("contributivo", "subsidiado-ips", "subsidiado-eps"):
        cs = sorted({a["corte"] for a in archivos if a["serie"] == serie})
        p("  %-15s %d cortes (%s a %s)" % (serie, len(cs), cs[0], cs[-1]))
    p("")
    p("Notas de esquema:")
    for e in esquema:
        if e["notas"]:
            p("  %s %s «%s»: %s" % (e["serie"], e["corte"], e["hoja"], e["notas"]))
    p("")
    p("Controles (sumas sobre todas las hojas de aristas):")
    for campo in ("filas_datos", "filas_descartadas", "girado_cero", "girado_negativo",
                  "sin_valor_girado", "ordenado_distinto_de_girado", "filas_duplicadas_exactas",
                  "codigo_corregido", "codigo_sin_correspondencia",
                  "id_no_8_9", "id_longitud_distinta_de_9"):
        p("  %-30s %s" % (campo, sum(int(c[campo] or 0) for c in controles)))
    p("  relaciones (corte, régimen, proceso, EPS, prestador): %d" % len(rel))
    p("  prestadores distintos: %d  ·  códigos de EPS distintos: %d" % (len(prestadores), len(codigos)))
    p("  operaciones con giro en cero u ordenado distinto de girado: %d" % len(diferencias))
    p("  identificaciones agregadas como posible persona natural: %d" % personas_naturales)
    p("")
    p("Códigos de EPS reasignados o sin correspondencia (por corte y hoja):")
    agrup = collections.Counter()
    for f in filas_corr:
        agrup[(f["serie"], f["corte"], f["proceso"], f["regla"], f["codigo_asignado"])] += f["operaciones"]
    for k, n in sorted(agrup.items()):
        p("  %s %s %-11s %-38s -> %-7s %5d operaciones" % (k + (n,)))
    p("")
    p("Causa citada en el campo Observación (todas las hojas de aristas; miles de millones):")
    agr = collections.defaultdict(lambda: [0, 0.0, 0.0, 0, 0])
    for (serie, _, tipo, causa), v in causas.items():
        a = agr[(REGIMEN[serie], tipo, causa)]
        for i in range(5):
            a[i] += v[i]
    for k, v in sorted(agr.items()):
        if k[2] != "(vacía)":
            p("  %-12s %-11s %-38s %6d operaciones · girado %9.1f · no girado %7.2f · por correo %d"
              % (k + (v[0], v[1] / 1e9, v[2] / 1e9, v[3])))
    p("")
    p("Operaciones repetidas entre cortes consecutivos (hojas con fecha por fila):")
    con_rep = [x for x in repetidas if x[4]]
    p("  %d pares de cortes comparados; %d con operaciones repetidas" % (len(repetidas), len(con_rep)))
    for x in con_rep:
        p("  %s %s: %s -> %s, %d operaciones idénticas" % x)
    p("")
    # Identidad de la certificación: lo que se va a girar se reparte entre descuentos,
    # giro directo (proceso y complemento) y giro neto a la EPS.
    descuentos = [c for c in CAMPOS_NUMERICOS_EPS if c.startswith("descuento_")]
    fuera = []
    for f in eps_filas:
        if f["tabla"] != "certificacion-eps" or not f["valor_a_girar"]:
            continue
        partes = sum(float(f[c] or 0) for c in descuentos + ["giro_directo_proceso",
                                                             "giro_directo_complemento", "giro_neto_eps"])
        if abs(float(f["valor_a_girar"]) - partes) > 1:
            fuera.append((f["corte"], f["codigo_eps"], float(f["valor_a_girar"]) - partes))
    certs = sum(1 for f in eps_filas if f["tabla"] == "certificacion-eps")
    p("Identidad de la certificación (valor a girar = descuentos + giro directo + giro neto): "
      "%d filas, %d no cuadran por más de $1" % (certs, len(fuera)))
    for x in fuera[:20]:
        p("  %s %s diferencia %.0f" % x)
    p("")
    p("Cotejo de la certificación del subsidiado con las aristas (por corte, EPS y proceso):")
    clases = collections.Counter((f["proceso"], f["clase"]) for f in filas_cot)
    for k, n in sorted(clases.items()):
        p("  %-11s %-28s %4d" % (k + (n,)))
    for f in filas_cot:
        if f["clase"] == "no cuadra":
            p("  no cuadra: %s %s %-11s certificación %s  ordenado %s  girado %s" % (
                f["corte"], f["codigo_eps"], f["proceso"], f["certificacion"],
                f["suma_ordenado"] or "-", f["suma_girado"]))
    with io.open(os.path.join(SALIDA, "resumen-ingesta.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lineas) + "\n")
    print("\n".join(lineas))


if __name__ == "__main__":
    main()
