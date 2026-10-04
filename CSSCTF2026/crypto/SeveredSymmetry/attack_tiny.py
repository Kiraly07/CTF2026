#!/usr/bin/env python3
"""Recover span(Q) on a tiny key via isotropic XL, then decrypt."""
import importlib.util
import itertools
import random
import time
from collections import Counter, defaultdict

spec = importlib.util.spec_from_file_location('src', 'source.py')
src = importlib.util.module_from_spec(spec)
spec.loader.exec_module(src)


def rref(matrix, columns, p):
    rows = [[v % p for v in row] for row in matrix]
    pivots = []
    for col in range(columns):
        pivot = next((i for i in range(len(pivots), len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        k = len(pivots)
        rows[k], rows[pivot] = rows[pivot], rows[k]
        inv = pow(rows[k][col], -1, p)
        rows[k] = [v * inv % p for v in rows[k]]
        for i in range(len(rows)):
            if i != k and rows[i][col]:
                f = rows[i][col]
                rows[i] = [(a - f * b) % p for a, b in zip(rows[i], rows[k])]
        pivots.append(col)
    return rows, pivots


def nullspace(matrix, p):
    cols = len(matrix[0])
    rows, pivots = rref([row[:] for row in matrix], cols, p)
    free = [j for j in range(cols) if j not in pivots]
    basis = []
    for f in free:
        v = [0] * cols
        v[f] = 1
        for i, pv in enumerate(pivots):
            v[pv] = (-rows[i][f]) % p
        basis.append(v)
    return basis


def mat_rank(rows, p):
    if not rows:
        return 0
    return len(rref([r[:] for r in rows], len(rows[0]), p)[1])


def main():
    t0 = time.time()
    rng = random.Random(2)
    p, n, m, t, s = 17, 9, 11, 3, 2
    pub, priv = src.keygen(p=p, n=n, m=m, t=t, s=s, rng=rng)
    polys = src.unpack(pub['polynomials'])
    qmap = src.unpack(priv['q'])
    A2inv = priv['A2_inverse']
    v = n - t
    D = v * (v + 1) // 2

    m4 = [(a, b, c, d)
          for a in range(v) for b in range(a, v)
          for c in range(b, v) for d in range(c, v)]
    m2 = [(a, b) for a in range(v) for b in range(a, v)]
    m4_index = {mon: i for i, mon in enumerate(m4)}
    m2_index = {mon: i for i, mon in enumerate(m2)}
    N4 = len(m4)

    def product_lookup(a, b):
        return m4_index[tuple(sorted(m2[a] + m2[b]))]

    def quad_part(poly):
        return {mm: c for mm, c in poly.items() if len(mm) == 2}

    def q_to_vec(qpoly):
        vec = [0] * D
        for mon, c in quad_part(qpoly).items():
            idx = m2_index[tuple(sorted(mon))]
            vec[idx] = (vec[idx] + c) % p
        return vec

    def eval_deg4(poly, x):
        tot = 0
        for mon, c in poly.items():
            if len(mon) == 4:
                term = c
                for i in mon:
                    term = term * x[i] % p
                tot = (tot + term) % p
        return tot

    def affine(A, b, vec):
        return [(sum(aa * x for aa, x in zip(row, vec)) + c) % p
                for row, c in zip(A, b)]

    def solve_section(y):
        return affine(A2inv, [0] * n, [0] * t + y)

    # Interpolate public H4 in y-coords
    samples_y, samples_P = [], []
    for _ in range(N4 + 5):
        y = [rng.randrange(p) for _ in range(v)]
        x = solve_section(y)
        p4 = [eval_deg4(poly, x) for poly in polys]
        row = []
        for mon in m4:
            term = 1
            for idx in mon:
                term = term * y[idx] % p
            row.append(term)
        samples_y.append(row)
        samples_P.append(p4)

    H4 = []
    for o in range(m):
        mat = [samples_y[i] + [samples_P[i][o]] for i in range(len(samples_y))]
        rows, piv = rref(mat, N4, p)
        sol = [0] * N4
        for i, pv in enumerate(piv):
            sol[pv] = rows[i][N4]
        H4.append(sol)

    Vr, Vp = rref([r[:] for r in H4], N4, p)
    Vbasis = Vr[:len(Vp)]
    Vperp = nullspace(Vbasis, p)
    print('dim V', len(Vp), 'dim Vperp', len(Vperp), 't=', time.time() - t0)

    def M_from_L(L):
        return [[L[product_lookup(a, b)] for b in range(D)] for a in range(D)]

    Ms = [M_from_L(L) for L in Vperp]
    Mbasis, Mbasis_vecs = [], []
    for M in Ms:
        Mv = [M[a][b] for a in range(D) for b in range(D)]
        if len(rref(Mbasis_vecs + [Mv], D * D, p)[1]) > len(Mbasis_vecs):
            Mbasis.append(M)
            Mbasis_vecs.append(Mv)
    print('dim M', len(Mbasis), 't=', time.time() - t0)

    # Permute so true S has pivot-first chart (for verification); for attack we try random perms
    Qvecs = [q_to_vec(q) for q in qmap]
    Ar, Ap = rref([row[:] for row in Qvecs], D, p)
    perm = Ap + [j for j in range(D) if j not in Ap]
    print('true Q pivots', Ap)

    def permute_M(M):
        return [[M[perm[i]][perm[j]] for j in range(D)] for i in range(D)]

    Ms_perm = [permute_M(M) for M in Mbasis]

    # Build quadratic eqs for W in chart X=[I|W]
    nW = t * (D - t)
    print('nW', nW)

    def widx(i, k):
        return i * (D - t) + k

    # Represent each eq as poly dict: mon tuple sorted -> coeff
    def factor_X(row, col):
        if col < t:
            return ('I', None) if col == row else None
        return ('W', (row, col - t))

    polys_eq = []
    for M in Ms_perm:
        for i in range(t):
            for j in range(i, t):
                poly = defaultdict(int)
                for a in range(D):
                    for b in range(D):
                        mab = M[a][b]
                        if not mab:
                            continue
                        fa = factor_X(i, a)
                        fb = factor_X(j, b)
                        if fa is None or fb is None:
                            continue
                        # multiply factors
                        parts = []
                        if fa[0] == 'W':
                            parts.append(widx(*fa[1]))
                        if fb[0] == 'W':
                            parts.append(widx(*fb[1]))
                        mon = tuple(sorted(parts))
                        poly[mon] = (poly[mon] + mab) % p
                # drop zero
                poly = {k: c for k, c in poly.items() if c}
                if poly:
                    polys_eq.append(poly)

    print('num quadratic eqs', len(polys_eq), 't=', time.time() - t0)

    # XL at degree 3
    mons3 = []
    mons3.append(())
    for i in range(nW):
        mons3.append((i,))
    for a, b in itertools.combinations_with_replacement(range(nW), 2):
        mons3.append((a, b))
    for a, b, c in itertools.combinations_with_replacement(range(nW), 3):
        mons3.append((a, b, c))
    mons3_index = {mon: i for i, mon in enumerate(mons3)}
    print('mons <=3', len(mons3))

    def mul_var(poly, var):
        out = defaultdict(int)
        for mon, c in poly.items():
            new = tuple(sorted(mon + (var,)))
            out[new] = (out[new] + c) % p
        return out

    xl_rows = []
    for poly in polys_eq:
        row = [0] * len(mons3)
        for mon, c in poly.items():
            row[mons3_index[mon]] = c
        xl_rows.append(row)
        for vi in range(nW):
            mp = mul_var(poly, vi)
            row = [0] * len(mons3)
            for mon, c in mp.items():
                row[mons3_index[mon]] = c
            xl_rows.append(row)

    print('XL matrix', len(xl_rows), 'x', len(mons3), 't=', time.time() - t0)
    rr3, piv3 = rref(xl_rows, len(mons3), p)
    print('XL rank', len(piv3), 't=', time.time() - t0)

    free = [j for j in range(len(mons3)) if j not in piv3]
    print('free mons', len(free), 'among them deg1',
          sum(1 for j in free if len(mons3[j]) == 1))

    # Solve affine with ()=1, free=0
    # For each pivot row: mon_pv + sum_{j>pv} rr[j] mon_j = 0  (since rr[pv]=1)
    # With mon_0=1 and free=0: mon_pv = -rr[0] if no other terms
    values = {0: 1}
    for j in free:
        values[j] = 0
    for i, pv in enumerate(piv3):
        val = 0
        for j, coef in enumerate(rr3[i]):
            if j == pv or not coef:
                continue
            if j in values:
                val = (val + coef * values[j]) % p
            else:
                # non-assigned non-free? shouldn't happen
                pass
        values[pv] = (-val) % p

    W_sol = [values.get(1 + i, 0) for i in range(nW)]
    print('W_sol', W_sol)

    # True W for comparison
    A_perm = [[Qvecs[r][perm[c]] for c in range(D)] for r in range(t)]
    rows, pivs = rref([row[:] for row in A_perm], D, p)
    W_true = [rows[i][t:] for i in range(t)]
    Wflat = [W_true[i][k] for i in range(t) for k in range(D - t)]
    print('W_true', Wflat)
    print('MATCH', W_sol == Wflat)
    print('done', time.time() - t0)


if __name__ == '__main__':
    main()
