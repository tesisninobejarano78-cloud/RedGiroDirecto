# -*- coding: utf-8 -*-
"""
Red observada del giro directo: red bipartita y métricas de estructura.

La red es bipartita, dirigida y con pesos: EPS (entidad) → prestador (NIT). La ADRES ejecuta el
pago por cuenta de la EPS y no es nodo de esta red. Se analiza el mes PRINCIPAL de
configuracion.py (septiembre de 2026, el último corte común a los dos regímenes) y, como control,
los meses de CONTROL (junio, julio y agosto de 2026, todos después del cambio de composición del
contributivo de abril de 2025).

Peso de la arista: lo girado en el corte, sumando proceso y complemento y los dos regímenes. Una
pareja con algo ordenado y nada girado no es arista del flujo: se cuenta aparte como «arista sin
giro».

Métricas:
  - grado y grado ponderado (fuerza) de cada nodo, y concentración de los dos lados;
  - dependencia: qué parte de lo que cada prestador recibe por giro directo viene de cada EPS;
  - criticidad de aristas: aristas puente (si se quitan, la red se parte; casi siempre porque el
    prestador queda aislado) y aristas de las que depende la mayor parte del giro de un
    prestador;
  - potencial de restricción por EPS: cuántos prestadores se quedan sin giro, o pierden la mayor
    parte, si esa EPS no programa;
  - intermediación sobre la versión no dirigida: en la dirigida es cero para todos, porque ningún
    camino EPS → prestador pasa por otro nodo. Se calcula sin pesos: mide la posición en la
    estructura, no un camino que recorra el dinero;
  - proyección EPS–EPS por prestadores compartidos;
  - robustez: las mismas métricas en los meses de control y su correlación de rangos;
  - comunidades (Louvain con diez semillas) y cuánto coinciden entre semillas.

Lectura: la dependencia se mide sobre el giro directo, no sobre todos los ingresos del prestador,
que también cobra a la EPS por fuera del giro y a otros pagadores.

Entradas (salida/): relaciones-giro-directo.csv.gz, eps-entidades.csv,
prestadores-clasificados.csv.

Salidas en salida/:
  aristas-red-observada.csv.gz     una fila por arista y corte, con sus partes y si es puente
  metricas-eps.csv                 una fila por EPS y corte
  metricas-prestadores.csv.gz      una fila por prestador y corte
  metricas-red-por-corte.csv       una fila por corte
  metricas-por-tipo-prestador.csv  corte principal, por tipo de prestador (REPS)
  metricas-por-departamento.csv    corte principal, por departamento del prestador (REPS)
  robustez-control.csv             corte principal frente a cada mes de control
  comunidades-louvain.csv          comunidades del corte principal (semilla 0)
  resumen-metricas-red.txt

Ejecutar:  python metricas-red-observada.py
"""

import io
import itertools
import os

import networkx as nx
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import configuracion as cfg

SALIDA = cfg.SALIDA
PRINCIPAL = cfg.PRINCIPAL
CONTROL = list(cfg.CONTROL)
MAYORIA = 0.5          # una EPS es «principal mayoritaria» si da al menos la mitad del giro del prestador
CASI_TOTAL = 0.95      # y «casi exclusiva» si da al menos el 95 %
SEMILLAS = range(10)   # para comprobar la estabilidad de las comunidades
SIN_DEPTO = "Sin departamento (no está en el REPS)"


def cargar():
    rel = pd.read_csv(os.path.join(SALIDA, "relaciones-giro-directo.csv.gz"),
                      dtype={"nit": str, "codigo_eps": str})
    ent = pd.read_csv(os.path.join(SALIDA, "eps-entidades.csv"), dtype=str)
    rel = rel.merge(ent[["regimen", "codigo_eps", "entidad"]], on=["regimen", "codigo_eps"],
                    how="left", validate="many_to_one")
    if rel.entidad.isna().any():
        raise SystemExit("ERROR: hay códigos de EPS sin entidad")
    nombres = ent.drop_duplicates("entidad").set_index("entidad").nombre_entidad
    pre = pd.read_csv(os.path.join(SALIDA, "prestadores-clasificados.csv"), dtype=str)
    pre["departamento"] = pre.departamento.fillna(SIN_DEPTO)
    return rel, nombres, pre.set_index("nit")


def aristas_del_corte(rel, corte):
    df = rel[rel.corte == corte]
    df = df.assign(
        girado_contributivo=np.where(df.regimen == "contributivo", df.valor_girado, 0),
        girado_subsidiado=np.where(df.regimen == "subsidiado", df.valor_girado, 0),
        girado_complemento=np.where(df.proceso == "complemento", df.valor_girado, 0))
    return df.groupby(["entidad", "nit"], as_index=False).agg(
        girado=("valor_girado", "sum"), ordenado=("valor_ordenado", "sum"),
        operaciones=("operaciones", "sum"), girado_contributivo=("girado_contributivo", "sum"),
        girado_subsidiado=("girado_subsidiado", "sum"), girado_complemento=("girado_complemento", "sum"))


def concentracion(valores):
    v = np.sort(np.asarray(valores, dtype=float))[::-1]
    s = 100 * v / v.sum()
    return {"cr1": s[:1].sum(), "cr4": s[:4].sum(), "cr20": s[:20].sum(), "hhi": (s ** 2).sum()}


def grafo(flujo):
    G = nx.Graph()
    G.add_nodes_from(("E:" + e for e in flujo.entidad.unique()), lado="eps")
    G.add_nodes_from(("P:" + n for n in flujo.nit.unique()), lado="prestador")
    G.add_weighted_edges_from(zip("E:" + flujo.entidad, "P:" + flujo.nit, flujo.girado))
    return G


def medir(corte, a, nombres, pre):
    """Todas las métricas de un corte. Devuelve (aristas, eps, prestadores, red, G)."""
    flujo = a[a.girado > 0].copy()
    sin_giro = a[(a.girado <= 0) & (a.ordenado > 0)]
    s_eps = flujo.groupby("entidad").girado.sum()
    s_pre = flujo.groupby("nit").girado.sum()
    k_eps = flujo.groupby("entidad").nit.nunique()
    k_pre = flujo.groupby("nit").entidad.nunique()
    total = flujo.girado.sum()
    flujo["parte_del_prestador"] = flujo.girado / flujo.nit.map(s_pre)
    flujo["parte_de_la_eps"] = flujo.girado / flujo.entidad.map(s_eps)
    flujo["eps_del_prestador"] = flujo.nit.map(k_pre)
    flujo["mayoritaria"] = flujo.parte_del_prestador >= MAYORIA

    G = grafo(flujo)
    puentes = {frozenset(p) for p in nx.bridges(G)}
    flujo["puente"] = [frozenset(("E:" + e, "P:" + n)) in puentes
                       for e, n in zip(flujo.entidad, flujo.nit)]
    puentes_no_hoja = int((flujo.puente & (flujo.eps_del_prestador > 1)).sum())
    comps = sorted(nx.connected_components(G), key=len, reverse=True)
    gig = comps[0]
    girado_gig = sum(d["weight"] for u, v, d in G.subgraph(gig).edges(data=True))
    # Normalizada por el máximo posible en un grafo bipartito con esos dos lados: los
    # valores se comparan dentro de cada lado, no entre EPS y prestadores.
    bc = nx.bipartite.betweenness_centrality(G, ["E:" + e for e in s_eps.index])

    # --- EPS
    eps = pd.DataFrame({"prestadores": k_eps, "girado": s_eps})
    eps["participacion_pct"] = 100 * eps.girado / total
    excl = flujo[flujo.eps_del_prestador == 1]
    may = flujo[flujo.mayoritaria]
    eps["prestadores_exclusivos"] = excl.groupby("entidad").nit.nunique()
    eps["girado_a_exclusivos"] = excl.groupby("entidad").girado.sum()
    eps["prestadores_dependientes"] = may.groupby("entidad").nit.nunique()
    eps["girado_a_dependientes"] = may.groupby("entidad").girado.sum()
    eps = eps.fillna(0)
    eps["cartera_exclusiva_pct"] = 100 * eps.prestadores_exclusivos / eps.prestadores
    eps["intermediacion"] = [bc["E:" + e] for e in eps.index]
    proy = nx.bipartite.weighted_projected_graph(G, ["E:" + e for e in eps.index])
    eps["eps_con_prestadores_comunes"] = [proy.degree("E:" + e) for e in eps.index]
    eps["prestadores_compartidos"] = eps.prestadores - eps.prestadores_exclusivos
    eps["girado_contributivo"] = flujo.groupby("entidad").girado_contributivo.sum()
    eps["girado_subsidiado"] = flujo.groupby("entidad").girado_subsidiado.sum()
    eps["girado_complemento"] = flujo.groupby("entidad").girado_complemento.sum()
    eps["aristas_sin_giro"] = sin_giro.groupby("entidad").size().reindex(eps.index, fill_value=0)
    eps["ordenado_sin_giro"] = sin_giro.groupby("entidad").ordenado.sum().reindex(eps.index, fill_value=0)
    eps.insert(0, "nombre", nombres.reindex(eps.index).values)
    eps.insert(0, "corte", corte)
    for c in ("prestadores_exclusivos", "prestadores_dependientes"):
        eps[c] = eps[c].astype(int)

    # --- prestadores
    prin = flujo.sort_values(["girado", "entidad"], ascending=[False, True]).drop_duplicates("nit").set_index("nit")
    pm = pd.DataFrame({"eps": k_pre, "girado": s_pre})
    pm["participacion_pct"] = 100 * pm.girado / total
    pm["eps_principal"] = prin.entidad
    pm["nombre_eps_principal"] = nombres.reindex(prin.entidad.reindex(pm.index)).values
    pm["parte_eps_principal_pct"] = 100 * prin.parte_del_prestador
    pm["hhi_fuentes"] = flujo.groupby("nit").parte_del_prestador.apply(lambda s: 10000 * float((s ** 2).sum()))
    pm["intermediacion"] = [bc["P:" + n] for n in pm.index]
    pm = pm.join(pre[["razon_social", "tipo_prestador", "departamento", "municipio"]], how="left")
    pm.insert(0, "corte", corte)

    # --- red
    ce, cp = concentracion(s_eps), concentracion(s_pre)
    red = {
        "corte": corte, "eps": len(s_eps), "prestadores": len(s_pre), "aristas": len(flujo),
        "girado": float(total), "densidad_bipartita": len(flujo) / (len(s_eps) * len(s_pre)),
        "aristas_sin_giro": len(sin_giro), "ordenado_sin_giro": float(sin_giro.ordenado.sum()),
        "componentes": len(comps), "nodos_componente_gigante_pct": 100 * len(gig) / G.number_of_nodes(),
        "girado_componente_gigante_pct": 100 * girado_gig / total,
        "grado_eps_min": int(k_eps.min()), "grado_eps_mediana": float(k_eps.median()),
        "grado_eps_max": int(k_eps.max()),
        "grado_prestador_mediana": float(k_pre.median()), "grado_prestador_p90": float(k_pre.quantile(.9)),
        "grado_prestador_max": int(k_pre.max()),
        "prestadores_con_una_eps_pct": 100 * float((k_pre == 1).mean()),
        "girado_a_prestadores_con_una_eps_pct": 100 * float(s_pre[k_pre == 1].sum() / total),
        "aristas_puente": len(puentes), "aristas_puente_pct": 100 * len(puentes) / len(flujo),
        "girado_en_puentes_pct": 100 * float(flujo[flujo.puente].girado.sum() / total),
        "puentes_sin_prestador_aislado": puentes_no_hoja,
        "prestadores_con_eps_mayoritaria_pct": 100 * float((pm.parte_eps_principal_pct >= 100 * MAYORIA).mean()),
        "prestadores_con_eps_casi_exclusiva_pct": 100 * float((pm.parte_eps_principal_pct >= 100 * CASI_TOTAL).mean()),
        "girado_a_prestadores_con_eps_casi_exclusiva_pct": 100 * float(
            pm[pm.parte_eps_principal_pct >= 100 * CASI_TOTAL].girado.sum() / total),
        "parte_eps_principal_ponderada_pct": float((pm.parte_eps_principal_pct * pm.girado).sum() / total),
        "eps_cr1": ce["cr1"], "eps_cr4": ce["cr4"], "eps_hhi": ce["hhi"],
        "prestador_cr4": cp["cr4"], "prestador_cr20": cp["cr20"], "prestador_hhi": cp["hhi"],
        "proyeccion_eps_densidad": nx.density(proy),
        "intermediacion_maxima_eps": eps.intermediacion.max(),
        "intermediacion_maxima_prestador": pm.intermediacion.max(),
    }
    flujo.insert(0, "corte", corte)
    return flujo, eps.reset_index(), pm.reset_index(), red, G


def por_tipo(flujo, pm, total):
    t = pm.groupby("tipo_prestador").agg(prestadores=("nit", "size"), girado=("girado", "sum"),
                                         eps_mediana=("eps", "median"),
                                         con_una_eps=("eps", lambda s: int((s == 1).sum())),
                                         parte_eps_principal_media_pct=("parte_eps_principal_pct", "mean"))
    t["girado_pct"] = 100 * t.girado / total
    t["con_una_eps_pct"] = 100 * t.con_una_eps / t.prestadores
    t["casi_exclusivos_pct"] = 100 * pm.groupby("tipo_prestador").parte_eps_principal_pct.apply(
        lambda s: float((s >= 100 * CASI_TOTAL).mean()))
    t["intermediacion_media"] = pm.groupby("tipo_prestador").intermediacion.mean()
    return t.sort_values("girado", ascending=False).reset_index()


def por_departamento(flujo, pm, nombres):
    f = flujo.merge(pm[["nit", "departamento"]], on="nit", how="left")
    filas = []
    for dep, g in f.groupby("departamento"):
        por_eps = g.groupby("entidad").girado.sum().sort_values(ascending=False)
        c = concentracion(por_eps)
        p = pm[pm.departamento == dep]
        filas.append({
            "departamento": dep, "prestadores": len(p), "girado": float(g.girado.sum()),
            "eps_que_giran": len(por_eps), "eps_principal": nombres.get(por_eps.index[0], por_eps.index[0]),
            "eps_cr1": c["cr1"], "eps_hhi": c["hhi"], "eps_n_equivalente": 10000 / c["hhi"],
            "prestadores_con_una_eps_pct": 100 * float((p.eps == 1).mean()),
            "girado_a_prestadores_con_una_eps_pct": 100 * float(p[p.eps == 1].girado.sum() / p.girado.sum()),
        })
    return pd.DataFrame(filas).sort_values("girado", ascending=False)


def robustez(principal, control):
    """Compara el corte principal con un mes de control."""
    (ep, pp, rp), (ec, pc, rc) = principal, control
    e = ep.merge(ec, on="entidad", suffixes=("", "_c"))
    p = pp.merge(pc, on="nit", suffixes=("", "_c"))
    top = lambda df, col: set(df.nlargest(20, col).nit)
    top5 = lambda df: set(df.nlargest(5, "prestadores_dependientes").entidad)
    return {
        "corte_control": ec.corte.iloc[0],
        "eps_comunes": len(e), "eps_solo_principal": len(ep) - len(e), "eps_solo_control": len(ec) - len(e),
        "spearman_eps_girado": spearmanr(e.girado, e.girado_c).statistic,
        "spearman_eps_dependientes": spearmanr(e.prestadores_dependientes, e.prestadores_dependientes_c).statistic,
        "spearman_eps_exclusivos": spearmanr(e.prestadores_exclusivos, e.prestadores_exclusivos_c).statistic,
        "spearman_eps_intermediacion": spearmanr(e.intermediacion, e.intermediacion_c).statistic,
        "top5_eps_dependientes_comunes": len(top5(ep) & top5(ec)),
        "prestadores_comunes": len(p),
        "spearman_prestador_girado": spearmanr(p.girado, p.girado_c).statistic,
        "spearman_prestador_intermediacion": spearmanr(p.intermediacion, p.intermediacion_c).statistic,
        "spearman_prestador_eps": spearmanr(p.eps, p.eps_c).statistic,
        "top20_intermediacion_comunes": len(top(pp, "intermediacion") & top(pc, "intermediacion")),
        "top20_girado_comunes": len(top(pp, "girado") & top(pc, "girado")),
    }


def acuerdo_eps(a, b):
    """Fracción de pares de EPS (presentes en las dos asignaciones) que las dos tratan igual:
    juntas en ambas o separadas en ambas."""
    comunes = sorted(n for n in a if n.startswith("E:") and n in b)
    pares = list(itertools.combinations(comunes, 2))
    return sum((a[x] == a[y]) == (b[x] == b[y]) for x, y in pares) / len(pares)


def asignar(G, semilla):
    cs = nx.community.louvain_communities(G, weight="weight", seed=semilla)
    return cs, {n: i for i, c in enumerate(cs) for n in c}


def comunidades(G, nombres, pm):
    """Louvain con varias semillas. Devuelve (tabla de la semilla 0, modularidades,
    acuerdo entre semillas, asignación de la semilla 0)."""
    asignaciones, modularidades = [], []
    for s in SEMILLAS:
        cs, etiqueta = asignar(G, s)
        modularidades.append(nx.community.modularity(G, cs, weight="weight"))
        asignaciones.append(etiqueta)
    acuerdo = [acuerdo_eps(a, b) for a, b in itertools.combinations(asignaciones, 2)]
    cs0 = nx.community.louvain_communities(G, weight="weight", seed=0)
    filas = []
    for i, c in enumerate(sorted(cs0, key=lambda c: -sum(G.degree(n, weight="weight") for n in c))):
        e = sorted((n[2:] for n in c if n.startswith("E:")),
                   key=lambda x: -G.degree("E:" + x, weight="weight"))
        nits = [n[2:] for n in c if n.startswith("P:")]
        deps = pm.set_index("nit").loc[nits].groupby("departamento").girado.sum().sort_values(ascending=False)
        filas.append({
            "comunidad": i + 1, "eps": len(e), "prestadores": len(nits),
            "girado_recibido": float(deps.sum()),
            "eps_miembros": "; ".join(str(nombres.get(x, x)) for x in e),
            "departamentos_principales": "; ".join("%s (%.0f %%)" % (d, 100 * v / deps.sum())
                                                   for d, v in deps.head(4).items()),
        })
    return pd.DataFrame(filas), modularidades, acuerdo, asignaciones[0]


def main():
    rel, nombres, pre = cargar()
    cortes = [PRINCIPAL] + CONTROL
    faltan = [c for c in cortes if c not in set(rel[rel.regimen == "contributivo"].corte)
              or c not in set(rel[rel.regimen == "subsidiado"].corte)]
    if faltan:
        raise SystemExit("ERROR: cortes sin los dos regímenes: %s" % faltan)

    res = {}
    for c in cortes:
        print("Midiendo %s…" % c, flush=True)
        res[c] = medir(c, aristas_del_corte(rel, c), nombres, pre)

    aristas = pd.concat([res[c][0] for c in cortes])
    eps = pd.concat([res[c][1] for c in cortes])
    pms = pd.concat([res[c][2] for c in cortes])
    red = pd.DataFrame([res[c][3] for c in cortes])
    aristas.to_csv(os.path.join(SALIDA, "aristas-red-observada.csv.gz"), index=False, encoding="utf-8-sig",
                   compression=cfg.GZIP, lineterminator="\n")
    eps.to_csv(os.path.join(SALIDA, "metricas-eps.csv"), index=False, encoding="utf-8-sig",
               lineterminator="\n")
    pms.to_csv(os.path.join(SALIDA, "metricas-prestadores.csv.gz"), index=False, encoding="utf-8-sig",
               compression=cfg.GZIP, lineterminator="\n")
    red.to_csv(os.path.join(SALIDA, "metricas-red-por-corte.csv"), index=False, encoding="utf-8-sig",
               lineterminator="\n")

    fp, ep, pp, rp, Gp = res[PRINCIPAL]
    tipos = por_tipo(fp, pp, rp["girado"])
    tipos.to_csv(os.path.join(SALIDA, "metricas-por-tipo-prestador.csv"), index=False, encoding="utf-8-sig",
                 lineterminator="\n")
    deps = por_departamento(fp, pp, nombres)
    deps.to_csv(os.path.join(SALIDA, "metricas-por-departamento.csv"), index=False, encoding="utf-8-sig",
                lineterminator="\n")
    com, mods, acuerdo, asig0 = comunidades(Gp, nombres, pp)
    com.to_csv(os.path.join(SALIDA, "comunidades-louvain.csv"), index=False, encoding="utf-8-sig",
               lineterminator="\n")
    filas_rob = []
    for c in CONTROL:
        f = robustez((ep, pp, rp), (res[c][1], res[c][2], res[c][3]))
        f["acuerdo_comunidades_eps"] = acuerdo_eps(asig0, asignar(res[c][4], 0)[1])
        filas_rob.append(f)
    rob = pd.DataFrame(filas_rob)
    rob.to_csv(os.path.join(SALIDA, "robustez-control.csv"), index=False, encoding="utf-8-sig",
               lineterminator="\n")

    # ------------------------------------------------------------ resumen
    L = []
    p = L.append
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 60)
    p("Red observada del giro directo — red bipartita EPS → prestador y métricas de estructura")
    p("Mes principal: %s · meses de control: %s" % (PRINCIPAL, ", ".join(CONTROL)))
    p("Peso: lo girado (proceso + complemento, dos regímenes). Dependencia medida sobre el giro directo.")
    p("")
    p("== La red en cada corte")
    t = red.set_index("corte").T
    p(t.to_string(float_format=lambda x: "%.4f" % x if abs(x) < 1 else "%.1f" % x))
    p("")
    p("== EPS en el corte principal, por prestadores que dependen de ella (≥ %d %% de su giro)" % (100 * MAYORIA))
    cols = ["nombre", "prestadores", "participacion_pct", "prestadores_exclusivos", "prestadores_dependientes",
            "cartera_exclusiva_pct", "intermediacion", "eps_con_prestadores_comunes", "girado_complemento",
            "aristas_sin_giro", "ordenado_sin_giro"]
    t = ep.sort_values("prestadores_dependientes", ascending=False)[cols].copy()
    t["girado_complemento"] = (t.girado_complemento / 1e9).round(1)
    t["ordenado_sin_giro"] = (t.ordenado_sin_giro / 1e9).round(2)
    p(t.to_string(index=False, float_format=lambda x: "%.3f" % x))
    p("")
    p("== Prestadores con mayor intermediación (no dirigida) en el corte principal")
    cols = ["nit", "razon_social", "tipo_prestador", "departamento", "eps", "participacion_pct",
            "parte_eps_principal_pct", "nombre_eps_principal", "intermediacion"]
    p(pp.nlargest(20, "intermediacion")[cols].to_string(index=False, float_format=lambda x: "%.4f" % x))
    p("")
    p("== Mayores receptores en el corte principal")
    p(pp.nlargest(20, "girado")[cols].to_string(index=False, float_format=lambda x: "%.4f" % x))
    p("")
    p("== Mayores receptores que reciben al menos el %d %% de su giro de una sola EPS" % (100 * CASI_TOTAL))
    p(pp[pp.parte_eps_principal_pct >= 100 * CASI_TOTAL].nlargest(20, "girado")[cols]
      .to_string(index=False, float_format=lambda x: "%.4f" % x))
    p("")
    p("== Por tipo de prestador (corte principal; tipo según el REPS)")
    p(tipos.to_string(index=False, float_format=lambda x: "%.2f" % x if abs(x) >= 0.01 else "%.2e" % x))
    p("")
    p("== Por departamento del prestador (corte principal; domicilio según el REPS)")
    t = deps.copy()
    t["girado"] = (t.girado / 1e9).round(1)
    p(t.to_string(index=False, float_format=lambda x: "%.1f" % x))
    p("")
    p("== Robustez: corte principal frente a cada mes de control")
    p(rob.set_index("corte_control").T.to_string(float_format=lambda x: "%.3f" % x))
    p("")
    p("== Comunidades (Louvain, %d semillas) en el corte principal" % len(mods))
    p("  modularidad en %d semillas: %.3f a %.3f · acuerdo entre semillas en la agrupación de EPS: %.3f a %.3f"
      % (len(mods), min(mods), max(mods), min(acuerdo), max(acuerdo)))
    p(com.to_string(index=False))
    texto = "\n".join(L) + "\n"
    with io.open(os.path.join(SALIDA, "resumen-metricas-red.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(texto)
    print(texto)


if __name__ == "__main__":
    main()
