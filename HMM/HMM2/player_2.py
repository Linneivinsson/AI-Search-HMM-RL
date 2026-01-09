import sys


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


def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return

    idx = 0

    rA, cA, A, idx = read_matrix(data, idx)
    rB, cB, B, idx = read_matrix(data, idx)
    rPi, cPi, Pi, idx = read_matrix(data, idx)

    T = int(data[idx])
    idx += 1
    obs = list(map(int, data[idx:idx + T]))

    pi = Pi[0]         
    N = cA              

    delta = [[0.0] * N for _ in range(T)]
    psi = [[-1] * N for _ in range(T)]

    o0 = obs[0]
    for i in range(N):
        delta[0][i] = pi[i] * B[i][o0]
        psi[0][i] = -1

    for t in range(1, T):
        ot = obs[t]
        for j in range(N):
            best_val = -1.0
            best_k = 0
            for k in range(N):
                val = delta[t - 1][k] * A[k][j]
                if val > best_val:
                    best_val = val
                    best_k = k
            delta[t][j] = best_val * B[j][ot]
            psi[t][j] = best_k

    last_state = max(range(N), key=lambda i: delta[T - 1][i])

    path = [0] * T
    path[T - 1] = last_state
    for t in range(T - 1, 0, -1):
        path[t - 1] = psi[t][path[t]]

    print(" ".join(str(s) for s in path))


if __name__ == "__main__":
    main()