# -*- coding: utf-8 -*-
"""
Figuras del análisis de teoría de redes y de la comparación con la norma.

Ocho figuras estáticas (PNG, 200 ppp) del mes principal. Todas las cifras se leen de las tablas
que escriben teoria-redes-observada.py y contraste-y-acoplamiento.py; el programa no calcula
resultados nuevos, salvo dos tablas que guarda junto a las figuras: el grado medio de los vecinos
por grado del prestador (figura 5) y el reparto del giro de cada EPS entre comunidades (figura 8).

Paleta: azul, naranja y aguamarina para las series y tintas neutras para el texto, con contraste
suficiente sobre fondo blanco; el aguamarina va siempre con etiqueta visible.

Salidas: salida/teoria-redes/figuras/*.png, knn-por-grado.csv y comunidades-matriz-eps.csv
Ejecutar:  python figuras-teoria-redes.py
"""

import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

import configuracion as cfg  # noqa: E402

SALIDA = cfg.SALIDA
TEORIA = os.path.join(SALIDA, "teoria-redes")
CONTRASTE = os.path.join(SALIDA, "contraste")
FIGURAS = os.path.join(TEORIA, "figuras")
MES = cfg.PRINCIPAL
NOMBRE_MES = cfg.nombre_mes(MES)

FONDO, TINTA, TINTA2, TENUE = "#ffffff", "#0b0b0b", "#52514e", "#898781"
REJILLA, BASE = "#e1e0d9", "#c3c2b7"
AZUL, NARANJA, AGUA = "#2a78d6", "#eb6834", "#1baf7a"
RAMPA = LinearSegmentedColormap.from_list("azul", ["#ffffff", "#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"])

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 9.5, "axes.titlesize": 11, "axes.titleweight": "bold",
    "axes.titlelocation": "left", "axes.labelcolor": TINTA2, "axes.edgecolor": BASE, "axes.linewidth": 0.8,
    "xtick.color": TENUE, "ytick.color": TENUE, "xtick.labelcolor": TINTA2, "ytick.labelcolor": TINTA2,
    "axes.grid": False, "figure.facecolor": FONDO, "axes.facecolor": FONDO, "savefig.facecolor": FONDO,
    "legend.frameon": False, "legend.fontsize": 8.5, "text.color": TINTA,
})


def coma(fmt):
    return FuncFormatter(lambda x, _: (fmt % x).replace(".", ","))


def miles(x, _=None):
    return "{:,.0f}".format(x).replace(",", ".")


def ejes(ax, rejilla="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if rejilla:
        ax.grid(axis=rejilla, color=REJILLA, linewidth=0.6)
        ax.set_axisbelow(True)


def guardar(fig, nombre):
    os.makedirs(FIGURAS, exist_ok=True)
    fig.savefig(os.path.join(FIGURAS, nombre), dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("figura:", nombre)


def nombre(n):
    """Nombre de la fuente en tipo título, con las partículas en minúscula y EPS en mayúscula."""
    t = str(n).title()
    for x in (" De ", " Del ", " La ", " Los ", " Y "):
        t = t.replace(x, x.lower())
    return t.replace("Eps", "EPS").replace("Ips", "IPS")


def corto(n, largo=34):
    """Razón social sin la sigla societaria final y recortada a `largo` caracteres. Las cajas de
    compensación se nombran por su sigla final (Comfama, Compensar)."""
    if re.match(r"^CAJA (DE COMPENSACI|COLOMBIANA DE SUBSIDIO)", str(n)):
        return "Caja " + str(n).split()[-1].title()
    t = re.sub(r"\s+(S\.?\s?A\.?\s?S\.?|S\.?\s?A\.?|LTDA\.?|E\.?S\.?E\.?)$", "", str(n).strip(), flags=re.I)
    t = nombre(t)
    return t if len(t) <= largo else t[:largo - 1].rstrip() + "…"


def leer(*partes, **kw):
    return pd.read_csv(os.path.join(*partes), **kw)


# 1 ---------------------------------------------------------------- prestadores exclusivos por EPS
def fig_exclusivos():
    c = leer(TEORIA, "centralidad-eps.csv").query("corte == @MES").sort_values("grado")
    fig, ax = plt.subplots(figsize=(7.2, 7.4))
    y = np.arange(len(c))
    ax.barh(y, c.exclusivos, height=0.62, color=AZUL, zorder=2)
    for yi, e, g in zip(y, c.exclusivos, c.grado):
        ax.annotate("%s (%s %%)" % (miles(e), ("%.0f" % (100 * e / g)).replace(".", ",")), (e, yi), xytext=(3, 0),
                    textcoords="offset points", va="center", fontsize=7.5, color=TINTA2)
    ax.set_yticks(y)
    ax.set_yticklabels([nombre(n) for n in c.nombre])
    ax.set_ylim(-0.7, len(c) - 0.3)
    ax.set_xlim(0, c.exclusivos.max() * 1.2)
    ax.xaxis.set_major_formatter(FuncFormatter(miles))
    ax.set_xlabel("Prestadores que solo reciben giro directo por cuenta de esa EPS (entre paréntesis, % de su cartera)")
    ax.set_title("Prestadores exclusivos de cada EPS, %s" % NOMBRE_MES)
    ejes(ax, "x")
    fig.text(0.01, -0.02, "Las EPS van de mayor (arriba) a menor número de prestadores.", fontsize=8, color=TINTA2)
    fig.tight_layout()
    guardar(fig, "01-exclusivos-por-eps.png")


# 2 ---------------------------------------------------------------- distribución del grado
def fig_grado():
    p = leer(TEORIA, "centralidad-prestadores.csv.gz", dtype={"nit": str}).query("corte == @MES")
    g = p.grado.value_counts().sort_index()
    c = leer(TEORIA, "centralidad-eps.csv").query("corte == @MES").sort_values("grado", ascending=False)
    fig, axs = plt.subplots(1, 2, figsize=(11, 3.6), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axs[0]
    ax.bar(g.index, 100 * g.values / len(p), width=0.62, color=AZUL, zorder=2)
    for k, v in zip(g.index[:3], g.values[:3]):
        ax.annotate(("%.1f %%" % (100 * v / len(p))).replace(".", ","), (k, 100 * v / len(p)), xytext=(0, 3),
                    textcoords="offset points", ha="center", fontsize=7.5, color=TINTA2)
    ax.set_xticks(g.index)
    ax.set_xlabel("EPS que ordenan giro al prestador")
    ax.set_ylabel("% de los prestadores")
    ax.yaxis.set_major_formatter(coma("%.0f"))
    ax.set_title("Prestadores según cuántas EPS ordenan su giro")
    ejes(ax)
    ax = axs[1]
    ax.bar(np.arange(len(c)), c.grado, width=0.7, color=AZUL, zorder=2)
    media = c.grado.sum() / len(c)
    ax.axhline(media, color=NARANJA, lw=2, label="Promedio por EPS: %s" % miles(media))
    ax.set_xticks([])
    ax.set_xlabel("EPS, de mayor a menor")
    ax.set_ylabel("Prestadores con giro por su cuenta")
    ax.yaxis.set_major_formatter(FuncFormatter(miles))
    for i in (0, len(c) - 1):
        ax.annotate("%s: %s" % (nombre(c.nombre.iloc[i]), miles(c.grado.iloc[i])), (i, c.grado.iloc[i]),
                    xytext=(6, 4) if i == 0 else (-2, 22), textcoords="offset points", fontsize=7.5, color=TINTA2,
                    ha="left" if i == 0 else "right")
    ax.set_title("Tamaño de la cartera de cada EPS")
    ax.legend(loc="upper right")
    ejes(ax)
    fig.tight_layout()
    guardar(fig, "02-distribucion-del-grado.png")


# 3 ---------------------------------------------------------------- Lorenz
def fig_lorenz():
    lz = leer(TEORIA, "lorenz.csv").query("corte == @MES")
    co = leer(TEORIA, "concentracion.csv").query("corte == @MES").set_index("lado")
    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    ax.plot([0, 1], [0, 1], color=BASE, lw=1)
    ax.annotate("reparto igual", (0.62, 0.66), rotation=38, fontsize=8, color=TENUE)
    for lado, col, nombre_lado in (("eps", AZUL, "EPS (lo girado por su cuenta)"), ("prestadores", NARANJA, "Prestadores (lo que reciben)")):
        d = lz[lz.lado == lado]
        ax.plot(d.fraccion_nodos, d.fraccion_dinero, color=col, lw=2,
                label="%s · Gini %s" % (nombre_lado, ("%.2f" % co.gini[lado]).replace(".", ",")))
    ax.set_xlabel("Fracción acumulada de actores, de menor a mayor")
    ax.set_ylabel("Fracción acumulada del dinero del mes")
    ax.xaxis.set_major_formatter(coma("%.1f"))
    ax.yaxis.set_major_formatter(coma("%.1f"))
    ax.set_title("Curvas de Lorenz del giro directo, %s" % NOMBRE_MES)
    ax.legend(loc="upper left")
    ejes(ax, "both")
    fig.tight_layout()
    guardar(fig, "03-lorenz.png")


# 4 ---------------------------------------------------------------- fuerza frente a grado
def fig_fuerza_grado():
    r = leer(TEORIA, "fuerza-grado-residuos.csv.gz", dtype={"nit": str})
    sk = leer(TEORIA, "fuerza-grado.csv").query("corte == @MES and lado == 'prestadores'").iloc[0]
    pre = leer(SALIDA, "prestadores-clasificados.csv", dtype=str).set_index("nit")
    rng = np.random.default_rng(1)
    x = r.grado * np.exp(rng.uniform(-0.09, 0.09, len(r)))
    fuera = r.z_modificado.abs() > 3.5
    kmax = int(r.grado.max())
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    ax.scatter(x[~fuera], r.fuerza[~fuera] / 1e6, s=6, color=AZUL, alpha=0.35, linewidth=0, label="Prestador")
    ax.scatter(x[fuera], r.fuerza[fuera] / 1e6, s=30, color=NARANJA, edgecolor=FONDO, linewidth=1.2, zorder=3,
               label="Muy por encima de la curva (z modificado > 3,5)")
    kk = np.array([1, kmax])
    ax.plot(kk, 10 ** (sk.intercepto_log10 + sk.exponente_beta * np.log10(kk)) / 1e6, color=TINTA2, lw=2,
            label="s(k) ∝ k^%s (IC 95 %%: %s–%s)" % tuple(("%.2f" % v).replace(".", ",") for v in (sk.exponente_beta, sk.ic95_inferior, sk.ic95_superior)))
    # etiquetas apiladas en la franja vacía por encima de todos los puntos, con línea guía al punto real
    top = r[fuera].nlargest(5, "fuerza")
    tope = r.fuerza.max() / 1e6
    columnas = ((top[top.grado <= 2], 1.12), (top[top.grado > 2], 3.3))
    for grupo, x0 in columnas:
        for i, (idx, t) in enumerate(grupo.sort_values("fuerza", ascending=False).iterrows()):
            ax.annotate(corto(pre.razon_social.get(t.nit, t.nit)), (x[idx], t.fuerza / 1e6),
                        xytext=(x0, tope * 8 / (1.8 ** i)), textcoords="data", fontsize=7.5, color=TINTA2, va="center",
                        arrowprops=dict(arrowstyle="-", color=BASE, lw=0.8, shrinkA=2, shrinkB=3))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(0.5, tope * 14)
    ax.set_xticks([k for k in (1, 2, 3, 5, 10) if k < kmax] + [kmax])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: "%d" % v))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: miles(v)))
    ax.set_xlabel("EPS que ordenan su giro (escala logarítmica; puntos separados un poco para que se vean)")
    ax.set_ylabel("Giro directo recibido en el mes (millones de pesos)")
    ax.set_title("Lo que recibe cada prestador frente a cuántas EPS ordenan su giro, %s" % NOMBRE_MES)
    ax.legend(loc="lower right")
    ejes(ax, "both")
    fig.tight_layout()
    guardar(fig, "04-fuerza-grado.png")


# 5 ---------------------------------------------------------------- correlaciones de grado
def fig_knn():
    p = leer(TEORIA, "centralidad-prestadores.csv.gz", dtype={"nit": str}).query("corte == @MES")
    k = (p.groupby("grado").agg(prestadores=("nit", "size"), knn_medio=("knn", "mean"))
         .reset_index().rename(columns={"grado": "grado_prestador"}))
    k.insert(0, "corte", MES)
    k.to_csv(os.path.join(TEORIA, "knn-por-grado.csv"), index=False, encoding="utf-8-sig",
             lineterminator="\n")
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(k.grado_prestador, k.knn_medio, color=AZUL, lw=2, marker="o", ms=5, mec=FONDO, mew=1.2, zorder=3)
    ax.set_xticks(k.grado_prestador)
    ax.set_xlabel("EPS que ordenan giro al prestador")
    ax.set_ylabel("Tamaño medio de sus EPS (prestadores)")
    ax.yaxis.set_major_formatter(FuncFormatter(miles))
    ax.set_ylim(0, k.knn_medio.max() * 1.1)
    ax.set_title("Tamaño medio de las EPS de cada prestador, según cuántas ordenan su giro, %s" % NOMBRE_MES)
    ejes(ax)
    fig.text(0.01, -0.02, "Cada punto promedia, entre los prestadores con ese número de EPS, el tamaño de la cartera de sus EPS.",
             fontsize=8, color=TINTA2)
    fig.tight_layout()
    guardar(fig, "05-correlaciones-de-grado.png")


# 6 ---------------------------------------------------------------- dependencia
def fig_dependencia():
    d = leer(TEORIA, "distribucion-dependencia.csv").query("corte == @MES")
    d = d[d.umbral_parte_eps_principal >= 0.25]
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.plot(100 * d.umbral_parte_eps_principal, d.prestadores_pct, color=AZUL, lw=2, marker="o", ms=4.5, mec=FONDO, mew=1, label="% de los prestadores")
    ax.plot(100 * d.umbral_parte_eps_principal, d.dinero_pct, color=NARANJA, lw=2, marker="o", ms=4.5, mec=FONDO, mew=1, label="% del dinero del mes")
    for u in (0.5, 0.95, 1.0):
        v = d[np.isclose(d.umbral_parte_eps_principal, u)].prestadores_pct.iloc[0]
        ax.annotate(("%.1f %%" % v).replace(".", ","), (100 * u, v), xytext=(0, 9) if u < 1 else (0, -15),
                    textcoords="offset points", fontsize=8, color=TINTA2, ha="center")
    ax.set_xlabel("Parte del giro directo del prestador que le da su EPS principal (al menos, %)")
    ax.set_ylabel("%")
    ax.set_ylim(0, 104)
    ax.set_title("Dependencia de los prestadores de una sola EPS, %s" % NOMBRE_MES)
    ax.legend(loc="lower left")
    ejes(ax)
    fig.tight_layout()
    guardar(fig, "06-dependencia.png")


# 7 ---------------------------------------------------------------- regla de la red pública
def fig_regla_ese():
    s = leer(CONTRASTE, "regla-ese-subsidiado.csv").query("corte == @MES and girado_subsidiado > 1e9").sort_values("a_ese_pct")
    fig, ax = plt.subplots(figsize=(7.2, 6.4))
    y = np.arange(len(s))
    ax.barh(y, s.a_ese_pct, height=0.62, color=AZUL, zorder=2)
    for yi, v in zip(y, s.a_ese_pct):
        ax.annotate(("%.0f %%" % v).replace(".", ","), (v, yi), xytext=(3, 0), textcoords="offset points", va="center", fontsize=7.5, color=TINTA2)
    ax.axvline(60, color=TINTA2, lw=1.2)
    ax.annotate("60 %: mínimo del art. 16 de la Ley 1122 de 2007, como referencia", (60, -1.15), xytext=(4, 0),
                textcoords="offset points", fontsize=8, color=TINTA2, va="center")
    ax.set_ylim(-1.7, len(s) - 0.4)
    ax.set_yticks(y)
    ax.set_yticklabels([nombre(n) for n in s.nombre])
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(coma("%.0f"))
    ax.set_xlabel("% del giro directo del régimen subsidiado que llega a empresas sociales del Estado (ESE)")
    ax.set_title("Giro directo del subsidiado que llega a la red pública, %s" % NOMBRE_MES)
    ejes(ax, "x")
    fig.tight_layout()
    guardar(fig, "07-giro-subsidiado-a-ese.png")


# 8 ---------------------------------------------------------------- EPS × comunidad
def fig_comunidades():
    nod = leer(TEORIA, "comunidades-nodos.csv.gz", dtype={"id": str}).query("corte == @MES")
    comp = leer(TEORIA, "comunidades-composicion.csv").query("corte == @MES").set_index("comunidad")
    a = leer(SALIDA, "aristas-red-observada.csv.gz", dtype={"nit": str}).query("corte == @MES and girado > 0")
    ent = leer(SALIDA, "eps-entidades.csv", dtype=str).drop_duplicates("entidad").set_index("entidad").nombre_entidad
    com_p = nod[nod.lado == "prestador"].set_index("id").comunidad_ponderada
    com_e = nod[nod.lado == "eps"].set_index("id").comunidad_ponderada
    a = a.assign(comunidad=a.nit.map(com_p))
    m = a.pivot_table(index="entidad", columns="comunidad", values="girado", aggfunc="sum", fill_value=0)
    m = 100 * m.div(m.sum(axis=1), axis=0)
    orden_c = comp.sort_values("dinero_recibido", ascending=False).index.tolist()
    orden_e = sorted(m.index, key=lambda e: (orden_c.index(com_e[e]), -a[a.entidad == e].girado.sum()))
    m = m.reindex(index=orden_e, columns=orden_c).fillna(0)
    m.rename(index=ent).to_csv(os.path.join(TEORIA, "comunidades-matriz-eps.csv"), encoding="utf-8-sig",
                               lineterminator="\n")
    etiqueta = lambda c: comp.departamentos_principales[c].split(";")[0].split(" (")[0]
    fig, ax = plt.subplots(figsize=(8.6, 7.6))
    ax.pcolormesh(np.arange(len(orden_c) + 1), np.arange(len(orden_e) + 1), m.values, cmap=RAMPA, vmin=0, vmax=100,
                  edgecolors=FONDO, linewidth=2)
    for i in range(len(orden_e)):
        for j in range(len(orden_c)):
            v = m.values[i, j]
            if v >= 25:
                ax.text(j + 0.5, i + 0.5, "%d" % round(v), ha="center", va="center", fontsize=7.5,
                        color="#ffffff" if v >= 55 else TINTA)
    ax.set_xticks(np.arange(len(orden_c)) + 0.5)
    ax.set_xticklabels(["C%d · %s" % (k + 1, etiqueta(c)) for k, c in enumerate(orden_c)], rotation=40, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(orden_e)) + 0.5)
    ax.set_yticklabels([nombre(ent.get(e, e)) for e in orden_e], fontsize=8)
    ax.invert_yaxis()
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("A qué comunidad va lo girado por cuenta de cada EPS (%%), %s" % NOMBRE_MES)
    fig.text(0.01, -0.02, "Comunidades: modularidad bipartita ponderada por el dinero (Barber). Cada columna lleva el departamento\n"
                          "que más recibe en ella. Se muestran los valores desde el 25 %.", fontsize=8, color=TINTA2)
    fig.tight_layout()
    guardar(fig, "08-comunidades-eps.png")


if __name__ == "__main__":
    fig_exclusivos()
    fig_grado()
    fig_lorenz()
    fig_fuerza_grado()
    fig_knn()
    fig_dependencia()
    fig_regla_ese()
    fig_comunidades()
