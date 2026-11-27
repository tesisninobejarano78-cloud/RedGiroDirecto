# -*- coding: utf-8 -*-
"""
Proyecciones de la red observada y comparación con la norma por criterios.

Todo lo que calcula este programa es descriptivo:

1. Las cuatro EPS más grandes: grado, fuerza (dinero girado por su cuenta) y giro medio por vínculo.
2. Proyección EPS–EPS (B·Bᵀ): prestadores compartidos, proporción compartida (índice de Jaccard),
   grado y fuerza en la proyección y comunidades (Louvain sobre el Jaccard), en el mes principal y
   en los meses de control.
3. Proyección prestador–prestador (Bᵀ·B): pares por número de EPS compartidas, sensibilidad al umbral
   y, con el umbral de dos EPS, grado, fuerza y comunidades, comparadas con el departamento (NMI, ARI).
4. Densidad sobre las mismas clases: la red normada y la observada agrupada en las clases de la normada,
   a nivel de clase y a nivel de EPS × clase.
5. Lo que entra y lo que sale de cada actor (cuellos de botella): ADRES, EPS, Supersalud y prestadores.

B es la matriz EPS × prestador con un 1 si la EPS le giró al prestador en el mes. Las redes salen de
aristas-red-observada.csv.gz y la clase de cada receptor, de la función clase_de() de
contraste-y-acoplamiento.py. Lectura: la ADRES gira por cuenta de la EPS; la EPS ordena el giro.

Ejecutar:  python proyecciones-y-comparacion.py      (unos minutos; salida en salida/proyecciones/)
"""

import importlib.util
import os
import re
import sys

import matplotlib
import networkx as nx
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.sparse.csgraph import connected_components
from scipy.stats import spearmanr

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import configuracion as cfg  # noqa: E402
import redes_metodos as rm  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = cfg.SALIDA
DESTINO = os.path.join(SALIDA, "proyecciones")
FIGURAS = os.path.join(DESTINO, "figuras")
PRINCIPAL = cfg.PRINCIPAL
CONTROL = list(cfg.CONTROL)
MES = cfg.nombre_mes(PRINCIPAL)
UMBRAL_PRESTADORES = 2   # se excluyen los que reciben de una sola EPS: solo pueden compartir esa
SEMILLAS = range(20)     # arranques de Louvain; se conserva la partición de mayor modularidad
SEMILLA_PRESTADORES = 20261111

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def cargar_contraste():
    spec = importlib.util.spec_from_file_location("contraste", os.path.join(AQUI, "contraste-y-acoplamiento.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def matriz(a):
    eps = sorted(a.entidad.unique())
    pres = sorted(a.nit.unique())
    ie = {e: i for i, e in enumerate(eps)}
    ip = {p: i for i, p in enumerate(pres)}
    B = sparse.csr_matrix((np.ones(len(a)), ([ie[e] for e in a.entidad], [ip[p] for p in a.nit])),
                          shape=(len(eps), len(pres)))
    B.data[:] = 1.0
    return B, eps, pres


def louvain_mejor(G, weight="weight", semillas=SEMILLAS):
    mejor, qmax = None, -1.0
    for s in semillas:
        cs = nx.community.louvain_communities(G, weight=weight, seed=s)
        q = nx.community.modularity(G, cs, weight=weight)
        if q > qmax + 1e-12:
            mejor, qmax = cs, q
    return sorted(mejor, key=lambda c: -len(c)), qmax


# ---------------------------------------------------------------- 1. cuatro mayores EPS


def cuatro_mayores(met, nombres):
    m = met[met.corte == PRINCIPAL].sort_values("girado", ascending=False).head(4).copy()
    m["nombre"] = [nombres.get(e, e) for e in m.entidad]
    m["giro_medio_por_vinculo"] = m.girado / m.prestadores
    return m[["entidad", "nombre", "prestadores", "girado", "participacion_pct", "prestadores_exclusivos",
              "cartera_exclusiva_pct", "giro_medio_por_vinculo"]]


# ---------------------------------------------------------------- 2. proyección EPS–EPS


def proyeccion_eps(a, nombres, pre):
    B, eps, pres = matriz(a)
    C = (B @ B.T).toarray()
    k = np.diag(C).copy()
    n = len(eps)
    J = C / (k[:, None] + k[None, :] - C)
    off = ~np.eye(n, dtype=bool)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if C[i, j] > 0:
                G.add_edge(i, j, weight=float(J[i, j]), compartidos=int(C[i, j]))
    cs, q = louvain_mejor(G)
    lab = np.empty(n, dtype=int)
    for c, nodos in enumerate(cs):
        lab[list(nodos)] = c
    kp = np.asarray(B.sum(0)).ravel()
    exclusivos = np.asarray(B[:, kp == 1].sum(1)).ravel()
    por_eps = pd.DataFrame({
        "entidad": eps, "nombre": [nombres.get(e, e) for e in eps], "prestadores": k.astype(int),
        "grado_proyeccion": (C * off > 0).sum(1), "fuerza_proyeccion": (C * off).sum(1).astype(int),
        "jaccard_medio": np.nanmean(np.where(off, J, np.nan), axis=1),
        "cartera_compartida_pct": 100 * (k - exclusivos) / k, "comunidad": lab + 1})
    pares = []
    for i in range(n):
        for j in range(i + 1, n):
            pares.append({"eps_a": por_eps.nombre[i], "eps_b": por_eps.nombre[j], "compartidos": int(C[i, j]),
                          "jaccard": J[i, j], "misma_comunidad": lab[i] == lab[j]})
    pares = pd.DataFrame(pares).sort_values("jaccard", ascending=False)
    # composición: departamentos que más reciben, por comunidad
    a2 = a.merge(pre[["departamento"]], left_on="nit", right_index=True, how="left")
    a2["comunidad"] = a2.entidad.map(dict(zip(eps, lab + 1)))
    comp = []
    for c, g in a2.groupby("comunidad"):
        top = (g.groupby("departamento").girado.sum() / g.girado.sum()).sort_values(ascending=False).head(3)
        comp.append({"comunidad": c, "eps": "; ".join(por_eps.nombre[por_eps.comunidad == c]),
                     "n_eps": int((por_eps.comunidad == c).sum()), "girado_pct": 100 * g.girado.sum() / a.girado.sum(),
                     "departamentos_principales": "; ".join(f"{d} {100 * v:.0f} %" for d, v in top.items())})
    res = {"eps": n, "densidad_sin_pesos": float((C[off] > 0).mean()), "modularidad_jaccard": q,
           "comunidades": len(cs), "jaccard_mediana": float(np.median(J[off])),
           "jaccard_max": float(J[off].max())}
    return por_eps, pares, pd.DataFrame(comp), res, (J, lab, por_eps.nombre.tolist())


# ---------------------------------------------------------------- 3. proyección prestador–prestador


def proyeccion_prestadores(a, pre):
    B, eps, pres = matriz(a)
    n = len(pres)
    kp = np.asarray(B.sum(0)).ravel().astype(int)
    P = (B.T @ B).tocoo()
    m = P.row < P.col
    r, c, w = P.row[m], P.col[m], P.data[m].astype(int)
    posibles = n * (n - 1) // 2
    sens = []
    for t in range(1, 9):
        s = w >= t
        deg = np.bincount(np.r_[r[s], c[s]], minlength=n)
        A = sparse.coo_matrix((np.ones(int(s.sum())), (r[s], c[s])), shape=(n, n))
        _, labc = connected_components(A, directed=False)
        con = deg > 0
        sens.append({"umbral_eps_compartidas": t, "pares": int(s.sum()), "densidad": s.sum() / posibles,
                     "prestadores_con_vinculo": int(con.sum()),
                     "prestadores_con_al_menos_t_eps": int((kp >= t).sum()),
                     "componente_mayor": int(np.bincount(labc[con]).max()) if con.any() else 0})
    dist = pd.Series(w).value_counts().sort_index().rename_axis("eps_compartidas").reset_index(name="pares")
    # red con el umbral
    s = w >= UMBRAL_PRESTADORES
    G = nx.Graph()
    G.add_weighted_edges_from(zip(r[s].tolist(), c[s].tolist(), w[s].astype(float).tolist()))
    cs = nx.community.louvain_communities(G, weight="weight", seed=SEMILLA_PRESTADORES)
    q = nx.community.modularity(G, cs, weight="weight")
    cs = sorted(cs, key=lambda x: -len(x))
    lab = np.zeros(n, dtype=int)
    for i, nodos in enumerate(cs):
        lab[list(nodos)] = i + 1
    nodos = np.array(sorted(G.nodes()))
    grado = np.array([G.degree(v) for v in nodos])
    fuerza = np.array([G.degree(v, weight="weight") for v in nodos])
    info = pre.reindex([pres[v] for v in nodos])
    tabla = pd.DataFrame({"nit": [pres[v] for v in nodos], "razon_social": info.razon_social.values,
                          "tipo_prestador": info.tipo_prestador.values, "departamento": info.departamento.values,
                          "eps_que_le_giran": kp[nodos], "grado_proyeccion": grado, "fuerza_proyeccion": fuerza,
                          "comunidad": lab[nodos]})
    dep = tabla.departamento.fillna("sin departamento").values
    pos = {p: i for i, p in enumerate(pres)}
    comp = []
    for cidx, g in tabla.groupby("comunidad"):
        tops = g.departamento.fillna("sin departamento").value_counts(normalize=True).head(3)
        tipos = g.tipo_prestador.fillna("sin tipo").value_counts(normalize=True).head(2)
        # EPS que más aparecen en la comunidad
        idx = [pos[x] for x in g.nit]
        sub = B[:, idx]
        cuenta = np.asarray(sub.sum(1)).ravel()
        orden = np.argsort(-cuenta)[:3]
        comp.append({"comunidad": cidx, "prestadores": len(g),
                     "eps_medias_por_prestador": g.eps_que_le_giran.mean(),
                     "departamentos_principales": "; ".join(f"{d} {100 * v:.0f} %" for d, v in tops.items()),
                     "tipos_principales": "; ".join(f"{d} {100 * v:.0f} %" for d, v in tipos.items()),
                     "eps_mas_presentes": "; ".join(f"{eps[o]} ({100 * cuenta[o] / len(g):.0f} %)" for o in orden)})
    res = {"prestadores": n, "pares_posibles": posibles, "umbral": UMBRAL_PRESTADORES,
           "prestadores_en_la_red_filtrada": int(len(nodos)), "pares_en_la_red_filtrada": int(s.sum()),
           "densidad_filtrada": s.sum() / (len(nodos) * (len(nodos) - 1) / 2),
           "comunidades": len(cs), "modularidad": q,
           "nmi_departamento": rm.nmi(tabla.comunidad.values, pd.factorize(dep)[0]),
           "ari_departamento": rm.ari(tabla.comunidad.values, pd.factorize(dep)[0]),
           "spearman_grado_proyeccion_vs_eps": float(spearmanr(tabla.eps_que_le_giran, tabla.grado_proyeccion).statistic),
           "spearman_fuerza_proyeccion_vs_eps": float(spearmanr(tabla.eps_que_le_giran, tabla.fuerza_proyeccion).statistic)}
    return pd.DataFrame(sens), dist, tabla, pd.DataFrame(comp), res


# ---------------------------------------------------------------- 4. densidad sobre las mismas clases


def densidad_clases(a, pre, CLASES, nombres):
    f = a.merge(pre[["clase"]], left_on="nit", right_index=True, how="left")
    normadas = {cl for cl, (_, v) in CLASES.items() if v}
    observadas = set(f.clase.dropna())
    union = sorted(normadas | observadas)
    eps = sorted(f.entidad.unique())
    usa = f.groupby(["entidad", "clase"]).girado.sum().unstack(fill_value=0).reindex(index=eps, columns=union, fill_value=0) > 0
    por_clase = pd.DataFrame({"clase": union, "clase_nombre": [CLASES[c][0] for c in union],
                              "vinculo_normado": [CLASES[c][1] or "sin vínculo normado" for c in union],
                              "en_la_norma": [c in normadas for c in union],
                              "eps_que_la_usan": usa.sum(0).values.astype(int)})
    n_eps, n_cl = len(eps), len(union)
    res = {"clases_en_la_parte_comun": n_cl, "clases_normadas": len(normadas), "clases_observadas": len(observadas),
           "densidad_clase_norma": len(normadas) / n_cl, "densidad_clase_observada": len(observadas) / n_cl,
           "eps": n_eps, "pares_eps_clase_posibles": n_eps * n_cl,
           "densidad_eps_clase_norma_habilita": len(normadas) / n_cl,
           "densidad_eps_clase_observada": float(usa.values.mean()),
           "uso_de_lo_que_la_norma_habilita": float(usa[sorted(normadas)].values.mean()),
           "pares_eps_clase_fuera_de_la_norma": int(usa[[c for c in union if c not in normadas]].values.sum())}
    usa.index = [nombres.get(e, e) for e in usa.index]
    return por_clase, usa, res


# ---------------------------------------------------------------- 5. lo que entra y lo que sale


def causa(obs):
    o = str(obs).upper()
    if re.search(r"\bSNS\b|SUPERINTENDENCIA|SUPERSALUD", o):
        return "comunicación de la Supersalud"
    if "EMBARGO" in o:
        return "embargo"
    if re.search(r"CUENTA|BANC|BLOQUEAD|CANCELAD|INACTIV", o):
        return "falla bancaria"
    return "otra"


def entradas_y_salidas():
    rel = pd.read_csv(os.path.join(SALIDA, "relaciones-giro-directo.csv.gz"), dtype={"nit": str})
    dif = pd.read_csv(os.path.join(SALIDA, "operaciones-con-diferencia.csv"), dtype={"nit": str})
    dif["no_girado"] = dif.valor_ordenado - dif.valor_girado
    dif["causa"] = dif.observacion.map(causa)
    var = pd.read_csv(os.path.join(SALIDA, "variables-eps-mes.csv"))
    sg = pd.read_csv(os.path.join(SALIDA, "contraste", "aristas-sin-giro.csv"), dtype={"nit": str})
    expo = pd.read_csv(os.path.join(SALIDA, "contraste", "acoplamiento-exposicion.csv"))
    filas = []
    # Solo las filas con valor ordenado: en parte de la serie el complemento no trae lo ordenado, así que
    # sumar todo daría más girado que ordenado. Lo no girado es la suma de las diferencias positivas.
    for alcance, r, d in ((MES, rel[rel.corte == PRINCIPAL], dif[dif.corte == PRINCIPAL]),
                          ("serie completa", rel, dif)):
        r = r[r.valor_ordenado.notna()]
        ordenado, girado = r.valor_ordenado.sum(), r.valor_girado.sum()
        no_girado = (r.valor_ordenado - r.valor_girado).clip(lower=0).sum()
        causas = d.groupby("causa").no_girado.sum()
        filas.append({"actor": "ADRES", "alcance": alcance, "entra": "órdenes de giro de las EPS (filas con valor ordenado)",
                      "entra_valor": ordenado, "sale": "giro a prestadores en esas filas", "sale_valor": girado,
                      "diferencia": no_girado, "diferencia_pct": 100 * no_girado / ordenado,
                      "explicacion": "; ".join(f"{k} {100 * v / max(causas.sum(), 1):.1f} %" for k, v in causas.sort_values(ascending=False).items())})
    v = var[var.corte == PRINCIPAL]
    for reg, g in v.groupby("regimen"):
        gg = g[g.giro_directo > 0]
        filas.append({"actor": f"EPS ({reg})", "alcance": MES, "entra": "UPC de la base del giro (upc_base)",
                      "entra_valor": gg.upc_base.sum(), "sale": "giro directo por cuenta de las EPS", "sale_valor": gg.giro_directo.sum(),
                      "diferencia": gg.upc_base.sum() - gg.giro_directo.sum(),
                      "diferencia_pct": 100 * (1 - gg.giro_directo.sum() / gg.upc_base.sum()),
                      "explicacion": f"{len(gg)} EPS con giro; mediana del porcentaje: {gg.pct_giro_directo.median():.2f} %; "
                                     f"retenido del giro neto a las EPS: {g.retenido.sum():,.0f}"})
    col_c = "complemento_por_comunicación de la Supersalud"
    col_n = "proceso_no_girado_por_comunicación de la Supersalud"
    filas.append({"actor": "Supersalud", "alcance": MES, "entra": "—", "entra_valor": np.nan,
                  "sale": "giro dirigido por sus comunicaciones (complemento)", "sale_valor": v[col_c].sum(),
                  "diferencia": v[col_n].sum(),
                  "diferencia_pct": np.nan,
                  "explicacion": f"relaciones ordenadas y no giradas: {len(sg)} por {sg.ordenado_no_girado.sum():,.0f}; "
                                 f"prestadores sin giro directo de ninguna EPS: {int((sg.eps_con_giro_en_el_mes == 0).sum())}"})
    e = expo[expo.corte == PRINCIPAL].set_index("criterio")
    filas.append({"actor": "Prestadores", "alcance": MES, "entra": "giro directo", "entra_valor": np.nan,
                  "sale": "—", "sale_valor": np.nan, "diferencia": np.nan, "diferencia_pct": np.nan,
                  "explicacion": f"expuestos a comunicaciones de la Supersalud: {int(e.prestadores_dependientes.get('condicionada_por_supersalud', 0))} "
                                 f"({e.prestadores_dependientes_pct.get('condicionada_por_supersalud', np.nan):.1f} %); "
                                 f"expuestos a una retención: {int(e.prestadores_dependientes.get('con_retencion', 0))} "
                                 f"({e.prestadores_dependientes_pct.get('con_retencion', np.nan):.1f} %)"})
    causas_serie = dif.groupby("causa").no_girado.sum().sort_values(ascending=False)
    return pd.DataFrame(filas), causas_serie


# ---------------------------------------------------------------- 6. figuras


def figuras(Jlab, sens, dist, usa):
    os.makedirs(FIGURAS, exist_ok=True)
    J, lab, nombres = Jlab
    orden = np.lexsort((-J.sum(1), lab))
    Jo = J[np.ix_(orden, orden)].copy()
    np.fill_diagonal(Jo, np.nan)
    fig, ax = plt.subplots(figsize=(8.6, 7.4))
    im = ax.imshow(Jo, cmap="Blues", vmin=0, vmax=np.nanmax(Jo))
    ax.set_xticks(range(len(orden)))
    ax.set_yticks(range(len(orden)))
    ax.set_xticklabels([nombres[i] for i in orden], rotation=90, fontsize=7)
    ax.set_yticklabels([nombres[i] for i in orden], fontsize=7)
    lo = lab[orden]
    for b in np.where(np.diff(lo) != 0)[0]:
        ax.axhline(b + 0.5, color="#E07A2F", lw=1)
        ax.axvline(b + 0.5, color="#E07A2F", lw=1)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Proporción de prestadores compartidos (Jaccard)")
    ax.set_title("Proyección EPS–EPS, %s\nEPS ordenadas por comunidad (líneas naranjas)" % MES, fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURAS, "01-proyeccion-eps-jaccard.png"), dpi=200)
    plt.close(fig)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
    a1.bar(dist.eps_compartidas, dist.pares, color="#2A78D6")
    a1.set_yscale("log")
    a1.set_xlabel("EPS que comparten los dos prestadores")
    a1.set_ylabel("Pares de prestadores (escala log)")
    a1.set_title("Pares por número de EPS compartidas", fontsize=10)
    a2.plot(sens.umbral_eps_compartidas, sens.prestadores_con_vinculo, "o-", color="#2A78D6", label="prestadores con vínculo")
    a2.plot(sens.umbral_eps_compartidas, sens.componente_mayor, "s--", color="#E07A2F", label="componente mayor")
    a2.set_xlabel("Umbral: EPS compartidas como mínimo")
    a2.set_ylabel("Prestadores")
    a2.set_title("Lo que queda con cada umbral", fontsize=10)
    a2.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURAS, "02-proyeccion-prestadores-umbral.png"), dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.6, 7.4))
    ax.imshow(usa.values.astype(int), cmap="Greens", vmin=0, vmax=1.6, aspect="auto")
    ax.set_yticks(range(len(usa.index)))
    ax.set_yticklabels(usa.index, fontsize=7)
    ax.set_xticks(range(len(usa.columns)))
    corto = {"ASC-010": "IPS", "ASC-047": "Cajas de compensación", "ASC-065": "Industria farmacéutica",
             "ASC-067": "Audifarma", "ASC-068": "Disfarma", "ASC-069": "Helpharma",
             "ASC-070": "Importadores y distribuidores", "ASC-071": "Droguerías y dispensación",
             "ASC-253": "Proveedores sin REPS"}
    ax.set_xticklabels([corto.get(c, c) for c in usa.columns], rotation=45, ha="right", fontsize=8)
    ax.set_title("Clases de receptor que alcanza el giro por cuenta de cada EPS\n(%s; verde: hubo giro)" % MES, fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGURAS, "03-eps-por-clase.png"), dpi=200)
    plt.close(fig)


# ---------------------------------------------------------------- principal


def main():
    os.makedirs(DESTINO, exist_ok=True)
    ct = cargar_contraste()
    a_all = pd.read_csv(os.path.join(SALIDA, "aristas-red-observada.csv.gz"), dtype={"nit": str})
    a_all = a_all[a_all.girado > 0]
    a = a_all[a_all.corte == PRINCIPAL]
    ent = pd.read_csv(os.path.join(SALIDA, "eps-entidades.csv"), dtype=str)
    nombres = ent.drop_duplicates("entidad").set_index("entidad").nombre_entidad.to_dict()
    pre = pd.read_csv(os.path.join(SALIDA, "prestadores-clasificados.csv"), dtype=str).set_index("nit")
    inv = pd.read_csv(ct.INVENTARIO, dtype=str).set_index("id")
    pre["parte_de"] = inv.parte_de.reindex(pre.id_inventario).values
    pre["clase"] = [ct.clase_de(p) for p in pre.itertuples()]
    met = pd.read_csv(os.path.join(SALIDA, "metricas-eps.csv"))

    mayores = cuatro_mayores(met, nombres)
    por_eps, pares, comp_eps, res_eps, Jlab = proyeccion_eps(a, nombres, pre)
    control = []
    for c in CONTROL:
        pe, _, _, r, _ = proyeccion_eps(a_all[a_all.corte == c], nombres, pre)
        comun = por_eps[["entidad", "comunidad"]].merge(pe[["entidad", "comunidad"]], on="entidad", suffixes=("_principal", "_control"))
        control.append({"corte": c, "eps": r["eps"], "densidad_sin_pesos": r["densidad_sin_pesos"],
                        "comunidades": r["comunidades"], "modularidad_jaccard": r["modularidad_jaccard"],
                        "nmi_con_el_mes_principal": rm.nmi(comun.comunidad_principal.values, comun.comunidad_control.values),
                        "eps_en_comun_con_el_mes_principal": len(comun)})
    sens, dist, tabla_p, comp_p, res_p = proyeccion_prestadores(a, pre)
    por_clase, usa, res_dens = densidad_clases(a, pre, ct.CLASES, nombres)
    es, causas_serie = entradas_y_salidas()
    figuras(Jlab, sens, dist, usa)

    tablas = {"cuatro-mayores-eps.csv": mayores, "proyeccion-eps-por-eps.csv": por_eps,
              "proyeccion-eps-pares.csv": pares, "proyeccion-eps-comunidades.csv": comp_eps,
              "proyeccion-eps-meses-control.csv": pd.DataFrame(control),
              "proyeccion-prestadores-umbral.csv": sens, "proyeccion-prestadores-distribucion.csv": dist,
              "proyeccion-prestadores-nodos.csv.gz": tabla_p, "proyeccion-prestadores-comunidades.csv": comp_p,
              "densidad-clases.csv": por_clase, "densidad-eps-por-clase.csv": usa.astype(int).reset_index(names="eps"),
              "entradas-y-salidas.csv": es, "no-girado-por-causa-serie.csv": causas_serie.rename_axis("causa").reset_index()}
    for n, df in tablas.items():
        df.to_csv(os.path.join(DESTINO, n), index=False, encoding="utf-8-sig",
                  compression=cfg.GZIP if n.endswith(".gz") else "infer", lineterminator="\n")
    import json
    with open(os.path.join(DESTINO, "resumen-proyecciones.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"eps": res_eps, "prestadores": res_p, "densidad": res_dens},
                  f, ensure_ascii=False, indent=1, default=float)

    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 120)
    lineas = ["Proyecciones de la red observada y comparación con la norma — %s" % MES, ""]
    lineas += ["1. Cuatro EPS más grandes", mayores.to_string(index=False), ""]
    lineas += ["2. Proyección EPS–EPS", str({k: round(v, 4) if isinstance(v, float) else v for k, v in res_eps.items()}),
               por_eps.sort_values("fuerza_proyeccion", ascending=False).to_string(index=False), "",
               comp_eps.to_string(index=False), "", "Pares con mayor Jaccard:", pares.head(10).to_string(index=False), "",
               "Meses de control:", pd.DataFrame(control).to_string(index=False), ""]
    top = tabla_p.sort_values("fuerza_proyeccion", ascending=False).head(10)
    lineas += ["3. Proyección prestador–prestador", str({k: round(v, 4) if isinstance(v, float) else v for k, v in res_p.items()}),
               sens.to_string(index=False), "", comp_p.to_string(index=False), "", "Mayor fuerza en la proyección:",
               top.drop(columns=["nit"]).to_string(index=False), ""]
    lineas += ["4. Densidad sobre las mismas clases", str({k: round(v, 4) if isinstance(v, float) else v for k, v in res_dens.items()}),
               por_clase.to_string(index=False), ""]
    lineas += ["5. Lo que entra y lo que sale", es.to_string(index=False), "", "No girado por causa, serie completa:",
               causas_serie.to_string(), ""]
    texto = "\n".join(lineas)
    with open(os.path.join(DESTINO, "resumen-proyecciones.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    print(texto)


if __name__ == "__main__":
    main()
