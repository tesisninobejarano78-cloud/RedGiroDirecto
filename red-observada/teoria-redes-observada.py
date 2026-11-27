# -*- coding: utf-8 -*-
"""
Red observada del giro directo: análisis con teoría de redes.

Completa las métricas de metricas-red-observada.py con:

  A. centralidad de cada EPS y de cada prestador (grado, fuerza, intermediación, cercanía y grado
     medio de los vecinos), sus correlaciones y las distancias en la red;
  B. distribuciones: concentración (Gini, CR4, CR20, índice de Herfindahl), curvas de Lorenz,
     heterogeneidad del grado, relación fuerza–grado s(k) ∝ k^β (Barrat et al., 2004) con su
     intervalo bootstrap, dependencia de una sola EPS y asortatividad;
  C. comunidades: modularidad bipartita de Barber, binaria y ponderada, Louvain estándar y la
     partición por departamento, y cuánto coinciden con el departamento del prestador (NMI y ARI,
     con una prueba de permutación);
  D. estabilidad de las aristas entre meses.

Todo es descriptivo. La red es la bipartita EPS (entidad) → prestador (NIT), con el peso de lo
girado en el mes; se analiza el mes PRINCIPAL de configuracion.py y, como control, los meses de
CONTROL.

Entradas (salida/): aristas-red-observada.csv.gz, prestadores-clasificados.csv,
eps-entidades.csv, metricas-eps.csv y metricas-prestadores.csv.gz (la intermediación ya calculada
se reutiliza; aquí se comprueba que el grado y la fuerza coinciden).

Salidas en salida/teoria-redes/ (la lista está en `main`).
Ejecutar:  python teoria-redes-observada.py      (después de verificar-metodos.py)
"""

import io
import os
import sys

import networkx as nx
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import configuracion as cfg
import redes_metodos as rm

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SALIDA = cfg.SALIDA
DESTINO = os.path.join(SALIDA, "teoria-redes")
PRINCIPAL = cfg.PRINCIPAL
CONTROL = list(cfg.CONTROL)
CORTES = [PRINCIPAL] + CONTROL
SIN_DEPTO = "Sin departamento (no está en el REPS)"

ARRANQUES = 30               # arranques al azar del optimizador de modularidad binaria
ARRANQUES_DESCRIPCION = 300  # arranques del optimizador de modularidad ponderada
PERMUTACIONES = 1000         # para comparar las comunidades con los departamentos
BOOTSTRAP = 2000             # remuestreos del intervalo del exponente fuerza–grado
SEMILLA = 20261104


# ---------------------------------------------------------------- datos


def cargar():
    a = pd.read_csv(os.path.join(SALIDA, "aristas-red-observada.csv.gz"), dtype={"nit": str})
    ent = pd.read_csv(os.path.join(SALIDA, "eps-entidades.csv"), dtype=str)
    nombres = ent.drop_duplicates("entidad").set_index("entidad").nombre_entidad
    pre = pd.read_csv(os.path.join(SALIDA, "prestadores-clasificados.csv"), dtype=str).set_index("nit")
    pre["departamento"] = pre.departamento.fillna(SIN_DEPTO)
    meps = pd.read_csv(os.path.join(SALIDA, "metricas-eps.csv"))
    mpre = pd.read_csv(os.path.join(SALIDA, "metricas-prestadores.csv.gz"), dtype={"nit": str})
    return a, nombres, pre, meps, mpre


def red_del_corte(a, corte, pre):
    f = a[(a.corte == corte) & (a.girado > 0)]
    eps = sorted(f.entidad.unique())
    nits = sorted(f.nit.unique())
    ie = {e: i for i, e in enumerate(eps)}
    ip = {p: j for j, p in enumerate(nits)}
    M, W = rm.biadyacencia(f.entidad.map(ie).values, f.nit.map(ip).values, len(eps), len(nits),
                           f.girado.values)
    depto = pre.departamento.reindex(nits).fillna(SIN_DEPTO).values
    tipo = pre.tipo_prestador.reindex(nits).fillna("Sin clasificar").values
    return {"corte": corte, "eps": eps, "nits": nits, "M": M, "W": W, "depto": depto,
            "tipo": tipo, "flujo": f}


def grafo(R):
    G = nx.Graph()
    G.add_nodes_from(("E:" + e for e in R["eps"]), lado="eps")
    G.add_nodes_from(("P:" + n for n in R["nits"]), lado="prestador")
    i, j = np.nonzero(R["M"])
    G.add_edges_from(zip(("E:" + R["eps"][x] for x in i), ("P:" + R["nits"][y] for y in j)))
    return G


# ---------------------------------------------------------------- A. centralidad


def centralidad(R, G, meps, mpre, nombres):
    M, W = R["M"], R["W"]
    kE, kP = M.sum(1), M.sum(0)
    sE, sP = W.sum(1), W.sum(0)
    knnE, knnP = rm.knn(M)
    cl = nx.bipartite.closeness_centrality(G, ["E:" + e for e in R["eps"]], normalized=True)
    c = R["corte"]
    me = meps[meps.corte == c].set_index("entidad")
    mp = mpre[mpre.corte == c].set_index("nit")
    # comprobación: el grado y la fuerza coinciden con los de metricas-red-observada.py
    if not (np.array_equal(me.prestadores.reindex(R["eps"]).values, kE)
            and np.allclose(me.girado.reindex(R["eps"]).values, sE)
            and np.array_equal(mp.eps.reindex(R["nits"]).values, kP)
            and np.allclose(mp.girado.reindex(R["nits"]).values, sP)):
        raise SystemExit("ERROR: el grado o la fuerza no coinciden con metricas-*.csv (%s)" % c)
    excl = M[:, kP == 1].sum(1)
    # perfil territorial de cada EPS: dónde gira
    dfe = []
    for i, e in enumerate(R["eps"]):
        por_depto = pd.Series(W[i], index=R["depto"]).groupby(level=0).sum()
        por_depto = por_depto[por_depto > 0].drop(SIN_DEPTO, errors="ignore").sort_values(ascending=False)
        dfe.append({
            "corte": c, "entidad": e, "nombre": nombres.get(e, e), "grado": int(kE[i]),
            "fuerza": float(sE[i]), "participacion_pct": 100 * sE[i] / sE.sum(),
            "intermediacion": float(me.intermediacion[e]), "cercania": cl["E:" + e],
            "knn": float(knnE[i]), "exclusivos": int(excl[i]),
            "departamentos_con_giro": int(por_depto.size),
            "departamento_principal": por_depto.index[0] if por_depto.size else "",
            "parte_departamento_principal_pct": 100 * por_depto.iloc[0] / por_depto.sum() if por_depto.size else np.nan,
        })
    dfe = pd.DataFrame(dfe)
    principal = W.max(0) / sP
    dfp = pd.DataFrame({
        "corte": c, "nit": R["nits"], "grado": kP, "fuerza": sP, "participacion_pct": 100 * sP / sP.sum(),
        "intermediacion": mp.intermediacion.reindex(R["nits"]).values,
        "cercania": [cl["P:" + n] for n in R["nits"]], "knn": knnP,
        "parte_eps_principal": principal, "departamento": R["depto"], "tipo_prestador": R["tipo"],
    })
    return dfe, dfp


def correlaciones_centralidad(dfe, dfp):
    filas = []
    for lado, df in (("eps", dfe), ("prestadores", dfp)):
        cols = ["grado", "fuerza", "intermediacion", "cercania", "knn"]
        for x in range(len(cols)):
            for y in range(x + 1, len(cols)):
                rho = spearmanr(df[cols[x]], df[cols[y]]).statistic
                filas.append({"corte": df.corte.iloc[0], "lado": lado, "medida_1": cols[x],
                              "medida_2": cols[y], "spearman": rho, "n": len(df)})
    return pd.DataFrame(filas)


def distancias(R):
    """Distancias más cortas entre todos los pares (búsqueda en anchura, sin pesos), por tipo de par."""
    from scipy.sparse import bmat, csr_matrix
    from scipy.sparse.csgraph import shortest_path
    nE = R["M"].shape[0]
    B = csr_matrix(R["M"].astype(float))
    D = shortest_path(bmat([[None, B], [B.T, None]]).tocsr(), unweighted=True, directed=False)
    if np.isinf(D).any():
        raise SystemExit("ERROR: la red de %s tiene más de un componente" % R["corte"])
    bloques = {"EPS–EPS": D[:nE, :nE][np.triu_indices(nE, 1)],
               "EPS–prestador": D[:nE, nE:].ravel(),
               "prestador–prestador": D[nE:, nE:][np.triu_indices(D.shape[0] - nE, 1)]}
    filas = []
    for tipo, v in bloques.items():
        d, n = np.unique(v.astype(int), return_counts=True)
        filas += [{"corte": R["corte"], "tipo_de_par": tipo, "distancia": int(x), "pares": int(y)} for x, y in zip(d, n)]
    df = pd.DataFrame(filas)
    media = (df.distancia * df.pares).sum() / df.pares.sum()
    return df, {"diametro": int(df.distancia.max()), "distancia_media": float(media)}


# ---------------------------------------------------------------- B. distribuciones


def concentracion(R):
    filas = []
    for lado, s in (("eps", R["W"].sum(1)), ("prestadores", R["W"].sum(0))):
        v = np.sort(s)[::-1]
        p = 100 * v / v.sum()
        filas.append({"corte": R["corte"], "lado": lado, "nodos": s.size, "gini": rm.gini(s),
                      "cr4_pct": p[:4].sum(), "cr20_pct": p[:20].sum(), "hhi": (p ** 2).sum()})
    for lado, k in (("eps", R["M"].sum(1)), ("prestadores", R["M"].sum(0))):
        h1, h2 = rm.heterogeneidad(k)
        filas.append({"corte": R["corte"], "lado": lado + " (grado)", "nodos": k.size, "gini": rm.gini(k),
                      "grado_medio": k.mean(), "heterogeneidad_k2_k": h1, "heterogeneidad_k2_k2": h2})
    return pd.DataFrame(filas)


def lorenz_tabla(R, puntos=200):
    filas = []
    for lado, s in (("eps", R["W"].sum(1)), ("prestadores", R["W"].sum(0))):
        x, y = rm.lorenz(s)
        idx = np.unique(np.linspace(0, x.size - 1, min(puntos, x.size)).round().astype(int))
        filas.append(pd.DataFrame({"corte": R["corte"], "lado": lado, "fraccion_nodos": x[idx],
                                   "fraccion_dinero": y[idx]}))
    return pd.concat(filas)


def fuerza_grado(R, rng):
    """s(k) ~ k^beta (Barrat et al., 2004): MCO de log10 s sobre log10 k, con intervalo bootstrap."""
    filas, residuos = [], None
    for lado, k, s in (("prestadores", R["M"].sum(0), R["W"].sum(0)), ("eps", R["M"].sum(1), R["W"].sum(1))):
        x, y = np.log10(k.astype(float)), np.log10(s)
        X = np.column_stack([np.ones_like(x), x])
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        res = y - X @ beta
        r2 = 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
        bs = []
        for _ in range(BOOTSTRAP):
            i = rng.integers(x.size, size=x.size)
            if np.ptp(x[i]) == 0:
                continue
            bs.append(np.polyfit(x[i], y[i], 1)[0])
        filas.append({"corte": R["corte"], "lado": lado, "n": x.size, "exponente_beta": beta[1],
                      "ic95_inferior": np.percentile(bs, 2.5), "ic95_superior": np.percentile(bs, 97.5),
                      "intercepto_log10": beta[0], "r2": r2, "spearman_fuerza_grado": spearmanr(k, s).statistic})
        if lado == "prestadores":
            mad = np.median(np.abs(res - np.median(res)))
            residuos = pd.DataFrame({"nit": R["nits"], "residuo_log10": res,
                                     "z_modificado": 0.6745 * (res - np.median(res)) / mad})
    return pd.DataFrame(filas), residuos


def asortatividad(R):
    """Asortatividad bipartita sin pesos (Pearson y por rangos) sobre las aristas del mes."""
    return {"corte": R["corte"], "asortatividad": rm.asortatividad(R["M"]),
            "asortatividad_rangos": rm.asortatividad(R["M"], rangos=True),
            "aristas": int(R["M"].sum())}


def distribucion_dependencia(dfp):
    x = np.sort(dfp.parte_eps_principal.values)
    umbrales = np.round(np.arange(0.05, 1.0001, 0.05), 2)
    filas = [{"corte": dfp.corte.iloc[0], "umbral_parte_eps_principal": u,
              "prestadores_pct": 100 * float((x >= u - 1e-12).mean()),
              "dinero_pct": 100 * float(dfp.fuerza[dfp.parte_eps_principal >= u - 1e-12].sum() / dfp.fuerza.sum())}
             for u in umbrales]
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- C. comunidades


def comunidades(R, G, rng, nombres):
    M, W = R["M"], R["W"]
    nE = len(R["eps"])
    qb, lfb, lcb = rm.optimizar_modularidad(M, rng, arranques=ARRANQUES)
    # Louvain con modularidad estándar ponderada (semilla 0), con el grafo armado en el mismo
    # orden que en metricas-red-observada.py para obtener la misma partición
    fl = R["flujo"]
    Gw = nx.Graph()
    Gw.add_nodes_from(("E:" + e for e in fl.entidad.unique()), lado="eps")
    Gw.add_nodes_from(("P:" + n for n in fl.nit.unique()), lado="prestador")
    Gw.add_weighted_edges_from(zip("E:" + fl.entidad, "P:" + fl.nit, fl.girado))
    cs = nx.community.louvain_communities(Gw, weight="weight", seed=0)
    q_estandar = nx.community.modularity(Gw, cs, weight="weight")
    lab = {n: i for i, c in enumerate(cs) for n in c}
    lv_f = np.array([lab["E:" + e] for e in R["eps"]])
    lv_c = np.array([lab["P:" + n] for n in R["nits"]])
    qw, lfw, lcw = rm.optimizar_modularidad(W, rng, arranques=ARRANQUES_DESCRIPCION, iniciales=[lv_c])
    Bw, mw = rm.matriz_modularidad(W)
    Bb, mb = rm.matriz_modularidad(M)
    todos = lambda f, c: np.concatenate([f, c])
    part = {"binaria": todos(lfb, lcb), "ponderada": todos(lfw, lcw), "louvain_estandar": todos(lv_f, lv_c)}
    resumen = [{"corte": R["corte"], "particion": "binaria (Barber, 30 arranques)", "modularidad_barber_binaria": qb,
                "modularidad_barber_ponderada": rm.modularidad(Bw, mw, lfb, lcb), "comunidades": len(np.unique(part["binaria"]))},
               {"corte": R["corte"], "particion": "ponderada (Barber, 300 arranques + Louvain)",
                "modularidad_barber_binaria": rm.modularidad(Bb, mb, lfw, lcw), "modularidad_barber_ponderada": qw,
                "comunidades": len(np.unique(part["ponderada"]))},
               {"corte": R["corte"], "particion": "Louvain estándar (semilla 0)",
                "modularidad_barber_binaria": rm.modularidad(Bb, mb, lv_f, lv_c),
                "modularidad_barber_ponderada": rm.modularidad(Bw, mw, lv_f, lv_c), "comunidades": len(cs),
                "modularidad_estandar_ponderada": q_estandar}]
    # partición territorial: cada prestador en su departamento y cada EPS en el departamento que
    # más le suma (medio paso de BRIM con las columnas fijas)
    dep_codigos = pd.factorize(R["depto"])[0]
    resumen.append({"corte": R["corte"], "particion": "territorial (departamento del prestador)",
                    "modularidad_barber_binaria": rm.modularidad(Bb, mb, rm.asignar_filas(Bb, dep_codigos), dep_codigos),
                    "modularidad_barber_ponderada": rm.modularidad(Bw, mw, rm.asignar_filas(Bw, dep_codigos), dep_codigos),
                    "comunidades": len(np.unique(dep_codigos))})
    resumen = pd.DataFrame(resumen)
    # acuerdo entre particiones (todos los nodos)
    acuerdo = []
    nombres_p = list(part)
    for x in range(3):
        for y in range(x + 1, 3):
            acuerdo.append({"corte": R["corte"], "particion_1": nombres_p[x], "particion_2": nombres_p[y],
                            "nmi": rm.nmi(part[nombres_p[x]], part[nombres_p[y]]),
                            "ari": rm.ari(part[nombres_p[x]], part[nombres_p[y]])})
    # comparación con el departamento (solo prestadores con departamento)
    con = R["depto"] != SIN_DEPTO
    dep = R["depto"][con]
    for nombre, lc in (("binaria", lcb), ("ponderada", lcw), ("louvain_estandar", lv_c)):
        n_obs, a_obs = rm.nmi(lc[con], dep), rm.ari(lc[con], dep)
        perm_n, perm_a = [], []
        for _ in range(PERMUTACIONES):
            d = rng.permutation(dep)
            perm_n.append(rm.nmi(lc[con], d))
            perm_a.append(rm.ari(lc[con], d))
        acuerdo.append({"corte": R["corte"], "particion_1": nombre, "particion_2": "departamento del prestador",
                        "nmi": n_obs, "ari": a_obs, "nmi_media_permutaciones": np.mean(perm_n),
                        "ari_media_permutaciones": np.mean(perm_a),
                        "p_nmi": rm.p_empirico(n_obs, perm_n, "mayor"), "p_ari": rm.p_empirico(a_obs, perm_a, "mayor"),
                        "prestadores": int(con.sum())})
    acuerdo = pd.DataFrame(acuerdo)
    # pertenencia de cada nodo
    nodos = pd.DataFrame({
        "corte": R["corte"], "lado": ["eps"] * nE + ["prestador"] * len(R["nits"]),
        "id": R["eps"] + R["nits"],
        "comunidad_binaria": part["binaria"], "comunidad_ponderada": part["ponderada"],
        "comunidad_louvain_estandar": part["louvain_estandar"],
        "departamento": [""] * nE + list(R["depto"]), "tipo_prestador": [""] * nE + list(R["tipo"])})
    # composición de la partición ponderada
    comp = []
    sP = W.sum(0)
    for cid in np.unique(part["ponderada"]):
        ef = [R["eps"][i] for i in np.flatnonzero(lfw == cid)]
        pc = np.flatnonzero(lcw == cid)
        dinero = pd.Series(sP[pc], index=R["depto"][pc]).groupby(level=0).sum().sort_values(ascending=False)
        tipos = pd.Series(sP[pc], index=R["tipo"][pc]).groupby(level=0).sum().sort_values(ascending=False)
        dentro = W[np.ix_(lfw == cid, lcw == cid)].sum()
        comp.append({"corte": R["corte"], "comunidad": int(cid), "eps": len(ef),
                     "eps_miembros": "; ".join(nombres.get(e, e) for e in sorted(ef, key=lambda e: -W[R["eps"].index(e)].sum())),
                     "prestadores": len(pc), "dinero_recibido": float(sP[pc].sum()),
                     "dinero_recibido_pct": 100 * float(sP[pc].sum() / sP.sum()),
                     "dinero_dentro_de_la_comunidad_pct": 100 * float(dentro / max(sP[pc].sum(), 1)),
                     "departamentos_principales": "; ".join("%s (%.0f %%)" % (d, 100 * v / dinero.sum()) for d, v in dinero.head(4).items()),
                     "tipos_principales": "; ".join("%s (%.0f %%)" % (t, 100 * v / tipos.sum()) for t, v in tipos.head(3).items())})
    comp = pd.DataFrame(comp).sort_values("dinero_recibido", ascending=False)
    return resumen, acuerdo, nodos, comp, (qb, lfb, lcb)


# ---------------------------------------------------------------- D. estabilidad entre meses


def robustez_meses(redes):
    filas = []
    orden = sorted(redes)
    for x, y in zip(orden[:-1], orden[1:]):
        fx = redes[x]["flujo"].set_index(["entidad", "nit"]).girado
        fy = redes[y]["flujo"].set_index(["entidad", "nit"]).girado
        comunes = fx.index.intersection(fy.index)
        union = fx.index.union(fy.index)
        filas.append({"mes_1": x, "mes_2": y, "aristas_mes_1": len(fx), "aristas_mes_2": len(fy),
                      "aristas_comunes": len(comunes), "jaccard_aristas": len(comunes) / len(union),
                      "dinero_mes_2_en_aristas_del_mes_1_pct": 100 * float(fy.loc[comunes].sum() / fy.sum())})
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- principal


def main():
    os.makedirs(DESTINO, exist_ok=True)
    a, nombres, pre, meps, mpre = cargar()
    rng = np.random.default_rng(SEMILLA)
    redes = {c: red_del_corte(a, c, pre) for c in CORTES}

    t_cent, t_corr, t_dist, t_dist_res, t_conc, t_lor, t_sk, t_dep, t_asor = [], [], [], [], [], [], [], [], []
    t_com_res, t_com_acu, t_com_nod, t_com_comp = [], [], [], []
    residuos_sk = None
    for c in CORTES:
        R = redes[c]
        print("%s: %d EPS, %d prestadores, %d aristas" % (c, *R["M"].shape, R["M"].sum()), flush=True)
        G = grafo(R)
        dfe, dfp = centralidad(R, G, meps, mpre, nombres)
        t_cent.append((dfe, dfp))
        t_corr.append(correlaciones_centralidad(dfe, dfp))
        d, dres = distancias(R)
        t_dist.append(d)
        dres["corte"] = c
        t_dist_res.append(dres)
        t_conc.append(concentracion(R))
        t_lor.append(lorenz_tabla(R))
        sk, res = fuerza_grado(R, rng)
        t_sk.append(sk)
        if c == PRINCIPAL:
            residuos_sk = res.merge(dfp[["nit", "grado", "fuerza", "participacion_pct", "parte_eps_principal",
                                         "tipo_prestador", "departamento"]], on="nit")
        t_dep.append(distribucion_dependencia(dfp))
        t_asor.append(asortatividad(R))
        cres, cacu, cnod, ccomp, _ = comunidades(R, G, rng, nombres)
        t_com_res.append(cres), t_com_acu.append(cacu), t_com_nod.append(cnod), t_com_comp.append(ccomp)

    escribir({
        "centralidad-eps.csv": pd.concat(x[0] for x in t_cent),
        "centralidad-prestadores.csv.gz": pd.concat(x[1] for x in t_cent),
        "correlaciones-centralidad.csv": pd.concat(t_corr),
        "distancias.csv": pd.concat(t_dist), "distancias-resumen.csv": pd.DataFrame(t_dist_res),
        "concentracion.csv": pd.concat(t_conc), "lorenz.csv": pd.concat(t_lor),
        "fuerza-grado.csv": pd.concat(t_sk), "fuerza-grado-residuos.csv.gz": residuos_sk,
        "distribucion-dependencia.csv": pd.concat(t_dep), "asortatividad.csv": pd.DataFrame(t_asor),
        "comunidades-resumen.csv": pd.concat(t_com_res), "comunidades-acuerdo.csv": pd.concat(t_com_acu),
        "comunidades-nodos.csv.gz": pd.concat(t_com_nod), "comunidades-composicion.csv": pd.concat(t_com_comp),
        "robustez-meses.csv": robustez_meses(redes),
    })
    resumen()


def escribir(tablas):
    for nombre, df in tablas.items():
        df.to_csv(os.path.join(DESTINO, nombre), index=False, encoding="utf-8-sig",
                  compression=cfg.GZIP if nombre.endswith(".gz") else "infer", lineterminator="\n")


def resumen():
    """resumen-teoria-redes.txt: las cifras principales, leídas de las tablas escritas."""
    def L(f):
        try:
            return pd.read_csv(os.path.join(DESTINO, f))
        except pd.errors.EmptyDataError:
            return pd.DataFrame({"(vacía)": []})
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 70)
    pd.set_option("display.max_columns", 30)
    out = ["Red observada del giro directo — teoría de redes (mes principal %s; meses de control %s)"
           % (PRINCIPAL, ", ".join(CONTROL)), ""]
    secciones = [
        ("Distancias", L("distancias-resumen.csv")),
        ("Concentración y heterogeneidad", L("concentracion.csv")),
        ("Fuerza–grado s(k) ~ k^beta", L("fuerza-grado.csv")),
        ("Correlaciones de Spearman entre centralidades (corte principal)",
         L("correlaciones-centralidad.csv").query("corte == @PRINCIPAL")),
        ("Asortatividad bipartita sin pesos", L("asortatividad.csv")),
        ("Prestadores exclusivos de cada EPS (corte principal)",
         L("centralidad-eps.csv").query("corte == @PRINCIPAL").sort_values("exclusivos", ascending=False)
         [["nombre", "grado", "exclusivos", "participacion_pct"]]),
        ("Comunidades", L("comunidades-resumen.csv")),
        ("Acuerdo entre particiones y con el departamento", L("comunidades-acuerdo.csv")),
        ("Composición de la partición ponderada (corte principal)",
         L("comunidades-composicion.csv").query("corte == @PRINCIPAL")),
        ("Dependencia: prestadores y dinero con una EPS principal que da al menos el umbral (corte principal)",
         L("distribucion-dependencia.csv").query("corte == @PRINCIPAL")),
        ("Prestadores lejos de la curva fuerza–grado (|z modificado| > 3,5, corte principal)",
         L("fuerza-grado-residuos.csv.gz").query("abs(z_modificado) > 3.5").sort_values("z_modificado")),
        ("Estabilidad de las aristas entre meses", L("robustez-meses.csv")),
    ]
    for titulo, df in secciones:
        out += ["== " + titulo, df.to_string(index=False, float_format=lambda x: "%.4g" % x), ""]
    texto = "\n".join(out) + "\n"
    with io.open(os.path.join(DESTINO, "resumen-teoria-redes.txt"), "w", encoding="utf-8",
                 newline="\n") as fh:
        fh.write(texto)
    print(texto)


if __name__ == "__main__":
    main()
