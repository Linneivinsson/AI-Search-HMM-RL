import sys


def read_matrix(tokens, idx):
    r = int(tokens[idx])
    c = int(tokens[idx + 1])
    idx += 2
    mat = []
    for _ in range(r):
        row = [float(tokens[idx + j]) for j in range(c)]
        mat.append(row)
        idx += c
    return r, c, mat, idx


def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return

    idx = 0
    rA, cA, A, idx = read_matrix(data, idx)
    rB, cB, B, idx = read_matrix(data, idx)
    rPi, cPi, Pi, idx = read_matrix(data, idx)

    pi = Pi[0]  

    next_pi = [0.0] * cA  
    for j in range(cA):         
        s = 0.0
        for i in range(rA):     
            s += pi[i] * A[i][j]
        next_pi[j] = s

    M = cB  
    emission = [0.0] * M
    for k in range(M):          
        s = 0.0
        for i in range(rB):     
            s += next_pi[i] * B[i][k]
        emission[k] = s

    out = ["1", str(M)] + [f"{x:.6f}" for x in emission]
    sys.stdout.write(" ".join(out))


if __name__ == "__main__":
    main()
