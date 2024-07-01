#!/usr/bin/env python3

import re
import z3
import sys

def main():
    xs = [z3.Bool("x%d" % (i + 1)) for i in range(50)]
    solver = z3.Solver()

    for line in sys.stdin:
        if line.strip() == "":
            break
        vs = [re.sub('[^!0123456789]', '', x.strip()) for x in line.split(' | ')]
        ps = [xs[int(v[1:])-1] == False if v[0] == '!' else xs[int(v)-1] == True for v in vs]
        solver.add(z3.Or(ps))

    result = solver.check()
    if result == z3.unsat:
        print("UNSAT")
        return

    model = solver.model()

    answer = 0
    result = [re.sub('[^TF=0123456789]', '', x) for x in str(model).split("\n")]
    for x in result:
        k, v = x.split("=")
        k = int(k) - 1
        if v == 'T':
            answer += 2 ** k
    print(answer)

    n = answer
    icfp = ''
    while n > 0:
        icfp = chr(n % 94 + 33) + icfp
        n //= 94
    print("I" + icfp)

if __name__ == '__main__':
    main()
