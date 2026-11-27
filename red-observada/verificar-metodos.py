# -*- coding: utf-8 -*-
"""
Verificación de los métodos de redes_metodos.py.

Cada método se compara con un caso de respuesta conocida o con su definición literal, que es lenta
pero no deja lugar a dudas. Si una prueba no cuadra, el programa termina con código 1 y
correr-todo.py se detiene antes del análisis.

  1. asortatividad: igual a la de NetworkX (dirigida, salida→entrada) y a Spearman de SciPy;
  2. modularidad de Barber: igual a la definición por pares; 1 - 1/c en c bloques completos
     disjuntos; el optimizador recupera una partición sembrada;
  3. NMI y ARI: 1 en particiones idénticas; ARI igual al conteo de pares; NMI igual a una
     implementación independiente;
  4. Gini, valor p de permutación y heterogeneidad: casos calculados a mano.

Salida: salida/teoria-redes/verificacion-metodos.txt
Ejecutar:  python verificar-metodos.py
"""

import io
import os
import sys

import networkx as nx
import numpy as np
from scipy.stats import spearmanr

import configuracion as cfg
import redes_metodos as rm

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SALIDA = os.path.join(cfg.SALIDA, "teoria-redes")
RESULTADOS = []


def prueba(nombre, condicion, detalle=""):
    RESULTADOS.append((nombre, bool(condicion), detalle))
    print(("OK    " if condicion else "FALLA ") + nombre + ("  · " + detalle if detalle else ""))


def main():
    os.makedirs(SALIDA, exist_ok=True)
    rng = np.random.default_rng(20261104)

    # ---------------------------------------------------------------- 1. asortatividad
    X = rng.random((20, 50)) < 0.15
    X = X[X.any(1)][:, X.any(0)]
    D = nx.DiGraph()
    D.add_edges_from((("E", i), ("P", j)) for i, j in zip(*np.nonzero(X)))
    r_nx = nx.degree_pearson_correlation_coefficient(D, x="out", y="in")
    prueba("asortatividad = NetworkX dirigida (salida→entrada)",
           np.isclose(rm.asortatividad(X), r_nx, atol=1e-10), "%.6f frente a %.6f" % (rm.asortatividad(X), r_nx))
    i, j = np.nonzero(X)
    r_sp = spearmanr(X.sum(1)[i], X.sum(0)[j]).statistic
    prueba("asortatividad por rangos = Spearman de SciPy sobre las aristas",
           np.isclose(rm.asortatividad(X, rangos=True), r_sp, atol=1e-10))

    # ---------------------------------------------------------------- 2. modularidad de Barber
    iguales = True
    for _ in range(10):
        A = (rng.random((7, 12)) < 0.4) * rng.random((7, 12)) * 10
        if not (A.sum(1) > 0).all() or not (A.sum(0) > 0).all():
            continue
        lf, lc = rng.integers(3, size=7), rng.integers(3, size=12)
        Bm, m = rm.matriz_modularidad(A)
        iguales &= np.isclose(rm.modularidad(Bm, m, lf, lc), rm.modularidad_por_pares(A, lf, lc))
        Ab = A > 0
        Bm, m = rm.matriz_modularidad(Ab)
        iguales &= np.isclose(rm.modularidad(Bm, m, lf, lc), rm.modularidad_por_pares(Ab, lf, lc))
    prueba("Q de Barber = definición por pares (binaria y ponderada)", iguales)
    c = 4
    A = np.kron(np.eye(c), np.ones((3, 5))).astype(bool)
    q, lf, lc = rm.optimizar_modularidad(A, rng, arranques=20)
    prueba("Q = 1 - 1/c en c bloques completos y el optimizador lo encuentra",
           np.isclose(q, 1 - 1 / c), "Q = %.6f" % q)
    verdad_f = np.repeat(np.arange(4), 3)
    verdad_c = np.repeat(np.arange(4), 15)
    # caso limpio: la partición sembrada es la óptima y debe recuperarse exacta
    P = np.where(verdad_f[:, None] == verdad_c[None, :], 0.9, 0.01)
    A = rng.random(P.shape) < P
    q, lf, lc = rm.optimizar_modularidad(A, rng, arranques=30)
    acuerdo = rm.nmi(np.concatenate([lf, lc + 100]), np.concatenate([verdad_f, verdad_c + 100]))
    prueba("el optimizador recupera exacta una partición sembrada nítida (NMI = 1)", np.isclose(acuerdo, 1),
           "NMI = %.3f, Q = %.3f" % (acuerdo, q))
    # caso con ruido: la sembrada ya no tiene por qué ser la óptima; lo hallado no puede ser peor
    ok_q, ok_inicio = True, True
    for _ in range(5):
        P = np.where(verdad_f[:, None] == verdad_c[None, :], 0.6, 0.05)
        A = rng.random(P.shape) < P
        Bm, m = rm.matriz_modularidad(A)
        q_sembrada = rm.modularidad(Bm, m, verdad_f, verdad_c)
        q, lf, lc = rm.optimizar_modularidad(A, rng, arranques=30)
        q_desde = rm.optimizar_modularidad(A, rng, arranques=0, iniciales=[verdad_c])[0]
        ok_q &= q >= q_sembrada - 1e-9
        ok_inicio &= q_desde <= q + 1e-9
    prueba("con ruido, la Q hallada nunca es menor que la de la partición sembrada", ok_q)
    prueba("arrancar desde la partición sembrada no supera la búsqueda al azar", ok_inicio)
    Bm, m = rm.matriz_modularidad(A)
    l0 = rng.integers(5, size=A.shape[1])
    q0 = rm.modularidad(Bm, m, rm.asignar_filas(Bm, l0), l0)
    q1 = rm.brim(Bm, m, l0)[0]
    prueba("BRIM nunca baja la modularidad", q1 >= q0 - 1e-12, "%.4f → %.4f" % (q0, q1))

    # ---------------------------------------------------------------- 3. NMI y ARI
    a = rng.integers(5, size=60)
    b = (a + 2) % 5
    prueba("NMI = 1 y ARI = 1 en particiones idénticas con otras etiquetas",
           np.isclose(rm.nmi(a, b), 1) and np.isclose(rm.ari(a, b), 1))
    iguales = True
    for _ in range(10):
        a, b = rng.integers(4, size=40), rng.integers(3, size=40)
        iguales &= np.isclose(rm.ari(a, b), rm.ari_por_pares(a, b))
    prueba("ARI = conteo de pares uno a uno", iguales)

    def nmi_directa(a, b):
        n = len(a)
        H = lambda x: -sum((list(x).count(v) / n) * np.log(list(x).count(v) / n) for v in set(x))
        I = 0.0
        for u in set(a):
            for v in set(b):
                nuv = sum(1 for x, y in zip(a, b) if x == u and y == v)
                if nuv:
                    I += nuv / n * np.log(nuv * n / (list(a).count(u) * list(b).count(v)))
        return 2 * I / (H(a) + H(b))
    iguales = True
    for _ in range(10):
        a, b = rng.integers(4, size=30), rng.integers(3, size=30)
        iguales &= np.isclose(rm.nmi(a, b), nmi_directa(a, b))
    prueba("NMI = implementación independiente", iguales)
    prueba("NMI = 0 en particiones independientes de cuatro elementos",
           np.isclose(rm.nmi([0, 0, 1, 1], [0, 1, 0, 1]), 0))

    # ---------------------------------------------------------------- 4. desigualdad y permutaciones
    x = rng.random(50) * 100
    prueba("Gini = diferencia media absoluta", np.isclose(rm.gini(x), rm.gini_por_pares(x)))
    prueba("Gini = 0 con valores iguales y (n-1)/n si uno tiene todo",
           np.isclose(rm.gini(np.ones(10)), 0) and np.isclose(rm.gini([0] * 9 + [5]), 0.9))
    prueba("p de permutación = 1/(n+1) si el observado supera a todos los permutados",
           np.isclose(rm.p_empirico(100, np.arange(99), cola="mayor"), 0.01))
    prueba("p de permutación de dos colas = 1 si el observado es la media de los permutados",
           np.isclose(rm.p_empirico(49, np.arange(99), cola="dos"), 1.0))
    prueba("heterogeneidad = 1 con grados iguales", np.allclose(rm.heterogeneidad([2, 2, 2]), (2, 1)))

    fallas = [n for n, ok, _ in RESULTADOS if not ok]
    texto = "Verificación de redes_metodos.py — %d pruebas, %d fallas\n\n" % (len(RESULTADOS), len(fallas))
    texto += "\n".join(("OK    " if ok else "FALLA ") + n + ("  · " + d if d else "") for n, ok, d in RESULTADOS)
    with io.open(os.path.join(SALIDA, "verificacion-metodos.txt"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(texto + "\n")
    if fallas:
        print("\nFALLAN: " + "; ".join(fallas))
        sys.exit(1)
    print("\nTodas las pruebas pasan.")


if __name__ == "__main__":
    main()
