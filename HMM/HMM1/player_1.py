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

    alpha = [pi[i] * B[i][obs[0]] for i in range(N)]

    for t in range(1, T):
        o = obs[t]
        new_alpha = [0.0] * N
        for j in range(N):
            s = 0.0
            for i in range(N):
                s += alpha[i] * A[i][j]
            new_alpha[j] = s * B[j][o]
        alpha = new_alpha

    prob = sum(alpha)

    print("{:.6f}".format(prob))


if __name__ == "__main__":
    main()