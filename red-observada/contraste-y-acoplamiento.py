# -*- coding: utf-8 -*-
"""
Comparación de la red observada con la red normada y acoplamiento entre las capas.

La comparación se limita a la parte común de las dos redes (ADRES, EPS y prestadores, con la
Supersalud en la capa de información) y usa los atributos que ya están en el proyecto (REPS e
inventario de actores). Dos niveles:

  1. vínculo por vínculo: la red observada se agrupa en las clases de la red normada y se compara
     qué vínculos normados aparecen en los datos, cuánto dinero pasa por cada uno y qué dinero
     llega a clases que la red normada no conecta;
  2. la regla, EPS por EPS, con la Ley 1122 de 2007 (texto vigente en la Secretaría del Senado y
     en la Función Pública):
       - art. 16: las EPS del subsidiado contratarán como mínimo el 60 % del gasto en salud con
         ESE habilitadas en el municipio de residencia del afiliado, si allí hay capacidad
         resolutiva, sujeto a calidad, oferta, gestión y tarifas. Se mide la parte del giro
         directo del subsidiado que llega a ESE. Es una comparación orientativa: el giro directo
         no es el gasto contratado, no se conoce la residencia de los afiliados ni la capacidad
         resolutiva, y la Ley 1438 de 2011 (art. 68) da trato de ESE a ciertas fundaciones que el
         REPS no distingue;
       - art. 15, parágrafo: las EPS del contributivo garantizarán IPS públicas en sus redes. Se
         cuenta cuántas IPS públicas reciben giro del contributivo de cada EPS (si las hay, están
         en la red; si no, no prueba que falten, porque la EPS también paga por fuera del giro);
       - art. 15, límite del 30 % con IPS propias: no se puede medir, porque la propiedad de las
         IPS no es pública en forma estructurada;
     la regla del 90 % del giro directo se mide en variables-capa-informacion.py.

Acoplamiento entre capas: qué parte de la red de recursos depende, en el mes, de EPS cuyo giro
quedó condicionado por la capa de información (comunicaciones de la Supersalud que dirigen o
excluyen giro; retenciones del giro neto por el porcentaje o por el cargue tardío del archivo), y
qué les pasó a los prestadores de las aristas ordenadas y no giradas.

Anomalías: tabla única con los prestadores muy por encima de la curva fuerza–grado, las aristas
ordenadas y no giradas del mes y los cambios de cartera fuera de lo usual entre el mes anterior y
el principal. Una anomalía señala dónde mirar; no es una irregularidad.

Entradas: aristas-normadas.csv y salida/nodos-red-normada.csv de la red normada, el inventario de
actores, salida/*.csv y salida/teoria-redes/fuerza-grado-residuos.csv.gz; las aristas sin giro se
reconstruyen con las funciones de metricas-red-observada.py.
Salidas en salida/contraste/ (la lista está en `main`).
Ejecutar:  python contraste-y-acoplamiento.py      (después de teoria-redes-observada.py)
"""

import importlib.util
import io
import os
import re
import sys

import networkx as nx
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import configuracion as cfg

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = cfg.SALIDA
TEORIA = os.path.join(SALIDA, "teoria-redes")
DESTINO = os.path.join(SALIDA, "contraste")
INVENTARIO = cfg.INVENTARIO
PRINCIPAL = cfg.PRINCIPAL
ANTERIOR = cfg.mes_anterior(PRINCIPAL)
CORTES = [PRINCIPAL] + list(cfg.CONTROL)
MES = cfg.nombre_mes(PRINCIPAL)
MINIMO_ESE = 60.0
MAYORIA = 0.5
SEMILLA = 20261104

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CLASES = {  # clase de la red normada → vínculo normado de recursos que la alcanza
    "ASC-010": ("IPS (prestadores inscritos en el REPS)", "R04"),
    "ASC-071": ("Droguerías, gestores farmacéuticos y canal de dispensación", "R07"),
    "ASC-067": ("Audifarma", "R08"),
    "ASC-068": ("Disfarma", "R09"),
    "ASC-069": ("Helpharma", "R10"),
    "ASC-047": ("Cajas de compensación familiar", "R11"),
    "ASC-070": ("Importadores y distribuidores mayoristas de medicamentos y tecnologías", "R25"),
    "ASC-065": ("Industria farmacéutica y de dispositivos médicos", "R26"),
    "ASC-253": ("Proveedores de servicios y tecnologías de salud sin inscripción en el REPS", "R27"),
}
TIPOS_REPS = {"ESE (empresa social del Estado)", "IPS privada", "IPS pública no ESE", "IPS mixta", "Otra clase del REPS"}
PUBLICOS = {"ESE (empresa social del Estado)", "IPS pública no ESE"}
CCF = re.compile(r"^CAJA (DE COMPENSACI|COLOMBIANA DE SUBSIDIO)")


def cargar_metricas():
    spec = importlib.util.spec_from_file_location("metricas", os.path.join(AQUI, "metricas-red-observada.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- red normada


def centralidad_normada():
    ar = pd.read_csv(cfg.ARISTAS_NORMADAS)
    nodos = pd.read_csv(cfg.NODOS_NORMADA)
    nodos = nodos[nodos.en_red.astype(str) == "True"].set_index("id")
    filas = []
    for capa in ("recursos", "informacion", "las dos capas"):
        sub = ar if capa == "las dos capas" else ar[ar.capa == capa]
        MG = nx.MultiDiGraph()
        MG.add_nodes_from(nodos.index)
        MG.add_edges_from(zip(sub.origen, sub.destino))
        D = nx.DiGraph(MG)
        bc = nx.betweenness_centrality(D, normalized=True)
        for n in nodos.index:
            filas.append({"capa": capa, "id": n, "actor": nodos.sigla[n], "vinculos_salida": MG.out_degree(n),
                          "vinculos_entrada": MG.in_degree(n), "vinculos": MG.degree(n),
                          "intermediacion_dirigida": bc[n], "alcance_aguas_abajo": len(nx.descendants(D, n))})
    df = pd.DataFrame(filas)
    return df, ar


def clase_de(p):
    if p.id_inventario in ("ASC-067", "ASC-068", "ASC-069"):
        return p.id_inventario
    if p.parte_de in ("ASC-071", "ASC-047", "ASC-070", "ASC-065"):
        return p.parte_de
    if isinstance(p.razon_social, str) and CCF.match(p.razon_social):
        return "ASC-047"
    if p.tipo_prestador in TIPOS_REPS:
        return "ASC-010"
    if p.tipo_prestador == "Gestor o dispensador farmacéutico":
        return "ASC-071"
    return "ASC-253"


def contraste_clases(a, pre, ar):
    filas = []
    for c in CORTES:
        f = a[a.corte == c].merge(pre[["clase"]], left_on="nit", right_index=True, how="left")
        tot = f.girado.sum()
        for clase, g in f.groupby("clase"):
            nombre, vinc = CLASES[clase]
            filas.append({"corte": c, "clase": clase, "clase_nombre": nombre, "vinculo_normado": vinc or "sin vínculo en la red normada",
                          "receptores": g.nit.nunique(), "aristas": len(g), "eps_que_giran": g.entidad.nunique(),
                          "girado": g.girado.sum(), "girado_pct": 100 * g.girado.sum() / tot})
    clases = pd.DataFrame(filas)
    # vínculos normados de la parte común (ADRES, EPS, prestadores; Supersalud en información)
    comunes = {"ASC-007", "ASC-009", "ASC-010", "ASC-011", "ASC-047", "ASC-065", "ASC-067", "ASC-068", "ASC-069",
               "ASC-070", "ASC-071", "ASC-253"}
    sub = ar[ar.origen.isin(comunes) & ar.destino.isin(comunes)].copy()
    s = clases[clases.corte == PRINCIPAL].set_index("vinculo_normado")
    sub["girado_en_el_mes"] = [s.girado.get(i, np.nan) if cap == "recursos" else np.nan for i, cap in zip(sub.id, sub.capa)]
    sub["receptores_en_el_mes"] = [s.receptores.get(i, np.nan) if cap == "recursos" else np.nan for i, cap in zip(sub.id, sub.capa)]
    vinc = sub[["id", "capa", "tipo", "origen", "destino", "observabilidad", "girado_en_el_mes", "receptores_en_el_mes"]]
    # índice de Jaccard en recursos (parte común; solo el giro de la UPC)
    norm_r = {"R04", "R07", "R08", "R09", "R10", "R11", "R25", "R26", "R27"}
    obs = set(clases[(clases.corte == PRINCIPAL) & (clases.girado > 0)].clase)
    obs_vinc = {CLASES[x][1] or "sin-vinculo:" + x for x in obs}
    jac = len(norm_r & obs_vinc) / len(norm_r | obs_vinc)
    sin = clases[(clases.corte == PRINCIPAL) & (clases.vinculo_normado == "sin vínculo en la red normada")]
    res = {"vinculos_normados_de_recursos_en_la_parte_comun": len(norm_r),
           "de_ellos_con_giro_en_el_mes": len(norm_r & obs_vinc),
           "clases_con_giro_sin_vinculo_normado": len(obs_vinc - norm_r),
           "jaccard_vinculos_recursos": jac,
           "girado_a_clases_sin_vinculo_normado_pct": float(sin.girado_pct.sum()),
           "vinculos_normados_de_informacion_en_la_parte_comun": int((sub.capa == "informacion").sum()),
           "de_ellos_observables": int(((sub.capa == "informacion") & (sub.observabilidad == "observable")).sum()),
           "de_ellos_en_parte": int(((sub.capa == "informacion") & (sub.observabilidad == "parcial")).sum())}
    return clases, vinc, res


# ---------------------------------------------------------------- la regla, EPS por EPS


def reglas_ley_1122(a, pre, nombres):
    sub, con = [], []
    for c in CORTES:
        f = a[a.corte == c].merge(pre[["tipo_prestador"]], left_on="nit", right_index=True, how="left")
        for e, g in f.groupby("entidad"):
            s = g[g.girado_subsidiado > 0]
            if len(s):
                tot = s.girado_subsidiado.sum()
                ese = s[s.tipo_prestador == "ESE (empresa social del Estado)"].girado_subsidiado.sum()
                pub = s[s.tipo_prestador.isin(PUBLICOS)].girado_subsidiado.sum()
                sub.append({"corte": c, "entidad": e, "nombre": nombres.get(e, e), "girado_subsidiado": tot,
                            "a_ese_pct": 100 * ese / tot, "a_publicos_pct": 100 * pub / tot,
                            "ese_que_reciben": s[s.tipo_prestador == "ESE (empresa social del Estado)"].nit.nunique(),
                            "prestadores": s.nit.nunique(), "por_debajo_del_60": 100 * ese / tot < MINIMO_ESE})
            k = g[g.girado_contributivo > 0]
            if len(k):
                tot = k.girado_contributivo.sum()
                pub = k[k.tipo_prestador.isin(PUBLICOS)]
                con.append({"corte": c, "entidad": e, "nombre": nombres.get(e, e), "girado_contributivo": tot,
                            "ips_publicas_que_reciben": pub.nit.nunique(), "a_publicos_pct": 100 * pub.girado_contributivo.sum() / tot,
                            "prestadores": k.nit.nunique()})
    return pd.DataFrame(sub), pd.DataFrame(con)


# ---------------------------------------------------------------- acoplamiento entre capas


def acoplamiento(a, var, nombres):
    v = var.copy()
    for col in ("complemento_por_comunicación de la Supersalud", "complemento_por_comunicación del agente interventor",
                "proceso_no_girado_por_comunicación de la Supersalud", "retenido"):
        v[col] = v[col].fillna(0)
    v = v.groupby(["corte", "entidad"], as_index=False).agg(
        dirigido_supersalud=("complemento_por_comunicación de la Supersalud", "sum"),
        dirigido_interventor=("complemento_por_comunicación del agente interventor", "sum"),
        excluido_supersalud=("proceso_no_girado_por_comunicación de la Supersalud", "sum"),
        retenido=("retenido", "sum"))
    filas, expo = [], []
    for c in CORTES:
        f = a[a.corte == c]
        s_pre = f.groupby("nit").girado.sum()
        prin = f.sort_values(["girado", "entidad"], ascending=[False, True]).drop_duplicates("nit").set_index("nit")
        parte = prin.girado / s_pre.reindex(prin.index)
        dep = prin[parte >= MAYORIA]
        vc = v[v.corte == c].set_index("entidad")
        for e, g in f.groupby("entidad"):
            d = vc.loc[e] if e in vc.index else pd.Series(0, index=["dirigido_supersalud", "dirigido_interventor", "excluido_supersalud", "retenido"])
            giro = g.girado.sum()
            filas.append({"corte": c, "entidad": e, "nombre": nombres.get(e, e), "girado": giro,
                          "dirigido_o_excluido_por_supersalud_o_interventor": d.dirigido_supersalud + d.dirigido_interventor + d.excluido_supersalud,
                          "condicionado_pct_del_giro": 100 * (d.dirigido_supersalud + d.dirigido_interventor + d.excluido_supersalud) / giro,
                          "retenido_giro_neto": d.retenido,
                          "condicionada_por_supersalud": (d.dirigido_supersalud + d.dirigido_interventor + d.excluido_supersalud) > 0,
                          "con_retencion": d.retenido > 0,
                          "prestadores": g.nit.nunique(), "prestadores_dependientes": int((dep.entidad == e).sum())})
        t = pd.DataFrame([x for x in filas if x["corte"] == c]).set_index("entidad")
        k = f.groupby("nit").entidad.nunique()
        exclusivos = set(k.index[k == 1])
        for criterio in ("condicionada_por_supersalud", "con_retencion"):
            eps_c = set(t.index[t[criterio]])
            d = dep[dep.entidad.isin(eps_c)]
            expo.append({"corte": c, "criterio": criterio, "eps": "; ".join(sorted(nombres.get(e, e) for e in eps_c)),
                         "eps_n": len(eps_c), "prestadores_dependientes": len(d),
                         "prestadores_dependientes_pct": 100 * len(d) / len(s_pre),
                         "giro_de_esos_prestadores_pct": 100 * s_pre.reindex(d.index).sum() / s_pre.sum(),
                         "prestadores_exclusivos": int(f[f.nit.isin(exclusivos) & f.entidad.isin(eps_c)].nit.nunique())})
    tabla = pd.DataFrame(filas)
    # asociación EPS por EPS (descriptiva: 25 EPS), con prueba de permutación
    rng = np.random.default_rng(SEMILLA)
    asoc = []
    for c in CORTES:
        t = tabla[tabla.corte == c]
        for x, y in (("condicionado_pct_del_giro", "prestadores_dependientes"),
                     ("retenido_giro_neto", "prestadores_dependientes")):
            xx, yy = t[x].values, t[y].values
            ok = ~np.isnan(yy)
            eps_con = int((xx[ok] > 0).sum())
            if np.ptp(xx[ok]) == 0 or np.ptp(yy[ok]) == 0:
                rho, p = np.nan, np.nan   # sin variación: no hay correlación que medir
            else:
                rho = spearmanr(xx[ok], yy[ok]).statistic
                perm = [spearmanr(rng.permutation(xx[ok]), yy[ok]).statistic for _ in range(5000)]
                p = (1 + sum(abs(q) >= abs(rho) - 1e-12 for q in perm)) / 5001
            asoc.append({"corte": c, "variable_informacion": x, "variable_red": y, "eps": int(ok.sum()),
                         "eps_con_valor_positivo": eps_con, "spearman": rho, "p_permutacion_dos_colas": p})
    return tabla, pd.DataFrame(expo), pd.DataFrame(asoc)


def aristas_sin_giro(met, a, pre, nombres):
    rel, _, _ = met.cargar()
    c = met.aristas_del_corte(rel, PRINCIPAL)
    sg = c[(c.girado <= 0) & (c.ordenado > 0)].copy()
    ant = a[a.corte == ANTERIOR]
    ant_tot = ant.groupby("nit").girado.sum()
    del_mes = a[a.corte == PRINCIPAL]
    mes_tot = del_mes.groupby("nit").girado.sum()
    mes_k = del_mes.groupby("nit").entidad.nunique()
    filas = []
    for _, r in sg.iterrows():
        prev = ant[(ant.entidad == r.entidad) & (ant.nit == r.nit)].girado.sum()
        filas.append({"entidad": r.entidad, "nombre_eps": nombres.get(r.entidad, r.entidad), "nit": r.nit,
                      "razon_social": pre.razon_social.get(r.nit, ""), "tipo_prestador": pre.tipo_prestador.get(r.nit, ""),
                      "departamento": pre.departamento.get(r.nit, ""), "ordenado_no_girado": r.ordenado,
                      "eps_con_giro_en_el_mes": int(mes_k.get(r.nit, 0)),
                      "recibido_en_el_mes_de_otras_eps": float(mes_tot.get(r.nit, 0)),
                      "parte_de_esa_eps_el_mes_anterior_pct": 100 * prev / ant_tot[r.nit] if r.nit in ant_tot.index and ant_tot[r.nit] > 0 else np.nan})
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- anomalías


def anomalias(a, pre, nombres, sg):
    filas = []
    res = pd.read_csv(os.path.join(TEORIA, "fuerza-grado-residuos.csv.gz"), dtype={"nit": str})
    del_mes = a[a.corte == PRINCIPAL]
    prin = del_mes.sort_values("girado", ascending=False).drop_duplicates("nit").set_index("nit").entidad
    for _, r in res[res.z_modificado.abs() > 3.5].sort_values("z_modificado", ascending=False).iterrows():
        filas.append({"tipo": "Receptor muy por encima de la curva fuerza–grado (z modificado > 3,5)",
                      "elemento": pre.razon_social.get(r.nit, r.nit),
                      "medida": "z modificado del residuo de log s(k), " + MES, "valor": r.z_modificado,
                      "lectura": "%d EPS; %.2f %% del giro del mes; %.0f %% de %s" % (r.grado, r.participacion_pct, 100 * r.parte_eps_principal,
                                                                                    nombres.get(prin.get(r.nit), prin.get(r.nit)))})
    for _, r in sg.iterrows():
        filas.append({"tipo": "Giro ordenado y no girado (%s)" % MES, "elemento": "%s → %s" % (r.nombre_eps, r.razon_social),
                      "medida": "ordenado no girado (pesos)", "valor": r.ordenado_no_girado,
                      "lectura": "recibe giro por cuenta de %d EPS en el mes" % r.eps_con_giro_en_el_mes})
    # rotación de la cartera de cada EPS entre el mes anterior y el principal
    ant = a[a.corte == ANTERIOR]
    rot = []
    for e in sorted(set(del_mes.entidad) & set(ant.entidad)):
        x, y = set(ant[ant.entidad == e].nit), set(del_mes[del_mes.entidad == e].nit)
        rot.append({"entidad": e, "jaccard": len(x & y) / len(x | y), "nuevas": len(y - x), "perdidas": len(x - y)})
    rot = pd.DataFrame(rot)
    med = rot.jaccard.median()
    mad = np.median(np.abs(rot.jaccard - med))
    rot["z_modificado"] = 0.6745 * (rot.jaccard - med) / mad
    for _, r in rot[rot.z_modificado.abs() > 3.5].iterrows():
        filas.append({"tipo": "Cambio de cartera frente al mes anterior fuera de lo usual (z modificado > 3,5)",
                      "elemento": nombres.get(r.entidad, r.entidad), "medida": "Jaccard de su cartera",
                      "valor": r.jaccard, "lectura": "%d prestadores nuevos, %d que salen" % (r.nuevas, r.perdidas)})
    return pd.DataFrame(filas), rot


# ---------------------------------------------------------------- principal


def main():
    os.makedirs(DESTINO, exist_ok=True)
    met = cargar_metricas()
    a = pd.read_csv(os.path.join(SALIDA, "aristas-red-observada.csv.gz"), dtype={"nit": str})
    a = a[a.corte.isin(CORTES) & (a.girado > 0)]
    ent = pd.read_csv(os.path.join(SALIDA, "eps-entidades.csv"), dtype=str)
    nombres = ent.drop_duplicates("entidad").set_index("entidad").nombre_entidad
    pre = pd.read_csv(os.path.join(SALIDA, "prestadores-clasificados.csv"), dtype=str).set_index("nit")
    inv = pd.read_csv(INVENTARIO, dtype=str).set_index("id")
    pre["parte_de"] = inv.parte_de.reindex(pre.id_inventario).values
    pre["clase"] = [clase_de(p) for p in pre.itertuples()]
    var = pd.read_csv(os.path.join(SALIDA, "variables-eps-mes.csv"))

    cn, ar = centralidad_normada()
    clases, vinc, jac = contraste_clases(a, pre, ar)
    rsub, rcon = reglas_ley_1122(a, pre, nombres)
    acop, expo, asoc = acoplamiento(a, var, nombres)
    sg = aristas_sin_giro(met, a, pre, nombres)
    anom, rot = anomalias(a, pre, nombres, sg)

    tablas = {"red-normada-centralidad.csv": cn, "clases-observadas.csv": clases, "vinculos-parte-comun.csv": vinc,
              "regla-ese-subsidiado.csv": rsub, "regla-ips-publicas-contributivo.csv": rcon,
              "acoplamiento-eps.csv": acop, "acoplamiento-exposicion.csv": expo, "acoplamiento-asociacion.csv": asoc,
              "aristas-sin-giro.csv": sg, "rotacion-carteras.csv": rot, "anomalias.csv": anom}
    for n, df in tablas.items():
        df.to_csv(os.path.join(DESTINO, n), index=False, encoding="utf-8-sig", lineterminator="\n")

    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 80)
    pd.set_option("display.max_columns", 30)
    fmt = lambda x: "%.4g" % x
    L = ["Comparación con la red normada y acoplamiento entre capas — mes principal %s" % PRINCIPAL, ""]
    L += ["== Red normada: centralidad por capa (%d actores con vínculos)" % len(cn[cn.capa == "las dos capas"]),
          cn.sort_values(["capa", "vinculos"], ascending=[True, False]).groupby("capa").head(6).to_string(index=False, float_format=fmt), ""]
    L += ["== Nivel 1: clases de la red normada en la red observada", clases[clases.corte == PRINCIPAL].sort_values("girado", ascending=False).to_string(index=False, float_format=fmt), ""]
    L += ["== Nivel 1: vínculos normados de la parte común", vinc.to_string(index=False, float_format=fmt), "",
          "== Nivel 1: resumen", pd.Series(jac).to_string(float_format=fmt), ""]
    s = rsub[rsub.corte == PRINCIPAL].sort_values("girado_subsidiado", ascending=False)
    L += ["== Nivel 2: Ley 1122, art. 16 — parte del giro directo del subsidiado que llega a ESE (orientativo)",
          s.to_string(index=False, float_format=fmt),
          "EPS por debajo del 60 %% por mes: %s" % rsub.groupby("corte").por_debajo_del_60.agg(["sum", "size"]).to_dict("index"),
          "Parte de todo el giro del subsidiado que llega a ESE, por mes: %s" % {c: round(100 * float((g.a_ese_pct * g.girado_subsidiado).sum() / g.girado_subsidiado.sum()) / 100, 2) for c, g in rsub.groupby("corte")}, ""]
    L += ["== Nivel 2: Ley 1122, art. 15, parágrafo — IPS públicas con giro del contributivo de cada EPS",
          rcon[rcon.corte == PRINCIPAL].sort_values("girado_contributivo", ascending=False).to_string(index=False, float_format=fmt), ""]
    L += ["== Acoplamiento: EPS condicionadas por la capa de información (corte principal)",
          acop[(acop.corte == PRINCIPAL) & (acop.condicionada_por_supersalud | acop.con_retencion)].to_string(index=False, float_format=fmt), "",
          "== Acoplamiento: exposición de los prestadores", expo.to_string(index=False, float_format=fmt), "",
          "== Acoplamiento: asociación EPS por EPS (Spearman, permutación)", asoc.to_string(index=False, float_format=fmt), "",
          "== Aristas ordenadas y no giradas (%s)" % MES, sg.to_string(index=False, float_format=fmt), "",
          "== Anomalías", anom.to_string(index=False, float_format=fmt), ""]
    texto = "\n".join(L) + "\n"
    with io.open(os.path.join(DESTINO, "resumen-contraste-acoplamiento.txt"), "w", encoding="utf-8",
                 newline="\n") as fh:
        fh.write(texto)
    print(texto)


if __name__ == "__main__":
    main()
