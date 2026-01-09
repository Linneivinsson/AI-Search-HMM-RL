import sys
import math


def read_matrix(tokens, idx):
    r = int(tokens[idx])
    c = int(tokens[idx + 1])
    idx += 2
    mat = []
    for _ in range(r):
        row = [float(tokens[idx + j]) for j in range(c)]
        idx += c
        mat.append(row)
    return r, c, mat, idx


def forward_scaled(A, B, pi, O):
    N = len(A)
    T = len(O)
    alpha = [[0.0] * N for _ in range(T)]
    c = [0.0] * T 

    c0 = 0.0
    o0 = O[0]
    for i in range(N):
        alpha[0][i] = pi[i] * B[i][o0]
        c0 += alpha[0][i]
    if c0 == 0.0:
        c0 = 1e-300
    c[0] = 1.0 / c0
    for i in range(N):
        alpha[0][i] *= c[0]

    for t in range(1, T):
        ct = 0.0
        ot = O[t]
        for i in range(N):
            s = 0.0
            for j in range(N):
                s += alpha[t - 1][j] * A[j][i]
            alpha[t][i] = s * B[i][ot]
            ct += alpha[t][i]
        if ct == 0.0:
            ct = 1e-300
        c[t] = 1.0 / ct
        for i in range(N):
            alpha[t][i] *= c[t]

    return alpha, c


def backward_scaled(A, B, O, c):
    N = len(A)
    T = len(O)
    beta = [[0.0] * N for _ in range(T)]

    for i in range(N):
        beta[T - 1][i] = c[T - 1]

    for t in range(T - 2, -1, -1):
        ot1 = O[t + 1]
        for i in range(N):
            s = 0.0
            for j in range(N):
                s += A[i][j] * B[j][ot1] * beta[t + 1][j]
            beta[t][i] = s * c[t]

    return beta


def compute_gamma_digamma(A, B, O, alpha, beta):
    N = len(A)
    T = len(O)
    gamma = [[0.0] * N for _ in range(T)]
    di_gamma = [[[0.0] * N for _ in range(N)] for _ in range(T - 1)]

    for t in range(T - 1):
        denom = 0.0
        ot1 = O[t + 1]
        for i in range(N):
            for j in range(N):
                denom += alpha[t][i] * A[i][j] * B[j][ot1] * beta[t + 1][j]
        if denom == 0.0:
            denom = 1e-300

        for i in range(N):
            g = 0.0
            for j in range(N):
                val = alpha[t][i] * A[i][j] * B[j][ot1] * beta[t + 1][j] / denom
                di_gamma[t][i][j] = val
                g += val
            gamma[t][i] = g

    for i in range(N):
        gamma[T - 1][i] = alpha[T - 1][i]

    return gamma, di_gamma


def baum_welch(A, B, pi, O, max_iters=100):
    N = len(A)
    M = len(B[0])
    T = len(O)

    old_log_prob = float("-inf")
    iters = 0

    while True:
        alpha, c = forward_scaled(A, B, pi, O)
        beta = backward_scaled(A, B, O, c)
        gamma, di_gamma = compute_gamma_digamma(A, B, O, alpha, beta)

        pi = [gamma[0][i] for i in range(N)]

        for i in range(N):
            denom = 0.0
            for t in range(T - 1):
                denom += gamma[t][i]
            if denom == 0.0:
                continue
            for j in range(N):
                numer = 0.0
                for t in range(T - 1):
                    numer += di_gamma[t][i][j]
                A[i][j] = numer / denom

        for i in range(N):
            denom = 0.0
            for t in range(T):
                denom += gamma[t][i]
            if denom == 0.0:
                continue
            for k in range(M):
                numer = 0.0
                for t in range(T):
                    if O[t] == k:
                        numer += gamma[t][i]
                B[i][k] = numer / denom

        log_prob = -sum(math.log(ci) for ci in c)

        iters += 1
        if log_prob <= old_log_prob or iters >= max_iters:
            break
        old_log_prob = log_prob

    return A, B


def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return

    idx = 0
    rA, cA, A, idx = read_matrix(data, idx)
    rB, cB, B, idx = read_matrix(data, idx)
    rPi, cPi, Pi, idx = read_matrix(data, idx)
    pi = Pi[0]

    T = int(data[idx])
    idx += 1
    O = list(map(int, data[idx:idx + T]))

    A, B = baum_welch(A, B, pi, O, max_iters=100)

    N = len(A)
    M = len(B[0])

    outA = ["4 4"]  
    outA = [str(N), str(N)] + [
        f"{A[i][j]:.6f}" for i in range(N) for j in range(N)
    ]
    outB = [str(N), str(M)] + [
        f"{B[i][k]:.6f}" for i in range(N) for k in range(M)
    ]

    print(" ".join(outA))
    print(" ".join(outB))


if __name__ == "__main__":
    main()