# -*- coding: utf-8 -*-
"""
Descriptivos de la red observada que no dependen de cómo se dibuje la red.

Lee la tabla de relaciones que produce ingerir-anexos-giro.py y calcula, por corte y para cada
alcance (contributivo, subsidiado y los dos juntos):

  - tamaño: EPS que ordenan giro, prestadores que lo reciben, parejas y montos;
  - concentración de lo girado por prestador y por EPS: CR1, CR4, CR10, CR20, índice de
    Herfindahl (HHI) y número equivalente (10.000 / HHI). Las cifras se dan sin calificar el
    nivel de concentración;
  - cuántas EPS le giran a cada prestador;
  - estabilidad entre cortes: cuánto se parecen dos meses. No es un análisis en el tiempo: mide
    cuánto depende la fotografía del mes elegido.

Además compara las cifras que da el texto del Boletín 72 de Lupa al Giro (junio de 2026) con lo
que suman los anexos, y resume por qué se mueve o no se mueve el dinero según el campo
Observación: quién ordena el complemento, qué causa lo no girado y cuándo la ADRES retiene el giro
neto a una EPS.

Salidas en salida/:
  eps-entidades.csv               código de EPS -> entidad (unificación por nombre)
  descriptivos-por-corte.csv
  estabilidad-entre-cortes.csv
  retenciones-giro-neto.csv       giro neto a EPS no aplicado por incumplir el giro directo
  resumen-red-observada.txt

Ejecutar:  python describir-red-observada.py
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
VACIAS_EPS = {"EPS", "EPSS", "EPSI", "EOC", "E", "P", "S", "SA", "SAS", "LTDA",
              "MOVILIDAD", "LA", "EL", "EN", "LIQUIDACION", "ESP"}


def canon_eps(nombre):
    s = unicodedata.normalize("NFKD", str(nombre or "")).encode("ascii", "ignore").decode().upper()
    s = s.replace(".", "")
    return "".join(t for t in re.split(r"[^A-Z0-9]+", s) if t and t not in VACIAS_EPS)


def entidades(codigos):
    """Une los códigos de una misma EPS (régimen, movilidad) por su nombre más frecuente.

    Dos nombres canónicos se unen cuando uno es prefijo del otro (mínimo 5 letras). El
    resultado se guarda para poder revisarlo: es una correspondencia derivada, no una fuente.
    """
    codigos = codigos.copy()
    codigos["clave"] = codigos.nombre_mas_frecuente.map(canon_eps)
    canon = {}
    for k in sorted(set(codigos.clave), key=len, reverse=True):
        destino = next((c for c in set(canon.values())
                        if c.startswith(k) and len(k) >= 5), k)
        canon[k] = destino
    codigos["entidad"] = codigos.clave.map(canon)
    nombre = (codigos.sort_values("cortes", ascending=False)
              .groupby("entidad").nombre_mas_frecuente.first())
    codigos["nombre_entidad"] = codigos.entidad.map(nombre)
    return codigos[["regimen", "codigo_eps", "nombre_mas_frecuente", "entidad", "nombre_entidad",
                    "primer_corte", "ultimo_corte", "cortes"]]


def pesos_observacion(s):
    """Primer monto en pesos de una observación: '$40.728.099.729,00' -> 40728099729.

    Tolera el error de la fuente '$488.794.926,495,00' (coma en lugar de punto de miles,
    Coosalud, julio de 2026), que se lee como $488.794,9 millones: es lo que suman los giros
    aplicados después.
    """
    t = re.search(r"\$\s*([\d.,]+\d)", s).group(1)
    t = re.sub(r",\d{2}$", "", t)
    return float(re.sub(r"[.,]", "", t))


def concentracion(valores, prefijo):
    v = np.sort(np.asarray(valores, dtype=float))[::-1]
    tot = v.sum()
    s = 100 * v / tot if tot else v
    hhi = float((s ** 2).sum())
    return {
        prefijo + "cr1": round(float(s[:1].sum()), 2),
        prefijo + "cr4": round(float(s[:4].sum()), 2),
        prefijo + "cr10": round(float(s[:10].sum()), 2),
        prefijo + "cr20": round(float(s[:20].sum()), 2),
        prefijo + "hhi": round(hhi, 1),
        prefijo + "n_equivalente": round(10000 / hhi, 1) if hhi else None,
    }


def describir(df):
    """df: relaciones de un corte y un alcance, con la columna 'entidad'."""
    par = df.groupby(["entidad", "nit"], as_index=False).valor_girado.sum()
    por_ips = par.groupby("nit").valor_girado.sum()
    por_eps = par.groupby("entidad").valor_girado.sum()
    eps_por_ips = par[par.valor_girado > 0].groupby("nit").entidad.nunique()
    principal = par.groupby("nit").valor_girado.max() / por_ips
    d = {
        "eps_codigos": df.codigo_eps.nunique(),
        "eps_entidades": df.entidad.nunique(),
        "prestadores": df.nit.nunique(),
        "parejas": len(par),
        "operaciones": int(df.operaciones.sum()),
        "valor_girado": round(float(df.valor_girado.sum())),
    }
    d.update(concentracion(por_ips[por_ips > 0], "ips_"))
    d.update(concentracion(por_eps[por_eps > 0], "eps_"))
    una = eps_por_ips == 1
    d.update({
        "ips_con_una_eps_pct": round(100 * una.mean(), 2),
        "girado_a_ips_con_una_eps_pct": round(100 * por_ips[una[una].index].sum() / por_ips.sum(), 2),
        "eps_por_ips_mediana": float(eps_por_ips.median()),
        "eps_por_ips_maximo": int(eps_por_ips.max()),
        "participacion_eps_principal_ponderada_pct": round(
            100 * float((principal * por_ips).sum() / por_ips.sum()), 2),
    })
    return d


def parecido(a, b):
    """Qué tanto se parece el corte b al corte a (dos tablas de relaciones)."""
    pa = a.groupby(["entidad", "nit"]).valor_girado.sum()
    pb = b.groupby(["entidad", "nit"]).valor_girado.sum()
    ia, ib = a.groupby("nit").valor_girado.sum(), b.groupby("nit").valor_girado.sum()
    union = ia.index.union(ib.index)
    rho = spearmanr(ia.reindex(union, fill_value=0), ib.reindex(union, fill_value=0)).statistic
    top_a, top_b = set(ia.nlargest(20).index), set(ib.nlargest(20).index)
    comunes = pb.index.intersection(pa.index)
    return {
        "jaccard_prestadores": round(len(ia.index.intersection(ib.index)) / len(union), 4),
        "jaccard_parejas": round(len(comunes) / len(pa.index.union(pb.index)), 4),
        "girado_en_parejas_comunes_pct": round(100 * float(pb[comunes].sum() / pb.sum()), 2),
        "spearman_girado_por_prestador": round(float(rho), 4),
        "top20_comunes": len(top_a & top_b),
    }


def main():
    rel = pd.read_csv(os.path.join(SALIDA, "relaciones-giro-directo.csv.gz"),
                      dtype={"nit": str, "codigo_eps": str})
    cod = pd.read_csv(os.path.join(SALIDA, "codigos-eps.csv"), dtype=str)
    cod["cortes"] = cod.cortes.astype(int)
    ent = entidades(cod)
    ent.to_csv(os.path.join(SALIDA, "eps-entidades.csv"), index=False, encoding="utf-8-sig",
               lineterminator="\n")
    rel = rel.merge(ent[["regimen", "codigo_eps", "entidad"]], on=["regimen", "codigo_eps"],
                    how="left", validate="many_to_one")
    if rel.entidad.isna().any():
        raise SystemExit("ERROR: hay códigos de EPS sin entidad")

    alcances = {"contributivo": rel[rel.regimen == "contributivo"],
                "subsidiado": rel[rel.regimen == "subsidiado"]}
    comunes = sorted(set(alcances["contributivo"].corte) & set(alcances["subsidiado"].corte))
    alcances["ambos"] = rel[rel.corte.isin(comunes)]

    desc, est = [], []
    for nombre, df in alcances.items():
        cortes = sorted(df.corte.unique())
        grupos = {c: g for c, g in df.groupby("corte")}
        for c in cortes:
            desc.append({"alcance": nombre, "corte": c, **describir(grupos[c])})
        for c0, c1 in zip(cortes, cortes[1:]):
            est.append({"alcance": nombre, "comparacion": "mes anterior",
                        "corte_base": c0, "corte": c1, **parecido(grupos[c0], grupos[c1])})
        ultimo = cortes[-1]
        for c in cortes[:-1]:
            est.append({"alcance": nombre, "comparacion": "último corte",
                        "corte_base": ultimo, "corte": c, **parecido(grupos[ultimo], grupos[c])})
    desc = pd.DataFrame(desc)
    est = pd.DataFrame(est)
    desc.to_csv(os.path.join(SALIDA, "descriptivos-por-corte.csv"), index=False, encoding="utf-8-sig",
                lineterminator="\n")
    est.to_csv(os.path.join(SALIDA, "estabilidad-entre-cortes.csv"), index=False, encoding="utf-8-sig",
               lineterminator="\n")

    # ------------------------------------------------------------ resumen
    L = []
    p = L.append
    pd.set_option("display.width", 220)
    p("Descriptivos de la red observada")
    p("Cortes: contributivo %s a %s · subsidiado %s a %s · ambos (meses comunes) %s a %s" % (
        alcances["contributivo"].corte.min(), alcances["contributivo"].corte.max(),
        alcances["subsidiado"].corte.min(), alcances["subsidiado"].corte.max(), comunes[0], comunes[-1]))
    p("Entidades EPS tras unificar códigos: %d (de %d códigos)" % (ent.entidad.nunique(), len(ent)))
    p("")
    cols = ["eps_entidades", "prestadores", "parejas", "valor_girado", "ips_cr4", "ips_cr20", "ips_hhi",
            "eps_cr1", "eps_cr4", "eps_hhi", "ips_con_una_eps_pct", "girado_a_ips_con_una_eps_pct"]
    for nombre in alcances:
        t = desc[desc.alcance == nombre].set_index("corte")[cols].copy()
        t["valor_girado"] = (t.valor_girado / 1e9).round(1)
        p("== %s (valor girado en miles de millones de pesos)" % nombre)
        p(t.to_string())
        p("")
    p("== Estabilidad entre meses consecutivos (mediana, mínimo y máximo por alcance y periodo)")
    for nombre in alcances:
        for etiqueta, filtro in (("todo el periodo", lambda s: s == s),
                                 ("desde 2025-01", lambda s: s >= "2025-01")):
            e = est[(est.alcance == nombre) & (est.comparacion == "mes anterior") & filtro(est.corte)]
            p("  %-12s %-16s jaccard prestadores %.3f [%.3f-%.3f] · jaccard parejas %.3f [%.3f-%.3f] · "
              "girado en parejas comunes %.1f%% [%.1f-%.1f] · spearman %.3f · top20 comunes %d [%d-%d]" % (
                  nombre, etiqueta,
                  e.jaccard_prestadores.median(), e.jaccard_prestadores.min(), e.jaccard_prestadores.max(),
                  e.jaccard_parejas.median(), e.jaccard_parejas.min(), e.jaccard_parejas.max(),
                  e.girado_en_parejas_comunes_pct.median(), e.girado_en_parejas_comunes_pct.min(),
                  e.girado_en_parejas_comunes_pct.max(), e.spearman_girado_por_prestador.median(),
                  e.top20_comunes.median(), e.top20_comunes.min(), e.top20_comunes.max()))
    p("")

    # Cotejo con el Boletín 72 de Lupa al Giro (junio de 2026): cifras que da el texto del
    # boletín frente a lo que suman los anexos.
    jun = rel[rel.corte == "2026-06"]
    sem = rel[(rel.corte >= "2026-01") & (rel.corte <= "2026-06")]
    por_ips_sem = sem.groupby("nit").valor_girado.sum().sort_values(ascending=False)
    filas = [
        ("Giro directo subsidiado, jun-2026 (billones)", "3,48",
         "%.2f" % (jun[jun.regimen == "subsidiado"].valor_girado.sum() / 1e12)),
        ("Receptores subsidiado, jun-2026", "3.290", str(jun[jun.regimen == "subsidiado"].nit.nunique())),
        ("Giro directo contributivo, jun-2026 (billones)", "3,10",
         "%.2f" % (jun[jun.regimen == "contributivo"].valor_girado.sum() / 1e12)),
        ("Receptores contributivo, jun-2026", "2.992", str(jun[jun.regimen == "contributivo"].nit.nunique())),
        ("Receptores con NIT único, jun-2026, ambos regímenes", "3.673", str(jun.nit.nunique())),
        ("EPS del contributivo con giro, jun-2026 (códigos)", "17",
         str(jun[jun.regimen == "contributivo"].codigo_eps.nunique())),
        ("EPS del subsidiado con giro, jun-2026 (códigos)", "26",
         str(jun[jun.regimen == "subsidiado"].codigo_eps.nunique())),
        ("Girado directamente ene-jun 2026 (billones)", "39,79", "%.2f" % (sem.valor_girado.sum() / 1e12)),
        ("Receptores ene-jun 2026", "4.072", str(sem.nit.nunique())),
        ("Participación de los 20 mayores receptores, ene-jun 2026 (%)", "21,63",
         "%.2f" % (100 * por_ips_sem.head(20).sum() / por_ips_sem.sum())),
    ]
    p("== Cotejo con el Boletín 72 (prosa del boletín, junio de 2026)")
    p("  %-62s %10s %10s" % ("cifra", "boletín", "anexos"))
    for f in filas:
        p("  %-62s %10s %10s" % f)
    p("")

    # Por qué se mueve o no se mueve el dinero: la causa que cita cada operación
    # (observaciones-por-corte.csv, de la ingesta).
    obs = pd.read_csv(os.path.join(SALIDA, "observaciones-por-corte.csv"))
    sub = rel[rel.regimen == "subsidiado"]
    comp = obs[(obs.serie == "subsidiado-ips") & (obs.proceso == "complemento")]
    tot_comp = comp.valor_girado.sum()
    p("== El complemento del subsidiado (%s a %s)" % (sub.corte.min(), sub.corte.max()))
    p("  girado como complemento: %.1f mil millones = %.2f %% del giro directo del subsidiado (%.1f mil millones)"
      % (tot_comp / 1e9, 100 * tot_comp / sub.valor_girado.sum(), sub.valor_girado.sum() / 1e9))
    p("  operaciones cuya comunicación llegó a la ADRES por correo electrónico: %d de %d"
      % (comp.operaciones_por_correo.sum(), comp.operaciones.sum()))
    t = comp.groupby("causa")[["operaciones", "valor_girado"]].sum().sort_values("valor_girado", ascending=False)
    t["pct_girado"] = (100 * t.valor_girado / tot_comp).round(2)
    t["valor_girado"] = (t.valor_girado / 1e9).round(1)
    p(t.to_string())
    p("")
    p("== Lo ordenado y no girado, por causa citada (hojas de proceso y exclusiones del complemento)")
    ng = (obs[obs.operaciones_no_giradas > 0].groupby(["serie", "causa"])
          [["operaciones_no_giradas", "valor_no_girado"]].sum())
    ng["pct_no_girado"] = (100 * ng.valor_no_girado / ng.valor_no_girado.sum()).round(2)
    ng["valor_no_girado"] = (ng.valor_no_girado / 1e9).round(2)
    p(ng.to_string())
    p("")

    # Retención del giro neto a la EPS (certificación del subsidiado): la ADRES deja de
    # girarle a la EPS cuando incumple el giro directo. Se cuenta solo lo que dice el texto.
    eps = pd.read_csv(os.path.join(SALIDA, "eps-por-corte.csv"), dtype={"codigo_eps": str})
    cert = eps[eps.tabla == "certificacion-eps"].copy()
    cert["o"] = cert.observacion.fillna("").map(
        lambda s: unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())
    ret = cert[cert.o.str.contains("porcentaje") | cert.o.str.contains("cargue del archivo")].copy()
    ret["regla"] = np.where(ret.o.str.contains("cargue del archivo"),
                            "cargue del archivo fuera de tiempo", "porcentaje mínimo de giro directo")
    ret["norma_citada"] = ret.o.map(lambda o: ", ".join(sorted(set(re.findall(
        r"(?:decreto|resolucion) \d+ de \d{4}", o)))) or ("«la norma»" if "norma" in o else ""))
    ret["no_aplicado"] = ret.observacion.map(pesos_observacion)
    ret["giro_directo_sobre_upc_neta_pct"] = (100 * ret.giro_directo_proceso / ret.upc_neta).round(2)
    ret[["corte", "codigo_eps", "nombre_eps", "regla", "norma_citada", "giro_directo_sobre_upc_neta_pct",
         "no_aplicado"]].to_csv(os.path.join(SALIDA, "retenciones-giro-neto.csv"), index=False,
                                encoding="utf-8-sig", lineterminator="\n")
    p("== Giro neto a la EPS no aplicado por incumplir el giro directo (certificación del subsidiado)")
    ret = ret.merge(ent[ent.regimen == "subsidiado"][["codigo_eps", "entidad"]], on="codigo_eps", how="left")
    p("  %d filas (EPS y corte) en los cortes %s · %d entidades · %.1f mil millones no aplicados" % (
        len(ret), ", ".join(sorted(ret.corte.unique())), ret.entidad.nunique(),
        ret.no_aplicado.sum() / 1e9))
    g = ret.groupby(["corte", "regla", "norma_citada"]).agg(filas=("codigo_eps", "size"),
                                                            no_aplicado=("no_aplicado", "sum"))
    g["no_aplicado"] = (g.no_aplicado / 1e9).round(1)
    p(g.to_string())
    p("  filas marcadas con un giro directo / UPC neta de 90 %% o más: %d (la base de cálculo de la ADRES "
      "no es necesariamente esta)" % (ret.giro_directo_sobre_upc_neta_pct >= 90).sum())
    texto = "\n".join(L) + "\n"
    with io.open(os.path.join(SALIDA, "resumen-red-observada.txt"), "w", encoding="utf-8",
                 newline="\n") as fh:
        fh.write(texto)
    print(texto)


if __name__ == "__main__":
    main()
