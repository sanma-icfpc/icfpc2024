#!/usr/bin/env python3

import re
import z3
import sys

def efficient8():
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


def efficient9():
    solver = z3.Solver()

    terms = []
    for line in sys.stdin:
        if line.strip() == "":
            break
        vs = [re.sub('[^!=x0123456789]', '', x.strip()) for x in line.split(' & ')]
        terms.extend(vs)
    # print(terms)

    xs = []
    for t in terms:
        x, y = re.sub('!', '', t).split('=')
        xs.append(x)
        xs.append(y)
    xs = list(set(xs))
    xs.sort()
    xs = [z3.Int(x) for x in xs]
    for x in xs:
        ps = z3.Or([x == v for v in range(10)])
        # print(ps)
        solver.add(ps)
    # print(xs)

    def find(x):
        for v in xs:
            if x == str(v):
                return v
        return None

    for t in terms:
        x, y = re.sub('!', '', t).split('=')
        x = find(x)
        y = find(y)
        if '!' in t:
            solver.add(x != y)
        else:
            solver.add(x == y)

    if solver.check() == z3.unsat:
        print("UNSAT")
        return

    print("Guarantee to have a solution!")

    assign = {}
    for x in reversed(xs):
        a = None
        for v in range(9):
            solver.push()
            solver.add(x == v)
            if solver.check() == z3.sat:
                a = v
                solver.pop(1)
                break
            solver.pop(1)
        if a is None:
            print(f"Error for {x}")
            return
        solver.add(x == a)
        assign[str(x)] = a

    print(assign)

    value = 0
    for x in reversed(xs):
        v = assign[str(x)]
        print(v, end='')
        value = value * 9 + v
    print()
    print(value)


def main():
    efficient8()
    # efficient9()

if __name__ == '__main__':
    main()
