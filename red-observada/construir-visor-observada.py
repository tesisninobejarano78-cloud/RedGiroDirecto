# -*- coding: utf-8 -*-
"""
Visor de la red observada del giro directo.

Genera visor-red-observada.html a partir de la plantilla plantilla-visor-observada.html y de las
salidas de:
  metricas-red-observada.py      aristas, métricas por EPS y por prestador
  variables-capa-informacion.py  porcentaje de giro directo, complemento y retenciones
  clasificar-prestadores.py      tipo, naturaleza y departamento del prestador (REPS)

Disposición (fija y reproducible, sin simulación de fuerzas):
  - las EPS en un anillo, agrupadas por comunidad del mes principal y ordenadas por lo girado;
    cada una ocupa un arco proporcional a su nube de prestadores;
  - los prestadores que reciben de una sola EPS, en una nube por fuera de su EPS;
  - los que reciben de varias, por dentro del anillo, en el promedio de las posiciones de sus EPS
    ponderado por lo que cada una le gira (más al centro, más repartido);
  - la ADRES y la Supersalud en el centro, con la capa de información: cada EPS programa su giro
    ante la ADRES, y la Supersalud le comunica giros y retenciones.

El visor es un solo archivo HTML, sin dependencias externas: se abre en cualquier navegador.

Ejecutar:  python construir-visor-observada.py
"""

import hashlib
import importlib.util
import json
import math
import os
import re

import networkx as nx
import numpy as np
import pandas as pd

import configuracion as cfg

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = cfg.SALIDA
PLANTILLA = cfg.PLANTILLA_VISOR
VISOR = cfg.VISOR
MESES_REPS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9,
              "Oct": 10, "Nov": 11, "Dec": 12}
TIPOS = ["ESE (empresa social del Estado)", "IPS pública no ESE", "IPS privada", "IPS mixta",
         "Otra clase del REPS", "Gestor o dispensador farmacéutico", "Sin inscripción en el REPS"]

# Geometría en unidades del lienzo (el visor escala y centra).
R_ANILLO = 340.0
R_HUECO = 78.0
PASO_NUBE = 4.4
HUELGO = 26.0


def fallar(mensaje):
    raise SystemExit("ERROR: " + mensaje)


def modulo(nombre, archivo):
    spec = importlib.util.spec_from_file_location(nombre, os.path.join(AQUI, archivo))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def nombre_mes(corte):
    return cfg.nombre_mes(corte)


def fecha_reps(texto):
    """'Fecha corte REPS: Mar 12 2026  3:11PM' -> '12 de marzo de 2026'."""
    m = re.search(r"([A-Z][a-z]{2}) +(\d{1,2}) +(\d{4})", str(texto))
    if not m:
        fallar("no se reconoce la fecha de corte del REPS: %r" % texto)
    return "%d de %s" % (int(m.group(2)), nombre_mes("%s-%02d" % (m.group(3), MESES_REPS[m.group(1)])))


def azar(clave, i):
    """Número en [0, 1) fijo para una clave: separa puntos que caerían en el mismo sitio."""
    h = hashlib.sha256(("%s|%d" % (clave, i)).encode()).hexdigest()
    return int(h[:8], 16) / 2 ** 32


def forma(f):
    if not f.en_reps:
        return "triangulo"
    return "circulo" if f.naturaleza_juridica == "Pública" else "cuadrado"


def main():
    met = modulo("metricas", "metricas-red-observada.py")
    rel, nombres, _ = met.cargar()
    cortes = [met.PRINCIPAL] + sorted(met.CONTROL, reverse=True)

    aristas = pd.read_csv(os.path.join(SALIDA, "aristas-red-observada.csv.gz"), dtype={"nit": str})
    meps = pd.read_csv(os.path.join(SALIDA, "metricas-eps.csv"))
    mpre = pd.read_csv(os.path.join(SALIDA, "metricas-prestadores.csv.gz"), dtype={"nit": str})
    cla = pd.read_csv(os.path.join(SALIDA, "prestadores-clasificados.csv"), dtype={"nit": str}).set_index("nit")
    var = pd.read_csv(os.path.join(SALIDA, "variables-eps-mes.csv"))
    ret = pd.read_csv(os.path.join(SALIDA, "retenciones-y-destino.csv"))
    obs = pd.read_csv(os.path.join(SALIDA, "observaciones-por-eps.csv"), dtype={"codigo_eps": str})
    ent = pd.read_csv(os.path.join(SALIDA, "eps-entidades.csv"), dtype=str)
    mapa = ent.set_index(["regimen", "codigo_eps"]).entidad

    # ------------------------------------------------ EPS: orden por comunidad del corte principal
    ep = meps[meps.corte == met.PRINCIPAL].set_index("entidad")
    a0 = met.aristas_del_corte(rel, met.PRINCIPAL)
    G0 = met.grafo(a0[a0.girado > 0])
    comunidades0, _ = met.asignar(G0, 0)
    peso = {c_i: sum(ep.girado.get(n[2:], 0) for n in c if n.startswith("E:"))
            for c_i, c in enumerate(comunidades0)}
    orden_com = sorted(peso, key=lambda c: -peso[c])
    lista_eps = []
    for c_i in orden_com:
        miembros = [n[2:] for n in comunidades0[c_i] if n.startswith("E:")]
        lista_eps += sorted(miembros, key=lambda e: -ep.girado.get(e, 0))
    todas = sorted(set(meps.entidad))
    lista_eps += [e for e in todas if e not in lista_eps]
    idx_eps = {e: i for i, e in enumerate(lista_eps)}

    # Arco de cada EPS: proporcional al diámetro de su nube más un huelgo. Se toma el
    # mayor número de prestadores exclusivos en los cuatro cortes, para que el anillo no
    # cambie al pasar de un mes a otro.
    excl_max = meps.groupby("entidad").prestadores_exclusivos.max()
    radio_nube = {e: PASO_NUBE * math.sqrt(max(excl_max.get(e, 0), 1)) for e in lista_eps}
    arco = np.array([2 * radio_nube[e] + HUELGO for e in lista_eps])
    angulos = -math.pi / 2 + 2 * math.pi * (np.cumsum(arco) - arco / 2) / arco.sum()
    pos_eps = {e: (R_ANILLO * math.cos(a), R_ANILLO * math.sin(a)) for e, a in zip(lista_eps, angulos)}
    ang_eps = dict(zip(lista_eps, angulos))

    # ------------------------------------------------ prestadores: catálogo de los cuatro cortes
    nits = sorted(set(aristas.nit))
    idx_pre = {n: i for i, n in enumerate(nits)}
    deptos = sorted(set(cla.departamento.dropna())) + [met.SIN_DEPTO]
    idx_dep = {d: i for i, d in enumerate(deptos)}
    prestadores = []
    for n in nits:
        f = cla.loc[n]
        prestadores.append([
            n, str(f.razon_social), TIPOS.index(f.tipo_prestador), forma(f),
            idx_dep[f.departamento if isinstance(f.departamento, str) else met.SIN_DEPTO],
            f.municipio if isinstance(f.municipio, str) else ""])

    # ------------------------------------------------ información por EPS y corte
    proc = rel[rel.proceso == "proceso"].copy()
    proc["programado"] = proc.valor_ordenado.fillna(proc.valor_girado)
    programado = proc.groupby(["corte", "entidad"]).programado.sum()
    o = obs[(obs.serie == "subsidiado-ips") & (obs.causa == "comunicación de la Supersalud")].copy()
    o["entidad"] = [mapa.get(("subsidiado", c)) for c in o.codigo_eps]
    sns_girado = o[o.proceso == "complemento"].groupby(["corte", "entidad"]).valor_girado.sum()
    sns_retenido = o[o.proceso == "proceso"].groupby(["corte", "entidad"]).valor_no_girado.sum()
    pct = var.set_index(["corte", "entidad", "regimen"])
    ret["entidad"] = ret.entidad.fillna("")
    motivo = ret.groupby(["corte", "entidad"]).agg(retenido=("retenido", "sum"), motivo=("motivo", "first"))

    datos_cortes = {}
    for corte in cortes:
        ar = aristas[aristas.corte == corte]
        me = meps[meps.corte == corte].set_index("entidad")
        mp = mpre[mpre.corte == corte].set_index("nit")
        a = met.aristas_del_corte(rel, corte)
        G = met.grafo(a[a.girado > 0])
        cs, _ = met.asignar(G, 0)
        grupo = {}
        for c in cs:
            miembros = sorted((n[2:] for n in c if n.startswith("E:")), key=lambda e: idx_eps[e])
            for e in miembros:
                grupo[e] = [idx_eps[x] for x in miembros if x != e]

        # posiciones de los prestadores de este corte
        pos = {}
        excl = ar[ar.eps_del_prestador == 1].sort_values(["entidad", "girado"], ascending=[True, False])
        for e, g in excl.groupby("entidad"):
            ex, ey = pos_eps[e]
            ux, uy = math.cos(ang_eps[e]), math.sin(ang_eps[e])
            cx, cy = ex + ux * (radio_nube[e] + 22), ey + uy * (radio_nube[e] + 22)
            for k, nit in enumerate(g.nit):
                r = PASO_NUBE * math.sqrt(k + 0.5)
                t = k * 2.399963229728653  # ángulo áureo
                pos[nit] = (cx + r * math.cos(t), cy + r * math.sin(t))
        comp = ar[ar.eps_del_prestador > 1]
        for nit, g in comp.groupby("nit"):
            w = g.girado.values / g.girado.sum()
            x = sum(wi * pos_eps[e][0] for wi, e in zip(w, g.entidad))
            y = sum(wi * pos_eps[e][1] for wi, e in zip(w, g.entidad))
            r = math.hypot(x, y)
            ang = math.atan2(y, x) if r > 1e-9 else 2 * math.pi * azar(nit, 0)
            r2 = R_HUECO + (R_ANILLO - 24 - R_HUECO) * min(r / R_ANILLO, 1.0)
            r2 += (azar(nit, 1) - 0.5) * 10
            ang += (azar(nit, 2) - 0.5) * 9 / max(r2, 1)
            pos[nit] = (r2 * math.cos(ang), r2 * math.sin(ang))

        filas_pre = []
        for nit in sorted(pos, key=lambda n: idx_pre[n]):
            f = mp.loc[nit]
            filas_pre.append([idx_pre[nit], round(pos[nit][0], 1), round(pos[nit][1], 1),
                              round(float(f.girado)), int(f.eps), round(float(f.parte_eps_principal_pct), 1),
                              round(float(f.intermediacion), 6)])
        filas_ar = [[idx_eps[e], idx_pre[n], round(float(w))]
                    for e, n, w in zip(ar.entidad, ar.nit, ar.girado)]

        filas_eps = []
        for e in lista_eps:
            if e not in me.index:
                continue
            f = me.loc[e]

            def pct_de(regimen, campo="pct_giro_directo"):
                k = (corte, e, regimen)
                if k not in pct.index:
                    return None
                v = pct.loc[k][campo]
                return None if pd.isna(v) else round(float(v), 2)

            mot = motivo.loc[(corte, e)] if (corte, e) in motivo.index else None
            filas_eps.append({
                "i": idx_eps[e], "girado": round(float(f.girado)), "participacion": round(float(f.participacion_pct), 2),
                "prestadores": int(f.prestadores), "exclusivos": int(f.prestadores_exclusivos),
                "dependientes": int(f.prestadores_dependientes),
                "intermediacion": round(float(f.intermediacion), 4),
                "eps_comunes": int(f.eps_con_prestadores_comunes),
                "contributivo": round(float(f.girado_contributivo)), "subsidiado": round(float(f.girado_subsidiado)),
                "complemento": round(float(f.girado_complemento)),
                "pct_contributivo": pct_de("contributivo"), "pct_subsidiado": pct_de("subsidiado"),
                "pct_subsidiado_proceso": pct_de("subsidiado", "pct_proceso"),
                "programado": round(float(programado.get((corte, e), 0))),
                "sns_girado": round(float(sns_girado.get((corte, e), 0))),
                "sns_retenido": round(float(sns_retenido.get((corte, e), 0))),
                "retenido": round(float(mot.retenido)) if mot is not None else 0,
                "motivo_retencion": str(mot.motivo) if mot is not None else "",
                "grupo": grupo.get(e, []),
            })
        red = {
            "eps": len(me), "prestadores": len(filas_pre), "aristas": len(filas_ar),
            "girado": round(float(ar.girado.sum())),
            "una_eps_pct": round(100 * float((mp.eps == 1).mean()), 1),
            "mayoritaria_pct": round(100 * float((mp.parte_eps_principal_pct >= 50).mean()), 1),
            "comunidades": sum(1 for c in cs if any(n.startswith("E:") for n in c)),
            "sns_girado": round(float(sns_girado.xs(corte, level=0).sum()) if corte in sns_girado.index.get_level_values(0) else 0),
            "sns_retenido": round(float(sns_retenido.xs(corte, level=0).sum()) if corte in sns_retenido.index.get_level_values(0) else 0),
        }
        datos_cortes[corte] = {"nombre": nombre_mes(corte), "eps": filas_eps, "prestadores": filas_pre,
                               "aristas": filas_ar, "red": red}

    meta = {
        "titulo": "Red observada del giro directo",
        "version": "Anexos de Lupa al Giro (ADRES) y REPS (MinSalud, corte del %s)"
                   % fecha_reps(cla.fecha_corte_reps.dropna().iloc[0]),
        "principal": met.PRINCIPAL,
        "cortes": cortes,
        "nota_principal": "Fotografía principal",
        "nota_control": "Mes de control",
        "fuentes": ("Giro directo de la UPC de los dos regímenes, por EPS y prestador, según los anexos de "
                    "Lupa al Giro de la ADRES. Tipo, naturaleza y departamento del prestador según el REPS "
                    "del Ministerio de Salud; los receptores que no figuran en él se marcan aparte."),
    }
    def rotulo_eps(e):
        """El nombre de la EPS va por fuera de su nube, en la dirección del radio."""
        a = ang_eps[e]
        d = R_ANILLO + 2 * radio_nube[e] + 22 + 12
        c = math.cos(a)
        return {"lx": round(d * c, 1), "ly": round(d * math.sin(a), 1),
                "ancla": "left" if c > 0.3 else ("right" if c < -0.3 else "center")}

    datos = {
        "meta": meta,
        "eps": [dict({"id": e, "nombre": str(nombres.get(e, e)), "x": round(pos_eps[e][0], 1),
                      "y": round(pos_eps[e][1], 1)}, **rotulo_eps(e)) for e in lista_eps],
        "tipos": TIPOS,
        "departamentos": deptos,
        "prestadores": prestadores,
        "cortes": datos_cortes,
    }
    carga = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    with open(PLANTILLA, encoding="utf-8") as f:
        plantilla = f.read()
    if "/*__DATOS__*/null" not in plantilla:
        fallar("la plantilla del visor no tiene el marcador de datos")
    with open(VISOR, "w", encoding="utf-8", newline="\n") as f:
        f.write(plantilla.replace("/*__DATOS__*/null", carga))
    print("Visor: %s (%.1f MB) · %d EPS · %d prestadores · cortes %s" % (
        os.path.basename(VISOR), os.path.getsize(VISOR) / 1e6, len(lista_eps), len(nits), ", ".join(cortes)))
    for corte in cortes:
        r = datos_cortes[corte]["red"]
        print("  %s: %d prestadores, %d aristas, %d comunidades" % (corte, r["prestadores"], r["aristas"],
                                                                   r["comunidades"]))


if __name__ == "__main__":
    main()
