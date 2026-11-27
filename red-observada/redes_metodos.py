# -*- coding: utf-8 -*-
"""
Métodos de teoría de redes para la red bipartita EPS → prestador.

Módulo que usan teoria-redes-observada.py, contraste-y-acoplamiento.py y
proyecciones-y-comparacion.py. Lo que NetworkX no trae se implementa aquí y se prueba en
verificar-metodos.py contra casos con respuesta conocida antes de usarlo con los datos:

  - matriz de biadyacencia: filas = EPS, columnas = prestadores (1 si la EPS le giró en el mes);
  - asortatividad bipartita (Newman, 2002 y 2003): correlación, sobre las aristas, entre el grado
    de la EPS y el del prestador;
  - grado medio de los vecinos (knn);
  - modularidad bipartita de Barber (2007) y su optimización con BRIM, más un paso de fusión de
    comunidades, desde varios arranques;
  - comparación de particiones: información mutua normalizada (Danon et al., 2005) e índice de
    Rand ajustado (Hubert y Arabie, 1985);
  - valor p de una prueba de permutación (Phipson y Smyth, 2010);
  - coeficiente de Gini, curva de Lorenz y heterogeneidad del grado.

Convenciones: las matrices son arreglos de NumPy; la binaria es booleana; las etiquetas de
comunidad son enteros 0..c-1.
"""

import numpy as np

# ---------------------------------------------------------------- matrices


def biadyacencia(filas_idx, cols_idx, n_filas, n_cols, pesos=None):
    """Matriz booleana (y la ponderada, si hay pesos) a partir de las listas de aristas."""
    B = np.zeros((n_filas, n_cols), dtype=bool)
    B[filas_idx, cols_idx] = True
    if pesos is None:
        return B
    W = np.zeros((n_filas, n_cols), dtype=float)
    np.add.at(W, (filas_idx, cols_idx), pesos)
    return B, W


# ---------------------------------------------------------------- correlaciones de grado


def asortatividad(M, rangos=False):
    """Asortatividad bipartita: correlación de Pearson, sobre las aristas, entre el grado de la
    fila (EPS) y el de la columna (prestador). Es la asortatividad dirigida de Newman (2003)
    —grado de salida del origen frente a grado de entrada del destino— porque todas las aristas
    van de EPS a prestador. Con rangos=True, la misma correlación sobre los rangos de los grados
    en la lista de aristas (versión de Spearman)."""
    M = np.asarray(M, dtype=bool)
    kf = M.sum(1).astype(float)
    kc = M.sum(0).astype(float)
    i, j = np.nonzero(M)
    x, y = kf[i], kc[j]
    if rangos:
        from scipy.stats import rankdata
        x, y = rankdata(x), rankdata(y)
    x = x - x.mean()
    y = y - y.mean()
    den = np.sqrt((x * x).sum() * (y * y).sum())
    return float((x * y).sum() / den) if den > 0 else float("nan")


def knn(M):
    """Grado medio de los vecinos: para cada fila, el grado medio de sus columnas, y para cada
    columna, el grado medio de sus filas."""
    M = np.asarray(M, dtype=float)
    kf, kc = M.sum(1), M.sum(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        knn_f = (M @ kc) / kf
        knn_c = (M.T @ kf) / kc
    return knn_f, knn_c


# ---------------------------------------------------------------- modularidad bipartita


def matriz_modularidad(A):
    """Matriz de modularidad bipartita de Barber (2007): B = A - k d^T / m, donde k son los grados
    (o fuerzas) de las filas, d los de las columnas y m el total. Solo une filas con columnas."""
    A = np.asarray(A, dtype=float)
    m = A.sum()
    return A - np.outer(A.sum(1), A.sum(0)) / m, m


def _una_caliente(lab, c):
    S = np.zeros((lab.size, c))
    S[np.arange(lab.size), lab] = 1.0
    return S


def _compactar(lab_f, lab_c):
    usadas = np.unique(np.concatenate([lab_f, lab_c]))
    mapa = -np.ones(usadas.max() + 1, dtype=int)
    mapa[usadas] = np.arange(usadas.size)
    return mapa[lab_f], mapa[lab_c], usadas.size


def modularidad(Bm, m, lab_f, lab_c):
    """Q de Barber para una partición (etiquetas de filas y de columnas)."""
    c = int(max(lab_f.max(), lab_c.max())) + 1
    R = Bm @ _una_caliente(lab_c, c)
    return float(R[np.arange(lab_f.size), lab_f].sum() / m)


def modularidad_por_pares(A, lab_f, lab_c):
    """Definición literal de Q de Barber (lenta). Solo para verificar."""
    A = np.asarray(A, dtype=float)
    m = A.sum()
    k, d = A.sum(1), A.sum(0)
    q = 0.0
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            if lab_f[i] == lab_c[j]:
                q += A[i, j] - k[i] * d[j] / m
    return q / m


def brim(Bm, m, lab_c, max_iter=500):
    """BRIM (Barber, 2007): con las columnas fijas, cada fila va a la comunidad que más le suma;
    con las filas fijas, lo mismo para las columnas; se repite hasta que Q no sube. Cada medio
    paso es la mejor asignación exacta de un lado dado el otro, así que Q nunca baja."""
    lab_c = np.asarray(lab_c).copy()
    c = int(lab_c.max()) + 1
    q_ant = -np.inf
    lab_f = None
    for _ in range(max_iter):
        R = Bm @ _una_caliente(lab_c, c)
        lab_f = R.argmax(1)
        T = Bm.T @ _una_caliente(lab_f, c)
        nuevo_c = T.argmax(1)
        q = float(T[np.arange(nuevo_c.size), nuevo_c].sum() / m)
        lab_c = nuevo_c
        if q <= q_ant + 1e-12:
            break
        q_ant = q
    lab_f, lab_c, _ = _compactar(lab_f, lab_c)
    return modularidad(Bm, m, lab_f, lab_c), lab_f, lab_c


def fusionar(Bm, m, lab_f, lab_c):
    """Une, mientras suba Q, el par de comunidades que más la aumenta."""
    lab_f, lab_c, c = _compactar(lab_f, lab_c)
    while c > 1:
        C = _una_caliente(lab_f, c).T @ Bm @ _una_caliente(lab_c, c)
        G = C + C.T
        np.fill_diagonal(G, -np.inf)
        g, h = np.unravel_index(np.argmax(G), G.shape)
        if G[g, h] / m <= 1e-12:
            break
        lab_f = np.where(lab_f == h, g, lab_f)
        lab_c = np.where(lab_c == h, g, lab_c)
        lab_f, lab_c, c = _compactar(lab_f, lab_c)
    return modularidad(Bm, m, lab_f, lab_c), lab_f, lab_c


def _refinar(Bm, m, lab_c):
    """BRIM, fusión y BRIM otra vez, hasta que Q deja de subir."""
    q, lf, lc = brim(Bm, m, lab_c)
    while True:
        q2, lf2, lc2 = fusionar(Bm, m, lf, lc)
        q3, lf3, lc3 = brim(Bm, m, lc2)
        if q3 <= q + 1e-12:
            return q, lf, lc
        q, lf, lc = q3, lf3, lc3


def optimizar_modularidad(A, rng, arranques=30, c_max=None, iniciales=()):
    """Busca la partición de máxima Q de Barber.

    Procedimiento fijo: un arranque en que
    cada fila es su propia comunidad, más `arranques` arranques con columnas en c comunidades al
    azar (c uniforme entre 2 y c_max); en cada uno, BRIM con fusión de comunidades. Se queda con
    la mejor Q. `iniciales` admite etiquetas de columnas adicionales (por ejemplo, de Louvain).
    Devuelve (Q, etiquetas de filas, etiquetas de columnas)."""
    Bm, m = matriz_modularidad(A)
    nf, nc = Bm.shape
    c_max = c_max or nf
    # arranque determinista: cada fila sola; las columnas van a su mejor fila
    lab_f0 = np.arange(nf)
    T = Bm.T @ _una_caliente(lab_f0, nf)
    candidatos = [T.argmax(1)]
    for _ in range(arranques):
        c = int(rng.integers(2, c_max + 1))
        candidatos.append(rng.integers(c, size=nc))
    candidatos.extend(np.asarray(x) for x in iniciales)
    mejor = (-np.inf, None, None)
    for lab_c in candidatos:
        res = _refinar(Bm, m, lab_c)
        if res[0] > mejor[0] + 1e-12:
            mejor = res
    return mejor


def asignar_filas(Bm, lab_c):
    """Mejor asignación de las filas dadas las etiquetas de columnas (medio paso de BRIM)."""
    c = int(lab_c.max()) + 1
    return (Bm @ _una_caliente(lab_c, c)).argmax(1)


# ---------------------------------------------------------------- comparación de particiones


def _contingencia(a, b):
    _, ia = np.unique(a, return_inverse=True)
    _, ib = np.unique(b, return_inverse=True)
    N = np.zeros((ia.max() + 1, ib.max() + 1))
    np.add.at(N, (ia, ib), 1)
    return N


def nmi(a, b):
    """Información mutua normalizada de Danon et al. (2005): 2 I(A;B) / (H(A) + H(B))."""
    N = _contingencia(a, b)
    n = N.sum()
    fa, fb = N.sum(1), N.sum(0)
    nz = N > 0
    I = (N[nz] / n * np.log(N[nz] * n / np.outer(fa, fb)[nz])).sum()
    Ha = -(fa / n * np.log(fa / n)).sum()
    Hb = -(fb / n * np.log(fb / n)).sum()
    if Ha + Hb == 0:
        return 1.0
    return float(2 * I / (Ha + Hb))


def ari(a, b):
    """Índice de Rand ajustado de Hubert y Arabie (1985)."""
    N = _contingencia(a, b)
    comb = lambda x: x * (x - 1) / 2
    n = N.sum()
    s_ij = comb(N).sum()
    s_a = comb(N.sum(1)).sum()
    s_b = comb(N.sum(0)).sum()
    esperado = s_a * s_b / comb(n)
    maximo = (s_a + s_b) / 2
    if maximo == esperado:
        return 1.0
    return float((s_ij - esperado) / (maximo - esperado))


def ari_por_pares(a, b):
    """ARI contando pares uno a uno (lento). Solo para verificar."""
    n = len(a)
    acuerdo = {"11": 0, "10": 0, "01": 0, "00": 0}
    for i in range(n):
        for j in range(i + 1, n):
            x, y = a[i] == a[j], b[i] == b[j]
            acuerdo[("1" if x else "0") + ("1" if y else "0")] += 1
    total = n * (n - 1) / 2
    n11, n10, n01 = acuerdo["11"], acuerdo["10"], acuerdo["01"]
    esperado = (n11 + n10) * (n11 + n01) / total
    maximo = ((n11 + n10) + (n11 + n01)) / 2
    return (n11 - esperado) / (maximo - esperado)


# ---------------------------------------------------------------- permutaciones


def p_empirico(obs, permutados, cola="dos"):
    """Valor p de una prueba de permutación, con la corrección de Phipson y Smyth (2010):
    (b + 1) / (n + 1), donde b cuenta los valores permutados al menos tan extremos como el
    observado. cola: 'mayor', 'menor' o 'dos' (dos colas, por distancia a la media)."""
    permutados = np.asarray(permutados, dtype=float)
    n = permutados.size
    if cola == "mayor":
        b = int((permutados >= obs).sum())
    elif cola == "menor":
        b = int((permutados <= obs).sum())
    else:
        mu = permutados.mean()
        b = int((np.abs(permutados - mu) >= abs(obs - mu) - 1e-12).sum())
    return (b + 1) / (n + 1)


# ---------------------------------------------------------------- desigualdad


def gini(x):
    """Coeficiente de Gini de valores no negativos (0 = todos iguales; (n-1)/n = uno lo tiene
    todo)."""
    x = np.sort(np.asarray(x, dtype=float))
    n = x.size
    if n == 0 or x.sum() == 0:
        return float("nan")
    i = np.arange(1, n + 1)
    return float(2 * (i * x).sum() / (n * x.sum()) - (n + 1) / n)


def gini_por_pares(x):
    """Gini por la diferencia media absoluta (lento). Solo para verificar."""
    x = np.asarray(x, dtype=float)
    return float(np.abs(x[:, None] - x[None, :]).sum() / (2 * x.size ** 2 * x.mean()))


def lorenz(x):
    """Curva de Lorenz: (fracción acumulada de nodos, fracción acumulada del total), de menor a
    mayor."""
    x = np.sort(np.asarray(x, dtype=float))
    return (np.concatenate([[0], np.arange(1, x.size + 1) / x.size]),
            np.concatenate([[0], np.cumsum(x) / x.sum()]))


def heterogeneidad(k):
    """<k^2>/<k> y <k^2>/<k>^2 de una secuencia de grados."""
    k = np.asarray(k, dtype=float)
    return float((k ** 2).mean() / k.mean()), float((k ** 2).mean() / k.mean() ** 2)
