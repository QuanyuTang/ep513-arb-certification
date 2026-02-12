#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import multiprocessing as mp

from flint import arb, acb, fmpq, ctx


def set_prec(dps: int):
    # Working precision for arb/acb (digits). Higher = tighter balls.
    ctx.dps = dps
    # Avoid oversubscription: we parallelize with multiprocessing, so keep Arb internal threads = 1
    ctx.threads = 1


def exact_parameters():
    # Exact rationals
    K0_q = fmpq(7137, 2000)                # 7137/2000
    alpha0_q = fmpq(198074929, 50000000)   # 198074929/50000000
    return K0_q, alpha0_q


def build_coeffs(K0, alpha0, nmax=5):
    # c_n = exp(i * alpha0 * T_n) / K0^{T_n},  T_n = n(n+1)/2
    cs = []
    for n in range(nmax + 1):
        T = n * (n + 1) // 2
        phase = acb(0, alpha0 * T).exp()     # exp(i * alpha0 * T)
        denom = K0 ** T
        cs.append(phase / denom)
    return cs


def P_theta(theta, cs):
    # P(theta) = 2 * sum_{n=0}^5 c_n * cos((2n+1)*theta)
    s = acb(0)
    for n, c in enumerate(cs):
        m = 2 * n + 1
        s += c * (theta * m).cos()
    return 2 * s


def scan_chunk(args):
    start, end, M, dps = args
    set_prec(dps)

    K0_q, alpha0_q = exact_parameters()
    K0 = arb(K0_q)
    alpha0 = arb(alpha0_q)

    cs = build_coeffs(K0, alpha0, nmax=5)

    two_pi_over_M = (arb.pi() * 2) / M

    max_u = arb(0)
    argmax = start

    for j in range(start, end):
        theta = two_pi_over_M * j
        u = P_theta(theta, cs).abs_upper()   # rigorous upper bound for |P(theta_j)|
        if u > max_u:
            max_u = u
            argmax = j

    return max_u, argmax


def compute_mesh_max(M: int, dps: int, workers: int):
    if workers <= 1:
        return scan_chunk((0, M, M, dps))

    step = (M + workers - 1) // workers
    tasks = []
    for k in range(workers):
        a = k * step
        b = min(M, (k + 1) * step)
        if a < b:
            tasks.append((a, b, M, dps))

    with mp.Pool(processes=workers) as pool:
        results = pool.map(scan_chunk, tasks)

    max_u, argmax = results[0]
    for u, j in results[1:]:
        if u > max_u:
            max_u, argmax = u, j
    return max_u, argmax


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--M", type=int, default=2_000_000)
    ap.add_argument("--dps", type=int, default=90)
    ap.add_argument("--workers", type=int, default=1)

    # exact bound used in the lemma: 1.709176398 = 1709176398 / 10^9
    ap.add_argument("--bound_num", type=int, default=1709176398)
    ap.add_argument("--bound_den", type=int, default=10**9)

    args = ap.parse_args()

    mesh_max_u, argmax = compute_mesh_max(args.M, args.dps, args.workers)

    bound = arb(fmpq(args.bound_num, args.bound_den))

    print("=== Arb-certified mesh bound ===")
    print(f"M = {args.M}, dps = {args.dps}, workers = {args.workers}")
    print("mesh_max_upper =", mesh_max_u.str(25, radius=False), "(attained at j =", argmax, ")")
    print("Target bound   =", bound.str(25, radius=False))
    print("Certified mesh_max_upper <= bound :", (mesh_max_u <= bound))


if __name__ == "__main__":
    mp.freeze_support()
    main()
