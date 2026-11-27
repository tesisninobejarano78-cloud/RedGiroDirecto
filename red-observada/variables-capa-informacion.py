# -*- coding: utf-8 -*-
"""
Variables de la capa de información por EPS y mes.

La comparación entre las capas de recursos e información necesita variables de la capa de
información medidas por EPS. Los anexos de Lupa al Giro ya traen tres, sin buscar otra fuente:

  1. cuánto de su UPC programó la EPS como giro directo en el proceso ordinario, cuánto se giró
     después como complemento y a pedido de quién;
  2. las retenciones del giro neto a la EPS por no llegar al porcentaje mínimo o por cargar tarde
     su archivo, y a dónde fue después ese dinero;
  3. el porcentaje de giro directo, con la base que reproduce el boletín de la ADRES.

Bases del porcentaje (comprobadas contra el Boletín 72 de junio de 2026, que se reproduce al
centésimo: 77,09 % y 78,95 %):
  - contributivo: giro directo / UPC de afiliados activos (hoja «Valores reconocidos proceso»);
  - subsidiado: (proceso + complemento) / UPC apropiada (certificación por EPS).
Además se calcula el porcentaje del proceso solo (lo que la EPS programó en la liquidación), que
es lo que la ADRES evalúa para retener el giro neto. La base exacta que usa la ADRES para el 90 %
del Decreto 930 de 2026 no está publicada en las fuentes consultadas: se informan las dos lecturas
y cuántos casos explica cada una.

Tamaño frente a cumplimiento: se mide la correlación de rangos (Spearman) entre la UPC de cada
entidad y su porcentaje, por régimen y mes, en cada mes de 2026. Con 17 a 25 entidades por
régimen, el resultado es descriptivo, no una prueba de causalidad.

Entradas (salida/): eps-por-corte.csv, relaciones-giro-directo.csv.gz,
observaciones-por-eps.csv, eps-entidades.csv.

Salidas en salida/:
  variables-eps-mes.csv              una fila por régimen, mes y entidad
  retenciones-y-destino.csv          cada retención del giro neto y a dónde fue después
  base-del-90-por-ciento.csv         cuántas retenciones explica cada base de cálculo
  tamano-y-cumplimiento.csv          correlación tamaño–porcentaje por régimen y mes
  resumen-capa-informacion.txt

Ejecutar:  python variables-capa-informacion.py
"""

import io
import os
import re
import unicodedata

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

import configuracion as cfg

SALIDA = cfg.SALIDA
VENTANA = sorted(cfg.CONTROL + [cfg.PRINCIPAL])   # mes principal y meses de control
MINIMO = 90.0


def plano(s):
    return unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()


def pesos(texto):
    """'$40.728.099.729,00' -> 40728099729. Tolera el error de la fuente '$488.794.926,495,00'."""
    t = texto.strip().rstrip(",.")
    t = re.sub(r",\d{2}$", "", t)          # centavos
    return float(re.sub(r"[.,]", "", t))


MONTO = r"\$\s*([\d.,]+\d)"


def leer_retencion(obs):
    """Retención del giro neto por incumplir el giro directo y destino posterior del dinero."""
    o = plano(obs)
    # La cláusula termina en el primer punto que no esté dentro del monto.
    m = re.search(r"no se aplico (?:el giro neto (?:a eps )?por )?" + MONTO
                  + r"[^.]*?(porcentaje|cargue del archivo)", o)
    if not m:
        return None
    resto = o[m.end():]
    gd = re.search(r"se aplico giro a? ?directo por valor de " + MONTO, resto)
    gt = re.search(r"giro (?:a )?tesoreria (?:por valor de )?" + MONTO, resto)
    quien = re.search(r"atendiendo comunicacion (de la eps|de la sns)?", resto)
    return {
        "motivo": "porcentaje mínimo de giro directo" if m.group(2) == "porcentaje"
                  else "cargue del archivo fuera de tiempo",
        "norma_citada": "Decreto 930 de 2026" if "decreto 930 de 2026" in o else "sin nombrarla",
        "retenido": pesos(m.group(1)),
        "luego_giro_directo": pesos(gd.group(1)) if gd else 0.0,
        "luego_tesoreria": pesos(gt.group(1)) if gt else 0.0,
        "comunicacion_de": {"de la eps": "la EPS", "de la sns": "la Supersalud"}.get(
            quien.group(1) if quien and quien.group(1) else "", "sin decir" if quien else "sin comunicación"),
        "menciona_embargo": "embargo" in resto,
    }


def main():
    eps = pd.read_csv(os.path.join(SALIDA, "eps-por-corte.csv"), dtype={"codigo_eps": str})
    rel = pd.read_csv(os.path.join(SALIDA, "relaciones-giro-directo.csv.gz"),
                      dtype={"nit": str, "codigo_eps": str})
    obs = pd.read_csv(os.path.join(SALIDA, "observaciones-por-eps.csv"), dtype={"codigo_eps": str})
    ent = pd.read_csv(os.path.join(SALIDA, "eps-entidades.csv"), dtype=str)
    mapa = ent.set_index(["regimen", "codigo_eps"]).entidad
    nombres = ent.drop_duplicates("entidad").set_index("entidad").nombre_entidad

    # ------------------------------------------------ subsidiado: certificación por código
    cert = eps[eps.tabla == "certificacion-eps"].copy()
    num = ["upc_apropiada", "upc_neta", "valor_a_girar", "giro_directo_proceso",
           "giro_directo_complemento", "giro_neto_eps"]
    cert[num] = cert[num].fillna(0)
    comp = obs[(obs.serie == "subsidiado-ips") & (obs.proceso == "complemento")]
    por_causa = comp.pivot_table(index=["corte", "codigo_eps"], columns="causa", values="valor_girado",
                                 aggfunc="sum", fill_value=0)
    cert = cert.merge(por_causa.add_prefix("complemento_por_").reset_index(), on=["corte", "codigo_eps"],
                      how="left")
    cert = cert.fillna({c: 0 for c in cert.columns if c.startswith("complemento_por_")})
    proc_no = obs[(obs.serie == "subsidiado-ips") & (obs.proceso == "proceso")].groupby(
        ["corte", "codigo_eps", "causa"]).valor_no_girado.sum().unstack(fill_value=0)
    cert = cert.merge(proc_no.add_prefix("proceso_no_girado_por_").reset_index(),
                      on=["corte", "codigo_eps"], how="left")
    cert = cert.fillna({c: 0 for c in cert.columns if c.startswith("proceso_no_girado_por_")})

    ret = []
    for _, f in cert.iterrows():
        r = leer_retencion(f.observacion)
        if r:
            ret.append({"corte": f.corte, "codigo_eps": f.codigo_eps, "nombre_eps": f.nombre_eps, **r,
                        "proceso_sobre_upc_apropiada_pct": 100 * f.giro_directo_proceso / f.upc_apropiada
                        if f.upc_apropiada else np.nan,
                        "proceso_sobre_upc_neta_pct": 100 * f.giro_directo_proceso / f.upc_neta
                        if f.upc_neta else np.nan})
    ret = pd.DataFrame(ret)
    ret["luego_giro_directo_pct"] = 100 * ret.luego_giro_directo / ret.retenido
    ret["entidad"] = [mapa.get(("subsidiado", c)) for c in ret.codigo_eps]
    ret.to_csv(os.path.join(SALIDA, "retenciones-y-destino.csv"), index=False, encoding="utf-8-sig",
               lineterminator="\n")

    # ¿Qué base explica las retenciones por el 90 %? Solo en los cortes donde la norma ya
    # se cita (Decreto 930) y solo entre las EPS sin otra causa que retenga su giro neto.
    otra_causa = cert.observacion.map(plano).str.contains(
        r"resolucion \d+-\d+ del|solicitud radicado|se excluyeron beneficiarios", regex=True)
    cortes_930 = sorted(ret[ret.norma_citada == "Decreto 930 de 2026"].corte.unique())
    base_filas = []
    for corte in cortes_930:
        x = cert[(cert.corte == corte) & (cert.upc_apropiada > 0)].copy()
        x["retenida"] = x.codigo_eps.isin(ret[(ret.corte == corte) & (ret.motivo.str.startswith("porcentaje"))]
                                          .codigo_eps)
        x["otra_causa"] = otra_causa.loc[x.index]
        for nombre, valor in (("proceso / UPC apropiada", x.giro_directo_proceso / x.upc_apropiada),
                              ("proceso / UPC neta", x.giro_directo_proceso / x.upc_neta),
                              ("(proceso + complemento) / UPC apropiada",
                               (x.giro_directo_proceso + x.giro_directo_complemento) / x.upc_apropiada)):
            bajo = 100 * valor < MINIMO
            libres = ~x.otra_causa
            base_filas.append({
                "corte": corte, "base": nombre, "retenidas": int(x.retenida.sum()),
                "retenidas_bajo_90": int((bajo & x.retenida).sum()),
                "no_retenidas_bajo_90_sin_otra_causa": int((bajo & ~x.retenida & libres).sum()),
                "no_retenidas_bajo_90_con_otra_causa": int((bajo & ~x.retenida & ~libres).sum()),
                "codigos_no_explicados": "; ".join(sorted(
                    x[(bajo != x.retenida) & libres].nombre_eps.astype(str) + " (" +
                    x[(bajo != x.retenida) & libres].codigo_eps + ")")),
            })
    base = pd.DataFrame(base_filas)
    base.to_csv(os.path.join(SALIDA, "base-del-90-por-ciento.csv"), index=False, encoding="utf-8-sig",
                lineterminator="\n")

    # ------------------------------------------------ variables por régimen, mes y entidad
    cert["entidad"] = [mapa.get(("subsidiado", c)) for c in cert.codigo_eps]
    cert["retenido"] = 0.0
    if len(ret):
        k = ret.groupby(["corte", "codigo_eps"]).retenido.sum()
        cert["retenido"] = [k.get((a, b), 0.0) for a, b in zip(cert.corte, cert.codigo_eps)]
    cols_comp = [c for c in cert.columns if c.startswith("complemento_por_")]
    cols_no = [c for c in cert.columns if c.startswith("proceso_no_girado_por_")]
    sub = cert.groupby(["corte", "entidad"], as_index=False)[
        ["upc_apropiada", "upc_neta", "giro_directo_proceso", "giro_directo_complemento", "giro_neto_eps",
         "retenido"] + cols_comp + cols_no].sum()
    sub["regimen"] = "subsidiado"
    sub["upc_base"] = sub.upc_apropiada
    sub["giro_directo"] = sub.giro_directo_proceso + sub.giro_directo_complemento
    sub["pct_giro_directo"] = 100 * sub.giro_directo / sub.upc_base
    sub["pct_proceso"] = 100 * sub.giro_directo_proceso / sub.upc_base
    sub["pct_proceso_upc_neta"] = 100 * sub.giro_directo_proceso / sub.upc_neta
    sub["complemento_pct_del_giro"] = 100 * sub.giro_directo_complemento / sub.giro_directo
    sub["complemento_supersalud_pct_del_giro"] = 100 * sub.get(
        "complemento_por_comunicación de la Supersalud", 0) / sub.giro_directo

    rec = eps[eps.tabla == "reconocimiento-eps"].copy()
    rec["entidad"] = [mapa.get(("contributivo", c)) for c in rec.codigo_eps]
    con_upc = rec.groupby(["corte", "entidad"], as_index=False).upc_afiliados_activos.sum()
    rc = rel[rel.regimen == "contributivo"].copy()
    rc["entidad"] = [mapa.get(("contributivo", c)) for c in rc.codigo_eps]
    con_giro = rc.groupby(["corte", "entidad"], as_index=False).agg(
        giro_directo=("valor_girado", "sum"), ordenado=("valor_ordenado", "sum"))
    con = con_upc.merge(con_giro, on=["corte", "entidad"], how="outer").fillna(0)
    con["regimen"] = "contributivo"
    con["upc_base"] = con.upc_afiliados_activos
    con["giro_directo_proceso"] = con.giro_directo
    con["pct_giro_directo"] = np.where(con.upc_base > 0, 100 * con.giro_directo / con.upc_base, np.nan)
    con["pct_proceso"] = con.pct_giro_directo
    con["ordenado_no_girado"] = con.ordenado - con.giro_directo

    var = pd.concat([sub, con], ignore_index=True, sort=False)
    var.insert(2, "nombre", nombres.reindex(var.entidad).values)
    orden = ["regimen", "corte", "entidad", "nombre", "upc_base", "giro_directo", "giro_directo_proceso",
             "giro_directo_complemento", "pct_giro_directo", "pct_proceso", "pct_proceso_upc_neta",
             "complemento_pct_del_giro", "complemento_supersalud_pct_del_giro", "retenido", "giro_neto_eps",
             "upc_neta", "ordenado_no_girado"] + cols_comp + cols_no
    var = var[[c for c in orden if c in var.columns]].sort_values(["regimen", "corte", "upc_base"],
                                                                  ascending=[True, True, False])
    var.to_csv(os.path.join(SALIDA, "variables-eps-mes.csv"), index=False, encoding="utf-8-sig",
               lineterminator="\n")

    # ------------------------------------------------ tamaño frente a cumplimiento
    tam = []
    cortes_2026 = sorted(c for c in var.corte.unique() if c >= "2026-01")
    for regimen in ("contributivo", "subsidiado"):
        for corte in cortes_2026:
            x = var[(var.regimen == regimen) & (var.corte == corte) & (var.upc_base > 0)
                    & (var.giro_directo > 0)]
            if len(x) < 5:
                continue
            for medida in ("pct_giro_directo", "pct_proceso"):
                if regimen == "contributivo" and medida == "pct_proceso":
                    continue
                rho = spearmanr(x.upc_base, x[medida])
                tam.append({"regimen": regimen, "corte": corte, "medida": medida, "entidades": len(x),
                            "spearman_tamano_vs_pct": rho.statistic, "p_valor": rho.pvalue,
                            "pct_min": x[medida].min(), "pct_p25": x[medida].quantile(.25),
                            "pct_mediana": x[medida].median(), "pct_p75": x[medida].quantile(.75),
                            "pct_max": x[medida].max(),
                            "bajo_80": int((x[medida] < 80).sum()), "bajo_90": int((x[medida] < 90).sum()),
                            "pct_agregado": 100 * (x.giro_directo if medida == "pct_giro_directo"
                                                   else x.giro_directo_proceso).sum() / x.upc_base.sum(),
                            "en_ventana": corte in VENTANA})
    tam = pd.DataFrame(tam)
    tam.to_csv(os.path.join(SALIDA, "tamano-y-cumplimiento.csv"), index=False, encoding="utf-8-sig",
               lineterminator="\n")

    # Acoplamiento descriptivo (subsidiado, 2026): donde la EPS programa menos en el proceso,
    # ¿pesa más el complemento que dirige la Supersalud?
    s26 = var[(var.regimen == "subsidiado") & (var.corte >= "2026-01") & (var.giro_directo > 0)]
    acople = spearmanr(s26.pct_proceso, s26.complemento_supersalud_pct_del_giro)

    # ------------------------------------------------ resumen
    L = []
    p = L.append
    pd.set_option("display.width", 250)
    p("Variables de la capa de información por EPS y mes")
    p("")
    p("== Reproducción del Boletín 72 (junio de 2026)")
    for regimen, cifra in (("contributivo", "77,09"), ("subsidiado", "78,95")):
        x = var[(var.regimen == regimen) & (var.corte == "2026-06")]
        p("  %-12s boletín %s %% · anexos %.2f %% (giro %.2f / UPC %.2f billones)" % (
            regimen, cifra, 100 * x.giro_directo.sum() / x.upc_base.sum(), x.giro_directo.sum() / 1e12,
            x.upc_base.sum() / 1e12))
    x = var[(var.regimen == "subsidiado") & (var.corte == "2026-06")]
    p("  subsidiado, solo el proceso: %.2f %% · el complemento aporta %.2f puntos" % (
        100 * x.giro_directo_proceso.sum() / x.upc_base.sum(),
        100 * x.giro_directo_complemento.sum() / x.upc_base.sum()))
    p("")
    p("== Porcentaje agregado por régimen y mes (meses de 2026)")
    t = tam[tam.medida == "pct_giro_directo"].pivot_table(index="corte", columns="regimen",
                                                           values="pct_agregado")
    t2 = tam[tam.medida == "pct_proceso"].set_index("corte").pct_agregado.rename("subsidiado_solo_proceso")
    p(t.join(t2).round(2).to_string())
    p("")
    p("== Tamaño frente a cumplimiento: correlación de rangos entre la UPC y el porcentaje, por régimen y mes")
    cols = ["regimen", "corte", "medida", "entidades", "spearman_tamano_vs_pct", "p_valor", "pct_min",
            "pct_mediana", "pct_max", "bajo_80", "bajo_90", "en_ventana"]
    p(tam[cols].to_string(index=False, float_format=lambda v: "%.3f" % v))
    p("")
    p("== Retenciones del giro neto y destino posterior")
    cols = ["corte", "codigo_eps", "nombre_eps", "motivo", "norma_citada", "retenido", "luego_giro_directo",
            "luego_tesoreria", "luego_giro_directo_pct", "comunicacion_de", "menciona_embargo",
            "proceso_sobre_upc_apropiada_pct", "proceso_sobre_upc_neta_pct"]
    t = ret[cols].copy()
    for c in ("retenido", "luego_giro_directo", "luego_tesoreria"):
        t[c] = (t[c] / 1e9).round(2)
    p(t.to_string(index=False, float_format=lambda v: "%.2f" % v))
    tot = ret.retenido.sum()
    p("  total retenido %.1f mil millones · luego a prestadores %.1f (%.1f %%) · luego a la EPS %.1f (%.1f %%)"
      % (tot / 1e9, ret.luego_giro_directo.sum() / 1e9, 100 * ret.luego_giro_directo.sum() / tot,
         ret.luego_tesoreria.sum() / 1e9, 100 * ret.luego_tesoreria.sum() / tot))
    p("")
    p("== ¿Qué base de cálculo explica las retenciones por el 90 %?")
    p(base.to_string(index=False))
    p("")
    p("== Acoplamiento descriptivo, subsidiado 2026 (EPS-mes con giro): Spearman entre el porcentaje del "
      "proceso y la parte del giro que dirigió la Supersalud = %.3f (n = %d, p = %.4f)"
      % (acople.statistic, len(s26), acople.pvalue))
    texto = "\n".join(L) + "\n"
    with io.open(os.path.join(SALIDA, "resumen-capa-informacion.txt"), "w", encoding="utf-8",
                 newline="\n") as fh:
        fh.write(texto)
    print(texto)


if __name__ == "__main__":
    main()
